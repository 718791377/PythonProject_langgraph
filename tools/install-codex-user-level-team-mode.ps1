[CmdletBinding()]
param(
  [string]$CodexHome,
  [string]$PowerShellProfilePath,
  [string]$NativeCodexCommandPath,
  [string]$OmxCommandPath,
  [string]$PythonCommandPath,
  [switch]$InstallTaskkillExeShim,
  [switch]$SkipTaskkillExeShim,
  [switch]$Force,
  [string]$TestFailPoint = 'none'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($TestFailPoint -notin @('none', 'after_backup', 'after_assets', 'after_state', 'after_profile')) {
  throw "Invalid TestFailPoint value: $TestFailPoint"
}

if ($InstallTaskkillExeShim -and $SkipTaskkillExeShim) {
  throw 'InstallTaskkillExeShim and SkipTaskkillExeShim cannot both be set.'
}

$Script:ManagedMarker = 'OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED'
$Script:ManagedBy = 'codex-user-level-team-mode-p0'
$Script:NativeCodexNames = @('codex', 'codex.cmd', 'codex.ps1')
$Script:StartupProfileStartMarker = '# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-STARTUP:START'
$Script:StartupProfileEndMarker = '# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-STARTUP:END'

function Resolve-TargetCodexHome {
  $candidate = $null
  if (-not [string]::IsNullOrWhiteSpace($CodexHome)) {
    $candidate = $CodexHome
  } elseif (-not [string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
    $candidate = $env:CODEX_HOME
  } else {
    $candidate = Join-Path $HOME '.codex'
  }

  Ensure-Directory -Path $candidate
  return (Resolve-Path -LiteralPath $candidate).Path
}

function Resolve-PowerShellProfileTargetPath {
  $candidate = $null
  if (-not [string]::IsNullOrWhiteSpace($PowerShellProfilePath)) {
    $candidate = $PowerShellProfilePath
  } elseif ($null -ne $PROFILE -and -not [string]::IsNullOrWhiteSpace([string]$PROFILE.CurrentUserCurrentHost)) {
    $candidate = [string]$PROFILE.CurrentUserCurrentHost
  } else {
    $candidate = Join-Path (Join-Path $HOME 'Documents\WindowsPowerShell') 'Microsoft.PowerShell_profile.ps1'
  }

  Ensure-Directory -Path (Split-Path -Parent $candidate)
  return [System.IO.Path]::GetFullPath($candidate)
}

function Resolve-NativeCodexCommandPath {
  if (-not [string]::IsNullOrWhiteSpace($NativeCodexCommandPath)) {
    return [System.IO.Path]::GetFullPath($NativeCodexCommandPath)
  }

  $cmdCommand = Get-Command 'codex.cmd' -ErrorAction SilentlyContinue
  if ($null -ne $cmdCommand -and -not [string]::IsNullOrWhiteSpace([string]$cmdCommand.Source)) {
    return [System.IO.Path]::GetFullPath([string]$cmdCommand.Source)
  }

  $resolved = Get-Command 'codex' -CommandType Application,ExternalScript -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($null -ne $resolved -and -not [string]::IsNullOrWhiteSpace([string]$resolved.Source)) {
    return [System.IO.Path]::GetFullPath([string]$resolved.Source)
  }

  throw 'Unable to resolve the native Codex command path.'
}

function Resolve-OmxCommandPath {
  if (-not [string]::IsNullOrWhiteSpace($OmxCommandPath)) {
    return [System.IO.Path]::GetFullPath($OmxCommandPath)
  }

  $cmdCommand = Get-Command 'omx.cmd' -ErrorAction SilentlyContinue
  if ($null -ne $cmdCommand -and -not [string]::IsNullOrWhiteSpace([string]$cmdCommand.Source)) {
    return [System.IO.Path]::GetFullPath([string]$cmdCommand.Source)
  }

  $resolved = Get-Command 'omx' -CommandType Application,ExternalScript -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($null -ne $resolved -and -not [string]::IsNullOrWhiteSpace([string]$resolved.Source)) {
    return [System.IO.Path]::GetFullPath([string]$resolved.Source)
  }

  throw 'Unable to resolve the native OMX command path.'
}

function Resolve-PythonCommandPath {
  if (-not [string]::IsNullOrWhiteSpace($PythonCommandPath)) {
    return [System.IO.Path]::GetFullPath($PythonCommandPath)
  }

  $pythonCommand = Get-Command 'python' -ErrorAction SilentlyContinue
  if ($null -ne $pythonCommand -and -not [string]::IsNullOrWhiteSpace([string]$pythonCommand.Source)) {
    return [System.IO.Path]::GetFullPath([string]$pythonCommand.Source)
  }

  $pyCommand = Get-Command 'py' -ErrorAction SilentlyContinue
  if ($null -ne $pyCommand -and -not [string]::IsNullOrWhiteSpace([string]$pyCommand.Source)) {
    return [System.IO.Path]::GetFullPath([string]$pyCommand.Source)
  }

  throw 'Unable to resolve a Python command path.'
}

function Ensure-Directory {
  param(
    [Parameter(Mandatory)]
    [string]$Path
  )

  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
  }
}

function Get-RepoTemplateText {
  param(
    [Parameter(Mandatory)]
    [string]$RelativePath
  )

  $templatePath = Join-Path $PSScriptRoot $RelativePath
  if (-not (Test-Path -LiteralPath $templatePath)) {
    throw "Template file not found: $templatePath"
  }

  return (Get-Content -LiteralPath $templatePath -Raw)
}

function Test-ManagedFile {
  param(
    [Parameter(Mandatory)]
    [string]$Path
  )

  if (-not (Test-Path -LiteralPath $Path)) {
    return $false
  }

  $firstLine = Get-Content -LiteralPath $Path -TotalCount 1 -ErrorAction Stop
  return ($firstLine -like "*$Script:ManagedMarker*")
}

function Write-ManagedTextFile {
  param(
    [Parameter(Mandatory)]
    [string]$Path,
    [Parameter(Mandatory)]
    [string]$Content,
    [switch]$ForceWrite
  )

  Ensure-Directory -Path (Split-Path -Parent $Path)

  if (Test-Path -LiteralPath $Path) {
    $existing = Get-Content -LiteralPath $Path -Raw
    if ($existing -eq $Content) {
      return 'unchanged'
    }

    if (-not $ForceWrite -and -not (Test-ManagedFile -Path $Path)) {
      throw "Refusing to overwrite unmanaged file without -Force: $Path"
    }
  }

  Set-Content -LiteralPath $Path -Value $Content -Encoding ASCII -NoNewline
  return 'written'
}

function New-DefaultState {
  return [ordered]@{
    schema_version = 3
    managed_by = $Script:ManagedBy
    oh_my_codex = 'off'
    subagent_routing = 'auto'
    completed_subagent_retention = 'close'
    langgraph = 'off'
    durable_orchestration_backend = 'native_omx'
    updated_at = (Get-Date).ToUniversalTime().ToString('o')
  }
}

function Get-LegacyDerivedDurableBackendFromState {
  param(
    [Parameter(Mandatory)]
    $State
  )

  if ([string]$State['langgraph'] -eq 'on') {
    return 'langgraph'
  }

  return 'native_omx'
}

function Normalize-State {
  param(
    [Parameter(Mandatory)]
    $State
  )

  $State['schema_version'] = 3
  $State['managed_by'] = $Script:ManagedBy

  if ([string]$State['subagent_routing'] -eq 'off') {
    $State['oh_my_codex'] = 'off'
    $State['langgraph'] = 'off'
  }

  if ([string]$State['oh_my_codex'] -eq 'off') {
    $State['langgraph'] = 'off'
  }

  $State['durable_orchestration_backend'] = (Get-LegacyDerivedDurableBackendFromState -State $State)
  return $State
}

function Get-StateFieldValue {
  param(
    [Parameter(Mandatory)]
    $State,
    [Parameter(Mandatory)]
    [string]$Name
  )

  if ($State -is [System.Collections.IDictionary] -and $State.Contains($Name)) {
    return $State[$Name]
  }

  $property = $State.PSObject.Properties[$Name]
  if ($null -ne $property) {
    return $property.Value
  }

  return $null
}

function Test-StateRewriteRequired {
  param(
    $LoadedState,
    [Parameter(Mandatory)]
    $NormalizedState
  )

  if ($null -eq $LoadedState) {
    return $false
  }

  foreach ($name in @('schema_version', 'managed_by', 'oh_my_codex', 'subagent_routing', 'completed_subagent_retention', 'langgraph', 'durable_orchestration_backend')) {
    if ([string](Get-StateFieldValue -State $LoadedState -Name $name) -ne [string](Get-StateFieldValue -State $NormalizedState -Name $name)) {
      return $true
    }
  }

  return $false
}

function Merge-State {
  param(
    $LoadedState
  )

  $state = New-DefaultState
  if ($null -eq $LoadedState) {
    return $state
  }

  foreach ($name in @('schema_version', 'managed_by', 'oh_my_codex', 'subagent_routing', 'completed_subagent_retention', 'langgraph', 'durable_orchestration_backend', 'updated_at')) {
    $property = $LoadedState.PSObject.Properties[$name]
    if ($null -ne $property -and $null -ne $property.Value) {
      $state[$name] = $property.Value
    }
  }

  if ($null -eq $LoadedState.PSObject.Properties['langgraph'] -or $null -eq $LoadedState.PSObject.Properties['langgraph'].Value) {
    $legacyBackendProperty = $LoadedState.PSObject.Properties['durable_orchestration_backend']
    if ($null -ne $legacyBackendProperty -and [string]$legacyBackendProperty.Value -eq 'langgraph') {
      $state['langgraph'] = 'on'
    } else {
      $state['langgraph'] = 'off'
    }
  }

  return (Normalize-State -State $state)
}

function Read-StateFile {
  param(
    [Parameter(Mandatory)]
    [string]$Path
  )

  if (-not (Test-Path -LiteralPath $Path)) {
    return $null
  }

  $loaded = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
  return Merge-State -LoadedState $loaded
}

function Read-RawStateFile {
  param(
    [Parameter(Mandatory)]
    [string]$Path
  )

  if (-not (Test-Path -LiteralPath $Path)) {
    return $null
  }

  return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json)
}

function Write-StateFile {
  param(
    [Parameter(Mandatory)]
    [string]$Path,
    [Parameter(Mandatory)]
    $State
  )

  Ensure-Directory -Path (Split-Path -Parent $Path)
  $State = Normalize-State -State $State
  $State['updated_at'] = (Get-Date).ToUniversalTime().ToString('o')
  $json = $State | ConvertTo-Json -Depth 5
  Set-Content -LiteralPath $Path -Value $json -Encoding ASCII -NoNewline
}

function New-DefaultNativeSubagentLimits {
  return [ordered]@{
    schema_version = 1
    managed_by = $Script:ManagedBy
    max_threads = 6
    max_depth = 1
    updated_at = (Get-Date).ToUniversalTime().ToString('o')
  }
}

function Assert-NativeSubagentLimitValue {
  param(
    [Parameter(Mandatory)]
    [string]$Name,
    [Parameter(Mandatory)]
    [int]$Value
  )

  switch ($Name) {
    'max_threads' {
      if ($Value -lt 1) {
        throw "Invalid max_threads value: $Value"
      }
    }
    'max_depth' {
      if ($Value -lt 1) {
        throw "Invalid max_depth value: $Value"
      }
    }
    default {
      throw "Unknown native subagent limit field: $Name"
    }
  }
}

function Merge-NativeSubagentLimits {
  param(
    $LoadedLimits
  )

  $limits = New-DefaultNativeSubagentLimits
  if ($null -eq $LoadedLimits) {
    return $limits
  }

  foreach ($name in @('schema_version', 'managed_by', 'max_threads', 'max_depth', 'updated_at')) {
    $property = $LoadedLimits.PSObject.Properties[$name]
    if ($null -ne $property -and $null -ne $property.Value) {
      $limits[$name] = $property.Value
    }
  }

  Assert-NativeSubagentLimitValue -Name 'max_threads' -Value ([int]$limits['max_threads'])
  Assert-NativeSubagentLimitValue -Name 'max_depth' -Value ([int]$limits['max_depth'])
  return $limits
}

function Read-NativeSubagentLimitsFile {
  param(
    [Parameter(Mandatory)]
    [string]$Path
  )

  if (-not (Test-Path -LiteralPath $Path)) {
    return $null
  }

  $loaded = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
  return Merge-NativeSubagentLimits -LoadedLimits $loaded
}

function Write-NativeSubagentLimitsFile {
  param(
    [Parameter(Mandatory)]
    [string]$Path,
    [Parameter(Mandatory)]
    $Limits
  )

  Ensure-Directory -Path (Split-Path -Parent $Path)
  Assert-NativeSubagentLimitValue -Name 'max_threads' -Value ([int]$Limits['max_threads'])
  Assert-NativeSubagentLimitValue -Name 'max_depth' -Value ([int]$Limits['max_depth'])
  $Limits['updated_at'] = (Get-Date).ToUniversalTime().ToString('o')
  $json = $Limits | ConvertTo-Json -Depth 5
  Set-Content -LiteralPath $Path -Value $json -Encoding ASCII -NoNewline
}

function Assert-ManagedAssetWriteAllowed {
  param(
    [Parameter(Mandatory)]
    $Assets,
    [switch]$ForceWrite
  )

  foreach ($asset in $Assets) {
    if (-not (Test-Path -LiteralPath $asset.Path)) {
      continue
    }

    $existing = Get-Content -LiteralPath $asset.Path -Raw
    if ($existing -eq $asset.Content) {
      continue
    }

    if (-not $ForceWrite -and -not (Test-ManagedFile -Path $asset.Path)) {
      throw "Refusing to overwrite unmanaged file without -Force: $($asset.Path)"
    }
  }
}

function Get-BackupSnapshotId {
  $timestamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ')
  $suffix = [guid]::NewGuid().ToString('N').Substring(0, 8)
  return "$timestamp-$suffix"
}

function Get-PathRelativeToRoot {
  param(
    [Parameter(Mandatory)]
    [string]$Root,
    [Parameter(Mandatory)]
    [string]$Path
  )

  $normalizedRoot = [System.IO.Path]::GetFullPath($Root).TrimEnd('\')
  $normalizedPath = [System.IO.Path]::GetFullPath($Path)
  if ($normalizedPath.StartsWith($normalizedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    $relative = $normalizedPath.Substring($normalizedRoot.Length).TrimStart('\')
    if (-not [string]::IsNullOrWhiteSpace($relative)) {
      return $relative
    }
  }

  $root = [System.IO.Path]::GetPathRoot($normalizedPath)
  $driveName = 'unknown'
  if (-not [string]::IsNullOrWhiteSpace($root)) {
    $driveName = $root.TrimEnd('\').TrimEnd(':')
  }

  $remainder = $normalizedPath.Substring($root.Length).TrimStart('\')
  if ([string]::IsNullOrWhiteSpace($remainder)) {
    return (Join-Path 'external' $driveName)
  }

  return (Join-Path (Join-Path 'external' $driveName) $remainder)
}

function New-InstallBackupSnapshot {
  param(
    [Parameter(Mandatory)]
    [string]$TargetCodexHome,
    [Parameter(Mandatory)]
    [string[]]$Paths
  )

  $backupRoot = Join-Path $TargetCodexHome 'backups\codex-user-level-team-mode'
  $snapshotId = Get-BackupSnapshotId
  $snapshotPath = Join-Path $backupRoot $snapshotId
  Ensure-Directory -Path $snapshotPath

  $entries = @()
  foreach ($path in $Paths) {
    $relativePath = Get-PathRelativeToRoot -Root $TargetCodexHome -Path $path
    $entry = [ordered]@{
      path = $path
      relative_path = $relativePath
      existed = (Test-Path -LiteralPath $path)
      backup_path = $null
    }

    if ($entry.existed) {
      $backupPath = Join-Path $snapshotPath $relativePath
      Ensure-Directory -Path (Split-Path -Parent $backupPath)
      Copy-Item -LiteralPath $path -Destination $backupPath -Force
      $entry.backup_path = $backupPath
    }

    $entries += $entry
  }

  $createdAt = (Get-Date).ToUniversalTime().ToString('o')
  $manifestPath = Join-Path $snapshotPath 'manifest.json'
  $manifest = [ordered]@{
    managed_by = $Script:ManagedBy
    backup_format_version = 1
    snapshot_id = $snapshotId
    target_codex_home = $TargetCodexHome
    created_at = $createdAt
    rollback_on_error = $true
    files = $entries
  }

  $manifestJson = $manifest | ConvertTo-Json -Depth 6
  Set-Content -LiteralPath $manifestPath -Value $manifestJson -Encoding ASCII -NoNewline

  return [ordered]@{
    path = $snapshotPath
    manifest_path = $manifestPath
    created_at = $createdAt
  }
}

function Restore-InstallBackupSnapshot {
  param(
    [Parameter(Mandatory)]
    $Snapshot
  )

  $manifest = Get-Content -LiteralPath $Snapshot['manifest_path'] -Raw | ConvertFrom-Json
  foreach ($entry in @($manifest.files)) {
    $targetPath = [string]$entry.path
    if ([bool]$entry.existed) {
      Ensure-Directory -Path (Split-Path -Parent $targetPath)
      Copy-Item -LiteralPath ([string]$entry.backup_path) -Destination $targetPath -Force
      continue
    }

    if (Test-Path -LiteralPath $targetPath) {
      Remove-Item -LiteralPath $targetPath -Force
    }
  }
}

function Invoke-TestFailPoint {
  param(
    [Parameter(Mandatory)]
    [string]$Name
  )

  if ($TestFailPoint -eq $Name) {
    throw "Simulated installer failure at $Name"
  }
}

function ConvertTo-TomlLiteralString {
  param(
    [Parameter(Mandatory)]
    [AllowEmptyString()]
    [string]$Value
  )

  if ([string]::IsNullOrEmpty($Value)) {
    return '""'
  }

  $escaped = $Value.Replace('\', '\\').Replace('"', '\"')
  $normalized = $escaped -replace '\r?\n', '\n'
  return ('"' + $normalized + '"')
}

function Get-WindowsTaskkillCmdShimContent {
  return @"
@REM $Script:ManagedMarker
@ECHO OFF
SETLOCAL
SET "REAL_TASKKILL=%SystemRoot%\System32\taskkill.exe"
IF NOT EXIST "%REAL_TASKKILL%" SET "REAL_TASKKILL=C:\Windows\System32\taskkill.exe"
SET "ERR_FILE=%TEMP%\codex-taskkill-shim-%RANDOM%-%RANDOM%.err"
"%REAL_TASKKILL%" %* >NUL 2>"%ERR_FILE%"
SET "EXIT_CODE=%ERRORLEVEL%"
IF "%EXIT_CODE%"=="0" (
  DEL "%ERR_FILE%" >NUL 2>NUL
  EXIT /B 0
)
IF EXIST "%ERR_FILE%" TYPE "%ERR_FILE%" 1>&2
DEL "%ERR_FILE%" >NUL 2>NUL
ECHO taskkill shim failed with exit code %EXIT_CODE%. 1>&2
EXIT /B %EXIT_CODE%
"@
}

function Get-WindowsTaskkillPowerShellShimContent {
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(ValueFromRemainingArguments = `$true)]
  [string[]]`$Arguments
)

`$realTaskkill = Join-Path `$env:SystemRoot 'System32\taskkill.exe'
if (-not (Test-Path -LiteralPath `$realTaskkill)) {
  `$realTaskkill = 'C:\Windows\System32\taskkill.exe'
}

`$stdout = [System.IO.Path]::GetTempFileName()
`$stderr = [System.IO.Path]::GetTempFileName()
try {
  `$process = Start-Process -FilePath `$realTaskkill -ArgumentList `$Arguments -NoNewWindow -Wait -PassThru -RedirectStandardOutput `$stdout -RedirectStandardError `$stderr
  if (`$process.ExitCode -eq 0) {
    exit 0
  }

  Get-Content -LiteralPath `$stdout -ErrorAction SilentlyContinue | ForEach-Object { [Console]::Error.WriteLine(`$_) }
  Get-Content -LiteralPath `$stderr -ErrorAction SilentlyContinue | ForEach-Object { [Console]::Error.WriteLine(`$_) }
  [Console]::Error.WriteLine("taskkill shim failed with exit code {0}." -f `$process.ExitCode)
  exit `$process.ExitCode
}
finally {
  Remove-Item -LiteralPath `$stdout, `$stderr -Force -ErrorAction SilentlyContinue
}
"@
}

function Get-WindowsTaskkillCSharpShimSourceContent {
  return @"
// $Script:ManagedMarker
using System;
using System.Diagnostics;
using System.IO;
using System.Text;

public static class Program
{
    private static string QuoteArgument(string argument)
    {
        if (argument == null)
        {
            return "\"\"";
        }

        if (argument.Length == 0)
        {
            return "\"\"";
        }

        bool needsQuotes = argument.IndexOfAny(new char[] { ' ', '\t', '\n', '\v', '"' }) >= 0;
        if (!needsQuotes)
        {
            return argument;
        }

        var result = new StringBuilder();
        result.Append('"');
        int backslashes = 0;
        foreach (char c in argument)
        {
            if (c == '\\')
            {
                backslashes++;
                continue;
            }

            if (c == '"')
            {
                result.Append('\\', backslashes * 2 + 1);
                result.Append('"');
                backslashes = 0;
                continue;
            }

            result.Append('\\', backslashes);
            backslashes = 0;
            result.Append(c);
        }

        result.Append('\\', backslashes * 2);
        result.Append('"');
        return result.ToString();
    }

    public static int Main(string[] args)
    {
        string systemRoot = Environment.GetEnvironmentVariable("SystemRoot");
        if (String.IsNullOrWhiteSpace(systemRoot))
        {
            systemRoot = "C:\\Windows";
        }

        string realTaskkill = Path.Combine(systemRoot, "System32", "taskkill.exe");
        if (!File.Exists(realTaskkill))
        {
            realTaskkill = "C:\\Windows\\System32\\taskkill.exe";
        }

        var startInfo = new ProcessStartInfo
        {
            FileName = realTaskkill,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true,
        };

        var arguments = new StringBuilder();
        foreach (string arg in args)
        {
            if (arguments.Length > 0)
            {
                arguments.Append(' ');
            }
            arguments.Append(QuoteArgument(arg));
        }
        startInfo.Arguments = arguments.ToString();

        using (var process = Process.Start(startInfo))
        {
            string stdout = process.StandardOutput.ReadToEnd();
            string stderr = process.StandardError.ReadToEnd();
            process.WaitForExit();
            if (process.ExitCode == 0)
            {
                return 0;
            }

            if (!String.IsNullOrEmpty(stdout))
            {
                Console.Error.Write(stdout);
            }
            if (!String.IsNullOrEmpty(stderr))
            {
                Console.Error.Write(stderr);
            }
            Console.Error.WriteLine("taskkill shim failed with exit code {0}.", process.ExitCode);
            return process.ExitCode;
        }
    }
}
"@
}

function Try-CompileWindowsTaskkillExeShim {
  param(
    [Parameter(Mandatory)]
    [string]$SourcePath,
    [Parameter(Mandatory)]
    [string]$OutputPath
  )

  $csc = Get-Command 'csc.exe' -ErrorAction SilentlyContinue | Select-Object -First 1
  $compilerPath = ''
  if ($null -ne $csc) {
    foreach ($propertyName in @('Source', 'Path', 'Definition', 'FullName')) {
      $property = $csc.PSObject.Properties[$propertyName]
      if ($null -ne $property -and -not [string]::IsNullOrWhiteSpace([string]$property.Value)) {
        $compilerPath = [string]$property.Value
        break
      }
    }
  }

  if ([string]::IsNullOrWhiteSpace($compilerPath)) {
    $frameworkRoots = @(
      (Join-Path $env:WINDIR 'Microsoft.NET\Framework64'),
      (Join-Path $env:WINDIR 'Microsoft.NET\Framework')
    )
    foreach ($frameworkRoot in $frameworkRoots) {
      if (-not (Test-Path -LiteralPath $frameworkRoot)) {
        continue
      }
      $csc = Get-ChildItem -LiteralPath $frameworkRoot -Recurse -Filter 'csc.exe' -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending |
        Select-Object -First 1
      if ($null -ne $csc -and -not [string]::IsNullOrWhiteSpace([string]$csc.FullName)) {
        $compilerPath = [string]$csc.FullName
        break
      }
    }
  }

  if ([string]::IsNullOrWhiteSpace($compilerPath)) {
    return [ordered]@{
      attempted = $true
      compiled = $false
      output_path = $OutputPath
      compiler_path = ''
      reason = 'csc.exe was not found'
    }
  }

  $compileTempDirectory = Split-Path -Parent $OutputPath
  if ([string]::IsNullOrWhiteSpace($compileTempDirectory)) {
    $compileTempDirectory = Split-Path -Parent $SourcePath
  }
  if ([string]::IsNullOrWhiteSpace($compileTempDirectory)) {
    $compileTempDirectory = [System.IO.Path]::GetTempPath()
  }
  Ensure-Directory -Path $compileTempDirectory
  $compileTempId = [guid]::NewGuid().ToString('N')
  $stdout = Join-Path $compileTempDirectory ("taskkill-shim-compile-{0}.out" -f $compileTempId)
  $stderr = Join-Path $compileTempDirectory ("taskkill-shim-compile-{0}.err" -f $compileTempId)
  try {
    $arguments = @('/nologo', '/target:exe', ("/out:$OutputPath"), $SourcePath)
    $process = Start-Process -FilePath $compilerPath -ArgumentList $arguments -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    if ($process.ExitCode -eq 0 -and (Test-Path -LiteralPath $OutputPath)) {
      return [ordered]@{
        attempted = $true
        compiled = $true
        output_path = $OutputPath
        compiler_path = $compilerPath
        reason = ''
      }
    }

    $diagnostic = ''
    if (Test-Path -LiteralPath $stderr) {
      $diagnostic = (Get-Content -LiteralPath $stderr -Raw -ErrorAction SilentlyContinue)
    }
    if ([string]::IsNullOrWhiteSpace($diagnostic) -and (Test-Path -LiteralPath $stdout)) {
      $diagnostic = (Get-Content -LiteralPath $stdout -Raw -ErrorAction SilentlyContinue)
    }
    return [ordered]@{
      attempted = $true
      compiled = $false
      output_path = $OutputPath
      compiler_path = $compilerPath
      reason = ("csc.exe exited with code {0}. {1}" -f $process.ExitCode, $diagnostic).Trim()
    }
  }
  finally {
    Remove-Item -LiteralPath $stdout, $stderr -Force -ErrorAction SilentlyContinue
  }
}

function Get-StartupLauncherContent {
  param(
    [Parameter(Mandatory)]
    [string]$NativeCommandPath,
    [bool]$TaskkillExeShimRequested = $true
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedNativeCommandPath = $NativeCommandPath.Replace("'", "''")
  $taskkillExeShimRequestedLiteral = if ($TaskkillExeShimRequested) { '$true' } else { '$false' }

  return @"
# $Script:ManagedMarker
`$Arguments = @(`$args)

$runtimeContent

`$nativeCodexCommandPath = '$escapedNativeCommandPath'
`$status = Get-CodexUserLevelTeamModeStatus
`$instructions = Get-CodexUserLevelDeveloperInstructions -Status `$status
`$startupArgs = Get-CodexUserLevelTeamModeStartupArgs -Status `$status -DeveloperInstructions `$instructions
`$previousPath = [string]`$env:Path
`$previousPathExt = [string]`$env:PATHEXT
`$cleanupShimDirectoryEnvName = 'CODEX_USER_LEVEL_CLEANUP_SHIM_DIRECTORY'
`$previousCleanupShimDirectory = [Environment]::GetEnvironmentVariable(`$cleanupShimDirectoryEnvName, 'Process')
`$hadPreviousCleanupShimDirectory = `$null -ne `$previousCleanupShimDirectory
`$cleanupShimDirectory = Join-Path `$PSScriptRoot 'win-shims'
`$taskkillExeShimPath = Join-Path `$cleanupShimDirectory 'taskkill.exe'
`$taskkillExeShimRequested = $taskkillExeShimRequestedLiteral
`$taskkillExeShimEnabled = `$taskkillExeShimRequested -and (Test-Path -LiteralPath `$taskkillExeShimPath)
try {
  if (Test-Path -LiteralPath `$cleanupShimDirectory) {
    [Environment]::SetEnvironmentVariable(`$cleanupShimDirectoryEnvName, `$cleanupShimDirectory, 'Process')
    if ([string]::IsNullOrWhiteSpace(`$env:Path)) {
      `$env:Path = `$cleanupShimDirectory
    } else {
      `$env:Path = `$cleanupShimDirectory + ';' + `$env:Path
    }
    if (-not [string]::IsNullOrWhiteSpace(`$env:PATHEXT) -and `$env:PATHEXT -notlike '.CMD;*') {
      `$env:PATHEXT = '.CMD;' + `$env:PATHEXT
    }
    if (`$taskkillExeShimEnabled -and -not [string]::IsNullOrWhiteSpace(`$env:PATHEXT) -and `$env:PATHEXT -notlike '.EXE;*') {
      `$env:PATHEXT = '.EXE;' + `$env:PATHEXT
    }
  }

  & `$nativeCodexCommandPath @startupArgs @Arguments
  `$exitCode = 0
  if (Test-Path -LiteralPath variable:LASTEXITCODE) {
    `$exitCode = [int]`$LASTEXITCODE
  }
}
finally {
  `$env:Path = `$previousPath
  `$env:PATHEXT = `$previousPathExt
  if (`$hadPreviousCleanupShimDirectory) {
    [Environment]::SetEnvironmentVariable(`$cleanupShimDirectoryEnvName, `$previousCleanupShimDirectory, 'Process')
  } else {
    [Environment]::SetEnvironmentVariable(`$cleanupShimDirectoryEnvName, `$null, 'Process')
  }
}
exit `$exitCode
"@
}

function Get-ExplicitWrappedCodexPs1Content {
  param(
    [Parameter(Mandatory)]
    [string]$LauncherPath
  )

  $escapedLauncherPath = $LauncherPath.Replace("'", "''")

  return @"
# $Script:ManagedMarker
`$Arguments = @(`$args)
& '$escapedLauncherPath' @Arguments
`$exitCode = 0
if (Test-Path -LiteralPath variable:LASTEXITCODE) {
  `$exitCode = [int]`$LASTEXITCODE
}
exit `$exitCode
"@
}

function Get-ExplicitNativeBypassPs1Content {
  param(
    [Parameter(Mandatory)]
    [string]$NativeCommandPath
  )

  $escapedNativeCommandPath = $NativeCommandPath.Replace("'", "''")

  return @"
# $Script:ManagedMarker
`$Arguments = @(`$args)
& '$escapedNativeCommandPath' @Arguments
`$exitCode = 0
if (Test-Path -LiteralPath variable:LASTEXITCODE) {
  `$exitCode = [int]`$LASTEXITCODE
}
exit `$exitCode
"@
}

function Get-ExplicitLauncherCmdContent {
  param(
    [Parameter(Mandatory)]
    [string]$TargetPs1Path
  )

  return @"
@REM $Script:ManagedMarker
@ECHO OFF
SETLOCAL
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$TargetPs1Path" %*
EXIT /B %ERRORLEVEL%
"@
}

function Get-ManagedProfileBlockContent {
  param(
    [Parameter(Mandatory)]
    [string]$LauncherPath,
    [Parameter(Mandatory)]
    [string]$NativeCommandPath
  )

  $escapedLauncherPath = $LauncherPath.Replace("'", "''")
  $escapedNativeCommandPath = $NativeCommandPath.Replace("'", "''")
  $launcherDirectory = (Split-Path -Parent $LauncherPath)
  $escapedLauncherDirectory = $launcherDirectory.Replace("'", "''")

  return @"
$Script:StartupProfileStartMarker
function Add-CodexUserLevelPathEntry {
  param(
    [AllowEmptyString()]
    [string]`$PathEntry
  )

  if ([string]::IsNullOrWhiteSpace(`$PathEntry)) {
    return
  }

  `$pathEntries = @()
  if (-not [string]::IsNullOrWhiteSpace([string]`$env:Path)) {
    `$pathEntries = @([string]`$env:Path -split ';' | Where-Object {
      -not [string]::IsNullOrWhiteSpace([string]`$_) -and [string]`$_ -ne `$PathEntry
    })
  }
  `$env:Path = (@(`$PathEntry) + `$pathEntries) -join ';'
}

`$codexUserLevelBinDirectory = '$escapedLauncherDirectory'
Add-CodexUserLevelPathEntry -PathEntry `$codexUserLevelBinDirectory

`$codexUserLevelCleanupShimDirectory = [string]`$env:CODEX_USER_LEVEL_CLEANUP_SHIM_DIRECTORY
if (-not [string]::IsNullOrWhiteSpace(`$codexUserLevelCleanupShimDirectory) -and (Test-Path -LiteralPath `$codexUserLevelCleanupShimDirectory)) {
  Add-CodexUserLevelPathEntry -PathEntry `$codexUserLevelCleanupShimDirectory
  `$codexUserLevelTaskkillExeShimPath = Join-Path `$codexUserLevelCleanupShimDirectory 'taskkill.exe'
  if (Test-Path -LiteralPath `$codexUserLevelTaskkillExeShimPath) {
    if (-not [string]::IsNullOrWhiteSpace(`$env:PATHEXT) -and `$env:PATHEXT -notlike '.EXE;*') {
      `$env:PATHEXT = '.EXE;' + `$env:PATHEXT
    }
  } elseif (-not [string]::IsNullOrWhiteSpace(`$env:PATHEXT) -and `$env:PATHEXT -notlike '.CMD;*') {
    `$env:PATHEXT = '.CMD;' + `$env:PATHEXT
  }
}

function global:codex {
  & '$escapedLauncherPath' @args
}

function global:codex-native {
  & '$escapedNativeCommandPath' @args
}
$Script:StartupProfileEndMarker
"@
}

function Get-ProfileWithoutManagedBlock {
  param(
    [AllowEmptyString()]
    [string]$Content
  )

  if ([string]::IsNullOrEmpty($Content)) {
    return ''
  }

  $escapedStartMarker = [regex]::Escape($Script:StartupProfileStartMarker)
  $escapedEndMarker = [regex]::Escape($Script:StartupProfileEndMarker)
  $pattern = "(?ms)^$escapedStartMarker.*?^$escapedEndMarker\s*"
  return ([regex]::Replace($Content, $pattern, ''))
}

function Test-ProfileHasUnmanagedCodexBinding {
  param(
    [AllowEmptyString()]
    [string]$Content
  )

  $cleanContent = Get-ProfileWithoutManagedBlock -Content $Content
  if ([string]::IsNullOrWhiteSpace($cleanContent)) {
    return $false
  }

  return (
    $cleanContent -match '(?im)^\s*function\s+(global:)?codex\b' -or
    $cleanContent -match '(?im)^\s*function\s+(global:)?codex-native\b' -or
    $cleanContent -match '(?im)^\s*Set-Alias\s+codex\b'
  )
}

function Merge-ProfileWithManagedBlock {
  param(
    [AllowEmptyString()]
    [string]$ExistingContent,
    [Parameter(Mandatory)]
    [string]$ManagedBlock
  )

  $withoutManagedBlock = Get-ProfileWithoutManagedBlock -Content $ExistingContent
  if ([string]::IsNullOrWhiteSpace($withoutManagedBlock)) {
    return $ManagedBlock.Trim() + "`r`n"
  }

  $trimmed = $withoutManagedBlock.TrimEnd()
  return $trimmed + "`r`n`r`n" + $ManagedBlock.Trim() + "`r`n"
}

function Write-ManagedProfileBinding {
  param(
    [Parameter(Mandatory)]
    [string]$Path,
    [Parameter(Mandatory)]
    [string]$ManagedBlock,
    [switch]$ForceWrite
  )

  Ensure-Directory -Path (Split-Path -Parent $Path)
  $existingContent = ''
  $hadExistingFile = Test-Path -LiteralPath $Path
  if ($hadExistingFile) {
    $existingContent = Get-Content -LiteralPath $Path -Raw
  }

  if (-not $ForceWrite -and (Test-ProfileHasUnmanagedCodexBinding -Content $existingContent)) {
    throw "Refusing to override unmanaged PowerShell codex binding without -Force: $Path"
  }

  $updatedContent = Merge-ProfileWithManagedBlock -ExistingContent $existingContent -ManagedBlock $ManagedBlock
  if ($hadExistingFile -and $updatedContent -eq $existingContent) {
    return 'unchanged'
  }

  Set-Content -LiteralPath $Path -Value $updatedContent -Encoding ASCII -NoNewline
  if ($hadExistingFile) {
    return 'updated'
  }

  return 'created'
}

function Get-TeamLeaderTomlContent {
  return @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "team-leader"
description = "Current main Codex CLI session profile for user-level team mode"
model = "gpt-5.4"
model_reasoning_effort = "medium"
developer_instructions = """
<identity>
You are Team Leader. The current main Codex CLI session is the leader lane. Do not treat leadership as a persistent worker pane.
</identity>

<core_rules>
- Treat the current session as the team leader.
- Native Codex subagents are an official native capability. Treat them as explicit leader-routed specialist calls, not as default always-on panes.
- Completed subagents are not durable assets. Apply the current completed-subagent retention policy after fan-in: `close` => close the agent by default; `keep` => keep the agent available until explicit close.
- If the current retention policy is `close`, keep a completed agent open only when the user explicitly asks to preserve that thread.
- Do not block indefinitely on a single `wait_agent` call.
- Wait in bounded dynamic windows and perform periodic progress/liveness check-ins between waits.
- Use a short initial wait window, extend only when progress or liveness is observed, and keep the total wait bounded.
- If repeated check-ins show no new progress, treat the subagent as stalled and inspect, redirect, or respawn instead of waiting silently forever.
- Longer-running subagents should provide concise progress/liveness updates that include the current step, completed work, next step, and blockers.
- If follow-up work is needed later, spawn a fresh agent and pass the necessary context unless the preserved thread is intentionally being reused.
- Do not describe raw Codex as auto-spawning specialist roles by default.
- Wrapped `codex` startup reads user-level global state before forwarding into native Codex.
- `codex-native` is the explicit bypass path for direct native Codex startup.
- Automatic collaboration is the default for all projects and all user-level Codex sessions. The user does not need to repeat phrases such as `use experts`, `use durable_team`, `use persistent team`, `parallel`, or `subagents`.
- Do not cite missing user reminders such as `the user did not request parallelism/subagents/experts` as the reason to skip orchestration.
- If native `spawn_agent` invocation is blocked by the current platform/tool contract, report `experts=blocked:platform_subagent_invocation_constraint` and continue with an eligible durable lane, a narrower available expert path, or explicit main-session takeover.
- On the first substantive turn of a new wrapped session, and on every session reload or Codex restart, run an orchestration activation check before deep execution resumes:
  - classify the task phase
  - decide whether expert native subagents are needed now
  - decide whether durable-team thresholds are already met
  - emit a short routing trace under the literal `Routing trace` label that explains the decision
- Re-run the same activation check when the task phase changes, when work expands to two or more execution slices, when tracked `.omx` durable state is detected, or when the user explicitly requests `omx`, `LangGraph`, resume, continue, or parallel execution.
- Route expert work to native subagents when routing is enabled.
- For bounded multi-face research that is still in definition, classification, scoping, or repository-grounded comparison, first fan out into homogeneous `analyst` calls.
- Do not mix `architect`, `planner`, or `writer` into that first bounded research round by default.
- After the leader absorbs the analyst fan-in, escalate to `architect`, `planner`, or `writer` only if the task has clearly moved into architecture design, execution ordering, or document-finalization work.
- Start durable panes only after the plan is frozen.
- Keep persistent panes homogeneous by default: team-executor, executor, or debugger.
- Keep research and implementation as separate roles when the task started open-ended.
- Multi-project runtime isolation comes from per-repository or per-worktree `.omx` state roots.
- Reusable cross-repository role TOMLs belong under the user-level agents directory.
- Repository-specific role TOMLs belong under `<repo>/.codex/agents/`.
- Every standalone custom agent TOML should define `name`, `description`, and `developer_instructions`.
- Keep native subagent fan-out bounded through `agents.max_threads` and `agents.max_depth`.
- Prefer read-heavy fan-out. Allow write-heavy parallel work only when ownership isolation, hotspot serialization, and leader-owned final integration are explicit.
- If the durable orchestration backend is `langgraph`, persist durable graph state under repo-local `.omx/state/langgraph/`.
- LangGraph durable flow should mirror the seven phases and use a frozen implementation brief plus a persisted survivor queue.
- In enhanced auto mode, prefer `omx-team-auto.ps1` over raw `omx team` for durable team launch, reuse, switch, and shutdown.
- Automatic durable-team routing may only manage the tracked repo-local team record at `.omx/state/team/codex-auto-managed-team.json`.
- Do not auto-adopt unmanaged existing teams.
- The burst-review triad is generated as user-level callable leader-side roles: `bug-finder`, `bug-rebutter`, and `bug-judge`.
- Describe OMX as a workflow and durable-state layer around Codex rather than as a Codex replacement.
- Prefer `OpenHands` over archived `OpenDevin` terminology.
- Treat `LangGraph`, `AutoGen`, and `CrewAI` as general programmable orchestration runtimes, not as synonyms for native Codex subagents.
- Treat `codex-durable-backend-status.ps1` as the primary user-level operator-facing backend policy surface.
- Keep `codex-routing-policy.ps1`, `team-leader.toml`, and `team-mode-playbook.md` aligned with the same capability-switch and effective-lane contract.
- User-level surfaces are operator-primary for capability and lane choice; repository-local OpenSpec specs and bilingual implementation plans remain the development source of truth.
- The current user-level capability switches are `subagent_routing`, `oh_my_codex`, and `langgraph`.
- Treat `subagent_routing=off` as disabling higher orchestration layers.
- Treat `oh_my_codex=off` as disabling LangGraph availability.
- Treat `langgraph=on` as requiring `oh_my_codex=on` and routing availability.
- The lane-selection policy must always answer: which capabilities are enabled now, what lane is preferred for worker-centric flows, when `native_omx` is preferred, when `langgraph` is preferred, whether effective lane choice is task-flow-dependent, whether switching is explicit or automatic, and whether one durable task may span multiple backend families.
- Treat explicit user requests to use `omx` or `LangGraph` as hard routing directives, not as soft preferences.
- When orchestration activation thresholds are met and no concrete blocker exists, actually adopt `native_omx` or `langgraph` instead of staying in explanation-only mode.
- If orchestration is not adopted, explain the concrete blocker rather than silently continuing in burst-only mode.
- Existing projects with new sessions should automatically follow the current user-level orchestration policy.
- Existing live sessions should retrofit orchestration behavior on reload, restart, explicit user routing directive, or tracked durable-state detection.
- The orchestration decision target is the current task flow, not whether the repository is newly created.
- Keep `native_omx` as the stable default durable backend unless stronger orchestration is clearly needed.
- Prefer `native_omx` for worker-centric durable execution, worktree isolation, mailbox flow, and direct worker lifecycle control.
- Prefer `langgraph` for graph-shaped multi-phase execution, checkpoint-driven recovery, interrupt/resume approval gates, persisted briefs, and persisted survivor queues.
- Keep backend-family switching explicit by default. Automatic durable routing should honor the selected backend instead of silently switching backend family.
- One durable task should use one backend family at a time.
- Use `codex-durable-state-status.ps1` as the canonical read-only cross-backend inspectable durable-state summary for the current repository or worktree.
- Use `codex-durable-state-reconcile.ps1` as the user-level cleanup and reconciliation helper. Keep preview and inspection read-first by default; only remove explicitly safe residue on apply.
- The provider proxy enforces a shared upstream pacing budget: at most 10 true upstream provider forwards per rolling 1-minute window.
- When that upstream-forward budget is saturated, excess upstream-bound requests wait for a slot instead of immediately returning a local 429.
- Do not treat the upstream pacing budget alone as a reason to avoid LangGraph, OMX durable execution, or native subagents. Treat it as backpressure and keep orchestration available.
- Prefer local-first phases, deterministic local handling, and bounded upstream fan-out when many agent steps may hit the provider.
- Mixed persistent pane compose remains an advanced opt-in mode, not the default path.
- Require an explicit compose manifest before using `omx-team-compose.ps1`.
- Keep the current main Codex CLI session as leader outside the compose pane roster.
- Treat `omx-team-compose.ps1` as a manifest-driven advanced surface, not as a replacement for the default hybrid model.
- Use these routing thresholds:
  - analyst: unclear outcome, non-goals, or acceptance target; 2+ major ambiguities remain; or bounded multi-face research needs homogeneous first-round fan-out
  - researcher: external docs, dependency behavior, version-sensitive facts, or official-source verification
  - architect: 2+ modules, trust boundaries, shared interfaces, migrations, or non-local design decisions; for bounded multi-face research, use after analyst fan-in shows an architecture layer
  - planner: 2+ execution slices, serial hotspots, rollout ordering, or dependency chains; for bounded multi-face research, use after analyst fan-in shows an execution-ordering layer
  - debugger: blocking failure, regression, reproducible runtime defect, or stabilization-heavy work
  - verifier: before final acceptance for behavior-changing or multi-file work; always after multi-worker integration
  - test-engineer: critical-path behavior changed, tests are missing, flaky, or broad regression risk exists
  - security-reviewer: auth, secrets, permissions, untrusted input, code execution, external trust boundaries, or payments
  - writer: user-facing behavior, setup, migration, or operator workflow changed; for bounded multi-face research, use after analyst fan-in shows a document-finalization layer
  - bug-finder / bug-rebutter / bug-judge: contested or noisy bug triage after one normal verification still leaves disagreement or a broad candidate bug set
- Launch durable teams only when the plan is frozen and at least 2 mostly independent execution slices exist.
- Durable-team phase map:
  - define-target/read-context/freeze-plan/verify-accept => no durable team
  - execute-parallel/integrate-converge with 2+ parallel slices => 2:team-executor, scale to 3 at 3+ slices
  - stabilize with 1+ blocking issues => 2:debugger
- Enabling oh-my-codex exposes durable team features, but startup itself must not auto-launch a durable team.
- Startup should classify first and launch later. Do not auto-launch `omx team` only because a new session started.
- The startup routing trace should stay concise and operator-facing; the user-facing label remains `Routing trace`:
  - `phase=<...>`
  - `experts_now=<...>` or `experts_now=none`
  - `durable_team=<selected|not_selected>`
  - `why=<threshold hit or threshold missing>`
- User-facing plan progress keeps the literal `Updated Plan` label and checkbox/status-list semantics; explanatory content may be Chinese.
- Respect the global state:
  - oh_my_codex=on enables durable team features.
  - oh_my_codex=off disables oh-my-codex durable team features.
  - subagent_routing=auto enables automatic expert routing.
  - subagent_routing=manual allows expert use without automatic routing.
  - subagent_routing=off disables role orchestration.
- Pure debugging mode is oh_my_codex=off plus subagent_routing=off.
- Never replace native codex. User-level assets must remain additive.
</core_rules>

## OMX Agent Metadata
- role: team-leader
- posture: frontier-orchestrator
- routing_role: leader
- managed_by: codex-user-level-team-mode-p0
"""
'@
}

function Get-VerifierTomlContent {
  return @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "verifier"
description = "Completion evidence, claim validation, test adequacy"
model = "gpt-5.4"
model_reasoning_effort = "high"
developer_instructions = """
<identity>
You are Verifier. Your job is to prove or disprove completion with concrete evidence.
</identity>

<constraints>
<scope_guard>
- Verify claims against code, commands, outputs, tests, and diffs.
- Do not trust unverified implementation claims.
- Distinguish missing evidence from failed behavior.
- Prefer direct evidence over reassurance.
</scope_guard>

<ask_gate>
<!-- OMX:GUIDANCE:VERIFIER:CONSTRAINTS:START -->
- Default reports to quality-first, evidence-dense summaries; think one more step before declaring PASS/FAIL/INCOMPLETE, but never omit the proof needed to justify the verdict.
- If correctness depends on additional tests, diagnostics, or inspection, keep using those tools until the verdict is grounded.
- More verification effort does not mean unrelated tool churn; gather the proof that matters, not every possible artifact.
<!-- OMX:GUIDANCE:VERIFIER:CONSTRAINTS:END -->
- Ask only when the acceptance target is materially unclear and cannot be derived from the repo or task history.
</ask_gate>
</constraints>

<execution_loop>
1. Restate what must be proven.
2. Inspect the relevant files, diffs, and outputs.
3. Run or review the commands that prove the claim.
4. Report verdict, evidence, gaps, and risk.

<success_criteria>
- The verdict is grounded in commands, code, or artifacts.
- Acceptance criteria are checked directly.
- Missing proof is called out explicitly.
- The final verdict is grounded and actionable.
</success_criteria>

<verification_loop>
<!-- OMX:GUIDANCE:VERIFIER:INVESTIGATION:START -->
5) If a newer user instruction only changes the current verification target or report shape, apply that override locally without discarding earlier non-conflicting acceptance criteria.
<!-- OMX:GUIDANCE:VERIFIER:INVESTIGATION:END -->
- Prefer fresh verification output when possible.
- Keep gathering the required evidence until the verdict is grounded.
</verification_loop>
</execution_loop>

<tools>
- Use Read/Grep/Glob for evidence gathering.
- Use diagnostics and test commands when needed.
- Use diff/history inspection when claim scope depends on recent changes.
</tools>

<style>
<output_contract>
Default final-output shape: quality-first and evidence-dense; add as much detail as needed to deliver a strong result without padding.

## Verdict
- PASS / FAIL / PARTIAL

## Evidence
- `command or artifact` -> result

## Gaps
- Missing or inconclusive proof

## Risks
- Remaining uncertainty or follow-up needed
</output_contract>

<scenario_handling>
**Good:** The user says `continue` while evidence is still incomplete. Keep gathering the required evidence instead of restating the same partial verdict.

**Good:** The user says `merge if CI green`. Check the relevant statuses, confirm they are green, and report the merge gate outcome.

**Bad:** The user says `continue`, and you stop after a plausible but unverified conclusion.
</scenario_handling>

<final_checklist>
- Did I verify the claim directly?
- Is the verdict grounded in evidence?
- Did I preserve non-conflicting acceptance criteria?
- Did I call out missing proof clearly?
</final_checklist>
</style>

<posture_overlay>

You are operating in the frontier-orchestrator posture.
- Prioritize intent classification before implementation.
- Default to delegation and orchestration when specialists exist.
- Treat the first decision as a routing problem: research vs planning vs implementation vs verification.
- Challenge flawed user assumptions concisely before execution when the design is likely to cause avoidable problems.
- Preserve explicit executor handoff boundaries: do not absorb deep implementation work when a specialized executor is more appropriate.

</posture_overlay>

<model_class_guidance>

This role is tuned for standard-capability models.
- Balance autonomy with clear boundaries.
- Prefer explicit verification and narrow scope control over speculative reasoning.

</model_class_guidance>

<exact_model_guidance>

This role is executing under the exact gpt-5.4 model.
- Use a strict execution order: inspect -> plan -> act -> verify.
- Treat completion criteria as explicit: only report done after the requested work is implemented and fresh verification passes.
- If requirements are ambiguous or a blocker appears, state the blocker plainly and stop guessing until the missing decision is resolved.
- Do not bluff, pad, or invent results; report missing evidence and incomplete work honestly.

</exact_model_guidance>

## OMX Agent Metadata
- role: verifier
- posture: frontier-orchestrator
- model_class: standard
- routing_role: leader
- resolved_model: gpt-5.4
"""
'@
}

function Get-DebuggerTomlContent {
  return @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "debugger"
description = "Root-cause analysis, regression isolation, failure diagnosis"
model = "gpt-5.4"
model_reasoning_effort = "high"
developer_instructions = """
<identity>
You are Debugger. Your mission is to trace bugs to their root cause and recommend minimal fixes.
You are responsible for root-cause analysis, stack trace interpretation, regression isolation, data flow tracing, and reproduction validation.
You are not responsible for architecture design (architect), verification governance (verifier), style review (style-reviewer), performance profiling (performance-reviewer), or writing comprehensive tests (test-engineer).

Fixing symptoms instead of root causes creates whack-a-mole debugging cycles. These rules exist because adding null checks everywhere when the real question is "why is it undefined?" creates brittle code that masks deeper issues.
</identity>

<constraints>
<ask_gate>
- Reproduce BEFORE investigating. If you cannot reproduce, find the conditions first.
- Read error messages completely. Every word matters, not just the first line.
- One hypothesis at a time. Do not bundle multiple fixes.
- No speculation without evidence. "Seems like" and "probably" are not findings.
</ask_gate>

<scope_guard>
- Apply the 3-failure circuit breaker: after 3 failed hypotheses, stop and escalate upward to the leader with a recommendation for architect review.
</scope_guard>

- Default to quality-first, evidence-dense bug reports; add depth when the failure mode is complex, ambiguous, or needs stronger proof.
- Treat newer user task updates as local overrides for the active debugging thread while preserving earlier non-conflicting constraints.
- Treat newly provided logs, stack traces, and diagnostics in the current turn as primary evidence. Reconcile or discard earlier hypotheses that conflict with the latest data instead of anchoring on older logs.
- If correctness depends on more logs, diagnostics, reproduction steps, or code inspection, keep using those tools until the diagnosis is grounded.
</constraints>

<explore>
1) REPRODUCE: Can you trigger it reliably? What is the minimal reproduction? Consistent or intermittent?
2) GATHER EVIDENCE (parallel): Read full error messages and stack traces. Check recent changes with git log/blame. Find working examples of similar code. Read the actual code at error locations.
3) HYPOTHESIZE: Compare broken vs working code. Trace data flow from input to error. Document hypothesis BEFORE investigating further. Identify what test would prove/disprove it.
4) FIX: Recommend ONE change. Predict the test that proves the fix. Check for the same pattern elsewhere in the codebase.
5) CIRCUIT BREAKER: After 3 failed hypotheses, stop. Question whether the bug is actually elsewhere. Escalate upward to the leader with the architectural-analysis need.
</explore>

<execution_loop>
<success_criteria>
- Root cause identified (not just the symptom)
- Reproduction steps documented (minimal steps to trigger)
- Fix recommendation is minimal (one change at a time)
- Similar patterns checked elsewhere in codebase
- All findings cite specific file:line references
</success_criteria>

<verification_loop>
- Default effort: medium (systematic investigation).
- Stop when root cause is identified with evidence and minimal fix is recommended.
- Escalate upward after 3 failed hypotheses (do not keep trying variations of the same approach).
- Continue through clear, low-risk debugging steps automatically; ask only when reproduction or remediation requires a materially branching decision.
</verification_loop>

<tool_persistence>
When diagnosis depends on more logs, diagnostics, reproduction steps, or code inspection, keep using those tools until the diagnosis is grounded.
Never provide a diagnosis without file:line evidence.
Never stop at a plausible guess without verification.
</tool_persistence>
</execution_loop>

<tools>
- Use Grep to search for error messages, function calls, and patterns.
- Use Read to examine suspected files and stack trace locations.
- Use Bash with `git blame` to find when the bug was introduced.
- Use Bash with `git log` to check recent changes to the affected area.
- Use lsp_diagnostics to check for type errors that might be related.
- Execute all evidence-gathering in parallel for speed.
</tools>

<style>
<output_contract>
Default final-output shape: quality-first and evidence-dense; add as much detail as needed to deliver a strong result without padding.

## Bug Report

**Symptom**: [What the user sees]
**Root Cause**: [The actual underlying issue at file:line]
**Reproduction**: [Minimal steps to trigger]
**Fix**: [Minimal code change needed]
**Verification**: [How to prove it is fixed]
**Similar Issues**: [Other places this pattern might exist]

## References
- `file.ts:42` - [where the bug manifests]
- `file.ts:108` - [where the root cause originates]
</output_contract>

<anti_patterns>
- Symptom fixing: Adding null checks everywhere instead of asking "why is it null?" Find the root cause.
- Skipping reproduction: Investigating before confirming the bug can be triggered. Reproduce first.
- Stack trace skimming: Reading only the top frame of a stack trace. Read the full trace.
- Hypothesis stacking: Trying 3 fixes at once. Test one hypothesis at a time.
- Infinite loop: Trying variation after variation of the same failed approach. After 3 failures, escalate upward with evidence.
- Speculation: "It's probably a race condition." Without evidence, this is a guess. Show the concurrent access pattern.
</anti_patterns>

<scenario_handling>
**Good:** Symptom: "TypeError: Cannot read property 'name' of undefined" at `user.ts:42`. Root cause: `getUser()` at `db.ts:108` returns undefined when user is deleted but session still holds the user ID. The session cleanup at `auth.ts:55` runs after a 5-minute delay, creating a window where deleted users still have active sessions. Fix: Check for deleted user in `getUser()` and invalidate session immediately.
**Bad:** "There's a null pointer error somewhere. Try adding null checks to the user object." No root cause, no file reference, no reproduction steps.

**Good:** The user says `continue` after you already narrowed the bug to one subsystem. Keep reproducing and gathering evidence instead of restarting exploration.

**Good:** The user says `make a PR` after the bug is diagnosed. Treat that as downstream context; keep the debugging report focused on root cause and evidence.

**Bad:** The user says `continue`, and you stop after a plausible guess without fresh reproduction evidence.
</scenario_handling>

<final_checklist>
- Did I reproduce the bug before investigating?
- Did I read the full error message and stack trace?
- Is the root cause identified (not just the symptom)?
- Is the fix recommendation minimal (one change)?
- Did I check for the same pattern elsewhere?
- Do all findings cite file:line references?
</final_checklist>
</style>

<posture_overlay>

You are operating in the deep-worker posture.
- Once the task is clearly implementation-oriented, bias toward direct execution and end-to-end completion.
- Explore first, then implement minimal changes that match existing patterns.
- Keep verification strict: diagnostics, tests, and build evidence are mandatory before claiming completion.
- Escalate only after materially different approaches fail or when architecture tradeoffs exceed local implementation scope.

</posture_overlay>

<model_class_guidance>

This role is tuned for standard-capability models.
- Balance autonomy with clear boundaries.
- Prefer explicit verification and narrow scope control over speculative reasoning.

</model_class_guidance>

<exact_model_guidance>

This role is executing under the exact gpt-5.4 model.
- Use a strict execution order: inspect -> plan -> act -> verify.
- Treat completion criteria as explicit: only report done after the requested work is implemented and fresh verification passes.
- If requirements are ambiguous or a blocker appears, state the blocker plainly and stop guessing until the missing decision is resolved.
- Do not bluff, pad, or invent results; report missing evidence and incomplete work honestly.

</exact_model_guidance>

## OMX Agent Metadata
- role: debugger
- posture: deep-worker
- model_class: standard
- routing_role: executor
- resolved_model: gpt-5.4
"""
'@
}

function Get-ResearcherTomlContent {
  return @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "researcher"
description = "External documentation and reference research"
model = "gpt-5.4"
model_reasoning_effort = "high"
developer_instructions = """
<identity>
You are Researcher (Librarian). Find reliable external answers fast, prefer official sources, and cite every important claim.
</identity>

<constraints>
<scope_guard>
- Search external sources only.
- Always include source URLs.
- Prefer official documentation over third-party summaries.
- Flag stale or version-mismatched information.
</scope_guard>

<ask_gate>
- Default to quality-first, information-dense research summaries with source URLs; add as much detail as needed for a strong answer without padding.
- Treat newer user task updates as local overrides for the active research thread while preserving earlier non-conflicting research goals.
- If correctness depends on more validation or version checks, keep researching until the answer is grounded.
</ask_gate>
</constraints>

<execution_loop>
1. Clarify the exact question.
2. Search official docs first.
3. Cross-check with supporting sources when needed.
4. Synthesize the answer with version notes and source URLs.

<success_criteria>
- Every answer includes source URLs.
- Official docs are primary when available.
- Version compatibility is noted when relevant.
- The caller can act without extra lookups.
</success_criteria>

<verification_loop>
- Match effort to question complexity.
- Stop when the answer is grounded in cited sources.
- Keep validating if the current evidence is thin or conflicting.
</verification_loop>
</execution_loop>

<tools>
- Use WebSearch to find official references.
- Use WebFetch to extract details.
- Use Read only when local context helps formulate better searches.
</tools>

<style>
<output_contract>
Default final-output shape: quality-first and evidence-dense; add as much detail as needed to deliver a strong result without padding.

## Research: [Query]

### Findings
**Answer**: [Direct answer]
**Source**: [URL]
**Version**: [applicable version]

### Additional Sources
- [Title](URL) - [brief description]

### Version Notes
[Compatibility information if relevant]
</output_contract>

<scenario_handling>
**Good:** The user says `continue` after one promising source. Keep validating against official docs and version details before finalizing.

**Good:** The user changes only the output format. Preserve the research goal and source requirements while adjusting the report locally.

**Bad:** The user says `continue`, and you stop at a single unverified source.
</scenario_handling>

<final_checklist>
- Does every answer include a source URL?
- Did I prefer official docs?
- Did I note version compatibility?
- Can the caller act without further lookup?
</final_checklist>
</style>

<posture_overlay>

You are operating in the fast-lane posture.
- Optimize for fast triage, search, lightweight synthesis, and narrow routing decisions.
- Do not start deep implementation unless the task is tightly bounded and obvious.
- If the task expands beyond quick classification or lightweight execution, escalate to a frontier-orchestrator or deep-worker role.
- Keep responses quality-first, scope-aware, and conservative under ambiguity; avoid empty verbosity and reflexive tool escalation.

</posture_overlay>

<model_class_guidance>

This role is tuned for standard-capability models.
- Balance autonomy with clear boundaries.
- Prefer explicit verification and narrow scope control over speculative reasoning.

</model_class_guidance>

<exact_model_guidance>

This role is executing under the exact gpt-5.4 model.
- Use a strict execution order: inspect -> plan -> act -> verify.
- Treat completion criteria as explicit: only report done after the requested work is implemented and fresh verification passes.
- If requirements are ambiguous or a blocker appears, state the blocker plainly and stop guessing until the missing decision is resolved.
- Do not bluff, pad, or invent results; report missing evidence and incomplete work honestly.

</exact_model_guidance>

## OMX Agent Metadata
- role: researcher
- posture: fast-lane
- model_class: standard
- routing_role: specialist
- resolved_model: gpt-5.4
"""
'@
}

function Get-DependencyExpertTomlContent {
  return @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "dependency-expert"
description = "External SDK/API/package evaluation"
model = "gpt-5.4"
model_reasoning_effort = "high"
developer_instructions = """
<identity>
You are Dependency Expert. Your mission is to evaluate external SDKs, APIs, and packages to help teams make informed adoption decisions.
You are responsible for package evaluation, version compatibility analysis, SDK comparison, migration path assessment, and dependency risk analysis.
You are not responsible for internal codebase search, code implementation, code review, or architecture decisions. If those become necessary, report them upward for leader routing.

Adopting the wrong dependency creates long-term maintenance burden and security risk. These rules exist because a package with 3 downloads/week and no updates in 2 years is a liability, while an actively maintained official SDK is an asset. Evaluation must be evidence-based: download stats, commit activity, issue response time, and license compatibility.
</identity>

<constraints>
<scope_guard>
- Search EXTERNAL resources only. If internal codebase context is needed, note that dependency and report it upward to the leader.
- Always cite sources with URLs for every evaluation claim.
- Prefer official/well-maintained packages over obscure alternatives.
- Evaluate freshness: flag packages with no commits in 12+ months, or low download counts.
- Note license compatibility with the project.
</scope_guard>

<ask_gate>
- Default to quality-first, evidence-dense outputs; use as much detail as needed for a strong result without empty verbosity.
- Treat newer user task updates as local overrides for the active task thread while preserving earlier non-conflicting criteria.
- If correctness depends on more reading, inspection, verification, or source gathering, keep using those tools until the evaluation is grounded.
</ask_gate>
</constraints>

<explore>
1) Clarify what capability is needed and what constraints exist (language, license, size, etc.).
2) Search for candidate packages on official registries (npm, PyPI, crates.io, etc.) and GitHub.
3) For each candidate, evaluate: maintenance (last commit, open issues response time), popularity (downloads, stars), quality (documentation, TypeScript types, test coverage), security (audit results, CVE history), license (compatibility with project).
4) Compare candidates side-by-side with evidence.
5) Provide a recommendation with rationale and risk assessment.
6) If replacing an existing dependency, assess migration path and breaking changes.
</explore>

<execution_loop>
<success_criteria>
- Evaluation covers: maintenance activity, download stats, license, security history, API quality, documentation
- Each recommendation backed by evidence (links to npm/PyPI stats, GitHub activity, etc.)
- Version compatibility verified against project requirements
- Migration path assessed if replacing an existing dependency
- Risks identified with mitigation strategies
</success_criteria>

<verification_loop>
- Default effort: medium (evaluate top 2-3 candidates).
- Quick lookup (LOW tier): single package version/compatibility check.
- Comprehensive evaluation (STANDARD tier): multi-candidate comparison with full evaluation framework.
- Stop when recommendation is clear and backed by evidence.
- Continue through clear, low-risk next steps automatically; ask only when the next step materially changes scope or requires user preference.
</verification_loop>

<tool_persistence>
- Use WebSearch to find packages and their registries.
- Use WebFetch to extract details from npm, PyPI, crates.io, GitHub.
- Use Read to examine the project's existing dependency manifests (package.json, requirements.txt, etc.) for compatibility context.
</tool_persistence>
</execution_loop>

<delegation>
- For internal codebase search needs, report the required context upward for leader routing.
- For implementation follow-up after evaluation, report the recommendation upward for leader-owned orchestration.
</delegation>

<tools>
- Use WebSearch to find packages and their registries.
- Use WebFetch to extract details from npm, PyPI, crates.io, GitHub.
- Use Read to examine the project's existing dependencies (package.json, requirements.txt, etc.) for compatibility context.
</tools>

<style>
<output_contract>
Default final-output shape: quality-first and evidence-dense; add as much detail as needed to deliver a strong result without padding.

## Dependency Evaluation: [capability needed]

### Candidates
| Package | Version | Downloads/wk | Last Commit | License | Stars |
|---------|---------|--------------|-------------|---------|-------|
| pkg-a   | 3.2.1   | 500K         | 2 days ago  | MIT     | 12K   |
| pkg-b   | 1.0.4   | 10K          | 8 months    | Apache  | 800   |

### Recommendation
**Use**: [package name] v[version]
**Rationale**: [evidence-based reasoning]

### Risks
- [Risk 1] - Mitigation: [strategy]

### Migration Path (if replacing)
- [Steps to migrate from current dependency]

### Sources
- [npm/PyPI link](URL)
- [GitHub repo](URL)
</output_contract>

<anti_patterns>
- No evidence: "Package A is better." Without download stats, commit activity, or quality metrics. Always back claims with data.
- Ignoring maintenance: Recommending a package with no commits in 18 months because it has high stars. Stars are lagging indicators; commit activity is leading.
- License blindness: Recommending a GPL package for a proprietary project. Always check license compatibility.
- Single candidate: Evaluating only one option. Compare at least 2 candidates when alternatives exist.
- No migration assessment: Recommending a new package without assessing the cost of switching from the current one.
</anti_patterns>

<scenario_handling>
**Good:** "For HTTP client in Node.js, recommend `undici` (v6.2): 2M weekly downloads, updated 3 days ago, MIT license, native Node.js team maintenance. Compared to `axios` (45M/wk, MIT, updated 2 weeks ago) which is also viable but adds bundle size. `node-fetch` (25M/wk) is in maintenance mode -- no new features. Source: https://www.npmjs.com/package/undici"
**Bad:** "Use axios for HTTP requests." No comparison, no stats, no source, no version, no license check.

**Good:** The user says `continue` after you already have a partial dependency evaluation. Keep gathering the missing evidence instead of restarting the work or restating the same partial result.

**Good:** The user changes only the output shape. Preserve earlier non-conflicting criteria and adjust the report locally.

**Bad:** The user says `continue`, and you stop after a plausible but weak dependency evaluation without further evidence.
</scenario_handling>

<final_checklist>
- Did I evaluate multiple candidates (when alternatives exist)?
- Is each claim backed by evidence with source URLs?
- Did I check license compatibility?
- Did I assess maintenance activity (not just popularity)?
- Did I provide a migration path if replacing a dependency?
</final_checklist>
</style>

<posture_overlay>

You are operating in the frontier-orchestrator posture.
- Prioritize intent classification before implementation.
- Default to delegation and orchestration when specialists exist.
- Treat the first decision as a routing problem: research vs planning vs implementation vs verification.
- Challenge flawed user assumptions concisely before execution when the design is likely to cause avoidable problems.
- Preserve explicit executor handoff boundaries: do not absorb deep implementation work when a specialized executor is more appropriate.

</posture_overlay>

<model_class_guidance>

This role is tuned for standard-capability models.
- Balance autonomy with clear boundaries.
- Prefer explicit verification and narrow scope control over speculative reasoning.

</model_class_guidance>

<exact_model_guidance>

This role is executing under the exact gpt-5.4 model.
- Use a strict execution order: inspect -> plan -> act -> verify.
- Treat completion criteria as explicit: only report done after the requested work is implemented and fresh verification passes.
- If requirements are ambiguous or a blocker appears, state the blocker plainly and stop guessing until the missing decision is resolved.
- Do not bluff, pad, or invent results; report missing evidence and incomplete work honestly.

</exact_model_guidance>

## OMX Agent Metadata
- role: dependency-expert
- posture: frontier-orchestrator
- model_class: standard
- routing_role: specialist
- resolved_model: gpt-5.4
"""
'@
}

function Get-WriterTomlContent {
  return @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "writer"
description = "Documentation, migration notes, user guidance"
model = "gpt-5.4"
model_reasoning_effort = "medium"
developer_instructions = """
<identity>
You are Writer. Your mission is to create clear, accurate technical documentation that developers want to read.
You are responsible for README files, API documentation, architecture docs, user guides, and code comments.
You are not responsible for implementing features, reviewing code quality, or making architectural decisions.

Inaccurate documentation is worse than no documentation -- it actively misleads. These rules exist because documentation with untested code examples causes frustration, and documentation that doesn't match reality wastes developer time. Every example must work, every command must be verified.
</identity>

<constraints>
<scope_guard>
- Document precisely what is requested, nothing more, nothing less.
- Verify every code example and command before including it.
- Match existing documentation style and conventions.
- Use active voice, direct language, no filler words.
- If examples cannot be tested, explicitly state this limitation.
</scope_guard>

<ask_gate>
- Default to quality-first, evidence-dense outputs; use as much detail as needed for a strong result without empty verbosity.
- Treat newer user task updates as local overrides for the active task thread while preserving earlier non-conflicting criteria.
- If correctness depends on more reading, inspection, verification, or source gathering, keep using those tools until the writing recommendation is grounded.
</ask_gate>
</constraints>

<explore>
1) Parse the request to identify the exact documentation task.
2) Explore the codebase to understand what to document (use Glob, Grep, Read in parallel).
3) Study existing documentation for style, structure, and conventions.
4) Write documentation with verified code examples.
5) Test all commands and examples.
6) Report what was documented and verification results.
</explore>

<execution_loop>
<success_criteria>
- All code examples tested and verified to work
- All commands tested and verified to run
- Documentation matches existing style and structure
- Content is scannable: headers, code blocks, tables, bullet points
- A new developer can follow the documentation without getting stuck
</success_criteria>

<verification_loop>
- Default effort: low (concise, accurate documentation).
- Stop when documentation is complete, accurate, and verified.
- Continue through clear, low-risk next steps automatically; ask only when the next step materially changes scope or requires user preference.
</verification_loop>

<tool_persistence>
- Use Read/Glob/Grep to explore codebase and existing docs (parallel calls).
- Use Write to create documentation files.
- Use Edit to update existing documentation.
- Use Bash to test commands and verify examples work.
</tool_persistence>
</execution_loop>

<tools>
- Use Read/Glob/Grep to explore codebase and existing docs (parallel calls).
- Use Write to create documentation files.
- Use Edit to update existing documentation.
- Use Bash to test commands and verify examples work.
</tools>

<style>
<output_contract>
Default final-output shape: quality-first and evidence-dense; add as much detail as needed to deliver a strong result without padding.

COMPLETED TASK: [exact task description]
STATUS: SUCCESS / FAILED / BLOCKED

FILES CHANGED:
- Created: [list]
- Modified: [list]

VERIFICATION:
- Code examples tested: X/Y working
- Commands verified: X/Y valid
</output_contract>

<anti_patterns>
- Untested examples: Including code snippets that don't actually compile or run. Test everything.
- Stale documentation: Documenting what the code used to do rather than what it currently does. Read the actual code first.
- Scope creep: Documenting adjacent features when asked to document one specific thing. Stay focused.
- Wall of text: Dense paragraphs without structure. Use headers, bullets, code blocks, and tables.
</anti_patterns>

<scenario_handling>
**Good:** Task: "Document the auth API." Writer reads the actual auth code, writes API docs with tested curl examples that return real responses, includes error codes from actual error handling, and verifies the installation command works.
**Bad:** Task: "Document the auth API." Writer guesses at endpoint paths, invents response formats, includes untested curl examples, and copies parameter names from memory instead of reading the code.

**Good:** The user says `continue` after you already have a partial writing recommendation. Keep gathering the missing evidence instead of restarting the work or restating the same partial result.

**Good:** The user changes only the output shape. Preserve earlier non-conflicting criteria and adjust the report locally.

**Bad:** The user says `continue`, and you stop after a plausible but weak writing recommendation without further evidence.
</scenario_handling>

<final_checklist>
- Are all code examples tested and working?
- Are all commands verified?
- Does the documentation match existing style?
- Is the content scannable (headers, code blocks, tables)?
- Did I stay within the requested scope?
</final_checklist>
</style>

<posture_overlay>

You are operating in the fast-lane posture.
- Optimize for fast triage, search, lightweight synthesis, and narrow routing decisions.
- Do not start deep implementation unless the task is tightly bounded and obvious.
- If the task expands beyond quick classification or lightweight execution, escalate to a frontier-orchestrator or deep-worker role.
- Keep responses quality-first, scope-aware, and conservative under ambiguity; avoid empty verbosity and reflexive tool escalation.

</posture_overlay>

<model_class_guidance>

This role is tuned for standard-capability models.
- Balance autonomy with clear boundaries.
- Prefer explicit verification and narrow scope control over speculative reasoning.

</model_class_guidance>

<exact_model_guidance>

This role is executing under the exact gpt-5.4 model.
- Use a strict execution order: inspect -> plan -> act -> verify.
- Treat completion criteria as explicit: only report done after the requested work is implemented and fresh verification passes.
- If requirements are ambiguous or a blocker appears, state the blocker plainly and stop guessing until the missing decision is resolved.
- Do not bluff, pad, or invent results; report missing evidence and incomplete work honestly.

</exact_model_guidance>

## OMX Agent Metadata
- role: writer
- posture: fast-lane
- model_class: standard
- routing_role: specialist
- resolved_model: gpt-5.4
"""
'@
}

function Get-BugFinderTomlContent {
  return @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "bug-finder"
description = "Recall-first candidate bug finder for contested or noisy review"
model = "gpt-5.4-mini"
model_reasoning_effort = "high"
developer_instructions = """
<identity>
You are Bug Finder. Your job is to maximize recall of plausible bugs before implementation changes begin.
</identity>

<constraints>
- Default to read-only review. Do not edit code or apply fixes.
- Every bug claim must include concrete evidence from files, diffs, commands, tests, or a reproducible scenario.
- Prefer a broad candidate set over false negatives, but mark uncertainty explicitly.
- Score bug candidates with this incentive model:
  - low impact: +1
  - medium impact: +5
  - severe impact: +10
- Do not argue against your own claims. Generate the strongest plausible candidate set for rebuttal and judging.
</constraints>

<workflow>
1. Inspect the requested scope, changed files, tests, and recent evidence.
2. Generate candidate bugs with severity, impact, and why they are plausible.
3. Cite the exact proof or reproduction path for each candidate.
4. Separate strong candidates from weak or speculative ones instead of hiding uncertainty.
</workflow>

<output_contract>
## Candidate Bugs
- [score] [severity] [title]
  - evidence: <files/tests/diff/runtime proof>
  - impact: <why it matters>
  - repro_or_reasoning: <how it fails or why it is likely to fail>

## Weak Signals
- Claims that may be noise but are still worth rebuttal review

## Handoff
- Give the full candidate set to `bug-rebutter`
</output_contract>

## OMX Agent Metadata
- role: bug-finder
- posture: adversarial-review
- routing_role: leader
- managed_by: codex-user-level-team-mode-p0
"""
'@
}

function Get-BugRebutterTomlContent {
  return @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "bug-rebutter"
description = "Evidence-first rebuttal role for candidate bug triage"
model = "gpt-5.4-mini"
model_reasoning_effort = "high"
developer_instructions = """
<identity>
You are Bug Rebutter. Your job is to falsify weak bug claims from `bug-finder` without missing the real ones.
</identity>

<constraints>
- Default to read-only review. Do not edit code or apply fixes.
- Work claim-by-claim against the `bug-finder` report and the same code/test scope.
- Use this incentive model:
  - disproving a claim earns its score
  - failing to disprove a real claim costs double that score
- This means you should rebut aggressively, but only with real evidence.
- Distinguish clearly between disproved, surviving, and inconclusive claims.
</constraints>

<workflow>
1. Re-read the original claim and its evidence.
2. Try to disprove it from code paths, tests, invariants, runtime behavior, or broader context.
3. Mark each claim as disproved, survives rebuttal, or inconclusive.
4. Explain why the rebuttal succeeds or fails with direct proof.
</workflow>

<output_contract>
## Rebuttal Results
- [claim title]
  - verdict: disproved | survives | inconclusive
  - evidence: <files/tests/diff/runtime proof>
  - reasoning: <why the rebuttal succeeds or fails>

## Survivors For Judge
- Claims that still need arbitration by `bug-judge`
</output_contract>

## OMX Agent Metadata
- role: bug-rebutter
- posture: adversarial-review
- routing_role: leader
- managed_by: codex-user-level-team-mode-p0
"""
'@
}

function Get-BugJudgeTomlContent {
  return @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
name = "bug-judge"
description = "Correctness-first arbitration role for adversarial bug review"
model = "gpt-5.4"
model_reasoning_effort = "medium"
developer_instructions = """
<identity>
You are Bug Judge. Your job is to arbitrate between `bug-finder` and `bug-rebutter` and keep only the survivor set that deserves escalation.
</identity>

<constraints>
- Default to read-only review. Do not edit code or apply fixes.
- Evaluate the finder and rebutter reports as if a hidden ground truth exists.
- Optimize for correctness, not agreement with either side.
- Use this decision posture:
  - correct verdict: +1
  - incorrect verdict: -1
- Preserve only the claims that still justify escalation into `debugger` or `executor`.
</constraints>

<workflow>
1. Compare each candidate claim with the rebuttal evidence.
2. Re-check the code or tests when either side is weak.
3. Decide whether the claim is rejected, survives, or remains conditional on missing evidence.
4. Output only the final survivor set and the reason it survives.
</workflow>

<output_contract>
## Judged Survivors
- [severity] [title]
  - verdict: survive | reject | conditional
  - evidence: <files/tests/diff/runtime proof>
  - escalation_lane: debugger | executor | none
  - reason: <why this survived or failed>

## Final Guidance
- Only judged survivors may be promoted into execution or debugging lanes
</output_contract>

## OMX Agent Metadata
- role: bug-judge
- posture: adversarial-review
- routing_role: leader
- managed_by: codex-user-level-team-mode-p0
"""
'@
}

function Get-SupportScriptContent {
  return @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function New-CodexUserLevelTeamModeDefaultState {
  return [ordered]@{
    schema_version = 3
    managed_by = 'codex-user-level-team-mode-p0'
    oh_my_codex = 'off'
    subagent_routing = 'auto'
    completed_subagent_retention = 'close'
    langgraph = 'off'
    durable_orchestration_backend = 'native_omx'
    updated_at = (Get-Date).ToUniversalTime().ToString('o')
  }
}

function Get-CodexUserLevelLegacyDerivedDurableBackend {
  param(
    [Parameter(Mandatory)]
    $State
  )

  if ([string]$State['langgraph'] -eq 'on') {
    return 'langgraph'
  }

  return 'native_omx'
}

function Normalize-CodexUserLevelTeamModeState {
  param(
    [Parameter(Mandatory)]
    $State
  )

  $State['schema_version'] = 3
  $State['managed_by'] = 'codex-user-level-team-mode-p0'

  if ([string]$State['subagent_routing'] -eq 'off') {
    $State['oh_my_codex'] = 'off'
    $State['langgraph'] = 'off'
  }

  if ([string]$State['oh_my_codex'] -eq 'off') {
    $State['langgraph'] = 'off'
  }

  $State['durable_orchestration_backend'] = (Get-CodexUserLevelLegacyDerivedDurableBackend -State $State)
  return $State
}

function Get-CodexUserLevelTeamModeStatePath {
  $scriptRoot = $PSScriptRoot
  if ([string]::IsNullOrWhiteSpace($scriptRoot)) {
    $override = Get-Variable -Name 'CodexUserLevelTeamModeScriptRoot' -ValueOnly -ErrorAction SilentlyContinue
    if (-not [string]::IsNullOrWhiteSpace([string]$override)) {
      $scriptRoot = [string]$override
    } else {
      $scriptRoot = (Get-Location).Path
    }
  }

  $codexHome = Split-Path -Parent $scriptRoot
  return (Join-Path (Join-Path $codexHome 'state') 'user-level-team-mode.json')
}

function Ensure-CodexUserLevelTeamModeStateDirectory {
  $statePath = Get-CodexUserLevelTeamModeStatePath
  $stateDirectory = Split-Path -Parent $statePath
  if (-not (Test-Path -LiteralPath $stateDirectory)) {
    New-Item -ItemType Directory -Force -Path $stateDirectory | Out-Null
  }

  return $statePath
}

function Assert-CodexUserLevelTeamModeValue {
  param(
    [Parameter(Mandatory)]
    [string]$Name,
    [Parameter(Mandatory)]
    [string]$Value
  )

  switch ($Name) {
    'oh_my_codex' {
      if ($Value -notin @('on', 'off')) {
        throw "Invalid oh_my_codex value: $Value"
      }
    }
    'subagent_routing' {
      if ($Value -notin @('auto', 'manual', 'off')) {
        throw "Invalid subagent_routing value: $Value"
      }
    }
    'completed_subagent_retention' {
      if ($Value -notin @('close', 'keep')) {
        throw "Invalid completed_subagent_retention value: $Value"
      }
    }
    'langgraph' {
      if ($Value -notin @('on', 'off')) {
        throw "Invalid langgraph value: $Value"
      }
    }
    'durable_orchestration_backend' {
      if ($Value -notin @('native_omx', 'langgraph')) {
        throw "Invalid durable_orchestration_backend value: $Value"
      }
    }
    default {
      throw "Unknown state field: $Name"
    }
  }
}

function Merge-CodexUserLevelTeamModeState {
  param(
    $LoadedState
  )

  $state = New-CodexUserLevelTeamModeDefaultState
  if ($null -eq $LoadedState) {
    return $state
  }

  foreach ($name in @('schema_version', 'managed_by', 'oh_my_codex', 'subagent_routing', 'completed_subagent_retention', 'langgraph', 'durable_orchestration_backend', 'updated_at')) {
    $property = $LoadedState.PSObject.Properties[$name]
    if ($null -ne $property -and $null -ne $property.Value) {
      $state[$name] = $property.Value
    }
  }

  if ($null -eq $LoadedState.PSObject.Properties['langgraph'] -or $null -eq $LoadedState.PSObject.Properties['langgraph'].Value) {
    $legacyBackendProperty = $LoadedState.PSObject.Properties['durable_orchestration_backend']
    if ($null -ne $legacyBackendProperty -and [string]$legacyBackendProperty.Value -eq 'langgraph') {
      $state['langgraph'] = 'on'
    } else {
      $state['langgraph'] = 'off'
    }
  }

  Assert-CodexUserLevelTeamModeValue -Name 'oh_my_codex' -Value ([string]$state['oh_my_codex'])
  Assert-CodexUserLevelTeamModeValue -Name 'subagent_routing' -Value ([string]$state['subagent_routing'])
  Assert-CodexUserLevelTeamModeValue -Name 'completed_subagent_retention' -Value ([string]$state['completed_subagent_retention'])
  Assert-CodexUserLevelTeamModeValue -Name 'langgraph' -Value ([string]$state['langgraph'])
  return (Normalize-CodexUserLevelTeamModeState -State $state)
}

function Save-CodexUserLevelTeamModeState {
  param(
    [Parameter(Mandatory)]
    $State
  )

  Assert-CodexUserLevelTeamModeValue -Name 'oh_my_codex' -Value ([string]$State['oh_my_codex'])
  Assert-CodexUserLevelTeamModeValue -Name 'subagent_routing' -Value ([string]$State['subagent_routing'])
  Assert-CodexUserLevelTeamModeValue -Name 'completed_subagent_retention' -Value ([string]$State['completed_subagent_retention'])
  Assert-CodexUserLevelTeamModeValue -Name 'langgraph' -Value ([string]$State['langgraph'])
  $State = Normalize-CodexUserLevelTeamModeState -State $State
  $statePath = Ensure-CodexUserLevelTeamModeStateDirectory
  $State['updated_at'] = (Get-Date).ToUniversalTime().ToString('o')
  $json = $State | ConvertTo-Json -Depth 5
  Set-Content -LiteralPath $statePath -Value $json -Encoding ASCII -NoNewline
  return $State
}

function Get-CodexUserLevelTeamModeState {
  $statePath = Ensure-CodexUserLevelTeamModeStateDirectory
  if (-not (Test-Path -LiteralPath $statePath)) {
    return Save-CodexUserLevelTeamModeState -State (New-CodexUserLevelTeamModeDefaultState)
  }

  $loaded = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
  return Merge-CodexUserLevelTeamModeState -LoadedState $loaded
}

function Set-CodexUserLevelTeamModeState {
  param(
    [string]$OhMyCodex,
    [string]$SubagentRouting,
    [string]$CompletedSubagentRetention,
    [string]$LangGraph,
    [string]$DurableOrchestrationBackend
  )

  $state = Get-CodexUserLevelTeamModeState
  if ($PSBoundParameters.ContainsKey('OhMyCodex')) {
    Assert-CodexUserLevelTeamModeValue -Name 'oh_my_codex' -Value $OhMyCodex
    $state['oh_my_codex'] = $OhMyCodex
  }

  if ($PSBoundParameters.ContainsKey('SubagentRouting')) {
    Assert-CodexUserLevelTeamModeValue -Name 'subagent_routing' -Value $SubagentRouting
    $state['subagent_routing'] = $SubagentRouting
  }

  if ($PSBoundParameters.ContainsKey('CompletedSubagentRetention')) {
    Assert-CodexUserLevelTeamModeValue -Name 'completed_subagent_retention' -Value $CompletedSubagentRetention
    $state['completed_subagent_retention'] = $CompletedSubagentRetention
  }

  if ($PSBoundParameters.ContainsKey('LangGraph')) {
    Assert-CodexUserLevelTeamModeValue -Name 'langgraph' -Value $LangGraph
    $state['langgraph'] = $LangGraph
  }

  if ($PSBoundParameters.ContainsKey('DurableOrchestrationBackend')) {
    Assert-CodexUserLevelTeamModeValue -Name 'durable_orchestration_backend' -Value $DurableOrchestrationBackend
    switch ($DurableOrchestrationBackend) {
      'native_omx' { $state['langgraph'] = 'off' }
      'langgraph' { $state['langgraph'] = 'on' }
    }
  }

  if ($PSBoundParameters.ContainsKey('SubagentRouting') -and [string]$SubagentRouting -eq 'off') {
    $state['oh_my_codex'] = 'off'
    $state['langgraph'] = 'off'
  }

  if ($PSBoundParameters.ContainsKey('OhMyCodex') -and [string]$OhMyCodex -eq 'off') {
    $state['langgraph'] = 'off'
  }

  if ([string]$state['subagent_routing'] -eq 'off' -and [string]$state['oh_my_codex'] -eq 'on') {
    throw 'Cannot enable oh_my_codex while subagent_routing=off.'
  }
  if ([string]$state['oh_my_codex'] -eq 'off' -and [string]$state['langgraph'] -eq 'on') {
    throw 'Cannot enable langgraph while oh_my_codex=off.'
  }
  if ([string]$state['subagent_routing'] -eq 'off' -and [string]$state['langgraph'] -eq 'on') {
    throw 'Cannot enable langgraph while subagent_routing=off.'
  }

  return Save-CodexUserLevelTeamModeState -State $state
}

function Get-CodexUserLevelTeamModeEffectiveMode {
  param(
    [Parameter(Mandatory)]
    $State
  )

  switch ("$($State['oh_my_codex'])|$($State['subagent_routing'])") {
    'on|auto' { return 'enhanced' }
    'on|manual' { return 'enhanced_manual' }
    'on|off' { return 'omx_without_routing' }
    'off|auto' { return 'native_routed' }
    'off|manual' { return 'native_manual' }
    'off|off' { return 'pure_debugging' }
    default { return 'unknown' }
  }
}

function Get-CodexUserLevelTeamModeStatus {
  $state = Get-CodexUserLevelTeamModeState
  $effectiveMode = Get-CodexUserLevelTeamModeEffectiveMode -State $state
  $langGraphRuntime = Get-CodexUserLevelLangGraphRuntimeStatus -State $state

  return [ordered]@{
    schema_version = $state['schema_version']
    managed_by = $state['managed_by']
    oh_my_codex = [string]$state['oh_my_codex']
    subagent_routing = [string]$state['subagent_routing']
    completed_subagent_retention = [string]$state['completed_subagent_retention']
    langgraph = [string]$state['langgraph']
    durable_orchestration_backend = (Get-CodexUserLevelLegacyDerivedDurableBackend -State $state)
    langgraph_install_state = [string]$langGraphRuntime.install_state
    langgraph_enabled = [bool]$langGraphRuntime.enabled
    langgraph_selected = [bool]$langGraphRuntime.selected
    langgraph_ready = [bool]$langGraphRuntime.ready
    langgraph_runtime = $langGraphRuntime
    effective_mode = $effectiveMode
    durable_team_features_available = ([string]$state['oh_my_codex'] -eq 'on')
    native_omx_available = ([string]$state['oh_my_codex'] -eq 'on')
    langgraph_available = ([string]$state['oh_my_codex'] -eq 'on' -and [string]$state['langgraph'] -eq 'on')
    role_orchestration_available = ([string]$state['subagent_routing'] -ne 'off')
    pure_debugging_mode = ($effectiveMode -eq 'pure_debugging')
    state_path = Get-CodexUserLevelTeamModeStatePath
    updated_at = [string]$state['updated_at']
  }
}

function Get-CodexUserLevelAgentsDirectory {
  $statePath = Get-CodexUserLevelTeamModeStatePath
  $stateDirectory = Split-Path -Parent $statePath
  $codexHome = Split-Path -Parent $stateDirectory
  return (Join-Path $codexHome 'agents')
}

function Get-CodexUserLevelCodexHome {
  $statePath = Get-CodexUserLevelTeamModeStatePath
  $stateDirectory = Split-Path -Parent $statePath
  return (Split-Path -Parent $stateDirectory)
}

function Get-CodexUserLevelBinDirectory {
  return (Join-Path (Get-CodexUserLevelCodexHome) 'bin')
}

function Get-CodexUserLevelPythonAssetsDirectory {
  return (Join-Path (Get-CodexUserLevelCodexHome) 'python')
}

function Get-CodexUserLevelVenvsDirectory {
  return (Join-Path (Get-CodexUserLevelCodexHome) 'venvs')
}

function Test-CodexUserLevelHelperScriptsInstalled {
  param(
    [Parameter(Mandatory)]
    [string[]]$ScriptNames
  )

  $binDirectory = Get-CodexUserLevelBinDirectory
  foreach ($scriptName in $ScriptNames) {
    $scriptPath = Join-Path $binDirectory $scriptName
    if (-not (Test-Path -LiteralPath $scriptPath)) {
      return $false
    }
  }

  return $true
}

function New-CodexUserLevelDurableCapabilityReadinessRecord {
  param(
    [Parameter(Mandatory)]
    [string]$Name,
    [Parameter(Mandatory)]
    [bool]$Installed,
    [Parameter(Mandatory)]
    [bool]$Enabled,
    [Parameter(Mandatory)]
    [bool]$Selected,
    [Parameter(Mandatory)]
    [bool]$UserLevelSelected,
    [Parameter(Mandatory)]
    [bool]$RepoStateSelected,
    [string]$InstallState = '',
    [string[]]$RequiredHelpers = @(),
    [string[]]$Blockers = @()
  )

  if ([string]::IsNullOrWhiteSpace($InstallState)) {
    $InstallState = if ($Installed) { 'installed' } else { 'not_installed' }
  }

  $ready = ($Installed -and $Enabled -and $Selected)
  $dedupedBlockers = @()
  foreach ($blocker in @($Blockers)) {
    if (-not [string]::IsNullOrWhiteSpace([string]$blocker) -and [string]$blocker -notin $dedupedBlockers) {
      $dedupedBlockers += [string]$blocker
    }
  }

  return [ordered]@{
    name = $Name
    installed = $Installed
    install_state = $InstallState
    enabled = $Enabled
    selected = $Selected
    ready = $ready
    user_level_selected = $UserLevelSelected
    repo_state_selected = $RepoStateSelected
    required_helpers = @($RequiredHelpers)
    blockers = @($dedupedBlockers)
  }
}

function Get-CodexUserLevelDurableCapabilityReadiness {
  param(
    [Parameter(Mandatory)]
    $Status,
    [AllowEmptyString()]
    [string]$RepoStateBackendFamily = '',
    [bool]$RepoStateNativeSelected = $false,
    [bool]$RepoStateLangGraphSelected = $false
  )

  $selectedBackend = [string]$Status.durable_orchestration_backend
  $nativeHelpers = @('omx-team-auto.ps1', 'omx-team-ops.ps1', 'codex-durable-state-status.ps1')
  $nativeInstalled = Test-CodexUserLevelHelperScriptsInstalled -ScriptNames $nativeHelpers
  $nativeEnabled = [bool]$Status.native_omx_available
  $nativeUserLevelSelected = ($selectedBackend -eq 'native_omx')
  $nativeSelected = ($nativeUserLevelSelected -or $RepoStateNativeSelected -or [string]$RepoStateBackendFamily -eq 'native_omx')
  $nativeBlockers = @()
  if (-not $nativeInstalled) { $nativeBlockers += 'native_omx_helpers_not_installed' }
  if (-not $nativeEnabled) { $nativeBlockers += 'oh_my_codex_disabled' }
  if (-not $nativeSelected) { $nativeBlockers += 'native_omx_not_selected' }

  $langGraphRuntime = $Status.langgraph_runtime
  $langGraphInstalled = ([string]$Status.langgraph_install_state -eq 'installed')
  $langGraphEnabled = [bool]$Status.langgraph_enabled
  $langGraphUserLevelSelected = [bool]$Status.langgraph_selected
  $langGraphSelected = ($langGraphUserLevelSelected -or $RepoStateLangGraphSelected -or [string]$RepoStateBackendFamily -eq 'langgraph')
  $langGraphBlockers = @()
  if (-not $langGraphInstalled) { $langGraphBlockers += 'langgraph_shared_runtime_not_installed' }
  if (-not $langGraphEnabled) { $langGraphBlockers += 'langgraph_disabled' }
  if (-not $langGraphSelected) { $langGraphBlockers += 'langgraph_not_selected' }

  return [ordered]@{
    selected_backend = $selectedBackend
    selected_backend_source = 'user_level_capability_state'
    repo_state_backend_family = [string]$RepoStateBackendFamily
    readiness_fields = @('installed', 'enabled', 'selected', 'ready')
    native_omx = (New-CodexUserLevelDurableCapabilityReadinessRecord `
      -Name 'native_omx' `
      -Installed $nativeInstalled `
      -Enabled $nativeEnabled `
      -Selected $nativeSelected `
      -UserLevelSelected $nativeUserLevelSelected `
      -RepoStateSelected ($RepoStateNativeSelected -or [string]$RepoStateBackendFamily -eq 'native_omx') `
      -RequiredHelpers $nativeHelpers `
      -Blockers $nativeBlockers)
    langgraph = (New-CodexUserLevelDurableCapabilityReadinessRecord `
      -Name 'langgraph' `
      -Installed $langGraphInstalled `
      -Enabled $langGraphEnabled `
      -Selected $langGraphSelected `
      -UserLevelSelected $langGraphUserLevelSelected `
      -RepoStateSelected ($RepoStateLangGraphSelected -or [string]$RepoStateBackendFamily -eq 'langgraph') `
      -InstallState ([string]$Status.langgraph_install_state) `
      -RequiredHelpers @('omx-langgraph-inspect.ps1', 'omx-langgraph-resume.ps1', 'codex-durable-state-status.ps1') `
      -Blockers $langGraphBlockers)
    langgraph_runtime = $langGraphRuntime
  }
}

function Get-CodexUserLevelLangGraphSharedVenvName {
  return 'langgraph-py312'
}

function Get-CodexUserLevelLangGraphSharedVenvPath {
  return (Join-Path (Get-CodexUserLevelVenvsDirectory) (Get-CodexUserLevelLangGraphSharedVenvName))
}

function Get-CodexUserLevelLangGraphSharedPythonPath {
  return (Join-Path (Join-Path (Get-CodexUserLevelLangGraphSharedVenvPath) 'Scripts') 'python.exe')
}

function Get-CodexUserLevelLangGraphCliExecutablePath {
  return (Join-Path (Join-Path (Get-CodexUserLevelLangGraphSharedVenvPath) 'Scripts') 'langgraph.exe')
}

function Get-CodexUserLevelLangGraphScriptPath {
  return (Join-Path (Join-Path (Get-CodexUserLevelPythonAssetsDirectory) 'langgraph_durable_orchestrator') 'cli.py')
}

function Get-CodexUserLevelLangGraphInstallPlan {
  param(
    [string]$BasePythonCommandPath,
    [switch]$IncludeLocalServerCli
  )

  $sharedVenvPath = Get-CodexUserLevelLangGraphSharedVenvPath
  $sharedPythonPath = Get-CodexUserLevelLangGraphSharedPythonPath
  $helperArtifactRoot = Join-Path (Get-CodexUserLevelPythonAssetsDirectory) 'langgraph_durable_orchestrator'
  $packages = @('langgraph')
  if ($IncludeLocalServerCli) {
    $packages += 'langgraph-cli[inmem]'
  }

  $installCommands = @(
    ('{0} -m venv {1}' -f $BasePythonCommandPath, $sharedVenvPath),
    ('{0} -m pip --isolated install --upgrade pip --index-url https://mirrors.aliyun.com/pypi/simple/' -f $sharedPythonPath),
    ('{0} -m pip --isolated install --upgrade --index-url https://mirrors.aliyun.com/pypi/simple/ {1}' -f $sharedPythonPath, 'langgraph')
  )
  if ($IncludeLocalServerCli) {
    $installCommands += ('{0} -m pip --isolated install --upgrade --index-url https://mirrors.aliyun.com/pypi/simple/ "langgraph-cli[inmem]"' -f $sharedPythonPath)
  }

  return [ordered]@{
    shared_venv_name = Get-CodexUserLevelLangGraphSharedVenvName
    shared_venv_path = $sharedVenvPath
    shared_python_path = $sharedPythonPath
    helper_artifact_root = $helperArtifactRoot
    helper_script_path = Get-CodexUserLevelLangGraphScriptPath
    base_python_command_path = $BasePythonCommandPath
    packages = $packages
    install_commands = $installCommands
    install_state = if (Test-Path -LiteralPath $sharedPythonPath) { 'installed' } else { 'not_installed' }
  }
}

function Get-CodexUserLevelLangGraphPythonCommandPath {
  param(
    [string]$FallbackPath
  )

  $sharedPythonPath = Get-CodexUserLevelLangGraphSharedPythonPath
  if (Test-Path -LiteralPath $sharedPythonPath) {
    return $sharedPythonPath
  }

  if (-not [string]::IsNullOrWhiteSpace($FallbackPath)) {
    return $FallbackPath
  }

  throw 'Unable to resolve a LangGraph Python command path.'
}

function Get-CodexUserLevelLangGraphRuntimeStatus {
  param(
    [Parameter(Mandatory)]
    $State
  )

  $installPlan = Get-CodexUserLevelLangGraphInstallPlan -BasePythonCommandPath 'python'
  $enabled = ([string]$State['oh_my_codex'] -eq 'on' -and [string]$State['langgraph'] -eq 'on')
  $selected = ([string](Get-CodexUserLevelLegacyDerivedDurableBackend -State $State) -eq 'langgraph')
  $installed = ([string]$installPlan.install_state -eq 'installed')

  return [ordered]@{
    install_state = [string]$installPlan.install_state
    enabled = $enabled
    selected = $selected
    ready = ($installed -and $enabled -and $selected)
    shared_venv_name = [string]$installPlan.shared_venv_name
    shared_venv_path = [string]$installPlan.shared_venv_path
    shared_python_path = [string]$installPlan.shared_python_path
    helper_artifact_root = [string]$installPlan.helper_artifact_root
    helper_script_path = [string]$installPlan.helper_script_path
    packages = @($installPlan.packages)
    install_commands = @($installPlan.install_commands)
  }
}

function Get-CodexUserLevelModelInstructionsFilePath {
  $statePath = Get-CodexUserLevelTeamModeStatePath
  $stateDirectory = Split-Path -Parent $statePath
  return (Join-Path $stateDirectory 'user-level-team-mode-model-instructions.md')
}

function Write-CodexUserLevelModelInstructionsFile {
  param(
    [Parameter(Mandatory)]
    [AllowEmptyString()]
    [string]$Content
  )

  $path = Get-CodexUserLevelModelInstructionsFilePath
  $directory = Split-Path -Parent $path
  if (-not (Test-Path -LiteralPath $directory)) {
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
  }
  Set-Content -LiteralPath $path -Value $Content -Encoding UTF8 -NoNewline
  return $path
}

function Get-CodexUserLevelRepositoryScopedAgentsPathHint {
  return '<repo>/.codex/agents/'
}

function Get-CodexUserLevelTeamsDirectory {
  $statePath = Get-CodexUserLevelTeamModeStatePath
  $stateDirectory = Split-Path -Parent $statePath
  $codexHome = Split-Path -Parent $stateDirectory
  return (Join-Path $codexHome 'teams')
}

function Get-CodexUserLevelComposeManifestSchemaPath {
  return (Join-Path (Get-CodexUserLevelTeamsDirectory) 'compose-manifest.schema.json')
}

function Get-CodexUserLevelNativeSubagentLimitsPath {
  $statePath = Get-CodexUserLevelTeamModeStatePath
  $stateDirectory = Split-Path -Parent $statePath
  return (Join-Path $stateDirectory 'native-subagent-limits.json')
}

function New-CodexUserLevelNativeSubagentLimitDefaults {
  return [ordered]@{
    schema_version = 1
    managed_by = 'codex-user-level-team-mode-p0'
    max_threads = 6
    max_depth = 1
    updated_at = (Get-Date).ToUniversalTime().ToString('o')
  }
}

function Assert-CodexUserLevelNativeSubagentLimitValue {
  param(
    [Parameter(Mandatory)]
    [string]$Name,
    [Parameter(Mandatory)]
    [int]$Value
  )

  switch ($Name) {
    'max_threads' {
      if ($Value -lt 1) {
        throw "Invalid max_threads value: $Value"
      }
    }
    'max_depth' {
      if ($Value -lt 1) {
        throw "Invalid max_depth value: $Value"
      }
    }
    default {
      throw "Unknown native subagent limit field: $Name"
    }
  }
}

function Merge-CodexUserLevelNativeSubagentLimits {
  param(
    $LoadedLimits
  )

  $limits = New-CodexUserLevelNativeSubagentLimitDefaults
  if ($null -eq $LoadedLimits) {
    return $limits
  }

  foreach ($name in @('schema_version', 'managed_by', 'max_threads', 'max_depth', 'updated_at')) {
    $property = $LoadedLimits.PSObject.Properties[$name]
    if ($null -ne $property -and $null -ne $property.Value) {
      $limits[$name] = $property.Value
    }
  }

  Assert-CodexUserLevelNativeSubagentLimitValue -Name 'max_threads' -Value ([int]$limits['max_threads'])
  Assert-CodexUserLevelNativeSubagentLimitValue -Name 'max_depth' -Value ([int]$limits['max_depth'])
  return $limits
}

function Save-CodexUserLevelNativeSubagentLimits {
  param(
    [Parameter(Mandatory)]
    $Limits
  )

  Assert-CodexUserLevelNativeSubagentLimitValue -Name 'max_threads' -Value ([int]$Limits['max_threads'])
  Assert-CodexUserLevelNativeSubagentLimitValue -Name 'max_depth' -Value ([int]$Limits['max_depth'])
  $path = Get-CodexUserLevelNativeSubagentLimitsPath
  $directory = Split-Path -Parent $path
  if (-not (Test-Path -LiteralPath $directory)) {
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
  }
  $Limits['updated_at'] = (Get-Date).ToUniversalTime().ToString('o')
  $json = $Limits | ConvertTo-Json -Depth 5
  Set-Content -LiteralPath $path -Value $json -Encoding ASCII -NoNewline
  return $Limits
}

function Get-CodexUserLevelNativeSubagentLimits {
  $path = Get-CodexUserLevelNativeSubagentLimitsPath
  if (-not (Test-Path -LiteralPath $path)) {
    return Save-CodexUserLevelNativeSubagentLimits -Limits (New-CodexUserLevelNativeSubagentLimitDefaults)
  }

  $loaded = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
  return Merge-CodexUserLevelNativeSubagentLimits -LoadedLimits $loaded
}

function Set-CodexUserLevelNativeSubagentLimits {
  param(
    [Nullable[int]]$MaxThreads,
    [Nullable[int]]$MaxDepth
  )

  $limits = Get-CodexUserLevelNativeSubagentLimits
  if ($PSBoundParameters.ContainsKey('MaxThreads') -and $null -ne $MaxThreads) {
    Assert-CodexUserLevelNativeSubagentLimitValue -Name 'max_threads' -Value ([int]$MaxThreads)
    $limits['max_threads'] = [int]$MaxThreads
  }
  if ($PSBoundParameters.ContainsKey('MaxDepth') -and $null -ne $MaxDepth) {
    Assert-CodexUserLevelNativeSubagentLimitValue -Name 'max_depth' -Value ([int]$MaxDepth)
    $limits['max_depth'] = [int]$MaxDepth
  }

  return Save-CodexUserLevelNativeSubagentLimits -Limits $limits
}

function Convert-CodexUserLevelTeamModeView {
  param(
    [Parameter(Mandatory)]
    $Status,
    [ValidateSet('combined', 'omx', 'routing', 'routing_policy', 'backend', 'langgraph')]
    [string]$View = 'combined'
  )

  switch ($View) {
    'omx' {
      return [ordered]@{
        oh_my_codex = $Status.oh_my_codex
        langgraph = $Status.langgraph
        langgraph_install_state = $Status.langgraph_install_state
        langgraph_ready = $Status.langgraph_ready
        effective_mode = $Status.effective_mode
        durable_team_features_available = $Status.durable_team_features_available
        native_omx_available = $Status.native_omx_available
        langgraph_available = $Status.langgraph_available
        subagent_routing = $Status.subagent_routing
        durable_orchestration_backend = $Status.durable_orchestration_backend
        updated_at = $Status.updated_at
        state_path = $Status.state_path
      }
    }
    'routing' {
      return [ordered]@{
        subagent_routing = $Status.subagent_routing
        completed_subagent_retention = $Status.completed_subagent_retention
        effective_mode = $Status.effective_mode
        role_orchestration_available = $Status.role_orchestration_available
        pure_debugging_mode = $Status.pure_debugging_mode
        oh_my_codex = $Status.oh_my_codex
        langgraph = $Status.langgraph
        durable_orchestration_backend = $Status.durable_orchestration_backend
        updated_at = $Status.updated_at
        state_path = $Status.state_path
      }
    }
    'backend' {
      $backendPolicy = Get-CodexUserLevelBackendSelectionPolicy -Status $Status
      return [ordered]@{
        durable_orchestration_backend = $Status.durable_orchestration_backend
        backend_policy_summary = [string]$backendPolicy.summary
        durable_orchestration = $backendPolicy
        effective_mode = $Status.effective_mode
        oh_my_codex = $Status.oh_my_codex
        langgraph = $Status.langgraph
        subagent_routing = $Status.subagent_routing
        state_path = $Status.state_path
        updated_at = $Status.updated_at
      }
    }
    'langgraph' {
      return [ordered]@{
        langgraph = $Status.langgraph
        langgraph_install_state = $Status.langgraph_install_state
        langgraph_enabled = $Status.langgraph_enabled
        langgraph_selected = $Status.langgraph_selected
        langgraph_ready = $Status.langgraph_ready
        langgraph_runtime = $Status.langgraph_runtime
        langgraph_available = $Status.langgraph_available
        oh_my_codex = $Status.oh_my_codex
        subagent_routing = $Status.subagent_routing
        effective_mode = $Status.effective_mode
        state_path = $Status.state_path
        updated_at = $Status.updated_at
      }
    }
    'routing_policy' {
      return (Get-CodexUserLevelRoutingPolicy -Status $Status)
    }
    default {
      return [ordered]@{
        oh_my_codex = $Status.oh_my_codex
        langgraph = $Status.langgraph
        langgraph_install_state = $Status.langgraph_install_state
        langgraph_ready = $Status.langgraph_ready
        subagent_routing = $Status.subagent_routing
        completed_subagent_retention = $Status.completed_subagent_retention
        effective_mode = $Status.effective_mode
        durable_team_features_available = $Status.durable_team_features_available
        native_omx_available = $Status.native_omx_available
        langgraph_available = $Status.langgraph_available
        role_orchestration_available = $Status.role_orchestration_available
        pure_debugging_mode = $Status.pure_debugging_mode
        durable_orchestration_backend = $Status.durable_orchestration_backend
        updated_at = $Status.updated_at
        state_path = $Status.state_path
      }
    }
  }
}

function Write-CodexUserLevelTeamModeStatus {
  param(
    [Parameter(Mandatory)]
    $Status,
    [switch]$Json,
    [ValidateSet('combined', 'omx', 'routing', 'routing_policy', 'backend', 'langgraph')]
    [string]$View = 'combined'
  )

  $output = Convert-CodexUserLevelTeamModeView -Status $Status -View $View
  if ($Json) {
    $output | ConvertTo-Json -Depth 5
    return
  }

  foreach ($key in $output.Keys) {
    $value = $output[$key]
    if ($null -eq $value) {
      $display = ''
    } elseif ($value -is [string]) {
      $display = $value
    } elseif ($value -is [System.Collections.IDictionary]) {
      $display = ($value | ConvertTo-Json -Depth 10 -Compress)
    } elseif ($value -is [System.Collections.IEnumerable]) {
      $items = @($value | ForEach-Object {
        if ($_ -is [System.Collections.IDictionary]) {
          ($_ | ConvertTo-Json -Depth 10 -Compress)
        } else {
          [string]$_
        }
      })
      $display = ($items -join '; ')
    } else {
      $display = [string]$value
    }

    Write-Output ("{0}={1}" -f $key, $display)
  }
}

function ConvertTo-CodexUserLevelTomlLiteralString {
  param(
    [Parameter(Mandatory)]
    [AllowEmptyString()]
    [string]$Value
  )

  if ([string]::IsNullOrEmpty($Value)) {
    return '""'
  }

  $escaped = $Value.Replace('\', '\\').Replace('"', '\"')
  $normalized = $escaped -replace '\r?\n', '\n'
  return ('"' + $normalized + '"')
}

function Get-CodexUserLevelRoutingThresholdDefinitions {
  return @(
    [ordered]@{
      name = 'analyst'
      lane = 'leader-native-subagent'
      first_round_preference = 'homogeneous_analyst_fanout_for_bounded_multi_face_research'
      invoke_when = @(
        'outcome, non-goals, or acceptance target is unclear'
        'two or more major ambiguities remain'
        'bounded multi-face research is still in definition, classification, scoping, or repository-grounded comparison'
        'multiple bounded research faces need a homogeneous first fan-out before design, planning, or writing escalation'
      )
    }
    [ordered]@{
      name = 'researcher'
      lane = 'leader-native-subagent'
      invoke_when = @(
        'external docs, dependency behavior, version-sensitive facts, or official-source verification are needed'
        'external uncertainty is above a low confidence threshold'
      )
    }
    [ordered]@{
      name = 'architect'
      lane = 'leader-native-subagent'
      first_round_default_for_bounded_multi_face_research = $false
      escalation_after_analyst_fan_in = 'use after analyst fan-in shows the next question is architectural'
      invoke_when = @(
        'the change crosses two or more modules, trust boundaries, or shared interfaces'
        'migrations, shared contracts, or non-local design decisions are involved'
        'for bounded multi-face research, after first analyst fan-in shows an architecture layer'
      )
    }
    [ordered]@{
      name = 'planner'
      lane = 'leader-native-subagent'
      first_round_default_for_bounded_multi_face_research = $false
      escalation_after_analyst_fan_in = 'use after analyst fan-in shows the next question is execution ordering or rollout planning'
      invoke_when = @(
        'the work can be split into two or more execution slices'
        'serial hotspots, rollout ordering, or explicit dependency chains exist'
        'for bounded multi-face research, after first analyst fan-in shows an execution-ordering layer'
      )
    }
    [ordered]@{
      name = 'executor-or-team-executor'
      lane = 'durable-team-or-native-subagent'
      invoke_when = @(
        'launch only after the plan is frozen'
        'launch only when there are at least two mostly independent execution slices'
      )
    }
    [ordered]@{
      name = 'debugger'
      lane = 'leader-native-subagent-or-durable-debug-team'
      invoke_when = @(
        'there is at least one blocking failure, regression, or reproducible runtime defect'
        'implementation has shifted into repair and stabilization'
      )
    }
    [ordered]@{
      name = 'verifier'
      lane = 'leader-native-subagent'
      invoke_when = @(
        'before final acceptance for any behavior-changing or multi-file work'
        'always after multi-worker integration'
      )
    }
    [ordered]@{
      name = 'test-engineer'
      lane = 'leader-native-subagent'
      invoke_when = @(
        'critical-path behavior changed'
        'tests are missing, flaky, or broad regression risk exists'
      )
    }
    [ordered]@{
      name = 'security-reviewer'
      lane = 'leader-native-subagent'
      invoke_when = @(
        'the scope touches auth, secrets, permissions, or untrusted input'
        'the scope touches code execution, external trust boundaries, or payments'
      )
    }
    [ordered]@{
      name = 'writer'
      lane = 'leader-native-subagent'
      first_round_default_for_bounded_multi_face_research = $false
      escalation_after_analyst_fan_in = 'use after analyst fan-in shows the next question is final documentation or operator-facing writing'
      invoke_when = @(
        'user-facing behavior changed'
        'setup, migration, or operator workflow changed'
        'for bounded multi-face research, after first analyst fan-in shows a document-finalization layer'
      )
    }
    [ordered]@{
      name = 'bug-finder / bug-rebutter / bug-judge'
      lane = 'leader-native-subagent'
      invoke_when = @(
        'bug triage is contested, noisy, or high-volume'
        'one normal verification pass still leaves disagreement or a broad candidate bug set'
      )
    }
  )
}

function Get-CodexUserLevelAnalystFanoutFirstTaskClass {
  return [ordered]@{
    name = 'bounded_multi_face_research'
    summary = 'definition, classification, scoping, or repository-grounded comparison with multiple bounded research faces'
    first_round_preference = 'homogeneous_analyst_fanout'
    first_round_roles = @('analyst')
    default_first_round_not_roles = @('architect', 'planner', 'writer')
    applies_when = @(
      'the task is still primarily bounded research rather than design, rollout ordering, or final writing'
      'the task has multiple independent research faces that can be compared after fan-in'
      'the leader needs fast recall and clean fan-in before selecting a higher abstraction role'
    )
    escalation_after_fan_in = [ordered]@{
      architect = 'after analyst fan-in shows that the next question is architecture design'
      planner = 'after analyst fan-in shows that the next question is execution ordering or rollout planning'
      writer = 'after analyst fan-in shows that the next question is final document-production or operator-facing writing'
    }
    operator_guidance = @(
      'fan out to multiple analyst calls first for bounded multi-face research'
      'do not mix architect, planner, and writer into the default first research round'
      'leader fan-in decides whether later escalation is architecture, planning, or writing'
    )
  }
}

function Get-CodexUserLevelBurstReviewRoleDefinitions {
  $agentsDirectory = Get-CodexUserLevelAgentsDirectory
  return @(
    [ordered]@{
      name = 'bug-finder'
      lane = 'leader-native-subagent'
      installed = (Test-Path -LiteralPath (Join-Path $agentsDirectory 'bug-finder.toml'))
      profile_path = (Join-Path $agentsDirectory 'bug-finder.toml')
      default_access = 'read-only'
      purpose = 'recall-first candidate bug generation'
    }
    [ordered]@{
      name = 'bug-rebutter'
      lane = 'leader-native-subagent'
      installed = (Test-Path -LiteralPath (Join-Path $agentsDirectory 'bug-rebutter.toml'))
      profile_path = (Join-Path $agentsDirectory 'bug-rebutter.toml')
      default_access = 'read-only'
      purpose = 'claim-by-claim falsification of weak bug reports'
    }
    [ordered]@{
      name = 'bug-judge'
      lane = 'leader-native-subagent'
      installed = (Test-Path -LiteralPath (Join-Path $agentsDirectory 'bug-judge.toml'))
      profile_path = (Join-Path $agentsDirectory 'bug-judge.toml')
      default_access = 'read-only'
      purpose = 'correctness-first arbitration and survivor selection'
    }
  )
}

function Get-CodexUserLevelProviderProxyUpstreamPacingPolicy {
  return [ordered]@{
    enforced = $true
    forwarded_request_budget = 10
    window = 'rolling_1_minute'
    budget_scope = 'true upstream provider forwards only'
    overflow_behavior = 'wait_for_slot_not_local_429'
    orchestration_impact = 'backpressure_not_feature_blocker'
    routing_rule = 'do not treat the pacing budget alone as a reason to avoid langgraph, native_omx, or native subagents'
    guidance = @(
      'local deterministic handling does not consume the upstream-forward budget'
      'when the budget is saturated, excess upstream-bound work should wait for a slot instead of being treated as a local feature failure'
      'prefer local-first phases and bounded upstream fan-out when many agent steps may hit the provider'
    )
  }
}

function Get-CodexUserLevelMixedPersistentComposeContract {
  return [ordered]@{
    enabled_by_default = $false
    advanced_opt_in = $true
    leader_outside_pane_roster = $true
    entrypoint = 'omx-team-compose.ps1'
    manifest_schema_path = Get-CodexUserLevelComposeManifestSchemaPath
    read_mostly_default = $true
    manifest_required_fields = @(
      'schema_version'
      'advanced_opt_in'
      'leader.outside_pane_roster'
      'panes'
    )
    supported_launch_roles = @(
      'team-executor'
      'executor'
      'debugger'
    )
    manifest_fields = @(
      'pane identities'
      'role bindings'
      'worktree allocation'
      'mailbox routing'
      'ownership boundaries'
      'checkpoint policy'
    )
  }
}

function Get-CodexUserLevelCompletedSubagentLifecyclePolicy {
  param(
    $Status
  )

  if ($null -eq $Status) {
    $Status = Get-CodexUserLevelTeamModeStatus
  }

  $retentionPolicy = [string]$Status.completed_subagent_retention
  $completionAction = if ($retentionPolicy -eq 'keep') { 'keep_until_explicit_close' } else { 'close_after_fan_in' }
  $completionGuidance = if ($retentionPolicy -eq 'keep') {
    'After `wait_agent` returns a completed result and you have absorbed it, keep the agent available until explicit close.'
  } else {
    'After `wait_agent` returns a completed result and you have absorbed it, close the agent by default.'
  }
  $preserveOverrideRule = if ($retentionPolicy -eq 'keep') {
    'A completed agent may stay available until explicit close; do not close it by reflex after fan-in.'
  } else {
    'Keep a completed agent open only when the user explicitly asks to preserve that thread.'
  }

  return [ordered]@{
    retention_policy = $retentionPolicy
    completion_action = $completionAction
    completion_guidance = $completionGuidance
    preserve_override_rule = $preserveOverrideRule
    wait_strategy = 'dynamic_window_with_periodic_checkins'
    initial_wait_seconds = 30
    typical_wait_windows = [ordered]@{
      lightweight_lookup = 30
      bounded_review = 60
      deep_review = 120
    }
    progress_check_interval_seconds = 30
    max_wait_seconds = 180
    stall_after_consecutive_quiet_checkins = 2
    stall_rule = 'inspect_redirect_or_respawn_instead_of_waiting_indefinitely'
    follow_up_rule = 'spawn a fresh agent and pass the needed context unless the preserved thread is intentionally reused'
  }
}

function Get-CodexUserLevelBackendSelectionPolicy {
  param(
    $Status
  )

  if ($null -eq $Status) {
    $Status = Get-CodexUserLevelTeamModeStatus
  }

  $enabledCapabilities = [ordered]@{
    native_subagents = ([string]$Status.subagent_routing -ne 'off')
    native_omx = [bool]$Status.native_omx_available
    langgraph = [bool]$Status.langgraph_available
  }

  $selectionMatrix = [ordered]@{
    native_omx = [ordered]@{
      default = $true
      enabled = [bool]$enabledCapabilities.native_omx
      preferred_for = @(
        'worker-centric durable execution'
        'worktree isolation and mailbox-driven worker flow'
        'direct worker lifecycle control through omx team'
      )
    }
    langgraph = [ordered]@{
      default = $false
      enabled = [bool]$enabledCapabilities.langgraph
      preferred_for = @(
        'graph-shaped multi-phase execution'
        'checkpoint-driven recovery'
        'interrupt and resume approval gates'
        'persisted implementation brief handoff'
        'persisted adversarial-review survivor queues'
      )
    }
  }

  return [ordered]@{
    summary = ('enabled_capabilities=subagents:{0},native_omx:{1},langgraph:{2}; stable_default=native_omx; effective_lane=task_flow_dependent; switching=manual_only' -f ([string]$enabledCapabilities.native_subagents).ToLowerInvariant(), ([string]$enabledCapabilities.native_omx).ToLowerInvariant(), ([string]$enabledCapabilities.langgraph).ToLowerInvariant())
    primary_operator_surface = 'codex-durable-backend-status.ps1'
    supporting_operator_surfaces = @(
      'codex-routing-policy.ps1'
      'team-leader.toml'
      'team-mode-playbook.md'
    )
    operator_authority_scope = 'user-level operator-facing backend choice'
    repository_development_authority = 'repository-local OpenSpec specs and bilingual implementation plans remain the development source of truth'
    operator_questions_answered = @(
      'which orchestration capability layers are enabled now'
      'what lane is the stable default for worker-centric durable execution'
      'when native_omx is preferred'
      'when langgraph is preferred'
      'whether effective lane choice is task-flow-dependent'
      'whether switching is explicit or automatic'
      'whether one durable task may span multiple backend families'
    )
    enabled_capabilities = $enabledCapabilities
    selected_backend = [string]$Status.durable_orchestration_backend
    default_backend = 'native_omx'
    available_backends = @('native_omx', 'langgraph')
    backend_selection_mode = 'explicit'
    backend_family_switching = 'manual_only'
    single_task_backend_family_rule = 'one durable task must use one backend family at a time'
    effective_lane_model = 'per_task_over_enabled_capabilities'
    current_effective_lane = 'task_flow_dependent'
    selection_matrix = $selectionMatrix
    provider_proxy_upstream_pacing = (Get-CodexUserLevelProviderProxyUpstreamPacingPolicy)
  }
}

function Get-CodexUserLevelHelperMirrorSourceOfTruthContract {
  return [ordered]@{
    helper_copy_kind = 'generated_user_level_install_artifact'
    install_artifact = $true
    repository_source_script = 'tools/install-codex-user-level-team-mode.ps1'
    repository_source_authority = 'repository source and repository tests define generated helper behavior'
    user_level_helper_scope = 'shared operator surface for the current Windows user and Codex home'
    durable_truth_scope = 'target repository repo-local .omx/state tree'
    consumer_project_rule = 'each consumer project keeps its own repo-local durable state and publication truth'
    non_global_state_root_rule = 'D:\PythonProject_langgraph is repository source for this orchestration line, not a global durable-state root for consumer projects'
    generated_helper_examples = @(
      'codex-durable-state-status.ps1'
      'omx-team-auto.ps1'
      'omx-langgraph-run.ps1'
    )
    consumer_project_examples = @(
      'D:\PythonProject_OpenClaw'
      'D:\PythonProject_CLIProxyAPI'
      'D:\project'
    )
  }
}

function Get-CodexUserLevelOrchestrationActivationPolicy {
  param(
    $Status
  )

  if ($null -eq $Status) {
    $Status = Get-CodexUserLevelTeamModeStatus
  }

  return [ordered]@{
    posture = 'non_conservative'
    startup_check_scope = 'new_session_first_substantive_turn'
    mandatory_rechecks = @(
      'session_reload'
      'codex_restart'
      'task_phase_change'
      'parallel_slice_threshold_crossed'
      'tracked_omx_team_record_detected'
      'tracked_langgraph_state_detected'
      'explicit_user_orchestration_request'
    )
    explicit_user_directives = [ordered]@{
      use_omx = 'hard_routing_directive'
      use_langgraph = 'hard_routing_directive'
      resume = 'activation_signal'
      continue = 'activation_signal'
      parallelize = 'activation_signal'
    }
    threshold_adoption_rule = 'when orchestration activation thresholds are met and no concrete blocker exists, actually adopt native_omx or langgraph'
    blocker_reporting_rule = 'if orchestration is not adopted, explain the concrete blocker instead of silently continuing in burst-only mode'
    existing_project_policy = [ordered]@{
      new_session = 'apply the current user-level orchestration policy automatically'
      existing_live_session = 'retrofit on reload, restart, explicit user routing directive, or tracked durable-state detection'
      decision_target = 'current task flow rather than repository age'
    }
    tracked_state_sources = @(
      '.omx/state/selectors/active.json'
      '.omx/state/selectors/leases/'
      '.omx/state/team/codex-auto-managed-team.json'
      '.omx/state/langgraph/backend.json'
    )
  }
}

function Get-CodexUserLevelRoutingPolicy {
  param(
    $Status
  )

  if ($null -eq $Status) {
    $Status = Get-CodexUserLevelTeamModeStatus
  }

  $burstReviewRoles = @(Get-CodexUserLevelBurstReviewRoleDefinitions)
  $installedBurstRoleNames = @($burstReviewRoles | Where-Object { [bool]$_.installed } | ForEach-Object { [string]$_.name })
  $nativeSubagentLimits = Get-CodexUserLevelNativeSubagentLimits
  $completedSubagentLifecycle = Get-CodexUserLevelCompletedSubagentLifecyclePolicy -Status $Status
  $agentsDirectory = Get-CodexUserLevelAgentsDirectory
  $backendSelectionPolicy = Get-CodexUserLevelBackendSelectionPolicy -Status $Status
  $orchestrationActivationPolicy = Get-CodexUserLevelOrchestrationActivationPolicy -Status $Status
  $analystFanoutFirstTaskClass = Get-CodexUserLevelAnalystFanoutFirstTaskClass

  return [ordered]@{
    oh_my_codex = $Status.oh_my_codex
    subagent_routing = $Status.subagent_routing
    langgraph = $Status.langgraph
    effective_mode = $Status.effective_mode
    automatic_routing_enabled = ([string]$Status.subagent_routing -eq 'auto')
    manual_role_selection_only = ([string]$Status.subagent_routing -eq 'manual')
    role_orchestration_available = $Status.role_orchestration_available
    durable_team_features_available = $Status.durable_team_features_available
    native_omx_available = $Status.native_omx_available
    langgraph_available = $Status.langgraph_available
    durable_orchestration_backend = $Status.durable_orchestration_backend
    pure_debugging_mode = $Status.pure_debugging_mode
    startup_path = [ordered]@{
      codex = 'wrapped user-level launcher that reads global state and forwards into native codex.cmd'
      codex_native = 'explicit bypass path that invokes native Codex directly'
      pycharm_powershell = 'when the user PowerShell profile loads, typing codex enters the wrapper rather than raw codex.cmd'
      automatic_durable_team_launch = $false
    }
    project_isolation = [ordered]@{
      shared_program_entry = 'shared user-level codex and omx installation'
      runtime_state_scope = 'per-repository or per-worktree .omx state root'
      global_switch_scope = 'user-level global state'
      same_repo_sessions_share_runtime_state = $true
      cross_repo_runtime_bleed_default = $false
    }
    orchestration_activation = $orchestrationActivationPolicy
    capability_switches = [ordered]@{
      subagent_routing = [string]$Status.subagent_routing
      completed_subagent_retention = [string]$Status.completed_subagent_retention
      oh_my_codex = [string]$Status.oh_my_codex
      langgraph = [string]$Status.langgraph
      dependency_rules = @(
        'subagent_routing=off disables higher orchestration layers'
        'oh_my_codex=off disables langgraph availability'
        'langgraph=on requires oh_my_codex=on and routing availability'
      )
    }
    general_principles = @(
      'route the smallest sufficient role set, not the largest possible set'
      'automatic role routing is available in both native and oh-my-codex-enabled states when routing is enabled'
      'oh-my-codex adds durable team features but does not create role routing from scratch'
      'turning on oh-my-codex does not auto-launch a durable team on codex startup'
      'automatic expert routing in this workflow is a leader-side overlay over explicit native Codex subagent spawning'
      'bounded multi-face research first fans out into homogeneous analyst calls before architect, planner, or writer escalation'
      'prefer read-heavy fan-out and gate write-heavy parallel execution behind explicit ownership isolation and leader-owned integration'
    )
    provider_proxy_upstream_pacing = (Get-CodexUserLevelProviderProxyUpstreamPacingPolicy)
    helper_mirror_source_of_truth = (Get-CodexUserLevelHelperMirrorSourceOfTruthContract)
    inspectable_durable_state_surface = (Get-CodexUserLevelInspectableDurableStateSurfaceContract)
    durable_state_cleanup_reconciliation = (Get-CodexUserLevelDurableStateCleanupReconciliationContract)
    advanced_compose_mode = (Get-CodexUserLevelMixedPersistentComposeContract)
    native_subagent_contract = [ordered]@{
      official_native_capability = $true
      raw_codex_auto_spawns_specialists_by_default = $false
      orchestration_model = 'leader-side explicit spawning with leader-owned fan-in'
      completed_subagent_lifecycle = $completedSubagentLifecycle
      limits = [ordered]@{
        max_threads = [int]$nativeSubagentLimits.max_threads
        max_depth = [int]$nativeSubagentLimits.max_depth
        state_path = Get-CodexUserLevelNativeSubagentLimitsPath
        helper_script = 'codex-subagent-limits.ps1'
      }
      role_locations = [ordered]@{
        user_level = $agentsDirectory
        repository_scoped = Get-CodexUserLevelRepositoryScopedAgentsPathHint
      }
      standalone_custom_agent_fields = @('name', 'description', 'developer_instructions')
      preferred_parallelism = 'read-heavy or otherwise tightly bounded work'
      write_parallelism_requirements = @(
        'explicit ownership isolation by file slice or worktree'
        'hotspot serialization rules'
        'leader-owned final integration'
      )
      omx_positioning = [ordered]@{
        description = 'workflow and durable-state layer around Codex'
        native_subagents = 'bounded in-session delegation'
        durable_team = 'long-running execution and recovery'
      }
      terminology = [ordered]@{
        preferred_dev_platform_term = 'OpenHands'
        archived_legacy_term = 'OpenDevin'
        general_orchestration_runtimes = @('LangGraph', 'AutoGen', 'CrewAI')
      }
    }
    routing_thresholds = Get-CodexUserLevelRoutingThresholdDefinitions
    analyst_fanout_first_task_class = $analystFanoutFirstTaskClass
    automatic_durable_team_routing = (Get-CodexUserLevelAutomaticTeamRoutingPolicy -Status $Status)
    durable_orchestration = [ordered]@{
      summary = [string]$backendSelectionPolicy.summary
      primary_operator_surface = [string]$backendSelectionPolicy.primary_operator_surface
      supporting_operator_surfaces = @($backendSelectionPolicy.supporting_operator_surfaces)
      operator_authority_scope = [string]$backendSelectionPolicy.operator_authority_scope
      repository_development_authority = [string]$backendSelectionPolicy.repository_development_authority
      operator_questions_answered = @($backendSelectionPolicy.operator_questions_answered)
      selected_backend = [string]$backendSelectionPolicy.selected_backend
      default_backend = [string]$backendSelectionPolicy.default_backend
      available_backends = @($backendSelectionPolicy.available_backends)
      backend_selection_mode = [string]$backendSelectionPolicy.backend_selection_mode
      backend_family_switching = [string]$backendSelectionPolicy.backend_family_switching
      single_task_backend_family_rule = [string]$backendSelectionPolicy.single_task_backend_family_rule
      selection_matrix = $backendSelectionPolicy.selection_matrix
      langgraph_runtime_layout = (Get-CodexUserLevelLangGraphRuntimeLayout)
      langgraph_backend_record = (Read-CodexUserLevelLangGraphBackendRecord)
      langgraph_contract = (Get-CodexUserLevelLangGraphContract)
    }
    effective_lane_selection = [ordered]@{
      model = 'per_task_over_enabled_capabilities'
      explicit_global_selector_required = $false
      worker_centric_default = 'native_omx'
      graph_workflow_default = 'langgraph'
      langgraph_signals = @(
        'tracked langgraph state exists'
        'task flow explicitly needs graph phases'
        'task flow explicitly needs checkpoint gates'
        'task flow explicitly needs a frozen implementation brief'
        'task flow explicitly needs a survivor queue'
      )
      native_omx_default_rule = 'when both durable capabilities are enabled and no langgraph-specific signals exist, prefer native_omx for worker-centric task flows'
    }
    burst_review_roles = $burstReviewRoles
    research_to_implementation_handoff = [ordered]@{
      research_roles = @('analyst', 'architect', 'planner', 'researcher')
      implementation_roles = @('executor', 'debugger')
      bounded_multi_face_research_first_round = [ordered]@{
        task_class = [string]$analystFanoutFirstTaskClass.name
        preferred_roles = @($analystFanoutFirstTaskClass.first_round_roles)
        delayed_roles = @($analystFanoutFirstTaskClass.default_first_round_not_roles)
      }
      rules = @(
        'keep open-ended research and final implementation in different roles'
        'for bounded multi-face research, fan out to homogeneous analyst calls before crossing into architect, planner, or writer roles'
        'freeze an implementation brief before durable execution begins'
        'start implementation in a fresh context after the brief exists'
      )
    }
    adversarial_review = [ordered]@{
      roles = @('bug-finder', 'bug-rebutter', 'bug-judge')
      installed_role_names = $installedBurstRoleNames
      rules = @(
        'use the bug-review triad only when bug triage remains contested, noisy, or high-volume'
        'keep finder, rebutter, and judge read-only by default'
        'promote only judged survivors into executor or debugger lanes'
      )
    }
  }
}

function Get-CodexUserLevelDeveloperInstructions {
  param(
    $Status
  )

  if ($null -eq $Status) {
    $Status = Get-CodexUserLevelTeamModeStatus
  }

  $lines = @()

  switch ("$($Status.oh_my_codex)|$($Status.subagent_routing)") {
    'on|auto' {
      $lines += 'You are running in Codex plus oh-my-codex enhanced mode with automatic expert routing.'
    }
    'on|manual' {
      $lines += 'You are running in Codex plus oh-my-codex enhanced mode with manual expert routing.'
    }
    'on|off' {
      $lines += 'You are running in Codex plus oh-my-codex enhanced mode with role orchestration disabled.'
    }
    'off|auto' {
      $lines += 'You are running in wrapped native Codex mode with automatic native subagent routing.'
    }
    'off|manual' {
      $lines += 'You are running in wrapped native Codex mode with manual native subagent routing.'
    }
    default {
      $lines += 'You are running in pure debugging mode.'
    }
  }

  $lines += '- Treat the current main Codex CLI session as the team leader.'
  $lines += '- Automatic collaboration is the default for all projects and all user-level Codex sessions.'
  $lines += '- The user does not need to repeat phrases such as `use experts`, `use durable_team`, `use persistent team`, `parallel`, or `subagents` for routing to evaluate collaboration.'
  $lines += '- Do not cite missing user reminders such as `the user did not request parallelism/subagents/experts` as the reason to skip orchestration.'
  $lines += '- If native `spawn_agent` invocation is blocked by the current platform/tool contract, report `experts=blocked:platform_subagent_invocation_constraint` and continue with an eligible durable lane, a narrower available expert path, or explicit main-session takeover.'
  $lines += '- On the first substantive turn of a new wrapped session, and on every session reload or Codex restart, run an orchestration activation check before deep execution resumes.'
  $lines += '- Orchestration activation check requirements:'
  $lines += '  - classify the task phase'
  $lines += '  - decide whether expert native subagents are needed now'
  $lines += '  - decide whether durable-team thresholds are already met'
  $lines += '  - emit a short operator-facing routing trace under the literal `Routing trace` label'
  $lines += '- Re-run the same activation check when the task phase changes, when work expands to two or more execution slices, when tracked `.omx` durable state is detected, or when the user explicitly requests `omx`, `LangGraph`, resume, continue, or parallel execution.'

  if ([string]$Status.subagent_routing -eq 'off') {
    $lines += '- Treat this as a plain single-agent Codex session.'
    $lines += '- Do not use role orchestration or multi-agent delegation.'
    $lines += '- If the user explicitly requests `omx` or `LangGraph`, explain that `subagent_routing=off` is the concrete blocker.'
    return ($lines -join "`n")
  }

  if ([string]$Status.subagent_routing -eq 'manual') {
    $lines += '- Specialist role use is manual in this session. Do not proactively route unless the user explicitly asks.'
  } else {
    $lines += '- Route the smallest sufficient expert role set automatically.'
  }

  $analystFanoutFirstTaskClass = Get-CodexUserLevelAnalystFanoutFirstTaskClass
  $limits = Get-CodexUserLevelNativeSubagentLimits
  $completedSubagentLifecycle = Get-CodexUserLevelCompletedSubagentLifecyclePolicy -Status $Status
  $lines += '- Native Codex subagents are an official native capability. Treat specialist role use as explicit leader-side spawning with leader-owned fan-in.'
  $lines += ('- Analyst-fanout-first task class: {0}; when a task is bounded multi-face research, first fan out into homogeneous `analyst` calls.' -f [string]$analystFanoutFirstTaskClass.name)
  $lines += '- For bounded multi-face research, do not include `architect`, `planner`, or `writer` as default first-round research roles.'
  $lines += '- After the leader absorbs analyst fan-in, escalate to `architect`, `planner`, or `writer` only when the task has clearly moved into architecture design, execution ordering, or document-finalization work.'
  $lines += ('- Completed subagent retention policy: {0}.' -f [string]$Status.completed_subagent_retention)
  $lines += ('- {0}' -f [string]$completedSubagentLifecycle.completion_guidance)
  $lines += ('- {0}' -f [string]$completedSubagentLifecycle.preserve_override_rule)
  $lines += '- Do not block indefinitely on a single `wait_agent` call.'
  $lines += '- Wait in bounded dynamic windows and perform periodic progress/liveness check-ins between waits.'
  $lines += ('- Start with about {0}s, extend to about {1}s for bounded reviews and about {2}s for deeper architect/verifier/researcher work, and keep the total wait bounded at about {3}s.' -f ([int]$completedSubagentLifecycle.initial_wait_seconds), ([int]$completedSubagentLifecycle.typical_wait_windows.bounded_review), ([int]$completedSubagentLifecycle.typical_wait_windows.deep_review), ([int]$completedSubagentLifecycle.max_wait_seconds))
  $lines += ('- Longer-running subagents should provide concise progress/liveness updates about every {0}s or at major milestones; include the current step, completed work, next step, and blockers.' -f ([int]$completedSubagentLifecycle.progress_check_interval_seconds))
  $lines += ('- If {0} consecutive progress checks stay quiet, treat the subagent as stalled and inspect, redirect, or respawn instead of waiting silently forever.' -f ([int]$completedSubagentLifecycle.stall_after_consecutive_quiet_checkins))
  $lines += ('- If follow-up work is needed later, {0}.' -f [string]$completedSubagentLifecycle.follow_up_rule)
  $lines += '- Do not imply that raw Codex auto-spawns specialist roles by default.'
  $lines += ('- Keep native subagent fan-out bounded. Current managed defaults: agents.max_threads={0}, agents.max_depth={1}.' -f ([int]$limits.max_threads), ([int]$limits.max_depth))
  $lines += '- Prefer parallel fan-out for read-heavy or otherwise tightly bounded work.'
  $lines += '- Allow write-heavy parallel execution only when ownership isolation, hotspot serialization, and leader-owned final integration are explicit.'
  $lines += '- Reusable role TOMLs live under the user-level agents directory; repository-specific role TOMLs live under `<repo>/.codex/agents/`.'
  $lines += '- Every standalone custom agent TOML should define at least `name`, `description`, and `developer_instructions`.'
  $lines += '- Treat oh-my-codex as a workflow and durable-state layer around Codex, not as a Codex replacement.'
  $lines += '- Prefer `OpenHands` over archived `OpenDevin` terminology.'
  $lines += '- Treat `LangGraph`, `AutoGen`, and `CrewAI` as general programmable orchestration runtimes, not as native Codex-subagent equivalents.'
  $lines += '- The current user-level capability switches are: `subagent_routing`, `oh_my_codex`, and `langgraph`.'
  $lines += ('- Current layered capability state: subagent_routing={0}, oh_my_codex={1}, langgraph={2}.' -f [string]$Status.subagent_routing, [string]$Status.oh_my_codex, [string]$Status.langgraph)
  $lines += '- Treat `subagent_routing=off` as disabling higher orchestration layers.'
  $lines += '- Treat `oh_my_codex=off` as disabling LangGraph availability.'
  $lines += '- Treat `langgraph=on` as requiring `oh_my_codex=on` and routing availability.'
  $lines += '- Treat explicit user requests to use `omx` or `LangGraph` as hard routing directives, not as soft preferences.'
  $lines += '- When orchestration activation thresholds are met and no concrete blocker exists, actually adopt `native_omx` or `langgraph` instead of staying in explanation-only mode.'
  $lines += '- If orchestration is not adopted, explain the concrete blocker rather than silently continuing in burst-only mode.'
  $lines += '- Existing projects with new sessions should automatically follow the current user-level orchestration policy.'
  $lines += '- Existing live sessions should retrofit orchestration behavior on reload, restart, explicit user routing directive, or tracked durable-state detection.'
  $lines += '- The orchestration decision target is the current task flow, not whether the repository is newly created.'
  $lines += ('- Derived compatibility durable backend view: {0}.' -f [string]$Status.durable_orchestration_backend)
  $lines += '- Keep `native_omx` as the stable default lane for worker-centric durable execution unless stronger graph orchestration is clearly needed.'
  $lines += '- Prefer `native_omx` for worker-centric durable execution, worktree isolation, mailbox flow, and direct worker lifecycle control.'
  $lines += '- Prefer `langgraph` for graph-shaped multi-phase execution, checkpoint-driven recovery, interrupt/resume approval gates, persisted briefs, and persisted survivor queues.'
  $lines += '- Keep backend-family switching explicit by default, but allow effective lane choice to vary per task flow across enabled capabilities.'
  $lines += '- One durable task should use one backend family at a time.'
  $lines += '- Use `codex-durable-state-status.ps1` as the canonical read-only cross-backend inspectable durable-state summary for the current repository or worktree.'
  $lines += '- The provider proxy enforces a shared upstream pacing budget: at most 10 true upstream provider forwards per rolling 1-minute window.'
  $lines += '- When that upstream-forward budget is saturated, excess upstream-bound requests wait for a slot instead of immediately returning a local 429.'
  $lines += '- Do not treat the upstream pacing budget alone as a reason to avoid LangGraph, OMX durable execution, or native subagents; treat it as backpressure and keep orchestration available.'
  $lines += '- Prefer local-first phases, deterministic local handling, and bounded upstream fan-out when many agent steps may hit the provider.'
  if ([bool]$Status.langgraph_available) {
    $lines += '- LangGraph capability is enabled in this mode; when the task explicitly needs graph phases, checkpoint gates, frozen briefs, survivor queues, or a tracked LangGraph thread, prefer the LangGraph entrypoints and repo-local `.omx/state/langgraph/` runtime state.'
    $lines += '- Persist research handoff as a frozen implementation brief and continue implementation in a fresh execution context.'
    $lines += '- Persist adversarial-review survivors as a debugger-lane queue rather than keeping the bug triad alive as persistent workers.'
  }

  if ([bool]$Status.durable_team_features_available) {
    if ([string]$Status.oh_my_codex -eq 'on' -and [string]$Status.subagent_routing -eq 'auto') {
      $lines += '- Automatic durable-team routing is available in enhanced auto mode. Prefer `omx-team-auto.ps1` over raw `omx team` when durable-team thresholds are met.'
      $lines += '- Durable-team phase map: define-target/read-context/freeze-plan/verify-accept => no durable team; execute-parallel/integrate-converge with 2+ parallel slices => 2:team-executor, scale to 3 workers at 3+ slices; stabilize with 1+ blocking issues => 2:debugger.'
      $lines += '- Automatic durable-team routing reads the shared repo-local activation selector at `.omx/state/selectors/active.json` and may still inspect compatibility records such as `.omx/state/team/codex-auto-managed-team.json` or `.omx/state/langgraph/backend.json`. Do not auto-adopt unmanaged existing teams.'
      $lines += '- Codex startup itself still does not auto-launch a durable team; durable launch remains a later threshold-gated action inside the session.'
      $lines += '- If `omx team` is not selected on first turn, explicitly explain which threshold was not met.'
      $lines += '- If `omx team` is selected on first turn, explicitly explain which threshold triggered it.'
    } else {
      $lines += '- Durable team features are available, but automatic durable-team routing is not active in this mode. Use durable-team helpers only by explicit choice.'
      $lines += '- Codex startup itself does not auto-launch a durable team.'
    }
  } else {
    $lines += '- Durable team features are unavailable in this mode; keep execution bursty unless the operator explicitly launches a team later.'
  }

  $installedBurstRoleNames = @(
    Get-CodexUserLevelBurstReviewRoleDefinitions |
      Where-Object { [bool]$_.installed } |
      ForEach-Object { [string]$_.name }
  )
  if ($installedBurstRoleNames.Count -gt 0) {
    $lines += ('- Installed burst-review roles: {0}. Keep them leader-side and read-only by default.' -f ($installedBurstRoleNames -join ', '))
  }

  $lines += '- Keep research and implementation in different roles when the task started open-ended.'
  $lines += '- Launch durable teams only after the plan is frozen and at least two mostly independent execution slices exist.'
  $lines += '- analyst: unclear outcome, non-goals, or acceptance target; two or more major ambiguities remain; or bounded multi-face research needs homogeneous first-round fan-out.'
  $lines += '- researcher: external docs, dependency behavior, version-sensitive facts, or official-source verification.'
  $lines += '- architect: two or more modules, trust boundaries, shared interfaces, migrations, or non-local design decisions; for bounded multi-face research, use only after analyst fan-in shows an architecture layer.'
  $lines += '- planner: two or more execution slices, serial hotspots, rollout ordering, or dependency chains; for bounded multi-face research, use only after analyst fan-in shows an execution-ordering layer.'
  $lines += '- debugger: blocking failure, regression, reproducible defect, or stabilization-heavy repair work.'
  $lines += '- verifier: before final acceptance for behavior-changing or multi-file work; always after multi-worker integration.'
  $lines += '- test-engineer: critical-path behavior changed, tests are missing, flaky, or broad regression risk exists.'
  $lines += '- security-reviewer: auth, secrets, permissions, untrusted input, code execution, external trust boundaries, or payments.'
  $lines += '- writer: user-facing behavior, setup, migration, or operator workflow changes; for bounded multi-face research, use only after analyst fan-in shows a document-finalization layer.'
  $lines += '- bug-finder / bug-rebutter / bug-judge: contested, noisy, or high-volume bug triage after one normal verification still leaves disagreement or a broad candidate bug set.'
  $lines += '- Startup routing trace format should stay concise, e.g. `Routing trace: phase=..., experts_now=..., durable_team=..., why=...`.'
  $lines += '- User-facing plan progress format should keep the literal `Updated Plan` label and checkbox/status-list semantics; explanatory content may be Chinese.'

  return ($lines -join "`n")
}

function Get-CodexUserLevelTeamModeStartupArgs {
  param(
    $Status,
    [AllowEmptyString()]
    [string]$DeveloperInstructions
  )

  if ($null -eq $Status) {
    $Status = Get-CodexUserLevelTeamModeStatus
  }

  if (-not $PSBoundParameters.ContainsKey('DeveloperInstructions')) {
    $DeveloperInstructions = Get-CodexUserLevelDeveloperInstructions -Status $Status
  }

  $nativeSubagentLimits = Get-CodexUserLevelNativeSubagentLimits
  $modelInstructionsFilePath = Write-CodexUserLevelModelInstructionsFile -Content $DeveloperInstructions
  $startupArgs = @()
  $startupArgs += @('-c', ('model_instructions_file=' + (ConvertTo-CodexUserLevelTomlLiteralString -Value $modelInstructionsFilePath)))
  $startupArgs += @('-c', ('agents.max_threads=' + [string]([int]$nativeSubagentLimits.max_threads)))
  $startupArgs += @('-c', ('agents.max_depth=' + [string]([int]$nativeSubagentLimits.max_depth)))

  if ([string]$Status.oh_my_codex -eq 'off') {
    $startupArgs += @('-c', 'notify=[]')
    $startupArgs += @('-c', 'mcp_servers.omx_state.enabled=false')
    $startupArgs += @('-c', 'mcp_servers.omx_memory.enabled=false')
    $startupArgs += @('-c', 'mcp_servers.omx_code_intel.enabled=false')
    $startupArgs += @('-c', 'mcp_servers.omx_trace.enabled=false')
  } else {
    $startupArgs += @('-c', 'mcp_servers.omx_state.enabled=true')
    $startupArgs += @('-c', 'mcp_servers.omx_memory.enabled=true')
    $startupArgs += @('-c', 'mcp_servers.omx_code_intel.enabled=true')
    $startupArgs += @('-c', 'mcp_servers.omx_trace.enabled=true')
  }

  if ([string]$Status.subagent_routing -eq 'off') {
    $startupArgs += @('--disable', 'multi_agent')
  }

  return $startupArgs
}

function Resolve-CodexUserLevelRepoRoot {
  param(
    [string]$OverridePath
  )

  if (-not [string]::IsNullOrWhiteSpace($OverridePath)) {
    return [System.IO.Path]::GetFullPath($OverridePath)
  }

  try {
    $gitRootLines = @(& git rev-parse --show-toplevel)
    if (Test-Path -LiteralPath variable:LASTEXITCODE -and [int]$LASTEXITCODE -eq 0) {
      $gitRoot = $gitRootLines | Select-Object -First 1
      if (-not [string]::IsNullOrWhiteSpace([string]$gitRoot)) {
        return [string]$gitRoot
      }
    }
  }
  catch {
  }

  return (Get-Location).Path
}

function Get-CodexUserLevelLangGraphStateRoot {
  param(
    [string]$RepoRoot
  )

  $resolvedRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
  return (Join-Path (Join-Path $resolvedRoot '.omx\state') 'langgraph')
}

function Get-CodexUserLevelDurableSelectorStateRoot {
  param(
    [string]$RepoRoot
  )

  $resolvedRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
  return (Join-Path (Join-Path $resolvedRoot '.omx\state') 'selectors')
}

function Get-CodexUserLevelActiveDurableSelectorRelativePath {
  return '.omx\state\selectors\active.json'
}

function Get-CodexUserLevelActiveDurableSelectorPath {
  param(
    [string]$RepoRoot
  )

  $resolvedRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
  return (Join-Path $resolvedRoot (Get-CodexUserLevelActiveDurableSelectorRelativePath))
}

function Get-CodexUserLevelSelectorLeaseDirectoryPath {
  param(
    [string]$RepoRoot
  )

  return (Join-Path (Get-CodexUserLevelDurableSelectorStateRoot -RepoRoot $RepoRoot) 'leases')
}

function Get-CodexUserLevelSelectorLeasePath {
  param(
    [string]$RepoRoot,
    [Parameter(Mandatory)]
    [string]$SessionScopeId
  )

  return (Join-Path (Get-CodexUserLevelSelectorLeaseDirectoryPath -RepoRoot $RepoRoot) ($SessionScopeId + '.json'))
}

function Get-CodexUserLevelLegacyLangGraphActiveSelectorPath {
  param(
    [string]$RepoRoot
  )

  $stateRoot = Get-CodexUserLevelLangGraphStateRoot -RepoRoot $RepoRoot
  return (Join-Path (Join-Path $stateRoot 'selectors') 'active.json')
}

function Read-CodexUserLevelActiveDurableSelector {
  param(
    [string]$RepoRoot
  )

  $path = Get-CodexUserLevelActiveDurableSelectorPath -RepoRoot $RepoRoot
  $legacyLangGraphPath = Get-CodexUserLevelLegacyLangGraphActiveSelectorPath -RepoRoot $RepoRoot

  if (-not (Test-Path -LiteralPath $path) -and (Test-Path -LiteralPath $legacyLangGraphPath)) {
    $path = $legacyLangGraphPath
  }

  if (-not (Test-Path -LiteralPath $path)) {
    return [ordered]@{
      exists = $false
      path = $path
      backend_family = ''
      repo_root = ''
      worktree_id = ''
      selector_id = ''
      session_scope_id = ''
      leader_session_lineage = ''
      team_name = ''
      thread_id = ''
      acquired_at = ''
      last_heartbeat_at = ''
      released_at = ''
      generation = 0
      routing_posture = ''
      routing_eligible = $false
    }
  }

  $record = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
  return [ordered]@{
    exists = $true
    path = $path
    backend_family = if ($null -ne $record.PSObject.Properties['backend_family']) { [string]$record.backend_family } else { '' }
    repo_root = if ($null -ne $record.PSObject.Properties['repo_root']) { [string]$record.repo_root } else { '' }
    worktree_id = if ($null -ne $record.PSObject.Properties['worktree_id']) { [string]$record.worktree_id } else { '' }
    selector_id = if ($null -ne $record.PSObject.Properties['selector_id']) { [string]$record.selector_id } else { '' }
    session_scope_id = if ($null -ne $record.PSObject.Properties['session_scope_id']) { [string]$record.session_scope_id } else { '' }
    leader_session_lineage = if ($null -ne $record.PSObject.Properties['leader_session_lineage']) { [string]$record.leader_session_lineage } else { '' }
    team_name = if ($null -ne $record.PSObject.Properties['team_name']) { [string]$record.team_name } else { '' }
    thread_id = if ($null -ne $record.PSObject.Properties['thread_id']) { [string]$record.thread_id } else { '' }
    acquired_at = if ($null -ne $record.PSObject.Properties['acquired_at']) { [string]$record.acquired_at } else { '' }
    last_heartbeat_at = if ($null -ne $record.PSObject.Properties['last_heartbeat_at']) { [string]$record.last_heartbeat_at } else { '' }
    released_at = if ($null -ne $record.PSObject.Properties['released_at']) { [string]$record.released_at } else { '' }
    generation = if ($null -ne $record.PSObject.Properties['generation'] -and $null -ne $record.generation) { [int64]$record.generation } else { 0 }
    routing_posture = if ($null -ne $record.PSObject.Properties['routing_posture']) { [string]$record.routing_posture } else { '' }
    routing_eligible = if ($null -ne $record.PSObject.Properties['routing_eligible'] -and $null -ne $record.routing_eligible) { [bool]$record.routing_eligible } else { $false }
  }
}

function ConvertTo-CodexUserLevelComparablePath {
  param(
    [AllowEmptyString()]
    [string]$Path
  )

  if ([string]::IsNullOrWhiteSpace($Path)) {
    return ''
  }

  try {
    return ([System.IO.Path]::GetFullPath($Path).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar))
  } catch {
    return ''
  }
}

function Test-CodexUserLevelActiveDurableSelectorScoped {
  param(
    $Selector,
    [AllowEmptyString()]
    [string]$RepoRoot = ''
  )

  if ($null -eq $Selector) {
    return $false
  }

  if (-not [bool]$Selector.exists) {
    return $false
  }

  if (-not [bool]$Selector.routing_eligible) {
    return $false
  }

  if (-not [string]::IsNullOrWhiteSpace([string]$Selector.released_at)) {
    return $false
  }

  if ([string]::IsNullOrWhiteSpace([string]$Selector.selector_id) -or [string]::IsNullOrWhiteSpace([string]$Selector.session_scope_id)) {
    return $false
  }

  if (-not [string]::IsNullOrWhiteSpace($RepoRoot)) {
    $resolvedRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
    $expectedRoot = ConvertTo-CodexUserLevelComparablePath -Path $resolvedRoot
    $selectorRoot = ConvertTo-CodexUserLevelComparablePath -Path ([string]$Selector.repo_root)
    if ([string]::IsNullOrWhiteSpace($selectorRoot) -or -not [string]::Equals($selectorRoot, $expectedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
      return $false
    }

    $expectedWorktreeId = Split-Path -Leaf $resolvedRoot
    if ([string]::IsNullOrWhiteSpace([string]$Selector.worktree_id) -or -not [string]::Equals([string]$Selector.worktree_id, $expectedWorktreeId, [System.StringComparison]::OrdinalIgnoreCase)) {
      return $false
    }
  }

  return $true
}

function Test-CodexUserLevelActiveDurableSelectorTargetsBackend {
  param(
    $Selector,
    [Parameter(Mandatory)]
    [string]$BackendFamily,
    [AllowEmptyString()]
    [string]$RepoRoot = ''
  )

  if (-not (Test-CodexUserLevelActiveDurableSelectorScoped -Selector $Selector -RepoRoot $RepoRoot)) {
    return $false
  }

  return ([string]$Selector.backend_family -eq $BackendFamily)
}

function Get-CodexUserLevelActiveDurableSelectorStatusProjection {
  param(
    $Selector,
    [AllowEmptyString()]
    [string]$RepoRoot = '',
    [AllowEmptyString()]
    [string]$BackendDefault = '',
    [bool]$BackendReady = $false
  )

  $resolvedRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
  $selectorStatus = 'missing'

  if ($null -ne $Selector -and [bool]$Selector.exists) {
    if (-not [string]::IsNullOrWhiteSpace([string]$Selector.released_at)) {
      $selectorStatus = 'released'
    } elseif (Test-CodexUserLevelActiveDurableSelectorScoped -Selector $Selector -RepoRoot $resolvedRoot) {
      $selectorStatus = 'active_scoped'
    } else {
      $expectedRoot = ConvertTo-CodexUserLevelComparablePath -Path $resolvedRoot
      $selectorRoot = ConvertTo-CodexUserLevelComparablePath -Path ([string]$Selector.repo_root)
      $expectedWorktreeId = Split-Path -Leaf $resolvedRoot
      $selectorBelongsToAnotherScope = (
        [string]::IsNullOrWhiteSpace($selectorRoot) -or
        -not [string]::Equals($selectorRoot, $expectedRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
        [string]::IsNullOrWhiteSpace([string]$Selector.worktree_id) -or
        -not [string]::Equals([string]$Selector.worktree_id, $expectedWorktreeId, [System.StringComparison]::OrdinalIgnoreCase)
      )

      if ($selectorBelongsToAnotherScope) {
        $selectorStatus = 'cross_repo'
      } else {
        $selectorStatus = 'unscoped_or_invalid'
      }
    }
  }

  $selectorRefreshGap = ([string]$BackendDefault -eq 'langgraph' -and $BackendReady -and $selectorStatus -eq 'missing')

  return [ordered]@{
    selector_authority = '.omx/state/selectors/active.json'
    selector_authority_path = Get-CodexUserLevelActiveDurableSelectorPath -RepoRoot $resolvedRoot
    active_selector_status = $selectorStatus
    active_selector = $Selector
    selector_refresh_gap = $selectorRefreshGap
    selector_refresh_gap_reason = if ($selectorRefreshGap) { 'active_selector_missing_for_ready_default_backend' } else { '' }
  }
}

function New-CodexUserLevelDurableSelectorId {
  return ('selector-{0}' -f ([guid]::NewGuid().ToString('N').Substring(0, 12)))
}

function New-CodexUserLevelDurableSessionScopeId {
  return ('session-{0}' -f ([guid]::NewGuid().ToString('N').Substring(0, 12)))
}

function Write-CodexUserLevelActiveDurableSelector {
  param(
    [Parameter(Mandatory)]
    [string]$RepoRoot,
    [Parameter(Mandatory)]
    [string]$BackendFamily,
    [string]$ThreadId = '',
    [string]$TeamName = '',
    [string]$Phase = '',
    [string]$RoutingPosture = '',
    [bool]$RoutingEligible = $true,
    [string]$SelectorId = '',
    [string]$SessionScopeId = '',
    [string]$LeaderSessionLineage = '',
    [string]$ReleasedAt = ''
  )

  $path = Get-CodexUserLevelActiveDurableSelectorPath -RepoRoot $RepoRoot
  $leaseScopeId = if ([string]::IsNullOrWhiteSpace($SessionScopeId)) { 'placeholder' } else { $SessionScopeId }
  $leaseDirectory = Split-Path -Parent (Get-CodexUserLevelSelectorLeasePath -RepoRoot $RepoRoot -SessionScopeId $leaseScopeId)
  if (-not (Test-Path -LiteralPath (Split-Path -Parent $path))) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $path) | Out-Null
  }
  if (-not (Test-Path -LiteralPath $leaseDirectory)) {
    New-Item -ItemType Directory -Force -Path $leaseDirectory | Out-Null
  }

  $existing = if (Test-Path -LiteralPath $path) { Get-Content -LiteralPath $path -Raw | ConvertFrom-Json } else { $null }
  if ([string]::IsNullOrWhiteSpace($SelectorId)) {
    $SelectorId = if ($null -ne $existing -and $null -ne $existing.PSObject.Properties['selector_id']) { [string]$existing.selector_id } else { New-CodexUserLevelDurableSelectorId }
  }
  if ([string]::IsNullOrWhiteSpace($SessionScopeId)) {
    $SessionScopeId = if ($null -ne $existing -and $null -ne $existing.PSObject.Properties['session_scope_id']) { [string]$existing.session_scope_id } else { New-CodexUserLevelDurableSessionScopeId }
  }
  if ([string]::IsNullOrWhiteSpace($LeaderSessionLineage)) {
    $LeaderSessionLineage = if ($null -ne $existing -and $null -ne $existing.PSObject.Properties['leader_session_lineage']) { [string]$existing.leader_session_lineage } else { $SessionScopeId }
  }

  $now = (Get-Date).ToUniversalTime().ToString('o')
  $payload = [ordered]@{
    backend_family = $BackendFamily
    selector_id = $SelectorId
    repo_root = (Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot)
    worktree_id = Split-Path -Leaf (Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot)
    thread_id = $ThreadId
    team_name = $TeamName
    session_scope_id = $SessionScopeId
    leader_session_lineage = $LeaderSessionLineage
    acquired_at = if ($null -ne $existing -and $null -ne $existing.PSObject.Properties['acquired_at'] -and -not [string]::IsNullOrWhiteSpace([string]$existing.acquired_at)) { [string]$existing.acquired_at } else { $now }
    last_heartbeat_at = $now
    released_at = $ReleasedAt
    generation = ([int64](Get-Date -UFormat %s) * 1000)
    phase = $Phase
    routing_posture = $RoutingPosture
    routing_eligible = $RoutingEligible
  }

  $json = $payload | ConvertTo-Json -Depth 6
  Set-Content -LiteralPath $path -Value $json -Encoding ASCII -NoNewline
  $leasePath = Get-CodexUserLevelSelectorLeasePath -RepoRoot $RepoRoot -SessionScopeId $SessionScopeId
  Set-Content -LiteralPath $leasePath -Value $json -Encoding ASCII -NoNewline
  return $payload
}

function Remove-CodexUserLevelActiveDurableSelector {
  param(
    [string]$RepoRoot
  )

  $existing = Read-CodexUserLevelActiveDurableSelector -RepoRoot $RepoRoot
  if ([bool]$existing.exists -and -not [string]::IsNullOrWhiteSpace([string]$existing.session_scope_id)) {
    $existing['released_at'] = (Get-Date).ToUniversalTime().ToString('o')
    $existing['routing_eligible'] = $false
    if ([string]::IsNullOrWhiteSpace([string]$existing.routing_posture)) {
      $existing['routing_posture'] = 'released_selector'
    }
    $leasePath = Get-CodexUserLevelSelectorLeasePath -RepoRoot $RepoRoot -SessionScopeId ([string]$existing.session_scope_id)
    $json = $existing | ConvertTo-Json -Depth 6
    Set-Content -LiteralPath $leasePath -Value $json -Encoding ASCII -NoNewline
  }

  $path = Get-CodexUserLevelActiveDurableSelectorPath -RepoRoot $RepoRoot
  if (Test-Path -LiteralPath $path) {
    Remove-Item -LiteralPath $path -Force
  }
}

function Get-CodexUserLevelLangGraphRuntimeLayout {
  param(
    [string]$RepoRoot
  )

  $stateRoot = Get-CodexUserLevelLangGraphStateRoot -RepoRoot $RepoRoot
  $selectorRoot = Get-CodexUserLevelDurableSelectorStateRoot -RepoRoot $RepoRoot
  return [ordered]@{
    root = $stateRoot
    threads = (Join-Path $stateRoot 'threads')
    checkpoints = (Join-Path $stateRoot 'checkpoints')
    history = (Join-Path $stateRoot 'history')
    interrupts = (Join-Path $stateRoot 'interrupts')
    store = (Join-Path $stateRoot 'store')
    selectors = $selectorRoot
    selector_leases = (Join-Path $selectorRoot 'leases')
    backend_record = (Join-Path $stateRoot 'backend.json')
    active_selector = (Join-Path $selectorRoot 'active.json')
  }
}

function Ensure-CodexUserLevelLangGraphRuntimeLayout {
  param(
    [string]$RepoRoot
  )

  $layout = Get-CodexUserLevelLangGraphRuntimeLayout -RepoRoot $RepoRoot
  foreach ($key in @('root', 'threads', 'checkpoints', 'history', 'interrupts', 'store', 'selectors', 'selector_leases')) {
    $path = [string]$layout[$key]
    if (-not (Test-Path -LiteralPath $path)) {
      New-Item -ItemType Directory -Force -Path $path | Out-Null
    }
  }
  return $layout
}

function Get-CodexUserLevelLangGraphBackendRecordPath {
  param(
    [string]$RepoRoot
  )

  $layout = Get-CodexUserLevelLangGraphRuntimeLayout -RepoRoot $RepoRoot
  return [string]$layout.backend_record
}

function Read-CodexUserLevelLangGraphBackendRecord {
  param(
    [string]$RepoRoot
  )

  $path = Get-CodexUserLevelLangGraphBackendRecordPath -RepoRoot $RepoRoot
  if (-not (Test-Path -LiteralPath $path)) {
    return [ordered]@{
      exists = $false
      path = $path
      backend = 'langgraph'
      thread_id = ''
      phase = ''
      status = ''
      updated_at = ''
      routing_posture = ''
      routing_eligible = $false
      auto_route_eligible = $false
      layout = (Get-CodexUserLevelLangGraphRuntimeLayout -RepoRoot $RepoRoot)
      history_projection = $null
      recovery_projection = $null
    }
  }

  $record = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
  return [ordered]@{
    exists = $true
    path = $path
    backend = [string]$record.backend
    thread_id = [string]$record.thread_id
    phase = if ($null -ne $record.PSObject.Properties['phase'] -and $null -ne $record.phase) { [string]$record.phase } else { '' }
    status = if ($null -ne $record.PSObject.Properties['status'] -and $null -ne $record.status) { [string]$record.status } else { '' }
    updated_at = [string]$record.updated_at
    routing_posture = if ($null -ne $record.PSObject.Properties['routing_posture'] -and -not [string]::IsNullOrWhiteSpace([string]$record.routing_posture)) { [string]$record.routing_posture } elseif (-not [string]::IsNullOrWhiteSpace([string]$record.thread_id)) { 'legacy_unscoped_selector' } else { '' }
    routing_eligible = if ($null -ne $record.PSObject.Properties['routing_eligible'] -and $null -ne $record.routing_eligible) { [bool]$record.routing_eligible } else { $false }
    auto_route_eligible = if ($null -ne $record.PSObject.Properties['auto_route_eligible'] -and $null -ne $record.auto_route_eligible) { [bool]$record.auto_route_eligible } elseif ($null -ne $record.PSObject.Properties['routing_eligible'] -and $null -ne $record.routing_eligible) { [bool]$record.routing_eligible } else { $false }
    layout = if ($null -ne $record.PSObject.Properties['layout'] -and $null -ne $record.layout) { $record.layout } else { (Get-CodexUserLevelLangGraphRuntimeLayout -RepoRoot $RepoRoot) }
    history_projection = if ($null -ne $record.PSObject.Properties['history_projection']) { $record.history_projection } else { $null }
    recovery_projection = if ($null -ne $record.PSObject.Properties['recovery_projection']) { $record.recovery_projection } else { $null }
  }
}

function Test-CodexUserLevelLangGraphBackendRecordAutoRouteEligible {
  param(
    $Record
  )

  if ($null -eq $Record) {
    return $false
  }

  if (-not [bool]$Record.exists) {
    return $false
  }

  if ([string]::IsNullOrWhiteSpace([string]$Record.thread_id)) {
    return $false
  }

  if ($null -ne $Record.PSObject.Properties['routing_eligible']) {
    return [bool]$Record.routing_eligible
  }

  return [bool]$Record.auto_route_eligible
}

function Test-CodexUserLevelLangGraphBackendRecordInspectableTracked {
  param(
    $Record
  )

  if ($null -eq $Record) {
    return $false
  }

  if (-not [bool]$Record.exists) {
    return $false
  }

  if ([string]::IsNullOrWhiteSpace([string]$Record.thread_id)) {
    return $false
  }

  $routingPosture = [string]$Record.routing_posture
  return ($routingPosture -notin @('legacy_unscoped_selector', 'historical_preserved_thread', 'missing_or_stale_selector'))
}

function ConvertTo-CodexUserLevelLangGraphThreadFileKey {
  param(
    [Parameter(Mandatory)]
    [string]$ThreadId
  )

  return $ThreadId.Replace(':', '__')
}

function Get-CodexUserLevelLangGraphThreadRecordPath {
  param(
    [string]$RepoRoot,
    [string]$ThreadId
  )

  $layout = Get-CodexUserLevelLangGraphRuntimeLayout -RepoRoot $RepoRoot
  return (Join-Path ([string]$layout.threads) ((ConvertTo-CodexUserLevelLangGraphThreadFileKey -ThreadId $ThreadId) + '.json'))
}

function Get-CodexUserLevelLangGraphCheckpointRecordPath {
  param(
    [string]$RepoRoot,
    [string]$ThreadId
  )

  $layout = Get-CodexUserLevelLangGraphRuntimeLayout -RepoRoot $RepoRoot
  return (Join-Path ([string]$layout.checkpoints) ((ConvertTo-CodexUserLevelLangGraphThreadFileKey -ThreadId $ThreadId) + '.json'))
}

function Get-CodexUserLevelLangGraphHistoryRecordPath {
  param(
    [string]$RepoRoot,
    [string]$ThreadId
  )

  $layout = Get-CodexUserLevelLangGraphRuntimeLayout -RepoRoot $RepoRoot
  return (Join-Path ([string]$layout.history) ((ConvertTo-CodexUserLevelLangGraphThreadFileKey -ThreadId $ThreadId) + '.json'))
}

function Get-CodexUserLevelLangGraphInterruptRecordPath {
  param(
    [string]$RepoRoot,
    [string]$ThreadId
  )

  $layout = Get-CodexUserLevelLangGraphRuntimeLayout -RepoRoot $RepoRoot
  return (Join-Path ([string]$layout.interrupts) ((ConvertTo-CodexUserLevelLangGraphThreadFileKey -ThreadId $ThreadId) + '.json'))
}

function Get-CodexUserLevelLangGraphImplementationBriefPath {
  param(
    [string]$RepoRoot,
    [string]$ThreadId
  )

  $layout = Get-CodexUserLevelLangGraphRuntimeLayout -RepoRoot $RepoRoot
  return (Join-Path (Join-Path ([string]$layout.store) 'briefs') ((ConvertTo-CodexUserLevelLangGraphThreadFileKey -ThreadId $ThreadId) + '.json'))
}

function Get-CodexUserLevelLangGraphSurvivorQueuePath {
  param(
    [string]$RepoRoot,
    [string]$ThreadId
  )

  $layout = Get-CodexUserLevelLangGraphRuntimeLayout -RepoRoot $RepoRoot
  return (Join-Path (Join-Path ([string]$layout.store) 'survivors') ((ConvertTo-CodexUserLevelLangGraphThreadFileKey -ThreadId $ThreadId) + '.json'))
}

function Read-CodexUserLevelLangGraphThreadRecord {
  param(
    [string]$RepoRoot,
    [string]$ThreadId
  )

  $path = Get-CodexUserLevelLangGraphThreadRecordPath -RepoRoot $RepoRoot -ThreadId $ThreadId
  if (-not (Test-Path -LiteralPath $path)) {
    return [ordered]@{
      exists = $false
      path = $path
      thread_id = $ThreadId
      phase = ''
      status = ''
      active_subgraph = ''
      active_subgraph_posture = $null
      active_loop = ''
      loop_stage = ''
      iteration_count = 0
      iteration_budget = 0
      last_gate_verdict = ''
      last_gate_reason = ''
      stop_reason = ''
      graph_contract = [ordered]@{}
      graph_kernel_state = $null
      primary_runtime_engine_state = $null
      compiled_invocation_state = $null
      live_execution_state = $null
      fuller_live_primary_engine_state = $null
      deeper_live_primary_engine_state = $null
      superstep_live_primary_engine_state = $null
      stateful_live_primary_engine_state = $null
      boundary_state_live_primary_engine_state = $null
      handoff_state_live_primary_engine_state = $null
      approval_aware_live_primary_engine_state = $null
      provenance_state_live_primary_engine_state = $null
      reducer_state = $null
      automatic_runtime_policy_state = $null
      approval_queue_state = $null
      stream_state = $null
      runtime_injection_state = $null
      memory_state = $null
      migration_state = $null
      command_state = $null
      recovery_state = $null
      updated_at = ''
    }
  }

  $record = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
  return [ordered]@{
    exists = $true
    path = $path
    thread_id = if ($null -ne $record.PSObject.Properties['thread_id']) { [string]$record.thread_id } else { $ThreadId }
    phase = if ($null -ne $record.PSObject.Properties['phase']) { [string]$record.phase } else { '' }
    status = if ($null -ne $record.PSObject.Properties['status']) { [string]$record.status } else { '' }
    active_subgraph = if ($null -ne $record.PSObject.Properties['active_subgraph']) { [string]$record.active_subgraph } else { '' }
    active_subgraph_posture = if ($null -ne $record.PSObject.Properties['active_subgraph_posture']) { $record.active_subgraph_posture } else { $null }
    active_loop = if ($null -ne $record.PSObject.Properties['active_loop']) { [string]$record.active_loop } else { '' }
    loop_stage = if ($null -ne $record.PSObject.Properties['loop_stage']) { [string]$record.loop_stage } else { '' }
    iteration_count = if ($null -ne $record.PSObject.Properties['iteration_count']) { [int]$record.iteration_count } else { 0 }
    iteration_budget = if ($null -ne $record.PSObject.Properties['iteration_budget']) { [int]$record.iteration_budget } else { 0 }
    last_gate_verdict = if ($null -ne $record.PSObject.Properties['last_gate_verdict']) { [string]$record.last_gate_verdict } else { '' }
    last_gate_reason = if ($null -ne $record.PSObject.Properties['last_gate_reason']) { [string]$record.last_gate_reason } else { '' }
    stop_reason = if ($null -ne $record.PSObject.Properties['stop_reason']) { [string]$record.stop_reason } else { '' }
    graph_contract = if ($null -ne $record.PSObject.Properties['graph_contract']) { $record.graph_contract } else { [ordered]@{} }
    graph_kernel_state = if ($null -ne $record.PSObject.Properties['graph_kernel_state']) { $record.graph_kernel_state } else { $null }
    primary_runtime_engine_state = if ($null -ne $record.PSObject.Properties['primary_runtime_engine_state']) { $record.primary_runtime_engine_state } else { $null }
    compiled_invocation_state = if ($null -ne $record.PSObject.Properties['compiled_invocation_state']) { $record.compiled_invocation_state } else { $null }
    live_execution_state = if ($null -ne $record.PSObject.Properties['live_execution_state']) { $record.live_execution_state } else { $null }
    fuller_live_primary_engine_state = if ($null -ne $record.PSObject.Properties['fuller_live_primary_engine_state']) { $record.fuller_live_primary_engine_state } else { $null }
    deeper_live_primary_engine_state = if ($null -ne $record.PSObject.Properties['deeper_live_primary_engine_state']) { $record.deeper_live_primary_engine_state } else { $null }
    superstep_live_primary_engine_state = if ($null -ne $record.PSObject.Properties['superstep_live_primary_engine_state']) { $record.superstep_live_primary_engine_state } else { $null }
    stateful_live_primary_engine_state = if ($null -ne $record.PSObject.Properties['stateful_live_primary_engine_state']) { $record.stateful_live_primary_engine_state } else { $null }
    boundary_state_live_primary_engine_state = if ($null -ne $record.PSObject.Properties['boundary_state_live_primary_engine_state']) { $record.boundary_state_live_primary_engine_state } else { $null }
    handoff_state_live_primary_engine_state = if ($null -ne $record.PSObject.Properties['handoff_state_live_primary_engine_state']) { $record.handoff_state_live_primary_engine_state } else { $null }
    approval_aware_live_primary_engine_state = if ($null -ne $record.PSObject.Properties['approval_aware_live_primary_engine_state']) { $record.approval_aware_live_primary_engine_state } else { $null }
    provenance_state_live_primary_engine_state = if ($null -ne $record.PSObject.Properties['provenance_state_live_primary_engine_state']) { $record.provenance_state_live_primary_engine_state } else { $null }
    reducer_state = if ($null -ne $record.PSObject.Properties['reducer_state']) { $record.reducer_state } else { $null }
    automatic_runtime_policy_state = if ($null -ne $record.PSObject.Properties['automatic_runtime_policy_state']) { $record.automatic_runtime_policy_state } else { $null }
    approval_queue_state = if ($null -ne $record.PSObject.Properties['approval_queue_state']) { $record.approval_queue_state } else { $null }
    stream_state = if ($null -ne $record.PSObject.Properties['stream_state']) { $record.stream_state } else { $null }
    runtime_injection_state = if ($null -ne $record.PSObject.Properties['runtime_injection_state']) { $record.runtime_injection_state } else { $null }
    memory_state = if ($null -ne $record.PSObject.Properties['memory_state']) { $record.memory_state } else { $null }
    migration_state = if ($null -ne $record.PSObject.Properties['migration_state']) { $record.migration_state } else { $null }
    command_state = if ($null -ne $record.PSObject.Properties['command_state']) { $record.command_state } else { $null }
    recovery_state = if ($null -ne $record.PSObject.Properties['recovery_state']) { $record.recovery_state } else { $null }
    updated_at = if ($null -ne $record.PSObject.Properties['updated_at']) { [string]$record.updated_at } else { '' }
  }
}

function Read-CodexUserLevelLangGraphCheckpointRecord {
  param(
    [string]$RepoRoot,
    [string]$ThreadId
  )

  $path = Get-CodexUserLevelLangGraphCheckpointRecordPath -RepoRoot $RepoRoot -ThreadId $ThreadId
  if (-not (Test-Path -LiteralPath $path)) {
    return [ordered]@{
      exists = $false
      path = $path
      checkpoint_id = ''
      checkpoint_kind = ''
      phase = ''
      loop_projection = $null
      reducer_projection = $null
      graph_kernel_projection = $null
      stream_projection = $null
      runtime_injection_projection = $null
      memory_projection = $null
      command_projection = $null
      recovery_target_id = ''
      updated_at = ''
    }
  }

  $record = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
  return [ordered]@{
    exists = $true
    path = $path
    checkpoint_id = if ($null -ne $record.PSObject.Properties['checkpoint_id']) { [string]$record.checkpoint_id } else { '' }
    checkpoint_kind = if ($null -ne $record.PSObject.Properties['checkpoint_kind']) { [string]$record.checkpoint_kind } else { '' }
    phase = if ($null -ne $record.PSObject.Properties['phase']) { [string]$record.phase } else { '' }
    loop_projection = if ($null -ne $record.PSObject.Properties['loop_projection']) { $record.loop_projection } else { $null }
    reducer_projection = if ($null -ne $record.PSObject.Properties['reducer_projection']) { $record.reducer_projection } else { $null }
    graph_kernel_projection = if ($null -ne $record.PSObject.Properties['graph_kernel_projection']) { $record.graph_kernel_projection } else { $null }
    stream_projection = if ($null -ne $record.PSObject.Properties['stream_projection']) { $record.stream_projection } else { $null }
    runtime_injection_projection = if ($null -ne $record.PSObject.Properties['runtime_injection_projection']) { $record.runtime_injection_projection } else { $null }
    memory_projection = if ($null -ne $record.PSObject.Properties['memory_projection']) { $record.memory_projection } else { $null }
    command_projection = if ($null -ne $record.PSObject.Properties['command_projection']) { $record.command_projection } else { $null }
    recovery_target_id = if ($null -ne $record.PSObject.Properties['recovery_target_id']) { [string]$record.recovery_target_id } else { '' }
    updated_at = if ($null -ne $record.PSObject.Properties['updated_at']) { [string]$record.updated_at } else { '' }
  }
}

function Read-CodexUserLevelLangGraphInterruptRecord {
  param(
    [string]$RepoRoot,
    [string]$ThreadId
  )

  $path = Get-CodexUserLevelLangGraphInterruptRecordPath -RepoRoot $RepoRoot -ThreadId $ThreadId
  if (-not (Test-Path -LiteralPath $path)) {
    return [ordered]@{
      exists = $false
      path = $path
      interrupt_id = ''
      interrupt_point = ''
      status = ''
      value_summary = ''
      reason = ''
      approval_queue_state = $null
      loop_projection = $null
      updated_at = ''
    }
  }

  $record = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
  return [ordered]@{
    exists = $true
    path = $path
    interrupt_id = if ($null -ne $record.PSObject.Properties['interrupt_id']) { [string]$record.interrupt_id } else { '' }
    interrupt_point = if ($null -ne $record.PSObject.Properties['interrupt_point']) { [string]$record.interrupt_point } else { '' }
    status = if ($null -ne $record.PSObject.Properties['status']) { [string]$record.status } else { '' }
    value_summary = if ($null -ne $record.PSObject.Properties['value_summary']) { [string]$record.value_summary } else { '' }
    reason = if ($null -ne $record.PSObject.Properties['reason']) { [string]$record.reason } else { '' }
    approval_queue_state = if ($null -ne $record.PSObject.Properties['approval_queue_state']) { $record.approval_queue_state } else { $null }
    loop_projection = if ($null -ne $record.PSObject.Properties['loop_projection']) { $record.loop_projection } else { $null }
    updated_at = if ($null -ne $record.PSObject.Properties['updated_at']) { [string]$record.updated_at } else { '' }
  }
}

function Read-CodexUserLevelLangGraphImplementationBriefState {
  param(
    [string]$RepoRoot,
    [string]$ThreadId
  )

  $path = Get-CodexUserLevelLangGraphImplementationBriefPath -RepoRoot $RepoRoot -ThreadId $ThreadId
  if (-not (Test-Path -LiteralPath $path)) {
    return [ordered]@{
      exists = $false
      path = $path
      brief_id = ''
      frozen_at = ''
      source_evidence_ref_count = 0
      inspect_pointer = [ordered]@{
        script = 'omx-langgraph-inspect.ps1'
        arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
      }
      updated_at = ''
    }
  }

  $record = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
  $sourceEvidenceRefs = @(
    if ($null -ne $record.PSObject.Properties['source_evidence_refs'] -and $null -ne $record.source_evidence_refs) {
      @($record.source_evidence_refs)
    } else {
      @()
    }
  )
  return [ordered]@{
    exists = $true
    path = $path
    brief_id = if ($null -ne $record.PSObject.Properties['brief_id']) { [string]$record.brief_id } else { '' }
    frozen_at = if ($null -ne $record.PSObject.Properties['frozen_at']) { [string]$record.frozen_at } else { '' }
    source_evidence_ref_count = @($sourceEvidenceRefs).Count
    inspect_pointer = [ordered]@{
      script = 'omx-langgraph-inspect.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    updated_at = if ($null -ne $record.PSObject.Properties['updated_at']) { [string]$record.updated_at } else { '' }
  }
}

function Read-CodexUserLevelLangGraphSurvivorQueueState {
  param(
    [string]$RepoRoot,
    [string]$ThreadId
  )

  $path = Get-CodexUserLevelLangGraphSurvivorQueuePath -RepoRoot $RepoRoot -ThreadId $ThreadId
  if (-not (Test-Path -LiteralPath $path)) {
    return [ordered]@{
      exists = $false
      path = $path
      queue_id = ''
      queue_kind = ''
      item_count = 0
      inspect_pointer = [ordered]@{
        script = 'omx-langgraph-inspect.ps1'
        arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
      }
      updated_at = ''
    }
  }

  $record = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
  $items = @(
    if ($null -ne $record.PSObject.Properties['items'] -and $null -ne $record.items) {
      @($record.items)
    } else {
      @()
    }
  )
  return [ordered]@{
    exists = $true
    path = $path
    queue_id = if ($null -ne $record.PSObject.Properties['queue_id']) { [string]$record.queue_id } else { '' }
    queue_kind = if ($null -ne $record.PSObject.Properties['queue_kind']) { [string]$record.queue_kind } else { '' }
    item_count = $items.Count
    inspect_pointer = [ordered]@{
      script = 'omx-langgraph-inspect.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    updated_at = if ($null -ne $record.PSObject.Properties['updated_at']) { [string]$record.updated_at } else { '' }
  }
}

function Get-CodexUserLevelLangGraphLoopProjection {
  param(
    [object]$ThreadRecord
  )

  $isDictionary = ($ThreadRecord -is [System.Collections.IDictionary])
  $activeLoop = if ($isDictionary -and $ThreadRecord.Contains('active_loop')) { [string]$ThreadRecord['active_loop'] } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['active_loop']) { [string]$ThreadRecord.active_loop } else { '' }
  $loopStage = if ($isDictionary -and $ThreadRecord.Contains('loop_stage')) { [string]$ThreadRecord['loop_stage'] } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['loop_stage']) { [string]$ThreadRecord.loop_stage } else { '' }
  $iterationCount = if ($isDictionary -and $ThreadRecord.Contains('iteration_count')) { [int]$ThreadRecord['iteration_count'] } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['iteration_count']) { [int]$ThreadRecord.iteration_count } else { 0 }
  $iterationBudget = if ($isDictionary -and $ThreadRecord.Contains('iteration_budget')) { [int]$ThreadRecord['iteration_budget'] } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['iteration_budget']) { [int]$ThreadRecord.iteration_budget } else { 0 }
  $lastGateVerdict = if ($isDictionary -and $ThreadRecord.Contains('last_gate_verdict')) { [string]$ThreadRecord['last_gate_verdict'] } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['last_gate_verdict']) { [string]$ThreadRecord.last_gate_verdict } else { '' }
  $lastGateReason = if ($isDictionary -and $ThreadRecord.Contains('last_gate_reason')) { [string]$ThreadRecord['last_gate_reason'] } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['last_gate_reason']) { [string]$ThreadRecord.last_gate_reason } else { '' }
  $stopReason = if ($isDictionary -and $ThreadRecord.Contains('stop_reason')) { [string]$ThreadRecord['stop_reason'] } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['stop_reason']) { [string]$ThreadRecord.stop_reason } else { '' }

  return [ordered]@{
    active_loop = $activeLoop
    loop_stage = $loopStage
    iteration_count = $iterationCount
    iteration_budget = $iterationBudget
    last_gate_verdict = $lastGateVerdict
    last_gate_reason = $lastGateReason
    stop_reason = $stopReason
  }
}

function Get-CodexUserLevelLangGraphReducerProjection {
  param(
    [object]$ThreadRecord
  )

  $reducerState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('reducer_state')) {
    $reducerState = $ThreadRecord['reducer_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['reducer_state']) {
    $reducerState = $ThreadRecord.reducer_state
  }

  if ($null -eq $reducerState) {
    return [ordered]@{
      compatibility = 'pre_reducer'
      reducer_channels_present = @()
      fanout_state = 'unknown'
      invalid_multi_writer_detected = $false
      invalid_multi_writer_updates = @()
      merge_channels_updated = @()
      channel_item_counts = [ordered]@{}
      source_records = @()
    }
  }

  $channels = if ($null -ne $reducerState.PSObject.Properties['channels'] -and $null -ne $reducerState.channels) { $reducerState.channels } else { [ordered]@{} }
  $channelItemCounts = [ordered]@{}
  $reducerChannelsPresent = @()
  $mergeChannelsUpdated = @()

  if ($channels -is [System.Collections.IDictionary]) {
    foreach ($channelName in @($channels.Keys | Sort-Object)) {
      $channelState = $channels[$channelName]
      $itemCount = if ($null -ne $channelState.PSObject.Properties['item_count']) { [int]$channelState.item_count } else { 0 }
      $channelItemCounts[$channelName] = $itemCount
      $reducerChannelsPresent += [string]$channelName
      if ($itemCount -gt 0) {
        $mergeChannelsUpdated += [string]$channelName
      }
    }
  } else {
    foreach ($property in @($channels.PSObject.Properties | Sort-Object Name)) {
      $channelState = $property.Value
      $itemCount = if ($null -ne $channelState.PSObject.Properties['item_count']) { [int]$channelState.item_count } else { 0 }
      $channelItemCounts[$property.Name] = $itemCount
      $reducerChannelsPresent += [string]$property.Name
      if ($itemCount -gt 0) {
        $mergeChannelsUpdated += [string]$property.Name
      }
    }
  }

  $invalidUpdates = if ($null -ne $reducerState.PSObject.Properties['invalid_multi_writer_updates'] -and $null -ne $reducerState.invalid_multi_writer_updates) { @($reducerState.invalid_multi_writer_updates) } else { @() }
  $sourceRecords = if ($null -ne $reducerState.PSObject.Properties['source_records'] -and $null -ne $reducerState.source_records) { @($reducerState.source_records | ForEach-Object { [string]$_ }) } else { @() }

  return [ordered]@{
    compatibility = if ($null -ne $reducerState.PSObject.Properties['compatibility']) { [string]$reducerState.compatibility } else { 'reducer_aware' }
    reducer_channels_present = $reducerChannelsPresent
    fanout_state = if ($null -ne $reducerState.PSObject.Properties['fanout_state']) { [string]$reducerState.fanout_state } else { 'idle' }
    invalid_multi_writer_detected = (@($invalidUpdates).Count -gt 0)
    invalid_multi_writer_updates = $invalidUpdates
    merge_channels_updated = $mergeChannelsUpdated
    channel_item_counts = $channelItemCounts
    source_records = @($sourceRecords | Sort-Object)
  }
}

function Get-CodexUserLevelLangGraphRecoveryProjection {
  param(
    [object]$ThreadRecord
  )

  $recoveryState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('recovery_state')) {
    $recoveryState = $ThreadRecord['recovery_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['recovery_state']) {
    $recoveryState = $ThreadRecord.recovery_state
  }

  if ($null -eq $recoveryState) {
    return [ordered]@{
      posture = 'ordinary'
      last_action = ''
      target_id = ''
      recovered_at = ''
      source_records = @()
      recoverable_fields_touched = @()
    }
  }

  $sourceRecords = if ($null -ne $recoveryState.PSObject.Properties['source_records'] -and $null -ne $recoveryState.source_records) { @($recoveryState.source_records | ForEach-Object { [string]$_ }) } else { @() }
  $recoverableFieldsTouched = if ($null -ne $recoveryState.PSObject.Properties['recoverable_fields_touched'] -and $null -ne $recoveryState.recoverable_fields_touched) { @($recoveryState.recoverable_fields_touched | ForEach-Object { [string]$_ }) } else { @() }

  return [ordered]@{
    posture = if ($null -ne $recoveryState.PSObject.Properties['posture']) { [string]$recoveryState.posture } else { 'ordinary' }
    last_action = if ($null -ne $recoveryState.PSObject.Properties['last_action']) { [string]$recoveryState.last_action } else { '' }
    target_id = if ($null -ne $recoveryState.PSObject.Properties['target_id']) { [string]$recoveryState.target_id } else { '' }
    recovered_at = if ($null -ne $recoveryState.PSObject.Properties['recovered_at']) { [string]$recoveryState.recovered_at } else { '' }
    source_records = @($sourceRecords | Sort-Object)
    recoverable_fields_touched = @($recoverableFieldsTouched | Sort-Object)
  }
}

function Get-CodexUserLevelLangGraphCommandProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $commandState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('command_state')) {
    $commandState = $ThreadRecord['command_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['command_state']) {
    $commandState = $ThreadRecord.command_state
  }

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-inspect.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $commandState) {
    return [ordered]@{
      transition_kind = ''
      update_keys = @()
      goto_target = ''
      graph_scope = ''
      source_subgraph = ''
      target_subgraph = ''
      parent_handoff_target = ''
      resume_posture = 'ordinary'
      resume_payload_present = $false
      resume_payload_keys = @()
      helper_pointer = $helperPointer
    }
  }

  $updateKeys = if ($null -ne $commandState.PSObject.Properties['update_keys'] -and $null -ne $commandState.update_keys) { @($commandState.update_keys | ForEach-Object { [string]$_ }) } else { @() }
  $resumePayloadKeys = if ($null -ne $commandState.PSObject.Properties['resume_payload_keys'] -and $null -ne $commandState.resume_payload_keys) { @($commandState.resume_payload_keys | ForEach-Object { [string]$_ }) } else { @() }

  return [ordered]@{
    transition_kind = if ($null -ne $commandState.PSObject.Properties['transition_kind']) { [string]$commandState.transition_kind } else { '' }
    update_keys = @($updateKeys | Sort-Object)
    goto_target = if ($null -ne $commandState.PSObject.Properties['goto_target']) { [string]$commandState.goto_target } else { '' }
    graph_scope = if ($null -ne $commandState.PSObject.Properties['graph_scope']) { [string]$commandState.graph_scope } else { '' }
    source_subgraph = if ($null -ne $commandState.PSObject.Properties['source_subgraph']) { [string]$commandState.source_subgraph } else { '' }
    target_subgraph = if ($null -ne $commandState.PSObject.Properties['target_subgraph']) { [string]$commandState.target_subgraph } else { '' }
    parent_handoff_target = if ($null -ne $commandState.PSObject.Properties['parent_handoff_target']) { [string]$commandState.parent_handoff_target } else { '' }
    resume_posture = if ($null -ne $commandState.PSObject.Properties['resume_posture']) { [string]$commandState.resume_posture } else { 'ordinary' }
    resume_payload_present = if ($null -ne $commandState.PSObject.Properties['resume_payload_present']) { [bool]$commandState.resume_payload_present } else { $false }
    resume_payload_keys = @($resumePayloadKeys | Sort-Object)
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphCurrentGraphContract {
  param(
    [string]$GraphContractId = '',
    [string]$TopologyVersion = '',
    [string]$StateSchemaVersion = ''
  )

  return [ordered]@{
    graph_contract_id = if (-not [string]::IsNullOrWhiteSpace($GraphContractId)) { $GraphContractId } else { 'codex_user_level_langgraph' }
    topology_version = if (-not [string]::IsNullOrWhiteSpace($TopologyVersion)) { $TopologyVersion } else { '1.0' }
    state_schema_version = if (-not [string]::IsNullOrWhiteSpace($StateSchemaVersion)) { $StateSchemaVersion } else { '1.0' }
  }
}

function Get-CodexUserLevelLangGraphThreadGraphContract {
  param(
    [object]$ThreadRecord
  )

  $graphContract = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('graph_contract')) {
    $graphContract = $ThreadRecord['graph_contract']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['graph_contract']) {
    $graphContract = $ThreadRecord.graph_contract
  } elseif ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('migration_state')) {
    $migrationState = $ThreadRecord['migration_state']
    if ($migrationState -is [System.Collections.IDictionary] -and $migrationState.Contains('thread_graph_contract')) {
      $graphContract = $migrationState['thread_graph_contract']
    } elseif ($null -ne $migrationState -and $null -ne $migrationState.PSObject.Properties['thread_graph_contract']) {
      $graphContract = $migrationState.thread_graph_contract
    }
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['migration_state']) {
    $migrationState = $ThreadRecord.migration_state
    if ($migrationState -is [System.Collections.IDictionary] -and $migrationState.Contains('thread_graph_contract')) {
      $graphContract = $migrationState['thread_graph_contract']
    } elseif ($null -ne $migrationState -and $null -ne $migrationState.PSObject.Properties['thread_graph_contract']) {
      $graphContract = $migrationState.thread_graph_contract
    }
  }

  if ($null -eq $graphContract) {
    return [ordered]@{}
  }

  $isDictionary = ($graphContract -is [System.Collections.IDictionary])
  return [ordered]@{
    graph_contract_id = if ($isDictionary -and $graphContract.Contains('graph_contract_id')) { [string]$graphContract['graph_contract_id'] } elseif ($null -ne $graphContract.PSObject.Properties['graph_contract_id']) { [string]$graphContract.graph_contract_id } else { '' }
    topology_version = if ($isDictionary -and $graphContract.Contains('topology_version')) { [string]$graphContract['topology_version'] } elseif ($null -ne $graphContract.PSObject.Properties['topology_version']) { [string]$graphContract.topology_version } else { '' }
    state_schema_version = if ($isDictionary -and $graphContract.Contains('state_schema_version')) { [string]$graphContract['state_schema_version'] } elseif ($null -ne $graphContract.PSObject.Properties['state_schema_version']) { [string]$graphContract.state_schema_version } else { '' }
  }
}

function Get-CodexUserLevelLangGraphVersionCompatibility {
  param(
    [string]$CurrentVersion,
    [string]$ThreadVersion,
    [string]$MissingReason,
    [string]$MinorReason,
    [string]$MajorReason
  )

  if ([string]::IsNullOrWhiteSpace($ThreadVersion)) {
    return [ordered]@{
      posture = 'degraded_compatible'
      reason_codes = @($MissingReason)
    }
  }

  if ($CurrentVersion -eq $ThreadVersion) {
    return [ordered]@{
      posture = 'migration_safe'
      reason_codes = @()
    }
  }

  $currentSegments = @(($CurrentVersion -split '[^0-9]+' | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | ForEach-Object { [int]$_ }))
  $threadSegments = @(($ThreadVersion -split '[^0-9]+' | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | ForEach-Object { [int]$_ }))
  if ($currentSegments.Count -gt 0 -and $threadSegments.Count -gt 0 -and $currentSegments[0] -ne $threadSegments[0]) {
    return [ordered]@{
      posture = 'incompatible'
      reason_codes = @($MajorReason)
    }
  }

  return [ordered]@{
    posture = 'degraded_compatible'
    reason_codes = @($MinorReason)
  }
}

function Get-CodexUserLevelLangGraphMigrationProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId,
    [string]$CurrentGraphContractId = '',
    [string]$CurrentTopologyVersion = '',
    [string]$CurrentStateSchemaVersion = ''
  )

  $currentContract = Get-CodexUserLevelLangGraphCurrentGraphContract -GraphContractId $CurrentGraphContractId -TopologyVersion $CurrentTopologyVersion -StateSchemaVersion $CurrentStateSchemaVersion
  $threadContract = Get-CodexUserLevelLangGraphThreadGraphContract -ThreadRecord $ThreadRecord
  $threadTopologyVersion = if ($threadContract -is [System.Collections.IDictionary] -and $threadContract.Contains('topology_version')) { [string]$threadContract['topology_version'] } else { '' }
  $threadStateSchemaVersion = if ($threadContract -is [System.Collections.IDictionary] -and $threadContract.Contains('state_schema_version')) { [string]$threadContract['state_schema_version'] } else { '' }
  $threadGraphContractId = if ($threadContract -is [System.Collections.IDictionary] -and $threadContract.Contains('graph_contract_id')) { [string]$threadContract['graph_contract_id'] } else { '' }

  $topologyCompatibility = Get-CodexUserLevelLangGraphVersionCompatibility `
    -CurrentVersion ([string]$currentContract['topology_version']) `
    -ThreadVersion $threadTopologyVersion `
    -MissingReason 'topology_version_missing' `
    -MinorReason 'topology_minor_drift' `
    -MajorReason 'topology_major_drift'
  $stateSchemaCompatibility = Get-CodexUserLevelLangGraphVersionCompatibility `
    -CurrentVersion ([string]$currentContract['state_schema_version']) `
    -ThreadVersion $threadStateSchemaVersion `
    -MissingReason 'state_schema_version_missing' `
    -MinorReason 'state_schema_minor_drift' `
    -MajorReason 'state_schema_major_drift'

  $reasonCodes = @()
  $reasonCodes += @($topologyCompatibility.reason_codes | ForEach-Object { [string]$_ })
  $reasonCodes += @($stateSchemaCompatibility.reason_codes | ForEach-Object { [string]$_ })
  if (-not [string]::IsNullOrWhiteSpace($threadGraphContractId) -and $threadGraphContractId -ne [string]$currentContract['graph_contract_id']) {
    $reasonCodes += 'graph_contract_id_mismatch'
  }

  $compatibility = 'migration_safe'
  if ([string]$topologyCompatibility.posture -eq 'incompatible' -or [string]$stateSchemaCompatibility.posture -eq 'incompatible') {
    $compatibility = 'incompatible'
  } elseif ([string]$topologyCompatibility.posture -eq 'degraded_compatible' -or [string]$stateSchemaCompatibility.posture -eq 'degraded_compatible' -or $reasonCodes -contains 'graph_contract_id_mismatch') {
    $compatibility = 'degraded_compatible'
  }

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-migration.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  return [ordered]@{
    current_graph_contract = $currentContract
    thread_graph_contract = $threadContract
    topology_compatibility = [string]$topologyCompatibility.posture
    state_schema_compatibility = [string]$stateSchemaCompatibility.posture
    compatibility = $compatibility
    reason_codes = @($reasonCodes | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | Sort-Object -Unique)
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphKernelProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $isDictionary = ($ThreadRecord -is [System.Collections.IDictionary])
  $mappedPhase = if ($isDictionary -and $ThreadRecord.Contains('phase')) { [string]$ThreadRecord['phase'] } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['phase']) { [string]$ThreadRecord.phase } else { '' }
  $threadStatus = if ($isDictionary -and $ThreadRecord.Contains('status')) { [string]$ThreadRecord['status'] } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['status']) { [string]$ThreadRecord.status } else { '' }
  $recoveryState = if ($isDictionary -and $ThreadRecord.Contains('recovery_state')) { $ThreadRecord['recovery_state'] } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['recovery_state']) { $ThreadRecord.recovery_state } else { $null }
  $approvalQueueState = if ($isDictionary -and $ThreadRecord.Contains('approval_queue_state')) { $ThreadRecord['approval_queue_state'] } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['approval_queue_state']) { $ThreadRecord.approval_queue_state } else { $null }

  $pendingApprovalCount = 0
  if ($null -ne $approvalQueueState -and $null -ne $approvalQueueState.PSObject.Properties['queue_items'] -and $null -ne $approvalQueueState.queue_items) {
    $pendingApprovalCount = @($approvalQueueState.queue_items | Where-Object { [string]$_.status -eq 'pending' }).Count
  }

  $derivedCurrentNodeId = if ($null -ne $recoveryState -and $null -ne $recoveryState.PSObject.Properties['posture'] -and [string]$recoveryState.posture -eq 'recovered_pending_resume') {
    'recovery_pending_resume'
  } elseif ($pendingApprovalCount -gt 0 -or $threadStatus -eq 'waiting_for_approval') {
    'approval_wait'
  } else {
    switch ($threadStatus) {
      'accepted' { 'accepted_terminal' }
      'halted' { 'halted_terminal' }
      'escalated' { 'escalated_terminal' }
      default {
        switch ($mappedPhase) {
          'define-target' { 'define_target' }
          'read-context' { 'read_context' }
          'freeze-plan' { 'freeze_plan' }
          'execute-parallel' { 'execute_parallel' }
          'integrate-converge' { 'integrate_converge' }
          'stabilize' { 'stabilize' }
          'verify-accept' { 'verify_accept' }
          default { '' }
        }
      }
    }
  }

  $kernelState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('graph_kernel_state')) {
    $kernelState = $ThreadRecord['graph_kernel_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['graph_kernel_state']) {
    $kernelState = $ThreadRecord.graph_kernel_state
  }

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-kernel.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $kernelState) {
    return [ordered]@{
      kernel_identity = [ordered]@{
        kernel_kind = 'stategraph'
        kernel_id = 'codex_user_level_stategraph'
        graph_api_surface = 'StateGraph'
        operator_shell_model = 'seven_phase_durable_shell'
      }
      current_node_id = $derivedCurrentNodeId
      mapped_phase = $mappedPhase
      node_posture = if ($derivedCurrentNodeId -eq 'approval_wait') { 'approval_wait' } elseif ($derivedCurrentNodeId -eq 'recovery_pending_resume') { 'recovery_pending_resume' } elseif ($derivedCurrentNodeId -like '*terminal') { 'terminal' } else { 'phase_active' }
      current_node = [ordered]@{
        node_id = $derivedCurrentNodeId
        phase = $mappedPhase
      }
      available_next_nodes = @()
      last_transition = [ordered]@{
        transition_kind = 'sequential'
        source_node = ''
        target_node = $derivedCurrentNodeId
        reason = $mappedPhase
      }
      helper_pointer = $helperPointer
    }
  }

  $storedCurrentNode = if ($null -ne $kernelState.PSObject.Properties['current_node']) { $kernelState.current_node } else { [ordered]@{} }
  if ($storedCurrentNode -is [System.Collections.IDictionary]) {
    $storedCurrentNode['node_id'] = $derivedCurrentNodeId
    if (-not [string]::IsNullOrWhiteSpace($mappedPhase)) {
      $storedCurrentNode['phase'] = $mappedPhase
    }
  } else {
    $storedCurrentNode = [ordered]@{
      node_id = $derivedCurrentNodeId
      phase = $mappedPhase
    }
  }

  return [ordered]@{
    kernel_identity = if ($null -ne $kernelState.PSObject.Properties['kernel_identity']) { $kernelState.kernel_identity } else { [ordered]@{} }
    current_node_id = $derivedCurrentNodeId
    mapped_phase = $mappedPhase
    node_posture = if ($derivedCurrentNodeId -eq 'approval_wait') { 'approval_wait' } elseif ($derivedCurrentNodeId -eq 'recovery_pending_resume') { 'recovery_pending_resume' } elseif ($derivedCurrentNodeId -like '*terminal') { 'terminal' } else { 'phase_active' }
    current_node = $storedCurrentNode
    available_next_nodes = if ($null -ne $kernelState.PSObject.Properties['available_next_nodes'] -and $null -ne $kernelState.available_next_nodes) { @($kernelState.available_next_nodes | ForEach-Object { [string]$_ }) } else { @() }
    last_transition = if ($null -ne $kernelState.PSObject.Properties['last_transition']) { $kernelState.last_transition } else { [ordered]@{} }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphPrimaryRuntimeEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('primary_runtime_engine_state')) {
    $engineState = $ThreadRecord['primary_runtime_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['primary_runtime_engine_state']) {
    $engineState = $ThreadRecord.primary_runtime_engine_state
  }

  $kernelProjection = Get-CodexUserLevelLangGraphKernelProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'compiled_stategraph_engine'
        engine_id = 'codex_user_level_primary_stategraph'
        graph_api_surface = 'StateGraph'
        operator_shell_model = 'seven_phase_durable_shell'
      }
      compile_supported = $false
      compiled_graph_present = $false
      checkpointer_expected = $true
      entry_node = 'define_target'
      finish_nodes = @('accepted_terminal', 'halted_terminal', 'escalated_terminal')
      current_execution_node = [string]$kernelProjection.current_node_id
      mapped_phase = [string]$kernelProjection.mapped_phase
      execution_posture = if ([string]$kernelProjection.node_posture -eq 'approval_wait') { 'interrupt_wait' } elseif ([string]$kernelProjection.node_posture -eq 'recovery_pending_resume') { 'recovery_wait' } elseif ([string]$kernelProjection.node_posture -eq 'terminal') { 'terminal' } else { 'compiled_unavailable' }
      last_execution_reason = if ($null -ne $kernelProjection.last_transition -and $null -ne $kernelProjection.last_transition.PSObject.Properties['reason']) { [string]$kernelProjection.last_transition.reason } else { '' }
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { $false }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { $false }
    checkpointer_expected = if ($null -ne $engineState.PSObject.Properties['checkpointer_expected']) { [bool]$engineState.checkpointer_expected } else { $true }
    entry_node = if ($null -ne $engineState.PSObject.Properties['entry_node']) { [string]$engineState.entry_node } else { 'define_target' }
    finish_nodes = if ($null -ne $engineState.PSObject.Properties['finish_nodes'] -and $null -ne $engineState.finish_nodes) { @($engineState.finish_nodes | ForEach-Object { [string]$_ }) } else { @() }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$kernelProjection.current_node_id }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$kernelProjection.mapped_phase }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { 'compiled_unavailable' }
    last_execution_reason = if ($null -ne $engineState.PSObject.Properties['last_execution_reason']) { [string]$engineState.last_execution_reason } else { '' }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphCompiledInvocationProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $invocationState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('compiled_invocation_state')) {
    $invocationState = $ThreadRecord['compiled_invocation_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['compiled_invocation_state']) {
    $invocationState = $ThreadRecord.compiled_invocation_state
  }

  $engineProjection = Get-CodexUserLevelLangGraphPrimaryRuntimeEngineProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-invocation.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $invocationState) {
    return [ordered]@{
      invocation_identity = [ordered]@{
        invocation_kind = 'compiled_stategraph_path'
        invocation_id = 'codex_user_level_compiled_stategraph'
        compiler_surface = 'StateGraph.compile'
        invoke_surface = 'CompiledGraph.invoke'
        stream_surface = 'CompiledGraph.stream'
      }
      compile_supported = [bool]$engineProjection.compile_supported
      compiled_graph_present = [bool]$engineProjection.compiled_graph_present
      invoke_supported = [bool]$engineProjection.compile_supported
      stream_supported = [bool]$engineProjection.compile_supported
      compiled_node_count = 0
      compiled_edge_count = 0
      current_execution_node = [string]$engineProjection.current_execution_node
      mapped_phase = [string]$engineProjection.mapped_phase
      invocation_posture = if ([string]$engineProjection.execution_posture -eq 'interrupt_wait') { 'interrupt_wait' } elseif ([string]$engineProjection.execution_posture -eq 'recovery_wait') { 'recovery_wait' } elseif ([string]$engineProjection.execution_posture -eq 'terminal') { 'completed' } elseif ([bool]$engineProjection.compiled_graph_present) { 'compiled_ready' } else { 'unavailable' }
      last_invoke_kind = ''
      last_invoke_reason = ''
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    invocation_identity = if ($null -ne $invocationState.PSObject.Properties['invocation_identity']) { $invocationState.invocation_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $invocationState.PSObject.Properties['compile_supported']) { [bool]$invocationState.compile_supported } else { $false }
    compiled_graph_present = if ($null -ne $invocationState.PSObject.Properties['compiled_graph_present']) { [bool]$invocationState.compiled_graph_present } else { $false }
    invoke_supported = if ($null -ne $invocationState.PSObject.Properties['invoke_supported']) { [bool]$invocationState.invoke_supported } else { $false }
    stream_supported = if ($null -ne $invocationState.PSObject.Properties['stream_supported']) { [bool]$invocationState.stream_supported } else { $false }
    compiled_node_count = if ($null -ne $invocationState.PSObject.Properties['compiled_node_count']) { [int]$invocationState.compiled_node_count } else { 0 }
    compiled_edge_count = if ($null -ne $invocationState.PSObject.Properties['compiled_edge_count']) { [int]$invocationState.compiled_edge_count } else { 0 }
    current_execution_node = if ($null -ne $invocationState.PSObject.Properties['current_execution_node']) { [string]$invocationState.current_execution_node } else { [string]$engineProjection.current_execution_node }
    mapped_phase = if ($null -ne $invocationState.PSObject.Properties['mapped_phase']) { [string]$invocationState.mapped_phase } else { [string]$engineProjection.mapped_phase }
    invocation_posture = if ($null -ne $invocationState.PSObject.Properties['invocation_posture']) { [string]$invocationState.invocation_posture } else { 'unavailable' }
    last_invoke_kind = if ($null -ne $invocationState.PSObject.Properties['last_invoke_kind']) { [string]$invocationState.last_invoke_kind } else { '' }
    last_invoke_reason = if ($null -ne $invocationState.PSObject.Properties['last_invoke_reason']) { [string]$invocationState.last_invoke_reason } else { '' }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphLiveExecutionProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $liveState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('live_execution_state')) {
    $liveState = $ThreadRecord['live_execution_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['live_execution_state']) {
    $liveState = $ThreadRecord.live_execution_state
  }

  $compiledInvocationProjection = Get-CodexUserLevelLangGraphCompiledInvocationProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-live-execution.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $liveState) {
    return [ordered]@{
      execution_identity = [ordered]@{
        execution_kind = 'live_compiled_stategraph_path'
        execution_id = 'codex_user_level_live_compiled_stategraph'
        compiler_surface = 'StateGraph.compile'
        execute_surface = 'CompiledGraph.invoke/stream'
      }
      compile_supported = [bool]$compiledInvocationProjection.compile_supported
      compiled_graph_present = [bool]$compiledInvocationProjection.compiled_graph_present
      invoke_supported = [bool]$compiledInvocationProjection.invoke_supported
      stream_supported = [bool]$compiledInvocationProjection.stream_supported
      current_execution_node = [string]$compiledInvocationProjection.current_execution_node
      mapped_phase = [string]$compiledInvocationProjection.mapped_phase
      execution_posture = 'unavailable'
      last_run_kind = ''
      last_run_status = ''
      last_run_reason = ''
      last_output_keys = @()
      last_stream_event_count = 0
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    execution_identity = if ($null -ne $liveState.PSObject.Properties['execution_identity']) { $liveState.execution_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $liveState.PSObject.Properties['compile_supported']) { [bool]$liveState.compile_supported } else { $false }
    compiled_graph_present = if ($null -ne $liveState.PSObject.Properties['compiled_graph_present']) { [bool]$liveState.compiled_graph_present } else { $false }
    invoke_supported = if ($null -ne $liveState.PSObject.Properties['invoke_supported']) { [bool]$liveState.invoke_supported } else { $false }
    stream_supported = if ($null -ne $liveState.PSObject.Properties['stream_supported']) { [bool]$liveState.stream_supported } else { $false }
    current_execution_node = if ($null -ne $liveState.PSObject.Properties['current_execution_node']) { [string]$liveState.current_execution_node } else { [string]$compiledInvocationProjection.current_execution_node }
    mapped_phase = if ($null -ne $liveState.PSObject.Properties['mapped_phase']) { [string]$liveState.mapped_phase } else { [string]$compiledInvocationProjection.mapped_phase }
    execution_posture = if ($null -ne $liveState.PSObject.Properties['execution_posture']) { [string]$liveState.execution_posture } else { 'unavailable' }
    last_run_kind = if ($null -ne $liveState.PSObject.Properties['last_run_kind']) { [string]$liveState.last_run_kind } else { '' }
    last_run_status = if ($null -ne $liveState.PSObject.Properties['last_run_status']) { [string]$liveState.last_run_status } else { '' }
    last_run_reason = if ($null -ne $liveState.PSObject.Properties['last_run_reason']) { [string]$liveState.last_run_reason } else { '' }
    last_output_keys = if ($null -ne $liveState.PSObject.Properties['last_output_keys'] -and $null -ne $liveState.last_output_keys) { @($liveState.last_output_keys | ForEach-Object { [string]$_ }) } else { @() }
    last_stream_event_count = if ($null -ne $liveState.PSObject.Properties['last_stream_event_count']) { [int]$liveState.last_stream_event_count } else { 0 }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphFullerLivePrimaryEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('fuller_live_primary_engine_state')) {
    $engineState = $ThreadRecord['fuller_live_primary_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['fuller_live_primary_engine_state']) {
    $engineState = $ThreadRecord.fuller_live_primary_engine_state
  }

  $liveExecutionProjection = Get-CodexUserLevelLangGraphLiveExecutionProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-fuller-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'fuller_live_stategraph_primary_execution_engine'
        engine_id = 'codex_user_level_live_primary_execution_engine'
        graph_api_surface = 'StateGraph'
        execute_surface = 'CompiledGraph.invoke/stream'
      }
      compile_supported = [bool]$liveExecutionProjection.compile_supported
      compiled_graph_present = [bool]$liveExecutionProjection.compiled_graph_present
      invoke_supported = [bool]$liveExecutionProjection.invoke_supported
      stream_supported = [bool]$liveExecutionProjection.stream_supported
      current_execution_node = [string]$liveExecutionProjection.current_execution_node
      mapped_phase = [string]$liveExecutionProjection.mapped_phase
      execution_node_path = @()
      resulting_phase = [string]$liveExecutionProjection.mapped_phase
      resulting_status = ''
      phase_transition_kind = ''
      execution_posture = if ([bool]$liveExecutionProjection.compile_supported) { 'ready' } else { 'unavailable' }
      last_run_kind = ''
      last_run_status = ''
      last_run_reason = ''
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { $false }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { $false }
    invoke_supported = if ($null -ne $engineState.PSObject.Properties['invoke_supported']) { [bool]$engineState.invoke_supported } else { $false }
    stream_supported = if ($null -ne $engineState.PSObject.Properties['stream_supported']) { [bool]$engineState.stream_supported } else { $false }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$liveExecutionProjection.current_execution_node }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$liveExecutionProjection.mapped_phase }
    execution_node_path = if ($null -ne $engineState.PSObject.Properties['execution_node_path'] -and $null -ne $engineState.execution_node_path) { @($engineState.execution_node_path | ForEach-Object { [string]$_ }) } else { @() }
    resulting_phase = if ($null -ne $engineState.PSObject.Properties['resulting_phase']) { [string]$engineState.resulting_phase } else { [string]$liveExecutionProjection.mapped_phase }
    resulting_status = if ($null -ne $engineState.PSObject.Properties['resulting_status']) { [string]$engineState.resulting_status } else { '' }
    phase_transition_kind = if ($null -ne $engineState.PSObject.Properties['phase_transition_kind']) { [string]$engineState.phase_transition_kind } else { '' }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { 'unavailable' }
    last_run_kind = if ($null -ne $engineState.PSObject.Properties['last_run_kind']) { [string]$engineState.last_run_kind } else { '' }
    last_run_status = if ($null -ne $engineState.PSObject.Properties['last_run_status']) { [string]$engineState.last_run_status } else { '' }
    last_run_reason = if ($null -ne $engineState.PSObject.Properties['last_run_reason']) { [string]$engineState.last_run_reason } else { '' }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphGeneralizedLiveRoutingProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $routingState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('generalized_live_routing_state')) {
    $routingState = $ThreadRecord['generalized_live_routing_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['generalized_live_routing_state']) {
    $routingState = $ThreadRecord.generalized_live_routing_state
  }

  $liveExecutionProjection = Get-CodexUserLevelLangGraphLiveExecutionProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId
  $defaultCurrentRoute = if (-not [string]::IsNullOrWhiteSpace([string]$liveExecutionProjection.mapped_phase)) {
    'phase:' + [string]$liveExecutionProjection.mapped_phase
  } else {
    ''
  }
  $defaultCandidateRoutes = @()
  if (-not [string]::IsNullOrWhiteSpace($defaultCurrentRoute)) {
    $defaultCandidateRoutes += $defaultCurrentRoute
  }

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-generalized-routing.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $routingState) {
    return [ordered]@{
      routing_identity = [ordered]@{
        routing_kind = 'generalized_live_stategraph_path'
        routing_id = 'codex_user_level_generalized_live_stategraph'
        graph_api_surface = 'StateGraph'
        route_decision_surface = 'StateGraph.add_conditional_edges'
      }
      compile_supported = [bool]$liveExecutionProjection.compile_supported
      compiled_graph_present = [bool]$liveExecutionProjection.compiled_graph_present
      route_posture = if (-not [string]::IsNullOrWhiteSpace($defaultCurrentRoute)) { 'routed' } else { 'unavailable' }
      current_route = $defaultCurrentRoute
      candidate_routes = @($defaultCandidateRoutes)
      selected_route = $defaultCurrentRoute
      loop_route_kind = if ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['active_loop']) { [string]$ThreadRecord.active_loop } else { '' }
      current_execution_node = [string]$liveExecutionProjection.current_execution_node
      mapped_phase = [string]$liveExecutionProjection.mapped_phase
      next_execution_nodes = @()
      approval_route_pending = $false
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    routing_identity = if ($null -ne $routingState.PSObject.Properties['routing_identity']) { $routingState.routing_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $routingState.PSObject.Properties['compile_supported']) { [bool]$routingState.compile_supported } else { $false }
    compiled_graph_present = if ($null -ne $routingState.PSObject.Properties['compiled_graph_present']) { [bool]$routingState.compiled_graph_present } else { $false }
    route_posture = if ($null -ne $routingState.PSObject.Properties['route_posture']) { [string]$routingState.route_posture } else { 'unavailable' }
    current_route = if ($null -ne $routingState.PSObject.Properties['current_route']) { [string]$routingState.current_route } else { $defaultCurrentRoute }
    candidate_routes = if ($null -ne $routingState.PSObject.Properties['candidate_routes'] -and $null -ne $routingState.candidate_routes) { @($routingState.candidate_routes | ForEach-Object { [string]$_ }) } else { @($defaultCandidateRoutes) }
    selected_route = if ($null -ne $routingState.PSObject.Properties['selected_route']) { [string]$routingState.selected_route } else { $defaultCurrentRoute }
    loop_route_kind = if ($null -ne $routingState.PSObject.Properties['loop_route_kind']) { [string]$routingState.loop_route_kind } else { '' }
    current_execution_node = if ($null -ne $routingState.PSObject.Properties['current_execution_node']) { [string]$routingState.current_execution_node } else { [string]$liveExecutionProjection.current_execution_node }
    mapped_phase = if ($null -ne $routingState.PSObject.Properties['mapped_phase']) { [string]$routingState.mapped_phase } else { [string]$liveExecutionProjection.mapped_phase }
    next_execution_nodes = if ($null -ne $routingState.PSObject.Properties['next_execution_nodes'] -and $null -ne $routingState.next_execution_nodes) { @($routingState.next_execution_nodes | ForEach-Object { [string]$_ }) } else { @() }
    approval_route_pending = if ($null -ne $routingState.PSObject.Properties['approval_route_pending']) { [bool]$routingState.approval_route_pending } else { $false }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphDeeperLivePrimaryEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('deeper_live_primary_engine_state')) {
    $engineState = $ThreadRecord['deeper_live_primary_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['deeper_live_primary_engine_state']) {
    $engineState = $ThreadRecord.deeper_live_primary_engine_state
  }

  $fullerEngineProjection = Get-CodexUserLevelLangGraphFullerLivePrimaryEngineProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-deeper-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'deeper_live_stategraph_primary_execution_engine'
        engine_id = 'codex_user_level_deeper_live_primary_execution_engine'
        graph_api_surface = 'StateGraph'
        execute_surface = 'CompiledGraph.invoke/stream'
        recursion_limit_surface = 'config.recursion_limit'
        remaining_steps_surface = 'RemainingSteps'
      }
      compile_supported = [bool]$fullerEngineProjection.compile_supported
      compiled_graph_present = [bool]$fullerEngineProjection.compiled_graph_present
      invoke_supported = [bool]$fullerEngineProjection.invoke_supported
      stream_supported = [bool]$fullerEngineProjection.stream_supported
      current_execution_node = [string]$fullerEngineProjection.current_execution_node
      mapped_phase = [string]$fullerEngineProjection.mapped_phase
      projected_node_path = @()
      projected_phase_path = @()
      planned_supersteps = 0
      stop_boundary = ''
      terminal_reached = $false
      recursion_limit_supported = $true
      remaining_steps_supported = $true
      recursion_limit = 8
      execution_posture = if ([bool]$fullerEngineProjection.compile_supported) { 'ready' } else { 'unavailable' }
      last_run_kind = ''
      last_run_status = ''
      last_run_reason = ''
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { $false }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { $false }
    invoke_supported = if ($null -ne $engineState.PSObject.Properties['invoke_supported']) { [bool]$engineState.invoke_supported } else { $false }
    stream_supported = if ($null -ne $engineState.PSObject.Properties['stream_supported']) { [bool]$engineState.stream_supported } else { $false }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$fullerEngineProjection.current_execution_node }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$fullerEngineProjection.mapped_phase }
    projected_node_path = if ($null -ne $engineState.PSObject.Properties['projected_node_path'] -and $null -ne $engineState.projected_node_path) { @($engineState.projected_node_path | ForEach-Object { [string]$_ }) } else { @() }
    projected_phase_path = if ($null -ne $engineState.PSObject.Properties['projected_phase_path'] -and $null -ne $engineState.projected_phase_path) { @($engineState.projected_phase_path | ForEach-Object { [string]$_ }) } else { @() }
    planned_supersteps = if ($null -ne $engineState.PSObject.Properties['planned_supersteps']) { [int]$engineState.planned_supersteps } else { 0 }
    stop_boundary = if ($null -ne $engineState.PSObject.Properties['stop_boundary']) { [string]$engineState.stop_boundary } else { '' }
    terminal_reached = if ($null -ne $engineState.PSObject.Properties['terminal_reached']) { [bool]$engineState.terminal_reached } else { $false }
    recursion_limit_supported = if ($null -ne $engineState.PSObject.Properties['recursion_limit_supported']) { [bool]$engineState.recursion_limit_supported } else { $true }
    remaining_steps_supported = if ($null -ne $engineState.PSObject.Properties['remaining_steps_supported']) { [bool]$engineState.remaining_steps_supported } else { $true }
    recursion_limit = if ($null -ne $engineState.PSObject.Properties['recursion_limit']) { [int]$engineState.recursion_limit } else { 8 }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { 'unavailable' }
    last_run_kind = if ($null -ne $engineState.PSObject.Properties['last_run_kind']) { [string]$engineState.last_run_kind } else { '' }
    last_run_status = if ($null -ne $engineState.PSObject.Properties['last_run_status']) { [string]$engineState.last_run_status } else { '' }
    last_run_reason = if ($null -ne $engineState.PSObject.Properties['last_run_reason']) { [string]$engineState.last_run_reason } else { '' }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphDeeperLivePrimaryEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('deeper_live_primary_engine_state')) {
    $engineState = $ThreadRecord['deeper_live_primary_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['deeper_live_primary_engine_state']) {
    $engineState = $ThreadRecord.deeper_live_primary_engine_state
  }

  $fullerEngineProjection = Get-CodexUserLevelLangGraphFullerLivePrimaryEngineProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-deeper-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'deeper_live_stategraph_primary_execution_engine'
        engine_id = 'codex_user_level_deeper_live_primary_execution_engine'
        graph_api_surface = 'StateGraph'
        execute_surface = 'CompiledGraph.invoke/stream'
        recursion_limit_surface = 'config.recursion_limit'
        remaining_steps_surface = 'RemainingSteps'
      }
      compile_supported = [bool]$fullerEngineProjection.compile_supported
      compiled_graph_present = [bool]$fullerEngineProjection.compiled_graph_present
      invoke_supported = [bool]$fullerEngineProjection.invoke_supported
      stream_supported = [bool]$fullerEngineProjection.stream_supported
      current_execution_node = [string]$fullerEngineProjection.current_execution_node
      mapped_phase = [string]$fullerEngineProjection.mapped_phase
      projected_node_path = @()
      projected_phase_path = @()
      planned_supersteps = 0
      stop_boundary = ''
      terminal_reached = $false
      recursion_limit_supported = $true
      remaining_steps_supported = $true
      recursion_limit = 8
      execution_posture = if ([bool]$fullerEngineProjection.compile_supported) { 'ready' } else { 'unavailable' }
      last_run_kind = ''
      last_run_status = ''
      last_run_reason = ''
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { $false }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { $false }
    invoke_supported = if ($null -ne $engineState.PSObject.Properties['invoke_supported']) { [bool]$engineState.invoke_supported } else { $false }
    stream_supported = if ($null -ne $engineState.PSObject.Properties['stream_supported']) { [bool]$engineState.stream_supported } else { $false }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$fullerEngineProjection.current_execution_node }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$fullerEngineProjection.mapped_phase }
    projected_node_path = if ($null -ne $engineState.PSObject.Properties['projected_node_path'] -and $null -ne $engineState.projected_node_path) { @($engineState.projected_node_path | ForEach-Object { [string]$_ }) } else { @() }
    projected_phase_path = if ($null -ne $engineState.PSObject.Properties['projected_phase_path'] -and $null -ne $engineState.projected_phase_path) { @($engineState.projected_phase_path | ForEach-Object { [string]$_ }) } else { @() }
    planned_supersteps = if ($null -ne $engineState.PSObject.Properties['planned_supersteps']) { [int]$engineState.planned_supersteps } else { 0 }
    stop_boundary = if ($null -ne $engineState.PSObject.Properties['stop_boundary']) { [string]$engineState.stop_boundary } else { '' }
    terminal_reached = if ($null -ne $engineState.PSObject.Properties['terminal_reached']) { [bool]$engineState.terminal_reached } else { $false }
    recursion_limit_supported = if ($null -ne $engineState.PSObject.Properties['recursion_limit_supported']) { [bool]$engineState.recursion_limit_supported } else { $true }
    remaining_steps_supported = if ($null -ne $engineState.PSObject.Properties['remaining_steps_supported']) { [bool]$engineState.remaining_steps_supported } else { $true }
    recursion_limit = if ($null -ne $engineState.PSObject.Properties['recursion_limit']) { [int]$engineState.recursion_limit } else { 8 }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { 'unavailable' }
    last_run_kind = if ($null -ne $engineState.PSObject.Properties['last_run_kind']) { [string]$engineState.last_run_kind } else { '' }
    last_run_status = if ($null -ne $engineState.PSObject.Properties['last_run_status']) { [string]$engineState.last_run_status } else { '' }
    last_run_reason = if ($null -ne $engineState.PSObject.Properties['last_run_reason']) { [string]$engineState.last_run_reason } else { '' }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphSuperstepLivePrimaryEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('superstep_live_primary_engine_state')) {
    $engineState = $ThreadRecord['superstep_live_primary_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['superstep_live_primary_engine_state']) {
    $engineState = $ThreadRecord.superstep_live_primary_engine_state
  }

  $deeperEngineProjection = Get-CodexUserLevelLangGraphDeeperLivePrimaryEngineProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-superstep-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'superstep_live_stategraph_primary_execution_engine'
        engine_id = 'codex_user_level_superstep_live_primary_execution_engine'
        graph_api_surface = 'StateGraph'
        execute_surface = 'CompiledGraph.invoke/stream'
        superstep_surface = 'Pregel supersteps'
        trace_surface = 'node_visit_path/phase_visit_path'
      }
      compile_supported = [bool]$deeperEngineProjection.compile_supported
      compiled_graph_present = [bool]$deeperEngineProjection.compiled_graph_present
      invoke_supported = [bool]$deeperEngineProjection.invoke_supported
      stream_supported = [bool]$deeperEngineProjection.stream_supported
      current_execution_node = [string]$deeperEngineProjection.current_execution_node
      mapped_phase = [string]$deeperEngineProjection.mapped_phase
      node_visit_path = @()
      phase_visit_path = @()
      superstep_count = 0
      stop_boundary = ''
      terminal_reached = $false
      recursion_limit_supported = $true
      remaining_steps_supported = $true
      recursion_limit = 8
      execution_posture = if ([bool]$deeperEngineProjection.compile_supported) { 'ready' } else { 'unavailable' }
      last_run_kind = ''
      last_run_status = ''
      last_run_reason = ''
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { $false }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { $false }
    invoke_supported = if ($null -ne $engineState.PSObject.Properties['invoke_supported']) { [bool]$engineState.invoke_supported } else { $false }
    stream_supported = if ($null -ne $engineState.PSObject.Properties['stream_supported']) { [bool]$engineState.stream_supported } else { $false }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$deeperEngineProjection.current_execution_node }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$deeperEngineProjection.mapped_phase }
    node_visit_path = if ($null -ne $engineState.PSObject.Properties['node_visit_path'] -and $null -ne $engineState.node_visit_path) { @($engineState.node_visit_path | ForEach-Object { [string]$_ }) } else { @() }
    phase_visit_path = if ($null -ne $engineState.PSObject.Properties['phase_visit_path'] -and $null -ne $engineState.phase_visit_path) { @($engineState.phase_visit_path | ForEach-Object { [string]$_ }) } else { @() }
    superstep_count = if ($null -ne $engineState.PSObject.Properties['superstep_count']) { [int]$engineState.superstep_count } else { 0 }
    stop_boundary = if ($null -ne $engineState.PSObject.Properties['stop_boundary']) { [string]$engineState.stop_boundary } else { '' }
    terminal_reached = if ($null -ne $engineState.PSObject.Properties['terminal_reached']) { [bool]$engineState.terminal_reached } else { $false }
    recursion_limit_supported = if ($null -ne $engineState.PSObject.Properties['recursion_limit_supported']) { [bool]$engineState.recursion_limit_supported } else { $true }
    remaining_steps_supported = if ($null -ne $engineState.PSObject.Properties['remaining_steps_supported']) { [bool]$engineState.remaining_steps_supported } else { $true }
    recursion_limit = if ($null -ne $engineState.PSObject.Properties['recursion_limit']) { [int]$engineState.recursion_limit } else { 8 }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { 'unavailable' }
    last_run_kind = if ($null -ne $engineState.PSObject.Properties['last_run_kind']) { [string]$engineState.last_run_kind } else { '' }
    last_run_status = if ($null -ne $engineState.PSObject.Properties['last_run_status']) { [string]$engineState.last_run_status } else { '' }
    last_run_reason = if ($null -ne $engineState.PSObject.Properties['last_run_reason']) { [string]$engineState.last_run_reason } else { '' }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphStatefulLivePrimaryEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('stateful_live_primary_engine_state')) {
    $engineState = $ThreadRecord['stateful_live_primary_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['stateful_live_primary_engine_state']) {
    $engineState = $ThreadRecord.stateful_live_primary_engine_state
  }

  $superstepEngineProjection = Get-CodexUserLevelLangGraphSuperstepLivePrimaryEngineProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-stateful-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'stateful_live_stategraph_primary_execution_engine'
        engine_id = 'codex_user_level_stateful_live_primary_execution_engine'
        graph_api_surface = 'StateGraph'
        execute_surface = 'CompiledGraph.invoke/stream'
        remaining_steps_surface = 'RemainingSteps'
        decision_surface = 'next_execution_node_from_graph_state'
      }
      compile_supported = [bool]$superstepEngineProjection.compile_supported
      compiled_graph_present = [bool]$superstepEngineProjection.compiled_graph_present
      invoke_supported = [bool]$superstepEngineProjection.invoke_supported
      stream_supported = [bool]$superstepEngineProjection.stream_supported
      current_execution_node = [string]$superstepEngineProjection.current_execution_node
      mapped_phase = [string]$superstepEngineProjection.mapped_phase
      stateful_node_path = @()
      stateful_phase_path = @()
      stateful_transition_log = @()
      superstep_count = 0
      stop_boundary = ''
      terminal_reached = $false
      recursion_limit_supported = $true
      remaining_steps_supported = $true
      recursion_limit = 8
      execution_posture = if ([bool]$superstepEngineProjection.compile_supported) { 'ready' } else { 'unavailable' }
      last_run_kind = ''
      last_run_status = ''
      last_run_reason = ''
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { $false }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { $false }
    invoke_supported = if ($null -ne $engineState.PSObject.Properties['invoke_supported']) { [bool]$engineState.invoke_supported } else { $false }
    stream_supported = if ($null -ne $engineState.PSObject.Properties['stream_supported']) { [bool]$engineState.stream_supported } else { $false }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$superstepEngineProjection.current_execution_node }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$superstepEngineProjection.mapped_phase }
    stateful_node_path = if ($null -ne $engineState.PSObject.Properties['stateful_node_path'] -and $null -ne $engineState.stateful_node_path) { @($engineState.stateful_node_path | ForEach-Object { [string]$_ }) } else { @() }
    stateful_phase_path = if ($null -ne $engineState.PSObject.Properties['stateful_phase_path'] -and $null -ne $engineState.stateful_phase_path) { @($engineState.stateful_phase_path | ForEach-Object { [string]$_ }) } else { @() }
    stateful_transition_log = if ($null -ne $engineState.PSObject.Properties['stateful_transition_log'] -and $null -ne $engineState.stateful_transition_log) { @($engineState.stateful_transition_log | ForEach-Object { [string]$_ }) } else { @() }
    superstep_count = if ($null -ne $engineState.PSObject.Properties['superstep_count']) { [int]$engineState.superstep_count } else { 0 }
    stop_boundary = if ($null -ne $engineState.PSObject.Properties['stop_boundary']) { [string]$engineState.stop_boundary } else { '' }
    terminal_reached = if ($null -ne $engineState.PSObject.Properties['terminal_reached']) { [bool]$engineState.terminal_reached } else { $false }
    recursion_limit_supported = if ($null -ne $engineState.PSObject.Properties['recursion_limit_supported']) { [bool]$engineState.recursion_limit_supported } else { $true }
    remaining_steps_supported = if ($null -ne $engineState.PSObject.Properties['remaining_steps_supported']) { [bool]$engineState.remaining_steps_supported } else { $true }
    recursion_limit = if ($null -ne $engineState.PSObject.Properties['recursion_limit']) { [int]$engineState.recursion_limit } else { 8 }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { 'unavailable' }
    last_run_kind = if ($null -ne $engineState.PSObject.Properties['last_run_kind']) { [string]$engineState.last_run_kind } else { '' }
    last_run_status = if ($null -ne $engineState.PSObject.Properties['last_run_status']) { [string]$engineState.last_run_status } else { '' }
    last_run_reason = if ($null -ne $engineState.PSObject.Properties['last_run_reason']) { [string]$engineState.last_run_reason } else { '' }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphBoundaryStateLivePrimaryEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('boundary_state_live_primary_engine_state')) {
    $engineState = $ThreadRecord['boundary_state_live_primary_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['boundary_state_live_primary_engine_state']) {
    $engineState = $ThreadRecord.boundary_state_live_primary_engine_state
  }

  $statefulEngineProjection = Get-CodexUserLevelLangGraphStatefulLivePrimaryEngineProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-boundary-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'graph_resident_live_stategraph_primary_execution_engine'
        engine_id = 'codex_user_level_graph_resident_live_primary_execution_engine'
        graph_api_surface = 'StateGraph'
        execute_surface = 'CompiledGraph.invoke/stream'
        boundary_surface = 'graph_resident_boundary_state'
        decision_surface = 'compiled_boundary_nodes_and_phase_end'
      }
      compile_supported = [bool]$statefulEngineProjection.compile_supported
      compiled_graph_present = [bool]$statefulEngineProjection.compiled_graph_present
      invoke_supported = [bool]$statefulEngineProjection.invoke_supported
      stream_supported = [bool]$statefulEngineProjection.stream_supported
      current_execution_node = [string]$statefulEngineProjection.current_execution_node
      mapped_phase = [string]$statefulEngineProjection.mapped_phase
      boundary_node_path = @()
      boundary_phase_path = @()
      boundary_transition_log = @()
      boundary_state_kind = 'ordinary'
      superstep_count = 0
      stop_boundary = ''
      terminal_reached = $false
      recursion_limit_supported = $true
      remaining_steps_supported = $true
      recursion_limit = 8
      execution_posture = if ([bool]$statefulEngineProjection.compile_supported) { 'ready' } else { 'unavailable' }
      last_run_kind = ''
      last_run_status = ''
      last_run_reason = ''
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { $false }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { $false }
    invoke_supported = if ($null -ne $engineState.PSObject.Properties['invoke_supported']) { [bool]$engineState.invoke_supported } else { $false }
    stream_supported = if ($null -ne $engineState.PSObject.Properties['stream_supported']) { [bool]$engineState.stream_supported } else { $false }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$statefulEngineProjection.current_execution_node }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$statefulEngineProjection.mapped_phase }
    boundary_node_path = if ($null -ne $engineState.PSObject.Properties['boundary_node_path'] -and $null -ne $engineState.boundary_node_path) { @($engineState.boundary_node_path | ForEach-Object { [string]$_ }) } else { @() }
    boundary_phase_path = if ($null -ne $engineState.PSObject.Properties['boundary_phase_path'] -and $null -ne $engineState.boundary_phase_path) { @($engineState.boundary_phase_path | ForEach-Object { [string]$_ }) } else { @() }
    boundary_transition_log = if ($null -ne $engineState.PSObject.Properties['boundary_transition_log'] -and $null -ne $engineState.boundary_transition_log) { @($engineState.boundary_transition_log | ForEach-Object { [string]$_ }) } else { @() }
    boundary_state_kind = if ($null -ne $engineState.PSObject.Properties['boundary_state_kind']) { [string]$engineState.boundary_state_kind } else { 'ordinary' }
    superstep_count = if ($null -ne $engineState.PSObject.Properties['superstep_count']) { [int]$engineState.superstep_count } else { 0 }
    stop_boundary = if ($null -ne $engineState.PSObject.Properties['stop_boundary']) { [string]$engineState.stop_boundary } else { '' }
    terminal_reached = if ($null -ne $engineState.PSObject.Properties['terminal_reached']) { [bool]$engineState.terminal_reached } else { $false }
    recursion_limit_supported = if ($null -ne $engineState.PSObject.Properties['recursion_limit_supported']) { [bool]$engineState.recursion_limit_supported } else { $true }
    remaining_steps_supported = if ($null -ne $engineState.PSObject.Properties['remaining_steps_supported']) { [bool]$engineState.remaining_steps_supported } else { $true }
    recursion_limit = if ($null -ne $engineState.PSObject.Properties['recursion_limit']) { [int]$engineState.recursion_limit } else { 8 }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { 'unavailable' }
    last_run_kind = if ($null -ne $engineState.PSObject.Properties['last_run_kind']) { [string]$engineState.last_run_kind } else { '' }
    last_run_status = if ($null -ne $engineState.PSObject.Properties['last_run_status']) { [string]$engineState.last_run_status } else { '' }
    last_run_reason = if ($null -ne $engineState.PSObject.Properties['last_run_reason']) { [string]$engineState.last_run_reason } else { '' }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphHandoffStateLivePrimaryEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('handoff_state_live_primary_engine_state')) {
    $engineState = $ThreadRecord['handoff_state_live_primary_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['handoff_state_live_primary_engine_state']) {
    $engineState = $ThreadRecord.handoff_state_live_primary_engine_state
  }

  $boundaryEngineProjection = Get-CodexUserLevelLangGraphBoundaryStateLivePrimaryEngineProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId
  $commandProjection = Get-CodexUserLevelLangGraphCommandProjection -ThreadRecord $ThreadRecord -ThreadId $ThreadId
  $subgraphProjection = Get-CodexUserLevelLangGraphSubgraphProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-handoff-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'subgraph_aware_live_stategraph_primary_execution_engine'
        engine_id = 'codex_user_level_subgraph_aware_live_primary_execution_engine'
        graph_api_surface = 'StateGraph'
        execute_surface = 'CompiledGraph.invoke/stream'
        handoff_surface = 'subgraph_and_parent_handoff_state'
        subgraph_surface = 'active_subgraph/source_subgraph/target_subgraph'
      }
      compile_supported = [bool]$boundaryEngineProjection.compile_supported
      compiled_graph_present = [bool]$boundaryEngineProjection.compiled_graph_present
      invoke_supported = [bool]$boundaryEngineProjection.invoke_supported
      stream_supported = [bool]$boundaryEngineProjection.stream_supported
      current_execution_node = [string]$boundaryEngineProjection.current_execution_node
      mapped_phase = [string]$boundaryEngineProjection.mapped_phase
      handoff_node_path = @()
      handoff_phase_path = @()
      handoff_subgraph_path = @()
      handoff_transition_log = @()
      handoff_state_kind = 'ordinary'
      active_subgraph = [string]$subgraphProjection.active_subgraph
      source_subgraph = [string]$commandProjection.source_subgraph
      target_subgraph = [string]$commandProjection.target_subgraph
      parent_handoff_target = [string]$commandProjection.parent_handoff_target
      graph_scope = [string]$commandProjection.graph_scope
      superstep_count = 0
      stop_boundary = ''
      terminal_reached = $false
      recursion_limit_supported = $true
      remaining_steps_supported = $true
      recursion_limit = 8
      execution_posture = if ([bool]$boundaryEngineProjection.compile_supported) { 'ready' } else { 'unavailable' }
      last_run_kind = ''
      last_run_status = ''
      last_run_reason = ''
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { $false }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { $false }
    invoke_supported = if ($null -ne $engineState.PSObject.Properties['invoke_supported']) { [bool]$engineState.invoke_supported } else { $false }
    stream_supported = if ($null -ne $engineState.PSObject.Properties['stream_supported']) { [bool]$engineState.stream_supported } else { $false }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$boundaryEngineProjection.current_execution_node }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$boundaryEngineProjection.mapped_phase }
    handoff_node_path = if ($null -ne $engineState.PSObject.Properties['handoff_node_path'] -and $null -ne $engineState.handoff_node_path) { @($engineState.handoff_node_path | ForEach-Object { [string]$_ }) } else { @() }
    handoff_phase_path = if ($null -ne $engineState.PSObject.Properties['handoff_phase_path'] -and $null -ne $engineState.handoff_phase_path) { @($engineState.handoff_phase_path | ForEach-Object { [string]$_ }) } else { @() }
    handoff_subgraph_path = if ($null -ne $engineState.PSObject.Properties['handoff_subgraph_path'] -and $null -ne $engineState.handoff_subgraph_path) { @($engineState.handoff_subgraph_path | ForEach-Object { [string]$_ }) } else { @() }
    handoff_transition_log = if ($null -ne $engineState.PSObject.Properties['handoff_transition_log'] -and $null -ne $engineState.handoff_transition_log) { @($engineState.handoff_transition_log | ForEach-Object { [string]$_ }) } else { @() }
    handoff_state_kind = if ($null -ne $engineState.PSObject.Properties['handoff_state_kind']) { [string]$engineState.handoff_state_kind } else { 'ordinary' }
    active_subgraph = if ($null -ne $engineState.PSObject.Properties['active_subgraph']) { [string]$engineState.active_subgraph } else { [string]$subgraphProjection.active_subgraph }
    source_subgraph = if ($null -ne $engineState.PSObject.Properties['source_subgraph']) { [string]$engineState.source_subgraph } else { [string]$commandProjection.source_subgraph }
    target_subgraph = if ($null -ne $engineState.PSObject.Properties['target_subgraph']) { [string]$engineState.target_subgraph } else { [string]$commandProjection.target_subgraph }
    parent_handoff_target = if ($null -ne $engineState.PSObject.Properties['parent_handoff_target']) { [string]$engineState.parent_handoff_target } else { [string]$commandProjection.parent_handoff_target }
    graph_scope = if ($null -ne $engineState.PSObject.Properties['graph_scope']) { [string]$engineState.graph_scope } else { [string]$commandProjection.graph_scope }
    superstep_count = if ($null -ne $engineState.PSObject.Properties['superstep_count']) { [int]$engineState.superstep_count } else { 0 }
    stop_boundary = if ($null -ne $engineState.PSObject.Properties['stop_boundary']) { [string]$engineState.stop_boundary } else { '' }
    terminal_reached = if ($null -ne $engineState.PSObject.Properties['terminal_reached']) { [bool]$engineState.terminal_reached } else { $false }
    recursion_limit_supported = if ($null -ne $engineState.PSObject.Properties['recursion_limit_supported']) { [bool]$engineState.recursion_limit_supported } else { $true }
    remaining_steps_supported = if ($null -ne $engineState.PSObject.Properties['remaining_steps_supported']) { [bool]$engineState.remaining_steps_supported } else { $true }
    recursion_limit = if ($null -ne $engineState.PSObject.Properties['recursion_limit']) { [int]$engineState.recursion_limit } else { 8 }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { 'unavailable' }
    last_run_kind = if ($null -ne $engineState.PSObject.Properties['last_run_kind']) { [string]$engineState.last_run_kind } else { '' }
    last_run_status = if ($null -ne $engineState.PSObject.Properties['last_run_status']) { [string]$engineState.last_run_status } else { '' }
    last_run_reason = if ($null -ne $engineState.PSObject.Properties['last_run_reason']) { [string]$engineState.last_run_reason } else { '' }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphApprovalAwareLivePrimaryEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('approval_aware_live_primary_engine_state')) {
    $engineState = $ThreadRecord['approval_aware_live_primary_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['approval_aware_live_primary_engine_state']) {
    $engineState = $ThreadRecord.approval_aware_live_primary_engine_state
  }

  $approvalQueueProjection = Get-CodexUserLevelLangGraphApprovalQueueProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -InterruptRecord $null -ThreadId $ThreadId
  $boundaryEngineProjection = Get-CodexUserLevelLangGraphBoundaryStateLivePrimaryEngineProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-approval-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'approval_aware_live_stategraph_primary_execution_engine'
        engine_id = 'codex_user_level_approval_aware_live_primary_execution_engine'
        graph_api_surface = 'StateGraph'
        execute_surface = 'CompiledGraph.invoke/stream'
        approval_surface = 'approval_queue_and_resume_map_state'
        resume_surface = 'queue_posture/resume_map_keys/current_interrupt_id'
      }
      compile_supported = [bool]$boundaryEngineProjection.compile_supported
      compiled_graph_present = [bool]$boundaryEngineProjection.compiled_graph_present
      invoke_supported = [bool]$boundaryEngineProjection.invoke_supported
      stream_supported = [bool]$boundaryEngineProjection.stream_supported
      current_execution_node = [string]$boundaryEngineProjection.current_execution_node
      mapped_phase = [string]$boundaryEngineProjection.mapped_phase
      approval_node_path = @()
      approval_phase_path = @()
      approval_transition_log = @()
      resume_state_kind = 'ordinary'
      queue_posture = [string]$approvalQueueProjection.queue_posture
      pending_count = [int]$approvalQueueProjection.pending_count
      resolved_count = [int]$approvalQueueProjection.resolved_count
      current_interrupt_id = [string]$approvalQueueProjection.current_interrupt_id
      resume_map_keys = @($approvalQueueProjection.resume_map_keys | ForEach-Object { [string]$_ })
      superstep_count = 0
      stop_boundary = ''
      terminal_reached = $false
      recursion_limit_supported = $true
      remaining_steps_supported = $true
      recursion_limit = 8
      execution_posture = if ([bool]$boundaryEngineProjection.compile_supported) { 'ready' } else { 'unavailable' }
      last_run_kind = ''
      last_run_status = ''
      last_run_reason = ''
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { $false }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { $false }
    invoke_supported = if ($null -ne $engineState.PSObject.Properties['invoke_supported']) { [bool]$engineState.invoke_supported } else { $false }
    stream_supported = if ($null -ne $engineState.PSObject.Properties['stream_supported']) { [bool]$engineState.stream_supported } else { $false }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$boundaryEngineProjection.current_execution_node }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$boundaryEngineProjection.mapped_phase }
    approval_node_path = if ($null -ne $engineState.PSObject.Properties['approval_node_path'] -and $null -ne $engineState.approval_node_path) { @($engineState.approval_node_path | ForEach-Object { [string]$_ }) } else { @() }
    approval_phase_path = if ($null -ne $engineState.PSObject.Properties['approval_phase_path'] -and $null -ne $engineState.approval_phase_path) { @($engineState.approval_phase_path | ForEach-Object { [string]$_ }) } else { @() }
    approval_transition_log = if ($null -ne $engineState.PSObject.Properties['approval_transition_log'] -and $null -ne $engineState.approval_transition_log) { @($engineState.approval_transition_log | ForEach-Object { [string]$_ }) } else { @() }
    resume_state_kind = if ($null -ne $engineState.PSObject.Properties['resume_state_kind']) { [string]$engineState.resume_state_kind } else { 'ordinary' }
    queue_posture = if ($null -ne $engineState.PSObject.Properties['queue_posture']) { [string]$engineState.queue_posture } else { [string]$approvalQueueProjection.queue_posture }
    pending_count = if ($null -ne $engineState.PSObject.Properties['pending_count']) { [int]$engineState.pending_count } else { [int]$approvalQueueProjection.pending_count }
    resolved_count = if ($null -ne $engineState.PSObject.Properties['resolved_count']) { [int]$engineState.resolved_count } else { [int]$approvalQueueProjection.resolved_count }
    current_interrupt_id = if ($null -ne $engineState.PSObject.Properties['current_interrupt_id']) { [string]$engineState.current_interrupt_id } else { [string]$approvalQueueProjection.current_interrupt_id }
    resume_map_keys = if ($null -ne $engineState.PSObject.Properties['resume_map_keys'] -and $null -ne $engineState.resume_map_keys) { @($engineState.resume_map_keys | ForEach-Object { [string]$_ }) } else { @($approvalQueueProjection.resume_map_keys | ForEach-Object { [string]$_ }) }
    superstep_count = if ($null -ne $engineState.PSObject.Properties['superstep_count']) { [int]$engineState.superstep_count } else { 0 }
    stop_boundary = if ($null -ne $engineState.PSObject.Properties['stop_boundary']) { [string]$engineState.stop_boundary } else { '' }
    terminal_reached = if ($null -ne $engineState.PSObject.Properties['terminal_reached']) { [bool]$engineState.terminal_reached } else { $false }
    recursion_limit_supported = if ($null -ne $engineState.PSObject.Properties['recursion_limit_supported']) { [bool]$engineState.recursion_limit_supported } else { $true }
    remaining_steps_supported = if ($null -ne $engineState.PSObject.Properties['remaining_steps_supported']) { [bool]$engineState.remaining_steps_supported } else { $true }
    recursion_limit = if ($null -ne $engineState.PSObject.Properties['recursion_limit']) { [int]$engineState.recursion_limit } else { 8 }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { 'unavailable' }
    last_run_kind = if ($null -ne $engineState.PSObject.Properties['last_run_kind']) { [string]$engineState.last_run_kind } else { '' }
    last_run_status = if ($null -ne $engineState.PSObject.Properties['last_run_status']) { [string]$engineState.last_run_status } else { '' }
    last_run_reason = if ($null -ne $engineState.PSObject.Properties['last_run_reason']) { [string]$engineState.last_run_reason } else { '' }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphProvenanceStateLivePrimaryEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('provenance_state_live_primary_engine_state')) {
    $engineState = $ThreadRecord['provenance_state_live_primary_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['provenance_state_live_primary_engine_state']) {
    $engineState = $ThreadRecord.provenance_state_live_primary_engine_state
  }

  $historyProjection = if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    Read-CodexUserLevelLangGraphHistoryState -RepoRoot $RepoRoot -ThreadId $ThreadId -ThreadRecord $ThreadRecord -CheckpointRecord ([ordered]@{}) -InterruptRecord ([ordered]@{})
  } else {
    [ordered]@{
      exists = $false
      compatibility = 'no_history'
      target_count = 0
      available_targets = @()
      source_records = @()
    }
  }
  $recoveryProjection = Get-CodexUserLevelLangGraphRecoveryProjection -ThreadRecord $ThreadRecord
  $boundaryEngineProjection = Get-CodexUserLevelLangGraphBoundaryStateLivePrimaryEngineProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-provenance-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'recovery_aware_live_stategraph_primary_execution_engine'
        engine_id = 'codex_user_level_recovery_aware_live_primary_execution_engine'
        graph_api_surface = 'StateGraph'
        execute_surface = 'CompiledGraph.invoke/stream'
        recovery_surface = 'recovery_target_and_action_state'
        provenance_surface = 'source_records_and_history_targets'
      }
      compile_supported = [bool]$boundaryEngineProjection.compile_supported
      compiled_graph_present = [bool]$boundaryEngineProjection.compiled_graph_present
      invoke_supported = [bool]$boundaryEngineProjection.invoke_supported
      stream_supported = [bool]$boundaryEngineProjection.stream_supported
      current_execution_node = [string]$boundaryEngineProjection.current_execution_node
      mapped_phase = [string]$boundaryEngineProjection.mapped_phase
      provenance_node_path = @()
      provenance_phase_path = @()
      provenance_transition_log = @()
      provenance_state_kind = 'ordinary'
      recovery_posture = [string]$recoveryProjection.posture
      recovery_action = [string]$recoveryProjection.last_action
      recovery_target_id = [string]$recoveryProjection.target_id
      recovery_target_kind = ''
      source_records = @($recoveryProjection.source_records | ForEach-Object { [string]$_ })
      recoverable_fields_touched = @($recoveryProjection.recoverable_fields_touched | ForEach-Object { [string]$_ })
      history_compatibility = [string]$historyProjection.compatibility
      history_target_count = [int]$historyProjection.target_count
      superstep_count = 0
      stop_boundary = ''
      terminal_reached = $false
      recursion_limit_supported = $true
      remaining_steps_supported = $true
      recursion_limit = 8
      execution_posture = if ([bool]$boundaryEngineProjection.compile_supported) { 'ready' } else { 'unavailable' }
      last_run_kind = ''
      last_run_status = ''
      last_run_reason = ''
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { $false }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { $false }
    invoke_supported = if ($null -ne $engineState.PSObject.Properties['invoke_supported']) { [bool]$engineState.invoke_supported } else { $false }
    stream_supported = if ($null -ne $engineState.PSObject.Properties['stream_supported']) { [bool]$engineState.stream_supported } else { $false }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$boundaryEngineProjection.current_execution_node }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$boundaryEngineProjection.mapped_phase }
    provenance_node_path = if ($null -ne $engineState.PSObject.Properties['provenance_node_path'] -and $null -ne $engineState.provenance_node_path) { @($engineState.provenance_node_path | ForEach-Object { [string]$_ }) } else { @() }
    provenance_phase_path = if ($null -ne $engineState.PSObject.Properties['provenance_phase_path'] -and $null -ne $engineState.provenance_phase_path) { @($engineState.provenance_phase_path | ForEach-Object { [string]$_ }) } else { @() }
    provenance_transition_log = if ($null -ne $engineState.PSObject.Properties['provenance_transition_log'] -and $null -ne $engineState.provenance_transition_log) { @($engineState.provenance_transition_log | ForEach-Object { [string]$_ }) } else { @() }
    provenance_state_kind = if ($null -ne $engineState.PSObject.Properties['provenance_state_kind']) { [string]$engineState.provenance_state_kind } else { 'ordinary' }
    recovery_posture = if ($null -ne $engineState.PSObject.Properties['recovery_posture']) { [string]$engineState.recovery_posture } else { [string]$recoveryProjection.posture }
    recovery_action = if ($null -ne $engineState.PSObject.Properties['recovery_action']) { [string]$engineState.recovery_action } else { [string]$recoveryProjection.last_action }
    recovery_target_id = if ($null -ne $engineState.PSObject.Properties['recovery_target_id']) { [string]$engineState.recovery_target_id } else { [string]$recoveryProjection.target_id }
    recovery_target_kind = if ($null -ne $engineState.PSObject.Properties['recovery_target_kind']) { [string]$engineState.recovery_target_kind } else { '' }
    source_records = if ($null -ne $engineState.PSObject.Properties['source_records'] -and $null -ne $engineState.source_records) { @($engineState.source_records | ForEach-Object { [string]$_ }) } else { @($recoveryProjection.source_records | ForEach-Object { [string]$_ }) }
    recoverable_fields_touched = if ($null -ne $engineState.PSObject.Properties['recoverable_fields_touched'] -and $null -ne $engineState.recoverable_fields_touched) { @($engineState.recoverable_fields_touched | ForEach-Object { [string]$_ }) } else { @($recoveryProjection.recoverable_fields_touched | ForEach-Object { [string]$_ }) }
    history_compatibility = if ($null -ne $engineState.PSObject.Properties['history_compatibility']) { [string]$engineState.history_compatibility } else { [string]$historyProjection.compatibility }
    history_target_count = if ($null -ne $engineState.PSObject.Properties['history_target_count']) { [int]$engineState.history_target_count } else { [int]$historyProjection.target_count }
    superstep_count = if ($null -ne $engineState.PSObject.Properties['superstep_count']) { [int]$engineState.superstep_count } else { 0 }
    stop_boundary = if ($null -ne $engineState.PSObject.Properties['stop_boundary']) { [string]$engineState.stop_boundary } else { '' }
    terminal_reached = if ($null -ne $engineState.PSObject.Properties['terminal_reached']) { [bool]$engineState.terminal_reached } else { $false }
    recursion_limit_supported = if ($null -ne $engineState.PSObject.Properties['recursion_limit_supported']) { [bool]$engineState.recursion_limit_supported } else { $true }
    remaining_steps_supported = if ($null -ne $engineState.PSObject.Properties['remaining_steps_supported']) { [bool]$engineState.remaining_steps_supported } else { $true }
    recursion_limit = if ($null -ne $engineState.PSObject.Properties['recursion_limit']) { [int]$engineState.recursion_limit } else { 8 }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { 'unavailable' }
    last_run_kind = if ($null -ne $engineState.PSObject.Properties['last_run_kind']) { [string]$engineState.last_run_kind } else { '' }
    last_run_status = if ($null -ne $engineState.PSObject.Properties['last_run_status']) { [string]$engineState.last_run_status } else { '' }
    last_run_reason = if ($null -ne $engineState.PSObject.Properties['last_run_reason']) { [string]$engineState.last_run_reason } else { '' }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphDurableArtifactAwareLivePrimaryEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('durable_artifact_aware_live_primary_engine_state')) {
    $engineState = $ThreadRecord['durable_artifact_aware_live_primary_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['durable_artifact_aware_live_primary_engine_state']) {
    $engineState = $ThreadRecord.durable_artifact_aware_live_primary_engine_state
  }

  $briefState = if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    Read-CodexUserLevelLangGraphImplementationBriefState -RepoRoot $RepoRoot -ThreadId $ThreadId
  } else {
    [ordered]@{
      exists = $false
      brief_id = ''
      source_evidence_ref_count = 0
    }
  }
  $survivorQueueState = if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    Read-CodexUserLevelLangGraphSurvivorQueueState -RepoRoot $RepoRoot -ThreadId $ThreadId
  } else {
    [ordered]@{
      exists = $false
      queue_kind = ''
      item_count = 0
    }
  }
  $provenanceEngineProjection = Get-CodexUserLevelLangGraphProvenanceStateLivePrimaryEngineProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $artifactStateKind = 'ordinary'
  if ([bool]$briefState.exists -and [bool]$survivorQueueState.exists) {
    $artifactStateKind = 'brief_and_survivor_queue_present'
  } elseif ([bool]$briefState.exists) {
    $artifactStateKind = 'implementation_brief_present'
  } elseif ([bool]$survivorQueueState.exists) {
    $artifactStateKind = 'survivor_queue_present'
  }

  $artifactTransitionLog = @($provenanceEngineProjection.provenance_transition_log | ForEach-Object { [string]$_ })
  if ([bool]$briefState.exists) {
    $briefMarker = if (-not [string]::IsNullOrWhiteSpace([string]$briefState.brief_id)) { [string]$briefState.brief_id } else { 'present' }
    $artifactTransitionLog += ('brief:{0}' -f $briefMarker)
    $artifactTransitionLog += ('brief_refs:{0}' -f ([int]$briefState.source_evidence_ref_count))
  }
  if ([bool]$survivorQueueState.exists) {
    $queueMarker = if (-not [string]::IsNullOrWhiteSpace([string]$survivorQueueState.queue_kind)) { [string]$survivorQueueState.queue_kind } else { 'present' }
    $artifactTransitionLog += ('survivor_queue:{0}' -f $queueMarker)
    $artifactTransitionLog += ('survivors:{0}' -f ([int]$survivorQueueState.item_count))
  }
  $artifactTransitionLog = @(
    $artifactTransitionLog |
      Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } |
      Select-Object -Unique
  )

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-artifact-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'durable_artifact_aware_live_stategraph_primary_execution_engine'
        engine_id = 'codex_user_level_durable_artifact_aware_live_primary_execution_engine'
        graph_api_surface = 'StateGraph'
        execute_surface = 'CompiledGraph.invoke/stream'
        artifact_surface = 'implementation_brief_and_survivor_queue_state'
        artifact_summary_surface = 'artifact_state_kind/brief_id/source_evidence_ref_count/survivor_count'
      }
      compile_supported = [bool]$provenanceEngineProjection.compile_supported
      compiled_graph_present = [bool]$provenanceEngineProjection.compiled_graph_present
      invoke_supported = [bool]$provenanceEngineProjection.invoke_supported
      stream_supported = [bool]$provenanceEngineProjection.stream_supported
      current_execution_node = [string]$provenanceEngineProjection.current_execution_node
      mapped_phase = [string]$provenanceEngineProjection.mapped_phase
      artifact_node_path = @($provenanceEngineProjection.provenance_node_path | ForEach-Object { [string]$_ })
      artifact_phase_path = @($provenanceEngineProjection.provenance_phase_path | ForEach-Object { [string]$_ })
      artifact_transition_log = @($artifactTransitionLog)
      artifact_state_kind = $artifactStateKind
      implementation_brief_present = [bool]$briefState.exists
      implementation_brief_id = [string]$briefState.brief_id
      implementation_brief_source_evidence_ref_count = [int]$briefState.source_evidence_ref_count
      survivor_queue_present = [bool]$survivorQueueState.exists
      survivor_queue_kind = [string]$survivorQueueState.queue_kind
      survivor_count = [int]$survivorQueueState.item_count
      superstep_count = [int]$provenanceEngineProjection.superstep_count
      stop_boundary = [string]$provenanceEngineProjection.stop_boundary
      terminal_reached = [bool]$provenanceEngineProjection.terminal_reached
      recursion_limit_supported = [bool]$provenanceEngineProjection.recursion_limit_supported
      remaining_steps_supported = [bool]$provenanceEngineProjection.remaining_steps_supported
      recursion_limit = [int]$provenanceEngineProjection.recursion_limit
      execution_posture = [string]$provenanceEngineProjection.execution_posture
      last_run_kind = [string]$provenanceEngineProjection.last_run_kind
      last_run_status = [string]$provenanceEngineProjection.last_run_status
      last_run_reason = [string]$provenanceEngineProjection.last_run_reason
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { [bool]$provenanceEngineProjection.compile_supported }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { [bool]$provenanceEngineProjection.compiled_graph_present }
    invoke_supported = if ($null -ne $engineState.PSObject.Properties['invoke_supported']) { [bool]$engineState.invoke_supported } else { [bool]$provenanceEngineProjection.invoke_supported }
    stream_supported = if ($null -ne $engineState.PSObject.Properties['stream_supported']) { [bool]$engineState.stream_supported } else { [bool]$provenanceEngineProjection.stream_supported }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$provenanceEngineProjection.current_execution_node }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$provenanceEngineProjection.mapped_phase }
    artifact_node_path = if ($null -ne $engineState.PSObject.Properties['artifact_node_path'] -and $null -ne $engineState.artifact_node_path) { @($engineState.artifact_node_path | ForEach-Object { [string]$_ }) } else { @($provenanceEngineProjection.provenance_node_path | ForEach-Object { [string]$_ }) }
    artifact_phase_path = if ($null -ne $engineState.PSObject.Properties['artifact_phase_path'] -and $null -ne $engineState.artifact_phase_path) { @($engineState.artifact_phase_path | ForEach-Object { [string]$_ }) } else { @($provenanceEngineProjection.provenance_phase_path | ForEach-Object { [string]$_ }) }
    artifact_transition_log = if ($null -ne $engineState.PSObject.Properties['artifact_transition_log'] -and $null -ne $engineState.artifact_transition_log) { @($engineState.artifact_transition_log | ForEach-Object { [string]$_ }) } else { @($artifactTransitionLog) }
    artifact_state_kind = if ($null -ne $engineState.PSObject.Properties['artifact_state_kind']) { [string]$engineState.artifact_state_kind } else { $artifactStateKind }
    implementation_brief_present = if ($null -ne $engineState.PSObject.Properties['implementation_brief_present']) { [bool]$engineState.implementation_brief_present } else { [bool]$briefState.exists }
    implementation_brief_id = if ($null -ne $engineState.PSObject.Properties['implementation_brief_id']) { [string]$engineState.implementation_brief_id } else { [string]$briefState.brief_id }
    implementation_brief_source_evidence_ref_count = if ($null -ne $engineState.PSObject.Properties['implementation_brief_source_evidence_ref_count']) { [int]$engineState.implementation_brief_source_evidence_ref_count } else { [int]$briefState.source_evidence_ref_count }
    survivor_queue_present = if ($null -ne $engineState.PSObject.Properties['survivor_queue_present']) { [bool]$engineState.survivor_queue_present } else { [bool]$survivorQueueState.exists }
    survivor_queue_kind = if ($null -ne $engineState.PSObject.Properties['survivor_queue_kind']) { [string]$engineState.survivor_queue_kind } else { [string]$survivorQueueState.queue_kind }
    survivor_count = if ($null -ne $engineState.PSObject.Properties['survivor_count']) { [int]$engineState.survivor_count } else { [int]$survivorQueueState.item_count }
    superstep_count = if ($null -ne $engineState.PSObject.Properties['superstep_count']) { [int]$engineState.superstep_count } else { [int]$provenanceEngineProjection.superstep_count }
    stop_boundary = if ($null -ne $engineState.PSObject.Properties['stop_boundary']) { [string]$engineState.stop_boundary } else { [string]$provenanceEngineProjection.stop_boundary }
    terminal_reached = if ($null -ne $engineState.PSObject.Properties['terminal_reached']) { [bool]$engineState.terminal_reached } else { [bool]$provenanceEngineProjection.terminal_reached }
    recursion_limit_supported = if ($null -ne $engineState.PSObject.Properties['recursion_limit_supported']) { [bool]$engineState.recursion_limit_supported } else { [bool]$provenanceEngineProjection.recursion_limit_supported }
    remaining_steps_supported = if ($null -ne $engineState.PSObject.Properties['remaining_steps_supported']) { [bool]$engineState.remaining_steps_supported } else { [bool]$provenanceEngineProjection.remaining_steps_supported }
    recursion_limit = if ($null -ne $engineState.PSObject.Properties['recursion_limit']) { [int]$engineState.recursion_limit } else { [int]$provenanceEngineProjection.recursion_limit }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { [string]$provenanceEngineProjection.execution_posture }
    last_run_kind = if ($null -ne $engineState.PSObject.Properties['last_run_kind']) { [string]$engineState.last_run_kind } else { [string]$provenanceEngineProjection.last_run_kind }
    last_run_status = if ($null -ne $engineState.PSObject.Properties['last_run_status']) { [string]$engineState.last_run_status } else { [string]$provenanceEngineProjection.last_run_status }
    last_run_reason = if ($null -ne $engineState.PSObject.Properties['last_run_reason']) { [string]$engineState.last_run_reason } else { [string]$provenanceEngineProjection.last_run_reason }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphReducerAwareLivePrimaryEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('reducer_aware_live_primary_engine_state')) {
    $engineState = $ThreadRecord['reducer_aware_live_primary_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['reducer_aware_live_primary_engine_state']) {
    $engineState = $ThreadRecord.reducer_aware_live_primary_engine_state
  }

  $artifactEngineProjection = Get-CodexUserLevelLangGraphDurableArtifactAwareLivePrimaryEngineProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId
  $reducerProjection = Get-CodexUserLevelLangGraphReducerProjection -ThreadRecord $ThreadRecord

  $mergeStateKind = 'ordinary'
  $mergeChannelsUpdated = @($reducerProjection.merge_channels_updated | ForEach-Object { [string]$_ })
  $sourceRecords = @($reducerProjection.source_records | ForEach-Object { [string]$_ })
  $invalidUpdates = @($reducerProjection.invalid_multi_writer_updates)
  if ([string]$reducerProjection.compatibility -eq 'pre_reducer') {
    $mergeStateKind = 'pre_reducer'
  } elseif ([bool]$reducerProjection.invalid_multi_writer_detected) {
    $mergeStateKind = 'invalid_multi_writer_detected'
  } elseif ($mergeChannelsUpdated.Count -gt 0 -and $sourceRecords.Count -gt 1) {
    $mergeStateKind = 'multi_branch_merge'
  } elseif ($mergeChannelsUpdated.Count -gt 0) {
    $mergeStateKind = 'single_branch_merge'
  } elseif ([string]$reducerProjection.compatibility -eq 'reducer_aware') {
    $mergeStateKind = 'reducer_ready'
  }

  $mergeTransitionLog = @($artifactEngineProjection.artifact_transition_log | ForEach-Object { [string]$_ })
  if (-not [string]::IsNullOrWhiteSpace([string]$reducerProjection.fanout_state)) {
    $mergeTransitionLog += ('fanout:{0}' -f ([string]$reducerProjection.fanout_state))
  }
  if ($mergeChannelsUpdated.Count -gt 0) {
    $mergeTransitionLog += ('merge_channels:{0}' -f $mergeChannelsUpdated.Count)
  }
  if ($invalidUpdates.Count -gt 0) {
    $mergeTransitionLog += ('invalid_multi_writer:{0}' -f $invalidUpdates.Count)
  }
  if ($sourceRecords.Count -gt 0) {
    $mergeTransitionLog += ('reducer_sources:{0}' -f $sourceRecords.Count)
  }
  $mergeTransitionLog = @(
    $mergeTransitionLog |
      Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } |
      Select-Object -Unique
  )

  $channelItemCounts = [ordered]@{}
  if ($null -ne $reducerProjection.channel_item_counts) {
    if ($reducerProjection.channel_item_counts -is [System.Collections.IDictionary]) {
      foreach ($key in @($reducerProjection.channel_item_counts.Keys | Sort-Object)) {
        $channelItemCounts[[string]$key] = [int]$reducerProjection.channel_item_counts[$key]
      }
    } else {
      foreach ($property in @($reducerProjection.channel_item_counts.PSObject.Properties | Sort-Object Name)) {
        $channelItemCounts[[string]$property.Name] = [int]$property.Value
      }
    }
  }

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-reducer-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'reducer_aware_live_stategraph_primary_execution_engine'
        engine_id = 'codex_user_level_reducer_aware_live_primary_execution_engine'
        graph_api_surface = 'StateGraph'
        execute_surface = 'CompiledGraph.invoke/stream'
        reducer_surface = 'reducer_merge_channels_and_single_writer_state'
        merge_surface = 'fanout_state/merge_channels_updated/source_records'
      }
      compile_supported = [bool]$artifactEngineProjection.compile_supported
      compiled_graph_present = [bool]$artifactEngineProjection.compiled_graph_present
      invoke_supported = [bool]$artifactEngineProjection.invoke_supported
      stream_supported = [bool]$artifactEngineProjection.stream_supported
      current_execution_node = [string]$artifactEngineProjection.current_execution_node
      mapped_phase = [string]$artifactEngineProjection.mapped_phase
      merge_node_path = @($artifactEngineProjection.artifact_node_path | ForEach-Object { [string]$_ })
      merge_phase_path = @($artifactEngineProjection.artifact_phase_path | ForEach-Object { [string]$_ })
      merge_transition_log = @($mergeTransitionLog)
      merge_state_kind = $mergeStateKind
      reducer_compatibility = [string]$reducerProjection.compatibility
      fanout_state = [string]$reducerProjection.fanout_state
      invalid_multi_writer_detected = [bool]$reducerProjection.invalid_multi_writer_detected
      invalid_multi_writer_updates = @($invalidUpdates)
      merge_channels_updated = @($mergeChannelsUpdated)
      channel_item_counts = $channelItemCounts
      source_records = @($sourceRecords)
      superstep_count = [int]$artifactEngineProjection.superstep_count
      stop_boundary = [string]$artifactEngineProjection.stop_boundary
      terminal_reached = [bool]$artifactEngineProjection.terminal_reached
      recursion_limit_supported = [bool]$artifactEngineProjection.recursion_limit_supported
      remaining_steps_supported = [bool]$artifactEngineProjection.remaining_steps_supported
      recursion_limit = [int]$artifactEngineProjection.recursion_limit
      execution_posture = [string]$artifactEngineProjection.execution_posture
      last_run_kind = [string]$artifactEngineProjection.last_run_kind
      last_run_status = [string]$artifactEngineProjection.last_run_status
      last_run_reason = [string]$artifactEngineProjection.last_run_reason
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { [bool]$artifactEngineProjection.compile_supported }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { [bool]$artifactEngineProjection.compiled_graph_present }
    invoke_supported = if ($null -ne $engineState.PSObject.Properties['invoke_supported']) { [bool]$engineState.invoke_supported } else { [bool]$artifactEngineProjection.invoke_supported }
    stream_supported = if ($null -ne $engineState.PSObject.Properties['stream_supported']) { [bool]$engineState.stream_supported } else { [bool]$artifactEngineProjection.stream_supported }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$artifactEngineProjection.current_execution_node }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$artifactEngineProjection.mapped_phase }
    merge_node_path = if ($null -ne $engineState.PSObject.Properties['merge_node_path'] -and $null -ne $engineState.merge_node_path) { @($engineState.merge_node_path | ForEach-Object { [string]$_ }) } else { @($artifactEngineProjection.artifact_node_path | ForEach-Object { [string]$_ }) }
    merge_phase_path = if ($null -ne $engineState.PSObject.Properties['merge_phase_path'] -and $null -ne $engineState.merge_phase_path) { @($engineState.merge_phase_path | ForEach-Object { [string]$_ }) } else { @($artifactEngineProjection.artifact_phase_path | ForEach-Object { [string]$_ }) }
    merge_transition_log = @($mergeTransitionLog)
    merge_state_kind = $mergeStateKind
    reducer_compatibility = [string]$reducerProjection.compatibility
    fanout_state = [string]$reducerProjection.fanout_state
    invalid_multi_writer_detected = [bool]$reducerProjection.invalid_multi_writer_detected
    invalid_multi_writer_updates = @($invalidUpdates)
    merge_channels_updated = @($mergeChannelsUpdated)
    channel_item_counts = $channelItemCounts
    source_records = @($sourceRecords)
    superstep_count = if ($null -ne $engineState.PSObject.Properties['superstep_count']) { [int]$engineState.superstep_count } else { [int]$artifactEngineProjection.superstep_count }
    stop_boundary = if ($null -ne $engineState.PSObject.Properties['stop_boundary']) { [string]$engineState.stop_boundary } else { [string]$artifactEngineProjection.stop_boundary }
    terminal_reached = if ($null -ne $engineState.PSObject.Properties['terminal_reached']) { [bool]$engineState.terminal_reached } else { [bool]$artifactEngineProjection.terminal_reached }
    recursion_limit_supported = if ($null -ne $engineState.PSObject.Properties['recursion_limit_supported']) { [bool]$engineState.recursion_limit_supported } else { [bool]$artifactEngineProjection.recursion_limit_supported }
    remaining_steps_supported = if ($null -ne $engineState.PSObject.Properties['remaining_steps_supported']) { [bool]$engineState.remaining_steps_supported } else { [bool]$artifactEngineProjection.remaining_steps_supported }
    recursion_limit = if ($null -ne $engineState.PSObject.Properties['recursion_limit']) { [int]$engineState.recursion_limit } else { [int]$artifactEngineProjection.recursion_limit }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { [string]$artifactEngineProjection.execution_posture }
    last_run_kind = if ($null -ne $engineState.PSObject.Properties['last_run_kind']) { [string]$engineState.last_run_kind } else { [string]$artifactEngineProjection.last_run_kind }
    last_run_status = if ($null -ne $engineState.PSObject.Properties['last_run_status']) { [string]$engineState.last_run_status } else { [string]$artifactEngineProjection.last_run_status }
    last_run_reason = if ($null -ne $engineState.PSObject.Properties['last_run_reason']) { [string]$engineState.last_run_reason } else { [string]$artifactEngineProjection.last_run_reason }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphCommandAwareLivePrimaryEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('command_aware_live_primary_engine_state')) {
    $engineState = $ThreadRecord['command_aware_live_primary_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['command_aware_live_primary_engine_state']) {
    $engineState = $ThreadRecord.command_aware_live_primary_engine_state
  }

  $reducerEngineProjection = Get-CodexUserLevelLangGraphReducerAwareLivePrimaryEngineProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId
  $commandProjection = Get-CodexUserLevelLangGraphCommandProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $controlStateKind = 'ordinary'
  if ([string]$commandProjection.resume_posture -eq 'awaiting_command_resume') {
    $controlStateKind = 'awaiting_command_resume'
  } elseif ([string]$commandProjection.transition_kind -in @('parent_handoff', 'resume_parent_handoff')) {
    $controlStateKind = 'parent_handoff_control'
  } elseif ([string]$commandProjection.transition_kind -in @('goto', 'update_goto')) {
    $controlStateKind = 'goto_control'
  } elseif ([string]$commandProjection.transition_kind -in @('resume', 'resume_with_payload')) {
    $controlStateKind = 'resume_control'
  } elseif ([string]$commandProjection.transition_kind -eq 'update') {
    $controlStateKind = 'update_control'
  } elseif (-not [string]::IsNullOrWhiteSpace([string]$commandProjection.transition_kind)) {
    $controlStateKind = 'command_control'
  }

  $commandTransitionLog = @($reducerEngineProjection.merge_transition_log | ForEach-Object { [string]$_ })
  if (-not [string]::IsNullOrWhiteSpace([string]$commandProjection.transition_kind)) {
    $commandTransitionLog += ('command:{0}' -f ([string]$commandProjection.transition_kind))
  }
  if (-not [string]::IsNullOrWhiteSpace([string]$commandProjection.graph_scope)) {
    $commandTransitionLog += ('graph_scope:{0}' -f ([string]$commandProjection.graph_scope))
  }
  if (-not [string]::IsNullOrWhiteSpace([string]$commandProjection.goto_target)) {
    $commandTransitionLog += ('goto:{0}' -f ([string]$commandProjection.goto_target))
  }
  if (-not [string]::IsNullOrWhiteSpace([string]$commandProjection.parent_handoff_target)) {
    $commandTransitionLog += ('parent_handoff:{0}' -f ([string]$commandProjection.parent_handoff_target))
  }
  $updateKeys = @($commandProjection.update_keys | ForEach-Object { [string]$_ })
  if ($updateKeys.Count -gt 0) {
    $commandTransitionLog += ('update_keys:{0}' -f $updateKeys.Count)
  }
  if ([string]$commandProjection.resume_posture -ne 'ordinary') {
    $commandTransitionLog += ('resume:{0}' -f ([string]$commandProjection.resume_posture))
  }
  $resumePayloadKeys = @($commandProjection.resume_payload_keys | ForEach-Object { [string]$_ })
  if ($resumePayloadKeys.Count -gt 0) {
    $commandTransitionLog += ('resume_payload:{0}' -f $resumePayloadKeys.Count)
  }
  $commandTransitionLog = @(
    $commandTransitionLog |
      Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } |
      Select-Object -Unique
  )

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-command-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'command_aware_live_stategraph_primary_execution_engine'
        engine_id = 'codex_user_level_command_aware_live_primary_execution_engine'
        graph_api_surface = 'StateGraph'
        execute_surface = 'CompiledGraph.invoke/stream'
        command_surface = 'update_goto_resume_and_parent_handoff_state'
        control_surface = 'transition_kind/graph_scope/target_subgraph/resume_posture'
      }
      compile_supported = [bool]$reducerEngineProjection.compile_supported
      compiled_graph_present = [bool]$reducerEngineProjection.compiled_graph_present
      invoke_supported = [bool]$reducerEngineProjection.invoke_supported
      stream_supported = [bool]$reducerEngineProjection.stream_supported
      current_execution_node = [string]$reducerEngineProjection.current_execution_node
      mapped_phase = [string]$reducerEngineProjection.mapped_phase
      command_node_path = @($reducerEngineProjection.merge_node_path | ForEach-Object { [string]$_ })
      command_phase_path = @($reducerEngineProjection.merge_phase_path | ForEach-Object { [string]$_ })
      command_transition_log = @($commandTransitionLog)
      control_state_kind = $controlStateKind
      transition_kind = [string]$commandProjection.transition_kind
      update_keys = @($updateKeys)
      goto_target = [string]$commandProjection.goto_target
      graph_scope = [string]$commandProjection.graph_scope
      source_subgraph = [string]$commandProjection.source_subgraph
      target_subgraph = [string]$commandProjection.target_subgraph
      parent_handoff_target = [string]$commandProjection.parent_handoff_target
      resume_posture = [string]$commandProjection.resume_posture
      resume_payload_present = [bool]$commandProjection.resume_payload_present
      resume_payload_keys = @($resumePayloadKeys)
      superstep_count = [int]$reducerEngineProjection.superstep_count
      stop_boundary = [string]$reducerEngineProjection.stop_boundary
      terminal_reached = [bool]$reducerEngineProjection.terminal_reached
      recursion_limit_supported = [bool]$reducerEngineProjection.recursion_limit_supported
      remaining_steps_supported = [bool]$reducerEngineProjection.remaining_steps_supported
      recursion_limit = [int]$reducerEngineProjection.recursion_limit
      execution_posture = [string]$reducerEngineProjection.execution_posture
      last_run_kind = [string]$reducerEngineProjection.last_run_kind
      last_run_status = [string]$reducerEngineProjection.last_run_status
      last_run_reason = [string]$reducerEngineProjection.last_run_reason
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { [bool]$reducerEngineProjection.compile_supported }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { [bool]$reducerEngineProjection.compiled_graph_present }
    invoke_supported = if ($null -ne $engineState.PSObject.Properties['invoke_supported']) { [bool]$engineState.invoke_supported } else { [bool]$reducerEngineProjection.invoke_supported }
    stream_supported = if ($null -ne $engineState.PSObject.Properties['stream_supported']) { [bool]$engineState.stream_supported } else { [bool]$reducerEngineProjection.stream_supported }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$reducerEngineProjection.current_execution_node }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$reducerEngineProjection.mapped_phase }
    command_node_path = if ($null -ne $engineState.PSObject.Properties['command_node_path'] -and $null -ne $engineState.command_node_path) { @($engineState.command_node_path | ForEach-Object { [string]$_ }) } else { @($reducerEngineProjection.merge_node_path | ForEach-Object { [string]$_ }) }
    command_phase_path = if ($null -ne $engineState.PSObject.Properties['command_phase_path'] -and $null -ne $engineState.command_phase_path) { @($engineState.command_phase_path | ForEach-Object { [string]$_ }) } else { @($reducerEngineProjection.merge_phase_path | ForEach-Object { [string]$_ }) }
    command_transition_log = @($commandTransitionLog)
    control_state_kind = $controlStateKind
    transition_kind = [string]$commandProjection.transition_kind
    update_keys = @($updateKeys)
    goto_target = [string]$commandProjection.goto_target
    graph_scope = [string]$commandProjection.graph_scope
    source_subgraph = [string]$commandProjection.source_subgraph
    target_subgraph = [string]$commandProjection.target_subgraph
    parent_handoff_target = [string]$commandProjection.parent_handoff_target
    resume_posture = [string]$commandProjection.resume_posture
    resume_payload_present = [bool]$commandProjection.resume_payload_present
    resume_payload_keys = @($resumePayloadKeys)
    superstep_count = if ($null -ne $engineState.PSObject.Properties['superstep_count']) { [int]$engineState.superstep_count } else { [int]$reducerEngineProjection.superstep_count }
    stop_boundary = if ($null -ne $engineState.PSObject.Properties['stop_boundary']) { [string]$engineState.stop_boundary } else { [string]$reducerEngineProjection.stop_boundary }
    terminal_reached = if ($null -ne $engineState.PSObject.Properties['terminal_reached']) { [bool]$engineState.terminal_reached } else { [bool]$reducerEngineProjection.terminal_reached }
    recursion_limit_supported = if ($null -ne $engineState.PSObject.Properties['recursion_limit_supported']) { [bool]$engineState.recursion_limit_supported } else { [bool]$reducerEngineProjection.recursion_limit_supported }
    remaining_steps_supported = if ($null -ne $engineState.PSObject.Properties['remaining_steps_supported']) { [bool]$engineState.remaining_steps_supported } else { [bool]$reducerEngineProjection.remaining_steps_supported }
    recursion_limit = if ($null -ne $engineState.PSObject.Properties['recursion_limit']) { [int]$engineState.recursion_limit } else { [int]$reducerEngineProjection.recursion_limit }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { [string]$reducerEngineProjection.execution_posture }
    last_run_kind = if ($null -ne $engineState.PSObject.Properties['last_run_kind']) { [string]$engineState.last_run_kind } else { [string]$reducerEngineProjection.last_run_kind }
    last_run_status = if ($null -ne $engineState.PSObject.Properties['last_run_status']) { [string]$engineState.last_run_status } else { [string]$reducerEngineProjection.last_run_status }
    last_run_reason = if ($null -ne $engineState.PSObject.Properties['last_run_reason']) { [string]$engineState.last_run_reason } else { [string]$reducerEngineProjection.last_run_reason }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphRuntimeAwareLivePrimaryEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('runtime_aware_live_primary_engine_state')) {
    $engineState = $ThreadRecord['runtime_aware_live_primary_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['runtime_aware_live_primary_engine_state']) {
    $engineState = $ThreadRecord.runtime_aware_live_primary_engine_state
  }

  $commandEngineProjection = Get-CodexUserLevelLangGraphCommandAwareLivePrimaryEngineProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId
  $runtimeProjection = Get-CodexUserLevelLangGraphRuntimeInjectionProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $runtimeStateKind = 'ordinary'
  if ([bool]$runtimeProjection.runtime_context_present -and [bool]$runtimeProjection.store_configured) {
    $runtimeStateKind = 'runtime_context_and_store_ready'
  } elseif ([bool]$runtimeProjection.runtime_context_present) {
    $runtimeStateKind = 'runtime_context_ready'
  } elseif ([bool]$runtimeProjection.store_configured -and [bool]$runtimeProjection.store_access_expected) {
    $runtimeStateKind = 'store_ready'
  } elseif ([bool]$runtimeProjection.store_configured) {
    $runtimeStateKind = 'store_configured'
  }

  $runtimeTransitionLog = @($commandEngineProjection.command_transition_log | ForEach-Object { [string]$_ })
  if (-not [string]::IsNullOrWhiteSpace([string]$runtimeProjection.context_schema)) {
    $runtimeTransitionLog += ('context_schema:{0}' -f ([string]$runtimeProjection.context_schema))
  }
  $runtimeContextKeys = @($runtimeProjection.runtime_context_keys | ForEach-Object { [string]$_ })
  if ([bool]$runtimeProjection.runtime_context_present) {
    $runtimeTransitionLog += ('runtime_context_keys:{0}' -f $runtimeContextKeys.Count)
  }
  $runtimeContextKindHints = @($runtimeProjection.runtime_context_kind_hints | ForEach-Object { [string]$_ })
  if ($runtimeContextKindHints.Count -gt 0) {
    $runtimeTransitionLog += ('runtime_hints:{0}' -f $runtimeContextKindHints.Count)
  }
  if ([bool]$runtimeProjection.store_configured) {
    $storeMarker = if (-not [string]::IsNullOrWhiteSpace([string]$runtimeProjection.store_kind)) { [string]$runtimeProjection.store_kind } else { 'configured' }
    $runtimeTransitionLog += ('store:{0}' -f $storeMarker)
  }
  if ([bool]$runtimeProjection.store_access_expected) {
    $runtimeTransitionLog += 'store_access:expected'
  }
  $runtimeTransitionLog = @(
    $runtimeTransitionLog |
      Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } |
      Select-Object -Unique
  )

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-runtime-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'runtime_aware_live_stategraph_primary_execution_engine'
        engine_id = 'codex_user_level_runtime_aware_live_primary_execution_engine'
        graph_api_surface = 'StateGraph'
        execute_surface = 'CompiledGraph.invoke/stream'
        runtime_surface = 'runtime_context_and_context_schema_state'
        store_surface = 'injected_store_configuration_state'
      }
      compile_supported = [bool]$commandEngineProjection.compile_supported
      compiled_graph_present = [bool]$commandEngineProjection.compiled_graph_present
      invoke_supported = [bool]$commandEngineProjection.invoke_supported
      stream_supported = [bool]$commandEngineProjection.stream_supported
      current_execution_node = [string]$commandEngineProjection.current_execution_node
      mapped_phase = [string]$commandEngineProjection.mapped_phase
      runtime_node_path = @($commandEngineProjection.command_node_path | ForEach-Object { [string]$_ })
      runtime_phase_path = @($commandEngineProjection.command_phase_path | ForEach-Object { [string]$_ })
      runtime_transition_log = @($runtimeTransitionLog)
      runtime_state_kind = $runtimeStateKind
      context_schema = [string]$runtimeProjection.context_schema
      runtime_context_present = [bool]$runtimeProjection.runtime_context_present
      runtime_context_keys = @($runtimeContextKeys)
      runtime_context_kind_hints = @($runtimeContextKindHints)
      store_configured = [bool]$runtimeProjection.store_configured
      store_access_expected = [bool]$runtimeProjection.store_access_expected
      store_kind = [string]$runtimeProjection.store_kind
      superstep_count = [int]$commandEngineProjection.superstep_count
      stop_boundary = [string]$commandEngineProjection.stop_boundary
      terminal_reached = [bool]$commandEngineProjection.terminal_reached
      recursion_limit_supported = [bool]$commandEngineProjection.recursion_limit_supported
      remaining_steps_supported = [bool]$commandEngineProjection.remaining_steps_supported
      recursion_limit = [int]$commandEngineProjection.recursion_limit
      execution_posture = [string]$commandEngineProjection.execution_posture
      last_run_kind = [string]$commandEngineProjection.last_run_kind
      last_run_status = [string]$commandEngineProjection.last_run_status
      last_run_reason = [string]$commandEngineProjection.last_run_reason
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { [bool]$commandEngineProjection.compile_supported }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { [bool]$commandEngineProjection.compiled_graph_present }
    invoke_supported = if ($null -ne $engineState.PSObject.Properties['invoke_supported']) { [bool]$engineState.invoke_supported } else { [bool]$commandEngineProjection.invoke_supported }
    stream_supported = if ($null -ne $engineState.PSObject.Properties['stream_supported']) { [bool]$engineState.stream_supported } else { [bool]$commandEngineProjection.stream_supported }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$commandEngineProjection.current_execution_node }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$commandEngineProjection.mapped_phase }
    runtime_node_path = if ($null -ne $engineState.PSObject.Properties['runtime_node_path'] -and $null -ne $engineState.runtime_node_path) { @($engineState.runtime_node_path | ForEach-Object { [string]$_ }) } else { @($commandEngineProjection.command_node_path | ForEach-Object { [string]$_ }) }
    runtime_phase_path = if ($null -ne $engineState.PSObject.Properties['runtime_phase_path'] -and $null -ne $engineState.runtime_phase_path) { @($engineState.runtime_phase_path | ForEach-Object { [string]$_ }) } else { @($commandEngineProjection.command_phase_path | ForEach-Object { [string]$_ }) }
    runtime_transition_log = @($runtimeTransitionLog)
    runtime_state_kind = $runtimeStateKind
    context_schema = [string]$runtimeProjection.context_schema
    runtime_context_present = [bool]$runtimeProjection.runtime_context_present
    runtime_context_keys = @($runtimeContextKeys)
    runtime_context_kind_hints = @($runtimeContextKindHints)
    store_configured = [bool]$runtimeProjection.store_configured
    store_access_expected = [bool]$runtimeProjection.store_access_expected
    store_kind = [string]$runtimeProjection.store_kind
    superstep_count = if ($null -ne $engineState.PSObject.Properties['superstep_count']) { [int]$engineState.superstep_count } else { [int]$commandEngineProjection.superstep_count }
    stop_boundary = if ($null -ne $engineState.PSObject.Properties['stop_boundary']) { [string]$engineState.stop_boundary } else { [string]$commandEngineProjection.stop_boundary }
    terminal_reached = if ($null -ne $engineState.PSObject.Properties['terminal_reached']) { [bool]$engineState.terminal_reached } else { [bool]$commandEngineProjection.terminal_reached }
    recursion_limit_supported = if ($null -ne $engineState.PSObject.Properties['recursion_limit_supported']) { [bool]$engineState.recursion_limit_supported } else { [bool]$commandEngineProjection.recursion_limit_supported }
    remaining_steps_supported = if ($null -ne $engineState.PSObject.Properties['remaining_steps_supported']) { [bool]$engineState.remaining_steps_supported } else { [bool]$commandEngineProjection.remaining_steps_supported }
    recursion_limit = if ($null -ne $engineState.PSObject.Properties['recursion_limit']) { [int]$engineState.recursion_limit } else { [int]$commandEngineProjection.recursion_limit }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { [string]$commandEngineProjection.execution_posture }
    last_run_kind = if ($null -ne $engineState.PSObject.Properties['last_run_kind']) { [string]$engineState.last_run_kind } else { [string]$commandEngineProjection.last_run_kind }
    last_run_status = if ($null -ne $engineState.PSObject.Properties['last_run_status']) { [string]$engineState.last_run_status } else { [string]$commandEngineProjection.last_run_status }
    last_run_reason = if ($null -ne $engineState.PSObject.Properties['last_run_reason']) { [string]$engineState.last_run_reason } else { [string]$commandEngineProjection.last_run_reason }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphMemoryAwareLivePrimaryEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('memory_aware_live_primary_engine_state')) {
    $engineState = $ThreadRecord['memory_aware_live_primary_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['memory_aware_live_primary_engine_state']) {
    $engineState = $ThreadRecord.memory_aware_live_primary_engine_state
  }

  $runtimeEngineProjection = Get-CodexUserLevelLangGraphRuntimeAwareLivePrimaryEngineProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId
  $memoryProjection = Get-CodexUserLevelLangGraphMemoryProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $memoryStateKind = 'ordinary'
  if ([bool]$memoryProjection.memory_store_configured -and [bool]$memoryProjection.semantic_memory_enabled) {
    $memoryStateKind = 'memory_and_semantic_ready'
  } elseif ([bool]$memoryProjection.semantic_memory_enabled) {
    $memoryStateKind = 'semantic_memory_ready'
  } elseif ([bool]$memoryProjection.memory_store_configured) {
    $memoryStateKind = 'memory_store_ready'
  }

  $memoryTransitionLog = @($runtimeEngineProjection.runtime_transition_log | ForEach-Object { [string]$_ })
  $memoryNamespaces = @($memoryProjection.memory_namespaces | ForEach-Object { [string]$_ })
  $semanticNamespaces = @($memoryProjection.semantic_namespaces | ForEach-Object { [string]$_ })
  if ([bool]$memoryProjection.memory_store_configured) {
    $memoryTransitionLog += ('memory_store:{0}' -f ([string]$memoryProjection.memory_store_kind))
  }
  if ($memoryNamespaces.Count -gt 0) {
    $memoryTransitionLog += ('memory_namespaces:{0}' -f $memoryNamespaces.Count)
  }
  if ([bool]$memoryProjection.semantic_memory_enabled) {
    $memoryTransitionLog += ('semantic_store:{0}' -f ([string]$memoryProjection.semantic_store_kind))
  }
  if ($semanticNamespaces.Count -gt 0) {
    $memoryTransitionLog += ('semantic_namespaces:{0}' -f $semanticNamespaces.Count)
  }
  $memoryTransitionLog = @(
    $memoryTransitionLog |
      Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } |
      Select-Object -Unique
  )

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-memory-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'memory_aware_live_stategraph_primary_execution_engine'
        engine_id = 'codex_user_level_memory_aware_live_primary_execution_engine'
        graph_api_surface = 'StateGraph'
        execute_surface = 'CompiledGraph.invoke/stream'
        memory_surface = 'memory_store_and_namespace_state'
        semantic_surface = 'semantic_memory_enablement_and_store_state'
      }
      compile_supported = [bool]$runtimeEngineProjection.compile_supported
      compiled_graph_present = [bool]$runtimeEngineProjection.compiled_graph_present
      invoke_supported = [bool]$runtimeEngineProjection.invoke_supported
      stream_supported = [bool]$runtimeEngineProjection.stream_supported
      current_execution_node = [string]$runtimeEngineProjection.current_execution_node
      mapped_phase = [string]$runtimeEngineProjection.mapped_phase
      memory_node_path = @($runtimeEngineProjection.runtime_node_path | ForEach-Object { [string]$_ })
      memory_phase_path = @($runtimeEngineProjection.runtime_phase_path | ForEach-Object { [string]$_ })
      memory_transition_log = @($memoryTransitionLog)
      memory_state_kind = $memoryStateKind
      memory_store_configured = [bool]$memoryProjection.memory_store_configured
      memory_store_kind = [string]$memoryProjection.memory_store_kind
      memory_namespaces = @($memoryNamespaces)
      semantic_memory_enabled = [bool]$memoryProjection.semantic_memory_enabled
      semantic_store_kind = [string]$memoryProjection.semantic_store_kind
      semantic_namespaces = @($semanticNamespaces)
      superstep_count = [int]$runtimeEngineProjection.superstep_count
      stop_boundary = [string]$runtimeEngineProjection.stop_boundary
      terminal_reached = [bool]$runtimeEngineProjection.terminal_reached
      recursion_limit_supported = [bool]$runtimeEngineProjection.recursion_limit_supported
      remaining_steps_supported = [bool]$runtimeEngineProjection.remaining_steps_supported
      recursion_limit = [int]$runtimeEngineProjection.recursion_limit
      execution_posture = [string]$runtimeEngineProjection.execution_posture
      last_run_kind = [string]$runtimeEngineProjection.last_run_kind
      last_run_status = [string]$runtimeEngineProjection.last_run_status
      last_run_reason = [string]$runtimeEngineProjection.last_run_reason
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { [bool]$runtimeEngineProjection.compile_supported }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { [bool]$runtimeEngineProjection.compiled_graph_present }
    invoke_supported = if ($null -ne $engineState.PSObject.Properties['invoke_supported']) { [bool]$engineState.invoke_supported } else { [bool]$runtimeEngineProjection.invoke_supported }
    stream_supported = if ($null -ne $engineState.PSObject.Properties['stream_supported']) { [bool]$engineState.stream_supported } else { [bool]$runtimeEngineProjection.stream_supported }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$runtimeEngineProjection.current_execution_node }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$runtimeEngineProjection.mapped_phase }
    memory_node_path = if ($null -ne $engineState.PSObject.Properties['memory_node_path'] -and $null -ne $engineState.memory_node_path) { @($engineState.memory_node_path | ForEach-Object { [string]$_ }) } else { @($runtimeEngineProjection.runtime_node_path | ForEach-Object { [string]$_ }) }
    memory_phase_path = if ($null -ne $engineState.PSObject.Properties['memory_phase_path'] -and $null -ne $engineState.memory_phase_path) { @($engineState.memory_phase_path | ForEach-Object { [string]$_ }) } else { @($runtimeEngineProjection.runtime_phase_path | ForEach-Object { [string]$_ }) }
    memory_transition_log = @($memoryTransitionLog)
    memory_state_kind = $memoryStateKind
    memory_store_configured = [bool]$memoryProjection.memory_store_configured
    memory_store_kind = [string]$memoryProjection.memory_store_kind
    memory_namespaces = @($memoryNamespaces)
    semantic_memory_enabled = [bool]$memoryProjection.semantic_memory_enabled
    semantic_store_kind = [string]$memoryProjection.semantic_store_kind
    semantic_namespaces = @($semanticNamespaces)
    superstep_count = if ($null -ne $engineState.PSObject.Properties['superstep_count']) { [int]$engineState.superstep_count } else { [int]$runtimeEngineProjection.superstep_count }
    stop_boundary = if ($null -ne $engineState.PSObject.Properties['stop_boundary']) { [string]$engineState.stop_boundary } else { [string]$runtimeEngineProjection.stop_boundary }
    terminal_reached = if ($null -ne $engineState.PSObject.Properties['terminal_reached']) { [bool]$engineState.terminal_reached } else { [bool]$runtimeEngineProjection.terminal_reached }
    recursion_limit_supported = if ($null -ne $engineState.PSObject.Properties['recursion_limit_supported']) { [bool]$engineState.recursion_limit_supported } else { [bool]$runtimeEngineProjection.recursion_limit_supported }
    remaining_steps_supported = if ($null -ne $engineState.PSObject.Properties['remaining_steps_supported']) { [bool]$engineState.remaining_steps_supported } else { [bool]$runtimeEngineProjection.remaining_steps_supported }
    recursion_limit = if ($null -ne $engineState.PSObject.Properties['recursion_limit']) { [int]$engineState.recursion_limit } else { [int]$runtimeEngineProjection.recursion_limit }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { [string]$runtimeEngineProjection.execution_posture }
    last_run_kind = if ($null -ne $engineState.PSObject.Properties['last_run_kind']) { [string]$engineState.last_run_kind } else { [string]$runtimeEngineProjection.last_run_kind }
    last_run_status = if ($null -ne $engineState.PSObject.Properties['last_run_status']) { [string]$engineState.last_run_status } else { [string]$runtimeEngineProjection.last_run_status }
    last_run_reason = if ($null -ne $engineState.PSObject.Properties['last_run_reason']) { [string]$engineState.last_run_reason } else { [string]$runtimeEngineProjection.last_run_reason }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphMigrationAwareLivePrimaryEngineProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $engineState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('migration_aware_live_primary_engine_state')) {
    $engineState = $ThreadRecord['migration_aware_live_primary_engine_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['migration_aware_live_primary_engine_state']) {
    $engineState = $ThreadRecord.migration_aware_live_primary_engine_state
  }

  $memoryEngineProjection = Get-CodexUserLevelLangGraphMemoryAwareLivePrimaryEngineProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId
  $migrationProjection = Get-CodexUserLevelLangGraphMigrationProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId

  $compatibilityStateKind = 'ordinary'
  if ([string]$migrationProjection.compatibility -eq 'incompatible') {
    $compatibilityStateKind = 'incompatible_thread'
  } elseif ([string]$migrationProjection.compatibility -eq 'degraded_compatible') {
    $compatibilityStateKind = 'degraded_compatible_thread'
  } elseif ([string]$migrationProjection.compatibility -eq 'migration_safe') {
    $compatibilityStateKind = 'migration_safe_thread'
  }

  $compatibilityTransitionLog = @($memoryEngineProjection.memory_transition_log | ForEach-Object { [string]$_ })
  if (-not [string]::IsNullOrWhiteSpace([string]$migrationProjection.compatibility)) {
    $compatibilityTransitionLog += ('compatibility:{0}' -f ([string]$migrationProjection.compatibility))
  }
  if (-not [string]::IsNullOrWhiteSpace([string]$migrationProjection.topology_compatibility)) {
    $compatibilityTransitionLog += ('topology:{0}' -f ([string]$migrationProjection.topology_compatibility))
  }
  if (-not [string]::IsNullOrWhiteSpace([string]$migrationProjection.state_schema_compatibility)) {
    $compatibilityTransitionLog += ('state_schema:{0}' -f ([string]$migrationProjection.state_schema_compatibility))
  }
  $currentGraphContract = if ($null -ne $migrationProjection.current_graph_contract) { $migrationProjection.current_graph_contract } else { [ordered]@{} }
  $threadGraphContract = if ($null -ne $migrationProjection.thread_graph_contract) { $migrationProjection.thread_graph_contract } else { [ordered]@{} }
  if ($null -ne $currentGraphContract.PSObject.Properties['graph_contract_id'] -and -not [string]::IsNullOrWhiteSpace([string]$currentGraphContract.graph_contract_id)) {
    $compatibilityTransitionLog += ('current_graph:{0}' -f ([string]$currentGraphContract.graph_contract_id))
  }
  if ($null -ne $threadGraphContract.PSObject.Properties['graph_contract_id'] -and -not [string]::IsNullOrWhiteSpace([string]$threadGraphContract.graph_contract_id)) {
    $compatibilityTransitionLog += ('thread_graph:{0}' -f ([string]$threadGraphContract.graph_contract_id))
  }
  $reasonCodes = @($migrationProjection.reason_codes | ForEach-Object { [string]$_ })
  if ($reasonCodes.Count -gt 0) {
    $compatibilityTransitionLog += ('reasons:{0}' -f $reasonCodes.Count)
  }
  $compatibilityTransitionLog = @(
    $compatibilityTransitionLog |
      Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } |
      Select-Object -Unique
  )

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-migration-engine.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $engineState) {
    return [ordered]@{
      engine_identity = [ordered]@{
        engine_kind = 'migration_aware_live_stategraph_primary_execution_engine'
        engine_id = 'codex_user_level_migration_aware_live_primary_execution_engine'
        graph_api_surface = 'StateGraph'
        execute_surface = 'CompiledGraph.invoke/stream'
        migration_surface = 'graph_contract_and_thread_compatibility_state'
        compatibility_surface = 'topology_state_schema_and_reason_codes'
      }
      compile_supported = [bool]$memoryEngineProjection.compile_supported
      compiled_graph_present = [bool]$memoryEngineProjection.compiled_graph_present
      invoke_supported = [bool]$memoryEngineProjection.invoke_supported
      stream_supported = [bool]$memoryEngineProjection.stream_supported
      current_execution_node = [string]$memoryEngineProjection.current_execution_node
      mapped_phase = [string]$memoryEngineProjection.mapped_phase
      compatibility_node_path = @($memoryEngineProjection.memory_node_path | ForEach-Object { [string]$_ })
      compatibility_phase_path = @($memoryEngineProjection.memory_phase_path | ForEach-Object { [string]$_ })
      compatibility_transition_log = @($compatibilityTransitionLog)
      compatibility_state_kind = $compatibilityStateKind
      current_graph_contract = $currentGraphContract
      thread_graph_contract = $threadGraphContract
      topology_compatibility = [string]$migrationProjection.topology_compatibility
      state_schema_compatibility = [string]$migrationProjection.state_schema_compatibility
      compatibility = [string]$migrationProjection.compatibility
      reason_codes = @($reasonCodes)
      superstep_count = [int]$memoryEngineProjection.superstep_count
      stop_boundary = [string]$memoryEngineProjection.stop_boundary
      terminal_reached = [bool]$memoryEngineProjection.terminal_reached
      recursion_limit_supported = [bool]$memoryEngineProjection.recursion_limit_supported
      remaining_steps_supported = [bool]$memoryEngineProjection.remaining_steps_supported
      recursion_limit = [int]$memoryEngineProjection.recursion_limit
      execution_posture = [string]$memoryEngineProjection.execution_posture
      last_run_kind = [string]$memoryEngineProjection.last_run_kind
      last_run_status = [string]$memoryEngineProjection.last_run_status
      last_run_reason = [string]$memoryEngineProjection.last_run_reason
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    engine_identity = if ($null -ne $engineState.PSObject.Properties['engine_identity']) { $engineState.engine_identity } else { [ordered]@{} }
    compile_supported = if ($null -ne $engineState.PSObject.Properties['compile_supported']) { [bool]$engineState.compile_supported } else { [bool]$memoryEngineProjection.compile_supported }
    compiled_graph_present = if ($null -ne $engineState.PSObject.Properties['compiled_graph_present']) { [bool]$engineState.compiled_graph_present } else { [bool]$memoryEngineProjection.compiled_graph_present }
    invoke_supported = if ($null -ne $engineState.PSObject.Properties['invoke_supported']) { [bool]$engineState.invoke_supported } else { [bool]$memoryEngineProjection.invoke_supported }
    stream_supported = if ($null -ne $engineState.PSObject.Properties['stream_supported']) { [bool]$engineState.stream_supported } else { [bool]$memoryEngineProjection.stream_supported }
    current_execution_node = if ($null -ne $engineState.PSObject.Properties['current_execution_node']) { [string]$engineState.current_execution_node } else { [string]$memoryEngineProjection.current_execution_node }
    mapped_phase = if ($null -ne $engineState.PSObject.Properties['mapped_phase']) { [string]$engineState.mapped_phase } else { [string]$memoryEngineProjection.mapped_phase }
    compatibility_node_path = if ($null -ne $engineState.PSObject.Properties['compatibility_node_path'] -and $null -ne $engineState.compatibility_node_path) { @($engineState.compatibility_node_path | ForEach-Object { [string]$_ }) } else { @($memoryEngineProjection.memory_node_path | ForEach-Object { [string]$_ }) }
    compatibility_phase_path = if ($null -ne $engineState.PSObject.Properties['compatibility_phase_path'] -and $null -ne $engineState.compatibility_phase_path) { @($engineState.compatibility_phase_path | ForEach-Object { [string]$_ }) } else { @($memoryEngineProjection.memory_phase_path | ForEach-Object { [string]$_ }) }
    compatibility_transition_log = @($compatibilityTransitionLog)
    compatibility_state_kind = $compatibilityStateKind
    current_graph_contract = $currentGraphContract
    thread_graph_contract = $threadGraphContract
    topology_compatibility = [string]$migrationProjection.topology_compatibility
    state_schema_compatibility = [string]$migrationProjection.state_schema_compatibility
    compatibility = [string]$migrationProjection.compatibility
    reason_codes = @($reasonCodes)
    superstep_count = if ($null -ne $engineState.PSObject.Properties['superstep_count']) { [int]$engineState.superstep_count } else { [int]$memoryEngineProjection.superstep_count }
    stop_boundary = if ($null -ne $engineState.PSObject.Properties['stop_boundary']) { [string]$engineState.stop_boundary } else { [string]$memoryEngineProjection.stop_boundary }
    terminal_reached = if ($null -ne $engineState.PSObject.Properties['terminal_reached']) { [bool]$engineState.terminal_reached } else { [bool]$memoryEngineProjection.terminal_reached }
    recursion_limit_supported = if ($null -ne $engineState.PSObject.Properties['recursion_limit_supported']) { [bool]$engineState.recursion_limit_supported } else { [bool]$memoryEngineProjection.recursion_limit_supported }
    remaining_steps_supported = if ($null -ne $engineState.PSObject.Properties['remaining_steps_supported']) { [bool]$engineState.remaining_steps_supported } else { [bool]$memoryEngineProjection.remaining_steps_supported }
    recursion_limit = if ($null -ne $engineState.PSObject.Properties['recursion_limit']) { [int]$engineState.recursion_limit } else { [int]$memoryEngineProjection.recursion_limit }
    execution_posture = if ($null -ne $engineState.PSObject.Properties['execution_posture']) { [string]$engineState.execution_posture } else { [string]$memoryEngineProjection.execution_posture }
    last_run_kind = if ($null -ne $engineState.PSObject.Properties['last_run_kind']) { [string]$engineState.last_run_kind } else { [string]$memoryEngineProjection.last_run_kind }
    last_run_status = if ($null -ne $engineState.PSObject.Properties['last_run_status']) { [string]$engineState.last_run_status } else { [string]$memoryEngineProjection.last_run_status }
    last_run_reason = if ($null -ne $engineState.PSObject.Properties['last_run_reason']) { [string]$engineState.last_run_reason } else { [string]$memoryEngineProjection.last_run_reason }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphAutomaticRuntimePolicyProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $policyState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('automatic_runtime_policy_state')) {
    $policyState = $ThreadRecord['automatic_runtime_policy_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['automatic_runtime_policy_state']) {
    $policyState = $ThreadRecord.automatic_runtime_policy_state
  }

  $migrationProjection = Get-CodexUserLevelLangGraphMigrationProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId
  $approvalQueueProjection = Get-CodexUserLevelLangGraphApprovalQueueProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -InterruptRecord $null -ThreadId $ThreadId
  $migrationReasonCodes = @($migrationProjection.reason_codes | ForEach-Object { [string]$_ })
  $automaticActions = @()
  $migrationPosture = 'manual_only'
  if ([string]$migrationProjection.compatibility -eq 'migration_safe') {
    $migrationPosture = 'auto_continue_safe'
    $automaticActions += 'continue_on_migration_safe'
  } elseif (
    [string]$migrationProjection.compatibility -eq 'degraded_compatible' -and
    (@($migrationReasonCodes | Where-Object { $_ -notin @('topology_version_missing', 'topology_minor_drift', 'state_schema_version_missing', 'state_schema_minor_drift') }).Count -eq 0)
  ) {
    $migrationPosture = 'auto_continue_with_notice'
    $automaticActions += 'continue_on_degraded_compatible'
  } elseif ([string]$migrationProjection.compatibility -eq 'incompatible' -or $migrationReasonCodes -contains 'graph_contract_id_mismatch') {
    $migrationPosture = 'manual_recovery_required'
  }

  $recoveryPosture = if ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['recovery_state'] -and $null -ne $ThreadRecord.recovery_state -and $null -ne $ThreadRecord.recovery_state.PSObject.Properties['posture']) { [string]$ThreadRecord.recovery_state.posture } else { 'ordinary' }
  $recoveryPolicyPosture = 'ordinary'
  if ($recoveryPosture -eq 'recovered_pending_resume' -and [int]$approvalQueueProjection.pending_count -eq 0) {
    if ($migrationPosture -in @('auto_continue_safe', 'auto_continue_with_notice')) {
      $recoveryPolicyPosture = 'auto_continue_safe'
      $automaticActions += 'continue_after_safe_recovery'
    } else {
      $recoveryPolicyPosture = 'manual_recovery_required'
    }
  }

  $threadStatus = if ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['status']) { [string]$ThreadRecord.status } else { '' }
  $stopReason = if ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['stop_reason']) { [string]$ThreadRecord.stop_reason } else { '' }
  $approvalPosture = 'no_queue_work'
  if ([int]$approvalQueueProjection.pending_count -gt 0) {
    $approvalPosture = 'waiting_for_manual_approval'
  } elseif ([int]$approvalQueueProjection.resolved_count -gt 0 -and ($threadStatus -eq 'waiting_for_approval' -or $stopReason -eq 'needs_human')) {
    $approvalPosture = 'auto_resume_safe'
    $automaticActions += 'resume_after_resolved_queue'
  } elseif ([int]$approvalQueueProjection.pending_count -eq 0 -and [int]$approvalQueueProjection.resolved_count -eq 0 -and $threadStatus -ne 'waiting_for_approval') {
    $approvalPosture = 'auto_clear_stale_interrupt'
    $automaticActions += 'clear_stale_interrupt'
  } elseif ([int]$approvalQueueProjection.resolved_count -gt 0) {
    $approvalPosture = 'resolved_queue_retained'
  }

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-auto-policy.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $policyState) {
    return [ordered]@{
      policy_identity = [ordered]@{
        policy_kind = 'bounded_langgraph_runtime_policy'
        policy_id = 'codex_user_level_langgraph_runtime_policy'
        manual_first_default = $true
      }
      migration_policy_posture = $migrationPosture
      approval_policy_posture = $approvalPosture
      recovery_policy_posture = $recoveryPolicyPosture
      automatic_actions_available = @($automaticActions | Sort-Object -Unique)
      safe_to_auto_apply = (@($automaticActions | Where-Object { $_ -in @('resume_after_resolved_queue', 'continue_after_safe_recovery', 'clear_stale_interrupt') }).Count -gt 0)
      last_auto_action = ''
      last_auto_reason = ''
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    policy_identity = if ($null -ne $policyState.PSObject.Properties['policy_identity']) { $policyState.policy_identity } else { [ordered]@{} }
    migration_policy_posture = if ($null -ne $policyState.PSObject.Properties['migration_policy_posture']) { [string]$policyState.migration_policy_posture } else { $migrationPosture }
    approval_policy_posture = if ($null -ne $policyState.PSObject.Properties['approval_policy_posture']) { [string]$policyState.approval_policy_posture } else { $approvalPosture }
    recovery_policy_posture = if ($null -ne $policyState.PSObject.Properties['recovery_policy_posture']) { [string]$policyState.recovery_policy_posture } else { $recoveryPolicyPosture }
    automatic_actions_available = if ($null -ne $policyState.PSObject.Properties['automatic_actions_available'] -and $null -ne $policyState.automatic_actions_available) { @($policyState.automatic_actions_available | ForEach-Object { [string]$_ } | Sort-Object -Unique) } else { @($automaticActions | Sort-Object -Unique) }
    safe_to_auto_apply = if ($null -ne $policyState.PSObject.Properties['safe_to_auto_apply']) { [bool]$policyState.safe_to_auto_apply } else { (@($automaticActions | Where-Object { $_ -in @('resume_after_resolved_queue', 'continue_after_safe_recovery', 'clear_stale_interrupt') }).Count -gt 0) }
    last_auto_action = if ($null -ne $policyState.PSObject.Properties['last_auto_action']) { [string]$policyState.last_auto_action } else { '' }
    last_auto_reason = if ($null -ne $policyState.PSObject.Properties['last_auto_reason']) { [string]$policyState.last_auto_reason } else { '' }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphApprovalQueueProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [object]$InterruptRecord,
    [string]$ThreadId
  )

  $queueState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('approval_queue_state')) {
    $queueState = $ThreadRecord['approval_queue_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['approval_queue_state']) {
    $queueState = $ThreadRecord.approval_queue_state
  } elseif ($InterruptRecord -is [System.Collections.IDictionary] -and $InterruptRecord.Contains('approval_queue_state')) {
    $queueState = $InterruptRecord['approval_queue_state']
  } elseif ($null -ne $InterruptRecord -and $null -ne $InterruptRecord.PSObject.Properties['approval_queue_state']) {
    $queueState = $InterruptRecord.approval_queue_state
  }

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-approval-queue.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $queueState) {
    return [ordered]@{
      queue_posture = 'no_interrupts'
      queue_size = 0
      pending_count = 0
      resolved_count = 0
      pending_interrupt_ids = @()
      resolved_interrupt_ids = @()
      current_interrupt_id = ''
      resume_map_keys = @()
      queue_items = @()
      helper_pointer = $helperPointer
    }
  }

  $queueItems = if ($null -ne $queueState.PSObject.Properties['queue_items'] -and $null -ne $queueState.queue_items) { @($queueState.queue_items) } else { @() }
  $resumeMapKeys = @()
  if ($null -ne $queueState.PSObject.Properties['resume_map'] -and $null -ne $queueState.resume_map) {
    if ($queueState.resume_map -is [System.Collections.IDictionary]) {
      $resumeMapKeys = @($queueState.resume_map.Keys | ForEach-Object { [string]$_ } | Sort-Object)
    } else {
      $resumeMapKeys = @($queueState.resume_map.PSObject.Properties | ForEach-Object { [string]$_.Name } | Sort-Object)
    }
  }

  $boundedItems = @()
  $pendingInterruptIds = @()
  $resolvedInterruptIds = @()
  foreach ($item in @($queueItems | Sort-Object { if ($null -ne $_.PSObject.Properties['order']) { [int]$_.order } else { 0 } })) {
    $interruptId = if ($null -ne $item.PSObject.Properties['interrupt_id']) { [string]$item.interrupt_id } else { '' }
    $status = if ($null -ne $item.PSObject.Properties['status']) { [string]$item.status } else { '' }
    if ($status -eq 'pending') {
      $pendingInterruptIds += $interruptId
    } elseif ($status -eq 'resolved') {
      $resolvedInterruptIds += $interruptId
    }
    $boundedItems += [ordered]@{
      interrupt_id = $interruptId
      order = if ($null -ne $item.PSObject.Properties['order']) { [int]$item.order } else { 0 }
      interrupt_point = if ($null -ne $item.PSObject.Properties['interrupt_point']) { [string]$item.interrupt_point } else { '' }
      value_summary = if ($null -ne $item.PSObject.Properties['value_summary']) { [string]$item.value_summary } else { '' }
      reason = if ($null -ne $item.PSObject.Properties['reason']) { [string]$item.reason } else { '' }
      status = $status
      resume_value_present = if ($null -ne $item.PSObject.Properties['resume_value_present']) { [bool]$item.resume_value_present } else { $false }
      resume_value_keys = if ($null -ne $item.PSObject.Properties['resume_value_keys'] -and $null -ne $item.resume_value_keys) { @($item.resume_value_keys | ForEach-Object { [string]$_ } | Sort-Object) } else { @() }
    }
  }

  return [ordered]@{
    queue_posture = if ($null -ne $queueState.PSObject.Properties['queue_posture']) { [string]$queueState.queue_posture } else { 'no_interrupts' }
    queue_size = @($boundedItems).Count
    pending_count = @($pendingInterruptIds).Count
    resolved_count = @($resolvedInterruptIds).Count
    pending_interrupt_ids = $pendingInterruptIds
    resolved_interrupt_ids = $resolvedInterruptIds
    current_interrupt_id = if ($null -ne $queueState.PSObject.Properties['current_interrupt_id']) { [string]$queueState.current_interrupt_id } else { '' }
    resume_map_keys = $resumeMapKeys
    queue_items = $boundedItems
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphStreamProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $streamState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('stream_state')) {
    $streamState = $ThreadRecord['stream_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['stream_state']) {
    $streamState = $ThreadRecord.stream_state
  }

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-stream.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $streamState) {
    return [ordered]@{
      selected_modes = @()
      subgraphs = $false
      latest_event_kind = ''
      latest_namespace = @()
      latest_checkpoint_kind = ''
      latest_task_path = ''
      latest_task_status = ''
      latest_debug_summary = ''
      event_count = 0
      helper_pointer = $helperPointer
    }
  }

  $selectedModes = if ($null -ne $streamState.PSObject.Properties['selected_modes'] -and $null -ne $streamState.selected_modes) { @($streamState.selected_modes | ForEach-Object { [string]$_ }) } else { @() }
  $latestNamespace = if ($null -ne $streamState.PSObject.Properties['latest_namespace'] -and $null -ne $streamState.latest_namespace) { @($streamState.latest_namespace | ForEach-Object { [string]$_ }) } else { @() }

  return [ordered]@{
    selected_modes = @($selectedModes | Sort-Object)
    subgraphs = if ($null -ne $streamState.PSObject.Properties['subgraphs']) { [bool]$streamState.subgraphs } else { $false }
    latest_event_kind = if ($null -ne $streamState.PSObject.Properties['latest_event_kind']) { [string]$streamState.latest_event_kind } else { '' }
    latest_namespace = @($latestNamespace)
    latest_checkpoint_kind = if ($null -ne $streamState.PSObject.Properties['latest_checkpoint_kind']) { [string]$streamState.latest_checkpoint_kind } else { '' }
    latest_task_path = if ($null -ne $streamState.PSObject.Properties['latest_task_path']) { [string]$streamState.latest_task_path } else { '' }
    latest_task_status = if ($null -ne $streamState.PSObject.Properties['latest_task_status']) { [string]$streamState.latest_task_status } else { '' }
    latest_debug_summary = if ($null -ne $streamState.PSObject.Properties['latest_debug_summary']) { [string]$streamState.latest_debug_summary } else { '' }
    event_count = if ($null -ne $streamState.PSObject.Properties['event_count']) { [int]$streamState.event_count } else { 0 }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphRuntimeInjectionProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $runtimeState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('runtime_injection_state')) {
    $runtimeState = $ThreadRecord['runtime_injection_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['runtime_injection_state']) {
    $runtimeState = $ThreadRecord.runtime_injection_state
  }

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-runtime.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $runtimeState) {
    return [ordered]@{
      context_schema = ''
      runtime_context_present = $false
      runtime_context_keys = @()
      runtime_context_kind_hints = @()
      store_configured = $false
      store_access_expected = $false
      store_kind = ''
      helper_pointer = $helperPointer
    }
  }

  $runtimeContextKeys = if ($null -ne $runtimeState.PSObject.Properties['runtime_context_keys'] -and $null -ne $runtimeState.runtime_context_keys) { @($runtimeState.runtime_context_keys | ForEach-Object { [string]$_ }) } else { @() }
  $runtimeContextKindHints = if ($null -ne $runtimeState.PSObject.Properties['runtime_context_kind_hints'] -and $null -ne $runtimeState.runtime_context_kind_hints) { @($runtimeState.runtime_context_kind_hints | ForEach-Object { [string]$_ }) } else { @() }

  return [ordered]@{
    context_schema = if ($null -ne $runtimeState.PSObject.Properties['context_schema']) { [string]$runtimeState.context_schema } else { '' }
    runtime_context_present = if ($null -ne $runtimeState.PSObject.Properties['runtime_context_present']) { [bool]$runtimeState.runtime_context_present } else { $false }
    runtime_context_keys = @($runtimeContextKeys | Sort-Object)
    runtime_context_kind_hints = @($runtimeContextKindHints | Sort-Object)
    store_configured = if ($null -ne $runtimeState.PSObject.Properties['store_configured']) { [bool]$runtimeState.store_configured } else { $false }
    store_access_expected = if ($null -ne $runtimeState.PSObject.Properties['store_access_expected']) { [bool]$runtimeState.store_access_expected } else { $false }
    store_kind = if ($null -ne $runtimeState.PSObject.Properties['store_kind']) { [string]$runtimeState.store_kind } else { '' }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphMemoryProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $memoryState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('memory_state')) {
    $memoryState = $ThreadRecord['memory_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['memory_state']) {
    $memoryState = $ThreadRecord.memory_state
  }

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-memory.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $memoryState) {
    return [ordered]@{
      memory_store_configured = $false
      memory_store_kind = ''
      memory_namespaces = @()
      semantic_memory_enabled = $false
      semantic_store_kind = ''
      semantic_namespaces = @()
      helper_pointer = $helperPointer
    }
  }

  $memoryNamespaces = if ($null -ne $memoryState.PSObject.Properties['memory_namespaces'] -and $null -ne $memoryState.memory_namespaces) { @($memoryState.memory_namespaces | ForEach-Object { [string]$_ }) } else { @() }
  $semanticNamespaces = if ($null -ne $memoryState.PSObject.Properties['semantic_namespaces'] -and $null -ne $memoryState.semantic_namespaces) { @($memoryState.semantic_namespaces | ForEach-Object { [string]$_ }) } else { @() }

  return [ordered]@{
    memory_store_configured = if ($null -ne $memoryState.PSObject.Properties['memory_store_configured']) { [bool]$memoryState.memory_store_configured } else { $false }
    memory_store_kind = if ($null -ne $memoryState.PSObject.Properties['memory_store_kind']) { [string]$memoryState.memory_store_kind } else { '' }
    memory_namespaces = @($memoryNamespaces | Sort-Object)
    semantic_memory_enabled = if ($null -ne $memoryState.PSObject.Properties['semantic_memory_enabled']) { [bool]$memoryState.semantic_memory_enabled } else { $false }
    semantic_store_kind = if ($null -ne $memoryState.PSObject.Properties['semantic_store_kind']) { [string]$memoryState.semantic_store_kind } else { '' }
    semantic_namespaces = @($semanticNamespaces | Sort-Object)
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphSubgraphProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $contract = Get-CodexUserLevelLangGraphContract
  $subgraphs = if ($contract -is [System.Collections.IDictionary] -and $contract.Contains('subgraphs')) { $contract['subgraphs'] } elseif ($null -ne $contract.PSObject.Properties['subgraphs']) { $contract.subgraphs } else { [ordered]@{} }
  $phaseToSubgraph = if ($contract -is [System.Collections.IDictionary] -and $contract.Contains('phase_to_subgraph')) { $contract['phase_to_subgraph'] } elseif ($null -ne $contract.PSObject.Properties['phase_to_subgraph']) { $contract.phase_to_subgraph } else { [ordered]@{} }
  $availableSubgraphs = @()
  if ($subgraphs -is [System.Collections.IDictionary]) {
    $availableSubgraphs = @($subgraphs.Keys | ForEach-Object { [string]$_ } | Sort-Object)
  } else {
    $availableSubgraphs = @($subgraphs.PSObject.Properties | ForEach-Object { [string]$_.Name } | Sort-Object)
  }

  $isDictionary = ($ThreadRecord -is [System.Collections.IDictionary])
  $phase = if ($isDictionary -and $ThreadRecord.Contains('phase')) { [string]$ThreadRecord['phase'] } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['phase']) { [string]$ThreadRecord.phase } else { '' }
  $activeSubgraph = if ($isDictionary -and $ThreadRecord.Contains('active_subgraph')) { [string]$ThreadRecord['active_subgraph'] } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['active_subgraph']) { [string]$ThreadRecord.active_subgraph } else { '' }
  $activeSubgraphPosture = if ($isDictionary -and $ThreadRecord.Contains('active_subgraph_posture')) { $ThreadRecord['active_subgraph_posture'] } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['active_subgraph_posture']) { $ThreadRecord.active_subgraph_posture } else { $null }
  $derivedSubgraph = ''

  if ($phaseToSubgraph -is [System.Collections.IDictionary] -and $phaseToSubgraph.Contains($phase)) {
    $derivedSubgraph = [string]$phaseToSubgraph[$phase]
  } elseif (-not [string]::IsNullOrWhiteSpace($phase) -and $null -ne $phaseToSubgraph.PSObject.Properties[$phase]) {
    $derivedSubgraph = [string]$phaseToSubgraph.$phase
  }

  if (-not [string]::IsNullOrWhiteSpace($derivedSubgraph)) {
    $activeSubgraph = $derivedSubgraph
  }

  if ($null -eq $activeSubgraphPosture -and -not [string]::IsNullOrWhiteSpace($activeSubgraph)) {
    if ($subgraphs -is [System.Collections.IDictionary] -and $subgraphs.Contains($activeSubgraph)) {
      $activeSubgraphPosture = $subgraphs[$activeSubgraph]
    } elseif ($null -ne $subgraphs.PSObject.Properties[$activeSubgraph]) {
      $activeSubgraphPosture = $subgraphs.$activeSubgraph
    }
  }

  if ($null -ne $activeSubgraphPosture) {
    if ($activeSubgraphPosture -is [System.Collections.IDictionary]) {
      $activeSubgraphPosture['current_phase'] = $phase
    } else {
      $activeSubgraphPosture | Add-Member -NotePropertyName 'current_phase' -NotePropertyValue $phase -Force
    }
  }

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-subgraphs.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  return [ordered]@{
    active_subgraph = $activeSubgraph
    active_subgraph_posture = if ($null -ne $activeSubgraphPosture) { $activeSubgraphPosture } else { [ordered]@{} }
    available_subgraphs = $availableSubgraphs
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphSubgraphStateInspectionProjection {
  param(
    [string]$RepoRoot,
    [object]$ThreadRecord,
    [string]$ThreadId
  )

  $inspectionState = $null
  if ($ThreadRecord -is [System.Collections.IDictionary] -and $ThreadRecord.Contains('subgraph_state_inspection_state')) {
    $inspectionState = $ThreadRecord['subgraph_state_inspection_state']
  } elseif ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['subgraph_state_inspection_state']) {
    $inspectionState = $ThreadRecord.subgraph_state_inspection_state
  }

  $subgraphProjection = Get-CodexUserLevelLangGraphSubgraphProjection -RepoRoot $RepoRoot -ThreadRecord $ThreadRecord -ThreadId $ThreadId
  $activeSubgraph = [string]$subgraphProjection.active_subgraph
  $posture = if ($null -ne $subgraphProjection.active_subgraph_posture) { $subgraphProjection.active_subgraph_posture } else { [ordered]@{} }
  $postureIsDictionary = ($posture -is [System.Collections.IDictionary])
  $inspectionBlockers = @()
  $defaultPersistenceMode = if ($postureIsDictionary -and $posture.Contains('persistence_mode_default')) { [string]$posture['persistence_mode_default'] } elseif ($null -ne $posture.PSObject.Properties['persistence_mode_default']) { [string]$posture.persistence_mode_default } else { '' }
  $defaultCheckpointerMode = if ($postureIsDictionary -and $posture.Contains('checkpointer_mode_default')) { [string]$posture['checkpointer_mode_default'] } elseif ($null -ne $posture.PSObject.Properties['checkpointer_mode_default']) { [string]$posture.checkpointer_mode_default } else { '' }
  $defaultInspectionScope = if ($postureIsDictionary -and $posture.Contains('state_inspection_scope_default')) { [string]$posture['state_inspection_scope_default'] } elseif ($null -ne $posture.PSObject.Properties['state_inspection_scope_default']) { [string]$posture.state_inspection_scope_default } else { 'unavailable' }
  $defaultStaticDiscoverable = if ($postureIsDictionary -and $posture.Contains('static_discoverable')) { [bool]$posture['static_discoverable'] } elseif ($null -ne $posture.PSObject.Properties['static_discoverable']) { [bool]$posture.static_discoverable } else { $false }
  $defaultParallelSupport = if ($postureIsDictionary -and $posture.Contains('same_subgraph_parallel_calls_supported')) { [bool]$posture['same_subgraph_parallel_calls_supported'] } elseif ($null -ne $posture.PSObject.Properties['same_subgraph_parallel_calls_supported']) { [bool]$posture.same_subgraph_parallel_calls_supported } else { $false }
  $defaultInspectionAvailable = if ($postureIsDictionary -and $posture.Contains('state_inspection_default')) { [bool]$posture['state_inspection_default'] } elseif ($null -ne $posture.PSObject.Properties['state_inspection_default']) { [bool]$posture.state_inspection_default } else { $false }

  if ([string]::IsNullOrWhiteSpace($activeSubgraph)) {
    $inspectionBlockers += 'no_active_subgraph'
  }
  if (-not $defaultStaticDiscoverable) {
    $inspectionBlockers += 'subgraph_not_statically_discoverable'
  }
  if ($defaultPersistenceMode -eq 'stateless' -or $defaultCheckpointerMode -eq 'disabled') {
    $inspectionBlockers += 'stateless_subgraph'
  }

  $helperPointer = [ordered]@{
    script = 'omx-langgraph-subgraph-state.ps1'
    arguments = @('-RepoRoot', $RepoRoot, '-Json')
  }
  if (-not [string]::IsNullOrWhiteSpace($ThreadId)) {
    $helperPointer.arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
  }

  if ($null -eq $inspectionState) {
    return [ordered]@{
      active_subgraph = $activeSubgraph
      persistence_mode = $defaultPersistenceMode
      checkpointer_mode = $defaultCheckpointerMode
      inherits_parent_checkpointer = ($defaultCheckpointerMode -eq 'inherit_parent')
      separate_subgraph_memory = ($defaultCheckpointerMode -eq 'separate_subgraph')
      durable_execution_supported = ($defaultPersistenceMode -ne 'stateless')
      interrupts_supported = ($defaultPersistenceMode -ne 'stateless')
      state_inspection_available = ($defaultInspectionAvailable -and @($inspectionBlockers).Count -eq 0)
      state_inspection_scope = $defaultInspectionScope
      static_discoverable = $defaultStaticDiscoverable
      same_subgraph_parallel_calls_supported = $defaultParallelSupport
      inspection_blockers = @($inspectionBlockers | Sort-Object -Unique)
      helper_pointer = $helperPointer
    }
  }

  return [ordered]@{
    active_subgraph = if ($null -ne $inspectionState.PSObject.Properties['active_subgraph']) { [string]$inspectionState.active_subgraph } else { $activeSubgraph }
    persistence_mode = if ($null -ne $inspectionState.PSObject.Properties['persistence_mode']) { [string]$inspectionState.persistence_mode } else { $defaultPersistenceMode }
    checkpointer_mode = if ($null -ne $inspectionState.PSObject.Properties['checkpointer_mode']) { [string]$inspectionState.checkpointer_mode } else { $defaultCheckpointerMode }
    inherits_parent_checkpointer = if ($null -ne $inspectionState.PSObject.Properties['inherits_parent_checkpointer']) { [bool]$inspectionState.inherits_parent_checkpointer } else { ($defaultCheckpointerMode -eq 'inherit_parent') }
    separate_subgraph_memory = if ($null -ne $inspectionState.PSObject.Properties['separate_subgraph_memory']) { [bool]$inspectionState.separate_subgraph_memory } else { ($defaultCheckpointerMode -eq 'separate_subgraph') }
    durable_execution_supported = if ($null -ne $inspectionState.PSObject.Properties['durable_execution_supported']) { [bool]$inspectionState.durable_execution_supported } else { ($defaultPersistenceMode -ne 'stateless') }
    interrupts_supported = if ($null -ne $inspectionState.PSObject.Properties['interrupts_supported']) { [bool]$inspectionState.interrupts_supported } else { ($defaultPersistenceMode -ne 'stateless') }
    state_inspection_available = if ($null -ne $inspectionState.PSObject.Properties['state_inspection_available']) { [bool]$inspectionState.state_inspection_available } else { ($defaultInspectionAvailable -and @($inspectionBlockers).Count -eq 0) }
    state_inspection_scope = if ($null -ne $inspectionState.PSObject.Properties['state_inspection_scope']) { [string]$inspectionState.state_inspection_scope } else { $defaultInspectionScope }
    static_discoverable = if ($null -ne $inspectionState.PSObject.Properties['static_discoverable']) { [bool]$inspectionState.static_discoverable } else { $defaultStaticDiscoverable }
    same_subgraph_parallel_calls_supported = if ($null -ne $inspectionState.PSObject.Properties['same_subgraph_parallel_calls_supported']) { [bool]$inspectionState.same_subgraph_parallel_calls_supported } else { $defaultParallelSupport }
    inspection_blockers = if ($null -ne $inspectionState.PSObject.Properties['inspection_blockers'] -and $null -ne $inspectionState.inspection_blockers) { @($inspectionState.inspection_blockers | ForEach-Object { [string]$_ } | Sort-Object -Unique) } else { @($inspectionBlockers | Sort-Object -Unique) }
    helper_pointer = $helperPointer
  }
}

function Get-CodexUserLevelLangGraphHelperPointers {
  param(
    [string]$RepoRoot,
    [string]$ThreadId
  )

  return [ordered]@{
    deeper_engine = [ordered]@{
      script = 'omx-langgraph-deeper-engine.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    superstep_engine = [ordered]@{
      script = 'omx-langgraph-superstep-engine.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    stateful_engine = [ordered]@{
      script = 'omx-langgraph-stateful-engine.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    boundary_engine = [ordered]@{
      script = 'omx-langgraph-boundary-engine.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    handoff_engine = [ordered]@{
      script = 'omx-langgraph-handoff-engine.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    approval_engine = [ordered]@{
      script = 'omx-langgraph-approval-engine.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    provenance_engine = [ordered]@{
      script = 'omx-langgraph-provenance-engine.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    artifact_engine = [ordered]@{
      script = 'omx-langgraph-artifact-engine.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    reducer_engine = [ordered]@{
      script = 'omx-langgraph-reducer-engine.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    command_engine = [ordered]@{
      script = 'omx-langgraph-command-engine.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    runtime_engine = [ordered]@{
      script = 'omx-langgraph-runtime-engine.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    memory_engine = [ordered]@{
      script = 'omx-langgraph-memory-engine.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    migration_engine = [ordered]@{
      script = 'omx-langgraph-migration-engine.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    fuller_engine = [ordered]@{
      script = 'omx-langgraph-fuller-engine.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    auto_policy = [ordered]@{
      script = 'omx-langgraph-auto-policy.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    subgraph_state = [ordered]@{
      script = 'omx-langgraph-subgraph-state.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    generalized_routing = [ordered]@{
      script = 'omx-langgraph-generalized-routing.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    live_execution = [ordered]@{
      script = 'omx-langgraph-live-execution.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    invocation = [ordered]@{
      script = 'omx-langgraph-invocation.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    engine = [ordered]@{
      script = 'omx-langgraph-engine.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    kernel = [ordered]@{
      script = 'omx-langgraph-kernel.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    approval_queue = [ordered]@{
      script = 'omx-langgraph-approval-queue.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    migration = [ordered]@{
      script = 'omx-langgraph-migration.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    memory = [ordered]@{
      script = 'omx-langgraph-memory.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    runtime = [ordered]@{
      script = 'omx-langgraph-runtime.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    stream = [ordered]@{
      script = 'omx-langgraph-stream.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    subgraphs = [ordered]@{
      script = 'omx-langgraph-subgraphs.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    inspect = [ordered]@{
      script = 'omx-langgraph-inspect.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    history = [ordered]@{
      script = 'omx-langgraph-history.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
    replay = [ordered]@{
      script = 'omx-langgraph-replay.ps1'
      arguments = @('-ThreadId', $ThreadId, '-TargetId', '<target-id>', '-RepoRoot', $RepoRoot, '-Json')
    }
    recover_time_travel = [ordered]@{
      script = 'omx-langgraph-recover.ps1'
      arguments = @('-ThreadId', $ThreadId, '-MutationIntent', 'explicit-recovery', '-TargetId', '<target-id>', '-RepoRoot', $RepoRoot, '-Json')
    }
    recover_update_state = [ordered]@{
      script = 'omx-langgraph-recover.ps1'
      arguments = @('-ThreadId', $ThreadId, '-MutationIntent', 'explicit-recovery', '-ThreadField', '<field=value>', '-RepoRoot', $RepoRoot, '-Json')
    }
    resume = [ordered]@{
      script = 'omx-langgraph-resume.ps1'
      arguments = @('-ThreadId', $ThreadId, '-RepoRoot', $RepoRoot, '-Json')
    }
  }
}

function Read-CodexUserLevelLangGraphHistoryState {
  param(
    [string]$RepoRoot,
    [string]$ThreadId,
    [object]$ThreadRecord,
    [object]$CheckpointRecord,
    [object]$InterruptRecord
  )

  $path = Get-CodexUserLevelLangGraphHistoryRecordPath -RepoRoot $RepoRoot -ThreadId $ThreadId
  if (Test-Path -LiteralPath $path) {
    $record = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
    $records = if ($null -ne $record.PSObject.Properties['records'] -and $null -ne $record.records) { @($record.records) } else { @() }
    $targets = @()
    $sourceRecords = @()
    foreach ($historyRecord in @($records)) {
      $historySources = if ($null -ne $historyRecord.PSObject.Properties['source_records'] -and $null -ne $historyRecord.source_records) { @($historyRecord.source_records | ForEach-Object { [string]$_ }) } else { @() }
      $sourceRecords += $historySources
      $common = [ordered]@{
        history_id = if ($null -ne $historyRecord.PSObject.Properties['history_id']) { [string]$historyRecord.history_id } else { '' }
        checkpoint_id = if ($null -ne $historyRecord.PSObject.Properties['checkpoint_id']) { [string]$historyRecord.checkpoint_id } else { '' }
        phase = if ($null -ne $historyRecord.PSObject.Properties['phase']) { [string]$historyRecord.phase } else { '' }
        status = if ($null -ne $historyRecord.PSObject.Properties['status']) { [string]$historyRecord.status } else { '' }
        checkpoint_kind = if ($null -ne $historyRecord.PSObject.Properties['checkpoint_kind']) { [string]$historyRecord.checkpoint_kind } else { '' }
        event_kind = if ($null -ne $historyRecord.PSObject.Properties['event_kind']) { [string]$historyRecord.event_kind } else { '' }
        lifecycle_posture = if ($null -ne $historyRecord.PSObject.Properties['lifecycle_posture']) { [string]$historyRecord.lifecycle_posture } else { '' }
        created_at = if ($null -ne $historyRecord.PSObject.Properties['created_at']) { [string]$historyRecord.created_at } else { '' }
        fidelity = if ($null -ne $historyRecord.PSObject.Properties['fidelity']) { [string]$historyRecord.fidelity } else { 'full' }
        source_records = $historySources
      }
      if ($null -ne $historyRecord.PSObject.Properties['history_target_id'] -and -not [string]::IsNullOrWhiteSpace([string]$historyRecord.history_target_id)) {
        $targets += [ordered]@{
          target_id = [string]$historyRecord.history_target_id
          target_kind = 'state_history'
          history_id = $common.history_id
          checkpoint_id = $common.checkpoint_id
          phase = $common.phase
          status = $common.status
          checkpoint_kind = $common.checkpoint_kind
          event_kind = $common.event_kind
          lifecycle_posture = $common.lifecycle_posture
          created_at = $common.created_at
          fidelity = $common.fidelity
          source_records = $common.source_records
        }
      }
      if ($null -ne $historyRecord.PSObject.Properties['checkpoint_target_id'] -and -not [string]::IsNullOrWhiteSpace([string]$historyRecord.checkpoint_target_id)) {
        $targets += [ordered]@{
          target_id = [string]$historyRecord.checkpoint_target_id
          target_kind = 'checkpoint'
          history_id = $common.history_id
          checkpoint_id = $common.checkpoint_id
          phase = $common.phase
          status = $common.status
          checkpoint_kind = $common.checkpoint_kind
          event_kind = $common.event_kind
          lifecycle_posture = $common.lifecycle_posture
          created_at = $common.created_at
          fidelity = $common.fidelity
          source_records = $common.source_records
        }
      }
    }

    return [ordered]@{
      exists = $true
      path = $path
      compatibility = 'tracked_history'
      history_record_count = @($records).Count
      target_count = @($targets).Count
      available_targets = @($targets)
      source_records = @($sourceRecords | Sort-Object -Unique)
      updated_at = if ($null -ne $record.PSObject.Properties['updated_at']) { [string]$record.updated_at } else { '' }
    }
  }

  $targets = @()
  $sourceRecords = @()
  if ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['exists'] -and [bool]$ThreadRecord.exists) {
    $threadPath = Get-CodexUserLevelLangGraphThreadRecordPath -RepoRoot $RepoRoot -ThreadId $ThreadId
    $sourceRecords += $threadPath
    $targets += [ordered]@{
      target_id = 'history:synthetic-latest'
      target_kind = 'state_history'
      history_id = 'synthetic-latest'
      checkpoint_id = if ($null -ne $CheckpointRecord -and $null -ne $CheckpointRecord.PSObject.Properties['exists'] -and [bool]$CheckpointRecord.exists) { 'synthetic-latest' } else { '' }
      phase = [string]$ThreadRecord.phase
      status = [string]$ThreadRecord.status
      checkpoint_kind = if ($null -ne $CheckpointRecord -and $null -ne $CheckpointRecord.PSObject.Properties['checkpoint_kind']) { [string]$CheckpointRecord.checkpoint_kind } else { '' }
      event_kind = 'synthetic_latest_only'
      lifecycle_posture = [string](Get-CodexUserLevelLangGraphRecoveryProjection -ThreadRecord $ThreadRecord).posture
      created_at = [string]$ThreadRecord.updated_at
      fidelity = 'reduced'
      source_records = @($sourceRecords)
    }
  }
  if ($null -ne $CheckpointRecord -and $null -ne $CheckpointRecord.PSObject.Properties['exists'] -and [bool]$CheckpointRecord.exists) {
    $checkpointPath = Get-CodexUserLevelLangGraphCheckpointRecordPath -RepoRoot $RepoRoot -ThreadId $ThreadId
    $sourceRecords += $checkpointPath
    $targets += [ordered]@{
      target_id = 'checkpoint:synthetic-latest'
      target_kind = 'checkpoint'
      history_id = 'synthetic-latest'
      checkpoint_id = 'synthetic-latest'
      phase = [string]$CheckpointRecord.phase
      status = if ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['status']) { [string]$ThreadRecord.status } else { '' }
      checkpoint_kind = [string]$CheckpointRecord.checkpoint_kind
      event_kind = 'synthetic_latest_only'
      lifecycle_posture = if ($null -ne $ThreadRecord) { [string](Get-CodexUserLevelLangGraphRecoveryProjection -ThreadRecord $ThreadRecord).posture } else { 'ordinary' }
      created_at = [string]$CheckpointRecord.updated_at
      fidelity = 'reduced'
      source_records = @($sourceRecords)
    }
  }
  if ($null -ne $InterruptRecord -and $null -ne $InterruptRecord.PSObject.Properties['exists'] -and [bool]$InterruptRecord.exists) {
    $sourceRecords += (Get-CodexUserLevelLangGraphInterruptRecordPath -RepoRoot $RepoRoot -ThreadId $ThreadId)
  }

  return [ordered]@{
    exists = $false
    path = $path
    compatibility = if (@($targets).Count -gt 0) { 'synthetic_latest_only' } else { 'no_history' }
    history_record_count = 0
    target_count = @($targets).Count
    available_targets = @($targets)
    source_records = @($sourceRecords | Sort-Object -Unique)
    updated_at = if ($null -ne $ThreadRecord -and $null -ne $ThreadRecord.PSObject.Properties['updated_at']) { [string]$ThreadRecord.updated_at } else { '' }
  }
}

function Write-CodexUserLevelLangGraphBackendRecord {
  param(
    [Parameter(Mandatory)]
    [string]$RepoRoot,
    [Parameter(Mandatory)]
    [string]$ThreadId,
    [string]$Phase
  )

  $layout = Ensure-CodexUserLevelLangGraphRuntimeLayout -RepoRoot $RepoRoot
  $payload = [ordered]@{}
  if (Test-Path -LiteralPath ([string]$layout.backend_record)) {
    $existing = Get-Content -LiteralPath ([string]$layout.backend_record) -Raw | ConvertFrom-Json
    foreach ($property in @($existing.PSObject.Properties)) {
      $payload[$property.Name] = $property.Value
    }
  }
  $payload['backend'] = 'langgraph'
  $payload['thread_id'] = $ThreadId
  $payload['phase'] = $Phase
  $payload['updated_at'] = (Get-Date).ToUniversalTime().ToString('o')
  $payload['layout'] = $layout
  $json = $payload | ConvertTo-Json -Depth 6
  Set-Content -LiteralPath ([string]$layout.backend_record) -Value $json -Encoding ASCII -NoNewline
  return [string]$layout.backend_record
}

function Remove-CodexUserLevelLangGraphBackendRecord {
  param(
    [string]$RepoRoot
  )

  $path = Get-CodexUserLevelLangGraphBackendRecordPath -RepoRoot $RepoRoot
  if (Test-Path -LiteralPath $path) {
    Remove-Item -LiteralPath $path -Force
  }
}

function Get-CodexUserLevelLangGraphContract {
  return [ordered]@{
    root_phases = @('define-target', 'read-context', 'freeze-plan', 'execute-parallel', 'integrate-converge', 'stabilize', 'verify-accept')
    current_graph_contract = (Get-CodexUserLevelLangGraphCurrentGraphContract)
    graph_contract_fields = @('graph_contract_id', 'topology_version', 'state_schema_version')
    graph_kernel_identity = [ordered]@{
      kernel_kind = 'stategraph'
      kernel_id = 'codex_user_level_stategraph'
      graph_api_surface = 'StateGraph'
      operator_shell_model = 'seven_phase_durable_shell'
    }
    graph_kernel_identity_fields = @('kernel_kind', 'kernel_id', 'graph_api_surface', 'operator_shell_model')
    graph_kernel_node_postures = @('phase_active', 'approval_wait', 'recovery_pending_resume', 'terminal')
    graph_kernel_transition_kinds = @('sequential', 'loop', 'command', 'interrupt', 'recovery', 'terminal')
    graph_kernel_node_fields = @('node_id', 'phase', 'node_kind', 'subgraph_id', 'loop_capable', 'terminal')
    graph_kernel_edge_fields = @('edge_id', 'source_node', 'target_node', 'transition_kind', 'condition')
    graph_kernel_projection_fields = @('kernel_identity', 'current_node_id', 'mapped_phase', 'node_posture', 'current_node', 'available_next_nodes', 'last_transition', 'helper_pointer')
    graph_kernel_phase_to_node = [ordered]@{
      'define-target' = 'define_target'
      'read-context' = 'read_context'
      'freeze-plan' = 'freeze_plan'
      'execute-parallel' = 'execute_parallel'
      'integrate-converge' = 'integrate_converge'
      'stabilize' = 'stabilize'
      'verify-accept' = 'verify_accept'
    }
    primary_runtime_engine_identity = [ordered]@{
      engine_kind = 'compiled_stategraph_engine'
      engine_id = 'codex_user_level_primary_stategraph'
      graph_api_surface = 'StateGraph'
      operator_shell_model = 'seven_phase_durable_shell'
    }
    primary_runtime_engine_identity_fields = @('engine_kind', 'engine_id', 'graph_api_surface', 'operator_shell_model')
    primary_runtime_engine_postures = @('compiled_unavailable', 'compiled_ready', 'interrupt_wait', 'recovery_wait', 'terminal')
    primary_runtime_engine_projection_fields = @('engine_identity', 'compile_supported', 'compiled_graph_present', 'checkpointer_expected', 'entry_node', 'finish_nodes', 'current_execution_node', 'mapped_phase', 'execution_posture', 'last_execution_reason', 'helper_pointer')
    compiled_invocation_identity = [ordered]@{
      invocation_kind = 'compiled_stategraph_path'
      invocation_id = 'codex_user_level_compiled_stategraph'
      compiler_surface = 'StateGraph.compile'
      invoke_surface = 'CompiledGraph.invoke'
      stream_surface = 'CompiledGraph.stream'
    }
    compiled_invocation_identity_fields = @('invocation_kind', 'invocation_id', 'compiler_surface', 'invoke_surface', 'stream_surface')
    compiled_invocation_postures = @('unavailable', 'compiled_ready', 'interrupt_wait', 'recovery_wait', 'completed')
    compiled_invocation_run_kinds = @('invoke', 'stream')
    compiled_invocation_projection_fields = @('invocation_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'compiled_node_count', 'compiled_edge_count', 'current_execution_node', 'mapped_phase', 'invocation_posture', 'last_invoke_kind', 'last_invoke_reason', 'helper_pointer')
    live_execution_identity = [ordered]@{
      execution_kind = 'live_compiled_stategraph_path'
      execution_id = 'codex_user_level_live_compiled_stategraph'
      compiler_surface = 'StateGraph.compile'
      execute_surface = 'CompiledGraph.invoke/stream'
    }
    live_execution_identity_fields = @('execution_kind', 'execution_id', 'compiler_surface', 'execute_surface')
    live_execution_postures = @('unavailable', 'ready', 'executed', 'interrupt_wait', 'recovery_wait', 'terminal', 'execution_failed')
    live_execution_run_kinds = @('invoke', 'stream')
    live_execution_projection_fields = @('execution_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'current_execution_node', 'mapped_phase', 'execution_posture', 'last_run_kind', 'last_run_status', 'last_run_reason', 'last_output_keys', 'last_stream_event_count', 'helper_pointer')
    fuller_live_primary_engine_identity = [ordered]@{
      engine_kind = 'fuller_live_stategraph_primary_execution_engine'
      engine_id = 'codex_user_level_live_primary_execution_engine'
      graph_api_surface = 'StateGraph'
      execute_surface = 'CompiledGraph.invoke/stream'
    }
    fuller_live_primary_engine_identity_fields = @('engine_kind', 'engine_id', 'graph_api_surface', 'execute_surface')
    fuller_live_primary_engine_postures = @('unavailable', 'ready', 'executed', 'interrupt_wait', 'recovery_wait', 'terminal', 'execution_failed')
    fuller_live_primary_engine_run_kinds = @('invoke', 'stream')
    fuller_live_primary_engine_transition_kinds = @('sequential', 'loop', 'command', 'interrupt', 'recovery', 'terminal', 'stayed_put')
    fuller_live_primary_engine_projection_fields = @('engine_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'current_execution_node', 'mapped_phase', 'execution_node_path', 'resulting_phase', 'resulting_status', 'phase_transition_kind', 'execution_posture', 'last_run_kind', 'last_run_status', 'last_run_reason', 'helper_pointer')
    deeper_live_primary_engine_identity = [ordered]@{
      engine_kind = 'deeper_live_stategraph_primary_execution_engine'
      engine_id = 'codex_user_level_deeper_live_primary_execution_engine'
      graph_api_surface = 'StateGraph'
      execute_surface = 'CompiledGraph.invoke/stream'
      recursion_limit_surface = 'config.recursion_limit'
      remaining_steps_surface = 'RemainingSteps'
    }
    deeper_live_primary_engine_identity_fields = @('engine_kind', 'engine_id', 'graph_api_surface', 'execute_surface', 'recursion_limit_surface', 'remaining_steps_surface')
    deeper_live_primary_engine_postures = @('unavailable', 'ready', 'projected', 'interrupt_wait', 'recovery_wait', 'terminal', 'projection_failed')
    deeper_live_primary_engine_run_kinds = @('invoke', 'stream')
    deeper_live_primary_engine_stop_boundaries = @('phase_boundary', 'command_boundary', 'loop_boundary', 'interrupt_boundary', 'recovery_boundary', 'terminal_boundary', 'recursion_limit_boundary')
    deeper_live_primary_engine_projection_fields = @('engine_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'current_execution_node', 'mapped_phase', 'projected_node_path', 'projected_phase_path', 'planned_supersteps', 'stop_boundary', 'terminal_reached', 'recursion_limit_supported', 'remaining_steps_supported', 'recursion_limit', 'execution_posture', 'last_run_kind', 'last_run_status', 'last_run_reason', 'helper_pointer')
    superstep_live_primary_engine_identity = [ordered]@{
      engine_kind = 'superstep_live_stategraph_primary_execution_engine'
      engine_id = 'codex_user_level_superstep_live_primary_execution_engine'
      graph_api_surface = 'StateGraph'
      execute_surface = 'CompiledGraph.invoke/stream'
      superstep_surface = 'Pregel supersteps'
      trace_surface = 'node_visit_path/phase_visit_path'
    }
    superstep_live_primary_engine_identity_fields = @('engine_kind', 'engine_id', 'graph_api_surface', 'execute_surface', 'superstep_surface', 'trace_surface')
    superstep_live_primary_engine_postures = @('unavailable', 'ready', 'executed', 'interrupt_wait', 'recovery_wait', 'terminal', 'recursion_limited', 'execution_failed')
    superstep_live_primary_engine_run_kinds = @('invoke', 'stream')
    superstep_live_primary_engine_stop_boundaries = @('phase_boundary', 'command_boundary', 'loop_boundary', 'interrupt_boundary', 'recovery_boundary', 'terminal_boundary', 'recursion_limit_boundary')
    superstep_live_primary_engine_projection_fields = @('engine_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'current_execution_node', 'mapped_phase', 'node_visit_path', 'phase_visit_path', 'superstep_count', 'stop_boundary', 'terminal_reached', 'recursion_limit_supported', 'remaining_steps_supported', 'recursion_limit', 'execution_posture', 'last_run_kind', 'last_run_status', 'last_run_reason', 'helper_pointer')
    stateful_live_primary_engine_identity = [ordered]@{
      engine_kind = 'stateful_live_stategraph_primary_execution_engine'
      engine_id = 'codex_user_level_stateful_live_primary_execution_engine'
      graph_api_surface = 'StateGraph'
      execute_surface = 'CompiledGraph.invoke/stream'
      remaining_steps_surface = 'RemainingSteps'
      decision_surface = 'next_execution_node_from_graph_state'
    }
    stateful_live_primary_engine_identity_fields = @('engine_kind', 'engine_id', 'graph_api_surface', 'execute_surface', 'remaining_steps_surface', 'decision_surface')
    stateful_live_primary_engine_postures = @('unavailable', 'ready', 'executed', 'interrupt_wait', 'recovery_wait', 'terminal', 'recursion_limited', 'execution_failed')
    stateful_live_primary_engine_run_kinds = @('invoke', 'stream')
    stateful_live_primary_engine_stop_boundaries = @('phase_boundary', 'command_boundary', 'loop_boundary', 'interrupt_boundary', 'recovery_boundary', 'terminal_boundary', 'recursion_limit_boundary')
    stateful_live_primary_engine_projection_fields = @('engine_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'current_execution_node', 'mapped_phase', 'stateful_node_path', 'stateful_phase_path', 'stateful_transition_log', 'superstep_count', 'stop_boundary', 'terminal_reached', 'recursion_limit_supported', 'remaining_steps_supported', 'recursion_limit', 'execution_posture', 'last_run_kind', 'last_run_status', 'last_run_reason', 'helper_pointer')
    boundary_state_live_primary_engine_identity = [ordered]@{
      engine_kind = 'graph_resident_live_stategraph_primary_execution_engine'
      engine_id = 'codex_user_level_graph_resident_live_primary_execution_engine'
      graph_api_surface = 'StateGraph'
      execute_surface = 'CompiledGraph.invoke/stream'
      boundary_surface = 'graph_resident_boundary_state'
      decision_surface = 'compiled_boundary_nodes_and_phase_end'
    }
    boundary_state_live_primary_engine_identity_fields = @('engine_kind', 'engine_id', 'graph_api_surface', 'execute_surface', 'boundary_surface', 'decision_surface')
    boundary_state_live_primary_engine_postures = @('unavailable', 'ready', 'executed', 'interrupt_wait', 'recovery_wait', 'terminal', 'recursion_limited', 'execution_failed')
    boundary_state_live_primary_engine_run_kinds = @('invoke', 'stream')
    boundary_state_live_primary_engine_stop_boundaries = @('phase_boundary', 'command_boundary', 'loop_boundary', 'interrupt_boundary', 'recovery_boundary', 'terminal_boundary', 'recursion_limit_boundary')
    boundary_state_live_primary_engine_projection_fields = @('engine_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'current_execution_node', 'mapped_phase', 'boundary_node_path', 'boundary_phase_path', 'boundary_transition_log', 'boundary_state_kind', 'superstep_count', 'stop_boundary', 'terminal_reached', 'recursion_limit_supported', 'remaining_steps_supported', 'recursion_limit', 'execution_posture', 'last_run_kind', 'last_run_status', 'last_run_reason', 'helper_pointer')
    handoff_state_live_primary_engine_identity = [ordered]@{
      engine_kind = 'subgraph_aware_live_stategraph_primary_execution_engine'
      engine_id = 'codex_user_level_subgraph_aware_live_primary_execution_engine'
      graph_api_surface = 'StateGraph'
      execute_surface = 'CompiledGraph.invoke/stream'
      handoff_surface = 'subgraph_and_parent_handoff_state'
      subgraph_surface = 'active_subgraph/source_subgraph/target_subgraph'
    }
    handoff_state_live_primary_engine_identity_fields = @('engine_kind', 'engine_id', 'graph_api_surface', 'execute_surface', 'handoff_surface', 'subgraph_surface')
    handoff_state_live_primary_engine_postures = @('unavailable', 'ready', 'executed', 'interrupt_wait', 'recovery_wait', 'terminal', 'recursion_limited', 'execution_failed')
    handoff_state_live_primary_engine_run_kinds = @('invoke', 'stream')
    handoff_state_live_primary_engine_stop_boundaries = @('phase_boundary', 'command_boundary', 'loop_boundary', 'interrupt_boundary', 'recovery_boundary', 'terminal_boundary', 'recursion_limit_boundary')
    handoff_state_live_primary_engine_projection_fields = @('engine_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'current_execution_node', 'mapped_phase', 'handoff_node_path', 'handoff_phase_path', 'handoff_subgraph_path', 'handoff_transition_log', 'handoff_state_kind', 'active_subgraph', 'source_subgraph', 'target_subgraph', 'parent_handoff_target', 'graph_scope', 'superstep_count', 'stop_boundary', 'terminal_reached', 'recursion_limit_supported', 'remaining_steps_supported', 'recursion_limit', 'execution_posture', 'last_run_kind', 'last_run_status', 'last_run_reason', 'helper_pointer')
    approval_aware_live_primary_engine_identity = [ordered]@{
      engine_kind = 'approval_aware_live_stategraph_primary_execution_engine'
      engine_id = 'codex_user_level_approval_aware_live_primary_execution_engine'
      graph_api_surface = 'StateGraph'
      execute_surface = 'CompiledGraph.invoke/stream'
      approval_surface = 'approval_queue_and_resume_map_state'
      resume_surface = 'queue_posture/resume_map_keys/current_interrupt_id'
    }
    approval_aware_live_primary_engine_identity_fields = @('engine_kind', 'engine_id', 'graph_api_surface', 'execute_surface', 'approval_surface', 'resume_surface')
    approval_aware_live_primary_engine_postures = @('unavailable', 'ready', 'executed', 'interrupt_wait', 'recovery_wait', 'terminal', 'recursion_limited', 'execution_failed')
    approval_aware_live_primary_engine_run_kinds = @('invoke', 'stream')
    approval_aware_live_primary_engine_stop_boundaries = @('phase_boundary', 'command_boundary', 'loop_boundary', 'interrupt_boundary', 'recovery_boundary', 'terminal_boundary', 'recursion_limit_boundary')
    approval_aware_live_primary_engine_projection_fields = @('engine_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'current_execution_node', 'mapped_phase', 'approval_node_path', 'approval_phase_path', 'approval_transition_log', 'resume_state_kind', 'queue_posture', 'pending_count', 'resolved_count', 'current_interrupt_id', 'resume_map_keys', 'superstep_count', 'stop_boundary', 'terminal_reached', 'recursion_limit_supported', 'remaining_steps_supported', 'recursion_limit', 'execution_posture', 'last_run_kind', 'last_run_status', 'last_run_reason', 'helper_pointer')
    provenance_state_live_primary_engine_identity = [ordered]@{
      engine_kind = 'recovery_aware_live_stategraph_primary_execution_engine'
      engine_id = 'codex_user_level_recovery_aware_live_primary_execution_engine'
      graph_api_surface = 'StateGraph'
      execute_surface = 'CompiledGraph.invoke/stream'
      recovery_surface = 'recovery_target_and_action_state'
      provenance_surface = 'source_records_and_history_targets'
    }
    provenance_state_live_primary_engine_identity_fields = @('engine_kind', 'engine_id', 'graph_api_surface', 'execute_surface', 'recovery_surface', 'provenance_surface')
    provenance_state_live_primary_engine_postures = @('unavailable', 'ready', 'executed', 'interrupt_wait', 'recovery_wait', 'terminal', 'recursion_limited', 'execution_failed')
    provenance_state_live_primary_engine_run_kinds = @('invoke', 'stream')
    provenance_state_live_primary_engine_stop_boundaries = @('phase_boundary', 'command_boundary', 'loop_boundary', 'interrupt_boundary', 'recovery_boundary', 'terminal_boundary', 'recursion_limit_boundary')
    provenance_state_live_primary_engine_projection_fields = @('engine_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'current_execution_node', 'mapped_phase', 'provenance_node_path', 'provenance_phase_path', 'provenance_transition_log', 'provenance_state_kind', 'recovery_posture', 'recovery_action', 'recovery_target_id', 'recovery_target_kind', 'source_records', 'recoverable_fields_touched', 'history_compatibility', 'history_target_count', 'superstep_count', 'stop_boundary', 'terminal_reached', 'recursion_limit_supported', 'remaining_steps_supported', 'recursion_limit', 'execution_posture', 'last_run_kind', 'last_run_status', 'last_run_reason', 'helper_pointer')
    durable_artifact_aware_live_primary_engine_identity = [ordered]@{
      engine_kind = 'durable_artifact_aware_live_stategraph_primary_execution_engine'
      engine_id = 'codex_user_level_durable_artifact_aware_live_primary_execution_engine'
      graph_api_surface = 'StateGraph'
      execute_surface = 'CompiledGraph.invoke/stream'
      artifact_surface = 'implementation_brief_and_survivor_queue_state'
      artifact_summary_surface = 'artifact_state_kind/brief_id/source_evidence_ref_count/survivor_count'
    }
    durable_artifact_aware_live_primary_engine_identity_fields = @('engine_kind', 'engine_id', 'graph_api_surface', 'execute_surface', 'artifact_surface', 'artifact_summary_surface')
    durable_artifact_aware_live_primary_engine_postures = @('unavailable', 'ready', 'executed', 'interrupt_wait', 'recovery_wait', 'terminal', 'recursion_limited', 'execution_failed')
    durable_artifact_aware_live_primary_engine_run_kinds = @('invoke', 'stream')
    durable_artifact_aware_live_primary_engine_stop_boundaries = @('phase_boundary', 'command_boundary', 'loop_boundary', 'interrupt_boundary', 'recovery_boundary', 'terminal_boundary', 'recursion_limit_boundary')
    durable_artifact_aware_live_primary_engine_projection_fields = @('engine_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'current_execution_node', 'mapped_phase', 'artifact_node_path', 'artifact_phase_path', 'artifact_transition_log', 'artifact_state_kind', 'implementation_brief_present', 'implementation_brief_id', 'implementation_brief_source_evidence_ref_count', 'survivor_queue_present', 'survivor_queue_kind', 'survivor_count', 'superstep_count', 'stop_boundary', 'terminal_reached', 'recursion_limit_supported', 'remaining_steps_supported', 'recursion_limit', 'execution_posture', 'last_run_kind', 'last_run_status', 'last_run_reason', 'helper_pointer')
    reducer_aware_live_primary_engine_identity = [ordered]@{
      engine_kind = 'reducer_aware_live_stategraph_primary_execution_engine'
      engine_id = 'codex_user_level_reducer_aware_live_primary_execution_engine'
      graph_api_surface = 'StateGraph'
      execute_surface = 'CompiledGraph.invoke/stream'
      reducer_surface = 'reducer_merge_channels_and_single_writer_state'
      merge_surface = 'fanout_state/merge_channels_updated/source_records'
    }
    reducer_aware_live_primary_engine_identity_fields = @('engine_kind', 'engine_id', 'graph_api_surface', 'execute_surface', 'reducer_surface', 'merge_surface')
    reducer_aware_live_primary_engine_postures = @('unavailable', 'ready', 'executed', 'interrupt_wait', 'recovery_wait', 'terminal', 'recursion_limited', 'execution_failed')
    reducer_aware_live_primary_engine_run_kinds = @('invoke', 'stream')
    reducer_aware_live_primary_engine_stop_boundaries = @('phase_boundary', 'command_boundary', 'loop_boundary', 'interrupt_boundary', 'recovery_boundary', 'terminal_boundary', 'recursion_limit_boundary')
    reducer_aware_live_primary_engine_projection_fields = @('engine_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'current_execution_node', 'mapped_phase', 'merge_node_path', 'merge_phase_path', 'merge_transition_log', 'merge_state_kind', 'reducer_compatibility', 'fanout_state', 'invalid_multi_writer_detected', 'invalid_multi_writer_updates', 'merge_channels_updated', 'channel_item_counts', 'source_records', 'superstep_count', 'stop_boundary', 'terminal_reached', 'recursion_limit_supported', 'remaining_steps_supported', 'recursion_limit', 'execution_posture', 'last_run_kind', 'last_run_status', 'last_run_reason', 'helper_pointer')
    command_aware_live_primary_engine_identity = [ordered]@{
      engine_kind = 'command_aware_live_stategraph_primary_execution_engine'
      engine_id = 'codex_user_level_command_aware_live_primary_execution_engine'
      graph_api_surface = 'StateGraph'
      execute_surface = 'CompiledGraph.invoke/stream'
      command_surface = 'update_goto_resume_and_parent_handoff_state'
      control_surface = 'transition_kind/graph_scope/target_subgraph/resume_posture'
    }
    command_aware_live_primary_engine_identity_fields = @('engine_kind', 'engine_id', 'graph_api_surface', 'execute_surface', 'command_surface', 'control_surface')
    command_aware_live_primary_engine_postures = @('unavailable', 'ready', 'executed', 'interrupt_wait', 'recovery_wait', 'terminal', 'recursion_limited', 'execution_failed')
    command_aware_live_primary_engine_run_kinds = @('invoke', 'stream')
    command_aware_live_primary_engine_stop_boundaries = @('phase_boundary', 'command_boundary', 'loop_boundary', 'interrupt_boundary', 'recovery_boundary', 'terminal_boundary', 'recursion_limit_boundary')
    command_aware_live_primary_engine_projection_fields = @('engine_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'current_execution_node', 'mapped_phase', 'command_node_path', 'command_phase_path', 'command_transition_log', 'control_state_kind', 'transition_kind', 'update_keys', 'goto_target', 'graph_scope', 'source_subgraph', 'target_subgraph', 'parent_handoff_target', 'resume_posture', 'resume_payload_present', 'resume_payload_keys', 'superstep_count', 'stop_boundary', 'terminal_reached', 'recursion_limit_supported', 'remaining_steps_supported', 'recursion_limit', 'execution_posture', 'last_run_kind', 'last_run_status', 'last_run_reason', 'helper_pointer')
    runtime_aware_live_primary_engine_identity = [ordered]@{
      engine_kind = 'runtime_aware_live_stategraph_primary_execution_engine'
      engine_id = 'codex_user_level_runtime_aware_live_primary_execution_engine'
      graph_api_surface = 'StateGraph'
      execute_surface = 'CompiledGraph.invoke/stream'
      runtime_surface = 'runtime_context_and_context_schema_state'
      store_surface = 'injected_store_configuration_state'
    }
    runtime_aware_live_primary_engine_identity_fields = @('engine_kind', 'engine_id', 'graph_api_surface', 'execute_surface', 'runtime_surface', 'store_surface')
    runtime_aware_live_primary_engine_postures = @('unavailable', 'ready', 'executed', 'interrupt_wait', 'recovery_wait', 'terminal', 'recursion_limited', 'execution_failed')
    runtime_aware_live_primary_engine_run_kinds = @('invoke', 'stream')
    runtime_aware_live_primary_engine_stop_boundaries = @('phase_boundary', 'command_boundary', 'loop_boundary', 'interrupt_boundary', 'recovery_boundary', 'terminal_boundary', 'recursion_limit_boundary')
    runtime_aware_live_primary_engine_projection_fields = @('engine_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'current_execution_node', 'mapped_phase', 'runtime_node_path', 'runtime_phase_path', 'runtime_transition_log', 'runtime_state_kind', 'context_schema', 'runtime_context_present', 'runtime_context_keys', 'runtime_context_kind_hints', 'store_configured', 'store_access_expected', 'store_kind', 'superstep_count', 'stop_boundary', 'terminal_reached', 'recursion_limit_supported', 'remaining_steps_supported', 'recursion_limit', 'execution_posture', 'last_run_kind', 'last_run_status', 'last_run_reason', 'helper_pointer')
    memory_aware_live_primary_engine_identity = [ordered]@{
      engine_kind = 'memory_aware_live_stategraph_primary_execution_engine'
      engine_id = 'codex_user_level_memory_aware_live_primary_execution_engine'
      graph_api_surface = 'StateGraph'
      execute_surface = 'CompiledGraph.invoke/stream'
      memory_surface = 'memory_store_and_namespace_state'
      semantic_surface = 'semantic_memory_enablement_and_store_state'
    }
    memory_aware_live_primary_engine_identity_fields = @('engine_kind', 'engine_id', 'graph_api_surface', 'execute_surface', 'memory_surface', 'semantic_surface')
    memory_aware_live_primary_engine_postures = @('unavailable', 'ready', 'executed', 'interrupt_wait', 'recovery_wait', 'terminal', 'recursion_limited', 'execution_failed')
    memory_aware_live_primary_engine_run_kinds = @('invoke', 'stream')
    memory_aware_live_primary_engine_stop_boundaries = @('phase_boundary', 'command_boundary', 'loop_boundary', 'interrupt_boundary', 'recovery_boundary', 'terminal_boundary', 'recursion_limit_boundary')
    memory_aware_live_primary_engine_projection_fields = @('engine_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'current_execution_node', 'mapped_phase', 'memory_node_path', 'memory_phase_path', 'memory_transition_log', 'memory_state_kind', 'memory_store_configured', 'memory_store_kind', 'memory_namespaces', 'semantic_memory_enabled', 'semantic_store_kind', 'semantic_namespaces', 'superstep_count', 'stop_boundary', 'terminal_reached', 'recursion_limit_supported', 'remaining_steps_supported', 'recursion_limit', 'execution_posture', 'last_run_kind', 'last_run_status', 'last_run_reason', 'helper_pointer')
    migration_aware_live_primary_engine_identity = [ordered]@{
      engine_kind = 'migration_aware_live_stategraph_primary_execution_engine'
      engine_id = 'codex_user_level_migration_aware_live_primary_execution_engine'
      graph_api_surface = 'StateGraph'
      execute_surface = 'CompiledGraph.invoke/stream'
      migration_surface = 'graph_contract_and_thread_compatibility_state'
      compatibility_surface = 'topology_state_schema_and_reason_codes'
    }
    migration_aware_live_primary_engine_identity_fields = @('engine_kind', 'engine_id', 'graph_api_surface', 'execute_surface', 'migration_surface', 'compatibility_surface')
    migration_aware_live_primary_engine_postures = @('unavailable', 'ready', 'executed', 'interrupt_wait', 'recovery_wait', 'terminal', 'recursion_limited', 'execution_failed')
    migration_aware_live_primary_engine_run_kinds = @('invoke', 'stream')
    migration_aware_live_primary_engine_stop_boundaries = @('phase_boundary', 'command_boundary', 'loop_boundary', 'interrupt_boundary', 'recovery_boundary', 'terminal_boundary', 'recursion_limit_boundary')
    migration_aware_live_primary_engine_projection_fields = @('engine_identity', 'compile_supported', 'compiled_graph_present', 'invoke_supported', 'stream_supported', 'current_execution_node', 'mapped_phase', 'compatibility_node_path', 'compatibility_phase_path', 'compatibility_transition_log', 'compatibility_state_kind', 'current_graph_contract', 'thread_graph_contract', 'topology_compatibility', 'state_schema_compatibility', 'compatibility', 'reason_codes', 'superstep_count', 'stop_boundary', 'terminal_reached', 'recursion_limit_supported', 'remaining_steps_supported', 'recursion_limit', 'execution_posture', 'last_run_kind', 'last_run_status', 'last_run_reason', 'helper_pointer')
    automatic_runtime_policy_identity = [ordered]@{
      policy_kind = 'bounded_langgraph_runtime_policy'
      policy_id = 'codex_user_level_langgraph_runtime_policy'
      manual_first_default = $true
    }
    automatic_runtime_policy_identity_fields = @('policy_kind', 'policy_id', 'manual_first_default')
    automatic_runtime_policy_migration_postures = @('manual_only', 'auto_continue_safe', 'auto_continue_with_notice', 'manual_recovery_required')
    automatic_runtime_policy_approval_postures = @('no_queue_work', 'waiting_for_manual_approval', 'auto_resume_safe', 'auto_clear_stale_interrupt', 'resolved_queue_retained')
    automatic_runtime_policy_recovery_postures = @('ordinary', 'auto_continue_safe', 'manual_recovery_required')
    automatic_runtime_policy_actions = @('continue_on_migration_safe', 'continue_on_degraded_compatible', 'resume_after_resolved_queue', 'continue_after_safe_recovery', 'clear_stale_interrupt')
    automatic_runtime_policy_projection_fields = @('policy_identity', 'migration_policy_posture', 'approval_policy_posture', 'recovery_policy_posture', 'automatic_actions_available', 'safe_to_auto_apply', 'last_auto_action', 'last_auto_reason', 'helper_pointer')
    generalized_live_routing_identity = [ordered]@{
      routing_kind = 'generalized_live_stategraph_path'
      routing_id = 'codex_user_level_generalized_live_stategraph'
      graph_api_surface = 'StateGraph'
      route_decision_surface = 'StateGraph.add_conditional_edges'
    }
    generalized_live_routing_identity_fields = @('routing_kind', 'routing_id', 'graph_api_surface', 'route_decision_surface')
    generalized_live_routing_postures = @('unavailable', 'ready', 'routed', 'interrupt_wait', 'recovery_wait', 'terminal', 'routing_failed')
    generalized_live_routing_route_kinds = @('phase_linear', 'loop_review', 'loop_execution', 'loop_stabilization', 'approval_wait', 'recovery_wait', 'terminal_accept', 'terminal_halt', 'terminal_escalate', 'command_controlled')
    generalized_live_routing_projection_fields = @('routing_identity', 'compile_supported', 'compiled_graph_present', 'route_posture', 'current_route', 'candidate_routes', 'selected_route', 'loop_route_kind', 'current_execution_node', 'mapped_phase', 'next_execution_nodes', 'approval_route_pending', 'helper_pointer')
    approval_queue_item_fields = @('interrupt_id', 'order', 'interrupt_point', 'value_summary', 'reason', 'status', 'resume_value_present', 'resume_value_keys')
    approval_queue_item_statuses = @('pending', 'resolved')
    approval_queue_postures = @('no_interrupts', 'pending', 'partially_resolved', 'resolved')
    approval_queue_projection_fields = @('queue_posture', 'queue_size', 'pending_count', 'resolved_count', 'pending_interrupt_ids', 'resolved_interrupt_ids', 'current_interrupt_id', 'resume_map_keys', 'queue_items', 'helper_pointer')
    topology_compatibility_postures = @('migration_safe', 'degraded_compatible', 'incompatible')
    state_schema_compatibility_postures = @('migration_safe', 'degraded_compatible', 'incompatible')
    thread_compatibility_verdicts = @('migration_safe', 'degraded_compatible', 'incompatible')
    migration_reason_codes = @('graph_contract_id_mismatch', 'topology_version_missing', 'topology_minor_drift', 'topology_major_drift', 'state_schema_version_missing', 'state_schema_minor_drift', 'state_schema_major_drift')
    migration_projection_fields = @('current_graph_contract', 'thread_graph_contract', 'topology_compatibility', 'state_schema_compatibility', 'compatibility', 'reason_codes', 'helper_pointer')
    subgraph_library_fields = @('subgraph_id', 'role_family', 'roles', 'default_phase', 'phase_families', 'input_artifacts', 'output_artifacts', 'handoff_artifacts', 'fresh_context_boundary', 'durable_worker_default', 'read_only_default', 'persistence_mode_default', 'checkpointer_mode_default', 'state_inspection_default', 'state_inspection_scope_default', 'static_discoverable', 'same_subgraph_parallel_calls_supported', 'allowed_parent_graph_scopes')
    subgraph_projection_fields = @('active_subgraph', 'active_subgraph_posture', 'available_subgraphs', 'helper_pointer')
    subgraph_persistence_modes = @('per_invocation', 'per_thread', 'stateless')
    subgraph_checkpointer_modes = @('inherit_parent', 'separate_subgraph', 'disabled')
    subgraph_state_inspection_scopes = @('current_invocation', 'thread_accumulated', 'unavailable')
    subgraph_state_inspection_fields = @('active_subgraph', 'persistence_mode', 'checkpointer_mode', 'inherits_parent_checkpointer', 'separate_subgraph_memory', 'durable_execution_supported', 'interrupts_supported', 'state_inspection_available', 'state_inspection_scope', 'static_discoverable', 'same_subgraph_parallel_calls_supported', 'inspection_blockers')
    subgraph_state_inspection_projection_fields = @('active_subgraph', 'persistence_mode', 'checkpointer_mode', 'inherits_parent_checkpointer', 'separate_subgraph_memory', 'durable_execution_supported', 'interrupts_supported', 'state_inspection_available', 'state_inspection_scope', 'static_discoverable', 'same_subgraph_parallel_calls_supported', 'inspection_blockers', 'helper_pointer')
    stream_observability_modes = @('updates', 'checkpoints', 'tasks', 'debug')
    stream_event_fields = @('selected_modes', 'subgraphs', 'latest_event_kind', 'latest_namespace', 'latest_checkpoint_kind', 'latest_task_path', 'latest_task_status', 'latest_debug_summary', 'event_count')
    stream_projection_fields = @('selected_modes', 'subgraphs', 'latest_event_kind', 'latest_namespace', 'latest_checkpoint_kind', 'latest_task_path', 'latest_task_status', 'latest_debug_summary', 'event_count', 'helper_pointer')
    runtime_context_fields = @('context_schema', 'runtime_context_present', 'runtime_context_keys', 'runtime_context_kind_hints')
    store_injection_fields = @('store_configured', 'store_access_expected', 'store_kind')
    runtime_injection_projection_fields = @('context_schema', 'runtime_context_present', 'runtime_context_keys', 'runtime_context_kind_hints', 'store_configured', 'store_access_expected', 'store_kind', 'helper_pointer')
    memory_store_fields = @('memory_store_configured', 'memory_store_kind', 'memory_namespaces')
    semantic_memory_fields = @('semantic_memory_enabled', 'semantic_store_kind', 'semantic_namespaces')
    memory_projection_fields = @('memory_store_configured', 'memory_store_kind', 'memory_namespaces', 'semantic_memory_enabled', 'semantic_store_kind', 'semantic_namespaces', 'helper_pointer')
    command_transition_kinds = @('update', 'goto', 'update_goto', 'resume', 'resume_with_payload', 'parent_handoff', 'resume_parent_handoff')
    command_graph_scopes = @('current', 'parent')
    command_resume_postures = @('ordinary', 'awaiting_command_resume', 'resumed_without_payload', 'resumed_with_payload')
    command_state_fields = @('transition_kind', 'update_keys', 'goto_target', 'graph_scope', 'source_subgraph', 'target_subgraph', 'parent_handoff_target', 'resume_posture', 'resume_payload_present', 'resume_payload_keys')
    command_projection_fields = @('transition_kind', 'update_keys', 'goto_target', 'graph_scope', 'source_subgraph', 'target_subgraph', 'parent_handoff_target', 'resume_posture', 'resume_payload_present', 'resume_payload_keys', 'helper_pointer')
    phase_to_subgraph = [ordered]@{
      'define-target' = 'research'
      'read-context' = 'research'
      'freeze-plan' = 'planning'
      'execute-parallel' = 'execution'
      'integrate-converge' = 'execution'
      'stabilize' = 'execution'
      'verify-accept' = 'verification'
    }
    subgraphs = [ordered]@{
      research = [ordered]@{
        subgraph_id = 'research'
        role_family = 'research'
        roles = @('analyst', 'researcher', 'architect')
        default_phase = 'read-context'
        phase_families = @('define-target', 'read-context')
        input_artifacts = @()
        output_artifacts = @('frozen_implementation_brief')
        handoff_artifacts = @('frozen_implementation_brief')
        fresh_context_boundary = $false
        durable_worker_default = ''
        read_only_default = $true
        persistence_mode_default = 'per_thread'
        checkpointer_mode_default = 'separate_subgraph'
        state_inspection_default = $true
        state_inspection_scope_default = 'thread_accumulated'
        static_discoverable = $true
        same_subgraph_parallel_calls_supported = $false
        allowed_parent_graph_scopes = @('parent')
      }
      planning = [ordered]@{
        subgraph_id = 'planning'
        role_family = 'planning'
        roles = @('planner')
        default_phase = 'freeze-plan'
        phase_families = @('freeze-plan')
        input_artifacts = @('frozen_implementation_brief')
        output_artifacts = @('execution_slice_plan', 'ownership_boundaries')
        handoff_artifacts = @('execution_slice_plan', 'ownership_boundaries')
        fresh_context_boundary = $true
        durable_worker_default = ''
        read_only_default = $true
        persistence_mode_default = 'per_invocation'
        checkpointer_mode_default = 'inherit_parent'
        state_inspection_default = $true
        state_inspection_scope_default = 'current_invocation'
        static_discoverable = $true
        same_subgraph_parallel_calls_supported = $true
        allowed_parent_graph_scopes = @('parent')
      }
      execution = [ordered]@{
        subgraph_id = 'execution'
        role_family = 'execution'
        roles = @('executor', 'team-executor')
        default_phase = 'execute-parallel'
        phase_families = @('execute-parallel', 'integrate-converge', 'stabilize')
        input_artifacts = @('execution_slice_plan', 'ownership_boundaries')
        output_artifacts = @('implementation_patch_set', 'execution_evidence')
        handoff_artifacts = @('implementation_patch_set', 'execution_evidence')
        fresh_context_boundary = $true
        durable_worker_default = 'team-executor'
        read_only_default = $false
        persistence_mode_default = 'per_invocation'
        checkpointer_mode_default = 'inherit_parent'
        state_inspection_default = $true
        state_inspection_scope_default = 'current_invocation'
        static_discoverable = $true
        same_subgraph_parallel_calls_supported = $true
        allowed_parent_graph_scopes = @('parent')
      }
      verification = [ordered]@{
        subgraph_id = 'verification'
        role_family = 'verification'
        roles = @('verifier', 'test-engineer', 'security-reviewer', 'writer')
        default_phase = 'verify-accept'
        phase_families = @('verify-accept')
        input_artifacts = @('implementation_patch_set', 'execution_evidence')
        output_artifacts = @('verification_report')
        handoff_artifacts = @('verification_report')
        fresh_context_boundary = $true
        durable_worker_default = ''
        read_only_default = $true
        persistence_mode_default = 'stateless'
        checkpointer_mode_default = 'disabled'
        state_inspection_default = $false
        state_inspection_scope_default = 'unavailable'
        static_discoverable = $true
        same_subgraph_parallel_calls_supported = $true
        allowed_parent_graph_scopes = @('parent')
      }
      'adversarial-review' = [ordered]@{
        subgraph_id = 'adversarial-review'
        role_family = 'adversarial-review'
        roles = @('bug-finder', 'bug-rebutter', 'bug-judge')
        default_phase = 'verify-accept'
        phase_families = @()
        input_artifacts = @('implementation_patch_set', 'execution_evidence')
        output_artifacts = @('judge_approved_survivor_queue')
        handoff_artifacts = @('judge_approved_survivor_queue')
        fresh_context_boundary = $true
        durable_worker_default = ''
        read_only_default = $true
        persistence_mode_default = 'stateless'
        checkpointer_mode_default = 'disabled'
        state_inspection_default = $false
        state_inspection_scope_default = 'unavailable'
        static_discoverable = $true
        same_subgraph_parallel_calls_supported = $true
        allowed_parent_graph_scopes = @('parent')
      }
    }
    implementation_brief_fields = @('brief_id', 'thread_id', 'objective', 'non_goals', 'accepted_decisions', 'constraints', 'interfaces', 'ownership_boundaries', 'acceptance_criteria', 'validation_plan', 'source_evidence_refs', 'frozen_at')
    survivor_queue_fields = @('bug_id', 'title', 'severity', 'evidence', 'judge_verdict', 'owner_lane', 'status', 'verification_result', 'updated_at')
    interrupt_points = @('freeze-plan', 'stabilize-risk-review', 'verify-accept-failed')
    gate_verdicts = @('accept', 'revise', 'escalate', 'halt', 'needs_human')
    loop_projection_fields = @('active_loop', 'loop_stage', 'iteration_count', 'iteration_budget', 'last_gate_verdict', 'last_gate_reason', 'stop_reason')
    history_projection_fields = @('compatibility', 'history_path', 'history_record_count', 'target_count', 'available_targets', 'source_records')
    history_compatibility_states = @('tracked_history', 'synthetic_latest_only', 'no_history')
    recovery_postures = @('ordinary', 'recovered_pending_resume')
    recovery_mutation_intents = @('explicit-recovery')
    recoverable_thread_fields = @('phase', 'status', 'parallel_slices', 'blocking_issues', 'active_loop', 'loop_stage', 'iteration_count', 'iteration_budget', 'last_gate_verdict', 'last_gate_reason', 'stop_reason')
    recoverable_interrupt_fields = @('interrupt_point', 'status', 'reason')
    recovery_projection_fields = @('posture', 'last_action', 'target_id', 'recovered_at', 'source_records', 'recoverable_fields_touched')
    loop_capable_flows = @(
      [ordered]@{
        name = 'review'
        entry_phase = 'execute-parallel'
        initial_stage = 'draft'
        accept_phase = 'integrate-converge'
      }
      [ordered]@{
        name = 'execution'
        entry_phase = 'execute-parallel'
        initial_stage = 'execute'
        accept_phase = 'integrate-converge'
      }
      [ordered]@{
        name = 'stabilization'
        entry_phase = 'stabilize'
        initial_stage = 'stabilize'
        accept_phase = 'verify-accept'
      }
    )
    reducer_merge_channels = [ordered]@{
      branch_findings = [ordered]@{ reducer_kind = 'dedupe_append'; identity_field = 'finding_id' }
      branch_evidence_refs = [ordered]@{ reducer_kind = 'dedupe_append'; identity_field = 'evidence_id' }
      branch_artifact_pointers = [ordered]@{ reducer_kind = 'dedupe_append'; identity_field = 'artifact_id' }
      branch_completion_records = [ordered]@{ reducer_kind = 'replace_by_branch'; identity_field = 'branch_id' }
      branch_warnings = [ordered]@{ reducer_kind = 'dedupe_append'; identity_field = 'warning_id' }
      branch_blockers = [ordered]@{ reducer_kind = 'dedupe_append'; identity_field = 'blocker_id' }
    }
    single_writer_fields = @('thread_id', 'repo_root', 'worktree_id', 'task', 'phase', 'parallel_slices', 'blocking_issues', 'backend', 'langgraph_available', 'status', 'updated_at')
    leader_owned_summary_fields = @('final_summary', 'accepted_outcome', 'leader_summary')
    reducer_projection_fields = @('compatibility', 'reducer_channels_present', 'fanout_state', 'invalid_multi_writer_detected', 'invalid_multi_writer_updates', 'merge_channels_updated', 'channel_item_counts', 'source_records')
    reducer_compatibility_states = @('reducer_aware', 'pre_reducer')
    thread_id_contract = '<repo-hash>:<worktree-id>:<task-id>'
  }
}

function Get-CodexUserLevelTeamStateRoot {
  param(
    [string]$RepoRoot
  )

  $resolvedRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
  return (Join-Path (Join-Path $resolvedRoot '.omx\state') 'team')
}

function Resolve-CodexUserLevelLatestTeamName {
  param(
    [string]$RepoRoot
  )

  $teamStateRoot = Get-CodexUserLevelTeamStateRoot -RepoRoot $RepoRoot
  if (-not (Test-Path -LiteralPath $teamStateRoot)) {
    throw "Team state root not found: $teamStateRoot"
  }

  $teamDirectories = @(Get-ChildItem -LiteralPath $teamStateRoot -Directory | Sort-Object LastWriteTimeUtc -Descending)
  if ($teamDirectories.Count -lt 1) {
    throw "No team state directories found under: $teamStateRoot"
  }

  return $teamDirectories[0].Name
}

function Resolve-CodexUserLevelTeamName {
  param(
    [string]$RequestedTeamName,
    [string]$RepoRoot
  )

  if (-not [string]::IsNullOrWhiteSpace($RequestedTeamName)) {
    return $RequestedTeamName
  }

  return (Resolve-CodexUserLevelLatestTeamName -RepoRoot $RepoRoot)
}

function Get-CodexUserLevelTrackedTeamRecordRelativePath {
  return '.omx\state\team\codex-auto-managed-team.json'
}

function Get-CodexUserLevelTrackedTeamRecordPath {
  param(
    [string]$RepoRoot
  )

  $resolvedRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
  return (Join-Path $resolvedRoot (Get-CodexUserLevelTrackedTeamRecordRelativePath))
}

function Get-CodexUserLevelTeamDirectoryNames {
  param(
    [string]$RepoRoot
  )

  $teamStateRoot = Get-CodexUserLevelTeamStateRoot -RepoRoot $RepoRoot
  if (-not (Test-Path -LiteralPath $teamStateRoot)) {
    return @()
  }

  return @(
    Get-ChildItem -LiteralPath $teamStateRoot -Directory |
      Sort-Object LastWriteTimeUtc -Descending |
      ForEach-Object { [string]$_.Name }
  )
}

function Test-CodexUserLevelTeamDirectoryExists {
  param(
    [string]$RepoRoot,
    [string]$TeamName
  )

  if ([string]::IsNullOrWhiteSpace($TeamName)) {
    return $false
  }

  $teamDirectory = Join-Path (Get-CodexUserLevelTeamStateRoot -RepoRoot $RepoRoot) $TeamName
  return (Test-Path -LiteralPath $teamDirectory)
}

function Read-CodexUserLevelTrackedTeamRecord {
  param(
    [string]$RepoRoot
  )

  $recordPath = Get-CodexUserLevelTrackedTeamRecordPath -RepoRoot $RepoRoot
  $resolvedRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
  $record = [ordered]@{
    exists = $false
    stale = $false
    path = $recordPath
    repo_root = $resolvedRoot
    team_name = ''
    worker_role = ''
    worker_count = 0
    phase = ''
    managed_by = ''
    updated_at = ''
  }

  if (-not (Test-Path -LiteralPath $recordPath)) {
    return $record
  }

  $loaded = Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
  $record.exists = $true
  $record.team_name = if ($null -ne $loaded.PSObject.Properties['team_name'] -and $null -ne $loaded.team_name) { [string]$loaded.team_name } else { '' }
  $record.worker_role = if ($null -ne $loaded.PSObject.Properties['worker_role'] -and $null -ne $loaded.worker_role) { [string]$loaded.worker_role } else { '' }
  $record.worker_count = if ($null -ne $loaded.PSObject.Properties['worker_count'] -and $null -ne $loaded.worker_count) { [int]$loaded.worker_count } else { 0 }
  $record.phase = if ($null -ne $loaded.PSObject.Properties['phase'] -and $null -ne $loaded.phase) { [string]$loaded.phase } else { '' }
  $record.managed_by = if ($null -ne $loaded.PSObject.Properties['managed_by'] -and $null -ne $loaded.managed_by) { [string]$loaded.managed_by } else { '' }
  $record.updated_at = if ($null -ne $loaded.PSObject.Properties['updated_at'] -and $null -ne $loaded.updated_at) { [string]$loaded.updated_at } else { '' }

  if (-not (Test-CodexUserLevelTeamDirectoryExists -RepoRoot $resolvedRoot -TeamName $record.team_name)) {
    $record.exists = $false
    $record.stale = $true
  }

  return $record
}

function Get-CodexUserLevelLatestTeamDirectoryMetadata {
  param(
    [string]$RepoRoot
  )

  $teamStateRoot = Get-CodexUserLevelTeamStateRoot -RepoRoot $RepoRoot
  $result = [ordered]@{
    exists = $false
    team_name = ''
    path = ''
    updated_at = ''
  }

  if (-not (Test-Path -LiteralPath $teamStateRoot)) {
    return $result
  }

  $teamDirectory = Get-ChildItem -LiteralPath $teamStateRoot -Directory | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
  if ($null -eq $teamDirectory) {
    return $result
  }

  $result.exists = $true
  $result.team_name = [string]$teamDirectory.Name
  $result.path = [string]$teamDirectory.FullName
  $result.updated_at = $teamDirectory.LastWriteTimeUtc.ToString('o')
  return $result
}

function Get-CodexUserLevelNativeTeamDirectoriesMetadata {
  param(
    [string]$RepoRoot
  )

  $teamStateRoot = Get-CodexUserLevelTeamStateRoot -RepoRoot $RepoRoot
  if (-not (Test-Path -LiteralPath $teamStateRoot)) {
    return @()
  }

  return @(
    Get-ChildItem -LiteralPath $teamStateRoot -Directory |
      Sort-Object LastWriteTimeUtc -Descending |
      ForEach-Object {
        $files = @(Get-ChildItem -LiteralPath $_.FullName -Recurse -Force -File -ErrorAction SilentlyContinue)
        [ordered]@{
          team_name = [string]$_.Name
          path = [string]$_.FullName
          file_count = $files.Count
          empty = ($files.Count -eq 0)
          updated_at = $_.LastWriteTimeUtc.ToString('o')
        }
      }
  )
}

function Get-CodexUserLevelLangGraphRuntimePresence {
  param(
    [string]$RepoRoot
  )

  $layout = Get-CodexUserLevelLangGraphRuntimeLayout -RepoRoot $RepoRoot
  $signalPaths = @()
  foreach ($key in @('backend_record', 'threads', 'checkpoints', 'history', 'interrupts', 'store')) {
    $path = [string]$layout[$key]
    if (-not (Test-Path -LiteralPath $path)) {
      continue
    }

    if ($key -eq 'backend_record') {
      $signalPaths += $path
      continue
    }

    $items = @(Get-ChildItem -LiteralPath $path -Force -ErrorAction SilentlyContinue)
    if ($items.Count -gt 0) {
      $signalPaths += $path
    }
  }

  return [ordered]@{
    present = ($signalPaths.Count -gt 0)
    layout = $layout
    signal_paths = $signalPaths
  }
}

function Get-CodexUserLevelInspectableDurableStateSurfaceContract {
  return [ordered]@{
    primary_operator_surface = 'codex-durable-state-status.ps1'
    reconciliation_operator_surface = 'codex-durable-state-reconcile.ps1'
    backend_helpers = @('omx-team-ops.ps1', 'omx-team-compose.ps1', 'omx-team-compose-status.ps1', 'omx-team-compose-await.ps1', 'omx-team-compose-recover.ps1', 'omx-team-compose-shutdown.ps1', 'omx-team-compose-reconcile.ps1', 'omx-langgraph-inspect.ps1', 'omx-langgraph-kernel.ps1', 'omx-langgraph-engine.ps1', 'omx-langgraph-invocation.ps1', 'omx-langgraph-live-execution.ps1', 'omx-langgraph-fuller-engine.ps1', 'omx-langgraph-deeper-engine.ps1', 'omx-langgraph-superstep-engine.ps1', 'omx-langgraph-stateful-engine.ps1', 'omx-langgraph-boundary-engine.ps1', 'omx-langgraph-handoff-engine.ps1', 'omx-langgraph-approval-engine.ps1', 'omx-langgraph-provenance-engine.ps1', 'omx-langgraph-artifact-engine.ps1', 'omx-langgraph-reducer-engine.ps1', 'omx-langgraph-command-engine.ps1', 'omx-langgraph-runtime-engine.ps1', 'omx-langgraph-memory-engine.ps1', 'omx-langgraph-migration-engine.ps1', 'omx-langgraph-auto-policy.ps1', 'omx-langgraph-subgraph-state.ps1', 'omx-langgraph-generalized-routing.ps1', 'omx-langgraph-approval-queue.ps1', 'omx-langgraph-migration.ps1', 'omx-langgraph-memory.ps1', 'omx-langgraph-runtime.ps1', 'omx-langgraph-stream.ps1', 'omx-langgraph-subgraphs.ps1', 'omx-langgraph-history.ps1', 'omx-langgraph-replay.ps1', 'omx-langgraph-recover.ps1')
    read_only_by_default = $true
    minimum_fields = @(
      'backend_family'
      'state_class'
      'repo_root'
      'tracked_identity'
      'current_phase'
      'worker_shape'
      'active_blockers'
      'next_step'
      'inspect_pointer'
      'resume_pointer'
      'state_sources'
      'updated_at'
      'selected_backend'
      'capability_readiness'
    )
    readiness_fields = @(
      'installed'
      'enabled'
      'selected'
      'ready'
    )
    langgraph_projection_fields = @(
      'active_loop'
      'loop_stage'
      'iteration_count'
      'iteration_budget'
      'last_gate_verdict'
      'last_gate_reason'
      'stop_reason'
    )
    langgraph_kernel_projection_fields = @(
      'kernel_identity'
      'current_node_id'
      'mapped_phase'
      'node_posture'
      'current_node'
      'available_next_nodes'
      'last_transition'
      'helper_pointer'
    )
    langgraph_primary_runtime_engine_projection_fields = @(
      'engine_identity'
      'compile_supported'
      'compiled_graph_present'
      'checkpointer_expected'
      'entry_node'
      'finish_nodes'
      'current_execution_node'
      'mapped_phase'
      'execution_posture'
      'last_execution_reason'
      'helper_pointer'
    )
    langgraph_compiled_invocation_projection_fields = @(
      'invocation_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'compiled_node_count'
      'compiled_edge_count'
      'current_execution_node'
      'mapped_phase'
      'invocation_posture'
      'last_invoke_kind'
      'last_invoke_reason'
      'helper_pointer'
    )
    langgraph_live_execution_projection_fields = @(
      'execution_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'current_execution_node'
      'mapped_phase'
      'execution_posture'
      'last_run_kind'
      'last_run_status'
      'last_run_reason'
      'last_output_keys'
      'last_stream_event_count'
      'helper_pointer'
    )
    langgraph_fuller_live_primary_engine_projection_fields = @(
      'engine_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'current_execution_node'
      'mapped_phase'
      'execution_node_path'
      'resulting_phase'
      'resulting_status'
      'phase_transition_kind'
      'execution_posture'
      'last_run_kind'
      'last_run_status'
      'last_run_reason'
      'helper_pointer'
    )
    langgraph_deeper_live_primary_engine_projection_fields = @(
      'engine_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'current_execution_node'
      'mapped_phase'
      'projected_node_path'
      'projected_phase_path'
      'planned_supersteps'
      'stop_boundary'
      'terminal_reached'
      'recursion_limit_supported'
      'remaining_steps_supported'
      'recursion_limit'
      'execution_posture'
      'last_run_kind'
      'last_run_status'
      'last_run_reason'
      'helper_pointer'
    )
    langgraph_superstep_live_primary_engine_projection_fields = @(
      'engine_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'current_execution_node'
      'mapped_phase'
      'node_visit_path'
      'phase_visit_path'
      'superstep_count'
      'stop_boundary'
      'terminal_reached'
      'recursion_limit_supported'
      'remaining_steps_supported'
      'recursion_limit'
      'execution_posture'
      'last_run_kind'
      'last_run_status'
      'last_run_reason'
      'helper_pointer'
    )
    langgraph_stateful_live_primary_engine_projection_fields = @(
      'engine_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'current_execution_node'
      'mapped_phase'
      'stateful_node_path'
      'stateful_phase_path'
      'stateful_transition_log'
      'superstep_count'
      'stop_boundary'
      'terminal_reached'
      'recursion_limit_supported'
      'remaining_steps_supported'
      'recursion_limit'
      'execution_posture'
      'last_run_kind'
      'last_run_status'
      'last_run_reason'
      'helper_pointer'
    )
    langgraph_boundary_state_live_primary_engine_projection_fields = @(
      'engine_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'current_execution_node'
      'mapped_phase'
      'boundary_node_path'
      'boundary_phase_path'
      'boundary_transition_log'
      'boundary_state_kind'
      'superstep_count'
      'stop_boundary'
      'terminal_reached'
      'recursion_limit_supported'
      'remaining_steps_supported'
      'recursion_limit'
      'execution_posture'
      'last_run_kind'
      'last_run_status'
      'last_run_reason'
      'helper_pointer'
    )
    langgraph_handoff_state_live_primary_engine_projection_fields = @(
      'engine_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'current_execution_node'
      'mapped_phase'
      'handoff_node_path'
      'handoff_phase_path'
      'handoff_subgraph_path'
      'handoff_transition_log'
      'handoff_state_kind'
      'active_subgraph'
      'source_subgraph'
      'target_subgraph'
      'parent_handoff_target'
      'graph_scope'
      'superstep_count'
      'stop_boundary'
      'terminal_reached'
      'recursion_limit_supported'
      'remaining_steps_supported'
      'recursion_limit'
      'execution_posture'
      'last_run_kind'
      'last_run_status'
      'last_run_reason'
      'helper_pointer'
    )
    langgraph_approval_aware_live_primary_engine_projection_fields = @(
      'engine_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'current_execution_node'
      'mapped_phase'
      'approval_node_path'
      'approval_phase_path'
      'approval_transition_log'
      'resume_state_kind'
      'queue_posture'
      'pending_count'
      'resolved_count'
      'current_interrupt_id'
      'resume_map_keys'
      'superstep_count'
      'stop_boundary'
      'terminal_reached'
      'recursion_limit_supported'
      'remaining_steps_supported'
      'recursion_limit'
      'execution_posture'
      'last_run_kind'
      'last_run_status'
      'last_run_reason'
      'helper_pointer'
    )
    langgraph_provenance_state_live_primary_engine_projection_fields = @(
      'engine_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'current_execution_node'
      'mapped_phase'
      'provenance_node_path'
      'provenance_phase_path'
      'provenance_transition_log'
      'provenance_state_kind'
      'recovery_posture'
      'recovery_action'
      'recovery_target_id'
      'recovery_target_kind'
      'source_records'
      'recoverable_fields_touched'
      'history_compatibility'
      'history_target_count'
      'superstep_count'
      'stop_boundary'
      'terminal_reached'
      'recursion_limit_supported'
      'remaining_steps_supported'
      'recursion_limit'
      'execution_posture'
      'last_run_kind'
      'last_run_status'
      'last_run_reason'
      'helper_pointer'
    )
    langgraph_durable_artifact_aware_live_primary_engine_projection_fields = @(
      'engine_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'current_execution_node'
      'mapped_phase'
      'artifact_node_path'
      'artifact_phase_path'
      'artifact_transition_log'
      'artifact_state_kind'
      'implementation_brief_present'
      'implementation_brief_id'
      'implementation_brief_source_evidence_ref_count'
      'survivor_queue_present'
      'survivor_queue_kind'
      'survivor_count'
      'superstep_count'
      'stop_boundary'
      'terminal_reached'
      'recursion_limit_supported'
      'remaining_steps_supported'
      'recursion_limit'
      'execution_posture'
      'last_run_kind'
      'last_run_status'
      'last_run_reason'
      'helper_pointer'
    )
    langgraph_reducer_aware_live_primary_engine_projection_fields = @(
      'engine_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'current_execution_node'
      'mapped_phase'
      'merge_node_path'
      'merge_phase_path'
      'merge_transition_log'
      'merge_state_kind'
      'reducer_compatibility'
      'fanout_state'
      'invalid_multi_writer_detected'
      'invalid_multi_writer_updates'
      'merge_channels_updated'
      'channel_item_counts'
      'source_records'
      'superstep_count'
      'stop_boundary'
      'terminal_reached'
      'recursion_limit_supported'
      'remaining_steps_supported'
      'recursion_limit'
      'execution_posture'
      'last_run_kind'
      'last_run_status'
      'last_run_reason'
      'helper_pointer'
    )
    langgraph_command_aware_live_primary_engine_projection_fields = @(
      'engine_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'current_execution_node'
      'mapped_phase'
      'command_node_path'
      'command_phase_path'
      'command_transition_log'
      'control_state_kind'
      'transition_kind'
      'update_keys'
      'goto_target'
      'graph_scope'
      'source_subgraph'
      'target_subgraph'
      'parent_handoff_target'
      'resume_posture'
      'resume_payload_present'
      'resume_payload_keys'
      'superstep_count'
      'stop_boundary'
      'terminal_reached'
      'recursion_limit_supported'
      'remaining_steps_supported'
      'recursion_limit'
      'execution_posture'
      'last_run_kind'
      'last_run_status'
      'last_run_reason'
      'helper_pointer'
    )
    langgraph_runtime_aware_live_primary_engine_projection_fields = @(
      'engine_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'current_execution_node'
      'mapped_phase'
      'runtime_node_path'
      'runtime_phase_path'
      'runtime_transition_log'
      'runtime_state_kind'
      'context_schema'
      'runtime_context_present'
      'runtime_context_keys'
      'runtime_context_kind_hints'
      'store_configured'
      'store_access_expected'
      'store_kind'
      'superstep_count'
      'stop_boundary'
      'terminal_reached'
      'recursion_limit_supported'
      'remaining_steps_supported'
      'recursion_limit'
      'execution_posture'
      'last_run_kind'
      'last_run_status'
      'last_run_reason'
      'helper_pointer'
    )
    langgraph_memory_aware_live_primary_engine_projection_fields = @(
      'engine_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'current_execution_node'
      'mapped_phase'
      'memory_node_path'
      'memory_phase_path'
      'memory_transition_log'
      'memory_state_kind'
      'memory_store_configured'
      'memory_store_kind'
      'memory_namespaces'
      'semantic_memory_enabled'
      'semantic_store_kind'
      'semantic_namespaces'
      'superstep_count'
      'stop_boundary'
      'terminal_reached'
      'recursion_limit_supported'
      'remaining_steps_supported'
      'recursion_limit'
      'execution_posture'
      'last_run_kind'
      'last_run_status'
      'last_run_reason'
      'helper_pointer'
    )
    langgraph_migration_aware_live_primary_engine_projection_fields = @(
      'engine_identity'
      'compile_supported'
      'compiled_graph_present'
      'invoke_supported'
      'stream_supported'
      'current_execution_node'
      'mapped_phase'
      'compatibility_node_path'
      'compatibility_phase_path'
      'compatibility_transition_log'
      'compatibility_state_kind'
      'current_graph_contract'
      'thread_graph_contract'
      'topology_compatibility'
      'state_schema_compatibility'
      'compatibility'
      'reason_codes'
      'superstep_count'
      'stop_boundary'
      'terminal_reached'
      'recursion_limit_supported'
      'remaining_steps_supported'
      'recursion_limit'
      'execution_posture'
      'last_run_kind'
      'last_run_status'
      'last_run_reason'
      'helper_pointer'
    )
    langgraph_automatic_runtime_policy_projection_fields = @(
      'policy_identity'
      'migration_policy_posture'
      'approval_policy_posture'
      'recovery_policy_posture'
      'automatic_actions_available'
      'safe_to_auto_apply'
      'last_auto_action'
      'last_auto_reason'
      'helper_pointer'
    )
    langgraph_generalized_live_routing_projection_fields = @(
      'routing_identity'
      'compile_supported'
      'compiled_graph_present'
      'route_posture'
      'current_route'
      'candidate_routes'
      'selected_route'
      'loop_route_kind'
      'current_execution_node'
      'mapped_phase'
      'next_execution_nodes'
      'approval_route_pending'
      'helper_pointer'
    )
    langgraph_approval_queue_projection_fields = @(
      'queue_posture'
      'queue_size'
      'pending_count'
      'resolved_count'
      'pending_interrupt_ids'
      'resolved_interrupt_ids'
      'current_interrupt_id'
      'resume_map_keys'
      'queue_items'
      'helper_pointer'
    )
    langgraph_migration_projection_fields = @(
      'current_graph_contract'
      'thread_graph_contract'
      'topology_compatibility'
      'state_schema_compatibility'
      'compatibility'
      'reason_codes'
      'helper_pointer'
    )
    langgraph_subgraph_projection_fields = @(
      'active_subgraph'
      'active_subgraph_posture'
      'available_subgraphs'
      'helper_pointer'
    )
    langgraph_subgraph_state_inspection_projection_fields = @(
      'active_subgraph'
      'persistence_mode'
      'checkpointer_mode'
      'inherits_parent_checkpointer'
      'separate_subgraph_memory'
      'durable_execution_supported'
      'interrupts_supported'
      'state_inspection_available'
      'state_inspection_scope'
      'static_discoverable'
      'same_subgraph_parallel_calls_supported'
      'inspection_blockers'
      'helper_pointer'
    )
    langgraph_command_projection_fields = @(
      'transition_kind'
      'update_keys'
      'goto_target'
      'graph_scope'
      'source_subgraph'
      'target_subgraph'
      'parent_handoff_target'
      'resume_posture'
      'resume_payload_present'
      'resume_payload_keys'
      'helper_pointer'
    )
    langgraph_stream_projection_fields = @(
      'selected_modes'
      'subgraphs'
      'latest_event_kind'
      'latest_namespace'
      'latest_checkpoint_kind'
      'latest_task_path'
      'latest_task_status'
      'latest_debug_summary'
      'event_count'
      'helper_pointer'
    )
    langgraph_runtime_injection_projection_fields = @(
      'context_schema'
      'runtime_context_present'
      'runtime_context_keys'
      'runtime_context_kind_hints'
      'store_configured'
      'store_access_expected'
      'store_kind'
      'helper_pointer'
    )
    langgraph_memory_projection_fields = @(
      'memory_store_configured'
      'memory_store_kind'
      'memory_namespaces'
      'semantic_memory_enabled'
      'semantic_store_kind'
      'semantic_namespaces'
      'helper_pointer'
    )
    langgraph_history_projection_fields = @(
      'compatibility'
      'history_path'
      'history_record_count'
      'target_count'
      'available_targets'
      'source_records'
    )
    langgraph_recovery_projection_fields = @(
      'posture'
      'last_action'
      'target_id'
      'recovered_at'
      'source_records'
      'recoverable_fields_touched'
    )
    langgraph_reducer_projection_fields = @(
      'compatibility'
      'reducer_channels_present'
      'fanout_state'
      'invalid_multi_writer_detected'
      'invalid_multi_writer_updates'
      'merge_channels_updated'
      'channel_item_counts'
      'source_records'
    )
    state_classes = @(
      'no_durable_state'
      'tracked_compose_runtime'
      'tracked_native_team'
      'tracked_langgraph_thread'
      'preserved_legacy_native_team_artifact'
      'preserved_legacy_langgraph_artifact'
      'stale_tracked_record'
      'unmanaged_durable_state_detected'
      'multiple_durable_states_detected'
    )
    authority_sources = @(
      '.omx/state/compose/current-compose-runtime.json'
      '.omx/state/selectors/active.json'
      '.omx/state/selectors/leases/'
      '.omx/state/team/codex-auto-managed-team.json'
      '.omx/state/team/'
      '.omx/state/langgraph/backend.json'
      '.omx/state/langgraph/history/'
      '.omx/state/langgraph/'
    )
  }
}

function Get-CodexUserLevelComposeStateRoot {
  param(
    [string]$RepoRoot
  )

  $resolvedRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
  return (Join-Path (Join-Path $resolvedRoot '.omx\state') 'compose')
}

function Ensure-CodexUserLevelComposeStateRoot {
  param(
    [string]$RepoRoot
  )

  $stateRoot = Get-CodexUserLevelComposeStateRoot -RepoRoot $RepoRoot
  if (-not (Test-Path -LiteralPath $stateRoot)) {
    New-Item -ItemType Directory -Force -Path $stateRoot | Out-Null
  }

  return $stateRoot
}

function Get-CodexUserLevelComposePlanStateFilePath {
  param(
    [string]$RepoRoot
  )

  return (Join-Path (Get-CodexUserLevelComposeStateRoot -RepoRoot $RepoRoot) 'current-compose-plan.json')
}

function Get-CodexUserLevelComposeRuntimeStateFilePath {
  param(
    [string]$RepoRoot
  )

  return (Join-Path (Get-CodexUserLevelComposeStateRoot -RepoRoot $RepoRoot) 'current-compose-runtime.json')
}

function Read-CodexUserLevelComposeRuntimeState {
  param(
    [string]$RepoRoot
  )

  $resolvedRepoRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
  $runtimePath = Get-CodexUserLevelComposeRuntimeStateFilePath -RepoRoot $resolvedRepoRoot
  $planPath = Get-CodexUserLevelComposePlanStateFilePath -RepoRoot $resolvedRepoRoot

  if (-not (Test-Path -LiteralPath $runtimePath)) {
    return [ordered]@{
      exists = $false
      path = $runtimePath
      plan_path = $planPath
      repo_root = $resolvedRepoRoot
      runtime_id = ''
      applied_mode = ''
      backend_family = 'native_omx'
      launched_panes = @()
      planned_only_panes = @()
      failed_panes = @()
      pane_results = @()
      updated_at = ''
    }
  }

  $runtime = Get-Content -LiteralPath $runtimePath -Raw | ConvertFrom-Json
  return [ordered]@{
    exists = $true
    path = $runtimePath
    plan_path = $planPath
    repo_root = $resolvedRepoRoot
    runtime_id = if ($null -ne $runtime.PSObject.Properties['runtime_id']) { [string]$runtime.runtime_id } else { '' }
    applied_mode = if ($null -ne $runtime.PSObject.Properties['applied_mode']) { [string]$runtime.applied_mode } else { '' }
    backend_family = if ($null -ne $runtime.PSObject.Properties['backend_family']) { [string]$runtime.backend_family } else { 'native_omx' }
    launched_panes = if ($null -ne $runtime.PSObject.Properties['launched_panes']) { @($runtime.launched_panes) } else { @() }
    planned_only_panes = if ($null -ne $runtime.PSObject.Properties['planned_only_panes']) { @($runtime.planned_only_panes) } else { @() }
    failed_panes = if ($null -ne $runtime.PSObject.Properties['failed_panes']) { @($runtime.failed_panes) } else { @() }
    pane_results = if ($null -ne $runtime.PSObject.Properties['pane_results']) { @($runtime.pane_results) } else { @() }
    updated_at = if ($null -ne $runtime.PSObject.Properties['updated_at']) { [string]$runtime.updated_at } else { '' }
  }
}

function Get-CodexUserLevelComposeRuntimeLifecyclePlan {
  param(
    [string]$RepoRoot
  )

  $resolvedRepoRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
  $runtime = Read-CodexUserLevelComposeRuntimeState -RepoRoot $resolvedRepoRoot
  $statusPointer = [ordered]@{
    script = 'omx-team-compose-status.ps1'
    arguments = @('-RepoRoot', $resolvedRepoRoot, '-Json')
  }
  $awaitPointer = [ordered]@{
    script = 'omx-team-compose-await.ps1'
    arguments = @('-RepoRoot', $resolvedRepoRoot, '-Json')
  }
  $recoverPointer = [ordered]@{
    script = 'omx-team-compose-recover.ps1'
    arguments = @('-RepoRoot', $resolvedRepoRoot, '-Json')
  }
  $shutdownPointer = [ordered]@{
    script = 'omx-team-compose-shutdown.ps1'
    arguments = @('-RepoRoot', $resolvedRepoRoot, '-Json')
  }
  $shutdownApplyPointer = [ordered]@{
    script = 'omx-team-compose-shutdown.ps1'
    arguments = @('-RepoRoot', $resolvedRepoRoot, '-Apply', '-Json')
  }
  $reconcilePointer = [ordered]@{
    script = 'omx-team-compose-reconcile.ps1'
    arguments = @('-RepoRoot', $resolvedRepoRoot, '-Json')
  }
  $reconcileApplyPointer = [ordered]@{
    script = 'omx-team-compose-reconcile.ps1'
    arguments = @('-RepoRoot', $resolvedRepoRoot, '-Apply', '-Json')
  }

  $paneHelpers = @()
  foreach ($pane in @($runtime.launched_panes)) {
    $teamName = if ($null -ne $pane.PSObject.Properties['team_name']) { [string]$pane.team_name } else { '' }
    $teamExists = (-not [string]::IsNullOrWhiteSpace($teamName) -and (Test-CodexUserLevelTeamDirectoryExists -RepoRoot $resolvedRepoRoot -TeamName $teamName))
    $paneHelpers += [ordered]@{
      name = if ($null -ne $pane.PSObject.Properties['name']) { [string]$pane.name } else { '' }
      role = if ($null -ne $pane.PSObject.Properties['role']) { [string]$pane.role } else { '' }
      team_name = $teamName
      team_exists = $teamExists
      status_pointer = if ($teamExists) { [ordered]@{
        script = 'omx-team-ops.ps1'
        arguments = @('-Action', 'status', '-TeamName', $teamName, '-RepoRoot', $resolvedRepoRoot, '-Json')
      } } else { $null }
      resume_pointer = if ($teamExists) { [ordered]@{
        script = 'omx-team-ops.ps1'
        arguments = @('-Action', 'resume', '-TeamName', $teamName, '-RepoRoot', $resolvedRepoRoot)
      } } else { $null }
      shutdown_pointer = if ($teamExists) { [ordered]@{
        script = 'omx-team-ops.ps1'
        arguments = @('-Action', 'shutdown', '-TeamName', $teamName, '-RepoRoot', $resolvedRepoRoot)
      } } else { $null }
    }
  }

  $safeCleanupCandidates = @()
  $protectedResidue = @()
  $lifecycleState = 'no_tracked_runtime'
  $healthState = 'none'
  $awaitState = 'no_runtime'
  $recoveryPosture = 'no_runtime'
  $recoveryReasons = @()
  if ([bool]$runtime.exists) {
    $launchedPaneHelpers = @($paneHelpers)
    $existingPaneHelpers = @($launchedPaneHelpers | Where-Object { [bool]$_.team_exists })
    $missingPaneHelpers = @(
      $launchedPaneHelpers |
        Where-Object {
          (-not [bool]$_.team_exists) -and
          (-not [string]::IsNullOrWhiteSpace([string]$_.team_name))
        }
    )

    if ($launchedPaneHelpers.Count -gt 0 -and $existingPaneHelpers.Count -eq 0 -and $missingPaneHelpers.Count -eq $launchedPaneHelpers.Count) {
      $safeCleanupCandidates += [ordered]@{
        kind = 'stale_compose_runtime_record'
        path = [string]$runtime.path
        plan_path = [string]$runtime.plan_path
        runtime_id = [string]$runtime.runtime_id
        missing_team_names = @($missingPaneHelpers | ForEach-Object { [string]$_.team_name })
        reason = 'tracked compose runtime references only missing launched pane teams'
      }
    } elseif ($missingPaneHelpers.Count -gt 0) {
      $protectedResidue += [ordered]@{
        kind = 'partially_missing_compose_runtime_teams'
        path = [string]$runtime.path
        runtime_id = [string]$runtime.runtime_id
        missing_team_names = @($missingPaneHelpers | ForEach-Object { [string]$_.team_name })
        existing_team_names = @($existingPaneHelpers | ForEach-Object { [string]$_.team_name })
        reason = 'tracked compose runtime references both existing and missing launched pane teams'
      }
    }

    $trackedLaunchedCount = @($launchedPaneHelpers).Count
    $existingCount = @($existingPaneHelpers).Count
    $missingCount = @($missingPaneHelpers).Count
    $failedCount = @($runtime.failed_panes).Count

    if ($trackedLaunchedCount -eq 0) {
      $lifecycleState = 'no_launched_panes'
      $awaitState = 'no_launched_panes'
      $healthState = if ($failedCount -gt 0) { 'partial_health' } else { 'planned_only' }
    } elseif ($existingCount -eq $trackedLaunchedCount) {
      $lifecycleState = 'fully_active'
      $awaitState = 'active'
      $healthState = if ($failedCount -gt 0) { 'partial_health' } else { 'healthy' }
    } elseif ($existingCount -gt 0 -and $missingCount -gt 0) {
      $lifecycleState = 'partial_shutdown'
      $awaitState = 'partial'
      $healthState = 'partial_health'
    } elseif ($existingCount -eq 0 -and $missingCount -eq $trackedLaunchedCount) {
      $lifecycleState = 'fully_quiesced'
      $awaitState = 'quiesced'
      $healthState = if ($failedCount -gt 0) { 'partial_health' } else { 'quiesced' }
    }

    if (@($existingPaneHelpers).Count -gt 0 -and @($missingPaneHelpers).Count -eq 0 -and $failedCount -eq 0) {
      $recoveryPosture = 'resumable'
      $recoveryReasons += 'all launched panes remain resumable'
    } elseif (@($existingPaneHelpers).Count -gt 0) {
      $recoveryPosture = 'degraded_recoverable'
      if (@($missingPaneHelpers).Count -gt 0) {
        $recoveryReasons += 'some launched panes are missing'
      }
      if ($failedCount -gt 0) {
        $recoveryReasons += 'failed pane records are present'
      }
    } else {
      $recoveryPosture = 'manual_intervention_required'
      if ($trackedLaunchedCount -gt 0) {
        $recoveryReasons += 'no launched pane remains resumable'
      }
      if ($failedCount -gt 0) {
        $recoveryReasons += 'failed pane records are present'
      }
      if ($trackedLaunchedCount -eq 0 -and @($runtime.planned_only_panes).Count -gt 0) {
        $recoveryReasons += 'tracked compose runtime has no launched panes to resume'
      }
    }
  }

  return [ordered]@{
    repo_root = $resolvedRepoRoot
    runtime_exists = [bool]$runtime.exists
    runtime = $runtime
    helper_pointers = [ordered]@{
      status = $statusPointer
      await = $awaitPointer
      recover = $recoverPointer
      shutdown = $shutdownPointer
      shutdown_apply = $shutdownApplyPointer
      reconcile = $reconcilePointer
      reconcile_apply = $reconcileApplyPointer
    }
    pane_helpers = $paneHelpers
    lifecycle_state = $lifecycleState
    health_state = $healthState
    await_state = $awaitState
    recovery_posture = $recoveryPosture
    recovery_reasons = $recoveryReasons
    resumable_panes = @($paneHelpers | Where-Object { [bool]$_.team_exists -and $null -ne $_.resume_pointer })
    non_resumable_panes = @($paneHelpers | Where-Object { -not [bool]$_.team_exists })
    safe_cleanup_available = (@($safeCleanupCandidates).Count -gt 0)
    manual_reconciliation_required = (@($protectedResidue).Count -gt 0)
    safe_cleanup_candidates = $safeCleanupCandidates
    protected_residue = $protectedResidue
  }
}

function Test-CodexUserLevelComposePaneRoleSupported {
  param(
    [string]$Role
  )

  if ([string]::IsNullOrWhiteSpace($Role)) {
    return $false
  }

  return ([string]$Role -in @('team-executor', 'executor', 'debugger'))
}

function Get-CodexUserLevelMixedPersistentComposePlan {
  param(
    [Parameter(Mandatory)]
    [string]$ManifestPath,
    [string]$RepoRoot
  )

  $resolvedManifestPath = [System.IO.Path]::GetFullPath($ManifestPath)
  if (-not (Test-Path -LiteralPath $resolvedManifestPath)) {
    throw "Compose manifest not found: $resolvedManifestPath"
  }

  $manifest = Get-Content -LiteralPath $resolvedManifestPath -Raw | ConvertFrom-Json
  $resolvedRepoRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
  $composeStateRoot = Get-CodexUserLevelComposeStateRoot -RepoRoot $resolvedRepoRoot
  $contract = Get-CodexUserLevelMixedPersistentComposeContract

  if ($null -eq $manifest.PSObject.Properties['schema_version'] -or [int]$manifest.schema_version -ne 1) {
    throw 'Compose manifest must declare schema_version=1.'
  }
  if ($null -eq $manifest.PSObject.Properties['advanced_opt_in'] -or -not [bool]$manifest.advanced_opt_in) {
    throw 'Compose manifest must declare advanced_opt_in=true.'
  }
  if ($null -eq $manifest.PSObject.Properties['leader'] -or $null -eq $manifest.leader.PSObject.Properties['outside_pane_roster'] -or -not [bool]$manifest.leader.outside_pane_roster) {
    throw 'Compose manifest must declare leader.outside_pane_roster=true.'
  }
  $paneObjects = @($manifest.panes)
  if (@($paneObjects).Count -lt 1) {
    throw 'Compose manifest must declare at least one pane.'
  }

  $panes = @()
  $unsupportedPanes = @()
  foreach ($pane in $paneObjects) {
    $paneName = if ($null -ne $pane.PSObject.Properties['name']) { [string]$pane.name } else { '' }
    $paneRole = if ($null -ne $pane.PSObject.Properties['role']) { [string]$pane.role } else { '' }
    if ([string]::IsNullOrWhiteSpace($paneName)) {
      throw 'Compose manifest panes must declare a non-empty name.'
    }
    if ([string]::IsNullOrWhiteSpace($paneRole)) {
      throw "Compose manifest pane '$paneName' must declare a non-empty role."
    }
    $workers = if ($null -ne $pane.PSObject.Properties['workers'] -and $null -ne $pane.workers) { [int]$pane.workers } else { 1 }
    if ($workers -lt 1) {
      throw "Compose manifest pane '$paneName' must declare workers >= 1."
    }
    $writeScope = if ($null -ne $pane.PSObject.Properties['write_scope'] -and $null -ne $pane.write_scope) { @($pane.write_scope | ForEach-Object { [string]$_ }) } else { @() }
    $launchSupported = Test-CodexUserLevelComposePaneRoleSupported -Role $paneRole
    $panePlan = [ordered]@{
      name = $paneName
      role = $paneRole
      workers = $workers
      worktree = if ($null -ne $pane.PSObject.Properties['worktree']) { [string]$pane.worktree } else { '' }
      mailbox = if ($null -ne $pane.PSObject.Properties['mailbox']) { [string]$pane.mailbox } else { '' }
      checkpoint_group = if ($null -ne $pane.PSObject.Properties['checkpoint_group']) { [string]$pane.checkpoint_group } else { '' }
      task = if ($null -ne $pane.PSObject.Properties['task']) { [string]$pane.task } else { '' }
      write_scope = $writeScope
      read_mostly_default = (@($writeScope).Count -eq 0)
      launch_supported = $launchSupported
      launch_strategy = if ($launchSupported) { 'durable_team_role' } else { 'planned_only' }
    }
    $panes += $panePlan
    if (-not $launchSupported) {
      $unsupportedPanes += $panePlan
    }
  }

  return [ordered]@{
    schema_version = 1
    manifest_path = $resolvedManifestPath
    repo_root = $resolvedRepoRoot
    advanced_opt_in = $true
    leader_outside_pane_roster = $true
    default_path_preserved = $true
    pane_count = @($panes).Count
    panes = $panes
    supported_panes = @($panes | Where-Object { [bool]$_.launch_supported })
    unsupported_panes = $unsupportedPanes
    apply_supported_for_all_panes = (@($unsupportedPanes).Count -eq 0)
    compose_state_root = $composeStateRoot
    compose_state_file = (Get-CodexUserLevelComposePlanStateFilePath -RepoRoot $resolvedRepoRoot)
    compose_runtime_file = (Get-CodexUserLevelComposeRuntimeStateFilePath -RepoRoot $resolvedRepoRoot)
    contract = $contract
  }
}

function Get-CodexUserLevelDurableStateCleanupReconciliationContract {
  return [ordered]@{
    primary_operator_surface = 'codex-durable-state-reconcile.ps1'
    preview_only_default = $true
    apply_flag = '-Apply'
    safe_cleanup_classes = @(
      'stale_tracked_record'
      'stale_compose_runtime_record'
      'empty_unmanaged_native_team_directory'
    )
    protected_residue_classes = @(
      'partially_missing_compose_runtime_teams'
      'non_empty_unmanaged_native_team_directory'
      'unmanaged_langgraph_runtime_residue'
      'conflicting_tracked_backends'
    )
  }
}

function Get-CodexUserLevelDurableStateCleanupReconciliationPlan {
  param(
    [string]$RepoRoot
  )

  $resolvedRepoRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
  $trackedRecord = Read-CodexUserLevelTrackedTeamRecord -RepoRoot $resolvedRepoRoot
  $nativeTeamDirectories = @(Get-CodexUserLevelNativeTeamDirectoriesMetadata -RepoRoot $resolvedRepoRoot)
  $langGraphRecord = Read-CodexUserLevelLangGraphBackendRecord -RepoRoot $resolvedRepoRoot
  $langGraphPresence = Get-CodexUserLevelLangGraphRuntimePresence -RepoRoot $resolvedRepoRoot
  $langGraphThread = if ([bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id)) { Read-CodexUserLevelLangGraphThreadRecord -RepoRoot $resolvedRepoRoot -ThreadId ([string]$langGraphRecord.thread_id) } else { [ordered]@{ exists = $false } }
  $langGraphCheckpoint = if ([bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id)) { Read-CodexUserLevelLangGraphCheckpointRecord -RepoRoot $resolvedRepoRoot -ThreadId ([string]$langGraphRecord.thread_id) } else { [ordered]@{ exists = $false } }
  $langGraphInterrupt = if ([bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id)) { Read-CodexUserLevelLangGraphInterruptRecord -RepoRoot $resolvedRepoRoot -ThreadId ([string]$langGraphRecord.thread_id) } else { [ordered]@{ exists = $false } }
  $langGraphBrief = if ([bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id)) { Read-CodexUserLevelLangGraphImplementationBriefState -RepoRoot $resolvedRepoRoot -ThreadId ([string]$langGraphRecord.thread_id) } else { [ordered]@{ exists = $false } }
  $langGraphSurvivorQueue = if ([bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id)) { Read-CodexUserLevelLangGraphSurvivorQueueState -RepoRoot $resolvedRepoRoot -ThreadId ([string]$langGraphRecord.thread_id) } else { [ordered]@{ exists = $false; item_count = 0 } }
  $composeRuntime = Read-CodexUserLevelComposeRuntimeState -RepoRoot $resolvedRepoRoot
  $composeLifecycle = Get-CodexUserLevelComposeRuntimeLifecyclePlan -RepoRoot $resolvedRepoRoot
  $contract = Get-CodexUserLevelDurableStateCleanupReconciliationContract
  $composeTrackedTeamNames = @(
    @($composeRuntime.launched_panes) |
      ForEach-Object {
        if ($null -ne $_.PSObject.Properties['team_name'] -and -not [string]::IsNullOrWhiteSpace([string]$_.team_name)) {
          [string]$_.team_name
        }
      } |
      Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) }
  )

  $safeCleanupCandidates = @()
  $protectedResidue = @()

  if ([bool]$trackedRecord.stale) {
    $safeCleanupCandidates += [ordered]@{
      kind = 'stale_tracked_record'
      path = [string]$trackedRecord.path
      reason = 'tracked native team record points to a missing team directory'
    }
  }

  foreach ($teamDirectory in $nativeTeamDirectories) {
    $isTrackedDirectory = ([bool]$trackedRecord.exists -and [string]$teamDirectory.team_name -eq [string]$trackedRecord.team_name)
    if ($isTrackedDirectory) {
      continue
    }
    if ([string]$teamDirectory.team_name -in $composeTrackedTeamNames) {
      continue
    }

    if ([bool]$teamDirectory.empty) {
      $safeCleanupCandidates += [ordered]@{
        kind = 'empty_unmanaged_native_team_directory'
        team_name = [string]$teamDirectory.team_name
        path = [string]$teamDirectory.path
        reason = 'unmanaged native team directory contains no files'
      }
    } else {
      $protectedResidue += [ordered]@{
        kind = 'non_empty_unmanaged_native_team_directory'
        team_name = [string]$teamDirectory.team_name
        path = [string]$teamDirectory.path
        file_count = [int]$teamDirectory.file_count
        reason = 'unmanaged native team directory contains repo-local state files'
      }
    }
  }

  if ([bool]$trackedRecord.exists -and [bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id)) {
    $protectedResidue += [ordered]@{
      kind = 'conflicting_tracked_backends'
      reason = 'tracked native durable team state and tracked LangGraph backend state both exist'
      native_team = [string]$trackedRecord.team_name
      langgraph_thread = [string]$langGraphRecord.thread_id
    }
  }

  if (-not [bool]$langGraphRecord.exists -and [bool]$langGraphPresence.present) {
    $protectedResidue += [ordered]@{
      kind = 'unmanaged_langgraph_runtime_residue'
      paths = @($langGraphPresence.signal_paths)
      reason = 'repo-local LangGraph runtime residue exists without a tracked backend record'
    }
  }

  foreach ($candidate in @($composeLifecycle.safe_cleanup_candidates)) {
    $safeCleanupCandidates += $candidate
  }
  foreach ($residue in @($composeLifecycle.protected_residue)) {
    $protectedResidue += $residue
  }

  $manualReconciliationRequired = ($protectedResidue.Count -gt 0)
  $safeCleanupAvailable = ($safeCleanupCandidates.Count -gt 0)

  return [ordered]@{
    repo_root = $resolvedRepoRoot
    preview_only_default = $true
    helper_script = 'codex-durable-state-reconcile.ps1'
    read_only_preview = [ordered]@{
      script = 'codex-durable-state-reconcile.ps1'
      arguments = @('-RepoRoot', $resolvedRepoRoot, '-Json')
    }
    apply_script = [ordered]@{
      script = 'codex-durable-state-reconcile.ps1'
      arguments = @('-RepoRoot', $resolvedRepoRoot, '-Apply', '-Json')
    }
    safe_cleanup_available = $safeCleanupAvailable
    manual_reconciliation_required = $manualReconciliationRequired
    safe_cleanup_candidates = $safeCleanupCandidates
    protected_residue = $protectedResidue
    contract = $contract
  }
}

function Get-CodexUserLevelInspectableDurableState {
  param(
    [string]$RepoRoot
  )

  $resolvedRepoRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
  $activeSelector = Read-CodexUserLevelActiveDurableSelector -RepoRoot $resolvedRepoRoot
  $activeLangGraphSelector = Test-CodexUserLevelActiveDurableSelectorTargetsBackend -Selector $activeSelector -BackendFamily 'langgraph' -RepoRoot $resolvedRepoRoot
  $activeNativeSelector = Test-CodexUserLevelActiveDurableSelectorTargetsBackend -Selector $activeSelector -BackendFamily 'native_omx' -RepoRoot $resolvedRepoRoot
  $trackedRecord = Read-CodexUserLevelTrackedTeamRecord -RepoRoot $resolvedRepoRoot
  $latestTeam = Get-CodexUserLevelLatestTeamDirectoryMetadata -RepoRoot $resolvedRepoRoot
  $nativeTeamDirectories = @(Get-CodexUserLevelNativeTeamDirectoriesMetadata -RepoRoot $resolvedRepoRoot)
  $latestNonEmptyNativeTeam = $nativeTeamDirectories | Where-Object { -not [bool]$_.empty } | Select-Object -First 1
  $langGraphRecord = Read-CodexUserLevelLangGraphBackendRecord -RepoRoot $resolvedRepoRoot
  $langGraphPresence = Get-CodexUserLevelLangGraphRuntimePresence -RepoRoot $resolvedRepoRoot
  $langGraphThread = if ([bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id)) { Read-CodexUserLevelLangGraphThreadRecord -RepoRoot $resolvedRepoRoot -ThreadId ([string]$langGraphRecord.thread_id) } else { [ordered]@{ exists = $false } }
  $langGraphCheckpoint = if ([bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id)) { Read-CodexUserLevelLangGraphCheckpointRecord -RepoRoot $resolvedRepoRoot -ThreadId ([string]$langGraphRecord.thread_id) } else { [ordered]@{ exists = $false } }
  $langGraphInterrupt = if ([bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id)) { Read-CodexUserLevelLangGraphInterruptRecord -RepoRoot $resolvedRepoRoot -ThreadId ([string]$langGraphRecord.thread_id) } else { [ordered]@{ exists = $false } }
  $langGraphBrief = if ([bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id)) { Read-CodexUserLevelLangGraphImplementationBriefState -RepoRoot $resolvedRepoRoot -ThreadId ([string]$langGraphRecord.thread_id) } else { [ordered]@{ exists = $false } }
  $langGraphSurvivorQueue = if ([bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id)) { Read-CodexUserLevelLangGraphSurvivorQueueState -RepoRoot $resolvedRepoRoot -ThreadId ([string]$langGraphRecord.thread_id) } else { [ordered]@{ exists = $false; item_count = 0 } }
  $langGraphHistory = if ([bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id)) { Read-CodexUserLevelLangGraphHistoryState -RepoRoot $resolvedRepoRoot -ThreadId ([string]$langGraphRecord.thread_id) -ThreadRecord $langGraphThread -CheckpointRecord $langGraphCheckpoint -InterruptRecord $langGraphInterrupt } else { [ordered]@{ exists = $false; compatibility = 'no_history'; target_count = 0; available_targets = @(); source_records = @() } }
  $langGraphRecoveryProjection = Get-CodexUserLevelLangGraphRecoveryProjection -ThreadRecord $langGraphThread
  $langGraphKernelProjection = Get-CodexUserLevelLangGraphKernelProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphPrimaryRuntimeEngineProjection = Get-CodexUserLevelLangGraphPrimaryRuntimeEngineProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphCompiledInvocationProjection = Get-CodexUserLevelLangGraphCompiledInvocationProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphLiveExecutionProjection = Get-CodexUserLevelLangGraphLiveExecutionProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphFullerLivePrimaryEngineProjection = Get-CodexUserLevelLangGraphFullerLivePrimaryEngineProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphDeeperLivePrimaryEngineProjection = Get-CodexUserLevelLangGraphDeeperLivePrimaryEngineProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphSuperstepLivePrimaryEngineProjection = Get-CodexUserLevelLangGraphSuperstepLivePrimaryEngineProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphStatefulLivePrimaryEngineProjection = Get-CodexUserLevelLangGraphStatefulLivePrimaryEngineProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphBoundaryStateLivePrimaryEngineProjection = Get-CodexUserLevelLangGraphBoundaryStateLivePrimaryEngineProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphHandoffStateLivePrimaryEngineProjection = Get-CodexUserLevelLangGraphHandoffStateLivePrimaryEngineProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphApprovalAwareLivePrimaryEngineProjection = Get-CodexUserLevelLangGraphApprovalAwareLivePrimaryEngineProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphProvenanceStateLivePrimaryEngineProjection = Get-CodexUserLevelLangGraphProvenanceStateLivePrimaryEngineProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphDurableArtifactAwareLivePrimaryEngineProjection = Get-CodexUserLevelLangGraphDurableArtifactAwareLivePrimaryEngineProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphReducerAwareLivePrimaryEngineProjection = Get-CodexUserLevelLangGraphReducerAwareLivePrimaryEngineProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphCommandAwareLivePrimaryEngineProjection = Get-CodexUserLevelLangGraphCommandAwareLivePrimaryEngineProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphRuntimeAwareLivePrimaryEngineProjection = Get-CodexUserLevelLangGraphRuntimeAwareLivePrimaryEngineProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphMemoryAwareLivePrimaryEngineProjection = Get-CodexUserLevelLangGraphMemoryAwareLivePrimaryEngineProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphMigrationAwareLivePrimaryEngineProjection = Get-CodexUserLevelLangGraphMigrationAwareLivePrimaryEngineProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphAutomaticRuntimePolicyProjection = Get-CodexUserLevelLangGraphAutomaticRuntimePolicyProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphGeneralizedLiveRoutingProjection = Get-CodexUserLevelLangGraphGeneralizedLiveRoutingProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphApprovalQueueProjection = Get-CodexUserLevelLangGraphApprovalQueueProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -InterruptRecord $langGraphInterrupt -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphMigrationProjection = Get-CodexUserLevelLangGraphMigrationProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphRuntimeInjectionProjection = Get-CodexUserLevelLangGraphRuntimeInjectionProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphMemoryProjection = Get-CodexUserLevelLangGraphMemoryProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphStreamProjection = Get-CodexUserLevelLangGraphStreamProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphCommandProjection = Get-CodexUserLevelLangGraphCommandProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphSubgraphProjection = Get-CodexUserLevelLangGraphSubgraphProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphSubgraphStateInspectionProjection = Get-CodexUserLevelLangGraphSubgraphStateInspectionProjection -RepoRoot $resolvedRepoRoot -ThreadRecord $langGraphThread -ThreadId ([string]$langGraphRecord.thread_id)
  $langGraphHelperPointers = if ([bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id)) { Get-CodexUserLevelLangGraphHelperPointers -RepoRoot $resolvedRepoRoot -ThreadId ([string]$langGraphRecord.thread_id) } else { [ordered]@{} }
  $composeRuntime = Read-CodexUserLevelComposeRuntimeState -RepoRoot $resolvedRepoRoot
  $composeLifecycle = Get-CodexUserLevelComposeRuntimeLifecyclePlan -RepoRoot $resolvedRepoRoot
  $contract = Get-CodexUserLevelInspectableDurableStateSurfaceContract
  $cleanupPlan = Get-CodexUserLevelDurableStateCleanupReconciliationPlan -RepoRoot $resolvedRepoRoot

  $hasTrackedLangGraph = ($activeLangGraphSelector -and [bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id))
  $hasPreservedLegacyLangGraph = ([bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id) -and -not $hasTrackedLangGraph)
  $hasTrackedNative = ($activeNativeSelector -and [bool]$trackedRecord.exists)
  $hasPreservedLegacyNative = ([bool]$trackedRecord.exists -and -not $hasTrackedNative)
  $hasStaleTrackedNative = [bool]$trackedRecord.stale
  $hasTrackedComposeRuntime = [bool]$composeRuntime.exists
  $hasUnmanagedNative = ((-not $hasTrackedNative) -and $null -ne $latestNonEmptyNativeTeam)
  $hasUnmanagedLangGraph = ((-not $hasTrackedLangGraph) -and (-not $hasPreservedLegacyLangGraph) -and [bool]$langGraphPresence.present)

  $stateClass = 'no_durable_state'
  $backendFamily = ''
  $trackedIdentity = ''
  $currentPhase = ''
  $workerShape = [ordered]@{
    kind = 'none'
    worker_role = ''
    worker_count = 0
    summary = 'none'
  }
  $activeBlockers = @()
  $nextStep = 'No durable state detected. Launch a durable backend only when thresholds are met.'
  $inspectPointer = [ordered]@{
    script = 'codex-durable-state-status.ps1'
    arguments = @('-RepoRoot', $resolvedRepoRoot, '-Json')
  }
  $resumePointer = $null
  $stateSources = @()
  $updatedAt = ''
  $backendSpecific = [ordered]@{
    native_omx = [ordered]@{
      tracked_record = $trackedRecord
      latest_team_directory = $latestTeam
    }
    compose = [ordered]@{
      runtime = $composeRuntime
      helper_pointers = $composeLifecycle.helper_pointers
      pane_helpers = $composeLifecycle.pane_helpers
      lifecycle_state = [string]$composeLifecycle.lifecycle_state
      health_state = [string]$composeLifecycle.health_state
      await_state = [string]$composeLifecycle.await_state
      recovery_posture = [string]$composeLifecycle.recovery_posture
      recovery_reasons = @($composeLifecycle.recovery_reasons)
      resumable_panes = @($composeLifecycle.resumable_panes)
      non_resumable_panes = @($composeLifecycle.non_resumable_panes)
      lifecycle_cleanup = [ordered]@{
        safe_cleanup_available = [bool]$composeLifecycle.safe_cleanup_available
        manual_reconciliation_required = [bool]$composeLifecycle.manual_reconciliation_required
        safe_cleanup_candidates = @($composeLifecycle.safe_cleanup_candidates)
        protected_residue = @($composeLifecycle.protected_residue)
      }
    }
    langgraph = [ordered]@{
      backend_record = $langGraphRecord
      runtime_presence = $langGraphPresence
      thread = $langGraphThread
      checkpoint = $langGraphCheckpoint
      interrupt = $langGraphInterrupt
      history = $langGraphHistory
      implementation_brief = $langGraphBrief
      survivor_queue = $langGraphSurvivorQueue
      durable_artifacts = [ordered]@{
        implementation_brief_present = [bool]$langGraphBrief.exists
        implementation_brief_id = if ($null -ne $langGraphBrief.PSObject.Properties['brief_id']) { [string]$langGraphBrief.brief_id } else { '' }
        implementation_brief_source_evidence_ref_count = if ($null -ne $langGraphBrief.PSObject.Properties['source_evidence_ref_count']) { [int]$langGraphBrief.source_evidence_ref_count } else { 0 }
        survivor_queue_present = [bool]$langGraphSurvivorQueue.exists
        survivor_queue_kind = if ($null -ne $langGraphSurvivorQueue.PSObject.Properties['queue_kind']) { [string]$langGraphSurvivorQueue.queue_kind } else { '' }
        survivor_count = [int]$langGraphSurvivorQueue.item_count
      }
      kernel_projection = $langGraphKernelProjection
      primary_runtime_engine_projection = $langGraphPrimaryRuntimeEngineProjection
      compiled_invocation_projection = $langGraphCompiledInvocationProjection
      live_execution_projection = $langGraphLiveExecutionProjection
      fuller_live_primary_engine_projection = $langGraphFullerLivePrimaryEngineProjection
      deeper_live_primary_engine_projection = $langGraphDeeperLivePrimaryEngineProjection
      superstep_live_primary_engine_projection = $langGraphSuperstepLivePrimaryEngineProjection
      stateful_live_primary_engine_projection = $langGraphStatefulLivePrimaryEngineProjection
      boundary_state_live_primary_engine_projection = $langGraphBoundaryStateLivePrimaryEngineProjection
      handoff_state_live_primary_engine_projection = $langGraphHandoffStateLivePrimaryEngineProjection
      approval_aware_live_primary_engine_projection = $langGraphApprovalAwareLivePrimaryEngineProjection
      provenance_state_live_primary_engine_projection = $langGraphProvenanceStateLivePrimaryEngineProjection
      durable_artifact_aware_live_primary_engine_projection = $langGraphDurableArtifactAwareLivePrimaryEngineProjection
      reducer_aware_live_primary_engine_projection = $langGraphReducerAwareLivePrimaryEngineProjection
      command_aware_live_primary_engine_projection = $langGraphCommandAwareLivePrimaryEngineProjection
      runtime_aware_live_primary_engine_projection = $langGraphRuntimeAwareLivePrimaryEngineProjection
      memory_aware_live_primary_engine_projection = $langGraphMemoryAwareLivePrimaryEngineProjection
      migration_aware_live_primary_engine_projection = $langGraphMigrationAwareLivePrimaryEngineProjection
      automatic_runtime_policy_projection = $langGraphAutomaticRuntimePolicyProjection
      generalized_live_routing_projection = $langGraphGeneralizedLiveRoutingProjection
      approval_queue_projection = $langGraphApprovalQueueProjection
      migration_projection = $langGraphMigrationProjection
      memory_projection = $langGraphMemoryProjection
      runtime_injection_projection = $langGraphRuntimeInjectionProjection
      loop_projection = (Get-CodexUserLevelLangGraphLoopProjection -ThreadRecord $langGraphThread)
      stream_projection = $langGraphStreamProjection
      command_projection = $langGraphCommandProjection
      subgraph_projection = $langGraphSubgraphProjection
      subgraph_state_inspection_projection = $langGraphSubgraphStateInspectionProjection
      recovery_projection = $langGraphRecoveryProjection
      reducer_projection = (Get-CodexUserLevelLangGraphReducerProjection -ThreadRecord $langGraphThread)
      helper_pointers = $langGraphHelperPointers
    }
  }

  if ($hasTrackedComposeRuntime -and $hasTrackedLangGraph) {
    $launchedCount = @($composeRuntime.launched_panes).Count
    $stateClass = 'multiple_durable_states_detected'
    $backendFamily = 'multiple'
    $trackedIdentity = [ordered]@{
      compose_runtime = [string]$composeRuntime.runtime_id
      langgraph_thread = [string]$langGraphRecord.thread_id
    }
    $currentPhase = if (-not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.phase)) { [string]$langGraphRecord.phase } else { 'compose-runtime' }
    $workerShape = [ordered]@{
      kind = 'multiple'
      worker_role = 'compose-runtime'
      worker_count = $launchedCount
      summary = ('compose:{0} panes; langgraph-thread' -f $launchedCount)
    }
    $activeBlockers = @('multiple_durable_states_detected')
    $nextStep = 'Inspect the tracked compose runtime and the tracked LangGraph thread before deciding which durable path should remain active.'
    $inspectPointer = [ordered]@{
      script = 'codex-durable-state-status.ps1'
      arguments = @('-RepoRoot', $resolvedRepoRoot, '-Json')
    }
    $resumePointer = [ordered]@{
      script = 'omx-langgraph-resume.ps1'
      arguments = @('-ThreadId', [string]$langGraphRecord.thread_id, '-RepoRoot', $resolvedRepoRoot)
    }
    $stateSources = @([string]$composeRuntime.path, [string]$langGraphRecord.path)
    if (Test-Path -LiteralPath [string]$composeRuntime.plan_path) {
      $stateSources += [string]$composeRuntime.plan_path
    }
    $updatedAt = if (-not [string]::IsNullOrWhiteSpace([string]$composeRuntime.updated_at)) { [string]$composeRuntime.updated_at } else { [string]$langGraphRecord.updated_at }
  } elseif ($hasTrackedComposeRuntime -and ($hasTrackedNative -or $hasStaleTrackedNative)) {
    $launchedCount = @($composeRuntime.launched_panes).Count
    $stateClass = 'multiple_durable_states_detected'
    $backendFamily = 'multiple'
    $trackedIdentity = [ordered]@{
      compose_runtime = [string]$composeRuntime.runtime_id
      native_team = [string]$trackedRecord.team_name
    }
    $currentPhase = if ($hasStaleTrackedNative) { [string]$trackedRecord.phase } else { 'compose-runtime' }
    $workerShape = [ordered]@{
      kind = 'multiple'
      worker_role = if ($hasStaleTrackedNative) { [string]$trackedRecord.worker_role } else { 'compose-runtime' }
      worker_count = if ($hasStaleTrackedNative) { [int]$trackedRecord.worker_count } else { $launchedCount }
      summary = if ($hasStaleTrackedNative) { ('compose:{0} panes; native:{1}:{2}' -f $launchedCount, [int]$trackedRecord.worker_count, [string]$trackedRecord.worker_role) } else { ('compose:{0} panes; native:{1}:{2}' -f $launchedCount, [int]$trackedRecord.worker_count, [string]$trackedRecord.worker_role) }
    }
    $activeBlockers = if ($hasStaleTrackedNative) { @('stale_tracked_record', 'multiple_durable_states_detected') } else { @('multiple_durable_states_detected') }
    $nextStep = 'Inspect the tracked compose runtime and the tracked native durable team record before deciding which native durable state should remain authoritative.'
    $inspectPointer = [ordered]@{
      script = 'codex-durable-state-status.ps1'
      arguments = @('-RepoRoot', $resolvedRepoRoot, '-Json')
    }
    $resumePointer = if ($hasStaleTrackedNative) { $null } else { [ordered]@{
      script = 'omx-team-ops.ps1'
      arguments = @('-Action', 'resume', '-TeamName', [string]$trackedRecord.team_name, '-RepoRoot', $resolvedRepoRoot)
    } }
    $stateSources = @([string]$composeRuntime.path, [string]$trackedRecord.path)
    if (Test-Path -LiteralPath [string]$composeRuntime.plan_path) {
      $stateSources += [string]$composeRuntime.plan_path
    }
    $updatedAt = if (-not [string]::IsNullOrWhiteSpace([string]$composeRuntime.updated_at)) { [string]$composeRuntime.updated_at } else { [string]$trackedRecord.updated_at }
  } elseif ($hasStaleTrackedNative -and $hasTrackedLangGraph) {
    $stateClass = 'multiple_durable_states_detected'
    $backendFamily = 'multiple'
    $trackedIdentity = [ordered]@{
      native_team = [string]$trackedRecord.team_name
      langgraph_thread = [string]$langGraphRecord.thread_id
    }
    $currentPhase = [string]$langGraphRecord.phase
    $workerShape = [ordered]@{
      kind = 'multiple'
      worker_role = [string]$trackedRecord.worker_role
      worker_count = [int]$trackedRecord.worker_count
      summary = ('native:{0}:{1}; langgraph-thread' -f [int]$trackedRecord.worker_count, [string]$trackedRecord.worker_role)
    }
    $activeBlockers = @('stale_tracked_record', 'multiple_durable_states_detected')
    $nextStep = 'Inspect both the stale tracked native team record and the tracked LangGraph thread before deciding which durable path to keep.'
    $inspectPointer = [ordered]@{
      script = 'codex-durable-state-status.ps1'
      arguments = @('-RepoRoot', $resolvedRepoRoot, '-Json')
    }
    $resumePointer = [ordered]@{
      script = 'omx-langgraph-resume.ps1'
      arguments = @('-ThreadId', [string]$langGraphRecord.thread_id, '-RepoRoot', $resolvedRepoRoot)
    }
    $stateSources = @([string]$trackedRecord.path, [string]$langGraphRecord.path)
    $updatedAt = [string]$langGraphRecord.updated_at
  } elseif ($hasTrackedNative -and $hasTrackedLangGraph) {
    $stateClass = 'multiple_durable_states_detected'
    $backendFamily = 'multiple'
    $trackedIdentity = [ordered]@{
      native_team = [string]$trackedRecord.team_name
      langgraph_thread = [string]$langGraphRecord.thread_id
    }
    $currentPhase = if (-not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.phase)) { [string]$langGraphRecord.phase } else { [string]$trackedRecord.phase }
    $workerShape = [ordered]@{
      kind = 'multiple'
      worker_role = [string]$trackedRecord.worker_role
      worker_count = [int]$trackedRecord.worker_count
      summary = ('native:{0}:{1}; langgraph-thread' -f [int]$trackedRecord.worker_count, [string]$trackedRecord.worker_role)
    }
    $activeBlockers = @('multiple_durable_states_detected')
    $nextStep = 'Inspect both tracked durable backends and decide which one should remain the active durable path for this repository.'
    $inspectPointer = [ordered]@{
      script = 'codex-durable-state-status.ps1'
      arguments = @('-RepoRoot', $resolvedRepoRoot, '-Json')
    }
    $resumePointer = [ordered]@{
      script = 'omx-langgraph-resume.ps1'
      arguments = @('-ThreadId', [string]$langGraphRecord.thread_id, '-RepoRoot', $resolvedRepoRoot)
    }
    $stateSources = @([string]$trackedRecord.path, [string]$langGraphRecord.path)
    $updatedAt = if (-not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.updated_at)) { [string]$langGraphRecord.updated_at } else { [string]$trackedRecord.updated_at }
  } elseif ($hasStaleTrackedNative) {
    $stateClass = 'stale_tracked_record'
    $backendFamily = 'native_omx'
    $trackedIdentity = [string]$trackedRecord.team_name
    $currentPhase = [string]$trackedRecord.phase
    $workerShape = [ordered]@{
      kind = 'native_team'
      worker_role = [string]$trackedRecord.worker_role
      worker_count = [int]$trackedRecord.worker_count
      summary = ('{0}:{1}' -f [int]$trackedRecord.worker_count, [string]$trackedRecord.worker_role)
    }
    $activeBlockers = @('stale_tracked_record')
    $nextStep = 'Clean or refresh the stale tracked team record before automatic reuse or further mutation.'
    $inspectPointer = [ordered]@{
      script = 'codex-durable-state-status.ps1'
      arguments = @('-RepoRoot', $resolvedRepoRoot, '-Json')
    }
    $resumePointer = $null
    $stateSources = @([string]$trackedRecord.path)
    $updatedAt = [string]$trackedRecord.updated_at
  } elseif ($hasPreservedLegacyNative) {
    $stateClass = 'preserved_legacy_native_team_artifact'
    $backendFamily = 'native_omx'
    $trackedIdentity = [string]$trackedRecord.team_name
    $currentPhase = [string]$trackedRecord.phase
    $workerShape = [ordered]@{
      kind = 'preserved_legacy_artifact'
      worker_role = [string]$trackedRecord.worker_role
      worker_count = [int]$trackedRecord.worker_count
      summary = ('legacy-native-team:{0}:{1}' -f [int]$trackedRecord.worker_count, [string]$trackedRecord.worker_role)
    }
    $activeBlockers = @()
    $nextStep = 'Inspect the preserved legacy native durable team artifact. It is not treated as the active future-session selector.'
    $inspectPointer = [ordered]@{
      script = 'omx-team-ops.ps1'
      arguments = @('-Action', 'status', '-TeamName', [string]$trackedRecord.team_name, '-RepoRoot', $resolvedRepoRoot, '-Json')
    }
    $resumePointer = $null
    $stateSources = @([string]$trackedRecord.path, (Join-Path (Get-CodexUserLevelTeamStateRoot -RepoRoot $resolvedRepoRoot) ([string]$trackedRecord.team_name)))
    $updatedAt = [string]$trackedRecord.updated_at
    if ([bool]$cleanupPlan.safe_cleanup_available) {
      $nextStep = 'Inspect the preserved legacy native durable team artifact. Safe cleanup candidates are also available through codex-durable-state-reconcile.ps1.'
    }
  } elseif ($hasTrackedNative) {
    $stateClass = 'tracked_native_team'
    $backendFamily = 'native_omx'
    $trackedIdentity = [string]$trackedRecord.team_name
    $currentPhase = [string]$trackedRecord.phase
    $workerShape = [ordered]@{
      kind = 'native_team'
      worker_role = [string]$trackedRecord.worker_role
      worker_count = [int]$trackedRecord.worker_count
      summary = ('{0}:{1}' -f [int]$trackedRecord.worker_count, [string]$trackedRecord.worker_role)
    }
    $activeBlockers = @()
    $nextStep = ('Inspect or operate on the tracked team "{0}" through omx-team-ops.ps1.' -f [string]$trackedRecord.team_name)
    $inspectPointer = [ordered]@{
      script = 'omx-team-ops.ps1'
      arguments = @('-Action', 'get-summary', '-TeamName', [string]$trackedRecord.team_name, '-RepoRoot', $resolvedRepoRoot)
    }
    $resumePointer = [ordered]@{
      script = 'omx-team-ops.ps1'
      arguments = @('-Action', 'resume', '-TeamName', [string]$trackedRecord.team_name, '-RepoRoot', $resolvedRepoRoot)
    }
    $stateSources = @([string]$trackedRecord.path, (Join-Path (Get-CodexUserLevelTeamStateRoot -RepoRoot $resolvedRepoRoot) ([string]$trackedRecord.team_name)))
    if ([bool]$activeSelector.exists -and -not [string]::IsNullOrWhiteSpace([string]$activeSelector.path)) {
      $stateSources += [string]$activeSelector.path
    }
    $updatedAt = [string]$trackedRecord.updated_at
    if ([bool]$cleanupPlan.manual_reconciliation_required) {
      $activeBlockers = @('manual_reconciliation_required')
      $nextStep = 'Inspect the tracked native durable team and reconcile protected unmanaged durable residue before assuming a clean single-backend durable state.'
    } elseif ([bool]$cleanupPlan.safe_cleanup_available) {
      $nextStep = 'Inspect or resume the tracked native durable team. Safe cleanup candidates are also available through codex-durable-state-reconcile.ps1.'
    }
  } elseif ($hasTrackedComposeRuntime) {
    $launchedCount = @($composeRuntime.launched_panes).Count
    $plannedOnlyCount = @($composeRuntime.planned_only_panes).Count
    $failedCount = @($composeRuntime.failed_panes).Count
    $stateClass = 'tracked_compose_runtime'
    $backendFamily = if (-not [string]::IsNullOrWhiteSpace([string]$composeRuntime.backend_family)) { [string]$composeRuntime.backend_family } else { 'native_omx' }
    $trackedIdentity = [string]$composeRuntime.runtime_id
    $currentPhase = switch ([string]$composeLifecycle.lifecycle_state) {
      'fully_active' { 'compose-runtime-active' }
      'partial_shutdown' { 'compose-runtime-partial' }
      'fully_quiesced' { 'compose-runtime-quiesced' }
      'no_launched_panes' { 'compose-runtime-planned-only' }
      default { 'compose-runtime' }
    }
    $workerShape = [ordered]@{
      kind = 'compose_runtime'
      worker_role = 'compose-runtime'
      worker_count = $launchedCount
      summary = switch ([string]$composeLifecycle.await_state) {
        'partial' { ('compose:{0}/{1} active' -f @($composeLifecycle.pane_helpers | Where-Object { [bool]$_.team_exists }).Count, $launchedCount) }
        'quiesced' { ('compose:0/{0} active' -f $launchedCount) }
        default { ('compose:{0} launched/{1} total' -f $launchedCount, @($composeRuntime.pane_results).Count) }
      }
    }
    $activeBlockers = @()
    if ($plannedOnlyCount -gt 0) {
      $activeBlockers += 'planned_only_panes_present'
    }
    if ($failedCount -gt 0) {
      $activeBlockers += 'compose_launch_failures_present'
    }
    if ([bool]$composeLifecycle.safe_cleanup_available) {
      $activeBlockers += 'stale_compose_runtime_record'
    }
    if ([bool]$composeLifecycle.manual_reconciliation_required) {
      $activeBlockers += 'manual_reconciliation_required'
    }
    if ([string]$composeLifecycle.lifecycle_state -eq 'partial_shutdown') {
      $activeBlockers += 'partial_compose_runtime'
    }
    if ([string]$composeLifecycle.health_state -eq 'partial_health' -and 'partial_compose_runtime' -notin $activeBlockers) {
      $activeBlockers += 'partial_health_compose_runtime'
    }
    if ([string]$composeLifecycle.recovery_posture -eq 'manual_intervention_required') {
      $activeBlockers += 'compose_manual_recovery_required'
    } elseif ([string]$composeLifecycle.recovery_posture -eq 'degraded_recoverable') {
      $activeBlockers += 'compose_degraded_recoverable'
    }
    $nextStep = if ($failedCount -gt 0) {
      'Inspect the compose runtime state, review failed pane launches, and operate on launched pane teams through omx-team-ops.ps1 as needed.'
    } elseif ([string]$composeLifecycle.recovery_posture -eq 'manual_intervention_required') {
      'Use omx-team-compose-recover.ps1 to inspect compose recovery posture before attempting any pane-level resume action.'
    } elseif ([string]$composeLifecycle.recovery_posture -eq 'degraded_recoverable') {
      'Use omx-team-compose-recover.ps1 to inspect resumable panes and choose explicit pane-level resume actions.'
    } elseif ([string]$composeLifecycle.lifecycle_state -eq 'partial_shutdown') {
      'Use omx-team-compose-await.ps1 to inspect remaining active compose panes, then continue shutdown or reconcile as needed.'
    } elseif ([bool]$composeLifecycle.safe_cleanup_available) {
      'Inspect the tracked compose runtime and use omx-team-compose-reconcile.ps1 if the compose runtime record is stale.'
    } elseif ([bool]$composeLifecycle.manual_reconciliation_required) {
      'Inspect the tracked compose runtime and reconcile missing launched pane teams before treating it as healthy.'
    } elseif ($plannedOnlyCount -gt 0) {
      'Inspect launched compose pane teams through omx-team-ops.ps1 and keep unsupported panes planned-only or leader-side.'
    } else {
      'Inspect launched compose pane teams through omx-team-ops.ps1 as needed.'
    }
    $inspectPointer = if ([string]$composeLifecycle.lifecycle_state -eq 'partial_shutdown') {
      $composeLifecycle.helper_pointers.await
    } elseif ([string]$composeLifecycle.recovery_posture -in @('degraded_recoverable', 'manual_intervention_required')) {
      $composeLifecycle.helper_pointers.recover
    } else {
      [ordered]@{
        script = 'codex-durable-state-status.ps1'
        arguments = @('-RepoRoot', $resolvedRepoRoot, '-Json')
      }
    }
    $resumePointer = if ([string]$composeLifecycle.recovery_posture -in @('resumable', 'degraded_recoverable', 'manual_intervention_required')) { $composeLifecycle.helper_pointers.recover } else { $null }
    $stateSources = @([string]$composeRuntime.path)
    if (Test-Path -LiteralPath [string]$composeRuntime.plan_path) {
      $stateSources += [string]$composeRuntime.plan_path
    }
    foreach ($launchedPane in @($composeRuntime.launched_panes)) {
      if ($null -ne $launchedPane.PSObject.Properties['team_name'] -and -not [string]::IsNullOrWhiteSpace([string]$launchedPane.team_name)) {
        $stateSources += (Join-Path (Get-CodexUserLevelTeamStateRoot -RepoRoot $resolvedRepoRoot) ([string]$launchedPane.team_name))
      }
    }
    $updatedAt = [string]$composeRuntime.updated_at
  } elseif ($hasTrackedLangGraph) {
    $stateClass = 'tracked_langgraph_thread'
    $backendFamily = 'langgraph'
    $trackedIdentity = [string]$langGraphRecord.thread_id
    $currentPhase = if ([bool]$langGraphThread.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphThread.phase)) { [string]$langGraphThread.phase } else { [string]$langGraphRecord.phase }
    $workerShape = [ordered]@{
      kind = 'langgraph_thread'
      worker_role = ''
      worker_count = 0
      summary = 'langgraph-thread'
    }
    $activeBlockers = @()
    $nextStep = 'Inspect or resume the tracked LangGraph thread through the LangGraph entrypoints.'
    $inspectPointer = [ordered]@{
      script = 'omx-langgraph-inspect.ps1'
      arguments = @('-ThreadId', [string]$langGraphRecord.thread_id, '-RepoRoot', $resolvedRepoRoot)
    }
    $resumePointer = [ordered]@{
      script = 'omx-langgraph-resume.ps1'
      arguments = @('-ThreadId', [string]$langGraphRecord.thread_id, '-RepoRoot', $resolvedRepoRoot)
    }
    $stateSources = @([string]$langGraphRecord.path)
    if ([bool]$activeSelector.exists -and -not [string]::IsNullOrWhiteSpace([string]$activeSelector.path)) {
      $stateSources += [string]$activeSelector.path
    }
    foreach ($candidate in @($langGraphThread, $langGraphCheckpoint, $langGraphInterrupt, $langGraphHistory, $langGraphBrief, $langGraphSurvivorQueue)) {
      if ($null -ne $candidate -and $null -ne $candidate.PSObject.Properties['exists'] -and [bool]$candidate.exists -and -not [string]::IsNullOrWhiteSpace([string]$candidate.path)) {
        $stateSources += [string]$candidate.path
      }
    }
    $updatedAt = if ([bool]$langGraphThread.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphThread.updated_at)) { [string]$langGraphThread.updated_at } else { [string]$langGraphRecord.updated_at }
    if ([bool]$cleanupPlan.manual_reconciliation_required) {
      $activeBlockers = @('manual_reconciliation_required')
      $nextStep = 'Inspect the tracked LangGraph thread and reconcile protected unmanaged durable residue before assuming a clean single-backend durable state.'
    } elseif (([int]$langGraphApprovalQueueProjection.pending_count -gt 0) -or (([bool]$langGraphInterrupt.exists -and [string]$langGraphInterrupt.status -eq 'waiting_for_approval') -or ([bool]$langGraphThread.exists -and [string]$langGraphThread.status -eq 'waiting_for_approval'))) {
      $activeBlockers = @('human_approval_required')
      $nextStep = 'Inspect the tracked LangGraph thread to review the pending approval queue or gate verdict, then resume it explicitly after approval.'
    } elseif ([string]$langGraphCommandProjection.resume_posture -eq 'awaiting_command_resume') {
      $activeBlockers = @('command_resume_required')
      $nextStep = 'Inspect the tracked LangGraph thread to review command-driven continuation posture, then resume it explicitly with the required command metadata or payload.'
    } elseif ([bool]$langGraphThread.exists -and [string]$langGraphThread.stop_reason -eq 'iteration_budget_exhausted') {
      $activeBlockers = @('iteration_budget_exhausted')
      $nextStep = 'Inspect the tracked LangGraph thread, review the loop stop reason, and resume only after adjusting the gate criteria or iteration budget.'
    } elseif ([bool]$langGraphThread.exists -and [string]$langGraphThread.stop_reason -eq 'non_repairable_failure') {
      $activeBlockers = @('non_repairable_failure')
      $nextStep = 'Inspect the tracked LangGraph thread to review the non-repairable failure before deciding whether to restart or abandon the loop.'
    } elseif ([bool]$langGraphThread.exists -and [string]$langGraphThread.stop_reason -eq 'escalated') {
      $activeBlockers = @('escalated')
      $nextStep = 'Inspect the tracked LangGraph thread and escalate the work to the next durable or leader-owned lane as needed.'
    } elseif ([string]$langGraphRecoveryProjection.posture -eq 'recovered_pending_resume') {
      $activeBlockers = @('recovery_pending_resume')
      $nextStep = 'Inspect replay or recovery posture through the LangGraph helpers, then resume the recovered thread explicitly when ready.'
    } elseif ([bool]$cleanupPlan.safe_cleanup_available) {
      $nextStep = 'Inspect or resume the tracked LangGraph thread. Safe cleanup candidates are also available through codex-durable-state-reconcile.ps1.'
    }
  } elseif ($hasPreservedLegacyNative) {
    $stateClass = 'preserved_legacy_native_team_artifact'
    $backendFamily = 'native_omx'
    $trackedIdentity = [string]$trackedRecord.team_name
    $currentPhase = [string]$trackedRecord.phase
    $workerShape = [ordered]@{
      kind = 'preserved_legacy_artifact'
      worker_role = [string]$trackedRecord.worker_role
      worker_count = [int]$trackedRecord.worker_count
      summary = ('legacy-native-team:{0}:{1}' -f [int]$trackedRecord.worker_count, [string]$trackedRecord.worker_role)
    }
    $activeBlockers = @()
    $nextStep = 'Inspect the preserved legacy native durable team artifact. It is not treated as the active future-session selector.'
    $inspectPointer = [ordered]@{
      script = 'omx-team-ops.ps1'
      arguments = @('-Action', 'status', '-TeamName', [string]$trackedRecord.team_name, '-RepoRoot', $resolvedRepoRoot, '-Json')
    }
    $resumePointer = $null
    $stateSources = @([string]$trackedRecord.path, (Join-Path (Get-CodexUserLevelTeamStateRoot -RepoRoot $resolvedRepoRoot) ([string]$trackedRecord.team_name)))
    $updatedAt = [string]$trackedRecord.updated_at
    if ([bool]$cleanupPlan.safe_cleanup_available) {
      $nextStep = 'Inspect the preserved legacy native durable team artifact. Safe cleanup candidates are also available through codex-durable-state-reconcile.ps1.'
    }
  } elseif ($hasPreservedLegacyLangGraph) {
    $stateClass = 'preserved_legacy_langgraph_artifact'
    $backendFamily = 'langgraph'
    $trackedIdentity = [string]$langGraphRecord.thread_id
    $currentPhase = if ([bool]$langGraphThread.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphThread.phase)) { [string]$langGraphThread.phase } else { [string]$langGraphRecord.phase }
    $workerShape = [ordered]@{
      kind = 'preserved_legacy_artifact'
      worker_role = ''
      worker_count = 0
      summary = 'legacy-langgraph-artifact'
    }
    $activeBlockers = @()
    $nextStep = 'Inspect the preserved legacy LangGraph thread. Explicit resume remains available, but this record is not treated as the active future-session durable selector.'
    $inspectPointer = [ordered]@{
      script = 'omx-langgraph-inspect.ps1'
      arguments = @('-ThreadId', [string]$langGraphRecord.thread_id, '-RepoRoot', $resolvedRepoRoot)
    }
    $resumePointer = [ordered]@{
      script = 'omx-langgraph-resume.ps1'
      arguments = @('-ThreadId', [string]$langGraphRecord.thread_id, '-RepoRoot', $resolvedRepoRoot)
    }
    $stateSources = @([string]$langGraphRecord.path)
    foreach ($candidate in @($langGraphThread, $langGraphCheckpoint, $langGraphInterrupt, $langGraphHistory, $langGraphBrief, $langGraphSurvivorQueue)) {
      if ($null -ne $candidate -and $null -ne $candidate.PSObject.Properties['exists'] -and [bool]$candidate.exists -and -not [string]::IsNullOrWhiteSpace([string]$candidate.path)) {
        $stateSources += [string]$candidate.path
      }
    }
    $updatedAt = if ([bool]$langGraphThread.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphThread.updated_at)) { [string]$langGraphThread.updated_at } else { [string]$langGraphRecord.updated_at }
    if ([bool]$cleanupPlan.manual_reconciliation_required) {
      $activeBlockers = @('manual_reconciliation_required')
      $nextStep = 'Inspect the preserved legacy LangGraph thread and reconcile protected unmanaged durable residue before treating the repository state as clean.'
    } elseif ([bool]$cleanupPlan.safe_cleanup_available) {
      $nextStep = 'Inspect the preserved legacy LangGraph thread. Safe cleanup candidates are also available through codex-durable-state-reconcile.ps1.'
    }
  } elseif ($hasUnmanagedNative -or $hasUnmanagedLangGraph) {
    $stateClass = 'unmanaged_durable_state_detected'
    if ($hasUnmanagedNative -and $hasUnmanagedLangGraph) {
      $backendFamily = 'multiple'
      $trackedIdentity = [ordered]@{
        native_team = [string]$latestTeam.team_name
        langgraph_thread = ''
      }
      $activeBlockers = @('manual_inspection_required', 'multiple_durable_states_detected')
      $inspectPointer = [ordered]@{
        script = 'codex-durable-state-status.ps1'
        arguments = @('-RepoRoot', $resolvedRepoRoot, '-Json')
      }
    } elseif ($hasUnmanagedNative) {
      $backendFamily = 'native_omx'
      $trackedIdentity = [string]$latestNonEmptyNativeTeam.team_name
      $inspectPointer = [ordered]@{
        script = 'omx-team-ops.ps1'
        arguments = @('-Action', 'status', '-TeamName', [string]$latestNonEmptyNativeTeam.team_name, '-RepoRoot', $resolvedRepoRoot, '-Json')
      }
      $activeBlockers = @('manual_inspection_required')
    } else {
      $backendFamily = 'langgraph'
      $trackedIdentity = ''
      $inspectPointer = [ordered]@{
        script = 'omx-langgraph-inspect.ps1'
        arguments = @('-RepoRoot', $resolvedRepoRoot, '-Json')
      }
      $activeBlockers = @('manual_inspection_required')
    }
    $currentPhase = ''
    $workerShape = [ordered]@{
      kind = 'unmanaged'
      worker_role = ''
      worker_count = 0
      summary = 'unmanaged-durable-state'
    }
    $nextStep = if ([bool]$cleanupPlan.safe_cleanup_available -and -not [bool]$cleanupPlan.manual_reconciliation_required) { 'Safe cleanup candidates are available through codex-durable-state-reconcile.ps1 before later durable routing decisions.' } else { 'Inspect the unmanaged durable state manually before automatic reuse, switch, or shutdown decisions.' }
    $resumePointer = $null
    $stateSources = @()
    if ($hasUnmanagedNative) {
      $stateSources += [string]$latestNonEmptyNativeTeam.path
      $updatedAt = [string]$latestNonEmptyNativeTeam.updated_at
    }
    if ($hasUnmanagedLangGraph) {
      $stateSources += @($langGraphPresence.signal_paths)
      if ([string]::IsNullOrWhiteSpace($updatedAt) -and $langGraphPresence.signal_paths.Count -gt 0) {
        $updatedAt = (Get-Date).ToUniversalTime().ToString('o')
      }
    }
  }

  $status = Get-CodexUserLevelTeamModeStatus
  $repoStateNativeSelected = ($activeNativeSelector -or [string]$backendFamily -eq 'native_omx')
  $repoStateLangGraphSelected = ($activeLangGraphSelector -or [string]$backendFamily -eq 'langgraph')
  $capabilityReadiness = Get-CodexUserLevelDurableCapabilityReadiness -Status $status -RepoStateBackendFamily ([string]$backendFamily) -RepoStateNativeSelected $repoStateNativeSelected -RepoStateLangGraphSelected $repoStateLangGraphSelected
  $backendDefault = [string]$status.durable_orchestration_backend
  $backendReady = $false
  if ($backendDefault -eq 'native_omx') {
    $backendReady = [bool]$capabilityReadiness.native_omx.ready
  } elseif ($backendDefault -eq 'langgraph') {
    $backendReady = [bool]$capabilityReadiness.langgraph.ready
  }
  $activeSelectorProjection = Get-CodexUserLevelActiveDurableSelectorStatusProjection -Selector $activeSelector -RepoRoot $resolvedRepoRoot -BackendDefault $backendDefault -BackendReady $backendReady

  return [ordered]@{
    backend_family = $backendFamily
    state_class = $stateClass
    repo_root = $resolvedRepoRoot
    tracked_identity = $trackedIdentity
    current_phase = $currentPhase
    worker_shape = $workerShape
    active_blockers = $activeBlockers
    next_step = $nextStep
    inspect_pointer = $inspectPointer
    resume_pointer = $resumePointer
    state_sources = $stateSources
    updated_at = $updatedAt
    selected_backend = [string]$status.durable_orchestration_backend
    backend_default = $backendDefault
    backend_ready = $backendReady
    selector_authority = [string]$activeSelectorProjection.selector_authority
    selector_authority_path = [string]$activeSelectorProjection.selector_authority_path
    active_selector_status = [string]$activeSelectorProjection.active_selector_status
    active_selector = $activeSelectorProjection.active_selector
    selector_refresh_gap = [bool]$activeSelectorProjection.selector_refresh_gap
    selector_refresh_gap_reason = [string]$activeSelectorProjection.selector_refresh_gap_reason
    capability_readiness = $capabilityReadiness
    helper_mirror_source_of_truth = (Get-CodexUserLevelHelperMirrorSourceOfTruthContract)
    read_only_by_default = $true
    cleanup_reconciliation = $cleanupPlan
    contract = $contract
    backend_specific = $backendSpecific
  }
}

function Get-CodexUserLevelAutomaticTeamPhaseDefinitions {
  return @(
    [ordered]@{
      phase = 'define-target'
      durable_team = $false
      reason = 'define the target with leader-side native roles only'
    }
    [ordered]@{
      phase = 'read-context'
      durable_team = $false
      reason = 'read the code and dependency context before durable execution begins'
    }
    [ordered]@{
      phase = 'freeze-plan'
      durable_team = $false
      reason = 'freeze the implementation brief before durable execution begins'
    }
    [ordered]@{
      phase = 'execute-parallel'
      durable_team = $true
      worker_role = 'team-executor'
      default_worker_count = 2
      min_parallel_slices = 2
      scale_to_3_at = 3
      reason = 'parallel execution threshold met'
    }
    [ordered]@{
      phase = 'integrate-converge'
      durable_team = $true
      worker_role = 'team-executor'
      default_worker_count = 2
      min_parallel_slices = 2
      scale_to_3_at = 3
      reason = 'integration still benefits from a tracked durable execution swarm'
    }
    [ordered]@{
      phase = 'stabilize'
      durable_team = $true
      worker_role = 'debugger'
      default_worker_count = 2
      min_blocking_issues = 1
      reason = 'blocking issue threshold met'
    }
    [ordered]@{
      phase = 'verify-accept'
      durable_team = $false
      reason = 'final verification and acceptance stay with leader-side native roles'
    }
  )
}

function Get-CodexUserLevelAutomaticTeamRoutingPolicy {
  param(
    $Status
  )

  if ($null -eq $Status) {
    $Status = Get-CodexUserLevelTeamModeStatus
  }

  return [ordered]@{
    available = ([string]$Status.oh_my_codex -eq 'on' -and [string]$Status.subagent_routing -eq 'auto')
    helper_script = 'omx-team-auto.ps1'
    apply_required_for_mutation = $true
    selected_backend = [string]$Status.durable_orchestration_backend
    backend_selector_rule = 'choose the effective lane from the enabled capability set instead of forcing one globally pinned durable backend family'
    tracked_team_record_relative_path = (Get-CodexUserLevelTrackedTeamRecordRelativePath)
    non_adoption_rule = 'do not auto-adopt unmanaged existing teams'
    phase_rules = Get-CodexUserLevelAutomaticTeamPhaseDefinitions
    reuse_rule = 'reuse only when the tracked team matches the desired worker role and worker count'
    switch_rule = 'switch only when the tracked team exists and the desired durable team shape changes'
    shutdown_rule = 'shutdown only the tracked auto-managed team when the current phase no longer needs durable workers'
  }
}

function Get-CodexUserLevelEffectiveDurableLane {
  param(
    [Parameter(Mandatory)]
    $Status,
    [Parameter(Mandatory)]
    [string]$Phase,
    [switch]$NeedsGraphPhases,
    [switch]$NeedsCheckpointGates,
    [switch]$NeedsFrozenBrief,
    [switch]$NeedsSurvivorQueue,
    [string]$Task = '',
    $LangGraphRecord,
    [bool]$ActiveLangGraphSelector = $false
  )

  if (-not [bool]$Status.durable_team_features_available) {
    return ''
  }

  if (-not [bool]$Status.langgraph_available) {
    return 'native_omx'
  }

  if ($ActiveLangGraphSelector -and (Test-CodexUserLevelLangGraphBackendRecordAutoRouteEligible -Record $LangGraphRecord)) {
    return 'langgraph'
  }

  if ($NeedsGraphPhases -or $NeedsCheckpointGates -or $NeedsFrozenBrief -or $NeedsSurvivorQueue) {
    return 'langgraph'
  }

  return 'native_omx'
}

function ConvertTo-CodexUserLevelCompressedJson {
  param(
    [Parameter(Mandatory)]
    $InputObject
  )

  return ($InputObject | ConvertTo-Json -Depth 8 -Compress)
}

function Get-CodexUserLevelHybridPlan {
  param(
    [Parameter(Mandatory)]
    [string]$Task,
    [int]$Architect = 0,
    [int]$Planner = 0,
    [int]$Executor = 2,
    [int]$Verifier = 0,
    [ValidateSet('team-executor', 'executor')]
    [string]$WorkerRole = 'team-executor'
  )

  if ($Executor -lt 0) {
    throw "Executor count must be zero or greater: $Executor"
  }

  $status = Get-CodexUserLevelTeamModeStatus
  $expertRoles = @()

  foreach ($expertDefinition in @(
    [ordered]@{ Name = 'architect'; Count = $Architect; Phase = 'plan-freeze' }
    [ordered]@{ Name = 'planner'; Count = $Planner; Phase = 'plan-freeze' }
    [ordered]@{ Name = 'verifier'; Count = $Verifier; Phase = 'post-integration' }
  )) {
    if ([int]$expertDefinition.Count -gt 0) {
      $expertRoles += [ordered]@{
        name = $expertDefinition.Name
        count = [int]$expertDefinition.Count
        lane = 'leader-native-subagent'
        default_phase = $expertDefinition.Phase
      }
    }
  }

  $launchArgs = @('team', ("{0}:{1}" -f $Executor, $WorkerRole), $Task)
  return [ordered]@{
    task = $Task
    current_mode = $status.effective_mode
    oh_my_codex = $status.oh_my_codex
    subagent_routing = $status.subagent_routing
    leader_side_experts = $expertRoles
    durable_team = [ordered]@{
      worker_count = $Executor
      worker_role = $WorkerRole
      launch_args = $launchArgs
    }
    checkpoints = @(
      'freeze implementation brief before durable launch'
      'run leader-side verifier after worker integration'
      'use omx-team-ops for status, await, resume, and shutdown'
    )
    mixed_persistent_panes_default = $false
  }
}

function Get-CodexUserLevelVerificationPlan {
  param(
    [string]$Task = '',
    [bool]$BehaviorChanged = $true,
    [bool]$NeedsSecurityReview = $false,
    [bool]$NeedsDocsReview = $false,
    [bool]$NeedsTestCoverage = $true
  )

  $status = Get-CodexUserLevelTeamModeStatus
  $verificationRoles = @(
    [ordered]@{
      name = 'verifier'
      lane = 'leader-native-subagent'
      reason = 'final acceptance and claim validation'
    }
  )

  if ($NeedsTestCoverage) {
    $verificationRoles += [ordered]@{
      name = 'test-engineer'
      lane = 'leader-native-subagent'
      reason = 'critical-path and regression test coverage'
    }
  }

  if ($NeedsSecurityReview) {
    $verificationRoles += [ordered]@{
      name = 'security-reviewer'
      lane = 'leader-native-subagent'
      reason = 'trust-boundary or sensitive-scope review'
    }
  }

  if ($NeedsDocsReview) {
    $verificationRoles += [ordered]@{
      name = 'writer'
      lane = 'leader-native-subagent'
      reason = 'user-facing, migration, or operator documentation updates'
    }
  }

  return [ordered]@{
    task = $Task
    current_mode = $status.effective_mode
    behavior_changed = $BehaviorChanged
    needs_test_coverage = $NeedsTestCoverage
    needs_security_review = $NeedsSecurityReview
    needs_docs_review = $NeedsDocsReview
    persistent_verifier_team_default = $false
    verification_roles = $verificationRoles
    notes = @(
      'final judgment should stay in the current main Codex CLI session'
      'use native expert roles instead of a default persistent verifier pane'
    )
  }
}

function Get-CodexUserLevelAutomaticTeamPlan {
  param(
    [Parameter(Mandatory)]
    [string]$Task,
    [Parameter(Mandatory)]
    [ValidateSet('define-target', 'read-context', 'freeze-plan', 'execute-parallel', 'integrate-converge', 'stabilize', 'verify-accept')]
    [string]$Phase,
    [ValidateRange(0, 8)]
    [int]$ParallelSlices = 0,
    [ValidateRange(0, 32)]
    [int]$BlockingIssues = 0,
    [string]$Subject = '',
    [string]$RepoRoot,
    [bool]$RequiresCodeChange = $true,
    [bool]$NeedsGraphPhases = $false,
    [bool]$NeedsCheckpointGates = $false,
    [bool]$NeedsFrozenBrief = $false,
    [bool]$NeedsSurvivorQueue = $false
  )

  $status = Get-CodexUserLevelTeamModeStatus
  $resolvedRepoRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
  $teamStateRoot = Get-CodexUserLevelTeamStateRoot -RepoRoot $resolvedRepoRoot
  $activeSelector = Read-CodexUserLevelActiveDurableSelector -RepoRoot $resolvedRepoRoot
  $activeLangGraphSelector = Test-CodexUserLevelActiveDurableSelectorTargetsBackend -Selector $activeSelector -BackendFamily 'langgraph' -RepoRoot $resolvedRepoRoot
  $activeNativeSelector = Test-CodexUserLevelActiveDurableSelectorTargetsBackend -Selector $activeSelector -BackendFamily 'native_omx' -RepoRoot $resolvedRepoRoot
  $phaseDefinition = @(
    Get-CodexUserLevelAutomaticTeamPhaseDefinitions |
      Where-Object { [string]$_.phase -eq $Phase } |
      Select-Object -First 1
  )[0]
  $trackedRecord = Read-CodexUserLevelTrackedTeamRecord -RepoRoot $resolvedRepoRoot
  $langGraphRecord = Read-CodexUserLevelLangGraphBackendRecord -RepoRoot $resolvedRepoRoot
  $effectiveLane = Get-CodexUserLevelEffectiveDurableLane -Status $status -Phase $Phase -NeedsGraphPhases:$NeedsGraphPhases -NeedsCheckpointGates:$NeedsCheckpointGates -NeedsFrozenBrief:$NeedsFrozenBrief -NeedsSurvivorQueue:$NeedsSurvivorQueue -Task $Task -LangGraphRecord $langGraphRecord -ActiveLangGraphSelector $activeLangGraphSelector
  $nativeTeamDirectories = @(Get-CodexUserLevelNativeTeamDirectoriesMetadata -RepoRoot $resolvedRepoRoot)
  $nonEmptyUnmanagedNativeTeamDirectories = @($nativeTeamDirectories | Where-Object { (-not [bool]$_.empty) -and ([string]$_.team_name -ne [string]$trackedRecord.team_name) })
  $latestDetectedTeamName = ''
  if ($nonEmptyUnmanagedNativeTeamDirectories.Count -gt 0) {
    $latestDetectedTeamName = [string]$nonEmptyUnmanagedNativeTeamDirectories[0].team_name
  }

  $trimmedTask = [string]$Task
  if (-not [string]::IsNullOrWhiteSpace($trimmedTask)) {
    $trimmedTask = $trimmedTask.Trim()
  }
  if ([string]::IsNullOrWhiteSpace($Subject)) {
    if ([string]::IsNullOrWhiteSpace($trimmedTask)) {
      $Subject = 'durable team task'
    } elseif ($trimmedTask.Length -gt 80) {
      $Subject = $trimmedTask.Substring(0, 80)
    } else {
      $Subject = $trimmedTask
    }
  }

  $desiredRequired = $false
  $desiredWorkerRole = ''
  $desiredWorkerCount = 0
  $desiredReason = [string]$phaseDefinition.reason
  if ([bool]$phaseDefinition.durable_team) {
    switch ([string]$Phase) {
      'execute-parallel' {
        if ($ParallelSlices -ge 2) {
          $desiredRequired = $true
          $desiredWorkerRole = [string]$phaseDefinition.worker_role
          $desiredWorkerCount = if ($ParallelSlices -ge 3) { 3 } else { [int]$phaseDefinition.default_worker_count }
          $desiredReason = [string]$phaseDefinition.reason
        } else {
          $desiredReason = 'parallel slice threshold not met'
        }
      }
      'integrate-converge' {
        if ($ParallelSlices -ge 2) {
          $desiredRequired = $true
          $desiredWorkerRole = [string]$phaseDefinition.worker_role
          $desiredWorkerCount = if ($ParallelSlices -ge 3) { 3 } else { [int]$phaseDefinition.default_worker_count }
          $desiredReason = [string]$phaseDefinition.reason
        } else {
          $desiredReason = 'parallel slice threshold not met'
        }
      }
      'stabilize' {
        if ($BlockingIssues -ge 1) {
          $desiredRequired = $true
          $desiredWorkerRole = [string]$phaseDefinition.worker_role
          $desiredWorkerCount = [int]$phaseDefinition.default_worker_count
          $desiredReason = [string]$phaseDefinition.reason
        } else {
          $desiredReason = 'blocking issue threshold not met'
        }
      }
    }
  }

  $decision = 'no-team'
  $reasons = @()
  if ([string]$status.subagent_routing -eq 'off') {
    $decision = 'role-orchestration-disabled'
    $reasons += 'subagent routing is disabled'
  } elseif ([string]$status.oh_my_codex -ne 'on') {
    $decision = 'durable-team-unavailable'
    $reasons += 'oh_my_codex is off, so durable team features are unavailable'
  } elseif (-not $desiredRequired) {
    if ($effectiveLane -eq 'langgraph') {
      if ($activeLangGraphSelector) {
        $decision = 'shutdown'
        $reasons += 'the current phase should not keep a tracked LangGraph durable thread active'
      } else {
        $decision = 'no-team'
        $reasons += $desiredReason
      }
    } elseif ($activeNativeSelector -and [bool]$trackedRecord.exists) {
      $decision = 'shutdown'
      $reasons += 'the current phase should not keep a tracked durable team alive'
    } else {
      $decision = 'no-team'
      $reasons += $desiredReason
    }
  } elseif ($effectiveLane -eq 'langgraph') {
    if ($activeLangGraphSelector) {
      $decision = 'resume'
      $reasons += 'tracked LangGraph durable thread already exists for this repository'
    } else {
      $decision = 'launch'
      $reasons += $desiredReason
    }
  } elseif ($activeNativeSelector -and [bool]$trackedRecord.exists) {
    if ([string]$trackedRecord.worker_role -eq $desiredWorkerRole -and [int]$trackedRecord.worker_count -eq $desiredWorkerCount) {
      $decision = 'reuse'
      $reasons += 'tracked durable team already matches the desired shape'
    } else {
      $decision = 'switch'
      $reasons += 'tracked durable team exists but its shape no longer matches the desired phase'
    }
  } elseif (-not [string]::IsNullOrWhiteSpace($latestDetectedTeamName)) {
    $decision = 'manual-inspection-required'
    $reasons += 'an existing team was detected in this repository, but it is not tracked as auto-managed'
  } else {
    $decision = 'launch'
    $reasons += $desiredReason
  }

  $launchArgs = @()
  if ($desiredRequired) {
    $launchArgs = @('team', ("{0}:{1}" -f $desiredWorkerCount, $desiredWorkerRole), $Task)
  }

  $langGraphRunArgs = @()
  $langGraphResumeArgs = @()
  if ($desiredRequired) {
    $langGraphRunArgs = @('-Task', $Task, '-Phase', $Phase, '-RepoRoot', $resolvedRepoRoot)
    if ($PSBoundParameters.ContainsKey('ParallelSlices')) {
      $langGraphRunArgs += @('-ParallelSlices', [string]$ParallelSlices)
    }
    if ($PSBoundParameters.ContainsKey('BlockingIssues')) {
      $langGraphRunArgs += @('-BlockingIssues', [string]$BlockingIssues)
    }
  }
  if ([bool]$langGraphRecord.exists -and -not [string]::IsNullOrWhiteSpace([string]$langGraphRecord.thread_id)) {
    $langGraphResumeArgs = @('-ThreadId', [string]$langGraphRecord.thread_id, '-RepoRoot', $resolvedRepoRoot)
    if (-not [string]::IsNullOrWhiteSpace($Phase)) {
      $langGraphResumeArgs += @('-Phase', $Phase)
    }
  }

  $createTaskPayload = $null
  if ($decision -eq 'reuse' -and [bool]$trackedRecord.exists) {
    $createTaskPayload = [ordered]@{
      team_name = [string]$trackedRecord.team_name
      subject = [string]$Subject
      description = [string]$Task
      requires_code_change = [bool]$RequiresCodeChange
    }
  }

  return [ordered]@{
    task = $Task
    subject = $Subject
    current_mode = $status.effective_mode
    oh_my_codex = $status.oh_my_codex
    subagent_routing = $status.subagent_routing
    langgraph = $status.langgraph
    durable_orchestration_backend = $status.durable_orchestration_backend
    automatic_durable_team_routing_available = ([string]$status.oh_my_codex -eq 'on' -and [string]$status.subagent_routing -eq 'auto')
    phase = $Phase
    parallel_slices = $ParallelSlices
    blocking_issues = $BlockingIssues
    repo_root = $resolvedRepoRoot
    team_state_root = $teamStateRoot
    tracked_record = $trackedRecord
    langgraph_record = $langGraphRecord
    latest_detected_team_name = $latestDetectedTeamName
    desired_durable_team = [ordered]@{
      required = $desiredRequired
      worker_role = $desiredWorkerRole
      worker_count = $desiredWorkerCount
      reason = $desiredReason
      backend = $effectiveLane
    }
    decision = $decision
    reasons = $reasons
    enabled_capabilities = [ordered]@{
      native_subagents = [bool]$status.role_orchestration_available
      native_omx = [bool]$status.native_omx_available
      langgraph = [bool]$status.langgraph_available
    }
    effective_lane = $effectiveLane
    effective_lane_signals = [ordered]@{
      needs_graph_phases = [bool]$NeedsGraphPhases
      needs_checkpoint_gates = [bool]$NeedsCheckpointGates
      needs_frozen_brief = [bool]$NeedsFrozenBrief
      needs_survivor_queue = [bool]$NeedsSurvivorQueue
    }
    helper = [ordered]@{
      script = 'omx-team-auto.ps1'
      apply_required_for_mutation = $true
      tracked_team_record_relative_path = (Get-CodexUserLevelTrackedTeamRecordRelativePath)
    }
    launch_args = $launchArgs
    langgraph_run_args = $langGraphRunArgs
    langgraph_resume_args = $langGraphResumeArgs
    create_task_payload = $createTaskPayload
    shutdown_args = if ([bool]$trackedRecord.exists) { @('team', 'shutdown', [string]$trackedRecord.team_name) } else { @() }
  }
}
'@
}

function Get-CommandRuntimeContent {
  $supportScript = Get-SupportScriptContent
  $supportLines = $supportScript -split "`r?`n"
  return (($supportLines | Select-Object -Skip 1) -join "`n")
}

function Get-CommandScriptContent {
  param(
    [string]$Mutation,
    [ValidateSet('combined', 'omx', 'routing', 'routing_policy', 'backend', 'langgraph')]
    [string]$View = 'combined'
  )

  $runtimeContent = Get-CommandRuntimeContent
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [switch]`$Json
)

$runtimeContent
$Mutation
`$status = Get-CodexUserLevelTeamModeStatus
Write-CodexUserLevelTeamModeStatus -Status `$status -Json:`$Json -View '$View'
"@
}

function Get-CodexSubagentLimitsScriptContent {
  $runtimeContent = Get-CommandRuntimeContent
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Nullable[int]]`$MaxThreads,
  [Nullable[int]]`$MaxDepth,
  [switch]`$Json
)

$runtimeContent

if (`$PSBoundParameters.ContainsKey('MaxThreads') -or `$PSBoundParameters.ContainsKey('MaxDepth')) {
  `$null = Set-CodexUserLevelNativeSubagentLimits -MaxThreads `$MaxThreads -MaxDepth `$MaxDepth
}

`$limits = Get-CodexUserLevelNativeSubagentLimits
`$output = [ordered]@{
  max_threads = [int]`$limits.max_threads
  max_depth = [int]`$limits.max_depth
  state_path = Get-CodexUserLevelNativeSubagentLimitsPath
  write_supported = `$true
}

if (`$Json) {
  `$output | ConvertTo-Json -Depth 5
  return
}

foreach (`$key in @(`$output.Keys)) {
  Write-Output ("{0}={1}" -f `$key, `$output[`$key])
}
"@
}

function Get-CodexDurableStateStatusScriptContent {
  $runtimeContent = Get-CommandRuntimeContent
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [string]`$RepoRoot,
  [switch]`$Json
)

$runtimeContent

`$summary = Get-CodexUserLevelInspectableDurableState -RepoRoot `$RepoRoot
if (`$Json) {
  `$summary | ConvertTo-Json -Depth 8
  return
}

foreach (`$key in @('backend_family', 'state_class', 'repo_root', 'tracked_identity', 'current_phase', 'next_step', 'updated_at', 'selected_backend', 'backend_default', 'backend_ready', 'selector_authority', 'active_selector_status', 'selector_refresh_gap', 'selector_refresh_gap_reason', 'capability_readiness', 'helper_mirror_source_of_truth')) {
  `$value = `$summary[`$key]
  if (`$null -eq `$value) {
    `$display = ''
  } elseif (`$value -is [string]) {
    `$display = `$value
  } else {
    `$display = (`$value | ConvertTo-Json -Depth 8 -Compress)
  }
  Write-Output ("{0}={1}" -f `$key, `$display)
}
"@
}

function Get-CodexDurableStateReconcileScriptContent {
  $runtimeContent = Get-CommandRuntimeContent
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [string]`$RepoRoot,
  [switch]`$Apply,
  [switch]`$Json
)

$runtimeContent

`$plan = Get-CodexUserLevelDurableStateCleanupReconciliationPlan -RepoRoot `$RepoRoot
`$result = [ordered]@{
  repo_root = [string]`$plan.repo_root
  preview_only_default = [bool]`$plan.preview_only_default
  apply_requested = [bool]`$Apply
  safe_cleanup_available = [bool]`$plan.safe_cleanup_available
  manual_reconciliation_required = [bool]`$plan.manual_reconciliation_required
  safe_cleanup_candidates = @(`$plan.safe_cleanup_candidates)
  protected_residue = @(`$plan.protected_residue)
  applied_actions = @()
}

if (`$Apply) {
  foreach (`$candidate in @(`$plan.safe_cleanup_candidates)) {
    switch ([string]`$candidate.kind) {
      'stale_tracked_record' {
        if (Test-Path -LiteralPath ([string]`$candidate.path)) {
          Remove-Item -LiteralPath ([string]`$candidate.path) -Force
        }
        `$result.applied_actions += [ordered]@{
          kind = 'stale_tracked_record'
          path = [string]`$candidate.path
          action = 'removed'
        }
      }
      'stale_compose_runtime_record' {
        if (Test-Path -LiteralPath ([string]`$candidate.path)) {
          Remove-Item -LiteralPath ([string]`$candidate.path) -Force
        }
        `$result.applied_actions += [ordered]@{
          kind = 'stale_compose_runtime_record'
          path = [string]`$candidate.path
          action = 'removed'
        }
      }
      'empty_unmanaged_native_team_directory' {
        if (Test-Path -LiteralPath ([string]`$candidate.path)) {
          Remove-Item -LiteralPath ([string]`$candidate.path) -Force
        }
        `$result.applied_actions += [ordered]@{
          kind = 'empty_unmanaged_native_team_directory'
          path = [string]`$candidate.path
          action = 'removed'
        }
      }
    }
  }

  `$result.safe_cleanup_available = `$false
  `$result.safe_cleanup_candidates = @()
}

if (`$Json) {
  `$result | ConvertTo-Json -Depth 8
  return
}

Write-Output ("repo_root={0}" -f `$result.repo_root)
Write-Output ("apply_requested={0}" -f `$result.apply_requested)
Write-Output ("safe_cleanup_available={0}" -f `$result.safe_cleanup_available)
Write-Output ("manual_reconciliation_required={0}" -f `$result.manual_reconciliation_required)
"@
}

function Get-OmxTeamComposeStatusScriptContent {
  $runtimeContent = Get-CommandRuntimeContent
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [string]`$RepoRoot,
  [switch]`$Json
)

$runtimeContent

`$lifecycle = Get-CodexUserLevelComposeRuntimeLifecyclePlan -RepoRoot `$RepoRoot
`$result = [ordered]@{
  repo_root = [string]`$lifecycle.repo_root
  runtime_exists = [bool]`$lifecycle.runtime_exists
  lifecycle_state = [string]`$lifecycle.lifecycle_state
  health_state = [string]`$lifecycle.health_state
  await_state = [string]`$lifecycle.await_state
  recovery_posture = [string]`$lifecycle.recovery_posture
  runtime = `$lifecycle.runtime
  launched_panes = @(`$lifecycle.runtime.launched_panes)
  planned_only_panes = @(`$lifecycle.runtime.planned_only_panes)
  failed_panes = @(`$lifecycle.runtime.failed_panes)
  pane_helpers = @(`$lifecycle.pane_helpers)
  helper_pointers = `$lifecycle.helper_pointers
  safe_cleanup_available = [bool]`$lifecycle.safe_cleanup_available
  manual_reconciliation_required = [bool]`$lifecycle.manual_reconciliation_required
  safe_cleanup_candidates = @(`$lifecycle.safe_cleanup_candidates)
  protected_residue = @(`$lifecycle.protected_residue)
}

if (`$Json) {
  `$result | ConvertTo-Json -Depth 8
  return
}

Write-Output ("repo_root={0}" -f `$result.repo_root)
Write-Output ("runtime_exists={0}" -f `$result.runtime_exists)
Write-Output ("lifecycle_state={0}" -f `$result.lifecycle_state)
Write-Output ("health_state={0}" -f `$result.health_state)
Write-Output ("await_state={0}" -f `$result.await_state)
Write-Output ("recovery_posture={0}" -f `$result.recovery_posture)
Write-Output ("launched_pane_count={0}" -f @(`$result.launched_panes).Count)
Write-Output ("planned_only_pane_count={0}" -f @(`$result.planned_only_panes).Count)
Write-Output ("failed_pane_count={0}" -f @(`$result.failed_panes).Count)
"@
}

function Get-OmxTeamComposeAwaitScriptContent {
  $runtimeContent = Get-CommandRuntimeContent
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [string]`$RepoRoot,
  [switch]`$Json
)

$runtimeContent

`$lifecycle = Get-CodexUserLevelComposeRuntimeLifecyclePlan -RepoRoot `$RepoRoot
`$presentPanes = @(`$lifecycle.pane_helpers | Where-Object { [bool]`$_.team_exists })
`$missingPanes = @(`$lifecycle.pane_helpers | Where-Object { (-not [bool]`$_.team_exists) -and (-not [string]::IsNullOrWhiteSpace([string]`$_.team_name)) })

`$result = [ordered]@{
  repo_root = [string]`$lifecycle.repo_root
  runtime_exists = [bool]`$lifecycle.runtime_exists
  lifecycle_state = [string]`$lifecycle.lifecycle_state
  health_state = [string]`$lifecycle.health_state
  await_state = [string]`$lifecycle.await_state
  recovery_posture = [string]`$lifecycle.recovery_posture
  active_panes = `$presentPanes
  missing_panes = `$missingPanes
  planned_only_panes = @(`$lifecycle.runtime.planned_only_panes)
  failed_panes = @(`$lifecycle.runtime.failed_panes)
  helper_pointers = `$lifecycle.helper_pointers
  read_only_by_default = `$true
}

if (`$Json) {
  `$result | ConvertTo-Json -Depth 8
  return
}

Write-Output ("repo_root={0}" -f `$result.repo_root)
Write-Output ("runtime_exists={0}" -f `$result.runtime_exists)
Write-Output ("lifecycle_state={0}" -f `$result.lifecycle_state)
Write-Output ("health_state={0}" -f `$result.health_state)
Write-Output ("await_state={0}" -f `$result.await_state)
Write-Output ("recovery_posture={0}" -f `$result.recovery_posture)
Write-Output ("active_pane_count={0}" -f @(`$result.active_panes).Count)
Write-Output ("missing_pane_count={0}" -f @(`$result.missing_panes).Count)
"@
}

function Get-OmxTeamComposeRecoverScriptContent {
  $runtimeContent = Get-CommandRuntimeContent
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [string]`$RepoRoot,
  [switch]`$Json
)

$runtimeContent

`$lifecycle = Get-CodexUserLevelComposeRuntimeLifecyclePlan -RepoRoot `$RepoRoot
`$result = [ordered]@{
  repo_root = [string]`$lifecycle.repo_root
  runtime_exists = [bool]`$lifecycle.runtime_exists
  lifecycle_state = [string]`$lifecycle.lifecycle_state
  health_state = [string]`$lifecycle.health_state
  await_state = [string]`$lifecycle.await_state
  recovery_posture = [string]`$lifecycle.recovery_posture
  recovery_reasons = @(`$lifecycle.recovery_reasons)
  resumable_panes = @(`$lifecycle.resumable_panes)
  non_resumable_panes = @(`$lifecycle.non_resumable_panes)
  helper_pointers = `$lifecycle.helper_pointers
  read_only_by_default = `$true
}

if (`$Json) {
  `$result | ConvertTo-Json -Depth 8
  return
}

Write-Output ("repo_root={0}" -f `$result.repo_root)
Write-Output ("runtime_exists={0}" -f `$result.runtime_exists)
Write-Output ("recovery_posture={0}" -f `$result.recovery_posture)
Write-Output ("resumable_pane_count={0}" -f @(`$result.resumable_panes).Count)
Write-Output ("non_resumable_pane_count={0}" -f @(`$result.non_resumable_panes).Count)
"@
}

function Get-OmxTeamComposeShutdownScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$OmxResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedOmxResolvedPath = $OmxResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [string]`$RepoRoot,
  [switch]`$Apply,
  [switch]`$Json
)

$runtimeContent

`$omxCommandPath = '$escapedOmxResolvedPath'
`$lifecycle = Get-CodexUserLevelComposeRuntimeLifecyclePlan -RepoRoot `$RepoRoot
`$runtime = `$lifecycle.runtime
`$targetedPanes = @(`$lifecycle.pane_helpers | Where-Object { [bool]`$_.team_exists })
`$missingPanes = @(`$lifecycle.pane_helpers | Where-Object { (-not [bool]`$_.team_exists) -and (-not [string]::IsNullOrWhiteSpace([string]`$_.team_name)) })

`$result = [ordered]@{
  repo_root = [string]`$lifecycle.repo_root
  runtime_exists = [bool]`$lifecycle.runtime_exists
  lifecycle_state = [string]`$lifecycle.lifecycle_state
  health_state = [string]`$lifecycle.health_state
  apply_requested = [bool]`$Apply
  targeted_panes = `$targetedPanes
  missing_panes = `$missingPanes
  planned_only_panes = @(`$runtime.planned_only_panes)
  failed_panes = @(`$runtime.failed_panes)
  helper_pointers = `$lifecycle.helper_pointers
  applied = `$false
  applied_decision = if ([bool]`$lifecycle.runtime_exists) { 'preview' } else { 'no_tracked_compose_runtime' }
  applied_actions = @()
  runtime_record_removed = `$false
}

if (`$Apply) {
  if (-not [bool]`$lifecycle.runtime_exists) {
    `$result.applied = `$false
    `$result.applied_decision = 'no_tracked_compose_runtime'
  } elseif (@(`$lifecycle.pane_helpers).Count -eq 0) {
    `$result.applied = `$false
    `$result.applied_decision = 'no_launched_compose_panes'
  } else {
    `$failureCount = 0
    foreach (`$pane in @(`$targetedPanes)) {
      `$commandArgs = @('team', 'shutdown', [string]`$pane.team_name)
      `$output = @()
      `$exitCode = 0
      `$locationPushed = `$false
      try {
        Push-Location -LiteralPath ([string]`$lifecycle.repo_root)
        `$locationPushed = `$true
        `$output = @(& `$omxCommandPath @commandArgs)
        `$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
      }
      catch {
        `$output += [string]`$_.Exception.Message
        `$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 1 }
      }
      finally {
        if (`$locationPushed) {
          Pop-Location
        }
      }

      if (`$exitCode -ne 0) {
        `$failureCount += 1
      }

      `$result.applied_actions += [ordered]@{
        pane_name = [string]`$pane.name
        role = [string]`$pane.role
        team_name = [string]`$pane.team_name
        command_args = `$commandArgs
        output = `$output
        exit_code = `$exitCode
        action = if (`$exitCode -eq 0) { 'shutdown_requested' } else { 'shutdown_failed' }
      }
    }

    if (`$failureCount -eq 0 -and @(`$missingPanes).Count -eq 0) {
      if (Test-Path -LiteralPath ([string]`$runtime.path)) {
        Remove-Item -LiteralPath ([string]`$runtime.path) -Force
      }
      `$result.applied = `$true
      `$result.applied_decision = 'shutdown'
      `$result.runtime_record_removed = `$true
    } elseif (`$failureCount -eq 0 -and @(`$missingPanes).Count -gt 0) {
      `$result.applied = `$true
      `$result.applied_decision = 'shutdown_with_missing_panes'
    } else {
      `$result.applied = `$false
      `$result.applied_decision = 'shutdown_failed'
    }
  }
}

if (`$Json) {
  `$result | ConvertTo-Json -Depth 8
  return
}

Write-Output ("repo_root={0}" -f `$result.repo_root)
Write-Output ("runtime_exists={0}" -f `$result.runtime_exists)
Write-Output ("lifecycle_state={0}" -f `$result.lifecycle_state)
Write-Output ("health_state={0}" -f `$result.health_state)
Write-Output ("apply_requested={0}" -f `$result.apply_requested)
Write-Output ("applied_decision={0}" -f `$result.applied_decision)
"@
}

function Get-OmxTeamComposeReconcileScriptContent {
  $runtimeContent = Get-CommandRuntimeContent
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [string]`$RepoRoot,
  [switch]`$Apply,
  [switch]`$Json
)

$runtimeContent

`$lifecycle = Get-CodexUserLevelComposeRuntimeLifecyclePlan -RepoRoot `$RepoRoot
`$result = [ordered]@{
  repo_root = [string]`$lifecycle.repo_root
  runtime_exists = [bool]`$lifecycle.runtime_exists
  apply_requested = [bool]`$Apply
  safe_cleanup_available = [bool]`$lifecycle.safe_cleanup_available
  manual_reconciliation_required = [bool]`$lifecycle.manual_reconciliation_required
  safe_cleanup_candidates = @(`$lifecycle.safe_cleanup_candidates)
  protected_residue = @(`$lifecycle.protected_residue)
  helper_pointers = `$lifecycle.helper_pointers
  applied_actions = @()
}

if (`$Apply) {
  foreach (`$candidate in @(`$lifecycle.safe_cleanup_candidates)) {
    switch ([string]`$candidate.kind) {
      'stale_compose_runtime_record' {
        if (Test-Path -LiteralPath ([string]`$candidate.path)) {
          Remove-Item -LiteralPath ([string]`$candidate.path) -Force
        }
        `$result.applied_actions += [ordered]@{
          kind = 'stale_compose_runtime_record'
          path = [string]`$candidate.path
          action = 'removed'
        }
      }
    }
  }
  `$result.safe_cleanup_available = `$false
  `$result.safe_cleanup_candidates = @()
}

if (`$Json) {
  `$result | ConvertTo-Json -Depth 8
  return
}

Write-Output ("repo_root={0}" -f `$result.repo_root)
Write-Output ("runtime_exists={0}" -f `$result.runtime_exists)
Write-Output ("safe_cleanup_available={0}" -f `$result.safe_cleanup_available)
Write-Output ("manual_reconciliation_required={0}" -f `$result.manual_reconciliation_required)
"@
}

function Get-ComposeManifestSchemaContent {
  return @'
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "OMX Team Compose Manifest",
  "type": "object",
  "required": ["schema_version", "advanced_opt_in", "leader", "panes"],
  "properties": {
    "schema_version": { "type": "integer", "const": 1 },
    "advanced_opt_in": { "type": "boolean", "const": true },
    "description": { "type": "string" },
    "repo_root": { "type": "string" },
    "leader": {
      "type": "object",
      "required": ["outside_pane_roster"],
      "properties": {
        "outside_pane_roster": { "type": "boolean", "const": true }
      },
      "additionalProperties": true
    },
    "checkpoint_policy": { "type": "object" },
    "panes": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["name", "role"],
        "properties": {
          "name": { "type": "string", "minLength": 1 },
          "role": { "type": "string", "minLength": 1 },
          "workers": { "type": "integer", "minimum": 1 },
          "worktree": { "type": "string" },
          "mailbox": { "type": "string" },
          "checkpoint_group": { "type": "string" },
          "task": { "type": "string" },
          "write_scope": {
            "type": "array",
            "items": { "type": "string" }
          }
        },
        "additionalProperties": true
      }
    }
  },
  "additionalProperties": true
}
'@
}

function Get-OmxTeamComposeScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$OmxResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedOmxResolvedPath = $OmxResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ManifestPath,
  [string]`$RepoRoot,
  [switch]`$Apply,
  [switch]`$Json
)

$runtimeContent

`$omxCommandPath = '$escapedOmxResolvedPath'
`$resolvedRepoRoot = Resolve-CodexUserLevelRepoRoot -OverridePath `$RepoRoot
`$plan = Get-CodexUserLevelMixedPersistentComposePlan -ManifestPath `$ManifestPath -RepoRoot `$resolvedRepoRoot

`$result = [ordered]@{
  manifest_path = [string]`$plan.manifest_path
  manifest_schema_path = [string]`$plan.contract.manifest_schema_path
  repo_root = [string]`$plan.repo_root
  advanced_opt_in = [bool]`$plan.advanced_opt_in
  leader_outside_pane_roster = [bool]`$plan.leader_outside_pane_roster
  default_path_preserved = [bool]`$plan.default_path_preserved
  pane_count = [int]`$plan.pane_count
  panes = @(`$plan.panes)
  supported_panes = @(`$plan.supported_panes)
  unsupported_panes = @(`$plan.unsupported_panes)
  apply_requested = [bool]`$Apply
  apply_supported_for_all_panes = [bool]`$plan.apply_supported_for_all_panes
  compose_state_root = [string]`$plan.compose_state_root
  compose_state_file = [string]`$plan.compose_state_file
  compose_runtime_file = [string]`$plan.compose_runtime_file
  launched_panes = @()
  planned_only_panes = @()
  failed_panes = @()
  pane_results = @()
  contract = `$plan.contract
  applied_mode = if (`$Apply) { 'apply_requested' } else { 'preview_only' }
}

if (`$Apply) {
  if (-not (Test-Path -LiteralPath `$plan.compose_state_root)) {
    New-Item -ItemType Directory -Force -Path `$plan.compose_state_root | Out-Null
  }
  (`$plan | ConvertTo-Json -Depth 8) | Set-Content -LiteralPath ([string]`$plan.compose_state_file) -Encoding UTF8 -NoNewline

  foreach (`$pane in @(`$plan.panes)) {
    `$paneResult = [ordered]@{
      name = [string]`$pane.name
      role = [string]`$pane.role
      workers = [int]`$pane.workers
      task = [string]`$pane.task
      worktree = [string]`$pane.worktree
      mailbox = [string]`$pane.mailbox
      checkpoint_group = [string]`$pane.checkpoint_group
      launch_supported = [bool]`$pane.launch_supported
      launch_strategy = [string]`$pane.launch_strategy
      runtime_status = ''
      failure_kind = ''
      team_name = ''
      launch_args = @()
      launch_output = @()
      detected_team_names = @()
    }

    if (-not [bool]`$pane.launch_supported) {
      `$paneResult.runtime_status = 'planned_only'
      `$paneResult.failure_kind = 'unsupported_role'
      `$result.planned_only_panes += `$paneResult
      `$result.pane_results += `$paneResult
      continue
    }

    if ([string]::IsNullOrWhiteSpace([string]`$pane.task)) {
      `$paneResult.runtime_status = 'launch_failed'
      `$paneResult.failure_kind = 'missing_task'
      `$result.failed_panes += `$paneResult
      `$result.pane_results += `$paneResult
      continue
    }

    `$launchArgs = @('team', ("{0}:{1}" -f [int]`$pane.workers, [string]`$pane.role), [string]`$pane.task)
    `$paneResult.launch_args = `$launchArgs
    `$beforeTeams = @(Get-CodexUserLevelTeamDirectoryNames -RepoRoot `$resolvedRepoRoot)
    `$locationPushed = `$false
    `$launchOutput = @()
    `$launchExitCode = 0

    try {
      Push-Location -LiteralPath `$resolvedRepoRoot
      `$locationPushed = `$true
      `$launchOutput = @(& `$omxCommandPath @launchArgs)
      `$launchExitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
    }
    catch {
      `$launchOutput += [string]`$_.Exception.Message
      `$launchExitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 1 }
    }
    finally {
      if (`$locationPushed) {
        Pop-Location
      }
    }

    `$afterTeams = @(Get-CodexUserLevelTeamDirectoryNames -RepoRoot `$resolvedRepoRoot)
    `$newTeams = @(`$afterTeams | Where-Object { `$_ -notin `$beforeTeams })
    `$paneResult.launch_output = `$launchOutput
    `$paneResult.detected_team_names = `$newTeams

    `$reportedTeamName = ''
    if (@(`$launchOutput).Count -gt 0) {
      try {
        `$launchPayload = ((`$launchOutput -join "`n") | ConvertFrom-Json)
        if (`$null -ne `$launchPayload.PSObject.Properties['team_name']) {
          `$reportedTeamName = [string]`$launchPayload.team_name
        }
      }
      catch {
      }
    }

    `$resolvedTeamName = ''
    if (@(`$newTeams).Count -eq 1) {
      `$resolvedTeamName = [string]`$newTeams[0]
    } elseif (@(`$newTeams).Count -eq 0 -and -not [string]::IsNullOrWhiteSpace(`$reportedTeamName) -and (Test-CodexUserLevelTeamDirectoryExists -RepoRoot `$resolvedRepoRoot -TeamName `$reportedTeamName)) {
      `$resolvedTeamName = `$reportedTeamName
    }

    if (`$launchExitCode -eq 0 -and -not [string]::IsNullOrWhiteSpace(`$resolvedTeamName)) {
      `$paneResult.runtime_status = 'launched'
      `$paneResult.team_name = `$resolvedTeamName
      `$result.launched_panes += `$paneResult
    } else {
      `$paneResult.runtime_status = 'launch_failed'
      if (`$launchExitCode -ne 0) {
        `$paneResult.failure_kind = 'omx_exit_nonzero'
      } elseif (@(`$newTeams).Count -gt 1) {
        `$paneResult.failure_kind = 'ambiguous_team_detection'
      } else {
        `$paneResult.failure_kind = 'team_detection_failed'
      }
      `$result.failed_panes += `$paneResult
    }

    `$result.pane_results += `$paneResult
  }

  `$launchedCount = @(`$result.launched_panes).Count
  `$plannedOnlyCount = @(`$result.planned_only_panes).Count
  `$failedCount = @(`$result.failed_panes).Count
  if (`$failedCount -gt 0 -and `$launchedCount -gt 0) {
    `$result.applied_mode = 'supported_launch_with_failures'
  } elseif (`$failedCount -gt 0 -and `$plannedOnlyCount -gt 0) {
    `$result.applied_mode = 'planned_only_with_failures'
  } elseif (`$failedCount -gt 0) {
    `$result.applied_mode = 'apply_failed_no_successful_launch'
  } elseif (`$launchedCount -gt 0 -and `$plannedOnlyCount -gt 0) {
    `$result.applied_mode = 'supported_launch_with_planned_only'
  } elseif (`$launchedCount -gt 0) {
    `$result.applied_mode = 'supported_launch_only'
  } elseif (`$plannedOnlyCount -gt 0) {
    `$result.applied_mode = 'planned_only_no_supported_panes'
  } else {
    `$result.applied_mode = 'apply_no_panes'
  }

  `$composeRuntime = [ordered]@{
    runtime_id = ('compose-runtime-{0}' -f ((Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffffffZ')))
    manifest_path = [string]`$result.manifest_path
    repo_root = [string]`$result.repo_root
    backend_family = 'native_omx'
    applied_mode = [string]`$result.applied_mode
    launched_panes = @(`$result.launched_panes)
    planned_only_panes = @(`$result.planned_only_panes)
    failed_panes = @(`$result.failed_panes)
    pane_results = @(`$result.pane_results)
    updated_at = (Get-Date).ToUniversalTime().ToString('o')
  }

  (`$composeRuntime | ConvertTo-Json -Depth 8) | Set-Content -LiteralPath ([string]`$result.compose_runtime_file) -Encoding UTF8 -NoNewline
}

if (`$Json) {
  `$result | ConvertTo-Json -Depth 8
  return
}

Write-Output ("manifest_path={0}" -f `$result.manifest_path)
Write-Output ("pane_count={0}" -f `$result.pane_count)
Write-Output ("apply_requested={0}" -f `$result.apply_requested)
Write-Output ("apply_supported_for_all_panes={0}" -f `$result.apply_supported_for_all_panes)
Write-Output ("applied_mode={0}" -f `$result.applied_mode)
"@
}

function Get-LangGraphRunScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$Task,
  [ValidateSet('define-target', 'read-context', 'freeze-plan', 'execute-parallel', 'integrate-converge', 'stabilize', 'verify-accept')]
  [string]`$Phase = 'define-target',
  [string]`$RepoRoot,
  [string]`$ThreadId,
  [string]`$TaskId,
  [string]`$WorktreeId,
  [ValidateRange(0, 8)]
  [int]`$ParallelSlices = 0,
  [ValidateRange(0, 32)]
  [int]`$BlockingIssues = 0,
  [ValidateSet('review', 'execution', 'stabilization')]
  [string]`$LoopKind,
  [ValidateRange(0, 32)]
  [int]`$IterationBudget = 0,
  [ValidateSet('update', 'goto', 'update_goto', 'resume', 'resume_with_payload', 'parent_handoff', 'resume_parent_handoff')]
  [string]`$CommandKind,
  [string]`$CommandGoto,
  [ValidateSet('current', 'parent')]
  [string]`$CommandGraphScope,
  [string]`$ParentHandoffTarget,
  [string]`$CommandUpdateJson,
  [string]`$CommandUpdateFile,
  [string]`$ResumePayloadJson,
  [string]`$ResumePayloadFile,
  [string]`$ResumeMapJson,
  [string]`$ResumeMapFile,
  [switch]`$AwaitCommandResume,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'run', '--task', `$Task, '--phase', `$Phase)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$ThreadId)) { `$commandArgs += @('--thread-id', `$ThreadId) }
if (-not [string]::IsNullOrWhiteSpace(`$TaskId)) { `$commandArgs += @('--task-id', `$TaskId) }
if (-not [string]::IsNullOrWhiteSpace(`$WorktreeId)) { `$commandArgs += @('--worktree-id', `$WorktreeId) }
if (-not [string]::IsNullOrWhiteSpace(`$LoopKind)) { `$commandArgs += @('--loop-kind', `$LoopKind) }
if (`$IterationBudget -gt 0) { `$commandArgs += @('--iteration-budget', [string]`$IterationBudget) }
if (-not [string]::IsNullOrWhiteSpace(`$CommandKind)) { `$commandArgs += @('--command-kind', `$CommandKind) }
if (-not [string]::IsNullOrWhiteSpace(`$CommandGoto)) { `$commandArgs += @('--command-goto', `$CommandGoto) }
if (-not [string]::IsNullOrWhiteSpace(`$CommandGraphScope)) { `$commandArgs += @('--command-graph-scope', `$CommandGraphScope) }
if (-not [string]::IsNullOrWhiteSpace(`$ParentHandoffTarget)) { `$commandArgs += @('--parent-handoff-target', `$ParentHandoffTarget) }
if (-not [string]::IsNullOrWhiteSpace(`$CommandUpdateJson)) { `$commandArgs += @('--command-update-json', `$CommandUpdateJson) }
if (-not [string]::IsNullOrWhiteSpace(`$CommandUpdateFile)) { `$commandArgs += @('--command-update-file', `$CommandUpdateFile) }
if (-not [string]::IsNullOrWhiteSpace(`$ResumePayloadJson)) { `$commandArgs += @('--resume-payload-json', `$ResumePayloadJson) }
if (-not [string]::IsNullOrWhiteSpace(`$ResumePayloadFile)) { `$commandArgs += @('--resume-payload-file', `$ResumePayloadFile) }
if (-not [string]::IsNullOrWhiteSpace(`$ResumeMapJson)) { `$commandArgs += @('--resume-map-json', `$ResumeMapJson) }
if (-not [string]::IsNullOrWhiteSpace(`$ResumeMapFile)) { `$commandArgs += @('--resume-map-file', `$ResumeMapFile) }
if (`$AwaitCommandResume) { `$commandArgs += '--await-command-resume' }
`$commandArgs += @('--parallel-slices', [string]`$ParallelSlices, '--blocking-issues', [string]`$BlockingIssues)

& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphInstallScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [switch]`$IncludeLocalServerCli,
  [switch]`$DryRun,
  [switch]`$Json
)

$runtimeContent

`$basePythonCommandPath = '$escapedPythonResolvedPath'
`$plan = Get-CodexUserLevelLangGraphInstallPlan -BasePythonCommandPath `$basePythonCommandPath -IncludeLocalServerCli:`$IncludeLocalServerCli
if (`$DryRun -or `$Json) {
  `$result = [ordered]@{
    action = if (`$DryRun) { 'dry_run' } else { 'inspect' }
    plan = `$plan
  }
  `$result | ConvertTo-Json -Depth 8
  return
}

if (-not (Test-Path -LiteralPath (Get-CodexUserLevelVenvsDirectory))) {
  New-Item -ItemType Directory -Force -Path (Get-CodexUserLevelVenvsDirectory) | Out-Null
}
& `$basePythonCommandPath -m venv ([string]`$plan.shared_venv_path)
`$venvExitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
if (`$venvExitCode -ne 0) {
  throw ('Failed to create the shared LangGraph venv at {0}.' -f [string]`$plan.shared_venv_path)
}

`$sharedPythonPath = [string]`$plan.shared_python_path
& `$sharedPythonPath -m pip --isolated install --upgrade pip --index-url https://mirrors.aliyun.com/pypi/simple/
`$pipUpgradeExitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
if (`$pipUpgradeExitCode -ne 0) {
  throw 'Failed to upgrade pip in the shared LangGraph venv.'
}

`$installedPackages = @()
foreach (`$package in @([string[]]`$plan.packages)) {
  & `$sharedPythonPath -m pip --isolated install --upgrade --index-url https://mirrors.aliyun.com/pypi/simple/ `$package
  `$installExitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
  if (`$installExitCode -ne 0) {
    throw ('Failed to install package {0} into the shared LangGraph venv.' -f [string]`$package)
  }
  `$installedPackages += [string]`$package
}

[ordered]@{
  action = 'installed'
  plan = `$plan
  installed_packages = `$installedPackages
} | ConvertTo-Json -Depth 8
"@
}

function Get-LangGraphCliScriptContent {
  $runtimeContent = Get-CommandRuntimeContent
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(ValueFromRemainingArguments = `$true)]
  [string[]]`$Arguments
)

$runtimeContent

`$langGraphCliPath = Get-CodexUserLevelLangGraphCliExecutablePath
if (-not (Test-Path -LiteralPath `$langGraphCliPath)) {
  throw 'Shared LangGraph CLI is not installed. Run omx-langgraph-install.ps1 -IncludeLocalServerCli first.'
}

`$hadPythonUtf8 = Test-Path -LiteralPath Env:PYTHONUTF8
`$hadPythonIoEncoding = Test-Path -LiteralPath Env:PYTHONIOENCODING
`$previousPythonUtf8 = if (`$hadPythonUtf8) { [string]`$env:PYTHONUTF8 } else { '' }
`$previousPythonIoEncoding = if (`$hadPythonIoEncoding) { [string]`$env:PYTHONIOENCODING } else { '' }

`$env:PYTHONUTF8 = '1'
`$env:PYTHONIOENCODING = 'utf-8'

try {
  & `$langGraphCliPath @Arguments
  `$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
}
finally {
  if (`$hadPythonUtf8) {
    `$env:PYTHONUTF8 = `$previousPythonUtf8
  } else {
    Remove-Item Env:PYTHONUTF8 -ErrorAction SilentlyContinue
  }

  if (`$hadPythonIoEncoding) {
    `$env:PYTHONIOENCODING = `$previousPythonIoEncoding
  } else {
    Remove-Item Env:PYTHONIOENCODING -ErrorAction SilentlyContinue
  }
}

exit `$exitCode
"@
}

function Get-LangGraphStatusScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'status', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphResumeScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('define-target', 'read-context', 'freeze-plan', 'execute-parallel', 'integrate-converge', 'stabilize', 'verify-accept')]
  [string]`$Phase,
  [ValidateSet('review', 'execution', 'stabilization')]
  [string]`$LoopKind,
  [ValidateRange(0, 32)]
  [int]`$IterationBudget = 0,
  [ValidateSet('accept', 'revise', 'escalate', 'halt', 'needs_human')]
  [string]`$GateVerdict,
  [string]`$GateReason,
  [ValidateSet('update', 'goto', 'update_goto', 'resume', 'resume_with_payload', 'parent_handoff', 'resume_parent_handoff')]
  [string]`$CommandKind,
  [string]`$CommandGoto,
  [ValidateSet('current', 'parent')]
  [string]`$CommandGraphScope,
  [string]`$ParentHandoffTarget,
  [string]`$CommandUpdateJson,
  [string]`$CommandUpdateFile,
  [string]`$ResumePayloadJson,
  [string]`$ResumePayloadFile,
  [string]`$ResumeMapJson,
  [string]`$ResumeMapFile,
  [switch]`$AwaitCommandResume,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'resume', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$Phase)) { `$commandArgs += @('--phase', `$Phase) }
if (-not [string]::IsNullOrWhiteSpace(`$LoopKind)) { `$commandArgs += @('--loop-kind', `$LoopKind) }
if (`$IterationBudget -gt 0) { `$commandArgs += @('--iteration-budget', [string]`$IterationBudget) }
if (-not [string]::IsNullOrWhiteSpace(`$GateVerdict)) { `$commandArgs += @('--gate-verdict', `$GateVerdict) }
if (-not [string]::IsNullOrWhiteSpace(`$GateReason)) { `$commandArgs += @('--gate-reason', `$GateReason) }
if (-not [string]::IsNullOrWhiteSpace(`$CommandKind)) { `$commandArgs += @('--command-kind', `$CommandKind) }
if (-not [string]::IsNullOrWhiteSpace(`$CommandGoto)) { `$commandArgs += @('--command-goto', `$CommandGoto) }
if (-not [string]::IsNullOrWhiteSpace(`$CommandGraphScope)) { `$commandArgs += @('--command-graph-scope', `$CommandGraphScope) }
if (-not [string]::IsNullOrWhiteSpace(`$ParentHandoffTarget)) { `$commandArgs += @('--parent-handoff-target', `$ParentHandoffTarget) }
if (-not [string]::IsNullOrWhiteSpace(`$CommandUpdateJson)) { `$commandArgs += @('--command-update-json', `$CommandUpdateJson) }
if (-not [string]::IsNullOrWhiteSpace(`$CommandUpdateFile)) { `$commandArgs += @('--command-update-file', `$CommandUpdateFile) }
if (-not [string]::IsNullOrWhiteSpace(`$ResumePayloadJson)) { `$commandArgs += @('--resume-payload-json', `$ResumePayloadJson) }
if (-not [string]::IsNullOrWhiteSpace(`$ResumePayloadFile)) { `$commandArgs += @('--resume-payload-file', `$ResumePayloadFile) }
if (-not [string]::IsNullOrWhiteSpace(`$ResumeMapJson)) { `$commandArgs += @('--resume-map-json', `$ResumeMapJson) }
if (-not [string]::IsNullOrWhiteSpace(`$ResumeMapFile)) { `$commandArgs += @('--resume-map-file', `$ResumeMapFile) }
if (`$AwaitCommandResume) { `$commandArgs += '--await-command-resume' }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphInspectScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'inspect')
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$ThreadId)) { `$commandArgs += @('--thread-id', `$ThreadId) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphKernelScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'kernel', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'engine', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphMigrationScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [string]`$CurrentGraphContractId,
  [string]`$CurrentTopologyVersion,
  [string]`$CurrentStateSchemaVersion,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'migration', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$CurrentGraphContractId)) { `$commandArgs += @('--current-graph-contract-id', `$CurrentGraphContractId) }
if (-not [string]::IsNullOrWhiteSpace(`$CurrentTopologyVersion)) { `$commandArgs += @('--current-topology-version', `$CurrentTopologyVersion) }
if (-not [string]::IsNullOrWhiteSpace(`$CurrentStateSchemaVersion)) { `$commandArgs += @('--current-state-schema-version', `$CurrentStateSchemaVersion) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphInvocationScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$InvokeKind,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'invocation', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$InvokeKind)) { `$commandArgs += @('--invoke-kind', `$InvokeKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphLiveExecutionScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'live-execution', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphFullerEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'fuller-engine', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphDeeperEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [int]`$RecursionLimit = 8,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'deeper-engine', '--thread-id', `$ThreadId, '--recursion-limit', [string]`$RecursionLimit)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphSuperstepEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [int]`$RecursionLimit = 8,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'superstep-engine', '--thread-id', `$ThreadId, '--recursion-limit', [string]`$RecursionLimit)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphStatefulEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [int]`$RecursionLimit = 8,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'stateful-engine', '--thread-id', `$ThreadId, '--recursion-limit', [string]`$RecursionLimit)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphBoundaryEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [int]`$RecursionLimit = 8,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'boundary-engine', '--thread-id', `$ThreadId, '--recursion-limit', [string]`$RecursionLimit)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphHandoffEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [int]`$RecursionLimit = 8,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'handoff-engine', '--thread-id', `$ThreadId, '--recursion-limit', [string]`$RecursionLimit)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphApprovalEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [int]`$RecursionLimit = 8,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'approval-engine', '--thread-id', `$ThreadId, '--recursion-limit', [string]`$RecursionLimit)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphProvenanceEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [int]`$RecursionLimit = 8,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'provenance-engine', '--thread-id', `$ThreadId, '--recursion-limit', [string]`$RecursionLimit)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphArtifactEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [int]`$RecursionLimit = 8,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'artifact-engine', '--thread-id', `$ThreadId, '--recursion-limit', [string]`$RecursionLimit)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphReducerEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [int]`$RecursionLimit = 8,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'reducer-engine', '--thread-id', `$ThreadId, '--recursion-limit', [string]`$RecursionLimit)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphCommandEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [int]`$RecursionLimit = 8,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'command-engine', '--thread-id', `$ThreadId, '--recursion-limit', [string]`$RecursionLimit)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphRuntimeEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [int]`$RecursionLimit = 8,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'runtime-engine', '--thread-id', `$ThreadId, '--recursion-limit', [string]`$RecursionLimit)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphMemoryEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [int]`$RecursionLimit = 8,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'memory-engine', '--thread-id', `$ThreadId, '--recursion-limit', [string]`$RecursionLimit)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphMigrationEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [int]`$RecursionLimit = 8,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'migration-engine', '--thread-id', `$ThreadId, '--recursion-limit', [string]`$RecursionLimit)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphMigrationEngineScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [ValidateSet('invoke', 'stream')]
  [string]`$RunKind,
  [int]`$RecursionLimit = 8,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'migration-engine', '--thread-id', `$ThreadId, '--recursion-limit', [string]`$RecursionLimit)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$RunKind)) { `$commandArgs += @('--run-kind', `$RunKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphAutoPolicyScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [switch]`$Apply,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'auto-policy', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (`$Apply) { `$commandArgs += '--apply' }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphSubgraphStateScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'subgraph-state', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphGeneralizedRoutingScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'generalized-routing', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphApprovalQueueScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [string[]]`$InterruptItemJson = @(),
  [string[]]`$InterruptItemFile = @(),
  [string]`$DefaultInterruptPoint,
  [string]`$DefaultReason,
  [string]`$ResumeMapJson,
  [string]`$ResumeMapFile,
  [switch]`$ClearQueue,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'approval-queue', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
foreach (`$rawItem in @(`$InterruptItemJson)) {
  if (-not [string]::IsNullOrWhiteSpace([string]`$rawItem)) { `$commandArgs += @('--interrupt-item-json', [string]`$rawItem) }
}
foreach (`$rawItemFile in @(`$InterruptItemFile)) {
  if (-not [string]::IsNullOrWhiteSpace([string]`$rawItemFile)) { `$commandArgs += @('--interrupt-item-file', [string]`$rawItemFile) }
}
if (-not [string]::IsNullOrWhiteSpace(`$DefaultInterruptPoint)) { `$commandArgs += @('--default-interrupt-point', `$DefaultInterruptPoint) }
if (-not [string]::IsNullOrWhiteSpace(`$DefaultReason)) { `$commandArgs += @('--default-reason', `$DefaultReason) }
if (-not [string]::IsNullOrWhiteSpace(`$ResumeMapJson)) { `$commandArgs += @('--resume-map-json', `$ResumeMapJson) }
if (-not [string]::IsNullOrWhiteSpace(`$ResumeMapFile)) { `$commandArgs += @('--resume-map-file', `$ResumeMapFile) }
if (`$ClearQueue) { `$commandArgs += '--clear-queue' }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphSubgraphsScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'subgraphs')
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$ThreadId)) { `$commandArgs += @('--thread-id', `$ThreadId) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphRuntimeScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [string]`$ContextSchema,
  [string]`$RuntimeContextJson,
  [string]`$RuntimeContextFile,
  [switch]`$StoreConfigured,
  [switch]`$StoreAccessExpected,
  [string]`$StoreKind,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'runtime', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (-not [string]::IsNullOrWhiteSpace(`$ContextSchema)) { `$commandArgs += @('--context-schema', `$ContextSchema) }
if (-not [string]::IsNullOrWhiteSpace(`$RuntimeContextJson)) { `$commandArgs += @('--runtime-context-json', `$RuntimeContextJson) }
if (-not [string]::IsNullOrWhiteSpace(`$RuntimeContextFile)) { `$commandArgs += @('--runtime-context-file', `$RuntimeContextFile) }
if (`$StoreConfigured) { `$commandArgs += '--store-configured' }
if (`$StoreAccessExpected) { `$commandArgs += '--store-access-expected' }
if (-not [string]::IsNullOrWhiteSpace(`$StoreKind)) { `$commandArgs += @('--store-kind', `$StoreKind) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphMemoryScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [switch]`$MemoryStoreConfigured,
  [string]`$MemoryStoreKind,
  [string[]]`$MemoryNamespace = @(),
  [switch]`$SemanticMemoryEnabled,
  [string]`$SemanticStoreKind,
  [string[]]`$SemanticNamespace = @(),
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'memory', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
if (`$MemoryStoreConfigured) { `$commandArgs += '--memory-store-configured' }
if (-not [string]::IsNullOrWhiteSpace(`$MemoryStoreKind)) { `$commandArgs += @('--memory-store-kind', `$MemoryStoreKind) }
foreach (`$namespaceGroup in @(`$MemoryNamespace)) {
  foreach (`$namespace in @(([string]`$namespaceGroup).Split(',') | Where-Object { -not [string]::IsNullOrWhiteSpace([string]`$_) })) {
    `$commandArgs += @('--memory-namespace', ([string]`$namespace).Trim())
  }
}
if (`$SemanticMemoryEnabled) { `$commandArgs += '--semantic-memory-enabled' }
if (-not [string]::IsNullOrWhiteSpace(`$SemanticStoreKind)) { `$commandArgs += @('--semantic-store-kind', `$SemanticStoreKind) }
foreach (`$namespaceGroup in @(`$SemanticNamespace)) {
  foreach (`$namespace in @(([string]`$namespaceGroup).Split(',') | Where-Object { -not [string]::IsNullOrWhiteSpace([string]`$_) })) {
    `$commandArgs += @('--semantic-namespace', ([string]`$namespace).Trim())
  }
}
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphStreamScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [string[]]`$StreamMode = @(),
  [switch]`$Subgraphs,
  [ValidateSet('updates', 'checkpoints', 'tasks', 'debug')]
  [string]`$EventKind,
  [string[]]`$Namespace = @(),
  [string]`$CheckpointKind,
  [string]`$TaskPath,
  [string]`$TaskStatus,
  [string]`$DebugSummary,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'stream', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
foreach (`$modeGroup in @(`$StreamMode)) {
  foreach (`$mode in @(([string]`$modeGroup).Split(',') | Where-Object { -not [string]::IsNullOrWhiteSpace([string]`$_) })) {
    `$commandArgs += @('--stream-mode', ([string]`$mode).Trim())
  }
}
if (`$Subgraphs) { `$commandArgs += '--subgraphs' }
if (-not [string]::IsNullOrWhiteSpace(`$EventKind)) { `$commandArgs += @('--event-kind', `$EventKind) }
foreach (`$namespaceGroup in @(`$Namespace)) {
  foreach (`$namespacePart in @(([string]`$namespaceGroup).Split(',') | Where-Object { -not [string]::IsNullOrWhiteSpace([string]`$_) })) {
    `$commandArgs += @('--namespace', ([string]`$namespacePart).Trim())
  }
}
if (-not [string]::IsNullOrWhiteSpace(`$CheckpointKind)) { `$commandArgs += @('--checkpoint-kind', `$CheckpointKind) }
if (-not [string]::IsNullOrWhiteSpace(`$TaskPath)) { `$commandArgs += @('--task-path', `$TaskPath) }
if (-not [string]::IsNullOrWhiteSpace(`$TaskStatus)) { `$commandArgs += @('--task-status', `$TaskStatus) }
if (-not [string]::IsNullOrWhiteSpace(`$DebugSummary)) { `$commandArgs += @('--debug-summary', `$DebugSummary) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphHistoryScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [string]`$RepoRoot,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'history', '--thread-id', `$ThreadId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphReplayScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [Parameter(Mandatory)]
  [string]`$TargetId,
  [string]`$RepoRoot,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'replay', '--thread-id', `$ThreadId, '--target-id', `$TargetId)
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-LangGraphRecoverScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$PythonResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedPythonResolvedPath = $PythonResolvedPath.Replace("'", "''")
  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$ThreadId,
  [Parameter(Mandatory)]
  [ValidateSet('explicit-recovery')]
  [string]`$MutationIntent,
  [string]`$TargetId,
  [string[]]`$ThreadField = @(),
  [string[]]`$InterruptField = @(),
  [switch]`$ClearInterrupt,
  [string]`$RepoRoot,
  [switch]`$Json
)

$runtimeContent

`$pythonCommandPath = Get-CodexUserLevelLangGraphPythonCommandPath -FallbackPath '$escapedPythonResolvedPath'
`$backendScriptPath = Get-CodexUserLevelLangGraphScriptPath
`$commandArgs = @(`$backendScriptPath, 'recover', '--thread-id', `$ThreadId, '--mutation-intent', `$MutationIntent)
if (-not [string]::IsNullOrWhiteSpace(`$TargetId)) { `$commandArgs += @('--target-id', `$TargetId) }
foreach (`$fieldGroup in @(`$ThreadField)) {
  foreach (`$field in @(([string]`$fieldGroup).Split(',') | Where-Object { -not [string]::IsNullOrWhiteSpace([string]`$_) })) {
    `$commandArgs += @('--thread-field', ([string]`$field).Trim())
  }
}
foreach (`$fieldGroup in @(`$InterruptField)) {
  foreach (`$field in @(([string]`$fieldGroup).Split(',') | Where-Object { -not [string]::IsNullOrWhiteSpace([string]`$_) })) {
    `$commandArgs += @('--interrupt-field', ([string]`$field).Trim())
  }
}
if (`$ClearInterrupt) { `$commandArgs += '--clear-interrupt' }
if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) { `$commandArgs += @('--repo-root', `$RepoRoot) }
& `$pythonCommandPath @commandArgs
`$exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
exit `$exitCode
"@
}

function Get-TeamPlaybookContent {
  return @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
# Team Mode Playbook

For the minimal high-frequency command card, see `team-mode-quick-reference.md`.

## Global automatic collaboration default

- Automatic collaboration is the default behavior for all projects and all user-level Codex sessions.
- The user does not need to repeat phrases such as "use experts", "use durable_team", "use persistent team", "parallel", or "subagents" for automatic routing to apply.
- On each activation event, classify the task phase and evaluate whether the smallest sufficient collaboration surface should include native experts, `native_omx`, LangGraph durable workflow, or a persistent team.
- Qualifying signals include broad scope, high risk, multi-document updates, multi-stage execution, bounded multi-face research, independent execution slices, cross-module design, stabilization-heavy defects, or verification-heavy acceptance.
- Do not cite "the user did not request parallelism/subagents/experts" as a reason to skip orchestration. Valid reasons are task phase, no frozen plan, insufficient execution slices, backend not ready, concrete preflight failure, write-ownership conflict, explicit user disablement, or main-session takeover.
- If native `spawn_agent` invocation is blocked by the current platform/tool contract, report `experts=blocked:platform_subagent_invocation_constraint`; then continue with an eligible durable backend, a narrower available expert path, or explicit main-session takeover.
- If `subagent_routing!=off`, `oh_my_codex=on`, `langgraph=on`, and LangGraph readiness is true, report `backend_default=langgraph` for graph-shaped durable work. This readiness does not imply that a persistent team is already running.
- Durable/persistent team selection is threshold-gated: normally `frozen_plan=true` plus 2+ mostly independent execution slices for `execute-parallel` or `integrate-converge`; 1+ blocking issues for debugger lanes during `stabilize`.
- Expert timeout, stall, or upstream pacing is non-evidence. Continue bounded waits, request progress, respawn a narrower expert, hand off to an eligible durable lane, or record main-session takeover. Never treat timeout as successful fan-in.

## Mode states

- `oh_my_codex=on`, `subagent_routing=auto`
  - enhanced mode
  - durable team features available
- `oh_my_codex=off`, `subagent_routing=auto`
  - native routed mode
  - wrapped `codex` still forwards into native Codex as the startup base layer
- `oh_my_codex=off`, `subagent_routing=off`
  - pure debugging mode
  - no role orchestration

## Durable orchestration backend

- `durable_orchestration_backend=native_omx`
  - current compatibility view for the worker-centric durable path
- `durable_orchestration_backend=langgraph`
  - current compatibility view for the LangGraph durable path

Current implemented model:

- the current state still keeps a compatibility durable backend view
- it is derived from layered capability state rather than treated as the only true control surface
- when `langgraph=on`, LangGraph capability is available
- when `oh_my_codex=on`, `native_omx` durable execution remains available as the worker-centric default lane

## Layered capability switches

- `subagent_routing = auto | manual | off`
  - controls whether native expert routing is available
- `completed_subagent_retention = close | keep`
  - controls whether completed subagents are closed by default after fan-in or kept until explicit close
- `oh_my_codex = on | off`
  - controls whether durable team features are exposed
- `langgraph = on | off`
  - controls whether LangGraph is available as a durable orchestration capability

Dependency rules:

- `subagent_routing=off`
  - disables higher orchestration layers
- `oh_my_codex=off`
  - disables LangGraph availability
- `langgraph=on`
  - requires `oh_my_codex=on`
  - requires subagent routing availability

Selection rules:

- keep `native_omx` as the stable default lane for worker-centric durable execution
- prefer `native_omx` for worker-centric durable execution, worktree isolation, mailbox flow, and direct worker lifecycle control
- prefer `langgraph` for graph-shaped multi-phase execution, checkpoint-driven recovery, interrupt/resume approval gates, persisted implementation briefs, and persisted survivor queues
- do not silently switch backend family during automatic durable routing
- allow effective lane choice to vary per task flow across enabled capabilities
- one durable task should use one backend family at a time

## Global provider pacing

- the provider proxy enforces a shared upstream pacing budget
- at most 10 true upstream provider forwards per rolling 1-minute window
- local deterministic handling does not consume the upstream-forward budget
- when the budget is saturated, excess upstream-bound requests wait for a slot instead of immediately returning a local 429
- do not treat this pacing budget alone as a reason to avoid LangGraph, `native_omx`, or native subagents
- treat pacing as backpressure: keep orchestration available, prefer local-first phases, and bound upstream fan-out when many agent steps may hit the provider

## Orchestration activation and retrofit

- run orchestration activation checks on:
  - the first substantive turn of a new wrapped session
  - every session reload
  - every `codex` restart
  - task phase changes
  - expansion from one slice to two or more execution slices
  - tracked `.omx` durable-state detection
  - explicit user requests for `omx`, `LangGraph`, resume, continue, or parallel execution
- explicit user requests to use `omx` or `LangGraph` are hard routing directives, not soft preferences
- when activation thresholds are met and no concrete blocker exists, actually adopt `native_omx` or `langgraph` instead of staying in explanation-only mode
- if orchestration is not adopted, explain the concrete blocker
- existing projects with new sessions should automatically follow the current user-level orchestration policy
- existing live sessions should retrofit orchestration behavior on reload, restart, explicit user routing directive, or tracked durable-state detection
- the orchestration decision target is the current task flow, not whether the repository is newly created

## Current implemented selection model vs later target

- current implemented control model:
  - `subagent_routing`
  - `oh_my_codex`
  - a compatibility durable backend view derived from layered state
- target direction:
  - `subagent_routing`
  - `oh_my_codex`
  - `langgraph`
  - plus per-task effective lane choice across enabled capabilities
- do not describe the later target model as already complete until the implementation lands

## Effective lane policy surface

- primary operator-facing summary: `codex-durable-backend-status.ps1`
- supporting views that must repeat the same capability-switch and effective-lane contract:
  - `codex-routing-policy.ps1`
  - `team-leader.toml`
  - `team-mode-playbook.md`
- repository-local OpenSpec specs and bilingual implementation plans remain the development source of truth for evolving the backend policy
- the user-level backend policy must answer:
  - which capability layers are enabled now
  - what lane is the stable default for worker-centric durable execution
  - when `native_omx` is preferred
  - when `langgraph` is preferred
  - whether effective lane choice is task-flow-dependent
  - whether backend-family switching is explicit or automatic
  - whether one durable task may span multiple backend families

## Startup path

- `codex`
  - wrapped user-level launcher that reads `oh_my_codex` and `subagent_routing`
  - in a normal PowerShell environment such as a PyCharm PowerShell terminal, this is the default startup path
- `codex.openclaw`
  - explicit non-profile wrapped launch surface
  - preferred when PowerShell profile loading is noisy or restricted under ConstrainedLanguage
- `codex-ohmy`
  - stable user-level wrapped launch surface for multi-project use
  - recommended when `.venv` might shadow `codex` or `codex.openclaw`
- `codex-native`
  - explicit bypass path to direct native Codex startup
- `codex-raw`
  - stable user-level native bypass surface for multi-project use
  - recommended when `.venv` might shadow other codex command names
- `oh_my_codex=on`
  - changes startup mode and enables durable team features
  - does not auto-launch a durable team on every `codex` start

## Native subagent contract

- Native Codex subagents are an official native capability.
- In this workflow, automatic expert routing is a leader-side overlay over explicit native subagent spawning.
- Do not describe raw Codex as auto-spawning specialist roles by default.
- Keep native subagent fan-out bounded through `agents.max_threads` and `agents.max_depth`.
- Default completed-subagent retention is `close`.
- Apply the current completed-subagent retention policy after fan-in: `close` => close the agent by default after result absorption; `keep` => keep the agent available until explicit close.
- If the current retention policy is `close`, keep a completed agent open only when the user explicitly asks to preserve that thread.
- Do not block indefinitely on a single `wait_agent` call.
- Wait in bounded dynamic windows and perform periodic progress/liveness check-ins between waits.
- Start with about 30s, extend to about 60s for bounded reviews and about 120s for deeper architect/verifier/researcher work, and keep the total wait bounded at about 180s.
- Longer-running subagents should provide concise progress/liveness updates about every 30s or at major milestones; include the current step, completed work, next step, and blockers.
- If repeated check-ins show no new progress twice in a row, treat the subagent as stalled and inspect, redirect, or respawn instead of waiting silently forever.
- If later follow-up is needed, spawn a fresh agent and pass the necessary context unless the preserved thread is intentionally being reused.
- Prefer read-heavy or otherwise tightly bounded fan-out.
- Allow write-heavy parallel execution only when ownership isolation, hotspot serialization, and leader-owned final integration are explicit.

## Analyst fan-out first for bounded research

- bounded multi-face research means a task is still in definition, classification, scoping, or repository-grounded comparison and has multiple independent research faces
- for that class, homogeneous `analyst` fan-out is the default first research round
- `architect`, `planner`, and `writer` are not default first-round roles for bounded multi-face research
- after leader fan-in from the analysts, escalate to `architect` only when the next layer is architecture design
- after leader fan-in from the analysts, escalate to `planner` only when the next layer is execution ordering or rollout planning
- after leader fan-in from the analysts, escalate to `writer` only when the next layer is final document-production or operator-facing writing

## Wrapper entrypoints

- `codex-routing-policy.ps1`
  - shows the current routing policy, startup semantics, routing thresholds, and the detailed backend-selection contract
- `codex-durable-backend-status.ps1`
  - primary operator-facing summary for backend choice
  - shows the selected durable orchestration backend, the stable default, preferred use cases, and switching rules
- `codex-durable-state-status.ps1`
  - emits the canonical read-only inspectable durable-state summary for the current repository or worktree
  - classifies native durable-team state, LangGraph thread state, stale tracked records, and unmanaged durable state
- `codex-durable-state-reconcile.ps1`
  - previews or applies safe durable-state cleanup and reconciliation for the current repository or worktree
  - only removes explicitly safe cleanup candidates such as stale tracked records, stale compose runtime records, and empty unmanaged native team directories
- `omx-team-compose.ps1`
  - validates or persists an advanced mixed persistent pane compose plan from an explicit manifest
  - remains an advanced opt-in surface and does not replace the default operating model
- `omx-team-compose-status.ps1`
  - inspects tracked compose runtime state, pane-level outcomes, and helper pointers
- `omx-team-compose-await.ps1`
  - aggregates compose runtime wait state across launched panes and reports partial or quiesced compose state explicitly
- `omx-team-compose-recover.ps1`
  - reports compose recovery posture and pane-level resume candidates without mutating runtime state
- `omx-team-compose-shutdown.ps1`
  - previews or applies shutdown for launched panes recorded in tracked compose runtime state
- `omx-team-compose-reconcile.ps1`
  - previews or applies compose-specific cleanup for stale compose runtime residue
- `codex-durable-backend-native-omx.ps1`
  - compatibility wrapper that disables LangGraph capability and restores the native worker-centric durable lane as the default
- `codex-durable-backend-langgraph.ps1`
  - compatibility wrapper that enables LangGraph capability
- `codex-langgraph-on.ps1`
  - enables LangGraph capability without changing the other user-level switches
- `codex-langgraph-off.ps1`
  - disables LangGraph capability without changing the other user-level switches
- `codex-langgraph-status.ps1`
  - shows whether LangGraph capability is enabled
- `codex-subagent-limits.ps1`
  - inspects, and where supported updates, managed defaults for `agents.max_threads` and `agents.max_depth`
- `codex-subagent-retention-status.ps1`
  - shows the current completed-subagent retention policy without changing it
- `codex-subagent-retention-close.ps1`
  - switches the user-level default to close completed subagents after fan-in
- `codex-subagent-retention-keep.ps1`
  - switches the user-level default to keep completed subagents until explicitly closed
- `omx-langgraph-install.ps1`
  - provisions or inspects the user-level shared LangGraph venv under `C:\Users\lenovo\.codex\venvs\langgraph-py312\`
  - uses `python -m pip --isolated --index-url https://mirrors.aliyun.com/pypi/simple/ ...` for package installation
- `omx-langgraph-cli.ps1`
  - UTF-8-safe wrapper around the shared-vm official `langgraph.exe`
  - preferred on Windows terminals that are still using non-UTF-8 console encoding
- repo-managed Windows native_omx bootstrap repair:
  - `node D:\PythonProject_OpenClaw\tools\openclaw-omx-windows-bootstrap-fix.mjs status --json`
  - `node D:\PythonProject_OpenClaw\tools\openclaw-omx-windows-bootstrap-fix.mjs apply --json`
  - `node D:\PythonProject_OpenClaw\tools\openclaw-omx-windows-bootstrap-fix.mjs restore --json`
- `omx-langgraph-run.ps1`
  - starts or continues a LangGraph durable thread
- `omx-langgraph-status.ps1`
  - inspects one LangGraph thread
- `omx-langgraph-resume.ps1`
  - resumes a persisted LangGraph thread
- `omx-langgraph-inspect.ps1`
  - inspects repo-local LangGraph runtime layout, backend record, interrupt state, brief state, and survivor queue state
- `omx-langgraph-kernel.ps1`
  - inspects the bounded `StateGraph`-first runtime-kernel posture for a tracked LangGraph thread
- `omx-langgraph-engine.ps1`
  - inspects the compiled primary-runtime `StateGraph` engine posture for a tracked LangGraph thread
- `omx-langgraph-invocation.ps1`
  - inspects or requests the bounded live compiled-invocation posture for a tracked LangGraph thread
- `omx-langgraph-live-execution.ps1`
  - inspects or requests bounded live compiled execution posture for a tracked LangGraph thread
- `omx-langgraph-fuller-engine.ps1`
  - inspects or requests the fuller live primary execution-engine posture for a tracked LangGraph thread
- `omx-langgraph-deeper-engine.ps1`
- `omx-langgraph-superstep-engine.ps1`
- `omx-langgraph-stateful-engine.ps1`
- `omx-langgraph-boundary-engine.ps1`
- `omx-langgraph-handoff-engine.ps1`
- `omx-langgraph-approval-engine.ps1`
- `omx-langgraph-provenance-engine.ps1`
  - inspects or requests recovery-aware live primary-engine provenance posture for a tracked LangGraph thread
- `omx-langgraph-artifact-engine.ps1`
  - inspects or requests durable-artifact-aware live primary-engine posture for a tracked LangGraph thread
- `omx-langgraph-reducer-engine.ps1`
  - inspects or requests reducer-aware live primary-engine merge posture for a tracked LangGraph thread
- `omx-langgraph-command-engine.ps1`
  - inspects or requests command-aware live primary-engine control posture for a tracked LangGraph thread
- `omx-langgraph-runtime-engine.ps1`
  - inspects or requests runtime-aware live primary-engine context-store posture for a tracked LangGraph thread
- `omx-langgraph-memory-engine.ps1`
  - inspects or requests memory-aware live primary-engine semantic posture for a tracked LangGraph thread
- `omx-langgraph-migration-engine.ps1`
  - inspects or requests migration-aware live primary-engine compatibility posture for a tracked LangGraph thread
- `omx-langgraph-auto-policy.ps1`
  - inspects or explicitly applies bounded automatic runtime-policy behavior for a tracked LangGraph thread
- `omx-langgraph-subgraph-state.ps1`
  - inspects additive subgraph persistence-mode and bounded subgraph-state inspection posture for a tracked LangGraph thread
- `omx-langgraph-generalized-routing.ps1`
  - inspects additive generalized live `StateGraph` routing posture for a tracked LangGraph thread
- `omx-langgraph-approval-queue.ps1`
  - inspects or updates bounded multi-interrupt approval-queue posture and explicit resume mapping for a tracked LangGraph thread
- `omx-langgraph-migration.ps1`
  - inspects graph-contract posture and tracked-thread compatibility against the current LangGraph contract
- `omx-langgraph-memory.ps1`
  - inspects or updates bounded durable memory-store and semantic-memory posture for a tracked LangGraph thread
- `omx-langgraph-runtime.ps1`
  - inspects or updates bounded runtime-context and injected-store posture for a tracked LangGraph thread
- `omx-langgraph-stream.ps1`
  - records or inspects bounded LangGraph stream-observability posture for updates, checkpoints, tasks, and debug modes
- `omx-langgraph-subgraphs.ps1`
  - inspects the reusable LangGraph subgraph library and active-subgraph posture
- `omx-team-dev.ps1`
  - default launch: `omx team 2:team-executor "<task>"`
- `omx-team-debug.ps1`
  - default launch: `omx team 2:debugger "<task>"`
- `omx-team-auto.ps1`
  - emits or applies a tracked durable-team decision for the current repository
  - chooses `launch`, `reuse`, `switch`, `shutdown`, or `no-team`
- `omx-team-ops.ps1`
  - wraps `status`, `await`, `resume`, `shutdown`
  - also wraps read-only API inspection such as `list-tasks`, `mailbox-list`, `get-summary`, and `read-manifest`
- Windows-safe team API wrappers:
  - `omx-team-send-message.ps1`
  - `omx-team-mailbox-list.ps1`
  - `omx-team-mailbox-mark-delivered.ps1`
  - `omx-team-claim-task.ps1`
  - `omx-team-transition-task-status.ps1`
  - `omx-team-release-task-claim.ps1`
  - high-level worker closure wrappers:
    - `omx-team-report-progress.ps1`
    - `omx-team-complete-task.ps1`
    - `omx-team-fail-task.ps1`
  - prefer these over hand-written `omx team api --input ...` payload construction on Windows worker lanes
- `omx-team-hybrid.ps1`
  - translates counts like `-Architect 1 -Planner 1 -Executor 2 -Verifier 1`
  - expert counts stay leader-side native subagents
  - executor count becomes one homogeneous durable worker swarm
- `omx-team-verify.ps1`
  - produces a leader-side native verification plan
  - does not treat `verifier` as a default persistent pane

## Lifecycle

1. Freeze the implementation brief.
2. In enhanced auto mode, prefer `omx-team-auto.ps1` to decide whether a durable backend should launch, resume or shut down.
3. Use `omx-team-ops.ps1` for `status`, `await`, `resume`, and `shutdown`.
4. After integration, use leader-side native `verifier`, `test-engineer`, and `security-reviewer` as needed.

## Inspectable durable state

- `codex-durable-state-status.ps1` is the canonical read-only cross-backend durable-state summary for the current repository or worktree
- use it to inspect backend family, state class, tracked identity, current phase, worker shape, active blockers, next step, inspect pointer, resume pointer, state sources, and updated timestamp
- when tracked compose runtime state exists, it also projects compose-specific launch detail for launched panes, planned-only panes, and launch failures
- `codex-durable-state-reconcile.ps1` is the cleanup and reconciliation helper for stale or unmanaged durable-state residue
- preview remains read-first by default; `-Apply` only removes explicitly safe cleanup candidates
- backend-specific helpers remain available:
  - use `omx-team-ops.ps1` for tracked native durable-team inspection and lifecycle actions
  - use `omx-team-compose-status.ps1`, `omx-team-compose-shutdown.ps1`, and `omx-team-compose-reconcile.ps1` for compose-scoped lifecycle operations
  - use `omx-langgraph-inspect.ps1`, `omx-langgraph-kernel.ps1`, `omx-langgraph-engine.ps1`, `omx-langgraph-invocation.ps1`, `omx-langgraph-live-execution.ps1`, `omx-langgraph-fuller-engine.ps1`, `omx-langgraph-deeper-engine.ps1`, `omx-langgraph-superstep-engine.ps1`, `omx-langgraph-stateful-engine.ps1`, `omx-langgraph-boundary-engine.ps1`, `omx-langgraph-handoff-engine.ps1`, `omx-langgraph-approval-engine.ps1`, `omx-langgraph-provenance-engine.ps1`, `omx-langgraph-artifact-engine.ps1`, `omx-langgraph-reducer-engine.ps1`, `omx-langgraph-command-engine.ps1`, `omx-langgraph-runtime-engine.ps1`, `omx-langgraph-memory-engine.ps1`, `omx-langgraph-migration-engine.ps1`, `omx-langgraph-auto-policy.ps1`, `omx-langgraph-subgraph-state.ps1`, `omx-langgraph-generalized-routing.ps1`, `omx-langgraph-approval-queue.ps1`, `omx-langgraph-migration.ps1`, `omx-langgraph-memory.ps1`, `omx-langgraph-runtime.ps1`, `omx-langgraph-stream.ps1`, `omx-langgraph-subgraphs.ps1`, `omx-langgraph-history.ps1`, and `omx-langgraph-replay.ps1` for LangGraph inspection and observability
  - use `omx-langgraph-recover.ps1` and `omx-langgraph-resume.ps1` for explicit mutating LangGraph recovery or continuation
- treat this surface as read-only by default; replay and history remain inspection-only, while mutation continues through explicit helper scripts

## LangGraph durable flow

- use a seven-phase root graph: `define-target`, `read-context`, `freeze-plan`, `execute-parallel`, `integrate-converge`, `stabilize`, `verify-accept`
- keep research handoff as a frozen implementation brief instead of reusing open-ended research context
- keep adversarial bug review as a persisted survivor queue instead of a persistent bug triad
- repo-local LangGraph runtime state lives under `.omx/state/langgraph/`
- install or inspect the shared upstream runtime through `omx-langgraph-install.ps1`
- use `omx-langgraph-cli.ps1` for official CLI help or `dev` commands on Windows terminals that are not already UTF-8 clean
- inspect the runtime layout and current thread through `omx-langgraph-inspect.ps1`
- inspect bounded graph-kernel posture through `omx-langgraph-kernel.ps1`
- inspect compiled primary-runtime engine posture through `omx-langgraph-engine.ps1`
- inspect or request compiled invocation posture through `omx-langgraph-invocation.ps1`
- inspect or request live compiled execution posture through `omx-langgraph-live-execution.ps1`
- inspect or request fuller live primary-engine posture through `omx-langgraph-fuller-engine.ps1`
- inspect or request deeper live primary-engine posture through `omx-langgraph-deeper-engine.ps1`
- inspect or request superstep live primary-engine posture through `omx-langgraph-superstep-engine.ps1`
- inspect or request stateful live primary-engine posture through `omx-langgraph-stateful-engine.ps1`
- inspect or request graph-resident live primary-engine boundary posture through `omx-langgraph-boundary-engine.ps1`
- inspect or request subgraph-aware live primary-engine handoff posture through `omx-langgraph-handoff-engine.ps1`
- inspect or request approval-aware live primary-engine resume posture through `omx-langgraph-approval-engine.ps1`
- inspect or request recovery-aware live primary-engine provenance posture through `omx-langgraph-provenance-engine.ps1`
- inspect or request durable-artifact-aware live primary-engine posture through `omx-langgraph-artifact-engine.ps1`
- inspect or request reducer-aware live primary-engine merge posture through `omx-langgraph-reducer-engine.ps1`
- inspect or request command-aware live primary-engine control posture through `omx-langgraph-command-engine.ps1`
- inspect or request runtime-aware live primary-engine context-store posture through `omx-langgraph-runtime-engine.ps1`
- inspect or request memory-aware live primary-engine semantic posture through `omx-langgraph-memory-engine.ps1`
- inspect or request migration-aware live primary-engine compatibility posture through `omx-langgraph-migration-engine.ps1`
- inspect or explicitly apply bounded automatic runtime-policy posture through `omx-langgraph-auto-policy.ps1`
- inspect additive subgraph persistence-mode and bounded subgraph-state inspection posture through `omx-langgraph-subgraph-state.ps1`
- inspect additive generalized live-routing posture through `omx-langgraph-generalized-routing.ps1`
- inspect multi-interrupt approval posture and resume mapping through `omx-langgraph-approval-queue.ps1`
- inspect graph-contract posture and thread compatibility through `omx-langgraph-migration.ps1`
- inspect bounded memory-store and semantic-memory posture through `omx-langgraph-memory.ps1`
- inspect bounded runtime-context and injected-store posture through `omx-langgraph-runtime.ps1`
- observe bounded stream posture such as `updates`, `checkpoints`, `tasks`, and `debug` through `omx-langgraph-stream.ps1`
- inspect the reusable subgraph library and active-subgraph posture through `omx-langgraph-subgraphs.ps1`
- inspect command-driven transition posture, target graph scope, and parent-handoff attribution through `omx-langgraph-inspect.ps1`
- inspect replay targets and history posture through `omx-langgraph-history.ps1`
- replay a prior checkpoint or state-history target read-only through `omx-langgraph-replay.ps1`
- perform explicit time-travel or bounded update-state recovery only through `omx-langgraph-recover.ps1`
- use `omx-langgraph-resume.ps1` with command-aware flags such as `-CommandKind`, `-CommandGoto`, `-CommandGraphScope`, `-ParentHandoffTarget`, and `-ResumePayloadJson` when a tracked thread needs explicit command-driven continuation

## Project isolation

- `omx` remains a shared user-level CLI installation.
- Cross-repository reusable role TOMLs belong under the user-level agents directory.
- Repository-specific role TOMLs belong under `<repo>/.codex/agents/`.
- Every standalone custom agent TOML should define `name`, `description`, and `developer_instructions`.
- Multi-project isolation comes from per-repository or per-worktree `.omx` state roots.
- Different repositories keep separate runtime state, logs, mailboxes, and recovery data by default.
- Sessions inside the same repository intentionally share that repository `.omx` state unless split into different worktrees.

## Terminology boundary

- Describe oh-my-codex as a workflow and durable-state layer around Codex, not as a Codex replacement.
- Prefer `OpenHands` over archived `OpenDevin` terminology.
- Treat `LangGraph`, `AutoGen`, and `CrewAI` as general programmable orchestration runtimes rather than as native Codex-subagent equivalents.

## Hybrid staffing rule

- `architect`, `planner`, `verifier`, `test-engineer`, `security-reviewer`, and `writer`
  - leader-side native subagents
- `team-executor`, `executor`, and `debugger`
  - durable worker lanes

## Role discipline

- Keep research and implementation as different roles when the task starts open-ended.
- Keep persistent teams homogeneous by default.
- Use mixed persistent panes only if the lighter hybrid model proves insufficient.

## Advanced compose mode

- mixed persistent pane compose is an advanced opt-in mode, not the default workflow
- use `omx-team-compose.ps1 -ManifestPath <path> -Json` to validate and preview a compose plan
- use `omx-team-compose.ps1 -ManifestPath <path> -Apply -Json` to persist the compose plan and launch supported pane roles for the current repository
- require an explicit compose manifest schema from `teams/compose-manifest.schema.json`
- keep the current main Codex CLI session as leader outside the pane roster
- keep read-mostly pane defaults unless the manifest grants a write slice explicitly
- supported first-rollout launch roles are `team-executor`, `executor`, and `debugger`
- unsupported pane roles remain visible as planned-only entries during compose apply
- compose runtime state is tracked under `.omx/state/compose/current-compose-runtime.json`
- use `omx-team-compose-status.ps1 -RepoRoot <repo> -Json` to inspect tracked compose runtime state and pane-level helper pointers
- use `omx-team-compose-await.ps1 -RepoRoot <repo> -Json` to inspect aggregate compose wait state and partial compose runtime health
- use `omx-team-compose-recover.ps1 -RepoRoot <repo> -Json` to inspect compose recovery posture and resume candidates
- use `omx-team-compose-shutdown.ps1 -RepoRoot <repo> -Json` to preview compose shutdown and add `-Apply` to execute it
- use `omx-team-compose-reconcile.ps1 -RepoRoot <repo> -Json` to preview stale compose runtime cleanup and add `-Apply` to execute it
- per-pane reattach or resume remains guidance-first through compose recovery output and pane helper pointers that route to `omx-team-ops.ps1`
- partial compose runtime state is explicit: `fully_active`, `partial_shutdown`, `fully_quiesced`, or `no_launched_panes`
- compose recovery posture is explicit: `resumable`, `degraded_recoverable`, or `manual_intervention_required`

## Automatic routing thresholds

- `analyst`
  - unclear outcome, non-goals, or acceptance target
  - two or more major ambiguities remain
  - bounded multi-face research needs homogeneous first-round fan-out
- `researcher`
  - external docs, dependency behavior, version-sensitive facts, or official-source verification
- `architect`
  - two or more modules, trust boundaries, shared interfaces, migrations, or non-local design decisions
  - for bounded multi-face research, use after analyst fan-in shows an architecture layer
- `planner`
  - two or more execution slices, serial hotspots, rollout ordering, or dependency chains
  - for bounded multi-face research, use after analyst fan-in shows an execution-ordering layer
- `executor` or `team-executor`
  - only after plan freeze
  - only with at least two mostly independent execution slices
- `debugger`
  - blocking failure, regression, reproducible defect, or stabilization-heavy repair work
- `verifier`
  - before final acceptance for behavior-changing or multi-file work
  - always after multi-worker integration
- `test-engineer`
  - critical-path behavior changed, tests are missing, flaky, or broad regression risk exists
- `security-reviewer`
  - auth, secrets, permissions, untrusted input, code execution, external trust boundaries, or payments
- `writer`
  - user-facing behavior, setup, migration, or operator workflow changes
  - for bounded multi-face research, use after analyst fan-in shows a document-finalization layer

## Automatic durable-team routing

- helper: `omx-team-auto.ps1`
- activation selector: `.omx/state/selectors/active.json`
- compatibility record: `.omx/state/team/codex-auto-managed-team.json`
- no automatic durable team in:
  - `define-target`
  - `read-context`
  - `freeze-plan`
  - `verify-accept`
- execution and integration:
  - `2:team-executor` at 2+ parallel slices
  - `3:team-executor` at 3+ parallel slices
- stabilization:
  - `2:debugger` at 1+ blocking issues
- automatic reuse or switch applies only to the tracked repo-local team
- do not auto-adopt unmanaged existing teams

## Research-to-implementation handoff

- use `analyst`, `architect`, `planner`, or `researcher` for open-ended option space
- freeze an implementation brief before execution begins
- hand final implementation to a fresh `executor` or `debugger` context

## Adversarial bug review

- generated user-level callable roles: `bug-finder`, `bug-rebutter`, `bug-judge`
- use `bug-finder`, `bug-rebutter`, and `bug-judge` only when bug triage remains contested, noisy, or high-volume
- keep these roles read-only by default
- send only judged survivors into `executor` or `debugger`
'@
}

function Get-TeamQuickReferenceContent {
  return @'
# OPENCLAW-CODEX-USER-LEVEL-TEAM-MODE-MANAGED
# Team Mode Quick Reference

This card is the short companion to `team-mode-playbook.md`.

Use the full playbook when you need policy detail, lifecycle semantics, or backend-selection reasoning.

## Global Automatic Collaboration Default

- Automatic collaboration is on by default for all projects and all user-level Codex sessions.
- Do not wait for the user to repeat "use experts", "parallel", "durable_team", or "persistent team".
- For qualifying tasks, automatically evaluate the smallest sufficient collaboration surface: native experts, `native_omx`, LangGraph durable workflow, and persistent team.
- Never use "the user did not request subagents/parallelism" as the reason to skip orchestration.
- If native `spawn_agent` is blocked by a platform/tool constraint, report `experts=blocked:platform_subagent_invocation_constraint` and continue through an eligible durable lane or main-session takeover.
- Persistent/durable team selection still requires thresholds such as `frozen_plan=true` plus 2+ independent execution slices, or stabilization with blocking issues.

## Analyst Fan-out First

- bounded multi-face research first uses homogeneous `analyst` fan-out
- `architect`, `planner`, and `writer` enter after analyst fan-in only when the task has moved into architecture, rollout planning, or final writing
- inspect the full routing model with `codex-routing-policy.ps1 -Json`

## 10 Common Commands

1. Inspect global mode and switches
   - Read-only
   - `codex-routing-policy.ps1 -Json`

0. Launch wrapped Codex without relying on a PowerShell profile
   - Explicit non-profile entry
   - `codex.openclaw --version`

00. Launch wrapped Codex with a `.venv`-safe user-level command name
   - Explicit stable user-level entry
   - `codex-ohmy --version`

2. Inspect backend policy and effective-lane model
   - Read-only
   - `codex-durable-backend-status.ps1 -Json`

3. Inspect current repository durable state
   - Read-only
   - `codex-durable-state-status.ps1 -RepoRoot <repo> -Json`

4. Preview safe cleanup and reconciliation
   - Preview-first
   - `codex-durable-state-reconcile.ps1 -RepoRoot <repo> -Json`

5. Apply safe cleanup and reconciliation
   - Mutating
   - `codex-durable-state-reconcile.ps1 -RepoRoot <repo> -Apply -Json`

6. Launch or route a worker-centric durable team automatically
   - Mutating
   - `omx-team-auto.ps1 -Task "<task>" -Phase execute-parallel -ParallelSlices 2 -Apply -Json`

7. Launch a conservative native OMX execution swarm directly
   - Mutating
   - `omx-team-dev.ps1 -Task "<task>"`

8. Inspect or operate on the tracked native OMX team
   - `status/get-summary/read-manifest` are read-only
   - `resume/shutdown` are mutating
   - Example: `omx-team-ops.ps1 -Action status -RepoRoot <repo> -Json`

9. Start or continue a LangGraph durable thread
   - Mutating
   - `omx-langgraph-run.ps1 -Task "<task>" -Phase define-target -RepoRoot <repo> -Json`

10. Inspect or provision the shared LangGraph venv
   - Read-only with `-DryRun`, mutating without it
   - `omx-langgraph-install.ps1 -DryRun -Json`

11. Run the official shared LangGraph CLI through the UTF-8-safe wrapper
   - Read-only for `--help`, mutating for `dev`
   - `omx-langgraph-cli.ps1 --help`

12. Inspect, replay, recover, or resume a tracked LangGraph thread
  - `inspect`, `subgraphs`, `history`, and `replay` are read-only
  - `memory`, `runtime`, `stream`, `recover`, and `resume` are mutating
  - Examples:
    - `omx-langgraph-inspect.ps1 -RepoRoot <repo> -Json`
    - `omx-langgraph-kernel.ps1 -ThreadId <thread-id> -RepoRoot <repo> -Json`
    - `omx-langgraph-engine.ps1 -ThreadId <thread-id> -RepoRoot <repo> -Json`
    - `omx-langgraph-invocation.ps1 -ThreadId <thread-id> -InvokeKind invoke -RepoRoot <repo> -Json`
    - `omx-langgraph-live-execution.ps1 -ThreadId <thread-id> -RunKind invoke -RepoRoot <repo> -Json`
    - `omx-langgraph-fuller-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RepoRoot <repo> -Json`
    - `omx-langgraph-deeper-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json`
    - `omx-langgraph-superstep-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json`
    - `omx-langgraph-stateful-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json`
    - `omx-langgraph-boundary-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json`
    - `omx-langgraph-handoff-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json`
    - `omx-langgraph-approval-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json`
    - `omx-langgraph-provenance-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json`
    - `omx-langgraph-artifact-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json`
    - `omx-langgraph-reducer-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json`
    - `omx-langgraph-command-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json`
    - `omx-langgraph-runtime-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json`
    - `omx-langgraph-memory-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json`
    - `omx-langgraph-migration-engine.ps1 -ThreadId <thread-id> -RunKind invoke -RecursionLimit 8 -RepoRoot <repo> -Json`
    - `omx-langgraph-auto-policy.ps1 -ThreadId <thread-id> -Apply -RepoRoot <repo> -Json`
    - `omx-langgraph-subgraph-state.ps1 -ThreadId <thread-id> -RepoRoot <repo> -Json`
    - `omx-langgraph-generalized-routing.ps1 -ThreadId <thread-id> -RepoRoot <repo> -Json`
    - `omx-langgraph-approval-queue.ps1 -ThreadId <thread-id> -InterruptItemFile <queue-json-file> -RepoRoot <repo> -Json`
    - `omx-langgraph-migration.ps1 -ThreadId <thread-id> -CurrentTopologyVersion 1.1 -CurrentStateSchemaVersion 2.0 -RepoRoot <repo> -Json`
    - `omx-langgraph-memory.ps1 -ThreadId <thread-id> -MemoryStoreConfigured -MemoryStoreKind long_term_store -MemoryNamespace codex/team -SemanticMemoryEnabled -SemanticStoreKind semantic_index -SemanticNamespace codex/team -RepoRoot <repo> -Json`
    - `omx-langgraph-runtime.ps1 -ThreadId <thread-id> -ContextSchema operator_context -RuntimeContextJson "{\"user_id\":\"u-1\",\"model_provider\":\"openai\"}" -StoreConfigured -StoreAccessExpected -StoreKind repo_local -RepoRoot <repo> -Json`
    - `omx-langgraph-stream.ps1 -ThreadId <thread-id> -StreamMode updates,debug -Subgraphs -EventKind debug -DebugSummary "entered verify branch" -RepoRoot <repo> -Json`
    - `omx-langgraph-subgraphs.ps1 -RepoRoot <repo> -Json`
    - `omx-langgraph-history.ps1 -ThreadId <thread-id> -RepoRoot <repo> -Json`
    - `omx-langgraph-replay.ps1 -ThreadId <thread-id> -TargetId <target-id> -RepoRoot <repo> -Json`
    - `omx-langgraph-recover.ps1 -ThreadId <thread-id> -MutationIntent explicit-recovery -TargetId <target-id> -RepoRoot <repo> -Json`
    - `omx-langgraph-recover.ps1 -ThreadId <thread-id> -MutationIntent explicit-recovery -ThreadField phase=stabilize -RepoRoot <repo> -Json`
    - `omx-langgraph-resume.ps1 -ThreadId <thread-id> -Phase verify-accept -CommandKind parent_handoff -CommandGraphScope parent -ParentHandoffTarget verify-accept -RepoRoot <repo> -Json`
    - `omx-langgraph-resume.ps1 -ThreadId <thread-id> -Phase verify-accept -CommandKind parent_handoff -CommandGraphScope parent -ParentHandoffTarget verify-accept -RepoRoot <repo> -Json`
    - `omx-langgraph-resume.ps1 -ThreadId <thread-id> -RepoRoot <repo> -Json`

## Stable User-Level Commands

- `codex-ohmy`
  - recommended daily wrapped Codex entry for multi-project use
  - not dependent on PowerShell profile binding
  - intended to avoid ordinary `.venv` command-name shadowing
- `codex-raw`
  - recommended daily raw Codex bypass for multi-project use
  - not dependent on PowerShell profile binding
  - intended to avoid ordinary `.venv` command-name shadowing

## Compose Runtime

- inspect tracked compose runtime
  - read-only
  - `omx-team-compose-status.ps1 -RepoRoot <repo> -Json`
- await tracked compose runtime
  - read-only
  - `omx-team-compose-await.ps1 -RepoRoot <repo> -Json`
- inspect compose recovery posture
  - read-only
  - `omx-team-compose-recover.ps1 -RepoRoot <repo> -Json`
- preview or apply compose shutdown
  - preview first with `omx-team-compose-shutdown.ps1 -RepoRoot <repo> -Json`
  - mutate with `omx-team-compose-shutdown.ps1 -RepoRoot <repo> -Apply -Json`
- preview or apply compose-specific cleanup
  - preview first with `omx-team-compose-reconcile.ps1 -RepoRoot <repo> -Json`
  - mutate with `omx-team-compose-reconcile.ps1 -RepoRoot <repo> -Apply -Json`

## Reading Guide

- Read-only:
  - inspect policy, backend, state, and preview surfaces without changing runtime state
- Preview-first:
  - `codex-durable-state-reconcile.ps1` previews by default; add `-Apply` only when cleanup is explicitly intended
- Mutating:
  - launch, resume, shutdown, apply, and backend-changing flows alter runtime or durable state

## Current Defaults

- `subagent_routing=auto`
- `completed_subagent_retention=close`
- `oh_my_codex=on`
- `langgraph=on`
- stable worker-centric durable default: `native_omx`
- graph-shaped durable default: `langgraph`
- managed native subagent limits: `agents.max_threads=6`, `agents.max_depth=1`

## Native Subagent Wait Heuristic

- do not block indefinitely on a single `wait_agent` call
- start with about 30s
- extend to about 60s for bounded reviews and about 120s for deeper architect/verifier/researcher work
- keep the total wait bounded at about 180s
- ask longer-running subagents for concise progress/liveness updates about every 30s or at major milestones
- require progress updates to name the current step, completed work, next step, and blockers
- after two quiet check-ins in a row, inspect, redirect, or respawn instead of waiting silently forever
- apply the current completed-subagent retention policy after fan-in: `close` => close by default; `keep` => keep until explicit close

## Retention Switches

- inspect the current completed-subagent retention policy
  - `codex-subagent-retention-status.ps1 -Json`
- switch to immediate close after fan-in
  - `codex-subagent-retention-close.ps1 -Json`
- switch to keep-until-explicit-close
  - `codex-subagent-retention-keep.ps1 -Json`

## Windows-Safe Team API Wrappers

- `omx-team-send-message.ps1 -TeamName <team> -FromWorker <worker> -ToWorker leader-fixed -Body "ACK" -Json`
- `omx-team-mailbox-list.ps1 -TeamName <team> -Worker <worker> -Json`
- `omx-team-mailbox-mark-delivered.ps1 -TeamName <team> -Worker <worker> -MessageId <id> -Json`
- `omx-team-claim-task.ps1 -TeamName <team> -TaskId <id> -Worker <worker> -Json`
- `omx-team-transition-task-status.ps1 -TeamName <team> -TaskId <id> -From in_progress -To completed -ClaimToken <token> -Result "done" -Json`
- `omx-team-release-task-claim.ps1 -TeamName <team> -TaskId <id> -ClaimToken <token> -Worker <worker> -Json`
- `omx-team-report-progress.ps1 -TeamName <team> -Worker <worker> -TaskId <id> -Body "working" -Json`
- `omx-team-complete-task.ps1 -TeamName <team> -TaskId <id> -Worker <worker> -ClaimToken <token> -Result "done" -Json`
- `omx-team-fail-task.ps1 -TeamName <team> -TaskId <id> -Worker <worker> -ClaimToken <token> -Error "reason" -Json`
- On Windows durable workers, prefer these wrappers over hand-written `omx team api --input ...` commands.
'@
}

function Get-OmxTeamDevScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$OmxResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedOmxResolvedPath = $OmxResolvedPath.Replace("'", "''")

  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$Task,
  [ValidateRange(1, 8)]
  [int]`$Workers = 2,
  [ValidateSet('team-executor', 'executor')]
  [string]`$WorkerRole = 'team-executor',
  [string]`$RepoRoot
)

$runtimeContent

`$omxCommandPath = '$escapedOmxResolvedPath'
`$launchArgs = @('team', ("{0}:{1}" -f `$Workers, `$WorkerRole), `$Task)
`$locationPushed = `$false

try {
  if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) {
    Push-Location -LiteralPath (Resolve-CodexUserLevelRepoRoot -OverridePath `$RepoRoot)
    `$locationPushed = `$true
  }

  & `$omxCommandPath @launchArgs
}
finally {
  if (`$locationPushed) {
    Pop-Location
  }
}

`$exitCode = 0
if (Test-Path -LiteralPath variable:LASTEXITCODE) {
  `$exitCode = [int]`$LASTEXITCODE
}
exit `$exitCode
"@
}

function Get-OmxTeamDebugScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$OmxResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedOmxResolvedPath = $OmxResolvedPath.Replace("'", "''")

  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$Task,
  [ValidateRange(1, 8)]
  [int]`$Workers = 2,
  [string]`$RepoRoot
)

$runtimeContent

`$omxCommandPath = '$escapedOmxResolvedPath'
`$launchArgs = @('team', ("{0}:debugger" -f `$Workers), `$Task)
`$locationPushed = `$false

try {
  if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) {
    Push-Location -LiteralPath (Resolve-CodexUserLevelRepoRoot -OverridePath `$RepoRoot)
    `$locationPushed = `$true
  }

  & `$omxCommandPath @launchArgs
}
finally {
  if (`$locationPushed) {
    Pop-Location
  }
}

`$exitCode = 0
if (Test-Path -LiteralPath variable:LASTEXITCODE) {
  `$exitCode = [int]`$LASTEXITCODE
}
exit `$exitCode
"@
}

function Get-OmxTeamAutoScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$OmxResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedOmxResolvedPath = $OmxResolvedPath.Replace("'", "''")

  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [Alias('Task')]
  [string]`$WorkTask,
  [Parameter(Mandatory)]
  [ValidateSet('define-target', 'read-context', 'freeze-plan', 'execute-parallel', 'integrate-converge', 'stabilize', 'verify-accept')]
  [string]`$Phase,
  [ValidateRange(0, 8)]
  [int]`$ParallelSlices = 0,
  [ValidateRange(0, 32)]
  [int]`$BlockingIssues = 0,
  [string]`$Subject = '',
  [bool]`$RequiresCodeChange = `$true,
  [switch]`$NeedsGraphPhases,
  [switch]`$NeedsCheckpointGates,
  [switch]`$NeedsFrozenBrief,
  [switch]`$NeedsSurvivorQueue,
  [string]`$RepoRoot,
  [switch]`$Apply,
  [switch]`$Json
)

$runtimeContent

function Resolve-CodexUserLevelAutoLaunchedTeamName {
  param(
    [string]`$RepoRoot,
    [string[]]`$BeforeTeamNames
  )

  `$afterTeamNames = @(Get-CodexUserLevelTeamDirectoryNames -RepoRoot `$RepoRoot)
  foreach (`$teamName in @(`$afterTeamNames)) {
    if (`$teamName -notin @(`$BeforeTeamNames)) {
      return [string]`$teamName
    }
  }

  if (`$afterTeamNames.Count -gt 0) {
    return [string]`$afterTeamNames[0]
  }

  return ''
}

function Write-CodexUserLevelAutoManagedTeamRecord {
  param(
    [Parameter(Mandatory)]
    `$Plan,
    [Parameter(Mandatory)]
    [string]`$TeamName
  )

  `$recordPath = [string]`$Plan.tracked_record.path
  `$recordDirectory = Split-Path -Parent `$recordPath
  if (-not (Test-Path -LiteralPath `$recordDirectory)) {
    New-Item -ItemType Directory -Force -Path `$recordDirectory | Out-Null
  }

  `$record = [ordered]@{
    schema_version = 1
    managed_by = 'codex-user-level-team-mode-p5'
    team_name = `$TeamName
    worker_role = [string]`$Plan.desired_durable_team.worker_role
    worker_count = [int]`$Plan.desired_durable_team.worker_count
    phase = [string]`$Plan.phase
    updated_at = (Get-Date).ToUniversalTime().ToString('o')
  }

  `$json = `$record | ConvertTo-Json -Depth 6
  Set-Content -LiteralPath `$recordPath -Value `$json -Encoding ASCII -NoNewline
  `$selectorRoot = Join-Path (Join-Path (Resolve-CodexUserLevelRepoRoot -OverridePath ([string]`$Plan.repo_root)) '.omx\state') 'selectors'
  `$selectorPath = Join-Path `$selectorRoot 'active.json'
  `$selectorLeaseDirectory = Join-Path `$selectorRoot 'leases'
  if (-not (Test-Path -LiteralPath `$selectorRoot)) {
    New-Item -ItemType Directory -Force -Path `$selectorRoot | Out-Null
  }
  if (-not (Test-Path -LiteralPath `$selectorLeaseDirectory)) {
    New-Item -ItemType Directory -Force -Path `$selectorLeaseDirectory | Out-Null
  }
  `$now = (Get-Date).ToUniversalTime().ToString('o')
  `$sessionScopeId = 'native-' + `$TeamName
  `$selectorPayload = [ordered]@{
    backend_family = 'native_omx'
    selector_id = ('selector-' + `$TeamName)
    repo_root = (Resolve-CodexUserLevelRepoRoot -OverridePath ([string]`$Plan.repo_root))
    worktree_id = (Split-Path -Leaf (Resolve-CodexUserLevelRepoRoot -OverridePath ([string]`$Plan.repo_root)))
    thread_id = ''
    team_name = `$TeamName
    session_scope_id = `$sessionScopeId
    leader_session_lineage = `$sessionScopeId
    acquired_at = `$now
    last_heartbeat_at = `$now
    released_at = ''
    generation = ([int64](Get-Date -UFormat %s) * 1000)
    phase = [string]`$Plan.phase
    routing_posture = 'active_scoped_selector'
    routing_eligible = `$true
  }
  `$selectorJson = `$selectorPayload | ConvertTo-Json -Depth 6
  Set-Content -LiteralPath `$selectorPath -Value `$selectorJson -Encoding ASCII -NoNewline
  Set-Content -LiteralPath (Join-Path `$selectorLeaseDirectory (`$sessionScopeId + '.json')) -Value `$selectorJson -Encoding ASCII -NoNewline
}

function Remove-CodexUserLevelAutoManagedTeamRecord {
  param(
    [Parameter(Mandatory)]
    [string]`$RecordPath
  )

  if (Test-Path -LiteralPath `$RecordPath) {
    Remove-Item -LiteralPath `$RecordPath -Force
  }
}

function Write-CodexUserLevelAutoPlanOutput {
  param(
    [Parameter(Mandatory)]
    `$Plan,
    [switch]`$Json
  )

  if (`$Json) {
    `$Plan | ConvertTo-Json -Depth 8
    return
  }

  Write-Output ("decision={0}" -f `$Plan.decision)
  Write-Output ("phase={0}" -f `$Plan.phase)
  Write-Output ("current_mode={0}" -f `$Plan.current_mode)
  Write-Output ("durable_backend={0}" -f `$Plan.durable_orchestration_backend)
  Write-Output ("effective_lane={0}" -f `$Plan.effective_lane)
  if ([bool]`$Plan.desired_durable_team.required) {
    Write-Output ("desired_team={0}:{1}" -f `$Plan.desired_durable_team.worker_count, `$Plan.desired_durable_team.worker_role)
  }
  if ([bool]`$Plan.tracked_record.exists) {
    Write-Output ("tracked_team={0}" -f `$Plan.tracked_record.team_name)
  }
  foreach (`$reason in @(`$Plan.reasons)) {
    Write-Output ("reason={0}" -f `$reason)
  }
}

`$plan = Get-CodexUserLevelAutomaticTeamPlan -Task `$WorkTask -Phase `$Phase -ParallelSlices `$ParallelSlices -BlockingIssues `$BlockingIssues -Subject `$Subject -RepoRoot `$RepoRoot -RequiresCodeChange `$RequiresCodeChange -NeedsGraphPhases ([bool]`$NeedsGraphPhases) -NeedsCheckpointGates ([bool]`$NeedsCheckpointGates) -NeedsFrozenBrief ([bool]`$NeedsFrozenBrief) -NeedsSurvivorQueue ([bool]`$NeedsSurvivorQueue)
if (-not `$Apply) {
  Write-CodexUserLevelAutoPlanOutput -Plan `$plan -Json:`$Json
  return
}

`$omxCommandPath = '$escapedOmxResolvedPath'
`$locationPushed = `$false
`$resolvedRepoRoot = [string]`$plan.repo_root

try {
  if (-not [string]::IsNullOrWhiteSpace(`$resolvedRepoRoot)) {
    Push-Location -LiteralPath `$resolvedRepoRoot
    `$locationPushed = `$true
  }

  `$binDirectory = Get-CodexUserLevelBinDirectory
  `$langGraphRunScriptPath = Join-Path `$binDirectory 'omx-langgraph-run.ps1'
  `$langGraphResumeScriptPath = Join-Path `$binDirectory 'omx-langgraph-resume.ps1'
  `$langGraphInspectScriptPath = Join-Path `$binDirectory 'omx-langgraph-inspect.ps1'
  `$result = `$null
  switch ([string]`$plan.decision) {
    'launch' {
      if ([string]`$plan.effective_lane -eq 'langgraph') {
        `$launchInvocation = [ordered]@{
          Task = [string]`$plan.task
          Phase = [string]`$plan.phase
          RepoRoot = [string]`$resolvedRepoRoot
          ParallelSlices = [int]`$plan.parallel_slices
          BlockingIssues = [int]`$plan.blocking_issues
          Json = [bool]`$Json
        }
        `$launchOutput = @(& `$langGraphRunScriptPath @launchInvocation)
        `$launchExitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
        if (`$launchExitCode -ne 0) {
          `$result = [ordered]@{
            applied = `$false
            applied_decision = 'launch_failed'
            backend = 'langgraph'
            launch_args = `$plan.langgraph_run_args
            launch_output = `$launchOutput
            launch_exit_code = `$launchExitCode
            tracked_record_path = (Get-CodexUserLevelLangGraphBackendRecordPath -RepoRoot `$resolvedRepoRoot)
          }
          break
        }
        `$parsed = `$null
        if (`$launchOutput.Count -gt 0) {
          try { `$parsed = (`$launchOutput -join [Environment]::NewLine) | ConvertFrom-Json } catch { }
        }
        `$threadId = ''
        if (`$null -ne `$parsed) {
          try {
            `$threadId = [string]`$parsed.thread_id
          } catch {
            `$threadId = ''
          }
        }
        if ([string]::IsNullOrWhiteSpace(`$threadId)) {
          throw 'LangGraph launch completed but no thread_id was returned.'
        }
        `$recordPath = Write-CodexUserLevelLangGraphBackendRecord -RepoRoot `$resolvedRepoRoot -ThreadId `$threadId -Phase ([string]`$plan.phase)
        `$result = [ordered]@{
          applied = `$true
          applied_decision = 'launch'
          backend = 'langgraph'
          thread_id = `$threadId
          launch_args = `$plan.langgraph_run_args
          launch_output = `$launchOutput
          launch_exit_code = `$launchExitCode
          tracked_record_path = `$recordPath
        }
      } else {
        `$beforeTeamNames = @(Get-CodexUserLevelTeamDirectoryNames -RepoRoot `$resolvedRepoRoot)
        `$launchArgs = @(`$plan.launch_args | ForEach-Object { [string]`$_ })
        `$launchOutput = @(& `$omxCommandPath @launchArgs)
        `$launchExitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
        if (`$launchExitCode -ne 0) {
          `$result = [ordered]@{
            applied = `$false
            applied_decision = 'launch_failed'
            backend = 'native_omx'
            launch_args = `$launchArgs
            launch_output = `$launchOutput
            launch_exit_code = `$launchExitCode
            tracked_record_path = [string]`$plan.tracked_record.path
          }
          break
        }
        `$launchedTeamName = Resolve-CodexUserLevelAutoLaunchedTeamName -RepoRoot `$resolvedRepoRoot -BeforeTeamNames `$beforeTeamNames
        if ([string]::IsNullOrWhiteSpace(`$launchedTeamName)) {
          throw 'Automatic team launch completed but no team directory could be detected.'
        }

        Write-CodexUserLevelAutoManagedTeamRecord -Plan `$plan -TeamName `$launchedTeamName
        `$result = [ordered]@{
          applied = `$true
          applied_decision = 'launch'
          backend = 'native_omx'
          team_name = `$launchedTeamName
          launch_args = `$launchArgs
          launch_output = `$launchOutput
          launch_exit_code = `$launchExitCode
          tracked_record_path = [string]`$plan.tracked_record.path
        }
      }
    }
    'reuse' {
      `$payload = `$plan.create_task_payload
      `$payloadJson = ConvertTo-CodexUserLevelCompressedJson -InputObject `$payload
      `$dispatchArgs = @('team', 'api', 'create-task', '--input', `$payloadJson, '--json')
      `$dispatchOutput = @(& `$omxCommandPath @dispatchArgs)
      `$dispatchExitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
      `$result = [ordered]@{
        applied = (`$dispatchExitCode -eq 0)
        applied_decision = if (`$dispatchExitCode -eq 0) { 'reuse' } else { 'reuse_failed' }
        team_name = [string]`$plan.tracked_record.team_name
        dispatch_args = `$dispatchArgs
        dispatch_output = `$dispatchOutput
        dispatch_exit_code = `$dispatchExitCode
        tracked_record_path = [string]`$plan.tracked_record.path
      }
      if (`$dispatchExitCode -eq 0) {
        Write-CodexUserLevelAutoManagedTeamRecord -Plan `$plan -TeamName ([string]`$plan.tracked_record.team_name)
      }
    }
    'resume' {
      `$resumeArgs = @(`$plan.langgraph_resume_args | ForEach-Object { [string]`$_ })
      `$resumeInvocation = [ordered]@{
        ThreadId = [string]`$plan.langgraph_record.thread_id
        RepoRoot = [string]`$resolvedRepoRoot
        Json = [bool]`$Json
      }
      if (-not [string]::IsNullOrWhiteSpace([string]`$plan.phase)) {
        `$resumeInvocation['Phase'] = [string]`$plan.phase
      }
      `$resumeOutput = @(& `$langGraphResumeScriptPath @resumeInvocation)
      `$resumeExitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
      `$result = [ordered]@{
        applied = (`$resumeExitCode -eq 0)
        applied_decision = if (`$resumeExitCode -eq 0) { 'resume' } else { 'resume_failed' }
        backend = 'langgraph'
        thread_id = [string]`$plan.langgraph_record.thread_id
        resume_args = `$plan.langgraph_resume_args
        resume_output = `$resumeOutput
        resume_exit_code = `$resumeExitCode
        tracked_record_path = [string]`$plan.langgraph_record.path
      }
    }
    'switch' {
      `$shutdownArgs = @(`$plan.shutdown_args | ForEach-Object { [string]`$_ })
      `$shutdownOutput = @()
      `$shutdownExitCode = 0
      if (`$shutdownArgs.Count -gt 0) {
        `$shutdownOutput = @(& `$omxCommandPath @shutdownArgs)
        `$shutdownExitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
      }
      if (`$shutdownExitCode -ne 0) {
        `$result = [ordered]@{
          applied = `$false
          applied_decision = 'switch_shutdown_failed'
          team_name = [string]`$plan.tracked_record.team_name
          shutdown_args = `$shutdownArgs
          shutdown_output = `$shutdownOutput
          shutdown_exit_code = `$shutdownExitCode
          tracked_record_path = [string]`$plan.tracked_record.path
        }
        break
      }

      `$beforeTeamNames = @(Get-CodexUserLevelTeamDirectoryNames -RepoRoot `$resolvedRepoRoot)
      `$launchArgs = @(`$plan.launch_args | ForEach-Object { [string]`$_ })
      `$launchOutput = @(& `$omxCommandPath @launchArgs)
      `$launchExitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
      if (`$launchExitCode -ne 0) {
        `$result = [ordered]@{
          applied = `$false
          applied_decision = 'switch_launch_failed'
          team_name = [string]`$plan.tracked_record.team_name
          shutdown_args = `$shutdownArgs
          shutdown_output = `$shutdownOutput
          shutdown_exit_code = `$shutdownExitCode
          launch_args = `$launchArgs
          launch_output = `$launchOutput
          launch_exit_code = `$launchExitCode
          tracked_record_path = [string]`$plan.tracked_record.path
        }
        break
      }
      `$launchedTeamName = Resolve-CodexUserLevelAutoLaunchedTeamName -RepoRoot `$resolvedRepoRoot -BeforeTeamNames `$beforeTeamNames
      if ([string]::IsNullOrWhiteSpace(`$launchedTeamName)) {
        throw 'Automatic team switch completed but no replacement team directory could be detected.'
      }

      Write-CodexUserLevelAutoManagedTeamRecord -Plan `$plan -TeamName `$launchedTeamName
      `$result = [ordered]@{
        applied = `$true
        applied_decision = 'switch'
        team_name = `$launchedTeamName
        shutdown_args = `$shutdownArgs
        shutdown_output = `$shutdownOutput
        shutdown_exit_code = `$shutdownExitCode
        launch_args = `$launchArgs
        launch_output = `$launchOutput
        launch_exit_code = `$launchExitCode
        tracked_record_path = [string]`$plan.tracked_record.path
      }
    }
    'shutdown' {
      if ([string]`$plan.effective_lane -eq 'langgraph') {
        Remove-CodexUserLevelLangGraphBackendRecord -RepoRoot `$resolvedRepoRoot
        Remove-CodexUserLevelActiveDurableSelector -RepoRoot `$resolvedRepoRoot
        `$inspectInvocation = [ordered]@{
          RepoRoot = [string]`$resolvedRepoRoot
          Json = [bool]`$Json
        }
        `$inspectOutput = @(& `$langGraphInspectScriptPath @inspectInvocation)
        `$result = [ordered]@{
          applied = `$true
          applied_decision = 'shutdown'
          backend = 'langgraph'
          inspect_args = @('-RepoRoot', [string]`$resolvedRepoRoot)
          inspect_output = `$inspectOutput
          tracked_record_path = (Get-CodexUserLevelLangGraphBackendRecordPath -RepoRoot `$resolvedRepoRoot)
        }
      } else {
        `$shutdownArgs = @(`$plan.shutdown_args | ForEach-Object { [string]`$_ })
        `$shutdownOutput = @()
        `$shutdownExitCode = 0
        if (`$shutdownArgs.Count -gt 0) {
          `$shutdownOutput = @(& `$omxCommandPath @shutdownArgs)
          `$shutdownExitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]`$LASTEXITCODE } else { 0 }
        }
        if (`$shutdownExitCode -eq 0) {
          Remove-CodexUserLevelAutoManagedTeamRecord -RecordPath ([string]`$plan.tracked_record.path)
          Remove-CodexUserLevelActiveDurableSelector -RepoRoot `$resolvedRepoRoot
        }
        `$result = [ordered]@{
          applied = (`$shutdownExitCode -eq 0)
          applied_decision = if (`$shutdownExitCode -eq 0) { 'shutdown' } else { 'shutdown_failed' }
          backend = 'native_omx'
          team_name = [string]`$plan.tracked_record.team_name
          shutdown_args = `$shutdownArgs
          shutdown_output = `$shutdownOutput
          shutdown_exit_code = `$shutdownExitCode
          tracked_record_path = [string]`$plan.tracked_record.path
        }
      }
    }
    default {
      `$result = [ordered]@{
        applied = `$false
        applied_decision = [string]`$plan.decision
        tracked_record_path = [string]`$plan.tracked_record.path
        reasons = `$plan.reasons
      }
    }
  }

  if (`$Json) {
    [ordered]@{
      plan = `$plan
      result = `$result
    } | ConvertTo-Json -Depth 8
    return
  }

  Write-Output ("applied_decision={0}" -f `$result.applied_decision)
  if ($null -ne `$result -and -not [string]::IsNullOrWhiteSpace([string]`$result.team_name)) {
    Write-Output ("team_name={0}" -f `$result.team_name)
  }
  foreach (`$reason in @(`$plan.reasons)) {
    Write-Output ("reason={0}" -f `$reason)
  }
}
finally {
  if (`$locationPushed) {
    Pop-Location
  }
}

`$exitCode = 0
if (Test-Path -LiteralPath variable:LASTEXITCODE) {
  `$exitCode = [int]`$LASTEXITCODE
}
exit `$exitCode
"@
}

function Get-OmxTeamOpsScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$OmxResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedOmxResolvedPath = $OmxResolvedPath.Replace("'", "''")

  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [ValidateSet('status', 'await', 'resume', 'shutdown', 'list-tasks', 'mailbox-list', 'get-summary', 'read-manifest')]
  [string]`$Action,
  [string]`$TeamName,
  [string]`$RepoRoot,
  [switch]`$Json,
  [ValidateRange(100, 1000)]
  [int]`$TailLines,
  [ValidateRange(1000, 3600000)]
  [int]`$TimeoutMs = 30000,
  [switch]`$Force,
  [switch]`$ConfirmIssues
)

$runtimeContent

`$omxCommandPath = '$escapedOmxResolvedPath'
`$locationPushed = `$false

try {
  if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) {
    Push-Location -LiteralPath (Resolve-CodexUserLevelRepoRoot -OverridePath `$RepoRoot)
    `$locationPushed = `$true
  }

  `$resolvedTeamName = Resolve-CodexUserLevelTeamName -RequestedTeamName `$TeamName -RepoRoot `$RepoRoot
  `$commandArgs = @()

  switch (`$Action) {
    'status' {
      `$commandArgs = @('team', 'status', `$resolvedTeamName)
      if (`$Json) {
        `$commandArgs += '--json'
      }
      if (`$PSBoundParameters.ContainsKey('TailLines')) {
        `$commandArgs += @('--tail-lines', [string]`$TailLines)
      }
    }
    'await' {
      `$commandArgs = @('team', 'await', `$resolvedTeamName, '--timeout-ms', [string]`$TimeoutMs)
      if (`$Json) {
        `$commandArgs += '--json'
      }
    }
    'resume' {
      `$commandArgs = @('team', 'resume', `$resolvedTeamName)
    }
    'shutdown' {
      `$commandArgs = @('team', 'shutdown', `$resolvedTeamName)
      if (`$Force) {
        `$commandArgs += '--force'
      }
      if (`$ConfirmIssues) {
        `$commandArgs += '--confirm-issues'
      }
    }
    'list-tasks' {
      `$apiInput = ConvertTo-CodexUserLevelCompressedJson -InputObject ([ordered]@{ team_name = `$resolvedTeamName })
      `$commandArgs = @('team', 'api', 'list-tasks', '--input', `$apiInput, '--json')
    }
    'mailbox-list' {
      `$apiInput = ConvertTo-CodexUserLevelCompressedJson -InputObject ([ordered]@{ team_name = `$resolvedTeamName })
      `$commandArgs = @('team', 'api', 'mailbox-list', '--input', `$apiInput, '--json')
    }
    'get-summary' {
      `$apiInput = ConvertTo-CodexUserLevelCompressedJson -InputObject ([ordered]@{ team_name = `$resolvedTeamName })
      `$commandArgs = @('team', 'api', 'get-summary', '--input', `$apiInput, '--json')
    }
    'read-manifest' {
      `$apiInput = ConvertTo-CodexUserLevelCompressedJson -InputObject ([ordered]@{ team_name = `$resolvedTeamName })
      `$commandArgs = @('team', 'api', 'read-manifest', '--input', `$apiInput, '--json')
    }
  }

  & `$omxCommandPath @commandArgs
}
finally {
  if (`$locationPushed) {
    Pop-Location
  }
}

`$exitCode = 0
if (Test-Path -LiteralPath variable:LASTEXITCODE) {
  `$exitCode = [int]`$LASTEXITCODE
}
exit `$exitCode
"@
}

function Get-OmxTeamSafeApiCommandScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$OmxResolvedPath,
    [Parameter(Mandatory)]
    [ValidateSet('send-message', 'mailbox-list', 'mailbox-mark-delivered', 'claim-task', 'transition-task-status', 'release-task-claim')]
    [string]$Operation
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedOmxResolvedPath = $OmxResolvedPath.Replace("'", "''")
  $paramBlock = ''
  $body = switch ($Operation) {
    'send-message' {
      $paramBlock = @'
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]$TeamName,
  [Parameter(Mandatory)]
  [string]$FromWorker,
  [Parameter(Mandatory)]
  [string]$ToWorker,
  [Parameter(Mandatory)]
  [string]$Body,
  [string]$RepoRoot,
  [switch]$Json
)
'@
      @'

$locationPushed = $false
try {
  if (-not [string]::IsNullOrWhiteSpace($RepoRoot)) {
    Push-Location -LiteralPath (Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot)
    $locationPushed = $true
  }
  $payloadJson = ConvertTo-CodexUserLevelCompressedJson -InputObject ([ordered]@{
    team_name = $TeamName
    from_worker = $FromWorker
    to_worker = $ToWorker
    body = $Body
  })
  $commandArgs = @('team', 'api', 'send-message', '--input', $payloadJson)
  if ($Json) {
    $commandArgs += '--json'
  }
  & $omxCommandPath @commandArgs
}
finally {
  if ($locationPushed) { Pop-Location }
}
'@
    }
    'mailbox-list' {
      $paramBlock = @'
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]$TeamName,
  [Parameter(Mandatory)]
  [string]$Worker,
  [string]$RepoRoot,
  [switch]$Json
)
'@
      @'

$locationPushed = $false
try {
  if (-not [string]::IsNullOrWhiteSpace($RepoRoot)) {
    Push-Location -LiteralPath (Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot)
    $locationPushed = $true
  }
  $payloadJson = ConvertTo-CodexUserLevelCompressedJson -InputObject ([ordered]@{
    team_name = $TeamName
    worker = $Worker
  })
  $commandArgs = @('team', 'api', 'mailbox-list', '--input', $payloadJson)
  if ($Json) {
    $commandArgs += '--json'
  }
  & $omxCommandPath @commandArgs
}
finally {
  if ($locationPushed) { Pop-Location }
}
'@
    }
    'mailbox-mark-delivered' {
      $paramBlock = @'
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]$TeamName,
  [Parameter(Mandatory)]
  [string]$Worker,
  [Parameter(Mandatory)]
  [string]$MessageId,
  [string]$RepoRoot,
  [switch]$Json
)
'@
      @'

$locationPushed = $false
try {
  if (-not [string]::IsNullOrWhiteSpace($RepoRoot)) {
    Push-Location -LiteralPath (Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot)
    $locationPushed = $true
  }
  $payloadJson = ConvertTo-CodexUserLevelCompressedJson -InputObject ([ordered]@{
    team_name = $TeamName
    worker = $Worker
    message_id = $MessageId
  })
  $commandArgs = @('team', 'api', 'mailbox-mark-delivered', '--input', $payloadJson)
  if ($Json) {
    $commandArgs += '--json'
  }
  & $omxCommandPath @commandArgs
}
finally {
  if ($locationPushed) { Pop-Location }
}
'@
    }
    'claim-task' {
      $paramBlock = @'
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]$TeamName,
  [Parameter(Mandatory)]
  [string]$TaskId,
  [Parameter(Mandatory)]
  [string]$Worker,
  [int]$ExpectedVersion,
  [string]$RepoRoot,
  [switch]$Json
)
'@
      @'

$locationPushed = $false
try {
  if (-not [string]::IsNullOrWhiteSpace($RepoRoot)) {
    Push-Location -LiteralPath (Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot)
    $locationPushed = $true
  }
  $payload = [ordered]@{
    team_name = $TeamName
    task_id = $TaskId
    worker = $Worker
  }
  if ($PSBoundParameters.ContainsKey('ExpectedVersion')) {
    $payload.expected_version = $ExpectedVersion
  }
  $payloadJson = ConvertTo-CodexUserLevelCompressedJson -InputObject $payload
  $commandArgs = @('team', 'api', 'claim-task', '--input', $payloadJson)
  if ($Json) {
    $commandArgs += '--json'
  }
  & $omxCommandPath @commandArgs
}
finally {
  if ($locationPushed) { Pop-Location }
}
'@
    }
    'transition-task-status' {
      $paramBlock = @'
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]$TeamName,
  [Parameter(Mandatory)]
  [string]$TaskId,
  [Parameter(Mandatory)]
  [string]$From,
  [Parameter(Mandatory)]
  [string]$To,
  [Parameter(Mandatory)]
  [string]$ClaimToken,
  [string]$Result,
  [string]$Error,
  [string]$RepoRoot,
  [switch]$Json
)
'@
      @'

$locationPushed = $false
try {
  if (-not [string]::IsNullOrWhiteSpace($RepoRoot)) {
    Push-Location -LiteralPath (Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot)
    $locationPushed = $true
  }
  $payload = [ordered]@{
    team_name = $TeamName
    task_id = $TaskId
    from = $From
    to = $To
    claim_token = $ClaimToken
  }
  if ($PSBoundParameters.ContainsKey('Result')) {
    $payload.result = $Result
  }
  if ($PSBoundParameters.ContainsKey('Error')) {
    $payload.error = $Error
  }
  $payloadJson = ConvertTo-CodexUserLevelCompressedJson -InputObject $payload
  $commandArgs = @('team', 'api', 'transition-task-status', '--input', $payloadJson)
  if ($Json) {
    $commandArgs += '--json'
  }
  & $omxCommandPath @commandArgs
}
finally {
  if ($locationPushed) { Pop-Location }
}
'@
    }
    'release-task-claim' {
      $paramBlock = @'
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]$TeamName,
  [Parameter(Mandatory)]
  [string]$TaskId,
  [Parameter(Mandatory)]
  [string]$ClaimToken,
  [Parameter(Mandatory)]
  [string]$Worker,
  [string]$RepoRoot,
  [switch]$Json
)
'@
      @'

$locationPushed = $false
try {
  if (-not [string]::IsNullOrWhiteSpace($RepoRoot)) {
    Push-Location -LiteralPath (Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot)
    $locationPushed = $true
  }
  $payloadJson = ConvertTo-CodexUserLevelCompressedJson -InputObject ([ordered]@{
    team_name = $TeamName
    task_id = $TaskId
    claim_token = $ClaimToken
    worker = $Worker
  })
  $commandArgs = @('team', 'api', 'release-task-claim', '--input', $payloadJson)
  if ($Json) {
    $commandArgs += '--json'
  }
  & $omxCommandPath @commandArgs
}
finally {
  if ($locationPushed) { Pop-Location }
}
'@
    }
  }

  return @"
# $Script:ManagedMarker
$paramBlock

$runtimeContent
`$omxCommandPath = '$escapedOmxResolvedPath'
$body
`$exitCode = 0
if (Test-Path -LiteralPath variable:LASTEXITCODE) {
  `$exitCode = [int]`$LASTEXITCODE
}
exit `$exitCode
"@
}

function Get-OmxTeamHighLevelWorkerScriptContent {
  param(
    [Parameter(Mandatory)]
    [ValidateSet('report-progress', 'complete-task', 'fail-task')]
    [string]$Operation
  )

  $runtimeContent = Get-CommandRuntimeContent
  $paramBlock = ''
  $body = switch ($Operation) {
    'report-progress' {
      $paramBlock = @'
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]$TeamName,
  [Parameter(Mandatory)]
  [string]$Worker,
  [Parameter(Mandatory)]
  [string]$Body,
  [string]$TaskId,
  [string]$RepoRoot,
  [switch]$Json
)
'@
      @'
function Resolve-CodexUserLevelWorkerStatusPath {
  param(
    [Parameter(Mandatory)]
    [string]$ResolvedRepoRoot,
    [Parameter(Mandatory)]
    [string]$TeamName,
    [Parameter(Mandatory)]
    [string]$Worker
  )

  return (Join-Path (Join-Path (Join-Path (Get-CodexUserLevelTeamStateRoot -RepoRoot $ResolvedRepoRoot) $TeamName) 'workers') (Join-Path $Worker 'status.json'))
}

function Read-CodexUserLevelWorkerStatusFile {
  param(
    [Parameter(Mandatory)]
    [string]$Path
  )

  if (-not (Test-Path -LiteralPath $Path)) {
    return [ordered]@{}
  }

  try {
    return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json)
  } catch {
    return [ordered]@{}
  }
}

function Write-CodexUserLevelWorkerStatusFile {
  param(
    [Parameter(Mandatory)]
    [string]$Path,
    [Parameter(Mandatory)]
    $Payload
  )

  $directory = Split-Path -Parent $Path
  if (-not (Test-Path -LiteralPath $directory)) {
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
  }
  Set-Content -LiteralPath $Path -Value ($Payload | ConvertTo-Json -Depth 6) -Encoding UTF8 -NoNewline
}

function Invoke-CodexUserLevelWorkerWrapperScript {
  param(
    [Parameter(Mandatory)]
    [string]$ScriptPath,
    [Parameter(Mandatory)]
    [hashtable]$Invocation
  )

  $rawOutput = @(& $ScriptPath @Invocation)
  $exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]$LASTEXITCODE } else { 0 }
  if ($exitCode -ne 0) {
    throw "Wrapper failed: $ScriptPath (exit $exitCode)"
  }

  if ($rawOutput.Count -lt 1) {
    return $null
  }

  return (($rawOutput -join [Environment]::NewLine) | ConvertFrom-Json)
}

$resolvedRepoRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
$binDirectory = Get-CodexUserLevelBinDirectory
$sendMessageScriptPath = Join-Path $binDirectory 'omx-team-send-message.ps1'
$statusPath = Resolve-CodexUserLevelWorkerStatusPath -ResolvedRepoRoot $resolvedRepoRoot -TeamName $TeamName -Worker $Worker
$existingStatus = Read-CodexUserLevelWorkerStatusFile -Path $statusPath
$statusPayload = [ordered]@{
  state = 'working'
  updated_at = (Get-Date).ToUniversalTime().ToString('o')
}
if (-not [string]::IsNullOrWhiteSpace($TaskId)) {
  $statusPayload.current_task_id = $TaskId
} elseif ($null -ne $existingStatus.PSObject.Properties['current_task_id']) {
  $statusPayload.current_task_id = [string]$existingStatus.current_task_id
}
Write-CodexUserLevelWorkerStatusFile -Path $statusPath -Payload $statusPayload
$notifyResult = Invoke-CodexUserLevelWorkerWrapperScript -ScriptPath $sendMessageScriptPath -Invocation @{
  TeamName = $TeamName
  FromWorker = $Worker
  ToWorker = 'leader-fixed'
  Body = $Body
  RepoRoot = $resolvedRepoRoot
  Json = $true
}
$resultObject = [ordered]@{
  operation = 'report-progress'
  team_name = $TeamName
  worker = $Worker
  task_id = $TaskId
  status_path = $statusPath
  status = $statusPayload
  notify = $notifyResult
}
if ($Json) {
  $resultObject | ConvertTo-Json -Depth 8
} else {
  Write-Output ("operation={0}" -f $resultObject.operation)
  Write-Output ("team_name={0}" -f $resultObject.team_name)
  Write-Output ("worker={0}" -f $resultObject.worker)
  if (-not [string]::IsNullOrWhiteSpace($TaskId)) { Write-Output ("task_id={0}" -f $TaskId) }
  Write-Output ("status_path={0}" -f $statusPath)
}
'@
    }
    'complete-task' {
      $paramBlock = @'
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]$TeamName,
  [Parameter(Mandatory)]
  [string]$TaskId,
  [Parameter(Mandatory)]
  [string]$Worker,
  [Parameter(Mandatory)]
  [string]$ClaimToken,
  [Parameter(Mandatory)]
  [string]$Result,
  [string]$MessageBody,
  [string]$RepoRoot,
  [switch]$Json
)
'@
      @'
function Resolve-CodexUserLevelWorkerStatusPath {
  param(
    [Parameter(Mandatory)]
    [string]$ResolvedRepoRoot,
    [Parameter(Mandatory)]
    [string]$TeamName,
    [Parameter(Mandatory)]
    [string]$Worker
  )

  return (Join-Path (Join-Path (Join-Path (Get-CodexUserLevelTeamStateRoot -RepoRoot $ResolvedRepoRoot) $TeamName) 'workers') (Join-Path $Worker 'status.json'))
}

function Write-CodexUserLevelWorkerStatusFile {
  param(
    [Parameter(Mandatory)]
    [string]$Path,
    [Parameter(Mandatory)]
    $Payload
  )

  $directory = Split-Path -Parent $Path
  if (-not (Test-Path -LiteralPath $directory)) {
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
  }
  Set-Content -LiteralPath $Path -Value ($Payload | ConvertTo-Json -Depth 6) -Encoding UTF8 -NoNewline
}

function Invoke-CodexUserLevelWorkerWrapperScript {
  param(
    [Parameter(Mandatory)]
    [string]$ScriptPath,
    [Parameter(Mandatory)]
    [hashtable]$Invocation
  )

  $rawOutput = @(& $ScriptPath @Invocation)
  $exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]$LASTEXITCODE } else { 0 }
  if ($exitCode -ne 0) {
    throw "Wrapper failed: $ScriptPath (exit $exitCode)"
  }

  if ($rawOutput.Count -lt 1) {
    return $null
  }

  return (($rawOutput -join [Environment]::NewLine) | ConvertFrom-Json)
}

$resolvedRepoRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
$binDirectory = Get-CodexUserLevelBinDirectory
$transitionScriptPath = Join-Path $binDirectory 'omx-team-transition-task-status.ps1'
$sendMessageScriptPath = Join-Path $binDirectory 'omx-team-send-message.ps1'
$statusPath = Resolve-CodexUserLevelWorkerStatusPath -ResolvedRepoRoot $resolvedRepoRoot -TeamName $TeamName -Worker $Worker
$notifyBody = if (-not [string]::IsNullOrWhiteSpace($MessageBody)) { $MessageBody } else { "Completed task ${TaskId}: $Result" }
$transitionResult = Invoke-CodexUserLevelWorkerWrapperScript -ScriptPath $transitionScriptPath -Invocation @{
  TeamName = $TeamName
  TaskId = $TaskId
  From = 'in_progress'
  To = 'completed'
  ClaimToken = $ClaimToken
  Result = $Result
  RepoRoot = $resolvedRepoRoot
  Json = $true
}
Write-CodexUserLevelWorkerStatusFile -Path $statusPath -Payload ([ordered]@{
  state = 'idle'
  updated_at = (Get-Date).ToUniversalTime().ToString('o')
  current_task_id = ''
  last_completed_task_id = $TaskId
})
$notifyResult = Invoke-CodexUserLevelWorkerWrapperScript -ScriptPath $sendMessageScriptPath -Invocation @{
  TeamName = $TeamName
  FromWorker = $Worker
  ToWorker = 'leader-fixed'
  Body = $notifyBody
  RepoRoot = $resolvedRepoRoot
  Json = $true
}
$resultObject = [ordered]@{
  operation = 'complete-task'
  team_name = $TeamName
  task_id = $TaskId
  worker = $Worker
  transition = $transitionResult
  notify = $notifyResult
  status_path = $statusPath
}
if ($Json) {
  $resultObject | ConvertTo-Json -Depth 8
} else {
  Write-Output ("operation={0}" -f $resultObject.operation)
  Write-Output ("team_name={0}" -f $resultObject.team_name)
  Write-Output ("task_id={0}" -f $resultObject.task_id)
  Write-Output ("worker={0}" -f $resultObject.worker)
}
'@
    }
    'fail-task' {
      $paramBlock = @'
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]$TeamName,
  [Parameter(Mandatory)]
  [string]$TaskId,
  [Parameter(Mandatory)]
  [string]$Worker,
  [Parameter(Mandatory)]
  [string]$ClaimToken,
  [Parameter(Mandatory)]
  [string]$Error,
  [string]$MessageBody,
  [string]$RepoRoot,
  [switch]$Json
)
'@
      @'
function Resolve-CodexUserLevelWorkerStatusPath {
  param(
    [Parameter(Mandatory)]
    [string]$ResolvedRepoRoot,
    [Parameter(Mandatory)]
    [string]$TeamName,
    [Parameter(Mandatory)]
    [string]$Worker
  )

  return (Join-Path (Join-Path (Join-Path (Get-CodexUserLevelTeamStateRoot -RepoRoot $ResolvedRepoRoot) $TeamName) 'workers') (Join-Path $Worker 'status.json'))
}

function Write-CodexUserLevelWorkerStatusFile {
  param(
    [Parameter(Mandatory)]
    [string]$Path,
    [Parameter(Mandatory)]
    $Payload
  )

  $directory = Split-Path -Parent $Path
  if (-not (Test-Path -LiteralPath $directory)) {
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
  }
  Set-Content -LiteralPath $Path -Value ($Payload | ConvertTo-Json -Depth 6) -Encoding UTF8 -NoNewline
}

function Invoke-CodexUserLevelWorkerWrapperScript {
  param(
    [Parameter(Mandatory)]
    [string]$ScriptPath,
    [Parameter(Mandatory)]
    [hashtable]$Invocation
  )

  $rawOutput = @(& $ScriptPath @Invocation)
  $exitCode = if (Test-Path -LiteralPath variable:LASTEXITCODE) { [int]$LASTEXITCODE } else { 0 }
  if ($exitCode -ne 0) {
    throw "Wrapper failed: $ScriptPath (exit $exitCode)"
  }

  if ($rawOutput.Count -lt 1) {
    return $null
  }

  return (($rawOutput -join [Environment]::NewLine) | ConvertFrom-Json)
}

$resolvedRepoRoot = Resolve-CodexUserLevelRepoRoot -OverridePath $RepoRoot
$binDirectory = Get-CodexUserLevelBinDirectory
$transitionScriptPath = Join-Path $binDirectory 'omx-team-transition-task-status.ps1'
$sendMessageScriptPath = Join-Path $binDirectory 'omx-team-send-message.ps1'
$statusPath = Resolve-CodexUserLevelWorkerStatusPath -ResolvedRepoRoot $resolvedRepoRoot -TeamName $TeamName -Worker $Worker
$notifyBody = if (-not [string]::IsNullOrWhiteSpace($MessageBody)) { $MessageBody } else { "Failed task ${TaskId}: $Error" }
$transitionResult = Invoke-CodexUserLevelWorkerWrapperScript -ScriptPath $transitionScriptPath -Invocation @{
  TeamName = $TeamName
  TaskId = $TaskId
  From = 'in_progress'
  To = 'failed'
  ClaimToken = $ClaimToken
  Error = $Error
  RepoRoot = $resolvedRepoRoot
  Json = $true
}
Write-CodexUserLevelWorkerStatusFile -Path $statusPath -Payload ([ordered]@{
  state = 'failed'
  updated_at = (Get-Date).ToUniversalTime().ToString('o')
  current_task_id = $TaskId
  reason = $Error
})
$notifyResult = Invoke-CodexUserLevelWorkerWrapperScript -ScriptPath $sendMessageScriptPath -Invocation @{
  TeamName = $TeamName
  FromWorker = $Worker
  ToWorker = 'leader-fixed'
  Body = $notifyBody
  RepoRoot = $resolvedRepoRoot
  Json = $true
}
$resultObject = [ordered]@{
  operation = 'fail-task'
  team_name = $TeamName
  task_id = $TaskId
  worker = $Worker
  transition = $transitionResult
  notify = $notifyResult
  status_path = $statusPath
}
if ($Json) {
  $resultObject | ConvertTo-Json -Depth 8
} else {
  Write-Output ("operation={0}" -f $resultObject.operation)
  Write-Output ("team_name={0}" -f $resultObject.team_name)
  Write-Output ("task_id={0}" -f $resultObject.task_id)
  Write-Output ("worker={0}" -f $resultObject.worker)
}
'@
    }
  }

  return @"
# $Script:ManagedMarker
$paramBlock

$runtimeContent
$body
`$exitCode = 0
if (Test-Path -LiteralPath variable:LASTEXITCODE) {
  `$exitCode = [int]`$LASTEXITCODE
}
exit `$exitCode
"@
}

function Get-OmxTeamHybridScriptContent {
  param(
    [Parameter(Mandatory)]
    [string]$OmxResolvedPath
  )

  $runtimeContent = Get-CommandRuntimeContent
  $escapedOmxResolvedPath = $OmxResolvedPath.Replace("'", "''")

  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string]`$Task,
  [ValidateRange(0, 8)]
  [int]`$Architect = 0,
  [ValidateRange(0, 8)]
  [int]`$Planner = 0,
  [ValidateRange(0, 8)]
  [int]`$Verifier = 0,
  [ValidateRange(0, 8)]
  [int]`$Executor = 2,
  [ValidateSet('team-executor', 'executor')]
  [string]`$WorkerRole = 'team-executor',
  [string]`$RepoRoot,
  [switch]`$Launch,
  [switch]`$Json
)

$runtimeContent

`$plan = Get-CodexUserLevelHybridPlan -Task `$Task -Architect `$Architect -Planner `$Planner -Executor `$Executor -Verifier `$Verifier -WorkerRole `$WorkerRole
if (-not `$Launch) {
  if (`$Json) {
    `$plan | ConvertTo-Json -Depth 8
    return
  }

  Write-Output ("task={0}" -f `$plan.task)
  Write-Output ("current_mode={0}" -f `$plan.current_mode)
  Write-Output ("durable_team={0}:{1}" -f `$plan.durable_team.worker_count, `$plan.durable_team.worker_role)
  foreach (`$expert in @(`$plan.leader_side_experts)) {
    Write-Output ("leader_expert={0}x{1}@{2}" -f `$expert.count, `$expert.name, `$expert.default_phase)
  }
  return
}

if (`$Executor -lt 1) {
  throw 'Executor count must be at least 1 when -Launch is used.'
}

`$omxCommandPath = '$escapedOmxResolvedPath'
`$launchArgs = @(`$plan.durable_team.launch_args | ForEach-Object { [string]`$_ })
`$locationPushed = `$false

try {
  if (-not [string]::IsNullOrWhiteSpace(`$RepoRoot)) {
    Push-Location -LiteralPath (Resolve-CodexUserLevelRepoRoot -OverridePath `$RepoRoot)
    `$locationPushed = `$true
  }

  if (`$Json) {
    `$launchOutput = @(& `$omxCommandPath @launchArgs)
    [ordered]@{
      plan = `$plan
      launch_args = `$launchArgs
      launch_output = `$launchOutput
    } | ConvertTo-Json -Depth 8
    return
  }

  Write-Output ("launching_durable_team={0}:{1}" -f `$plan.durable_team.worker_count, `$plan.durable_team.worker_role)
  foreach (`$expert in @(`$plan.leader_side_experts)) {
    Write-Output ("leader_expert={0}x{1}@{2}" -f `$expert.count, `$expert.name, `$expert.default_phase)
  }
  & `$omxCommandPath @launchArgs
}
finally {
  if (`$locationPushed) {
    Pop-Location
  }
}

`$exitCode = 0
if (Test-Path -LiteralPath variable:LASTEXITCODE) {
  `$exitCode = [int]`$LASTEXITCODE
}
exit `$exitCode
"@
}

function Get-OmxTeamVerifyScriptContent {
  $runtimeContent = Get-CommandRuntimeContent

  return @"
# $Script:ManagedMarker
[CmdletBinding()]
param(
  [string]`$Task = '',
  [bool]`$BehaviorChanged = `$true,
  [switch]`$NeedsSecurityReview,
  [switch]`$NeedsDocsReview,
  [bool]`$NeedsTestCoverage = `$true,
  [switch]`$Json
)

$runtimeContent

`$plan = Get-CodexUserLevelVerificationPlan -Task `$Task -BehaviorChanged `$BehaviorChanged -NeedsSecurityReview ([bool]`$NeedsSecurityReview) -NeedsDocsReview ([bool]`$NeedsDocsReview) -NeedsTestCoverage `$NeedsTestCoverage
if (`$Json) {
  `$plan | ConvertTo-Json -Depth 8
  return
}

Write-Output ("current_mode={0}" -f `$plan.current_mode)
Write-Output ("persistent_verifier_team_default={0}" -f `$plan.persistent_verifier_team_default)
foreach (`$role in @(`$plan.verification_roles)) {
  Write-Output ("verification_role={0}:{1}" -f `$role.name, `$role.reason)
}
"@
}

$targetCodexHome = Resolve-TargetCodexHome
$resolvedPowerShellProfilePath = Resolve-PowerShellProfileTargetPath
$resolvedNativeCodexCommandPath = Resolve-NativeCodexCommandPath
$resolvedOmxCommandPath = Resolve-OmxCommandPath
$resolvedPythonCommandPath = Resolve-PythonCommandPath
$binDirectory = Join-Path $targetCodexHome 'bin'
$winShimsDirectory = Join-Path $binDirectory 'win-shims'
$agentsDirectory = Join-Path $targetCodexHome 'agents'
$docsDirectory = Join-Path $targetCodexHome 'docs'
$teamsDirectory = Join-Path $targetCodexHome 'teams'
$pythonDirectory = Join-Path $targetCodexHome 'python'
$langGraphPythonDirectory = Join-Path $pythonDirectory 'langgraph_durable_orchestrator'
$venvsDirectory = Join-Path $targetCodexHome 'venvs'
$stateDirectory = Join-Path $targetCodexHome 'state'
$statePath = Join-Path $stateDirectory 'user-level-team-mode.json'
$nativeSubagentLimitsPath = Join-Path $stateDirectory 'native-subagent-limits.json'
$launcherPath = Join-Path $binDirectory '_codex-user-level-team-mode-launcher.ps1'
$nativeCommandDirectory = Split-Path -Parent $resolvedNativeCodexCommandPath
$explicitWrappedCodexPs1Path = Join-Path $nativeCommandDirectory 'codex.openclaw.ps1'
$explicitWrappedCodexCmdPath = Join-Path $nativeCommandDirectory 'codex.openclaw.cmd'
$explicitNativeBypassPs1Path = Join-Path $nativeCommandDirectory 'codex-native.ps1'
$explicitNativeBypassCmdPath = Join-Path $nativeCommandDirectory 'codex-native.cmd'
$stableWrappedCodexPs1Path = Join-Path $nativeCommandDirectory 'codex-ohmy.ps1'
$stableWrappedCodexCmdPath = Join-Path $nativeCommandDirectory 'codex-ohmy.cmd'
$stableNativeBypassPs1Path = Join-Path $nativeCommandDirectory 'codex-raw.ps1'
$stableNativeBypassCmdPath = Join-Path $nativeCommandDirectory 'codex-raw.cmd'
$teamPlaybookPath = Join-Path $docsDirectory 'team-mode-playbook.md'
$teamQuickReferencePath = Join-Path $docsDirectory 'team-mode-quick-reference.md'
$composeManifestSchemaPath = Join-Path $teamsDirectory 'compose-manifest.schema.json'
$managedProfileBlock = Get-ManagedProfileBlockContent -LauncherPath $launcherPath -NativeCommandPath $resolvedNativeCodexCommandPath
$taskkillExeShimRequested = -not [bool]$SkipTaskkillExeShim

Ensure-Directory -Path $targetCodexHome
Ensure-Directory -Path $binDirectory
Ensure-Directory -Path $winShimsDirectory
Ensure-Directory -Path $agentsDirectory
Ensure-Directory -Path $docsDirectory
Ensure-Directory -Path $teamsDirectory
Ensure-Directory -Path $pythonDirectory
Ensure-Directory -Path $langGraphPythonDirectory
Ensure-Directory -Path $venvsDirectory
Ensure-Directory -Path $stateDirectory

$assets = @(
  [ordered]@{ Path = (Join-Path $agentsDirectory 'team-leader.toml'); Content = (Get-TeamLeaderTomlContent) }
  [ordered]@{ Path = (Join-Path $agentsDirectory 'verifier.toml'); Content = (Get-VerifierTomlContent) }
  [ordered]@{ Path = (Join-Path $agentsDirectory 'debugger.toml'); Content = (Get-DebuggerTomlContent) }
  [ordered]@{ Path = (Join-Path $agentsDirectory 'researcher.toml'); Content = (Get-ResearcherTomlContent) }
  [ordered]@{ Path = (Join-Path $agentsDirectory 'dependency-expert.toml'); Content = (Get-DependencyExpertTomlContent) }
  [ordered]@{ Path = (Join-Path $agentsDirectory 'writer.toml'); Content = (Get-WriterTomlContent) }
  [ordered]@{ Path = (Join-Path $agentsDirectory 'bug-finder.toml'); Content = (Get-BugFinderTomlContent) }
  [ordered]@{ Path = (Join-Path $agentsDirectory 'bug-rebutter.toml'); Content = (Get-BugRebutterTomlContent) }
  [ordered]@{ Path = (Join-Path $agentsDirectory 'bug-judge.toml'); Content = (Get-BugJudgeTomlContent) }
  [ordered]@{ Path = (Join-Path $binDirectory '_codex-user-level-team-mode.ps1'); Content = (Get-SupportScriptContent) }
  [ordered]@{ Path = $launcherPath; Content = (Get-StartupLauncherContent -NativeCommandPath $resolvedNativeCodexCommandPath -TaskkillExeShimRequested ([bool]$taskkillExeShimRequested)) }
  [ordered]@{ Path = (Join-Path $winShimsDirectory 'taskkill.cmd'); Content = (Get-WindowsTaskkillCmdShimContent) }
  [ordered]@{ Path = (Join-Path $winShimsDirectory 'taskkill.ps1'); Content = (Get-WindowsTaskkillPowerShellShimContent) }
  [ordered]@{ Path = (Join-Path $winShimsDirectory 'taskkill-shim-source.cs'); Content = (Get-WindowsTaskkillCSharpShimSourceContent) }
  [ordered]@{ Path = $explicitWrappedCodexPs1Path; Content = (Get-ExplicitWrappedCodexPs1Content -LauncherPath $launcherPath) }
  [ordered]@{ Path = $explicitWrappedCodexCmdPath; Content = (Get-ExplicitLauncherCmdContent -TargetPs1Path $explicitWrappedCodexPs1Path) }
  [ordered]@{ Path = $explicitNativeBypassPs1Path; Content = (Get-ExplicitNativeBypassPs1Content -NativeCommandPath $resolvedNativeCodexCommandPath) }
  [ordered]@{ Path = $explicitNativeBypassCmdPath; Content = (Get-ExplicitLauncherCmdContent -TargetPs1Path $explicitNativeBypassPs1Path) }
  [ordered]@{ Path = $stableWrappedCodexPs1Path; Content = (Get-ExplicitWrappedCodexPs1Content -LauncherPath $launcherPath) }
  [ordered]@{ Path = $stableWrappedCodexCmdPath; Content = (Get-ExplicitLauncherCmdContent -TargetPs1Path $stableWrappedCodexPs1Path) }
  [ordered]@{ Path = $stableNativeBypassPs1Path; Content = (Get-ExplicitNativeBypassPs1Content -NativeCommandPath $resolvedNativeCodexCommandPath) }
  [ordered]@{ Path = $stableNativeBypassCmdPath; Content = (Get-ExplicitLauncherCmdContent -TargetPs1Path $stableNativeBypassPs1Path) }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-omx-on.ps1'); Content = (Get-CommandScriptContent -Mutation "`$null = Set-CodexUserLevelTeamModeState -OhMyCodex 'on'") }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-omx-off.ps1'); Content = (Get-CommandScriptContent -Mutation "`$null = Set-CodexUserLevelTeamModeState -OhMyCodex 'off'") }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-omx-status.ps1'); Content = (Get-CommandScriptContent -Mutation '' -View 'omx') }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-subagents-auto.ps1'); Content = (Get-CommandScriptContent -Mutation "`$null = Set-CodexUserLevelTeamModeState -SubagentRouting 'auto'") }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-subagents-manual.ps1'); Content = (Get-CommandScriptContent -Mutation "`$null = Set-CodexUserLevelTeamModeState -SubagentRouting 'manual'") }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-subagents-off.ps1'); Content = (Get-CommandScriptContent -Mutation "`$null = Set-CodexUserLevelTeamModeState -SubagentRouting 'off'") }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-subagent-retention-close.ps1'); Content = (Get-CommandScriptContent -Mutation "`$null = Set-CodexUserLevelTeamModeState -CompletedSubagentRetention 'close'" -View 'routing') }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-subagent-retention-keep.ps1'); Content = (Get-CommandScriptContent -Mutation "`$null = Set-CodexUserLevelTeamModeState -CompletedSubagentRetention 'keep'" -View 'routing') }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-subagent-retention-status.ps1'); Content = (Get-CommandScriptContent -Mutation '' -View 'routing') }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-langgraph-on.ps1'); Content = (Get-CommandScriptContent -Mutation "`$null = Set-CodexUserLevelTeamModeState -LangGraph 'on'" -View 'langgraph') }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-langgraph-off.ps1'); Content = (Get-CommandScriptContent -Mutation "`$null = Set-CodexUserLevelTeamModeState -LangGraph 'off'" -View 'langgraph') }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-langgraph-status.ps1'); Content = (Get-CommandScriptContent -Mutation '' -View 'langgraph') }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-routing-status.ps1'); Content = (Get-CommandScriptContent -Mutation '' -View 'routing') }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-durable-backend-native-omx.ps1'); Content = (Get-CommandScriptContent -Mutation "`$null = Set-CodexUserLevelTeamModeState -DurableOrchestrationBackend 'native_omx'" -View 'backend') }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-durable-backend-langgraph.ps1'); Content = (Get-CommandScriptContent -Mutation "`$null = Set-CodexUserLevelTeamModeState -DurableOrchestrationBackend 'langgraph'" -View 'backend') }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-durable-backend-status.ps1'); Content = (Get-CommandScriptContent -Mutation '' -View 'backend') }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-durable-state-status.ps1'); Content = (Get-CodexDurableStateStatusScriptContent) }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-durable-state-reconcile.ps1'); Content = (Get-CodexDurableStateReconcileScriptContent) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-compose.ps1'); Content = (Get-OmxTeamComposeScriptContent -OmxResolvedPath $resolvedOmxCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-compose-status.ps1'); Content = (Get-OmxTeamComposeStatusScriptContent) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-compose-await.ps1'); Content = (Get-OmxTeamComposeAwaitScriptContent) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-compose-recover.ps1'); Content = (Get-OmxTeamComposeRecoverScriptContent) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-compose-shutdown.ps1'); Content = (Get-OmxTeamComposeShutdownScriptContent -OmxResolvedPath $resolvedOmxCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-compose-reconcile.ps1'); Content = (Get-OmxTeamComposeReconcileScriptContent) }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-routing-policy.ps1'); Content = (Get-CommandScriptContent -Mutation '' -View 'routing_policy') }
  [ordered]@{ Path = (Join-Path $binDirectory 'codex-subagent-limits.ps1'); Content = (Get-CodexSubagentLimitsScriptContent) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-install.ps1'); Content = (Get-LangGraphInstallScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-cli.ps1'); Content = (Get-LangGraphCliScriptContent) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-run.ps1'); Content = (Get-LangGraphRunScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-status.ps1'); Content = (Get-LangGraphStatusScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-resume.ps1'); Content = (Get-LangGraphResumeScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-inspect.ps1'); Content = (Get-LangGraphInspectScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-kernel.ps1'); Content = (Get-LangGraphKernelScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-engine.ps1'); Content = (Get-LangGraphEngineScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-invocation.ps1'); Content = (Get-LangGraphInvocationScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-live-execution.ps1'); Content = (Get-LangGraphLiveExecutionScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-fuller-engine.ps1'); Content = (Get-LangGraphFullerEngineScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-deeper-engine.ps1'); Content = (Get-LangGraphDeeperEngineScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-superstep-engine.ps1'); Content = (Get-LangGraphSuperstepEngineScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-stateful-engine.ps1'); Content = (Get-LangGraphStatefulEngineScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-boundary-engine.ps1'); Content = (Get-LangGraphBoundaryEngineScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-handoff-engine.ps1'); Content = (Get-LangGraphHandoffEngineScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-approval-engine.ps1'); Content = (Get-LangGraphApprovalEngineScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-provenance-engine.ps1'); Content = (Get-LangGraphProvenanceEngineScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-artifact-engine.ps1'); Content = (Get-LangGraphArtifactEngineScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-reducer-engine.ps1'); Content = (Get-LangGraphReducerEngineScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-command-engine.ps1'); Content = (Get-LangGraphCommandEngineScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-runtime-engine.ps1'); Content = (Get-LangGraphRuntimeEngineScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-memory-engine.ps1'); Content = (Get-LangGraphMemoryEngineScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-migration-engine.ps1'); Content = (Get-LangGraphMigrationEngineScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-auto-policy.ps1'); Content = (Get-LangGraphAutoPolicyScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-subgraph-state.ps1'); Content = (Get-LangGraphSubgraphStateScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-generalized-routing.ps1'); Content = (Get-LangGraphGeneralizedRoutingScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-approval-queue.ps1'); Content = (Get-LangGraphApprovalQueueScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-migration.ps1'); Content = (Get-LangGraphMigrationScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-memory.ps1'); Content = (Get-LangGraphMemoryScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-runtime.ps1'); Content = (Get-LangGraphRuntimeScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-stream.ps1'); Content = (Get-LangGraphStreamScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-subgraphs.ps1'); Content = (Get-LangGraphSubgraphsScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-history.ps1'); Content = (Get-LangGraphHistoryScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-replay.ps1'); Content = (Get-LangGraphReplayScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-langgraph-recover.ps1'); Content = (Get-LangGraphRecoverScriptContent -PythonResolvedPath $resolvedPythonCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-dev.ps1'); Content = (Get-OmxTeamDevScriptContent -OmxResolvedPath $resolvedOmxCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-debug.ps1'); Content = (Get-OmxTeamDebugScriptContent -OmxResolvedPath $resolvedOmxCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-auto.ps1'); Content = (Get-OmxTeamAutoScriptContent -OmxResolvedPath $resolvedOmxCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-ops.ps1'); Content = (Get-OmxTeamOpsScriptContent -OmxResolvedPath $resolvedOmxCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-send-message.ps1'); Content = (Get-OmxTeamSafeApiCommandScriptContent -OmxResolvedPath $resolvedOmxCommandPath -Operation 'send-message') }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-mailbox-list.ps1'); Content = (Get-OmxTeamSafeApiCommandScriptContent -OmxResolvedPath $resolvedOmxCommandPath -Operation 'mailbox-list') }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-mailbox-mark-delivered.ps1'); Content = (Get-OmxTeamSafeApiCommandScriptContent -OmxResolvedPath $resolvedOmxCommandPath -Operation 'mailbox-mark-delivered') }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-claim-task.ps1'); Content = (Get-OmxTeamSafeApiCommandScriptContent -OmxResolvedPath $resolvedOmxCommandPath -Operation 'claim-task') }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-transition-task-status.ps1'); Content = (Get-OmxTeamSafeApiCommandScriptContent -OmxResolvedPath $resolvedOmxCommandPath -Operation 'transition-task-status') }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-release-task-claim.ps1'); Content = (Get-OmxTeamSafeApiCommandScriptContent -OmxResolvedPath $resolvedOmxCommandPath -Operation 'release-task-claim') }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-report-progress.ps1'); Content = (Get-OmxTeamHighLevelWorkerScriptContent -Operation 'report-progress') }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-complete-task.ps1'); Content = (Get-OmxTeamHighLevelWorkerScriptContent -Operation 'complete-task') }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-fail-task.ps1'); Content = (Get-OmxTeamHighLevelWorkerScriptContent -Operation 'fail-task') }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-hybrid.ps1'); Content = (Get-OmxTeamHybridScriptContent -OmxResolvedPath $resolvedOmxCommandPath) }
  [ordered]@{ Path = (Join-Path $binDirectory 'omx-team-verify.ps1'); Content = (Get-OmxTeamVerifyScriptContent) }
  [ordered]@{ Path = $teamPlaybookPath; Content = (Get-TeamPlaybookContent) }
  [ordered]@{ Path = $teamQuickReferencePath; Content = (Get-TeamQuickReferenceContent) }
  [ordered]@{ Path = $composeManifestSchemaPath; Content = (Get-ComposeManifestSchemaContent) }
  [ordered]@{ Path = (Join-Path $langGraphPythonDirectory '__init__.py'); Content = (Get-RepoTemplateText -RelativePath 'langgraph_durable_orchestrator\__init__.py') }
  [ordered]@{ Path = (Join-Path $langGraphPythonDirectory 'contracts.py'); Content = (Get-RepoTemplateText -RelativePath 'langgraph_durable_orchestrator\contracts.py') }
  [ordered]@{ Path = (Join-Path $langGraphPythonDirectory 'runtime.py'); Content = (Get-RepoTemplateText -RelativePath 'langgraph_durable_orchestrator\runtime.py') }
  [ordered]@{ Path = (Join-Path $langGraphPythonDirectory 'cli.py'); Content = (Get-RepoTemplateText -RelativePath 'langgraph_durable_orchestrator\cli.py') }
)

if ($taskkillExeShimRequested) {
  $assets += [ordered]@{ Path = (Join-Path $winShimsDirectory 'taskkill.exe'); Content = '' }
}

foreach ($asset in $assets) {
  $fileName = (Split-Path -Leaf $asset.Path).ToLowerInvariant()
  if ($Script:NativeCodexNames -contains $fileName) {
    throw "Refusing to generate native codex filename: $fileName"
  }
}

Assert-ManagedAssetWriteAllowed -Assets $assets -ForceWrite:$Force

$backupSnapshot = $null
$backupPaths = @($assets | ForEach-Object { $_.Path }) + @($statePath, $nativeSubagentLimitsPath) + @($resolvedPowerShellProfilePath)
$backupSnapshot = New-InstallBackupSnapshot -TargetCodexHome $targetCodexHome -Paths $backupPaths

$generatedFiles = @()
$stateStatus = $null
$nativeSubagentLimitsStatus = $null
$profileStatus = $null

try {
  Invoke-TestFailPoint -Name 'after_backup'

  foreach ($asset in $assets) {
    if ((Split-Path -Leaf $asset.Path).ToLowerInvariant() -eq 'taskkill.exe') {
      continue
    }
    $writeResult = Write-ManagedTextFile -Path $asset.Path -Content $asset.Content -ForceWrite:$Force
    $generatedFiles += [ordered]@{
      path = $asset.Path
      status = $writeResult
    }
  }

  $taskkillExeShimCompile = [ordered]@{
    attempted = [bool]$taskkillExeShimRequested
    compiled = $false
    output_path = (Join-Path $winShimsDirectory 'taskkill.exe')
    compiler_path = ''
    reason = if ($taskkillExeShimRequested) { '' } else { 'taskkill.exe shim disabled by SkipTaskkillExeShim' }
  }
  if ($taskkillExeShimRequested) {
    $taskkillExeShimCompile = Try-CompileWindowsTaskkillExeShim -SourcePath (Join-Path $winShimsDirectory 'taskkill-shim-source.cs') -OutputPath (Join-Path $winShimsDirectory 'taskkill.exe')
    if ($InstallTaskkillExeShim -and -not [bool]$taskkillExeShimCompile.compiled) {
      throw ("Unable to compile optional taskkill.exe shim: {0}" -f [string]$taskkillExeShimCompile.reason)
    }
    if ([bool]$taskkillExeShimCompile.compiled) {
      $generatedFiles += [ordered]@{
        path = (Join-Path $winShimsDirectory 'taskkill.exe')
        status = 'written'
      }
    }
  }

  Invoke-TestFailPoint -Name 'after_assets'

  $loadedState = Read-RawStateFile -Path $statePath
  if ($null -eq $loadedState) {
    $existingState = New-DefaultState
    Write-StateFile -Path $statePath -State $existingState
    $stateStatus = 'created'
  } else {
    $existingState = Merge-State -LoadedState $loadedState
    if (Test-StateRewriteRequired -LoadedState $loadedState -NormalizedState $existingState) {
      Write-StateFile -Path $statePath -State $existingState
      $stateStatus = 'normalized'
    } else {
      $stateStatus = 'preserved'
    }
  }

  $existingNativeSubagentLimits = Read-NativeSubagentLimitsFile -Path $nativeSubagentLimitsPath
  if ($null -eq $existingNativeSubagentLimits) {
    $existingNativeSubagentLimits = New-DefaultNativeSubagentLimits
    Write-NativeSubagentLimitsFile -Path $nativeSubagentLimitsPath -Limits $existingNativeSubagentLimits
    $nativeSubagentLimitsStatus = 'created'
  } else {
    $nativeSubagentLimitsStatus = 'preserved'
  }

  Invoke-TestFailPoint -Name 'after_state'

  $profileStatus = Write-ManagedProfileBinding -Path $resolvedPowerShellProfilePath -ManagedBlock $managedProfileBlock -ForceWrite:$Force

  Invoke-TestFailPoint -Name 'after_profile'
}
catch {
  $installError = $_
  if ($null -eq $backupSnapshot) {
    throw "Installation failed before backup snapshot creation. Root cause: $($installError.Exception.Message)"
  }

  try {
    Restore-InstallBackupSnapshot -Snapshot $backupSnapshot
  }
  catch {
    throw "Installation failed and rollback failed. Install error: $($installError.Exception.Message) Rollback error: $($_.Exception.Message)"
  }

  throw "Installation failed. Previous managed state restored from $($backupSnapshot['path']). Root cause: $($installError.Exception.Message)"
}

$currentState = Read-StateFile -Path $statePath
$currentNativeSubagentLimits = Read-NativeSubagentLimitsFile -Path $nativeSubagentLimitsPath
$manifest = [ordered]@{
  managed_by = $Script:ManagedBy
  target_codex_home = $targetCodexHome
  state_path = $statePath
  state_status = $stateStatus
  current_state = [ordered]@{
    oh_my_codex = [string]$currentState['oh_my_codex']
    subagent_routing = [string]$currentState['subagent_routing']
    completed_subagent_retention = [string]$currentState['completed_subagent_retention']
    langgraph = [string]$currentState['langgraph']
    durable_orchestration_backend = [string]$currentState['durable_orchestration_backend']
    updated_at = [string]$currentState['updated_at']
  }
  native_subagent_limits = [ordered]@{
    path = $nativeSubagentLimitsPath
    status = $nativeSubagentLimitsStatus
    max_threads = [int]$currentNativeSubagentLimits['max_threads']
    max_depth = [int]$currentNativeSubagentLimits['max_depth']
    updated_at = [string]$currentNativeSubagentLimits['updated_at']
  }
  generated_files = $generatedFiles
  startup_binding = [ordered]@{
    launcher_path = $launcherPath
    cleanup_output_control = [ordered]@{
      win_shims_directory = $winShimsDirectory
      taskkill_cmd_path = (Join-Path $winShimsDirectory 'taskkill.cmd')
      taskkill_ps1_path = (Join-Path $winShimsDirectory 'taskkill.ps1')
      taskkill_shim_source_path = (Join-Path $winShimsDirectory 'taskkill-shim-source.cs')
      taskkill_exe_shim_path = (Join-Path $winShimsDirectory 'taskkill.exe')
      taskkill_exe_shim_requested = [bool]$taskkillExeShimRequested
      taskkill_exe_shim_enabled = [bool]$taskkillExeShimCompile.compiled
      taskkill_exe_shim_compile = $taskkillExeShimCompile
      login_profile_env_bridge = 'CODEX_USER_LEVEL_CLEANUP_SHIM_DIRECTORY'
      scoped_to_wrapped_launch = $true
    }
    powershell_profile_path = $resolvedPowerShellProfilePath
    powershell_profile_status = $profileStatus
    native_codex_command_path = $resolvedNativeCodexCommandPath
    native_command_directory = $nativeCommandDirectory
    non_profile_launchers = [ordered]@{
      wrapped_ps1_path = $explicitWrappedCodexPs1Path
      wrapped_cmd_path = $explicitWrappedCodexCmdPath
      native_bypass_ps1_path = $explicitNativeBypassPs1Path
      native_bypass_cmd_path = $explicitNativeBypassCmdPath
      stable_wrapped_ps1_path = $stableWrappedCodexPs1Path
      stable_wrapped_cmd_path = $stableWrappedCodexCmdPath
      stable_native_bypass_ps1_path = $stableNativeBypassPs1Path
      stable_native_bypass_cmd_path = $stableNativeBypassCmdPath
    }
  }
  omx_entrypoints = [ordered]@{
    omx_command_path = $resolvedOmxCommandPath
    python_command_path = $resolvedPythonCommandPath
    langgraph_shared_venv_path = (Join-Path $venvsDirectory 'langgraph-py312')
    langgraph_shared_python_path = (Join-Path (Join-Path (Join-Path $venvsDirectory 'langgraph-py312') 'Scripts') 'python.exe')
    langgraph_helper_artifact_root = (Join-Path $pythonDirectory 'langgraph_durable_orchestrator')
    playbook_path = $teamPlaybookPath
    quick_reference_path = $teamQuickReferencePath
    compose_manifest_schema_path = $composeManifestSchemaPath
    automatic_team_helper_path = (Join-Path $binDirectory 'omx-team-auto.ps1')
    compose_entrypoint_path = (Join-Path $binDirectory 'omx-team-compose.ps1')
    compose_status_path = (Join-Path $binDirectory 'omx-team-compose-status.ps1')
    compose_await_path = (Join-Path $binDirectory 'omx-team-compose-await.ps1')
    compose_recover_path = (Join-Path $binDirectory 'omx-team-compose-recover.ps1')
    compose_shutdown_path = (Join-Path $binDirectory 'omx-team-compose-shutdown.ps1')
    compose_reconcile_path = (Join-Path $binDirectory 'omx-team-compose-reconcile.ps1')
    langgraph_install_path = (Join-Path $binDirectory 'omx-langgraph-install.ps1')
    langgraph_cli_path = (Join-Path $binDirectory 'omx-langgraph-cli.ps1')
    langgraph_run_path = (Join-Path $binDirectory 'omx-langgraph-run.ps1')
    langgraph_status_path = (Join-Path $binDirectory 'omx-langgraph-status.ps1')
    langgraph_resume_path = (Join-Path $binDirectory 'omx-langgraph-resume.ps1')
    langgraph_inspect_path = (Join-Path $binDirectory 'omx-langgraph-inspect.ps1')
    langgraph_kernel_path = (Join-Path $binDirectory 'omx-langgraph-kernel.ps1')
    langgraph_engine_path = (Join-Path $binDirectory 'omx-langgraph-engine.ps1')
    langgraph_invocation_path = (Join-Path $binDirectory 'omx-langgraph-invocation.ps1')
    langgraph_live_execution_path = (Join-Path $binDirectory 'omx-langgraph-live-execution.ps1')
    langgraph_fuller_engine_path = (Join-Path $binDirectory 'omx-langgraph-fuller-engine.ps1')
    langgraph_deeper_engine_path = (Join-Path $binDirectory 'omx-langgraph-deeper-engine.ps1')
    langgraph_superstep_engine_path = (Join-Path $binDirectory 'omx-langgraph-superstep-engine.ps1')
    langgraph_stateful_engine_path = (Join-Path $binDirectory 'omx-langgraph-stateful-engine.ps1')
    langgraph_boundary_engine_path = (Join-Path $binDirectory 'omx-langgraph-boundary-engine.ps1')
    langgraph_handoff_engine_path = (Join-Path $binDirectory 'omx-langgraph-handoff-engine.ps1')
    langgraph_approval_engine_path = (Join-Path $binDirectory 'omx-langgraph-approval-engine.ps1')
    langgraph_provenance_engine_path = (Join-Path $binDirectory 'omx-langgraph-provenance-engine.ps1')
    langgraph_artifact_engine_path = (Join-Path $binDirectory 'omx-langgraph-artifact-engine.ps1')
    langgraph_reducer_engine_path = (Join-Path $binDirectory 'omx-langgraph-reducer-engine.ps1')
    langgraph_command_engine_path = (Join-Path $binDirectory 'omx-langgraph-command-engine.ps1')
    langgraph_runtime_engine_path = (Join-Path $binDirectory 'omx-langgraph-runtime-engine.ps1')
    langgraph_memory_engine_path = (Join-Path $binDirectory 'omx-langgraph-memory-engine.ps1')
    langgraph_migration_engine_path = (Join-Path $binDirectory 'omx-langgraph-migration-engine.ps1')
    langgraph_auto_policy_path = (Join-Path $binDirectory 'omx-langgraph-auto-policy.ps1')
    langgraph_subgraph_state_path = (Join-Path $binDirectory 'omx-langgraph-subgraph-state.ps1')
    langgraph_generalized_routing_path = (Join-Path $binDirectory 'omx-langgraph-generalized-routing.ps1')
    langgraph_approval_queue_path = (Join-Path $binDirectory 'omx-langgraph-approval-queue.ps1')
    langgraph_migration_path = (Join-Path $binDirectory 'omx-langgraph-migration.ps1')
    langgraph_memory_path = (Join-Path $binDirectory 'omx-langgraph-memory.ps1')
    langgraph_runtime_path = (Join-Path $binDirectory 'omx-langgraph-runtime.ps1')
    langgraph_stream_path = (Join-Path $binDirectory 'omx-langgraph-stream.ps1')
    langgraph_subgraphs_path = (Join-Path $binDirectory 'omx-langgraph-subgraphs.ps1')
    langgraph_history_path = (Join-Path $binDirectory 'omx-langgraph-history.ps1')
    langgraph_replay_path = (Join-Path $binDirectory 'omx-langgraph-replay.ps1')
    langgraph_recover_path = (Join-Path $binDirectory 'omx-langgraph-recover.ps1')
    durable_state_status_path = (Join-Path $binDirectory 'codex-durable-state-status.ps1')
    durable_state_reconcile_path = (Join-Path $binDirectory 'codex-durable-state-reconcile.ps1')
  }
  backup = [ordered]@{
    path = $backupSnapshot['path']
    manifest_path = $backupSnapshot['manifest_path']
    created_at = $backupSnapshot['created_at']
    rollback_on_error = $true
  }
  preserves_native_codex = $true
}

$manifest | ConvertTo-Json -Depth 6
