---
doc_id: one_person_company_pmi_operations_refresh_plan
lang: en
canonical: docs_bilingual/implementation_plans/one_person_company_pmi_operations_refresh_plan.md
translation_of: null
doc_class: implementation_plan
status: active
---

# One-Person Company PMI Operations Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refresh the personal production one-person-company operations corpus from fresh Business Management, PMP, and lifecycle-document reading, then integrate the result through local `main` while stopping at the remote-publication gate.

**Architecture:** This is a two-stage local-main-first documentation rollout. Stage A freezes this plan as the implementation authority. Stage B performs a fresh source extraction pass, updates the one-person-company white paper, creates a dedicated one-person-company North Star, refreshes lifecycle/tailoring references, validates the bilingual documentation corpus, and integrates the implementation package into local `main`.

**Tech Stack:** Markdown, YAML registry, PowerShell local CI gates, Python source-extraction and governance checkers, git worktrees, `complete_local_flow_to_remote_gate.py`, Codex native experts, and LangGraph-backed durable-team routing.

---

<!-- CURRENT_STATUS_START -->
Status: active frozen plan for Stage B
Stage: Stage A validation complete; local-main integration handoff
Owner session: main Codex leader session
Current gate: local commit, local-main integration, then Stage B live implementation from latest local main
Remote publication: not authorized; stop at the remote-publication gate
<!-- CURRENT_STATUS_END -->

<!-- TASK_BACKLOG_START -->
- [x] Stage A: create the English ASCII primary implementation plan.
- [x] Stage A: create the Chinese companion implementation plan.
- [x] Stage A: register the plan pair in `docs_bilingual/docs_registry.yaml`.
- [x] Stage A: run document pair, governance, precommit, OpenSpec, local gate, and local MR review checks.
- [ ] Stage A: commit and integrate the frozen plan into local `main` (commit prepared; integration performed by local helper after this package is committed).
- [ ] Stage B: start a fresh implementation worktree from the integrated local `main`.
- [ ] Stage B: run fresh source extraction for `Business Management/`, `PMP/`, and `docs_bilingual/product_lifecycle/`.
- [ ] Stage B: update the one-person-company white paper, dedicated North Star, lifecycle maps, tailoring rules, and registry.
- [ ] Stage B: validate, commit, integrate local `main`, preserve rollback evidence, and stop before remote publication.
<!-- TASK_BACKLOG_END -->

<!-- EVIDENCE_INDEX_START -->
- Stage A planned evidence: this frozen plan pair, `docs_bilingual/docs_registry.yaml`, `python tools/check_document_pair_policy.py --root . --json`, `python tools/check_document_governance_rules.py --root . --json`, `python tools/check_precommit_update_archive.py --root . --json`, `python tools/run_openspec_guard.py --root . --json`, `tools/ci/local_gate.ps1`, `tools/ci/local_mr_review.ps1`, and `tools/complete_local_flow_to_remote_gate.py --execute --json`.
- Stage B planned evidence: fresh extraction manifests under ignored `.omx/state/langgraph/extraction/`, updated tracked synthesis documents, validation command output, rollback ref, completed claim, and `remote_publication_performed=false`.
<!-- EVIDENCE_INDEX_END -->

## 1. Scope And Source Authority

This plan implements the user request to update the `personal production one-person company operations` document family by freshly reading and synthesizing:

- `Business Management/`: business, product, growth, architecture, operations, discovery, and one-person-company references.
- `PMP/`: PMBOK, Process Groups, program management, portfolio management, PMO, and agile practice references.
- `docs_bilingual/product_lifecycle/`: current repository lifecycle, inventory, PMI, and tailoring documents.

The implementation must not rely on stale cache-only claims. It must run a fresh extraction pass and cite only aggregate extraction evidence in tracked docs. Raw extracted text remains local ignored evidence. Current tracked source-evidence authorities that must be checked before writing are `docs_bilingual/product_lifecycle/fresh_source_reading_evidence.md`, `docs_bilingual/product_lifecycle/business_management_source_synthesis.md`, and `docs_bilingual/product_lifecycle/durable_team_source_traceability.md`.

PMI authority order for this rollout:

1. PMBOK 8th Edition is primary for value delivery, project canvas, performance domains, AI-era project work, hybrid delivery, and tailoring.
2. Process Groups: A Practice Guide is the execution grammar authority for Initiating, Planning, Executing, Monitoring and Controlling, and Closing.
3. The Standard for Program Management, Fifth Edition is primary only when one-person-company work becomes a set of related initiatives with shared benefits, dependencies, sequencing, or capability increments.
4. The Standard for Portfolio Management, Fourth Edition is primary only when value, risk, runway, capacity, and competing business lines must be balanced.
5. Project Management Offices: A Practice Guide is primary for the solo PMO / chief-of-staff governance service model when a governance service layer is needed.
6. Agile Practice Guide is primary for adaptive discovery, MVP slicing, feedback loops, and lightweight reversible work.
7. PMBOK 6, PMBOK 7, and older local references are supporting sources for I/T/O vocabulary, principles, comparison, and backward-compatible interpretation.
8. PMI overlays do not replace the white paper, North Star, lifecycle maps, OpenSpec, docs registry, or repository checkers.

## 2. Target Deliverables

The implementation package must update or create the following tracked bilingual artifacts:

| Artifact | Required action |
| --- | --- |
| `docs_bilingual/whitepapers/personal_production_one_person_company_operations_whitepaper.md` and `.zh-CN.md` | Expand into the PMI-informed operating white paper. Keep the 12-layer target inventory and make each execution-facing layer explicit in Inputs / Tools and Techniques / Outputs form. |
| `docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.md` and `.zh-CN.md` | Create the dedicated one-person-company North Star pair. Keep it separate from the Codex durable-team platform North Star. |
| `docs_bilingual/product_lifecycle/one_person_company_inventory_map.md` and `.zh-CN.md` | Refresh the count authority and cross-link the white paper and new North Star. |
| `docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.md` and `.zh-CN.md` | Make the full/lightweight/hybrid tailoring policy decision-complete for one-person-company work. |
| `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.md` and `.zh-CN.md` | Record the one-person-company PMI overlay and latest-primary authority rule. |
| `docs_bilingual/product_lifecycle/business_management_source_synthesis.md` and `.zh-CN.md` | Refresh source synthesis with the new extraction run and the Business Management / PMP interpretation. |
| `docs_bilingual/product_lifecycle/fresh_source_reading_evidence.md` and `.zh-CN.md` | Update compact tracked extraction evidence if the new run supersedes the previous source-count boundary. |
| `docs_bilingual/product_lifecycle/durable_team_source_traceability.md` and `.zh-CN.md` | Preserve traceability from source families to affected lifecycle documents when refresh claims change. |
| `docs_bilingual/product_lifecycle/durable_team_process_group_contract.md` and `.zh-CN.md` | Keep process-group I/T/O terminology aligned with the one-person-company refresh. |
| `docs_bilingual/product_lifecycle/product_business_document_lifecycle.md` and `.zh-CN.md` | Check whether the product/business lifecycle needs a downstream one-person-company cross-reference. |
| `docs_bilingual/north_star_plan.md` and `.zh-CN.md` | Remain the Codex durable-team platform North Star content authority; do not convert them into downstream one-person-company truth. |
| `docs_bilingual/north_star/codex_cli_personal_production_durable_team_north_star.md` and `.zh-CN.md` | Remain discoverability aliases only. |
| `docs_bilingual/docs_registry.yaml` | Register the new North Star pair and this implementation plan pair. |

The implementation may add a small `fresh_source_reading_evidence` update only if existing evidence docs require a tracked summary of the new extraction run. It must not add raw book/source excerpts to tracked docs.

## 3. Tailoring Rules To Implement

The refreshed corpus must explicitly answer when to use each architecture depth:

| Tailoring outcome | Use when | Minimum governance surface |
| --- | --- | --- |
| Full architecture for affected scope | Customer-visible release, payments, regulated or sensitive data, external commitment, support obligation, repeated delivery, material revenue/risk, cross-system automation, or broad governed-agent execution. | Affected layers show Inputs / Tools and Techniques / Outputs, owner, risks, validation, release/rollback, and retrospective path. |
| Whole-project lightweight | The entire project is private, reversible, low-risk, has no external users, no money movement, no sensitive data, no support promise, no shared runtime, and no release commitment. | 12 minimal startup docs or their compact equivalents, explicit stop condition, one owner, and one review cadence. |
| Phase-local lightweight | Discovery, prototype, interview, content exploration, or spike is low-risk inside a larger governed effort. | Lightweight treatment is limited to that phase and must expand before revenue, customer, trust, release, or compliance impact. |
| Module-level lightweight | A bounded module is reversible and does not change the whole operating model. | Module I/T/O, owner, validation, rollback path, and coupling check. |
| Hybrid | Discovery is uncertain but likely delivery may affect production, users, revenue, trust, compliance, runtime behavior, or release safety. | Lightweight discovery followed by full controls for affected delivery layers before external impact. |

Default rule: use local lightness, not global informality. Expand only the layer, phase, or module carrying risk; expand the whole project only when coupling becomes systemic.

## 4. Process-Group Contract For This Refresh

| Process group | Inputs | Tools and Techniques | Outputs |
| --- | --- | --- | --- |
| Initiating | User request, current source-evidence boundary, affected authority docs, non-goals, local-only publication boundary | Scope-boundary review, authority-split review, no-runtime/no-remote framing | Refresh scope, success criteria, constraints, explicit remote-publication stop |
| Planning | White paper, lifecycle docs, PMI map, tailoring rules, docs registry, source traceability docs | Target-file mapping, tailoring review, validation design, collaboration threshold check | Frozen file list, section intent, acceptance checklist, validation path |
| Executing | Frozen plan, fresh extraction outputs, bilingual source files, worker handoffs | Tracked-doc editing only, bilingual pair alignment, raw-cache exclusion, leader-owned fan-in | Docs deltas, changed-path list, traceability updates, new North Star pair |
| Monitoring and Controlling | Current diff, registry, count authority, PMI authority order, source evidence claims | Authority drift check, count drift check, PMI misuse check, alias misuse check, registry mismatch check | Corrected diff, validation evidence, unresolved issue list or clean acceptance |
| Closing | Validation outputs, local MR review, local-main helper result, rollback ref, completed claim | Local-main-first integration, cleanup helper, lessons/next-cycle note | Local `main` commit, rollback evidence, completed claim, remote-publication gate stop |

## 5. Collaboration And Runtime Plan

Stage A freezes this plan only. It must not launch a durable team because the threshold is not met until this plan is integrated: `threshold_not_met:no_frozen_plan`. After this plan is merged into local `main`, Stage B must run as a fresh implementation worktree from latest local `main`.

- Native expert fan-out: use the smallest sufficient set. For bounded multi-face research, start with analyst/researcher-only read work and do not default to architect, planner, or writer. Prefer `researcher` for PMI/source synthesis and `verifier` for final completion review. Use `writer` only if the main session is unable to keep bilingual docs structurally aligned.
- Durable backend distinction: native expert bursts, `native_omx`, LangGraph, and persistent team are separate surfaces and must not be described as already-running durable team evidence.
- Durable team: because Stage B has a frozen plan and at least three independent slices, adopt durable-team routing with three parallel slices:
  - Worker A: fresh extraction and source-evidence synthesis.
  - Worker B: white paper and inventory map update.
  - Worker C: dedicated North Star, tailoring rules, and PMI reference map update.
- Leader responsibilities: current main Codex session owns docs registry, conflict resolution, bilingual pair alignment, validation gates, local-main integration, rollback evidence, and remote-publication stop.
- If native expert invocation is blocked, record `experts=blocked:platform_subagent_invocation_constraint` in the routing trace and continue with durable-team or leader-owned execution.
- If durable-team launch fails, do not abandon the task; continue with main-session execution and record the named blocker.

## 6. Stage B Work Breakdown

### Task 1: Create the implementation worktree and evidence receipt

**Files:** ignored `.omx/` receipt/claim files only.

- [ ] Create a fresh feature worktree from latest local `main`.
- [ ] Record worktree receipt and session claim under ignored `.omx/` with status `in-progress`.
- [ ] Confirm local `main` is not behind `gitlab/main` before starting.

### Task 2: Run fresh source extraction

**Files:** ignored `.omx/state/langgraph/extraction/` only.

- [ ] Run `tools/fresh_extract_sources.py` for `Business Management/`.
- [ ] Run `tools/fresh_extract_sources.py` for `PMP/`.
- [ ] Run `tools/fresh_extract_sources.py` for `docs_bilingual/product_lifecycle/`.
- [ ] Summarize counts by source root, format, source count, unit count, and extraction status.
- [ ] Treat unsupported non-PDF/EPUB/Markdown residue as out of scope unless the tool reports a source error for supported files.

### Task 3: Update source synthesis and PMI authority docs

**Files:** `business_management_source_synthesis.*`, `pmi_project_management_reference_map.*`.

- [ ] Add the new extraction-run summary and source boundaries.
- [ ] Explain how PMBOK 8, program, portfolio, PMO, and agile practice sources map to one-person-company operations.
- [ ] Preserve older-version use as support, not primary authority.

### Task 4: Update the white paper and inventory map

**Files:** `personal_production_one_person_company_operations_whitepaper.*`, `one_person_company_inventory_map.*`.

- [ ] Preserve the canonical counts: 12 layers, 5 virtual departments, 30 domains, 20 modules, 60 documents, 15 governed AI agents, 15 books, and 12 startup documents.
- [ ] Ensure each 12-layer row or subsection includes Inputs, Tools and Techniques, and Outputs.
- [ ] Add explicit PMBOK/program/portfolio/PMO/agile interpretation where it changes operating rules.
- [ ] Link the dedicated one-person-company North Star.

### Task 5: Create the dedicated one-person-company North Star

**Files:** `docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.md` and `.zh-CN.md`.

- [ ] Define the primary metric as validated operating-loop throughput.
- [ ] Define input metrics for customer evidence, revenue/cash, delivery stability, support load, learning cadence, and governed-agent review.
- [ ] Define guardrails for unreviewed AI commitments, runway, support risk, privacy/compliance risk, and over-documentation.
- [ ] Define decision thresholds that trigger full architecture, lightweight mode, module-level escalation, or stop/pivot.

### Task 6: Update tailoring rules and registry

**Files:** `lifecycle_tailoring_rules.*`, `docs_registry.yaml`.

- [ ] Add the one-person-company-specific full/lightweight/hybrid tailoring matrix.
- [ ] Register the new North Star pair.
- [ ] Keep English primary files ASCII-clean where existing policy expects it.

### Task 7: Validate, commit, and integrate locally

**Files:** no additional content files unless validation requires fixes.

- [ ] Run `python tools/check_document_pair_policy.py --root . --json`.
- [ ] Run `python tools/check_document_governance_rules.py --root . --json`.
- [ ] Run `python tools/check_precommit_update_archive.py --root . --json`.
- [ ] Run `python tools/run_openspec_guard.py --root . --json`.
- [ ] Run `powershell -NoProfile -ExecutionPolicy Bypass -File tools\ci\local_gate.ps1`.
- [ ] Run `powershell -NoProfile -ExecutionPolicy Bypass -File tools\ci\local_mr_review.ps1`.
- [ ] Commit the implementation package.
- [ ] Use `tools/complete_local_flow_to_remote_gate.py --execute --json` from the primary root to integrate local `main`.
- [ ] Confirm rollback ref, completed claim, cleanup, and `remote_publication_performed=false`.

## 7. Acceptance Criteria

The rollout is complete only when:

- This frozen plan pair is committed and integrated into local `main` before Stage B starts.
- Stage B docs cite a new fresh extraction run for all three source roots.
- The new one-person-company North Star pair exists, is registered, and is linked from the white paper or inventory map.
- The white paper and inventory map preserve the exact canonical counts.
- Execution-facing flow is written in Inputs / Tools and Techniques / Outputs form.
- Tailoring rules clearly distinguish full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, and hybrid mode.
- All local validation gates pass.
- Local `main` contains the final implementation commit and rollback evidence.
- Remote publication is not performed without explicit user approval.
