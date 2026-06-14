<#
.SYNOPSIS
Collect PDF metadata and font information with Poppler.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$InputPdf,
    [string]$ReportDir = "$(Join-Path (Get-Location) '.local\user_level_document_tools\doc_quality_reports')",
    [string]$JobName,
    [string]$ConfigPath = "$(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')",
    [string]$PopplerBinDir
)

$ErrorActionPreference = 'Stop'

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
        try {
            $candidateExists = Test-Path -LiteralPath $candidate -ErrorAction Stop
        } catch { }
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
function Invoke-ToolCapture {
    param([Parameter(Mandatory=$true)][string]$ToolName, [Parameter(Mandatory=$true)][string[]]$Arguments, [string]$BinDir)
    $exe = Resolve-ToolPath -ToolName $ToolName -BinDir $BinDir
    if ($null -eq $exe) {
        return [ordered]@{ tool = $ToolName; available = $false; exit_code = $null; output = ''; error = 'tool not found on PATH or PopplerBinDir' }
    }
    try {
        $output = & $exe @Arguments 2>&1
        $code = $LASTEXITCODE
        return [ordered]@{ tool = $ToolName; available = $true; path = $exe; exit_code = $code; output = (($output | ForEach-Object { [string]$_ }) -join "`n"); error = $null }
    } catch {
        return [ordered]@{ tool = $ToolName; available = $true; path = $exe; exit_code = 1; output = ''; error = $_.Exception.Message }
    }
}

$config = Read-Config -Path $ConfigPath
if ([string]::IsNullOrWhiteSpace($PopplerBinDir) -and $config -and $config.poppler_bin_dir) { $PopplerBinDir = [string]$config.poppler_bin_dir }
$inputItem = Get-Item -LiteralPath $InputPdf -ErrorAction Stop
if ([string]::IsNullOrWhiteSpace($JobName)) { $JobName = [System.IO.Path]::GetFileNameWithoutExtension($inputItem.Name) }
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$pdfInfo = Invoke-ToolCapture -ToolName 'pdfinfo' -Arguments @($inputItem.FullName) -BinDir $PopplerBinDir
$pdfFonts = Invoke-ToolCapture -ToolName 'pdffonts' -Arguments @($inputItem.FullName) -BinDir $PopplerBinDir

$pageCount = $null
$pageSize = $null
if ($pdfInfo.output -match '(?m)^Pages:\s+(\d+)') { $pageCount = [int]$Matches[1] }
if ($pdfInfo.output -match '(?m)^Page\s+size:\s+(.+)$') { $pageSize = $Matches[1].Trim() }
$fontLines = @()
if ($pdfFonts.output) { $fontLines = $pdfFonts.output -split "`r?`n" | Where-Object { $_.Trim() -ne '' } }
$fontDataLines = @()
if ($fontLines.Count -gt 2) { $fontDataLines = $fontLines | Select-Object -Skip 2 }

$result = [ordered]@{
    job_name = $JobName
    input_pdf = $inputItem.FullName
    generated_at = (Get-Date).ToString('o')
    poppler_bin_dir = $PopplerBinDir
    page_count = $pageCount
    page_size = $pageSize
    pdfinfo = $pdfInfo
    pdffonts = $pdfFonts
    font_row_count = $fontDataLines.Count
}

$jsonPath = Join-Path $ReportDir ($JobName + '_pdf_info.json')
$mdPath = Join-Path $ReportDir ($JobName + '_pdf_info.md')
$infoTxt = Join-Path $ReportDir ($JobName + '_pdfinfo.txt')
$fontsTxt = Join-Path $ReportDir ($JobName + '_pdffonts.txt')
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $jsonPath -Encoding UTF8
$pdfInfo.output | Set-Content -LiteralPath $infoTxt -Encoding UTF8
$pdfFonts.output | Set-Content -LiteralPath $fontsTxt -Encoding UTF8

$lines = @(
    '# PDF Metadata and Font Report',
    '',
    "- Job: $JobName",
    "- Input PDF: $($inputItem.FullName)",
    "- Poppler bin dir: $PopplerBinDir",
    "- Page count: $pageCount",
    "- Page size: $pageSize",
    "- Font rows: $($fontDataLines.Count)",
    "- JSON: $jsonPath",
    "- pdfinfo raw: $infoTxt",
    "- pdffonts raw: $fontsTxt"
)
if (-not $pdfInfo.available) { $lines += ''; $lines += "WARNING: pdfinfo not available: $($pdfInfo.error)" }
if (-not $pdfFonts.available) { $lines += ''; $lines += "WARNING: pdffonts not available: $($pdfFonts.error)" }
$lines | Set-Content -LiteralPath $mdPath -Encoding UTF8

Write-Host "Wrote: $jsonPath"
Write-Host "Wrote: $mdPath"
if (($pdfInfo.available -and $pdfInfo.exit_code -eq 0) -or ($pdfFonts.available -and $pdfFonts.exit_code -eq 0)) { exit 0 }
exit 1
