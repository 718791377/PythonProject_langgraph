[CmdletBinding()]
param(
  [string]$Root = '.',
  [string]$BaseRef = 'main',
  [string]$HeadRef = 'HEAD',
  [switch]$AllowDirty,
  [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-GitText {
  param(
    [Parameter(Mandatory)] [string]$RepoRoot,
    [Parameter(Mandatory)] [string[]]$Arguments,
    [switch]$AllowFailure
  )
  $previousLocation = Get-Location
  try {
    Set-Location -LiteralPath $RepoRoot
    $output = & git @Arguments 2>&1
    $exitCode = [int]$LASTEXITCODE
    $stdout = ($output | ForEach-Object { [string]$_ }) -join [Environment]::NewLine
    if ($stdout.Length -gt 0) { $stdout += [Environment]::NewLine }
    if ($exitCode -ne 0 -and -not $AllowFailure) {
      throw ('git {0} failed with exit code {1}: {2}' -f ($Arguments -join ' '), $exitCode, $stdout)
    }
    return [ordered]@{
      command = @('git') + $Arguments
      exit_code = $exitCode
      ok = ($exitCode -eq 0)
      stdout = $stdout
      stderr = ""
    }
  } finally {
    Set-Location -LiteralPath $previousLocation
  }
}

$repoRoot = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Root).Path)
$dirtyText = (Invoke-GitText -RepoRoot $repoRoot -Arguments @('status', '--porcelain')).stdout
$dirtyEntries = @($dirtyText -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$baseSha = (Invoke-GitText -RepoRoot $repoRoot -Arguments @('rev-parse', $BaseRef)).stdout.Trim()
$headSha = (Invoke-GitText -RepoRoot $repoRoot -Arguments @('rev-parse', $HeadRef)).stdout.Trim()
$mergeBase = (Invoke-GitText -RepoRoot $repoRoot -Arguments @('merge-base', $BaseRef, $HeadRef)).stdout.Trim()
# Local MR Review changed-files command: git diff --name-status.
$changedFilesText = (Invoke-GitText -RepoRoot $repoRoot -Arguments @('diff', '--name-status', ('{0}...{1}' -f $BaseRef, $HeadRef))).stdout
# Local MR Review commit-log command: git log --oneline.
$logText = (Invoke-GitText -RepoRoot $repoRoot -Arguments @('log', '--oneline', ('{0}..{1}' -f $BaseRef, $HeadRef))).stdout
# Local MR Review diff-stat command: git diff --stat.
$diffStatText = (Invoke-GitText -RepoRoot $repoRoot -Arguments @('diff', '--stat', ('{0}...{1}' -f $BaseRef, $HeadRef))).stdout
$mergeTree = Invoke-GitText -RepoRoot $repoRoot -Arguments @('merge-tree', $mergeBase, $BaseRef, $HeadRef) -AllowFailure

$changedFiles = @($changedFilesText -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$commits = @($logText -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$conflictMarkers = @($mergeTree.stdout -split "`r?`n" | Where-Object { $_ -match '^(<<<<<<<|>>>>>>>|=======)' })
$errors = @()
if ($dirtyEntries.Count -gt 0 -and -not $AllowDirty) {
  $errors += 'git status --porcelain detected dirty worktree entries; commit, move, or discard local changes before local MR review.'
}
if ($mergeTree.exit_code -ne 0) {
  $errors += 'git merge-tree failed; local MR review could not simulate merge cleanly.'
}
if ($conflictMarkers.Count -gt 0) {
  $errors += 'git merge-tree output contains conflict markers.'
}

$result = [ordered]@{
  schema_version = 1
  check_name = 'local_mr_review'
  generated_at = ([DateTimeOffset]::UtcNow).ToString('o')
  root = $repoRoot
  ok = ($errors.Count -eq 0)
  base_ref = $BaseRef
  base_sha = $baseSha
  head_ref = $HeadRef
  head_sha = $headSha
  merge_base = $mergeBase
  allow_dirty = [bool]$AllowDirty
  dirty_worktree = ($dirtyEntries.Count -gt 0)
  dirty_files = $dirtyEntries
  changed_files = $changedFiles
  commits = $commits
  diff_stat = $diffStatText
  merge_tree = [ordered]@{
    exit_code = $mergeTree.exit_code
    ok = $mergeTree.ok
    conflict_marker_count = $conflictMarkers.Count
  }
  errors = $errors
  counts = [ordered]@{
    changed_files = $changedFiles.Count
    commits = $commits.Count
    dirty_files = $dirtyEntries.Count
    errors = $errors.Count
  }
}

if ($Json) {
  $result | ConvertTo-Json -Depth 10
} else {
  Write-Host ('local_mr_review: base={0} head={1}' -f $BaseRef, $HeadRef)
  Write-Host ('commits={0} changed_files={1} dirty_files={2}' -f $commits.Count, $changedFiles.Count, $dirtyEntries.Count)
  if ($diffStatText) { Write-Host $diffStatText.TrimEnd() }
  if ([bool]$result.ok) { Write-Host 'local_mr_review: ok' } else { foreach ($errorMessage in $errors) { Write-Error $errorMessage } }
}

if ([bool]$result.ok) { exit 0 }
exit 1
