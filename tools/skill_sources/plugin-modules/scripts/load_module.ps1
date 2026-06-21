[CmdletBinding()]
param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string]$Module,
  [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }),
  [string]$RepoRoot = $(Get-Location),
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

function Get-ProfileProperty {
  param($Object, [string]$Name)
  if ($null -eq $Object) { return @() }
  return @($Object.PSObject.Properties | Where-Object { $_.Name -eq $Name } | Select-Object -First 1)
}

function Get-PropertyValue {
  param($Object, [string]$Name, $Default = $null)
  $property = Get-ProfileProperty -Object $Object -Name $Name
  if ($property) { return $property[0].Value }
  return $Default
}

function ConvertTo-StringArray {
  param($Value)
  if ($null -eq $Value) { return @() }
  if ($Value -is [string]) { return @([string]$Value) }
  return @($Value | ForEach-Object { [string]$_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}

$entryKind = 'profile'
$targetProfile = $Module
$taskModule = $null
$scenarioProfile = $null
$entry = $null
$profileEntry = $null

$property = Get-ProfileProperty -Object $profiles.modules -Name $Module
if ($property) {
  $entry = $property[0].Value
  $profileEntry = $entry
} elseif ($Module.Contains('.')) {
  $parts = $Module.Split('.', 2)
  $profileName = $parts[0]
  $moduleName = $parts[1]
  $profileProperty = Get-ProfileProperty -Object $profiles.modules -Name $profileName
  if (-not $profileProperty) {
    $known = (@($profiles.modules.PSObject.Properties) | ForEach-Object { $_.Name }) -join ', '
    throw "Unknown plugin profile '$profileName' for task module '$Module'. Known profiles: $known"
  }
  $profileEntry = $profileProperty[0].Value
  $taskProperty = Get-ProfileProperty -Object (Get-PropertyValue -Object $profileEntry -Name 'task_modules') -Name $moduleName
  if (-not $taskProperty) {
    $knownTasks = (@((Get-PropertyValue -Object $profileEntry -Name 'task_modules').PSObject.Properties) | ForEach-Object { "$profileName.$($_.Name)" }) -join ', '
    throw "Unknown task module '$Module'. Known task modules for '$profileName': $knownTasks"
  }
  $entryKind = 'task_module'
  $targetProfile = $profileName
  $taskModule = $moduleName
  $entry = $taskProperty[0].Value
} else {
  $scenarioProperty = Get-ProfileProperty -Object (Get-PropertyValue -Object $profiles -Name 'scenario_profiles') -Name $Module
  if ($scenarioProperty) {
    $scenario = $scenarioProperty[0].Value
    $scenarioProfile = $Module
    $targetProfile = [string](Get-PropertyValue -Object $scenario -Name 'target_profile')
    $profileProperty = Get-ProfileProperty -Object $profiles.modules -Name $targetProfile
    if (-not $profileProperty) { throw "Scenario profile '$Module' points to unknown target_profile '$targetProfile'." }
    $entryKind = 'scenario_profile'
    $entry = $scenario
    $profileEntry = $profileProperty[0].Value
  } else {
    $known = (@($profiles.modules.PSObject.Properties) | ForEach-Object { $_.Name }) -join ', '
    $knownScenarios = (@((Get-PropertyValue -Object $profiles -Name 'scenario_profiles').PSObject.Properties) | ForEach-Object { $_.Name }) -join ', '
    throw "Unknown plugin module '$Module'. Known profiles: $known. Known scenario profiles: $knownScenarios"
  }
}

$codexHomePath = [System.IO.Path]::GetFullPath($CodexHome)
$repoRootPath = [System.IO.Path]::GetFullPath($RepoRoot)
$resolved = New-Object System.Collections.Generic.List[string]
$missing = New-Object System.Collections.Generic.List[string]
$totalMatches = 0

$entrySoftLoad = Get-PropertyValue -Object $entry -Name 'soft_load'
$profileSoftLoad = Get-PropertyValue -Object $profileEntry -Name 'soft_load'
$hintSources = @()
$hintSources += ConvertTo-StringArray (Get-PropertyValue -Object $entry -Name 'skill_doc_hints')
$hintSources += ConvertTo-StringArray (Get-PropertyValue -Object $entrySoftLoad -Name 'skill_doc_hints')
if ($hintSources.Count -eq 0 -and $profileEntry) {
  $hintSources += ConvertTo-StringArray (Get-PropertyValue -Object $profileEntry -Name 'skill_doc_hints')
  $hintSources += ConvertTo-StringArray (Get-PropertyValue -Object $profileSoftLoad -Name 'skill_doc_hints')
}

foreach ($hint in @($hintSources)) {
  if ([string]::IsNullOrWhiteSpace([string]$hint)) { continue }
  $pattern = [string]$hint
  if ($pattern.StartsWith('repo:', [System.StringComparison]::OrdinalIgnoreCase)) {
    $repoRelativePattern = $pattern.Substring(5).TrimStart('\', '/')
    $pattern = Join-Path $repoRootPath $repoRelativePattern
  } elseif (-not [System.IO.Path]::IsPathRooted($pattern)) {
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

$plugins = Get-PropertyValue -Object $entry -Name 'plugin_hints'
if ($null -eq $plugins) { $plugins = Get-PropertyValue -Object $entry -Name 'plugins' }
if ($null -eq $plugins -and $profileEntry) { $plugins = Get-PropertyValue -Object $profileEntry -Name 'plugins' }
if ($plugins -is [string] -and $plugins -eq 'all_known_plugins') {
  $plugins = @($profiles.known_plugins)
} else {
  $plugins = ConvertTo-StringArray $plugins
}

$description = [string](Get-PropertyValue -Object $entry -Name 'description' (Get-PropertyValue -Object $entry -Name 'scene_description' (Get-PropertyValue -Object $entry -Name 'scenario_description' '')))
$useFor = @()
$useFor += ConvertTo-StringArray (Get-PropertyValue -Object $entrySoftLoad -Name 'use_for')
$useFor += ConvertTo-StringArray (Get-PropertyValue -Object $entry -Name 'route_when')
$notes = ConvertTo-StringArray (Get-PropertyValue -Object $entrySoftLoad -Name 'notes')

$payload = [ordered]@{
  module = $Module
  entry_kind = $entryKind
  target_profile = $targetProfile
  task_module = $taskModule
  scenario_profile = $scenarioProfile
  mode = 'soft-load'
  codex_home = $codexHomePath
  repo_root = $repoRootPath
  description = $description
  load_policy = [string](Get-PropertyValue -Object $entry -Name 'load_policy' 'soft-load')
  plugins = @($plugins)
  plugin_hints = @(ConvertTo-StringArray (Get-PropertyValue -Object $entry -Name 'plugin_hints'))
  use_for = @($useFor)
  skill_docs = @($resolved)
  omitted_after_max_files = [Math]::Max(0, $totalMatches - $resolved.Count)
  missing_hints = @($missing)
  notes = @($notes)
  routing_explanation = [string](Get-PropertyValue -Object $entry -Name 'routing_explanation' '')
  ranking_signals = @(ConvertTo-StringArray (Get-PropertyValue -Object $entry -Name 'ranking_signals'))
  instructions = @(
    'Read only the returned skill_docs relevant to the current user task.',
    'Soft-load does not edit config.toml and does not add omitted skills back to the startup-visible list.',
    'Task modules are focused soft-load guidance; hard-load applies only to top-level profiles.',
    'If live plugin tools or startup-visible skills are required, preview set_plugin_profile.ps1 and apply only after operator approval.'
  )
}

if ($Json) {
  $payload | ConvertTo-Json -Depth 32
  return
}

Write-Output ("Plugin module: {0}" -f $payload.module)
Write-Output ("Entry kind: {0}" -f $payload.entry_kind)
Write-Output ("Target profile: {0}" -f $payload.target_profile)
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
