# codex-user-level-windows-cleanup-output-control Delta

## Modified Requirements

### Requirement: Wrapped cleanup-output control SHALL cover explicit taskkill.exe paths by default

用户级 installer 默认应为 wrapped `codex-ohmy` 启动请求 explicit `taskkill.exe` cleanup-output shim。

installer 应先从 PATH 和标准 Windows .NET Framework compiler directories（包括 Framework64 与 Framework 位置）发现 C# compiler，然后才能判定 executable shim 不可用。

installer 应把 executable-shim compiler 的 stdout 与 stderr 捕获到 generated shim directory 下的文件中，而不是只依赖 ambient temp directory。

generated executable shim 在真实 Windows `taskkill.exe` 以 exit code 0 退出时，应抑制全部 stdout 与 stderr，包括 `成功: 已终止 PID ...` 这类中文本地化成功行。

generated executable shim 应保留非零 cleanup failure：把捕获到的输出转发到 stderr，并返回原始 exit code。

生成的 launcher 只有在运行时确实存在生成的 `win-shims\taskkill.exe` 文件时，才应在 `PATHEXT` 中优先 `.EXE`。如果该 executable shim 不可用，launcher 应回退到现有 `.CMD` shim，且不应破坏 wrapped launch。

installer 应提供显式 opt-out 开关，用于不能或不应编译 executable shim 的环境。

#### Scenario: Default install can intercept explicit taskkill.exe cleanup with Framework compiler fallback

- **WHEN** `csc.exe` 不在 PATH 中，但存在于标准 Windows .NET Framework compiler directory 下
- **THEN** installer 应编译 `win-shims\taskkill.exe`
- **AND** wrapped launcher 应把 `win-shims` 目录前置到 PATH
- **AND** 它应在该 wrapped 子进程树的 `PATHEXT` 中优先 `.EXE`
- **AND** successful explicit `taskkill.exe` cleanup output 应由 shim 抑制

#### Scenario: Localized successful cleanup output

- **WHEN** 真实 Windows `taskkill.exe` 以 exit code 0 退出，并输出以 `成功: 已终止 PID ` 开头的中文成功行
- **THEN** executable shim 应返回 exit code 0
- **AND** 它不应把这些成功行转发到 stdout 或 stderr

#### Scenario: Cleanup fails

- **WHEN** 真实 Windows `taskkill.exe` 返回非零 exit code
- **THEN** executable shim 应返回相同的非零 exit code
- **AND** 它应把捕获到的诊断输出转发到 stderr