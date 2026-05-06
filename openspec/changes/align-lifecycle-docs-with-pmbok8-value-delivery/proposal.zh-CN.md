## 为什么

仓库已经有双语 0-8 产品与商业文档生命周期、Codex 持久化团队平台建设生命周期，以及下游项目消费生命周期。本轮本地 `PMP/` 读取审计显示，PMBOK 第8版 PDF 已经足够可读，可以作为主要项目管理参考；Process Groups 指南、PMBOK 第6版、PMBOK 第7版和 Agile Practice Guide 则适合作为补充来源。

当前文档仍然低估了三个对本仓库很重要的观点：

- 价值交付比文档完成或流程合规更重要。
- 在展开完整文档栈前，轻量项目画布很适合作为前置对齐工件。
- predictive gates、adaptive discovery 和 hybrid release slices 应在 implementation plans 与下游项目消费中显式化。

## 变更内容

- 更新 PMI 参考映射，使 PMBOK 第8版成为主要叠加层，并把 PMBOK 第6/7版、Process Groups 和 Agile guidance 作为补充叠加层。
- 在通用产品/商业生命周期中加入项目画布概念和价值交付检查。
- 在 Codex 持久化团队平台建设生命周期中加入平台价值指标、AI 时代角色边界和治理系统裁剪。
- 在下游项目消费生命周期中加入 adoption canvas、consumer value feedback 和 adoption outcome checks。
- 更新持久化团队白皮书，把平台描述为 AI 时代价值交付系统，而不仅是工具链。
- 更新长期持久化团队实施方案，使 release slices 带有 value increment、feedback point 和 rollback boundary，同时继续保持 draft 状态。
- 新增双语平台项目画布，作为轻量对齐工件。

## 能力

### 修改的能力

- `codex-product-lifecycle-document-governance` - 产品生命周期治理能力，用来定义 lifecycle documents、平台/下游分离，以及 PMI reference overlays。

### 新增能力

- 无。本变更是文档与治理对齐，不改运行时代码。

## 影响范围

- 影响路径：
  - `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.md` 是 PMI 参考映射英文主版。
  - `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.zh-CN.md` 是 PMI 参考映射中文对照版。
  - `docs_bilingual/product_lifecycle/product_business_document_lifecycle.md` 是通用产品/商业生命周期英文主版。
  - `docs_bilingual/product_lifecycle/product_business_document_lifecycle.zh-CN.md` 是通用产品/商业生命周期中文对照版。
  - `docs_bilingual/product_lifecycle/codex_durable_team_platform_build_lifecycle.md` 是 Codex 平台建设生命周期英文主版。
  - `docs_bilingual/product_lifecycle/codex_durable_team_platform_build_lifecycle.zh-CN.md` 是 Codex 平台建设生命周期中文对照版。
  - `docs_bilingual/product_lifecycle/codex_project_consumption_lifecycle.md` 是下游项目消费生命周期英文主版。
  - `docs_bilingual/product_lifecycle/codex_project_consumption_lifecycle.zh-CN.md` 是下游项目消费生命周期中文对照版。
  - `docs_bilingual/product_lifecycle/codex_platform_project_canvas.md` 是平台项目画布英文主版。
  - `docs_bilingual/product_lifecycle/codex_platform_project_canvas.zh-CN.md` 是平台项目画布中文对照版。
  - `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md` 是持久化团队白皮书英文主版。
  - `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.zh-CN.md` 是持久化团队白皮书中文对照版。
  - `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` 是长期实施方案英文主版。
  - `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` 是长期实施方案中文对照版。
- 不改运行时代码。
- 不直接写入 `PMP/`；`PMP/` 是本地私有参考目录。
- 不改变 native Codex、`native_omx` 或 `langgraph` 的运行行为。
