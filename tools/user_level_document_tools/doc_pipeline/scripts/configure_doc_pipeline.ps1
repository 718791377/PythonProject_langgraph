<#
.SYNOPSIS
Create or update the document pipeline local config file.
#>
[CmdletBinding()]
param(
    [string]$ConfigPath = "$(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')",
    [string]$PopplerBinDir,
    [string]$AcrobatExe,
    [string]$PythonExe,
    [int]$DefaultDpi = 200,
    [int]$FinalReviewDpi = 300,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

function Resolve-ExistingFileOrEmpty {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return '' }
    try { if (Test-Path -LiteralPath $Path -PathType Leaf) { return (Get-Item -LiteralPath $Path).FullName } } catch { }
    return $Path
}
function Resolve-ExistingDirOrEmpty {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return '' }
    try { if (Test-Path -LiteralPath $Path -PathType Container) { return (Get-Item -LiteralPath $Path).FullName } } catch { }
    return $Path
}

$parent = Split-Path -Parent $ConfigPath
if (-not [string]::IsNullOrWhiteSpace($parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
if ((Test-Path -LiteralPath $ConfigPath) -and -not $Force) {
    throw "Config already exists: $ConfigPath. Use -Force to overwrite."
}

if ([string]::IsNullOrWhiteSpace($AcrobatExe)) {
    foreach ($p in @('C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe','C:\Program Files\Adobe\Acrobat\Acrobat.exe','C:\Program Files (x86)\Adobe\Acrobat DC\Acrobat\Acrobat.exe')) {
        if (Test-Path -LiteralPath $p -PathType Leaf) { $AcrobatExe = $p; break }
    }
}
if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    $py = Get-Command python -ErrorAction SilentlyContinue
    if ($py) { $PythonExe = $py.Source }
}

$config = [ordered]@{
    poppler_bin_dir = Resolve-ExistingDirOrEmpty -Path $PopplerBinDir
    acrobat_exe = Resolve-ExistingFileOrEmpty -Path $AcrobatExe
    python_exe = Resolve-ExistingFileOrEmpty -Path $PythonExe
    default_dpi = $DefaultDpi
    final_review_dpi = $FinalReviewDpi
    word_com_requires_interactive_desktop = $true
    safe_output_roots = @('$(Get-Location)\result','$(Get-Location)\intermediate')
    development_asset_roots = @('$(Resolve-Path (Join-Path $PSScriptRoot '..'))','$(Join-Path (Get-Location) 'config\doc_pipeline')','$(Join-Path (Get-Location) '.venv')')
    python_packages_dir = '$(Join-Path $PSScriptRoot '..\python_packages')'
    updated_at = (Get-Date).ToString('o')
}
$config | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ConfigPath -Encoding UTF8
Write-Host "Wrote: $ConfigPath"
