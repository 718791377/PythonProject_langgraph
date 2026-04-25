[CmdletBinding()]
param(
    [string]$ProjectRoot = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Step {
    param([string]$Message)
    Write-Host "[git-hooks] $Message"
}

if (-not (Test-Path -LiteralPath $ProjectRoot)) {
    throw "Project root not found: $ProjectRoot"
}

$projectRootPath = (Resolve-Path -LiteralPath $ProjectRoot).Path
$hooksPath = Join-Path $projectRootPath '.githooks'

if (-not (Test-Path -LiteralPath $hooksPath)) {
    throw "Missing .githooks directory: $hooksPath"
}

if (-not (Test-Path -LiteralPath (Join-Path $projectRootPath '.git'))) {
    Write-Warning "No .git directory was found under $projectRootPath. Run this script again after git init or after cloning the repository."
    exit 0
}

$gitPath = Get-Command git.exe -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -eq $gitPath) {
    $gitPath = Get-Command git -ErrorAction SilentlyContinue | Select-Object -First 1
}

if ($null -eq $gitPath) {
    throw "git executable was not found."
}

Push-Location $projectRootPath
try {
    & $gitPath.Source config core.hooksPath .githooks
    if ($LASTEXITCODE -ne 0) {
        throw "git config core.hooksPath .githooks failed."
    }
} finally {
    Pop-Location
}

Write-Step "Configured core.hooksPath=.githooks"
