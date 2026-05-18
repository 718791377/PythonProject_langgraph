[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
$InstallerPath = Join-Path $Root 'tools\install-codex-user-level-team-mode.ps1'
$TempRoot = Join-Path $Root '.tmp\codex-user-level-team-mode-test'
$CodexHome = Join-Path $TempRoot 'codex-home'
$LegacyStateHome = Join-Path $TempRoot 'legacy-state-home'
$RollbackHome = Join-Path $TempRoot 'rollback-home'
$ConflictHome = Join-Path $TempRoot 'conflict-home'
$FakeRepoRoot = Join-Path $TempRoot 'fake-repo'
$ComposeRepoRoot = Join-Path $TempRoot 'compose-repo'
$NoStateRepoRoot = Join-Path $TempRoot 'no-state-repo'
$AutoRepoRoot = Join-Path $TempRoot 'auto-repo'
$UnmanagedAutoRepoRoot = Join-Path $TempRoot 'auto-repo-unmanaged'
$CleanupRepoRoot = Join-Path $TempRoot 'cleanup-repo'
$LegacySelectorRepoRoot = Join-Path $TempRoot 'legacy-selector-repo'
$CrossRepoSelectorRepoRoot = Join-Path $TempRoot 'cross-repo-selector-repo'
$ReleasedSelectorRepoRoot = Join-Path $TempRoot 'released-selector-repo'
$EmptyResidueRepoRoot = Join-Path $TempRoot 'empty-residue-repo'
$ProfilePath = Join-Path $TempRoot 'profile\Microsoft.PowerShell_profile.ps1'
$LegacyProfilePath = Join-Path $TempRoot 'legacy-profile\Microsoft.PowerShell_profile.ps1'
$RollbackProfilePath = Join-Path $TempRoot 'rollback-profile\Microsoft.PowerShell_profile.ps1'
$ConflictProfilePath = Join-Path $TempRoot 'conflict-profile\Microsoft.PowerShell_profile.ps1'
$FakeNativeCodexPath = Join-Path $TempRoot 'fake-native-codex.ps1'
$ExplicitWrappedCodexPs1Path = Join-Path $TempRoot 'codex.openclaw.ps1'
$ExplicitWrappedCodexCmdPath = Join-Path $TempRoot 'codex.openclaw.cmd'
$ExplicitNativeBypassPs1Path = Join-Path $TempRoot 'codex-native.ps1'
$ExplicitNativeBypassCmdPath = Join-Path $TempRoot 'codex-native.cmd'
$StableWrappedCodexPs1Path = Join-Path $TempRoot 'codex-ohmy.ps1'
$StableWrappedCodexCmdPath = Join-Path $TempRoot 'codex-ohmy.cmd'
$StableNativeBypassPs1Path = Join-Path $TempRoot 'codex-raw.ps1'
$StableNativeBypassCmdPath = Join-Path $TempRoot 'codex-raw.cmd'
$FakeOmxPath = Join-Path $TempRoot 'fake-omx.ps1'
$PrimaryRepoRoot = if ((Split-Path -Leaf (Split-Path -Parent $Root)) -eq '.worktrees') {
  Split-Path -Parent (Split-Path -Parent $Root)
} else {
  $Root
}
$RepoVenvPythonPath = Join-Path $PrimaryRepoRoot '.venv\Scripts\python.exe'
$ResolvedPythonPath = if (Test-Path -LiteralPath $RepoVenvPythonPath) {
  [System.IO.Path]::GetFullPath($RepoVenvPythonPath)
} else {
  [System.IO.Path]::GetFullPath((Get-Command 'python' -ErrorAction Stop).Source)
}

function Assert-Equal {
  param(
    [Parameter(Mandatory)]
    $Actual,
    [Parameter(Mandatory)]
    $Expected,
    [Parameter(Mandatory)]
    [string]$Message
  )

  if ($Actual -ne $Expected) {
    throw "$Message`nExpected: $Expected`nActual: $Actual"
  }
}

function Assert-True {
  param(
    [Parameter(Mandatory)]
    [bool]$Condition,
    [Parameter(Mandatory)]
    [string]$Message
  )

  if (-not $Condition) {
    throw $Message
  }
}

function Assert-ArrayContains {
  param(
    [Parameter(Mandatory)]
    [string[]]$Actual,
    [Parameter(Mandatory)]
    [string]$Expected,
    [Parameter(Mandatory)]
    [string]$Message
  )

  if ($Expected -notin $Actual) {
    throw "$Message`nExpected item: $Expected`nActual: $($Actual -join ', ')"
  }
}

function Ensure-Directory {
  param(
    [Parameter(Mandatory)]
    [string]$Path
  )

  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
  }
}

function Quote-PowerShellLiteral {
  param(
    [Parameter(Mandatory)]
    [string]$Value
  )

  return "'" + $Value.Replace("'", "''") + "'"
}

function Get-PowerShellInvocationText {
  param(
    [Parameter(Mandatory)]
    [string]$FilePath,
    [string[]]$Arguments = @()
  )

  $tokens = @((Quote-PowerShellLiteral -Value $FilePath))
  foreach ($argument in $Arguments) {
    if ($argument -like '-*') {
      $tokens += $argument
      continue
    }

    $tokens += (Quote-PowerShellLiteral -Value $argument)
  }

  return "& { & $($tokens -join ' ') }"
}

function Invoke-PowerShellScriptJson {
  param(
    [Parameter(Mandatory)]
    [string]$FilePath,
    [string[]]$Arguments = @()
  )

  $commandText = Get-PowerShellInvocationText -FilePath $FilePath -Arguments $Arguments
  $output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -Command $commandText
  if ($LASTEXITCODE -ne 0) {
    throw "PowerShell script failed: $FilePath (exit code $LASTEXITCODE)"
  }

  return ($output | ConvertFrom-Json)
}

function Invoke-PowerShellScriptExpectFailure {
  param(
    [Parameter(Mandatory)]
    [string]$FilePath,
    [string[]]$Arguments = @()
  )

  $commandText = Get-PowerShellInvocationText -FilePath $FilePath -Arguments $Arguments
  powershell.exe -NoProfile -ExecutionPolicy Bypass -Command $commandText | Out-Null
  return $LASTEXITCODE
}

function Invoke-PowerShellCommandJson {
  param(
    [Parameter(Mandatory)]
    [string]$CommandText
  )

  $output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -Command $CommandText
  if ($LASTEXITCODE -ne 0) {
    throw "PowerShell command failed (exit code $LASTEXITCODE): $CommandText"
  }

  return ($output | ConvertFrom-Json)
}

if (Test-Path -LiteralPath $TempRoot) {
  Remove-Item -LiteralPath $TempRoot -Recurse -Force
}

New-Item -ItemType Directory -Force -Path (Join-Path $CodexHome 'bin') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $CodexHome 'agents') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $CodexHome 'docs') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $CodexHome 'state') | Out-Null
Ensure-Directory -Path (Split-Path -Parent $ProfilePath)
Ensure-Directory -Path (Split-Path -Parent $LegacyProfilePath)
Ensure-Directory -Path (Split-Path -Parent $RollbackProfilePath)
Ensure-Directory -Path (Split-Path -Parent $ConflictProfilePath)
Ensure-Directory -Path (Join-Path $FakeRepoRoot '.omx\state\team')
Ensure-Directory -Path (Join-Path $ComposeRepoRoot '.omx\state\team')
Ensure-Directory -Path $NoStateRepoRoot
Ensure-Directory -Path (Join-Path $AutoRepoRoot '.omx\state\team')
Ensure-Directory -Path (Join-Path $UnmanagedAutoRepoRoot '.omx\state\team')
Ensure-Directory -Path (Join-Path $CleanupRepoRoot '.omx\state\team')
Ensure-Directory -Path $LegacySelectorRepoRoot
Ensure-Directory -Path $CrossRepoSelectorRepoRoot
Ensure-Directory -Path $ReleasedSelectorRepoRoot
Ensure-Directory -Path (Join-Path $EmptyResidueRepoRoot '.omx\state\team')

$nativeCodexCmdPath = Join-Path $CodexHome 'bin\codex.cmd'
$nativeCodexPs1Path = Join-Path $CodexHome 'bin\codex.ps1'
Set-Content -LiteralPath $nativeCodexCmdPath -Encoding ASCII -Value '@ECHO OFF'
Set-Content -LiteralPath $nativeCodexPs1Path -Encoding ASCII -Value '$host.Name'
Set-Content -LiteralPath $FakeNativeCodexPath -Encoding ASCII -NoNewline -Value @'
param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$Arguments
)

[ordered]@{
  args = $Arguments
  path = [string]$env:Path
  pathext = [string]$env:PATHEXT
  cleanup_shim_directory = [string]$env:CODEX_USER_LEVEL_CLEANUP_SHIM_DIRECTORY
} | ConvertTo-Json -Depth 4
'@
Set-Content -LiteralPath $FakeOmxPath -Encoding ASCII -NoNewline -Value @'
param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$Arguments
)

function Ensure-Directory {
  param(
    [Parameter(Mandatory)]
    [string]$Path
  )

  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
  }
}

function Get-TeamStateRoot {
  return (Join-Path (Get-Location) '.omx\state\team')
}

function Get-NextTeamName {
  $teamStateRoot = Get-TeamStateRoot
  Ensure-Directory -Path $teamStateRoot
  $counterPath = Join-Path $teamStateRoot '.fake-counter'
  $counter = 0
  if (Test-Path -LiteralPath $counterPath) {
    $counter = [int](Get-Content -LiteralPath $counterPath -Raw)
  }
  $counter += 1
  Set-Content -LiteralPath $counterPath -Encoding ASCII -NoNewline -Value ([string]$counter)
  return ('auto-team-{0}' -f $counter)
}

$result = [ordered]@{
  args = $Arguments
}

if ($Arguments.Count -ge 2 -and [string]$Arguments[0] -eq 'team') {
  if ([string]$Arguments[1] -match '^\d+\:') {
    $teamName = Get-NextTeamName
    $teamDirectory = Join-Path (Get-TeamStateRoot) $teamName
    Ensure-Directory -Path $teamDirectory
    $result.operation = 'launch'
    $result.team_name = $teamName
  } elseif ([string]$Arguments[1] -eq 'shutdown' -and $Arguments.Count -ge 3) {
    $teamDirectory = Join-Path (Get-TeamStateRoot) ([string]$Arguments[2])
    if (Test-Path -LiteralPath $teamDirectory) {
      Remove-Item -LiteralPath $teamDirectory -Recurse -Force
    }
    $result.operation = 'shutdown'
    $result.team_name = [string]$Arguments[2]
  } elseif ([string]$Arguments[1] -eq 'api' -and $Arguments.Count -ge 3) {
    $result.operation = [string]$Arguments[2]
    $inputIndex = [Array]::IndexOf($Arguments, '--input')
    if ($inputIndex -ge 0 -and ($inputIndex + 1) -lt $Arguments.Count) {
      $inputText = [string]$Arguments[$inputIndex + 1]
      $result.input = ($inputText | ConvertFrom-Json)
    }
  }
}

$result | ConvertTo-Json -Depth 6
'@

$manifest = Invoke-PowerShellScriptJson -FilePath $InstallerPath -Arguments @(
  '-CodexHome', $CodexHome,
  '-PowerShellProfilePath', $ProfilePath,
  '-NativeCodexCommandPath', $FakeNativeCodexPath,
  '-OmxCommandPath', $FakeOmxPath,
  '-PythonCommandPath', $ResolvedPythonPath
)

Assert-True ($manifest.preserves_native_codex -eq $true) 'Installer did not report native Codex preservation.'
Assert-Equal $manifest.current_state.oh_my_codex 'off' 'Default oh_my_codex state is wrong.'
Assert-Equal $manifest.current_state.subagent_routing 'auto' 'Default subagent_routing state is wrong.'
Assert-Equal $manifest.current_state.completed_subagent_retention 'close' 'Default completed_subagent_retention state is wrong.'
Assert-Equal $manifest.current_state.langgraph 'off' 'Default langgraph switch state is wrong.'
Assert-Equal $manifest.current_state.durable_orchestration_backend 'native_omx' 'Default durable orchestration backend is wrong.'
Assert-Equal ([int]$manifest.native_subagent_limits.max_threads) 6 'Default max_threads is wrong.'
Assert-Equal ([int]$manifest.native_subagent_limits.max_depth) 1 'Default max_depth is wrong.'
Assert-True ($manifest.startup_binding.cleanup_output_control.taskkill_exe_shim_requested -eq $true) 'Installer did not request taskkill.exe cleanup-output shimming by default.'
Assert-True ($manifest.startup_binding.cleanup_output_control.taskkill_exe_shim_compile.attempted -eq $true) 'Default install did not attempt taskkill.exe shim compilation.'
if ($manifest.startup_binding.cleanup_output_control.taskkill_exe_shim_enabled -eq $true) {
  Assert-True (Test-Path -LiteralPath (Join-Path $CodexHome 'bin\win-shims\taskkill.exe')) 'Default EXE shim install reported enabled but did not create taskkill.exe.'
}
Assert-True (Test-Path -LiteralPath $manifest.backup.path) 'Installer did not create a backup snapshot directory.'
Assert-True (Test-Path -LiteralPath $manifest.backup.manifest_path) 'Installer did not create a backup snapshot manifest.'

$legacyStatePath = Join-Path $LegacyStateHome 'state\user-level-team-mode.json'
Ensure-Directory -Path (Split-Path -Parent $legacyStatePath)
Set-Content -LiteralPath $legacyStatePath -Encoding ASCII -NoNewline -Value @'
{
  "schema_version": 1,
  "managed_by": "codex-user-level-team-mode-p0",
  "oh_my_codex": "on",
  "subagent_routing": "auto",
  "durable_orchestration_backend": "langgraph",
  "updated_at": "2026-04-15T23:55:31.4913241Z"
}
'@

$legacyManifest = Invoke-PowerShellScriptJson -FilePath $InstallerPath -Arguments @(
  '-CodexHome', $LegacyStateHome,
  '-PowerShellProfilePath', $LegacyProfilePath,
  '-NativeCodexCommandPath', $FakeNativeCodexPath,
  '-OmxCommandPath', $FakeOmxPath,
  '-PythonCommandPath', $ResolvedPythonPath
)

Assert-Equal $legacyManifest.state_status 'normalized' 'Installer did not normalize a legacy user-level state file.'
Assert-Equal $legacyManifest.current_state.completed_subagent_retention 'close' 'Legacy user-level state normalization did not backfill completed_subagent_retention.'
Assert-Equal $legacyManifest.current_state.langgraph 'on' 'Legacy user-level state normalization did not derive langgraph correctly.'
Assert-Equal $legacyManifest.current_state.durable_orchestration_backend 'langgraph' 'Legacy user-level state normalization changed the durable backend unexpectedly.'
$legacyStateFile = Get-Content -LiteralPath $legacyStatePath -Raw | ConvertFrom-Json
Assert-Equal ([int]$legacyStateFile.schema_version) 3 'Legacy user-level state file was not upgraded to schema version 3.'
Assert-Equal $legacyStateFile.completed_subagent_retention 'close' 'Legacy user-level state file did not persist completed_subagent_retention.'
Assert-Equal $legacyStateFile.langgraph 'on' 'Legacy user-level state file did not persist the derived langgraph flag.'

$expectedManagedFiles = @(
  (Join-Path $CodexHome 'agents\team-leader.toml')
  (Join-Path $CodexHome 'agents\verifier.toml')
  (Join-Path $CodexHome 'agents\debugger.toml')
  (Join-Path $CodexHome 'agents\researcher.toml')
  (Join-Path $CodexHome 'agents\dependency-expert.toml')
  (Join-Path $CodexHome 'agents\writer.toml')
  (Join-Path $CodexHome 'agents\bug-finder.toml')
  (Join-Path $CodexHome 'agents\bug-rebutter.toml')
  (Join-Path $CodexHome 'agents\bug-judge.toml')
  (Join-Path $CodexHome 'bin\_codex-user-level-team-mode.ps1')
  (Join-Path $CodexHome 'bin\_codex-user-level-team-mode-launcher.ps1')
  (Join-Path $CodexHome 'bin\win-shims\taskkill.cmd')
  (Join-Path $CodexHome 'bin\win-shims\taskkill.ps1')
  (Join-Path $CodexHome 'bin\win-shims\taskkill-shim-source.cs')
  $ExplicitWrappedCodexPs1Path
  $ExplicitWrappedCodexCmdPath
  $ExplicitNativeBypassPs1Path
  $ExplicitNativeBypassCmdPath
  $StableWrappedCodexPs1Path
  $StableWrappedCodexCmdPath
  $StableNativeBypassPs1Path
  $StableNativeBypassCmdPath
  (Join-Path $CodexHome 'bin\codex-omx-on.ps1')
  (Join-Path $CodexHome 'bin\codex-omx-off.ps1')
  (Join-Path $CodexHome 'bin\codex-omx-status.ps1')
  (Join-Path $CodexHome 'bin\codex-subagents-auto.ps1')
  (Join-Path $CodexHome 'bin\codex-subagents-manual.ps1')
  (Join-Path $CodexHome 'bin\codex-subagents-off.ps1')
  (Join-Path $CodexHome 'bin\codex-subagent-retention-close.ps1')
  (Join-Path $CodexHome 'bin\codex-subagent-retention-keep.ps1')
  (Join-Path $CodexHome 'bin\codex-subagent-retention-status.ps1')
  (Join-Path $CodexHome 'bin\codex-langgraph-on.ps1')
  (Join-Path $CodexHome 'bin\codex-langgraph-off.ps1')
  (Join-Path $CodexHome 'bin\codex-langgraph-status.ps1')
  (Join-Path $CodexHome 'bin\codex-routing-status.ps1')
  (Join-Path $CodexHome 'bin\codex-durable-backend-native-omx.ps1')
  (Join-Path $CodexHome 'bin\codex-durable-backend-langgraph.ps1')
  (Join-Path $CodexHome 'bin\codex-durable-backend-status.ps1')
  (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1')
  (Join-Path $CodexHome 'bin\codex-durable-state-reconcile.ps1')
  (Join-Path $CodexHome 'bin\omx-team-compose.ps1')
  (Join-Path $CodexHome 'bin\omx-team-compose-status.ps1')
  (Join-Path $CodexHome 'bin\omx-team-compose-await.ps1')
  (Join-Path $CodexHome 'bin\omx-team-compose-recover.ps1')
  (Join-Path $CodexHome 'bin\omx-team-compose-shutdown.ps1')
  (Join-Path $CodexHome 'bin\omx-team-compose-reconcile.ps1')
  (Join-Path $CodexHome 'bin\codex-routing-policy.ps1')
  (Join-Path $CodexHome 'bin\codex-subagent-limits.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-install.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-cli.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-run.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-status.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-resume.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-inspect.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-fuller-engine.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-deeper-engine.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-superstep-engine.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-stateful-engine.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-boundary-engine.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-handoff-engine.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-approval-engine.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-provenance-engine.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-artifact-engine.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-reducer-engine.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-command-engine.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-runtime-engine.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-memory-engine.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-migration-engine.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-auto-policy.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-subgraph-state.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-memory.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-runtime.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-stream.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-subgraphs.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-history.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-replay.ps1')
  (Join-Path $CodexHome 'bin\omx-langgraph-recover.ps1')
  (Join-Path $CodexHome 'bin\omx-team-dev.ps1')
  (Join-Path $CodexHome 'bin\omx-team-debug.ps1')
  (Join-Path $CodexHome 'bin\omx-team-auto.ps1')
  (Join-Path $CodexHome 'bin\omx-team-ops.ps1')
  (Join-Path $CodexHome 'bin\omx-team-send-message.ps1')
  (Join-Path $CodexHome 'bin\omx-team-mailbox-list.ps1')
  (Join-Path $CodexHome 'bin\omx-team-mailbox-mark-delivered.ps1')
  (Join-Path $CodexHome 'bin\omx-team-claim-task.ps1')
  (Join-Path $CodexHome 'bin\omx-team-transition-task-status.ps1')
  (Join-Path $CodexHome 'bin\omx-team-release-task-claim.ps1')
  (Join-Path $CodexHome 'bin\omx-team-report-progress.ps1')
  (Join-Path $CodexHome 'bin\omx-team-complete-task.ps1')
  (Join-Path $CodexHome 'bin\omx-team-fail-task.ps1')
  (Join-Path $CodexHome 'bin\omx-team-hybrid.ps1')
  (Join-Path $CodexHome 'bin\omx-team-verify.ps1')
  (Join-Path $CodexHome 'docs\team-mode-playbook.md')
  (Join-Path $CodexHome 'docs\team-mode-quick-reference.md')
  (Join-Path $CodexHome 'teams\compose-manifest.schema.json')
  (Join-Path $CodexHome 'python\langgraph_durable_orchestrator\__init__.py')
  (Join-Path $CodexHome 'python\langgraph_durable_orchestrator\contracts.py')
  (Join-Path $CodexHome 'python\langgraph_durable_orchestrator\runtime.py')
  (Join-Path $CodexHome 'python\langgraph_durable_orchestrator\cli.py')
  (Join-Path $CodexHome 'state\native-subagent-limits.json')
  (Join-Path $CodexHome 'state\user-level-team-mode.json')
)

$backupManifest = Get-Content -LiteralPath $manifest.backup.manifest_path -Raw | ConvertFrom-Json
$backupManifestPaths = @($backupManifest.files | ForEach-Object { [string]$_.path })
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'state\user-level-team-mode.json')) 'Backup snapshot manifest did not include the shared state file.'
Assert-True ($backupManifestPaths -contains $ProfilePath) 'Backup snapshot manifest did not include the PowerShell profile path.'
Assert-True ($backupManifestPaths -contains $ExplicitWrappedCodexPs1Path) 'Backup snapshot manifest did not include the explicit wrapped codex PowerShell launcher path.'
Assert-True ($backupManifestPaths -contains $ExplicitWrappedCodexCmdPath) 'Backup snapshot manifest did not include the explicit wrapped codex cmd launcher path.'
Assert-True ($backupManifestPaths -contains $ExplicitNativeBypassPs1Path) 'Backup snapshot manifest did not include the explicit native bypass PowerShell launcher path.'
Assert-True ($backupManifestPaths -contains $ExplicitNativeBypassCmdPath) 'Backup snapshot manifest did not include the explicit native bypass cmd launcher path.'
Assert-True ($backupManifestPaths -contains $StableWrappedCodexPs1Path) 'Backup snapshot manifest did not include the stable wrapped codex PowerShell launcher path.'
Assert-True ($backupManifestPaths -contains $StableWrappedCodexCmdPath) 'Backup snapshot manifest did not include the stable wrapped codex cmd launcher path.'
Assert-True ($backupManifestPaths -contains $StableNativeBypassPs1Path) 'Backup snapshot manifest did not include the stable native bypass PowerShell launcher path.'
Assert-True ($backupManifestPaths -contains $StableNativeBypassCmdPath) 'Backup snapshot manifest did not include the stable native bypass cmd launcher path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'docs\team-mode-playbook.md')) 'Backup snapshot manifest did not include the generated playbook path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'docs\team-mode-quick-reference.md')) 'Backup snapshot manifest did not include the generated quick-reference path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'teams\compose-manifest.schema.json')) 'Backup snapshot manifest did not include the compose manifest schema path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'teams\compose-manifest.schema.json')) 'Backup snapshot manifest did not include the compose manifest schema path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\codex-routing-policy.ps1')) 'Backup snapshot manifest did not include the routing policy script path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1')) 'Backup snapshot manifest did not include the durable-state status script path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\codex-durable-state-reconcile.ps1')) 'Backup snapshot manifest did not include the durable-state reconcile script path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-team-compose.ps1')) 'Backup snapshot manifest did not include the compose entrypoint path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-team-compose.ps1')) 'Backup snapshot manifest did not include the compose entrypoint path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-team-compose-status.ps1')) 'Backup snapshot manifest did not include the compose status helper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-team-compose-await.ps1')) 'Backup snapshot manifest did not include the compose await helper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-team-compose-recover.ps1')) 'Backup snapshot manifest did not include the compose recover helper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-team-compose-shutdown.ps1')) 'Backup snapshot manifest did not include the compose shutdown helper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-team-compose-reconcile.ps1')) 'Backup snapshot manifest did not include the compose reconcile helper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\codex-subagent-limits.ps1')) 'Backup snapshot manifest did not include the native subagent limits script path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\codex-langgraph-on.ps1')) 'Backup snapshot manifest did not include the LangGraph on switch path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\codex-langgraph-off.ps1')) 'Backup snapshot manifest did not include the LangGraph off switch path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-install.ps1')) 'Backup snapshot manifest did not include the LangGraph install helper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-cli.ps1')) 'Backup snapshot manifest did not include the LangGraph CLI wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-run.ps1')) 'Backup snapshot manifest did not include the LangGraph run wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-history.ps1')) 'Backup snapshot manifest did not include the LangGraph history wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-subgraphs.ps1')) 'Backup snapshot manifest did not include the LangGraph subgraphs wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-fuller-engine.ps1')) 'Backup snapshot manifest did not include the LangGraph fuller-engine wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-deeper-engine.ps1')) 'Backup snapshot manifest did not include the LangGraph deeper-engine wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-superstep-engine.ps1')) 'Backup snapshot manifest did not include the LangGraph superstep-engine wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-stateful-engine.ps1')) 'Backup snapshot manifest did not include the LangGraph stateful-engine wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-boundary-engine.ps1')) 'Backup snapshot manifest did not include the LangGraph boundary-engine wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-handoff-engine.ps1')) 'Backup snapshot manifest did not include the LangGraph handoff-engine wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-approval-engine.ps1')) 'Backup snapshot manifest did not include the LangGraph approval-engine wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-provenance-engine.ps1')) 'Backup snapshot manifest did not include the LangGraph provenance-engine wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-artifact-engine.ps1')) 'Backup snapshot manifest did not include the LangGraph artifact-engine wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-reducer-engine.ps1')) 'Backup snapshot manifest did not include the LangGraph reducer-engine wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-command-engine.ps1')) 'Backup snapshot manifest did not include the LangGraph command-engine wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-runtime-engine.ps1')) 'Backup snapshot manifest did not include the LangGraph runtime-engine wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-memory-engine.ps1')) 'Backup snapshot manifest did not include the LangGraph memory-engine wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-migration-engine.ps1')) 'Backup snapshot manifest did not include the LangGraph migration-engine wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-auto-policy.ps1')) 'Backup snapshot manifest did not include the LangGraph auto-policy wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-subgraph-state.ps1')) 'Backup snapshot manifest did not include the LangGraph subgraph-state wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-memory.ps1')) 'Backup snapshot manifest did not include the LangGraph memory wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-runtime.ps1')) 'Backup snapshot manifest did not include the LangGraph runtime wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-stream.ps1')) 'Backup snapshot manifest did not include the LangGraph stream wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-replay.ps1')) 'Backup snapshot manifest did not include the LangGraph replay wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-langgraph-recover.ps1')) 'Backup snapshot manifest did not include the LangGraph recover wrapper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\win-shims\taskkill.cmd')) 'Backup snapshot manifest did not include the Windows taskkill CMD shim path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\win-shims\taskkill.ps1')) 'Backup snapshot manifest did not include the Windows taskkill PowerShell shim path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\win-shims\taskkill-shim-source.cs')) 'Backup snapshot manifest did not include the Windows taskkill C# shim source path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\win-shims\taskkill.exe')) 'Backup snapshot manifest did not include the Windows taskkill EXE shim path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'python\langgraph_durable_orchestrator\cli.py')) 'Backup snapshot manifest did not include the LangGraph CLI template path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'state\native-subagent-limits.json')) 'Backup snapshot manifest did not include the native subagent limits state path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'bin\omx-team-auto.ps1')) 'Backup snapshot manifest did not include the automatic team helper path.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'agents\verifier.toml')) 'Backup snapshot manifest did not include verifier.toml.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'agents\debugger.toml')) 'Backup snapshot manifest did not include debugger.toml.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'agents\researcher.toml')) 'Backup snapshot manifest did not include researcher.toml.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'agents\dependency-expert.toml')) 'Backup snapshot manifest did not include dependency-expert.toml.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'agents\writer.toml')) 'Backup snapshot manifest did not include writer.toml.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'agents\bug-finder.toml')) 'Backup snapshot manifest did not include bug-finder.toml.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'agents\bug-rebutter.toml')) 'Backup snapshot manifest did not include bug-rebutter.toml.'
Assert-True ($backupManifestPaths -contains (Join-Path $CodexHome 'agents\bug-judge.toml')) 'Backup snapshot manifest did not include bug-judge.toml.'

foreach ($path in $expectedManagedFiles) {
  Assert-True (Test-Path -LiteralPath $path) "Expected generated file is missing: $path"
}

Assert-Equal ((Get-Content -LiteralPath $nativeCodexCmdPath -Raw).Trim()) '@ECHO OFF' 'Native codex.cmd was modified.'
Assert-Equal ((Get-Content -LiteralPath $nativeCodexPs1Path -Raw).Trim()) '$host.Name' 'Native codex.ps1 was modified.'

$leaderProfile = Get-Content -LiteralPath (Join-Path $CodexHome 'agents\team-leader.toml') -Raw
Assert-True ($leaderProfile.Contains('current main Codex CLI session')) 'team-leader.toml does not describe the main Codex CLI session as leader.'
Assert-True ($leaderProfile.Contains('bug-finder / bug-rebutter / bug-judge')) 'team-leader.toml does not mention the adversarial bug-review burst roles.'
Assert-True ($leaderProfile.Contains('per-repository or per-worktree `.omx` state roots')) 'team-leader.toml does not describe repository-scoped runtime isolation.'
Assert-True ($leaderProfile.Contains('omx-team-auto.ps1')) 'team-leader.toml does not mention the automatic durable-team helper.'
Assert-True ($leaderProfile.Contains('codex-auto-managed-team.json')) 'team-leader.toml does not mention the tracked automatic team record.'
Assert-True ($leaderProfile.Contains('official native capability')) 'team-leader.toml does not describe native Codex subagents as an official native capability.'
Assert-True ($leaderProfile.Contains('<repo>/.codex/agents/')) 'team-leader.toml does not mention repository-scoped agent TOML placement.'
Assert-True ($leaderProfile.Contains('agents.max_threads') -and $leaderProfile.Contains('agents.max_depth')) 'team-leader.toml does not mention native subagent limits.'
Assert-True ($leaderProfile.Contains('close the agent by default') -and $leaderProfile.Contains('keep the agent available until explicit close')) 'team-leader.toml does not describe retention-dependent completed-subagent handling.'
Assert-True ($leaderProfile.Contains('single `wait_agent` call')) 'team-leader.toml does not require bounded wait_agent windows.'
Assert-True ($leaderProfile.Contains('periodic progress/liveness check-ins')) 'team-leader.toml does not require periodic native-subagent progress updates.'
Assert-True ($leaderProfile.Contains('OpenHands')) 'team-leader.toml does not mention OpenHands terminology.'
Assert-True ($leaderProfile.Contains('.omx/state/langgraph/')) 'team-leader.toml does not mention repo-local LangGraph state.'
Assert-True ($leaderProfile.Contains('primary user-level operator-facing backend policy surface')) 'team-leader.toml does not identify the primary user-level backend policy surface.'
Assert-True ($leaderProfile.Contains('repository-local OpenSpec specs and bilingual implementation plans remain the development source of truth')) 'team-leader.toml does not distinguish user-level operator authority from repository-local development authority.'
Assert-True ($leaderProfile.Contains('every session reload or Codex restart')) 'team-leader.toml does not require activation re-checks on reload or restart.'
Assert-True ($leaderProfile.Contains('hard routing directives')) 'team-leader.toml does not describe explicit omx/LangGraph requests as hard directives.'
Assert-True ($leaderProfile.Contains('actually adopt `native_omx` or `langgraph`')) 'team-leader.toml does not require actual orchestration adoption after threshold hits.'
Assert-True ($leaderProfile.Contains('Existing live sessions should retrofit orchestration behavior')) 'team-leader.toml does not describe retrofit for existing live sessions.'
Assert-True ($leaderProfile.Contains('Automatic collaboration is the default for all projects')) 'team-leader.toml does not preserve the global automatic collaboration default.'
Assert-True ($leaderProfile.Contains('platform_subagent_invocation_constraint')) 'team-leader.toml does not preserve the platform subagent invocation blocker token.'
Assert-True ($leaderProfile.Contains('10 true upstream provider forwards per rolling 1-minute window')) 'team-leader.toml does not describe the global upstream pacing budget.'
Assert-True ($leaderProfile.Contains('wait for a slot instead of immediately returning a local 429')) 'team-leader.toml does not describe pacing overflow as slot waiting.'
Assert-True ($leaderProfile.Contains('Do not treat the upstream pacing budget alone as a reason to avoid LangGraph')) 'team-leader.toml does not preserve the orchestration-safe pacing interpretation.'
Assert-True ($leaderProfile.Contains('codex-durable-state-status.ps1')) 'team-leader.toml does not mention the canonical inspectable durable-state surface.'
Assert-True ($leaderProfile.Contains('codex-durable-state-reconcile.ps1')) 'team-leader.toml does not mention the durable-state cleanup and reconciliation helper.'
Assert-True ($leaderProfile.Contains('Mixed persistent pane compose remains an advanced opt-in mode')) 'team-leader.toml does not preserve the advanced compose boundary.'
Assert-True ($leaderProfile.Contains('omx-team-compose.ps1')) 'team-leader.toml does not mention the compose entrypoint.'
Assert-True ($leaderProfile.Contains('Mixed persistent pane compose remains an advanced opt-in mode')) 'team-leader.toml does not preserve the advanced opt-in compose boundary.'
Assert-True ($leaderProfile.Contains('omx-team-compose.ps1')) 'team-leader.toml does not mention the compose entrypoint.'
Assert-True ($leaderProfile.Contains('first fan out into homogeneous `analyst` calls')) 'team-leader.toml does not describe analyst-fanout-first bounded research routing.'
Assert-True ($leaderProfile.Contains('Do not mix `architect`, `planner`, or `writer` into that first bounded research round by default')) 'team-leader.toml does not keep architect/planner/writer out of the default first bounded research round.'
$verifierProfile = Get-Content -LiteralPath (Join-Path $CodexHome 'agents\verifier.toml') -Raw
Assert-True ($verifierProfile.Contains('name = "verifier"')) 'verifier.toml was not generated with the expected role name.'
Assert-True ($verifierProfile.Contains('model = "gpt-5.4"')) 'verifier.toml did not promote the model to gpt-5.4.'
Assert-True ($verifierProfile.Contains('model_reasoning_effort = "high"')) 'verifier.toml did not preserve high reasoning effort.'
$debuggerProfile = Get-Content -LiteralPath (Join-Path $CodexHome 'agents\debugger.toml') -Raw
Assert-True ($debuggerProfile.Contains('name = "debugger"')) 'debugger.toml was not generated with the expected role name.'
Assert-True ($debuggerProfile.Contains('model = "gpt-5.4"')) 'debugger.toml did not promote the model to gpt-5.4.'
Assert-True ($debuggerProfile.Contains('model_reasoning_effort = "high"')) 'debugger.toml did not preserve high reasoning effort.'
$researcherProfile = Get-Content -LiteralPath (Join-Path $CodexHome 'agents\researcher.toml') -Raw
Assert-True ($researcherProfile.Contains('name = "researcher"')) 'researcher.toml was not generated with the expected role name.'
Assert-True ($researcherProfile.Contains('model = "gpt-5.4"')) 'researcher.toml did not promote the model to gpt-5.4.'
Assert-True ($researcherProfile.Contains('model_reasoning_effort = "high"')) 'researcher.toml did not preserve high reasoning effort.'
$dependencyExpertProfile = Get-Content -LiteralPath (Join-Path $CodexHome 'agents\dependency-expert.toml') -Raw
Assert-True ($dependencyExpertProfile.Contains('name = "dependency-expert"')) 'dependency-expert.toml was not generated with the expected role name.'
Assert-True ($dependencyExpertProfile.Contains('model = "gpt-5.4"')) 'dependency-expert.toml did not promote the model to gpt-5.4.'
Assert-True ($dependencyExpertProfile.Contains('model_reasoning_effort = "high"')) 'dependency-expert.toml did not preserve high reasoning effort.'
$writerProfile = Get-Content -LiteralPath (Join-Path $CodexHome 'agents\writer.toml') -Raw
Assert-True ($writerProfile.Contains('name = "writer"')) 'writer.toml was not generated with the expected role name.'
Assert-True ($writerProfile.Contains('model = "gpt-5.4"')) 'writer.toml did not promote the model to gpt-5.4.'
Assert-True ($writerProfile.Contains('model_reasoning_effort = "medium"')) 'writer.toml did not set the intended medium reasoning effort.'
$bugFinderProfile = Get-Content -LiteralPath (Join-Path $CodexHome 'agents\bug-finder.toml') -Raw
Assert-True ($bugFinderProfile.Contains('name = "bug-finder"')) 'bug-finder.toml was not generated with the expected role name.'
Assert-True ($bugFinderProfile.Contains('Default to read-only review.')) 'bug-finder.toml did not preserve read-only review discipline.'
Assert-True ($bugFinderProfile.Contains('low impact: +1')) 'bug-finder.toml did not encode the recall scoring incentives.'
$bugRebutterProfile = Get-Content -LiteralPath (Join-Path $CodexHome 'agents\bug-rebutter.toml') -Raw
Assert-True ($bugRebutterProfile.Contains('name = "bug-rebutter"')) 'bug-rebutter.toml was not generated with the expected role name.'
Assert-True ($bugRebutterProfile.Contains('disproving a claim earns its score')) 'bug-rebutter.toml did not encode the rebuttal scoring incentives.'
Assert-True ($bugRebutterProfile.Contains('Default to read-only review.')) 'bug-rebutter.toml did not preserve read-only review discipline.'
$bugJudgeProfile = Get-Content -LiteralPath (Join-Path $CodexHome 'agents\bug-judge.toml') -Raw
Assert-True ($bugJudgeProfile.Contains('name = "bug-judge"')) 'bug-judge.toml was not generated with the expected role name.'
Assert-True ($bugJudgeProfile.Contains('correct verdict: +1')) 'bug-judge.toml did not encode the judging incentive model.'
Assert-True ($bugJudgeProfile.Contains('Only judged survivors may be promoted')) 'bug-judge.toml did not preserve the escalation gate.'

$startupBinding = $manifest.startup_binding
Assert-Equal $startupBinding.powershell_profile_path $ProfilePath 'Installer reported the wrong PowerShell profile path.'
Assert-Equal $startupBinding.native_codex_command_path $FakeNativeCodexPath 'Installer reported the wrong native Codex command path.'
Assert-Equal $startupBinding.native_command_directory $TempRoot 'Installer reported the wrong native command directory.'
Assert-Equal $startupBinding.cleanup_output_control.win_shims_directory (Join-Path $CodexHome 'bin\win-shims') 'Installer reported the wrong cleanup-output win-shims directory.'
Assert-Equal $startupBinding.cleanup_output_control.taskkill_cmd_path (Join-Path $CodexHome 'bin\win-shims\taskkill.cmd') 'Installer reported the wrong taskkill CMD shim path.'
Assert-Equal $startupBinding.cleanup_output_control.taskkill_ps1_path (Join-Path $CodexHome 'bin\win-shims\taskkill.ps1') 'Installer reported the wrong taskkill PowerShell shim path.'
Assert-Equal $startupBinding.cleanup_output_control.taskkill_shim_source_path (Join-Path $CodexHome 'bin\win-shims\taskkill-shim-source.cs') 'Installer reported the wrong taskkill C# shim source path.'
Assert-Equal $startupBinding.cleanup_output_control.taskkill_exe_shim_path (Join-Path $CodexHome 'bin\win-shims\taskkill.exe') 'Installer reported the wrong taskkill EXE shim path.'
Assert-True ($startupBinding.cleanup_output_control.taskkill_exe_shim_requested -eq $true) 'Installer did not request the taskkill EXE shim by default.'
Assert-True ($startupBinding.cleanup_output_control.taskkill_exe_shim_compile.attempted -eq $true) 'Installer did not attempt taskkill EXE compilation by default.'
Assert-True ($startupBinding.cleanup_output_control.scoped_to_wrapped_launch -eq $true) 'Installer did not report cleanup-output control as scoped to wrapped launches.'
Assert-Equal $startupBinding.non_profile_launchers.wrapped_ps1_path $ExplicitWrappedCodexPs1Path 'Installer reported the wrong explicit wrapped codex PowerShell launcher path.'
Assert-Equal $startupBinding.non_profile_launchers.wrapped_cmd_path $ExplicitWrappedCodexCmdPath 'Installer reported the wrong explicit wrapped codex cmd launcher path.'
Assert-Equal $startupBinding.non_profile_launchers.native_bypass_ps1_path $ExplicitNativeBypassPs1Path 'Installer reported the wrong explicit native bypass PowerShell launcher path.'
Assert-Equal $startupBinding.non_profile_launchers.native_bypass_cmd_path $ExplicitNativeBypassCmdPath 'Installer reported the wrong explicit native bypass cmd launcher path.'
Assert-Equal $startupBinding.non_profile_launchers.stable_wrapped_ps1_path $StableWrappedCodexPs1Path 'Installer reported the wrong stable wrapped codex PowerShell launcher path.'
Assert-Equal $startupBinding.non_profile_launchers.stable_wrapped_cmd_path $StableWrappedCodexCmdPath 'Installer reported the wrong stable wrapped codex cmd launcher path.'
Assert-Equal $startupBinding.non_profile_launchers.stable_native_bypass_ps1_path $StableNativeBypassPs1Path 'Installer reported the wrong stable native bypass PowerShell launcher path.'
Assert-Equal $startupBinding.non_profile_launchers.stable_native_bypass_cmd_path $StableNativeBypassCmdPath 'Installer reported the wrong stable native bypass cmd launcher path.'
$omxEntrypoints = $manifest.omx_entrypoints
Assert-Equal $omxEntrypoints.omx_command_path $FakeOmxPath 'Installer reported the wrong OMX command path.'
Assert-Equal $omxEntrypoints.python_command_path $ResolvedPythonPath 'Installer reported the wrong Python command path.'
Assert-Equal $omxEntrypoints.langgraph_shared_venv_path (Join-Path $CodexHome 'venvs\langgraph-py312') 'Installer reported the wrong shared LangGraph venv path.'
Assert-Equal $omxEntrypoints.langgraph_shared_python_path (Join-Path $CodexHome 'venvs\langgraph-py312\Scripts\python.exe') 'Installer reported the wrong shared LangGraph Python path.'
Assert-Equal $omxEntrypoints.langgraph_helper_artifact_root (Join-Path $CodexHome 'python\langgraph_durable_orchestrator') 'Installer reported the wrong LangGraph helper artifact root.'
Assert-Equal $omxEntrypoints.playbook_path (Join-Path $CodexHome 'docs\team-mode-playbook.md') 'Installer reported the wrong playbook path.'
Assert-Equal $omxEntrypoints.quick_reference_path (Join-Path $CodexHome 'docs\team-mode-quick-reference.md') 'Installer reported the wrong quick-reference path.'
Assert-Equal $omxEntrypoints.compose_manifest_schema_path (Join-Path $CodexHome 'teams\compose-manifest.schema.json') 'Installer reported the wrong compose manifest schema path.'
Assert-Equal $omxEntrypoints.automatic_team_helper_path (Join-Path $CodexHome 'bin\omx-team-auto.ps1') 'Installer reported the wrong automatic team helper path.'
Assert-Equal $omxEntrypoints.compose_entrypoint_path (Join-Path $CodexHome 'bin\omx-team-compose.ps1') 'Installer reported the wrong compose entrypoint path.'
Assert-Equal $omxEntrypoints.compose_status_path (Join-Path $CodexHome 'bin\omx-team-compose-status.ps1') 'Installer reported the wrong compose status helper path.'
Assert-Equal $omxEntrypoints.compose_await_path (Join-Path $CodexHome 'bin\omx-team-compose-await.ps1') 'Installer reported the wrong compose await helper path.'
Assert-Equal $omxEntrypoints.compose_recover_path (Join-Path $CodexHome 'bin\omx-team-compose-recover.ps1') 'Installer reported the wrong compose recover helper path.'
Assert-Equal $omxEntrypoints.compose_shutdown_path (Join-Path $CodexHome 'bin\omx-team-compose-shutdown.ps1') 'Installer reported the wrong compose shutdown helper path.'
Assert-Equal $omxEntrypoints.compose_reconcile_path (Join-Path $CodexHome 'bin\omx-team-compose-reconcile.ps1') 'Installer reported the wrong compose reconcile helper path.'
Assert-Equal $omxEntrypoints.langgraph_install_path (Join-Path $CodexHome 'bin\omx-langgraph-install.ps1') 'Installer reported the wrong LangGraph install helper path.'
Assert-Equal $omxEntrypoints.langgraph_cli_path (Join-Path $CodexHome 'bin\omx-langgraph-cli.ps1') 'Installer reported the wrong LangGraph CLI wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_run_path (Join-Path $CodexHome 'bin\omx-langgraph-run.ps1') 'Installer reported the wrong LangGraph run wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_status_path (Join-Path $CodexHome 'bin\omx-langgraph-status.ps1') 'Installer reported the wrong LangGraph status wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_resume_path (Join-Path $CodexHome 'bin\omx-langgraph-resume.ps1') 'Installer reported the wrong LangGraph resume wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_inspect_path (Join-Path $CodexHome 'bin\omx-langgraph-inspect.ps1') 'Installer reported the wrong LangGraph inspect wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_fuller_engine_path (Join-Path $CodexHome 'bin\omx-langgraph-fuller-engine.ps1') 'Installer reported the wrong LangGraph fuller-engine wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_deeper_engine_path (Join-Path $CodexHome 'bin\omx-langgraph-deeper-engine.ps1') 'Installer reported the wrong LangGraph deeper-engine wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_superstep_engine_path (Join-Path $CodexHome 'bin\omx-langgraph-superstep-engine.ps1') 'Installer reported the wrong LangGraph superstep-engine wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_stateful_engine_path (Join-Path $CodexHome 'bin\omx-langgraph-stateful-engine.ps1') 'Installer reported the wrong LangGraph stateful-engine wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_boundary_engine_path (Join-Path $CodexHome 'bin\omx-langgraph-boundary-engine.ps1') 'Installer reported the wrong LangGraph boundary-engine wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_handoff_engine_path (Join-Path $CodexHome 'bin\omx-langgraph-handoff-engine.ps1') 'Installer reported the wrong LangGraph handoff-engine wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_approval_engine_path (Join-Path $CodexHome 'bin\omx-langgraph-approval-engine.ps1') 'Installer reported the wrong LangGraph approval-engine wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_provenance_engine_path (Join-Path $CodexHome 'bin\omx-langgraph-provenance-engine.ps1') 'Installer reported the wrong LangGraph provenance-engine wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_artifact_engine_path (Join-Path $CodexHome 'bin\omx-langgraph-artifact-engine.ps1') 'Installer reported the wrong LangGraph artifact-engine wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_reducer_engine_path (Join-Path $CodexHome 'bin\omx-langgraph-reducer-engine.ps1') 'Installer reported the wrong LangGraph reducer-engine wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_command_engine_path (Join-Path $CodexHome 'bin\omx-langgraph-command-engine.ps1') 'Installer reported the wrong LangGraph command-engine wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_runtime_engine_path (Join-Path $CodexHome 'bin\omx-langgraph-runtime-engine.ps1') 'Installer reported the wrong LangGraph runtime-engine wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_memory_engine_path (Join-Path $CodexHome 'bin\omx-langgraph-memory-engine.ps1') 'Installer reported the wrong LangGraph memory-engine wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_migration_engine_path (Join-Path $CodexHome 'bin\omx-langgraph-migration-engine.ps1') 'Installer reported the wrong LangGraph migration-engine wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_auto_policy_path (Join-Path $CodexHome 'bin\omx-langgraph-auto-policy.ps1') 'Installer reported the wrong LangGraph auto-policy wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_subgraph_state_path (Join-Path $CodexHome 'bin\omx-langgraph-subgraph-state.ps1') 'Installer reported the wrong LangGraph subgraph-state wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_memory_path (Join-Path $CodexHome 'bin\omx-langgraph-memory.ps1') 'Installer reported the wrong LangGraph memory wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_runtime_path (Join-Path $CodexHome 'bin\omx-langgraph-runtime.ps1') 'Installer reported the wrong LangGraph runtime wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_stream_path (Join-Path $CodexHome 'bin\omx-langgraph-stream.ps1') 'Installer reported the wrong LangGraph stream wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_subgraphs_path (Join-Path $CodexHome 'bin\omx-langgraph-subgraphs.ps1') 'Installer reported the wrong LangGraph subgraphs wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_history_path (Join-Path $CodexHome 'bin\omx-langgraph-history.ps1') 'Installer reported the wrong LangGraph history wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_replay_path (Join-Path $CodexHome 'bin\omx-langgraph-replay.ps1') 'Installer reported the wrong LangGraph replay wrapper path.'
Assert-Equal $omxEntrypoints.langgraph_recover_path (Join-Path $CodexHome 'bin\omx-langgraph-recover.ps1') 'Installer reported the wrong LangGraph recover wrapper path.'
Assert-Equal $omxEntrypoints.durable_state_status_path (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') 'Installer reported the wrong durable-state status wrapper path.'
Assert-Equal $omxEntrypoints.durable_state_reconcile_path (Join-Path $CodexHome 'bin\codex-durable-state-reconcile.ps1') 'Installer reported the wrong durable-state reconcile wrapper path.'

$langGraphInstallPlan = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-install.ps1') -Arguments @(
  '-DryRun',
  '-Json'
)
Assert-Equal $langGraphInstallPlan.action 'dry_run' 'LangGraph install helper did not expose dry-run action.'
Assert-Equal $langGraphInstallPlan.plan.shared_venv_path (Join-Path $CodexHome 'venvs\langgraph-py312') 'LangGraph install helper did not report the shared venv path.'
Assert-Equal $langGraphInstallPlan.plan.shared_python_path (Join-Path $CodexHome 'venvs\langgraph-py312\Scripts\python.exe') 'LangGraph install helper did not report the shared Python path.'
Assert-ArrayContains -Actual @($langGraphInstallPlan.plan.packages | ForEach-Object { [string]$_ }) -Expected 'langgraph' -Message 'LangGraph install helper did not include the base langgraph package.'

$langGraphRunWrapperContent = Get-Content -LiteralPath (Join-Path $CodexHome 'bin\omx-langgraph-run.ps1') -Raw
Assert-True ($langGraphRunWrapperContent.Contains('Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath')) 'LangGraph run wrapper did not prefer the shared LangGraph venv Python path.'
$langGraphCliWrapperContent = Get-Content -LiteralPath (Join-Path $CodexHome 'bin\omx-langgraph-cli.ps1') -Raw
Assert-True ($langGraphCliWrapperContent.Contains("`$env:PYTHONIOENCODING = 'utf-8'")) 'LangGraph CLI wrapper did not force PYTHONIOENCODING=utf-8.'
Assert-True ($langGraphCliWrapperContent.Contains("`$env:PYTHONUTF8 = '1'")) 'LangGraph CLI wrapper did not force PYTHONUTF8=1.'
Assert-True ($langGraphCliWrapperContent.Contains('Get-CodexUserLevelLangGraphCliExecutablePath')) 'LangGraph CLI wrapper did not resolve the shared-vm langgraph executable path.'

Assert-True (Test-Path -LiteralPath $ProfilePath) 'Installer did not create the PowerShell profile file.'
$profileContent = Get-Content -LiteralPath $ProfilePath -Raw
Assert-True ($profileContent.Contains('OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-STARTUP:START')) 'Managed startup profile block was not installed.'
Assert-True ($profileContent.Contains('$codexUserLevelBinDirectory')) 'Managed startup profile block did not add the user-level bin directory to PATH.'
Assert-True ($profileContent.Contains('CODEX_USER_LEVEL_CLEANUP_SHIM_DIRECTORY')) 'Managed startup profile block did not bridge the wrapped cleanup shim directory into login shells.'
Assert-True ($profileContent.Contains('function global:codex-native')) 'Managed startup profile block did not add codex-native.'

$profileShimProbe = Invoke-PowerShellCommandJson -CommandText ("& { `$env:CODEX_USER_LEVEL_CLEANUP_SHIM_DIRECTORY = " + (Quote-PowerShellLiteral -Value (Join-Path $CodexHome 'bin\win-shims')) + "; `$env:Path = 'C:\Windows\system32;C:\Windows'; `$env:PATHEXT = '.EXE;.CMD;.COM'; & " + (Quote-PowerShellLiteral -Value $ProfilePath) + "; [ordered]@{ path = [string]`$env:Path; pathext = [string]`$env:PATHEXT; taskkill_exe = (Get-Command 'taskkill.exe' -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source) } | ConvertTo-Json -Depth 4 }")
$profileShimPathSegments = @(([string]$profileShimProbe.path).Split(';') | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
Assert-True ($profileShimPathSegments.Count -gt 0) 'Managed startup profile probe did not expose PATH entries.'
Assert-Equal ([System.IO.Path]::GetFullPath($profileShimPathSegments[0])) (Join-Path $CodexHome 'bin\win-shims') 'Managed startup profile did not restore win-shims after a login-shell PATH reset.'
if ($manifest.startup_binding.cleanup_output_control.taskkill_exe_shim_enabled -eq $true) {
  Assert-Equal ([System.IO.Path]::GetFullPath([string]$profileShimProbe.taskkill_exe)) (Join-Path (Join-Path $CodexHome 'bin\win-shims') 'taskkill.exe') 'Managed startup profile did not make taskkill.exe resolve to the cleanup shim.'
  Assert-True (([string]$profileShimProbe.pathext).StartsWith('.EXE', [System.StringComparison]::OrdinalIgnoreCase)) 'Managed startup profile did not keep .EXE prioritized for taskkill.exe cleanup-output shimming.'
}

$resolvedInstallHelper = Invoke-PowerShellCommandJson -CommandText ("& { & " + (Quote-PowerShellLiteral -Value $ProfilePath) + "; Get-Command 'omx-langgraph-install.ps1' | Select-Object Name,Source,CommandType | ConvertTo-Json -Depth 4 }")
Assert-Equal $resolvedInstallHelper.Name 'omx-langgraph-install.ps1' 'Managed startup profile block did not expose omx-langgraph-install.ps1 on PATH.'
Assert-Equal $resolvedInstallHelper.Source (Join-Path $CodexHome 'bin\omx-langgraph-install.ps1') 'Managed startup profile block resolved the wrong omx-langgraph-install.ps1 path.'
$playbookContent = Get-Content -LiteralPath (Join-Path $CodexHome 'docs\team-mode-playbook.md') -Raw
Assert-True ($playbookContent.Contains('team-mode-quick-reference.md')) 'Generated playbook does not link to the quick-reference companion.'
Assert-True ($playbookContent.Contains('completed-subagent retention is `close`')) 'Generated playbook does not describe the default completed-subagent retention policy.'
Assert-True ($playbookContent.Contains('keep the agent available until explicit close')) 'Generated playbook does not describe retention-dependent completed-subagent handling.'
Assert-True ($playbookContent.Contains('periodic progress/liveness check-ins')) 'Generated playbook does not describe periodic native-subagent progress updates.'
Assert-True ($playbookContent.Contains('omx-team-dev.ps1')) 'Generated playbook does not mention the dev team wrapper.'
Assert-True ($playbookContent.Contains('leader-side native subagents')) 'Generated playbook does not describe leader-side native subagents.'
Assert-True ($playbookContent.Contains('codex.openclaw')) 'Generated playbook does not describe the explicit non-profile wrapped codex command.'
Assert-True ($playbookContent.Contains('codex-ohmy')) 'Generated playbook does not describe the stable user-level wrapped codex command.'
Assert-True ($playbookContent.Contains('codex-native')) 'Generated playbook does not describe the native bypass command.'
Assert-True ($playbookContent.Contains('codex-raw')) 'Generated playbook does not describe the stable user-level native bypass command.'
Assert-True ($playbookContent.Contains('bug-finder')) 'Generated playbook does not mention adversarial bug-review roles.'
Assert-True ($playbookContent.Contains('generated user-level callable roles')) 'Generated playbook does not describe the burst-review triad as callable generated roles.'
Assert-True ($playbookContent.Contains('omx-team-auto.ps1')) 'Generated playbook does not mention the automatic durable-team helper.'
Assert-True ($playbookContent.Contains('codex-auto-managed-team.json')) 'Generated playbook does not mention the tracked automatic team record.'
Assert-True ($playbookContent.Contains('codex-subagent-limits.ps1')) 'Generated playbook does not mention the native subagent limits control surface.'
Assert-True ($playbookContent.Contains('omx-team-send-message.ps1')) 'Generated playbook does not mention the Windows-safe team API send-message wrapper.'
Assert-True ($playbookContent.Contains('omx-team-transition-task-status.ps1')) 'Generated playbook does not mention the Windows-safe task transition wrapper.'
Assert-True ($playbookContent.Contains('omx-team-complete-task.ps1')) 'Generated playbook does not mention the high-level complete-task wrapper.'
Assert-True ($playbookContent.Contains('omx-team-fail-task.ps1')) 'Generated playbook does not mention the high-level fail-task wrapper.'
Assert-True ($playbookContent.Contains('codex-subagent-retention-status.ps1')) 'Generated playbook does not mention the completed-subagent retention status command.'
Assert-True ($playbookContent.Contains('codex-subagent-retention-close.ps1')) 'Generated playbook does not mention the completed-subagent retention close command.'
Assert-True ($playbookContent.Contains('codex-subagent-retention-keep.ps1')) 'Generated playbook does not mention the completed-subagent retention keep command.'
Assert-True ($playbookContent.Contains('<repo>/.codex/agents/')) 'Generated playbook does not mention repository-scoped agent TOMLs.'
Assert-True ($playbookContent.Contains('OpenHands')) 'Generated playbook does not mention OpenHands terminology.'
Assert-True ($playbookContent.Contains('durable_orchestration_backend=langgraph')) 'Generated playbook does not mention the LangGraph backend selector.'
Assert-True ($playbookContent.Contains('`langgraph = on | off`')) 'Generated playbook does not describe the LangGraph capability switch.'
Assert-True ($playbookContent.Contains('codex-langgraph-on.ps1')) 'Generated playbook does not mention the LangGraph on switch.'
Assert-True ($playbookContent.Contains('omx-langgraph-install.ps1')) 'Generated playbook does not mention the LangGraph install helper.'
Assert-True ($playbookContent.Contains('omx-langgraph-cli.ps1')) 'Generated playbook does not mention the LangGraph CLI wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-run.ps1')) 'Generated playbook does not mention the LangGraph run wrapper.'
Assert-True ($playbookContent.Contains('langgraph-py312')) 'Generated playbook does not mention the shared LangGraph venv path.'
Assert-True ($playbookContent.Contains('omx-langgraph-memory.ps1')) 'Generated playbook does not mention the LangGraph memory wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-runtime.ps1')) 'Generated playbook does not mention the LangGraph runtime wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-stream.ps1')) 'Generated playbook does not mention the LangGraph stream wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-subgraphs.ps1')) 'Generated playbook does not mention the LangGraph subgraphs wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-fuller-engine.ps1')) 'Generated playbook does not mention the LangGraph fuller-engine wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-deeper-engine.ps1')) 'Generated playbook does not mention the LangGraph deeper-engine wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-superstep-engine.ps1')) 'Generated playbook does not mention the LangGraph superstep-engine wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-stateful-engine.ps1')) 'Generated playbook does not mention the LangGraph stateful-engine wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-boundary-engine.ps1')) 'Generated playbook does not mention the LangGraph boundary-engine wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-handoff-engine.ps1')) 'Generated playbook does not mention the LangGraph handoff-engine wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-approval-engine.ps1')) 'Generated playbook does not mention the LangGraph approval-engine wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-provenance-engine.ps1')) 'Generated playbook does not mention the LangGraph provenance-engine wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-artifact-engine.ps1')) 'Generated playbook does not mention the LangGraph artifact-engine wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-reducer-engine.ps1')) 'Generated playbook does not mention the LangGraph reducer-engine wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-command-engine.ps1')) 'Generated playbook does not mention the LangGraph command-engine wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-runtime-engine.ps1')) 'Generated playbook does not mention the LangGraph runtime-engine wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-memory-engine.ps1')) 'Generated playbook does not mention the LangGraph memory-engine wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-migration-engine.ps1')) 'Generated playbook does not mention the LangGraph migration-engine wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-auto-policy.ps1')) 'Generated playbook does not mention the LangGraph auto-policy wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-subgraph-state.ps1')) 'Generated playbook does not mention the LangGraph subgraph-state wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-history.ps1')) 'Generated playbook does not mention the LangGraph history wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-replay.ps1')) 'Generated playbook does not mention the LangGraph replay wrapper.'
Assert-True ($playbookContent.Contains('omx-langgraph-recover.ps1')) 'Generated playbook does not mention the LangGraph recover wrapper.'
Assert-True ($playbookContent.Contains('.omx/state/langgraph/')) 'Generated playbook does not describe the LangGraph runtime layout.'
Assert-True ($playbookContent.Contains('keep `native_omx` as the stable default')) 'Generated playbook does not declare native_omx as the stable default backend.'
Assert-True ($playbookContent.Contains('do not silently switch backend family')) 'Generated playbook does not prohibit silent backend-family switching.'
Assert-True ($playbookContent.Contains('one backend family at a time')) 'Generated playbook does not describe the one-backend-family rule.'
Assert-True ($playbookContent.Contains('primary operator-facing summary: `codex-durable-backend-status.ps1`')) 'Generated playbook does not identify the primary backend policy surface.'
Assert-True ($playbookContent.Contains('which capability layers are enabled now')) 'Generated playbook does not list the capability and lane questions the user-level surface must answer.'
Assert-True ($playbookContent.Contains('repository-local OpenSpec specs and bilingual implementation plans remain the development source of truth')) 'Generated playbook does not distinguish user-level operator authority from repository-local development authority.'
Assert-True ($playbookContent.Contains('every session reload')) 'Generated playbook does not require orchestration re-checks on session reload.'
Assert-True ($playbookContent.Contains('hard routing directives')) 'Generated playbook does not describe explicit omx/LangGraph requests as hard directives.'
Assert-True ($playbookContent.Contains('actually adopt `native_omx` or `langgraph`')) 'Generated playbook does not require actual orchestration adoption after threshold hits.'
Assert-True ($playbookContent.Contains('existing live sessions should retrofit orchestration behavior')) 'Generated playbook does not describe retrofit for existing live sessions.'
Assert-True ($playbookContent.Contains('## Global automatic collaboration default')) 'Generated playbook does not expose the global automatic collaboration section.'
Assert-True ($playbookContent.Contains('Automatic collaboration is the default behavior for all projects')) 'Generated playbook does not preserve the global automatic collaboration default.'
Assert-True ($playbookContent.Contains('platform_subagent_invocation_constraint')) 'Generated playbook does not preserve the platform subagent invocation blocker token.'
Assert-True ($playbookContent.Contains('## Global provider pacing')) 'Generated playbook does not expose the global provider pacing section.'
Assert-True ($playbookContent.Contains('10 true upstream provider forwards per rolling 1-minute window')) 'Generated playbook does not describe the global upstream pacing budget.'
Assert-True ($playbookContent.Contains('wait for a slot instead of immediately returning a local 429')) 'Generated playbook does not describe slot waiting for pacing overflow.'
Assert-True ($playbookContent.Contains('do not treat this pacing budget alone as a reason to avoid LangGraph')) 'Generated playbook does not preserve the orchestration-safe pacing interpretation.'
Assert-True ($playbookContent.Contains('codex-durable-state-status.ps1')) 'Generated playbook does not mention the canonical inspectable durable-state surface.'
Assert-True ($playbookContent.Contains('backend family, state class, tracked identity, current phase, worker shape')) 'Generated playbook does not describe the inspectable durable-state fields.'
Assert-True ($playbookContent.Contains('codex-durable-state-reconcile.ps1')) 'Generated playbook does not mention the durable-state cleanup and reconciliation helper.'
Assert-True ($playbookContent.Contains('only removes explicitly safe cleanup candidates')) 'Generated playbook does not preserve the narrow safe-cleanup boundary.'
Assert-True ($playbookContent.Contains('## Advanced compose mode')) 'Generated playbook does not expose the advanced compose mode section.'
Assert-True ($playbookContent.Contains('omx-team-compose.ps1')) 'Generated playbook does not mention the compose entrypoint.'
Assert-True ($playbookContent.Contains('compose-manifest.schema.json')) 'Generated playbook does not mention the compose manifest schema.'
Assert-True ($playbookContent.Contains('launch supported pane roles')) 'Generated playbook does not describe supported compose launch behavior.'
Assert-True ($playbookContent.Contains('planned-only entries')) 'Generated playbook does not describe planned-only unsupported panes during compose apply.'
Assert-True ($playbookContent.Contains('current-compose-runtime.json')) 'Generated playbook does not mention tracked compose runtime state.'
Assert-True ($playbookContent.Contains('omx-team-compose-status.ps1')) 'Generated playbook does not mention the compose status helper.'
Assert-True ($playbookContent.Contains('omx-team-compose-await.ps1')) 'Generated playbook does not mention the compose await helper.'
Assert-True ($playbookContent.Contains('omx-team-compose-recover.ps1')) 'Generated playbook does not mention the compose recover helper.'
Assert-True ($playbookContent.Contains('omx-team-compose-shutdown.ps1')) 'Generated playbook does not mention the compose shutdown helper.'
Assert-True ($playbookContent.Contains('omx-team-compose-reconcile.ps1')) 'Generated playbook does not mention the compose reconcile helper.'
Assert-True ($playbookContent.Contains('partial compose runtime state is explicit')) 'Generated playbook does not describe explicit partial compose state semantics.'
Assert-True ($playbookContent.Contains('compose recovery posture is explicit')) 'Generated playbook does not describe explicit compose recovery posture semantics.'
Assert-True ($playbookContent.Contains('## Analyst fan-out first for bounded research')) 'Generated playbook does not expose the analyst-fanout-first bounded research section.'
Assert-True ($playbookContent.Contains('homogeneous `analyst` fan-out is the default first research round')) 'Generated playbook does not describe homogeneous analyst fan-out as the first bounded research round.'
Assert-True ($playbookContent.Contains('`architect`, `planner`, and `writer` are not default first-round roles')) 'Generated playbook does not describe architect/planner/writer as post-fan-in bounded research roles.'

$quickReferenceContent = Get-Content -LiteralPath (Join-Path $CodexHome 'docs\team-mode-quick-reference.md') -Raw
Assert-True ($quickReferenceContent.Contains('# Team Mode Quick Reference')) 'Generated quick-reference card has the wrong title.'
Assert-True ($quickReferenceContent.Contains('## Global Automatic Collaboration Default')) 'Generated quick-reference card does not expose the global automatic collaboration default section.'
Assert-True ($quickReferenceContent.Contains('Automatic collaboration is on by default for all projects')) 'Generated quick-reference card does not preserve the global automatic collaboration default.'
Assert-True ($quickReferenceContent.Contains('platform_subagent_invocation_constraint')) 'Generated quick-reference card does not preserve the platform subagent invocation blocker token.'
Assert-True ($quickReferenceContent.Contains('## Analyst Fan-out First')) 'Generated quick-reference card does not expose analyst-fanout-first guidance.'
Assert-True ($quickReferenceContent.Contains('bounded multi-face research first uses homogeneous `analyst` fan-out')) 'Generated quick-reference card does not describe homogeneous analyst fan-out first.'
Assert-True ($quickReferenceContent.Contains('## 10 Common Commands')) 'Generated quick-reference card does not expose the common-commands section.'
Assert-True ($quickReferenceContent.Contains('codex.openclaw --version')) 'Generated quick-reference card does not include the explicit non-profile wrapped codex command.'
Assert-True ($quickReferenceContent.Contains('codex-ohmy --version')) 'Generated quick-reference card does not include the stable user-level wrapped codex command.'
Assert-True ($quickReferenceContent.Contains('codex-routing-policy.ps1 -Json')) 'Generated quick-reference card does not include routing-policy inspection.'
Assert-True ($quickReferenceContent.Contains('completed_subagent_retention=close')) 'Generated quick-reference card does not expose the completed-subagent retention default.'
Assert-True ($quickReferenceContent.Contains('codex-subagent-retention-status.ps1 -Json')) 'Generated quick-reference card does not include the completed-subagent retention status command.'
Assert-True ($quickReferenceContent.Contains('codex-subagent-retention-close.ps1 -Json')) 'Generated quick-reference card does not include the completed-subagent retention close command.'
Assert-True ($quickReferenceContent.Contains('codex-subagent-retention-keep.ps1 -Json')) 'Generated quick-reference card does not include the completed-subagent retention keep command.'
Assert-True ($quickReferenceContent.Contains('omx-team-send-message.ps1 -TeamName <team> -FromWorker <worker> -ToWorker leader-fixed -Body "ACK" -Json')) 'Generated quick-reference card does not include the Windows-safe send-message wrapper.'
Assert-True ($quickReferenceContent.Contains('omx-team-transition-task-status.ps1 -TeamName <team> -TaskId <id> -From in_progress -To completed -ClaimToken <token> -Result "done" -Json')) 'Generated quick-reference card does not include the Windows-safe transition wrapper.'
Assert-True ($quickReferenceContent.Contains('omx-team-complete-task.ps1 -TeamName <team> -TaskId <id> -Worker <worker> -ClaimToken <token> -Result "done" -Json')) 'Generated quick-reference card does not include the high-level complete-task wrapper.'
Assert-True ($quickReferenceContent.Contains('omx-team-fail-task.ps1 -TeamName <team> -TaskId <id> -Worker <worker> -ClaimToken <token> -Error "reason" -Json')) 'Generated quick-reference card does not include the high-level fail-task wrapper.'
Assert-True ($quickReferenceContent.Contains('## Native Subagent Wait Heuristic')) 'Generated quick-reference card does not include the native-subagent wait heuristic section.'
Assert-True ($quickReferenceContent.Contains('about every 30s or at major milestones')) 'Generated quick-reference card does not describe periodic native-subagent progress updates.'
Assert-True ($quickReferenceContent.Contains('codex-durable-state-status.ps1 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include durable-state inspection.'
Assert-True ($quickReferenceContent.Contains('codex-durable-state-reconcile.ps1 -RepoRoot <repo> -Apply -Json')) 'Generated quick-reference card does not include cleanup apply guidance.'
Assert-True ($quickReferenceContent.Contains('omx-team-auto.ps1 -Task "<task>" -Phase execute-parallel -ParallelSlices 2 -Apply -Json')) 'Generated quick-reference card does not include the automatic native OMX launch example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-run.ps1 -Task "<task>" -Phase define-target -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph run example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-install.ps1 -DryRun -Json')) 'Generated quick-reference card does not include the LangGraph install helper example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-cli.ps1 --help')) 'Generated quick-reference card does not include the LangGraph CLI wrapper example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-history.ps1 -ThreadId <thread-id> -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph history example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-subgraphs.ps1 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph subgraphs example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-fuller-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph fuller-engine example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-deeper-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph deeper-engine example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-superstep-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph superstep-engine example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-stateful-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph stateful-engine example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-boundary-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph boundary-engine example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-handoff-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph handoff-engine example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-approval-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph approval-engine example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-provenance-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph provenance-engine example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-artifact-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph artifact-engine example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-reducer-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph reducer-engine example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-command-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph command-engine example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-runtime-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph runtime-engine example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-memory-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph memory-engine example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-migration-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph migration-engine example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-auto-policy.ps1 -ThreadId <thread-id> -Apply -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph auto-policy example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-subgraph-state.ps1 -ThreadId <thread-id> -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph subgraph-state example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-memory.ps1 -ThreadId <thread-id> -MemoryStoreConfigured')) 'Generated quick-reference card does not include the LangGraph memory example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-runtime.ps1 -ThreadId <thread-id> -ContextSchema operator_context')) 'Generated quick-reference card does not include the LangGraph runtime example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-stream.ps1 -ThreadId <thread-id> -StreamMode updates,debug -Subgraphs')) 'Generated quick-reference card does not include the LangGraph stream example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-runtime.ps1 -ThreadId <thread-id> -ContextSchema operator_context')) 'Generated quick-reference card does not include the LangGraph runtime example.'
Assert-True ($quickReferenceContent.Contains('-CommandKind parent_handoff -CommandGraphScope parent')) 'Generated quick-reference card does not include the command-driven LangGraph resume example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-replay.ps1 -ThreadId <thread-id> -TargetId <target-id> -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph replay example.'
Assert-True ($quickReferenceContent.Contains('omx-langgraph-recover.ps1 -ThreadId <thread-id> -MutationIntent explicit-recovery -TargetId <target-id> -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include the LangGraph time-travel recovery example.'
Assert-True ($quickReferenceContent.Contains('## Compose Runtime')) 'Generated quick-reference card does not expose the compose runtime section.'
Assert-True ($quickReferenceContent.Contains('omx-team-compose-status.ps1 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include compose status guidance.'
Assert-True ($quickReferenceContent.Contains('omx-team-compose-await.ps1 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include compose await guidance.'
Assert-True ($quickReferenceContent.Contains('omx-team-compose-recover.ps1 -RepoRoot <repo> -Json')) 'Generated quick-reference card does not include compose recovery guidance.'
Assert-True ($quickReferenceContent.Contains('omx-team-compose-shutdown.ps1 -RepoRoot <repo> -Apply -Json')) 'Generated quick-reference card does not include compose shutdown guidance.'
Assert-True ($quickReferenceContent.Contains('omx-team-compose-reconcile.ps1 -RepoRoot <repo> -Apply -Json')) 'Generated quick-reference card does not include compose reconcile guidance.'

$composeSchemaContent = Get-Content -LiteralPath (Join-Path $CodexHome 'teams\compose-manifest.schema.json') -Raw
Assert-True ($composeSchemaContent.Contains('OMX Team Compose Manifest')) 'Generated compose manifest schema has the wrong title.'
Assert-True ($composeSchemaContent.Contains('"advanced_opt_in"')) 'Generated compose manifest schema does not require the advanced opt-in flag.'
$composeManifestPath = Join-Path $TempRoot 'compose-manifest.json'
Set-Content -LiteralPath $composeManifestPath -Encoding ASCII -NoNewline -Value @'
{
  "schema_version": 1,
  "advanced_opt_in": true,
  "leader": {
    "outside_pane_roster": true
  },
  "panes": [
    {
      "name": "exec-pane",
      "role": "executor",
      "workers": 2,
      "worktree": "wt-exec",
      "mailbox": "exec-box",
      "task": "ship feature slice"
    },
    {
      "name": "architect-pane",
      "role": "architect",
      "workers": 1,
      "worktree": "wt-arch",
      "mailbox": "arch-box",
      "write_scope": ["docs/"]
    }
  ]
}
'@

$composePreview = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-compose.ps1') -Arguments @(
  '-ManifestPath', $composeManifestPath,
  '-RepoRoot', $ComposeRepoRoot,
  '-Json'
)
Assert-True ($composePreview.advanced_opt_in -eq $true) 'Compose wrapper did not preserve advanced opt-in mode.'
Assert-True ($composePreview.leader_outside_pane_roster -eq $true) 'Compose wrapper did not preserve leader-outside-pane-roster.'
Assert-Equal ([int]$composePreview.pane_count) 2 'Compose wrapper reported the wrong pane count.'
Assert-True ($composePreview.apply_supported_for_all_panes -eq $false) 'Compose wrapper should not claim full apply support when unsupported pane roles exist.'
$composeUnsupportedRoles = @($composePreview.unsupported_panes | ForEach-Object { [string]$_.role })
Assert-ArrayContains -Actual $composeUnsupportedRoles -Expected 'architect' -Message 'Compose wrapper did not classify unsupported persistent expert panes correctly.'

$composeApply = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-compose.ps1') -Arguments @(
  '-ManifestPath', $composeManifestPath,
  '-RepoRoot', $ComposeRepoRoot,
  '-Apply',
  '-Json'
)
Assert-Equal $composeApply.applied_mode 'supported_launch_with_planned_only' 'Compose wrapper did not launch supported panes while preserving unsupported panes as planned-only.'
$composeStateFile = Join-Path $ComposeRepoRoot '.omx\state\compose\current-compose-plan.json'
Assert-True (Test-Path -LiteralPath $composeStateFile) 'Compose wrapper did not persist the compose state file.'
$composeRuntimeFile = Join-Path $ComposeRepoRoot '.omx\state\compose\current-compose-runtime.json'
Assert-True (Test-Path -LiteralPath $composeRuntimeFile) 'Compose wrapper did not persist the compose runtime state file.'
$composeLaunchedRoles = @($composeApply.launched_panes | ForEach-Object { [string]$_.role })
Assert-ArrayContains -Actual $composeLaunchedRoles -Expected 'executor' -Message 'Compose wrapper did not launch the supported executor pane in the mixed manifest.'
$composePlannedOnlyRoles = @($composeApply.planned_only_panes | ForEach-Object { [string]$_.role })
Assert-ArrayContains -Actual $composePlannedOnlyRoles -Expected 'architect' -Message 'Compose wrapper did not preserve unsupported panes as planned-only entries.'
$composeLaunchArgs = @($composeApply.launched_panes[0].launch_args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $composeLaunchArgs -Expected 'team' -Message 'Compose wrapper did not route supported pane launch through omx team.'
Assert-ArrayContains -Actual $composeLaunchArgs -Expected '2:executor' -Message 'Compose wrapper did not derive the supported executor launch shape correctly.'
$composeLaunchedTeamNames = @($composeApply.launched_panes | ForEach-Object { [string]$_.team_name } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
Assert-True (@($composeLaunchedTeamNames).Count -eq 1) 'Compose wrapper did not capture the launched team identity for the supported pane.'
$durableStateMixedComposeRuntime = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') -Arguments @(
  '-RepoRoot', $ComposeRepoRoot,
  '-Json'
)
Assert-Equal $durableStateMixedComposeRuntime.state_class 'tracked_compose_runtime' 'Durable-state status did not classify mixed compose runtime state correctly.'
Assert-Equal $durableStateMixedComposeRuntime.backend_specific.compose.runtime.applied_mode 'supported_launch_with_planned_only' 'Durable-state status did not expose planned-only compose runtime mode for mixed manifests.'
Assert-Equal $durableStateMixedComposeRuntime.backend_specific.compose.helper_pointers.shutdown.script 'omx-team-compose-shutdown.ps1' 'Durable-state status did not expose the compose shutdown helper pointer.'
Assert-Equal $durableStateMixedComposeRuntime.backend_specific.compose.pane_helpers[0].resume_pointer.script 'omx-team-ops.ps1' 'Durable-state status did not expose pane-level reattach guidance through omx-team-ops.ps1.'
$durableStateMixedPlannedOnlyRoles = @($durableStateMixedComposeRuntime.backend_specific.compose.runtime.planned_only_panes | ForEach-Object { [string]$_.role })
Assert-ArrayContains -Actual $durableStateMixedPlannedOnlyRoles -Expected 'architect' -Message 'Durable-state status did not preserve planned-only compose panes for mixed manifests.'

$composeStatus = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-compose-status.ps1') -Arguments @(
  '-RepoRoot', $ComposeRepoRoot,
  '-Json'
)
Assert-True ($composeStatus.runtime_exists -eq $true) 'Compose status helper did not detect the tracked compose runtime.'
Assert-Equal $composeStatus.helper_pointers.shutdown.script 'omx-team-compose-shutdown.ps1' 'Compose status helper did not expose the compose shutdown helper pointer.'
$composeStatusLaunchedRoles = @($composeStatus.launched_panes | ForEach-Object { [string]$_.role })
Assert-ArrayContains -Actual $composeStatusLaunchedRoles -Expected 'executor' -Message 'Compose status helper did not expose launched compose panes.'
$composePaneResumeScript = [string]$composeStatus.pane_helpers[0].resume_pointer.script
Assert-Equal $composePaneResumeScript 'omx-team-ops.ps1' 'Compose status helper did not expose pane-level resume guidance through omx-team-ops.ps1.'

$composeShutdownPreview = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-compose-shutdown.ps1') -Arguments @(
  '-RepoRoot', $ComposeRepoRoot,
  '-Json'
)
Assert-True ($composeShutdownPreview.runtime_exists -eq $true) 'Compose shutdown helper preview did not detect tracked compose runtime.'
Assert-Equal (@($composeShutdownPreview.targeted_panes).Count) 1 'Compose shutdown helper preview targeted the wrong number of launched panes.'

$composeShutdownApply = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-compose-shutdown.ps1') -Arguments @(
  '-RepoRoot', $ComposeRepoRoot,
  '-Apply',
  '-Json'
)
Assert-Equal $composeShutdownApply.applied_decision 'shutdown' 'Compose shutdown helper did not shut down the tracked compose runtime.'
Assert-True ($composeShutdownApply.runtime_record_removed -eq $true) 'Compose shutdown helper did not remove the tracked compose runtime record after successful shutdown.'
Assert-True (-not (Test-Path -LiteralPath $composeRuntimeFile)) 'Compose shutdown helper did not remove current-compose-runtime.json after successful shutdown.'

$composeManifestPath = Join-Path $TempRoot 'compose-manifest.json'
Set-Content -LiteralPath $composeManifestPath -Encoding ASCII -NoNewline -Value @'
{
  "schema_version": 1,
  "advanced_opt_in": true,
  "leader": {
    "outside_pane_roster": true
  },
  "panes": [
    {
      "name": "exec-pane",
      "role": "team-executor",
      "workers": 2,
      "worktree": "wt-exec",
      "mailbox": "exec-box",
      "task": "ship feature slice"
    },
    {
      "name": "debug-pane",
      "role": "debugger",
      "workers": 1,
      "worktree": "wt-debug",
      "mailbox": "debug-box",
      "task": "stabilize feature slice"
    }
  ]
}
'@

$composePreview = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-compose.ps1') -Arguments @(
  '-ManifestPath', $composeManifestPath,
  '-RepoRoot', $ComposeRepoRoot,
  '-Json'
)
Assert-True ($composePreview.advanced_opt_in -eq $true) 'Compose wrapper did not preserve advanced opt-in mode.'
Assert-True ($composePreview.leader_outside_pane_roster -eq $true) 'Compose wrapper did not preserve leader-outside-pane-roster.'
Assert-Equal ([int]$composePreview.pane_count) 2 'Compose wrapper reported the wrong pane count.'
Assert-True ($composePreview.apply_supported_for_all_panes -eq $true) 'Compose wrapper should report full apply support when all pane roles are supported.'
Assert-Equal (@($composePreview.unsupported_panes).Count) 0 'Compose wrapper incorrectly marked supported pane roles as unsupported.'

$composeApply = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-compose.ps1') -Arguments @(
  '-ManifestPath', $composeManifestPath,
  '-RepoRoot', $ComposeRepoRoot,
  '-Apply',
  '-Json'
)
Assert-Equal $composeApply.applied_mode 'supported_launch_only' 'Compose wrapper did not fully launch the supported compose pane set.'
$composeStateFile = Join-Path $ComposeRepoRoot '.omx\state\compose\current-compose-plan.json'
Assert-True (Test-Path -LiteralPath $composeStateFile) 'Compose wrapper did not persist the compose state file.'
Assert-True (Test-Path -LiteralPath $composeRuntimeFile) 'Compose wrapper did not persist the compose runtime state file for a supported-only manifest.'
$composeSupportedLaunchRoles = @($composeApply.launched_panes | ForEach-Object { [string]$_.role })
Assert-ArrayContains -Actual $composeSupportedLaunchRoles -Expected 'team-executor' -Message 'Compose wrapper did not launch the supported team-executor pane.'
Assert-ArrayContains -Actual $composeSupportedLaunchRoles -Expected 'debugger' -Message 'Compose wrapper did not launch the supported debugger pane.'
Assert-Equal (@($composeApply.planned_only_panes).Count) 0 'Compose wrapper should not leave any planned-only panes when all pane roles are supported.'
Assert-Equal (@($composeApply.failed_panes).Count) 0 'Compose wrapper should not report failed panes for a supported-only manifest.'

$durableStateComposeRuntime = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') -Arguments @(
  '-RepoRoot', $ComposeRepoRoot,
  '-Json'
)
Assert-Equal $durableStateComposeRuntime.state_class 'tracked_compose_runtime' 'Durable-state status did not classify tracked compose runtime state correctly.'
Assert-Equal $durableStateComposeRuntime.backend_family 'native_omx' 'Durable-state status did not project compose runtime as native_omx-backed durable state.'
Assert-Equal $durableStateComposeRuntime.inspect_pointer.script 'codex-durable-state-status.ps1' 'Durable-state status did not preserve canonical inspection for compose runtime state.'
Assert-Equal $durableStateComposeRuntime.backend_specific.compose.runtime.applied_mode 'supported_launch_only' 'Durable-state status did not expose compose runtime apply mode.'
$composeRecoverHealthy = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-compose-recover.ps1') -Arguments @(
  '-RepoRoot', $ComposeRepoRoot,
  '-Json'
)
Assert-Equal $composeRecoverHealthy.recovery_posture 'resumable' 'Compose recover helper did not classify a healthy compose runtime as resumable.'
Assert-True ($composeRecoverHealthy.read_only_by_default -eq $true) 'Compose recover helper did not preserve read-only-by-default behavior.'
Assert-Equal (@($composeRecoverHealthy.resumable_panes).Count) 2 'Compose recover helper reported the wrong resumable pane count for a healthy compose runtime.'
$composeRuntimeLaunchRoles = @($durableStateComposeRuntime.backend_specific.compose.runtime.launched_panes | ForEach-Object { [string]$_.role })
Assert-ArrayContains -Actual $composeRuntimeLaunchRoles -Expected 'team-executor' -Message 'Durable-state status did not expose launched team-executor compose runtime panes.'
Assert-ArrayContains -Actual $composeRuntimeLaunchRoles -Expected 'debugger' -Message 'Durable-state status did not expose launched debugger compose panes.'

$firstComposeTeamName = [string]$composeApply.launched_panes[0].team_name
$firstComposeTeamDirectory = Join-Path $ComposeRepoRoot ('.omx\state\team\' + $firstComposeTeamName)
if (Test-Path -LiteralPath $firstComposeTeamDirectory) {
  Remove-Item -LiteralPath $firstComposeTeamDirectory -Recurse -Force
}

$composeAwait = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-compose-await.ps1') -Arguments @(
  '-RepoRoot', $ComposeRepoRoot,
  '-Json'
)
Assert-True ($composeAwait.runtime_exists -eq $true) 'Compose await helper did not detect tracked compose runtime.'
Assert-Equal $composeAwait.lifecycle_state 'partial_shutdown' 'Compose await helper did not classify partial compose shutdown state correctly.'
Assert-Equal $composeAwait.health_state 'partial_health' 'Compose await helper did not classify partial compose health correctly.'
Assert-Equal $composeAwait.await_state 'partial' 'Compose await helper did not classify aggregate await state correctly.'
Assert-Equal (@($composeAwait.active_panes).Count) 1 'Compose await helper reported the wrong active pane count during partial shutdown.'
Assert-Equal (@($composeAwait.missing_panes).Count) 1 'Compose await helper reported the wrong missing pane count during partial shutdown.'
$composeRecoverPartial = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-compose-recover.ps1') -Arguments @(
  '-RepoRoot', $ComposeRepoRoot,
  '-Json'
)
Assert-Equal $composeRecoverPartial.recovery_posture 'degraded_recoverable' 'Compose recover helper did not classify partial compose runtime as degraded_recoverable.'
Assert-Equal (@($composeRecoverPartial.resumable_panes).Count) 1 'Compose recover helper reported the wrong resumable pane count during degraded recovery.'
Assert-Equal (@($composeRecoverPartial.non_resumable_panes).Count) 1 'Compose recover helper reported the wrong non-resumable pane count during degraded recovery.'

$durableStatePartialComposeRuntime = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') -Arguments @(
  '-RepoRoot', $ComposeRepoRoot,
  '-Json'
)
Assert-Equal $durableStatePartialComposeRuntime.inspect_pointer.script 'omx-team-compose-await.ps1' 'Durable-state status did not point partial compose runtime inspection to the compose await helper.'
Assert-Equal $durableStatePartialComposeRuntime.resume_pointer.script 'omx-team-compose-recover.ps1' 'Durable-state status did not point partial compose runtime recovery to the compose recover helper.'
Assert-Equal $durableStatePartialComposeRuntime.backend_specific.compose.lifecycle_state 'partial_shutdown' 'Durable-state status did not expose partial compose lifecycle state.'
Assert-Equal $durableStatePartialComposeRuntime.backend_specific.compose.await_state 'partial' 'Durable-state status did not expose partial compose await state.'
Assert-Equal $durableStatePartialComposeRuntime.backend_specific.compose.helper_pointers.await.script 'omx-team-compose-await.ps1' 'Durable-state status did not expose the compose await helper pointer.'
Assert-Equal $durableStatePartialComposeRuntime.backend_specific.compose.helper_pointers.recover.script 'omx-team-compose-recover.ps1' 'Durable-state status did not expose the compose recover helper pointer.'
Assert-Equal $durableStatePartialComposeRuntime.backend_specific.compose.recovery_posture 'degraded_recoverable' 'Durable-state status did not expose degraded compose recovery posture.'

foreach ($launchedPane in @($composeApply.launched_panes)) {
  $teamName = [string]$launchedPane.team_name
  if (-not [string]::IsNullOrWhiteSpace($teamName)) {
    $teamDirectory = Join-Path $ComposeRepoRoot ('.omx\state\team\' + $teamName)
    if (Test-Path -LiteralPath $teamDirectory) {
      Remove-Item -LiteralPath $teamDirectory -Recurse -Force
    }
  }
}
$composeRecoverMissing = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-compose-recover.ps1') -Arguments @(
  '-RepoRoot', $ComposeRepoRoot,
  '-Json'
)
Assert-Equal $composeRecoverMissing.recovery_posture 'manual_intervention_required' 'Compose recover helper did not classify fully missing launched panes as manual_intervention_required.'
Assert-Equal (@($composeRecoverMissing.resumable_panes).Count) 0 'Compose recover helper should not report resumable panes when all launched panes are missing.'

$composeReconcilePreview = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-compose-reconcile.ps1') -Arguments @(
  '-RepoRoot', $ComposeRepoRoot,
  '-Json'
)
Assert-True ($composeReconcilePreview.safe_cleanup_available -eq $true) 'Compose reconcile helper did not expose stale compose runtime as a safe cleanup candidate.'
$composeReconcileKinds = @($composeReconcilePreview.safe_cleanup_candidates | ForEach-Object { [string]$_.kind })
Assert-ArrayContains -Actual $composeReconcileKinds -Expected 'stale_compose_runtime_record' -Message 'Compose reconcile helper did not classify stale compose runtime residue correctly.'

$genericCleanupPreview = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-reconcile.ps1') -Arguments @(
  '-RepoRoot', $ComposeRepoRoot,
  '-Json'
)
$genericCleanupKinds = @($genericCleanupPreview.safe_cleanup_candidates | ForEach-Object { [string]$_.kind })
Assert-ArrayContains -Actual $genericCleanupKinds -Expected 'stale_compose_runtime_record' -Message 'Generic durable-state reconcile helper did not include stale compose runtime residue.'

$composeReconcileApply = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-compose-reconcile.ps1') -Arguments @(
  '-RepoRoot', $ComposeRepoRoot,
  '-Apply',
  '-Json'
)
Assert-Equal (@($composeReconcileApply.applied_actions).Count) 1 'Compose reconcile helper did not remove the expected stale compose runtime record.'
Assert-True (-not (Test-Path -LiteralPath $composeRuntimeFile)) 'Compose reconcile helper did not remove current-compose-runtime.json.'
Assert-True (Test-Path -LiteralPath $composeStateFile) 'Compose reconcile helper should preserve current-compose-plan.json when cleaning stale compose runtime residue.'
$durableStateAfterComposeReconcile = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') -Arguments @(
  '-RepoRoot', $ComposeRepoRoot,
  '-Json'
)
Assert-Equal $durableStateAfterComposeReconcile.state_class 'no_durable_state' 'Durable-state status did not return to no_durable_state after compose runtime cleanup.'

$nativeSubagentLimits = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-subagent-limits.ps1') -Arguments @(
  '-Json'
)
Assert-Equal ([int]$nativeSubagentLimits.max_threads) 6 'Native subagent limits script reported the wrong default max_threads.'
Assert-Equal ([int]$nativeSubagentLimits.max_depth) 1 'Native subagent limits script reported the wrong default max_depth.'

$updatedNativeSubagentLimits = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-subagent-limits.ps1') -Arguments @(
  '-MaxThreads', '4',
  '-MaxDepth', '2',
  '-Json'
)
Assert-Equal ([int]$updatedNativeSubagentLimits.max_threads) 4 'Native subagent limits script did not update max_threads.'
Assert-Equal ([int]$updatedNativeSubagentLimits.max_depth) 2 'Native subagent limits script did not update max_depth.'

$devLaunch = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-dev.ps1') -Arguments @(
  '-Task', 'ship feature'
)
$devLaunchArgs = @($devLaunch.args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $devLaunchArgs -Expected 'team' -Message 'Dev wrapper did not route through omx team.'
Assert-ArrayContains -Actual $devLaunchArgs -Expected '2:team-executor' -Message 'Dev wrapper did not use the conservative default role.'
Assert-ArrayContains -Actual $devLaunchArgs -Expected 'ship feature' -Message 'Dev wrapper did not forward the task.'

$debugLaunch = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-debug.ps1') -Arguments @(
  '-Task', 'stabilize regression'
)
$debugLaunchArgs = @($debugLaunch.args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $debugLaunchArgs -Expected '2:debugger' -Message 'Debug wrapper did not use the debugger preset.'
Assert-ArrayContains -Actual $debugLaunchArgs -Expected 'stabilize regression' -Message 'Debug wrapper did not forward the task.'

$olderTeamPath = Join-Path $FakeRepoRoot '.omx\state\team\older-team'
$newerTeamPath = Join-Path $FakeRepoRoot '.omx\state\team\newer-team'
Ensure-Directory -Path $olderTeamPath
Start-Sleep -Milliseconds 1100
Ensure-Directory -Path $newerTeamPath

$opsStatus = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-ops.ps1') -Arguments @(
  '-Action', 'status',
  '-RepoRoot', $FakeRepoRoot,
  '-Json'
)
$opsStatusArgs = @($opsStatus.args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $opsStatusArgs -Expected 'status' -Message 'Ops wrapper did not call team status.'
Assert-ArrayContains -Actual $opsStatusArgs -Expected 'newer-team' -Message 'Ops wrapper did not discover the latest team directory.'
Assert-ArrayContains -Actual $opsStatusArgs -Expected '--json' -Message 'Ops wrapper did not forward the JSON flag for team status.'

$opsListTasks = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-ops.ps1') -Arguments @(
  '-Action', 'list-tasks',
  '-TeamName', 'manual-team'
)
$opsListTaskArgs = @($opsListTasks.args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $opsListTaskArgs -Expected 'api' -Message 'Ops wrapper did not route read-only inspection through team api.'
Assert-ArrayContains -Actual $opsListTaskArgs -Expected 'list-tasks' -Message 'Ops wrapper did not select the list-tasks operation.'
Assert-ArrayContains -Actual $opsListTaskArgs -Expected '--json' -Message 'Ops wrapper did not request JSON output for list-tasks.'
$opsListTaskInput = @($opsListTaskArgs | Where-Object { $_ -like '*manual-team*' } | Select-Object -First 1)[0]
Assert-True ($opsListTaskInput.Contains('"team_name":"manual-team"')) 'Ops wrapper did not encode the team API input payload correctly.'

$safeSend = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-send-message.ps1') -Arguments @(
  '-TeamName', 'manual-team',
  '-FromWorker', 'worker-1',
  '-ToWorker', 'leader-fixed',
  '-Body', 'ACK',
  '-Json'
)
$safeSendArgs = @($safeSend.args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $safeSendArgs -Expected 'send-message' -Message 'Safe send-message wrapper did not select the send-message operation.'
$safeSendInput = @($safeSendArgs | Where-Object { $_ -like '*manual-team*' } | Select-Object -First 1)[0]
Assert-True ($safeSendInput.Contains('"from_worker":"worker-1"') -and $safeSendInput.Contains('"to_worker":"leader-fixed"')) 'Safe send-message wrapper did not encode the payload correctly.'

$safeMailboxList = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-mailbox-list.ps1') -Arguments @(
  '-TeamName', 'manual-team',
  '-Worker', 'worker-1',
  '-Json'
)
$safeMailboxListArgs = @($safeMailboxList.args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $safeMailboxListArgs -Expected 'mailbox-list' -Message 'Safe mailbox-list wrapper did not select the mailbox-list operation.'

$safeTransition = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-transition-task-status.ps1') -Arguments @(
  '-TeamName', 'manual-team',
  '-TaskId', '1',
  '-From', 'in_progress',
  '-To', 'completed',
  '-ClaimToken', 'token-1',
  '-Result', 'done',
  '-Json'
)
$safeTransitionArgs = @($safeTransition.args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $safeTransitionArgs -Expected 'transition-task-status' -Message 'Safe transition-task-status wrapper did not select the transition operation.'
$safeTransitionInput = @($safeTransitionArgs | Where-Object { $_ -like '*token-1*' } | Select-Object -First 1)[0]
Assert-True ($safeTransitionInput.Contains('"claim_token":"token-1"') -and $safeTransitionInput.Contains('"to":"completed"')) 'Safe transition-task-status wrapper did not encode the payload correctly.'

$safeProgress = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-report-progress.ps1') -Arguments @(
  '-TeamName', 'manual-team',
  '-Worker', 'worker-1',
  '-TaskId', '1',
  '-Body', 'working',
  '-RepoRoot', $FakeRepoRoot,
  '-Json'
)
Assert-Equal $safeProgress.operation 'report-progress' 'High-level progress wrapper reported the wrong operation.'
Assert-Equal $safeProgress.status.state 'working' 'High-level progress wrapper did not write a working status payload.'
Assert-Equal $safeProgress.notify.input.team_name 'manual-team' 'High-level progress wrapper did not route the notify payload through the safe send wrapper.'

$safeComplete = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-complete-task.ps1') -Arguments @(
  '-TeamName', 'manual-team',
  '-TaskId', '1',
  '-Worker', 'worker-1',
  '-ClaimToken', 'token-1',
  '-Result', 'done',
  '-RepoRoot', $FakeRepoRoot,
  '-Json'
)
Assert-Equal $safeComplete.operation 'complete-task' 'High-level complete wrapper reported the wrong operation.'
Assert-Equal $safeComplete.transition.input.to 'completed' 'High-level complete wrapper did not transition the task to completed.'
Assert-Equal $safeComplete.notify.input.to_worker 'leader-fixed' 'High-level complete wrapper did not notify the leader.'

$safeFail = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-fail-task.ps1') -Arguments @(
  '-TeamName', 'manual-team',
  '-TaskId', '1',
  '-Worker', 'worker-1',
  '-ClaimToken', 'token-1',
  '-Error', 'broken',
  '-RepoRoot', $FakeRepoRoot,
  '-Json'
)
Assert-Equal $safeFail.operation 'fail-task' 'High-level fail wrapper reported the wrong operation.'
Assert-Equal $safeFail.transition.input.to 'failed' 'High-level fail wrapper did not transition the task to failed.'
Assert-Equal $safeFail.notify.input.body 'Failed task 1: broken' 'High-level fail wrapper did not build the expected default failure message.'

$hybridPlan = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-hybrid.ps1') -Arguments @(
  '-Task', 'implement rollout',
  '-Architect', '1',
  '-Planner', '1',
  '-Executor', '2',
  '-Verifier', '1',
  '-Json'
)
Assert-Equal $hybridPlan.durable_team.worker_role 'team-executor' 'Hybrid wrapper produced the wrong default durable worker role.'
$hybridExpertNames = @($hybridPlan.leader_side_experts | ForEach-Object { [string]$_.name })
Assert-ArrayContains -Actual $hybridExpertNames -Expected 'architect' -Message 'Hybrid wrapper did not preserve architect as a leader-side expert.'
Assert-ArrayContains -Actual $hybridExpertNames -Expected 'planner' -Message 'Hybrid wrapper did not preserve planner as a leader-side expert.'
Assert-ArrayContains -Actual $hybridExpertNames -Expected 'verifier' -Message 'Hybrid wrapper did not preserve verifier as a leader-side expert.'

$hybridLaunch = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-hybrid.ps1') -Arguments @(
  '-Task', 'implement rollout',
  '-Architect', '1',
  '-Planner', '1',
  '-Executor', '2',
  '-Verifier', '1',
  '-Launch',
  '-Json'
)
$hybridLaunchArgs = @($hybridLaunch.launch_args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $hybridLaunchArgs -Expected 'team' -Message 'Hybrid wrapper did not derive an omx team launch.'
Assert-ArrayContains -Actual $hybridLaunchArgs -Expected '2:team-executor' -Message 'Hybrid wrapper did not derive the default durable worker swarm.'

$verifyPlan = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-verify.ps1') -Arguments @(
  '-Task', 'final acceptance',
  '-NeedsSecurityReview',
  '-NeedsDocsReview',
  '-Json'
)
Assert-True ($verifyPlan.persistent_verifier_team_default -eq $false) 'Verify wrapper should not default to a persistent verifier team.'
$verifyRoleNames = @($verifyPlan.verification_roles | ForEach-Object { [string]$_.name })
Assert-ArrayContains -Actual $verifyRoleNames -Expected 'verifier' -Message 'Verify wrapper did not include verifier in the leader-side verification plan.'
Assert-ArrayContains -Actual $verifyRoleNames -Expected 'test-engineer' -Message 'Verify wrapper did not include test-engineer in the leader-side verification plan.'
Assert-ArrayContains -Actual $verifyRoleNames -Expected 'security-reviewer' -Message 'Verify wrapper did not include security-reviewer when requested.'
Assert-ArrayContains -Actual $verifyRoleNames -Expected 'writer' -Message 'Verify wrapper did not include writer when docs review was requested.'

$wrappedNativeRouted = Invoke-PowerShellCommandJson -CommandText ("& { & " + (Quote-PowerShellLiteral -Value $ProfilePath) + "; codex 'user-task' }")
$wrappedNativeRoutedArgs = @($wrappedNativeRouted.args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $wrappedNativeRoutedArgs -Expected 'mcp_servers.omx_state.enabled=false' -Message 'Wrapped native-mode launch did not disable omx_state.'
Assert-ArrayContains -Actual $wrappedNativeRoutedArgs -Expected 'notify=[]' -Message 'Wrapped native-mode launch did not disable notify.'
Assert-ArrayContains -Actual $wrappedNativeRoutedArgs -Expected 'user-task' -Message 'Wrapped native-mode launch did not forward the user argument.'
Assert-ArrayContains -Actual $wrappedNativeRoutedArgs -Expected 'agents.max_threads=4' -Message 'Wrapped native-mode launch did not forward the managed max_threads value.'
Assert-ArrayContains -Actual $wrappedNativeRoutedArgs -Expected 'agents.max_depth=2' -Message 'Wrapped native-mode launch did not forward the managed max_depth value.'
Assert-True ('--disable' -notin $wrappedNativeRoutedArgs) 'Native routed launch should not disable multi_agent.'
$modelInstructionsArg = @($wrappedNativeRoutedArgs | Where-Object { $_ -like 'model_instructions_file=*' } | Select-Object -First 1)[0]
Assert-True (-not [string]::IsNullOrWhiteSpace($modelInstructionsArg)) 'Wrapped native-mode launch did not inject model_instructions_file.'
Assert-True ($modelInstructionsArg -notmatch "`r|`n") 'Wrapped native-mode launch should not pass raw newlines in model_instructions_file.'
$modelInstructionsPath = $modelInstructionsArg.Substring('model_instructions_file='.Length).Trim('"').Replace('\\', '\')
Assert-Equal $modelInstructionsPath (Join-Path $CodexHome 'state\user-level-team-mode-model-instructions.md') 'Wrapped native-mode launch did not point at the expected model instructions file.'
Assert-True (Test-Path -LiteralPath $modelInstructionsPath) 'Wrapped native-mode launch did not create the model instructions file.'
$modelInstructionsContent = Get-Content -LiteralPath $modelInstructionsPath -Raw
Assert-True ($modelInstructionsContent.Contains('wrapped native Codex mode with automatic native subagent routing')) 'Wrapped native-mode launch did not describe wrapped native-routed startup.'
Assert-True ($modelInstructionsContent.Contains('Completed subagent retention policy: close.')) 'Wrapped native-mode launch did not describe the completed-subagent retention policy.'
Assert-True ($modelInstructionsContent.Contains('close the agent by default')) 'Wrapped native-mode launch did not require closing completed agents after fan-in.'
Assert-True ($modelInstructionsContent.Contains('single `wait_agent` call')) 'Wrapped native-mode launch did not require bounded wait windows.'
Assert-True ($modelInstructionsContent.Contains('progress/liveness updates about every 30s')) 'Wrapped native-mode launch did not require periodic native-subagent progress updates.'
Assert-True ($modelInstructionsContent.Contains('current step, completed work, next step, and blockers')) 'Wrapped native-mode launch did not require progress updates to include useful liveness detail.'
Assert-True ($modelInstructionsContent.Contains('analyst: unclear outcome')) 'Wrapped native-mode launch did not include analyst routing thresholds.'
Assert-True ($modelInstructionsContent.Contains('Analyst-fanout-first task class: bounded_multi_face_research')) 'Wrapped native-mode launch did not describe analyst-fanout-first task class.'
Assert-True ($modelInstructionsContent.Contains('do not include `architect`, `planner`, or `writer` as default first-round research roles')) 'Wrapped native-mode launch did not delay architect/planner/writer until after analyst fan-in.'
Assert-True ($modelInstructionsContent.Contains('Automatic collaboration is the default for all projects')) 'Wrapped native-mode launch did not preserve the global automatic collaboration default.'
Assert-True ($modelInstructionsContent.Contains('platform_subagent_invocation_constraint')) 'Wrapped native-mode launch did not preserve the platform subagent invocation blocker token.'
Assert-True ($modelInstructionsContent.Contains('bug-finder / bug-rebutter / bug-judge')) 'Wrapped native-mode launch did not include adversarial bug-review thresholds.'
Assert-True ($modelInstructionsContent.Contains('Installed burst-review roles: bug-finder, bug-rebutter, bug-judge')) 'Wrapped native-mode launch did not mention the installed burst-review roles.'

$wrappedNativeVersion = Invoke-PowerShellCommandJson -CommandText ("& { & " + (Quote-PowerShellLiteral -Value $ProfilePath) + "; codex --version }")
$wrappedNativeVersionArgs = @($wrappedNativeVersion.args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $wrappedNativeVersionArgs -Expected '--version' -Message 'Wrapped launch did not forward --version through the profile binding and launcher.'

$wrappedNativeBypass = Invoke-PowerShellCommandJson -CommandText ("& { & " + (Quote-PowerShellLiteral -Value $ProfilePath) + "; codex-native 'user-task' }")
$wrappedNativeBypassArgs = @($wrappedNativeBypass.args | ForEach-Object { [string]$_ })
Assert-Equal ($wrappedNativeBypassArgs -join ',') 'user-task' 'codex-native should bypass all launcher-injected arguments.'

$explicitWrappedLaunch = Invoke-PowerShellScriptJson -FilePath $ExplicitWrappedCodexPs1Path -Arguments @(
  '--version'
)
$explicitWrappedLaunchArgs = @($explicitWrappedLaunch.args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $explicitWrappedLaunchArgs -Expected '--version' -Message 'Explicit non-profile wrapped launcher did not forward --version.'

$explicitNativeBypass = Invoke-PowerShellScriptJson -FilePath $ExplicitNativeBypassPs1Path -Arguments @(
  'user-task'
)
$explicitNativeBypassArgs = @($explicitNativeBypass.args | ForEach-Object { [string]$_ })
Assert-Equal ($explicitNativeBypassArgs -join ',') 'user-task' 'Explicit non-profile native bypass launcher should bypass all wrapper-injected arguments.'

$stableWrappedLaunch = Invoke-PowerShellScriptJson -FilePath $StableWrappedCodexPs1Path -Arguments @(
  '--version'
)
$stableWrappedLaunchArgs = @($stableWrappedLaunch.args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $stableWrappedLaunchArgs -Expected '--version' -Message 'Stable user-level wrapped launcher did not forward --version.'

$stableNativeBypass = Invoke-PowerShellScriptJson -FilePath $StableNativeBypassPs1Path -Arguments @(
  'user-task'
)
$stableNativeBypassArgs = @($stableNativeBypass.args | ForEach-Object { [string]$_ })
Assert-Equal ($stableNativeBypassArgs -join ',') 'user-task' 'Stable user-level native bypass launcher should bypass all wrapper-injected arguments.'

$omxStatus = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-omx-status.ps1') -Arguments @(
  '-Json'
)
Assert-Equal $omxStatus.oh_my_codex 'off' 'Initial omx status should be off.'
Assert-Equal $omxStatus.effective_mode 'native_routed' 'Initial effective mode should be native_routed.'

$routingStatus = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-routing-status.ps1') -Arguments @(
  '-Json'
)
Assert-Equal $routingStatus.subagent_routing 'auto' 'Initial routing status should be auto.'
Assert-True ($routingStatus.role_orchestration_available -eq $true) 'Initial routing should allow role orchestration.'

$backendStatus = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-backend-status.ps1') -Arguments @(
  '-Json'
)
Assert-Equal $backendStatus.langgraph 'off' 'Backend status did not report the default LangGraph switch state.'
Assert-Equal $backendStatus.durable_orchestration_backend 'native_omx' 'Initial durable backend should be native_omx.'
Assert-True ([string]$backendStatus.backend_policy_summary -like '*stable_default=native_omx*') 'Backend status did not expose a backend policy summary.'
Assert-Equal $backendStatus.durable_orchestration.primary_operator_surface 'codex-durable-backend-status.ps1' 'Backend status did not identify itself as the primary operator-facing backend surface.'
Assert-Equal $backendStatus.durable_orchestration.default_backend 'native_omx' 'Backend status did not report native_omx as the stable default.'
Assert-Equal $backendStatus.durable_orchestration.backend_selection_mode 'explicit' 'Backend status did not report explicit backend selection.'
Assert-Equal $backendStatus.durable_orchestration.backend_family_switching 'manual_only' 'Backend status did not keep backend-family switching manual-only.'
Assert-True ([string]$backendStatus.durable_orchestration.repository_development_authority -like '*OpenSpec specs*') 'Backend status did not distinguish repository-local development authority.'
$backendStatusSupportingSurfaces = @($backendStatus.durable_orchestration.supporting_operator_surfaces | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $backendStatusSupportingSurfaces -Expected 'codex-routing-policy.ps1' -Message 'Backend status did not expose supporting operator-facing policy surfaces.'
$backendStatusQuestions = @($backendStatus.durable_orchestration.operator_questions_answered | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $backendStatusQuestions -Expected 'which orchestration capability layers are enabled now' -Message 'Backend status did not expose the operator questions it must answer.'
$backendStatusNativePreferred = @($backendStatus.durable_orchestration.selection_matrix.native_omx.preferred_for | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $backendStatusNativePreferred -Expected 'worker-centric durable execution' -Message 'Backend status did not expose native_omx preferred use cases.'
$backendStatusLangGraphPreferred = @($backendStatus.durable_orchestration.selection_matrix.langgraph.preferred_for | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $backendStatusLangGraphPreferred -Expected 'graph-shaped multi-phase execution' -Message 'Backend status did not expose LangGraph preferred use cases.'
Assert-True ($null -ne $backendStatus.durable_orchestration.PSObject.Properties['enabled_capabilities']) 'Backend status did not expose enabled capability layers.'
Assert-True ($backendStatus.durable_orchestration.enabled_capabilities.langgraph -eq $false) 'Backend status did not expose the default LangGraph capability state.'
Assert-Equal $backendStatus.durable_orchestration.effective_lane_model 'per_task_over_enabled_capabilities' 'Backend status did not expose the layered effective-lane model.'
Assert-Equal ([int]$backendStatus.durable_orchestration.provider_proxy_upstream_pacing.forwarded_request_budget) 10 'Backend status did not expose the global upstream pacing budget.'
Assert-Equal ([string]$backendStatus.durable_orchestration.provider_proxy_upstream_pacing.overflow_behavior) 'wait_for_slot_not_local_429' 'Backend status did not expose slot waiting for pacing overflow.'

$routingPolicy = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-routing-policy.ps1') -Arguments @(
  '-Json'
)
Assert-True ($routingPolicy.automatic_routing_enabled -eq $true) 'Initial routing policy should report automatic routing enabled.'
Assert-Equal $routingPolicy.capability_switches.completed_subagent_retention 'close' 'Initial routing policy did not expose completed_subagent_retention.'
Assert-Equal $routingPolicy.native_subagent_contract.completed_subagent_lifecycle.retention_policy 'close' 'Initial routing policy did not expose the completed-subagent lifecycle policy.'
Assert-True ($routingPolicy.durable_team_features_available -eq $false) 'Initial routing policy should report oh-my-codex durable features disabled.'
Assert-Equal $routingPolicy.langgraph 'off' 'Routing policy did not report the default LangGraph switch state.'
Assert-True ($routingPolicy.startup_path.automatic_durable_team_launch -eq $false) 'Routing policy should report that codex startup does not auto-launch durable teams.'
Assert-True ([string]$routingPolicy.project_isolation.runtime_state_scope -like '*.omx state root*') 'Routing policy should describe per-repository runtime isolation.'
Assert-True ($routingPolicy.automatic_durable_team_routing.available -eq $false) 'Initial automatic durable-team routing should be unavailable while oh-my-codex is off.'
Assert-Equal $routingPolicy.automatic_durable_team_routing.helper_script 'omx-team-auto.ps1' 'Routing policy did not report the automatic team helper name.'
Assert-True ([string]$routingPolicy.automatic_durable_team_routing.tracked_team_record_relative_path -like '*.omx*codex-auto-managed-team.json') 'Routing policy did not expose the tracked automatic team record path.'
Assert-Equal $routingPolicy.capability_switches.langgraph 'off' 'Routing policy did not expose the LangGraph capability switch.'
Assert-Equal $routingPolicy.effective_lane_selection.model 'per_task_over_enabled_capabilities' 'Routing policy did not expose the per-task effective-lane model.'
Assert-Equal $routingPolicy.effective_lane_selection.worker_centric_default 'native_omx' 'Routing policy did not keep native_omx as the worker-centric default lane.'
Assert-Equal $routingPolicy.orchestration_activation.posture 'non_conservative' 'Routing policy did not expose the non-conservative orchestration activation posture.'
$activationRechecks = @($routingPolicy.orchestration_activation.mandatory_rechecks | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $activationRechecks -Expected 'session_reload' -Message 'Routing policy did not require orchestration re-checks on session reload.'
Assert-ArrayContains -Actual $activationRechecks -Expected 'codex_restart' -Message 'Routing policy did not require orchestration re-checks on codex restart.'
Assert-ArrayContains -Actual $activationRechecks -Expected 'tracked_langgraph_state_detected' -Message 'Routing policy did not expose tracked LangGraph state as an activation trigger.'
Assert-Equal $routingPolicy.orchestration_activation.explicit_user_directives.use_omx 'hard_routing_directive' 'Routing policy did not treat explicit omx requests as hard directives.'
Assert-Equal $routingPolicy.orchestration_activation.explicit_user_directives.use_langgraph 'hard_routing_directive' 'Routing policy did not treat explicit LangGraph requests as hard directives.'
Assert-True ([string]$routingPolicy.orchestration_activation.threshold_adoption_rule -like '*actually adopt native_omx or langgraph*') 'Routing policy did not require actual orchestration adoption after threshold hits.'
Assert-True ([string]$routingPolicy.orchestration_activation.blocker_reporting_rule -like '*concrete blocker*') 'Routing policy did not require concrete blocker reporting when orchestration is skipped.'
Assert-True ([string]$routingPolicy.orchestration_activation.existing_project_policy.existing_live_session -like '*retrofit*') 'Routing policy did not expose the retrofit policy for existing live sessions.'
$activationTrackedSources = @($routingPolicy.orchestration_activation.tracked_state_sources | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $activationTrackedSources -Expected '.omx/state/langgraph/backend.json' -Message 'Routing policy did not expose the tracked LangGraph backend record as an activation source.'
Assert-True ($routingPolicy.provider_proxy_upstream_pacing.enforced -eq $true) 'Routing policy did not expose provider pacing as enabled.'
Assert-Equal ([int]$routingPolicy.provider_proxy_upstream_pacing.forwarded_request_budget) 10 'Routing policy did not expose the upstream pacing budget.'
Assert-Equal ([string]$routingPolicy.provider_proxy_upstream_pacing.overflow_behavior) 'wait_for_slot_not_local_429' 'Routing policy did not expose slot waiting for pacing overflow.'
Assert-Equal ([string]$routingPolicy.provider_proxy_upstream_pacing.orchestration_impact) 'backpressure_not_feature_blocker' 'Routing policy did not expose pacing as backpressure rather than a feature blocker.'
Assert-Equal ([string]$routingPolicy.inspectable_durable_state_surface.primary_operator_surface) 'codex-durable-state-status.ps1' 'Routing policy did not expose the canonical inspectable durable-state surface.'
$inspectableStateFields = @($routingPolicy.inspectable_durable_state_surface.minimum_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $inspectableStateFields -Expected 'tracked_identity' -Message 'Routing policy did not expose tracked_identity in the inspectable durable-state field set.'
Assert-ArrayContains -Actual $inspectableStateFields -Expected 'capability_readiness' -Message 'Routing policy did not expose capability_readiness in the inspectable durable-state field set.'
$durableReadinessFields = @($routingPolicy.inspectable_durable_state_surface.readiness_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $durableReadinessFields -Expected 'installed' -Message 'Routing policy did not expose durable capability installed readiness field.'
Assert-ArrayContains -Actual $durableReadinessFields -Expected 'enabled' -Message 'Routing policy did not expose durable capability enabled readiness field.'
Assert-ArrayContains -Actual $durableReadinessFields -Expected 'selected' -Message 'Routing policy did not expose durable capability selected readiness field.'
Assert-ArrayContains -Actual $durableReadinessFields -Expected 'ready' -Message 'Routing policy did not expose durable capability ready readiness field.'
$inspectableStateClasses = @($routingPolicy.inspectable_durable_state_surface.state_classes | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $inspectableStateClasses -Expected 'tracked_native_team' -Message 'Routing policy did not expose tracked_native_team as an inspectable durable-state class.'
Assert-ArrayContains -Actual $inspectableStateClasses -Expected 'tracked_langgraph_thread' -Message 'Routing policy did not expose tracked_langgraph_thread as an inspectable durable-state class.'
$inspectableStateHelpers = @($routingPolicy.inspectable_durable_state_surface.backend_helpers | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-history.ps1' -Message 'Routing policy did not expose the LangGraph history helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-runtime.ps1' -Message 'Routing policy did not expose the LangGraph runtime helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-memory.ps1' -Message 'Routing policy did not expose the LangGraph memory helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-subgraphs.ps1' -Message 'Routing policy did not expose the LangGraph subgraphs helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-fuller-engine.ps1' -Message 'Routing policy did not expose the LangGraph fuller-engine helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-deeper-engine.ps1' -Message 'Routing policy did not expose the LangGraph deeper-engine helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-superstep-engine.ps1' -Message 'Routing policy did not expose the LangGraph superstep-engine helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-stateful-engine.ps1' -Message 'Routing policy did not expose the LangGraph stateful-engine helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-boundary-engine.ps1' -Message 'Routing policy did not expose the LangGraph boundary-engine helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-handoff-engine.ps1' -Message 'Routing policy did not expose the LangGraph handoff-engine helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-approval-engine.ps1' -Message 'Routing policy did not expose the LangGraph approval-engine helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-provenance-engine.ps1' -Message 'Routing policy did not expose the LangGraph provenance-engine helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-artifact-engine.ps1' -Message 'Routing policy did not expose the LangGraph artifact-engine helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-reducer-engine.ps1' -Message 'Routing policy did not expose the LangGraph reducer-engine helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-command-engine.ps1' -Message 'Routing policy did not expose the LangGraph command-engine helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-runtime-engine.ps1' -Message 'Routing policy did not expose the LangGraph runtime-engine helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-memory-engine.ps1' -Message 'Routing policy did not expose the LangGraph memory-engine helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-migration-engine.ps1' -Message 'Routing policy did not expose the LangGraph migration-engine helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-auto-policy.ps1' -Message 'Routing policy did not expose the LangGraph auto-policy helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-subgraph-state.ps1' -Message 'Routing policy did not expose the LangGraph subgraph-state helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-stream.ps1' -Message 'Routing policy did not expose the LangGraph stream helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-replay.ps1' -Message 'Routing policy did not expose the LangGraph replay helper.'
Assert-ArrayContains -Actual $inspectableStateHelpers -Expected 'omx-langgraph-recover.ps1' -Message 'Routing policy did not expose the LangGraph recover helper.'
Assert-Equal ([string]$routingPolicy.durable_state_cleanup_reconciliation.primary_operator_surface) 'codex-durable-state-reconcile.ps1' 'Routing policy did not expose the cleanup and reconciliation helper.'
$safeCleanupClasses = @($routingPolicy.durable_state_cleanup_reconciliation.safe_cleanup_classes | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $safeCleanupClasses -Expected 'empty_unmanaged_native_team_directory' -Message 'Routing policy did not expose empty unmanaged native team directories as safe cleanup candidates.'
Assert-Equal ([string]$routingPolicy.advanced_compose_mode.entrypoint) 'omx-team-compose.ps1' 'Routing policy did not expose the compose entrypoint.'
Assert-True ($routingPolicy.advanced_compose_mode.enabled_by_default -eq $false) 'Routing policy did not keep compose mode opt-in by default.'
Assert-True ($routingPolicy.advanced_compose_mode.leader_outside_pane_roster -eq $true) 'Routing policy did not preserve the leader-outside-pane-roster rule for compose mode.'
$composeManifestFields = @($routingPolicy.advanced_compose_mode.manifest_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $composeManifestFields -Expected 'mailbox routing' -Message 'Routing policy did not expose compose manifest field expectations.'
Assert-Equal ([string]$routingPolicy.analyst_fanout_first_task_class.name) 'bounded_multi_face_research' 'Routing policy did not expose the bounded analyst-fanout-first task class.'
Assert-Equal ([string]$routingPolicy.analyst_fanout_first_task_class.first_round_preference) 'homogeneous_analyst_fanout' 'Routing policy did not prefer homogeneous analyst fan-out for bounded multi-face research.'
$analystFirstRoundRoles = @($routingPolicy.analyst_fanout_first_task_class.first_round_roles | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $analystFirstRoundRoles -Expected 'analyst' -Message 'Routing policy did not select analyst for first-round bounded research fan-out.'
$delayedBoundedResearchRoles = @($routingPolicy.analyst_fanout_first_task_class.default_first_round_not_roles | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $delayedBoundedResearchRoles -Expected 'architect' -Message 'Routing policy did not delay architect until after analyst fan-in for bounded research.'
Assert-ArrayContains -Actual $delayedBoundedResearchRoles -Expected 'planner' -Message 'Routing policy did not delay planner until after analyst fan-in for bounded research.'
Assert-ArrayContains -Actual $delayedBoundedResearchRoles -Expected 'writer' -Message 'Routing policy did not delay writer until after analyst fan-in for bounded research.'
$architectThreshold = @($routingPolicy.routing_thresholds | Where-Object { [string]$_.name -eq 'architect' } | Select-Object -First 1)[0]
$plannerThreshold = @($routingPolicy.routing_thresholds | Where-Object { [string]$_.name -eq 'planner' } | Select-Object -First 1)[0]
$writerThreshold = @($routingPolicy.routing_thresholds | Where-Object { [string]$_.name -eq 'writer' } | Select-Object -First 1)[0]
Assert-True ($architectThreshold.first_round_default_for_bounded_multi_face_research -eq $false) 'Routing policy incorrectly treats architect as a default first-round bounded research role.'
Assert-True ($plannerThreshold.first_round_default_for_bounded_multi_face_research -eq $false) 'Routing policy incorrectly treats planner as a default first-round bounded research role.'
Assert-True ($writerThreshold.first_round_default_for_bounded_multi_face_research -eq $false) 'Routing policy incorrectly treats writer as a default first-round bounded research role.'
Assert-True ($routingPolicy.native_subagent_contract.official_native_capability -eq $true) 'Routing policy did not mark native subagents as an official native capability.'
Assert-True ($routingPolicy.native_subagent_contract.raw_codex_auto_spawns_specialists_by_default -eq $false) 'Routing policy did not clarify that raw Codex does not auto-spawn specialist roles by default.'
Assert-Equal ([int]$routingPolicy.native_subagent_contract.limits.max_threads) 4 'Routing policy did not expose the managed max_threads value.'
Assert-Equal ([int]$routingPolicy.native_subagent_contract.limits.max_depth) 2 'Routing policy did not expose the managed max_depth value.'
Assert-True ([string]$routingPolicy.native_subagent_contract.role_locations.repository_scoped -like '*.codex/agents*') 'Routing policy did not expose the repository-scoped role TOML hint.'
$completedSubagentLifecycle = $routingPolicy.native_subagent_contract.completed_subagent_lifecycle
Assert-Equal ([string]$completedSubagentLifecycle.completion_action) 'close_after_fan_in' 'Routing policy did not expose the retention-dependent completion action.'
Assert-Equal ([string]$completedSubagentLifecycle.wait_strategy) 'dynamic_window_with_periodic_checkins' 'Routing policy did not expose the dynamic native-subagent wait strategy.'
Assert-Equal ([int]$completedSubagentLifecycle.initial_wait_seconds) 30 'Routing policy did not expose the initial native-subagent wait window.'
Assert-Equal ([int]$completedSubagentLifecycle.typical_wait_windows.deep_review) 120 'Routing policy did not expose the deeper-review native-subagent wait window.'
Assert-Equal ([int]$completedSubagentLifecycle.progress_check_interval_seconds) 30 'Routing policy did not expose the native-subagent progress check interval.'
Assert-Equal ([int]$completedSubagentLifecycle.max_wait_seconds) 180 'Routing policy did not expose the maximum native-subagent wait window.'
Assert-Equal ([int]$completedSubagentLifecycle.stall_after_consecutive_quiet_checkins) 2 'Routing policy did not expose the quiet-check stall threshold.'
Assert-True ([string]$completedSubagentLifecycle.stall_rule -like '*inspect_redirect_or_respawn*') 'Routing policy did not expose the stalled-subagent handling rule.'
$customAgentFieldNames = @($routingPolicy.native_subagent_contract.standalone_custom_agent_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $customAgentFieldNames -Expected 'developer_instructions' -Message 'Routing policy did not expose the minimum standalone custom-agent schema.'
$writeParallelRequirements = @($routingPolicy.native_subagent_contract.write_parallelism_requirements | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $writeParallelRequirements -Expected 'explicit ownership isolation by file slice or worktree' -Message 'Routing policy did not expose write-heavy ownership isolation requirements.'
$generalRuntimeNames = @($routingPolicy.native_subagent_contract.terminology.general_orchestration_runtimes | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $generalRuntimeNames -Expected 'LangGraph' -Message 'Routing policy did not expose general orchestration runtimes distinctly.'
$availableDurableBackends = @($routingPolicy.durable_orchestration.available_backends | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $availableDurableBackends -Expected 'langgraph' -Message 'Routing policy did not expose LangGraph as an available durable backend.'
Assert-Equal $routingPolicy.durable_orchestration.selected_backend 'native_omx' 'Routing policy did not report the selected durable backend.'
Assert-Equal $routingPolicy.durable_orchestration.default_backend 'native_omx' 'Routing policy did not report native_omx as the default durable backend.'
Assert-Equal $routingPolicy.durable_orchestration.backend_selection_mode 'explicit' 'Routing policy did not report explicit backend selection.'
Assert-Equal $routingPolicy.durable_orchestration.backend_family_switching 'manual_only' 'Routing policy did not keep backend-family switching manual-only.'
Assert-True ([string]$routingPolicy.durable_orchestration.single_task_backend_family_rule -like '*one backend family*') 'Routing policy did not expose the one-backend-family rule.'
$nativeOmxPreferred = @($routingPolicy.durable_orchestration.selection_matrix.native_omx.preferred_for | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $nativeOmxPreferred -Expected 'worker-centric durable execution' -Message 'Routing policy did not expose native_omx preferred use cases.'
$langGraphPreferred = @($routingPolicy.durable_orchestration.selection_matrix.langgraph.preferred_for | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphPreferred -Expected 'graph-shaped multi-phase execution' -Message 'Routing policy did not expose LangGraph preferred use cases.'
Assert-True ([string]$routingPolicy.durable_orchestration.langgraph_runtime_layout.root -like '*.omx*langgraph') 'Routing policy did not expose the LangGraph runtime root.'
$langGraphRootPhases = @($routingPolicy.durable_orchestration.langgraph_contract.root_phases | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphRootPhases -Expected 'freeze-plan' -Message 'Routing policy did not expose the LangGraph root-graph phases.'
$langGraphSubgraphFields = @($routingPolicy.durable_orchestration.langgraph_contract.subgraph_library_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphSubgraphFields -Expected 'input_artifacts' -Message 'Routing policy did not expose the LangGraph subgraph-library fields.'
$langGraphAvailableSubgraphs = @($routingPolicy.durable_orchestration.langgraph_contract.subgraphs.PSObject.Properties | ForEach-Object { [string]$_.Name })
Assert-ArrayContains -Actual $langGraphAvailableSubgraphs -Expected 'research' -Message 'Routing policy did not expose the research subgraph contract.'
$langGraphCommandStateFields = @($routingPolicy.durable_orchestration.langgraph_contract.command_state_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphCommandStateFields -Expected 'graph_scope' -Message 'Routing policy did not expose LangGraph command state fields.'
$langGraphStreamModes = @($routingPolicy.durable_orchestration.langgraph_contract.stream_observability_modes | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphStreamModes -Expected 'debug' -Message 'Routing policy did not expose LangGraph stream observability modes.'
$langGraphRuntimeContextFields = @($routingPolicy.durable_orchestration.langgraph_contract.runtime_context_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphRuntimeContextFields -Expected 'context_schema' -Message 'Routing policy did not expose LangGraph runtime context fields.'
$langGraphMemoryStoreFields = @($routingPolicy.durable_orchestration.langgraph_contract.memory_store_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphMemoryStoreFields -Expected 'memory_store_kind' -Message 'Routing policy did not expose LangGraph memory store fields.'
$langGraphGraphContractFields = @($routingPolicy.durable_orchestration.langgraph_contract.graph_contract_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphGraphContractFields -Expected 'topology_version' -Message 'Routing policy did not expose LangGraph graph-contract fields.'
$langGraphKernelIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.graph_kernel_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphKernelIdentityFields -Expected 'graph_api_surface' -Message 'Routing policy did not expose LangGraph graph-kernel identity fields.'
$langGraphKernelProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_kernel_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphKernelProjectionFields -Expected 'current_node_id' -Message 'Routing policy did not expose LangGraph graph-kernel projection fields.'
$langGraphPrimaryRuntimeIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.primary_runtime_engine_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphPrimaryRuntimeIdentityFields -Expected 'engine_kind' -Message 'Routing policy did not expose LangGraph primary-runtime identity fields.'
$langGraphPrimaryRuntimeProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_primary_runtime_engine_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphPrimaryRuntimeProjectionFields -Expected 'current_execution_node' -Message 'Routing policy did not expose LangGraph primary-runtime projection fields.'
$langGraphCompiledInvocationIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.compiled_invocation_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphCompiledInvocationIdentityFields -Expected 'compiler_surface' -Message 'Routing policy did not expose LangGraph compiled-invocation identity fields.'
$langGraphCompiledInvocationProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_compiled_invocation_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphCompiledInvocationProjectionFields -Expected 'last_invoke_kind' -Message 'Routing policy did not expose LangGraph compiled-invocation projection fields.'
$langGraphLiveExecutionIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.live_execution_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphLiveExecutionIdentityFields -Expected 'execute_surface' -Message 'Routing policy did not expose LangGraph live-execution identity fields.'
$langGraphLiveExecutionProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_live_execution_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphLiveExecutionProjectionFields -Expected 'last_run_status' -Message 'Routing policy did not expose LangGraph live-execution projection fields.'
$langGraphFullerEngineIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.fuller_live_primary_engine_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphFullerEngineIdentityFields -Expected 'execute_surface' -Message 'Routing policy did not expose LangGraph fuller-engine identity fields.'
$langGraphFullerEngineProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_fuller_live_primary_engine_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphFullerEngineProjectionFields -Expected 'resulting_phase' -Message 'Routing policy did not expose LangGraph fuller-engine projection fields.'
$langGraphDeeperEngineIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.deeper_live_primary_engine_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphDeeperEngineIdentityFields -Expected 'remaining_steps_surface' -Message 'Routing policy did not expose LangGraph deeper-engine identity fields.'
$langGraphDeeperEngineProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_deeper_live_primary_engine_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphDeeperEngineProjectionFields -Expected 'projected_phase_path' -Message 'Routing policy did not expose LangGraph deeper-engine projection fields.'
$langGraphSuperstepEngineIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.superstep_live_primary_engine_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphSuperstepEngineIdentityFields -Expected 'superstep_surface' -Message 'Routing policy did not expose LangGraph superstep-engine identity fields.'
$langGraphSuperstepEngineProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_superstep_live_primary_engine_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphSuperstepEngineProjectionFields -Expected 'phase_visit_path' -Message 'Routing policy did not expose LangGraph superstep-engine projection fields.'
$langGraphStatefulEngineIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.stateful_live_primary_engine_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphStatefulEngineIdentityFields -Expected 'decision_surface' -Message 'Routing policy did not expose LangGraph stateful-engine identity fields.'
$langGraphStatefulEngineProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_stateful_live_primary_engine_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphStatefulEngineProjectionFields -Expected 'stateful_transition_log' -Message 'Routing policy did not expose LangGraph stateful-engine projection fields.'
$langGraphBoundaryEngineIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.boundary_state_live_primary_engine_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphBoundaryEngineIdentityFields -Expected 'boundary_surface' -Message 'Routing policy did not expose LangGraph boundary-engine identity fields.'
$langGraphBoundaryEngineProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_boundary_state_live_primary_engine_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphBoundaryEngineProjectionFields -Expected 'boundary_state_kind' -Message 'Routing policy did not expose LangGraph boundary-engine projection fields.'
$langGraphHandoffEngineIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.handoff_state_live_primary_engine_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphHandoffEngineIdentityFields -Expected 'handoff_surface' -Message 'Routing policy did not expose LangGraph handoff-engine identity fields.'
$langGraphHandoffEngineProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_handoff_state_live_primary_engine_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphHandoffEngineProjectionFields -Expected 'handoff_transition_log' -Message 'Routing policy did not expose LangGraph handoff-engine projection fields.'
$langGraphApprovalEngineIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.approval_aware_live_primary_engine_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphApprovalEngineIdentityFields -Expected 'approval_surface' -Message 'Routing policy did not expose LangGraph approval-engine identity fields.'
$langGraphApprovalEngineProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_approval_aware_live_primary_engine_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphApprovalEngineProjectionFields -Expected 'resume_state_kind' -Message 'Routing policy did not expose LangGraph approval-engine projection fields.'
$langGraphProvenanceEngineIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.provenance_state_live_primary_engine_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphProvenanceEngineIdentityFields -Expected 'provenance_surface' -Message 'Routing policy did not expose LangGraph provenance-engine identity fields.'
$langGraphProvenanceEngineProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_provenance_state_live_primary_engine_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphProvenanceEngineProjectionFields -Expected 'recovery_target_id' -Message 'Routing policy did not expose LangGraph provenance-engine projection fields.'
$langGraphArtifactEngineIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.durable_artifact_aware_live_primary_engine_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphArtifactEngineIdentityFields -Expected 'artifact_surface' -Message 'Routing policy did not expose LangGraph artifact-engine identity fields.'
$langGraphArtifactEngineProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_durable_artifact_aware_live_primary_engine_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphArtifactEngineProjectionFields -Expected 'implementation_brief_id' -Message 'Routing policy did not expose LangGraph artifact-engine projection fields.'
$langGraphReducerEngineIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.reducer_aware_live_primary_engine_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphReducerEngineIdentityFields -Expected 'reducer_surface' -Message 'Routing policy did not expose LangGraph reducer-engine identity fields.'
$langGraphReducerEngineProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_reducer_aware_live_primary_engine_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphReducerEngineProjectionFields -Expected 'fanout_state' -Message 'Routing policy did not expose LangGraph reducer-engine projection fields.'
$langGraphCommandEngineIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.command_aware_live_primary_engine_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphCommandEngineIdentityFields -Expected 'command_surface' -Message 'Routing policy did not expose LangGraph command-engine identity fields.'
$langGraphCommandEngineProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_command_aware_live_primary_engine_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphCommandEngineProjectionFields -Expected 'parent_handoff_target' -Message 'Routing policy did not expose LangGraph command-engine projection fields.'
$langGraphRuntimeEngineIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.runtime_aware_live_primary_engine_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphRuntimeEngineIdentityFields -Expected 'runtime_surface' -Message 'Routing policy did not expose LangGraph runtime-engine identity fields.'
$langGraphRuntimeEngineProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_runtime_aware_live_primary_engine_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphRuntimeEngineProjectionFields -Expected 'store_kind' -Message 'Routing policy did not expose LangGraph runtime-engine projection fields.'
$langGraphMemoryEngineIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.memory_aware_live_primary_engine_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphMemoryEngineIdentityFields -Expected 'memory_surface' -Message 'Routing policy did not expose LangGraph memory-engine identity fields.'
$langGraphMemoryEngineProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_memory_aware_live_primary_engine_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphMemoryEngineProjectionFields -Expected 'semantic_store_kind' -Message 'Routing policy did not expose LangGraph memory-engine projection fields.'
$langGraphMigrationEngineIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.migration_aware_live_primary_engine_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphMigrationEngineIdentityFields -Expected 'migration_surface' -Message 'Routing policy did not expose LangGraph migration-engine identity fields.'
$langGraphMigrationEngineProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_migration_aware_live_primary_engine_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphMigrationEngineProjectionFields -Expected 'reason_codes' -Message 'Routing policy did not expose LangGraph migration-engine projection fields.'
$langGraphAutomaticPolicyIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.automatic_runtime_policy_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphAutomaticPolicyIdentityFields -Expected 'manual_first_default' -Message 'Routing policy did not expose LangGraph automatic runtime-policy identity fields.'
$langGraphAutomaticPolicyProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_automatic_runtime_policy_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphAutomaticPolicyProjectionFields -Expected 'safe_to_auto_apply' -Message 'Routing policy did not expose LangGraph automatic runtime-policy projection fields.'
Assert-ArrayContains -Actual $langGraphAutomaticPolicyProjectionFields -Expected 'recovery_policy_posture' -Message 'Routing policy did not expose LangGraph automatic runtime-policy recovery posture fields.'
$langGraphGeneralizedRoutingIdentityFields = @($routingPolicy.durable_orchestration.langgraph_contract.generalized_live_routing_identity_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphGeneralizedRoutingIdentityFields -Expected 'route_decision_surface' -Message 'Routing policy did not expose LangGraph generalized-routing identity fields.'
$langGraphGeneralizedRoutingProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_generalized_live_routing_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphGeneralizedRoutingProjectionFields -Expected 'selected_route' -Message 'Routing policy did not expose LangGraph generalized-routing projection fields.'
$langGraphApprovalQueueItemFields = @($routingPolicy.durable_orchestration.langgraph_contract.approval_queue_item_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphApprovalQueueItemFields -Expected 'interrupt_id' -Message 'Routing policy did not expose LangGraph approval-queue item fields.'
$langGraphApprovalQueuePostures = @($routingPolicy.durable_orchestration.langgraph_contract.approval_queue_postures | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphApprovalQueuePostures -Expected 'partially_resolved' -Message 'Routing policy did not expose LangGraph approval-queue postures.'
$langGraphMigrationReasonCodes = @($routingPolicy.durable_orchestration.langgraph_contract.migration_reason_codes | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphMigrationReasonCodes -Expected 'topology_major_drift' -Message 'Routing policy did not expose LangGraph migration reason codes.'
$langGraphApprovalQueueProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_approval_queue_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphApprovalQueueProjectionFields -Expected 'pending_interrupt_ids' -Message 'Routing policy did not expose LangGraph approval-queue projection fields.'
$langGraphMigrationProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_migration_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphMigrationProjectionFields -Expected 'compatibility' -Message 'Routing policy did not expose LangGraph migration projection fields.'
$langGraphSubgraphProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_subgraph_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphSubgraphProjectionFields -Expected 'active_subgraph' -Message 'Routing policy did not expose LangGraph subgraph projection fields.'
$langGraphSubgraphPersistenceModes = @($routingPolicy.durable_orchestration.langgraph_contract.subgraph_persistence_modes | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphSubgraphPersistenceModes -Expected 'per_thread' -Message 'Routing policy did not expose LangGraph subgraph persistence modes.'
$langGraphSubgraphStateInspectionProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_subgraph_state_inspection_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphSubgraphStateInspectionProjectionFields -Expected 'state_inspection_available' -Message 'Routing policy did not expose LangGraph subgraph-state inspection projection fields.'
$langGraphCommandProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_command_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphCommandProjectionFields -Expected 'parent_handoff_target' -Message 'Routing policy did not expose LangGraph command projection fields.'
$langGraphStreamProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_stream_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphStreamProjectionFields -Expected 'latest_event_kind' -Message 'Routing policy did not expose LangGraph stream projection fields.'
$langGraphRuntimeProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_runtime_injection_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphRuntimeProjectionFields -Expected 'store_kind' -Message 'Routing policy did not expose LangGraph runtime/store projection fields.'
$langGraphMemoryProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_memory_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphMemoryProjectionFields -Expected 'semantic_store_kind' -Message 'Routing policy did not expose LangGraph memory projection fields.'
$langGraphInterruptPoints = @($routingPolicy.durable_orchestration.langgraph_contract.interrupt_points | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphInterruptPoints -Expected 'verify-accept-failed' -Message 'Routing policy did not expose the LangGraph interrupt points.'
$langGraphHistoryProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_history_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphHistoryProjectionFields -Expected 'available_targets' -Message 'Routing policy did not expose LangGraph history projection fields.'
$langGraphRecoveryProjectionFields = @($routingPolicy.inspectable_durable_state_surface.langgraph_recovery_projection_fields | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphRecoveryProjectionFields -Expected 'target_id' -Message 'Routing policy did not expose LangGraph recovery projection fields.'
$routingPolicyNames = @($routingPolicy.routing_thresholds | ForEach-Object { [string]$_.name })
Assert-ArrayContains -Actual $routingPolicyNames -Expected 'analyst' -Message 'Routing policy did not include analyst thresholds.'
Assert-ArrayContains -Actual $routingPolicyNames -Expected 'bug-finder / bug-rebutter / bug-judge' -Message 'Routing policy did not include adversarial bug-review thresholds.'
$routingBurstRoleNames = @($routingPolicy.burst_review_roles | ForEach-Object { [string]$_.name })
Assert-ArrayContains -Actual $routingBurstRoleNames -Expected 'bug-finder' -Message 'Routing policy did not expose bug-finder as an installed burst-review role.'
Assert-ArrayContains -Actual $routingBurstRoleNames -Expected 'bug-rebutter' -Message 'Routing policy did not expose bug-rebutter as an installed burst-review role.'
Assert-ArrayContains -Actual $routingBurstRoleNames -Expected 'bug-judge' -Message 'Routing policy did not expose bug-judge as an installed burst-review role.'
$installedBurstRoleNames = @($routingPolicy.burst_review_roles | Where-Object { [bool]$_.installed } | ForEach-Object { [string]$_.name })
Assert-ArrayContains -Actual $installedBurstRoleNames -Expected 'bug-finder' -Message 'Routing policy did not mark bug-finder as installed.'
Assert-ArrayContains -Actual $installedBurstRoleNames -Expected 'bug-rebutter' -Message 'Routing policy did not mark bug-rebutter as installed.'
Assert-ArrayContains -Actual $installedBurstRoleNames -Expected 'bug-judge' -Message 'Routing policy did not mark bug-judge as installed.'
$adversarialInstalledNames = @($routingPolicy.adversarial_review.installed_role_names | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $adversarialInstalledNames -Expected 'bug-judge' -Message 'Routing policy adversarial-review metadata did not expose installed burst-review roles.'
Assert-Equal $routingPolicy.helper_mirror_source_of_truth.helper_copy_kind 'generated_user_level_install_artifact' 'Routing policy did not classify user-level helper mirrors as generated install artifacts.'
Assert-Equal $routingPolicy.helper_mirror_source_of_truth.repository_source_script 'tools/install-codex-user-level-team-mode.ps1' 'Routing policy did not point helper mirror provenance back to the installer source script.'
Assert-True ([string]$routingPolicy.helper_mirror_source_of_truth.non_global_state_root_rule).Contains('not a global durable-state root') 'Routing policy did not prevent treating the repository as a global durable-state root.'

$durableStateNone = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') -Arguments @(
  '-RepoRoot', $NoStateRepoRoot,
  '-Json'
)
Assert-Equal $durableStateNone.state_class 'no_durable_state' 'Durable-state status did not classify the no-state case correctly.'
Assert-Equal $durableStateNone.backend_family '' 'Durable-state status should not report a backend family when no state exists.'
Assert-Equal $durableStateNone.selected_backend 'native_omx' 'Durable-state status should expose the default selected backend for a cold no-state repo.'
Assert-True ($durableStateNone.capability_readiness.native_omx.installed -eq $true) 'Durable-state status should report generated native_omx helpers as installed.'
Assert-True ($durableStateNone.capability_readiness.native_omx.enabled -eq $false) 'Durable-state status should keep native_omx disabled while oh_my_codex is off.'
Assert-True ($durableStateNone.capability_readiness.native_omx.selected -eq $true) 'Durable-state status should report native_omx as the default selected backend.'
Assert-True ($durableStateNone.capability_readiness.native_omx.ready -eq $false) 'Durable-state status should not report native_omx ready before it is enabled.'
Assert-True ($durableStateNone.capability_readiness.langgraph.installed -eq $false) 'Durable-state status should report LangGraph shared runtime as not installed in the isolated test home.'
Assert-True ($durableStateNone.capability_readiness.langgraph.enabled -eq $false) 'Durable-state status should report LangGraph disabled by default.'
Assert-True ($durableStateNone.capability_readiness.langgraph.selected -eq $false) 'Durable-state status should not report LangGraph selected by default.'
Assert-True ($durableStateNone.capability_readiness.langgraph.ready -eq $false) 'Durable-state status should not report LangGraph ready by default.'
Assert-ArrayContains -Actual @($durableStateNone.capability_readiness.readiness_fields | ForEach-Object { [string]$_ }) -Expected 'ready' -Message 'Durable-state status did not publish readiness field names.'
Assert-True (-not (Test-Path -LiteralPath (Join-Path $NoStateRepoRoot '.omx'))) 'Read-only durable-state status should not create repo-local .omx state in a no-state repo.'
Assert-True ($durableStateNone.read_only_by_default -eq $true) 'Durable-state status did not preserve read-only posture.'
Assert-Equal $durableStateNone.helper_mirror_source_of_truth.helper_copy_kind 'generated_user_level_install_artifact' 'Durable-state status did not expose generated helper install-artifact provenance.'
Assert-Equal $durableStateNone.helper_mirror_source_of_truth.repository_source_script 'tools/install-codex-user-level-team-mode.ps1' 'Durable-state status did not identify the repository source script.'
Assert-Equal $durableStateNone.helper_mirror_source_of_truth.durable_truth_scope 'target repository repo-local .omx/state tree' 'Durable-state status did not keep durable truth scoped to the target repository.'
Assert-ArrayContains -Actual @($durableStateNone.helper_mirror_source_of_truth.consumer_project_examples | ForEach-Object { [string]$_ }) -Expected 'D:\PythonProject_CLIProxyAPI' -Message 'Durable-state status did not preserve consumer project isolation examples.'
Assert-True ([string]$durableStateNone.helper_mirror_source_of_truth.non_global_state_root_rule).Contains('not a global durable-state root') 'Durable-state status did not reject global durable-state-root interpretation.'

$cleanupPreviewNone = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-reconcile.ps1') -Arguments @(
  '-RepoRoot', $NoStateRepoRoot,
  '-Json'
)
Assert-True ($cleanupPreviewNone.preview_only_default -eq $true) 'Durable-state reconcile helper did not preserve preview-by-default behavior.'
Assert-True ($cleanupPreviewNone.safe_cleanup_available -eq $false) 'Durable-state reconcile helper should not report cleanup work for the no-state case.'

$omxOn = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-omx-on.ps1') -Arguments @(
  '-Json'
)
Assert-Equal $omxOn.oh_my_codex 'on' 'codex-omx-on.ps1 did not enable oh_my_codex.'
Assert-Equal $omxOn.subagent_routing 'auto' 'codex-omx-on.ps1 changed routing unexpectedly.'
Assert-Equal $omxOn.effective_mode 'enhanced' 'codex-omx-on.ps1 produced the wrong effective mode.'

$wrappedEnhanced = Invoke-PowerShellCommandJson -CommandText ("& { & " + (Quote-PowerShellLiteral -Value $ProfilePath) + "; codex 'enhanced-task' }")
$wrappedEnhancedArgs = @($wrappedEnhanced.args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $wrappedEnhancedArgs -Expected 'mcp_servers.omx_state.enabled=true' -Message 'Wrapped enhanced launch did not keep omx_state enabled.'
Assert-ArrayContains -Actual $wrappedEnhancedArgs -Expected 'enhanced-task' -Message 'Wrapped enhanced launch did not forward the user argument.'
Assert-ArrayContains -Actual $wrappedEnhancedArgs -Expected 'agents.max_threads=4' -Message 'Wrapped enhanced launch did not forward the managed max_threads value.'
Assert-ArrayContains -Actual $wrappedEnhancedArgs -Expected 'agents.max_depth=2' -Message 'Wrapped enhanced launch did not forward the managed max_depth value.'
Assert-True ('notify=[]' -notin $wrappedEnhancedArgs) 'Enhanced launch should not force notify off.'
$enhancedModelInstructionsArg = @($wrappedEnhancedArgs | Where-Object { $_ -like 'model_instructions_file=*' } | Select-Object -First 1)[0]
$enhancedModelInstructionsPath = $enhancedModelInstructionsArg.Substring('model_instructions_file='.Length).Trim('"').Replace('\\', '\')
$enhancedModelInstructionsContent = Get-Content -LiteralPath $enhancedModelInstructionsPath -Raw
Assert-True ($enhancedModelInstructionsContent.Contains('does not auto-launch a durable team')) 'Enhanced launch did not state that startup itself does not auto-launch a durable team.'
Assert-True ($enhancedModelInstructionsContent.Contains('omx-team-auto.ps1')) 'Enhanced launch did not mention the automatic durable-team helper.'
Assert-True ($enhancedModelInstructionsContent.Contains('codex-auto-managed-team.json')) 'Enhanced launch did not mention the tracked automatic team record.'
Assert-True ($enhancedModelInstructionsContent.Contains('every session reload or Codex restart')) 'Enhanced launch did not require activation re-checks on reload or restart.'
Assert-True ($enhancedModelInstructionsContent.Contains('hard routing directives')) 'Enhanced launch did not treat explicit omx/LangGraph requests as hard directives.'
Assert-True ($enhancedModelInstructionsContent.Contains('actually adopt `native_omx` or `langgraph`')) 'Enhanced launch did not require actual orchestration adoption after threshold hits.'
Assert-True ($enhancedModelInstructionsContent.Contains('Automatic collaboration is the default for all projects')) 'Enhanced launch did not preserve the global automatic collaboration default.'
Assert-True ($enhancedModelInstructionsContent.Contains('platform_subagent_invocation_constraint')) 'Enhanced launch did not preserve the platform subagent invocation blocker token.'
Assert-True ($enhancedModelInstructionsContent.Contains('10 true upstream provider forwards per rolling 1-minute window')) 'Enhanced launch did not expose the global upstream pacing budget.'
Assert-True ($enhancedModelInstructionsContent.Contains('wait for a slot instead of immediately returning a local 429')) 'Enhanced launch did not expose pacing overflow as slot waiting.'
Assert-True ($enhancedModelInstructionsContent.Contains('Do not treat the upstream pacing budget alone as a reason to avoid LangGraph')) 'Enhanced launch did not preserve the orchestration-safe pacing interpretation.'

$enhancedRoutingPolicy = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-routing-policy.ps1') -Arguments @(
  '-Json'
)
Assert-True ($enhancedRoutingPolicy.automatic_durable_team_routing.available -eq $true) 'Enhanced routing policy should enable automatic durable-team routing.'
Assert-Equal $enhancedRoutingPolicy.automatic_durable_team_routing.selected_backend 'native_omx' 'Enhanced routing policy should initially preserve the native durable backend.'

$langGraphSwitchOn = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-langgraph-on.ps1') -Arguments @(
  '-Json'
)
Assert-Equal $langGraphSwitchOn.langgraph 'on' 'LangGraph on switch did not enable LangGraph.'

$langGraphBackendOn = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-backend-langgraph.ps1') -Arguments @(
  '-Json'
)
Assert-Equal $langGraphBackendOn.langgraph 'on' 'Durable backend compatibility wrapper did not keep LangGraph enabled.'
Assert-Equal $langGraphBackendOn.durable_orchestration_backend 'langgraph' 'Durable backend selector did not switch to langgraph.'
$langGraphSwitchStatus = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-langgraph-status.ps1') -Arguments @(
  '-Json'
)
Assert-Equal $langGraphSwitchStatus.langgraph 'on' 'LangGraph status script did not report LangGraph as enabled.'
Assert-Equal $langGraphSwitchStatus.langgraph_install_state 'not_installed' 'LangGraph status script did not distinguish install state.'
Assert-True ($langGraphSwitchStatus.langgraph_enabled -eq $true) 'LangGraph status script did not expose enabled state.'
Assert-True ($langGraphSwitchStatus.langgraph_selected -eq $true) 'LangGraph status script did not expose selected state.'
Assert-True ($langGraphSwitchStatus.langgraph_ready -eq $false) 'LangGraph status script should not report ready before the shared venv exists.'
Assert-Equal $langGraphSwitchStatus.langgraph_runtime.shared_venv_path (Join-Path $CodexHome 'venvs\langgraph-py312') 'LangGraph status script did not expose the shared venv path.'

$durableStateLangGraphSelected = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') -Arguments @(
  '-RepoRoot', $NoStateRepoRoot,
  '-Json'
)
Assert-Equal $durableStateLangGraphSelected.selected_backend 'langgraph' 'Durable-state status should expose the selected LangGraph backend after switching.'
Assert-True ($durableStateLangGraphSelected.capability_readiness.native_omx.enabled -eq $true) 'Durable-state status should keep native_omx enabled when oh_my_codex is on.'
Assert-True ($durableStateLangGraphSelected.capability_readiness.native_omx.selected -eq $false) 'Durable-state status should distinguish native_omx as not selected when LangGraph is selected and no repo state exists.'
Assert-True ($durableStateLangGraphSelected.capability_readiness.native_omx.ready -eq $false) 'Durable-state status should not report native_omx ready when it is not selected.'
Assert-True ($durableStateLangGraphSelected.capability_readiness.langgraph.enabled -eq $true) 'Durable-state status should report LangGraph enabled after switching.'
Assert-True ($durableStateLangGraphSelected.capability_readiness.langgraph.selected -eq $true) 'Durable-state status should report LangGraph selected after switching.'
Assert-True ($durableStateLangGraphSelected.capability_readiness.langgraph.ready -eq $false) 'Durable-state status should not report LangGraph ready before the shared runtime is installed.'
Assert-ArrayContains -Actual @($durableStateLangGraphSelected.capability_readiness.langgraph.blockers | ForEach-Object { [string]$_ }) -Expected 'langgraph_shared_runtime_not_installed' -Message 'Durable-state status did not explain the LangGraph not-ready blocker.'
Assert-True (-not (Test-Path -LiteralPath (Join-Path $NoStateRepoRoot '.omx'))) 'Durable-state status after LangGraph selection should remain read-only for repo-local state.'

$fakeSharedLangGraphPythonPath = Join-Path $CodexHome 'venvs\langgraph-py312\Scripts\python.exe'
Ensure-Directory -Path (Split-Path -Parent $fakeSharedLangGraphPythonPath)
Set-Content -LiteralPath $fakeSharedLangGraphPythonPath -Encoding ASCII -NoNewline -Value ''
$durableStateLangGraphReadyMissingSelector = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') -Arguments @(
  '-RepoRoot', $NoStateRepoRoot,
  '-Json'
)
Assert-Equal $durableStateLangGraphReadyMissingSelector.selected_backend 'langgraph' 'Durable-state status should preserve the selected LangGraph backend when the active selector is missing.'
Assert-Equal $durableStateLangGraphReadyMissingSelector.backend_default 'langgraph' 'Durable-state status should report LangGraph as the backend default when selected and ready.'
Assert-True ($durableStateLangGraphReadyMissingSelector.backend_ready -eq $true) 'Durable-state status should report the selected LangGraph backend as ready after the shared runtime exists.'
Assert-True ($durableStateLangGraphReadyMissingSelector.capability_readiness.langgraph.ready -eq $true) 'Durable-state status should report LangGraph capability readiness after the shared runtime exists.'
Assert-Equal $durableStateLangGraphReadyMissingSelector.selector_authority '.omx/state/selectors/active.json' 'Durable-state status should expose the canonical active selector authority.'
Assert-Equal $durableStateLangGraphReadyMissingSelector.active_selector_status 'missing' 'Durable-state status should report a missing active selector explicitly.'
Assert-True ($durableStateLangGraphReadyMissingSelector.selector_refresh_gap -eq $true) 'Durable-state status should classify a ready LangGraph backend with no active selector as a selector refresh gap.'
Assert-Equal $durableStateLangGraphReadyMissingSelector.selector_refresh_gap_reason 'active_selector_missing_for_ready_default_backend' 'Durable-state status should expose a stable selector refresh gap reason.'
Assert-True (-not (Test-Path -LiteralPath (Join-Path $NoStateRepoRoot '.omx'))) 'Durable-state status for a missing selector should remain read-only and not create repo-local .omx state.'
Remove-Item -LiteralPath $fakeSharedLangGraphPythonPath -Force
$langGraphBackendStatus = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-backend-status.ps1') -Arguments @(
  '-Json'
)
Assert-Equal $langGraphBackendStatus.langgraph 'on' 'Backend status did not report LangGraph as enabled.'
Assert-Equal $langGraphBackendStatus.durable_orchestration_backend 'langgraph' 'Backend status did not report the LangGraph backend selection.'
Assert-Equal $langGraphBackendStatus.durable_orchestration.default_backend 'native_omx' 'Backend status should keep native_omx as the stable default after switching to LangGraph.'
Assert-Equal $langGraphBackendStatus.durable_orchestration.backend_family_switching 'manual_only' 'Backend status should still report manual-only backend-family switching after selecting LangGraph.'

$langGraphRoutingPolicy = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-routing-policy.ps1') -Arguments @(
  '-Json'
)
Assert-Equal $langGraphRoutingPolicy.durable_orchestration.selected_backend 'langgraph' 'Routing policy did not report the LangGraph backend selection.'
Assert-Equal $langGraphRoutingPolicy.automatic_durable_team_routing.selected_backend 'langgraph' 'Automatic durable routing policy did not honor the LangGraph backend selection.'
Assert-Equal $langGraphRoutingPolicy.durable_orchestration.backend_family_switching 'manual_only' 'LangGraph backend selection should still report manual-only backend-family switching.'
Assert-Equal $langGraphRoutingPolicy.capability_switches.langgraph 'on' 'Routing policy did not expose LangGraph as enabled after turning it on.'
Assert-True ($langGraphRoutingPolicy.native_omx_available -eq $true) 'Routing policy should keep native_omx available when oh_my_codex is on.'
Assert-True ($langGraphRoutingPolicy.langgraph_available -eq $true) 'Routing policy should report LangGraph as available after enabling it.'

$autoPlanUnavailable = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-auto.ps1') -Arguments @(
  '-Task', 'parallel feature work',
  '-Phase', 'execute-parallel',
  '-ParallelSlices', '2',
  '-RepoRoot', $AutoRepoRoot,
  '-Json'
)
Assert-Equal $autoPlanUnavailable.decision 'launch' 'Automatic team helper should derive a launch decision in enhanced auto mode.'
Assert-Equal $autoPlanUnavailable.effective_lane 'native_omx' 'Automatic team helper should default to native_omx for worker-centric execution when both durable capabilities are enabled.'
Assert-Equal $autoPlanUnavailable.desired_durable_team.worker_role 'team-executor' 'Automatic team helper derived the wrong worker role for execution.'
Assert-Equal ([int]$autoPlanUnavailable.desired_durable_team.worker_count) 2 'Automatic team helper derived the wrong worker count for two parallel slices.'
Assert-Equal $autoPlanUnavailable.durable_orchestration_backend 'langgraph' 'Automatic team helper did not preserve the selected LangGraph backend in the plan.'

Ensure-Directory -Path (Join-Path $LegacySelectorRepoRoot '.omx\state\langgraph\threads')
$legacySelectorThreadId = 'legacy-selector-repo:default:thread-1'
$legacySelectorThreadFileKey = $legacySelectorThreadId.Replace(':', '__')
$legacySelectorBackendPath = Join-Path $LegacySelectorRepoRoot '.omx\state\langgraph\backend.json'
$legacySelectorThreadPath = Join-Path $LegacySelectorRepoRoot ('.omx\state\langgraph\threads\' + $legacySelectorThreadFileKey + '.json')
Set-Content -LiteralPath $legacySelectorBackendPath -Encoding ASCII -NoNewline -Value @'
{
  "backend": "langgraph",
  "thread_id": "legacy-selector-repo:default:thread-1",
  "phase": "freeze-plan",
  "updated_at": "2026-04-21T00:00:00Z",
  "auto_route_eligible": false,
  "routing_posture": "preserved_legacy"
}
'@
Set-Content -LiteralPath $legacySelectorThreadPath -Encoding ASCII -NoNewline -Value @'
{
  "thread_id": "legacy-selector-repo:default:thread-1",
  "phase": "freeze-plan",
  "status": "resumed",
  "updated_at": "2026-04-21T00:00:00Z"
}
'@

$legacySelectorPlan = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-auto.ps1') -Arguments @(
  '-Task', 'parallel feature work',
  '-Phase', 'execute-parallel',
  '-ParallelSlices', '2',
  '-RepoRoot', $LegacySelectorRepoRoot,
  '-Json'
)
Assert-True ($legacySelectorPlan.langgraph_record.exists -eq $true) 'Automatic team helper should keep a preserved legacy LangGraph backend record inspectable.'
Assert-Equal $legacySelectorPlan.langgraph_record.thread_id $legacySelectorThreadId 'Automatic team helper did not preserve the legacy LangGraph thread identity.'
Assert-Equal $legacySelectorPlan.effective_lane 'native_omx' 'Automatic team helper should not let a preserved legacy LangGraph selector dominate a future worker-centric task flow.'
Assert-Equal $legacySelectorPlan.decision 'launch' 'Automatic team helper should launch native_omx instead of auto-resuming LangGraph from a preserved legacy selector.'
Assert-Equal $legacySelectorPlan.desired_durable_team.backend 'native_omx' 'Automatic team helper should keep the desired future-session durable backend on native_omx when only a preserved legacy LangGraph selector exists.'

$legacySelectorCleanup = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-reconcile.ps1') -Arguments @(
  '-RepoRoot', $LegacySelectorRepoRoot,
  '-Json'
)
Assert-True ($legacySelectorCleanup.safe_cleanup_available -eq $false) 'Durable-state reconcile should preserve legacy LangGraph selector artifacts instead of classifying them as safe cleanup.'
Assert-True ($legacySelectorCleanup.manual_reconciliation_required -eq $false) 'Durable-state reconcile should not require manual reconciliation for a preserved legacy LangGraph selector by itself.'

Ensure-Directory -Path (Join-Path $CrossRepoSelectorRepoRoot '.omx\state\selectors')
Ensure-Directory -Path (Join-Path $CrossRepoSelectorRepoRoot '.omx\state\langgraph\threads')
$crossRepoSelectorThreadId = 'cross-repo-selector:default:thread-1'
$crossRepoSelectorThreadFileKey = $crossRepoSelectorThreadId.Replace(':', '__')
$crossRepoSelectorActivePath = Join-Path $CrossRepoSelectorRepoRoot '.omx\state\selectors\active.json'
$crossRepoSelectorBackendPath = Join-Path $CrossRepoSelectorRepoRoot '.omx\state\langgraph\backend.json'
$crossRepoSelectorThreadPath = Join-Path $CrossRepoSelectorRepoRoot ('.omx\state\langgraph\threads\' + $crossRepoSelectorThreadFileKey + '.json')
Set-Content -LiteralPath $crossRepoSelectorActivePath -Encoding ASCII -NoNewline -Value @"
{
  "backend_family": "langgraph",
  "selector_id": "selector-cross-repo",
  "repo_root": "$($LegacySelectorRepoRoot.Replace('\', '\\'))",
  "worktree_id": "legacy-selector-repo",
  "thread_id": "$crossRepoSelectorThreadId",
  "team_name": "",
  "session_scope_id": "cross-repo-session",
  "leader_session_lineage": "cross-repo-session",
  "acquired_at": "2026-04-26T00:00:00Z",
  "last_heartbeat_at": "2026-04-26T00:00:00Z",
  "released_at": "",
  "generation": 1,
  "phase": "execute-parallel",
  "routing_posture": "copied_cross_repo_selector",
  "routing_eligible": true
}
"@
Set-Content -LiteralPath $crossRepoSelectorBackendPath -Encoding ASCII -NoNewline -Value @"
{
  "backend": "langgraph",
  "thread_id": "$crossRepoSelectorThreadId",
  "phase": "execute-parallel",
  "status": "resumed",
  "updated_at": "2026-04-26T00:00:00Z",
  "routing_eligible": true,
  "auto_route_eligible": true,
  "routing_posture": "active_scoped_selector"
}
"@
Set-Content -LiteralPath $crossRepoSelectorThreadPath -Encoding ASCII -NoNewline -Value @"
{
  "thread_id": "$crossRepoSelectorThreadId",
  "phase": "execute-parallel",
  "status": "resumed",
  "updated_at": "2026-04-26T00:00:00Z"
}
"@

$crossRepoSelectorDurableState = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') -Arguments @(
  '-RepoRoot', $CrossRepoSelectorRepoRoot,
  '-Json'
)
Assert-Equal $crossRepoSelectorDurableState.state_class 'preserved_legacy_langgraph_artifact' 'Durable-state status should reject a copied cross-repo active selector and keep the LangGraph record inspect-only.'

$crossRepoSelectorPlan = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-auto.ps1') -Arguments @(
  '-Task', 'parallel feature work',
  '-Phase', 'execute-parallel',
  '-ParallelSlices', '2',
  '-RepoRoot', $CrossRepoSelectorRepoRoot,
  '-Json'
)
Assert-Equal $crossRepoSelectorPlan.effective_lane 'native_omx' 'Automatic team helper should fail closed to native_omx when an active selector belongs to another repo root.'
Assert-Equal $crossRepoSelectorPlan.decision 'launch' 'Automatic team helper should not auto-resume LangGraph from a copied cross-repo selector.'
Assert-Equal $crossRepoSelectorPlan.desired_durable_team.backend 'native_omx' 'Automatic team helper should keep the desired durable backend on native_omx for a copied cross-repo selector.'

Ensure-Directory -Path (Join-Path $ReleasedSelectorRepoRoot '.omx\state\selectors')
Ensure-Directory -Path (Join-Path $ReleasedSelectorRepoRoot '.omx\state\langgraph\threads')
$releasedSelectorThreadId = 'released-selector:default:thread-1'
$releasedSelectorThreadFileKey = $releasedSelectorThreadId.Replace(':', '__')
$releasedSelectorActivePath = Join-Path $ReleasedSelectorRepoRoot '.omx\state\selectors\active.json'
$releasedSelectorBackendPath = Join-Path $ReleasedSelectorRepoRoot '.omx\state\langgraph\backend.json'
$releasedSelectorThreadPath = Join-Path $ReleasedSelectorRepoRoot ('.omx\state\langgraph\threads\' + $releasedSelectorThreadFileKey + '.json')
Set-Content -LiteralPath $releasedSelectorActivePath -Encoding ASCII -NoNewline -Value @"
{
  "backend_family": "langgraph",
  "selector_id": "selector-released",
  "repo_root": "$($ReleasedSelectorRepoRoot.Replace('\', '\\'))",
  "worktree_id": "$(Split-Path -Leaf $ReleasedSelectorRepoRoot)",
  "thread_id": "$releasedSelectorThreadId",
  "team_name": "",
  "session_scope_id": "released-selector-session",
  "leader_session_lineage": "released-selector-session",
  "acquired_at": "2026-04-26T00:00:00Z",
  "last_heartbeat_at": "2026-04-26T00:00:00Z",
  "released_at": "2026-04-26T00:30:00Z",
  "generation": 1,
  "phase": "execute-parallel",
  "routing_posture": "released_selector",
  "routing_eligible": true
}
"@
Set-Content -LiteralPath $releasedSelectorBackendPath -Encoding ASCII -NoNewline -Value @"
{
  "backend": "langgraph",
  "thread_id": "$releasedSelectorThreadId",
  "phase": "execute-parallel",
  "status": "resumed",
  "updated_at": "2026-04-26T00:00:00Z",
  "routing_eligible": true,
  "auto_route_eligible": true,
  "routing_posture": "active_scoped_selector"
}
"@
Set-Content -LiteralPath $releasedSelectorThreadPath -Encoding ASCII -NoNewline -Value @"
{
  "thread_id": "$releasedSelectorThreadId",
  "phase": "execute-parallel",
  "status": "resumed",
  "updated_at": "2026-04-26T00:00:00Z"
}
"@

$releasedSelectorDurableState = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') -Arguments @(
  '-RepoRoot', $ReleasedSelectorRepoRoot,
  '-Json'
)
Assert-Equal $releasedSelectorDurableState.state_class 'preserved_legacy_langgraph_artifact' 'Durable-state status should reject a released active selector and keep the LangGraph record inspect-only.'

$releasedSelectorPlan = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-auto.ps1') -Arguments @(
  '-Task', 'parallel feature work',
  '-Phase', 'execute-parallel',
  '-ParallelSlices', '2',
  '-RepoRoot', $ReleasedSelectorRepoRoot,
  '-Json'
)
Assert-Equal $releasedSelectorPlan.effective_lane 'native_omx' 'Automatic team helper should fail closed to native_omx when an active selector has been released.'
Assert-Equal $releasedSelectorPlan.decision 'launch' 'Automatic team helper should not auto-resume LangGraph from a released selector.'
Assert-Equal $releasedSelectorPlan.desired_durable_team.backend 'native_omx' 'Automatic team helper should keep the desired durable backend on native_omx for a released selector.'

Ensure-Directory -Path (Join-Path $EmptyResidueRepoRoot '.omx\state\team\auto-team-empty')

$emptyResiduePlan = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-auto.ps1') -Arguments @(
  '-Task', 'parallel feature work',
  '-Phase', 'execute-parallel',
  '-ParallelSlices', '2',
  '-RepoRoot', $EmptyResidueRepoRoot,
  '-Json'
)
Assert-Equal $emptyResiduePlan.effective_lane 'native_omx' 'Automatic team helper should keep worker-centric future-session routing on native_omx when only empty unmanaged native residue exists.'
Assert-Equal $emptyResiduePlan.decision 'launch' 'Automatic team helper should ignore empty unmanaged native residue instead of forcing manual inspection.'

$emptyResidueCleanup = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-reconcile.ps1') -Arguments @(
  '-RepoRoot', $EmptyResidueRepoRoot,
  '-Json'
)
Assert-True ($emptyResidueCleanup.safe_cleanup_available -eq $true) 'Durable-state reconcile should keep empty unmanaged native residue as safe cleanup.'
Assert-True ($emptyResidueCleanup.manual_reconciliation_required -eq $false) 'Durable-state reconcile should not require manual reconciliation for empty unmanaged native residue.'
$emptyResidueSafeKinds = @($emptyResidueCleanup.safe_cleanup_candidates | ForEach-Object { [string]$_.kind })
Assert-ArrayContains -Actual $emptyResidueSafeKinds -Expected 'empty_unmanaged_native_team_directory' -Message 'Durable-state reconcile did not classify empty unmanaged native residue as safe cleanup.'

$autoPlanGraph = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-auto.ps1') -Arguments @(
  '-Task', 'checkpointed workflow execution',
  '-Phase', 'execute-parallel',
  '-ParallelSlices', '2',
  '-NeedsGraphPhases',
  '-RepoRoot', $AutoRepoRoot,
  '-Json'
)
Assert-Equal $autoPlanGraph.effective_lane 'langgraph' 'Automatic team helper did not select LangGraph when graph-phase signals were provided.'

$autoLaunch = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-auto.ps1') -Arguments @(
  '-Task', 'parallel feature work',
  '-Phase', 'execute-parallel',
  '-ParallelSlices', '2',
  '-RepoRoot', $AutoRepoRoot,
  '-Apply',
  '-Json'
)
Assert-Equal $autoLaunch.result.applied_decision 'launch' 'Automatic team helper did not launch the initial tracked team.'
Assert-Equal $autoLaunch.result.backend 'native_omx' 'Automatic team helper should launch native_omx for worker-centric execution by default when both capabilities are enabled.'
$trackedRecordPath = Join-Path $AutoRepoRoot '.omx\state\team\codex-auto-managed-team.json'
Assert-True (Test-Path -LiteralPath $trackedRecordPath) 'Automatic team helper did not create the tracked native_omx team record.'
$trackedRecord = Get-Content -LiteralPath $trackedRecordPath -Raw | ConvertFrom-Json
Assert-Equal $trackedRecord.worker_role 'team-executor' 'Tracked native_omx team record stored the wrong worker role.'
Assert-Equal ([int]$trackedRecord.worker_count) 2 'Tracked native_omx team record stored the wrong worker count.'

$durableStateTrackedNative = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') -Arguments @(
  '-RepoRoot', $AutoRepoRoot,
  '-Json'
)
Assert-Equal $durableStateTrackedNative.state_class 'tracked_native_team' 'Durable-state status did not classify tracked native durable-team state correctly.'
Assert-Equal $durableStateTrackedNative.backend_family 'native_omx' 'Durable-state status did not report native_omx for tracked team state.'
Assert-Equal $durableStateTrackedNative.tracked_identity $trackedRecord.team_name 'Durable-state status did not report the tracked native team identity.'
Assert-Equal $durableStateTrackedNative.worker_shape.worker_role 'team-executor' 'Durable-state status did not report the tracked native worker role.'
Assert-Equal ([int]$durableStateTrackedNative.worker_shape.worker_count) 2 'Durable-state status did not report the tracked native worker count.'
Assert-Equal $durableStateTrackedNative.inspect_pointer.script 'omx-team-ops.ps1' 'Durable-state status did not point native inspection to omx-team-ops.ps1.'
Assert-Equal $durableStateTrackedNative.selected_backend 'langgraph' 'Durable-state status should preserve the user-level selected backend even when repo state is native_omx.'
Assert-True ($durableStateTrackedNative.capability_readiness.native_omx.user_level_selected -eq $false) 'Durable-state status should distinguish native_omx as not selected by the user-level backend switch.'
Assert-True ($durableStateTrackedNative.capability_readiness.native_omx.repo_state_selected -eq $true) 'Durable-state status should distinguish native_omx as selected by tracked repo-local state.'
Assert-True ($durableStateTrackedNative.capability_readiness.native_omx.ready -eq $true) 'Durable-state status should report tracked native_omx state ready when helpers are installed and oh_my_codex is enabled.'
Assert-True ($durableStateTrackedNative.capability_readiness.langgraph.user_level_selected -eq $true) 'Durable-state status should preserve the user-level LangGraph selection alongside tracked native state.'
Assert-True ($durableStateTrackedNative.capability_readiness.langgraph.ready -eq $false) 'Durable-state status should keep LangGraph not ready when the shared runtime is missing.'

$autoReuse = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-auto.ps1') -Arguments @(
  '-Task', 'follow-up implementation slice',
  '-Phase', 'execute-parallel',
  '-ParallelSlices', '2',
  '-RepoRoot', $AutoRepoRoot,
  '-Apply',
  '-Json'
)
Assert-Equal $autoReuse.result.applied_decision 'reuse' 'Automatic team helper did not reuse the tracked native_omx team.'
Assert-Equal $autoReuse.result.team_name $trackedRecord.team_name 'Automatic team helper reused the wrong native_omx team.'

$autoSwitch = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-auto.ps1') -Arguments @(
  '-Task', 'stabilize regression cluster',
  '-Phase', 'stabilize',
  '-BlockingIssues', '2',
  '-RepoRoot', $AutoRepoRoot,
  '-Apply',
  '-Json'
)
Assert-Equal $autoSwitch.result.applied_decision 'switch' 'Automatic team helper should switch the tracked native_omx team shape during stabilization.'
$trackedRecord = Get-Content -LiteralPath $trackedRecordPath -Raw | ConvertFrom-Json
Assert-Equal $trackedRecord.worker_role 'debugger' 'Tracked native_omx team record did not switch to the debugger role during stabilization.'

$autoPlanGraphLaunch = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-auto.ps1') -Arguments @(
  '-Task', 'checkpointed workflow execution',
  '-Phase', 'execute-parallel',
  '-ParallelSlices', '2',
  '-NeedsGraphPhases',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Apply',
  '-Json'
)
Assert-Equal $autoPlanGraphLaunch.result.applied_decision 'launch' 'Automatic team helper did not launch the LangGraph lane when graph-phase signals were provided.'
Assert-Equal $autoPlanGraphLaunch.result.backend 'langgraph' 'Automatic team helper did not use LangGraph for graph-signaled execution.'
$langGraphTrackedRecordPath = Join-Path $UnmanagedAutoRepoRoot '.omx\state\langgraph\backend.json'
Assert-True (Test-Path -LiteralPath $langGraphTrackedRecordPath) 'Automatic team helper did not create the tracked LangGraph backend record.'
$langGraphTrackedRecord = Get-Content -LiteralPath $langGraphTrackedRecordPath -Raw | ConvertFrom-Json
Assert-Equal $langGraphTrackedRecord.backend 'langgraph' 'Tracked LangGraph backend record stored the wrong backend.'
Assert-True (-not [string]::IsNullOrWhiteSpace([string]$langGraphTrackedRecord.thread_id)) 'Tracked LangGraph backend record did not store a thread_id.'
$langGraphThreadId = [string]$langGraphTrackedRecord.thread_id
$langGraphThreadFileKey = $langGraphThreadId.Replace(':', '__')
$langGraphThreadPath = Join-Path $UnmanagedAutoRepoRoot ('.omx\state\langgraph\threads\' + $langGraphThreadFileKey + '.json')
Assert-True (Test-Path -LiteralPath $langGraphThreadPath) 'Automatic LangGraph launch did not create the thread record.'
$trackedRecord = Get-Content -LiteralPath $trackedRecordPath -Raw | ConvertFrom-Json
Assert-Equal $trackedRecord.worker_role 'debugger' 'Tracked native_omx team record changed unexpectedly after the separate LangGraph launch.'

$autoShutdownPlan = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-auto.ps1') -Arguments @(
  '-Task', 'final acceptance',
  '-Phase', 'verify-accept',
  '-RepoRoot', $AutoRepoRoot,
  '-Json'
)
Assert-Equal $autoShutdownPlan.decision 'shutdown' 'Automatic team helper should plan a shutdown in verify-accept when a tracked team exists.'

$autoShutdown = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-auto.ps1') -Arguments @(
  '-Task', 'final acceptance',
  '-Phase', 'verify-accept',
  '-RepoRoot', $AutoRepoRoot,
  '-Apply',
  '-Json'
)
Assert-Equal $autoShutdown.result.applied_decision 'shutdown' 'Automatic team helper did not shut down the tracked team in verify-accept.'
Assert-True (-not (Test-Path -LiteralPath $trackedRecordPath)) 'Automatic team helper did not remove the tracked team record after shutdown.'

$langGraphDirectRun = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-run.ps1') -Arguments @(
  '-Task', 'langgraph direct task',
  '-Phase', 'freeze-plan',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
$langGraphDirectThreadId = [string]$langGraphDirectRun.thread_id
Assert-True (-not [string]::IsNullOrWhiteSpace($langGraphDirectThreadId)) 'LangGraph run wrapper did not return a thread_id.'
$langGraphDirectBackendPath = Join-Path $UnmanagedAutoRepoRoot '.omx\state\langgraph\backend.json'
$langGraphDirectSelectorActivePath = Join-Path $UnmanagedAutoRepoRoot '.omx\state\selectors\active.json'
$langGraphDirectBackendRecord = Get-Content -LiteralPath $langGraphDirectBackendPath -Raw | ConvertFrom-Json
Assert-True ($langGraphDirectBackendRecord.routing_eligible -eq $true) 'LangGraph run wrapper did not persist a scoped routing-eligible backend record for a new thread.'
Assert-True (Test-Path -LiteralPath $langGraphDirectSelectorActivePath) 'LangGraph run wrapper did not persist the active selector file for a scoped activation.'
$langGraphDirectSelectorRecord = Get-Content -LiteralPath $langGraphDirectSelectorActivePath -Raw | ConvertFrom-Json
Assert-Equal ([string]$langGraphDirectSelectorRecord.thread_id) $langGraphDirectThreadId 'LangGraph active selector did not point at the new thread.'
Assert-True (-not [string]::IsNullOrWhiteSpace([string]$langGraphDirectSelectorRecord.session_scope_id)) 'LangGraph active selector did not persist a session_scope_id.'

$langGraphDirectStatus = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-status.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectStatus.thread.thread_id $langGraphDirectThreadId 'LangGraph status wrapper did not read the expected thread.'

$langGraphDirectResume = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-resume.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-Phase', 'execute-parallel',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectResume.thread.phase 'execute-parallel' 'LangGraph resume wrapper did not update the phase.'

$langGraphDirectInspect = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-inspect.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-True ([string]$langGraphDirectInspect.layout.root -like '*.omx*langgraph') 'LangGraph inspect wrapper did not expose the runtime layout.'
Assert-ArrayContains -Actual @($langGraphDirectInspect.contract.root_phases | ForEach-Object { [string]$_ }) -Expected 'freeze-plan' -Message 'LangGraph inspect wrapper did not expose the root graph contract.'
Assert-ArrayContains -Actual @($langGraphDirectInspect.contract.graph_contract_fields | ForEach-Object { [string]$_ }) -Expected 'state_schema_version' -Message 'LangGraph inspect wrapper did not expose graph-contract fields.'
$langGraphDirectKernel = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-kernel.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectKernel.graph_kernel_projection.current_node_id 'execute_parallel' 'LangGraph kernel wrapper did not expose the mapped execution node.'
Assert-Equal $langGraphDirectKernel.graph_kernel_projection.kernel_identity.graph_api_surface 'StateGraph' 'LangGraph kernel wrapper did not expose the StateGraph API surface.'
Assert-ArrayContains -Actual @($langGraphDirectKernel.graph_kernel_projection.available_next_nodes | ForEach-Object { [string]$_ }) -Expected 'integrate_converge' -Message 'LangGraph kernel wrapper did not expose next-node posture.'
$langGraphDirectEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectEngine.primary_runtime_engine_projection.current_execution_node 'execute_parallel' 'LangGraph engine wrapper did not expose the current execution node.'
Assert-Equal $langGraphDirectEngine.primary_runtime_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'LangGraph engine wrapper did not expose the StateGraph API surface.'
Assert-True ($null -ne $langGraphDirectEngine.primary_runtime_engine_projection.compile_supported) 'LangGraph engine wrapper did not expose compile support posture.'
$langGraphDirectInvocation = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-invocation.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-InvokeKind', 'invoke',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectInvocation.compiled_invocation_projection.current_execution_node 'execute_parallel' 'LangGraph invocation wrapper did not expose the current execution node.'
Assert-Equal $langGraphDirectInvocation.compiled_invocation_projection.invocation_identity.compiler_surface 'StateGraph.compile' 'LangGraph invocation wrapper did not expose the compiler surface.'
Assert-Equal $langGraphDirectInvocation.compiled_invocation_projection.last_invoke_kind 'invoke' 'LangGraph invocation wrapper did not record the requested invoke kind.'
$langGraphDirectLiveExecution = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-live-execution.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectLiveExecution.live_execution_projection.current_execution_node 'execute_parallel' 'LangGraph live-execution wrapper did not expose the current execution node.'
Assert-Equal $langGraphDirectLiveExecution.live_execution_projection.execution_identity.compiler_surface 'StateGraph.compile' 'LangGraph live-execution wrapper did not expose the compiler surface.'
Assert-Equal $langGraphDirectLiveExecution.live_execution_projection.last_run_kind 'invoke' 'LangGraph live-execution wrapper did not record the requested run kind.'
$langGraphDirectFullerEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-fuller-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectFullerEngine.fuller_live_primary_engine_projection.current_execution_node 'execute_parallel' 'LangGraph fuller-engine wrapper did not expose the current execution node.'
Assert-Equal $langGraphDirectFullerEngine.fuller_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'LangGraph fuller-engine wrapper did not expose the StateGraph API surface.'
Assert-Equal $langGraphDirectFullerEngine.fuller_live_primary_engine_projection.resulting_phase 'integrate-converge' 'LangGraph fuller-engine wrapper did not expose the resulting phase.'
$langGraphDirectDeeperEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-deeper-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RecursionLimit', '8',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectDeeperEngine.deeper_live_primary_engine_projection.current_execution_node 'execute_parallel' 'LangGraph deeper-engine wrapper did not expose the current execution node.'
Assert-Equal $langGraphDirectDeeperEngine.deeper_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'LangGraph deeper-engine wrapper did not expose the StateGraph API surface.'
Assert-Equal $langGraphDirectDeeperEngine.deeper_live_primary_engine_projection.stop_boundary 'phase_boundary' 'LangGraph deeper-engine wrapper did not expose the expected stop boundary.'
Assert-ArrayContains -Actual @($langGraphDirectDeeperEngine.deeper_live_primary_engine_projection.projected_phase_path | ForEach-Object { [string]$_ }) -Expected 'verify-accept' -Message 'LangGraph deeper-engine wrapper did not expose the projected phase path.'
$langGraphDirectSuperstepEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-superstep-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RecursionLimit', '8',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectSuperstepEngine.superstep_live_primary_engine_projection.current_execution_node 'execute_parallel' 'LangGraph superstep-engine wrapper did not expose the current execution node.'
Assert-Equal $langGraphDirectSuperstepEngine.superstep_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'LangGraph superstep-engine wrapper did not expose the StateGraph API surface.'
Assert-Equal $langGraphDirectSuperstepEngine.superstep_live_primary_engine_projection.stop_boundary 'phase_boundary' 'LangGraph superstep-engine wrapper did not expose the expected stop boundary.'
Assert-ArrayContains -Actual @($langGraphDirectSuperstepEngine.superstep_live_primary_engine_projection.phase_visit_path | ForEach-Object { [string]$_ }) -Expected 'verify-accept' -Message 'LangGraph superstep-engine wrapper did not expose the phase visit path.'
$langGraphDirectStatefulEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-stateful-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RecursionLimit', '8',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectStatefulEngine.stateful_live_primary_engine_projection.current_execution_node 'verify_accept' 'LangGraph stateful-engine wrapper did not expose the resulting execution node.'
Assert-Equal $langGraphDirectStatefulEngine.stateful_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'LangGraph stateful-engine wrapper did not expose the StateGraph API surface.'
Assert-Equal $langGraphDirectStatefulEngine.stateful_live_primary_engine_projection.stop_boundary 'phase_boundary' 'LangGraph stateful-engine wrapper did not expose the expected stop boundary.'
Assert-ArrayContains -Actual @($langGraphDirectStatefulEngine.stateful_live_primary_engine_projection.stateful_phase_path | ForEach-Object { [string]$_ }) -Expected 'verify-accept' -Message 'LangGraph stateful-engine wrapper did not expose the stateful phase path.'
Assert-ArrayContains -Actual @($langGraphDirectStatefulEngine.stateful_live_primary_engine_projection.stateful_transition_log | ForEach-Object { [string]$_ }) -Expected 'sequential:execute-parallel->integrate-converge' -Message 'LangGraph stateful-engine wrapper did not expose the stateful transition log.'
$langGraphDirectBoundaryEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-boundary-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RecursionLimit', '8',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectBoundaryEngine.boundary_state_live_primary_engine_projection.current_execution_node 'verify_accept' 'LangGraph boundary-engine wrapper did not expose the resulting execution node.'
Assert-Equal $langGraphDirectBoundaryEngine.boundary_state_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'LangGraph boundary-engine wrapper did not expose the StateGraph API surface.'
Assert-Equal $langGraphDirectBoundaryEngine.boundary_state_live_primary_engine_projection.stop_boundary 'phase_boundary' 'LangGraph boundary-engine wrapper did not expose the expected stop boundary.'
Assert-Equal $langGraphDirectBoundaryEngine.boundary_state_live_primary_engine_projection.boundary_state_kind 'ordinary' 'LangGraph boundary-engine wrapper did not expose the expected boundary-state kind.'
Assert-ArrayContains -Actual @($langGraphDirectBoundaryEngine.boundary_state_live_primary_engine_projection.boundary_phase_path | ForEach-Object { [string]$_ }) -Expected 'verify-accept' -Message 'LangGraph boundary-engine wrapper did not expose the boundary phase path.'
$langGraphDirectHandoffEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-handoff-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RecursionLimit', '8',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectHandoffEngine.handoff_state_live_primary_engine_projection.current_execution_node 'verify_accept' 'LangGraph handoff-engine wrapper did not expose the resulting execution node.'
Assert-Equal $langGraphDirectHandoffEngine.handoff_state_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'LangGraph handoff-engine wrapper did not expose the StateGraph API surface.'
Assert-Equal $langGraphDirectHandoffEngine.handoff_state_live_primary_engine_projection.stop_boundary 'phase_boundary' 'LangGraph handoff-engine wrapper did not expose the expected stop boundary.'
Assert-ArrayContains -Actual @($langGraphDirectHandoffEngine.handoff_state_live_primary_engine_projection.handoff_subgraph_path | ForEach-Object { [string]$_ }) -Expected 'verification' -Message 'LangGraph handoff-engine wrapper did not expose the handoff subgraph path.'
$langGraphDirectApprovalEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-approval-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RecursionLimit', '8',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectApprovalEngine.approval_aware_live_primary_engine_projection.current_execution_node 'verify_accept' 'LangGraph approval-engine wrapper did not expose the current execution node.'
Assert-Equal $langGraphDirectApprovalEngine.approval_aware_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'LangGraph approval-engine wrapper did not expose the StateGraph API surface.'
Assert-Equal $langGraphDirectApprovalEngine.approval_aware_live_primary_engine_projection.queue_posture 'no_interrupts' 'LangGraph approval-engine wrapper did not expose the ordinary queue posture before queue setup.'
Assert-Equal $langGraphDirectApprovalEngine.approval_aware_live_primary_engine_projection.resume_state_kind 'ordinary' 'LangGraph approval-engine wrapper did not expose the ordinary approval-aware resume state kind before queue setup.'
$langGraphDirectProvenanceEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-provenance-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RecursionLimit', '8',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectProvenanceEngine.provenance_state_live_primary_engine_projection.current_execution_node 'verify_accept' 'LangGraph provenance-engine wrapper did not expose the current execution node.'
Assert-Equal $langGraphDirectProvenanceEngine.provenance_state_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'LangGraph provenance-engine wrapper did not expose the StateGraph API surface.'
Assert-True ([int]$langGraphDirectProvenanceEngine.provenance_state_live_primary_engine_projection.history_target_count -ge 1) 'LangGraph provenance-engine wrapper did not expose history target count.'
$langGraphDirectAutoPolicy = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-auto-policy.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectAutoPolicy.automatic_runtime_policy_projection.migration_policy_posture 'auto_continue_safe' 'LangGraph auto-policy wrapper did not expose safe migration posture.'
Assert-ArrayContains -Actual @($langGraphDirectAutoPolicy.automatic_runtime_policy_projection.automatic_actions_available | ForEach-Object { [string]$_ }) -Expected 'continue_on_migration_safe' -Message 'LangGraph auto-policy wrapper did not expose automatic migration actions.'
$langGraphDirectGeneralizedRouting = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-generalized-routing.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectGeneralizedRouting.generalized_live_routing_projection.current_execution_node 'execute_parallel' 'LangGraph generalized-routing wrapper did not expose the current execution node.'
Assert-Equal $langGraphDirectGeneralizedRouting.generalized_live_routing_projection.routing_identity.graph_api_surface 'StateGraph' 'LangGraph generalized-routing wrapper did not expose the StateGraph API surface.'
Assert-Equal $langGraphDirectGeneralizedRouting.generalized_live_routing_projection.helper_pointer.command 'generalized-routing' 'LangGraph generalized-routing wrapper did not expose the helper command.'
$langGraphDirectMigration = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-migration.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-CurrentTopologyVersion', '1.1',
  '-CurrentStateSchemaVersion', '2.0',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectMigration.migration_projection.compatibility 'incompatible' 'LangGraph migration wrapper did not expose incompatible thread posture.'
Assert-Equal $langGraphDirectMigration.migration_projection.state_schema_compatibility 'incompatible' 'LangGraph migration wrapper did not expose state-schema incompatibility.'
Assert-ArrayContains -Actual @($langGraphDirectMigration.migration_projection.reason_codes | ForEach-Object { [string]$_ }) -Expected 'topology_minor_drift' -Message 'LangGraph migration wrapper did not expose bounded migration reason codes.'
Assert-Equal $langGraphDirectMigration.migration_projection.helper_pointer.command 'migration' 'LangGraph migration wrapper did not expose the migration helper pointer.'
$langGraphDirectMigrationEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-migration-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RecursionLimit', '8',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectMigrationEngine.migration_aware_live_primary_engine_projection.compatibility 'migration_safe' 'LangGraph migration-engine wrapper did not expose migration-safe posture for the live engine.'
Assert-Equal $langGraphDirectMigrationEngine.migration_aware_live_primary_engine_projection.compatibility_state_kind 'migration_safe_thread' 'LangGraph migration-engine wrapper did not expose the compatibility state kind.'
Assert-Equal $langGraphDirectMigrationEngine.migration_aware_live_primary_engine_projection.current_graph_contract.graph_contract_id 'codex_user_level_langgraph' 'LangGraph migration-engine wrapper did not expose current graph contract identity.'
Assert-Equal $langGraphDirectMigrationEngine.migration_aware_live_primary_engine_projection.helper_pointer.command 'migration-engine' 'LangGraph migration-engine wrapper did not expose the migration-engine helper pointer.'
$langGraphDirectMigrationEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-migration-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RecursionLimit', '8',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectMigrationEngine.migration_aware_live_primary_engine_projection.compatibility 'migration_safe' 'LangGraph migration-engine wrapper did not expose migration-safe posture for the live engine.'
Assert-Equal $langGraphDirectMigrationEngine.migration_aware_live_primary_engine_projection.compatibility_state_kind 'migration_safe_thread' 'LangGraph migration-engine wrapper did not expose the compatibility state kind.'
Assert-Equal $langGraphDirectMigrationEngine.migration_aware_live_primary_engine_projection.current_graph_contract.graph_contract_id 'codex_user_level_langgraph' 'LangGraph migration-engine wrapper did not expose current graph contract identity.'
Assert-Equal $langGraphDirectMigrationEngine.migration_aware_live_primary_engine_projection.helper_pointer.command 'migration-engine' 'LangGraph migration-engine wrapper did not expose the migration-engine helper pointer.'
$langGraphApprovalQueuePath = Join-Path $UnmanagedAutoRepoRoot 'approval-queue.json'
Set-Content -LiteralPath $langGraphApprovalQueuePath -Encoding UTF8 -NoNewline -Value @'
[
  { "interrupt_point": "freeze-plan", "value_summary": "review_plan", "reason": "approve_plan" },
  { "interrupt_point": "freeze-plan", "value_summary": "review_budget", "reason": "approve_budget" }
]
'@
$langGraphDirectApprovalQueue = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-approval-queue.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-InterruptItemFile', $langGraphApprovalQueuePath,
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectApprovalQueue.approval_queue_projection.queue_posture 'pending' 'LangGraph approval-queue wrapper did not expose pending queue posture.'
Assert-Equal ([int]$langGraphDirectApprovalQueue.approval_queue_projection.queue_size) 2 'LangGraph approval-queue wrapper did not expose queue size.'
$langGraphApprovalPendingIds = @($langGraphDirectApprovalQueue.approval_queue_projection.pending_interrupt_ids | ForEach-Object { [string]$_ })
Assert-Equal $langGraphDirectApprovalQueue.interrupt.interrupt_id $langGraphApprovalPendingIds[0] 'LangGraph approval-queue wrapper did not expose the current interrupt id.'
$langGraphApprovalResumeMapAPath = Join-Path $UnmanagedAutoRepoRoot 'approval-resume-a.json'
([ordered]@{ $langGraphApprovalPendingIds[0] = [ordered]@{ approved = $true } } | ConvertTo-Json -Compress) | Set-Content -LiteralPath $langGraphApprovalResumeMapAPath -Encoding UTF8 -NoNewline
$langGraphDirectPartialApprovalResume = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-resume.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-ResumeMapFile', $langGraphApprovalResumeMapAPath,
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectPartialApprovalResume.approval_queue_projection.queue_posture 'partially_resolved' 'LangGraph resume wrapper did not preserve partially resolved approval posture.'
Assert-Equal ([int]$langGraphDirectPartialApprovalResume.approval_queue_projection.pending_count) 1 'LangGraph resume wrapper did not preserve pending approval count.'
$langGraphApprovalResumeMapBPath = Join-Path $UnmanagedAutoRepoRoot 'approval-resume-b.json'
([ordered]@{ $langGraphApprovalPendingIds[1] = 'approved' } | ConvertTo-Json -Compress) | Set-Content -LiteralPath $langGraphApprovalResumeMapBPath -Encoding UTF8 -NoNewline
$langGraphDirectFinalApprovalResume = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-resume.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-ResumeMapFile', $langGraphApprovalResumeMapBPath,
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectFinalApprovalResume.approval_queue_projection.queue_posture 'resolved' 'LangGraph resume wrapper did not resolve the approval queue.'
Assert-Equal ([int]$langGraphDirectFinalApprovalResume.approval_queue_projection.resolved_count) 2 'LangGraph resume wrapper did not expose resolved approval count.'
$langGraphFinalInterruptPropertyCount = if ($null -eq $langGraphDirectFinalApprovalResume.interrupt) { 0 } else { @($langGraphDirectFinalApprovalResume.interrupt.PSObject.Properties).Count }
Assert-True ($langGraphFinalInterruptPropertyCount -eq 0) 'LangGraph resume wrapper should clear the interrupt after the approval queue resolves.'
$langGraphDirectApprovalEngineResolved = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-approval-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RecursionLimit', '8',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectApprovalEngineResolved.approval_aware_live_primary_engine_projection.queue_posture 'resolved' 'LangGraph approval-engine wrapper did not expose the resolved queue posture.'
Assert-Equal $langGraphDirectApprovalEngineResolved.approval_aware_live_primary_engine_projection.resume_state_kind 'resolved_queue_retained' 'LangGraph approval-engine wrapper did not expose the approval-aware resume state kind after queue resolution.'
$langGraphResolvedResumeKeys = @($langGraphDirectApprovalEngineResolved.approval_aware_live_primary_engine_projection.resume_map_keys | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $langGraphResolvedResumeKeys -Expected $langGraphApprovalPendingIds[0] -Message 'LangGraph approval-engine wrapper did not expose resolved resume-map keys.'
$langGraphRecoveredWaiting = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-recover.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-MutationIntent', 'explicit-recovery',
  '-ThreadField', 'status=waiting_for_approval,stop_reason=needs_human',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphRecoveredWaiting.thread.status 'waiting_for_approval' 'LangGraph recover wrapper did not restore the waiting_for_approval posture for auto-policy testing.'
$langGraphDirectAutoPolicyApply = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-auto-policy.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-Apply',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectAutoPolicyApply.thread.status 'resumed' 'LangGraph auto-policy wrapper did not auto-resume a resolved approval queue.'
Assert-Equal ([string]$langGraphDirectAutoPolicyApply.thread.stop_reason) '' 'LangGraph auto-policy wrapper did not clear the needs_human stop reason.'
Assert-True ([string]$langGraphDirectAutoPolicyApply.automatic_runtime_policy_projection.last_auto_action -like '*resume_after_resolved_queue*') 'LangGraph auto-policy wrapper did not record the resolved-queue auto action.'
$langGraphDirectMemory = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-memory.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-MemoryStoreConfigured',
  '-MemoryStoreKind', 'long_term_store',
  '-MemoryNamespace', 'codex/team,codex/bugs',
  '-SemanticMemoryEnabled',
  '-SemanticStoreKind', 'semantic_index',
  '-SemanticNamespace', 'codex/team',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectMemory.memory_projection.memory_store_kind 'long_term_store' 'LangGraph memory wrapper did not expose memory store kind.'
Assert-True ($langGraphDirectMemory.memory_projection.semantic_memory_enabled -eq $true) 'LangGraph memory wrapper did not expose semantic-memory posture.'
$langGraphDirectMemoryEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-memory-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RecursionLimit', '8',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectMemoryEngine.memory_aware_live_primary_engine_projection.memory_store_kind 'long_term_store' 'LangGraph memory-engine wrapper did not expose memory store kind.'
Assert-Equal $langGraphDirectMemoryEngine.memory_aware_live_primary_engine_projection.memory_state_kind 'memory_and_semantic_ready' 'LangGraph memory-engine wrapper did not expose memory state kind.'
Assert-True ($langGraphDirectMemoryEngine.memory_aware_live_primary_engine_projection.semantic_memory_enabled -eq $true) 'LangGraph memory-engine wrapper did not expose semantic-memory posture.'
Assert-Equal $langGraphDirectMemoryEngine.memory_aware_live_primary_engine_projection.semantic_store_kind 'semantic_index' 'LangGraph memory-engine wrapper did not expose semantic store kind.'
Assert-Equal $langGraphDirectMemoryEngine.memory_aware_live_primary_engine_projection.helper_pointer.command 'memory-engine' 'LangGraph memory-engine wrapper did not expose the memory-engine helper pointer.'
$langGraphRuntimeContextPath = Join-Path $UnmanagedAutoRepoRoot 'runtime-context.json'
Set-Content -LiteralPath $langGraphRuntimeContextPath -Encoding UTF8 -NoNewline -Value '{"user_id":"u-1","model_provider":"openai","db_dependency":"sqlite"}'
$langGraphDirectRuntime = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-runtime.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-ContextSchema', 'operator_context',
  '-RuntimeContextFile', $langGraphRuntimeContextPath,
  '-StoreConfigured',
  '-StoreAccessExpected',
  '-StoreKind', 'repo_local',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectRuntime.runtime_injection_projection.context_schema 'operator_context' 'LangGraph runtime wrapper did not expose context schema.'
Assert-True ($langGraphDirectRuntime.runtime_injection_projection.runtime_context_present -eq $true) 'LangGraph runtime wrapper did not expose runtime-context presence.'
Assert-Equal $langGraphDirectRuntime.runtime_injection_projection.store_kind 'repo_local' 'LangGraph runtime wrapper did not expose store kind.'
$langGraphDirectRuntimeEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-runtime-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RecursionLimit', '8',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectRuntimeEngine.runtime_aware_live_primary_engine_projection.context_schema 'operator_context' 'LangGraph runtime-engine wrapper did not expose context schema.'
Assert-Equal $langGraphDirectRuntimeEngine.runtime_aware_live_primary_engine_projection.runtime_state_kind 'runtime_context_and_store_ready' 'LangGraph runtime-engine wrapper did not expose runtime state kind.'
Assert-True ($langGraphDirectRuntimeEngine.runtime_aware_live_primary_engine_projection.runtime_context_present -eq $true) 'LangGraph runtime-engine wrapper did not expose runtime-context presence.'
Assert-Equal $langGraphDirectRuntimeEngine.runtime_aware_live_primary_engine_projection.store_kind 'repo_local' 'LangGraph runtime-engine wrapper did not expose store kind.'
Assert-Equal $langGraphDirectRuntimeEngine.runtime_aware_live_primary_engine_projection.helper_pointer.command 'runtime-engine' 'LangGraph runtime-engine wrapper did not expose the runtime-engine helper pointer.'
$langGraphDirectStream = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-stream.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-StreamMode', 'updates,debug',
  '-Subgraphs',
  '-EventKind', 'debug',
  '-Namespace', 'execution,verify',
  '-DebugSummary', 'entered verify branch',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal (@($langGraphDirectStream.stream_projection.selected_modes) -join ',') 'debug,updates' 'LangGraph stream wrapper did not expose selected stream modes.'
Assert-True ($langGraphDirectStream.stream_projection.subgraphs -eq $true) 'LangGraph stream wrapper did not expose nested subgraph posture.'
Assert-Equal $langGraphDirectStream.stream_projection.latest_event_kind 'debug' 'LangGraph stream wrapper did not expose latest event kind.'
$langGraphDirectSubgraphs = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-subgraphs.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-ArrayContains -Actual @($langGraphDirectSubgraphs.subgraph_projection.available_subgraphs | ForEach-Object { [string]$_ }) -Expected 'execution' -Message 'LangGraph subgraphs wrapper did not expose the execution subgraph.'
Assert-Equal ([string]$langGraphDirectSubgraphs.subgraph_projection.active_subgraph) 'execution' 'LangGraph subgraphs wrapper did not expose the active subgraph for the tracked thread.'
$langGraphDirectSubgraphState = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-subgraph-state.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal ([string]$langGraphDirectSubgraphState.subgraph_state_inspection_projection.active_subgraph) 'execution' 'LangGraph subgraph-state wrapper did not expose the active subgraph.'
Assert-Equal ([string]$langGraphDirectSubgraphState.subgraph_state_inspection_projection.persistence_mode) 'per_invocation' 'LangGraph subgraph-state wrapper did not expose the bounded persistence mode.'
Assert-Equal ([string]$langGraphDirectSubgraphState.subgraph_state_inspection_projection.helper_pointer.command) 'subgraph-state' 'LangGraph subgraph-state wrapper did not expose the helper command.'
$langGraphDirectHistory = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-history.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectHistory.history_projection.compatibility 'tracked_history' 'LangGraph history wrapper did not expose tracked history.'
$langGraphReplayTargetId = [string](@($langGraphDirectHistory.history_projection.available_targets | Where-Object { [string]$_.target_kind -eq 'checkpoint' -and [string]$_.checkpoint_kind -eq 'skeleton' } | Select-Object -First 1).target_id)
Assert-True (-not [string]::IsNullOrWhiteSpace($langGraphReplayTargetId)) 'LangGraph history wrapper did not expose a replayable skeleton checkpoint target.'
$langGraphDirectReplay = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-replay.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-TargetId', $langGraphReplayTargetId,
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectReplay.target_kind 'checkpoint' 'LangGraph replay wrapper did not expose the requested checkpoint target.'
Assert-True ($langGraphDirectReplay.read_only -eq $true) 'LangGraph replay wrapper did not remain read-only.'
$langGraphCliPath = Join-Path $CodexHome 'python\langgraph_durable_orchestrator\cli.py'

$langGraphWriteBrief = & $ResolvedPythonPath $langGraphCliPath 'write-brief' '--thread-id' $langGraphDirectThreadId '--repo-root' $UnmanagedAutoRepoRoot '--objective' 'ship stable artifact contract' '--source-evidence-refs' 'doc:proposal' 'doc:design'
$langGraphWriteBriefExitCode = $LASTEXITCODE
Assert-Equal $langGraphWriteBriefExitCode 0 'Generated LangGraph CLI did not write a frozen implementation brief successfully.'
$langGraphWriteBriefJson = $langGraphWriteBrief | ConvertFrom-Json
Assert-True (-not [string]::IsNullOrWhiteSpace([string]$langGraphWriteBriefJson.brief.brief_id)) 'LangGraph write-brief did not persist a brief_id.'
Assert-Equal (@($langGraphWriteBriefJson.brief.source_evidence_refs).Count) 2 'LangGraph write-brief did not preserve source_evidence_refs.'

$langGraphEnqueueSurvivor = & $ResolvedPythonPath $langGraphCliPath 'enqueue-survivor' '--thread-id' $langGraphDirectThreadId '--repo-root' $UnmanagedAutoRepoRoot '--bug-id' 'bug-1' '--title' 'judge survivor' '--severity' 'high' '--evidence' 'trace pointer' '--judge-verdict' 'survives' '--owner-lane' 'debugger' '--status' 'queued' '--verification-result' 'pending'
$langGraphEnqueueSurvivorExitCode = $LASTEXITCODE
Assert-Equal $langGraphEnqueueSurvivorExitCode 0 'Generated LangGraph CLI did not enqueue a survivor successfully.'
$langGraphEnqueueSurvivorJson = $langGraphEnqueueSurvivor | ConvertFrom-Json
Assert-Equal $langGraphEnqueueSurvivorJson.queue.queue_kind 'judge_approved_survivor_queue' 'LangGraph enqueue-survivor did not persist the stable queue_kind.'
Assert-Equal ([int]$langGraphEnqueueSurvivorJson.durable_artifacts.survivor_count) 1 'LangGraph enqueue-survivor did not report the expected survivor count.'
$langGraphDirectArtifactEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-artifact-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RecursionLimit', '8',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectArtifactEngine.durable_artifact_aware_live_primary_engine_projection.current_execution_node 'verify_accept' 'LangGraph artifact-engine wrapper did not expose the current execution node.'
Assert-Equal $langGraphDirectArtifactEngine.durable_artifact_aware_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'LangGraph artifact-engine wrapper did not expose the StateGraph API surface.'
Assert-Equal $langGraphDirectArtifactEngine.durable_artifact_aware_live_primary_engine_projection.artifact_state_kind 'brief_and_survivor_queue_present' 'LangGraph artifact-engine wrapper did not expose the durable artifact state kind.'
Assert-Equal ([int]$langGraphDirectArtifactEngine.durable_artifact_aware_live_primary_engine_projection.implementation_brief_source_evidence_ref_count) 2 'LangGraph artifact-engine wrapper did not expose the implementation brief evidence count.'
Assert-Equal $langGraphDirectArtifactEngine.durable_artifact_aware_live_primary_engine_projection.survivor_queue_kind 'judge_approved_survivor_queue' 'LangGraph artifact-engine wrapper did not expose the survivor queue kind.'
Assert-Equal ([int]$langGraphDirectArtifactEngine.durable_artifact_aware_live_primary_engine_projection.survivor_count) 1 'LangGraph artifact-engine wrapper did not expose the survivor count.'

$langGraphReducerPayloadPath = Join-Path $UnmanagedAutoRepoRoot 'reducer-branch-a.json'
Set-Content -LiteralPath $langGraphReducerPayloadPath -Encoding UTF8 -NoNewline -Value @'
{
  "branch_id": "branch-a",
  "fanout_state": "partial",
  "reducer_channels": {
    "branch_findings": [
      { "finding_id": "finding-2", "message": "second" },
      { "finding_id": "finding-1", "message": "first" }
    ],
    "branch_evidence_refs": [
      { "evidence_id": "evidence-1", "pointer": "trace:a" }
    ]
  }
}
'@

$langGraphMergeBranch = & $ResolvedPythonPath $langGraphCliPath 'merge-branch' '--thread-id' $langGraphDirectThreadId '--repo-root' $UnmanagedAutoRepoRoot '--payload-file' $langGraphReducerPayloadPath
$langGraphMergeBranchExitCode = $LASTEXITCODE
Assert-Equal $langGraphMergeBranchExitCode 0 'Generated LangGraph CLI did not merge reducer-backed branch payload successfully.'
$langGraphMergeBranchJson = $langGraphMergeBranch | ConvertFrom-Json
Assert-Equal $langGraphMergeBranchJson.reducer_projection.compatibility 'reducer_aware' 'LangGraph reducer merge did not expose reducer-aware compatibility.'
Assert-Equal $langGraphMergeBranchJson.reducer_projection.fanout_state 'partial' 'LangGraph reducer merge did not preserve fanout_state.'
Assert-Equal ([int]$langGraphMergeBranchJson.reducer_projection.channel_item_counts.branch_findings) 2 'LangGraph reducer merge did not expose the expected finding count.'

$langGraphReducerInvalidPayloadPath = Join-Path $UnmanagedAutoRepoRoot 'reducer-invalid.json'
Set-Content -LiteralPath $langGraphReducerInvalidPayloadPath -Encoding UTF8 -NoNewline -Value @'
{
  "branch_id": "branch-b",
  "fanout_state": "complete",
  "single_writer_updates": {
    "phase": "stabilize"
  }
}
'@

$langGraphMergeInvalid = & $ResolvedPythonPath $langGraphCliPath 'merge-branch' '--thread-id' $langGraphDirectThreadId '--repo-root' $UnmanagedAutoRepoRoot '--payload-file' $langGraphReducerInvalidPayloadPath
$langGraphMergeInvalidExitCode = $LASTEXITCODE
Assert-Equal $langGraphMergeInvalidExitCode 0 'Generated LangGraph CLI did not surface invalid multi-writer state successfully.'
$langGraphMergeInvalidJson = $langGraphMergeInvalid | ConvertFrom-Json
Assert-True ($langGraphMergeInvalidJson.reducer_projection.invalid_multi_writer_detected -eq $true) 'LangGraph reducer merge did not detect invalid multi-writer updates.'
Assert-Equal $langGraphMergeInvalidJson.thread.phase 'execute-parallel' 'LangGraph reducer merge should not overwrite protected single-writer fields.'
$langGraphDirectReducerEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-reducer-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphDirectThreadId,
  '-RunKind', 'invoke',
  '-RecursionLimit', '8',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectReducerEngine.reducer_aware_live_primary_engine_projection.current_execution_node 'verify_accept' 'LangGraph reducer-engine wrapper did not expose the current execution node.'
Assert-Equal $langGraphDirectReducerEngine.reducer_aware_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'LangGraph reducer-engine wrapper did not expose the StateGraph API surface.'
Assert-Equal $langGraphDirectReducerEngine.reducer_aware_live_primary_engine_projection.merge_state_kind 'invalid_multi_writer_detected' 'LangGraph reducer-engine wrapper did not expose the reducer merge state kind.'
Assert-Equal $langGraphDirectReducerEngine.reducer_aware_live_primary_engine_projection.fanout_state 'complete' 'LangGraph reducer-engine wrapper did not expose the reducer fanout state.'
Assert-True ($langGraphDirectReducerEngine.reducer_aware_live_primary_engine_projection.invalid_multi_writer_detected -eq $true) 'LangGraph reducer-engine wrapper did not expose invalid multi-writer posture.'
Assert-Equal ([int]$langGraphDirectReducerEngine.reducer_aware_live_primary_engine_projection.channel_item_counts.branch_findings) 2 'LangGraph reducer-engine wrapper did not expose reducer channel item counts.'

$durableStateTrackedLangGraph = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') -Arguments @(
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $durableStateTrackedLangGraph.state_class 'tracked_langgraph_thread' 'Durable-state status did not classify scoped LangGraph state correctly.'
Assert-Equal $durableStateTrackedLangGraph.backend_family 'langgraph' 'Durable-state status did not report langgraph for tracked LangGraph state.'
Assert-Equal $durableStateTrackedLangGraph.tracked_identity $langGraphDirectThreadId 'Durable-state status did not report the tracked LangGraph thread identity.'
Assert-Equal $durableStateTrackedLangGraph.inspect_pointer.script 'omx-langgraph-inspect.ps1' 'Durable-state status did not point LangGraph inspection to omx-langgraph-inspect.ps1.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.kernel_projection.current_node_id 'execute_parallel' 'Durable-state status did not expose LangGraph graph-kernel current node.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.kernel_projection.kernel_identity.graph_api_surface 'StateGraph' 'Durable-state status did not expose LangGraph graph-kernel identity.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.kernel_projection.helper_pointer.script 'omx-langgraph-kernel.ps1' 'Durable-state status did not expose the LangGraph graph-kernel helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.primary_runtime_engine_projection.current_execution_node 'execute_parallel' 'Durable-state status did not expose LangGraph primary-runtime execution node.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.primary_runtime_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'Durable-state status did not expose LangGraph primary-runtime engine identity.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.primary_runtime_engine_projection.helper_pointer.script 'omx-langgraph-engine.ps1' 'Durable-state status did not expose the LangGraph primary-runtime helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.compiled_invocation_projection.current_execution_node 'execute_parallel' 'Durable-state status did not expose LangGraph compiled-invocation execution node.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.compiled_invocation_projection.invocation_identity.compiler_surface 'StateGraph.compile' 'Durable-state status did not expose LangGraph compiled-invocation identity.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.compiled_invocation_projection.helper_pointer.script 'omx-langgraph-invocation.ps1' 'Durable-state status did not expose the LangGraph compiled-invocation helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.live_execution_projection.current_execution_node 'execute_parallel' 'Durable-state status did not expose LangGraph live-execution execution node.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.live_execution_projection.execution_identity.compiler_surface 'StateGraph.compile' 'Durable-state status did not expose LangGraph live-execution identity.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.live_execution_projection.helper_pointer.script 'omx-langgraph-live-execution.ps1' 'Durable-state status did not expose the LangGraph live-execution helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.fuller_live_primary_engine_projection.current_execution_node 'execute_parallel' 'Durable-state status did not expose LangGraph fuller-engine execution node.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.fuller_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'Durable-state status did not expose LangGraph fuller-engine identity.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.fuller_live_primary_engine_projection.resulting_phase 'integrate-converge' 'Durable-state status did not expose LangGraph fuller-engine resulting phase.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.fuller_live_primary_engine_projection.helper_pointer.script 'omx-langgraph-fuller-engine.ps1' 'Durable-state status did not expose the LangGraph fuller-engine helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.deeper_live_primary_engine_projection.current_execution_node 'execute_parallel' 'Durable-state status did not expose LangGraph deeper-engine execution node.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.deeper_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'Durable-state status did not expose LangGraph deeper-engine identity.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.deeper_live_primary_engine_projection.stop_boundary 'phase_boundary' 'Durable-state status did not expose LangGraph deeper-engine stop boundary.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.deeper_live_primary_engine_projection.helper_pointer.script 'omx-langgraph-deeper-engine.ps1' 'Durable-state status did not expose the LangGraph deeper-engine helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.superstep_live_primary_engine_projection.current_execution_node 'execute_parallel' 'Durable-state status did not expose LangGraph superstep-engine execution node.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.superstep_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'Durable-state status did not expose LangGraph superstep-engine identity.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.superstep_live_primary_engine_projection.stop_boundary 'phase_boundary' 'Durable-state status did not expose LangGraph superstep-engine stop boundary.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.superstep_live_primary_engine_projection.helper_pointer.script 'omx-langgraph-superstep-engine.ps1' 'Durable-state status did not expose the LangGraph superstep-engine helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.stateful_live_primary_engine_projection.current_execution_node 'verify_accept' 'Durable-state status did not expose LangGraph stateful-engine resulting execution node.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.stateful_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'Durable-state status did not expose LangGraph stateful-engine identity.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.stateful_live_primary_engine_projection.stop_boundary 'phase_boundary' 'Durable-state status did not expose LangGraph stateful-engine stop boundary.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.stateful_live_primary_engine_projection.helper_pointer.script 'omx-langgraph-stateful-engine.ps1' 'Durable-state status did not expose the LangGraph stateful-engine helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.boundary_state_live_primary_engine_projection.current_execution_node 'verify_accept' 'Durable-state status did not expose LangGraph boundary-engine resulting execution node.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.boundary_state_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'Durable-state status did not expose LangGraph boundary-engine identity.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.boundary_state_live_primary_engine_projection.stop_boundary 'phase_boundary' 'Durable-state status did not expose LangGraph boundary-engine stop boundary.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.boundary_state_live_primary_engine_projection.helper_pointer.script 'omx-langgraph-boundary-engine.ps1' 'Durable-state status did not expose the LangGraph boundary-engine helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.handoff_state_live_primary_engine_projection.current_execution_node 'verify_accept' 'Durable-state status did not expose LangGraph handoff-engine resulting execution node.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.handoff_state_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'Durable-state status did not expose LangGraph handoff-engine identity.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.handoff_state_live_primary_engine_projection.stop_boundary 'phase_boundary' 'Durable-state status did not expose LangGraph handoff-engine stop boundary.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.handoff_state_live_primary_engine_projection.helper_pointer.script 'omx-langgraph-handoff-engine.ps1' 'Durable-state status did not expose the LangGraph handoff-engine helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.approval_aware_live_primary_engine_projection.current_execution_node 'verify_accept' 'Durable-state status did not expose LangGraph approval-engine current execution node.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.approval_aware_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'Durable-state status did not expose LangGraph approval-engine identity.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.approval_aware_live_primary_engine_projection.queue_posture 'resolved' 'Durable-state status did not expose LangGraph approval-engine queue posture.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.approval_aware_live_primary_engine_projection.helper_pointer.script 'omx-langgraph-approval-engine.ps1' 'Durable-state status did not expose the LangGraph approval-engine helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.provenance_state_live_primary_engine_projection.current_execution_node 'verify_accept' 'Durable-state status did not expose LangGraph provenance-engine current execution node.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.provenance_state_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'Durable-state status did not expose LangGraph provenance-engine identity.'
Assert-True ([int]$durableStateTrackedLangGraph.backend_specific.langgraph.provenance_state_live_primary_engine_projection.history_target_count -ge 1) 'Durable-state status did not expose LangGraph provenance-engine history target count.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.provenance_state_live_primary_engine_projection.helper_pointer.script 'omx-langgraph-provenance-engine.ps1' 'Durable-state status did not expose the LangGraph provenance-engine helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.durable_artifact_aware_live_primary_engine_projection.current_execution_node 'verify_accept' 'Durable-state status did not expose LangGraph artifact-engine current execution node.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.durable_artifact_aware_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'Durable-state status did not expose LangGraph artifact-engine identity.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.durable_artifact_aware_live_primary_engine_projection.artifact_state_kind 'brief_and_survivor_queue_present' 'Durable-state status did not expose LangGraph artifact-engine state kind.'
Assert-Equal ([int]$durableStateTrackedLangGraph.backend_specific.langgraph.durable_artifact_aware_live_primary_engine_projection.implementation_brief_source_evidence_ref_count) 2 'Durable-state status did not expose LangGraph artifact-engine brief evidence count.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.durable_artifact_aware_live_primary_engine_projection.survivor_queue_kind 'judge_approved_survivor_queue' 'Durable-state status did not expose LangGraph artifact-engine survivor queue kind.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.durable_artifact_aware_live_primary_engine_projection.helper_pointer.script 'omx-langgraph-artifact-engine.ps1' 'Durable-state status did not expose the LangGraph artifact-engine helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.reducer_aware_live_primary_engine_projection.current_execution_node 'verify_accept' 'Durable-state status did not expose LangGraph reducer-engine current execution node.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.reducer_aware_live_primary_engine_projection.engine_identity.graph_api_surface 'StateGraph' 'Durable-state status did not expose LangGraph reducer-engine identity.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.reducer_aware_live_primary_engine_projection.merge_state_kind 'invalid_multi_writer_detected' 'Durable-state status did not expose LangGraph reducer-engine state kind.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.reducer_aware_live_primary_engine_projection.fanout_state 'complete' 'Durable-state status did not expose LangGraph reducer-engine fanout state.'
Assert-True ($durableStateTrackedLangGraph.backend_specific.langgraph.reducer_aware_live_primary_engine_projection.invalid_multi_writer_detected -eq $true) 'Durable-state status did not expose LangGraph reducer-engine invalid multi-writer posture.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.reducer_aware_live_primary_engine_projection.helper_pointer.script 'omx-langgraph-reducer-engine.ps1' 'Durable-state status did not expose the LangGraph reducer-engine helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.automatic_runtime_policy_projection.migration_policy_posture 'auto_continue_safe' 'Durable-state status did not expose LangGraph automatic runtime-policy migration posture.'
Assert-True ([string]$durableStateTrackedLangGraph.backend_specific.langgraph.automatic_runtime_policy_projection.last_auto_action -like '*resume_after_resolved_queue*') 'Durable-state status did not expose the LangGraph automatic runtime-policy action.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.automatic_runtime_policy_projection.helper_pointer.script 'omx-langgraph-auto-policy.ps1' 'Durable-state status did not expose the LangGraph auto-policy helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.generalized_live_routing_projection.current_execution_node 'execute_parallel' 'Durable-state status did not expose LangGraph generalized-routing execution node.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.generalized_live_routing_projection.routing_identity.graph_api_surface 'StateGraph' 'Durable-state status did not expose LangGraph generalized-routing identity.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.generalized_live_routing_projection.helper_pointer.script 'omx-langgraph-generalized-routing.ps1' 'Durable-state status did not expose the LangGraph generalized-routing helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.approval_queue_projection.queue_posture 'resolved' 'Durable-state status did not expose LangGraph approval-queue posture.'
Assert-Equal ([int]$durableStateTrackedLangGraph.backend_specific.langgraph.approval_queue_projection.resolved_count) 2 'Durable-state status did not expose LangGraph resolved approval count.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.approval_queue_projection.helper_pointer.script 'omx-langgraph-approval-queue.ps1' 'Durable-state status did not expose the LangGraph approval-queue helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.migration_projection.compatibility 'migration_safe' 'Durable-state status did not expose LangGraph migration compatibility.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.migration_projection.current_graph_contract.graph_contract_id 'codex_user_level_langgraph' 'Durable-state status did not expose the current LangGraph graph-contract identity.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.migration_projection.helper_pointer.script 'omx-langgraph-migration.ps1' 'Durable-state status did not expose the LangGraph migration helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.migration_aware_live_primary_engine_projection.compatibility 'migration_safe' 'Durable-state status did not expose LangGraph migration-engine compatibility.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.migration_aware_live_primary_engine_projection.compatibility_state_kind 'migration_safe_thread' 'Durable-state status did not expose LangGraph migration-engine state kind.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.migration_aware_live_primary_engine_projection.current_graph_contract.graph_contract_id 'codex_user_level_langgraph' 'Durable-state status did not expose LangGraph migration-engine current graph contract.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.migration_aware_live_primary_engine_projection.helper_pointer.script 'omx-langgraph-migration-engine.ps1' 'Durable-state status did not expose the LangGraph migration-engine helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.memory_projection.memory_store_kind 'long_term_store' 'Durable-state status did not expose LangGraph memory store kind.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.memory_projection.semantic_store_kind 'semantic_index' 'Durable-state status did not expose LangGraph semantic store kind.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.memory_projection.helper_pointer.script 'omx-langgraph-memory.ps1' 'Durable-state status did not expose the LangGraph memory helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.runtime_injection_projection.context_schema 'operator_context' 'Durable-state status did not expose LangGraph runtime context schema.'
Assert-True ($durableStateTrackedLangGraph.backend_specific.langgraph.runtime_injection_projection.runtime_context_present -eq $true) 'Durable-state status did not expose LangGraph runtime-context presence.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.runtime_injection_projection.store_kind 'repo_local' 'Durable-state status did not expose LangGraph store kind.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.runtime_injection_projection.helper_pointer.script 'omx-langgraph-runtime.ps1' 'Durable-state status did not expose the LangGraph runtime helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.runtime_aware_live_primary_engine_projection.context_schema 'operator_context' 'Durable-state status did not expose LangGraph runtime-engine context schema.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.runtime_aware_live_primary_engine_projection.runtime_state_kind 'runtime_context_and_store_ready' 'Durable-state status did not expose LangGraph runtime-engine state kind.'
Assert-True ($durableStateTrackedLangGraph.backend_specific.langgraph.runtime_aware_live_primary_engine_projection.runtime_context_present -eq $true) 'Durable-state status did not expose LangGraph runtime-engine context presence.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.runtime_aware_live_primary_engine_projection.store_kind 'repo_local' 'Durable-state status did not expose LangGraph runtime-engine store kind.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.runtime_aware_live_primary_engine_projection.helper_pointer.script 'omx-langgraph-runtime-engine.ps1' 'Durable-state status did not expose the LangGraph runtime-engine helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.memory_aware_live_primary_engine_projection.memory_store_kind 'long_term_store' 'Durable-state status did not expose LangGraph memory-engine memory store kind.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.memory_aware_live_primary_engine_projection.memory_state_kind 'memory_and_semantic_ready' 'Durable-state status did not expose LangGraph memory-engine state kind.'
Assert-True ($durableStateTrackedLangGraph.backend_specific.langgraph.memory_aware_live_primary_engine_projection.semantic_memory_enabled -eq $true) 'Durable-state status did not expose LangGraph memory-engine semantic posture.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.memory_aware_live_primary_engine_projection.semantic_store_kind 'semantic_index' 'Durable-state status did not expose LangGraph memory-engine semantic store kind.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.memory_aware_live_primary_engine_projection.helper_pointer.script 'omx-langgraph-memory-engine.ps1' 'Durable-state status did not expose the LangGraph memory-engine helper pointer.'
Assert-Equal (@($durableStateTrackedLangGraph.backend_specific.langgraph.stream_projection.selected_modes) -join ',') 'debug,updates' 'Durable-state status did not expose LangGraph stream modes.'
Assert-True ($durableStateTrackedLangGraph.backend_specific.langgraph.stream_projection.subgraphs -eq $true) 'Durable-state status did not expose LangGraph nested subgraph stream posture.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.stream_projection.latest_event_kind 'debug' 'Durable-state status did not expose LangGraph latest stream event kind.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.stream_projection.helper_pointer.script 'omx-langgraph-stream.ps1' 'Durable-state status did not expose the LangGraph stream helper pointer.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.subgraph_projection.active_subgraph 'execution' 'Durable-state status did not expose the active LangGraph subgraph.'
Assert-ArrayContains -Actual @($durableStateTrackedLangGraph.backend_specific.langgraph.subgraph_projection.available_subgraphs | ForEach-Object { [string]$_ }) -Expected 'verification' -Message 'Durable-state status did not expose the available LangGraph subgraphs.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.subgraph_projection.helper_pointer.script 'omx-langgraph-subgraphs.ps1' 'Durable-state status did not expose the LangGraph subgraph-library helper.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.subgraph_state_inspection_projection.active_subgraph 'execution' 'Durable-state status did not expose LangGraph subgraph-state active subgraph.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.subgraph_state_inspection_projection.persistence_mode 'per_invocation' 'Durable-state status did not expose LangGraph subgraph-state persistence mode.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.subgraph_state_inspection_projection.helper_pointer.script 'omx-langgraph-subgraph-state.ps1' 'Durable-state status did not expose the LangGraph subgraph-state helper.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.history.compatibility 'tracked_history' 'Durable-state status did not expose LangGraph history compatibility.'
Assert-True ([int]$durableStateTrackedLangGraph.backend_specific.langgraph.history.target_count -ge 4) 'Durable-state status did not expose LangGraph history targets.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.helper_pointers.recover_time_travel.script 'omx-langgraph-recover.ps1' 'Durable-state status did not expose the LangGraph time-travel recovery helper.'
Assert-True ($durableStateTrackedLangGraph.backend_specific.langgraph.implementation_brief.exists -eq $true) 'Durable-state status did not report the frozen implementation brief as present.'
Assert-True (-not [string]::IsNullOrWhiteSpace([string]$durableStateTrackedLangGraph.backend_specific.langgraph.implementation_brief.brief_id)) 'Durable-state status did not expose the persisted brief_id.'
Assert-Equal ([int]$durableStateTrackedLangGraph.backend_specific.langgraph.implementation_brief.source_evidence_ref_count) 2 'Durable-state status did not expose the expected source_evidence_ref_count.'
Assert-True ($durableStateTrackedLangGraph.backend_specific.langgraph.survivor_queue.exists -eq $true) 'Durable-state status did not report the survivor queue as present.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.survivor_queue.queue_kind 'judge_approved_survivor_queue' 'Durable-state status did not expose the stable survivor queue kind.'
Assert-Equal ([int]$durableStateTrackedLangGraph.backend_specific.langgraph.survivor_queue.item_count) 1 'Durable-state status did not expose the expected survivor queue count.'
Assert-True ($durableStateTrackedLangGraph.backend_specific.langgraph.durable_artifacts.implementation_brief_present -eq $true) 'Durable-state status did not expose LangGraph durable artifact presence for the brief.'
Assert-Equal ([int]$durableStateTrackedLangGraph.backend_specific.langgraph.durable_artifacts.survivor_count) 1 'Durable-state status did not expose LangGraph durable artifact survivor count.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.reducer_projection.compatibility 'reducer_aware' 'Durable-state status did not expose reducer-aware compatibility.'
Assert-Equal $durableStateTrackedLangGraph.backend_specific.langgraph.reducer_projection.fanout_state 'complete' 'Durable-state status did not expose the reducer fanout state.'
Assert-Equal ([int]$durableStateTrackedLangGraph.backend_specific.langgraph.reducer_projection.channel_item_counts.branch_findings) 2 'Durable-state status did not expose reducer channel item counts.'
Assert-True ($durableStateTrackedLangGraph.backend_specific.langgraph.reducer_projection.invalid_multi_writer_detected -eq $true) 'Durable-state status did not surface invalid multi-writer reducer updates.'
Assert-ArrayContains -Actual @($durableStateTrackedLangGraph.backend_specific.langgraph.reducer_projection.source_records | ForEach-Object { [string]$_ }) -Expected 'branch:branch-a' -Message 'Durable-state status did not expose reducer source attribution.'

Ensure-Directory -Path (Join-Path $UnmanagedAutoRepoRoot '.omx\state\team\manual-existing')
$durableStateTrackedLangGraphWithNativeResidue = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') -Arguments @(
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $durableStateTrackedLangGraphWithNativeResidue.state_class 'tracked_langgraph_thread' 'Durable-state status changed the primary tracked LangGraph classification unexpectedly when empty unmanaged native residue exists.'
$trackedLangGraphSafeCleanupKinds = @($durableStateTrackedLangGraphWithNativeResidue.cleanup_reconciliation.safe_cleanup_candidates | ForEach-Object { [string]$_.kind })
Assert-ArrayContains -Actual $trackedLangGraphSafeCleanupKinds -Expected 'empty_unmanaged_native_team_directory' -Message 'Durable-state status did not classify empty unmanaged native residue as a safe cleanup candidate.'
Assert-True ($durableStateTrackedLangGraphWithNativeResidue.cleanup_reconciliation.manual_reconciliation_required -eq $false) 'Durable-state status incorrectly required manual reconciliation for empty unmanaged native residue.'
Assert-True ([string]$durableStateTrackedLangGraphWithNativeResidue.next_step -like '*Safe cleanup candidates are also available*') 'Durable-state status did not explain safe cleanup availability in next_step.'

$langGraphLoopRepoRoot = Join-Path $TempRoot 'langgraph-loop-repo'
Ensure-Directory -Path $langGraphLoopRepoRoot

$langGraphLoopRun = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-run.ps1') -Arguments @(
  '-Task', 'execution loop task',
  '-Phase', 'execute-parallel',
  '-LoopKind', 'execution',
  '-IterationBudget', '2',
  '-RepoRoot', $langGraphLoopRepoRoot,
  '-Json'
)
$langGraphLoopThreadId = [string]$langGraphLoopRun.thread_id
Assert-True (-not [string]::IsNullOrWhiteSpace($langGraphLoopThreadId)) 'LangGraph loop run did not return a thread_id.'
Assert-Equal $langGraphLoopRun.loop_projection.active_loop 'execution' 'LangGraph loop run did not seed the execution loop.'
Assert-Equal ([int]$langGraphLoopRun.loop_projection.iteration_budget) 2 'LangGraph loop run did not preserve the requested iteration budget.'

$langGraphLoopStatus = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-status.ps1') -Arguments @(
  '-ThreadId', $langGraphLoopThreadId,
  '-RepoRoot', $langGraphLoopRepoRoot,
  '-Json'
)
Assert-Equal $langGraphLoopStatus.thread.active_loop 'execution' 'LangGraph loop status did not expose the active loop.'
Assert-Equal ([int]$langGraphLoopStatus.thread.iteration_budget) 2 'LangGraph loop status did not expose the iteration budget.'

$langGraphLoopRevise = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-resume.ps1') -Arguments @(
  '-ThreadId', $langGraphLoopThreadId,
  '-LoopKind', 'execution',
  '-GateVerdict', 'revise',
  '-GateReason', 'validation_failed',
  '-RepoRoot', $langGraphLoopRepoRoot,
  '-Json'
)
Assert-Equal ([int]$langGraphLoopRevise.thread.iteration_count) 1 'LangGraph loop revise did not increment iteration_count.'
Assert-Equal $langGraphLoopRevise.thread.last_gate_verdict 'revise' 'LangGraph loop revise did not preserve the gate verdict.'
Assert-Equal ([string]$langGraphLoopRevise.thread.stop_reason) '' 'LangGraph loop revise unexpectedly stopped the loop.'

$langGraphLoopNeedsHuman = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-resume.ps1') -Arguments @(
  '-ThreadId', $langGraphLoopThreadId,
  '-GateVerdict', 'needs_human',
  '-GateReason', 'manual_approval_required',
  '-RepoRoot', $langGraphLoopRepoRoot,
  '-Json'
)
Assert-Equal $langGraphLoopNeedsHuman.thread.status 'waiting_for_approval' 'LangGraph loop did not enter waiting_for_approval on needs_human.'
Assert-Equal $langGraphLoopNeedsHuman.interrupt.status 'waiting_for_approval' 'LangGraph loop did not persist interrupt status for needs_human.'

$langGraphLoopInspect = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-inspect.ps1') -Arguments @(
  '-ThreadId', $langGraphLoopThreadId,
  '-RepoRoot', $langGraphLoopRepoRoot,
  '-Json'
)
Assert-Equal $langGraphLoopInspect.loop_projection.active_loop 'execution' 'LangGraph inspect did not expose loop projection for the active loop.'
Assert-ArrayContains -Actual @($langGraphLoopInspect.contract.loop_projection_fields | ForEach-Object { [string]$_ }) -Expected 'active_loop' -Message 'LangGraph inspect contract did not expose loop projection fields.'
Assert-ArrayContains -Actual @($langGraphLoopInspect.contract.gate_verdicts | ForEach-Object { [string]$_ }) -Expected 'needs_human' -Message 'LangGraph inspect contract did not expose the gate verdict contract.'
Assert-Equal $langGraphLoopInspect.generalized_live_routing_projection.current_route 'approval_wait' 'LangGraph inspect did not expose generalized approval routing for the active loop.'
Assert-True ($langGraphLoopInspect.generalized_live_routing_projection.approval_route_pending -eq $true) 'LangGraph inspect did not expose pending generalized approval routing posture.'

$langGraphBudgetRun = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-run.ps1') -Arguments @(
  '-Task', 'budget exhaustion task',
  '-Phase', 'execute-parallel',
  '-LoopKind', 'execution',
  '-IterationBudget', '1',
  '-RepoRoot', $langGraphLoopRepoRoot,
  '-Json'
)
$langGraphBudgetThreadId = [string]$langGraphBudgetRun.thread_id

$langGraphBudgetExhaust = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-resume.ps1') -Arguments @(
  '-ThreadId', $langGraphBudgetThreadId,
  '-LoopKind', 'execution',
  '-GateVerdict', 'revise',
  '-GateReason', 'retry_budget_hit',
  '-RepoRoot', $langGraphLoopRepoRoot,
  '-Json'
)
Assert-Equal $langGraphBudgetExhaust.thread.stop_reason 'iteration_budget_exhausted' 'LangGraph loop did not stop explicitly when the iteration budget was exhausted.'
Assert-Equal $langGraphBudgetExhaust.thread.status 'halted' 'LangGraph loop did not halt on iteration budget exhaustion.'
$langGraphRecoverLoop = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-recover.ps1') -Arguments @(
  '-ThreadId', $langGraphBudgetThreadId,
  '-MutationIntent', 'explicit-recovery',
  '-ThreadField', 'phase=stabilize,iteration_budget=4',
  '-ClearInterrupt',
  '-RepoRoot', $langGraphLoopRepoRoot,
  '-Json'
)
Assert-Equal $langGraphRecoverLoop.recovery_projection.posture 'recovered_pending_resume' 'LangGraph recover wrapper did not expose recovered_pending_resume posture.'
Assert-Equal $langGraphRecoverLoop.thread.phase 'stabilize' 'LangGraph recover wrapper did not update the requested phase.'

$durableStateLoopLangGraph = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') -Arguments @(
  '-RepoRoot', $langGraphLoopRepoRoot,
  '-Json'
)
Assert-Equal $durableStateLoopLangGraph.state_class 'preserved_legacy_langgraph_artifact' 'Durable-state status did not classify the loop repo as preserved legacy LangGraph state after terminal or recovery-preserved posture.'
Assert-Equal $durableStateLoopLangGraph.backend_specific.langgraph.loop_projection.active_loop 'execution' 'Durable-state status did not project LangGraph loop metadata.'
Assert-Equal ([int]$durableStateLoopLangGraph.backend_specific.langgraph.loop_projection.iteration_count) 1 'Durable-state status did not project LangGraph iteration_count.'
Assert-Equal $durableStateLoopLangGraph.backend_specific.langgraph.loop_projection.stop_reason 'iteration_budget_exhausted' 'Durable-state status did not project LangGraph stop_reason.'
Assert-Equal $durableStateLoopLangGraph.backend_specific.langgraph.recovery_projection.posture 'recovered_pending_resume' 'Durable-state status did not project LangGraph recovery posture.'

$langGraphCommandRepoRoot = Join-Path $TempRoot 'langgraph-command-repo'
Ensure-Directory -Path $langGraphCommandRepoRoot
$langGraphCommandRun = & $ResolvedPythonPath $langGraphCliPath 'run' '--task' 'command-driven task' '--phase' 'freeze-plan' '--repo-root' $langGraphCommandRepoRoot
$langGraphCommandRunExitCode = $LASTEXITCODE
Assert-Equal $langGraphCommandRunExitCode 0 'Generated LangGraph CLI did not start a command-driven test thread successfully.'
$langGraphCommandRunJson = $langGraphCommandRun | ConvertFrom-Json
$langGraphCommandThreadId = [string]$langGraphCommandRunJson.thread_id
Assert-True (-not [string]::IsNullOrWhiteSpace($langGraphCommandThreadId)) 'Generated LangGraph CLI did not return a command-driven thread_id.'

$langGraphCommandUpdatePath = Join-Path $langGraphCommandRepoRoot 'command-update.json'
Set-Content -LiteralPath $langGraphCommandUpdatePath -Encoding UTF8 -NoNewline -Value (@{ ownership_boundaries = @('src/worker.py') } | ConvertTo-Json -Compress)
$langGraphCommandLocalResume = & $ResolvedPythonPath $langGraphCliPath 'resume' '--thread-id' $langGraphCommandThreadId '--repo-root' $langGraphCommandRepoRoot '--phase' 'execute-parallel' '--command-kind' 'update_goto' '--command-goto' 'execute-parallel' '--command-graph-scope' 'current' '--command-update-file' $langGraphCommandUpdatePath
$langGraphCommandLocalResumeExitCode = $LASTEXITCODE
Assert-Equal $langGraphCommandLocalResumeExitCode 0 'Generated LangGraph CLI did not persist command-driven local transition metadata.'
$langGraphCommandLocalResumeJson = $langGraphCommandLocalResume | ConvertFrom-Json
Assert-Equal $langGraphCommandLocalResumeJson.command_projection.transition_kind 'update_goto' 'Generated LangGraph CLI did not expose command-driven local transition kind.'
Assert-Equal $langGraphCommandLocalResumeJson.command_projection.source_subgraph 'planning' 'Generated LangGraph CLI did not expose the command-driven source subgraph.'
Assert-Equal $langGraphCommandLocalResumeJson.command_projection.target_subgraph 'execution' 'Generated LangGraph CLI did not expose the command-driven target subgraph.'

$langGraphCommandAwaitingResume = & $ResolvedPythonPath $langGraphCliPath 'resume' '--thread-id' $langGraphCommandThreadId '--repo-root' $langGraphCommandRepoRoot '--phase' 'verify-accept' '--command-kind' 'parent_handoff' '--command-graph-scope' 'parent' '--parent-handoff-target' 'verify-accept' '--await-command-resume'
$langGraphCommandAwaitingResumeExitCode = $LASTEXITCODE
Assert-Equal $langGraphCommandAwaitingResumeExitCode 0 'Generated LangGraph CLI did not persist parent-handoff resume posture.'
$langGraphCommandAwaitingResumeJson = $langGraphCommandAwaitingResume | ConvertFrom-Json
Assert-Equal $langGraphCommandAwaitingResumeJson.command_projection.resume_posture 'awaiting_command_resume' 'Generated LangGraph CLI did not expose awaiting_command_resume posture.'
Assert-Equal $langGraphCommandAwaitingResumeJson.command_projection.graph_scope 'parent' 'Generated LangGraph CLI did not expose parent graph scope.'

$langGraphCommandResumePayloadPath = Join-Path $langGraphCommandRepoRoot 'resume-payload.json'
Set-Content -LiteralPath $langGraphCommandResumePayloadPath -Encoding UTF8 -NoNewline -Value (@{ approved = $true; route = 'verify' } | ConvertTo-Json -Compress)
$langGraphCommandResumeWithPayload = & $ResolvedPythonPath $langGraphCliPath 'resume' '--thread-id' $langGraphCommandThreadId '--repo-root' $langGraphCommandRepoRoot '--phase' 'verify-accept' '--command-kind' 'resume_parent_handoff' '--command-graph-scope' 'parent' '--parent-handoff-target' 'verify-accept' '--resume-payload-file' $langGraphCommandResumePayloadPath
$langGraphCommandResumeWithPayloadExitCode = $LASTEXITCODE
Assert-Equal $langGraphCommandResumeWithPayloadExitCode 0 'Generated LangGraph CLI did not persist command-driven resume payload posture.'
$langGraphCommandResumeWithPayloadJson = $langGraphCommandResumeWithPayload | ConvertFrom-Json
Assert-Equal $langGraphCommandResumeWithPayloadJson.command_projection.resume_posture 'resumed_with_payload' 'Generated LangGraph CLI did not expose resumed_with_payload posture.'
Assert-True ($langGraphCommandResumeWithPayloadJson.command_projection.resume_payload_present -eq $true) 'Generated LangGraph CLI did not expose resume payload presence.'
$langGraphDirectCommandEngine = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-langgraph-command-engine.ps1') -Arguments @(
  '-ThreadId', $langGraphCommandThreadId,
  '-RunKind', 'invoke',
  '-RecursionLimit', '8',
  '-RepoRoot', $langGraphCommandRepoRoot,
  '-Json'
)
Assert-Equal $langGraphDirectCommandEngine.command_aware_live_primary_engine_projection.transition_kind 'resume_parent_handoff' 'LangGraph command-engine wrapper did not expose the command transition kind.'
Assert-Equal $langGraphDirectCommandEngine.command_aware_live_primary_engine_projection.control_state_kind 'parent_handoff_control' 'LangGraph command-engine wrapper did not expose the command control state kind.'
Assert-Equal $langGraphDirectCommandEngine.command_aware_live_primary_engine_projection.graph_scope 'parent' 'LangGraph command-engine wrapper did not expose the command graph scope.'
Assert-Equal $langGraphDirectCommandEngine.command_aware_live_primary_engine_projection.parent_handoff_target 'verify-accept' 'LangGraph command-engine wrapper did not expose the parent handoff target.'
Assert-Equal $langGraphDirectCommandEngine.command_aware_live_primary_engine_projection.resume_posture 'resumed_with_payload' 'LangGraph command-engine wrapper did not expose the command resume posture.'
Assert-True ($langGraphDirectCommandEngine.command_aware_live_primary_engine_projection.resume_payload_present -eq $true) 'LangGraph command-engine wrapper did not expose resume payload presence.'
Assert-ArrayContains -Actual @($langGraphDirectCommandEngine.command_aware_live_primary_engine_projection.resume_payload_keys | ForEach-Object { [string]$_ }) -Expected 'approved' -Message 'LangGraph command-engine wrapper did not expose resume payload keys.'

$durableStateCommandLangGraph = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') -Arguments @(
  '-RepoRoot', $langGraphCommandRepoRoot,
  '-Json'
)
Assert-Equal $durableStateCommandLangGraph.backend_specific.langgraph.command_projection.transition_kind 'resume_parent_handoff' 'Durable-state status did not expose command-driven transition kind.'
Assert-Equal $durableStateCommandLangGraph.backend_specific.langgraph.command_projection.graph_scope 'parent' 'Durable-state status did not expose command-driven graph scope.'
Assert-Equal $durableStateCommandLangGraph.backend_specific.langgraph.command_projection.source_subgraph 'execution' 'Durable-state status did not expose command-driven source subgraph.'
Assert-Equal $durableStateCommandLangGraph.backend_specific.langgraph.command_projection.target_subgraph 'verification' 'Durable-state status did not expose command-driven target subgraph.'
Assert-Equal $durableStateCommandLangGraph.backend_specific.langgraph.command_projection.parent_handoff_target 'verify-accept' 'Durable-state status did not expose parent handoff target.'
Assert-Equal $durableStateCommandLangGraph.backend_specific.langgraph.command_projection.resume_posture 'resumed_with_payload' 'Durable-state status did not expose command-driven resume posture.'
Assert-Equal $durableStateCommandLangGraph.backend_specific.langgraph.command_projection.helper_pointer.script 'omx-langgraph-inspect.ps1' 'Durable-state status did not expose the command-aware inspection helper pointer.'
Assert-ArrayContains -Actual @($durableStateCommandLangGraph.backend_specific.langgraph.command_projection.resume_payload_keys | ForEach-Object { [string]$_ }) -Expected 'approved' -Message 'Durable-state status did not expose command-driven resume payload keys.'
Assert-Equal $durableStateCommandLangGraph.backend_specific.langgraph.command_aware_live_primary_engine_projection.transition_kind 'resume_parent_handoff' 'Durable-state status did not expose command-engine transition kind.'
Assert-Equal $durableStateCommandLangGraph.backend_specific.langgraph.command_aware_live_primary_engine_projection.control_state_kind 'parent_handoff_control' 'Durable-state status did not expose command-engine control state kind.'
Assert-Equal $durableStateCommandLangGraph.backend_specific.langgraph.command_aware_live_primary_engine_projection.graph_scope 'parent' 'Durable-state status did not expose command-engine graph scope.'
Assert-Equal $durableStateCommandLangGraph.backend_specific.langgraph.command_aware_live_primary_engine_projection.parent_handoff_target 'verify-accept' 'Durable-state status did not expose command-engine parent handoff target.'
Assert-Equal $durableStateCommandLangGraph.backend_specific.langgraph.command_aware_live_primary_engine_projection.resume_posture 'resumed_with_payload' 'Durable-state status did not expose command-engine resume posture.'
Assert-Equal $durableStateCommandLangGraph.backend_specific.langgraph.command_aware_live_primary_engine_projection.helper_pointer.script 'omx-langgraph-command-engine.ps1' 'Durable-state status did not expose the LangGraph command-engine helper pointer.'
Assert-ArrayContains -Actual @($durableStateCommandLangGraph.backend_specific.langgraph.command_aware_live_primary_engine_projection.resume_payload_keys | ForEach-Object { [string]$_ }) -Expected 'approved' -Message 'Durable-state status did not expose command-engine resume payload keys.'

Get-ChildItem -LiteralPath (Join-Path $FakeRepoRoot '.omx\state\team') -Recurse -Force -File -ErrorAction SilentlyContinue |
  Remove-Item -Force
$durableStateUnmanaged = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-status.ps1') -Arguments @(
  '-RepoRoot', $FakeRepoRoot,
  '-Json'
)
Assert-Equal $durableStateUnmanaged.state_class 'no_durable_state' 'Durable-state status did not treat empty unmanaged native directories as non-blocking cleanup context.'
$durableStateUnmanagedCleanupKinds = @($durableStateUnmanaged.cleanup_reconciliation.safe_cleanup_candidates | ForEach-Object { [string]$_.kind })
Assert-ArrayContains -Actual $durableStateUnmanagedCleanupKinds -Expected 'empty_unmanaged_native_team_directory' -Message 'Durable-state status did not retain empty unmanaged native directories as safe cleanup candidates.'
Assert-True ($durableStateUnmanaged.cleanup_reconciliation.manual_reconciliation_required -eq $false) 'Durable-state status incorrectly required manual reconciliation for empty unmanaged native directories.'

Ensure-Directory -Path (Join-Path $CleanupRepoRoot '.omx\state\team\empty-native-team')
$staleTrackedRecordPath = Join-Path $CleanupRepoRoot '.omx\state\team\codex-auto-managed-team.json'
Set-Content -LiteralPath $staleTrackedRecordPath -Encoding ASCII -NoNewline -Value @'
{
  "schema_version": 1,
  "managed_by": "test",
  "team_name": "missing-team",
  "worker_role": "team-executor",
  "worker_count": 2,
  "phase": "execute-parallel",
  "updated_at": "2026-04-16T00:00:00Z"
}
'@

$cleanupPreview = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-reconcile.ps1') -Arguments @(
  '-RepoRoot', $CleanupRepoRoot,
  '-Json'
)
Assert-True ($cleanupPreview.safe_cleanup_available -eq $true) 'Durable-state reconcile preview did not expose safe cleanup candidates.'
Assert-True ($cleanupPreview.manual_reconciliation_required -eq $false) 'Durable-state reconcile preview incorrectly required manual reconciliation for safe residue.'
$cleanupSafeKinds = @($cleanupPreview.safe_cleanup_candidates | ForEach-Object { [string]$_.kind })
Assert-ArrayContains -Actual $cleanupSafeKinds -Expected 'stale_tracked_record' -Message 'Durable-state reconcile preview did not expose stale tracked records as safe cleanup candidates.'
Assert-ArrayContains -Actual $cleanupSafeKinds -Expected 'empty_unmanaged_native_team_directory' -Message 'Durable-state reconcile preview did not expose empty unmanaged native team directories as safe cleanup candidates.'

$cleanupApply = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-durable-state-reconcile.ps1') -Arguments @(
  '-RepoRoot', $CleanupRepoRoot,
  '-Apply',
  '-Json'
)
Assert-Equal (@($cleanupApply.applied_actions).Count) 2 'Durable-state reconcile apply did not remove the expected safe cleanup candidates.'
Assert-True (-not (Test-Path -LiteralPath $staleTrackedRecordPath)) 'Durable-state reconcile apply did not remove the stale tracked record.'
Assert-True (-not (Test-Path -LiteralPath (Join-Path $CleanupRepoRoot '.omx\state\team\empty-native-team'))) 'Durable-state reconcile apply did not remove the empty unmanaged native team directory.'

$unmanagedAutoPlan = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\omx-team-auto.ps1') -Arguments @(
  '-Task', 'parallel feature work',
  '-Phase', 'execute-parallel',
  '-ParallelSlices', '2',
  '-RepoRoot', $UnmanagedAutoRepoRoot,
  '-Json'
)
Assert-Equal $unmanagedAutoPlan.decision 'resume' 'LangGraph backend planning should ignore unmanaged native team directories while honoring the active scoped LangGraph backend record.'
Assert-Equal $unmanagedAutoPlan.langgraph_record.thread_id $langGraphDirectThreadId 'LangGraph backend planning did not preserve the tracked direct-run thread.'

$manualRouting = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-subagents-manual.ps1') -Arguments @(
  '-Json'
)
Assert-Equal $manualRouting.oh_my_codex 'on' 'codex-subagents-manual.ps1 changed oh_my_codex unexpectedly.'
Assert-Equal $manualRouting.subagent_routing 'manual' 'codex-subagents-manual.ps1 did not set manual routing.'
Assert-Equal $manualRouting.effective_mode 'enhanced_manual' 'Manual routing effective mode is wrong.'

$wrappedManual = Invoke-PowerShellCommandJson -CommandText ("& { & " + (Quote-PowerShellLiteral -Value $ProfilePath) + "; codex 'manual-task' }")
$wrappedManualArgs = @($wrappedManual.args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $wrappedManualArgs -Expected 'manual-task' -Message 'Wrapped manual launch did not forward the user argument.'
Assert-True ('--disable' -notin $wrappedManualArgs) 'Manual routing should keep multi_agent available.'
$wrappedManualPathSegments = @(([string]$wrappedManual.path).Split(';') | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
Assert-True ($wrappedManualPathSegments.Count -gt 0) 'Wrapped manual launch did not expose the child PATH.'
Assert-Equal ([System.IO.Path]::GetFullPath($wrappedManualPathSegments[0])) (Join-Path $CodexHome 'bin\win-shims') 'Wrapped manual launch did not prepend win-shims to child PATH.'
Assert-Equal ([System.IO.Path]::GetFullPath([string]$wrappedManual.cleanup_shim_directory)) (Join-Path $CodexHome 'bin\win-shims') 'Wrapped manual launch did not expose the cleanup shim directory bridge to child login shells.'
Assert-Equal $manifest.startup_binding.cleanup_output_control.login_profile_env_bridge 'CODEX_USER_LEVEL_CLEANUP_SHIM_DIRECTORY' 'Installer did not report the cleanup shim login-profile environment bridge.'
if ($manifest.startup_binding.cleanup_output_control.taskkill_exe_shim_enabled -eq $true) {
  Assert-True (([string]$wrappedManual.pathext).StartsWith('.EXE', [System.StringComparison]::OrdinalIgnoreCase)) 'Wrapped manual launch did not prioritize taskkill.exe cleanup-output shimming when the EXE shim is installed.'
} else {
  Assert-True (([string]$wrappedManual.pathext).StartsWith('.CMD', [System.StringComparison]::OrdinalIgnoreCase)) 'Wrapped manual launch did not prioritize .CMD in PATHEXT when taskkill.exe shim is unavailable.'
}
$manualModelInstructionsArg = @($wrappedManualArgs | Where-Object { $_ -like 'model_instructions_file=*' } | Select-Object -First 1)[0]
$manualModelInstructionsPath = $manualModelInstructionsArg.Substring('model_instructions_file='.Length).Trim('"').Replace('\\', '\')
$manualModelInstructionsContent = Get-Content -LiteralPath $manualModelInstructionsPath -Raw
Assert-True ($manualModelInstructionsContent.Contains('manual expert routing')) 'Wrapped manual launch did not describe manual routing mode.'
Assert-True ($manualModelInstructionsContent.Contains('Do not proactively route unless the user explicitly asks')) 'Wrapped manual launch did not preserve the manual-routing restriction.'

$rawManual = Invoke-PowerShellCommandJson -CommandText ("& { & " + (Quote-PowerShellLiteral -Value $ExplicitNativeBypassPs1Path) + " 'raw-task' }")
$rawManualArgs = @($rawManual.args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $rawManualArgs -Expected 'raw-task' -Message 'Native bypass launch did not forward the user argument.'
$rawManualPathSegments = @(([string]$rawManual.path).Split(';') | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
if ($rawManualPathSegments.Count -gt 0) {
  Assert-True ([System.IO.Path]::GetFullPath($rawManualPathSegments[0]) -ne (Join-Path $CodexHome 'bin\win-shims')) 'Native bypass launch unexpectedly prepended win-shims to child PATH.'
}

$ExeShimHome = Join-Path $TempRoot 'exe-shim-home'
$ExeShimProfilePath = Join-Path $TempRoot 'exe-shim-profile\Microsoft.PowerShell_profile.ps1'
Ensure-Directory -Path (Split-Path -Parent $ExeShimProfilePath)
$exeShimInstallArgs = @(
  '-CodexHome', $ExeShimHome,
  '-PowerShellProfilePath', $ExeShimProfilePath,
  '-NativeCodexCommandPath', $FakeNativeCodexPath,
  '-OmxCommandPath', $FakeOmxPath,
  '-PythonCommandPath', $ResolvedPythonPath,
  '-InstallTaskkillExeShim'
)
$exeShimInstall = Invoke-PowerShellScriptJson -FilePath $InstallerPath -Arguments $exeShimInstallArgs
Assert-True ($exeShimInstall.startup_binding.cleanup_output_control.taskkill_exe_shim_enabled -eq $true) 'Explicit EXE shim install did not report taskkill_exe_shim_enabled=true.'
Assert-True ($exeShimInstall.startup_binding.cleanup_output_control.taskkill_exe_shim_compile.attempted -eq $true) 'Explicit EXE shim install did not attempt compilation.'
Assert-True (Test-Path -LiteralPath (Join-Path $ExeShimHome 'bin\win-shims\taskkill.exe')) 'Explicit EXE shim install did not create taskkill.exe.'
$exeShimWrapped = Invoke-PowerShellCommandJson -CommandText ("& { & " + (Quote-PowerShellLiteral -Value (Join-Path $ExeShimHome 'bin\_codex-user-level-team-mode-launcher.ps1')) + " 'exe-shim-task' }")
Assert-True (([string]$exeShimWrapped.pathext).StartsWith('.EXE', [System.StringComparison]::OrdinalIgnoreCase)) 'Explicit EXE shim launch did not prioritize .EXE in PATHEXT.'

$SkipExeShimHome = Join-Path $TempRoot 'skip-exe-shim-home'
$SkipExeShimProfilePath = Join-Path $TempRoot 'skip-exe-shim-profile\Microsoft.PowerShell_profile.ps1'
Ensure-Directory -Path (Split-Path -Parent $SkipExeShimProfilePath)
$skipExeShimInstall = Invoke-PowerShellScriptJson -FilePath $InstallerPath -Arguments @(
  '-CodexHome', $SkipExeShimHome,
  '-PowerShellProfilePath', $SkipExeShimProfilePath,
  '-NativeCodexCommandPath', $FakeNativeCodexPath,
  '-OmxCommandPath', $FakeOmxPath,
  '-PythonCommandPath', $ResolvedPythonPath,
  '-SkipTaskkillExeShim'
)
Assert-True ($skipExeShimInstall.startup_binding.cleanup_output_control.taskkill_exe_shim_requested -eq $false) 'SkipTaskkillExeShim did not report taskkill_exe_shim_requested=false.'
Assert-True ($skipExeShimInstall.startup_binding.cleanup_output_control.taskkill_exe_shim_enabled -eq $false) 'SkipTaskkillExeShim still reported taskkill_exe_shim_enabled=true.'
Assert-True (-not (Test-Path -LiteralPath (Join-Path $SkipExeShimHome 'bin\win-shims\taskkill.exe'))) 'SkipTaskkillExeShim unexpectedly created taskkill.exe.'
$skipExeShimWrapped = Invoke-PowerShellCommandJson -CommandText ("& { & " + (Quote-PowerShellLiteral -Value (Join-Path $SkipExeShimHome 'bin\_codex-user-level-team-mode-launcher.ps1')) + " 'skip-exe-shim-task' }")
Assert-True (([string]$skipExeShimWrapped.pathext).StartsWith('.CMD', [System.StringComparison]::OrdinalIgnoreCase)) 'SkipTaskkillExeShim launch did not fall back to .CMD cleanup-output shimming.'

$omxOff = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-omx-off.ps1') -Arguments @(
  '-Json'
)
Assert-Equal $omxOff.oh_my_codex 'off' 'codex-omx-off.ps1 did not disable oh_my_codex.'
Assert-Equal $omxOff.subagent_routing 'manual' 'codex-omx-off.ps1 changed routing unexpectedly.'
Assert-Equal $omxOff.effective_mode 'native_manual' 'codex-omx-off.ps1 produced the wrong effective mode.'

$routingOff = Invoke-PowerShellScriptJson -FilePath (Join-Path $CodexHome 'bin\codex-subagents-off.ps1') -Arguments @(
  '-Json'
)
Assert-Equal $routingOff.oh_my_codex 'off' 'codex-subagents-off.ps1 changed oh_my_codex unexpectedly.'
Assert-Equal $routingOff.subagent_routing 'off' 'codex-subagents-off.ps1 did not disable routing.'
Assert-Equal $routingOff.effective_mode 'pure_debugging' 'Pure debugging mode was not reported.'
Assert-True ($routingOff.pure_debugging_mode -eq $true) 'Pure debugging mode flag was not set.'
Assert-True ($routingOff.role_orchestration_available -eq $false) 'Role orchestration should be unavailable in pure debugging mode.'

$wrappedPureDebugging = Invoke-PowerShellCommandJson -CommandText ("& { & " + (Quote-PowerShellLiteral -Value $ProfilePath) + "; codex 'debug-task' }")
$wrappedPureDebuggingArgs = @($wrappedPureDebugging.args | ForEach-Object { [string]$_ })
Assert-ArrayContains -Actual $wrappedPureDebuggingArgs -Expected '--disable' -Message 'Pure debugging launch did not disable multi_agent.'
Assert-ArrayContains -Actual $wrappedPureDebuggingArgs -Expected 'multi_agent' -Message 'Pure debugging launch did not target multi_agent.'
Assert-ArrayContains -Actual $wrappedPureDebuggingArgs -Expected 'debug-task' -Message 'Pure debugging launch did not forward the user argument.'
$pureDebuggingModelInstructionsArg = @($wrappedPureDebuggingArgs | Where-Object { $_ -like 'model_instructions_file=*' } | Select-Object -First 1)[0]
$pureDebuggingModelInstructionsPath = $pureDebuggingModelInstructionsArg.Substring('model_instructions_file='.Length).Trim('"').Replace('\\', '\')
$pureDebuggingModelInstructionsContent = Get-Content -LiteralPath $pureDebuggingModelInstructionsPath -Raw
Assert-True ($pureDebuggingModelInstructionsContent.Contains('plain single-agent Codex session')) 'Pure debugging launch did not describe the single-agent fallback.'

$stateFile = Get-Content -LiteralPath (Join-Path $CodexHome 'state\user-level-team-mode.json') -Raw | ConvertFrom-Json
Assert-Equal $stateFile.oh_my_codex 'off' 'Persisted state ended with wrong oh_my_codex value.'
Assert-Equal $stateFile.subagent_routing 'off' 'Persisted state ended with wrong subagent_routing value.'
Assert-Equal $stateFile.completed_subagent_retention 'close' 'Persisted state ended with wrong completed_subagent_retention value.'

$customManagedLeaderContent = @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "team-leader"
description = "custom prior version for rollback test"
'@
Set-Content -LiteralPath (Join-Path $CodexHome 'agents\team-leader.toml') -Encoding ASCII -NoNewline -Value $customManagedLeaderContent
$customManagedVerifierContent = @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "verifier"
description = "custom prior version for rollback test"
'@
Set-Content -LiteralPath (Join-Path $CodexHome 'agents\verifier.toml') -Encoding ASCII -NoNewline -Value $customManagedVerifierContent
$customManagedDebuggerContent = @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "debugger"
description = "custom prior version for rollback test"
'@
Set-Content -LiteralPath (Join-Path $CodexHome 'agents\debugger.toml') -Encoding ASCII -NoNewline -Value $customManagedDebuggerContent
$customManagedResearcherContent = @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "researcher"
description = "custom prior version for rollback test"
'@
Set-Content -LiteralPath (Join-Path $CodexHome 'agents\researcher.toml') -Encoding ASCII -NoNewline -Value $customManagedResearcherContent
$customManagedDependencyExpertContent = @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "dependency-expert"
description = "custom prior version for rollback test"
'@
Set-Content -LiteralPath (Join-Path $CodexHome 'agents\dependency-expert.toml') -Encoding ASCII -NoNewline -Value $customManagedDependencyExpertContent
$customManagedWriterContent = @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "writer"
description = "custom prior version for rollback test"
'@
Set-Content -LiteralPath (Join-Path $CodexHome 'agents\writer.toml') -Encoding ASCII -NoNewline -Value $customManagedWriterContent
$customManagedBugFinderContent = @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "bug-finder"
description = "custom prior version for rollback test"
'@
Set-Content -LiteralPath (Join-Path $CodexHome 'agents\bug-finder.toml') -Encoding ASCII -NoNewline -Value $customManagedBugFinderContent

$rollbackExistingInstallExitCode = Invoke-PowerShellScriptExpectFailure -FilePath $InstallerPath -Arguments @(
  '-CodexHome', $CodexHome,
  '-PowerShellProfilePath', $ProfilePath,
  '-NativeCodexCommandPath', $FakeNativeCodexPath,
  '-OmxCommandPath', $FakeOmxPath,
  '-PythonCommandPath', $ResolvedPythonPath,
  '-TestFailPoint', 'after_assets'
)
Assert-True ($rollbackExistingInstallExitCode -ne 0) 'Installer should fail when the rollback test fail point is injected.'
Assert-Equal ((Get-Content -LiteralPath (Join-Path $CodexHome 'agents\team-leader.toml') -Raw).Trim()) $customManagedLeaderContent.Trim() 'Rollback did not restore the previous managed leader profile.'
Assert-Equal ((Get-Content -LiteralPath (Join-Path $CodexHome 'agents\verifier.toml') -Raw).Trim()) $customManagedVerifierContent.Trim() 'Rollback did not restore the previous managed verifier profile.'
Assert-Equal ((Get-Content -LiteralPath (Join-Path $CodexHome 'agents\debugger.toml') -Raw).Trim()) $customManagedDebuggerContent.Trim() 'Rollback did not restore the previous managed debugger profile.'
Assert-Equal ((Get-Content -LiteralPath (Join-Path $CodexHome 'agents\researcher.toml') -Raw).Trim()) $customManagedResearcherContent.Trim() 'Rollback did not restore the previous managed researcher profile.'
Assert-Equal ((Get-Content -LiteralPath (Join-Path $CodexHome 'agents\dependency-expert.toml') -Raw).Trim()) $customManagedDependencyExpertContent.Trim() 'Rollback did not restore the previous managed dependency-expert profile.'
Assert-Equal ((Get-Content -LiteralPath (Join-Path $CodexHome 'agents\writer.toml') -Raw).Trim()) $customManagedWriterContent.Trim() 'Rollback did not restore the previous managed writer profile.'
Assert-Equal ((Get-Content -LiteralPath (Join-Path $CodexHome 'agents\bug-finder.toml') -Raw).Trim()) $customManagedBugFinderContent.Trim() 'Rollback did not restore the previous managed bug-finder profile.'
Assert-Equal ((Get-Content -LiteralPath $nativeCodexCmdPath -Raw).Trim()) '@ECHO OFF' 'Rollback path modified native codex.cmd.'
Assert-Equal ((Get-Content -LiteralPath $nativeCodexPs1Path -Raw).Trim()) '$host.Name' 'Rollback path modified native codex.ps1.'

$rollbackFreshInstallExitCode = Invoke-PowerShellScriptExpectFailure -FilePath $InstallerPath -Arguments @(
  '-CodexHome', $RollbackHome,
  '-PowerShellProfilePath', $RollbackProfilePath,
  '-NativeCodexCommandPath', $FakeNativeCodexPath,
  '-OmxCommandPath', $FakeOmxPath,
  '-PythonCommandPath', $ResolvedPythonPath,
  '-TestFailPoint', 'after_state'
)
Assert-True ($rollbackFreshInstallExitCode -ne 0) 'Installer should fail when the fresh-install rollback fail point is injected.'

$rollbackManagedFiles = @(
  (Join-Path $RollbackHome 'agents\team-leader.toml')
  (Join-Path $RollbackHome 'agents\verifier.toml')
  (Join-Path $RollbackHome 'agents\debugger.toml')
  (Join-Path $RollbackHome 'agents\researcher.toml')
  (Join-Path $RollbackHome 'agents\dependency-expert.toml')
  (Join-Path $RollbackHome 'agents\writer.toml')
  (Join-Path $RollbackHome 'agents\bug-finder.toml')
  (Join-Path $RollbackHome 'agents\bug-rebutter.toml')
  (Join-Path $RollbackHome 'agents\bug-judge.toml')
  (Join-Path $RollbackHome 'bin\_codex-user-level-team-mode.ps1')
  (Join-Path $RollbackHome 'bin\_codex-user-level-team-mode-launcher.ps1')
  (Join-Path $RollbackHome 'bin\codex-omx-on.ps1')
  (Join-Path $RollbackHome 'bin\codex-omx-off.ps1')
  (Join-Path $RollbackHome 'bin\codex-omx-status.ps1')
  (Join-Path $RollbackHome 'bin\codex-subagents-auto.ps1')
  (Join-Path $RollbackHome 'bin\codex-subagents-manual.ps1')
  (Join-Path $RollbackHome 'bin\codex-subagents-off.ps1')
  (Join-Path $RollbackHome 'bin\codex-langgraph-on.ps1')
  (Join-Path $RollbackHome 'bin\codex-langgraph-off.ps1')
  (Join-Path $RollbackHome 'bin\codex-langgraph-status.ps1')
  (Join-Path $RollbackHome 'bin\codex-routing-status.ps1')
  (Join-Path $RollbackHome 'bin\codex-durable-backend-native-omx.ps1')
  (Join-Path $RollbackHome 'bin\codex-durable-backend-langgraph.ps1')
  (Join-Path $RollbackHome 'bin\codex-durable-backend-status.ps1')
  (Join-Path $RollbackHome 'bin\codex-durable-state-status.ps1')
  (Join-Path $RollbackHome 'bin\codex-durable-state-reconcile.ps1')
  (Join-Path $RollbackHome 'bin\omx-team-compose.ps1')
  (Join-Path $RollbackHome 'bin\codex-routing-policy.ps1')
  (Join-Path $RollbackHome 'bin\codex-subagent-limits.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-install.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-cli.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-run.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-status.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-resume.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-inspect.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-fuller-engine.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-deeper-engine.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-superstep-engine.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-stateful-engine.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-boundary-engine.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-handoff-engine.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-approval-engine.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-provenance-engine.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-artifact-engine.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-reducer-engine.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-command-engine.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-runtime-engine.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-memory-engine.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-migration-engine.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-auto-policy.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-subgraph-state.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-memory.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-runtime.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-stream.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-subgraphs.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-history.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-replay.ps1')
  (Join-Path $RollbackHome 'bin\omx-langgraph-recover.ps1')
  (Join-Path $RollbackHome 'bin\omx-team-dev.ps1')
  (Join-Path $RollbackHome 'bin\omx-team-debug.ps1')
  (Join-Path $RollbackHome 'bin\omx-team-auto.ps1')
  (Join-Path $RollbackHome 'bin\omx-team-ops.ps1')
  (Join-Path $RollbackHome 'bin\omx-team-hybrid.ps1')
  (Join-Path $RollbackHome 'bin\omx-team-verify.ps1')
  (Join-Path $RollbackHome 'docs\team-mode-playbook.md')
  (Join-Path $RollbackHome 'docs\team-mode-quick-reference.md')
  (Join-Path $RollbackHome 'teams\compose-manifest.schema.json')
  (Join-Path $RollbackHome 'python\langgraph_durable_orchestrator\__init__.py')
  (Join-Path $RollbackHome 'python\langgraph_durable_orchestrator\contracts.py')
  (Join-Path $RollbackHome 'python\langgraph_durable_orchestrator\runtime.py')
  (Join-Path $RollbackHome 'python\langgraph_durable_orchestrator\cli.py')
  (Join-Path $RollbackHome 'state\native-subagent-limits.json')
  (Join-Path $RollbackHome 'state\user-level-team-mode.json')
)

foreach ($path in $rollbackManagedFiles) {
  Assert-True (-not (Test-Path -LiteralPath $path)) "Rollback did not remove the newly created managed file: $path"
}

$rollbackBackupManifest = Get-ChildItem -Path (Join-Path $RollbackHome 'backups\codex-user-level-team-mode') -Recurse -Filter manifest.json -ErrorAction SilentlyContinue | Select-Object -First 1
Assert-True ($null -ne $rollbackBackupManifest) 'Failed install did not leave a backup manifest for diagnostics.'

$existingRollbackProfileContent = "# existing profile content"
Set-Content -LiteralPath $RollbackProfilePath -Encoding ASCII -NoNewline -Value $existingRollbackProfileContent
$rollbackProfileExitCode = Invoke-PowerShellScriptExpectFailure -FilePath $InstallerPath -Arguments @(
  '-CodexHome', $RollbackHome,
  '-PowerShellProfilePath', $RollbackProfilePath,
  '-NativeCodexCommandPath', $FakeNativeCodexPath,
  '-OmxCommandPath', $FakeOmxPath,
  '-PythonCommandPath', $ResolvedPythonPath,
  '-TestFailPoint', 'after_profile'
)
Assert-True ($rollbackProfileExitCode -ne 0) 'Installer should fail when the profile rollback fail point is injected.'
Assert-Equal ((Get-Content -LiteralPath $RollbackProfilePath -Raw).Trim()) $existingRollbackProfileContent 'Rollback did not restore the pre-install PowerShell profile content.'

New-Item -ItemType Directory -Force -Path (Join-Path $ConflictHome 'bin') | Out-Null
Set-Content -LiteralPath (Join-Path $ConflictHome 'bin\codex-omx-on.ps1') -Encoding ASCII -Value '# user owned script'
$failureExitCode = Invoke-PowerShellScriptExpectFailure -FilePath $InstallerPath -Arguments @(
  '-CodexHome', $ConflictHome,
  '-PowerShellProfilePath', $ConflictProfilePath,
  '-NativeCodexCommandPath', $FakeNativeCodexPath,
  '-OmxCommandPath', $FakeOmxPath,
  '-PythonCommandPath', $ResolvedPythonPath
)
Assert-True ($failureExitCode -ne 0) 'Installer should fail when an unmanaged conflicting wrapper already exists.'

Set-Content -LiteralPath $ConflictProfilePath -Encoding ASCII -NoNewline -Value "function codex { 'user-owned' }"
$profileConflictExitCode = Invoke-PowerShellScriptExpectFailure -FilePath $InstallerPath -Arguments @(
  '-CodexHome', (Join-Path $TempRoot 'profile-conflict-home'),
  '-PowerShellProfilePath', $ConflictProfilePath,
  '-NativeCodexCommandPath', $FakeNativeCodexPath,
  '-OmxCommandPath', $FakeOmxPath,
  '-PythonCommandPath', $ResolvedPythonPath
)
Assert-True ($profileConflictExitCode -ne 0) 'Installer should fail when the PowerShell profile already contains an unmanaged codex binding.'

Write-Output 'ok'
