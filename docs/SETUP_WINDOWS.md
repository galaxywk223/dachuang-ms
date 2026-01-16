# Windows one-click backend start

This repo already ships a Linux/macOS/WSL launcher at `backend/scripts/start-backend.sh`.
For native Windows, use the PowerShell launcher below.

## Start (recommended)

From the repo root:

```powershell
.\backend\scripts\start-backend.ps1
```

If PowerShell blocks running scripts in your terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\backend\scripts\start-backend.ps1
```

Or run the CMD wrapper (double-clickable):

```bat
backend\scripts\start-backend.cmd
```

## What it does

- Creates `backend/venv` if missing
- Installs `backend/requirements.txt` when needed
- Loads `backend/.env` into environment variables (optional)
- Starts Django dev server on `0.0.0.0:8000`

## Configuration

- `DJANGO_RUNSERVER_ADDR`: bind address, default `0.0.0.0:8000`
- `DJANGO_SERVER_MODE`: ignored on native Windows (always uses `runserver`)
