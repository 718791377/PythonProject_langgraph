# OMX MCP Windows 清理输出控制实施计划

## 状态

- 阶段：active follow-up implementation，表示这是当前可实施的后续修复任务。
- 主线：Codex user-level orchestration maintenance，表示这是用户级 Codex 编排维护工作。
- OpenSpec change：`harden-windows-cleanup-output-control`，这是用于硬化 direct `omx_*` MCP 工作流，并在 wrapped launch 与 subagent cleanup 路径中抑制正常 Windows cleanup 输出的变更。

## 问题

操作者希望先运行 `codex-ohmy`，进入一个临时 Codex TUI 会话，然后在该临时会话里使用 `/resume` 继续旧会话。`codex-ohmy` 是用户级包装入口，用于启用 oh-my-codex、native subagent、native_omx 和 LangGraph 相关用户级策略。`/resume` 是 Codex TUI 内部恢复旧会话的命令。

当 `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace` 启用时，`/resume` 路径可能会清理临时会话的 Windows 子进程，并把正常的 Windows `taskkill` 成功输出写进对话。`taskkill` 是 Windows 自带的进程终止命令；成功输出不是功能错误，但会污染会话上下文，也会影响后续冷启动恢复判断。

## 目标

- 保持 `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace` 在 `codex-ohmy` full mode 中启用；这些是 Codex 专用的 oh-my-codex MCP 工具。
- 保持“先进入临时会话，再在 TUI 内 `/resume`”的工作流；这避免强制操作者改用直接 resume-first 命令。
- 抑制正常成功的 `taskkill` 输出；这些输出包括英文 `SUCCESS: The process with PID ... has been terminated.` 和中文“成功: 已终止 PID ... 的进程。”。
- 保留 cleanup 失败和非零退出诊断；如果真实清理失败，仍应把错误输出到 stderr。
- 将所有 PATH 或 shim 变更限定在 wrapped launch 内；wrapped launch 指 `codex-ohmy` 调用 native Codex 的这一次子进程树。
- 不修改 `C:\Users\lenovo\.codex\config.toml`；这是用户级 Codex 配置文件，应由操作者控制。

## 非目标

- 不把禁用 `omx_*` MCP 工具作为长期修复；这会损失 subagent / omx / langgraph 长期能力。
- 不要求 `codex-ohmy resume <session-id>` 成为唯一恢复路径；该命令是直接以 session id 启动恢复的替代入口。
- 不把 `omx_*` MCP 工具迁移进 MCP Router；MCP Router 是跨 IDE 的共享 MCP 聚合器，不应托管 Codex 专属 `omx_*` 工具。
- 不过滤整个 Codex TUI 交互流；全局过滤可能破坏交互式终端行为。
- 不宣称最终的个人生产级持久化团队已经完成；本计划只是生产硬化步骤。

## 实施步骤

1. 添加 OpenSpec artifacts；OpenSpec artifacts 是 proposal、design、tasks 和 delta spec，用来定义 cleanup-output control 合同。
2. 在 `tools/install-codex-user-level-team-mode.ps1` 中添加 `win-shims` 生成逻辑；该脚本是用户级安装器，用来写入托管 launcher 和 helper 脚本。
3. 生成 `taskkill.cmd`、`taskkill.ps1` 和 `taskkill-shim-source.cs`；这些文件分别是 CMD shim、PowerShell shim 和可选 C# shim 源码，用来调用真实 `taskkill.exe` 并抑制成功输出。
4. 添加 `InstallTaskkillExeShim` 安装器开关；该开关只在证据显示调用方绕过 PATHEXT 并直接执行 `.exe` 路径时，才编译并安装 `taskkill.exe` shim。
5. 保持默认路径保守；默认 wrapped launch 只优先使用 `taskkill.cmd`，只有显式 opt-in 后 wrapped launch 才同时优先使用 `taskkill.exe`。
6. 更新生成的 startup launcher；startup launcher 是 `codex-ohmy` 间接调用 native Codex 的托管脚本，它只在调用 native Codex 期间把 `win-shims` 放到 PATH 前面，并在 `finally` 中恢复 PATH 和 PATHEXT。
7. 添加 `tools/check_windows_cleanup_output_control.py`；这是仓库 checker，用来验证 shim 生成、可选 EXE 控制、PATH 恢复和 `omx_*` MCP 启用覆盖没有被破坏。
8. 添加安装器测试和 checker 测试；测试应覆盖默认非 EXE 模式、显式 EXE opt-in、生成文件、manifest 输出、wrapped launch PATH 作用域以及 native bypass 不受影响。
9. 运行验证并通过 local-main-first integration package 发布；local-main-first integration package 是本仓库默认的评审和合并流程。

## 验证

- `powershell -NoProfile -ExecutionPolicy Bypass -File test/install-codex-user-level-team-mode.test.ps1`：验证安装器生成的 launcher、helper 和 shim。
- `python test/check_windows_cleanup_output_control.test.py`：验证 cleanup-output control checker。
- `python tools/check_windows_cleanup_output_control.py --root . --json`：直接运行 cleanup-output control checker 并输出 JSON。
- `openspec validate --all`：验证全部 OpenSpec artifacts。
- `python tools/run_openspec_guard.py --root . --tool codex --json`：运行仓库总 guard。
- `git diff --check`：检查补丁格式是否存在空白错误。

## 回滚

- 回滚本仓库变更并重新安装用户级 team-mode assets；用户级 team-mode assets 是安装器写入 `C:\Users\lenovo\.codex\bin` 等位置的托管文件。
- 或恢复 `C:\Users\lenovo\.codex\backups` 下的安装器备份；该目录是托管安装产生的用户级备份目录。
- 不需要回滚 MCP Router 状态，因为本计划不使用 MCP Router。
