<#
.SYNOPSIS
Find a local Poppler installation and optionally write a detection report.
#>
[CmdletBinding()]
param(
    [string]$ReportDir = "$(Join-Path (Get-Location) '.local\user_level_document_tools\doc_quality_reports')",
    [string]$JsonPath,
    [string]$MarkdownPath,
    [string[]]$ExtraSearchRoots = @(),
    [switch]$DeepSearch
)

$ErrorActionPreference = 'Stop'

function Test-PopplerBin {
    param([Parameter(Mandatory=$true)][string]$Dir)
    if (-not (Test-Path -LiteralPath $Dir -PathType Container)) { return $null }
    $need = @('pdfinfo.exe','pdffonts.exe','pdftoppm.exe','pdftocairo.exe')
    $found = @()
    foreach ($n in $need) {
        $p = Join-Path $Dir $n
        if (Test-Path -LiteralPath $p -PathType Leaf) { $found += $n }
    }
    return [ordered]@{
        path = (Get-Item -LiteralPath $Dir).FullName
        found_count = $found.Count
        expected_count = $need.Count
        found = $found
        complete = ($found.Count -eq $need.Count)
    }
}

function Add-CandidateDir {
    param([System.Collections.Generic.List[string]]$List, [string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return }
    try { $full = [System.IO.Path]::GetFullPath($Path) } catch { return }
    if (-not $List.Contains($full)) { [void]$List.Add($full) }
}

New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
if ([string]::IsNullOrWhiteSpace($JsonPath)) { $JsonPath = Join-Path $ReportDir 'poppler_detection_report.json' }
if ([string]::IsNullOrWhiteSpace($MarkdownPath)) { $MarkdownPath = Join-Path $ReportDir 'poppler_detection_report.md' }

$candidates = New-Object System.Collections.Generic.List[string]
foreach ($p in (($env:PATH -split ';') | Where-Object { $_ })) { Add-CandidateDir -List $candidates -Path $p }
foreach ($root in @(
    'C:\Tools\poppler\Library\bin',
    'C:\Tools\poppler\bin',
    'C:\Program Files\poppler\Library\bin',
    'C:\Program Files\poppler\bin',
    'C:\Program Files (x86)\poppler\Library\bin',
    'C:\Program Files (x86)\poppler\bin',
    (Join-Path $env:USERPROFILE 'scoop\apps\poppler\current\bin'),
    (Join-Path $env:USERPROFILE 'scoop\shims'),
    (Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages')
)) { Add-CandidateDir -List $candidates -Path $root }
foreach ($root in $ExtraSearchRoots) { Add-CandidateDir -List $candidates -Path $root }

if ($DeepSearch) {
    foreach ($root in @('C:\Tools','C:\Program Files','C:\Program Files (x86)', (Join-Path $env:USERPROFILE 'scoop\apps'), (Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages'))) {
        if (Test-Path -LiteralPath $root -PathType Container) {
            try {
                Get-ChildItem -LiteralPath $root -Filter 'pdfinfo.exe' -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
                    Add-CandidateDir -List $candidates -Path $_.DirectoryName
                }
            } catch { }
        }
    }
}

$results = @()
foreach ($c in $candidates) {
    $r = Test-PopplerBin -Dir $c
    if ($r -and $r.found_count -gt 0) { $results += $r }
}
$best = $null
$complete = @($results | Where-Object { $_.complete })
if ($complete.Count -gt 0) { $best = $complete[0] }
elseif ($results.Count -gt 0) { $best = ($results | Sort-Object -Property found_count -Descending | Select-Object -First 1) }

$payload = [ordered]@{
    generated_at = (Get-Date).ToString('o')
    deep_search = [bool]$DeepSearch
    candidate_count = $candidates.Count
    result_count = $results.Count
    best = $best
    results = $results
}
$payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $JsonPath -Encoding UTF8

$lines = @()
$lines += '# Poppler Detection Report'
$lines += ''
$lines += "- Generated at: $($payload.generated_at)"
$lines += "- Deep search: $($payload.deep_search)"
$lines += "- Candidate directories checked: $($payload.candidate_count)"
$lines += "- Candidate directories with Poppler tools: $($payload.result_count)"
if ($best) {
    $lines += "- Best candidate: $($best.path)"
    $lines += "- Complete: $($best.complete)"
    $lines += "- Found tools: $($best.found -join ', ')"
} else {
    $lines += '- Best candidate: not found'
}
$lines += ''
$lines += '## Results'
$lines += ''
$lines += '| Complete | Found | Path |'
$lines += '|---:|---:|---|'
foreach ($r in $results) { $lines += "| $($r.complete) | $($r.found_count)/$($r.expected_count) | $($r.path) |" }
$lines += ''
$lines += "JSON report: $JsonPath"
$lines | Set-Content -LiteralPath $MarkdownPath -Encoding UTF8

Write-Host "Wrote: $JsonPath"
Write-Host "Wrote: $MarkdownPath"
if ($best -and $best.complete) { Write-Host "POPPLER_BIN_DIR=$($best.path)"; exit 0 }
exit 1
