@echo off
setlocal

REM One-click Windows launcher for the backend (PowerShell).
REM Keeps the current console open so you can see logs and stop with Ctrl+C.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-backend.ps1"

