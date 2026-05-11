# Design: Lifecycle Tailoring Rules

## Boundaries

This change is documentation-only. It does not change launchers, wrappers, checkers, CI, MCP configuration, user-level skills, durable state, or runtime behavior.

The local `Business Management/` and `PMP/` directories remain ignored private references. The change may use the existing extraction coverage and repository synthesis, but it must not commit raw book text, extracted pages, OCR output, or long copyrighted excerpts.

## Tailoring Model

The tailoring model adds a decision gate above the existing 12-layer lifecycle. The gate chooses the minimum sufficient governance depth for a project, phase, module, or release slice.

The model has four outcomes:

1. Full architecture for the affected scope.
2. Whole-project lightweight architecture.
3. Phase-local or gate-local lightweight architecture.
4. Module-level lightweight architecture inside an otherwise full-governed system.

Escalation is mandatory when a lightweight scope starts to affect money, external users, trust, compliance, security, privacy, data, release safety, shared interfaces, cross-project templates, runtime entrypoints, durable state, or long-lived platform behavior.

## Process-Group Style

The tailoring gate itself is execution-facing and therefore uses Inputs, Tools and Techniques, and Outputs.

- Inputs include architecture mode, project type, risk, uncertainty, affected layers, ownership, release surface, source evidence, and current state.
- Tools and Techniques include tailoring scorecards, risk classification, predictive/adaptive/hybrid selection, module boundary review, OpenSpec and local-main-first gate selection, and escalation review.
- Outputs include the tailoring decision record, selected minimum document set, affected layers, lightweight scope boundary, escalation triggers, validation plan, release or rollback evidence, and owner approval.

## Documentation Targets

- Add `docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.md`.
- Add `docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.zh-CN.md`.
- Link the new rule from:
  - `product_business_document_lifecycle.*` - explains the general 12-layer product and business document stack.
  - `pmi_project_management_reference_map.*` - maps PMI project-management references to repository lifecycle gates.
  - `codex_durable_team_platform_build_lifecycle.*` - defines the Codex platform-build lifecycle.
  - `codex_project_consumption_lifecycle.*` - defines how downstream projects consume the platform.
  - `codex_cli_personal_production_durable_team_whitepaper.*` - explains the platform cognitive narrative.
  - `codex_cli_personal_production_durable_team_mrd.*` - defines market requirements and capability profiles.
  - `codex_cli_personal_production_durable_team_plan.*` - defines the North Star and implementation-bridge plan.

## Validation

Run the normal repository documentation and OpenSpec gates:

- `openspec validate --all` - validates all active changes and stable specs.
- `openspec validate add-lifecycle-tailoring-rules` - validates this OpenSpec change.
- `python .\tools\run_openspec_guard.py --root .` - runs the repository OpenSpec guard.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1` - runs the shared local CI gate.
- `git diff --check` - checks whitespace in the diff.
