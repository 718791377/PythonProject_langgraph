# 设计：持久化团队文档族与 10-to-12 规格同步

## Change

`sync-durable-team-spec-12-layer-20260615`

## 背景

当前文档已经把战略白皮书和证据密集研究稿分开，也已经说明 10 层运行时模型是能力核心，12 层生命周期是仓库的产品/商业规划框架。剩余缺口是同步证据：稳定 durable-team 规格、中文对照规格和核心文档族需要一个明确检查点，说明当前口径、已提交证据，以及哪些内容不能当作 runtime proof。

## 决策

1. 白皮书与研究稿继续分离。本变更只增加跨文档同步证据，不合并它们的生命周期角色。
2. 以稳定 OpenSpec requirement 作为实施方案桥接行为的验收权威。
3. 显式记录 ignored extraction cache 的限制。已提交文档可以通过报告和归档证据引用 2026 年 6 月 extraction run，但不得暗示每个 worktree 都存在原始 ignored cache。
4. 保持 docs-only。不改变 runtime、launcher、model 或远程发布行为。

## 文件范围

- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.*` - core draft implementation plan and 10-to-12 bridge authority.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_playbook.*` - release-slice operating playbook for the draft target.
- `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.*` - strategic white paper for the durable-team corpus.
- `docs_bilingual/market_requirements/codex_cli_personal_production_durable_team_mrd.*` - market requirements document for target users and tailoring.
- `docs_bilingual/governance/solo_maintainable_production_persistent_team_research.*` - evidence-heavy research note and merge-boundary record.
- `docs_bilingual/north_star_plan.*` - metrics and decision-threshold north-star plan.
- `openspec/specs/codex-cli-personal-production-durable-team-plan/spec.*` - stable OpenSpec acceptance authority.
- `openspec/changes/sync-durable-team-spec-12-layer-20260615/...` - active delta-spec and workflow evidence package.
- `docs/superpowers/specs/2026-06-15-durable-team-corpus-sync-design.*` - HOW-layer design artifact for this sync slice.
- `docs/superpowers/plans/2026-06-15-sync-durable-team-spec-12-layer.*` - HOW-layer execution plan for this sync slice.

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 过度声称 fresh extraction evidence | 明确 raw extraction artifacts 被忽略且可能缺席；只引用已提交的 report/archive evidence。 |
| 重新打开白皮书/研究稿合并问题 | 保持独立角色，并指向既有合并策略。 |
| 把 draft 文档误当成 runtime evidence | 在规格和检查点里重复 no-runtime-evidence 边界。 |
| 中文编辑产生乱码 | 使用显式 UTF-8 写入，并在编辑后运行 mojibake 检查。 |

## 验收证据

- 本 change 的 OpenSpec strict validation 通过。
- 稳定与增量规格提到 10-to-12 bridge 和 no-runtime-evidence boundary。
- 核心 durable-team 文档族包含 2026-06-15 corpus sync checkpoint。
- touched files 的 UTF-8/乱码检查通过。
