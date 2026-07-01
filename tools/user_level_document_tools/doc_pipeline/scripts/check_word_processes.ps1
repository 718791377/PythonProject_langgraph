<#
.SYNOPSIS
Non-destructively report Microsoft Word processes after Word COM export runs.

.DESCRIPTION
This helper is intentionally read-only. It does not close, kill, or modify any
Word process. It is used to interpret Word COM cleanup warnings such as:

word quit failed: The RPC server is unavailable. (Exception from HRESULT: 0x800706BA)
#>
[CmdletBinding()]
param(
    [string]$ReportDir = "$(Join-Path (Get-Location) '.local\user_level_document_tools\doc_quality_reports')",
    [string]$JsonPath,
    [string]$MarkdownPath
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
if ([string]::IsNullOrWhiteSpace($JsonPath)) { $JsonPath = Join-Path $ReportDir 'word_process_check_report.json' }
if ([string]::IsNullOrWhiteSpace($MarkdownPath)) { $MarkdownPath = Join-Path $ReportDir 'word_process_check_report.md' }

$processes = @()
foreach ($p in @(Get-Process -Name WINWORD -ErrorAction SilentlyContinue)) {
    $commandLine = $null
    try {
        $cim = Get-CimInstance Win32_Process -Filter "ProcessId=$($p.Id)" -ErrorAction Stop
        $commandLine = $cim.CommandLine
    } catch {
        $commandLine = $null
    }
    $processes += [ordered]@{
        id = $p.Id
        process_name = $p.ProcessName
        start_time = $(try { $p.StartTime.ToString('o') } catch { $null })
        main_window_title = $p.MainWindowTitle
        has_main_window = -not [string]::IsNullOrWhiteSpace($p.MainWindowTitle)
        responding = $(try { [bool]$p.Responding } catch { $null })
        command_line = $commandLine
    }
}

$payload = [ordered]@{
    generated_at = (Get-Date).ToString('o')
    process_name = 'WINWORD'
    process_count = $processes.Count
    non_destructive = $true
    action_taken = 'none'
    interpretation = if ($processes.Count -eq 0) {
        'No WINWORD process was found at check time. The prior Word quit RPC warning did not leave a visible lingering Word process.'
    } else {
        'One or more WINWORD processes were found. This report is read-only; close Word manually after confirming no user document is open, or rerun the document pipeline after cleanup.'
    }
    processes = $processes
}
$payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $JsonPath -Encoding UTF8

$lines = @()
$lines += '# Word Process Check Report'
$lines += ''
$lines += "- Generated at: $($payload.generated_at)"
$lines += "- Process name: WINWORD"
$lines += "- Process count: $($payload.process_count)"
$lines += "- Non-destructive: true"
$lines += "- Action taken: none"
$lines += ''
$lines += '## Interpretation'
$lines += ''
$lines += $payload.interpretation
$lines += ''
if ($processes.Count -gt 0) {
    $lines += '## Processes'
    $lines += ''
    $lines += '| PID | Start time | Has window | Responding | Window title |'
    $lines += '|---:|---|---:|---:|---|'
    foreach ($p in $processes) {
        $title = if ($p.main_window_title) { $p.main_window_title -replace '\|', '/' } else { '' }
        $lines += "| $($p.id) | $($p.start_time) | $($p.has_main_window) | $($p.responding) | $title |"
    }
    $lines += ''
    $lines += '## Safe handling'
    $lines += ''
    $lines += '- Do not auto-kill Word while user documents may be open.'
    $lines += '- If these processes are pipeline leftovers, close Word from the desktop or Task Manager after confirming no unsaved user work is present.'
    $lines += '- Then rerun the affected quality-check job if needed.'
}
$lines += ''
$lines += "JSON: $JsonPath"
$lines | Set-Content -LiteralPath $MarkdownPath -Encoding UTF8

Write-Host "Wrote: $JsonPath"
Write-Host "Wrote: $MarkdownPath"
if ($processes.Count -gt 0) { exit 1 }
exit 0
