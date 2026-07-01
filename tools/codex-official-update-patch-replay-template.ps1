[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$OfficialOmxRoot,
    [string]$CodexHome = (Join-Path $HOME '.codex'),
    [string]$SnapshotRoot,
    [ValidateSet('custom', 'precheck', 'update', 'diff', 'replay', 'test', 'all')]
    [string]$Stage = 'custom',
    [switch]$RunOfficialUpdate,
    [switch]$AllowLockedCodexUpdate,
    [switch]$RunOmxSetup,
    [switch]$RunOmxUpdate,
    [switch]$ReplayOfficialInstallPatches,
    [switch]$ReplayUserLevelSurfacePatches,
    [switch]$RegenerateUserLevelLayer,
    [switch]$RunInstallerTests,
    [switch]$ApproveDiff,
    [string]$DiffApprovalNote = '',
    [string[]]$PatchName = @(),
    [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Step {
    param([string]$Message)
    Write-Host "[official-update-replay] $Message"
}

function Resolve-StagePlan {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SelectedStage,

        [switch]$RequestedOfficialUpdate,
        [switch]$RequestedOmxSetup,
        [switch]$RequestedOmxUpdate,
        [switch]$RequestedReplayOfficialInstallPatches,
        [switch]$RequestedReplayUserLevelSurfacePatches,
        [switch]$RequestedRegenerateUserLevelLayer,
        [switch]$RequestedRunInstallerTests
    )

    $effective = [ordered]@{
        stage = $SelectedStage
        stage_description = ''
        run_official_update = $RequestedOfficialUpdate.IsPresent
        run_omx_setup = $RequestedOmxSetup.IsPresent
        run_omx_update = $RequestedOmxUpdate.IsPresent
        replay_official_install_patches = $RequestedReplayOfficialInstallPatches.IsPresent
        replay_user_level_surface_patches = $RequestedReplayUserLevelSurfacePatches.IsPresent
        regenerate_user_level_layer = $RequestedRegenerateUserLevelLayer.IsPresent
        run_installer_tests = $RequestedRunInstallerTests.IsPresent
    }

    switch ($SelectedStage) {
        'custom' {
            $effective.stage_description = 'Use the explicitly requested switches only.'
        }
        'precheck' {
            $effective.stage_description = 'Read-only inventory and snapshot stage before any official update.'
        }
        'update' {
            $effective.stage_description = 'Run the official update lane and capture post-update inventory.'
            $effective.run_official_update = $true
            $effective.run_omx_setup = $true
        }
        'diff' {
            $effective.stage_description = 'Read-only post-update comparison stage that regenerates the checklist and patch decision table.'
        }
        'replay' {
            $effective.stage_description = 'Replay required official-install patches and regenerate the local wrapper layer.'
            $effective.replay_official_install_patches = $true
            $effective.regenerate_user_level_layer = $true
        }
        'test' {
            $effective.stage_description = 'Run the regression test lane after replay/regeneration.'
            $effective.run_installer_tests = $true
        }
        'all' {
            $effective.stage_description = 'Run update, replay, and test as one end-to-end maintenance lane.'
            $effective.run_official_update = $true
            $effective.run_omx_setup = $true
            $effective.replay_official_install_patches = $true
            $effective.regenerate_user_level_layer = $true
            $effective.run_installer_tests = $true
        }
        default {
            throw "Unsupported stage: $SelectedStage"
        }
    }

    return [pscustomobject]$effective
}

function Resolve-ExistingPathOrLiteral {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (Test-Path -LiteralPath $Path) {
        return (Resolve-Path -LiteralPath $Path).Path
    }

    return [System.IO.Path]::GetFullPath($Path)
}

function Ensure-Directory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Read-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }

    $raw = Get-Content -LiteralPath $Path -Raw -ErrorAction SilentlyContinue
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return $null
    }

    try {
        return ($raw | ConvertFrom-Json)
    } catch {
        return $null
    }
}

function Get-LatestCheckpointPointerPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRootPath
    )

    return Join-Path (Join-Path $RepoRootPath '.tmp') 'official-update-patch-replay-latest.json'
}

function Get-LatestCheckpointInfo {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRootPath
    )

    $pointerPath = Get-LatestCheckpointPointerPath -RepoRootPath $RepoRootPath
    $pointer = Read-JsonFile -Path $pointerPath
    if ($null -ne $pointer -and -not [string]::IsNullOrWhiteSpace([string]$pointer.snapshot_root) -and (Test-Path -LiteralPath ([string]$pointer.snapshot_root))) {
        return [pscustomobject]@{
            source = 'pointer'
            pointer_path = $pointerPath
            snapshot_root = Resolve-ExistingPathOrLiteral -Path ([string]$pointer.snapshot_root)
            manifest_path = if (-not [string]::IsNullOrWhiteSpace([string]$pointer.checkpoint_manifest_path)) { [string]$pointer.checkpoint_manifest_path } else { '' }
            stage = if (-not [string]::IsNullOrWhiteSpace([string]$pointer.stage)) { [string]$pointer.stage } else { '' }
            report_json_path = if (-not [string]::IsNullOrWhiteSpace([string]$pointer.report_json_path)) { [string]$pointer.report_json_path } else { '' }
        }
    }

    $tmpRoot = Join-Path $RepoRootPath '.tmp'
    if (-not (Test-Path -LiteralPath $tmpRoot)) {
        return $null
    }

    $latestDirectory = Get-ChildItem -LiteralPath $tmpRoot -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like 'official-update-patch-replay-*' } |
        Sort-Object Name |
        Select-Object -Last 1
    if ($null -eq $latestDirectory) {
        return $null
    }

    return [pscustomobject]@{
        source = 'latest_directory'
        pointer_path = $pointerPath
        snapshot_root = $latestDirectory.FullName
        manifest_path = (Join-Path $latestDirectory.FullName 'checkpoint.json')
        stage = ''
        report_json_path = (Join-Path $latestDirectory.FullName 'report.json')
    }
}

function Resolve-SnapshotRootPlan {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRootPath,

        [Parameter(Mandatory = $true)]
        [string]$SelectedStage,

        [string]$ExplicitSnapshotRoot
    )

    if (-not [string]::IsNullOrWhiteSpace($ExplicitSnapshotRoot)) {
        $resolved = Resolve-ExistingPathOrLiteral -Path $ExplicitSnapshotRoot
        return [pscustomobject]@{
            snapshot_root = $resolved
            source = 'explicit'
            latest_checkpoint = $null
        }
    }

    $shouldReuseLatest = $SelectedStage -in @('update', 'diff', 'replay', 'test')
    if ($shouldReuseLatest) {
        $latest = Get-LatestCheckpointInfo -RepoRootPath $RepoRootPath
        if ($null -ne $latest -and -not [string]::IsNullOrWhiteSpace([string]$latest.snapshot_root)) {
            return [pscustomobject]@{
                snapshot_root = Resolve-ExistingPathOrLiteral -Path ([string]$latest.snapshot_root)
                source = "checkpoint:$([string]$latest.source)"
                latest_checkpoint = $latest
            }
        }
    }

    $generated = Resolve-ExistingPathOrLiteral -Path (Join-Path $RepoRootPath (Join-Path '.tmp' ("official-update-patch-replay-{0}" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))))
    return [pscustomobject]@{
        snapshot_root = $generated
        source = 'generated_new'
        latest_checkpoint = $null
    }
}

function Read-CheckpointManifest {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SnapshotRootPath
    )

    return Read-JsonFile -Path (Join-Path $SnapshotRootPath 'checkpoint.json')
}

function Write-CheckpointManifest {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SnapshotRootPath,

        [Parameter(Mandatory = $true)]
        [pscustomobject]$Manifest
    )

    $manifestPath = Join-Path $SnapshotRootPath 'checkpoint.json'
    ($Manifest | ConvertTo-Json -Depth 50) | Set-Content -LiteralPath $manifestPath -Encoding UTF8
    return $manifestPath
}

function Get-CompletedCheckpointStages {
    param(
        [pscustomobject]$CheckpointManifest
    )

    $completed = @()
    if ($null -ne $CheckpointManifest -and $null -ne $CheckpointManifest.stage_history) {
        foreach ($entry in @($CheckpointManifest.stage_history)) {
            $stageName = [string]$entry.stage
            if (-not [string]::IsNullOrWhiteSpace($stageName)) {
                $completed += $stageName
            }
        }
    }

    return @($completed)
}

function Test-CompletedStage {
    param(
        [AllowEmptyCollection()]
        [string[]]$CompletedStages = @(),

        [Parameter(Mandatory = $true)]
        [string[]]$Names
    )

    foreach ($name in $Names) {
        if ($CompletedStages -contains $name) {
            return $true
        }
    }

    return $false
}

function Get-ObjectPropertyValue {
    param(
        [AllowNull()]
        [object]$InputObject,

        [Parameter(Mandatory = $true)]
        [string]$PropertyName
    )

    if ($null -eq $InputObject) {
        return $null
    }

    $property = $InputObject.PSObject.Properties[$PropertyName]
    if ($null -eq $property) {
        return $null
    }

    return $property.Value
}

function Test-TruthyValue {
    param(
        [AllowNull()]
        [object]$Value
    )

    if ($null -eq $Value) {
        return $false
    }

    if ($Value -is [bool]) {
        return [bool]$Value
    }

    $text = ([string]$Value).Trim()
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $false
    }

    return ($text -in @('1', 'true', 'yes', 'y', 'on'))
}

function New-DiffReviewApprovalState {
    param(
        [bool]$Approved = $false,
        [string]$ApprovedAt = '',
        [string]$ApprovalNote = ''
    )

    return [ordered]@{
        approved = $Approved
        approved_at = $ApprovedAt
        approval_note = $ApprovalNote
    }
}

function Get-DiffReviewApprovalState {
    param(
        [AllowNull()]
        [pscustomobject]$CheckpointManifest
    )

    $approvals = Get-ObjectPropertyValue -InputObject $CheckpointManifest -PropertyName 'approvals'
    $diffReview = Get-ObjectPropertyValue -InputObject $approvals -PropertyName 'diff_review'
    if ($null -eq $diffReview) {
        return [pscustomobject](New-DiffReviewApprovalState)
    }

    return [pscustomobject](New-DiffReviewApprovalState `
        -Approved:(Test-TruthyValue -Value (Get-ObjectPropertyValue -InputObject $diffReview -PropertyName 'approved')) `
        -ApprovedAt:(Normalize-DecisionValue -Value (Get-ObjectPropertyValue -InputObject $diffReview -PropertyName 'approved_at')) `
        -ApprovalNote:(Normalize-DecisionValue -Value (Get-ObjectPropertyValue -InputObject $diffReview -PropertyName 'approval_note')))
}

function Test-DiffReviewApproved {
    param(
        [AllowNull()]
        [pscustomobject]$CheckpointManifest
    )

    $diffReview = Get-DiffReviewApprovalState -CheckpointManifest $CheckpointManifest
    return (Test-TruthyValue -Value $diffReview.approved)
}

function Resolve-DiffReviewApprovalState {
    param(
        [AllowNull()]
        [pscustomobject]$CheckpointManifest,

        [Parameter(Mandatory = $true)]
        [string]$SelectedStage,

        [Parameter(Mandatory = $true)]
        [string]$GeneratedAt,

        [switch]$Approve,

        [string]$ApprovalNote = ''
    )

    $existing = Get-DiffReviewApprovalState -CheckpointManifest $CheckpointManifest
    if ($SelectedStage -eq 'diff') {
        if ($Approve) {
            $note = $ApprovalNote
            if ([string]::IsNullOrWhiteSpace($note)) {
                $note = 'Approved via -Stage diff -ApproveDiff.'
            }

            return [pscustomobject](New-DiffReviewApprovalState -Approved $true -ApprovedAt $GeneratedAt -ApprovalNote $note)
        }

        return [pscustomobject](New-DiffReviewApprovalState)
    }

    return $existing
}

function Get-StageGateResult {
    param(
        [Parameter(Mandatory = $true)]
        [pscustomobject]$StagePlan,

        [Parameter(Mandatory = $true)]
        [string]$SelectedStage,

        [Parameter(Mandatory = $true)]
        [string]$SnapshotRootPath,

        [pscustomobject]$CheckpointManifest,

        [Parameter(Mandatory = $true)]
        [string]$SnapshotRootSource
    )

    $completedStages = @(Get-CompletedCheckpointStages -CheckpointManifest $CheckpointManifest)
    $warnings = @()
    $errors = @()

    $replayRequested = $StagePlan.replay_official_install_patches -or $StagePlan.replay_user_level_surface_patches -or $StagePlan.regenerate_user_level_layer
    $testRequested = $StagePlan.run_installer_tests
    $updateRequested = $StagePlan.run_official_update -or $StagePlan.run_omx_setup -or $StagePlan.run_omx_update
    $hasPrecheck = Test-CompletedStage -CompletedStages $completedStages -Names @('precheck')
    $hasDiff = Test-CompletedStage -CompletedStages $completedStages -Names @('diff')
    $hasReplay = Test-CompletedStage -CompletedStages $completedStages -Names @('replay', 'all')
    $hasApprovedDiff = Test-DiffReviewApproved -CheckpointManifest $CheckpointManifest

    if ($SelectedStage -in @('update', 'diff')) {
        if (-not $hasPrecheck -and $SelectedStage -ne 'all') {
            $errors += "Stage '$SelectedStage' requires a checkpoint that already contains stage 'precheck'. Run -Stage precheck first, or supply -SnapshotRoot pointing at an existing checkpoint with precheck completed."
        }
    }

    if ($replayRequested) {
        if ($SelectedStage -ne 'all') {
            if (-not $hasPrecheck) {
                $errors += "Replay/regeneration requires a checkpoint that already contains stage 'precheck'. Run -Stage precheck first, or supply -SnapshotRoot pointing at an existing checkpoint with precheck completed."
            }
            if (-not $hasDiff) {
                $errors += "Replay/regeneration requires a checkpoint that already contains stage 'diff'. Run -Stage diff first so the patch decision table is reviewed before applying patches."
            }
        }
        if (-not $hasApprovedDiff) {
            $errors += "Replay/regeneration requires approvals.diff_review.approved = true in checkpoint.json. Run -Stage diff -ApproveDiff first after reviewing the patch decision table."
        }
    }

    if ($testRequested -and $SelectedStage -ne 'all') {
        if (-not $hasPrecheck) {
            $errors += "Test execution requires a checkpoint that already contains stage 'precheck'. Run -Stage precheck first, or supply -SnapshotRoot pointing at an existing checkpoint with precheck completed."
        }
        if (-not $hasDiff) {
            $errors += "Test execution requires a checkpoint that already contains stage 'diff'. Run -Stage diff first so the decision table is up to date before testing."
        }
        if (-not $hasReplay) {
            $errors += "Test execution requires a checkpoint that already contains stage 'replay'. Run -Stage replay first so tests run against a replayed install state."
        }
    }

    return [pscustomobject]@{
        snapshot_root = $SnapshotRootPath
        snapshot_root_source = $SnapshotRootSource
        completed_stages = @($completedStages)
        diff_review_approved = $hasApprovedDiff
        update_requested = $updateRequested
        replay_requested = $replayRequested
        test_requested = $testRequested
        warnings = @($warnings)
        errors = @($errors)
        allowed = ($errors.Count -eq 0)
    }
}

function Get-FirstCommandPath {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Candidates
    )

    foreach ($candidate in $Candidates) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($null -ne $command -and -not [string]::IsNullOrWhiteSpace([string]$command.Source)) {
            return [string]$command.Source
        }
    }

    return $null
}

function ConvertTo-ProcessArgument {
    param(
        [AllowNull()]
        [string]$Argument
    )

    if ($null -eq $Argument -or $Argument.Length -eq 0) {
        return '""'
    }

    if ($Argument -notmatch '[\s"]') {
        return $Argument
    }

    $quoted = New-Object System.Text.StringBuilder
    [void]$quoted.Append('"')
    $backslashCount = 0
    foreach ($character in $Argument.ToCharArray()) {
        if ($character -eq '\') {
            $backslashCount += 1
            continue
        }

        if ($character -eq '"') {
            if ($backslashCount -gt 0) {
                [void]$quoted.Append(('\' * ($backslashCount * 2)))
            }
            [void]$quoted.Append('\"')
            $backslashCount = 0
            continue
        }

        if ($backslashCount -gt 0) {
            [void]$quoted.Append(('\' * $backslashCount))
            $backslashCount = 0
        }
        [void]$quoted.Append($character)
    }

    if ($backslashCount -gt 0) {
        [void]$quoted.Append(('\' * ($backslashCount * 2)))
    }
    [void]$quoted.Append('"')
    return $quoted.ToString()
}

function Invoke-ExternalCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [string[]]$Arguments = @(),

        [string]$WorkingDirectory,

        [switch]$IgnoreExitCode
    )

    $stdoutPath = Join-Path ([System.IO.Path]::GetTempPath()) ("codex-official-update-stdout-{0}.log" -f ([guid]::NewGuid().ToString('N')))
    $stderrPath = Join-Path ([System.IO.Path]::GetTempPath()) ("codex-official-update-stderr-{0}.log" -f ([guid]::NewGuid().ToString('N')))
    $lines = @()
    $effectiveWorkingDirectory = if ($WorkingDirectory) { $WorkingDirectory } else { (Get-Location).Path }
    if ($WorkingDirectory) {
        Push-Location $WorkingDirectory
    }

    try {
        $startInfo = New-Object System.Diagnostics.ProcessStartInfo
        $startInfo.FileName = $FilePath
        $startInfo.Arguments = (@($Arguments) | ForEach-Object { ConvertTo-ProcessArgument -Argument ([string]$_) }) -join ' '
        $startInfo.WorkingDirectory = $effectiveWorkingDirectory
        $startInfo.UseShellExecute = $false
        $startInfo.RedirectStandardOutput = $true
        $startInfo.RedirectStandardError = $true
        $startInfo.CreateNoWindow = $true

        $process = $null
        try {
            $process = New-Object System.Diagnostics.Process
            $process.StartInfo = $startInfo
            if (-not $process.Start()) {
                throw "Command failed to start: $FilePath"
            }
            $stdoutTask = $process.StandardOutput.ReadToEndAsync()
            $stderrTask = $process.StandardError.ReadToEndAsync()
            $process.WaitForExit()
            $stdoutTask.Wait()
            $stderrTask.Wait()
            [System.IO.File]::WriteAllText($stdoutPath, [string]$stdoutTask.Result, (New-Object System.Text.UTF8Encoding($false)))
            [System.IO.File]::WriteAllText($stderrPath, [string]$stderrTask.Result, (New-Object System.Text.UTF8Encoding($false)))
            $exitCode = [int]$process.ExitCode
        } finally {
            if ($null -ne $process) {
                $process.Dispose()
            }
        }

        if (Test-Path -LiteralPath $stdoutPath) {
            $lines += @(Get-Content -LiteralPath $stdoutPath -ErrorAction SilentlyContinue)
        }
        if (Test-Path -LiteralPath $stderrPath) {
            $lines += @(Get-Content -LiteralPath $stderrPath -ErrorAction SilentlyContinue)
        }
    } finally {
        if ($WorkingDirectory) {
            Pop-Location
        }
        foreach ($tempPath in @($stdoutPath, $stderrPath)) {
            if (Test-Path -LiteralPath $tempPath) {
                Remove-Item -LiteralPath $tempPath -Force -ErrorAction SilentlyContinue
            }
        }
    }

    $result = [ordered]@{
        file_path = $FilePath
        arguments = @($Arguments)
        working_directory = if ($WorkingDirectory) { $WorkingDirectory } else { '' }
        exit_code = $exitCode
        output = @($lines | ForEach-Object { [string]$_ })
    }

    if (-not $IgnoreExitCode -and $exitCode -ne 0) {
        throw "Command failed (exit $exitCode): $FilePath $($Arguments -join ' ')"
    }

    return [pscustomobject]$result
}


function Get-GlobalNpmRootInfo {
    param(
        [AllowNull()]
        [string]$NpmPath
    )

    if ([string]::IsNullOrWhiteSpace($NpmPath)) {
        return [pscustomobject]@{
            root_path = ''
            exit_code = -1
            output = @('npm not found')
            status = 'npm_missing'
        }
    }

    try {
        $result = Invoke-ExternalCommand -FilePath $NpmPath -Arguments @('root', '-g') -IgnoreExitCode
        $npmRoot = ''
        if ($result.exit_code -eq 0) {
            $npmRoot = ($result.output | Select-Object -First 1).Trim()
        }

        return [pscustomobject]@{
            root_path = $npmRoot
            exit_code = [int]$result.exit_code
            output = @($result.output)
            status = if ($result.exit_code -eq 0 -and -not [string]::IsNullOrWhiteSpace($npmRoot)) { 'ok' } else { 'unavailable' }
        }
    } catch {
        return [pscustomobject]@{
            root_path = ''
            exit_code = -1
            output = @([string]$_.Exception.Message)
            status = 'error'
        }
    }
}

function Normalize-PathForComparison {
    param(
        [AllowNull()]
        [string]$Path
    )

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ''
    }

    $normalized = ([string]$Path).Trim().Trim('"') -replace '/', '\'
    try {
        $normalized = [System.IO.Path]::GetFullPath($normalized)
    } catch {
        # Some process command lines contain partial paths or shell syntax; keep the normalized text.
    }

    return $normalized.TrimEnd('\').ToLowerInvariant()
}

function Test-TextContainsPath {
    param(
        [AllowNull()]
        [string]$Text,

        [AllowNull()]
        [string]$Path
    )

    $normalizedText = Normalize-PathForComparison -Path $Text
    $normalizedPath = Normalize-PathForComparison -Path $Path
    if ([string]::IsNullOrWhiteSpace($normalizedText) -or [string]::IsNullOrWhiteSpace($normalizedPath)) {
        return $false
    }

    return $normalizedText.Contains($normalizedPath)
}

function Get-JsonPropertyValue {
    param(
        [AllowNull()]
        [object]$InputObject,

        [Parameter(Mandatory = $true)]
        [string[]]$PropertyNames
    )

    if ($null -eq $InputObject) {
        return $null
    }

    foreach ($propertyName in $PropertyNames) {
        $property = $InputObject.PSObject.Properties[$propertyName]
        if ($null -ne $property) {
            return $property.Value
        }
    }

    return $null
}

function ConvertTo-CodexUpdateProcessInventoryEntry {
    param(
        [AllowNull()]
        [object]$InputObject
    )

    $pidValue = Get-JsonPropertyValue -InputObject $InputObject -PropertyNames @('pid', 'Pid', 'id', 'Id', 'ProcessId', 'process_id')
    $processId = 0
    if ($null -ne $pidValue) {
        [void][int]::TryParse([string]$pidValue, [ref]$processId)
    }

    $nameValue = Get-JsonPropertyValue -InputObject $InputObject -PropertyNames @('process_name', 'ProcessName', 'name', 'Name')
    $pathValue = Get-JsonPropertyValue -InputObject $InputObject -PropertyNames @('executable_path', 'ExecutablePath', 'path', 'Path')
    $commandLineValue = Get-JsonPropertyValue -InputObject $InputObject -PropertyNames @('command_line', 'CommandLine', 'commandLine', 'args')
    $lockedPathValue = Get-JsonPropertyValue -InputObject $InputObject -PropertyNames @('locked_paths', 'LockedPaths', 'open_files', 'OpenFiles', 'modules', 'Modules')

    $lockedPaths = @()
    foreach ($lockedPath in @($lockedPathValue)) {
        if ($null -ne $lockedPath -and -not [string]::IsNullOrWhiteSpace([string]$lockedPath)) {
            $lockedPaths += [string]$lockedPath
        }
    }

    return [pscustomobject]@{
        pid = $processId
        process_name = if ($null -ne $nameValue) { [string]$nameValue } else { '' }
        executable_path = if ($null -ne $pathValue) { [string]$pathValue } else { '' }
        command_line = if ($null -ne $commandLineValue) { [string]$commandLineValue } else { '' }
        locked_paths = @($lockedPaths)
    }
}

function Get-CodexUpdateProcessInventory {
    $fakeInventoryJson = [Environment]::GetEnvironmentVariable('CODEX_OFFICIAL_UPDATE_FAKE_PROCESS_INVENTORY_JSON', 'Process')
    if (-not [string]::IsNullOrWhiteSpace($fakeInventoryJson)) {
        try {
            $rawEntries = $fakeInventoryJson | ConvertFrom-Json
            return [pscustomobject]@{
                source = 'env:CODEX_OFFICIAL_UPDATE_FAKE_PROCESS_INVENTORY_JSON'
                processes = @($rawEntries | ForEach-Object { ConvertTo-CodexUpdateProcessInventoryEntry -InputObject $_ })
                error = ''
            }
        } catch {
            return [pscustomobject]@{
                source = 'env:CODEX_OFFICIAL_UPDATE_FAKE_PROCESS_INVENTORY_JSON'
                processes = @()
                error = "Failed to parse fake process inventory JSON: $([string]$_.Exception.Message)"
            }
        }
    }

    try {
        $processes = @(Get-CimInstance Win32_Process -ErrorAction Stop | ForEach-Object {
            [pscustomobject]@{
                pid = [int]$_.ProcessId
                process_name = [string]$_.Name
                executable_path = if ($null -ne $_.ExecutablePath) { [string]$_.ExecutablePath } else { '' }
                command_line = if ($null -ne $_.CommandLine) { [string]$_.CommandLine } else { '' }
                locked_paths = @()
            }
        })
        return [pscustomobject]@{
            source = 'cim:Win32_Process'
            processes = @($processes)
            error = ''
        }
    } catch {
        return [pscustomobject]@{
            source = 'cim:Win32_Process'
            processes = @()
            error = [string]$_.Exception.Message
        }
    }
}

function Get-CodexPackageLockTargets {
    param(
        [AllowNull()]
        [string]$GlobalNpmRoot
    )

    $openAiScopeRoot = ''
    $codexPackageRoot = ''
    $stagingDirectories = @()
    if (-not [string]::IsNullOrWhiteSpace($GlobalNpmRoot)) {
        $openAiScopeRoot = Join-Path $GlobalNpmRoot '@openai'
        $codexPackageRoot = Join-Path $openAiScopeRoot 'codex'
        if (Test-Path -LiteralPath $openAiScopeRoot) {
            $stagingDirectories = @(Get-ChildItem -LiteralPath $openAiScopeRoot -Directory -Filter '.codex-*' -ErrorAction SilentlyContinue | ForEach-Object {
                [pscustomobject]@{
                    path = [string]$_.FullName
                    exists = $true
                }
            })
        }
    }

    return [pscustomobject]@{
        global_npm_root = if ($GlobalNpmRoot) { $GlobalNpmRoot } else { '' }
        openai_scope_root = $openAiScopeRoot
        codex_package_root = $codexPackageRoot
        staging_directories = @($stagingDirectories)
    }
}

function Find-CodexPackageLockingProcesses {
    param(
        [Parameter(Mandatory = $true)]
        [object[]]$Processes,

        [Parameter(Mandatory = $true)]
        [pscustomobject]$Targets
    )

    $targetPaths = @()
    if (-not [string]::IsNullOrWhiteSpace([string]$Targets.codex_package_root)) {
        $targetPaths += [string]$Targets.codex_package_root
    }
    foreach ($stagingDirectory in @($Targets.staging_directories)) {
        if (-not [string]::IsNullOrWhiteSpace([string]$stagingDirectory.path)) {
            $targetPaths += [string]$stagingDirectory.path
        }
    }

    if ($targetPaths.Count -eq 0) {
        return @()
    }

    $locking = @()
    foreach ($process in @($Processes)) {
        $name = ([string]$process.process_name).ToLowerInvariant()
        $isCodexProcess = $name -in @('codex', 'codex.exe')
        $isCandidate = $isCodexProcess -or $name -in @('node', 'node.exe')
        if (-not $isCandidate) {
            continue
        }

        $matchedPaths = @()
        $matchedFields = @()
        if ($isCodexProcess) {
            $matchedFields += 'process_name'
            if (-not [string]::IsNullOrWhiteSpace([string]$Targets.codex_package_root)) {
                $matchedPaths += [string]$Targets.codex_package_root
            }
        }
        foreach ($targetPath in $targetPaths) {
            if (Test-TextContainsPath -Text ([string]$process.executable_path) -Path $targetPath) {
                $matchedPaths += $targetPath
                $matchedFields += 'executable_path'
            }
            if (Test-TextContainsPath -Text ([string]$process.command_line) -Path $targetPath) {
                $matchedPaths += $targetPath
                $matchedFields += 'command_line'
            }
            foreach ($lockedPath in @($process.locked_paths)) {
                if (Test-TextContainsPath -Text ([string]$lockedPath) -Path $targetPath) {
                    $matchedPaths += $targetPath
                    $matchedFields += 'locked_paths'
                }
            }
        }

        $matchedPaths = @($matchedPaths | Select-Object -Unique)
        $matchedFields = @($matchedFields | Select-Object -Unique)
        if ($matchedPaths.Count -gt 0) {
            $locking += [pscustomobject]@{
                pid = [int]$process.pid
                process_name = [string]$process.process_name
                executable_path = [string]$process.executable_path
                matched_fields = @($matchedFields)
                matched_paths = @($matchedPaths)
            }
        }
    }

    return @($locking)
}

function Get-CodexUpdateLockPreflight {
    param(
        [Parameter(Mandatory = $true)]
        [pscustomobject]$GlobalNpmRootInfo,

        [switch]$AllowLockedUpdate
    )

    $runningOnWindows = ([System.Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT)
    $targets = Get-CodexPackageLockTargets -GlobalNpmRoot ([string]$GlobalNpmRootInfo.root_path)
    if (-not $runningOnWindows) {
        return [pscustomobject]@{
            platform = [string][System.Environment]::OSVersion.Platform
            checked = $false
            blocking_enabled = $false
            lock_risk = 'unknown'
            matched_processes = @()
            npm_global_root = if ($GlobalNpmRootInfo.root_path) { [string]$GlobalNpmRootInfo.root_path } else { '' }
            openai_codex_package_root = if ($targets.codex_package_root) { [string]$targets.codex_package_root } else { '' }
            leftover_staging_candidates = @($targets.staging_directories | ForEach-Object { [string]$_.path })
            recommended_action = 'manual_review'
            override_used = $AllowLockedUpdate.IsPresent
            allowed = $true
            process_inventory_source = ''
            process_inventory_error = ''
            checked_process_count = 0
            warnings = @('Windows lock preflight is only actionable on Windows.')
            errors = @()
        }
    }

    $inventory = Get-CodexUpdateProcessInventory
    $lockingProcesses = @()
    if ([string]::IsNullOrWhiteSpace([string]$inventory.error) -and @($inventory.processes).Count -gt 0) {
        $lockingProcesses = @(Find-CodexPackageLockingProcesses -Processes @($inventory.processes) -Targets $targets)
    }

    $errors = @()
    $warnings = @()
    if (-not [string]::IsNullOrWhiteSpace([string]$inventory.error)) {
        $warnings += "Process inventory unavailable: $($inventory.error)"
    }
    if ([string]$GlobalNpmRootInfo.status -ne 'ok') {
        $warnings += 'Unable to resolve `npm root -g`; Codex update lock preflight could not inspect the official @openai/codex tree.'
    }
    $lockRisk = 'clear'
    if (-not [string]::IsNullOrWhiteSpace([string]$inventory.error) -or [string]$GlobalNpmRootInfo.status -ne 'ok') {
        $lockRisk = 'unknown'
    }
    if ($lockingProcesses.Count -gt 0) {
        $lockRisk = 'detected'
    }

    $blockingEnabled = -not $AllowLockedUpdate.IsPresent
    $recommendedAction = switch ($lockRisk) {
        'detected' { 'close_codex_sessions_then_rerun' }
        'clear' { 'safe_to_update' }
        default { 'manual_review' }
    }

    if ($lockRisk -eq 'detected' -and $blockingEnabled) {
        $errors += 'Windows Codex lock preflight detected likely active Codex or Node processes that can hold @openai/codex or @openai/.codex-* files. Close those sessions and rerun, or use -AllowLockedCodexUpdate to override.'
    } elseif ($lockRisk -eq 'unknown' -and $blockingEnabled) {
        $errors += 'Windows Codex lock preflight could not complete safely. Review process and npm-root evidence, then rerun or use -AllowLockedCodexUpdate to override.'
    }

    $matchedProcesses = @($lockingProcesses | Select-Object -First 20 | ForEach-Object {
        [pscustomobject]@{
            pid = [int]$_.pid
            name = [string]$_.process_name
            path = [string]$_.executable_path
            match_reason = ('matched {0} under Codex npm package/staging tree' -f ((@($_.matched_fields) | Select-Object -Unique) -join ','))
            matched_paths = @($_.matched_paths)
        }
    })

    return [pscustomobject]@{
        platform = 'Win32NT'
        checked = $true
        blocking_enabled = $blockingEnabled
        lock_risk = $lockRisk
        matched_processes = @($matchedProcesses)
        npm_global_root = if ($GlobalNpmRootInfo.root_path) { [string]$GlobalNpmRootInfo.root_path } else { '' }
        openai_codex_package_root = if ($targets.codex_package_root) { [string]$targets.codex_package_root } else { '' }
        leftover_staging_candidates = @($targets.staging_directories | ForEach-Object { [string]$_.path })
        recommended_action = $recommendedAction
        override_used = $AllowLockedUpdate.IsPresent
        allowed = ($errors.Count -eq 0)
        global_npm_root = $GlobalNpmRootInfo.root_path
        global_npm_root_status = $GlobalNpmRootInfo.status
        openai_scope_root = $targets.openai_scope_root
        codex_package_root = $targets.codex_package_root
        staging_directories = @($targets.staging_directories)
        process_inventory_source = $inventory.source
        process_inventory_error = $inventory.error
        checked_process_count = @($inventory.processes).Count
        locking_processes = @($lockingProcesses)
        detected = ($lockRisk -eq 'detected')
        allow_locked_update = $AllowLockedUpdate.IsPresent
        warnings = @($warnings)
        errors = @($errors)
    }
}

function Get-OfficialUpdateCleanupWarnings {
    param(
        [AllowNull()]
        [pscustomobject]$OfficialUpdateResult
    )

    if ($null -eq $OfficialUpdateResult -or [int]$OfficialUpdateResult.exit_code -ne 0) {
        return @()
    }

    $outputText = (@($OfficialUpdateResult.output) | ForEach-Object { [string]$_ }) -join [Environment]::NewLine
    if ([string]::IsNullOrWhiteSpace($outputText)) {
        return @()
    }

    $lower = $outputText.ToLowerInvariant()
    $isWindowsFileLockCleanupWarning = $lower.Contains('cleanup') -and $lower.Contains('eperm') -and $lower.Contains('unlink') -and $lower.Contains('codex.exe')
    if (-not $isWindowsFileLockCleanupWarning) {
        return @()
    }

    $evidenceLines = @(@($OfficialUpdateResult.output) | ForEach-Object { [string]$_ } | Where-Object {
        $line = $_.ToLowerInvariant()
        $line.Contains('cleanup') -or $line.Contains('eperm') -or $line.Contains('unlink') -or $line.Contains('codex.exe')
    } | Select-Object -First 12)

    return @(
        [pscustomobject]@{
            type = 'windows_file_lock_eperm'
            severity = 'warning'
            message = 'npm install exited 0 but reported cleanup EPERM unlink warnings for codex.exe, consistent with a Windows file lock on the previous Codex binary.'
            evidence = @($evidenceLines)
        }
    )
}

function Resolve-OfficialOmxInstallRoot {
    param([string]$ExplicitRoot)

    if (-not [string]::IsNullOrWhiteSpace($ExplicitRoot)) {
        return Resolve-ExistingPathOrLiteral -Path $ExplicitRoot
    }

    $npmPath = Get-FirstCommandPath -Candidates @('npm.cmd', 'npm')
    if ($npmPath) {
        try {
            $npmRootResult = Invoke-ExternalCommand -FilePath $npmPath -Arguments @('root', '-g') -IgnoreExitCode
            if ($npmRootResult.exit_code -eq 0) {
                $npmRoot = ($npmRootResult.output | Select-Object -First 1).Trim()
                if (-not [string]::IsNullOrWhiteSpace($npmRoot)) {
                    return Resolve-ExistingPathOrLiteral -Path (Join-Path $npmRoot 'oh-my-codex')
                }
            }
        } catch {
            # Fall through to the conventional APPDATA-based path.
        }
    }

    $appData = if (-not [string]::IsNullOrWhiteSpace($env:APPDATA)) { $env:APPDATA } else { Join-Path $HOME 'AppData\Roaming' }
    return Resolve-ExistingPathOrLiteral -Path (Join-Path $appData 'npm\node_modules\oh-my-codex')
}

function Get-PowerShellHostPath {
    $pwshPath = Get-FirstCommandPath -Candidates @('pwsh.exe', 'pwsh', 'powershell.exe', 'powershell')
    if ($pwshPath) {
        return $pwshPath
    }

    throw 'PowerShell host executable was not found in PATH.'
}

function Get-PatchCatalog {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRootPath,

        [Parameter(Mandatory = $true)]
        [string]$OfficialRoot,

        [Parameter(Mandatory = $true)]
        [string]$CodexHomePath
    )

    $toolsRoot = Join-Path $RepoRootPath 'tools'
    $runtimePath = Join-Path $OfficialRoot 'dist\team\runtime.js'
    $controllerPath = Join-Path $OfficialRoot 'dist\team\windows-worker-controller.js'
    $bootstrapPath = Join-Path $OfficialRoot 'dist\team\worker-bootstrap.js'
    $workerSkillPath = Join-Path $CodexHomePath 'skills\worker\SKILL.md'

    return @(
        [pscustomobject]@{ name = 'runtime-observability'; scope = 'official_install'; category = 'runtime.js'; target_path = $runtimePath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-prompt-controller-observability-fix.mjs'); suggested_home = 'official_install_runtime'; suggested_decision = 'replay_or_rebase'; decision_reason = 'Runtime launch/observability semantics must be fixed inside the installed team engine until upstream absorbs them.' }
        [pscustomobject]@{ name = 'runtime-detach'; scope = 'official_install'; category = 'runtime.js'; target_path = $runtimePath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-prompt-controller-detach-fix.mjs'); suggested_home = 'official_install_runtime'; suggested_decision = 'replay_or_rebase'; decision_reason = 'Detach and teardown behavior is runtime-owned and cannot be repaired later by a wrapper.' }
        [pscustomobject]@{ name = 'runtime-prompt-shutdown'; scope = 'official_install'; category = 'runtime.js'; target_path = $runtimePath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-prompt-runtime-shutdown-fix.mjs'); suggested_home = 'official_install_runtime'; suggested_decision = 'replay_or_rebase'; decision_reason = 'Prompt-controller shutdown must terminate both controller and active exec child PIDs before wrappers can report a real durable-team lifecycle.' }
        [pscustomobject]@{ name = 'runtime-startup-evidence'; scope = 'official_install'; category = 'runtime.js'; target_path = $runtimePath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-prompt-startup-evidence-fix.mjs'); suggested_home = 'official_install_runtime'; suggested_decision = 'replay_or_rebase'; decision_reason = 'Startup readiness/evidence handling affects worker launch correctness before user-level wrappers can help.' }
        [pscustomobject]@{ name = 'runtime-writable-roots'; scope = 'official_install'; category = 'runtime.js'; target_path = $runtimePath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-worktree-writable-roots-fix.mjs'); suggested_home = 'official_install_runtime'; suggested_decision = 'replay_or_rebase'; decision_reason = 'Writable-root fixes affect sandbox/worktree access during launch and integration, so they still belong in the runtime until upstream provides the behavior.' }
        [pscustomobject]@{ name = 'controller-debug-root'; scope = 'official_install'; category = 'windows-worker-controller.js'; target_path = $controllerPath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-prompt-controller-debug-root-fix.mjs'); suggested_home = 'official_install_runtime'; suggested_decision = 'replay_or_rebase'; decision_reason = 'Controller-side debug-root wiring is needed during prompt-worker bootstrap and is not a wrapper-only concern.' }
        [pscustomobject]@{ name = 'controller-startup-status'; scope = 'official_install'; category = 'windows-worker-controller.js'; target_path = $controllerPath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-prompt-controller-startup-status-fix.mjs'); suggested_home = 'official_install_runtime'; suggested_decision = 'replay_or_rebase'; decision_reason = 'Status seeding is emitted by the controller while the worker starts and therefore still belongs in the installed runtime path.' }
        [pscustomobject]@{ name = 'controller-stdin-close'; scope = 'official_install'; category = 'windows-worker-controller.js'; target_path = $controllerPath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-prompt-controller-stdin-close-fix.mjs'); suggested_home = 'official_install_runtime'; suggested_decision = 'replay_or_rebase'; decision_reason = 'STDIN close behavior is owned by the controller process and must be fixed before the worker loop begins.' }
        [pscustomobject]@{ name = 'controller-prompt-shutdown'; scope = 'official_install'; category = 'windows-worker-controller.js'; target_path = $controllerPath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-prompt-controller-shutdown-fix.mjs'); suggested_home = 'official_install_runtime'; suggested_decision = 'replay_or_rebase'; decision_reason = 'The Windows prompt controller must persist active exec child PID evidence and handle shutdown signals for reliable team teardown; apply before controller-exec-status because it owns child PID helper insertion.' }
        [pscustomobject]@{ name = 'controller-exec-status'; scope = 'official_install'; category = 'windows-worker-controller.js'; target_path = $controllerPath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-prompt-controller-exec-status-fix.mjs'); suggested_home = 'official_install_runtime'; suggested_decision = 'replay_or_rebase'; decision_reason = 'The Windows prompt controller must demote worker status when the real codex exec child exits non-zero so failed child auth cannot remain as false working state.' }
        [pscustomobject]@{ name = 'controller-stdin-prompt'; scope = 'official_install'; category = 'windows-worker-controller.js'; target_path = $controllerPath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-prompt-controller-stdin-prompt-fix.mjs'); suggested_home = 'official_install_runtime'; suggested_decision = 'replay_or_rebase'; decision_reason = 'Prompt-read behavior on Windows is controller/runtime logic, not merely documentation.' }
        [pscustomobject]@{ name = 'bootstrap-oneliner'; scope = 'official_install'; category = 'worker-bootstrap.js'; target_path = $bootstrapPath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-worker-bootstrap-oneliner-fix.mjs'); suggested_home = 'worker_bootstrap_move_down_when_possible'; suggested_decision = 'move_down_if_hook_exists_else_replay'; decision_reason = 'Worker-visible examples should move into wrappers/skills when possible, but still need replay while upstream bootstrap emits unsafe Windows examples.' }
        [pscustomobject]@{ name = 'bootstrap-command-style'; scope = 'official_install'; category = 'worker-bootstrap.js'; target_path = $bootstrapPath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-command-style-guidance-fix.mjs'); suggested_home = 'worker_bootstrap_move_down_when_possible'; suggested_decision = 'move_down_if_hook_exists_else_replay'; decision_reason = 'This is worker-visible command guidance and should be pushed downward once a stable prompt hook exists.' }
        [pscustomobject]@{ name = 'bootstrap-mailbox-example'; scope = 'official_install'; category = 'worker-bootstrap.js'; target_path = $bootstrapPath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-worker-bootstrap-mailbox-example-fix.mjs'); suggested_home = 'worker_bootstrap_move_down_when_possible'; suggested_decision = 'move_down_if_hook_exists_else_replay'; decision_reason = 'Mailbox examples are guidance-layer concerns, but still require replay if upstream bootstrap keeps emitting unsafe forms.' }
        [pscustomobject]@{ name = 'bootstrap-wrapper-guidance'; scope = 'official_install'; category = 'worker-bootstrap.js'; target_path = $bootstrapPath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-worker-wrapper-guidance-fix.mjs'); suggested_home = 'worker_bootstrap_move_down_when_possible'; suggested_decision = 'move_down_if_hook_exists_else_replay'; decision_reason = 'Wrapper-first guidance should ideally live in local prompt assets, but remains an upstream replay target until the bootstrap surface is externally overrideable.' }
        [pscustomobject]@{ name = 'bootstrap-lifecycle-wrapper-guidance'; scope = 'official_install'; category = 'worker-bootstrap.js'; target_path = $bootstrapPath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-lifecycle-wrapper-guidance-fix.mjs'); suggested_home = 'worker_bootstrap_move_down_when_possible'; suggested_decision = 'move_down_if_hook_exists_else_replay'; decision_reason = 'Lifecycle closure examples belong in wrappers/skills long-term, but still need replay if the upstream bootstrap keeps sending raw/unsafe completion guidance.' }
        [pscustomobject]@{ name = 'bootstrap-wrapper-only'; scope = 'official_install'; category = 'worker-bootstrap.js'; target_path = $bootstrapPath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-worker-visible-wrapper-only-fix.mjs'); suggested_home = 'worker_bootstrap_move_down_when_possible'; suggested_decision = 'move_down_if_hook_exists_else_replay'; decision_reason = 'Windows-visible wrapper-only guidance is a move-down candidate, but replay remains necessary until upstream bootstraps are safe on their own.' }
        [pscustomobject]@{ name = 'bootstrap-wrapper-only-guidance'; scope = 'official_install'; category = 'worker-bootstrap.js'; target_path = $bootstrapPath; script_path = (Join-Path $toolsRoot 'openclaw-omx-windows-worker-wrapper-only-guidance-fix.mjs'); suggested_home = 'worker_bootstrap_move_down_when_possible'; suggested_decision = 'move_down_if_hook_exists_else_replay'; decision_reason = 'The goal is wrapper-first worker guidance, with replay retained only as long as the upstream bootstrap remains the source of emitted instructions.' }
        [pscustomobject]@{ name = 'bootstrap-raw-abstraction'; scope = 'official_install'; category = 'worker-bootstrap.js'; target_path = $bootstrapPath; script_path = (Join-Path $toolsRoot 'openclaw-omx-worker-visible-raw-abstraction-fix.mjs'); suggested_home = 'worker_bootstrap_move_down_when_possible'; suggested_decision = 'move_down_if_hook_exists_else_replay'; decision_reason = 'Raw-abstraction is documentation/guidance shaping and should be pushed downward when the installed bootstrap can be safely overridden.' }
        [pscustomobject]@{ name = 'worker-skill-powershell-oneliner'; scope = 'user_level_surface'; category = 'worker-skill'; target_path = $workerSkillPath; script_path = (Join-Path $toolsRoot 'openclaw-omx-worker-skill-powershell-oneliner-fix.mjs'); suggested_home = 'user_level_surface'; suggested_decision = 'keep_local_move_down'; decision_reason = 'Worker-skill examples are already a local user-level surface and should stay out of the official npm install.' }
    )
}

function Get-TrackedWrapperPaths {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CodexHomePath
    )

    $binRoot = Join-Path $CodexHomePath 'bin'
    return @(
        (Join-Path $binRoot 'omx-team-send-message.ps1')
        (Join-Path $binRoot 'omx-team-mailbox-list.ps1')
        (Join-Path $binRoot 'omx-team-mailbox-mark-delivered.ps1')
        (Join-Path $binRoot 'omx-team-claim-task.ps1')
        (Join-Path $binRoot 'omx-team-transition-task-status.ps1')
        (Join-Path $binRoot 'omx-team-release-task-claim.ps1')
        (Join-Path $binRoot 'omx-team-report-progress.ps1')
        (Join-Path $binRoot 'omx-team-complete-task.ps1')
        (Join-Path $binRoot 'omx-team-fail-task.ps1')
    )
}

function Get-FilePresenceSummary {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Paths
    )

    return @(
        foreach ($path in $Paths) {
            [pscustomobject]@{
                path = $path
                exists = (Test-Path -LiteralPath $path)
            }
        }
    )
}

function Copy-FileToSnapshot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourcePath,

        [Parameter(Mandatory = $true)]
        [string]$SnapshotBasePath,

        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    if (-not (Test-Path -LiteralPath $SourcePath)) {
        return $null
    }

    $targetRoot = Join-Path $SnapshotBasePath $Label
    Ensure-Directory -Path $targetRoot
    $targetPath = Join-Path $targetRoot ([System.IO.Path]::GetFileName($SourcePath))
    Copy-Item -LiteralPath $SourcePath -Destination $targetPath -Force
    return $targetPath
}

function Get-MarkerInventory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$OfficialRoot
    )

    $teamRoot = Join-Path $OfficialRoot 'dist\team'
    if (-not (Test-Path -LiteralPath $teamRoot)) {
        return @()
    }

    $matches = Get-ChildItem -LiteralPath $teamRoot -File -Recurse | Select-String -Pattern 'OPENCLAW_' -SimpleMatch
    return @(
        foreach ($match in $matches) {
            [pscustomobject]@{
                path = $match.Path
                line_number = $match.LineNumber
                line = [string]$match.Line
            }
        }
    )
}

function Invoke-PatchScript {
    param(
        [Parameter(Mandatory = $true)]
        [string]$NodePath,

        [Parameter(Mandatory = $true)]
        [pscustomobject]$Patch,

        [Parameter(Mandatory = $true)]
        [ValidateSet('status', 'apply')]
        [string]$Action,

        [Parameter(Mandatory = $true)]
        [string]$SnapshotBasePath
    )

    $backupDir = Join-Path $SnapshotBasePath (Join-Path 'patch-backups' $Patch.name)
    Ensure-Directory -Path $backupDir

    if (-not (Test-Path -LiteralPath $Patch.script_path)) {
        return [pscustomobject]@{
            patch = $Patch.name
            scope = $Patch.scope
            category = $Patch.category
            action = $Action
            ok = $false
            status = 'script_missing'
            script_path = $Patch.script_path
            target_path = $Patch.target_path
            backup_dir = $backupDir
        }
    }

    $result = Invoke-ExternalCommand -FilePath $NodePath -Arguments @(
        $Patch.script_path
        $Action
        '--target'
        $Patch.target_path
        '--backup-dir'
        $backupDir
        '--json'
    ) -IgnoreExitCode

    $parsed = $null
    $joinedOutput = ($result.output -join [Environment]::NewLine).Trim()
    if (-not [string]::IsNullOrWhiteSpace($joinedOutput)) {
        try {
            $parsed = $joinedOutput | ConvertFrom-Json
        } catch {
            $parsed = [pscustomobject]@{
                ok = ($result.exit_code -eq 0)
                status = 'non_json_output'
                raw_output = @($result.output)
            }
        }
    } else {
        $parsed = [pscustomobject]@{
            ok = ($result.exit_code -eq 0)
            status = if ($result.exit_code -eq 0) { 'silent_success_no_output' } else { 'silent_failure_no_output' }
            raw_output = @($result.output)
        }
    }

    $ordered = [ordered]@{
        patch = $Patch.name
        scope = $Patch.scope
        category = $Patch.category
        action = $Action
        script_path = $Patch.script_path
        target_path = $Patch.target_path
        backup_dir = $backupDir
        command_exit_code = $result.exit_code
        command_output = @($result.output)
    }

    foreach ($property in $parsed.PSObject.Properties) {
        $ordered[$property.Name] = $property.Value
    }

    return [pscustomobject]$ordered
}

function Write-ChecklistMarkdown {
    param(
        [Parameter(Mandatory = $true)]
        [pscustomobject]$Report,

        [Parameter(Mandatory = $true)]
        [string]$OutputPath
    )

    $officialStatuses = @($Report.patch_status_before | Where-Object { $_.scope -eq 'official_install' })
    $localStatuses = @($Report.patch_status_before | Where-Object { $_.scope -eq 'user_level_surface' })

    $lines = New-Object System.Collections.Generic.List[string]
    $null = $lines.Add('# Official update + diff check + local patch replay checklist')
    $null = $lines.Add('')
    $null = $lines.Add("Generated at: $($Report.generated_at)")
    $null = $lines.Add("Stage: $($Report.stage.stage)")
    $null = $lines.Add("Stage description: $($Report.stage.stage_description)")
    $null = $lines.Add("Repo root: $($Report.repo_root)")
    $null = $lines.Add("Official oh-my-codex root: $($Report.official_omx_root)")
    $null = $lines.Add("Codex home: $($Report.codex_home)")
    $null = $lines.Add("Snapshot root: $($Report.snapshot_root)")
    $null = $lines.Add("Patch decision table: $($Report.patch_decision_table_path)")
    $null = $lines.Add('')
    if ($null -ne $Report.stage_gate) {
        $null = $lines.Add('## Stage gate')
        $null = $lines.Add(('- allowed: `{0}`' -f $Report.stage_gate.allowed))
        $completedStagesRendered = (@($Report.stage_gate.completed_stages) -join ', ')
        $null = $lines.Add(('- completed_stages_seen: `{0}`' -f $completedStagesRendered))
        $null = $lines.Add(('- diff_review_approved: `{0}`' -f $Report.stage_gate.diff_review_approved))
        foreach ($warning in @($Report.stage_gate.warnings)) {
            $null = $lines.Add(('- warning: {0}' -f $warning))
        }
        foreach ($error in @($Report.stage_gate.errors)) {
            $null = $lines.Add(('- error: {0}' -f $error))
        }
        $null = $lines.Add('')
    }
    $null = $lines.Add('## 1. Pre-update')
    $null = $lines.Add('- [ ] Record global `oh-my-codex` / `@openai/codex` versions from `environment.global_npm_listing`.')
    $null = $lines.Add('- [ ] Confirm `environment.node_path`, `environment.npm_path`, and `environment.omx_path` are available.')
    $null = $lines.Add('- [ ] Review `windows_codex_lock_preflight` before running the official update.')
    $null = $lines.Add('- [ ] If `windows_codex_lock_preflight.leftover_staging_candidates` is not empty, quit active Codex/Node/npm shells first; cleanup is manual only.')
    $null = $lines.Add('- [ ] Review the `marker_inventory_before` section for current `OPENCLAW_` residues.')
    $null = $lines.Add('- [ ] Confirm the wrapper presence section below is healthy before starting the official update.')
    if ($null -ne $Report.windows_codex_lock_preflight) {
        $null = $lines.Add(('- windows_codex_lock_preflight.lock_risk: `{0}`' -f $Report.windows_codex_lock_preflight.lock_risk))
        $null = $lines.Add(('- windows_codex_lock_preflight.recommended_action: `{0}`' -f $Report.windows_codex_lock_preflight.recommended_action))
        $leftoverCount = @($Report.windows_codex_lock_preflight.leftover_staging_candidates).Count
        $null = $lines.Add(('- windows_codex_lock_preflight.leftover_staging_candidates: `{0}`' -f $leftoverCount))
    }
    $null = $lines.Add('')
    $null = $lines.Add('## 2. Update')
    $null = $lines.Add('- [ ] Run the official update path: `npm install -g @openai/codex oh-my-codex`.')
    $null = $lines.Add('- [ ] If `official_update_cleanup_warnings` reports `windows_file_lock_eperm` with exit code 0, the update likely succeeded but npm cleanup was blocked by a Windows file lock.')
    $null = $lines.Add('- [ ] Run `omx setup` and, if needed, `omx update`.')
    $null = $lines.Add('- [ ] Do not start a new durable team during the mixed old/new window.')
    $null = $lines.Add('')
    $null = $lines.Add('## 3. Diff check')
    $null = $lines.Add('- [ ] Compare the current `runtime.js`, `windows-worker-controller.js`, and `worker-bootstrap.js` with the pre-update snapshots.')
    $null = $lines.Add('- [ ] For each patch below, classify it as `drop`, `move-down`, `rebase`, or `replay`.')
    $null = $lines.Add('- [ ] After reviewing the decision table, approve the diff with `.\tools\codex-official-update-patch-replay-template.ps1 -Stage diff -ApproveDiff -SnapshotRoot <snapshot-root>`.')
    if ($null -ne $Report.approvals -and $null -ne $Report.approvals.diff_review) {
        $null = $lines.Add(('- diff_review.approved: `{0}`' -f $Report.approvals.diff_review.approved))
        $null = $lines.Add(('- diff_review.approved_at: `{0}`' -f $Report.approvals.diff_review.approved_at))
        $null = $lines.Add(('- diff_review.approval_note: {0}' -f $Report.approvals.diff_review.approval_note))
    }
    $null = $lines.Add('')
    $null = $lines.Add('### Official-install patch status before update')
    if ($officialStatuses.Count -eq 0) {
        $null = $lines.Add('- (none)')
    } else {
        foreach ($entry in $officialStatuses) {
            $entryStatus = Normalize-DecisionValue -Value (Get-ObjectPropertyValue -InputObject $entry -PropertyName 'status')
            $entryExitCode = Normalize-DecisionValue -Value (Get-ObjectPropertyValue -InputObject $entry -PropertyName 'command_exit_code')
            $null = $lines.Add(('- [ ] {0} (`{1}`) status=`{2}` exit=`{3}` target=`{4}`' -f $entry.patch, $entry.category, $entryStatus, $entryExitCode, $entry.target_path))
        }
    }
    $null = $lines.Add('')
    $null = $lines.Add('### Local-surface patch status before update')
    if ($localStatuses.Count -eq 0) {
        $null = $lines.Add('- (none)')
    } else {
        foreach ($entry in $localStatuses) {
            $entryStatus = Normalize-DecisionValue -Value (Get-ObjectPropertyValue -InputObject $entry -PropertyName 'status')
            $entryExitCode = Normalize-DecisionValue -Value (Get-ObjectPropertyValue -InputObject $entry -PropertyName 'command_exit_code')
            $null = $lines.Add(('- [ ] {0} (`{1}`) status=`{2}` exit=`{3}` target=`{4}`' -f $entry.patch, $entry.category, $entryStatus, $entryExitCode, $entry.target_path))
        }
    }
    $null = $lines.Add('')
    $null = $lines.Add('## 4. Replay')
    $null = $lines.Add('- [ ] Replay required official-install patches only after `precheck`, `diff`, and explicit `approvals.diff_review.approved = true` are present in `checkpoint.json`.')
    $null = $lines.Add('- [ ] Regenerate the user-level wrapper layer via `tools/install-codex-user-level-team-mode.ps1`.')
    $null = $lines.Add('- [ ] Run `test/install-codex-user-level-team-mode.test.ps1`.')
    $null = $lines.Add('- [ ] Run a focused Windows durable-worker smoke test and verify task convergence to `completed`.')
    $null = $lines.Add('')
    $null = $lines.Add('## Wrapper presence')
    foreach ($wrapper in @($Report.wrapper_presence_before)) {
        $mark = if ($wrapper.exists) { 'x' } else { ' ' }
        $null = $lines.Add(('- [{0}] {1}' -f $mark, $wrapper.path))
    }

    Set-Content -LiteralPath $OutputPath -Encoding UTF8 -Value $lines
}

function Write-PatchDecisionTableMarkdown {
    param(
        [Parameter(Mandatory = $true)]
        [pscustomobject]$Report,

        [Parameter(Mandatory = $true)]
        [object[]]$Rows,

        [Parameter(Mandatory = $true)]
        [string]$OutputPath
    )

    $lines = New-Object System.Collections.Generic.List[string]
    $null = $lines.Add('# Patch decision table')
    $null = $lines.Add('')
    $null = $lines.Add("Generated at: $($Report.generated_at)")
    $null = $lines.Add("Stage: $($Report.stage.stage)")
    $null = $lines.Add("Stage description: $($Report.stage.stage_description)")
    $null = $lines.Add("Report: $($Report.report_json_path)")
    $null = $lines.Add('')
    $null = $lines.Add('Use this table after an official update to classify every patch as one of:')
    $null = $lines.Add('')
    $null = $lines.Add('- `drop`')
    $null = $lines.Add('- `move-down`')
    $null = $lines.Add('- `rebase`')
    $null = $lines.Add('- `replay`')
    $null = $lines.Add('')
    $null = $lines.Add('Suggested-decision values are hints only. Final decision should be recorded explicitly below.')
    $null = $lines.Add('')

    foreach ($row in @($Rows)) {
        $null = $lines.Add(("## {0}" -f $row.patch))
        $null = $lines.Add('')
        $null = $lines.Add(('- scope: `{0}`' -f $row.scope))
        $null = $lines.Add(('- category: `{0}`' -f $row.category))
        $null = $lines.Add(('- target: `{0}`' -f $row.target_path))
        $null = $lines.Add(('- script: `{0}`' -f $row.script_path))
        $null = $lines.Add(('- suggested_home: `{0}`' -f $row.suggested_home))
        $null = $lines.Add(('- suggested_decision: `{0}`' -f $row.suggested_decision))
        $null = $lines.Add(('- suggested_reason: {0}' -f $row.suggested_reason))
        $null = $lines.Add(('- auto_suggested_final_decision: `{0}`' -f $row.auto_suggested_final_decision))
        $null = $lines.Add(('- auto_suggestion_reason: {0}' -f $row.auto_suggestion_reason))
        if (-not [string]::IsNullOrWhiteSpace([string]$row.current_status)) {
            $null = $lines.Add(('- current_status: `{0}`' -f $row.current_status))
            $null = $lines.Add(('- last_exit_code: `{0}`' -f $row.last_exit_code))
        } else {
            $null = $lines.Add('- current_status: `(not captured)`')
            $null = $lines.Add('- last_exit_code: `(not captured)`')
        }
        $null = $lines.Add(('- decision_status: `{0}`' -f $row.decision_status))
        $null = $lines.Add(('- decision_locked: `{0}`' -f $row.decision_locked))
        $null = $lines.Add(('- decision_lock_reason: {0}' -f ($(if ([string]::IsNullOrWhiteSpace([string]$row.decision_lock_reason)) { '______' } else { [string]$row.decision_lock_reason }))))
        $null = $lines.Add(('- final_decision: `{0}`' -f $row.final_decision))
        $null = $lines.Add(('- decision_reason: {0}' -f $row.decision_reason))
        $null = $lines.Add(('- follow_up_action: `{0}`' -f ($(if ([string]::IsNullOrWhiteSpace([string]$row.follow_up_action)) { '______' } else { [string]$row.follow_up_action }))))
        $null = $lines.Add(('- manual_override_if_needed: `{0}`' -f ($(if ([string]::IsNullOrWhiteSpace([string]$row.manual_override_if_needed)) { '______' } else { [string]$row.manual_override_if_needed }))))
        $null = $lines.Add('')
    }

    Set-Content -LiteralPath $OutputPath -Encoding UTF8 -Value $lines
}

function Resolve-AutoSuggestedFinalDecision {
    param(
        [Parameter(Mandatory = $true)]
        [pscustomobject]$Patch,

        [pscustomobject]$Status
    )

    $commandExitCode = Get-ObjectPropertyValue -InputObject $Status -PropertyName 'command_exit_code'
    if ($null -ne $Status -and $null -ne $commandExitCode -and [int]$commandExitCode -ne 0) {
        return [pscustomobject]@{
            final_decision = 'rebase'
            reason = 'The patch probe did not cleanly succeed against the current target, so the local patch most likely needs retargeting before replay.'
        }
    }

    if ($Patch.scope -eq 'user_level_surface') {
        return [pscustomobject]@{
            final_decision = 'move-down'
            reason = 'This patch belongs on the local user-level surface and should stay out of the official npm install.'
        }
    }

    switch ([string]$Patch.category) {
        'runtime.js' {
            return [pscustomobject]@{
                final_decision = 'replay'
                reason = 'This patch affects installed runtime semantics such as launch, detach, readiness, or writable-root handling, so replay remains the default unless upstream has clearly absorbed it.'
            }
        }
        'windows-worker-controller.js' {
            return [pscustomobject]@{
                final_decision = 'replay'
                reason = 'This patch affects controller-side Windows worker startup or IO behavior, so replay remains the default unless upstream has clearly absorbed it.'
            }
        }
        'worker-bootstrap.js' {
            return [pscustomobject]@{
                final_decision = 'replay'
                reason = 'Long-term these instructions should move down into wrappers or prompt assets, but while upstream bootstrap still emits the worker-visible guidance directly, replay remains the operational default.'
            }
        }
        default {
            return [pscustomobject]@{
                final_decision = 'replay'
                reason = 'No more specific rule matched, so replay is the conservative default until a deliberate diff decision is recorded.'
            }
        }
    }
}

function Normalize-DecisionValue {
    param(
        [AllowNull()]
        [object]$Value
    )

    $text = [string]$Value
    if ([string]::IsNullOrWhiteSpace($text)) {
        return ''
    }

    $trimmed = $text.Trim()
    if ($trimmed -eq '______') {
        return ''
    }

    return $trimmed
}

function Normalize-PatchDecisionRows {
    param(
        [AllowNull()]
        [object]$Rows
    )

    $normalized = @()
    foreach ($row in @($Rows)) {
        if ($null -eq $row) {
            continue
        }

        $rowPatch = Get-ObjectPropertyValue -InputObject $row -PropertyName 'patch'
        $rowValue = Get-ObjectPropertyValue -InputObject $row -PropertyName 'value'
        $rowCount = Get-ObjectPropertyValue -InputObject $row -PropertyName 'Count'
        if ($null -eq $rowPatch -and $null -ne $rowValue -and $null -ne $rowCount) {
            foreach ($innerRow in @($rowValue)) {
                if ($null -ne $innerRow) {
                    $normalized += $innerRow
                }
            }
        } else {
            $normalized += $row
        }
    }

    return @($normalized)
}

function Get-PatchDecisionRows {
    param(
        [Parameter(Mandatory = $true)]
        [pscustomobject]$Report,

        [AllowNull()]
        [object[]]$PreviousRows = @()
    )

    $statusLookup = @{}
    foreach ($entry in @($Report.patch_status_after_update)) {
        $statusLookup[[string]$entry.patch] = $entry
    }
    foreach ($entry in @($Report.patch_status_before)) {
        if (-not $statusLookup.ContainsKey([string]$entry.patch)) {
            $statusLookup[[string]$entry.patch] = $entry
        }
    }

    $previousLookup = @{}
    foreach ($row in @($PreviousRows)) {
        $patchName = Normalize-DecisionValue -Value $row.patch
        if (-not [string]::IsNullOrWhiteSpace($patchName)) {
            $previousLookup[$patchName] = $row
        }
    }

    $rows = @()
    foreach ($patch in @($Report.patch_catalog | Sort-Object scope, category, name)) {
        $status = $null
        if ($statusLookup.ContainsKey([string]$patch.name)) {
            $status = $statusLookup[[string]$patch.name]
        }
        $autoDecision = Resolve-AutoSuggestedFinalDecision -Patch $patch -Status $status
        $previousRow = $null
        if ($previousLookup.ContainsKey([string]$patch.name)) {
            $previousRow = $previousLookup[[string]$patch.name]
        }

        $decisionStatus = 'auto_prefilled'
        $finalDecision = $autoDecision.final_decision
        $decisionReason = $autoDecision.reason
        $followUpAction = ''
        $manualOverride = ''
        $decisionLocked = $false
        $decisionLockReason = ''

        if ($null -ne $previousRow) {
            $previousStatus = Normalize-DecisionValue -Value (Get-ObjectPropertyValue -InputObject $previousRow -PropertyName 'decision_status')
            $previousFinal = Normalize-DecisionValue -Value (Get-ObjectPropertyValue -InputObject $previousRow -PropertyName 'final_decision')
            $previousReason = Normalize-DecisionValue -Value (Get-ObjectPropertyValue -InputObject $previousRow -PropertyName 'decision_reason')
            $previousFollowUp = Normalize-DecisionValue -Value (Get-ObjectPropertyValue -InputObject $previousRow -PropertyName 'follow_up_action')
            $previousManualOverride = Normalize-DecisionValue -Value (Get-ObjectPropertyValue -InputObject $previousRow -PropertyName 'manual_override_if_needed')
            $previousDecisionLocked = Test-TruthyValue -Value (Get-ObjectPropertyValue -InputObject $previousRow -PropertyName 'decision_locked')
            $previousDecisionLockReason = Normalize-DecisionValue -Value (Get-ObjectPropertyValue -InputObject $previousRow -PropertyName 'decision_lock_reason')

            $followUpAction = $previousFollowUp
            $manualOverride = $previousManualOverride
            $decisionLocked = $previousDecisionLocked
            $decisionLockReason = $previousDecisionLockReason

            if ($previousDecisionLocked) {
                $decisionStatus = if (-not [string]::IsNullOrWhiteSpace($previousStatus)) { $previousStatus } else { 'manually_overridden' }
                $finalDecision = if (-not [string]::IsNullOrWhiteSpace($previousFinal)) { $previousFinal } else { 'unresolved' }
                $decisionReason = if (-not [string]::IsNullOrWhiteSpace($previousReason)) { $previousReason } else { 'Locked manual review decision preserved.' }
            } else {
                $isExplicitlyUnresolved = ($previousStatus -eq 'unresolved') -or ($previousFinal -eq 'unresolved')
                if ($isExplicitlyUnresolved) {
                    $decisionStatus = 'unresolved'
                    $finalDecision = if (-not [string]::IsNullOrWhiteSpace($previousFinal)) { $previousFinal } else { 'unresolved' }
                    $decisionReason = if (-not [string]::IsNullOrWhiteSpace($previousReason)) { $previousReason } else { 'Manual review still required.' }
                } else {
                    $manualChanged = $false
                    if (-not [string]::IsNullOrWhiteSpace($previousFinal) -and $previousFinal -ne $autoDecision.final_decision) {
                        $manualChanged = $true
                    }
                    if (-not [string]::IsNullOrWhiteSpace($previousReason) -and $previousReason -ne $autoDecision.reason) {
                        $manualChanged = $true
                    }
                    if (-not [string]::IsNullOrWhiteSpace($previousFollowUp)) {
                        $manualChanged = $true
                    }
                    if (-not [string]::IsNullOrWhiteSpace($previousManualOverride)) {
                        $manualChanged = $true
                    }
                    if ($previousStatus -eq 'manually_overridden') {
                        $manualChanged = $true
                    }

                    if ($manualChanged) {
                        $decisionStatus = 'manually_overridden'
                        if (-not [string]::IsNullOrWhiteSpace($previousFinal)) {
                            $finalDecision = $previousFinal
                        }
                        if (-not [string]::IsNullOrWhiteSpace($previousReason)) {
                            $decisionReason = $previousReason
                        }
                    }
                }
            }
        }

        $statusValue = Normalize-DecisionValue -Value (Get-ObjectPropertyValue -InputObject $status -PropertyName 'status')
        $statusExitCode = Normalize-DecisionValue -Value (Get-ObjectPropertyValue -InputObject $status -PropertyName 'command_exit_code')

        $rows += [pscustomobject][ordered]@{
            patch = $patch.name
            scope = $patch.scope
            category = $patch.category
            target_path = $patch.target_path
            script_path = $patch.script_path
            suggested_home = $patch.suggested_home
            suggested_decision = $patch.suggested_decision
            suggested_reason = $patch.decision_reason
            auto_suggested_final_decision = $autoDecision.final_decision
            auto_suggestion_reason = $autoDecision.reason
            current_status = $statusValue
            last_exit_code = $statusExitCode
            decision_status = $decisionStatus
            decision_locked = $decisionLocked
            decision_lock_reason = $decisionLockReason
            final_decision = $finalDecision
            decision_reason = $decisionReason
            follow_up_action = $followUpAction
            manual_override_if_needed = $manualOverride
        }
    }

    return @($rows)
}

$repoRootPath = Resolve-ExistingPathOrLiteral -Path $RepoRoot
$officialOmxRootPath = Resolve-OfficialOmxInstallRoot -ExplicitRoot $OfficialOmxRoot
$codexHomePath = Resolve-ExistingPathOrLiteral -Path $CodexHome
$stagePlan = Resolve-StagePlan -SelectedStage $Stage `
    -RequestedOfficialUpdate:$RunOfficialUpdate `
    -RequestedOmxSetup:$RunOmxSetup `
    -RequestedOmxUpdate:$RunOmxUpdate `
    -RequestedReplayOfficialInstallPatches:$ReplayOfficialInstallPatches `
    -RequestedReplayUserLevelSurfacePatches:$ReplayUserLevelSurfacePatches `
    -RequestedRegenerateUserLevelLayer:$RegenerateUserLevelLayer `
    -RequestedRunInstallerTests:$RunInstallerTests
if ($ApproveDiff -and $Stage -ne 'diff') {
    throw '-ApproveDiff is only supported with -Stage diff.'
}
$snapshotRootPlan = Resolve-SnapshotRootPlan -RepoRootPath $repoRootPath -SelectedStage $Stage -ExplicitSnapshotRoot $SnapshotRoot
$snapshotRootPath = $snapshotRootPlan.snapshot_root
$checkpointManifestBefore = if (Test-Path -LiteralPath $snapshotRootPath) { Read-CheckpointManifest -SnapshotRootPath $snapshotRootPath } else { $null }
$stageGate = Get-StageGateResult -StagePlan $stagePlan -SelectedStage $Stage -SnapshotRootPath $snapshotRootPath -CheckpointManifest $checkpointManifestBefore -SnapshotRootSource $snapshotRootPlan.source
foreach ($warningMessage in @($stageGate.warnings)) {
    Write-Warning $warningMessage
}
if (-not $stageGate.allowed) {
    throw ($stageGate.errors -join ' ')
}

Ensure-Directory -Path $snapshotRootPath
$previousReportPath = Join-Path $snapshotRootPath 'report.json'
$previousReport = Read-JsonFile -Path $previousReportPath
$existingDecisionRowsPath = Join-Path $snapshotRootPath 'patch-decision-table.json'
$existingDecisionRows = @()
$existingDecisionRowsRaw = Read-JsonFile -Path $existingDecisionRowsPath
if ($null -ne $existingDecisionRowsRaw) {
    $existingDecisionRows = @(Normalize-PatchDecisionRows -Rows $existingDecisionRowsRaw)
}

$nodePath = Get-FirstCommandPath -Candidates @('node.exe', 'node')
$npmPath = Get-FirstCommandPath -Candidates @('npm.cmd', 'npm')
$omxPath = Get-FirstCommandPath -Candidates @('omx.cmd', 'omx')
$powerShellPath = Get-PowerShellHostPath

$patchCatalog = Get-PatchCatalog -RepoRootPath $repoRootPath -OfficialRoot $officialOmxRootPath -CodexHomePath $codexHomePath
if ($PatchName.Count -gt 0) {
    $requestedPatchNames = @($PatchName | ForEach-Object { [string]$_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($requestedPatchNames.Count -eq 0) {
        throw 'PatchName must contain at least one non-empty patch name.'
    }
    $knownPatchNames = @($patchCatalog | ForEach-Object { [string]$_.name })
    $unknownPatchNames = @($requestedPatchNames | Where-Object { $_ -notin $knownPatchNames })
    if ($unknownPatchNames.Count -gt 0) {
        throw ("Unknown patch name(s): {0}" -f ($unknownPatchNames -join ', '))
    }
    $patchCatalog = @($patchCatalog | Where-Object { [string]$_.name -in $requestedPatchNames })
}
$trackedOfficialFiles = @(
    Join-Path $officialOmxRootPath 'dist\team\runtime.js'
    Join-Path $officialOmxRootPath 'dist\team\windows-worker-controller.js'
    Join-Path $officialOmxRootPath 'dist\team\worker-bootstrap.js'
)
$trackedWrapperPaths = Get-TrackedWrapperPaths -CodexHomePath $codexHomePath

$precheckSnapshotLabel = 'precheck'
$precheckSnapshotRoot = Join-Path $snapshotRootPath $precheckSnapshotLabel
$shouldCreatePrecheckSnapshot = -not (Test-Path -LiteralPath $precheckSnapshotRoot)
if ($shouldCreatePrecheckSnapshot) {
    foreach ($path in $trackedOfficialFiles + $trackedWrapperPaths) {
        Copy-FileToSnapshot -SourcePath $path -SnapshotBasePath $snapshotRootPath -Label $precheckSnapshotLabel | Out-Null
    }
}

$globalListing = if ($npmPath) {
    Invoke-ExternalCommand -FilePath $npmPath -Arguments @('ls', '-g', 'oh-my-codex', '@openai/codex', '--depth=0') -IgnoreExitCode
} else {
    [pscustomobject]@{ file_path = ''; arguments = @(); working_directory = ''; exit_code = -1; output = @('npm not found') }
}

$globalNpmRootInfo = Get-GlobalNpmRootInfo -NpmPath $npmPath
$officialUpdateLockPreflight = Get-CodexUpdateLockPreflight -GlobalNpmRootInfo $globalNpmRootInfo -AllowLockedUpdate:$AllowLockedCodexUpdate

$patchStatusBefore = @()
if ($nodePath) {
    foreach ($patch in $patchCatalog) {
        $patchStatusBefore += Invoke-PatchScript -NodePath $nodePath -Patch $patch -Action 'status' -SnapshotBasePath $snapshotRootPath
    }
} else {
    $patchStatusBefore = @(
        foreach ($patch in $patchCatalog) {
            [pscustomobject]@{
                patch = $patch.name
                scope = $patch.scope
                category = $patch.category
                action = 'status'
                ok = $false
                status = 'node_missing'
                script_path = $patch.script_path
                target_path = $patch.target_path
            }
        }
    )
}

$officialUpdateResult = $null
$officialUpdateCleanupWarnings = @()
$officialUpdateFailureMessage = ''
if ($stagePlan.run_official_update) {
    if (-not $npmPath) {
        throw 'Cannot run the official update because npm was not found.'
    }
    foreach ($warningMessage in @($officialUpdateLockPreflight.warnings)) {
        Write-Warning $warningMessage
    }
    if (-not $officialUpdateLockPreflight.allowed) {
        $officialUpdateFailureMessage = ($officialUpdateLockPreflight.errors -join ' ')
    } elseif ($PSCmdlet.ShouldProcess('global npm packages', 'npm install -g @openai/codex oh-my-codex')) {
        Write-Step 'Running official npm update'
        $officialUpdateResult = Invoke-ExternalCommand -FilePath $npmPath -Arguments @('install', '-g', '@openai/codex', 'oh-my-codex') -IgnoreExitCode
        $officialUpdateCleanupWarnings = @(Get-OfficialUpdateCleanupWarnings -OfficialUpdateResult $officialUpdateResult)
        if ([int]$officialUpdateResult.exit_code -ne 0) {
            $officialUpdateFailureMessage = "Command failed (exit $([int]$officialUpdateResult.exit_code)): $npmPath install -g @openai/codex oh-my-codex"
        }
    }
}

$omxSetupResult = $null
if ($stagePlan.run_omx_setup -and [string]::IsNullOrWhiteSpace($officialUpdateFailureMessage)) {
    if (-not $omxPath) {
        throw 'Cannot run omx setup because omx was not found.'
    }
    if ($PSCmdlet.ShouldProcess('OMX install', 'omx setup')) {
        Write-Step 'Running omx setup'
        $omxSetupResult = Invoke-ExternalCommand -FilePath $omxPath -Arguments @('setup')
    }
}

$omxUpdateResult = $null
if ($stagePlan.run_omx_update -and [string]::IsNullOrWhiteSpace($officialUpdateFailureMessage)) {
    if (-not $omxPath) {
        throw 'Cannot run omx update because omx was not found.'
    }
    if ($PSCmdlet.ShouldProcess('OMX install', 'omx update')) {
        Write-Step 'Running omx update'
        $omxUpdateResult = Invoke-ExternalCommand -FilePath $omxPath -Arguments @('update')
    }
}

$postcheckSnapshotLabel = 'post-update'
foreach ($path in $trackedOfficialFiles + $trackedWrapperPaths) {
    Copy-FileToSnapshot -SourcePath $path -SnapshotBasePath $snapshotRootPath -Label $postcheckSnapshotLabel | Out-Null
}

$patchStatusAfterUpdate = @()
if ($nodePath) {
    foreach ($patch in $patchCatalog) {
        $patchStatusAfterUpdate += Invoke-PatchScript -NodePath $nodePath -Patch $patch -Action 'status' -SnapshotBasePath $snapshotRootPath
    }
} else {
    $patchStatusAfterUpdate = @()
}

$officialPatchReplayResults = @()
if ($stagePlan.replay_official_install_patches) {
    if (-not $nodePath) {
        throw 'Cannot replay official-install patches because node was not found.'
    }

    foreach ($patch in @($patchCatalog | Where-Object { $_.scope -eq 'official_install' })) {
        if ($PSCmdlet.ShouldProcess($patch.target_path, "Apply patch $($patch.name)")) {
            Write-Step "Applying official-install patch: $($patch.name)"
            $officialPatchReplayResults += Invoke-PatchScript -NodePath $nodePath -Patch $patch -Action 'apply' -SnapshotBasePath $snapshotRootPath
        }
    }
}

$userLevelPatchReplayResults = @()
if ($stagePlan.replay_user_level_surface_patches) {
    if (-not $nodePath) {
        throw 'Cannot replay user-level surface patches because node was not found.'
    }

    foreach ($patch in @($patchCatalog | Where-Object { $_.scope -eq 'user_level_surface' })) {
        if ($PSCmdlet.ShouldProcess($patch.target_path, "Apply patch $($patch.name)")) {
            Write-Step "Applying user-level surface patch: $($patch.name)"
            $userLevelPatchReplayResults += Invoke-PatchScript -NodePath $nodePath -Patch $patch -Action 'apply' -SnapshotBasePath $snapshotRootPath
        }
    }
}

$installerResult = $null
if ($stagePlan.regenerate_user_level_layer) {
    $installerPath = Join-Path $repoRootPath 'tools\install-codex-user-level-team-mode.ps1'
    if (-not (Test-Path -LiteralPath $installerPath)) {
        throw "Installer script not found: $installerPath"
    }

    if ($PSCmdlet.ShouldProcess($codexHomePath, 'Regenerate user-level team-mode layer')) {
        Write-Step 'Regenerating the user-level wrapper layer'
        $installerResult = Invoke-ExternalCommand -FilePath $powerShellPath -Arguments @(
            '-NoProfile'
            '-ExecutionPolicy'
            'Bypass'
            '-File'
            $installerPath
            '-CodexHome'
            $codexHomePath
            '-Force'
        ) -WorkingDirectory $repoRootPath
    }
}

$installerTestResult = $null
if ($stagePlan.run_installer_tests) {
    $testPath = Join-Path $repoRootPath 'test\install-codex-user-level-team-mode.test.ps1'
    if (-not (Test-Path -LiteralPath $testPath)) {
        throw "Installer test script not found: $testPath"
    }

    if ($PSCmdlet.ShouldProcess($testPath, 'Run installer regression tests')) {
        Write-Step 'Running installer regression tests'
        $installerTestResult = Invoke-ExternalCommand -FilePath $powerShellPath -Arguments @(
            '-NoProfile'
            '-ExecutionPolicy'
            'Bypass'
            '-File'
            $testPath
        ) -WorkingDirectory $repoRootPath
    }
}

$report = [pscustomobject]@{
    generated_at = (Get-Date).ToString('o')
    repo_root = $repoRootPath
    official_omx_root = $officialOmxRootPath
    codex_home = $codexHomePath
    snapshot_root = $snapshotRootPath
    stage = $stagePlan
    stage_gate = $stageGate
    checkpoint = [pscustomobject]@{
        snapshot_root_source = $snapshotRootPlan.source
        latest_pointer_path = (Get-LatestCheckpointPointerPath -RepoRootPath $repoRootPath)
        previous_report_path = if (Test-Path -LiteralPath $previousReportPath) { $previousReportPath } else { '' }
        previous_stage = if ($null -ne $previousReport -and $null -ne $previousReport.stage -and -not [string]::IsNullOrWhiteSpace([string]$previousReport.stage.stage)) { [string]$previousReport.stage.stage } else { '' }
        previous_generated_at = if ($null -ne $previousReport -and -not [string]::IsNullOrWhiteSpace([string]$previousReport.generated_at)) { [string]$previousReport.generated_at } else { '' }
        prior_manifest_present = ($null -ne $checkpointManifestBefore)
        prior_stage_history = if ($null -ne $checkpointManifestBefore -and $null -ne $checkpointManifestBefore.stage_history) { @($checkpointManifestBefore.stage_history) } else { @() }
    }
    environment = [pscustomobject]@{
        node_path = if ($nodePath) { $nodePath } else { '' }
        npm_path = if ($npmPath) { $npmPath } else { '' }
        omx_path = if ($omxPath) { $omxPath } else { '' }
        powershell_path = $powerShellPath
        global_npm_listing = [pscustomobject]$globalListing
        global_npm_root = [pscustomobject]$globalNpmRootInfo
        codex_update_lock_preflight = [pscustomobject]$officialUpdateLockPreflight
    }
    patch_catalog = @($patchCatalog)
    windows_codex_lock_preflight = [pscustomobject]$officialUpdateLockPreflight
    official_file_presence_before = @(Get-FilePresenceSummary -Paths $trackedOfficialFiles)
    wrapper_presence_before = @(Get-FilePresenceSummary -Paths $trackedWrapperPaths)
    marker_inventory_before = @(Get-MarkerInventory -OfficialRoot $officialOmxRootPath)
    patch_status_before = @($patchStatusBefore)
    patch_status_after_update = @($patchStatusAfterUpdate)
    official_update = $officialUpdateResult
    official_update_failure = $officialUpdateFailureMessage
    official_update_cleanup_warnings = @($officialUpdateCleanupWarnings)
    omx_setup = $omxSetupResult
    omx_update = $omxUpdateResult
    official_patch_replay = @($officialPatchReplayResults)
    user_level_patch_replay = @($userLevelPatchReplayResults)
    installer_regeneration = $installerResult
    installer_tests = $installerTestResult
    recommended_next_commands = @(
        ".\\tools\\codex-official-update-patch-replay-template.ps1 -Stage precheck -Json"
        ".\\tools\\codex-official-update-patch-replay-template.ps1 -Stage update"
        ".\\tools\\codex-official-update-patch-replay-template.ps1 -Stage diff"
        ".\\tools\\codex-official-update-patch-replay-template.ps1 -Stage diff -ApproveDiff"
        ".\\tools\\codex-official-update-patch-replay-template.ps1 -Stage replay"
        ".\\tools\\codex-official-update-patch-replay-template.ps1 -Stage test"
        ".\\tools\\codex-official-update-patch-replay-template.ps1 -Stage all"
        (".\\tools\\codex-official-update-patch-replay-template.ps1 -SnapshotRoot `"{0}`" -Stage diff" -f $snapshotRootPath)
        (".\\tools\\codex-official-update-patch-replay-template.ps1 -SnapshotRoot `"{0}`" -Stage diff -ApproveDiff" -f $snapshotRootPath)
        (".\\tools\\codex-official-update-patch-replay-template.ps1 -SnapshotRoot `"{0}`" -Stage replay" -f $snapshotRootPath)
        (".\\tools\\codex-official-update-patch-replay-template.ps1 -SnapshotRoot `"{0}`" -Stage test" -f $snapshotRootPath)
    )
}

$reportJsonPath = Join-Path $snapshotRootPath 'report.json'
$checklistPath = Join-Path $snapshotRootPath 'checklist.md'
$decisionTablePath = Join-Path $snapshotRootPath 'patch-decision-table.md'
$decisionTableJsonPath = Join-Path $snapshotRootPath 'patch-decision-table.json'
$decisionTableCsvPath = Join-Path $snapshotRootPath 'patch-decision-table.csv'
$checkpointManifestPath = Join-Path $snapshotRootPath 'checkpoint.json'
$latestCheckpointPointerPath = Get-LatestCheckpointPointerPath -RepoRootPath $repoRootPath
$report | Add-Member -NotePropertyName report_json_path -NotePropertyValue $reportJsonPath
$report | Add-Member -NotePropertyName checklist_path -NotePropertyValue $checklistPath
$report | Add-Member -NotePropertyName patch_decision_table_path -NotePropertyValue $decisionTablePath
$report | Add-Member -NotePropertyName patch_decision_table_json_path -NotePropertyValue $decisionTableJsonPath
$report | Add-Member -NotePropertyName patch_decision_table_csv_path -NotePropertyValue $decisionTableCsvPath
$report | Add-Member -NotePropertyName checkpoint_manifest_path -NotePropertyValue $checkpointManifestPath
$diffReviewApprovalState = Resolve-DiffReviewApprovalState -CheckpointManifest $checkpointManifestBefore -SelectedStage $Stage -GeneratedAt $report.generated_at -Approve:$ApproveDiff -ApprovalNote $DiffApprovalNote
$report | Add-Member -NotePropertyName approvals -NotePropertyValue ([pscustomobject][ordered]@{
    diff_review = $diffReviewApprovalState
})
$decisionRows = @(Normalize-PatchDecisionRows -Rows (Get-PatchDecisionRows -Report $report -PreviousRows $existingDecisionRows))
$report | Add-Member -NotePropertyName patch_decision_rows -NotePropertyValue $decisionRows
($report | ConvertTo-Json -Depth 20) | Set-Content -LiteralPath $reportJsonPath -Encoding UTF8
Write-ChecklistMarkdown -Report $report -OutputPath $checklistPath
Write-PatchDecisionTableMarkdown -Report $report -Rows $decisionRows -OutputPath $decisionTablePath
ConvertTo-Json -InputObject @($decisionRows) -Depth 20 | Set-Content -LiteralPath $decisionTableJsonPath -Encoding UTF8
($decisionRows | ConvertTo-Csv -NoTypeInformation) | Set-Content -LiteralPath $decisionTableCsvPath -Encoding UTF8

$stageHistory = @()
if ($null -ne $checkpointManifestBefore -and $null -ne $checkpointManifestBefore.stage_history) {
    foreach ($entry in @($checkpointManifestBefore.stage_history)) {
        $stageHistory += $entry
    }
}
$stageHistory += [ordered]@{
    stage = $stagePlan.stage
    stage_description = $stagePlan.stage_description
    executed_at = $report.generated_at
    report_json_path = $reportJsonPath
    checklist_path = $checklistPath
    patch_decision_table_path = $decisionTablePath
    patch_decision_table_json_path = $decisionTableJsonPath
    patch_decision_table_csv_path = $decisionTableCsvPath
}
$createdAtValue = $report.generated_at
if ($null -ne $checkpointManifestBefore -and -not [string]::IsNullOrWhiteSpace([string]$checkpointManifestBefore.created_at)) {
    $createdAtValue = [string]$checkpointManifestBefore.created_at
}
$checkpointManifest = [ordered]@{
    schema = 'codex-official-update-patch-replay-checkpoint-v1'
    repo_root = $repoRootPath
    snapshot_root = $snapshotRootPath
    current_stage = $stagePlan.stage
    current_stage_description = $stagePlan.stage_description
    created_at = $createdAtValue
    updated_at = $report.generated_at
    latest_report_path = $reportJsonPath
    latest_checklist_path = $checklistPath
    latest_patch_decision_table_path = $decisionTablePath
    latest_patch_decision_table_json_path = $decisionTableJsonPath
    latest_patch_decision_table_csv_path = $decisionTableCsvPath
    approvals = [ordered]@{
        diff_review = [ordered]@{
            approved = [bool]$diffReviewApprovalState.approved
            approved_at = [string]$diffReviewApprovalState.approved_at
            approval_note = [string]$diffReviewApprovalState.approval_note
        }
    }
    stage_history = @($stageHistory)
}
$checkpointManifestPath = Write-CheckpointManifest -SnapshotRootPath $snapshotRootPath -Manifest $checkpointManifest
$latestPointer = [ordered]@{
    schema = 'codex-official-update-patch-replay-latest-v1'
    repo_root = $repoRootPath
    snapshot_root = $snapshotRootPath
    stage = $stagePlan.stage
    generated_at = $report.generated_at
    checkpoint_manifest_path = $checkpointManifestPath
    report_json_path = $reportJsonPath
    checklist_path = $checklistPath
    patch_decision_table_path = $decisionTablePath
    patch_decision_table_json_path = $decisionTableJsonPath
    patch_decision_table_csv_path = $decisionTableCsvPath
}
Ensure-Directory -Path (Split-Path -Parent $latestCheckpointPointerPath)
($latestPointer | ConvertTo-Json -Depth 20) | Set-Content -LiteralPath $latestCheckpointPointerPath -Encoding UTF8

if ($Json) {
    $report | ConvertTo-Json -Depth 20
} else {
    Write-Step "Snapshot root: $snapshotRootPath"
    Write-Step "Report: $reportJsonPath"
    Write-Step "Checklist: $checklistPath"
    Write-Step "Patch decision table: $decisionTablePath"
    Write-Step "Patch decision table JSON: $decisionTableJsonPath"
    Write-Step "Patch decision table CSV: $decisionTableCsvPath"
    Write-Step "Checkpoint manifest: $checkpointManifestPath"
    Write-Step "Latest checkpoint pointer: $latestCheckpointPointerPath"
}

if (-not [string]::IsNullOrWhiteSpace($officialUpdateFailureMessage)) {
    throw $officialUpdateFailureMessage
}
