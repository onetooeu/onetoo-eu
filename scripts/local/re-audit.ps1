# ONETOO re-audit (read-only) - PowerShell
# Checks deploy marker + sha256 inventory on both domains, then probes search.onetoo.eu (expected 404).
$ErrorActionPreference = "Stop"

function CB { return [int][double]::Parse((Get-Date -UFormat %s)) }

function Fetch([string]$Url) {
  return (Invoke-WebRequest -UseBasicParsing -Uri $Url).Content
}

Write-Host "=== (1) deploy markers ==="
$hosts = @("https://onetoo-eu.pages.dev", "https://www.onetoo.eu")
foreach ($h in $hosts) {
  $u = "$h/.well-known/deploy.txt?cb=$(CB)"
  Write-Host "--- $u"
  $c = Fetch $u
  ($c -split "`n" | Select-Object -First 6) -join "`n" | Write-Host
}

Write-Host ""
Write-Host "=== (2) sha256.json (commit line) ==="
foreach ($h in $hosts) {
  $u = "$h/.well-known/sha256.json?cb=$(CB)"
  Write-Host "--- $u"
  $c = Fetch $u
  ($c -split "`n" | Select-String '"commit"' | Select-Object -First 1).Line | Write-Host
}

Write-Host ""
Write-Host "=== (3) search.onetoo.eu check (expected 404) ==="
$paths = @("/", "/health", "/openapi.json", "/.well-known/ai-search.json")
foreach ($p in $paths) {
  $u = "https://search.onetoo.eu$p?cb=$(CB)"
  try {
    $resp = Invoke-WebRequest -UseBasicParsing -Uri $u -Method GET
    Write-Host "$u -> HTTP $($resp.StatusCode)"
  } catch {
    if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
      $code = [int]$_.Exception.Response.StatusCode
      Write-Host "$u -> HTTP $code"
    } else {
      Write-Host "$u -> ERROR"
    }
  }
}

Write-Host ""
Write-Host "OK: re-audit script finished."
