# Dachuang-MS 本地配置与运行指南

> 目标：在本机完成运行（后端 + 前端 + 数据库）。

## 0. 组件说明

- 后端：Django（REST API 前缀：`/api/v1`），默认端口 `8000`
- 前端：Vite dev server，默认端口 `3000`
- 数据库：PostgreSQL（默认连接：`localhost:5432`，库名 `dachuang_db`，用户 `postgres`，密码 `123456`）

默认的前端请求地址为 `http://localhost:8000/api/v1`（可用环境变量覆盖）。

## 1. 环境要求（建议版本）

### 必需

- Python：建议 `3.12+`
- Node.js：建议 `18+`（项目在较新版本也可运行）
- PostgreSQL：建议 `14+`（项目开发环境使用 `16`）

命令执行位置约定：

- 下文命令默认在“项目根目录”执行（即与 `backend/`、`frontend/` 同级的目录）。

## 2. 初始化数据库（PostgreSQL）

项目后端默认连接配置写在 `backend/config/settings.py`，并可用环境变量覆盖：  
`DB_NAME=dachuang_db`、`DB_USER=postgres`、`DB_PASSWORD=123456`、`DB_HOST=localhost`、`DB_PORT=5432`。

数据库需使用本机 PostgreSQL 服务。

更详细的说明见：`docs/DB.md`。

### 2.1 创建数据库并设置账号密码

确保本机 PostgreSQL 已启动，并执行（以 psql 为例）：

```sql
-- 进入 psql 后执行
CREATE DATABASE dachuang_db;
ALTER USER postgres WITH PASSWORD '123456';
```

如不使用 `postgres/123456`，请通过 `backend/.env`（推荐）或环境变量设置 `DB_USER/DB_PASSWORD` 等连接信息。

### 2.2 导入数据库结构与测试数据（推荐）

仓库根目录提供 `dachuang_db_full.sql`，包含数据库结构与测试数据。

Linux/macOS：

```bash
PGPASSWORD='123456' psql -h localhost -p 5432 -U postgres -d dachuang_db -f ./dachuang_db_full.sql
```

Windows PowerShell：

```powershell
$env:PGPASSWORD="123456"; psql -h localhost -p 5432 -U postgres -d dachuang_db -f .\dachuang_db_full.sql
```

说明：

- 导入前需确保数据库 `dachuang_db` 已存在。
- `dachuang_db_full.sql` 由 `pg_dump` 生成，包含 `DROP TABLE IF EXISTS` 等清理语句；导入到目标数据库将覆盖同名对象。

### 2.3 仅导入数据库结构（可选）

如希望从空数据开始，可导入 `dachuang_db_schema.sql`（仅结构，无测试数据）。导入后建议执行一次 `python manage.py migrate` 以确保迁移与代码一致。

## 3. 启动后端（Django）

### 3.1 创建虚拟环境并安装依赖（首次必做）

Linux/macOS/WSL：

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

Windows PowerShell（示例）：

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

Windows CMD（示例）：

```bat
cd backend
python -m venv venv
venv\Scripts\activate.bat
pip install -U pip
pip install -r requirements.txt
```

### 3.2 迁移数据库表结构（可选）

如已导入 `dachuang_db_full.sql`，此步骤可跳过；如需确保迁移与代码一致，可执行一次迁移（通常不会产生变更）。

```bash
python manage.py migrate
```

说明：

- 字典项（dictionaries）会在迁移中自动写入一些初始数据（见 `backend/apps/dictionaries/migrations/`）。

### 3.3 创建一个可登录的管理员账号（必要时执行）

系统登录接口仅允许使用 `employee_id` 登录（不是 Django 默认的 `username`）。如数据库中不存在可登录的管理员账号，可通过 Django Shell 创建一个“一级管理员（LEVEL1_ADMIN）”账号：

```bash
python manage.py shell
```

在交互式 Shell 中执行：

```python
from apps.users.models import User

User.objects.create_superuser(
    username="admin",
    email="admin@example.com",
    password="admin123456",
    employee_id="admin",
    real_name="系统管理员",
    role=User.UserRole.LEVEL1_ADMIN,
)
```

之后可用该账号调用后端登录接口：

- `POST http://localhost:8000/api/v1/auth/login/`
- body 示例：
  - `{"employee_id":"admin","password":"admin123456","role":"level1_admin"}`

### 3.4（可选但推荐）设置后端环境变量

后端会读取以下环境变量（不设置也能运行，但不利于多人开发一致性）：

- `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT`：数据库连接信息（默认值见上文）
- `DJANGO_SECRET_KEY`：JWT 签名 key（不设置会每次启动随机生成，导致旧 token 失效）
- `DEFAULT_USER_PASSWORD`：管理员创建用户时的默认密码（不设置则必须在接口中传 `password`）
- `DEFAULT_RESET_PASSWORD`：管理员重置密码时的默认密码
- `DJANGO_MEDIA_ROOT`：上传文件目录（默认在 `.local/backend/media`）
- `DJANGO_LOG_DIR`：日志目录（默认在 `.local/backend/logs`）
- `DJANGO_SERVER_MODE`：`gunicorn`（默认）或 `runserver`

可将这些写入本机的 `backend/.env`（该文件已被 `.gitignore` 忽略，不会提交）。`backend/.env.example` 提供了示例配置。

Linux/macOS/WSL（复制示例）：

```bash
cp backend/.env.example backend/.env
```

如当前目录已位于 `backend/`，使用以下命令：

```bash
cp .env.example .env
```

Windows PowerShell（复制示例）：

```powershell
Copy-Item backend\.env.example backend\.env
```

如当前目录已位于 `backend/`，使用以下命令：

```powershell
Copy-Item .env.example .env
```

Linux/macOS/WSL（在当前终端加载环境变量）：

```bash
set -a
source backend/.env
set +a
```

如当前目录已位于 `backend/`，使用以下命令：

```bash
set -a
source .env
set +a
```

### 3.5 启动后端服务

Linux/macOS/WSL（推荐）：使用脚本启动（自动创建 venv、安装依赖，**并自动加载 `backend/.env`（如存在）**，默认以 `0.0.0.0:8000` 启动服务）。

```bash
./backend/scripts/start-backend.sh
```

如提示 `Permission denied`，执行以下命令后重试：

```bash
chmod +x ./backend/scripts/start-backend.sh
```

Windows：`backend/scripts/start-backend.sh` 依赖 Bash 且默认使用 gunicorn，通常不适用于原生 Windows 环境；使用 Django 开发服务器启动。

Windows PowerShell：

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000
```

Windows CMD：

```bat
cd backend
venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
```

## 4. 初始化“项目批次”（推荐）

很多页面会读取“当前批次”（`GET /api/v1/system-settings/batches/current/`），如未创建批次，返回值可能为 `null`。

如 `dachuang_db_full.sql` 已包含批次数据，可跳过本节。

如需手动创建批次：使用 `LEVEL1_ADMIN` 账号登录后创建批次。

Linux/macOS/WSL（curl 示例）：

```bash
# 1) 登录（注意 role）；响应中的 token 位于 data.access_token
curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"employee_id":"admin","password":"admin123456","role":"level1_admin"}'
```

将返回 JSON 中的 `data.access_token` 替换下方命令中的 `<TOKEN>` 后创建批次：

```bash
# 2) 创建批次
curl -s -X POST http://localhost:8000/api/v1/system-settings/batches/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H 'Content-Type: application/json' \
  -d '{"name":"2026年大创","year":2026,"code":"2026","status":"active"}'
```

Windows PowerShell（Invoke-RestMethod 示例）：

```powershell
$login = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/auth/login/" -ContentType "application/json" -Body '{"employee_id":"admin","password":"admin123456","role":"level1_admin"}'
$token = $login.data.access_token
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/system-settings/batches/" -ContentType "application/json" -Headers @{ Authorization = "Bearer $token" } -Body '{"name":"2026年大创","year":2026,"code":"2026","status":"active"}'
```

说明：

- `status` 可用值见后端模型 `backend/apps/system_settings/models.py`（常用：`draft` / `active` / `finished` / `archived`）。
- 当 `status=active` 时会自动设为当前批次（`is_current=true`）。

## 5. 启动前端（Vue + Vite）

### 5.1 安装依赖（首次必做）

```bash
cd frontend
npm ci
```

如需使用 `npm install` 亦可，但推荐使用 `npm ci` 以保持 lockfile 一致。

### 5.2（可选）配置后端地址

默认开发环境使用 `http://localhost:8000`，无需额外配置。

如需改成其他地址，可在 `frontend/.env.development.local` 写入：

```bash
VITE_API_BASE_URL=http://localhost:8000
```

### 5.3 启动前端

```bash
npm run dev
```

访问：

- 前端：`http://localhost:3000`
- 后端：`http://localhost:8000`

## 6. 常见问题（排错）

### 6.1 后端连不上数据库

典型报错：`connection refused` / `password authentication failed`。

检查顺序：

1. PostgreSQL 是否启动、端口是否正确（默认 `5432`）
2. 数据库是否存在：`dachuang_db`
3. 用户/密码是否匹配（默认 `postgres/123456`）
4. 如修改了数据库主机/端口/账号信息，需同步修改 `backend/config/settings.py`

### 6.2 `psql` 命令不可用

现象：终端提示找不到 `psql`。

处理：

- 安装 PostgreSQL 客户端工具（或完整 PostgreSQL）
- 确保 `psql` 已加入系统 `PATH`

### 6.3 `start-backend.sh` 无法执行

现象：提示 `Permission denied` 或无法识别脚本文件。

处理：

- Linux/macOS/WSL：执行 `chmod +x ./backend/scripts/start-backend.sh` 后重试，或使用 `bash ./backend/scripts/start-backend.sh`
- Windows：按 `4.5` 使用 `python manage.py runserver` 启动

### 6.4 登录失败（学号/工号或密码错误 / role_mismatch）

登录接口只接受 `employee_id` + `password`：

- 确认账号的 `employee_id` 存在
- 确认密码正确
- `role` 参数必须与账号 `role` 匹配（示例：一级管理员用 `role=level1_admin`）

### 6.5 pip 安装依赖失败（lxml / pillow 等编译问题）

在某些系统上如果没有对应 wheel，可能需要系统依赖（示例）：

- Ubuntu/Debian：`sudo apt-get install -y build-essential python3-dev libxml2-dev libxslt1-dev zlib1g-dev libjpeg-dev`

### 6.6 端口被占用

- 后端默认 `8000`，前端默认 `3000`，PostgreSQL 默认 `5432`
- 修改后端端口：自行调整启动命令/脚本
- 修改前端端口：`frontend/vite.config.ts` 的 `server.port`

### 6.7 需要“重置”本地数据

如需回到“干净状态”：

- 数据库：删除并重建数据库 `dachuang_db`，或使用新的数据库名并同步修改 `backend/config/settings.py`
- 后端迁移：数据库清空后重新执行 `python manage.py migrate`
- 管理员账号：重新用 `python manage.py shell` 创建
