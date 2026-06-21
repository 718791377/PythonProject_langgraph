[CmdletBinding()]
param(
  [Alias('Name')]
  [string]$Module,
  [switch]$IncludeTaskModules,
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
$scenarioProperties = @($profiles.scenario_profiles.PSObject.Properties)

function ConvertTo-ArrayCount {
  param($Value)
  if ($null -eq $Value) { return 0 }
  if ($Value -is [string]) { return 1 }
  return @($Value).Count
}

function Get-ProfilePropertyValue {
  param($Object, [string]$Name, $Default = $null)
  if ($null -eq $Object) { return $Default }
  $property = @($Object.PSObject.Properties | Where-Object { $_.Name -eq $Name } | Select-Object -First 1)
  if ($property) { return $property[0].Value }
  return $Default
}

function ConvertTo-ModuleSummary {
  param($Name, $Entry, [string]$EntryKind, [string]$TargetProfile = $null, [string]$TaskModule = $null, [string]$ScenarioProfile = $null)
  $plugins = Get-ProfilePropertyValue -Object $Entry -Name 'plugin_hints'
  if ($null -eq $plugins) { $plugins = Get-ProfilePropertyValue -Object $Entry -Name 'plugins' -Default @() }
  if ($plugins -is [string]) { $plugins = @($plugins) }
  $taskModules = Get-ProfilePropertyValue -Object $Entry -Name 'task_modules'
  $taskCount = 0
  if ($null -ne $taskModules) { $taskCount = @($taskModules.PSObject.Properties).Count }
  $hardLoad = Get-ProfilePropertyValue -Object $Entry -Name 'hard_load'
  $softLoad = Get-ProfilePropertyValue -Object $Entry -Name 'soft_load'
  [ordered]@{
    name = [string]$Name
    entry_kind = $EntryKind
    target_profile = $(if ($TargetProfile) { $TargetProfile } else { $Name })
    task_module = $TaskModule
    scenario_profile = $ScenarioProfile
    description = [string]$(if (Get-ProfilePropertyValue -Object $Entry -Name 'description') { Get-ProfilePropertyValue -Object $Entry -Name 'description' } else { Get-ProfilePropertyValue -Object $Entry -Name 'scenario_description' })
    load_policy = [string](Get-ProfilePropertyValue -Object $Entry -Name 'load_policy')
    plugins = @($plugins)
    hard_load_disables_other_known_plugins = [bool](Get-ProfilePropertyValue -Object $hardLoad -Name 'disable_other_known_plugins' -Default $false)
    soft_load_hint_count = $(if ($null -ne $softLoad) { ConvertTo-ArrayCount (Get-ProfilePropertyValue -Object $softLoad -Name 'skill_doc_hints') } else { ConvertTo-ArrayCount (Get-ProfilePropertyValue -Object $Entry -Name 'skill_doc_hints') })
    task_module_count = $taskCount
  }
}

$items = New-Object System.Collections.Generic.List[object]
foreach ($property in $moduleProperties) {
  $items.Add((ConvertTo-ModuleSummary -Name $property.Name -Entry $property.Value -EntryKind 'profile')) | Out-Null
  $taskModulesForProfile = Get-ProfilePropertyValue -Object $property.Value -Name 'task_modules'
  if ($IncludeTaskModules -and $null -ne $taskModulesForProfile) {
    foreach ($task in @($taskModulesForProfile.PSObject.Properties)) {
      $items.Add((ConvertTo-ModuleSummary -Name "$($property.Name).$($task.Name)" -Entry $task.Value -EntryKind 'task_module' -TargetProfile $property.Name -TaskModule $task.Name)) | Out-Null
    }
  }
}
foreach ($scenario in $scenarioProperties) {
  $items.Add((ConvertTo-ModuleSummary -Name $scenario.Name -Entry $scenario.Value -EntryKind 'scenario_profile' -TargetProfile ([string]$scenario.Value.target_profile) -ScenarioProfile $scenario.Name)) | Out-Null
}

if (-not [string]::IsNullOrWhiteSpace($Module)) {
  $items = @($items | Where-Object { $_.name -eq $Module })
  if ($items.Count -eq 0) {
    $known = (@($moduleProperties | ForEach-Object { $_.Name }) + @($scenarioProperties | ForEach-Object { $_.Name })) -join ', '
    throw "Unknown plugin module '$Module'. Known profiles or scenarios: $known. Use -IncludeTaskModules to list nested task modules."
  }
}

if ($items.Count -eq 1) {
  $payload = $items.Item(0)
} else {
  $payload = @($items.ToArray())
}
if ($Json) {
  $payload | ConvertTo-Json -Depth 24
  return
}

foreach ($item in @($items)) {
  Write-Output ("{0} [{1}] -> {2}: {3}" -f $item.name, $item.entry_kind, $item.target_profile, $item.description)
  Write-Output ("  plugins: {0}" -f (($item.plugins) -join ', '))
}
