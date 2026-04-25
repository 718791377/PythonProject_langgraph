[CmdletBinding()]
param(
  [string]$SourceRoot = 'D:\PythonProject_OpenClaw',
  [string]$DestinationRoot = 'D:\PythonProject_langgraph',
  [switch]$Force
)

$ErrorActionPreference = 'Stop'

function Ensure-Directory {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path | Out-Null
  }
}

function Copy-RelativePath {
  param(
    [string]$SourceRoot,
    [string]$DestinationRoot,
    [string]$RelativePath
  )

  $sourcePath = Join-Path $SourceRoot $RelativePath
  if (-not (Test-Path -LiteralPath $sourcePath)) {
    return
  }

  $destinationPath = Join-Path $DestinationRoot $RelativePath
  $parent = Split-Path -Parent $destinationPath
  if (-not [string]::IsNullOrWhiteSpace($parent)) {
    Ensure-Directory -Path $parent
  }

  $item = Get-Item -LiteralPath $sourcePath
  if ($item.PSIsContainer) {
    Copy-Item -LiteralPath $sourcePath -Destination $destinationPath -Recurse -Force
  } else {
    Copy-Item -LiteralPath $sourcePath -Destination $destinationPath -Force
  }
}

function Copy-MatchingChildren {
  param(
    [string]$SourceDirectory,
    [string]$DestinationDirectory,
    [string[]]$Patterns
  )

  Ensure-Directory -Path $DestinationDirectory
  foreach ($pattern in @($Patterns)) {
    foreach ($item in @(Get-ChildItem -LiteralPath $SourceDirectory -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -like $pattern })) {
      $target = Join-Path $DestinationDirectory $item.Name
      if ($item.PSIsContainer) {
        Copy-Item -LiteralPath $item.FullName -Destination $target -Recurse -Force
      } else {
        Copy-Item -LiteralPath $item.FullName -Destination $target -Force
      }
    }
  }
}

if ((Test-Path -LiteralPath $DestinationRoot) -and -not $Force) {
  $existingItems = @(Get-ChildItem -LiteralPath $DestinationRoot -Force -ErrorAction SilentlyContinue)
  if ($existingItems.Count -gt 0) {
    throw "Destination already exists and is not empty: $DestinationRoot"
  }
}

Ensure-Directory -Path $DestinationRoot

$topLevelRelativePaths = @(
  '.migration\langgraph_repo_seed\README.md',
  '.migration\langgraph_repo_seed\.gitignore',
  '.migration\langgraph_repo_seed\AGENTS.md',
  '.migration\langgraph_repo_seed\docs_bilingual\project_startup_summary.md',
  '.migration\langgraph_repo_seed\docs_bilingual\project_startup_summary.zh-CN.md',
  'openspec\config.yaml',
  'docs_bilingual\docs_registry.yaml',
  'docs_bilingual\governance\openspec_usage_convention.md',
  'docs_bilingual\governance\openspec_usage_convention.zh-CN.md',
  'docs_bilingual\governance\openspec_opsx_project_usage_policy.md',
  'docs_bilingual\governance\openspec_opsx_project_usage_policy.zh-CN.md',
  'docs_bilingual\governance\openspec_official_workflow_policy.md',
  'docs_bilingual\governance\openspec_official_workflow_policy.zh-CN.md',
  'docs_bilingual\implementation_plans\codex_oh_my_codex_user_level_team_mode_plan.md',
  'docs_bilingual\implementation_plans\codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md',
  'docs_bilingual\implementation_plans\codex_langgraph_repository_split_migration_plan.md',
  'docs_bilingual\implementation_plans\codex_langgraph_repository_split_migration_plan.zh-CN.md',
  'tools\install-codex-user-level-team-mode.ps1',
  'tools\migrate-codex-langgraph-to-new-repo.ps1',
  'tools\langgraph_durable_orchestrator',
  'tools\openclaw-omx-windows-bootstrap-fix.mjs',
  'tools\bootstrap-official-openspec.ps1',
  'tools\run_openspec_guard.py',
  'tools\verify_official_openspec.py',
  'tools\install-git-hooks.ps1',
  'test\install-codex-user-level-team-mode.test.ps1',
  'test\run-install-codex-user-level-team-mode-test.cmd',
  'test\langgraph_durable_orchestrator_durable_artifacts.test.py',
  'test\langgraph_durable_orchestrator_quality_loops.test.py',
  'test\langgraph_durable_orchestrator_replay_recovery.test.py',
  'test\langgraph_durable_orchestrator_state_reducers.test.py',
  'test\openclaw-omx-windows-bootstrap-fix.test.mjs'
)

foreach ($relativePath in @($topLevelRelativePaths)) {
  if ($relativePath.StartsWith('.migration\langgraph_repo_seed\')) {
    $seedRelative = $relativePath.Substring('.migration\langgraph_repo_seed\'.Length)
    Copy-RelativePath -SourceRoot (Join-Path $SourceRoot '.migration\langgraph_repo_seed') -DestinationRoot $DestinationRoot -RelativePath $seedRelative
  } else {
    Copy-RelativePath -SourceRoot $SourceRoot -DestinationRoot $DestinationRoot -RelativePath $relativePath
  }
}

Copy-MatchingChildren -SourceDirectory (Join-Path $SourceRoot 'openspec\specs') -DestinationDirectory (Join-Path $DestinationRoot 'openspec\specs') -Patterns @('codex-user-level*', 'langgraph-durable-orchestration-backend')
Copy-MatchingChildren -SourceDirectory (Join-Path $SourceRoot 'openspec\changes') -DestinationDirectory (Join-Path $DestinationRoot 'openspec\changes') -Patterns @('implement-langgraph-reusable-subgraph-library')
Copy-MatchingChildren -SourceDirectory (Join-Path $SourceRoot 'openspec\changes\archive') -DestinationDirectory (Join-Path $DestinationRoot 'openspec\changes\archive') -Patterns @('*codex-user-level*', '*langgraph*', '*omx*', '*team-mode*')
Copy-MatchingChildren -SourceDirectory (Join-Path $SourceRoot '.codex\skills') -DestinationDirectory (Join-Path $DestinationRoot '.codex\skills') -Patterns @('openspec-*')

if (Test-Path -LiteralPath (Join-Path $SourceRoot '.githooks')) {
  Copy-RelativePath -SourceRoot $SourceRoot -DestinationRoot $DestinationRoot -RelativePath '.githooks'
}
if (Test-Path -LiteralPath (Join-Path $SourceRoot '.github\workflows\openspec-guard.yml')) {
  Copy-RelativePath -SourceRoot $SourceRoot -DestinationRoot $DestinationRoot -RelativePath '.github\workflows\openspec-guard.yml'
}
if (Test-Path -LiteralPath (Join-Path $SourceRoot '.gitlab-ci.yml')) {
  Copy-RelativePath -SourceRoot $SourceRoot -DestinationRoot $DestinationRoot -RelativePath '.gitlab-ci.yml'
}

Push-Location -LiteralPath $DestinationRoot
try {
  if (-not (Test-Path -LiteralPath (Join-Path $DestinationRoot '.git'))) {
    git init | Out-Null
  }
} finally {
  Pop-Location
}

Write-Output $DestinationRoot
