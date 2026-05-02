[CmdletBinding()]
param()

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Wrapper = Join-Path $RepoRoot "tools\mcp-router-log-filter-wrapper.ps1"
$TmpRoot = Join-Path $RepoRoot ".tmp\mcp-router-log-filter-wrapper-test"
$PowerShellExe = (Get-Command powershell.exe -ErrorAction Stop).Source
$PythonExe = (Get-Command python -ErrorAction Stop).Source

if (Test-Path -LiteralPath $TmpRoot) {
    Remove-Item -LiteralPath $TmpRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $TmpRoot | Out-Null

function Assert-True {
    param(
        [bool] $Condition,
        [string] $Message
    )

    if (-not $Condition) {
        throw $Message
    }
}

function Invoke-WrapperCase {
    param(
        [string] $ChildScript,
        [string] $CaseName
    )

    $caseRoot = Join-Path $TmpRoot $CaseName
    New-Item -ItemType Directory -Force -Path $caseRoot | Out-Null
    $childPath = Join-Path $caseRoot "child.py"
    $stdoutPath = Join-Path $caseRoot "stdout.txt"
    $stderrPath = Join-Path $caseRoot "stderr.txt"
    $logRoot = Join-Path $caseRoot "logs"
    $argsJsonPath = Join-Path $caseRoot "args.json"

    Set-Content -LiteralPath $childPath -Encoding UTF8 -Value $ChildScript
    Set-Content -LiteralPath $argsJsonPath -Encoding UTF8 -Value (ConvertTo-Json @($childPath) -Compress)

    $args = @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $Wrapper,
        "-CommandPath",
        $PythonExe,
        "-CommandArgsFile",
        $argsJsonPath,
        "-LogRoot",
        $logRoot
    )

    $process = Start-Process -FilePath $PowerShellExe -ArgumentList $args -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath

    return [pscustomobject]@{
        ExitCode = $process.ExitCode
        Stdout = if (Test-Path -LiteralPath $stdoutPath) { Get-Content -LiteralPath $stdoutPath -Raw } else { "" }
        Stderr = if (Test-Path -LiteralPath $stderrPath) { Get-Content -LiteralPath $stderrPath -Raw } else { "" }
        Logs = Get-ChildItem -LiteralPath $logRoot -File -ErrorAction SilentlyContinue
    }
}

$normalChild = @'
import sys
print("checking-for-update")
print("libpng warning: iCCP: known incorrect sRGB profile", file=sys.stderr)
print('{"jsonrpc":"2.0","id":1,"result":{"ok":true}}')
print("No valid workflows found for tools/list")
print("ERROR: simulated actionable failure", file=sys.stderr)
sys.exit(0)
'@

$normal = Invoke-WrapperCase -ChildScript $normalChild -CaseName "normal"
Assert-True ($normal.ExitCode -eq 0) "normal case should exit 0"
Assert-True ($normal.Stdout -match '"jsonrpc"') "protocol JSON should be forwarded to stdout"
Assert-True ($normal.Stdout -notmatch "checking-for-update") "benign updater noise should not be forwarded to stdout"
Assert-True ($normal.Stdout -notmatch "No valid workflows found") "workflow fallback noise should not be forwarded to stdout"
Assert-True ($normal.Stderr -match "ERROR: simulated actionable failure") "actionable errors should be forwarded to stderr"
Assert-True ($normal.Stderr -notmatch "libpng warning") "benign libpng warning should not be forwarded to stderr"
Assert-True (($normal.Logs | Measure-Object).Count -eq 1) "normal case should create one raw log file"
$normalLog = Get-Content -LiteralPath $normal.Logs[0].FullName -Raw
Assert-True ($normalLog -match "checking-for-update") "raw log should retain suppressed updater noise"
Assert-True ($normalLog -match "libpng warning") "raw log should retain suppressed stderr noise"

$nonZeroChild = @'
import sys
print('{"jsonrpc":"2.0","id":2,"result":{"ok":false}}')
sys.exit(7)
'@

$nonZero = Invoke-WrapperCase -ChildScript $nonZeroChild -CaseName "nonzero"
Assert-True ($nonZero.ExitCode -eq 7) "nonzero case should propagate child exit code"
Assert-True ($nonZero.Stdout -match '"jsonrpc"') "nonzero case should still forward protocol JSON"
Assert-True ($nonZero.Stderr -match "MCP Router command exited with code 7") "nonzero case should report exit code to stderr"
Assert-True (($nonZero.Logs | Measure-Object).Count -eq 1) "nonzero case should create one raw log file"

Write-Output "mcp_router_log_filter_wrapper: ok"
