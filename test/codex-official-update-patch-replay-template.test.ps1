[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
$TemplatePath = Join-Path $Root 'tools\codex-official-update-patch-replay-template.ps1'
$TempRoot = Join-Path $Root '.tmp\codex-official-update-patch-replay-template-test'
$OfficialRoot = Join-Path $TempRoot 'official-omx'
$CodexHome = Join-Path $TempRoot 'codex-home'
$SnapshotRoot = Join-Path $TempRoot 'snapshot'
$FakeBin = Join-Path $TempRoot 'fake-bin'
$PatchNames = @('runtime-prompt-shutdown', 'controller-prompt-shutdown', 'controller-exec-status')

function Assert-Equal {
  param(
    [Parameter(Mandatory)] $Actual,
    [Parameter(Mandatory)] $Expected,
    [Parameter(Mandatory)] [string]$Message
  )
  if ($Actual -ne $Expected) {
    throw "$Message`nExpected: $Expected`nActual: $Actual"
  }
}

function Assert-True {
  param(
    [Parameter(Mandatory)] [bool]$Condition,
    [Parameter(Mandatory)] [string]$Message
  )
  if (-not $Condition) { throw $Message }
}

function Assert-ArrayContains {
  param(
    [Parameter(Mandatory)] [string[]]$Actual,
    [Parameter(Mandatory)] [string]$Expected,
    [Parameter(Mandatory)] [string]$Message
  )
  if ($Expected -notin $Actual) {
    throw "$Message`nExpected item: $Expected`nActual: $($Actual -join ', ')"
  }
}

function Ensure-Directory {
  param([Parameter(Mandatory)] [string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
  }
}

function Remove-TestTree {
  param([Parameter(Mandatory)] [string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) { return }
  $fullRoot = [System.IO.Path]::GetFullPath($Root)
  $fullPath = [System.IO.Path]::GetFullPath($Path)
  if (-not $fullPath.StartsWith($fullRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to remove test tree outside repository root: $fullPath"
  }
  Remove-Item -LiteralPath $Path -Recurse -Force
}

function New-TemplateInvocation {
  param(
    [Parameter(Mandatory)]
    [string]$Stage,
    [string[]]$PatchName = $PatchNames,
    [switch]$ApproveDiff,
    [string]$DiffApprovalNote = ''
  )

  $invocation = @{
    RepoRoot = $Root
    OfficialOmxRoot = $OfficialRoot
    CodexHome = $CodexHome
    SnapshotRoot = $SnapshotRoot
    PatchName = $PatchName
    Stage = $Stage
    Json = $true
  }
  if ($ApproveDiff) {
    $invocation['ApproveDiff'] = $true
  }
  if (-not [string]::IsNullOrWhiteSpace($DiffApprovalNote)) {
    $invocation['DiffApprovalNote'] = $DiffApprovalNote
  }
  return $invocation
}

function Invoke-TemplateJson {
  param(
    [Parameter(Mandatory)]
    [string]$Stage,
    [string[]]$PatchName = $PatchNames,
    [switch]$ApproveDiff,
    [string]$DiffApprovalNote = ''
  )

  $invocation = New-TemplateInvocation -Stage $Stage -PatchName $PatchName -ApproveDiff:$ApproveDiff -DiffApprovalNote $DiffApprovalNote
  $output = @(& $TemplatePath @invocation)
  $jsonText = ($output | ForEach-Object { [string]$_ }) -join [Environment]::NewLine
  if ([string]::IsNullOrWhiteSpace($jsonText)) {
    throw "Template command produced no JSON output for stage: $Stage"
  }
  return ($jsonText | ConvertFrom-Json)
}

function Invoke-TemplateFailureText {
  param(
    [Parameter(Mandatory)]
    [string]$Stage,
    [string[]]$PatchName = $PatchNames,
    [switch]$ApproveDiff,
    [string]$DiffApprovalNote = ''
  )

  $invocation = New-TemplateInvocation -Stage $Stage -PatchName $PatchName -ApproveDiff:$ApproveDiff -DiffApprovalNote $DiffApprovalNote
  try {
    $null = & $TemplatePath @invocation 2>&1
  } catch {
    return [string]$_.Exception.Message
  }
  throw "Template command unexpectedly succeeded for stage: $Stage"
}

function New-StagedOfficialInstallTree {
  $teamRoot = Join-Path $OfficialRoot 'dist\team'
  Ensure-Directory -Path $teamRoot
  Ensure-Directory -Path (Join-Path $CodexHome 'bin')
  Ensure-Directory -Path (Join-Path $CodexHome 'skills\worker')

  $RuntimeSource = @(
    'import { join, resolve, dirname } from ''path'';'
    'import { existsSync, appendFileSync, mkdirSync, openSync, closeSync } from ''fs'';'
    'import { mkdir, readdir, readFile, writeFile } from ''fs/promises'';'
    'import { spawn, spawnSync } from ''child_process'';'
    'import { resolveCanonicalTeamStateRoot } from ''./state-root.js'';'
    ''
    'function isPidAlive(pid) {'
    '    return Number.isFinite(pid) && pid > 0;'
    '}'
    'async function waitForTrackedPidsExit(tracked, timeoutMs) {'
    '    return tracked.every((pid) => !isPidAlive(pid));'
    '}'
    'async function terminateTrackedProcessTree(rootPid, processGroupId = null, graceMs = PROMPT_WORKER_SIGTERM_WAIT_MS, killWaitMs = PROMPT_WORKER_SIGKILL_WAIT_MS) {'
    '    if (process.platform === ''win32'') {'
    '        const trackedPids = Number.isFinite(rootPid) && rootPid > 0 ? [rootPid] : [];'
    '        if (trackedPids.length === 0) {'
    '            return { terminated: true, forcedKill: false, trackedPids: [] };'
    '        }'
    '        const taskkill = spawnSync(''taskkill'', [''/PID'', String(rootPid), ''/T'', ''/F''], {'
    '            stdio: ''ignore'','
    '            windowsHide: true,'
    '        });'
    '        if (taskkill.error && taskkill.error.code !== ''ESRCH'') {'
    '            process.stderr.write(`[team/runtime] operation failed: ${taskkill.error}\n`);'
    '        }'
    '        return {'
    '            terminated: await waitForTrackedPidsExit(trackedPids, killWaitMs),'
    '            forcedKill: true,'
    '            trackedPids,'
    '        };'
    '    }'
    '    return { terminated: true, forcedKill: false, trackedPids: [] };'
    '}'
    'async function teardownPromptWorker(teamName, workerName, fallbackPid, cwd, context) {'
    '    const handle = getPromptWorkerHandle(teamName, workerName);'
    '    const handlePid = handle?.pid;'
    '    const processGroupId = handle?.processGroupId ?? null;'
    '    const pid = (typeof handlePid === ''number'' && Number.isFinite(handlePid))'
    '        ? handlePid'
    '        : (Number.isFinite(fallbackPid) && (fallbackPid ?? 0) > 0 ? fallbackPid : null);'
    '    if (pid === null && processGroupId === null) {'
    '        removePromptWorkerHandle(teamName, workerName);'
    '        return { terminated: true, forcedKill: false, pid: null };'
    '    }'
    '    const teardown = await terminateTrackedProcessTree(pid ?? 0, processGroupId);'
    '    const processGone = processGroupId ? !isProcessGroupAlive(processGroupId) : !isPidAlive(pid);'
    '    if (teardown.terminated && processGone) {'
    '        removePromptWorkerHandle(teamName, workerName);'
    '        return { terminated: true, forcedKill: teardown.forcedKill, pid };'
    '    }'
    '}'
  ) -join [Environment]::NewLine
  Set-Content -LiteralPath (Join-Path $teamRoot 'runtime.js') -Encoding UTF8 -NoNewline -Value $RuntimeSource

  $ControllerSource = @(
    'import { appendFileSync, closeSync, existsSync, mkdirSync, openSync, readFileSync, writeFileSync } from ''fs'';'
    'import { dirname, join } from ''path'';'
    'import { spawn } from ''child_process'';'
    ''
    'async function main() {'
    '    const teamName = ''team-a'';'
    '    const workerName = ''worker-1'';'
    '    const teamStateRoot = join(process.cwd(), ''.omx'', ''state'');'
    '    const controllerDebugRoot = join(teamStateRoot, ''prompt-controller-debug'', teamName);'
    '    const statusPath = teamName && workerName && teamStateRoot'
    '        ? join(teamStateRoot, ''team'', teamName, ''workers'', workerName, ''status.json'')'
    '        : '''';'
    '    const omxEntryPath = resolveOmxCliEntryPath();'
    '    const queue = [];'
    '    let activeChild = null;'
    '    const log = (event, details = {}) => {'
    '        if (controllerLogPath === '''')'
    '            return;'
    '        try {'
    '            mkdirSync(dirname(controllerLogPath), { recursive: true });'
    '        }'
    '        catch {'
    '            // Fall through to append attempt.'
    '        }'
    '        try {'
    '            appendFileSync(controllerLogPath, `${JSON.stringify({ ts: new Date().toISOString(), event, ...details })}\n`, ''utf-8'');'
    '        }'
    '        catch {'
    '            // Best-effort debug log only.'
    '        }'
    '    };'
    '    function launchExecTurn(promptText) {'
    '        const normalizedPrompt = promptText;'
    '        const launchMode = ''exec_arg'';'
    '        const command = ''node'';'
    '        const args = [''worker.js''];'
    '        const stdoutFd = execStdoutLogPath !== '''' ? openSync(execStdoutLogPath, ''a'') : ''ignore'';'
    '        const stderrFd = execStderrLogPath !== '''' ? openSync(execStderrLogPath, ''a'') : ''ignore'';'
    '        activeChild = spawn(command, args, {'
    '                cwd: process.cwd(),'
    '                env: process.env,'
    '                stdio: [''pipe'', stdoutFd, stderrFd],'
    '                windowsHide: true,'
    '            });'
    '            // OPENCLAW_OMX_WINDOWS_PROMPT_CONTROLLER_STDIN_CLOSE_FIX_V1'
    '        activeChild.once(''exit'', () => {'
    '            log(''exec_exit'', { code: activeChild?.exitCode ?? null, signal: activeChild?.signalCode ?? null });'
    '            activeChild = null;'
    '            if (queue.length > 0) {'
    '                const next = queue.shift();'
    '                launchExecTurn(next);'
    '                return;'
    '            }'
    '        });'
    '    }'
    '}'
  ) -join [Environment]::NewLine
  Set-Content -LiteralPath (Join-Path $teamRoot 'windows-worker-controller.js') -Encoding UTF8 -NoNewline -Value $ControllerSource

  Set-Content -LiteralPath (Join-Path $teamRoot 'worker-bootstrap.js') -Encoding UTF8 -NoNewline -Value "// staged worker bootstrap placeholder`n"
  Set-Content -LiteralPath (Join-Path $CodexHome 'skills\worker\SKILL.md') -Encoding UTF8 -NoNewline -Value "---`nname: worker`ndescription: staged worker skill`n---`n"
}

function New-FakeCommandBin {
  Ensure-Directory -Path $FakeBin
  $fakeNpm = @(
    '@echo off',
    'if "%1"=="ls" (',
    '  echo staged npm listing stdout',
    '  echo staged npm listing stderr 1>&2',
    '  exit /b 7',
    ')',
    'if "%1"=="root" (',
    '  echo C:\staged\npm-root',
    '  exit /b 0',
    ')',
    'echo staged npm %*',
    'exit /b 0'
  ) -join [Environment]::NewLine
  Set-Content -LiteralPath (Join-Path $FakeBin 'npm.cmd') -Encoding ASCII -NoNewline -Value $fakeNpm

  $fakeOmx = @(
    '@echo off',
    'echo staged omx %*',
    'exit /b 0'
  ) -join [Environment]::NewLine
  Set-Content -LiteralPath (Join-Path $FakeBin 'omx.cmd') -Encoding ASCII -NoNewline -Value $fakeOmx

  $fakePwsh = @(
    '@echo off',
    'echo staged powershell cwd %CD%',
    'echo staged powershell host %*',
    'echo staged powershell stderr raw 1>&2',
    'exit /b 0'
  ) -join [Environment]::NewLine
  Set-Content -LiteralPath (Join-Path $FakeBin 'pwsh.cmd') -Encoding ASCII -NoNewline -Value $fakePwsh
}

Remove-TestTree -Path $TempRoot
New-StagedOfficialInstallTree
New-FakeCommandBin

$previousPath = [Environment]::GetEnvironmentVariable('Path', 'Process')
$previousUpperPath = [Environment]::GetEnvironmentVariable('PATH', 'Process')
try {
  $nodeCommand = Get-Command 'node.exe' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($null -eq $nodeCommand) {
    $nodeCommand = Get-Command 'node' -ErrorAction Stop | Select-Object -First 1
  }
  $nodeDirectory = Split-Path -Parent ([string]$nodeCommand.Source)
  $system32 = Join-Path $env:SystemRoot 'System32'
  [Environment]::SetEnvironmentVariable('PATH', 'C:\stale-uppercase-path-entry', 'Process')
  [Environment]::SetEnvironmentVariable('Path', ($FakeBin + ';' + $nodeDirectory + ';' + $system32), 'Process')

  $replayTemplateContent = Get-Content -LiteralPath $TemplatePath -Raw
  $invokeExternalCommandBody = [regex]::Match($replayTemplateContent, 'function Invoke-ExternalCommand \{(?s:.*?)^}', [System.Text.RegularExpressions.RegexOptions]::Multiline).Value
  Assert-True (-not [string]::IsNullOrWhiteSpace($invokeExternalCommandBody)) 'Could not find Invoke-ExternalCommand in the replay template.'
  Assert-True (-not $invokeExternalCommandBody.Contains('Start-Process')) 'Invoke-ExternalCommand must not use Start-Process because Windows process environments may expose duplicate PATH/Path keys.'

  $replayBeforePrecheckError = Invoke-TemplateFailureText -Stage 'replay'
  Assert-True ($replayBeforePrecheckError.Contains("requires a checkpoint that already contains stage 'precheck'")) 'Replay stage did not fail closed before a precheck checkpoint existed.'

  $precheck = Invoke-TemplateJson -Stage 'precheck'
  Assert-Equal $precheck.stage.stage 'precheck' 'Precheck stage report used the wrong stage.'
  Assert-Equal (@($precheck.patch_catalog).Count) 3 'PatchName filtering did not narrow the precheck patch catalog.'
  Assert-ArrayContains -Actual @($precheck.patch_catalog | ForEach-Object { [string]$_.name }) -Expected 'runtime-prompt-shutdown' -Message 'Precheck patch catalog omitted runtime-prompt-shutdown.'
  Assert-Equal ([int]$precheck.environment.global_npm_listing.exit_code) 7 'Global npm listing should preserve non-zero exit codes when IgnoreExitCode is used.'
  $globalNpmListingOutput = @($precheck.environment.global_npm_listing.output | ForEach-Object { [string]$_ })
  Assert-ArrayContains -Actual $globalNpmListingOutput -Expected 'staged npm listing stdout' -Message 'Global npm listing did not preserve raw stdout.'
  Assert-ArrayContains -Actual $globalNpmListingOutput -Expected 'staged npm listing stderr ' -Message 'Global npm listing did not preserve raw stderr.'
  Assert-True (-not (($globalNpmListingOutput -join [Environment]::NewLine).Contains('NativeCommandError'))) 'Global npm listing stderr was polluted by PowerShell NativeCommandError formatting.'
  Assert-True (-not (($globalNpmListingOutput -join [Environment]::NewLine).Contains('FullyQualifiedErrorId'))) 'Global npm listing stderr was polluted by PowerShell error-record metadata.'

  $diff = Invoke-TemplateJson -Stage 'diff'
  Assert-Equal $diff.stage.stage 'diff' 'Diff stage report used the wrong stage.'
  Assert-True ($diff.approvals.diff_review.approved -eq $false) 'Diff stage without -ApproveDiff should not approve replay.'

  $replayWithoutApprovalError = Invoke-TemplateFailureText -Stage 'replay'
  Assert-True ($replayWithoutApprovalError.Contains('approvals.diff_review.approved = true')) 'Replay stage did not require explicit diff-review approval.'

  $approvedDiff = Invoke-TemplateJson -Stage 'diff' -ApproveDiff -DiffApprovalNote 'test approval for staged official install patches'
  Assert-True ($approvedDiff.approvals.diff_review.approved -eq $true) 'Diff approval was not persisted in the report.'

  $replay = Invoke-TemplateJson -Stage 'replay'
  Assert-Equal $replay.stage.stage 'replay' 'Replay stage report used the wrong stage.'
  Assert-True ($replay.stage_gate.diff_review_approved -eq $true) 'Replay stage did not observe the approved diff gate.'
  Assert-Equal (Get-Location).Path $Root 'Template invocation did not restore the parent PowerShell location after running a command with WorkingDirectory.'
  $installerRegenerationOutput = @($replay.installer_regeneration.output | ForEach-Object { [string]$_ })
  Assert-ArrayContains -Actual $installerRegenerationOutput -Expected "staged powershell cwd $Root" -Message 'Installer regeneration command did not run in the requested working directory.'
  Assert-ArrayContains -Actual $installerRegenerationOutput -Expected 'staged powershell stderr raw ' -Message 'Installer regeneration did not preserve raw stderr.'
  Assert-True (-not (($installerRegenerationOutput -join [Environment]::NewLine).Contains('NativeCommandError'))) 'Installer regeneration stderr was polluted by PowerShell NativeCommandError formatting.'
  Assert-Equal (@($replay.patch_catalog).Count) 3 'PatchName filtering did not narrow the replay patch catalog.'
  $replayedPatchNames = @($replay.official_patch_replay | ForEach-Object { [string]$_.patch })
  foreach ($patchName in $PatchNames) {
    Assert-ArrayContains -Actual $replayedPatchNames -Expected $patchName -Message "Replay results did not include $patchName."
  }
  $reversedPatchNameReplay = Invoke-TemplateJson -Stage 'replay' -PatchName @('controller-exec-status', 'controller-prompt-shutdown')
  $reversedPatchNameReplayNames = @($reversedPatchNameReplay.official_patch_replay | ForEach-Object { [string]$_.patch })
  Assert-Equal (@($reversedPatchNameReplayNames).Count) 2 'Reverse PatchName replay should include exactly the requested controller patches.'
  Assert-Equal ([string]$reversedPatchNameReplayNames[0]) 'controller-prompt-shutdown' 'PatchName filtering must preserve catalog order before controller exec-status replay.'
  Assert-Equal ([string]$reversedPatchNameReplayNames[1]) 'controller-exec-status' 'PatchName filtering must preserve catalog order for controller exec-status replay.'
  foreach ($result in @($replay.official_patch_replay)) {
    Assert-True ($result.ok -eq $true) "Replay result for $($result.patch) was not ok."
    Assert-Equal ([string]$result.status) 'patched' "Replay result for $($result.patch) did not apply a patch."
  }

  $runtimeContent = Get-Content -LiteralPath (Join-Path $OfficialRoot 'dist\team\runtime.js') -Raw
  $controllerContent = Get-Content -LiteralPath (Join-Path $OfficialRoot 'dist\team\windows-worker-controller.js') -Raw
  Assert-True ($runtimeContent.Contains('OPENCLAW_OMX_WINDOWS_PROMPT_RUNTIME_SHUTDOWN_FIX_V1')) 'Replay did not write the runtime shutdown marker to the staged official install tree.'
  Assert-True ($controllerContent.Contains('OPENCLAW_OMX_WINDOWS_PROMPT_CONTROLLER_SHUTDOWN_FIX_V1')) 'Replay did not write the controller shutdown marker to the staged official install tree.'
  Assert-True ($controllerContent.Contains('OPENCLAW_OMX_WINDOWS_PROMPT_CONTROLLER_EXEC_STATUS_FIX_V1')) 'Replay did not write the controller exec-status marker to the staged official install tree.'

  $checkpoint = Get-Content -LiteralPath (Join-Path $SnapshotRoot 'checkpoint.json') -Raw | ConvertFrom-Json
  Assert-True ($checkpoint.approvals.diff_review.approved -eq $true) 'Checkpoint did not retain diff-review approval after replay.'
  Assert-ArrayContains -Actual @($checkpoint.stage_history | ForEach-Object { [string]$_.stage }) -Expected 'precheck' -Message 'Checkpoint history omitted precheck.'
  Assert-ArrayContains -Actual @($checkpoint.stage_history | ForEach-Object { [string]$_.stage }) -Expected 'diff' -Message 'Checkpoint history omitted diff.'
  Assert-ArrayContains -Actual @($checkpoint.stage_history | ForEach-Object { [string]$_.stage }) -Expected 'replay' -Message 'Checkpoint history omitted replay.'

  $unknownPatchError = Invoke-TemplateFailureText -Stage 'precheck' -PatchName @('missing-patch-name')
  Assert-True ($unknownPatchError.Contains('Unknown patch name(s): missing-patch-name')) 'Unknown PatchName did not fail closed.'
  $blankPatchError = Invoke-TemplateFailureText -Stage 'precheck' -PatchName @('  ')
  Assert-True ($blankPatchError.Contains('PatchName must contain at least one non-empty patch name.')) 'Blank PatchName did not fail closed.'

  Write-Host 'codex-official-update-patch-replay-template: ok'
} finally {
  [Environment]::SetEnvironmentVariable('Path', $previousPath, 'Process')
  [Environment]::SetEnvironmentVariable('PATH', $previousUpperPath, 'Process')
  Remove-TestTree -Path $TempRoot
}
