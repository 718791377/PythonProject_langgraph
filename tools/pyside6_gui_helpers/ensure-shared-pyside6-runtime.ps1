<#
.SYNOPSIS
Preview, provision, or verify the shared PySide6 runtime maintained by this repository.

.DESCRIPTION
The shared runtime is the default PySide6 installation surface for local consumer
projects. Preview mode is read-only. Provision mode creates or updates only
`.shared_runtimes/pyside6` and installs PySide6 only inside that runtime. Verify
mode performs import-only checks and never launches a visible GUI window.
#>
[CmdletBinding()]
param(
    [ValidateSet("preview", "provision", "verify")]
    [string]$Mode = "preview",
    [string]$RuntimeRoot = "D:\PythonProject_langgraph\.shared_runtimes\pyside6",
    [string]$PythonPath = "",
    [switch]$Json
)

$ErrorActionPreference = "Stop"
$Utf8NoBom = [System.Text.UTF8Encoding]::new($false)

function Get-RepoRoot {
    $helperDirectory = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
    return (Resolve-Path -LiteralPath (Join-Path $helperDirectory "..\..")).ProviderPath
}

function New-Blocker {
    param([string]$Code, [string]$Message)
    return [ordered]@{ code = $Code; message = $Message }
}

function Write-TextIfChanged {
    param([string]$Path, [string]$Content)
    $parent = [System.IO.Path]::GetDirectoryName($Path)
    if (-not [string]::IsNullOrWhiteSpace($parent)) {
        [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    }
    if ((Test-Path -LiteralPath $Path -PathType Leaf) -and ([System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8) -eq $Content)) {
        return
    }
    [System.IO.File]::WriteAllText($Path, $Content, $Utf8NoBom)
}

function Get-TemplateRequirementsContent {
    param([string]$TemplatePath)
    if (Test-Path -LiteralPath $TemplatePath -PathType Leaf) {
        return [System.IO.File]::ReadAllText($TemplatePath, [System.Text.Encoding]::UTF8)
    }
    return "PySide6`r`nPySide6-Fluent-Widgets`r`n"
}

function Split-RequirementLines {
    param([string]$Content)
    $lines = @()
    if (-not [string]::IsNullOrWhiteSpace($Content)) {
        $lines = $Content -split "`r?`n"
    }
    return @($lines | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
}

function Merge-RequirementsContent {
    param([string]$ExistingContent, [string]$TemplateContent)
    $existingLines = @(Split-RequirementLines $ExistingContent)
    $templateLines = @(Split-RequirementLines $TemplateContent)
    $merged = [System.Collections.Generic.List[string]]::new()
    $seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    $added = [System.Collections.Generic.List[string]]::new()

    foreach ($line in $existingLines) {
        $trimmed = ([string]$line).Trim()
        if ([string]::IsNullOrWhiteSpace($trimmed)) { continue }
        [void]$merged.Add($trimmed)
        [void]$seen.Add($trimmed)
    }

    foreach ($line in $templateLines) {
        $trimmed = ([string]$line).Trim()
        if ([string]::IsNullOrWhiteSpace($trimmed)) { continue }
        if (-not $seen.Contains($trimmed)) {
            [void]$merged.Add($trimmed)
            [void]$seen.Add($trimmed)
            [void]$added.Add($trimmed)
        }
    }

    $content = (($merged | ForEach-Object { [string]$_ }) -join "`r`n") + "`r`n"
    return [ordered]@{
        content = $content
        added = @($added)
        backfilled = ($added.Count -gt 0)
    }
}

function Invoke-JsonPython {
    param([string]$RuntimePython)
    $probe = @'
import json, platform, sys
payload = {
    "python_version": platform.python_version(),
    "runtime_python": sys.executable,
    "pyside6_version": None,
    "qt_version": None,
    "qfluentwidgets_version": None,
    "qfluentwidgets_import_status": None,
    "import_only_verified": False,
}
try:
    import PySide6
    from PySide6.QtCore import qVersion
    from PySide6.QtWidgets import QApplication
    payload["pyside6_version"] = getattr(PySide6, "__version__", "")
    payload["qt_version"] = qVersion()
    import qfluentwidgets
    payload["qfluentwidgets_version"] = getattr(qfluentwidgets, "__version__", None)
    payload["qfluentwidgets_import_status"] = "import_ok"
    payload["import_only_verified"] = True
except Exception as exc:
    payload["error"] = str(exc)
    payload.setdefault("qfluentwidgets_import_status", "missing")
print(json.dumps(payload, ensure_ascii=False))
'@
    $probePath = [System.IO.Path]::ChangeExtension([System.IO.Path]::GetTempFileName(), ".py")
    try {
        [System.IO.File]::WriteAllText($probePath, $probe, $Utf8NoBom)
        $output = & $RuntimePython $probePath 2>&1
        $exitCode = $LASTEXITCODE
        $combinedOutput = ($output | Out-String).Trim()
        if ($exitCode -ne 0) {
            throw "PySide6 and qfluentwidgets import-only probe failed with exit code ${exitCode}: $combinedOutput"
        }
        $jsonLine = $output | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | Select-Object -Last 1
        if ([string]::IsNullOrWhiteSpace([string]$jsonLine)) {
            throw "PySide6 and qfluentwidgets import-only probe did not emit JSON output."
        }
        return ([string]$jsonLine | ConvertFrom-Json)
    } finally {
        if (Test-Path -LiteralPath $probePath -PathType Leaf) {
            Remove-Item -LiteralPath $probePath -Force
        }
    }
}

$repoRoot = Get-RepoRoot
$resolvedRuntimeRoot = [System.IO.Path]::GetFullPath($RuntimeRoot)
$defaultRuntimeRoot = [System.IO.Path]::GetFullPath("D:\PythonProject_langgraph\.shared_runtimes\pyside6")
$runtimePython = Join-Path $resolvedRuntimeRoot ".venv\Scripts\python.exe"
$requirementsFile = Join-Path $resolvedRuntimeRoot "requirements-pyside6.txt"
$runtimeJson = Join-Path $resolvedRuntimeRoot "runtime.json"
$templateRequirements = Join-Path $repoRoot "tools\pyside6_gui_templates\shared_runtime\requirements-pyside6.txt.template"

$blockers = @()
$warnings = @()
$info = @()
$plannedCommands = @()
$localOnlyArtifacts = @(
    ".shared_runtimes/pyside6/.venv/",
    ".shared_runtimes/pyside6/logs/",
    ".shared_runtimes/pyside6/runtime.json"
)
$rollbackSteps = @(
    "Remove or rename the shared runtime directory if this provision attempt must be discarded.",
    "Restore the previous requirements-pyside6.txt or runtime.json snapshot if one was captured.",
    "Run this helper again in -Mode provision only after the operator approves shared runtime maintenance."
)

if ($resolvedRuntimeRoot -ne $defaultRuntimeRoot -and ($resolvedRuntimeRoot -notmatch "\\\.shared_runtimes\\pyside6$")) {
    $blockers += New-Blocker "runtime_root_outside_shared_runtime" "RuntimeRoot must target a .shared_runtimes\pyside6 directory."
}

if ($Mode -eq "preview") {
    $plannedCommands += "Create $resolvedRuntimeRoot only if the operator approves shared runtime provisioning."
    $plannedCommands += "Create .venv under $resolvedRuntimeRoot and install PySide6 plus PySide6-Fluent-Widgets from requirements-pyside6.txt."
    $plannedCommands += "Run verify mode for import_only_verified evidence; no visible GUI launch is allowed."
}

if ($Mode -in @("verify", "provision") -and -not (Test-Path -LiteralPath $runtimePython -PathType Leaf)) {
    if ($Mode -eq "verify") {
        $blockers += New-Blocker "shared_runtime_missing" "Shared runtime Python was not found at $runtimePython."
    }
}

if ($Mode -eq "provision" -and $blockers.Count -eq 0) {
    [System.IO.Directory]::CreateDirectory($resolvedRuntimeRoot) | Out-Null
    $templateRequirementsContent = Get-TemplateRequirementsContent $templateRequirements
    $existingRequirementsContent = if (Test-Path -LiteralPath $requirementsFile -PathType Leaf) {
        [System.IO.File]::ReadAllText($requirementsFile, [System.Text.Encoding]::UTF8)
    } else {
        ""
    }
    $mergedRequirements = Merge-RequirementsContent $existingRequirementsContent $templateRequirementsContent
    if ((-not (Test-Path -LiteralPath $requirementsFile -PathType Leaf)) -or ($existingRequirementsContent -ne $mergedRequirements.content)) {
        Write-TextIfChanged $requirementsFile $mergedRequirements.content
        if ([bool]$mergedRequirements.backfilled) {
            $info += "requirements_backfilled_from_template: added $($mergedRequirements.added -join ', ') to requirements-pyside6.txt."
        } else {
            $info += "requirements_created_from_template: wrote requirements-pyside6.txt from the shared runtime template."
        }
    }
    if (-not (Test-Path -LiteralPath $runtimePython -PathType Leaf)) {
        $basePython = if (-not [string]::IsNullOrWhiteSpace($PythonPath)) { $PythonPath } else { (Get-Command python -ErrorAction Stop).Source }
        & $basePython -m venv (Join-Path $resolvedRuntimeRoot ".venv")
        if ($LASTEXITCODE -ne 0) {
            $blockers += New-Blocker "venv_create_failed" "Failed to create shared runtime venv at $resolvedRuntimeRoot."
        }
    }
    if ($blockers.Count -eq 0) {
        & $runtimePython -m pip install --upgrade pip
        if ($LASTEXITCODE -ne 0) { $blockers += New-Blocker "pip_upgrade_failed" "Failed to upgrade pip inside the shared PySide6 runtime." }
    }
    if ($blockers.Count -eq 0) {
        & $runtimePython -m pip install -r $requirementsFile
        if ($LASTEXITCODE -ne 0) { $blockers += New-Blocker "pyside6_install_failed" "Failed to install PySide6 and PySide6-Fluent-Widgets from requirements-pyside6.txt inside the shared runtime." }
    }
}

$probePayload = $null
if ($blockers.Count -eq 0 -and (Test-Path -LiteralPath $runtimePython -PathType Leaf) -and $Mode -in @("verify", "provision")) {
    try {
        $probePayload = Invoke-JsonPython $runtimePython
    } catch {
        $blockers += New-Blocker "import_only_probe_failed" $_.Exception.Message
    }
}

if ($blockers.Count -eq 0 -and $probePayload -and (-not [bool]$probePayload.import_only_verified)) {
    $probeError = if ($probePayload.error) { $probePayload.error } else { "unknown import-only probe failure" }
    $blockers += New-Blocker "qfluentwidgets_import_missing" "PySide6 and qfluentwidgets import-only verification failed: $probeError. Ensure PySide6-Fluent-Widgets is present in requirements-pyside6.txt and installed in the shared runtime."
}

if ($blockers.Count -eq 0 -and $Mode -eq "provision" -and $probePayload) {
    $now = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $runtimeRecord = [ordered]@{
        schema_version = 1
        runtime_mode = "shared"
        runtime_owner_repo = "D:\PythonProject_langgraph"
        runtime_root = $resolvedRuntimeRoot
        runtime_python = $runtimePython
        python_version = $probePayload.python_version
        pyside6_version = $probePayload.pyside6_version
        qt_version = $probePayload.qt_version
        qfluentwidgets_version = $probePayload.qfluentwidgets_version
        qfluentwidgets_import_status = $probePayload.qfluentwidgets_import_status
        qfluentwidgets_package = "PySide6-Fluent-Widgets"
        qfluentwidgets_import_name = "qfluentwidgets"
        qfluentwidgets_license_family = "GPLv3-or-commercial-dual-license"
        qfluentwidgets_license_review_required_before_redistribution = $true
        requirements_file = $requirementsFile
        runtime_json = $runtimeJson
        updated_at = $now
        import_only_verified = [bool]$probePayload.import_only_verified
        visible_gui_requires_explicit_request = $true
        local_only_artifacts = $localOnlyArtifacts
        rollback_steps = $rollbackSteps
    }
    Write-TextIfChanged $runtimeJson ($runtimeRecord | ConvertTo-Json -Depth 8)
}

$runtimeStatus = if (Test-Path -LiteralPath $runtimePython -PathType Leaf) { "present" } else { "missing" }
if ($probePayload -and $probePayload.import_only_verified) { $runtimeStatus = "import_only_verified" }
if ($Mode -eq "preview" -and $runtimeStatus -eq "missing") {
    $warnings += "shared_runtime_missing: provision the shared runtime as a separate approved maintenance task before consumer-project verification."
}

$payload = [ordered]@{
    schema_version = 1
    check_name = "shared_pyside6_runtime_helper"
    mode = $Mode
    ok = ($blockers.Count -eq 0)
    runtime_root = $resolvedRuntimeRoot
    runtime_python = $runtimePython
    runtime_status = $runtimeStatus
    python_version = if ($probePayload) { $probePayload.python_version } else { $null }
    pyside6_version = if ($probePayload) { $probePayload.pyside6_version } else { $null }
    qt_version = if ($probePayload) { $probePayload.qt_version } else { $null }
    qfluentwidgets_version = if ($probePayload) { $probePayload.qfluentwidgets_version } else { $null }
    qfluentwidgets_import_status = if ($probePayload) { $probePayload.qfluentwidgets_import_status } else { $null }
    qfluentwidgets_package = "PySide6-Fluent-Widgets"
    qfluentwidgets_import_name = "qfluentwidgets"
    import_only_verified = if ($probePayload) { [bool]$probePayload.import_only_verified } else { $false }
    requirements_file = $requirementsFile
    runtime_json = $runtimeJson
    planned_commands = $plannedCommands
    local_only_artifacts = $localOnlyArtifacts
    blockers = $blockers
    warnings = $warnings
    info = $info
    rollback_steps = $rollbackSteps
}

if ($Json) {
    $payload | ConvertTo-Json -Depth 10
} else {
    Write-Output "Shared PySide6 runtime helper"
    Write-Output "Mode: $Mode"
    Write-Output "Runtime root: $resolvedRuntimeRoot"
    Write-Output "Runtime status: $runtimeStatus"
    if ($blockers.Count -gt 0) {
        Write-Output "Blockers:"
        foreach ($blocker in $blockers) { Write-Output "  - $($blocker.code): $($blocker.message)" }
    }
    Write-Output ""
    Write-Output "Structured JSON:"
    $payload | ConvertTo-Json -Depth 10
}

if ($payload.ok) { exit 0 }
exit 2
