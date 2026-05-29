## ADDED Requirements

### Requirement: Comet-tracked automatic routing plan refactor

仓库必须保持 automatic orchestration routing enforcement plan 的 Comet-requested refactor 可追踪，同时不得暗示 runtime enforcement 已改变。

#### Scenario: Documentation-only Comet tweak

- **WHEN** 用户要求按 Comet 重构 `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md`，且变更仅限文档结构
- **THEN** 仓库用 OpenSpec/Comet artifacts 记录该 tweak
- **AND** 文档说明该 refactor 不是 experts、durable teams 或 persistent teams 已运行的 runtime evidence
- **AND** 除非另有授权，不修改 runtime code、生成式用户级资产、本地 `main` 或远端引用

#### Scenario: Phase status is preserved

- **WHEN** refactor 更新计划结构
- **THEN** Phase 0-3 completion status 必须与 Phase 4 planned follow-up status 分开
- **AND** 未来 Phase 4 implementation work 仍代表未来 bounded change，而不是被该 tweak 完成

#### Scenario: Comet shell helper unavailable

- **WHEN** 当前 Windows shell 因缺少 `bash` 无法运行 Comet shell scripts
- **THEN** 会话记录 blocker，并使用 OpenSpec artifacts 与 repository validation gates 作为可追踪 fallback
