## Why

The repository already has a bilingual 0-8 product and business document lifecycle, a Codex durable-team platform-build lifecycle, and a downstream project-consumption lifecycle. The local `PMP/` reference audit now shows that the PMBOK 8th Edition PDF is readable enough to serve as the primary project-management reference, while the Process Groups guide, PMBOK 6th Edition, PMBOK 7th Edition, and Agile Practice Guide are useful supplemental sources.

The current documents still understate three ideas that matter for this repository:

- Value delivery is stronger than document completion or process compliance.
- A lightweight project canvas is useful before expanding a full document stack.
- Predictive gates, adaptive discovery, and hybrid release slices should be made explicit in implementation plans and downstream project consumption.

## What Changes

- Update the PMI reference map so PMBOK 8th Edition is the primary overlay and PMBOK 6th/7th Edition, Process Groups, and Agile guidance are supplemental overlays.
- Add a project-canvas concept and value-delivery checks to the general product/business lifecycle.
- Add platform-specific value indicators, AI-era role boundaries, and governance-system tailoring to the Codex durable-team platform-build lifecycle.
- Add downstream adoption canvas, consumer value feedback, and adoption outcome checks to the downstream project-consumption lifecycle.
- Update the durable-team white paper so it frames the platform as an AI-era value-delivery system, not only a toolchain.
- Update the long-term durable-team implementation plan so its release slices carry value increments, feedback points, and rollback boundaries while remaining a draft.
- Add a bilingual platform project canvas as a lightweight alignment artifact.

## Capabilities

### Modified Capabilities

- `codex-product-lifecycle-document-governance` - the product-lifecycle governance capability that defines lifecycle documents, platform/downstream separation, and PMI reference overlays.

### New Capabilities

- None. This is a documentation and governance alignment change.

## Impact

- Affected paths:
  - `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.md` - English PMI reference map used to explain project-management overlays.
  - `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.zh-CN.md` - Chinese companion for the PMI reference map.
  - `docs_bilingual/product_lifecycle/product_business_document_lifecycle.md` - English general product and business lifecycle document.
  - `docs_bilingual/product_lifecycle/product_business_document_lifecycle.zh-CN.md` - Chinese companion for the general lifecycle document.
  - `docs_bilingual/product_lifecycle/codex_durable_team_platform_build_lifecycle.md` - English lifecycle for building the Codex durable-team platform.
  - `docs_bilingual/product_lifecycle/codex_durable_team_platform_build_lifecycle.zh-CN.md` - Chinese companion for the platform-build lifecycle.
  - `docs_bilingual/product_lifecycle/codex_project_consumption_lifecycle.md` - English lifecycle for downstream projects consuming platform capabilities.
  - `docs_bilingual/product_lifecycle/codex_project_consumption_lifecycle.zh-CN.md` - Chinese companion for the downstream-consumption lifecycle.
  - `docs_bilingual/product_lifecycle/codex_platform_project_canvas.md` - English lightweight platform project canvas.
  - `docs_bilingual/product_lifecycle/codex_platform_project_canvas.zh-CN.md` - Chinese companion for the platform project canvas.
  - `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md` - English white paper for the durable-team platform narrative.
  - `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.zh-CN.md` - Chinese companion for the durable-team white paper.
  - `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` - English long-term draft implementation plan.
  - `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` - Chinese companion for the long-term draft implementation plan.
- No runtime code changes.
- No direct writes to `PMP/`, the local private reference directory.
- No change to native Codex, `native_omx`, or `langgraph` runtime behavior.
