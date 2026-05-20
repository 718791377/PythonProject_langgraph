<#
.SYNOPSIS
Preview-first PySide6 GUI enablement helper for project-local GUI adoption.

.DESCRIPTION
This helper intentionally defaults to preview mode. Preview mode inspects a target
project root, reports root/dependency/Python evidence, and emits a structured JSON
preview without creating files, installing packages, launching visible GUI windows,
or modifying global/user-level configuration.
#>
[CmdletBinding()]
param(
    [string]$ProjectRoot = ".",
    [ValidateSet("preview", "apply")]
    [string]$Mode = "preview",
    [ValidateSet("auto", "requirements", "pyproject-extra", "group")]
    [string]$DependencyStyle = "auto",
    [string]$PythonPath = "",
    [string]$PackageVersion = "",
    [switch]$CreateTemplate,
    [switch]$RunSmokeTest,
    [string]$PackageName = "",
    [switch]$Json
)

$ErrorActionPreference = "Stop"

function New-Blocker {
    param([string]$Code, [string]$Message)
    return [ordered]@{ code = $Code; message = $Message }
}

function Normalize-PackageName {
    param([string]$Name)
    $normalized = ($Name -replace "[^A-Za-z0-9_]", "_").Trim("_")
    if ([string]::IsNullOrWhiteSpace($normalized)) { return "project_gui" }
    if ($normalized -notmatch "^[A-Za-z_]") { $normalized = "gui_$normalized" }
    return $normalized.ToLowerInvariant()
}

function Add-PathIfExists {
    param([string]$RelativePath, [string[]]$Evidence)
    if (Test-Path -LiteralPath (Join-Path $script:ResolvedProjectRoot $RelativePath)) {
        return @($Evidence + $RelativePath)
    }
    return $Evidence
}

$blockers = @()
$warnings = @()
$info = @("Preview-first helper: no files are created, no packages are installed, and no GUI window is launched.")
$projectRootInput = $ProjectRoot
$script:ResolvedProjectRoot = $null

if (Test-Path -LiteralPath $ProjectRoot -PathType Container) {
    $script:ResolvedProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).ProviderPath
} else {
    $blockers += New-Blocker "project_root_missing" "ProjectRoot does not exist or is not a directory: $ProjectRoot"
}

$projectRootEvidence = @()
$packageManager = "unknown"
$detectedDependencyStyle = "unknown"

if ($script:ResolvedProjectRoot) {
    foreach ($marker in @(".git", "pyproject.toml", "requirements.txt", "requirements-gui.txt", "setup.cfg", "setup.py", "poetry.lock", "uv.lock", "README.md")) {
        if (Test-Path -LiteralPath (Join-Path $script:ResolvedProjectRoot $marker)) {
            $projectRootEvidence += $marker
        }
    }
    if ($projectRootEvidence.Count -eq 0) {
        $blockers += New-Blocker "unsafe_project_root" "No project root evidence found. Expected markers such as .git, pyproject.toml, requirements.txt, setup.cfg, setup.py, or README.md."
    }

    if (Test-Path -LiteralPath (Join-Path $script:ResolvedProjectRoot "uv.lock")) {
        $packageManager = "uv"
        $detectedDependencyStyle = "group"
    } elseif (Test-Path -LiteralPath (Join-Path $script:ResolvedProjectRoot "poetry.lock")) {
        $packageManager = "poetry"
        $detectedDependencyStyle = "pyproject-extra"
    } elseif (Test-Path -LiteralPath (Join-Path $script:ResolvedProjectRoot "pyproject.toml")) {
        $packageManager = "pyproject"
        $detectedDependencyStyle = "pyproject-extra"
    } elseif ((Test-Path -LiteralPath (Join-Path $script:ResolvedProjectRoot "requirements.txt")) -or (Test-Path -LiteralPath (Join-Path $script:ResolvedProjectRoot "requirements-gui.txt"))) {
        $packageManager = "pip"
        $detectedDependencyStyle = "requirements"
    } elseif ((Test-Path -LiteralPath (Join-Path $script:ResolvedProjectRoot "setup.cfg")) -or (Test-Path -LiteralPath (Join-Path $script:ResolvedProjectRoot "setup.py"))) {
        $packageManager = "setuptools"
        $detectedDependencyStyle = "pyproject-extra"
    } else {
        $blockers += New-Blocker "dependency_style_unknown" "No supported dependency declaration surface was found. Add pyproject.toml or requirements.txt, or pass -DependencyStyle explicitly."
    }
}

$selectedDependencyStyle = $DependencyStyle
if ($DependencyStyle -eq "auto") {
    $selectedDependencyStyle = $detectedDependencyStyle
}
if ($selectedDependencyStyle -eq "unknown" -or [string]::IsNullOrWhiteSpace($selectedDependencyStyle)) {
    $selectedDependencyStyle = "unknown"
}

$pythonPathResolved = $null
$pythonVersion = $null
if (-not [string]::IsNullOrWhiteSpace($PythonPath)) {
    if (Test-Path -LiteralPath $PythonPath -PathType Leaf) {
        $pythonPathResolved = (Resolve-Path -LiteralPath $PythonPath).ProviderPath
    } else {
        $blockers += New-Blocker "python_path_missing" "PythonPath does not exist: $PythonPath"
    }
} elseif ($script:ResolvedProjectRoot -and (Test-Path -LiteralPath (Join-Path $script:ResolvedProjectRoot ".venv\Scripts\python.exe") -PathType Leaf)) {
    $pythonPathResolved = (Resolve-Path -LiteralPath (Join-Path $script:ResolvedProjectRoot ".venv\Scripts\python.exe")).ProviderPath
} else {
    $command = Get-Command python -ErrorAction SilentlyContinue
    if ($command) {
        $pythonPathResolved = $command.Source
    } else {
        $blockers += New-Blocker "python_not_found" "No project .venv Python and no python command found on PATH."
    }
}

if ($pythonPathResolved) {
    try {
        $pythonVersion = (& $pythonPathResolved --version 2>&1 | Select-Object -First 1).ToString()
    } catch {
        $blockers += New-Blocker "python_version_probe_failed" "Unable to run Python version probe: $($_.Exception.Message)"
    }
}

if ($Mode -eq "apply") {
    $blockers += New-Blocker "apply_not_implemented" "Apply mode is intentionally blocked in the preview-helper slice. Implement slice 3 with its own tests before enabling writes."
}

$rootLeaf = if ($script:ResolvedProjectRoot) { Split-Path -Leaf $script:ResolvedProjectRoot } else { "project" }
$basePackage = if ([string]::IsNullOrWhiteSpace($PackageName)) { "$rootLeaf`_gui" } else { $PackageName }
$normalizedPackage = Normalize-PackageName $basePackage
$pySideSpec = if ([string]::IsNullOrWhiteSpace($PackageVersion)) { "PySide6" } else { "PySide6==$PackageVersion" }

$plannedFileChanges = @()
if ($selectedDependencyStyle -eq "requirements") {
    $plannedFileChanges += [ordered]@{ path = "requirements-gui.txt"; action = "create_or_update"; reason = "Declare $pySideSpec in a project-local requirements surface." }
} elseif ($selectedDependencyStyle -eq "pyproject-extra") {
    $plannedFileChanges += [ordered]@{ path = "pyproject.toml"; action = "update"; reason = "Declare $pySideSpec in a GUI optional dependency extra." }
} elseif ($selectedDependencyStyle -eq "group") {
    $plannedFileChanges += [ordered]@{ path = "pyproject.toml"; action = "update"; reason = "Declare $pySideSpec in a GUI dependency group." }
}

if ($CreateTemplate) {
    $plannedFileChanges += [ordered]@{ path = "src/$normalizedPackage/__init__.py"; action = "create_if_missing"; source_template = "tools/pyside6_gui_templates/src/package_gui/__init__.py.template" }
    $plannedFileChanges += [ordered]@{ path = "src/$normalizedPackage/app.py"; action = "create_if_missing"; source_template = "tools/pyside6_gui_templates/src/package_gui/app.py.template" }
    $plannedFileChanges += [ordered]@{ path = "src/$normalizedPackage/main_window.py"; action = "create_if_missing"; source_template = "tools/pyside6_gui_templates/src/package_gui/main_window.py.template" }
    $plannedFileChanges += [ordered]@{ path = "tools/gui/check_pyside6_env.py"; action = "create_if_missing"; source_template = "tools/pyside6_gui_templates/tools/gui/check_pyside6_env.py.template" }
    $plannedFileChanges += [ordered]@{ path = "tools/gui/run_gui.ps1"; action = "create_if_missing"; source_template = "tools/pyside6_gui_templates/tools/gui/run_gui.ps1.template" }
    $plannedFileChanges += [ordered]@{ path = "tests/test_gui_import.py"; action = "create_if_missing"; source_template = "tools/pyside6_gui_templates/tests/test_gui_import.py.template" }
}

$plannedCommands = @(
    [ordered]@{ command = "Review preview JSON and create a feature branch or rollback commit before apply."; execution = "manual_review" },
    [ordered]@{ command = "python -m pip install -r requirements-gui.txt"; execution = "apply_phase_only" },
    [ordered]@{ command = "python -m unittest tests/test_gui_import.py"; execution = if ($RunSmokeTest) { "apply_phase_after_install" } else { "optional_after_apply" } }
)

$localOnlyArtifacts = @(
    ".venv/",
    "__pycache__/",
    ".pytest_cache/",
    "build/",
    "dist/",
    "*.spec"
)

$rollbackSteps = @(
    "Revert the feature branch or local commit created for GUI enablement.",
    "Remove the project-local PySide6 dependency declaration from the selected dependency surface.",
    "Delete generated GUI template files under src/$normalizedPackage, tools/gui, tests, and packaging if they were created by apply mode.",
    "Restore any lockfile changed by the project-local package manager."
)

$payload = [ordered]@{
    schema_version = 1
    check_name = "pyside6_gui_preview"
    mode = $Mode
    ok = ($blockers.Count -eq 0)
    project_root = $script:ResolvedProjectRoot
    project_root_input = $projectRootInput
    project_root_evidence = $projectRootEvidence
    python_path = $pythonPathResolved
    python_version = $pythonVersion
    package_manager = $packageManager
    dependency_style = $selectedDependencyStyle
    package_name = $normalizedPackage
    package_version = $PackageVersion
    create_template = [bool]$CreateTemplate
    run_smoke_test = [bool]$RunSmokeTest
    planned_file_changes = $plannedFileChanges
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
    Write-Output "PySide6 GUI helper preview"
    Write-Output "Project root: $($payload.project_root)"
    Write-Output "Dependency style: $($payload.dependency_style)"
    Write-Output "Planned file changes: $($payload.planned_file_changes.Count)"
    if ($payload.blockers.Count -gt 0) {
        Write-Output "Blockers:"
        foreach ($blocker in $payload.blockers) { Write-Output "  - $($blocker.code): $($blocker.message)" }
    } else {
        Write-Output "No blockers detected. Preview only; no files were changed."
    }
    Write-Output ""
    Write-Output "Structured preview JSON:"
    $payload | ConvertTo-Json -Depth 10
}

if ($payload.ok) { exit 0 }
exit 2
