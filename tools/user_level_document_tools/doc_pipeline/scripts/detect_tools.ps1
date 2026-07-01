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
    [string]$PythonExe,
    [string]$SofficeExe,
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

function Join-OptionalPath {
    param([string]$Base, [string]$Child)
    if ([string]::IsNullOrWhiteSpace($Base)) { return $null }
    return (Join-Path $Base $Child)
}

function Invoke-VersionProbe {
    param([string]$Exe, [string[]]$VersionArgs)
    if ([string]::IsNullOrWhiteSpace($Exe)) { return $null }
    try {
        # Poppler and some native CLIs write version information to stderr.
        # Capture stdout/stderr directly so script-level Stop preference and
        # PowerShell native-command error wrapping do not turn version text into
        # misleading "version probe failed" evidence.
        $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
        $startInfo.FileName = $Exe
        $startInfo.Arguments = (($VersionArgs | ForEach-Object {
            if ($_ -match '[\s"]') { '"' + ($_ -replace '"', '\"') + '"' } else { $_ }
        }) -join ' ')
        $startInfo.RedirectStandardOutput = $true
        $startInfo.RedirectStandardError = $true
        $startInfo.UseShellExecute = $false
        $startInfo.CreateNoWindow = $true
        $process = [System.Diagnostics.Process]::Start($startInfo)
        $stdout = $process.StandardOutput.ReadToEnd()
        $stderr = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        $combined = @($stdout, $stderr) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
        return ((($combined -join "`n") -split "`r?`n") | Select-Object -First 5) -join "`n"
    } catch {
        return "version probe failed: $($_.Exception.Message)"
    }
}

$config = Read-Config -Path $ConfigPath
if ([string]::IsNullOrWhiteSpace($PopplerBinDir) -and $config -and $config.poppler_bin_dir) { $PopplerBinDir = [string]$config.poppler_bin_dir }
if ([string]::IsNullOrWhiteSpace($PythonExe) -and $config -and $config.python_exe) { $PythonExe = [string]$config.python_exe }
if ([string]::IsNullOrWhiteSpace($SofficeExe) -and $config -and $config.soffice_exe) { $SofficeExe = [string]$config.soffice_exe }
if ([string]::IsNullOrWhiteSpace($SofficeExe) -and $config -and $config.libreoffice_exe) { $SofficeExe = [string]$config.libreoffice_exe }

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
    (Join-OptionalPath $programFiles 'Adobe\Acrobat DC\Acrobat\Acrobat.exe'),
    (Join-OptionalPath $programFiles 'Adobe\Acrobat\Acrobat.exe'),
    (Join-OptionalPath $programFilesX86 'Adobe\Acrobat DC\Acrobat\Acrobat.exe'),
    (Join-OptionalPath $programFilesX86 'Adobe\Acrobat\Acrobat.exe')
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
    $version = if ($cmd) { Invoke-VersionProbe -Exe $cmd.source -VersionArgs @('-v') } else { $null }
    $tools += [ordered]@{
        name = $name
        backend = $name
        capability = 'Poppler PDF metadata/font/render utility'
        installed = [bool]$cmd
        usable = [bool]$cmd
        command = $cmd
        path = if ($cmd) { $cmd.source } else { $null }
        version = $version
        probe_status = if ($cmd) { 'found' } else { 'not_found' }
        note = ''
        notes = ''
    }
}

$pyCmd = Get-CommandInfo -Name 'python'
if ($PythonExe -and (Test-Path -LiteralPath $PythonExe)) {
    $pyCmd = [ordered]@{ name = 'python'; source = (Get-Item -LiteralPath $PythonExe).FullName; command_type = 'Application' }
}
$pyVersion = if ($pyCmd) { Invoke-VersionProbe -Exe $pyCmd.source -VersionArgs @('--version') } else { $null }
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
$pythonPackagesDir = if ($config -and $config.python_packages_dir) { [string]$config.python_packages_dir } else { Join-Path $PSScriptRoot '..\python_packages' }
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
    notes = if ($pillowAvailable) { '' } else { 'Install Pillow or use -SkipContactSheet.' }
}

$pdf2imageAvailable = $false
$pdf2imageVersion = $null
$pdf2imageProbeStatus = 'python_not_found'
$pdf2imageNote = ''
$pdftoppmForPdf2Image = Get-CommandInfo -Name 'pdftoppm' -BinDir $PopplerBinDir
if ($pyCmd) {
    $oldPythonPath = $env:PYTHONPATH
    if (Test-Path -LiteralPath $pythonPackagesDir) {
        if ([string]::IsNullOrWhiteSpace($oldPythonPath)) { $env:PYTHONPATH = $pythonPackagesDir } else { $env:PYTHONPATH = $pythonPackagesDir + ';' + $oldPythonPath }
    }
    try {
        $pdf2imageOut = & $pyCmd.source -c "import importlib.metadata as m; print(m.version('pdf2image'))" 2>&1
        $pdf2imageAvailable = ($LASTEXITCODE -eq 0)
        $pdf2imageVersion = (($pdf2imageOut | ForEach-Object { [string]$_ }) -join "`n")
        if ($pdf2imageAvailable -and $pdftoppmForPdf2Image) {
            $pdf2imageProbeStatus = 'found'
        } elseif ($pdf2imageAvailable) {
            $pdf2imageProbeStatus = 'poppler_missing'
            $pdf2imageNote = 'pdf2image is installed, but Windows rendering still requires a Poppler backend such as pdftoppm.'
        } else {
            $pdf2imageProbeStatus = 'package_not_found'
        }
    } catch {
        $pdf2imageAvailable = $false
        $pdf2imageVersion = $_.Exception.Message
        $pdf2imageProbeStatus = 'package_not_found'
    } finally {
        $env:PYTHONPATH = $oldPythonPath
    }
}
$tools += [ordered]@{
    name = 'pdf2image'
    backend = 'pdf2image'
    capability = 'Python PDF rendering wrapper backed by Poppler'
    installed = [bool]$pdf2imageAvailable
    usable = [bool]($pdf2imageAvailable -and $pdftoppmForPdf2Image)
    command = if ($pyCmd) { $pyCmd } else { $null }
    path = if ($pyCmd) { $pyCmd.source } else { $null }
    version = $pdf2imageVersion
    probe_status = $pdf2imageProbeStatus
    note = $pdf2imageNote
    notes = $pdf2imageNote
    poppler_backend_path = if ($pdftoppmForPdf2Image) { $pdftoppmForPdf2Image.source } else { $null }
}

$sofficeCmd = Get-CommandInfo -Name 'soffice.exe'
if ($null -eq $sofficeCmd) { $sofficeCmd = Get-CommandInfo -Name 'soffice' }
if ($null -eq $sofficeCmd) { $sofficeCmd = Get-CommandInfo -Name 'libreoffice' }
$sofficePaths = @(
    $SofficeExe,
    (Join-OptionalPath $programFiles 'LibreOffice\program\soffice.exe'),
    (Join-OptionalPath $programFilesX86 'LibreOffice\program\soffice.exe')
)
$sofficePath = if ($sofficeCmd) { $sofficeCmd.source } else { Test-PathList -Paths $sofficePaths }
$sofficeVersion = if ($sofficePath) { Invoke-VersionProbe -Exe $sofficePath -VersionArgs @('--version') } else { $null }
$tools += [ordered]@{
    name = 'LibreOffice'
    backend = 'soffice'
    capability = 'Fallback DOCX to PDF conversion only'
    installed = [bool]$sofficePath
    usable = [bool]$sofficePath
    command = if ($sofficeCmd) { $sofficeCmd } else { $null }
    path = $sofficePath
    version = $sofficeVersion
    probe_status = if ($sofficePath) { 'found' } else { 'not_found' }
    note = 'Fallback only; not the final quality baseline for Word deliverables.'
    notes = 'Fallback only; not the final quality baseline for Word deliverables.'
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
