---
doc_id: operations_package_generation_and_runtime_plan
doc_class: implementation_plan
status: final
change: generate-operations-package-runtime-20260620
base_ref: 513788164167bbbb0c22872bcac9dd64de8b2b2b
archived-with: 2026-06-20-generate-operations-package-runtime-20260620
---

# Operations Package Generation And Runtime Implementation Plan

> For agentic workers: use subagent-driven-development or executing-plans to implement this plan task-by-task. Keep Stage A and Stage B as separate local-main integration packages.

**Goal:** generate governed bilingual operations packages for the Codex CLI personal production durable-team system and the personal production one-person-company operations system, with explicit tailoring rules and process-group Inputs / Tools And Techniques / Outputs for execution-facing flows.

**Architecture:** Stage A freezes this plan, OpenSpec contract, and registry entry only. Stage B adds a deterministic generator, a checker, tests, generated bilingual operations-package documents, and registry coverage from the frozen plan.

**Tech Stack:** Python CLI helpers, Markdown document generation, YAML registry updates, OpenSpec artifacts, unittest-based repository tests, local-main-first Git workflow.

## Stage A: Freeze Plan Package

Files:

- Create `openspec/changes/generate-operations-package-runtime-20260620/` with proposal, design, tasks, management, and delta spec files.
- Create `docs_bilingual/implementation_plans/operations_package_generation_and_runtime_plan.md` and `.zh-CN.md`.
- Update `docs_bilingual/docs_registry.yaml` with the new implementation plan pair.

Rules:

1. Stage A is documentation/governance only. It does not create runtime scripts, tests, generated package documents, or CI-manifest entries.
2. Stage A freezes the Stage B required output set, tailoring rules, I/T/O contract, and validation commands.
3. Stage A remains leader-owned. Advisory experts may review scope, but durable/persistent team launch waits until the frozen plan exists on local `main`.

Validation:

```powershell
openspec validate generate-operations-package-runtime-20260620 --strict
python .	ools\check_document_pair_policy.py --root . --base-ref main --json
python .	ools\check_precommit_update_archive.py --root . --json
python .	ools
un_openspec_guard.py --root . --tool codex --json
powershell -NoProfile -ExecutionPolicy Bypass -File .	ools\ci\local_gate.ps1 -StepTimeoutSeconds 1500 -Json
powershell -NoProfile -ExecutionPolicy Bypass -File .	ools\ci\local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json
```

Commit Stage A with a Chinese commit subject, then integrate it into local `main` through `tools/complete_local_flow_to_remote_gate.py --execute`.

## Stage B: Runtime And Generated Package

Files:

- Create `tools/generate_operations_package.py`.
- Create `tools/check_operations_package_docs.py`.
- Create `test/operations_package_docs.test.py`.
- Modify `tools/ci/ci_test_manifest.json` to register `operations_package_docs.test.py`.
- Modify `docs_bilingual/docs_registry.yaml` to register generated document pairs.
- Generate Codex durable-team package documents: BRD, PRD, template update policy, core-documents register, responsibility RACI, governed-agent catalog, cross-cutting-module map, reference-books map, virtual-departments operating map, document generation order, and operating slice template.
- Generate one-person-company package documents: operations document system, tailoring decision tree, minimum startup documents, core-documents register, responsibility RACI, governed-agent catalog, cross-cutting-module map, PMI process-group playbook, architecture mode selection guide, and operations metrics/monthly review.

Runtime behavior:

1. `generate_operations_package.py` writes deterministic UTF-8 Markdown and can run repeatedly without changing unchanged output.
2. The generator supports `--root`, `--package codex|one-person-company|all`, `--check`, and `--json`.
3. `check_operations_package_docs.py` validates required files, bilingual companions, required counts, required tailoring mode names, required I/T/O headings, and registry entries.
4. The checker supports `--root` and `--json`; it exits non-zero on validation failure.

## Tailoring Contract

| Mode | Use When | Lightweight Scope |
| --- | --- | --- |
| Full architecture | Cross-stage, cross-department, external customer, revenue, compliance, security, publication, rollback, durable-state, or multi-agent work | Whole project is governed end-to-end |
| Whole-project lightweight | Low-risk internal exploration, disposable experiment, no external commitment, no durable-state impact, no publication | Entire project may be lightweight |
| Phase-local lightweight | Overall project matters, but one phase has low uncertainty and limited blast radius | Only that phase is lightweight |
| Module-level lightweight | Single module or document family is low risk while surrounding areas remain governed | Only that module is lightweight |
| Hybrid architecture | Most real work, especially when strategy/risk/revenue/publication remain material but discovery or content work can stay light | Complete governance for critical layers, lightweight treatment for low-risk phases/modules |

Every tailoring decision record must state why the selected mode is not heavier or lighter and list escalation triggers.

## Process-Group I/T/O Contract

Every execution-facing generated document must include `Inputs`, `Tools And Techniques`, and `Outputs`. Every Chinese companion must include equivalent localized headings. The checker rejects missing headings in required generated package files.

## Collaboration Plan

- Stage A: leader session plus advisory experts; no durable/persistent team because the frozen plan does not yet exist.
- Stage B: after Stage A is on local `main`, adopt durable/persistent execution when the preflight confirms a ready lane and the work remains split into 2+ independent slices.
- If durable team tooling is blocked, use native subagents with disjoint ownership: runtime/checker/test worker for `tools/` and `test/`; documentation/registry worker for generated docs and registry; leader for fan-in, validation, commit, local-main integration, cleanup, and remote-publication stop.

## Stage B Validation Plan

Focused validation:

```powershell
python .	ools\generate_operations_package.py --root . --package all --check --json
python .	ools\check_operations_package_docs.py --root . --json
python .	ools\ci
un_python_tests.py --root . --pattern operations_package_docs.test.py
```

Full local integration gates:

```powershell
openspec validate generate-operations-package-runtime-20260620 --strict
python .	ools\check_document_pair_policy.py --root . --base-ref main --json
python .	ools\check_precommit_update_archive.py --root . --json
python .	ools
un_openspec_guard.py --root . --tool codex --json
powershell -NoProfile -ExecutionPolicy Bypass -File .	ools\ci\local_gate.ps1 -StepTimeoutSeconds 1500 -Json
powershell -NoProfile -ExecutionPolicy Bypass -File .	ools\ci\local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json
```

After Stage B passes and is locally integrated, archive the OpenSpec change only if the stable spec sync and archive validation pass; otherwise record an explicit archive deferral.

## Assumptions

- The existing refreshed Business Management/PMP synthesis is sufficient for this operations-package runtime; Stage B does not re-extract raw PDFs/EPUBs.
- The first Stage B package uses registers and operating maps rather than fully writing all 48 or 60 future document bodies.
- Remote publication is not authorized by this plan.
- Generated documents are source-controlled Markdown, not ignored runtime cache.

## Current Status

<!-- CURRENT_STATUS_START -->
- Stage A plan-freeze package is integrated into local `main` at `459b28ad14f7d26f0a837d51318f006affc3c01f`.
- Stage B runtime/package implementation is integrated into local `main` at `7863c4dd8daaa3b113b57e83b5252e68220446b9`.
- OpenSpec closeout is being archived in `openspec/changes/archive/2026-06-20-generate-operations-package-runtime-20260620/` through a local-only closeout branch.
- Remote publication remains unauthorized.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Stage A: completed and merged into local `main`.
- Stage B: completed and merged into local `main`.
- Archive: complete the OpenSpec archive/sync closeout and stop at the remote-publication gate.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- `docs_bilingual/implementation_plans/operations_package_generation_and_runtime_plan.md` - frozen implementation plan and closeout evidence index.
- `tools/generate_operations_package.py` - deterministic operations-package generator.
- `tools/check_operations_package_docs.py` - generated package/tailoring/I/T/O/registry checker.
- `test/operations_package_docs.test.py` - focused regression tests registered in local CI.
- `openspec/changes/archive/2026-06-20-generate-operations-package-runtime-20260620/` - archived OpenSpec lifecycle evidence after closeout.
- `refs/backup/local-main/20260620-042238-before-ops-package-runtime-20260620` - rollback ref preserved before Stage B local-main integration.
<!-- EVIDENCE_INDEX_END -->
