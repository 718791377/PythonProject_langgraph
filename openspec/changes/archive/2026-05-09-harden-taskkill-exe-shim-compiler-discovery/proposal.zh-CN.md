## Why

wrapped `codex-ohmy` resume 后仍会暴露本地化 Windows `taskkill` 成功行，因为用户级安装目录缺少生成的 `win-shims\taskkill.exe` shim。installer 已默认请求 explicit `taskkill.exe` 覆盖，但 compiler 发现路径和临时输出路径还不够稳健。

## What Changes

- 加固 user-level team-mode installer：即使 `csc.exe` 不在 PATH 中，也从 Windows Framework compiler 目录编译 `taskkill.exe` cleanup shim。
- 将 compiler stdout/stderr 捕获文件写到 generated shim directory，避免依赖 ambient temp directory。
- 扩展 cleanup-output checker 和测试，覆盖 Framework compiler fallback、本地 compiler temp 文件，以及中文 `taskkill` 成功输出抑制。
- 验证后重新生成/安装 user-level wrapper，让本机实际获得 `win-shims\taskkill.exe`。
- 对已授权的两个 Twilio plugin cache `SKILL.md` metadata 错误做本机热修；这不是仓库 source truth。
- 无 breaking changes。

## Capabilities

### New Capabilities

- 无。

### Modified Capabilities

- `codex-user-level-windows-cleanup-output-control`：explicit `taskkill.exe` shim 要求现在包含稳健 compiler discovery 与本地 compiler 输出捕获，确保默认安装能在普通 Windows 主机上实际生成 executable shim。

## Impact

- 影响源码：`tools/install-codex-user-level-team-mode.ps1`。
- 影响验证：`tools/check_windows_cleanup_output_control.py` 与 `test/check_windows_cleanup_output_control.test.py`。
- 影响本机安装产物：`C:\Users\lenovo\.codex\bin\win-shims\taskkill.exe` 及重新生成的 managed wrappers。
- 影响本机 plugin cache 热修：`C:\Users\lenovo\.codex\plugins\cache\...` 下两个 Twilio Developer Kit `SKILL.md` 文件。

## Required Governance Fields

- impact_scope：用户级 wrapped Codex startup cleanup-output control；本机 Twilio plugin cache metadata warning cleanup。
- explicit_non_goals：不禁用 direct `omx_*` MCP entries；不修改 `C:\Users\lenovo\.codex\config.toml`；不删除 Twilio/browser/Vercel/design skills；不改变 native `codex-raw` 行为。
- rollout_sequence：source patch、focused tests、OpenSpec guard、重新生成 user-level wrapper、修补已授权 Twilio cache、验证安装产物。
- rollback_plan：重跑上一版本 installer 或只移除 generated `win-shims\taskkill.exe`；Twilio cache 可通过 plugin refresh/update 恢复。
- validation_path：cleanup-output focused Python tests、installer compile smoke、repository OpenSpec guard、installed file existence 与 metadata validation。
- mainline_classification：现有当前主线 `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` 下的维护切片。