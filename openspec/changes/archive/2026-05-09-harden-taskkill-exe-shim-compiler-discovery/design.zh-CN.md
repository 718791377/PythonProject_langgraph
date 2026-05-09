## Design

### Root cause

泄漏行是本地化 `taskkill` 成功输出。scoped `taskkill.cmd` 与 `taskkill.ps1` shim 能抑制普通 `taskkill` 调用，但 explicit `taskkill.exe` 调用需要 executable shim。当前用户级安装目录没有 `C:\Users\lenovo\.codex\bin\win-shims\taskkill.exe`，所以 native cleanup 仍可能解析到真实 Windows executable。

repository installer 已有 optional executable shim 路径，但默认编译路径仍有两个脆弱点：

- `csc.exe` 可能在 `C:\Windows\Microsoft.NET\Framework64\...` 或 `Framework\...` 下存在，但不在 PATH。
- compiler stdout/stderr 捕获使用 ambient temp directory；在 constrained/sandboxed 执行中，即使 generated shim directory 可写，也可能失败。

### Approach

保持现有 scoped wrapper 设计，只让 executable shim 默认更可靠地可用：

1. 先从 PATH 解析 compiler，再从 Framework64 与 Framework Windows 目录解析。
2. 使用 generated shim directory 下的唯一文件名捕获 compiler stdout/stderr。
3. 保持 executable shim 语义不变：exit code 0 时完全抑制 stdout/stderr；非零 exit 时转发捕获诊断并返回原始 exit code。
4. 扩展 checker，增加 compiler fallback、本地 compiler temp 文件和 success-output suppression source markers。
5. 增加对操作者报告的中文成功行类别的回归覆盖。

### Local plugin cache hotfix

Twilio cache patch 是战术性本机修补：

- `twilio-agent-connect` 补 missing YAML frontmatter。
- `twilio-enterprise-knowledge` 保持正文不变，只把 frontmatter description 缩短到 loader limit 以内。

这些文件是 plugin-managed cache artifacts，持久修复仍应来自上游/plugin refresh；本 change 只消除当前本机 startup warning noise。

### Risks

- Executable shim generation 依赖本机 Windows C# compiler。如果 PATH 和 Framework compiler locations 都不存在，installer 仍会报告 shim unavailable 并回退到 cmd/ps1 shim。
- Plugin cache edits 可能被 plugin update 覆盖。