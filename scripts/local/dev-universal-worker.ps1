\
    Param()

    # Local dev helper for ONETOO Universal Worker
    # Usage: powershell -ExecutionPolicy Bypass -File scripts/local/dev-universal-worker.ps1

    $ErrorActionPreference = "Stop"

    $root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
    $workerDir = Join-Path $root "worker\onetoo-universal"

    if (-not (Get-Command wrangler -ErrorAction SilentlyContinue)) {
      Write-Error "wrangler not found. Install: npm i -g wrangler"
      exit 1
    }

    Set-Location $workerDir
    Write-Host "[dev] cwd: $workerDir"
    Write-Host "[dev] starting wrangler dev ..."
    wrangler dev
