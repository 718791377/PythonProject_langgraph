## ADDED Requirements

### Requirement: Full Comet traceability for automatic routing plan refactors

仓库必须保持 automatic orchestration routing enforcement plan 的完整 `/comet` 重构可追踪，同时不得暗示 runtime enforcement 已改变。

#### Scenario: Full workflow documentation refactor

- **WHEN** 用户要求按照完整 `/comet` 重构 `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md`
- **THEN** 仓库记录包含 proposal、design、tasks 与 delta spec 的 full OpenSpec change
- **AND** 仓库记录 Superpowers design 与 implementation-plan artifacts
- **AND** 目标计划标出这些 artifacts，并说明本次 refactor 是 documentation-only

#### Scenario: Runtime evidence boundary is preserved

- **WHEN** refactor 更新计划结构或 reading paths
- **THEN** 文档保持 Phase 0-3 completion 与 Phase 4 planned follow-up 分离
- **AND** 文档不得声称 durable teams、persistent teams、LangGraph workflows 或 native experts 已运行
- **AND** 文档不得把 LangGraph backend readiness 当成 persistent team runtime evidence

#### Scenario: Comet shell helper unavailable

- **WHEN** 当前 Windows shell 因缺少 `bash` 无法运行 Comet shell scripts
- **THEN** change 必须显式记录 blocker
- **AND** validation 使用 OpenSpec artifacts 与 repository checks 作为 fallback evidence
- **AND** reports 不得声称 `comet-state.sh` 或 `comet-guard.sh` transition 成功

#### Scenario: Bilingual companion alignment

- **WHEN** 中文 implementation plan 获得 full Comet framing update
- **THEN** 英文 companion 必须在同一批次获得 matching high-level framing，除非未来用户明确批准临时例外
