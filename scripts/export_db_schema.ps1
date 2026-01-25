param(
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Defaults align with backend/config/settings.py (and scripts/export_db_schema.sh)
$dbName = if ($env:DB_NAME) { $env:DB_NAME } else { "dachuang_db" }
$dbUser = if ($env:DB_USER) { $env:DB_USER } else { "postgres" }
$dbPassword = if ($env:DB_PASSWORD) { $env:DB_PASSWORD } else { "123456" }
$dbHost = if ($env:DB_HOST) { $env:DB_HOST } else { "localhost" }
$dbPort = if ($env:DB_PORT) { $env:DB_PORT } else { "5432" }

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$outputFile = if ($env:OUTPUT_FILE) { $env:OUTPUT_FILE } else { (Join-Path $repoRoot "dachuang_db_schema.sql") }

$pgDump = Get-Command pg_dump -ErrorAction SilentlyContinue
if (-not $pgDump) {
  $msg = "pg_dump is not available in PATH. Please install PostgreSQL client tools and add its bin directory to PATH."
  if ($DryRun) {
    Write-Host $msg
    exit 0
  }
  throw $msg
}

$outputDir = Split-Path -Parent $outputFile
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$args = @(
  "--host", $dbHost,
  "--port", $dbPort,
  "--username", $dbUser,
  "--schema-only",
  "--format=plain",
  "--file", $outputFile,
  $dbName
)

if ($DryRun) {
  Write-Host "Dry run. Would execute:"
  $prettyArgs = $args | ForEach-Object { if ($_ -match "\\s") { '"' + $_ + '"' } else { $_ } }
  Write-Host ("pg_dump " + ($prettyArgs -join " "))
  exit 0
}

$oldPgPassword = $env:PGPASSWORD
try {
  $env:PGPASSWORD = $dbPassword
  & $pgDump.Source @args
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally {
  if ($null -eq $oldPgPassword) { Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue }
  else { $env:PGPASSWORD = $oldPgPassword }
}

Write-Host "Exported schema to $outputFile"
