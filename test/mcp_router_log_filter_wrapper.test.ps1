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
        [string] $CaseName,
        [byte[]] $InputBytes = @()
    )

    $caseRoot = Join-Path $TmpRoot $CaseName
    New-Item -ItemType Directory -Force -Path $caseRoot | Out-Null
    $childPath = Join-Path $caseRoot "child.py"
    $stdoutPath = Join-Path $caseRoot "stdout.bin"
    $stderrPath = Join-Path $caseRoot "stderr.txt"
    $stdinPath = Join-Path $caseRoot "stdin.bin"
    $logRoot = Join-Path $caseRoot "logs"
    $argsJsonPath = Join-Path $caseRoot "args.json"

    Set-Content -LiteralPath $childPath -Encoding UTF8 -Value $ChildScript
    Set-Content -LiteralPath $argsJsonPath -Encoding UTF8 -Value (ConvertTo-Json @($childPath) -Compress)
    [System.IO.File]::WriteAllBytes($stdinPath, $InputBytes)

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

    $process = Start-Process -FilePath $PowerShellExe -ArgumentList $args -NoNewWindow -Wait -PassThru -RedirectStandardInput $stdinPath -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath

    return [pscustomobject]@{
        ExitCode = $process.ExitCode
        StdoutBytes = if (Test-Path -LiteralPath $stdoutPath) { [System.IO.File]::ReadAllBytes($stdoutPath) } else { [byte[]]@() }
        Stdout = if (Test-Path -LiteralPath $stdoutPath) { [System.Text.Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes($stdoutPath)) } else { "" }
        Stderr = if (Test-Path -LiteralPath $stderrPath) { Get-Content -LiteralPath $stderrPath -Raw } else { "" }
        Logs = Get-ChildItem -LiteralPath $logRoot -File -ErrorAction SilentlyContinue
    }
}

$noNewlineChild = @'
import sys
sys.stdout.buffer.write(b'{"jsonrpc":"2.0","id":1,"result":{"ok":true}}')
sys.stderr.write("checking-for-update\n")
sys.stderr.write("ERROR: simulated actionable failure\n")
sys.exit(0)
'@

$noNewline = Invoke-WrapperCase -ChildScript $noNewlineChild -CaseName "no-newline"
$expectedNoNewline = '{"jsonrpc":"2.0","id":1,"result":{"ok":true}}'
Assert-True ($noNewline.ExitCode -eq 0) "no-newline case should exit 0"
Assert-True ($noNewline.Stdout -eq $expectedNoNewline) "stdout should be byte-transparent and not append newline"
Assert-True ($noNewline.Stderr -match "ERROR: simulated actionable failure") "actionable stderr should be forwarded"
Assert-True ($noNewline.Stderr -notmatch "checking-for-update") "benign stderr should be suppressed"
Assert-True (($noNewline.Logs | Measure-Object).Count -eq 1) "no-newline case should create one raw log file"
$noNewlineLog = Get-Content -LiteralPath $noNewline.Logs[0].FullName -Raw
Assert-True ($noNewlineLog -match "checking-for-update") "raw log should retain suppressed stderr noise"

$framedChild = @'
import sys
body = b'{"jsonrpc":"2.0","id":2,"result":{"framed":true}}'
frame = b'Content-Length: ' + str(len(body)).encode('ascii') + b'\r\n\r\n' + body
sys.stdout.buffer.write(frame)
sys.exit(0)
'@

$framed = Invoke-WrapperCase -ChildScript $framedChild -CaseName "framed"
$body = [System.Text.Encoding]::ASCII.GetBytes('{"jsonrpc":"2.0","id":2,"result":{"framed":true}}')
$expectedFramePrefix = [System.Text.Encoding]::ASCII.GetBytes("Content-Length: $($body.Length)`r`n`r`n")
$expectedFrame = New-Object byte[] ($expectedFramePrefix.Length + $body.Length)
[Array]::Copy($expectedFramePrefix, 0, $expectedFrame, 0, $expectedFramePrefix.Length)
[Array]::Copy($body, 0, $expectedFrame, $expectedFramePrefix.Length, $body.Length)
Assert-True ($framed.ExitCode -eq 0) "framed case should exit 0"
Assert-True ([System.Linq.Enumerable]::SequenceEqual([byte[]]$framed.StdoutBytes, [byte[]]$expectedFrame)) "Content-Length frame should be forwarded byte-for-byte"

$largeChild = @'
import json
import sys
tools = [{"name": f"tool_{i}", "description": "x" * 200} for i in range(300)]
payload = json.dumps({"jsonrpc":"2.0","id":3,"result":{"tools":tools}}, separators=(",",":"))
sys.stdout.write(payload)
sys.exit(0)
'@

$large = Invoke-WrapperCase -ChildScript $largeChild -CaseName "large"
Assert-True ($large.ExitCode -eq 0) "large case should exit 0"
Assert-True ($large.Stdout -match '"tool_299"') "large tools/list-like payload should be complete"
Assert-True ($large.Stdout.Length -gt 50000) "large payload should stay large after forwarding"

$stdinChild = @'
import sys
data = sys.stdin.buffer.read()
sys.stdout.buffer.write(b'echo:' + data)
sys.exit(0)
'@
$stdinBytes = [System.Text.Encoding]::UTF8.GetBytes('{"jsonrpc":"2.0","method":"initialize"}')
$stdinCase = Invoke-WrapperCase -ChildScript $stdinChild -CaseName "stdin" -InputBytes $stdinBytes
Assert-True ($stdinCase.Stdout -eq 'echo:{"jsonrpc":"2.0","method":"initialize"}') "stdin should be forwarded byte-for-byte to child"

$nonZeroChild = @'
import sys
sys.stdout.buffer.write(b'{"jsonrpc":"2.0","id":4,"result":{"ok":false}}')
sys.exit(7)
'@

$nonZero = Invoke-WrapperCase -ChildScript $nonZeroChild -CaseName "nonzero"
Assert-True ($nonZero.ExitCode -eq 7) "nonzero case should propagate child exit code"
Assert-True ($nonZero.Stdout -eq '{"jsonrpc":"2.0","id":4,"result":{"ok":false}}') "nonzero case should still forward protocol bytes"
Assert-True ($nonZero.Stderr -match "MCP Router command exited with code 7") "nonzero case should report exit code to stderr"
Assert-True (($nonZero.Logs | Measure-Object).Count -eq 1) "nonzero case should create one raw log file"

Write-Output "mcp_router_log_filter_wrapper: ok"
