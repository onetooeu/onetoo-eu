param(
  [Parameter(Mandatory=$true)]
  [string]$KeyPath,
  [string]$RootPath = (Resolve-Path ".").Path,
  [string]$MinisignPath = "minisign",
  [switch]$SignTargets
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host ("[onetoo-sign] " + $msg) }

function Get-RelPath($full, $base) {
  $u1 = New-Object System.Uri(($base.TrimEnd('\') + '\'))
  $u2 = New-Object System.Uri($full)
  $rel = $u1.MakeRelativeUri($u2).ToString().Replace('/', '\')
  return $rel
}

$RootPath = (Resolve-Path $RootPath).Path
$dumps = Join-Path $RootPath "dumps"
$sigs  = Join-Path $dumps "sigs"
New-Item -ItemType Directory -Force -Path $sigs | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $sigs "targets") | Out-Null

Write-Info "RootPath = $RootPath"
Write-Info "Using minisign = $MinisignPath"
Write-Info "KeyPath = $KeyPath"

# 1) Generate dumps/sha256.json (static-first integrity dump)
Write-Info "Generating dumps\sha256.json ..."
$files = Get-ChildItem -Path $RootPath -File -Recurse |
  Where-Object {
    $_.FullName -notmatch '\\\.git\\' -and
    $_.FullName -notmatch '\\node_modules\\' -and
    $_.FullName -notmatch '\\\.wrangler\\' -and
    $_.FullName -notmatch '\\dumps\\sigs\\' -and
    $_.FullName -notmatch '\\\.github\\' # workflows are signed separately in git
  }

$items = @()
foreach ($f in $files) {
  $rel = (Get-RelPath $f.FullName $RootPath).Replace('\','/')
  $hash = (Get-FileHash -Algorithm SHA256 -Path $f.FullName).Hash.ToLowerInvariant()
  $items += [PSCustomObject]@{ path = "/" + $rel; sha256 = $hash; bytes = $f.Length }
}

$sha256 = [PSCustomObject]@{
  version = "1.0"
  generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  count = $items.Count
  files = $items
}

$sha256Path = Join-Path $dumps "sha256.json"
$sha256 | ConvertTo-Json -Depth 6 | Out-File -Encoding utf8 $sha256Path

# 2) Generate dumps/targets.json (pinned trust surfaces)
Write-Info "Generating dumps\targets.json ..."
$targetList = @(
  "/.well-known/ai-trust-hub.json",
  "/.well-known/llms.txt",
  "/.well-known/minisign.pub",
  "/api/v1/index.json",
  "/api/v1/openapi.json",
  "/dumps/release.json",
  "/dumps/sha256.json",
  "/dumps/targets.json",
  "/status.json",
  "/contract.md"
)

$targetObjs = @()
foreach ($p in $targetList) {
  $local = Join-Path $RootPath ($p.TrimStart("/") -replace '/', '\')
  if (-not (Test-Path $local)) {
    Write-Warning "Target missing on disk: $p"
    continue
  }
  $h = (Get-FileHash -Algorithm SHA256 -Path $local).Hash.ToLowerInvariant()
  $targetObjs += [PSCustomObject]@{ path = $p; sha256 = $h }
}

$targets = [PSCustomObject]@{
  version = "1.0"
  generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  targets = $targetObjs
}

$targetsPath = Join-Path $dumps "targets.json"
$targets | ConvertTo-Json -Depth 6 | Out-File -Encoding utf8 $targetsPath

# 3) Sign official artifacts
Write-Info "Signing dumps\sha256.json -> dumps\sigs\sha256.json.minisig"
& $MinisignPath -S -s $KeyPath -m $sha256Path -x (Join-Path $sigs "sha256.json.minisig")

Write-Info "Signing dumps\targets.json -> dumps\sigs\targets.json.minisig"
& $MinisignPath -S -s $KeyPath -m $targetsPath -x (Join-Path $sigs "targets.json.minisig")

if ($SignTargets) {
  Write-Info "Signing each target to dumps\sigs\targets\*.minisig ..."
  foreach ($t in $targetObjs) {
    $p = $t.path
    $local = Join-Path $RootPath ($p.TrimStart("/") -replace '/', '\')
    $out = Join-Path (Join-Path $sigs "targets") ((($p.TrimStart("/")) -replace '/', '__') + ".minisig")
    & $MinisignPath -S -s $KeyPath -m $local -x $out
  }
}

Write-Info "Done. Verify with: minisign -V -p .well-known\minisign.pub -m dumps\sha256.json -x dumps\sigs\sha256.json.minisig"
