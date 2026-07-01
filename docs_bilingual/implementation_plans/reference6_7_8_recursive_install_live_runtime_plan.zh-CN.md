---
doc_id: reference6_7_8_recursive_install_live_runtime_plan
doc_class: implementation_plan
lang: zh-CN
status: active
translation_of: docs_bilingual/implementation_plans/reference6_7_8_recursive_install_live_runtime_plan.md
parent_plan: docs_bilingual/implementation_plans/reference6_reference7_reference8_user_project_live_runtime_plan.zh-CN.md
source_files: reference_files/6.md, reference_files/7.md, reference_files/8.md
plan_stage: R6-recursive-live-runtime
priority_order: Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit
remote_publication_allowed: false
browserbase_policy: disabled_by_user
recursive_unit_policy: installable_unit_only
---

# Reference 6/7/8 Recursive Installable-Unit Live Runtime Plan (zh-CN companion)

## Goal

This zh-CN companion intentionally keeps ASCII-safe wording for the cold-start console path while preserving the same implementation meaning as the English canonical plan. The implementation upgrades the existing Reference 6/7/8 per-link R6 live runtime result to recursive installable-unit granularity: child SKILL.md units, native-agent TOML units, plugin/MCP manifests, CLI/package/runtime wrapper units, and template units must each have a Codex usable surface plus receipt/smoke evidence.

## Scope and exclusions

- Inputs: `reference_files/6.md`, `reference_files/7.md`, and `reference_files/8.md`.
- Included units: `SKILL.md`, native-agent TOML, plugin/MCP manifest, workspace package/runtime wrapper package, and repository subdirectories containing those installable markers.
- Excluded units: plain docs folders, examples without an install marker, raw source files that do not define Codex skill/agent/plugin/CLI surfaces, caches, generated files, and private/commercial payloads without an owned local runtime.
- Browserbase remains disabled. Browserbase child skill units inherit disabled receipts and do not count as live-executed while `browserbase_policy=disabled_by_user`.
- Visio, CAE, and Ansys remain provision/probe lanes unless real local runtime or license evidence exists.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: planned and frozen for implementation. The parent plan proves per-link completion; the remaining gap is recursive child-unit install and child receipt evidence, especially Matt Pocock child skills under `skills/*/SKILL.md`.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Planned: add recursive discovery and checker coverage for Reference 6/7/8 installable units.
- Planned: add user-level child adapters and hash-redacted child update/smoke receipts.
- Planned: install Matt Pocock child skills individually instead of only a coarse parent adapter.
- Planned: keep Browserbase recursive child units disabled under user policy.
- Planned: recursively expand large skill collections such as Nature and Scientific Agent Skills to installable-unit level.
- Planned: update `D:/PythonProject_General` and `D:/PythonProject_General_2` with reusable recursive surfaces.
- Planned: run parent checkers, recursive checker, template gates, repository gates, local MR review, and local-main integration.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Pending implementation evidence: `tools/check_reference_recursive_capability_install.py --root . --json`.
- Pending user-level install evidence: child receipts under `state/reference-recursive-capability-install/receipts` in Codex home.
- Pending template evidence: recursive helper/checker/template surfaces in `D:/PythonProject_General` and `D:/PythonProject_General_2`.
- Pending gate evidence: Reference 6/7/8 parent checkers, recursive checker, template gates, local gate, and local MR review.
<!-- EVIDENCE_INDEX_END -->

## Implementation sequence

### Stage A: Freeze this child plan

1. Create the English canonical plan and this zh-CN companion.
2. Register both files in `docs_bilingual/docs_registry.yaml` as an active child implementation plan.
3. Record local worktree receipt and session claim metadata.
4. Run precommit, plan, and OpenSpec guards that are valid before implementation.
5. Commit and merge the plan to local `main`; stop at the remote-publication gate.

### Stage B: Build recursive source of truth and checker

1. Add `tools/check_reference_recursive_capability_install.py`.
2. Load Reference 6/7/8 manifests and expand each capability source into recursive installable units.
3. Require each unit to be `live-executed`, `disabled`, `dedupe`, or `provision-recorded`.
4. Fail closed when discovered child `SKILL.md` units have only a coarse parent adapter.
5. Enforce no raw upstream install-only completion, no secret copy, hash-redacted receipts, Browserbase disabled inheritance, and no remote mutation.

### Stage C: Install recursive user-level Codex surfaces

1. Write child adapters under Codex home without changing native Codex files or `config.toml`.
2. Generate child `SKILL.md` adapters with stable child id, source path, parent id, upstream URL, smoke kind, and governance priority.
3. Generate minimal Codex-native agent TOML, service-adapter JSON, or runtime-wrapper adapters for non-skill units.
4. Generate child update/smoke receipts with source URL, source path, parent id, child id, state, stage, artifact hash, command hash, rollback hash, and redaction status.
5. Keep Browserbase child units disabled and counted separately from live-executed units.

### Stage D: Update reusable templates

1. Update `D:/PythonProject_General` with active recursive helpers and checker surfaces.
2. Update `D:/PythonProject_General_2` with inert recursive samples for disabled/provision/commercial lanes.
3. Commit template updates on local `main` when the template roots are Git repositories.
4. Preserve unrelated dirty files and do not overwrite consumer project state.

### Stage E: Verify and integrate locally

1. Run strict Reference 6, Reference 7, and Reference 8 checkers.
2. Run the new recursive checker with user-level and template requirements.
3. Run repository OpenSpec guard, local gate, and local MR review.
4. Run both template local gates.
5. Commit implementation and merge to local `main` with rollback and claim evidence; do not publish remotely without explicit approval.

## Collaboration routing

- Stage A is one document/governance slice and does not itself start a durable team.
- After Stage A, Stage B-D have at least three independent slices: recursive checker, user-level install/receipts, and template sync.
- Use explorer, researcher, test-engineer, verifier, and code-reviewer experts when available; main session owns fan-in and final integration.

## Acceptance criteria

- Every Reference 6/7/8 link has per-link and recursive installable-unit Codex completion evidence.
- Every discovered child unit has a child adapter or explicit disabled/dedupe/provision receipt.
- Matt Pocock child skills are installed individually.
- Browserbase remains disabled and child units inherit disabled receipts.
- Large skill collections are expanded only at installable-unit level; no fake skills are made from plain docs/examples.
- `D:/PythonProject_General` and `D:/PythonProject_General_2` receive reusable recursive surfaces.
- Receipts are hash-redacted and human-checkable; no secret values or raw private paths are committed.
- Changes are committed, verified, and integrated into local `main`; remote publication remains gated.
