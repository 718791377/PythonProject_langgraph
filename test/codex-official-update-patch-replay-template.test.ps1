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
$FakeNpmRoot = Join-Path $TempRoot 'npm-root'
$NpmInstallMarker = Join-Path $TempRoot 'npm-install.marker'
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
    [switch]$AllowLockedCodexUpdate,
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
  if ($AllowLockedCodexUpdate) {
    $invocation['AllowLockedCodexUpdate'] = $true
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
    [switch]$AllowLockedCodexUpdate,
    [string]$DiffApprovalNote = ''
  )

  $invocation = New-TemplateInvocation -Stage $Stage -PatchName $PatchName -ApproveDiff:$ApproveDiff -AllowLockedCodexUpdate:$AllowLockedCodexUpdate -DiffApprovalNote $DiffApprovalNote
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
    [switch]$AllowLockedCodexUpdate,
    [string]$DiffApprovalNote = ''
  )

  $invocation = New-TemplateInvocation -Stage $Stage -PatchName $PatchName -ApproveDiff:$ApproveDiff -AllowLockedCodexUpdate:$AllowLockedCodexUpdate -DiffApprovalNote $DiffApprovalNote
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

function Test-IsWindowsPlatform {
  return ([System.Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT)
}

function Set-ExecutableBitIfNeeded {
  param([Parameter(Mandatory)] [string[]]$Path)
  if (Test-IsWindowsPlatform) { return }
  foreach ($item in $Path) {
    if (Test-Path -LiteralPath $item) {
      & chmod '+x' $item
      if ($LASTEXITCODE -ne 0) {
        throw "chmod failed for fake command: $item"
      }
    }
  }
}

function New-FakeCommandBin {
  Ensure-Directory -Path $FakeBin
  $fakeNpm = @(
    '@echo off',
    'if "%1"=="ls" goto ls',
    'if "%1"=="root" goto root',
    'if "%1"=="install" goto install',
    'echo staged npm %*',
    'exit /b 0',
    ':ls',
    'echo staged npm listing stdout',
    'echo staged npm listing stderr 1>&2',
    'exit /b 7',
    ':root',
    'if not "%CODEX_TEST_NPM_ROOT%"=="" echo %CODEX_TEST_NPM_ROOT%',
    'if "%CODEX_TEST_NPM_ROOT%"=="" echo C:\staged\npm-root',
    'exit /b 0',
    ':install',
    'if not "%CODEX_TEST_NPM_INSTALL_MARKER%"=="" echo staged npm install>"%CODEX_TEST_NPM_INSTALL_MARKER%"',
    'if "%CODEX_TEST_NPM_INSTALL_OUTPUT_MODE%"=="cleanup_eperm" goto cleanup_eperm',
    'if "%CODEX_TEST_NPM_INSTALL_OUTPUT_MODE%"=="eperm_only" goto eperm_only',
    'goto install_exit',
    ':cleanup_eperm',
    'echo npm warn cleanup Failed to remove some directories [',
    'echo npm warn cleanup EPERM: operation not permitted, unlink "%CODEX_TEST_NPM_ROOT%\@openai\.codex-locked\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe"',
    'echo npm warn cleanup ]',
    'goto install_exit',
    ':eperm_only',
    'echo npm warn EPERM: operation not permitted while probing "%CODEX_TEST_NPM_ROOT%\@openai\codex\vendor\x86_64-pc-windows-msvc\bin\codex.exe"',
    'goto install_exit',
    ':install_exit',
    'if not "%CODEX_TEST_NPM_INSTALL_EXIT_CODE%"=="" exit /b %CODEX_TEST_NPM_INSTALL_EXIT_CODE%',
    'echo staged npm install %*',
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

  if (-not (Test-IsWindowsPlatform)) {
    $fakeNpmPath = Join-Path $FakeBin 'npm'
    $fakeNpmUnix = @'
#!/bin/sh
case "$1" in
  ls)
    echo "staged npm listing stdout"
    echo "staged npm listing stderr " >&2
    exit 7
    ;;
  root)
    if [ -n "$CODEX_TEST_NPM_ROOT" ]; then printf '%s\n' "$CODEX_TEST_NPM_ROOT"; else printf '%s\n' '/tmp/staged/npm-root'; fi
    exit 0
    ;;
  install)
    if [ -n "$CODEX_TEST_NPM_INSTALL_MARKER" ]; then printf '%s\n' 'staged npm install' > "$CODEX_TEST_NPM_INSTALL_MARKER"; fi
    case "$CODEX_TEST_NPM_INSTALL_OUTPUT_MODE" in
      cleanup_eperm)
        echo 'npm warn cleanup Failed to remove some directories ['
        printf '%s\n' "npm warn cleanup EPERM: operation not permitted, unlink \"$CODEX_TEST_NPM_ROOT\\@openai\\.codex-locked\\node_modules\\@openai\\codex-win32-x64\\vendor\\x86_64-pc-windows-msvc\\bin\\codex.exe\""
        echo 'npm warn cleanup ]'
        ;;
      eperm_only)
        printf '%s\n' "npm warn EPERM: operation not permitted while probing \"$CODEX_TEST_NPM_ROOT\\@openai\\codex\\vendor\\x86_64-pc-windows-msvc\\bin\\codex.exe\""
        ;;
    esac
    if [ -n "$CODEX_TEST_NPM_INSTALL_EXIT_CODE" ]; then exit "$CODEX_TEST_NPM_INSTALL_EXIT_CODE"; fi
    echo "staged npm install $*"
    exit 0
    ;;
esac
echo "staged npm $*"
exit 0
'@
    Set-Content -LiteralPath $fakeNpmPath -Encoding ASCII -NoNewline -Value $fakeNpmUnix

    $fakeOmxPath = Join-Path $FakeBin 'omx'
    $fakeOmxUnix = @'
#!/bin/sh
echo "staged omx $*"
exit 0
'@
    Set-Content -LiteralPath $fakeOmxPath -Encoding ASCII -NoNewline -Value $fakeOmxUnix

    $fakePwshPath = Join-Path $FakeBin 'pwsh'
    $fakePwshUnix = @'
#!/bin/sh
echo "staged powershell cwd $(pwd)"
echo "staged powershell host $*"
echo "staged powershell stderr raw " >&2
exit 0
'@
    Set-Content -LiteralPath $fakePwshPath -Encoding ASCII -NoNewline -Value $fakePwshUnix
    Set-ExecutableBitIfNeeded -Path @($fakeNpmPath, $fakeOmxPath, $fakePwshPath)
  }
}

function Reset-TemplateCheckpoint {
  if (Test-Path -LiteralPath $SnapshotRoot) {
    Remove-Item -LiteralPath $SnapshotRoot -Recurse -Force
  }
}

function Reset-OfficialUpdateEnv {
  foreach ($name in @(
    'CODEX_TEST_NPM_INSTALL_EXIT_CODE',
    'CODEX_TEST_NPM_INSTALL_OUTPUT_MODE'
  )) {
    [Environment]::SetEnvironmentVariable($name, $null, 'Process')
  }
  [Environment]::SetEnvironmentVariable('CODEX_OFFICIAL_UPDATE_FAKE_PROCESS_INVENTORY_JSON', '[]', 'Process')
  [Environment]::SetEnvironmentVariable('CODEX_TEST_NPM_ROOT', $FakeNpmRoot, 'Process')
  [Environment]::SetEnvironmentVariable('CODEX_TEST_NPM_INSTALL_MARKER', $NpmInstallMarker, 'Process')
  if (Test-Path -LiteralPath $NpmInstallMarker) {
    Remove-Item -LiteralPath $NpmInstallMarker -Force
  }
}

function Initialize-OfficialUpdateCheckpoint {
  Reset-TemplateCheckpoint
  $null = Invoke-TemplateJson -Stage 'precheck'
}

function Get-TemplateReport {
  $reportPath = Join-Path $SnapshotRoot 'report.json'
  Assert-True (Test-Path -LiteralPath $reportPath) "Expected template report to exist at $reportPath."
  return (Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json)
}

function Set-FakeProcessInventory {
  param([object[]]$Processes)
  $json = ConvertTo-Json -InputObject @($Processes) -Depth 10 -Compress
  [Environment]::SetEnvironmentVariable('CODEX_OFFICIAL_UPDATE_FAKE_PROCESS_INVENTORY_JSON', $json, 'Process')
}

function New-FakeCodexLockProcess {
  $fakeCodexExe = Join-Path $FakeNpmRoot '@openai\codex\vendor\x86_64-pc-windows-msvc\bin\codex.exe'
  return [pscustomobject]@{
    id = 1234
    name = 'codex'
    path = $fakeCodexExe
    command_line = "`"$fakeCodexExe`""
  }
}

Remove-TestTree -Path $TempRoot
New-StagedOfficialInstallTree
New-FakeCommandBin
Ensure-Directory -Path (Join-Path $FakeNpmRoot '@openai')
Ensure-Directory -Path (Join-Path $FakeNpmRoot '@openai\.codex-leftover')

$previousPath = [Environment]::GetEnvironmentVariable('Path', 'Process')
$previousUpperPath = [Environment]::GetEnvironmentVariable('PATH', 'Process')
$previousFakeProcessInventory = [Environment]::GetEnvironmentVariable('CODEX_OFFICIAL_UPDATE_FAKE_PROCESS_INVENTORY_JSON', 'Process')
$previousFakeNpmRoot = [Environment]::GetEnvironmentVariable('CODEX_TEST_NPM_ROOT', 'Process')
$previousFakeNpmInstallMarker = [Environment]::GetEnvironmentVariable('CODEX_TEST_NPM_INSTALL_MARKER', 'Process')
$previousFakeNpmInstallExitCode = [Environment]::GetEnvironmentVariable('CODEX_TEST_NPM_INSTALL_EXIT_CODE', 'Process')
$previousFakeNpmInstallOutputMode = [Environment]::GetEnvironmentVariable('CODEX_TEST_NPM_INSTALL_OUTPUT_MODE', 'Process')
try {
  $nodeCommand = Get-Command 'node.exe' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($null -eq $nodeCommand) {
    $nodeCommand = Get-Command 'node' -ErrorAction Stop | Select-Object -First 1
  }
  $nodeDirectory = Split-Path -Parent ([string]$nodeCommand.Source)
  $pathSeparator = [string][System.IO.Path]::PathSeparator
  if (Test-IsWindowsPlatform) {
    $testPathEntries = @($FakeBin, $nodeDirectory)
    $systemRoot = [Environment]::GetEnvironmentVariable('SystemRoot', 'Process')
    if ([string]::IsNullOrWhiteSpace($systemRoot)) {
      $systemRoot = [Environment]::GetEnvironmentVariable('SystemRoot', 'Machine')
    }
    if (-not [string]::IsNullOrWhiteSpace($systemRoot)) {
      $testPathEntries += (Join-Path $systemRoot 'System32')
    }
    [Environment]::SetEnvironmentVariable('PATH', 'C:\stale-uppercase-path-entry', 'Process')
    [Environment]::SetEnvironmentVariable('Path', ($testPathEntries -join $pathSeparator), 'Process')
  } else {
    $existingPath = [Environment]::GetEnvironmentVariable('PATH', 'Process')
    $testPathEntries = @($FakeBin, $nodeDirectory)
    if (-not [string]::IsNullOrWhiteSpace($existingPath)) {
      $testPathEntries += $existingPath.Split($pathSeparator, [System.StringSplitOptions]::RemoveEmptyEntries)
    }
    [Environment]::SetEnvironmentVariable('PATH', (($testPathEntries | Select-Object -Unique) -join $pathSeparator), 'Process')
    [Environment]::SetEnvironmentVariable('Path', $null, 'Process')
  }
  Reset-OfficialUpdateEnv

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

  Reset-OfficialUpdateEnv
  Initialize-OfficialUpdateCheckpoint
  Set-FakeProcessInventory -Processes @((New-FakeCodexLockProcess))
  $lockedUpdateError = Invoke-TemplateFailureText -Stage 'update'
  Assert-True ($lockedUpdateError.Contains('Windows Codex lock preflight detected likely active Codex or Node processes')) 'Update stage did not fail closed when fake Codex lock inventory was present.'
  Assert-True (-not (Test-Path -LiteralPath $NpmInstallMarker)) 'Lock-risk blocking must happen before fake npm install creates the marker.'
  $lockedUpdateReport = Get-TemplateReport
  Assert-Equal ([string]$lockedUpdateReport.windows_codex_lock_preflight.lock_risk) 'detected' 'Lock-risk blocking should still write a structured preflight report.'
  Assert-Equal ([string]$lockedUpdateReport.windows_codex_lock_preflight.recommended_action) 'close_codex_sessions_then_rerun' 'Lock-risk blocking report should recommend closing Codex sessions and rerunning.'

  Reset-OfficialUpdateEnv
  Initialize-OfficialUpdateCheckpoint
  Set-FakeProcessInventory -Processes @((New-FakeCodexLockProcess))
  $overrideUpdate = Invoke-TemplateJson -Stage 'update' -AllowLockedCodexUpdate
  Assert-True (Test-Path -LiteralPath $NpmInstallMarker) 'AllowLockedCodexUpdate should let fake npm install proceed.'
  Assert-True ($overrideUpdate.windows_codex_lock_preflight.override_used -eq $true) 'Lock preflight did not record override_used=true.'
  Assert-Equal ([string]$overrideUpdate.windows_codex_lock_preflight.lock_risk) 'detected' 'Override update should still report detected lock risk.'

  Reset-OfficialUpdateEnv
  Initialize-OfficialUpdateCheckpoint
  [Environment]::SetEnvironmentVariable('CODEX_OFFICIAL_UPDATE_FAKE_PROCESS_INVENTORY_JSON', '{not valid json', 'Process')
  $unknownUpdateError = Invoke-TemplateFailureText -Stage 'update'
  Assert-True ($unknownUpdateError.Contains('Windows Codex lock preflight could not complete safely')) 'Update stage did not fail closed when lock preflight inventory was unknown.'
  Assert-True (-not (Test-Path -LiteralPath $NpmInstallMarker)) 'Unknown lock-risk blocking must happen before fake npm install creates the marker.'
  $unknownUpdateReport = Get-TemplateReport
  Assert-Equal ([string]$unknownUpdateReport.windows_codex_lock_preflight.lock_risk) 'unknown' 'Unknown inventory failure should be reported as lock_risk=unknown.'
  Assert-Equal ([string]$unknownUpdateReport.windows_codex_lock_preflight.recommended_action) 'manual_review' 'Unknown lock-risk report should recommend manual review.'
  Assert-True ($null -eq $unknownUpdateReport.official_update) 'Unknown preflight failure should not execute official npm update by default.'

  Reset-OfficialUpdateEnv
  Initialize-OfficialUpdateCheckpoint
  [Environment]::SetEnvironmentVariable('CODEX_OFFICIAL_UPDATE_FAKE_PROCESS_INVENTORY_JSON', '{not valid json', 'Process')
  $unknownOverrideUpdate = Invoke-TemplateJson -Stage 'update' -AllowLockedCodexUpdate
  Assert-True (Test-Path -LiteralPath $NpmInstallMarker) 'AllowLockedCodexUpdate should let fake npm install proceed when preflight is unknown.'
  Assert-True ($unknownOverrideUpdate.windows_codex_lock_preflight.override_used -eq $true) 'Unknown preflight override did not record override_used=true.'
  Assert-Equal ([string]$unknownOverrideUpdate.windows_codex_lock_preflight.lock_risk) 'unknown' 'Unknown override update should still report lock_risk=unknown.'
  Assert-Equal ([string]$unknownOverrideUpdate.windows_codex_lock_preflight.recommended_action) 'manual_review' 'Unknown override report should keep manual_review recommendation.'

  Reset-OfficialUpdateEnv
  Initialize-OfficialUpdateCheckpoint
  [Environment]::SetEnvironmentVariable('CODEX_TEST_NPM_INSTALL_OUTPUT_MODE', 'cleanup_eperm', 'Process')
  $warningUpdate = Invoke-TemplateJson -Stage 'update'
  Assert-Equal ([int]$warningUpdate.official_update.exit_code) 0 'Successful fake npm install exit code was not preserved.'
  Assert-Equal ([string]$warningUpdate.official_update_cleanup_warnings[0].type) 'windows_file_lock_eperm' 'Successful cleanup EPERM warning was not classified.'

  Reset-OfficialUpdateEnv
  Initialize-OfficialUpdateCheckpoint
  [Environment]::SetEnvironmentVariable('CODEX_TEST_NPM_INSTALL_OUTPUT_MODE', 'eperm_only', 'Process')
  $negativeWarningUpdate = Invoke-TemplateJson -Stage 'update'
  Assert-Equal ([int]$negativeWarningUpdate.official_update.exit_code) 0 'Negative cleanup-warning fixture should still be a successful fake npm install.'
  Assert-Equal (@($negativeWarningUpdate.official_update_cleanup_warnings).Count) 0 'Classifier should not report a cleanup warning without cleanup+unlink+codex.exe evidence.'

  Reset-OfficialUpdateEnv
  Initialize-OfficialUpdateCheckpoint
  [Environment]::SetEnvironmentVariable('CODEX_TEST_NPM_INSTALL_OUTPUT_MODE', 'cleanup_eperm', 'Process')
  [Environment]::SetEnvironmentVariable('CODEX_TEST_NPM_INSTALL_EXIT_CODE', '23', 'Process')
  $failedUpdateError = Invoke-TemplateFailureText -Stage 'update'
  Assert-True ($failedUpdateError.Contains('Command failed (exit 23)')) 'Non-zero fake npm install should remain a command failure.'
  $failedUpdateReport = Get-TemplateReport
  Assert-Equal ([int]$failedUpdateReport.official_update.exit_code) 23 'Failed update report should preserve non-zero npm exit code.'
  Assert-Equal (@($failedUpdateReport.official_update_cleanup_warnings).Count) 0 'Classifier must not turn non-zero npm output into a successful cleanup warning.'
  Assert-True ($null -eq $failedUpdateReport.omx_setup) 'Non-zero npm install must not continue to omx setup.'
  Assert-True ($null -eq $failedUpdateReport.omx_update) 'Non-zero npm install must not continue to omx update.'

  Reset-OfficialUpdateEnv
  Initialize-OfficialUpdateCheckpoint
  $stagingUpdate = Invoke-TemplateJson -Stage 'update'
  $stagingCandidates = @($stagingUpdate.windows_codex_lock_preflight.leftover_staging_candidates | ForEach-Object { [string]$_ })
  Assert-ArrayContains -Actual $stagingCandidates -Expected (Join-Path $FakeNpmRoot '@openai\.codex-leftover') -Message 'Lock preflight did not report fake leftover @openai/.codex-* staging directory.'
  Assert-True (Test-Path -LiteralPath (Join-Path $FakeNpmRoot '@openai\.codex-leftover')) 'Template must report but not delete leftover Codex staging directories.'

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
  [Environment]::SetEnvironmentVariable('CODEX_OFFICIAL_UPDATE_FAKE_PROCESS_INVENTORY_JSON', $previousFakeProcessInventory, 'Process')
  [Environment]::SetEnvironmentVariable('CODEX_TEST_NPM_ROOT', $previousFakeNpmRoot, 'Process')
  [Environment]::SetEnvironmentVariable('CODEX_TEST_NPM_INSTALL_MARKER', $previousFakeNpmInstallMarker, 'Process')
  [Environment]::SetEnvironmentVariable('CODEX_TEST_NPM_INSTALL_EXIT_CODE', $previousFakeNpmInstallExitCode, 'Process')
  [Environment]::SetEnvironmentVariable('CODEX_TEST_NPM_INSTALL_OUTPUT_MODE', $previousFakeNpmInstallOutputMode, 'Process')
  Remove-TestTree -Path $TempRoot
}
