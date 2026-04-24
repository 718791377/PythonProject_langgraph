## Why

P0 和 P1 已经把用户级状态模型与启动绑定做实了，但日常 `omx team` 操作面仍然过于手工。下一步缺口是把它收敛成一套可跨仓库复用的用户级操作面，在不破坏原生 Codex 基座的前提下，把已经批准的“同构持久团队 + 专家短突发”工作流落成真正可用的入口脚本，而不是继续依赖仓库内零散命令。

## What Changes

- 增加用户级 `omx team` 入口包装脚本，覆盖开发、调试、运维操作、异构编制桥接，以及验收规划。
- 扩展安装器，使其能够把新的入口资产生成到目标 Codex home，并纳入统一备份与回滚。
- 生成用户级 playbook，说明模式含义、包装脚本用法、安全团队生命周期命令，以及 hybrid staffing 的实际落地方式。
- 保持所有包装脚本都是 additive-only，并显式解析真实 `omx` 命令路径，而不是替换或强行覆盖原生 `omx` 可执行入口。
- 明确把“验证/验收”视为 leader 侧原生 subagent 规划面，而不是默认持久 `verifier` pane。
- impact_scope:
  - 安装器 / 生成器
  - 用户级 PowerShell 生成资产
  - 用户级 team-mode 文档
- explicit_non_goals:
  - 不实现 mixed persistent pane compose layer
  - 不改 `cmd.exe` 的 startup binding
  - 不改 OpenClaw runtime 配置
  - 不强推持久 `verifier` pane 模型
- rollout_sequence:
  1. 定义新的用户级 team 入口 capability
  2. 扩展安装器与共享 support script
  3. 在临时 Codex home 中用 fake `omx` 验证包装脚本行为
  4. 仓库验证通过后，再生成到真实用户 home
- rollback_plan:
  - 复用安装器的事务式写入逻辑，把新 wrapper / playbook 路径纳入备份快照与失败回滚
- validation_path:
  - 使用 fake `omx` 的 PowerShell 包装脚本测试
  - `openspec validate --all`
  - `python .\tools\run_openspec_guard.py --root .`
- mainline_classification:
  - 既有主线：Codex / oh-my-codex 用户级 team mode

## Capabilities

### New Capabilities
- `codex-user-level-team-mode-team-entrypoints`: 用户级 `omx team` 包装脚本、hybrid staffing 桥接、验证规划 wrapper，以及生成式 playbook

### Modified Capabilities
- None.

## Impact

- 受影响代码：
  - `tools/install-codex-user-level-team-mode.ps1`
  - `test/install-codex-user-level-team-mode.test.ps1`
  - `openspec/changes/implement-codex-user-level-team-mode-p2-team-entrypoints/`
- 生成到目标 Codex home 的用户级资产：
  - `bin/omx-team-dev.ps1`
  - `bin/omx-team-debug.ps1`
  - `bin/omx-team-verify.ps1`
  - `bin/omx-team-ops.ps1`
  - `bin/omx-team-hybrid.ps1`
  - `docs/team-mode-playbook.md`
- 影响系统：
  - 用户级 PowerShell `omx team` 操作面
  - 新生成资产对应的备份快照与回滚覆盖
