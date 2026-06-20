@echo off
setlocal

REM One-click Windows launcher for the full local development stack.
REM Opens backend and frontend servers in separate PowerShell windows.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-dev.ps1"

echo.
echo Press any key to close this launcher window.
pause >nul
