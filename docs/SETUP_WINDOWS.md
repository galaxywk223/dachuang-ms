# Windows 一键启动

`start-dev.cmd` 用于原生 Windows 环境启动完整开发服务。脚本会分别打开后端和前端窗口，等待服务可用后打开浏览器。

`backend/scripts/start-backend.ps1` 仍可单独启动后端服务。Linux、macOS、WSL 环境使用 `backend/scripts/start-backend.sh`。

## 启动命令

项目根目录执行以下命令：

```bat
start-dev.cmd
```

PowerShell 也可直接运行：

```powershell
.\scripts\start-dev.ps1
```

PowerShell 当前会话阻止脚本执行时，使用以下命令临时放开执行策略：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\start-dev.ps1
```

后端单独启动可使用：

```bat
backend\scripts\start-backend.cmd
```

## 脚本行为

- `start-dev.cmd` 会调用 `scripts/start-dev.ps1`。
- 后端服务在独立 PowerShell 窗口运行。
- 前端服务在独立 PowerShell 窗口运行。
- 前端依赖缺失或 `package-lock.json` 更新后自动执行 `npm install`。
- 后端和前端可访问后自动打开 `http://localhost:3000`。
- `backend/venv` 不存在时自动创建虚拟环境。
- `backend/requirements.txt` 更新后自动安装依赖。
- `backend/.env` 存在时自动加载环境变量。
- Django 开发服务器默认绑定 `0.0.0.0:8000`。
- Vite 开发服务器默认绑定 `localhost:3000`。
- 本地日志和上传目录默认写入 `.local/backend/`。

## 配置项

- `DJANGO_RUNSERVER_ADDR`：服务绑定地址，默认值为 `0.0.0.0:8000`。
- `DJANGO_SERVER_MODE`：原生 Windows 环境忽略该配置，固定使用 `runserver`。
