# Design: 硬化 Windows 清理输出控制

## Context

仓库已经为 wrapped `codex-ohmy` launch 生成受限 `win-shims` 目录。`win-shims` 是托管 shim 目录，用来在 native Codex 运行期间临时覆盖命令查找路径。launcher 会在 native Codex 运行期间把该目录放到 PATH 前面，然后恢复 PATH 和 PATHEXT。生成的 `taskkill.cmd` 和 `taskkill.ps1` shim 会抑制 Windows `taskkill` 成功输出，同时保留非零退出诊断。

最近仍然观察到 native subagent 或 `/resume` cleanup 后有输出泄漏。这说明当前 CMD shim 是必要的，但不足以覆盖所有 cleanup path。最可能的瓶颈是命令解析：某些 cleanup 调用方可能显式调用 `taskkill.exe`，可能不使用 PATHEXT 查找，或者在比初始 wrapped process 更窄的环境中启动。

相关方：

- 操作者：需要干净对话和 error-only cleanup diagnostics。
- main Codex session：主会话保持 leader 角色，不能丢失 `omx_*` MCP 工具。
- native subagent 和 `/resume` 路径：这些路径可能启动并清理 Windows 子进程树。
- future installers：后续安装器必须保留 native Codex bypass 行为，并避免修改 `config.toml`。

## Goals / Non-Goals

**Goals:**

- 保持默认 cleanup-output control 受限且保守。
- 保留 direct `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace` MCP 可用性。
- 增加显式 opt-in 的 `.exe` 级 `taskkill` 拦截路径，用于证据显示 CMD shimming 被绕过的情况。
- 让 opt-in 路径具备脚本控制、测试覆盖，并出现在安装器 JSON 输出中。
- 通过现有 managed installer backup 保持回滚安全。

**Non-Goals:**

- 不全局过滤 Codex TUI 输出。
- 不通过禁用 native subagents、omx、LangGraph 或 MCP 工具来隐藏日志。
- 不把 Codex 专用 MCP 工具迁移进 MCP Router。
- 不默认安装 `taskkill.exe` 拦截。
- 不编辑用户级 `config.toml`。

## Decisions

### Decision 1: 默认保留 CMD shimming

默认 wrapped launch 继续通过 PATH/PATHEXT 优先使用 `taskkill.cmd`。这让既有行为保持最小化，并避免让不需要的环境看到 shadow `taskkill.exe`。

备选方案：始终安装 `taskkill.exe`。拒绝原因：可执行文件 shadowing 比 CMD 命令查找影响更广，必须显式 opt-in。

### Decision 2: 增加 opt-in `InstallTaskkillExeShim` 开关

安装器增加显式 `InstallTaskkillExeShim` 开关。启用后，安装器会把托管 C# shim 源码编译为 `win-shims\taskkill.exe`，在 JSON 中报告编译结果，并让生成的 launcher 在 wrapped child process tree 内优先 `.EXE` PATHEXT。

备选方案：在仓库中提交预编译二进制。拒绝原因：仓库应保持 source-first，不提交本地二进制构建产物。

### Decision 3: 安装时从托管 C# 源码编译

现有 `taskkill-shim-source.cs` 继续作为 executable shim 的源码权威。安装器尝试从 PATH 或 Windows .NET Framework 目录查找 `csc.exe`，如果显式请求 EXE shim 但无法编译，则快速失败并报告原因。

备选方案：找不到 compiler 时静默跳过 EXE shim。拒绝原因：显式 opt-in 应该确定且可见。

### Decision 4: `.EXE` PATHEXT 变更仅限 wrapped launch

生成的 startup launcher 只有在 opt-in EXE shim 启用时才把 `.EXE` 放到 PATHEXT 前面。和现有 CMD shim 一样，PATH/PATHEXT 会在 `finally` 中恢复。

备选方案：修改用户 shell profile 或全局 PATH。拒绝原因：cleanup-output control 不应泄漏到其他终端或项目。

### Decision 5: 强化 checker 证据

checker 必须验证可选 EXE 开关、编译函数、报告字段和受限 PATHEXT 行为标记。这把安全规则变成脚本控制，而不是提示词提醒。

备选方案：只依赖安装器测试。拒绝原因：仓库 guard 需要快速静态合同检查。

## Risks / Trade-offs

- [Risk] 某个 cleanup path 直接调用绝对路径 `C:\Windows\System32\taskkill.exe`。→ Mitigation：本次变更覆盖 command-name 和 PATHEXT 拦截；绝对路径拦截仍属于上游或调用方特定调查，不做全局替换。
- [Risk] 目标 Windows 机器没有 `csc.exe`。→ Mitigation：默认行为不需要编译；显式 EXE opt-in 会用清晰原因失败。
- [Risk] `.EXE` PATHEXT 优先级可能影响无关子命令。→ Mitigation：只在显式开关启用时生效，并且只在 wrapped native Codex 子进程树内生效。
- [Risk] 可选 EXE shim 可能掩盖真实 cleanup failure。→ Mitigation：shim 只抑制零退出成功输出，并把非零诊断转发到 stderr。

## Migration Plan

1. 合入仓库源码、测试和 OpenSpec 更新。
2. 运行本地验证。
3. 仅在本地验证通过且模型向用户建议发布时，通过 GitLab-first MR 发布。
4. 合并后，正常重新安装用户级 team-mode assets，以保留默认 CMD shimming。
5. 如果 PID 成功行仍出现，再使用显式 `InstallTaskkillExeShim` 开关重新运行安装器，并验证可选 `taskkill.exe` shim 是否移除剩余泄漏。

## Open Questions

- native Codex subagent cleanup 是按 command name 调用 `taskkill.exe`、按 PATHEXT 解析调用，还是使用绝对系统路径？本变更覆盖 command-name 和 PATHEXT 拦截；绝对路径拦截仍需要上游或调用方专项调查。
- 后续是否需要增加 diagnostic mode，记录 cleanup command path 的解析结果但不打印到 Codex 对话？这有价值，但不是当前硬化必需项。
