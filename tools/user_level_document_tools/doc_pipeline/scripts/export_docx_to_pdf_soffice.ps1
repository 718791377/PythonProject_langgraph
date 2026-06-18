<#
.SYNOPSIS
Export DOCX to PDF with LibreOffice/soffice and structured evidence.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$InputDocx,
    [string]$OutputDir = "$(Join-Path (Get-Location) '.local\user_level_document_tools\converted\soffice_pdf')",
    [string]$ReportDir = "$(Join-Path (Get-Location) '.local\user_level_document_tools\doc_quality_reports')",
    [string]$JobName,
    [string]$ConfigPath = "$(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')",
    [string]$SofficeExe
)

$ErrorActionPreference = 'Stop'

function Read-Config {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path -LiteralPath $Path)) { return $null }
    try { return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json) } catch { return $null }
}

function Test-PathList {
    param([string[]]$Paths)
    foreach ($p in $Paths) {
        if ([string]::IsNullOrWhiteSpace($p)) { continue }
        try {
            if (Test-Path -LiteralPath $p -ErrorAction Stop) { return (Get-Item -LiteralPath $p -ErrorAction Stop).FullName }
        } catch { }
    }
    return $null
}

function Resolve-Soffice {
    param([string]$Configured)
    if (-not [string]::IsNullOrWhiteSpace($Configured)) {
        try {
            if (Test-Path -LiteralPath $Configured -ErrorAction Stop) { return (Get-Item -LiteralPath $Configured -ErrorAction Stop).FullName }
        } catch { }
    }
    foreach ($name in @('soffice.exe','soffice','libreoffice')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }
    return Test-PathList -Paths @(
        (Join-Path ${env:ProgramFiles} 'LibreOffice\program\soffice.exe'),
        (Join-Path ${env:ProgramFiles(x86)} 'LibreOffice\program\soffice.exe')
    )
}

$config = Read-Config -Path $ConfigPath
if ([string]::IsNullOrWhiteSpace($SofficeExe) -and $config -and $config.soffice_exe) { $SofficeExe = [string]$config.soffice_exe }
if ([string]::IsNullOrWhiteSpace($SofficeExe) -and $config -and $config.libreoffice_exe) { $SofficeExe = [string]$config.libreoffice_exe }

$inputItem = Get-Item -LiteralPath $InputDocx -ErrorAction Stop
if ([string]::IsNullOrWhiteSpace($JobName)) { $JobName = [System.IO.Path]::GetFileNameWithoutExtension($inputItem.Name) }
New-Item -ItemType Directory -Force -Path $OutputDir, $ReportDir | Out-Null
$jsonPath = Join-Path $ReportDir ($JobName + '_soffice_export.json')
$mdPath = Join-Path $ReportDir ($JobName + '_soffice_export.md')
$started = (Get-Date).ToString('o')
$soffice = Resolve-Soffice -Configured $SofficeExe
$result = [ordered]@{
    job_name = $JobName
    input_docx = $inputItem.FullName
    backend = 'soffice'
    soffice_path = $soffice
    output_pdf = $null
    output_dir = (Resolve-Path -LiteralPath $OutputDir).Path
    status = 'unavailable'
    installed = [bool]$soffice
    usable = [bool]$soffice
    exit_code = 1
    started_at = $started
    finished_at = $null
    tool_output = ''
    notes = ''
    error_message = ''
}

try {
    if (-not $soffice) {
        $result.notes = 'LibreOffice/soffice is not installed or not configured. This backend is optional unless required.'
    } else {
        $oldErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        try {
            $output = & $soffice --headless --convert-to pdf --outdir $OutputDir $inputItem.FullName 2>&1
            $exitCode = $LASTEXITCODE
        } finally {
            $ErrorActionPreference = $oldErrorActionPreference
        }
        $result.exit_code = $exitCode
        $result.tool_output = (($output | ForEach-Object { [string]$_ }) -join "`n")
        $converted = Join-Path $OutputDir ([System.IO.Path]::GetFileNameWithoutExtension($inputItem.Name) + '.pdf')
        if ($exitCode -eq 0 -and (Test-Path -LiteralPath $converted)) {
            $target = Join-Path $OutputDir ($JobName + '.pdf')
            if ((Get-Item -LiteralPath $converted).FullName -ne [System.IO.Path]::GetFullPath($target)) {
                Move-Item -LiteralPath $converted -Destination $target -Force
            }
            $result.output_pdf = (Get-Item -LiteralPath $target).FullName
            $result.status = 'ok'
            $result.notes = 'Converted through LibreOffice/soffice fallback backend.'
        } else {
            $result.status = 'failed'
            $result.error_message = 'LibreOffice conversion did not produce the expected PDF.'
        }
    }
} catch {
    $result.status = 'failed'
    $result.error_message = $_.Exception.Message
} finally {
    $result.finished_at = (Get-Date).ToString('o')
    $result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $jsonPath -Encoding UTF8
    $lines = @(
        '# LibreOffice DOCX to PDF Export Report',
        '',
        "- Job: $JobName",
        "- Input DOCX: $($inputItem.FullName)",
        "- Status: $($result.status)",
        "- soffice path: $($result.soffice_path)",
        "- Output PDF: $($result.output_pdf)",
        "- JSON: $jsonPath"
    )
    if ($result.notes) { $lines += ''; $lines += "Notes: $($result.notes)" }
    if ($result.error_message) { $lines += ''; $lines += "Error: $($result.error_message)" }
    $lines | Set-Content -LiteralPath $mdPath -Encoding UTF8
}

Write-Host "Wrote: $jsonPath"
Write-Host "Wrote: $mdPath"
if ($result.status -eq 'ok') { exit 0 }
exit 1
