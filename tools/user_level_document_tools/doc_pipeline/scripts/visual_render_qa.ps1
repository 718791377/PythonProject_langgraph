<#
.SYNOPSIS
Run optional/strict visual rendering QA through pdftoppm, pdf2image, and soffice.
#>
[CmdletBinding(DefaultParameterSetName='Pdf')]
param(
    [Parameter(ParameterSetName='Pdf', Mandatory=$true)][string]$InputPdf,
    [Parameter(ParameterSetName='Docx', Mandatory=$true)][string]$InputDocx,
    [string]$JobName,
    [ValidateRange(50,600)][int]$Dpi = 200,
    [string[]]$Backends = @('pdftoppm','pdf2image','soffice'),
    [string[]]$RequireBackends = @(),
    [string]$ConfigPath = "$(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')",
    [string]$PopplerBinDir,
    [string]$PythonExe,
    [string]$SofficeExe,
    [string]$OutputRoot = "$(Join-Path (Get-Location) '.local\user_level_document_tools\visual_render_qa')",
    [switch]$KeepIntermediatePdf
)

$ErrorActionPreference = 'Stop'
$scriptDir = $PSScriptRoot

function Read-Config {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path -LiteralPath $Path)) { return $null }
    try { return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json) } catch { return $null }
}

function Resolve-ToolPath {
    param([Parameter(Mandatory=$true)][string]$ToolName, [string]$BinDir)
    if (-not [string]::IsNullOrWhiteSpace($BinDir)) {
        $candidate = Join-Path $BinDir $ToolName
        $candidateExists = $false
        try { $candidateExists = Test-Path -LiteralPath $candidate -ErrorAction Stop } catch { }
        if (-not $candidateExists -and -not $candidate.EndsWith('.exe')) {
            $candidate = $candidate + '.exe'
            try { $candidateExists = Test-Path -LiteralPath $candidate -ErrorAction Stop } catch { $candidateExists = $false }
        }
        if ($candidateExists) {
            try { return (Get-Item -LiteralPath $candidate -ErrorAction Stop).FullName } catch { }
        }
    }
    $cmd = Get-Command $ToolName -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}

function Add-BackendResult {
    param(
        [System.Collections.ArrayList]$Results,
        [string]$Backend,
        [bool]$Installed,
        [bool]$Usable,
        [bool]$Required,
        [string]$Status,
        [string]$Path,
        [string]$Version,
        [string]$Notes,
        [Nullable[int]]$ExitCode,
        [string]$ReportJson,
        [string]$ReportMd,
        [string[]]$ArtifactPaths
    )
    $normalizedArtifacts = @()
    if ($null -ne $ArtifactPaths) { $normalizedArtifacts = @($ArtifactPaths) }
    [void]$Results.Add([ordered]@{
        backend = $Backend
        installed = $Installed
        usable = $Usable
        required = $Required
        status = $Status
        path = $Path
        version = $Version
        notes = $Notes
        exit_code = $ExitCode
        report_json = $ReportJson
        report_md = $ReportMd
        artifact_paths = $normalizedArtifacts
    })
}

function Normalize-BackendList {
    param([string[]]$Values)
    $result = @()
    foreach ($value in @($Values)) {
        if ([string]::IsNullOrWhiteSpace($value)) { continue }
        foreach ($part in ([string]$value -split ',')) {
            $normalized = $part.Trim().ToLowerInvariant()
            if (-not [string]::IsNullOrWhiteSpace($normalized) -and $result -notcontains $normalized) {
                $result += $normalized
            }
        }
    }
    return @($result)
}

$config = Read-Config -Path $ConfigPath
if ([string]::IsNullOrWhiteSpace($PopplerBinDir) -and $config -and $config.poppler_bin_dir) { $PopplerBinDir = [string]$config.poppler_bin_dir }
if ([string]::IsNullOrWhiteSpace($PythonExe) -and $config -and $config.python_exe) { $PythonExe = [string]$config.python_exe }
if ([string]::IsNullOrWhiteSpace($SofficeExe) -and $config -and $config.soffice_exe) { $SofficeExe = [string]$config.soffice_exe }
if ([string]::IsNullOrWhiteSpace($SofficeExe) -and $config -and $config.libreoffice_exe) { $SofficeExe = [string]$config.libreoffice_exe }
if ($config -and $config.visual_qa_default_dpi -and -not $PSBoundParameters.ContainsKey('Dpi')) { $Dpi = [int]$config.visual_qa_default_dpi }
if ($config -and $config.visual_qa_default_backends -and -not $PSBoundParameters.ContainsKey('Backends')) { $Backends = @($config.visual_qa_default_backends | ForEach-Object { [string]$_ }) }
if ($config -and $config.visual_qa_require_backends -and -not $PSBoundParameters.ContainsKey('RequireBackends')) { $RequireBackends = @($config.visual_qa_require_backends | ForEach-Object { [string]$_ }) }
if ($config -and $config.visual_qa_output_root -and -not $PSBoundParameters.ContainsKey('OutputRoot')) { $OutputRoot = [string]$config.visual_qa_output_root }

$inputKind = if ($PSCmdlet.ParameterSetName -eq 'Docx') { 'docx' } else { 'pdf' }
$inputPath = if ($inputKind -eq 'docx') { (Get-Item -LiteralPath $InputDocx -ErrorAction Stop).FullName } else { (Get-Item -LiteralPath $InputPdf -ErrorAction Stop).FullName }
if ([string]::IsNullOrWhiteSpace($JobName)) { $JobName = [System.IO.Path]::GetFileNameWithoutExtension($inputPath) }

$jobRoot = Join-Path $OutputRoot $JobName
$reportDir = Join-Path $jobRoot 'reports'
$artifactDir = Join-Path $jobRoot 'artifacts'
$pdfDir = Join-Path $jobRoot 'intermediate_pdf'
New-Item -ItemType Directory -Force -Path $reportDir, $artifactDir, $pdfDir | Out-Null
$jsonPath = Join-Path $reportDir ($JobName + '_visual_render_qa.json')
$mdPath = Join-Path $reportDir ($JobName + '_visual_render_qa.md')
$started = (Get-Date).ToString('o')
$backendResults = [System.Collections.ArrayList]::new()
$warnings = @()
$errors = @()
$selected = @(Normalize-BackendList -Values $Backends)
$required = @(Normalize-BackendList -Values $RequireBackends)
$effectivePdf = if ($inputKind -eq 'pdf') { $inputPath } else { $null }

if ($inputKind -eq 'docx' -and $selected -contains 'soffice') {
    $sofficeReportDir = Join-Path $reportDir 'soffice'
    $sofficeOutDir = Join-Path $pdfDir 'soffice'
    $args = @{
        InputDocx = $inputPath
        OutputDir = $sofficeOutDir
        ReportDir = $sofficeReportDir
        JobName = $JobName
        ConfigPath = $ConfigPath
    }
    if ($SofficeExe) { $args.SofficeExe = $SofficeExe }
    & (Join-Path $scriptDir 'export_docx_to_pdf_soffice.ps1') @args
    $code = $LASTEXITCODE
    $sofficeJson = Join-Path $sofficeReportDir ($JobName + '_soffice_export.json')
    $sofficeMd = Join-Path $sofficeReportDir ($JobName + '_soffice_export.md')
    $sofficePayload = $null
    if (Test-Path -LiteralPath $sofficeJson) { try { $sofficePayload = Get-Content -LiteralPath $sofficeJson -Raw | ConvertFrom-Json } catch { } }
    if ($sofficePayload -and $sofficePayload.output_pdf) { $effectivePdf = [string]$sofficePayload.output_pdf }
    $sofficeStatus = if ($sofficePayload) { [string]$sofficePayload.status } elseif ($code -eq 0) { 'ok' } else { 'unavailable' }
    $sofficePath = if ($sofficePayload) { [string]$sofficePayload.soffice_path } else { '' }
    $sofficeNotes = if ($sofficePayload) { [string]$sofficePayload.notes } else { '' }
    $sofficeArtifacts = @()
    if ($effectivePdf) { $sofficeArtifacts += $effectivePdf }
    Add-BackendResult -Results $backendResults -Backend 'soffice' -Installed ([bool]($sofficePayload -and $sofficePayload.installed)) -Usable ([bool]($sofficePayload -and $sofficePayload.usable)) -Required ($required -contains 'soffice') -Status $sofficeStatus -Path $sofficePath -Version '' -Notes $sofficeNotes -ExitCode $code -ReportJson $sofficeJson -ReportMd $sofficeMd -ArtifactPaths $sofficeArtifacts
} elseif ($inputKind -eq 'docx') {
    $warnings += 'DOCX visual QA needs a PDF intermediate. Select soffice or provide a PDF input for pdftoppm/pdf2image.'
}

if ($selected -contains 'pdftoppm') {
    $pdftoppm = Resolve-ToolPath -ToolName 'pdftoppm' -BinDir $PopplerBinDir
    if (-not $effectivePdf) {
        Add-BackendResult -Results $backendResults -Backend 'pdftoppm' -Installed ([bool]$pdftoppm) -Usable $false -Required ($required -contains 'pdftoppm') -Status 'skipped' -Path $pdftoppm -Version '' -Notes 'No effective PDF was available to render.' -ExitCode $null -ReportJson '' -ReportMd '' -ArtifactPaths @()
    } elseif (-not $pdftoppm) {
        Add-BackendResult -Results $backendResults -Backend 'pdftoppm' -Installed $false -Usable $false -Required ($required -contains 'pdftoppm') -Status 'unavailable' -Path '' -Version '' -Notes 'pdftoppm was not found on PATH or PopplerBinDir.' -ExitCode $null -ReportJson '' -ReportMd '' -ArtifactPaths @()
    } else {
        $pdftoppmDir = Join-Path $artifactDir 'pdftoppm'
        $pdftoppmReportDir = Join-Path $reportDir 'pdftoppm'
        & (Join-Path $scriptDir 'render_pdf_poppler.ps1') -InputPdf $effectivePdf -OutputDir $pdftoppmDir -ReportDir $pdftoppmReportDir -JobName ($JobName + '_pdftoppm') -Dpi $Dpi -Renderer pdftoppm -ConfigPath $ConfigPath -PopplerBinDir $PopplerBinDir
        $code = $LASTEXITCODE
        $files = @(Get-ChildItem -LiteralPath $pdftoppmDir -Filter '*.png' -File -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
        $pdftoppmStatus = if ($code -eq 0) { 'ok' } else { 'failed' }
        Add-BackendResult -Results $backendResults -Backend 'pdftoppm' -Installed $true -Usable ($code -eq 0) -Required ($required -contains 'pdftoppm') -Status $pdftoppmStatus -Path $pdftoppm -Version '' -Notes '' -ExitCode $code -ReportJson (Join-Path $pdftoppmReportDir ($JobName + '_pdftoppm_render.json')) -ReportMd (Join-Path $pdftoppmReportDir ($JobName + '_pdftoppm_render.md')) -ArtifactPaths $files
    }
}

if ($selected -contains 'pdf2image') {
    $python = $PythonExe
    if ([string]::IsNullOrWhiteSpace($python)) {
        $pyCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($pyCmd) { $python = $pyCmd.Source }
    }
    $pdf2imageScript = Join-Path $scriptDir 'render_pdf_pdf2image.py'
    if (-not $effectivePdf) {
        Add-BackendResult -Results $backendResults -Backend 'pdf2image' -Installed ([bool]$python) -Usable $false -Required ($required -contains 'pdf2image') -Status 'skipped' -Path $python -Version '' -Notes 'No effective PDF was available to render.' -ExitCode $null -ReportJson '' -ReportMd '' -ArtifactPaths @()
    } elseif (-not $python) {
        Add-BackendResult -Results $backendResults -Backend 'pdf2image' -Installed $false -Usable $false -Required ($required -contains 'pdf2image') -Status 'unavailable' -Path '' -Version '' -Notes 'Python was not found for pdf2image.' -ExitCode $null -ReportJson '' -ReportMd '' -ArtifactPaths @()
    } else {
        $pdf2imageDir = Join-Path $artifactDir 'pdf2image'
        $pdf2imageReportDir = Join-Path $reportDir 'pdf2image'
        $args = @(
            $pdf2imageScript,
            '--input-pdf', $effectivePdf,
            '--output-dir', $pdf2imageDir,
            '--report-dir', $pdf2imageReportDir,
            '--job-name', ($JobName + '_pdf2image'),
            '--dpi', [string]$Dpi
        )
        if ($PopplerBinDir) { $args += @('--poppler-bin-dir', $PopplerBinDir) }
        if ($config -and $config.python_packages_dir) { $args += @('--python-packages-dir', [string]$config.python_packages_dir) }
        & $python @args
        $code = $LASTEXITCODE
        $pdf2imageJson = Join-Path $pdf2imageReportDir ($JobName + '_pdf2image_pdf2image_render.json')
        $pdf2imageMd = Join-Path $pdf2imageReportDir ($JobName + '_pdf2image_pdf2image_render.md')
        $pdf2imagePayload = $null
        if (Test-Path -LiteralPath $pdf2imageJson) { try { $pdf2imagePayload = Get-Content -LiteralPath $pdf2imageJson -Raw | ConvertFrom-Json } catch { } }
        $files = if ($pdf2imagePayload -and $pdf2imagePayload.rendered_files) { @($pdf2imagePayload.rendered_files | ForEach-Object { [string]$_ }) } else { @() }
        $pdf2imageStatus = if ($pdf2imagePayload) { [string]$pdf2imagePayload.status } elseif ($code -eq 0) { 'ok' } else { 'unavailable' }
        $pdf2imageNotes = if ($pdf2imagePayload) { [string]$pdf2imagePayload.notes } else { '' }
        Add-BackendResult -Results $backendResults -Backend 'pdf2image' -Installed ([bool]($pdf2imagePayload -and $pdf2imagePayload.package_installed)) -Usable ($code -eq 0) -Required ($required -contains 'pdf2image') -Status $pdf2imageStatus -Path $python -Version '' -Notes $pdf2imageNotes -ExitCode $code -ReportJson $pdf2imageJson -ReportMd $pdf2imageMd -ArtifactPaths $files
    }
}

foreach ($backend in $selected) {
    if (@($backendResults | Where-Object { $_.backend -eq $backend }).Count -eq 0) {
        Add-BackendResult -Results $backendResults -Backend $backend -Installed $false -Usable $false -Required ($required -contains $backend) -Status 'skipped' -Path '' -Version '' -Notes 'Backend is not implemented for this input kind.' -ExitCode $null -ReportJson '' -ReportMd '' -ArtifactPaths @()
    }
}

$missingRequired = @()
foreach ($backend in $required) {
    $match = @($backendResults | Where-Object { $_.backend -eq $backend -and $_.status -eq 'ok' })
    if ($match.Count -eq 0) { $missingRequired += $backend }
}
if ($missingRequired.Count -gt 0) { $errors += "Required visual QA backend(s) did not pass: $($missingRequired -join ', ')" }

$okCount = @($backendResults | Where-Object { $_.status -eq 'ok' }).Count
$failedCount = @($backendResults | Where-Object { $_.status -eq 'failed' }).Count
$status = if ($missingRequired.Count -gt 0) { 'failed' } elseif ($okCount -gt 0 -and $failedCount -eq 0) { 'ok' } elseif ($okCount -gt 0) { 'partial' } else { 'partial' }

$summary = [ordered]@{
    job_name = $JobName
    input_kind = $inputKind
    input_path = $inputPath
    effective_pdf = $effectivePdf
    output_root = (Resolve-Path -LiteralPath $OutputRoot).Path
    report_dir = (Resolve-Path -LiteralPath $reportDir).Path
    artifact_dir = (Resolve-Path -LiteralPath $artifactDir).Path
    selected_backends = @($selected)
    required_backends = @($required)
    started_at = $started
    finished_at = (Get-Date).ToString('o')
    status = $status
    backend_results = @($backendResults.ToArray())
    missing_required_backends = @($missingRequired)
    warnings = @($warnings)
    errors = @($errors)
}
$summary | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

$lines = @(
    '# Visual Rendering QA Summary',
    '',
    "- Job: $JobName",
    "- Input kind: $inputKind",
    "- Input path: $inputPath",
    "- Effective PDF: $effectivePdf",
    "- Status: $status",
    "- Selected backends: $($selected -join ', ')",
    "- Required backends: $($required -join ', ')",
    "- JSON: $jsonPath",
    '',
    '| Backend | Required | Status | Path | Artifacts | Notes |',
    '|---|---:|---|---|---:|---|'
)
foreach ($r in $backendResults) {
    $lines += "| $($r.backend) | $($r.required) | $($r.status) | $($r.path) | $(@($r.artifact_paths).Count) | $($r.notes) |"
}
if ($warnings.Count -gt 0) { $lines += ''; $lines += '## Warnings'; $warnings | ForEach-Object { $lines += "- $_" } }
if ($errors.Count -gt 0) { $lines += ''; $lines += '## Errors'; $errors | ForEach-Object { $lines += "- $_" } }
$lines | Set-Content -LiteralPath $mdPath -Encoding UTF8

if (-not $KeepIntermediatePdf -and $inputKind -eq 'docx' -and $effectivePdf -and (Test-Path -LiteralPath $effectivePdf)) {
    # Keep the evidence by default through backend reports; remove only transient intermediate PDFs if explicitly outside artifacts is not safe.
}

Write-Host "Wrote: $jsonPath"
Write-Host "Wrote: $mdPath"
if ($status -eq 'failed') { exit 1 }
exit 0
