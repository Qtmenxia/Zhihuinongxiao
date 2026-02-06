from pathlib import Path
import os
import json
import yaml
from jinja2 import Template
from typing import Optional, Dict, Any, List

# 获取项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

# 尝试导入logger，如果失败使用标准logging
try:
    from logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def find_api_file(resources_dir: Path, api_name: str) -> Optional[Path]:
    """Find the OpenAPI file (YAML or JSON) for a given API name."""
    api_dir = resources_dir / api_name
    if not api_dir.is_dir():
        logger.warning(f"API directory not found: {api_dir}")
        return None
    
    for ext in ["*.yaml", "*.yml", "*.json"]:
        files = list(api_dir.glob(ext))
        if files:
            return files[0]
    return None


def load_api_spec(file_path: Path) -> Optional[Dict[str, Any]]:
    """Load API specification from a YAML or JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if file_path.suffix in [".yaml", ".yml"]:
                return yaml.safe_load(f)
            else:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading API spec: {e}")
        return None


def load_mcp_doc(resources_dir: Path) -> Optional[str]:
    """Load the MCP documentation content."""
    mcp_doc_path = resources_dir / "mcp-server-doc.md"
    if not mcp_doc_path.exists():
        return None
    try:
        with open(mcp_doc_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def read_file_content(file_path: Path) -> Optional[str]:
    if not file_path.exists():
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def list_server_files(output_dir: Path) -> List[str]:
    if not output_dir.exists():
        return []
    return [f.name for f in output_dir.glob("*.py")]


def list_report_files(report_dir: Path) -> List[str]:
    if not report_dir.exists():
        return []
    return [f.name for f in report_dir.glob("*.md")]


def load_prompt(prompt_path: str) -> Template:
    full_path = PROMPTS_DIR / prompt_path
    with open(full_path, 'r', encoding='utf-8') as f:
        return Template(f.read())