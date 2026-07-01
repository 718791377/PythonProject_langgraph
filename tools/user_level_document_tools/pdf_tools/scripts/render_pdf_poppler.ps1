<#
.SYNOPSIS
Render a PDF to PNG page images using Poppler.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$InputPdf,
    [string]$OutputDir = "$(Join-Path (Get-Location) '.local\user_level_document_tools\renders')",
    [string]$Prefix,
    [ValidateRange(50,600)][int]$Dpi = 200,
    [ValidateSet('pdftoppm','pdftocairo')][string]$Renderer = 'pdftoppm',
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
$config = Read-Config -Path $ConfigPath
if ([string]::IsNullOrWhiteSpace($PopplerBinDir) -and $config -and $config.poppler_bin_dir) { $PopplerBinDir = [string]$config.poppler_bin_dir }
$inputItem = Get-Item -LiteralPath $InputPdf -ErrorAction Stop
if ([string]::IsNullOrWhiteSpace($JobName)) { $JobName = [System.IO.Path]::GetFileNameWithoutExtension($inputItem.Name) }
if ([string]::IsNullOrWhiteSpace($Prefix)) { $Prefix = $JobName + '_page' }
New-Item -ItemType Directory -Force -Path $OutputDir, $ReportDir | Out-Null

$exe = Resolve-ToolPath -ToolName $Renderer -BinDir $PopplerBinDir
if ($null -eq $exe) { throw "$Renderer not found on PATH or PopplerBinDir" }

$prefixPath = Join-Path $OutputDir $Prefix
$started = (Get-Date).ToString('o')
$oldErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    $output = & $exe -png -r $Dpi $inputItem.FullName $prefixPath 2>&1
    $exitCode = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $oldErrorActionPreference
}
$files = Get-ChildItem -LiteralPath $OutputDir -Filter ($Prefix + '*.png') -File -ErrorAction SilentlyContinue | Sort-Object Name

$result = [ordered]@{
    job_name = $JobName
    input_pdf = $inputItem.FullName
    renderer = $Renderer
    renderer_path = $exe
    poppler_bin_dir = $PopplerBinDir
    dpi = $Dpi
    output_dir = (Resolve-Path -LiteralPath $OutputDir).Path
    prefix = $Prefix
    started_at = $started
    finished_at = (Get-Date).ToString('o')
    exit_code = $exitCode
    tool_output = (($output | ForEach-Object { [string]$_ }) -join "`n")
    rendered_count = $files.Count
    rendered_files = @($files | ForEach-Object { $_.FullName })
}

$jsonPath = Join-Path $ReportDir ($JobName + '_render.json')
$mdPath = Join-Path $ReportDir ($JobName + '_render.md')
$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

$lines = @(
    '# PDF Render Report',
    '',
    "- Job: $JobName",
    "- Input PDF: $($inputItem.FullName)",
    "- Renderer: $Renderer",
    "- Renderer path: $exe",
    "- DPI: $Dpi",
    "- Output directory: $($result.output_dir)",
    "- Rendered pages: $($files.Count)",
    "- JSON: $jsonPath"
)
if ($exitCode -ne 0) { $lines += ''; $lines += "WARNING: renderer exit code $exitCode"; $lines += '```'; $lines += $result.tool_output; $lines += '```' }
$lines | Set-Content -LiteralPath $mdPath -Encoding UTF8

Write-Host "Wrote: $jsonPath"
Write-Host "Wrote: $mdPath"
Write-Host "Rendered files: $($files.Count)"
if ($exitCode -eq 0 -and $files.Count -gt 0) { exit 0 }
exit 1
