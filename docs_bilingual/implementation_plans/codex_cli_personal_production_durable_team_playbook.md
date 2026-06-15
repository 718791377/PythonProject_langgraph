---
doc_id: codex_cli_personal_production_durable_team_playbook
lang: en
canonical: docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_playbook.md
translation_of: null
doc_class: implementation_plan
status: draft
---

# Codex CLI Personal Production Durable Team Playbook

## Purpose

This playbook turns the draft personal production durable-team target into release slices that a cold-start maintainer can follow. The draft target explains the architecture. This playbook explains what to do next.


## Authority Stack And Parity Links

This playbook is procedural. It does not replace the authoritative count maps, whitepaper, research note, or PMI tailoring documents; each release slice must link back to the relevant authority before changing architecture, governance depth, or runtime behavior.

- Codex durable-team platform target: 12 trunk layers, 4 virtual departments, 24 responsibility domains, 18 cross-cutting modules, 48 core documents, 12 governed AI agents, and 12 recommended books. The canonical inventory is `docs_bilingual/product_lifecycle/codex_platform_inventory_map.md`.
- One-person-company operating-system target: 12 trunk layers, 5 virtual departments, 30 responsibility domains, 20 cross-cutting modules, 60 core documents, 15 governed AI agents, 15 recommended books, and 12 minimal startup documents. The canonical inventory is `docs_bilingual/product_lifecycle/one_person_company_inventory_map.md`.
- Whitepaper versus research: `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md` remains the strategic narrative, while `docs_bilingual/governance/solo_maintainable_production_persistent_team_research.md` remains the evidence-heavy runtime/governance research canon. Do not physically merge them unless a later governed change proves one lifecycle role is obsolete.
- 10-to-12 bridge: use `docs_bilingual/product_lifecycle/ten_to_twelve_layer_bridge.md` to map the 10-layer runtime research model to the 12-layer product/business lifecycle model.
- PMI tailoring: use `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.md` and `docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.md` when a release slice needs process-group style Inputs, Tools and Techniques, Outputs, or a decision between full, whole-project lightweight, phase-local lightweight, module-level lightweight, and hybrid governance.

## Fixed Rules

- Use OpenSpec for structural repository changes.
- Keep native Codex as the base layer.
- Do not modify `C:\Users\lenovo\.codex\config.toml` without explicit operator consent.
- Do not start `native_omx`, `omx team`, or LangGraph runtime apply mode unless the release slice explicitly allows it.
- Keep project durable state under each repository's `.omx/state/` directory.
- Keep local GGUF model files out of ordinary Git.

## Release Slice Template

Each release slice must define:

- `goal` - what this slice achieves.
- `non_goals` - what this slice must not do.
- `preconditions` - state required before work starts.
- `file_scope` - files or directories that may change.
- `forbidden_scope` - files or directories that must not change.
- `commands` - commands that must be run.
- `evidence` - artifacts proving the slice worked.
- `rollback` - how to undo the slice.
- `runtime_apply_allowed` - whether runtime mutation is allowed.

## R0.6.x Read-Only Gate Slices

### R0.6.2 Read-Only State Sampling

Goal: sample one target repository's durable status without starting a team or writing durable state.

Allowed scope: status scripts, read-only reports, documentation, and fixtures.

Forbidden scope: `.omx/state/`, real user-level Codex configuration, and OpenClaw business state.

Runtime apply allowed: no.

### R0.6.3 Dry-Run Routing Decision

Goal: explain no-team, `native_omx`, or `langgraph` selection without launching a durable team.

Allowed scope: dry-run decision helpers, fixtures, and documentation.

Forbidden scope: worker launch, LangGraph checkpoint mutation, and automatic team apply.

Runtime apply allowed: no.

### R0.6.4 Expected-Result Fixture

Goal: create regression fixtures for expected dry-run decisions.

Allowed scope: fixture files, checker logic, and documentation.

Runtime apply allowed: no.

### R0.6.5 Cross-Project Read-Only Review

Goal: prove that consumer repository state does not leak into the orchestration repository.

Allowed scope: inventory reports, fixture descriptions, and read-only checkers.

Runtime apply allowed: no.

## Local Model Asset Migration Slice

Goal: document and later implement central management of local llama and GGUF model assets under `D:\PythonProject_langgraph` while allowing OpenClaw to start or call those services through provider profiles.

Preconditions:

- Both repositories are clean according to `git status --short --branch`.
- Ignore rules for `.local/`, `.runtime/`, `*.gguf`, and `*.GGUF` are present before copying model files.
- Provider profiles are documented before OpenClaw wiring is changed.

Allowed scope:

- migration plan
- provider policy
- profile templates
- health-check design
- documentation

Forbidden scope:

- real GGUF files
- `.omx/state/` - repo-local durable state directory that must not be changed by the model-asset documentation slice.
- OpenClaw domain-agent state
- user-level Codex configuration

Runtime apply allowed: no for the documentation slice; later local migration may copy ignored files only after explicit operator action.

Evidence:

- `git check-ignore -v` output for model paths.
- clean `git status --short --branch` after local model copy.
- provider profile health-check report when runtime testing is later allowed.

Rollback:

- revert tracked documentation and script changes through Git.
- manually move or delete ignored local model files if the operator decides to undo local migration.

## Expert Routing Playbook

For bounded multi-face research, run homogeneous analyst fan-out first. Use architect or planner only after analyst fan-in shows a need for architecture design or execution ordering.

A subagent that does not finish must not be silently skipped. Record the role, prompt scope, wait windows, last signal, suspected cause, action taken, and whether its result was used.

## Validation

Before publishing a release slice, run:

- `openspec validate --all` - OpenSpec validation for all active and stable specs.
- `python .\tools\run_openspec_guard.py --root . --tool codex --json` - aggregate repository guard.
- `python .\tools\check_name_clarity_rules.py --root . --json` - checker for script, path, command, variable, profile, and role explanations.
- `git diff --check` - whitespace validation.
