## Why

`project_moe_agent_gui_toolchain_plan.zh-CN.md` 已经完成过一次结构整理，但仍需要按完整 `/comet` 语义补齐 Open / Design / Build / Verify 证据、archive deferral、实施事项顺序和 readiness lane 解释。现在重构可以避免后续代码实施时把“方案结构就绪”“目标项目 ready”“GUI runtime 已完成”混成一个状态。

## What Changes

- 重构 `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md`，使其与新版 Pi sidecar 方案同级：目标、架构、source of truth、contract、gate、rollback、风险、自检、验证路径齐全。
- 新增完整 Comet/OpenSpec active change 证据：proposal、design、delta spec、tasks、management、`.comet.yaml`。
- 新增 Superpowers design doc 与 implementation plan，记录本次文档重构的设计选择和执行计划。
- 明确 `D:\PythonProject_paper_suggest` 仍是 blocked/repair-lane 证据，不得误称 ready。
- 明确 archive deferral：本地 feature 分支提交后，archive 等待后续本地集成/验证报告/branch handling 决策。

## Capabilities

### New Capabilities

- `project-moe-agent-gui-plan-contract`: 约束 Project MOE GUI 实施方案必须区分文档结构就绪、目标项目 readiness、GUI runtime 完成度与远端发布授权边界。

### Modified Capabilities

- 无。本次不修改 stable spec 中已存在 capability；active change 只新增文档方案合同。

## Impact

- Affected docs: `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md`
- Affected OpenSpec artifacts: `openspec/changes/refine-project-moe-gui-plan-comet-structure/`
- Affected Superpowers artifacts: `docs/superpowers/specs/2026-05-27-project-moe-gui-plan-comet-design.md` and `docs/superpowers/plans/2026-05-27-refine-project-moe-gui-plan-comet-structure.md`
- No runtime code, dependency, user-level install, target-project write, GitLab/GitHub publication, or PySide6 installation is performed by this change.

## Governance Fields

- `impact_scope`: documentation plan + active OpenSpec artifacts only.
- `explicit_non_goals`: runtime implementation, target project writes, PySide6 install, remote publication, user-level config mutation.
- `rollout_sequence`: feature worktree -> document rewrite -> local validation -> feature branch commit -> await local main integration instruction.
- `rollback_plan`: revert the feature branch commit or reset local branch to the pre-change base; no external state is mutated.
- `validation_path`: `git diff --check`, `openspec validate`, implementation-plan checker, precommit update/archive gate, OpenSpec guard, local MR review.
- `mainline_classification`: existing Project MOE GUI documentation/implementation planning lane under the repository's user-level orchestration product line.
