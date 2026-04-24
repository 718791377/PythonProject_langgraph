## Why

P2 已经把用户级 team 入口做成了真实可用的脚本，但 leader 侧的角色路由策略仍然过于隐式。下一步缺口是把“自动角色路由阈值”做成可复用、可检查的用户级能力层：既保持原生 Codex 为基础路径，又把包装 `codex` 的启动行为写实，并让普通项目在不依赖仓库私有胶水的情况下复用同一套专家角色选择规则。

## What Changes

- 在生成的 shared support script 中加入统一的用户级 routing-policy 模型。
- 生成用户级 `codex-routing-policy.ps1` 检查入口。
- 让启动器从 routing-policy 模型派生 developer instructions，而不再只使用简短硬编码摘要。
- 扩展生成的 `team-leader.toml` 与 `docs/team-mode-playbook.md`，补入角色路由阈值、研究到实现交接规则、对抗式 bug 评审规则、启动路径语义，以及仓库级运行态隔离说明。
- 让新的 routing-policy 资产继续落在现有 additive-only 备份快照与回滚事务之内。
- 扩展 PowerShell 测试，覆盖 `auto / manual / off` 三种 routing 状态下的 routing-policy 输出与 developer-instructions 注入。
- impact_scope:
  - 安装器 / 生成器
  - 生成的用户级 PowerShell 资产
  - 生成的用户级 leader profile 与 playbook
  - wrapper 验证测试
- explicit_non_goals:
  - 不引入新的持久 pane compose 层
  - 不在每次执行 `codex` 时自动拉起 durable team
  - 不把全局开关改成项目级
  - 不修改 OpenClaw 运行时配置
- rollout_sequence:
  1. 定义 routing-threshold capability 与检查入口
  2. 扩展 shared support script 与启动器生成逻辑
  3. 扩展生成的 leader/profile 与 playbook
  4. 在临时 Codex home 中验证 policy 输出与 developer-instructions 注入
  5. 只有仓库校验通过后才重新安装到真实用户 home
- rollback_plan:
  - 复用现有安装事务，确保新的 routing-policy 脚本及更新后的生成资产在失败时被恢复
- validation_path:
  - 使用 fake native Codex 和 fake `omx` 的 PowerShell 安装器测试
  - `openspec validate --all`
  - `python .\tools\run_openspec_guard.py --root .`
- mainline_classification:
  - existing mainline: Codex / oh-my-codex user-level team mode

## Capabilities

### New Capabilities
- `codex-user-level-team-mode-routing-thresholds`: 可检查的 routing policy、基于启动模式的 developer-instructions 生成、以及面向角色路由阈值的 leader/playbook 更新

### Modified Capabilities
- None.

## Impact

- Affected code:
  - `tools/install-codex-user-level-team-mode.ps1`
  - `test/install-codex-user-level-team-mode.test.ps1`
  - `openspec/changes/implement-codex-user-level-team-mode-p3-routing-thresholds/`
- 目标 Codex home 下生成的用户级资产：
  - `bin/codex-routing-policy.ps1`
  - `bin/_codex-user-level-team-mode.ps1`
  - `bin/_codex-user-level-team-mode-launcher.ps1`
  - `agents/team-leader.toml`
  - `docs/team-mode-playbook.md`
- Systems:
  - 包装 `codex` 的用户级启动行为
  - 面向操作者可见的 routing-policy 检查面
  - 用户级角色路由文档与验证
