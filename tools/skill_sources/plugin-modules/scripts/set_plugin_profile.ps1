[CmdletBinding()]
param(
  [Parameter(Position = 0)]
  [string]$Module,
  [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }),
  [string]$ConfigPath,
  [switch]$Apply,
  [switch]$RestoreLatest,
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
$codexHomePath = [System.IO.Path]::GetFullPath($CodexHome)
if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
  $ConfigPath = Join-Path $codexHomePath 'config.toml'
}
$configFile = [System.IO.Path]::GetFullPath($ConfigPath)
$backupRoot = Join-Path $codexHomePath 'backups\plugin-modules-profile'

function Backup-CodexPluginModulesConfig {
  param([string]$Path, [string]$BackupRoot)
  New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
  $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ')
  $backupPath = Join-Path $BackupRoot ("$stamp-config.toml")
  if (Test-Path -LiteralPath $Path) {
    Copy-Item -LiteralPath $Path -Destination $backupPath -Force
  } else {
    Set-Content -LiteralPath $backupPath -Encoding UTF8 -Value "# config.toml was absent before plugin-modules profile apply.`n"
  }
  return $backupPath
}

function Get-LatestPluginModulesBackup {
  param([string]$BackupRoot)
  if (-not (Test-Path -LiteralPath $BackupRoot)) { return $null }
  return Get-ChildItem -LiteralPath $BackupRoot -Filter '*-config.toml' -File | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
}

function Get-TargetMap {
  param($Profiles, [string]$ModuleName)
  $property = @($Profiles.modules.PSObject.Properties | Where-Object { $_.Name -eq $ModuleName } | Select-Object -First 1)
  if (-not $property) {
    $known = (@($Profiles.modules.PSObject.Properties) | ForEach-Object { $_.Name }) -join ', '
    throw "Unknown plugin module '$ModuleName'. Known modules: $known"
  }
  $entry = $property[0].Value
  $enable = $entry.hard_load.enable_plugins
  if ($enable -is [string] -and $enable -eq 'all_known_plugins') {
    $enable = @($Profiles.known_plugins)
  } elseif ($enable -is [string]) {
    $enable = @($enable)
  }
  $map = [ordered]@{}
  foreach ($plugin in @($enable)) { $map[[string]$plugin] = $true }
  if ([bool]$entry.hard_load.disable_other_known_plugins) {
    foreach ($plugin in @($Profiles.known_plugins)) {
      if (-not $map.Contains([string]$plugin)) { $map[[string]$plugin] = $false }
    }
  }
  return [ordered]@{ entry = $entry; target_map = $map }
}

function Update-PluginEnabledToml {
  param([string]$Content, $TargetMap)
  $lines = @(if (-not [string]::IsNullOrEmpty($Content)) { $Content -split "`r?`n", 0, 'RegexMatch' })
  if ($lines.Count -gt 0 -and $lines[-1] -eq '') { $lines = $lines[0..($lines.Count - 2)] }
  $out = New-Object System.Collections.Generic.List[string]
  $seen = @{}
  $currentPlugin = $null
  $currentIsTarget = $false
  $currentHadEnabled = $false

  function Add-MissingEnabledLine {
    param([System.Collections.Generic.List[string]]$OutLines, [string]$Plugin, [bool]$HadEnabled)
    if ($Plugin -and -not $HadEnabled) {
      $value = if ($TargetMap[$Plugin]) { 'true' } else { 'false' }
      $OutLines.Add("enabled = $value") | Out-Null
    }
  }

  foreach ($line in $lines) {
    $sectionMatch = [regex]::Match($line, '^\s*\[plugins\."([^"]+)"\]\s*$')
    $anySectionMatch = [regex]::Match($line, '^\s*\[[^\]]+\]\s*$')
    if ($anySectionMatch.Success) {
      if ($currentIsTarget) {
        Add-MissingEnabledLine -OutLines $out -Plugin $currentPlugin -HadEnabled $currentHadEnabled
      }
      $currentPlugin = $null
      $currentIsTarget = $false
      $currentHadEnabled = $false
      if ($sectionMatch.Success) {
        $candidate = $sectionMatch.Groups[1].Value
        if ($TargetMap.Contains($candidate)) {
          $currentPlugin = $candidate
          $currentIsTarget = $true
          $seen[$candidate] = $true
        }
      }
      $out.Add($line) | Out-Null
      continue
    }
    if ($currentIsTarget -and $line -match '^\s*enabled\s*=') {
      $value = if ($TargetMap[$currentPlugin]) { 'true' } else { 'false' }
      $out.Add("enabled = $value") | Out-Null
      $currentHadEnabled = $true
      continue
    }
    $out.Add($line) | Out-Null
  }

  if ($currentIsTarget) {
    Add-MissingEnabledLine -OutLines $out -Plugin $currentPlugin -HadEnabled $currentHadEnabled
  }

  foreach ($plugin in $TargetMap.Keys) {
    if ($seen.Contains($plugin)) { continue }
    if ($out.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace($out[$out.Count - 1])) { $out.Add('') | Out-Null }
    $escaped = $plugin.Replace('"', '\"')
    $value = if ($TargetMap[$plugin]) { 'true' } else { 'false' }
    $out.Add("[plugins.`"$escaped`"]") | Out-Null
    $out.Add("enabled = $value") | Out-Null
  }

  return (($out -join "`n") + "`n")
}

if ($RestoreLatest) {
  $latest = Get-LatestPluginModulesBackup -BackupRoot $backupRoot
  if ($null -eq $latest) { throw "No plugin-modules config backup found under $backupRoot" }
  $payload = [ordered]@{
    mode = 'restore'
    apply = [bool]$Apply
    config_path = $configFile
    backup_path = $latest.FullName
    restart_instructions = @('Restart Codex with codex-ohmy after restore.', 'To continue an existing thread, use the same resume flow you normally use after starting codex-ohmy.')
  }
  if ($Apply) {
    New-Item -ItemType Directory -Path (Split-Path -Parent $configFile) -Force | Out-Null
    Copy-Item -LiteralPath $latest.FullName -Destination $configFile -Force
  }
  if ($Json) { $payload | ConvertTo-Json -Depth 16 } else { $payload.GetEnumerator() | ForEach-Object { Write-Output ("{0}: {1}" -f $_.Key, ($_.Value -join ', ')) } }
  return
}

if ([string]::IsNullOrWhiteSpace($Module)) {
  $known = (@($profiles.modules.PSObject.Properties) | ForEach-Object { $_.Name }) -join ', '
  throw "Module is required unless -RestoreLatest is used. Known modules: $known"
}

$result = Get-TargetMap -Profiles $profiles -ModuleName $Module
$targetMap = $result.target_map
$currentContent = if (Test-Path -LiteralPath $configFile) { Get-Content -LiteralPath $configFile -Raw -Encoding UTF8 } else { '' }
$newContent = Update-PluginEnabledToml -Content $currentContent -TargetMap $targetMap
$changed = $newContent -ne $currentContent
$backupPath = $null

if ($Apply) {
  New-Item -ItemType Directory -Path (Split-Path -Parent $configFile) -Force | Out-Null
  $backupPath = Backup-CodexPluginModulesConfig -Path $configFile -BackupRoot $backupRoot
  Set-Content -LiteralPath $configFile -Encoding UTF8 -NoNewline -Value $newContent
}

$targets = @($targetMap.Keys | Sort-Object | ForEach-Object { [ordered]@{ plugin = $_; enabled = [bool]$targetMap[$_] } })
$payload = [ordered]@{
  mode = 'hard-load'
  module = $Module
  apply = [bool]$Apply
  changed = [bool]$changed
  config_path = $configFile
  backup_path = $backupPath
  target_plugins = $targets
  safety = [ordered]@{
    backup_before_write = [bool]$Apply
    only_plugin_enabled_keys_changed = $true
    plugin_cache_edited = $false
    direct_mcp_entries_edited = $false
  }
  restart_instructions = @(
    'Restart Codex with codex-ohmy so the startup-visible skills list and plugin tools are recomputed.',
    'To continue an existing thread, use the same resume flow you normally use after starting codex-ohmy.',
    'Use set_plugin_profile.ps1 full -Apply to enable every known plugin, or set_plugin_profile.ps1 -RestoreLatest -Apply to restore the previous config backup.'
  )
}

if ($Json) {
  $payload | ConvertTo-Json -Depth 32
  return
}

Write-Output ("Plugin module profile: {0}" -f $Module)
Write-Output ("Apply: {0}" -f [bool]$Apply)
Write-Output ("Config: {0}" -f $configFile)
if ($backupPath) { Write-Output ("Backup: {0}" -f $backupPath) }
Write-Output 'Target plugin states:'
foreach ($target in $targets) { Write-Output ("  - {0}: enabled = {1}" -f $target.plugin, $target.enabled.ToString().ToLowerInvariant()) }
Write-Output 'Restart instructions:'
foreach ($item in $payload.restart_instructions) { Write-Output ("  - {0}" -f $item) }
