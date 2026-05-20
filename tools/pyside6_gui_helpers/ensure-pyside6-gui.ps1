<#
.SYNOPSIS
Preview-first PySide6 GUI enablement helper for project-local GUI adoption.

.DESCRIPTION
This helper defaults to preview mode. Preview mode inspects a target project root,
reports root/dependency/Python evidence, and emits structured JSON without creating
files, installing packages, launching visible GUI windows, or modifying global/user
configuration. Apply mode is explicit and only writes project-local dependency,
template, and rollback-note files under the verified ProjectRoot.
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
$script:Utf8NoBom = [System.Text.UTF8Encoding]::new($false)

function New-Blocker {
    param([string]$Code, [string]$Message)
    return [ordered]@{ code = $Code; message = $Message }
}

function New-FileChange {
    param(
        [string]$Path,
        [string]$Action,
        [string]$Reason,
        [string]$Status = "planned",
        [string]$SourceTemplate = ""
    )
    $change = [ordered]@{ path = $Path; action = $Action; reason = $Reason; status = $Status }
    if (-not [string]::IsNullOrWhiteSpace($SourceTemplate)) {
        $change.source_template = $SourceTemplate
    }
    return $change
}

function Normalize-PackageName {
    param([string]$Name)
    $normalized = ($Name -replace "[^A-Za-z0-9_]", "_").Trim("_")
    if ([string]::IsNullOrWhiteSpace($normalized)) { return "project_gui" }
    if ($normalized -notmatch "^[A-Za-z_]") { $normalized = "gui_$normalized" }
    return $normalized.ToLowerInvariant()
}

function Get-HelperTemplateRoot {
    $helperDirectory = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
    $toolsDirectory = Split-Path -Parent $helperDirectory
    return Join-Path $toolsDirectory "pyside6_gui_templates"
}

function Get-ProjectRelativeFullPath {
    param([string]$RelativePath)
    if (-not $script:ResolvedProjectRoot) {
        throw "Project root is not resolved."
    }
    $relativeNative = $RelativePath -replace "/", [System.IO.Path]::DirectorySeparatorChar
    $rootFull = [System.IO.Path]::GetFullPath($script:ResolvedProjectRoot)
    $targetFull = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($rootFull, $relativeNative))
    $comparison = if ($IsWindows -or $env:OS -eq "Windows_NT") { [System.StringComparison]::OrdinalIgnoreCase } else { [System.StringComparison]::Ordinal }
    $rootWithSeparator = $rootFull.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
    if (($targetFull -ne $rootFull) -and (-not $targetFull.StartsWith($rootWithSeparator, $comparison))) {
        throw "Refusing to write outside ProjectRoot: $RelativePath"
    }
    return $targetFull
}

function Read-TextFileIfPresent {
    param([string]$FullPath)
    if ([System.IO.File]::Exists($FullPath)) {
        return [System.IO.File]::ReadAllText($FullPath, [System.Text.Encoding]::UTF8)
    }
    return ""
}

function Write-TextFileIfChanged {
    param(
        [string]$RelativePath,
        [string]$Content,
        [string]$Action,
        [string]$Reason,
        [switch]$OverwriteExisting,
        [string]$SourceTemplate = ""
    )
    $fullPath = Get-ProjectRelativeFullPath $RelativePath
    $exists = [System.IO.File]::Exists($fullPath)
    if ($exists -and (-not $OverwriteExisting)) {
        return New-FileChange $RelativePath $Action $Reason "skipped_exists" $SourceTemplate
    }
    $previous = if ($exists) { Read-TextFileIfPresent $fullPath } else { $null }
    if ($exists -and $previous -eq $Content) {
        return New-FileChange $RelativePath $Action $Reason "unchanged" $SourceTemplate
    }
    $parent = [System.IO.Path]::GetDirectoryName($fullPath)
    if (-not [string]::IsNullOrWhiteSpace($parent)) {
        [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    }
    [System.IO.File]::WriteAllText($fullPath, $Content, $script:Utf8NoBom)
    $status = if ($exists) { "updated" } else { "created" }
    return New-FileChange $RelativePath $Action $Reason $status $SourceTemplate
}

function Update-RequirementsGui {
    param([string]$PySideSpec)
    $relativePath = "requirements-gui.txt"
    $fullPath = Get-ProjectRelativeFullPath $relativePath
    $content = Read-TextFileIfPresent $fullPath
    $lines = @()
    if (-not [string]::IsNullOrWhiteSpace($content)) {
        $lines = @($content -split "\r?\n" | Where-Object { $_ -ne "" })
    }
    $alreadyDeclared = $false
    foreach ($line in $lines) {
        if ($line.Trim() -match "^PySide6(\s*(==|~=|>=|<=|>|<|!=).*)?$") {
            $alreadyDeclared = $true
        }
    }
    if (-not $alreadyDeclared) {
        $lines += $PySideSpec
    }
    $newContent = (($lines | Where-Object { $_ -ne $null }) -join "`r`n") + "`r`n"
    return Write-TextFileIfChanged $relativePath $newContent "create_or_update" "Declare $PySideSpec in a project-local requirements surface." -OverwriteExisting
}

function Test-PyProjectGuiConflict {
    param([string]$Style)
    if ($Style -notin @("pyproject-extra", "group")) { return $null }
    $pyprojectPath = Get-ProjectRelativeFullPath "pyproject.toml"
    if (-not [System.IO.File]::Exists($pyprojectPath)) {
        return New-Blocker "pyproject_missing" "DependencyStyle $Style requires an existing pyproject.toml."
    }
    $content = Read-TextFileIfPresent $pyprojectPath
    $guiLine = [regex]::Match($content, "(?m)^\s*gui\s*=\s*\[(?<value>[^\]]*)\]")
    if ($guiLine.Success -and $guiLine.Value -notmatch "PySide6") {
        return New-Blocker "pyproject_gui_dependency_conflict" "pyproject.toml already has a gui dependency list that does not mention PySide6; review manually before apply."
    }
    return $null
}

function Update-PyProjectDependency {
    param([string]$Style, [string]$PySideSpec)
    $relativePath = "pyproject.toml"
    $fullPath = Get-ProjectRelativeFullPath $relativePath
    $content = Read-TextFileIfPresent $fullPath
    if ($content -match "(?m)^\s*gui\s*=\s*\[[^\]]*PySide6[^\]]*\]") {
        return Write-TextFileIfChanged $relativePath $content "update" "PySide6 GUI dependency already declared." -OverwriteExisting
    }

    if ($Style -eq "pyproject-extra") {
        $section = "[project.optional-dependencies]"
        $guiLine = "gui = [`"$PySideSpec`"]"
    } else {
        $section = "[dependency-groups]"
        $guiLine = "gui = [`"$PySideSpec`"]"
    }

    if ($content -match [regex]::Escape($section)) {
        $escaped = [regex]::Escape($section)
        $newContent = [regex]::Replace($content, "(?m)^$escaped\s*$", "$section`r`n$guiLine", 1)
    } else {
        $suffix = if ($content.EndsWith("`n")) { "" } else { "`r`n" }
        $newContent = $content + $suffix + "`r`n$section`r`n$guiLine`r`n"
    }
    return Write-TextFileIfChanged $relativePath $newContent "update" "Declare $PySideSpec in pyproject.toml using $Style." -OverwriteExisting
}

function Expand-TemplateContent {
    param(
        [string]$TemplateFullPath,
        [string]$ProjectName,
        [string]$PackageName,
        [string]$WindowTitle
    )
    $content = [System.IO.File]::ReadAllText($TemplateFullPath, [System.Text.Encoding]::UTF8)
    $content = $content.Replace("{{project_name}}", $ProjectName)
    $content = $content.Replace("{{package_name}}", $PackageName)
    $content = $content.Replace("{{window_title}}", $WindowTitle)
    return $content
}

function Apply-TemplateFiles {
    param(
        [string]$TemplateRoot,
        [string]$ProjectName,
        [string]$PackageName,
        [string]$WindowTitle
    )
    $applied = @()
    $templateMappings = @(
        [ordered]@{ source = "src/package_gui/__init__.py.template"; target = "src/$PackageName/__init__.py" },
        [ordered]@{ source = "src/package_gui/app.py.template"; target = "src/$PackageName/app.py" },
        [ordered]@{ source = "src/package_gui/main_window.py.template"; target = "src/$PackageName/main_window.py" },
        [ordered]@{ source = "tools/gui/check_pyside6_env.py.template"; target = "tools/gui/check_pyside6_env.py" },
        [ordered]@{ source = "tools/gui/run_gui.ps1.template"; target = "tools/gui/run_gui.ps1" },
        [ordered]@{ source = "tests/test_gui_import.py.template"; target = "tests/test_gui_import.py" }
    )
    foreach ($mapping in $templateMappings) {
        $sourceFullPath = Join-Path $TemplateRoot ($mapping.source -replace "/", [System.IO.Path]::DirectorySeparatorChar)
        $content = Expand-TemplateContent $sourceFullPath $ProjectName $PackageName $WindowTitle
        $applied += Write-TextFileIfChanged $mapping.target $content "create_if_missing" "Create a minimal PySide6 GUI template file." -SourceTemplate ("tools/pyside6_gui_templates/" + $mapping.source)
    }
    return $applied
}

function Write-RollbackNote {
    param(
        [string]$ProjectName,
        [string]$DependencyStyle,
        [string]$PySideSpec,
        [string]$PackageName,
        [object[]]$AppliedChanges
    )
    $timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $changeLines = @()
    foreach ($change in $AppliedChanges) {
        $changeLines += "- $($change.status): `$($change.path)` ($($change.action))"
    }
    if ($changeLines.Count -eq 0) { $changeLines += "- no files changed" }
    $content = @"
# PySide6 GUI rollback note

Generated at: $timestamp
Project: $ProjectName
Dependency style: $DependencyStyle
Dependency declaration: $PySideSpec
GUI package: $PackageName

## Applied changes

$($changeLines -join "`r`n")

## Rollback steps

1. Revert the local commit or feature branch that introduced the GUI changes.
2. Remove the PySide6 declaration from the selected project-local dependency surface.
3. Delete generated GUI template files under `src/$PackageName/`, `tools/gui/`, and `tests/` if they were created by apply mode.
4. Restore any project lockfile changed by a later package-manager install step.
5. Keep user-level templates and unrelated project files unchanged.
"@
    return Write-TextFileIfChanged "docs/pyside6_gui_rollback.md" $content "create_or_update" "Record the project-local rollback path for PySide6 GUI enablement." -OverwriteExisting
}

$blockers = @()
$warnings = @()
$info = @("Preview-first helper: preview creates no files, installs no packages, and launches no GUI window.")
$projectRootInput = $ProjectRoot
$script:ResolvedProjectRoot = $null
$templateRoot = Get-HelperTemplateRoot

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
if ($Mode -eq "apply" -and $selectedDependencyStyle -eq "unknown") {
    $blockers += New-Blocker "dependency_style_unknown_for_apply" "Apply mode requires a supported dependency style."
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
        $warnings += "No project .venv Python and no python command found on PATH; dependency/template apply can still proceed, but smoke tests require a project interpreter."
    }
}

if ($pythonPathResolved) {
    try {
        $pythonVersion = (& $pythonPathResolved --version 2>&1 | Select-Object -First 1).ToString()
    } catch {
        $blockers += New-Blocker "python_version_probe_failed" "Unable to run Python version probe: $($_.Exception.Message)"
    }
}

$rootLeaf = if ($script:ResolvedProjectRoot) { Split-Path -Leaf $script:ResolvedProjectRoot } else { "project" }
$basePackage = if ([string]::IsNullOrWhiteSpace($PackageName)) { "$rootLeaf`_gui" } else { $PackageName }
$normalizedPackage = Normalize-PackageName $basePackage
$pySideSpec = if ([string]::IsNullOrWhiteSpace($PackageVersion)) { "PySide6" } else { "PySide6==$PackageVersion" }
$windowTitle = "$rootLeaf GUI"

$plannedFileChanges = @()
if ($selectedDependencyStyle -eq "requirements") {
    $plannedFileChanges += New-FileChange "requirements-gui.txt" "create_or_update" "Declare $pySideSpec in a project-local requirements surface."
} elseif ($selectedDependencyStyle -eq "pyproject-extra") {
    $plannedFileChanges += New-FileChange "pyproject.toml" "update" "Declare $pySideSpec in a GUI optional dependency extra."
} elseif ($selectedDependencyStyle -eq "group") {
    $plannedFileChanges += New-FileChange "pyproject.toml" "update" "Declare $pySideSpec in a GUI dependency group."
}

if ($CreateTemplate) {
    $plannedFileChanges += New-FileChange "src/$normalizedPackage/__init__.py" "create_if_missing" "Create a minimal PySide6 GUI template file." "planned" "tools/pyside6_gui_templates/src/package_gui/__init__.py.template"
    $plannedFileChanges += New-FileChange "src/$normalizedPackage/app.py" "create_if_missing" "Create a minimal PySide6 GUI template file." "planned" "tools/pyside6_gui_templates/src/package_gui/app.py.template"
    $plannedFileChanges += New-FileChange "src/$normalizedPackage/main_window.py" "create_if_missing" "Create a minimal PySide6 GUI template file." "planned" "tools/pyside6_gui_templates/src/package_gui/main_window.py.template"
    $plannedFileChanges += New-FileChange "tools/gui/check_pyside6_env.py" "create_if_missing" "Create a project-local PySide6 environment checker." "planned" "tools/pyside6_gui_templates/tools/gui/check_pyside6_env.py.template"
    $plannedFileChanges += New-FileChange "tools/gui/run_gui.ps1" "create_if_missing" "Create a visible-GUI launcher that uses project-local Python." "planned" "tools/pyside6_gui_templates/tools/gui/run_gui.ps1.template"
    $plannedFileChanges += New-FileChange "tests/test_gui_import.py" "create_if_missing" "Create an import-only GUI smoke test." "planned" "tools/pyside6_gui_templates/tests/test_gui_import.py.template"
}
if ($Mode -eq "apply") {
    $plannedFileChanges += New-FileChange "docs/pyside6_gui_rollback.md" "create_or_update" "Record rollback instructions for generated GUI files and dependency declarations."
}

if ($Mode -eq "apply") {
    if ($CreateTemplate -and (-not (Test-Path -LiteralPath $templateRoot -PathType Container))) {
        $blockers += New-Blocker "template_root_missing" "Template root was not found: $templateRoot"
    }
    if ($CreateTemplate -and (Test-Path -LiteralPath $templateRoot -PathType Container)) {
        foreach ($relativeTemplate in @("src/package_gui/__init__.py.template", "src/package_gui/app.py.template", "src/package_gui/main_window.py.template", "tools/gui/check_pyside6_env.py.template", "tools/gui/run_gui.ps1.template", "tests/test_gui_import.py.template")) {
            $candidate = Join-Path $templateRoot ($relativeTemplate -replace "/", [System.IO.Path]::DirectorySeparatorChar)
            if (-not [System.IO.File]::Exists($candidate)) {
                $blockers += New-Blocker "template_file_missing" "Template file was not found: $relativeTemplate"
            }
        }
    }
    if ($script:ResolvedProjectRoot -and $selectedDependencyStyle -in @("pyproject-extra", "group")) {
        $pyprojectConflict = Test-PyProjectGuiConflict $selectedDependencyStyle
        if ($pyprojectConflict) { $blockers += $pyprojectConflict }
    }
}

$plannedCommands = @(
    [ordered]@{ command = "Review preview JSON and create a feature branch or rollback commit before apply."; execution = "manual_review" },
    [ordered]@{ command = "python -m pip install -r requirements-gui.txt"; execution = "optional_project_venv_only_after_apply" },
    [ordered]@{ command = "python -m unittest tests/test_gui_import.py"; execution = if ($RunSmokeTest) { "apply_phase_if_project_env_ready" } else { "optional_after_apply" } }
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

$appliedFileChanges = @()
$rollbackNote = $null
$smokeTest = [ordered]@{ requested = [bool]$RunSmokeTest; executed = $false; status = "not_requested"; details = "" }

if ($Mode -eq "apply" -and $blockers.Count -eq 0) {
    if ($selectedDependencyStyle -eq "requirements") {
        $appliedFileChanges += Update-RequirementsGui $pySideSpec
    } elseif ($selectedDependencyStyle -in @("pyproject-extra", "group")) {
        $appliedFileChanges += Update-PyProjectDependency $selectedDependencyStyle $pySideSpec
    }

    if ($CreateTemplate) {
        $appliedFileChanges += Apply-TemplateFiles $templateRoot $rootLeaf $normalizedPackage $windowTitle
    }

    $rollbackChange = Write-RollbackNote $rootLeaf $selectedDependencyStyle $pySideSpec $normalizedPackage $appliedFileChanges
    $appliedFileChanges += $rollbackChange
    $rollbackNote = $rollbackChange.path

    if ($RunSmokeTest) {
        $smokeTest.status = "planned_not_executed"
        $smokeTest.details = "Apply mode writes dependency/template files only. Install PySide6 into the project environment, then run the import smoke command from planned_commands."
    }
}

$payload = [ordered]@{
    schema_version = 2
    check_name = "pyside6_gui_helper"
    mode = $Mode
    apply_mode = ($Mode -eq "apply")
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
    applied_file_changes = $appliedFileChanges
    rollback_note = $rollbackNote
    smoke_test = $smokeTest
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
    Write-Output "PySide6 GUI helper"
    Write-Output "Project root: $($payload.project_root)"
    Write-Output "Mode: $($payload.mode)"
    Write-Output "Dependency style: $($payload.dependency_style)"
    Write-Output "Planned file changes: $($payload.planned_file_changes.Count)"
    Write-Output "Applied file changes: $($payload.applied_file_changes.Count)"
    if ($payload.blockers.Count -gt 0) {
        Write-Output "Blockers:"
        foreach ($blocker in $payload.blockers) { Write-Output "  - $($blocker.code): $($blocker.message)" }
    } elseif ($Mode -eq "preview") {
        Write-Output "No blockers detected. Preview only; no files were changed."
    } else {
        Write-Output "No blockers detected. Apply completed with project-local writes only."
    }
    Write-Output ""
    Write-Output "Structured JSON:"
    $payload | ConvertTo-Json -Depth 10
}

if ($payload.ok) { exit 0 }
exit 2
