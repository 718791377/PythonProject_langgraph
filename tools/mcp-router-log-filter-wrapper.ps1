<#
.SYNOPSIS
PowerShell launcher for the MCP Router error-only log filter.

.DESCRIPTION
This script is intentionally thin: it delegates filtering to
tools/mcp_router_log_filter_wrapper.py so the wrapper can safely shuttle stdio
without PowerShell DataReceived event noise. It does not edit Codex config or
MCP Router state.
#>

[CmdletBinding()]
param(
    [string] $CommandPath = "C:\Program Files\nodejs\npx.cmd",
    [string[]] $CommandArgs = @("-y", "@mcp_router/cli@latest", "connect"),
    [string] $CommandArgsJson,
    [string] $CommandArgsFile,
    [string] $LogRoot
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$Python = (Get-Command python -ErrorAction Stop).Source
$Wrapper = Join-Path $PSScriptRoot "mcp_router_log_filter_wrapper.py"

$ArgsList = @($Wrapper, "--command-path", $CommandPath)

if ($CommandArgsFile) {
    $ArgsList += @("--command-args-file", $CommandArgsFile)
}
elseif ($CommandArgsJson) {
    $ArgsList += @("--command-args-json", $CommandArgsJson)
}
else {
    if ($PSBoundParameters.ContainsKey("CommandArgs")) {
        foreach ($CommandArg in $CommandArgs) {
            $ArgsList += @("--command-arg", $CommandArg)
        }
    }
}

if ($LogRoot) {
    $ArgsList += @("--log-root", $LogRoot)
}

& $Python @ArgsList
exit $LASTEXITCODE
