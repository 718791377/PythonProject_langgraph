[CmdletBinding()]
param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string]$Module,
  [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }),
  [int]$MaxFiles = 12,
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
$property = @($profiles.modules.PSObject.Properties | Where-Object { $_.Name -eq $Module } | Select-Object -First 1)
if (-not $property) {
  $known = (@($profiles.modules.PSObject.Properties) | ForEach-Object { $_.Name }) -join ', '
  throw "Unknown plugin module '$Module'. Known modules: $known"
}

$entry = $property[0].Value
$codexHomePath = [System.IO.Path]::GetFullPath($CodexHome)
$resolved = New-Object System.Collections.Generic.List[string]
$missing = New-Object System.Collections.Generic.List[string]
$totalMatches = 0

foreach ($hint in @($entry.soft_load.skill_doc_hints)) {
  if ([string]::IsNullOrWhiteSpace([string]$hint)) { continue }
  $pattern = [string]$hint
  if (-not [System.IO.Path]::IsPathRooted($pattern)) {
    $pattern = Join-Path $codexHomePath $pattern
  }
  $matches = @(Get-ChildItem -Path $pattern -File -ErrorAction SilentlyContinue | Sort-Object FullName)
  if ($matches.Count -eq 0) {
    $missing.Add([string]$hint) | Out-Null
    continue
  }
  $totalMatches += $matches.Count
  foreach ($match in $matches) {
    if ($resolved.Count -lt $MaxFiles) {
      $resolved.Add($match.FullName) | Out-Null
    }
  }
}

$plugins = $entry.plugins
if ($plugins -is [string] -and $plugins -eq 'all_known_plugins') {
  $plugins = @($profiles.known_plugins)
} elseif ($plugins -is [string]) {
  $plugins = @($plugins)
}

$payload = [ordered]@{
  module = $Module
  mode = 'soft-load'
  codex_home = $codexHomePath
  description = [string]$entry.description
  plugins = @($plugins)
  use_for = @($entry.soft_load.use_for)
  skill_docs = @($resolved)
  omitted_after_max_files = [Math]::Max(0, $totalMatches - $resolved.Count)
  missing_hints = @($missing)
  notes = @($entry.soft_load.notes)
  instructions = @(
    'Read only the returned skill_docs relevant to the current user task.',
    'Soft-load does not edit config.toml and does not add omitted skills back to the startup-visible list.',
    'If live plugin tools or startup-visible skills are required, preview set_plugin_profile.ps1 and apply only after operator approval.'
  )
}

if ($Json) {
  $payload | ConvertTo-Json -Depth 32
  return
}

Write-Output ("Plugin module: {0}" -f $payload.module)
Write-Output $payload.description
Write-Output ("Plugins: {0}" -f (($payload.plugins) -join ', '))
Write-Output 'Skill docs to read:'
foreach ($path in $payload.skill_docs) { Write-Output ("  - {0}" -f $path) }
if ($payload.missing_hints.Count -gt 0) {
  Write-Output 'Missing hints:'
  foreach ($hint in $payload.missing_hints) { Write-Output ("  - {0}" -f $hint) }
}
Write-Output 'Notes:'
foreach ($note in $payload.notes) { Write-Output ("  - {0}" -f $note) }
