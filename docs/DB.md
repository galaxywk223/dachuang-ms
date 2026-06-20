# 数据库文件与数据库配置说明（PostgreSQL）

后端使用 PostgreSQL。仓库根目录仅保留数据库结构文件：

- `dachuang_db_schema.sql`：仅数据库结构，用于从空数据开始初始化。

完整数据导出属于本地运行数据，默认写入 `.local/db/local_data.sql`，不纳入版本控制。

## 1. 初始化方式

### 1.1 导入结构文件

适用场景：全新环境初始化、迁移验证、生产或准生产环境部署前建表。

Windows PowerShell：

```powershell
$env:PGPASSWORD="<local-db-password>"
psql -h localhost -p 5432 -U <local-db-user> -d dachuang_db -f .\dachuang_db_schema.sql
Remove-Item Env:PGPASSWORD
```

Linux/macOS/WSL：

```bash
export PGPASSWORD='<local-db-password>'
psql -h localhost -p 5432 -U <local-db-user> -d dachuang_db -f ./dachuang_db_schema.sql
unset PGPASSWORD
```

结构导入完成后，后端迁移命令负责补齐当前代码版本的迁移状态：

```powershell
cd backend
python manage.py migrate
```

### 1.2 导入本地完整数据文件

适用场景：本地演示数据恢复、课程演示环境复制、调试现场复现。

完整数据文件路径：

```text
.local/db/local_data.sql
```

Windows PowerShell：

```powershell
$env:PGPASSWORD="<local-db-password>"
psql -h localhost -p 5432 -U <local-db-user> -d dachuang_db -f .\.local\db\local_data.sql
Remove-Item Env:PGPASSWORD
```

Linux/macOS/WSL：

```bash
export PGPASSWORD='<local-db-password>'
psql -h localhost -p 5432 -U <local-db-user> -d dachuang_db -f ./.local/db/local_data.sql
unset PGPASSWORD
```

完整数据导入会覆盖目标库中的同名对象和数据。该文件可能包含登录凭据、联系信息、项目材料路径等敏感内容，因此不提交到 Git。

## 2. 后端数据库配置

后端数据库连接配置位于 `backend/config/settings.py`，并支持环境变量覆盖：

- `DB_NAME`：默认 `dachuang_db`
- `DB_USER`：本地数据库用户
- `DB_PASSWORD`：本地数据库密码
- `DB_HOST`：默认 `localhost`
- `DB_PORT`：默认 `5432`

环境变量文件模板为 `backend/.env.example`。实际配置文件 `backend/.env` 已被 `.gitignore` 忽略。

## 3. 常见问题

### 3.1 psql/pg_dump 命令找不到

PostgreSQL 客户端工具需要安装并加入 `PATH`。可执行文件通常位于 PostgreSQL 安装目录的 `bin` 子目录。

### 3.2 连接失败或密码错误

排查项：

- PostgreSQL 服务状态。
- `DB_HOST` 与 `DB_PORT`。
- `DB_USER` 与 `DB_PASSWORD`。
- 目标数据库 `DB_NAME` 是否已创建。

## 4. 重新导出 SQL

Windows PowerShell：

```powershell
# 导出结构到 dachuang_db_schema.sql
.\scripts\export_db_schema.ps1

# 导出完整数据到 .local/db/local_data.sql
.\scripts\export_db_full.ps1
```

Bash：

```bash
./scripts/export_db_schema.sh
./scripts/export_db_full.sh
```

可用环境变量：

- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `OUTPUT_FILE`

`OUTPUT_FILE` 可覆盖输出路径。完整数据导出路径应保持在 `.local/`、临时目录或其他未纳入版本控制的位置。
`DB_PASSWORD` 必须由本地环境显式提供。
