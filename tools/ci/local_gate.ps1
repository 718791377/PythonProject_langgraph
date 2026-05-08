[CmdletBinding()]
param(
  [string]$Root = '.',
  [switch]$Json,
  [switch]$RefreshManagedFiles,
  [switch]$RequireCleanGit,
  [int]$StepTimeoutSeconds = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Root).Path)
$pythonGate = Join-Path $scriptRoot 'local_gate.py'

$arguments = @(
  $pythonGate,
  '--root',
  $repoRoot,
  '--step-timeout-seconds',
  ([string]$StepTimeoutSeconds)
)

if ($Json) { $arguments += '--json' }
if ($RefreshManagedFiles) { $arguments += '--refresh-managed-files' }
if ($RequireCleanGit) { $arguments += '--require-clean-git' }

& python @arguments
exit $LASTEXITCODE
