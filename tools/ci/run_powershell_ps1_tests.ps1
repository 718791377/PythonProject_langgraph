[CmdletBinding()]
param(
  [string]$Root = '.',
  [string]$Manifest = 'tools/ci/ci_test_manifest.json'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Root).Path)
$testRoot = Join-Path $repoRoot 'test'
$manifestPath = Join-Path $repoRoot $Manifest
$manifestPayload = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$testFiles = @()
foreach ($name in @($manifestPayload.powershell_ps1)) {
  $testPath = Join-Path $testRoot ([string]$name)
  if (-not (Test-Path -LiteralPath $testPath)) {
    throw "Missing PowerShell test file: $testPath"
  }
  $testFiles += Get-Item -LiteralPath $testPath
}
$currentPowerShell = (Get-Process -Id $PID).Path

foreach ($testFile in $testFiles) {
  & $currentPowerShell -NoProfile -ExecutionPolicy Bypass -File $testFile.FullName
  if ($LASTEXITCODE -ne 0) {
    throw "PowerShell test failed: $($testFile.FullName)"
  }
}

Write-Host ("powershell_ps1_tests: ok ({0} files)" -f $testFiles.Count)
