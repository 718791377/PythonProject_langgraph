# Proposal: 硬化 Windows 清理输出控制

## Why

wrapped `codex-ohmy` 会话在 native subagent 或 `/resume` 清理后仍可能把正常的 Windows `taskkill` 成功行泄漏进对话。现有 `taskkill.cmd` shim 覆盖了普通 PATHEXT 查找路径，但这次 subagent 路径说明，部分清理调用方可能绕过该路径，或没有继承预期 shim 行为。

## What Changes

- 硬化现有 Windows cleanup-output control；cleanup-output control 是用于抑制正常清理成功输出、保留失败诊断的控制层，而不是禁用 `omx_*` MCP 工具或避免 native subagent。
- 保持默认 wrapped launch 保守；wrapped launch 是 `codex-ohmy` 调用 native Codex 的托管启动路径，默认继续优先使用 `taskkill.cmd` 处理普通命令查找。
- 增加显式 opt-in 的 `InstallTaskkillExeShim` 安装器开关；该开关用于在确有 direct `.exe` 拦截需求时，从托管 C# shim 源码编译并安装 `taskkill.exe`。
- 扩展生成的 startup launcher；startup launcher 是托管启动器，只有在 opt-in EXE shim 已安装时才增加 `.EXE` PATHEXT 优先级。
- 扩展 checker 和测试；checker 是仓库本地验证脚本，用来覆盖默认 CMD shimming、可选 EXE shimming、受限 PATH/PATHEXT 变更，以及 direct `omx_*` MCP 启动覆盖仍然保留。

不引入破坏性变更。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `codex-user-level-windows-cleanup-output-control`：增加可选 `taskkill.exe` shim 硬化能力，用于覆盖绕过 `taskkill.cmd` 的清理路径，同时保持默认 wrapped launch 保守且作用域受限。

## Impact

- 受影响源码：
  - `tools/install-codex-user-level-team-mode.ps1`：用户级安装器，用来生成托管 wrapper 和 helper assets。
  - `tools/check_windows_cleanup_output_control.py`：Windows cleanup-output control 的仓库 checker。
  - `test/install-codex-user-level-team-mode.test.ps1`：安装器行为测试。
  - `test/check_windows_cleanup_output_control.test.py`：checker 行为测试。
  - `docs_bilingual/implementation_plans/omx_mcp_windows_cleanup_output_control_plan.md` 和 `.zh-CN.md`：本次硬化工作的 implementation plan 双语文件。
  - `openspec/specs/codex-user-level-windows-cleanup-output-control/spec.md` 和 `.zh-CN.md`：同步或归档后的稳定 cleanup-output control 合同。
- 不修改 `C:\Users\lenovo\.codex\config.toml`；这是用户级 Codex 配置文件。
- 不依赖 MCP Router；MCP Router 是跨 IDE 的共享 MCP 聚合器。
- 不改变 native Codex bypass launcher；native Codex bypass launcher 是绕开 wrapper 的原生启动入口。

## Impact Scope

这是 Codex user-level orchestration maintenance 主线下的跨主线维护硬化变更。它影响 Windows wrapped launch 行为和生成的用户级 helper assets，不影响具体业务项目运行面。

## Explicit Non-Goals

- 不禁用 `omx_state`、`omx_memory`、`omx_code_intel` 或 `omx_trace`；这些是 Codex 专用的 oh-my-codex MCP 工具。
- 不要求用户放弃“先进入临时会话，再在 TUI 内 `/resume`”的工作流。
- 不把 Codex 专用 `omx_*` MCP 工具路由进 MCP Router。
- 不全局过滤整个 Codex TUI 输出流。
- 不在没有显式 operator 或 installer opt-in 的情况下默认安装可选 `taskkill.exe` 拦截。

## Rollout Sequence

1. 更新现有 implementation plan 双语文件；implementation plan 是实施计划文件，用来让冷启动会话理解目标和边界。
2. 添加本 OpenSpec change 和 delta spec；OpenSpec change 是仓库内可验证的变更记录。
3. 在本地硬化 installer、checker 和 tests。
4. 只运行本地验证。
5. 本地验证通过后，再由当前会话模型判断是否建议发布 GitLab。
6. GitLab 合并后，如操作者希望新硬化影响未来 `codex-ohmy` 启动，再重新安装用户级 team-mode assets。

## Rollback Plan

- 回滚本仓库变更并重新安装上一版用户级 team-mode assets；user-level team-mode assets 是安装器写入 `C:\Users\lenovo\.codex\bin` 等位置的托管文件。
- 或恢复 `C:\Users\lenovo\.codex\backups` 下的对应托管安装备份；该目录是安装器生成的用户级备份目录。
- 如果 opt-in 路径出现环境特定问题，只删除生成的可选 `taskkill.exe` shim，保留默认 CMD shim 路径。

## Validation Path

- `python test/check_windows_cleanup_output_control.test.py`：验证 cleanup-output checker 行为。
- `powershell -NoProfile -ExecutionPolicy Bypass -File test/install-codex-user-level-team-mode.test.ps1`：验证安装器生成的 wrapped launch 和可选 EXE shim 行为。
- `python tools/check_windows_cleanup_output_control.py --root . --json`：验证 cleanup-output control 源码标记。
- `openspec validate --all`：验证 OpenSpec artifacts。
- `python tools/run_openspec_guard.py --root . --tool codex --json`：运行仓库 guard 检查。
- `git diff --check`：检查补丁格式。

## Mainline Classification

这是 Codex user-level orchestration maintenance 下的既有跨主线维护问题。它硬化既有用户级 Windows cleanup-output capability，不创建新主线。
