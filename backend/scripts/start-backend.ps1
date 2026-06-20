$ErrorActionPreference = "Stop"

# Start the Django backend on 0.0.0.0:8000 (Windows PowerShell),
# creating the venv and installing dependencies if they are missing.

$rootDir = Resolve-Path (Join-Path $PSScriptRoot "..\\..")
$backendDir = Join-Path $rootDir "backend"
$venvDir = Join-Path $backendDir "venv"

Set-Location $backendDir

$pythonExe = Join-Path $venvDir "Scripts\\python.exe"
if (-not (Test-Path $pythonExe)) {
  if (Test-Path $venvDir) {
    Remove-Item -Recurse -Force $venvDir
  }
  python -m venv $venvDir
}

. (Join-Path $venvDir "Scripts\\Activate.ps1")

$depsMarker = Join-Path $venvDir ".deps-installed"
$requirementsFile = Join-Path $backendDir "requirements.txt"
if (
  (-not (Test-Path $depsMarker)) -or
  ((Get-Item $requirementsFile).LastWriteTimeUtc -gt (Get-Item $depsMarker).LastWriteTimeUtc)
) {
  pip install -U pip
  pip install -r $requirementsFile
  New-Item -ItemType File -Force -Path $depsMarker | Out-Null
}

# Load environment variables from backend/.env (optional).
$dotenvPath = Join-Path $backendDir ".env"
if (Test-Path $dotenvPath) {
  Get-Content $dotenvPath | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) { return }
    $match = [regex]::Match($line, "^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$")
    if (-not $match.Success) { return }

    $key = $match.Groups[1].Value
    $value = $match.Groups[2].Value.Trim()
    if (
      ($value.Length -ge 2) -and
      (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'")))
    ) {
      $value = $value.Substring(1, $value.Length - 2)
    }

    Set-Item -Path "env:$key" -Value $value
  }
}

# Ensure default local data dirs exist (matches backend/config/settings.py defaults).
$localDataDir = Join-Path $rootDir ".local\\backend"
$defaultLogDir = Join-Path $localDataDir "logs"
$defaultMediaDir = Join-Path $localDataDir "media"
New-Item -ItemType Directory -Force -Path $defaultLogDir | Out-Null
New-Item -ItemType Directory -Force -Path $defaultMediaDir | Out-Null

if (-not $env:DJANGO_LOG_DIR) { $env:DJANGO_LOG_DIR = $defaultLogDir }
if (-not $env:DJANGO_MEDIA_ROOT) { $env:DJANGO_MEDIA_ROOT = $defaultMediaDir }

# Some Windows setups can accidentally mark the log file as read-only.
$debugLog = Join-Path $env:DJANGO_LOG_DIR "debug.log"
if (Test-Path $debugLog) {
  try { attrib -R $debugLog | Out-Null } catch { }
}

$bind = $env:DJANGO_RUNSERVER_ADDR
if (-not $bind) { $bind = "0.0.0.0:8000" }

# Gunicorn is not supported on native Windows; default to Django's dev server.
$serverMode = $env:DJANGO_SERVER_MODE
if (-not $serverMode) { $serverMode = "runserver" }
if ($serverMode -ne "runserver") {
  Write-Host "DJANGO_SERVER_MODE=$serverMode is not supported on native Windows; falling back to runserver."
}

python manage.py runserver $bind

