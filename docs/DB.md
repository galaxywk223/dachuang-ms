# 数据库文件与数据库配置说明（PostgreSQL）

本项目后端使用 PostgreSQL，仓库根目录提供了两份 SQL：

- `dachuang_db_full.sql`：**数据库结构 + 测试数据**（用于“开箱即用”快速初始化）
- `dachuang_db_schema.sql`：**仅数据库结构**（用于从空数据开始）

## 1. 初始化方式

### 方式 A：导入 `dachuang_db_full.sql`（推荐）

适合课程演示/快速跑通业务流程。

Windows PowerShell：

```powershell
# 先确保已创建数据库 dachuang_db
$env:PGPASSWORD="123456"
psql -h localhost -p 5432 -U postgres -d dachuang_db -f .\dachuang_db_full.sql
```

Linux/macOS/WSL：

```bash
export PGPASSWORD='123456'
psql -h localhost -p 5432 -U postgres -d dachuang_db -f ./dachuang_db_full.sql
unset PGPASSWORD
```

说明：

- `dachuang_db_full.sql` 由 `pg_dump` 导出，通常包含清理同名对象的语句；导入到目标库会覆盖同名表/视图等对象。

### 方式 B：导入 `dachuang_db_schema.sql`

适合希望“从 0 开始”自行录入数据或通过接口生成初始数据。

Windows PowerShell：

```powershell
$env:PGPASSWORD="123456"
psql -h localhost -p 5432 -U postgres -d dachuang_db -f .\dachuang_db_schema.sql
```

导入完成后，建议在后端执行一次迁移：

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py migrate
```

## 2. 后端数据库配置（连接信息）

后端数据库连接配置位于 `backend/config/settings.py`，并支持通过环境变量覆盖：

- `DB_NAME`（默认 `dachuang_db`）
- `DB_USER`（默认 `postgres`）
- `DB_PASSWORD`（默认 `123456`）
- `DB_HOST`（默认 `localhost`）
- `DB_PORT`（默认 `5432`）

推荐做法：复制 `backend/.env.example` 为 `backend/.env` 并按需修改（`backend/.env` 已被 `.gitignore` 忽略，不会提交）。

## 3. 常见问题

### 3.1 psql/pg_dump 命令找不到

请确认 PostgreSQL 已安装，并将 PostgreSQL 的 `bin` 目录加入 PATH（或使用安装目录下的 `psql.exe` / `pg_dump.exe` 的绝对路径）。

### 3.2 连接失败/密码错误

请核对：

- PostgreSQL 服务是否启动
- `DB_HOST/DB_PORT` 是否正确
- `DB_USER/DB_PASSWORD` 是否与本机实际账号一致

## 4. （可选）重新导出 SQL（Windows）

如你在本机修改了数据库，想重新导出 SQL 文件，可使用仓库自带的 Windows 脚本：

```powershell
# 导出“结构 + 数据”
.\scripts\export_db_full.ps1

# 仅导出结构
.\scripts\export_db_schema.ps1
```

可用环境变量覆盖连接与输出路径（与后端一致）：

- `DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT`
- `OUTPUT_FILE`：输出文件路径（默认分别为根目录的 `dachuang_db_full.sql` / `dachuang_db_schema.sql`）
