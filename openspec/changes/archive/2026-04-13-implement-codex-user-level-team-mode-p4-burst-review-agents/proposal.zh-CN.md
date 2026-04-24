## Why

P3 已经把角色路由阈值做成了可检查的策略面，但“最强执行闭环”里最关键的一条支路还没有真正落地：`bug-finder`、`bug-rebutter`、`bug-judge` 目前仍然只是文档中的路由概念，还不是可真实调用的用户级角色。

下一步要补上的缺口，是把这套对抗式缺陷审查流变成可安装、可回滚、可验证的用户级 agent 资产，让 Codex CLI 在阈值命中时可以真正路由进去，而不是只停留在说明文字里。

## What Changes

- 生成以下增量式用户级 agent 配置：
  - `agents/bug-finder.toml`
  - `agents/bug-rebutter.toml`
  - `agents/bug-judge.toml`
- 扩展生成出来的 routing policy 检查面，使其把 burst-review 角色描述为“可调用的已生成资产”，而不只是抽象名称。
- 更新生成的 `team-leader.toml` 与 `docs/team-mode-playbook.md`，明确这三个角色是 leader 侧可调用的短突发专家角色。
- 将这三份新 agent 文件纳入现有的备份快照与失败回滚事务。
- 扩展 PowerShell 安装器测试，验证生成、备份清单覆盖、失败回滚，以及 routing policy 对 burst-review 角色的可见性。
- impact_scope:
  - 安装器 / 生成器
  - 生成出来的用户级 agent 资产
  - 生成出来的 routing-policy 输出
  - 生成出来的 leader profile 与 playbook
  - 包装层验证测试
- explicit_non_goals:
  - 不实现 mixed persistent pane compose 层
  - 不在普通 `codex` 启动时自动拉起 burst-review 角色
  - 不实现持久化 bug-review swarm
  - 不替换原生 `codex` 或原生 `omx`
  - 不修改 OpenClaw runtime 配置
- rollout_sequence:
  1. 定义 burst-review 角色 capability 和 routing-policy 增量 spec
  2. 扩展安装器，生成 burst-review agent profiles
  3. 扩展共享 support script、leader profile 和 playbook，补上可调用 burst-role 元数据
  4. 在临时 Codex home 中验证生成与回滚
  5. 仅在仓库验证通过后，再重装到真实用户目录
- rollback_plan:
  - 复用现有安装事务，使新增 agent 文件和更新后的生成资产在失败时都能恢复
- validation_path:
  - 使用 fake native Codex 与 fake `omx` 的 PowerShell 安装器测试
  - 真实用户级 `omx agents list --scope user`
  - `openspec validate --all`
  - `python .\tools\run_openspec_guard.py --root .`
- mainline_classification:
  - 既有主线：Codex / oh-my-codex 用户级团队模式

## Capabilities

### New Capabilities

- `codex-user-level-team-mode-burst-review-agents`：为 leader 侧对抗式审查短突发流程生成 `bug-finder`、`bug-rebutter`、`bug-judge` 用户级角色配置

### Modified Capabilities

- `codex-user-level-team-mode-routing-thresholds`：当 burst-review 角色已安装时，routing-policy 输出与生成文档必须把它们描述为真实可调用的已生成角色

## Impact

- 受影响代码：
  - `tools/install-codex-user-level-team-mode.ps1`
  - `test/install-codex-user-level-team-mode.test.ps1`
  - `openspec/changes/implement-codex-user-level-team-mode-p4-burst-review-agents/`
- 目标 Codex home 下新增 / 更新的用户级资产：
  - `agents/bug-finder.toml`
  - `agents/bug-rebutter.toml`
  - `agents/bug-judge.toml`
  - `bin/_codex-user-level-team-mode.ps1`
  - `bin/codex-routing-policy.ps1`
  - `agents/team-leader.toml`
  - `docs/team-mode-playbook.md`
- 系统影响：
  - wrapped `codex` 会话可用的用户级 burst-review 角色
  - 面向操作者的 routing-policy 检查面
  - 新增生成 agent 资产的备份快照与失败回滚覆盖
