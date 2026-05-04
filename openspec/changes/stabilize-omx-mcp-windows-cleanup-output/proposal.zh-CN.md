## 原因

`codex-ohmy` 保持 Codex 用户级编排层可用，包括 `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace`。这些 `omx_*` MCP 工具是 Codex 专用的 oh-my-codex 状态、记忆、代码索引和追踪工具。

当前 Windows cleanup 路径可能会在操作者先进入临时 Codex TUI 会话、再使用 `/resume` 时，把正常的 `taskkill` 成功行泄漏到对话中。`taskkill` 是 Windows 自带的进程终止命令；这些成功行本身不是错误，但会污染上下文，并让长期个人持久化团队工作流变得嘈杂。

## 变更内容

- 添加一个托管的 Windows cleanup-output control layer；该层用于 `codex-ohmy` wrapped launch，并抑制正常 `taskkill` 成功输出，同时保留错误。
- 保持 `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace` 在完整 `codex-ohmy` 会话中启用。
- 保留操作者工作流：先启动 `codex-ohmy` 进入临时会话，再在该临时会话内使用 `/resume`。
- 添加脚本化验证，避免未来 launcher 或 helper 变更重新引入可见的正常 Windows cleanup 噪声。
- 不切换到 MCP Router，也不要求直接使用 `codex-ohmy resume <session-id>` 作为唯一入口。

## 能力

### 新增能力

- `codex-user-level-windows-cleanup-output-control`：定义用户级 Codex 编排启动时的 Windows cleanup 成功输出抑制，并保留 direct Codex MCP 工具。

### 修改能力

- `codex-user-level-team-mode-startup-binding`：startup-binding launcher 获得 scoped cleanup-output quiet layer，用于 wrapped `codex-ohmy` launch。
- `codex-user-level-mcp-scope-policy`：策略澄清 Codex-private `omx_*` MCP server 应保持 direct 和 enabled，cleanup 噪声由单独的 cleanup-output control 处理。

## 影响

影响范围：

- `docs_bilingual/implementation_plans/omx_mcp_windows_cleanup_output_control_plan.md`：cleanup-output control rollout 的 ASCII 主版计划。
- `docs_bilingual/implementation_plans/omx_mcp_windows_cleanup_output_control_plan.zh-CN.md`：同一 rollout 的 UTF-8 中文对照计划。
- `tools/install-codex-user-level-team-mode.ps1`：用户级安装器和生成的 `codex-ohmy` launcher 源；它会安装 scoped Windows cleanup shim，并只对 wrapped launch 预置 PATH。
- `tools/check_windows_cleanup_output_control.py`：仓库 checker，用来验证托管 cleanup-output control 合同。
- `test/install-codex-user-level-team-mode.test.ps1`：安装器测试，覆盖生成 shim 文件和 launcher PATH 作用域。
- `test/check_windows_cleanup_output_control.test.py`：checker 测试，覆盖必要的源码和 artifact 证据。

明确非目标：

- 不把禁用 `omx_state`、`omx_memory`、`omx_code_intel` 或 `omx_trace` 作为长期修复。
- 不把 `codex-ohmy resume <session-id>` 变成唯一支持的恢复路径。
- 不通过 MCP Router 路由 Codex-private `omx_*` MCP server。
- 不编辑 `C:\Users\lenovo\.codex\config.toml`；该文件是用户级 Codex 配置文件，由操作者控制。
- 不抑制可执行的 cleanup 错误、非零退出、认证失败或堆栈跟踪。

发布顺序：

1. 添加本 OpenSpec change 和双语 implementation plan。
2. 添加托管 cleanup shim 生成和 wrapped-launch PATH 作用域控制。
3. 添加 checker 和测试。
4. 通过安装器测试、checker 测试和 OpenSpec guard 完成本地验证。
5. 通过 GitLab-first MR 流程发布，并在 GitLab main 绿色后同步 GitHub。
6. 合并后运行用户级安装器，更新操作者机器上的 `C:\Users\lenovo\.codex\bin`。

回滚计划：

- 重新运行现有安装器回滚路径，或从 `C:\Users\lenovo\.codex\backups` 下的时间戳备份恢复。
- 如需移除 scoped shim 目录，只能通过回滚仓库变更并重新安装来移除生成的 `codex-ohmy` launcher PATH 逻辑。
- 不需要回滚 repository durable state 或 MCP Router state。

验证路径：

- `powershell -NoProfile -ExecutionPolicy Bypass -File test/install-codex-user-level-team-mode.test.ps1`：验证生成的 launcher、安装器输出和回滚行为。
- `python test/check_windows_cleanup_output_control.test.py`：验证 checker 行为。
- `python tools/check_windows_cleanup_output_control.py --root . --json`：直接检查仓库合同。
- `openspec validate --all`：验证 OpenSpec artifacts。
- `python tools/run_openspec_guard.py --root . --tool codex --json`：运行仓库 OpenSpec guard。
- `git diff --check`：检查补丁格式。

主线分类：

- 这是当前 active team-mode 和 cross-session durable-state isolation 计划下的用户级编排维护；它是面向未来个人生产级持久化团队目标的生产硬化步骤，不宣称最终生产级团队已经完成。
