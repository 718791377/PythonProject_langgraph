## Why

仓库当前采用 GitLab-first 发布流程，但如果远端 CI 配置自己写一套命令逻辑，本地检查和远端检查可能漂移。用户希望同时保留本地 CI、本地 MR 审查、远端 CI 和远端 MR 审查，并尽量避免本地与远端格式或规则不一致。

## What Changes

- 采用 local-first + mirrored CI/MR gate 发布姿态。
- 新增 `tools/ci/local_gate.ps1`，作为本地和远端 CI 复用的统一入口。
- 新增 `tools/ci/local_mr_review.ps1`，作为本地 MR review summary 和 merge simulation 入口。
- 更新 GitLab CI 和 GitHub workflow，使远端 job 调用同一个 local gate 脚本，而不是在 CI 配置里重复写 OpenSpec guard 命令。
- 更新 startup 和 worktree governance 文档，要求推送远端 MR 工作前先完成本地 CI 和本地 MR review。

## Capabilities

### New Capabilities

- `codex-repository-multi-session-worktree-isolation`：增加 mirrored local/remote CI and MR gate 发布契约。

### Modified Capabilities

- 无。

## Impact

- impact_scope：`AGENTS.md`、启动摘要、worktree governance policy、CI 配置、本地 CI/MR 脚本，以及本 OpenSpec change。
- explicit_non_goals：不移除 GitLab MR review，不移除 GitLab CI，不默认使用 GitHub PR，不执行用户级 launcher 安装，不写 durable state。
- rollout_sequence：新增 local gate 脚本，让远端 CI 调用同一脚本，更新治理文本，本地验证，然后按现有远端 MR 流程发布。
- rollback_plan：回滚本 change，恢复直接 CI 命令和之前 GitLab-first-only 发布表述。
- validation_path：运行 local gate、local MR review、`openspec validate --all`、`python .\tools\run_openspec_guard.py --root . --tool codex --json`、`git diff --check`。
