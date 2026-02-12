"""
服务部署管理
管理已部署 MCP 服务的生命周期

支持两种部署模式：
1) http: 以 uvicorn 子进程方式启动（适配 FastMCP / FastAPI）
2) mcp: 预留（如你后续要做 MCPClientAdapter 直连，可在此扩展）
"""

import asyncio
import logging
import os
import re
import signal
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DeploymentService:
    """服务部署管理器"""

    def __init__(self):
        self.running_services: Dict[str, Dict[str, Any]] = {}  # service_id -> deployment_info
        self.base_port = 8100
        self.max_port = 8200
        self._used_ports: set[int] = set()
        logger.info("DeploymentService initialized")

    # -------------------- port utils --------------------
    def _allocate_port(self) -> int:
        for port in range(self.base_port, self.max_port):
            if port not in self._used_ports:
                self._used_ports.add(port)
                return port
        raise RuntimeError("No available ports for deployment")

    def _release_port(self, port: int) -> None:
        if port:
            self._used_ports.discard(port)

    # -------------------- path / entry resolution --------------------
    def _resolve_entry_file(self, file_path: str) -> Path:
        """
        允许 file_path 是目录或文件：
        - 若是 .py 文件：直接返回
        - 若是目录：优先选择 {dir}/{dir_name}.py，其次 main.py，再其次目录下最大的 .py（排除 *_original.py 和 __init__.py）
        """
        p = Path(file_path)

        if p.is_file():
            if p.suffix.lower() != ".py":
                raise FileNotFoundError(f"Service file is not a .py: {p}")
            return p

        if p.is_dir():
            # 1) 同名主文件
            same = p / f"{p.name}.py"
            if same.exists():
                return same

            # 2) main.py
            main = p / "main.py"
            if main.exists():
                return main

            # 3) 最大的可运行 py
            candidates = [
                x for x in p.glob("*.py")
                if x.name not in {"__init__.py"} and not x.name.endswith("_original.py")
            ]
            if not candidates:
                raise FileNotFoundError(f"No runnable .py found under directory: {p}")

            candidates.sort(key=lambda x: x.stat().st_size, reverse=True)
            return candidates[0]

        raise FileNotFoundError(f"Service path not found: {p}")

    def _detect_asgi_attr(self, entry_file: Path) -> str:
        """
        自动识别 uvicorn 应该启动的 ASGI 对象变量名：
        - 优先 app（FastAPI 或 mcp.*_app() 转出来的 ASGI）
        - 其次 mcp（仅当代码没有导出 app 时才用；但 FastMCP 本身不是 ASGI callable）
        """
        text = entry_file.read_text(encoding="utf-8", errors="ignore")

        # 1) FastAPI
        if re.search(r"^\s*app\s*=\s*FastAPI\s*\(", text, re.M):
            return "app"

        # 2) Starlette（我们会用 Starlette 包一层来挂载 MCP）
        if re.search(r"^\s*app\s*=\s*Starlette\s*\(", text, re.M):
            return "app"

        # 3) 直接导出 mcp_app / streamable_http_app 也可以（兜底）
        if re.search(r"^\s*(app|mcp_app)\s*=\s*mcp\.streamable_http_app\s*\(", text, re.M):
            return "app" if re.search(r"^\s*app\s*=", text, re.M) else "mcp_app"

        if re.search(r"^\s*(app|mcp_app)\s*=\s*mcp\.sse_app\s*\(", text, re.M):
            return "app" if re.search(r"^\s*app\s*=", text, re.M) else "mcp_app"

        # 4) 旧逻辑：如果只有 mcp=FastMCP(...)，仍返回 mcp（但注意它不是 ASGI callable）
        if re.search(r"^\s*mcp\s*=\s*FastMCP\s*\(", text, re.M):
            return "mcp"

        return "app"

    # -------------------- precheck --------------------
    async def _precheck_uvicorn(
        self,
        cwd: str,
        module_name: str,
        asgi_attr: str,
        port: int,
        env: Dict[str, str],
        max_output_length: int = 8000,
    ) -> None:
        """
        预检：启动 uvicorn 0.8s，若秒退则抓 stdout/stderr
        """
        cmd = [
            sys.executable, "-m", "uvicorn",
            f"{module_name}:{asgi_attr}",
            "--host", "0.0.0.0",
            "--port", str(port),
            "--workers", "1",
            "--log-level", "info",
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        await asyncio.sleep(0.8)
        ret = proc.returncode
        if ret is not None:
            out = (await proc.stdout.read()).decode("utf-8", errors="ignore")
            err = (await proc.stderr.read()).decode("utf-8", errors="ignore")
            logger.error("❌ uvicorn 预检秒退 (returncode=%s)", ret)
            if out.strip():
                logger.error("---- server stdout ----\n%s", out[-max_output_length:])
            if err.strip():
                logger.error("---- server stderr ----\n%s", err[-max_output_length:])
            raise RuntimeError("部署预检失败：服务启动即退出，请根据 stderr 修复生成代码/依赖/环境变量")

        # 仍在运行：终止预检进程（避免占用端口），正式部署再启动一次
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=1.0)
        except Exception:
            proc.kill()

    # -------------------- public APIs --------------------
    async def deploy_service(self, service_id: str, file_path: str, mode: str = "http") -> Dict[str, Any]:
        """
        部署 MCP 服务
        返回 dict 会被 router 用来写回 DB（is_deployed / deployed_at / endpoints / deploy_port）
        """
        logger.info("Deploying service %s from %s in %s mode", service_id, file_path, mode)

        if not file_path:
            raise FileNotFoundError("Service file_path is empty")

        if mode == "http":
            return await self._deploy_as_http(service_id, file_path)
        if mode == "mcp":
            return await self._deploy_as_mcp(service_id, file_path)

        raise ValueError(f"Unknown deployment mode: {mode}")

    async def _deploy_as_http(self, service_id: str, file_path: str) -> Dict[str, Any]:
        """
        以 HTTP 服务方式部署（uvicorn 子进程）
        - 自动解析入口文件
        - 自动检测 ASGI 对象名（app / mcp）
        - 预检秒退抓日志
        - 返回 deploy_port / endpoints / deployed_at（naive UTC）
        """
        port = self._allocate_port()

        try:
            entry_file = self._resolve_entry_file(file_path)
            service_dir = str(entry_file.parent)
            module_name = entry_file.stem
            asgi_attr = self._detect_asgi_attr(entry_file)

            env = os.environ.copy()
            env["MCP_PORT"] = str(port)
            env["PORT"] = str(port)

            # 预检（秒退直接报 stderr）
            await self._precheck_uvicorn(
                cwd=service_dir,
                module_name=module_name,
                asgi_attr=asgi_attr,
                port=port,
                env=env,
            )

            cmd = [
                sys.executable, "-m", "uvicorn",
                f"{module_name}:{asgi_attr}",
                "--host", "0.0.0.0",
                "--port", str(port),
                "--workers", "1",
                "--log-level", "info",
            ]

            logger.info("Starting service with command: %s (cwd=%s)", " ".join(cmd), service_dir)

            # Windows / POSIX 分别处理子进程组，便于 stop 时整体杀掉
            popen_kwargs: Dict[str, Any] = {
                "cwd": service_dir,
                "env": env,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "text": False,
            }
            if os.name != "nt":
                popen_kwargs["preexec_fn"] = os.setsid
            else:
                popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]

            process = subprocess.Popen(cmd, **popen_kwargs)

            # 按你要求：DB 写入用 naive UTC datetime
            deployed_at_dt = datetime.now(timezone.utc).replace(tzinfo=None)
            deployed_at_iso = deployed_at_dt.isoformat()

            base_url = f"http://127.0.0.1:{port}"
            endpoints = [
                f"{base_url}/mcp",          # MCP HTTP endpoint
                f"{base_url}/",             # root
                f"{base_url}/docs",         # only meaningful if FastAPI/OpenAPI exists
                f"{base_url}/openapi.json", # only meaningful if FastAPI/OpenAPI exists
            ]


            self.running_services[service_id] = {
                "mode": "http",
                "process": process,
                "pid": process.pid,
                "port": port,
                "deploy_port": port,
                "base_url": base_url,
                "endpoints": endpoints,
                "entry": f"{module_name}:{asgi_attr}",
                "cwd": service_dir,
                "deployed_at": deployed_at_iso,
                "deployed_at_dt": deployed_at_dt,
            }

            logger.info(
                "Service %s deployed at port %s, PID=%s, entry=%s",
                service_id, port, process.pid, f"{module_name}:{asgi_attr}"
            )

            # 这个 dict 建议 router 直接用来写 DB
            return {
                "service_id": service_id,
                "mode": "http",
                "pid": process.pid,
                "deploy_port": port,  # ✅ 关键：写回 service.deploy_port
                "base_url": base_url,
                "endpoints": endpoints,
                # ✅ 关键：按你要求返回 isoformat 的 naive UTC 字符串
                "deployed_at": deployed_at_iso,
                # ✅ 同时也给一个 naive datetime，方便你 router 直接写 DB
                "deployed_at_dt": deployed_at_dt,
            }

        except Exception:
            self._release_port(port)
            raise

    async def _deploy_as_mcp(self, service_id: str, file_path: str) -> Dict[str, Any]:
        """
        预留：如你后续需要 MCPClientAdapter 直连
        当前先抛出明确错误，避免误用
        """
        raise NotImplementedError("mcp mode is not implemented yet; use mode='http'")

    async def stop_service(self, service_id: str) -> bool:
        """停止部署的服务"""
        if service_id not in self.running_services:
            return False

        deployment_info = self.running_services[service_id]

        try:
            if deployment_info["mode"] == "http":
                process: subprocess.Popen = deployment_info["process"]

                if process.poll() is None:
                    if os.name != "nt":
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    else:
                        process.terminate()

                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        if os.name != "nt":
                            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                        else:
                            process.kill()

                self._release_port(int(deployment_info.get("port") or 0))

            # mcp mode：未来扩展

            del self.running_services[service_id]
            logger.info("Service %s stopped successfully", service_id)
            return True

        except Exception as e:
            logger.error("Failed to stop service %s: %s", service_id, e)
            return False

    async def get_service_status(self, service_id: str) -> Optional[Dict[str, Any]]:
        """获取服务状态"""
        if service_id not in self.running_services:
            return None

        deployment_info = self.running_services[service_id]

        is_running = False
        if deployment_info["mode"] == "http":
            process = deployment_info.get("process")
            is_running = bool(process) and process.poll() is None
        elif deployment_info["mode"] == "mcp":
            is_running = True

        return {
            "service_id": service_id,
            "status": "running" if is_running else "stopped",
            "mode": deployment_info.get("mode"),
            "port": deployment_info.get("port"),
            "deploy_port": deployment_info.get("deploy_port"),
            "base_url": deployment_info.get("base_url"),
            "endpoints": deployment_info.get("endpoints", []),
            "deployed_at": deployment_info.get("deployed_at"),
            "pid": deployment_info.get("pid"),
        }

    async def list_deployed_services(self) -> List[Dict[str, Any]]:
        """列出所有已部署的服务"""
        services: List[Dict[str, Any]] = []
        for sid in list(self.running_services.keys()):
            status = await self.get_service_status(sid)
            if status:
                services.append(status)
        return services

    async def health_check(self, service_id: str) -> bool:
        """检查服务健康状态（若服务未实现 /health，可能返回 False）"""
        if service_id not in self.running_services:
            return False

        deployment_info = self.running_services[service_id]

        if deployment_info["mode"] == "http":
            health_url = f"{deployment_info.get('base_url', '')}/health"
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        health_url,
                        timeout=aiohttp.ClientTimeout(total=5),
                    ) as resp:
                        return resp.status == 200
            except Exception:
                return False

        if deployment_info["mode"] == "mcp":
            # 未来扩展
            return True

        return False

    def get_running_services(self) -> List[str]:
        """获取所有运行中的服务ID列表"""
        return list(self.running_services.keys())
