<#
.SYNOPSIS
Open a DOCX with Microsoft Word COM in read-only mode and export it to PDF.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$InputDocx,
    [string]$OutputPdf,
    [string]$ReportDir = "$(Join-Path (Get-Location) '.local\user_level_document_tools\doc_quality_reports')",
    [string]$JobName,
    [switch]$Visible
)

$ErrorActionPreference = 'Stop'

function Get-FullPathForOutput {
    param([string]$Path)
    $parent = Split-Path -Parent $Path
    if (-not [string]::IsNullOrWhiteSpace($parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    return [System.IO.Path]::GetFullPath($Path)
}

$inputItem = Get-Item -LiteralPath $InputDocx -ErrorAction Stop
if ([string]::IsNullOrWhiteSpace($JobName)) { $JobName = [System.IO.Path]::GetFileNameWithoutExtension($inputItem.Name) }
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
if ([string]::IsNullOrWhiteSpace($OutputPdf)) {
    $OutputPdf = Join-Path '$(Join-Path (Get-Location) '.local\user_level_document_tools\converted\pdf')' ($JobName + '.pdf')
}
$outputPdfFull = Get-FullPathForOutput -Path $OutputPdf
$jsonPath = Join-Path $ReportDir ($JobName + '_word_export_status.json')
$mdPath = Join-Path $ReportDir ($JobName + '_word_export_status.md')

$status = [ordered]@{
    job_name = $JobName
    input_docx = $inputItem.FullName
    output_pdf = $outputPdfFull
    started_at = (Get-Date).ToString('o')
    finished_at = $null
    word_version = $null
    open_result = 'not_started'
    export_result = 'not_started'
    page_count = $null
    warnings = @()
    errors = @()
}

$word = $null
$doc = $null
$success = $false
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = [bool]$Visible
    $word.DisplayAlerts = 0
    $status.word_version = [string]$word.Version

    $readOnly = $true
    $confirmConversions = $false
    $addToRecentFiles = $false
    $doc = $word.Documents.Open($inputItem.FullName, $confirmConversions, $readOnly, $addToRecentFiles)
    $status.open_result = 'ok'

    try { $status.page_count = [int]$doc.ComputeStatistics(2) } catch { $status.warnings += "page count failed: $($_.Exception.Message)" }

    # wdExportFormatPDF = 17; wdExportOptimizeForPrint = 0; wdExportAllDocument = 0
    $doc.ExportAsFixedFormat($outputPdfFull, 17, $false, 0, 0)
    $status.export_result = 'ok'
    $success = $true
} catch {
    if ($status.open_result -eq 'not_started') { $status.open_result = 'failed' }
    if ($status.export_result -eq 'not_started') { $status.export_result = 'failed' }
    $status.errors += $_.Exception.Message
} finally {
    if ($null -ne $doc) {
        try { $doc.Close([ref]$false) | Out-Null } catch { $status.warnings += "document close failed: $($_.Exception.Message)" }
        try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) | Out-Null } catch { }
    }
    if ($null -ne $word) {
        try { $word.Quit() | Out-Null } catch { $status.warnings += "word quit failed: $($_.Exception.Message)" }
        try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null } catch { }
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
    $status.finished_at = (Get-Date).ToString('o')
    $status | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

    $lines = @(
        '# Word DOCX Check and PDF Export Status',
        '',
        "- Job: $JobName",
        "- Input DOCX: $($inputItem.FullName)",
        "- Output PDF: $outputPdfFull",
        "- Word version: $($status.word_version)",
        "- Open result: $($status.open_result)",
        "- Export result: $($status.export_result)",
        "- Page count: $($status.page_count)",
        "- JSON: $jsonPath"
    )
    if ($status.warnings.Count -gt 0) { $lines += ''; $lines += '## Warnings'; $status.warnings | ForEach-Object { $lines += "- $_" } }
    if ($status.errors.Count -gt 0) { $lines += ''; $lines += '## Errors'; $status.errors | ForEach-Object { $lines += "- $_" } }
    $lines | Set-Content -LiteralPath $mdPath -Encoding UTF8
}

Write-Host "Wrote: $jsonPath"
Write-Host "Wrote: $mdPath"
if ($success) { Write-Host "Wrote: $outputPdfFull"; exit 0 }
exit 1
