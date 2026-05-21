<#
.SYNOPSIS
Preview-first PySide6 GUI enablement helper for cross-project shared-runtime adoption.

.DESCRIPTION
The default runtime mode is `shared`: target projects receive GUI source, an adapter
placeholder, an import-only smoke test, a run wrapper, and a runtime contract pointing
at `D:\PythonProject_langgraph\.shared_runtimes\pyside6`. The helper does not install
PySide6 into consumer projects by default. Project-local dependency writes are limited
to the explicit `project-local-override` runtime mode.
#>
[CmdletBinding()]
param(
    [string]$ProjectRoot = ".",
    [ValidateSet("preview", "apply")]
    [string]$Mode = "preview",
    [ValidateSet("shared", "project-local-override")]
    [string]$RuntimeMode = "shared",
    [string]$RuntimeRoot = "D:\PythonProject_langgraph\.shared_runtimes\pyside6",
    [ValidateSet("auto", "requirements", "pyproject-extra", "group")]
    [string]$DependencyStyle = "auto",
    [string]$PythonPath = "",
    [string]$PackageVersion = "",
    [string]$OverrideReason = "",
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
    if (-not $alreadyDeclared) { $lines += $PySideSpec }
    $newContent = (($lines | Where-Object { $_ -ne $null }) -join "`r`n") + "`r`n"
    return Write-TextFileIfChanged $relativePath $newContent "create_or_update" "Project-local override: declare $PySideSpec in requirements-gui.txt." -OverwriteExisting
}

function Update-PyProjectDependency {
    param([string]$Style, [string]$PySideSpec)
    $relativePath = "pyproject.toml"
    $fullPath = Get-ProjectRelativeFullPath $relativePath
    $content = Read-TextFileIfPresent $fullPath
    if ($content -match "(?m)^\s*gui\s*=\s*\[[^\]]*PySide6[^\]]*\]") {
        return Write-TextFileIfChanged $relativePath $content "update" "Project-local override: PySide6 GUI dependency already declared." -OverwriteExisting
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
    return Write-TextFileIfChanged $relativePath $newContent "update" "Project-local override: declare $PySideSpec in pyproject.toml using $Style." -OverwriteExisting
}

function Expand-TemplateContent {
    param(
        [string]$TemplateFullPath,
        [string]$ProjectName,
        [string]$PackageName,
        [string]$WindowTitle,
        [string]$SharedRuntimeRoot,
        [string]$SharedRuntimePython,
        [string]$SharedRuntimeStatus
    )
    $content = [System.IO.File]::ReadAllText($TemplateFullPath, [System.Text.Encoding]::UTF8)
    $content = $content.Replace("{{project_name}}", $ProjectName)
    $content = $content.Replace("{{package_name}}", $PackageName)
    $content = $content.Replace("{{window_title}}", $WindowTitle)
    $content = $content.Replace("{{runtime_root}}", ($SharedRuntimeRoot -replace "\\", "\\"))
    $content = $content.Replace("{{runtime_python}}", ($SharedRuntimePython -replace "\\", "\\"))
    $content = $content.Replace("{{project_root}}", (($script:ResolvedProjectRoot) -replace "\\", "\\"))
    $content = $content.Replace("{{shared_runtime_status}}", $SharedRuntimeStatus)
    return $content
}

function Apply-TemplateFiles {
    param(
        [string]$TemplateRoot,
        [string]$ProjectName,
        [string]$PackageName,
        [string]$WindowTitle,
        [string]$SharedRuntimeRoot,
        [string]$SharedRuntimePython,
        [string]$SharedRuntimeStatus
    )
    $applied = @()
    $templateMappings = @(
        [ordered]@{ source = "src/package_gui/__init__.py.template"; target = "src/$PackageName/__init__.py" },
        [ordered]@{ source = "src/package_gui/app.py.template"; target = "src/$PackageName/app.py" },
        [ordered]@{ source = "src/package_gui/main_window.py.template"; target = "src/$PackageName/main_window.py" },
        [ordered]@{ source = "tools/gui/check_pyside6_env.py.template"; target = "tools/gui/check_pyside6_env.py" },
        [ordered]@{ source = "tools/gui/run_gui.ps1.template"; target = "tools/gui/run_gui.ps1" },
        [ordered]@{ source = "tools/gui/pyside6_runtime_contract.json.template"; target = "tools/gui/pyside6_runtime_contract.json" },
        [ordered]@{ source = "tools/gui/adapters/README.md.template"; target = "tools/gui/adapters/README.md" },
        [ordered]@{ source = "tests/test_gui_import.py.template"; target = "tests/test_gui_import.py" }
    )
    foreach ($mapping in $templateMappings) {
        $sourceFullPath = Join-Path $TemplateRoot ($mapping.source -replace "/", [System.IO.Path]::DirectorySeparatorChar)
        $content = Expand-TemplateContent $sourceFullPath $ProjectName $PackageName $WindowTitle $SharedRuntimeRoot $SharedRuntimePython $SharedRuntimeStatus
        $applied += Write-TextFileIfChanged $mapping.target $content "create_if_missing" "Create a minimal PySide6 GUI shared-runtime template file." -SourceTemplate ("tools/pyside6_gui_templates/" + $mapping.source)
    }
    return $applied
}

function Write-RollbackNote {
    param(
        [string]$ProjectName,
        [string]$RuntimeMode,
        [string]$DependencyStyle,
        [string]$PySideSpec,
        [string]$PackageName,
        [string]$SharedRuntimeRoot,
        [object[]]$AppliedChanges
    )
    $timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $changeLines = @()
    foreach ($change in $AppliedChanges) {
        $changeLines += "- $($change.status): `$($change.path)` ($($change.action))"
    }
    if ($changeLines.Count -eq 0) { $changeLines += "- no files changed" }
    $dependencyLine = if ($RuntimeMode -eq "shared") { "No PySide6 dependency was written to this consumer project." } else { "Project-local override dependency declaration: $PySideSpec via $DependencyStyle." }
    $content = @"
# PySide6 GUI rollback note

Generated at: $timestamp
Project: $ProjectName
Runtime mode: $RuntimeMode
Shared runtime root: $SharedRuntimeRoot
GUI package: $PackageName

## Dependency boundary

$dependencyLine

## Applied changes

$($changeLines -join "`r`n")

## Rollback steps

1. Revert the local commit or feature branch that introduced the GUI changes.
2. Delete generated GUI template files under `src/$PackageName/`, `tools/gui/`, and `tests/` if they were created by apply mode.
3. Keep the shared PySide6 runtime maintained by `D:\PythonProject_langgraph` unless this task explicitly provisioned or upgraded it.
4. If `project-local-override` was used, remove the project-local PySide6 dependency declaration and restore any changed lockfile.
5. Keep user-level templates and unrelated project files unchanged.
"@
    return Write-TextFileIfChanged "docs/pyside6_gui_rollback.md" $content "create_or_update" "Record the project-local rollback path for PySide6 GUI enablement." -OverwriteExisting
}

function New-PlannedCommand {
    param(
        [string]$Command,
        [string]$Execution,
        [string]$Reason,
        [bool]$AffectsLockfile = $false
    )
    return [ordered]@{
        command = $Command
        execution = $Execution
        reason = $Reason
        affects_lockfile = $AffectsLockfile
    }
}

function Get-PackageManagerCommandEvidence {
    param(
        [string]$PackageManager,
        [string]$DependencyStyle,
        [string]$PySideSpec,
        [string]$RuntimeMode,
        [string]$SharedRuntimePython,
        [bool]$RunSmokeTestRequested
    )
    if ($RuntimeMode -eq "shared") {
        return [ordered]@{
            project_package_manager = $PackageManager
            dependency_style = "none-shared-runtime"
            runtime_mode = $RuntimeMode
            dependency_declaration_spec = ""
            project_native_dependency_command = ""
            install_command = ""
            lockfile_update_command = ""
            lockfile_expectation = "Shared runtime mode does not modify project dependency files or lockfiles."
            smoke_test_command = "`"$SharedRuntimePython`" tools/gui/check_pyside6_env.py --project-root . --json"
            run_smoke_test_requested = $RunSmokeTestRequested
            policy = "Use the shared runtime for import-only verification; provision it separately with ensure-shared-pyside6-runtime.ps1."
        }
    }

    $projectNativeDependencyCommand = ""
    $installCommand = ""
    $lockfileUpdateCommand = ""
    $lockfileExpectation = "Review the target project's dependency and lockfile workflow before claiming project_local_override_ready."
    if ($DependencyStyle -eq "requirements") {
        $projectNativeDependencyCommand = "Edit requirements-gui.txt to include $PySideSpec"
        $installCommand = "python -m pip install -r requirements-gui.txt"
        $lockfileUpdateCommand = "Review the target project's pip lock workflow if one exists."
    } elseif ($DependencyStyle -eq "pyproject-extra") {
        $projectNativeDependencyCommand = "Edit pyproject.toml [project.optional-dependencies].gui to include $PySideSpec"
        $installCommand = "python -m pip install -e `".[gui]`""
        $lockfileUpdateCommand = "Update the target project's pyproject lockfile only if its package manager requires one."
    } elseif ($DependencyStyle -eq "group") {
        $projectNativeDependencyCommand = "Edit pyproject.toml [dependency-groups].gui to include $PySideSpec"
        $installCommand = "python -m pip install -e ."
        $lockfileUpdateCommand = "Use the target project's dependency-group-aware lockfile workflow after reviewing pyproject.toml changes."
    }
    return [ordered]@{
        project_package_manager = $PackageManager
        dependency_style = $DependencyStyle
        runtime_mode = $RuntimeMode
        dependency_declaration_spec = $PySideSpec
        project_native_dependency_command = $projectNativeDependencyCommand
        install_command = $installCommand
        lockfile_update_command = $lockfileUpdateCommand
        lockfile_expectation = $lockfileExpectation
        smoke_test_command = "python -m unittest tests/test_gui_import.py"
        run_smoke_test_requested = $RunSmokeTestRequested
        policy = "Project-local PySide6 installs are exceptions and require an override reason, version evidence, and rollback evidence."
    }
}

$blockers = @()
$warnings = @()
$info = @("Preview-first helper: preview creates no files, installs no packages, and launches no GUI window.")
$projectRootInput = $ProjectRoot
$script:ResolvedProjectRoot = $null
$templateRoot = Get-HelperTemplateRoot
$sharedRuntimeRoot = [System.IO.Path]::GetFullPath($RuntimeRoot)
$sharedRuntimePython = Join-Path $sharedRuntimeRoot ".venv\Scripts\python.exe"
$sharedRuntimeJson = Join-Path $sharedRuntimeRoot "runtime.json"
$sharedRuntimeStatus = if (Test-Path -LiteralPath $sharedRuntimePython -PathType Leaf) { "present" } else { "missing" }
if (Test-Path -LiteralPath $sharedRuntimeJson -PathType Leaf) {
    try {
        $runtimeRecord = Get-Content -LiteralPath $sharedRuntimeJson -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($runtimeRecord.import_only_verified -eq $true) { $sharedRuntimeStatus = "import_only_verified" }
    } catch {
        $warnings += "shared_runtime_metadata_unreadable: $($_.Exception.Message)"
    }
}

if ($RuntimeMode -eq "shared" -and $Mode -eq "apply" -and $sharedRuntimeStatus -eq "missing") {
    $blockers += New-Blocker "shared_runtime_missing" "Shared PySide6 runtime is missing at $sharedRuntimePython. Run ensure-shared-pyside6-runtime.ps1 as a separate approved maintenance task."
}
if ($RuntimeMode -eq "project-local-override" -and $Mode -eq "apply" -and [string]::IsNullOrWhiteSpace($OverrideReason)) {
    $blockers += New-Blocker "project_local_override_reason_required" "Project-local override requires an explicit -OverrideReason."
}

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
        $warnings += "dependency_style_unknown: shared runtime mode can still create GUI files, but project-local override needs a supported dependency surface."
    }
}

$selectedDependencyStyle = $DependencyStyle
if ($DependencyStyle -eq "auto") { $selectedDependencyStyle = $detectedDependencyStyle }
if ($selectedDependencyStyle -eq "unknown" -or [string]::IsNullOrWhiteSpace($selectedDependencyStyle)) { $selectedDependencyStyle = "unknown" }
if ($RuntimeMode -eq "project-local-override" -and $Mode -eq "apply" -and $selectedDependencyStyle -eq "unknown") {
    $blockers += New-Blocker "dependency_style_unknown_for_project_local_override" "Project-local override apply mode requires a supported dependency style."
}

$rootLeaf = if ($script:ResolvedProjectRoot) { Split-Path -Leaf $script:ResolvedProjectRoot } else { "project" }
$basePackage = if ([string]::IsNullOrWhiteSpace($PackageName)) { "$rootLeaf`_gui" } else { $PackageName }
$normalizedPackage = Normalize-PackageName $basePackage
$pySideSpec = if ([string]::IsNullOrWhiteSpace($PackageVersion)) { "PySide6" } else { "PySide6==$PackageVersion" }
$windowTitle = "$rootLeaf GUI"

$plannedFileChanges = @()
if ($RuntimeMode -eq "project-local-override") {
    if ($selectedDependencyStyle -eq "requirements") {
        $plannedFileChanges += New-FileChange "requirements-gui.txt" "create_or_update" "Project-local override: declare $pySideSpec in a requirements surface."
    } elseif ($selectedDependencyStyle -eq "pyproject-extra" -or $selectedDependencyStyle -eq "group") {
        $plannedFileChanges += New-FileChange "pyproject.toml" "update" "Project-local override: declare $pySideSpec in a GUI dependency surface."
    }
}

if ($CreateTemplate) {
    $plannedFileChanges += New-FileChange "tools/gui/pyside6_runtime_contract.json" "create_if_missing" "Create a shared PySide6 runtime contract." "planned" "tools/pyside6_gui_templates/tools/gui/pyside6_runtime_contract.json.template"
    $plannedFileChanges += New-FileChange "src/$normalizedPackage/__init__.py" "create_if_missing" "Create a minimal PySide6 GUI template file." "planned" "tools/pyside6_gui_templates/src/package_gui/__init__.py.template"
    $plannedFileChanges += New-FileChange "src/$normalizedPackage/app.py" "create_if_missing" "Create a minimal PySide6 GUI template file." "planned" "tools/pyside6_gui_templates/src/package_gui/app.py.template"
    $plannedFileChanges += New-FileChange "src/$normalizedPackage/main_window.py" "create_if_missing" "Create a minimal PySide6 GUI template file." "planned" "tools/pyside6_gui_templates/src/package_gui/main_window.py.template"
    $plannedFileChanges += New-FileChange "tools/gui/check_pyside6_env.py" "create_if_missing" "Create a shared-runtime PySide6 environment checker." "planned" "tools/pyside6_gui_templates/tools/gui/check_pyside6_env.py.template"
    $plannedFileChanges += New-FileChange "tools/gui/run_gui.ps1" "create_if_missing" "Create a visible-GUI launcher that uses the shared runtime Python." "planned" "tools/pyside6_gui_templates/tools/gui/run_gui.ps1.template"
    $plannedFileChanges += New-FileChange "tools/gui/adapters/README.md" "create_if_missing" "Create a GUI adapter boundary placeholder." "planned" "tools/pyside6_gui_templates/tools/gui/adapters/README.md.template"
    $plannedFileChanges += New-FileChange "tests/test_gui_import.py" "create_if_missing" "Create an import-only GUI smoke test." "planned" "tools/pyside6_gui_templates/tests/test_gui_import.py.template"
}
if ($Mode -eq "apply") {
    $plannedFileChanges += New-FileChange "docs/pyside6_gui_rollback.md" "create_or_update" "Record rollback instructions for generated GUI files and runtime contract."
}

if ($Mode -eq "apply" -and $CreateTemplate) {
    if (-not (Test-Path -LiteralPath $templateRoot -PathType Container)) {
        $blockers += New-Blocker "template_root_missing" "Template root was not found: $templateRoot"
    } else {
        foreach ($relativeTemplate in @(
            "src/package_gui/__init__.py.template",
            "src/package_gui/app.py.template",
            "src/package_gui/main_window.py.template",
            "tools/gui/check_pyside6_env.py.template",
            "tools/gui/run_gui.ps1.template",
            "tools/gui/pyside6_runtime_contract.json.template",
            "tools/gui/adapters/README.md.template",
            "tests/test_gui_import.py.template"
        )) {
            $candidate = Join-Path $templateRoot ($relativeTemplate -replace "/", [System.IO.Path]::DirectorySeparatorChar)
            if (-not [System.IO.File]::Exists($candidate)) {
                $blockers += New-Blocker "template_file_missing" "Template file was not found: $relativeTemplate"
            }
        }
    }
}

$commandEvidence = Get-PackageManagerCommandEvidence $packageManager $selectedDependencyStyle $pySideSpec $RuntimeMode $sharedRuntimePython ([bool]$RunSmokeTest)
$plannedCommands = @()
$plannedCommands += New-PlannedCommand "Review preview JSON and create a feature branch or rollback commit before apply." "manual_review" "Preserve a rollback boundary before project-local GUI writes."
if ($RuntimeMode -eq "shared") {
    $plannedCommands += New-PlannedCommand "tools/pyside6_gui_helpers/ensure-shared-pyside6-runtime.ps1 -Mode verify -RuntimeRoot `"$sharedRuntimeRoot`" -Json" "preflight_or_after_apply" "Verify shared runtime import-only status without launching a visible GUI window."
} else {
    if (-not [string]::IsNullOrWhiteSpace($commandEvidence.project_native_dependency_command)) {
        $plannedCommands += New-PlannedCommand $commandEvidence.project_native_dependency_command "optional_manual_project_local_override" "Use the target project's native dependency manager instead of editing multiple dependency surfaces."
    }
    if (-not [string]::IsNullOrWhiteSpace($commandEvidence.install_command)) {
        $plannedCommands += New-PlannedCommand $commandEvidence.install_command "optional_project_env_only_after_apply" "Install or sync PySide6 only inside the explicit target project environment." $true
    }
    if (-not [string]::IsNullOrWhiteSpace($commandEvidence.lockfile_update_command)) {
        $plannedCommands += New-PlannedCommand $commandEvidence.lockfile_update_command "optional_project_native_lockfile_update" "Update only the target project's lockfile when its package manager requires it." $true
    }
}
$smokeExecution = if ($RunSmokeTest) { "planned_import_only_no_visible_gui" } else { "optional_after_apply" }
$plannedCommands += New-PlannedCommand $commandEvidence.smoke_test_command $smokeExecution "Verify import-only behavior without launching a visible GUI window."

$localOnlyArtifacts = @(
    ".shared_runtimes/pyside6/.venv/",
    ".shared_runtimes/pyside6/logs/",
    "__pycache__/",
    ".pytest_cache/",
    "build/",
    "dist/",
    "*.spec"
)

$rollbackSteps = @(
    "Revert the feature branch or local commit created for GUI enablement.",
    "Delete generated GUI template files under src/$normalizedPackage, tools/gui, tests, and packaging if they were created by apply mode.",
    "Keep the shared PySide6 runtime untouched unless this task explicitly provisioned or upgraded it.",
    "If project-local override was used, remove the PySide6 dependency declaration and restore any changed lockfile."
)

$appliedFileChanges = @()
$rollbackNote = $null
$smokeTest = [ordered]@{ requested = [bool]$RunSmokeTest; executed = $false; status = "not_requested"; details = "" }

if ($Mode -eq "apply" -and $blockers.Count -eq 0) {
    if ($RuntimeMode -eq "project-local-override") {
        if ($selectedDependencyStyle -eq "requirements") {
            $appliedFileChanges += Update-RequirementsGui $pySideSpec
        } elseif ($selectedDependencyStyle -eq "pyproject-extra" -or $selectedDependencyStyle -eq "group") {
            $appliedFileChanges += Update-PyProjectDependency $selectedDependencyStyle $pySideSpec
        }
    }
    if ($CreateTemplate) {
        $appliedFileChanges += Apply-TemplateFiles $templateRoot $rootLeaf $normalizedPackage $windowTitle $sharedRuntimeRoot $sharedRuntimePython $sharedRuntimeStatus
    }
    $rollbackChange = Write-RollbackNote $rootLeaf $RuntimeMode $selectedDependencyStyle $pySideSpec $normalizedPackage $sharedRuntimeRoot $appliedFileChanges
    $appliedFileChanges += $rollbackChange
    $rollbackNote = $rollbackChange.path
    if ($RunSmokeTest) {
        $smokeTest.status = "planned_not_executed"
        $smokeTest.details = "Apply mode writes contract/template files only. Run the import-only smoke command from planned_commands after shared runtime verification."
    }
}

$payload = [ordered]@{
    schema_version = 3
    check_name = "pyside6_gui_helper"
    mode = $Mode
    apply_mode = ($Mode -eq "apply")
    ok = ($blockers.Count -eq 0)
    project_root = $script:ResolvedProjectRoot
    project_root_input = $projectRootInput
    project_root_evidence = $projectRootEvidence
    runtime_mode = $RuntimeMode
    shared_runtime_root = $sharedRuntimeRoot
    shared_runtime_python = $sharedRuntimePython
    shared_runtime_status = $sharedRuntimeStatus
    python_path = $PythonPath
    python_version = $null
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
    package_manager_command_evidence = $commandEvidence
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
    Write-Output "Runtime mode: $($payload.runtime_mode)"
    Write-Output "Shared runtime status: $($payload.shared_runtime_status)"
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
