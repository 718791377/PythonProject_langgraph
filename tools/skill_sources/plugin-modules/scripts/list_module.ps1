[CmdletBinding()]
param(
  [Alias('Name')]
  [string]$Module,
  [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$skillRoot = Split-Path -Parent $PSScriptRoot
$profilesPath = Join-Path $skillRoot 'references\profiles.json'
if (-not (Test-Path -LiteralPath $profilesPath)) {
  throw "Missing profiles registry: $profilesPath"
}

$profiles = Get-Content -LiteralPath $profilesPath -Raw -Encoding UTF8 | ConvertFrom-Json
$moduleProperties = @($profiles.modules.PSObject.Properties)

function ConvertTo-ModuleSummary {
  param($Property)
  $entry = $Property.Value
  $plugins = $entry.plugins
  if ($plugins -is [string]) { $plugins = @($plugins) }
  [ordered]@{
    name = [string]$Property.Name
    description = [string]$entry.description
    plugins = @($plugins)
    hard_load_disables_other_known_plugins = [bool]$entry.hard_load.disable_other_known_plugins
    soft_load_hint_count = @($entry.soft_load.skill_doc_hints).Count
  }
}

if (-not [string]::IsNullOrWhiteSpace($Module)) {
  $match = $moduleProperties | Where-Object { $_.Name -eq $Module } | Select-Object -First 1
  if ($null -eq $match) {
    $known = ($moduleProperties | ForEach-Object { $_.Name }) -join ', '
    throw "Unknown plugin module '$Module'. Known modules: $known"
  }
  $payload = ConvertTo-ModuleSummary -Property $match
} else {
  $payload = @($moduleProperties | ForEach-Object { ConvertTo-ModuleSummary -Property $_ })
}

if ($Json) {
  $payload | ConvertTo-Json -Depth 16
  return
}

if ($payload -is [array]) {
  foreach ($item in $payload) {
    Write-Output ("{0}: {1}" -f $item.name, $item.description)
    Write-Output ("  plugins: {0}" -f (($item.plugins) -join ', '))
  }
} else {
  Write-Output ("{0}: {1}" -f $payload.name, $payload.description)
  Write-Output ("plugins: {0}" -f (($payload.plugins) -join ', '))
  Write-Output ("soft-load hints: {0}" -f $payload.soft_load_hint_count)
}
