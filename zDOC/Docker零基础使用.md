# Docker 零基础使用指南（智农链销）

不会用 Docker 也没关系，按下面步骤**从上到下、一步一步**做就行。每一步都有说明，照着做就能把项目跑起来。

> **可以不配置 API 密钥吗？**  
> **可以。** 不配 API 密钥也能正常启动项目，可以访问 API 文档、产品/订单/农户管理等接口。  
> 只有用到 **「AI 服务生成」**（用自然语言生成 MCP 服务）时才会需要密钥；到时再配也可以。

---

## 第 0 步：确认 Docker 已启动

1. 在电脑上找到 **Docker Desktop**，双击打开。
2. 等待右下角（或任务栏）的 Docker 图标**不再转圈**，变成稳定的小鲸鱼图标。
3. 图标变绿或显示 "Docker Desktop is running" 就说明好了。

**如果没装 Docker Desktop**：去 https://www.docker.com/products/docker-desktop 下载安装，安装后重启电脑再打开。

---

## 第 1 步：准备 API 密钥（可选）

**如果暂时不想配**：可以跳过这一步，直接做第 2 步，在 `.env` 里把 `GEMINI_API_KEY=` 留空即可，项目照常能启动（只是不能使用「AI 服务生成」功能）。

**如果要用 AI 服务生成功能**：需要至少一个 LLM 的“钥匙”，推荐 **Gemini**（免费）：

1. 用浏览器打开：**https://aistudio.google.com/app/apikey**
2. 用你的 **Google 账号**登录。
3. 点击 **「创建 API 密钥」**。
4. 复制生成的那一串字符（一般像 `AIzaSy...` 这样），先粘贴到记事本里备用。

---

## 第 2 步：在项目里创建配置文件

1. 打开项目文件夹：`e:\gitlab\Zhihuinongxiao`。
2. 看看有没有一个叫 **`backend`** 的文件夹，点进去。
3. 里面有一个 **`.env.example`** 文件（如果看不到后缀，可能是 `.env.example` 文本文件）。
4. **复制**这个文件，在同一目录下 **粘贴**，然后把复制出来的文件**重命名**为：**`.env`**（把 `.example` 和后面的都删掉，只保留 `.env`）。
5. 用 **记事本** 或 **VS Code** 打开 **`.env`**。
6. 找到这几行，按下面说明改（**只改等号右边的值**，别删掉左边的名字）：

   ```env
   GEMINI_API_KEY=
   POSTGRES_PASSWORD=123456
   SECRET_KEY=abcdefghijklmnopqrstuvwxyz123456
   ```

   - **不配 API 密钥时**：`GEMINI_API_KEY=` 后面留空即可（如上）。
   - **配了 API 密钥时**：把 `GEMINI_API_KEY=` 后面粘贴你的 Gemini 密钥。
   - `POSTGRES_PASSWORD` 和 `SECRET_KEY` 可以就按上面写，不用改（想改也可以，SECRET_KEY 至少 32 个字符）。

7. **保存** 并关闭文件。

这样 Docker 启动时才能读到你的配置（数据库密码等）；API 密钥不填也能正常启动。

---

## 第 3 步：让 Docker 能读到你的配置

Docker 启动时会在 **运行命令的那个目录** 找 `.env` 文件。我们有两种做法，**任选一种**即可。

### 做法 A：复制一份 .env 到 docker 目录（推荐，最简单）

1. 在项目根目录 `e:\gitlab\Zhihuinongxiao` 下，进入 `backend`，找到你刚改好的 **`.env`**。
2. **复制** 这个 `.env` 文件。
3. 进入文件夹：`e:\gitlab\Zhihuinongxiao\infrastructure\docker`。
4. 在这个 `docker` 文件夹里 **粘贴**，保证 `docker` 目录下有一份 **`.env`**。

这样后面在 `docker` 目录里运行命令时，Docker 就能自动读到配置。

### 做法 B：在项目根目录用脚本部署（会从根目录读 .env）

1. 把 **`.env`** 放在 **项目根目录**：`e:\gitlab\Zhihuinongxiao\.env`（和 `backend`、`frontend` 同级）。
2. 后面用「一键部署脚本」启动（见第 4 步做法 B）。

---

## 第 4 步：用 Docker 启动项目

在电脑上打开 **PowerShell**（或 CMD）：

- 按 `Win + R`，输入 `powershell`，回车；  
  或者：在开始菜单搜“PowerShell”，打开即可。

然后**二选一**执行下面一种方式。

### 做法 A：直接启动（你已按做法 A 把 .env 复制到了 docker 目录）

在 PowerShell 里**一行一行**输入（可以复制粘贴），每行输完按回车：

```powershell
cd e:\gitlab\Zhihuinongxiao\infrastructure\docker
```

再输入：

```powershell
docker-compose up -d
```

第一次会下载镜像、构建镜像，可能要几分钟，等它跑完不要关窗口。最后出现类似 “Creating zhinong-postgres ... done” 就说明启动成功了。

### 做法 B：用脚本一键部署（你已按做法 B 把 .env 放在项目根目录）

在 **Git Bash** 或 **WSL** 里（没有的话就用做法 A），在项目根目录执行：

```bash
cd e:/gitlab/Zhihuinongxiao
./scripts/deploy.sh
```

脚本会检查环境、读 `.env`、构建并启动所有服务，按提示等待即可。  
未配置 API 密钥时脚本会提示一句警告，但会继续部署，不影响启动。

---

## 第 5 步：确认项目已经跑起来

1. 等 **大约 30 秒～1 分钟**（第一次可能稍久一点）。
2. 打开浏览器，在地址栏输入：**http://localhost:8000/docs**，回车。
3. 如果能看到 **API 文档** 页面（有很多接口列表），说明**已经运行成功**。

你也可以再打开：**http://localhost:8000/health**  
如果页面显示 `"status":"healthy"` 之类的，说明服务正常。

---

## 常用操作（以后会用到）

### 查看运行状态

在 PowerShell 里执行（先进入 docker 目录）：

```powershell
cd e:\gitlab\Zhihuinongxiao\infrastructure\docker
docker-compose ps
```

会列出几个容器（postgres、redis、api、worker、nginx），状态是 “Up” 就表示在运行。

### 查看日志（出错时用）

```powershell
cd e:\gitlab\Zhihuinongxiao\infrastructure\docker
docker-compose logs
```

想看持续滚动的日志可以加 `-f`：

```powershell
docker-compose logs -f
```

按 `Ctrl + C` 退出查看。

### 停止项目

```powershell
cd e:\gitlab\Zhihuinongxiao\infrastructure\docker
docker-compose down
```

执行后所有容器会停止并删除（数据一般会保留在 Docker 的卷里）。

### 下次再启动

和第一次一样，先确保 Docker Desktop 已启动，然后：

```powershell
cd e:\gitlab\Zhihuinongxiao\infrastructure\docker
docker-compose up -d
```

再等几十秒，访问 http://localhost:8000/docs 即可。

---

## 常见问题

**Q：提示“找不到 docker-compose”或“不是内部或外部命令”？**  
A：说明 Docker Desktop 没装好或没启动。请先打开 Docker Desktop，等它完全启动后再试。新版本也可能要用 `docker compose`（没有横杠），可以试：

```powershell
docker compose up -d
```

**Q：端口被占用（port is already allocated）？**  
A：说明 8000 或 5432、6379 等端口被别的程序占了。可以：关掉占用端口的程序；或者改 `docker-compose.yml` 里对应服务的 `ports`（例如把 `8000:8000` 改成 `8001:8000`，然后访问 http://localhost:8001/docs）。

**Q：访问 http://localhost:8000/docs 打不开？**  
A：先等 1～2 分钟再试；再在 PowerShell 里执行 `docker-compose ps` 看 api 容器是否 “Up”；然后执行 `docker-compose logs api` 看有没有报错（例如 API 密钥错误、数据库连不上等）。

**Q：.env 里填错了 API 密钥怎么办？**  
A：用记事本或 VS Code 打开 `backend\.env`（或 `infrastructure\docker\.env`），改好保存，然后执行：

```powershell
cd e:\gitlab\Zhihuinongxiao\infrastructure\docker
docker-compose down
docker-compose up -d
```

---

## 小结：你一共要做的事

1. 打开 **Docker Desktop**，等它启动完成。  
2. 去 Google 申请 **Gemini API 密钥**，复制下来。  
3. 在 **backend** 里复制 `.env.example` 为 **`.env`**，填好 **GEMINI_API_KEY**、**POSTGRES_PASSWORD**、**SECRET_KEY** 并保存。  
4. 把 **`.env`** 复制到 **infrastructure\docker** 目录（或按做法 B 放到项目根目录并用脚本）。  
5. 在 PowerShell 里执行：  
   `cd e:\gitlab\Zhihuinongxiao\infrastructure\docker`  
   `docker-compose up -d`  
6. 等约 1 分钟后浏览器打开 **http://localhost:8000/docs**，能看到文档就成功了。

以后想停掉项目就执行：`docker-compose down`；想再开就再执行一次 `docker-compose up -d`。
