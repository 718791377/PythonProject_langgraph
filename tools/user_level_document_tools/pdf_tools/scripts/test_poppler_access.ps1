<#
.SYNOPSIS
Test whether the configured Poppler tools are accessible and executable.

.DESCRIPTION
This script is intentionally separate from general tool detection. It focuses on
the common Windows case where Poppler is installed but the current host cannot
read or execute the configured bin directory.
#>
[CmdletBinding()]
param(
    [string]$ConfigPath = "$(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')",
    [string]$PopplerBinDir,
    [string]$ReportDir = "$(Join-Path (Get-Location) '.local\user_level_document_tools\doc_quality_reports')",
    [string]$JsonPath,
    [string]$MarkdownPath
)

$ErrorActionPreference = 'Stop'

function Read-Config {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $null }
    try {
        if (Test-Path -LiteralPath $Path -ErrorAction Stop) {
            return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json)
        }
    } catch {
        return $null
    }
    return $null
}

function Test-Tool {
    param(
        [Parameter(Mandatory=$true)][string]$ToolName,
        [Parameter(Mandatory=$true)][string]$BinDir
    )
    $candidate = Join-Path $BinDir $ToolName
    $exists = $false
    $testPathError = $null
    $invokeOutput = ''
    $invokeError = $null
    $exitCode = $null

    try {
        $exists = Test-Path -LiteralPath $candidate -PathType Leaf -ErrorAction Stop
    } catch {
        $testPathError = $_.Exception.Message
    }

    if ($exists) {
        try {
            $out = & $candidate -v 2>&1
            $exitCode = $LASTEXITCODE
            $invokeOutput = (($out | ForEach-Object { [string]$_ }) -join "`n")
        } catch {
            $invokeError = $_.Exception.Message
        }
    } else {
        # Try a direct invocation anyway so access-denied or command-resolution
        # behavior is visible in the report.
        try {
            $out = & $candidate -v 2>&1
            $exitCode = $LASTEXITCODE
            $invokeOutput = (($out | ForEach-Object { [string]$_ }) -join "`n")
        } catch {
            $invokeError = $_.Exception.Message
        }
    }

    $versionOnErrorStream = (-not [string]::IsNullOrWhiteSpace($invokeError) -and $invokeError -match 'version\s+\d')
    $accessible = ($exists -and ([string]::IsNullOrWhiteSpace($invokeError) -or $versionOnErrorStream))
    return [ordered]@{
        tool = $ToolName
        candidate = $candidate
        exists = [bool]$exists
        test_path_error = $testPathError
        executable = [bool]$accessible
        exit_code = $exitCode
        invoke_output = $invokeOutput
        invoke_error = $invokeError
    }
}

$config = Read-Config -Path $ConfigPath
if ([string]::IsNullOrWhiteSpace($PopplerBinDir) -and $config -and $config.poppler_bin_dir) {
    $PopplerBinDir = [string]$config.poppler_bin_dir
}
if ([string]::IsNullOrWhiteSpace($PopplerBinDir)) {
    throw "PopplerBinDir is empty. Pass -PopplerBinDir or set poppler_bin_dir in $ConfigPath."
}

New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
if ([string]::IsNullOrWhiteSpace($JsonPath)) { $JsonPath = Join-Path $ReportDir 'poppler_access_report.json' }
if ([string]::IsNullOrWhiteSpace($MarkdownPath)) { $MarkdownPath = Join-Path $ReportDir 'poppler_access_report.md' }

$tools = @('pdfinfo.exe','pdffonts.exe','pdftoppm.exe','pdftocairo.exe')
$results = @()
foreach ($tool in $tools) {
    $results += Test-Tool -ToolName $tool -BinDir $PopplerBinDir
}
$okCount = @($results | Where-Object { $_.executable }).Count

$payload = [ordered]@{
    generated_at = (Get-Date).ToString('o')
    config_path = $ConfigPath
    poppler_bin_dir = $PopplerBinDir
    expected_count = $tools.Count
    executable_count = $okCount
    all_executable = ($okCount -eq $tools.Count)
    results = $results
}
$payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $JsonPath -Encoding UTF8

$lines = @()
$lines += '# Poppler Access Report'
$lines += ''
$lines += "- Generated at: $($payload.generated_at)"
$lines += "- Config path: $ConfigPath"
$lines += "- Poppler bin dir: $PopplerBinDir"
$lines += "- Executable tools: $okCount / $($tools.Count)"
$lines += "- All executable: $($payload.all_executable)"
$lines += ''
$lines += '| Tool | Exists | Executable | Test-Path error | Invoke error/output |'
$lines += '|---|---:|---:|---|---|'
foreach ($r in $results) {
    $detail = if ($r.invoke_error) { $r.invoke_error } elseif ($r.invoke_output) { ($r.invoke_output -replace "`r?`n", '<br>') } else { '' }
    $lines += "| $($r.tool) | $($r.exists) | $($r.executable) | $($r.test_path_error) | $detail |"
}
if ($okCount -ne $tools.Count) {
    $lines += ''
    $lines += '## Recommended action'
    $lines += ''
    $lines += '- If this report was run from a constrained host, retry from a normal interactive desktop PowerShell or CMD session.'
    $lines += '- If the configured WinGet package path remains inaccessible, install or copy Poppler to an accessible development path such as `C:\Tools\poppler\Library\bin` or another user-approved tools directory, then rerun `configure_doc_pipeline.ps1 -PopplerBinDir <path> -Force`.'
}
$lines += ''
$lines += "JSON report: $JsonPath"
$lines | Set-Content -LiteralPath $MarkdownPath -Encoding UTF8

Write-Host "Wrote: $JsonPath"
Write-Host "Wrote: $MarkdownPath"
if ($okCount -eq $tools.Count) { exit 0 }
exit 2
