<#
.SYNOPSIS
Detect local tools for the Word COM + Acrobat Pro + Poppler document pipeline.
#>
[CmdletBinding()]
param(
    [string]$ReportDir = "$(Join-Path (Get-Location) '.local\user_level_document_tools\doc_quality_reports')",
    [string]$JsonPath,
    [string]$MarkdownPath,
    [string]$ConfigPath = "$(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')",
    [string]$PopplerBinDir,
    [switch]$ProbeCom
)

$ErrorActionPreference = 'Stop'

function Read-Config {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path -LiteralPath $Path)) { return $null }
    try { return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json) } catch { return $null }
}

function Get-CommandInfo {
    param([Parameter(Mandatory=$true)][string]$Name, [string]$BinDir)
    if (-not [string]::IsNullOrWhiteSpace($BinDir)) {
        $candidate = Join-Path $BinDir $Name
        $candidateExists = $false
        try { $candidateExists = Test-Path -LiteralPath $candidate -ErrorAction Stop } catch { $candidateExists = $false }
        if (-not $candidateExists -and -not $candidate.EndsWith('.exe')) {
            $candidate = $candidate + '.exe'
            try { $candidateExists = Test-Path -LiteralPath $candidate -ErrorAction Stop } catch { $candidateExists = $false }
        }
        if ($candidateExists) {
            try {
                return [ordered]@{ name = $Name; source = (Get-Item -LiteralPath $candidate -ErrorAction Stop).FullName; command_type = 'Application' }
            } catch { }
        }
    }
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -eq $cmd) { return $null }
    return [ordered]@{ name = $Name; source = $cmd.Source; command_type = [string]$cmd.CommandType }
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

function Invoke-VersionProbe {
    param([string]$Exe, [string[]]$Args)
    if ([string]::IsNullOrWhiteSpace($Exe)) { return $null }
    try {
        $out = & $Exe @Args 2>&1 | Select-Object -First 5
        return (($out | ForEach-Object { [string]$_ }) -join "`n")
    } catch {
        return "version probe failed: $($_.Exception.Message)"
    }
}

$config = Read-Config -Path $ConfigPath
if ([string]::IsNullOrWhiteSpace($PopplerBinDir) -and $config -and $config.poppler_bin_dir) { $PopplerBinDir = [string]$config.poppler_bin_dir }

New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
if ([string]::IsNullOrWhiteSpace($JsonPath)) { $JsonPath = Join-Path $ReportDir 'tool_detection_report.json' }
if ([string]::IsNullOrWhiteSpace($MarkdownPath)) { $MarkdownPath = Join-Path $ReportDir 'tool_detection_report.md' }

$programFiles = ${env:ProgramFiles}
$programFilesX86 = ${env:ProgramFiles(x86)}
$tools = @()

$winwordCmd = Get-CommandInfo -Name 'winword.exe'
$wordReg = $null
try { $wordReg = Get-ItemProperty -LiteralPath 'Registry::HKEY_CLASSES_ROOT\Word.Application\CurVer' -ErrorAction SilentlyContinue } catch { $wordReg = $null }
$wordComStatus = 'not_probed'
$wordVersion = $null
if ($ProbeCom) {
    $word = $null
    try {
        $word = New-Object -ComObject Word.Application
        $word.Visible = $false
        $wordVersion = [string]$word.Version
        $wordComStatus = 'available'
    } catch {
        $wordComStatus = "failed: $($_.Exception.Message)"
    } finally {
        if ($null -ne $word) {
            try { $word.Quit() | Out-Null } catch { }
            try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null } catch { }
        }
    }
}
$wordInstalled = [bool]($winwordCmd -or $wordReg)
$wordUsable = if ($ProbeCom) { ($wordComStatus -eq 'available') } else { $null }
$tools += [ordered]@{
    name = 'Microsoft Word'
    capability = 'DOCX open check and DOCX to PDF via COM'
    installed = [bool]$wordInstalled
    usable = $wordUsable
    command = $winwordCmd
    registry_curver = if ($wordReg) { [string]$wordReg.'(default)' } else { $null }
    probe_status = $wordComStatus
    version = $wordVersion
}

$acrobatCmd = Get-CommandInfo -Name 'Acrobat.exe'
$acrobatPaths = @()
if ($config -and $config.acrobat_exe) { $acrobatPaths += [string]$config.acrobat_exe }
$acrobatPaths += @(
    (Join-Path $programFiles 'Adobe\Acrobat DC\Acrobat\Acrobat.exe'),
    (Join-Path $programFiles 'Adobe\Acrobat\Acrobat.exe'),
    (Join-Path $programFilesX86 'Adobe\Acrobat DC\Acrobat\Acrobat.exe'),
    (Join-Path $programFilesX86 'Adobe\Acrobat\Acrobat.exe')
)
$acrobatPath = if ($acrobatCmd) { $acrobatCmd.source } else { Test-PathList -Paths $acrobatPaths }
$tools += [ordered]@{
    name = 'Adobe Acrobat Pro'
    capability = 'PDF to DOCX, OCR, Acrobat Action Wizard workflows'
    installed = [bool]$acrobatPath
    usable = [bool]$acrobatPath
    command = if ($acrobatCmd) { $acrobatCmd } else { $null }
    path = $acrobatPath
    probe_status = if ($acrobatPath) { 'found' } else { 'not_found' }
    note = 'Desktop-assisted conversion is expected; downstream checks are automated.'
}

foreach ($name in @('pdfinfo','pdffonts','pdftoppm','pdftocairo')) {
    $cmd = Get-CommandInfo -Name $name -BinDir $PopplerBinDir
    $version = if ($cmd) { Invoke-VersionProbe -Exe $cmd.source -Args @('-v') } else { $null }
    $tools += [ordered]@{
        name = $name
        capability = 'Poppler PDF metadata/font/render utility'
        installed = [bool]$cmd
        usable = [bool]$cmd
        command = $cmd
        version = $version
        probe_status = if ($cmd) { 'found' } else { 'not_found' }
    }
}

$pyCmd = Get-CommandInfo -Name 'python'
if ($config -and $config.python_exe -and (Test-Path -LiteralPath ([string]$config.python_exe))) {
    $pyCmd = [ordered]@{ name = 'python'; source = (Get-Item -LiteralPath ([string]$config.python_exe)).FullName; command_type = 'Application' }
}
$pyVersion = if ($pyCmd) { Invoke-VersionProbe -Exe $pyCmd.source -Args @('--version') } else { $null }
$tools += [ordered]@{
    name = 'Python'
    capability = 'Contact sheet and helper report scripts'
    installed = [bool]$pyCmd
    usable = [bool]$pyCmd
    command = $pyCmd
    version = $pyVersion
    probe_status = if ($pyCmd) { 'found' } else { 'not_found' }
}

$pillowAvailable = $false
$pillowVersion = $null
$pythonPackagesDir = if ($config -and $config.python_packages_dir) { [string]$config.python_packages_dir } else { '$(Join-Path $PSScriptRoot '..\python_packages')' }
if ($pyCmd) {
    $oldPythonPath = $env:PYTHONPATH
    if (Test-Path -LiteralPath $pythonPackagesDir) {
        if ([string]::IsNullOrWhiteSpace($oldPythonPath)) { $env:PYTHONPATH = $pythonPackagesDir } else { $env:PYTHONPATH = $pythonPackagesDir + ';' + $oldPythonPath }
    }
    try {
        $pillowOut = & $pyCmd.source -c "import PIL; print(PIL.__version__)" 2>&1
        $pillowAvailable = ($LASTEXITCODE -eq 0)
        $pillowVersion = (($pillowOut | ForEach-Object { [string]$_ }) -join "`n")
    } catch {
        $pillowAvailable = $false
        $pillowVersion = $_.Exception.Message
    } finally {
        $env:PYTHONPATH = $oldPythonPath
    }
}
$tools += [ordered]@{
    name = 'Python Pillow'
    capability = 'Required by build_contact_sheet.py for PNG contact sheets'
    installed = [bool]$pillowAvailable
    usable = [bool]$pillowAvailable
    command = if ($pyCmd) { $pyCmd } else { $null }
    version = $pillowVersion
    probe_status = if ($pillowAvailable) { 'found' } else { 'not_found' }
    note = if ($pillowAvailable) { '' } else { 'Install Pillow or use -SkipContactSheet.' }
}

$sofficeCmd = Get-CommandInfo -Name 'soffice.exe'
$sofficePaths = @(
    (Join-Path $programFiles 'LibreOffice\program\soffice.exe'),
    (Join-Path $programFilesX86 'LibreOffice\program\soffice.exe')
)
$sofficePath = if ($sofficeCmd) { $sofficeCmd.source } else { Test-PathList -Paths $sofficePaths }
$tools += [ordered]@{
    name = 'LibreOffice'
    capability = 'Fallback DOCX to PDF conversion only'
    installed = [bool]$sofficePath
    usable = [bool]$sofficePath
    command = if ($sofficeCmd) { $sofficeCmd } else { $null }
    path = $sofficePath
    probe_status = if ($sofficePath) { 'found' } else { 'not_found' }
    note = 'Fallback only; not the final quality baseline for Word deliverables.'
}

$result = [ordered]@{
    generated_at = (Get-Date).ToString('o')
    host = $env:COMPUTERNAME
    report_dir = (Resolve-Path -LiteralPath $ReportDir).Path
    config_path = if (Test-Path -LiteralPath $ConfigPath) { (Get-Item -LiteralPath $ConfigPath).FullName } else { $null }
    poppler_bin_dir = $PopplerBinDir
    probe_com = [bool]$ProbeCom
    tools = $tools
}

$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $JsonPath -Encoding UTF8

$lines = @()
$lines += '# Document Pipeline Tool Detection Report'
$lines += ''
$lines += "- Generated at: $($result.generated_at)"
$lines += "- Host: $($result.host)"
$lines += "- Config path: $($result.config_path)"
$lines += "- Poppler bin dir: $PopplerBinDir"
$lines += "- COM probe enabled: $($result.probe_com)"
$lines += ''
$lines += '| Tool | Installed | Usable | Status | Path / Command | Notes |'
$lines += '|---|---:|---:|---|---|---|'
foreach ($t in $tools) {
    $path = ''
    if ($t.command -and $t.command.source) { $path = $t.command.source } elseif ($t.path) { $path = $t.path }
    $note = if ($t.note) { $t.note } elseif ($t.version) { $t.version } else { '' }
    $lines += "| $($t.name) | $($t.installed) | $($t.usable) | $($t.probe_status) | $path | $note |"
}
$lines += ''
$lines += '## Raw JSON'
$lines += ''
$lines += "JSON report: $JsonPath"
$lines | Set-Content -LiteralPath $MarkdownPath -Encoding UTF8

Write-Host "Wrote: $JsonPath"
Write-Host "Wrote: $MarkdownPath"
