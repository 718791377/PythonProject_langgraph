[CmdletBinding()]
param(
    [string]$ProjectRoot = (Get-Location).Path,
    [string]$OpenSpecTools = 'codex',
    [switch]$SkipCliInstall,
    [switch]$ForceCliUpgrade,
    [switch]$SkipValidation,
    [switch]$SkipGitHookInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Step {
    param([string]$Message)
    Write-Host "[openspec-bootstrap] $Message"
}

function Resolve-AbsolutePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Path not found: $Path"
    }

    return (Resolve-Path -LiteralPath $Path).Path
}

function Get-CommandPath {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Candidates
    )

    foreach ($candidate in $Candidates) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($null -ne $command) {
            return $command.Source
        }
    }

    return $null
}

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,

        [string]$WorkingDirectory,

        [Parameter(Mandatory = $true)]
        [string]$FailureMessage
    )

    if ($WorkingDirectory) {
        Push-Location $WorkingDirectory
    }

    try {
        & $FilePath @Arguments
        $exitCode = $LASTEXITCODE
    } finally {
        if ($WorkingDirectory) {
            Pop-Location
        }
    }

    if ($exitCode -ne 0) {
        throw "$FailureMessage Exit code: $exitCode"
    }
}

function Resolve-PythonCommand {
    foreach ($candidate in @('python', 'python3', 'py')) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($null -ne $command) {
            if ($candidate -eq 'py') {
                return ,@($command.Source, '-3')
            }

            return ,@($command.Source)
        }
    }

    return $null
}

$projectRootPath = Resolve-AbsolutePath -Path $ProjectRoot
$openspecPath = Get-CommandPath -Candidates @('openspec', 'openspec.cmd')

if ($null -eq $openspecPath) {
    if ($SkipCliInstall) {
        throw "OpenSpec CLI was not found and -SkipCliInstall was supplied."
    }

    $npmPath = Get-CommandPath -Candidates @('npm.cmd', 'npm')
    if ($null -eq $npmPath) {
        throw "OpenSpec CLI was not found and npm is unavailable. Install Node.js >= 20.19.0 and run npm install -g @fission-ai/openspec@latest."
    }

    Write-Step "Installing official OpenSpec CLI via npm"
    Invoke-Checked -FilePath $npmPath -Arguments @('install', '-g', '@fission-ai/openspec@latest') -FailureMessage 'Failed to install the official OpenSpec CLI.'
    $openspecPath = Get-CommandPath -Candidates @('openspec', 'openspec.cmd')
    if ($null -eq $openspecPath) {
        throw "OpenSpec CLI still was not found after installation."
    }
} elseif ($ForceCliUpgrade) {
    $npmPath = Get-CommandPath -Candidates @('npm.cmd', 'npm')
    if ($null -eq $npmPath) {
        throw "Cannot upgrade the OpenSpec CLI because npm is unavailable."
    }

    Write-Step "Upgrading official OpenSpec CLI via npm"
    Invoke-Checked -FilePath $npmPath -Arguments @('install', '-g', '@fission-ai/openspec@latest') -FailureMessage 'Failed to upgrade the official OpenSpec CLI.'
    $openspecPath = Get-CommandPath -Candidates @('openspec', 'openspec.cmd')
}

Write-Step "Detected official OpenSpec CLI"
Invoke-Checked -FilePath $openspecPath -Arguments @('--version') -FailureMessage 'Failed to query the OpenSpec CLI version.'

Write-Step "Initializing official OpenSpec integration for tools: $OpenSpecTools"
Invoke-Checked -FilePath $openspecPath -Arguments @('init', '--tools', $OpenSpecTools, '--force') -WorkingDirectory $projectRootPath -FailureMessage 'OpenSpec initialization failed.'

Write-Step "Refreshing official OpenSpec instruction files"
Invoke-Checked -FilePath $openspecPath -Arguments @('update', '--force') -WorkingDirectory $projectRootPath -FailureMessage 'OpenSpec update failed.'

if (-not $SkipGitHookInstall) {
    $gitHookInstaller = Join-Path $projectRootPath 'tools\install-git-hooks.ps1'
    if (Test-Path -LiteralPath $gitHookInstaller) {
        if (Test-Path -LiteralPath (Join-Path $projectRootPath '.git')) {
            Write-Step "Installing git hooks"
            & $gitHookInstaller -ProjectRoot $projectRootPath
            if ($LASTEXITCODE -ne 0) {
                throw "Git hook installation failed."
            }
        } else {
            Write-Step "Skipping git hook install because .git is not present yet"
        }
    }
}

if (-not $SkipValidation) {
    $pythonCommand = Resolve-PythonCommand
    if ($null -eq $pythonCommand) {
        throw "Python launcher was not found. Install Python and rerun the bootstrap so verify_official_openspec.py can execute."
    }

    $verifyScript = Join-Path $projectRootPath 'tools\verify_official_openspec.py'
    if (-not (Test-Path -LiteralPath $verifyScript)) {
        throw "Missing verification script: $verifyScript"
    }

    Write-Step "Running official OpenSpec verification"
    $pythonExe = $pythonCommand[0]
    $pythonArgs = @()
    if ($pythonCommand.Count -gt 1) {
        $pythonArgs += $pythonCommand[1..($pythonCommand.Count - 1)]
    }
    $pythonArgs += @($verifyScript, '--root', $projectRootPath)

    Invoke-Checked -FilePath $pythonExe -Arguments $pythonArgs -WorkingDirectory $projectRootPath -FailureMessage 'Official OpenSpec verification failed.'
}

Write-Host ''
Write-Host "OpenSpec bootstrap complete at: $projectRootPath"
