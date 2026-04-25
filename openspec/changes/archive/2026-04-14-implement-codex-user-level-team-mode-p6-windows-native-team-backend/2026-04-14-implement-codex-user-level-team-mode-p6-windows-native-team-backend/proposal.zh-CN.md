## Why

P5 已经完成了自动 durable-team 路由层，但 native Windows 下真实执行 `omx team -Apply` 仍然被运行时挡住，因为当前 runtime 还依赖 `tmux`。所以下一批不是继续改路由策略，而是补一个原生 Windows durable-team backend，让现有用户级 team-mode surface 在不依赖 WSL2 的前提下真正跑起来。

## What Changes

- 为 `omx team` 增加原生 Windows durable-team backend，让 worker launch、status、await、resume、shutdown 在无 WSL2、无 Unix `tmux` 的条件下可运行。
- 保留现有 Unix `tmux` 路径作为独立 backend，而不是替换它。
- 保持 repo-local `.omx/state/team/...` 的状态、mailbox、heartbeat、worktree 合同在不同 backend 间一致。
- 让 `omx-team-dev.ps1`、`omx-team-debug.ps1`、`omx-team-auto.ps1` 等生成 wrapper 保持 backend-neutral，在 Windows backend 存在后直接可用。
- 保持原生 Codex 基座不变，并保持当前用户级备份与回滚模型不变。
- impact_scope:
  - oh-my-codex team runtime
  - 用户级 team-mode wrapper 与 policy guidance
  - Windows 专属 durable worker 生命周期
- explicit_non_goals:
  - 不依赖 WSL2
  - 不替换 native `codex.cmd` 或 native `omx.cmd`
  - 不把 mixed persistent pane compose 作为默认形态
  - 不把 GUI pane 自动化作为第一版实现策略
- rollout_sequence:
  1. 定义 Windows backend 合同与验收面
  2. 在 `omx team` 下增加 backend abstraction
  3. 实现原生 Windows durable-team backend
  4. 验证 launch、status、await、resume、shutdown 与 `omx-team-auto.ps1 -Apply`
- rollback_plan:
  - 保持用户级 wrapper surface 可通过现有 installer backup snapshot 回滚
  - 保持 runtime backend 变化隔离，不影响 native Codex 与非 team 路径
- validation_path:
  - backend 专项 runtime 测试
  - native Windows 下的用户级 wrapper 验证
  - `openspec validate --all`
  - `python .\tools\run_openspec_guard.py --root .`
- mainline_classification:
  - existing mainline: Codex / oh-my-codex user-level team mode

## Capabilities

### New Capabilities
- `codex-user-level-team-mode-windows-native-team-backend`：`omx team` 的原生 Windows durable-team backend 合同

### Modified Capabilities
- `codex-user-level-team-mode-team-entrypoints`：生成的 team entrypoint wrapper 必须能在 native Windows 下工作，而不能继续默认假设 Unix `tmux`
- `codex-user-level-team-mode-automatic-team-routing`：一旦 Windows backend 存在，`omx-team-auto.ps1 -Apply` 必须能在 native Windows 下真正执行 tracked durable-team 决策

## Impact

- Affected code:
  - oh-my-codex runtime team backend 实现
  - `tools/install-codex-user-level-team-mode.ps1`
  - `test/install-codex-user-level-team-mode.test.ps1`
  - `openspec/changes/implement-codex-user-level-team-mode-p6-windows-native-team-backend/`
- Systems:
  - native Windows durable team runtime
  - repo-local `.omx` team state 生命周期
  - native Windows 下的 `omx-team-auto.ps1 -Apply`
