## Why

持久化团队文档族已经围绕生命周期、白皮书、研究稿、MRD、北极星、实施方案和 playbook 做过刷新，但稳定 OpenSpec 规格的第一条 requirement 仍以旧的“十层落地图”标题和中文表述为中心。当前长期目标还需要一个明确的文档族同步检查点，让后续维护者区分“已提交的报告/归档/文档证据”和“未提交且当前可能不存在的原始 extraction cache”，避免过度声称所有相关文件已经在同一批次完成刷新。

## What Changes

- 将稳定 `codex-cli-personal-production-durable-team-plan` requirement 重新表述为 10 层运行时能力核心到 12 层产品/商业生命周期的桥接、文档族同步证据，以及 draft-only runtime 边界。
- 在核心文档族中加入小型同步检查点：实施方案、playbook、白皮书、MRD、北极星和研究稿。
- 记录 2026 年 6 月 fresh-source evidence 的可验证边界：已提交证据来自报告、归档和文档；原始 extraction cache 被忽略，当前 worktree 中不一定存在。
- 为本轮受限的文档/规格同步补充验证证据。

## Capabilities

### New Capabilities

- 无。

### Modified Capabilities

- `codex-cli-personal-production-durable-team-plan`：明确 draft plan requirement 覆盖 10 层运行时能力核心、当前 12 层产品/商业生命周期目标、核心持久化团队文档族同步检查点，以及不得把文档当成 runtime evidence 的边界。

## Impact

- 受影响文档：核心 durable-team plan/playbook/whitepaper/MRD/North Star/research 文档，以及 `codex-cli-personal-production-durable-team-plan` 的稳定/增量 OpenSpec 规格。
- 不改变 runtime code、用户级 launcher、原生 subagent、`native_omx`、LangGraph、model-provider 或远程发布行为。

## Governance Fields

- `impact_scope`：docs-only 稳定规格与核心 durable-team 文档族同步。
- `explicit_non_goals`：不重新运行 fresh extraction；不声称当前 worktree 存在被忽略的原始 extraction artifacts；不启动 runtime persistent team；不远程发布；不合并白皮书和研究稿。
- `rollout_sequence`：更新 OpenSpec artifacts；更新稳定/增量规格语言；加入文档族同步检查点；运行 OpenSpec 和文档检查；在隔离分支提交。
- `rollback_plan`：回退本分支提交，或从 `main` 恢复被触碰的文档/规格文件。
- `validation_path`：`openspec validate sync-durable-team-spec-12-layer-20260615 --strict --json`、`openspec validate --all`、文档配对/乱码/name 检查、precommit update/archive review；若推进到 local main，再运行 local gate。
- `mainline_classification`：既有 durable-team documentation governance 主线，归属长期 `codex_cli_personal_production_durable_team` 目标。
