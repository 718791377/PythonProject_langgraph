[CmdletBinding(SupportsShouldProcess = $true)]
param(
  [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }),
  [string]$SourcePath,
  [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($SourcePath)) {
  $SourcePath = Join-Path $repoRoot 'tools\skill_sources\plugin-modules'
}
$source = [System.IO.Path]::GetFullPath($SourcePath)
$codexHomePath = [System.IO.Path]::GetFullPath($CodexHome)
$destination = Join-Path (Join-Path $codexHomePath 'skills') 'plugin-modules'
$backupRoot = Join-Path $codexHomePath 'backups\plugin-modules-skill'

if (-not (Test-Path -LiteralPath (Join-Path $source 'SKILL.md'))) {
  throw "Source plugin-modules skill is missing SKILL.md: $source"
}

if ((Test-Path -LiteralPath $destination) -and -not $Force) {
  throw "Destination already exists: $destination. Re-run with -Force to back it up and replace it."
}

$backupPath = $null
if (Test-Path -LiteralPath $destination) {
  New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
  $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ')
  $backupPath = Join-Path $backupRoot $stamp
  if ($PSCmdlet.ShouldProcess($destination, "backup to $backupPath")) {
    Copy-Item -LiteralPath $destination -Destination $backupPath -Recurse -Force
  }
}

New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
if (Test-Path -LiteralPath $destination) {
  if ($PSCmdlet.ShouldProcess($destination, 'replace plugin-modules skill')) {
    Remove-Item -LiteralPath $destination -Recurse -Force
  }
}
if ($PSCmdlet.ShouldProcess($destination, 'install plugin-modules skill')) {
  Copy-Item -LiteralPath $source -Destination $destination -Recurse -Force
}

[ordered]@{
  installed = $true
  source = $source
  destination = $destination
  backup_path = $backupPath
  restart_required = $true
  restart_instruction = 'Restart codex-ohmy or resume the target thread in a fresh codex-ohmy process so plugin-modules appears in the skills list.'
} | ConvertTo-Json -Depth 8
