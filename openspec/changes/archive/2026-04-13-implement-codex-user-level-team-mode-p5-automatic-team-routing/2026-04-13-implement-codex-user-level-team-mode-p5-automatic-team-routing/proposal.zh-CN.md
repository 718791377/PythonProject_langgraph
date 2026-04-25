## Why

P0 到 P4 已经把包装启动、专家路由阈值、`omx team` 入口层和 burst-review 角色做成了真实能力，但 durable `omx team` 的使用仍然过于手动。P5 要补上的就是最后一段闭环：让增强模式下的 Codex 会话能够按阈值决定何时只用原生 subagent，何时启动或复用 durable team，何时切换或停止它，同时不破坏原生 Codex。

## What Changes

- 增加一个自动 durable-team 路由 helper，可针对当前仓库输出或执行 `launch`、`reuse`、`switch`、`shutdown`、`no-team` 决策。
- 扩展共享的用户级 runtime，让 routing policy 以结构化形式暴露 durable-team 阶段映射、阈值、tracked-team 规则和 helper 路径。
- 扩展生成的 leader/playbook 指南，让包装后的 Codex 会话知道什么时候优先使用原生 subagent，什么时候优先走 durable-team helper。
- 保持 durable-team helper additive-only、仓库级隔离、默认安全：不自动接管未知的 unmanaged team，不破坏原生 Codex 启动路径。
- 保持启动语义不变：包装后的 `codex` 启动本身仍然不会在每次启动时自动拉起 durable team；只有在 leader 判断阈值满足后，才会在会话内稍后启动。
- impact_scope:
  - installer/generator
  - 生成的用户级 PowerShell 资产
  - 生成的 leader/playbook 指南
  - 仓库级 `.omx` tracked team 元数据
- explicit_non_goals:
  - 不修改原生 `codex.cmd` 或原生 `omx.cmd`
  - 不在每次 `codex` 启动时强制启动 durable team
  - 不自动接管未知的 unmanaged team
  - 不修改 OpenClaw runtime 配置
- rollout_sequence:
  1. 定义自动 durable-team 路由 capability 与 spec delta
  2. 扩展 installer 与 shared runtime，加入新 helper 和 tracked-team 模型
  3. 在临时 Codex home 中通过 fake `omx` 验证 launch、reuse、switch、shutdown
  4. 只有仓库验证通过后，才重新部署到真实用户目录
- rollback_plan:
  - 将新 helper 与 tracked-team 相关资产纳入现有 installer 备份与回滚事务
  - 安装失败时，从 snapshot 恢复之前的用户级状态与生成资产
- validation_path:
  - 使用 fake `omx` 的 PowerShell wrapper 测试
  - `openspec validate --all`
  - `python .\tools\run_openspec_guard.py --root .`
- mainline_classification:
  - existing mainline: Codex / oh-my-codex user-level team mode

## Capabilities

### New Capabilities
- `codex-user-level-team-mode-automatic-team-routing`：自动 durable-team 路由 helper、tracked-team 元数据，以及仓库安全的 launch / reuse / switch / shutdown 行为

### Modified Capabilities
- `codex-user-level-team-mode-routing-thresholds`：routing policy 与 developer instructions 现在要暴露 durable-team 自动路由规则和 helper 用法
- `codex-user-level-team-mode-team-entrypoints`：生成的用户级 team entrypoints 现在要包含自动 durable-team 路由 helper

## Impact

- Affected code:
  - `tools/install-codex-user-level-team-mode.ps1`
  - `test/install-codex-user-level-team-mode.test.ps1`
  - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md`
  - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md`
  - `openspec/changes/implement-codex-user-level-team-mode-p5-automatic-team-routing/`
- 目标 Codex home 下生成的用户级资产：
  - `bin/omx-team-auto.ps1`
  - `bin/codex-routing-policy.ps1`
  - `agents/team-leader.toml`
  - `docs/team-mode-playbook.md`
- 仓库级 runtime 状态：
  - `.omx/state/team/codex-auto-managed-team.json`
- Systems:
  - enhanced auto mode 下的包装 Codex 启动指导
  - 跨仓库 durable-team 启动、复用、切换与停止协调
