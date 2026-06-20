$ErrorActionPreference = "Stop"

# Start the full local development stack on Windows.
# The backend and frontend run in separate PowerShell windows so each log stays readable.

$rootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$backendLauncher = Join-Path $rootDir "backend\scripts\start-backend.ps1"
$frontendDir = Join-Path $rootDir "frontend"
$packageJson = Join-Path $frontendDir "package.json"
$packageLock = Join-Path $frontendDir "package-lock.json"
$nodeModulesDir = Join-Path $frontendDir "node_modules"
$frontendDepsMarker = Join-Path $nodeModulesDir ".deps-installed"

function Assert-PathExists {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(Mandatory = $true)][string]$Description
  )

  if (-not (Test-Path $Path)) {
    throw "$Description not found: $Path"
  }
}

function Wait-HttpReady {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$Url,
    [int]$TimeoutSeconds = 90
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  $lastError = $null

  while ((Get-Date) -lt $deadline) {
    try {
      $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
      if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
        Write-Host "$Name is ready: $Url"
        return
      }
    } catch {
      $lastError = $_.Exception.Message
      $statusCode = $null
      if ($_.Exception.Response) {
        try {
          $statusCode = [int]$_.Exception.Response.StatusCode
        } catch {
          $statusCode = $null
        }
      }
      if ($statusCode -ge 200 -and $statusCode -lt 500) {
        Write-Host "$Name is ready: $Url"
        return
      }
    }

    Start-Sleep -Seconds 2
  }

  throw "$Name did not become ready within $TimeoutSeconds seconds at $Url. Last error: $lastError"
}

function Install-FrontendDependencies {
  $needsInstall = -not (Test-Path $nodeModulesDir)

  if (-not $needsInstall -and (Test-Path $packageLock)) {
    if (
      (-not (Test-Path $frontendDepsMarker)) -or
      ((Get-Item $packageLock).LastWriteTimeUtc -gt (Get-Item $frontendDepsMarker).LastWriteTimeUtc)
    ) {
      $needsInstall = $true
    }
  }

  if (-not $needsInstall) {
    Write-Host "Frontend dependencies are already installed."
    return
  }

  Write-Host "Installing frontend dependencies..."
  Push-Location $frontendDir
  try {
    npm install
    New-Item -ItemType File -Force -Path $frontendDepsMarker | Out-Null
  } finally {
    Pop-Location
  }
}

function ConvertTo-EncodedPowerShellCommand {
  param([Parameter(Mandatory = $true)][string]$Command)

  return [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Command))
}

Assert-PathExists -Path $backendLauncher -Description "Backend launcher"
Assert-PathExists -Path $frontendDir -Description "Frontend directory"
Assert-PathExists -Path $packageJson -Description "Frontend package.json"
Assert-PathExists -Path $packageLock -Description "Frontend package-lock.json"

Write-Host "Starting Dachuang-MS development stack..."
Write-Host "Project root: $rootDir"

Install-FrontendDependencies

$backendCommand = "& '$backendLauncher'"
$frontendCommand = "Set-Location '$frontendDir'; npm run dev"
$backendEncodedCommand = ConvertTo-EncodedPowerShellCommand -Command $backendCommand
$frontendEncodedCommand = ConvertTo-EncodedPowerShellCommand -Command $frontendCommand

Start-Process powershell -ArgumentList @(
  "-NoProfile",
  "-ExecutionPolicy", "Bypass",
  "-NoExit",
  "-EncodedCommand", $backendEncodedCommand
) -WorkingDirectory $rootDir

Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList @(
  "-NoProfile",
  "-ExecutionPolicy", "Bypass",
  "-NoExit",
  "-EncodedCommand", $frontendEncodedCommand
) -WorkingDirectory $frontendDir

Write-Host "Waiting for backend and frontend..."
Wait-HttpReady -Name "Backend" -Url "http://localhost:8000" -TimeoutSeconds 120
Wait-HttpReady -Name "Frontend" -Url "http://localhost:3000" -TimeoutSeconds 120

Write-Host "Opening browser: http://localhost:3000"
Start-Process "http://localhost:3000"
Write-Host "Dachuang-MS is running."
