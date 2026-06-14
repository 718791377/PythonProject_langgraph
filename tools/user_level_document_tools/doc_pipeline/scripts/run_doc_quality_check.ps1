<#
.SYNOPSIS
Run the reusable document quality-check pipeline from any consumer project.
#>
[CmdletBinding(DefaultParameterSetName='Docx')]
param(
    [Parameter(ParameterSetName='Docx', Mandatory=$true)][string]$InputDocx,
    [Parameter(ParameterSetName='Pdf', Mandatory=$true)][string]$InputPdf,
    [string]$JobName,
    [ValidateRange(50,600)][int]$Dpi = 200,
    [string]$ConfigPath,
    [string]$PopplerBinDir,
    [string]$OutputRoot,
    [string]$GuardCommand,
    [switch]$SkipContactSheet
)

$ErrorActionPreference = 'Stop'
$scriptDir = $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path (Get-Location) '.local\user_level_document_tools'
}
if ([string]::IsNullOrWhiteSpace($ConfigPath)) {
    $ConfigPath = Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json'
}
$reportDir = Join-Path $OutputRoot 'doc_quality_reports'
$pdfDir = Join-Path $OutputRoot 'converted\pdf'
$renderBase = Join-Path $OutputRoot 'renders'
New-Item -ItemType Directory -Force -Path $reportDir, $pdfDir, $renderBase | Out-Null

$pythonPackagesDir = $null
$pythonExeFromConfig = $null
if (Test-Path -LiteralPath $ConfigPath) {
    try {
        $cfg = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
        if ([string]::IsNullOrWhiteSpace($PopplerBinDir) -and $cfg.poppler_bin_dir) { $PopplerBinDir = [string]$cfg.poppler_bin_dir }
        if ($cfg.python_packages_dir) { $pythonPackagesDir = [string]$cfg.python_packages_dir }
        if ($cfg.python_exe) { $pythonExeFromConfig = [string]$cfg.python_exe }
        if ($cfg.default_dpi -and -not $PSBoundParameters.ContainsKey('Dpi')) { $Dpi = [int]$cfg.default_dpi }
    } catch { Write-Warning "Could not parse config: $ConfigPath" }
}

if ([string]::IsNullOrWhiteSpace($JobName)) {
    if ($PSCmdlet.ParameterSetName -eq 'Docx') { $JobName = [System.IO.Path]::GetFileNameWithoutExtension((Get-Item -LiteralPath $InputDocx).Name) }
    else { $JobName = [System.IO.Path]::GetFileNameWithoutExtension((Get-Item -LiteralPath $InputPdf).Name) }
}

$jobRenderDir = Join-Path $renderBase $JobName
New-Item -ItemType Directory -Force -Path $jobRenderDir | Out-Null
$guardStarted = $false
try {
    if ($GuardCommand -and (Test-Path -LiteralPath $GuardCommand)) {
        & $GuardCommand check --paths $reportDir $pdfDir $jobRenderDir
        if ($LASTEXITCODE -ne 0) { throw 'guard preflight failed' }
        & $GuardCommand model begin --reason "document quality check $JobName"
        if ($LASTEXITCODE -ne 0) { throw 'guard model begin failed' }
        $guardStarted = $true
    }

    $pdfForInspection = $null
    if ($PSCmdlet.ParameterSetName -eq 'Docx') {
        $outputPdf = Join-Path $pdfDir ($JobName + '.pdf')
        & (Join-Path $scriptDir 'word_docx_check_and_export.ps1') -InputDocx $InputDocx -OutputPdf $outputPdf -ReportDir $reportDir -JobName $JobName
        if ($LASTEXITCODE -ne 0) { throw 'Word DOCX check/export failed. Rerun from an interactive desktop PowerShell if Word COM is blocked.' }
        $pdfForInspection = $outputPdf
    } else {
        $pdfForInspection = (Get-Item -LiteralPath $InputPdf).FullName
    }

    & (Join-Path $scriptDir 'collect_pdf_info.ps1') -InputPdf $pdfForInspection -ReportDir $reportDir -JobName $JobName -ConfigPath $ConfigPath -PopplerBinDir $PopplerBinDir
    if ($LASTEXITCODE -ne 0) { Write-Warning 'PDF info collection failed or Poppler tools are missing.' }

    & (Join-Path $scriptDir 'render_pdf_poppler.ps1') -InputPdf $pdfForInspection -OutputDir $jobRenderDir -ReportDir $reportDir -JobName $JobName -Dpi $Dpi -ConfigPath $ConfigPath -PopplerBinDir $PopplerBinDir
    if ($LASTEXITCODE -ne 0) { throw 'PDF rendering failed. Install Poppler or pass -PopplerBinDir.' }

    $summaryPath = Join-Path $reportDir ($JobName + '_quality_report.md')
    @(
        '# Document Quality Check Summary','',
        "- Job: $JobName",
        "- Input type: $($PSCmdlet.ParameterSetName)",
        "- PDF inspected: $pdfForInspection",
        "- Render directory: $jobRenderDir",
        "- DPI: $Dpi",
        "- Poppler bin dir: $PopplerBinDir",
        "- Generated at: $((Get-Date).ToString('o'))"
    ) | Set-Content -LiteralPath $summaryPath -Encoding UTF8
    Write-Host "Wrote: $summaryPath"
} finally {
    if ($GuardCommand -and $guardStarted -and (Test-Path -LiteralPath $GuardCommand)) {
        & $GuardCommand model end
        & $GuardCommand verify
    }
}
