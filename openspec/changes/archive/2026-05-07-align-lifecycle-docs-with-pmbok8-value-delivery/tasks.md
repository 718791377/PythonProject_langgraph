## 1. OpenSpec Artifacts

- [x] 1.1 Create `proposal.md`, the OpenSpec proposal for PMBOK8 value-delivery alignment.
- [x] 1.2 Create `design.md`, the OpenSpec design that records reference boundaries, project-canvas scope, and non-runtime scope.
- [x] 1.3 Create `specs/codex-product-lifecycle-document-governance/spec.md`, the delta spec for lifecycle governance.

## 2. Product Lifecycle Documents

- [x] 2.1 Update `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.md`, the English PMI reference map, to make PMBOK8 the primary overlay and PMBOK6/7/Process Groups/Agile supplemental overlays.
- [x] 2.2 Update `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.zh-CN.md`, the Chinese PMI reference map companion, with the same scope.
- [x] 2.3 Update `docs_bilingual/product_lifecycle/product_business_document_lifecycle.md`, the English general lifecycle document, with value-delivery, project-canvas, performance-domain, and tailoring-system guidance.
- [x] 2.4 Update `docs_bilingual/product_lifecycle/product_business_document_lifecycle.zh-CN.md`, the Chinese general lifecycle companion, with the same guidance.
- [x] 2.5 Add `docs_bilingual/product_lifecycle/codex_platform_project_canvas.md`, the English lightweight platform project canvas.
- [x] 2.6 Add `docs_bilingual/product_lifecycle/codex_platform_project_canvas.zh-CN.md`, the Chinese lightweight platform project canvas companion.

## 3. Platform And Consumption Documents

- [x] 3.1 Update `docs_bilingual/product_lifecycle/codex_durable_team_platform_build_lifecycle.md`, the English platform-build lifecycle, with value outcomes and AI-era role boundaries.
- [x] 3.2 Update `docs_bilingual/product_lifecycle/codex_durable_team_platform_build_lifecycle.zh-CN.md`, the Chinese platform-build lifecycle companion, with the same boundaries.
- [x] 3.3 Update `docs_bilingual/product_lifecycle/codex_project_consumption_lifecycle.md`, the English downstream-consumption lifecycle, with adoption canvas and value feedback.
- [x] 3.4 Update `docs_bilingual/product_lifecycle/codex_project_consumption_lifecycle.zh-CN.md`, the Chinese downstream-consumption lifecycle companion, with the same guidance.
- [x] 3.5 Update `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md`, the English white paper, to frame the platform as an AI-era value-delivery system.
- [x] 3.6 Update `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.zh-CN.md`, the Chinese white paper companion, with the same framing.
- [x] 3.7 Update `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md`, the English long-term draft plan, with value increments, feedback points, and rollback-boundary release-slice rules.
- [x] 3.8 Update `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md`, the Chinese long-term draft plan companion, with the same rules.

## 4. Validation

- [x] 4.1 Run `openspec validate --all`, the OpenSpec validation command for all specs and changes.
- [x] 4.2 Run `python tools/run_openspec_guard.py --root . --tool codex --json`, the repository OpenSpec guard command.
- [x] 4.3 Run `python tools/check_name_clarity_rules.py --root . --json`, the name clarity checker for docs and OpenSpec files.
- [x] 4.4 Run `git diff --check`, the whitespace validation command.
