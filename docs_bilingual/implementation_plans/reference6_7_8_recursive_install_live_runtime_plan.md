---
doc_id: reference6_7_8_recursive_install_live_runtime_plan
doc_class: implementation_plan
lang: en
status: active
plan_stage: R6-recursive-live-runtime
parent_plan: docs_bilingual/implementation_plans/reference6_reference7_reference8_user_project_live_runtime_plan.md
source_files: reference_files/6.md, reference_files/7.md, reference_files/8.md
priority_order: Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit
remote_publication_allowed: false
browserbase_policy: disabled_by_user
recursive_unit_policy: installable_unit_only
---

# Reference 6/7/8 Recursive Installable-Unit Live Runtime Plan

## Goal

Extend the existing Reference 6/7/8 live-runtime installation so every reference link has a Codex-usable completion surface plus receipt/smoke evidence at **recursive installable-unit** granularity. The parent plan already proves per-link R6 live runtime for Reference 6, Reference 7, and Reference 8; this child plan closes the remaining granularity gap by discovering upstream child skills, agent packs, CLI/package wrappers, MCP/plugin manifests, and template units under each upstream repository and installing/adapting each unit that is actually installable in Codex.

## Scope and exclusions

- Inputs: `reference_files/6.md`, `reference_files/7.md`, and `reference_files/8.md`.
- Included unit types: `SKILL.md`, native-agent TOML definitions, plugin/MCP manifests, workspace package/runtime-wrapper packages, and repository subdirectories that contain one of those installable markers.
- Excluded unit types: plain documentation folders, examples without an install marker, raw source files that do not define a Codex skill/agent/plugin/CLI surface, caches, generated files, and private/commercial runtime payloads without an owned local runtime.
- Browserbase remains disabled. Browserbase child `SKILL.md` units receive disabled child receipts and must not be counted as live-executed while `browserbase_policy=disabled_by_user`.
- External proprietary/desktop lanes such as Visio, CAE, and Ansys keep the parent-plan rule: record adapter/provision receipts and opt-in probes, but do not fake live-executed status without a real runtime/license probe.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: planned and frozen for implementation. The known gap is that the parent Reference 6/7/8 plan proves per-link completion, while recursive child installable units such as the Matt Pocock `skills/*/SKILL.md` tree are not yet individually installed with child receipts.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Planned: add a recursive discovery manifest/checker that expands every Reference 6/7/8 upstream into installable units and records disabled/dedupe/provision classifications.
- Planned: extend the user-level installer to generate Codex child-skill/agent/runtime adapter surfaces and hash-redacted child update/smoke receipts.
- Planned: recursively install all Matt Pocock child skills under `https://github.com/mattpocock/skills/tree/main/skills` as distinct Codex skills instead of a single coarse adapter.
- Planned: recursively classify Browserbase child skills as disabled child lanes, preserving the user-disabled Browserbase policy.
- Planned: recursively classify large skill collections such as Nature and Scientific Agent Skills and install/adapt each discovered `SKILL.md` unit that has an installable marker.
- Planned: update `D:/PythonProject_General` and `D:/PythonProject_General_2` with reusable recursive discovery/checker/template surfaces.
- Planned: run strict Reference 6/7/8 parent checkers plus the new recursive checker, template gates, local CI, local MR review, and local-main integration.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Pending implementation evidence: `tools/check_reference_recursive_capability_install.py --root . --json` after the implementation commit.
- Pending user-level install evidence: hash-redacted child receipts under Codex-home state `state/reference-recursive-capability-install/receipts`.
- Pending template evidence: recursive manifest/checker surfaces copied into `D:/PythonProject_General` and inert/upgrade samples copied into `D:/PythonProject_General_2`.
- Pending gate evidence: Reference 6/7/8 parent checker runs, recursive checker run, template local gates, repository local gate, and local MR review.
<!-- EVIDENCE_INDEX_END -->

## Implementation sequence

### Stage A: Freeze this child implementation plan

1. Create this English plan and the Chinese companion.
2. Register both files in `docs_bilingual/docs_registry.yaml` as an active implementation child plan of the existing Reference 6/7/8 parent plan.
3. Create local worktree receipt and session claim metadata for the plan worktree.
4. Run precommit/plan/OpenSpec guards that are valid before implementation.
5. Commit and merge the plan into local `main` through the local-main-first helper, then stop at the remote-publication gate.

### Stage B: Build recursive source-of-truth and checker

1. Add a repository checker `tools/check_reference_recursive_capability_install.py`.
2. The checker must load Reference 6/7/8 manifests, expand each capability source into recursive installable units, and validate that every unit has one of these states: `live-executed`, `disabled`, `dedupe`, or `provision-recorded`.
3. The checker must fail closed when a GitHub upstream with discovered `SKILL.md` units has only a coarse parent adapter and no per-child receipts.
4. The checker must enforce no raw upstream install-only completion, no secret copies, hash-redacted receipts, Browserbase disabled inheritance, and no remote publication mutation.
5. Register the checker in `tools/run_openspec_guard.py`, `tools/ci/ci_test_manifest.json` if tests are added, and `tools/safety_rule_script_backing_registry.json`.

### Stage C: Install recursive user-level Codex surfaces

1. Implement or extend the installer to write child adapters under Codex-home without mutating native Codex program files or `config.toml`.
2. For child `SKILL.md` units, generate Codex `SKILL.md` adapters with a stable child id, source path, parent capability id, upstream URL, smoke kind, and governance priority.
3. For agent/plugin/package units, generate the smallest Codex-native agent TOML, service-adapter JSON, or runtime-wrapper adapter that is sufficient for Codex usage.
4. Generate child update and smoke receipts containing source URL, source path, parent id, child id, child state, stage, artifact hash, command hash, rollback pointer hash, and redaction status.
5. Keep Browserbase child units disabled and count them separately from live-executed units.

### Stage D: Update reusable templates

1. Update `D:/PythonProject_General` with recursive active-template helpers and a local checker that can smoke child adapters in generated projects.
2. Update `D:/PythonProject_General_2` with inert recursive samples for disabled/provision/commercial lanes.
3. Commit template updates in each template repository on local `main` when they have Git repositories.
4. Preserve unrelated dirty files and do not overwrite consumer-project state.

### Stage E: Verification and local integration

1. Run Reference 6, Reference 7, and Reference 8 strict checkers with installed/smoke/live/template flags where supported.
2. Run the new recursive checker with user-level and template requirements.
3. Run repository `python tools/run_openspec_guard.py --root . --json`, `tools/ci/local_gate.ps1`, and `tools/ci/local_mr_review.ps1`.
4. Run `D:/PythonProject_General/tools/ci/local_gate.ps1` and `D:/PythonProject_General_2/tools/ci/local_gate.ps1` after template sync.
5. Commit implementation changes and merge into local `main` with rollback/claim evidence, then stop before remote publication.

## Collaboration routing

- Stage A is a single document/governance slice and does not start a durable team by itself.
- After Stage A is frozen, Stage B through Stage D have at least three independent slices: recursive discovery/checker, user-level install/receipts, and template sync. That meets the durable-team threshold if the current selector/backend is ready.
- Native expert use: explorer for repo mapping, researcher for official upstream inventory, test-engineer/verifier for gate adequacy, and code-reviewer for final integration review.
- The current main Codex CLI session remains leader-owned fan-in and final integration authority.

## Acceptance criteria

- Every link in `reference_files/6.md`, `reference_files/7.md`, and `reference_files/8.md` has a Codex usable completion surface and a receipt/smoke record at per-link and recursive installable-unit granularity.
- Every discovered installable child unit is represented by a child adapter or an explicit disabled/dedupe/provision receipt.
- Matt Pocock upstream child skills are installed individually rather than only through the coarse `mattpocock-skills` parent adapter.
- Browserbase remains disabled and its recursive child units inherit disabled receipts.
- Large skill collections are recursively expanded to the installable-unit level, with no fake skills created from plain docs/examples.
- `D:/PythonProject_General` and `D:/PythonProject_General_2` receive reusable recursive install/checker/template surfaces.
- All receipts are hash-redacted and human-checkable; no secret values or raw private paths are committed.
- All implementation changes are committed, verified, and integrated into local `main`; remote publication is not performed without explicit approval.
