## Why

自动协同路由强制化实施计划是用户级协同路由的 active baseline。之前的 Comet pass 是 tweak 级文档清理；本次用户明确要求完整 `/comet` 重构 `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md` 并提交本地 Git。

完整 pass 的目的，是让文档维护本身可审计：OpenSpec 解释 WHAT，Superpowers 记录 HOW，目标计划明确区分 policy expectation、Phase 0-3 completed evidence、Phase 4 planned hardening 与 runtime evidence boundaries。

## What Changes

- 重构中文目标 implementation plan，增加 full Comet reading path、artifact map 与 documentation-only evidence boundary。
- 同步更新英文 companion 的 high-level full Comet framing。
- 增加 full Comet/OpenSpec/Superpowers trace artifacts。
- 保留既有 policy 事实：Phase 0-3 已完成、Phase 4 仍 planned follow-up、LangGraph ready 不等于 persistent team running、plan text 不是 runtime evidence。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `automatic-orchestration-plan-doc-refactor` - 为 automatic orchestration routing enforcement plan 的 full Comet refactor 提供 document-maintenance traceability。

## Impact

影响文档包括中文目标计划、英文 companion、OpenSpec archive 与 Superpowers design/plan。该 change 不修改 runtime code、生成式用户级资产、目标项目文件、本地 `main` 或远端引用。

## Non-Goals

- 不实现 Phase 4 prompt-independent parity checkers。
- 不声称 durable teams、persistent teams、LangGraph workflows 或 native experts 已运行。
- 不修改用户级 Codex 资产、`.omx` durable state 或外部项目仓库。
- 不在未获授权时合入 local main 或发布 GitLab/GitHub。
