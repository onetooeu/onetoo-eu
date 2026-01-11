Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..\..\worker\onetoo-universal")
Write-Host "== dev: onetoo-universal =="
wrangler dev
