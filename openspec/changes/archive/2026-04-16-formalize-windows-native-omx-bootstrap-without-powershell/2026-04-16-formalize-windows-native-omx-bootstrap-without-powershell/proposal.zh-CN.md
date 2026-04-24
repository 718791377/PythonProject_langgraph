## Why

在用户级 capability-switch 模型下，`native_omx` lane 现在已经能被正确选中，但它的成功仍然依赖我对全局安装 `oh-my-codex` runtime 做的一次手工热修。当前上游 Windows worker bootstrap 仍使用 `spawnSync('powershell.exe', ...)`，而在这个环境里，Node 无法拉起 `powershell.exe` 或 `cmd.exe`，会直接得到 `EPERM`。所以这次修复必须被正式化为 repo-managed、可重复应用、可升级后恢复的方案，而不能继续停留在一次性全局 patch。

## What Changes

- 把 Windows 原生 `omx` prompt-worker bootstrap 修复正式化，不再依赖 `powershell.exe`
- 把受支持的 Windows bootstrap contract 定义为“直接使用 Node 启动 worker-controller”，而不是“通过 PowerShell 中介创建进程”
- 定义仓库在全局 `oh-my-codex` runtime 升级后，如何重新安装、重打补丁或验证这条修复
- 增加回归验证，能明确区分“旧的 PowerShell-blocked 路径”和“修复后的 Node bootstrap 路径”

## Capabilities

### New Capabilities
- `codex-user-level-windows-native-omx-bootstrap-fix`: 为原生 `omx` prompt workers 提供一个绕开 PowerShell controller 启动的 repo-managed Windows bootstrap 修复路径

### Modified Capabilities
- `codex-user-level-team-mode-windows-native-team-backend`: 细化 Windows backend contract，要求 prompt-worker bootstrap 不再依赖 `powershell.exe`
- `codex-user-level-team-mode-automatic-team-routing`: 确保在正式化修复之后，worker-centric 的 native_omx launch 仍然有效

## Impact

- impact_scope:
  - 面向全局安装 `oh-my-codex` runtime 的 repo-managed repair 文档和/或脚本
  - Windows 原生 `native_omx` bootstrap 行为
  - worker-centric durable launch 的用户级验证
- explicit_non_goals:
  - 不引入新的 backend family
  - 不移除 LangGraph 支持
  - 不重构当前用户级 capability-switch 模型
- rollout_sequence:
  - 先定义正式的 Windows bootstrap repair contract
  - 再决定这条 repo-managed repair 应该放在仓库的什么位置
  - 再验证 worker-centric native_omx launch 能在没有 PowerShell bootstrap 的情况下成功
  - 最后把 upgrade/reinstall 后的可恢复性写清楚
- rollback_plan:
  - 如果修复后的 bootstrap path 失败，就恢复之前备份的全局 runtime 文件
  - 保持 repo-managed repair assets 可回滚
- validation_path:
  - 先验证旧的 PowerShell bootstrap 确实会复现 EPERM
  - 再验证修复后的 Node bootstrap path 能成功启动 native_omx team
  - 运行 `openspec validate --all`
- mainline_classification:
  - 现有主线延续
  - 具体属于用户级 Windows native_omx bootstrap 的强化与正式化
