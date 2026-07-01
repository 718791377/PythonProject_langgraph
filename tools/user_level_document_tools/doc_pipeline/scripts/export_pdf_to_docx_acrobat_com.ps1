<#
.SYNOPSIS
Attempt a desktop Acrobat Pro PDF-to-DOCX export through Acrobat COM.

.DESCRIPTION
This helper is a local desktop-assisted test surface for Acrobat Pro. Acrobat
Pro may reject scripted export depending on local licensing, Protected Mode,
security, or installed COM support. In that case, the generated report records
the failure and the operator should use Acrobat Pro's desktop Export PDF UI.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$InputPdf,
    [Parameter(Mandatory=$true)][string]$OutputDocx,
    [string]$ReportDir = "$(Join-Path (Get-Location) '.local\user_level_document_tools\doc_quality_reports')",
    [string]$JobName = "acrobat_pdf_to_word_test"
)

$ErrorActionPreference = 'Stop'

New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$outputParent = Split-Path -Parent $OutputDocx
if (-not [string]::IsNullOrWhiteSpace($outputParent)) {
    New-Item -ItemType Directory -Force -Path $outputParent | Out-Null
}

$inputItem = Get-Item -LiteralPath $InputPdf -ErrorAction Stop
$outputFull = [System.IO.Path]::GetFullPath($OutputDocx)
$jsonPath = Join-Path $ReportDir ($JobName + '_report.json')
$mdPath = Join-Path $ReportDir ($JobName + '_report.md')

$status = [ordered]@{
    job_name = $JobName
    input_pdf = $inputItem.FullName
    output_docx = $outputFull
    started_at = (Get-Date).ToString('o')
    finished_at = $null
    acrobat_app_created = $false
    pddoc_created = $false
    open_result = 'not_started'
    export_result = 'not_started'
    output_exists = $false
    output_length = $null
    conversion_id_attempted = 'com.adobe.acrobat.docx'
    warnings = @()
    errors = @()
}

$app = $null
$pdDoc = $null
$success = $false

try {
    $app = New-Object -ComObject AcroExch.App
    $status.acrobat_app_created = $true
    $pdDoc = New-Object -ComObject AcroExch.PDDoc
    $status.pddoc_created = $true

    $opened = $pdDoc.Open($inputItem.FullName)
    if (-not $opened) {
        $status.open_result = 'failed'
        throw "Acrobat PDDoc.Open returned false."
    }
    $status.open_result = 'ok'

    $js = $pdDoc.GetJSObject()
    if ($null -eq $js) {
        $status.export_result = 'failed'
        throw "Acrobat GetJSObject returned null."
    }

    # Acrobat JavaScript saveAs conversion IDs are installation dependent.
    # This is the documented practical attempt for Word DOCX export.
    $js.SaveAs($outputFull, 'com.adobe.acrobat.docx')
    Start-Sleep -Seconds 2
    if (Test-Path -LiteralPath $outputFull -PathType Leaf) {
        $out = Get-Item -LiteralPath $outputFull
        $status.output_exists = $true
        $status.output_length = $out.Length
        $status.export_result = 'ok'
        $success = $true
    } else {
        $status.export_result = 'failed'
        throw "Acrobat saveAs returned without creating the DOCX output."
    }
} catch {
    if ($status.open_result -eq 'not_started') { $status.open_result = 'failed' }
    if ($status.export_result -eq 'not_started') { $status.export_result = 'failed' }
    $status.errors += $_.Exception.Message
} finally {
    if ($null -ne $pdDoc) {
        try { $pdDoc.Close() | Out-Null } catch { $status.warnings += "PDDoc close failed: $($_.Exception.Message)" }
        try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pdDoc) | Out-Null } catch { }
    }
    if ($null -ne $app) {
        try { $app.Exit() | Out-Null } catch { $status.warnings += "Acrobat app exit failed: $($_.Exception.Message)" }
        try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null } catch { }
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
    $status.finished_at = (Get-Date).ToString('o')
    $status | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

    $lines = @()
    $lines += '# Acrobat PDF to Word Export Test Report'
    $lines += ''
    $lines += "- Job: $JobName"
    $lines += "- Input PDF: $($status.input_pdf)"
    $lines += "- Output DOCX: $($status.output_docx)"
    $lines += "- Acrobat app created: $($status.acrobat_app_created)"
    $lines += "- PDDoc created: $($status.pddoc_created)"
    $lines += "- Open result: $($status.open_result)"
    $lines += "- Export result: $($status.export_result)"
    $lines += "- Output exists: $($status.output_exists)"
    $lines += "- Output length: $($status.output_length)"
    $lines += "- Conversion ID attempted: $($status.conversion_id_attempted)"
    $lines += "- JSON: $jsonPath"
    if ($status.warnings.Count -gt 0) {
        $lines += ''
        $lines += '## Warnings'
        foreach ($w in $status.warnings) { $lines += "- $w" }
    }
    if ($status.errors.Count -gt 0) {
        $lines += ''
        $lines += '## Errors'
        foreach ($e in $status.errors) { $lines += "- $e" }
        $lines += ''
        $lines += '## Manual fallback'
        $lines += ''
        $fallbackDocxDir = Join-Path (Get-Location) '.local\user_level_document_tools\converted\docx_from_pdf'
        $lines += "Open the sample PDF in Adobe Acrobat Pro, use Export PDF -> Microsoft Word -> Word Document, save the DOCX under ``$fallbackDocxDir``, then run the Word COM + Poppler post-check."
    }
    $lines | Set-Content -LiteralPath $mdPath -Encoding UTF8
}

Write-Host "Wrote: $jsonPath"
Write-Host "Wrote: $mdPath"
if ($success) { Write-Host "Wrote: $outputFull"; exit 0 }
exit 1
