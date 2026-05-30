---
doc_id: multi_plan_parallel_session_orchestration_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
---

# Multi-Plan Parallel Session Orchestration Plan

## Purpose

Create the parent orchestration plan for this plan family, rebuilding the covered implementation plans into smaller, claimable work packages. This file is not the global parent plan for every plan under `docs_bilingual/implementation_plans/`.
The target execution model is:

- this parent plan owns phase ordering, dependencies, integration gates, Work-Conserving admission, and hotspot leases only inside its plan family;
- each related child `implementation_plan` owns one executable slice;
- the same `implementation_plan` can have only one active session claim at a time;
- different plans can run in parallel when write scopes do not conflict or have explicit serialization, even when they do not share the same parent plan;
- local `main` writes remain serial; the later target is for the session holding the `local-main-retire` lock to merge only its own ready branch instead of relying on a fixed main-session controller.

## Scope Decision

- Level: project-level governance for `D:/PythonProject_langgraph`.
- Reuse shape: generic and portable pattern that can later be copied to other repositories, but this Stage A does not edit user-level global config.
- Current stage: Stage A; create the parent documentation package only.
- Stage B type: after the user confirms this parent plan, create child implementation plans for this plan family.
- Stage C and later: implement plan locking, routing, durable-state, context-retention, Comet runtime, and Spec Kit boundary work through this plan family's child plans.
- Parent scope: this parent plan coordinates only implementation plans whose front matter `parent_plan` points to this file, or whose body explicitly lists them as source, split, or integration targets for this plan family.
- Unrelated plans: other implementation plans do not become children of this parent merely because they live under `docs_bilingual/implementation_plans/`; they may have no parent plan or belong to another parent plan.
- New-session reading: new sessions do not read this file by default; they read it only when they handle this file, its child plans, its task/evidence sections, or plans listed in this file's phases or batches.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Source Plans Covered

This parent plan coordinates the following existing plans inside this plan family without replacing their detailed content; plans that are not listed and do not declare `parent_plan` pointing to this file are not governed by this parent plan:

1. automatic_orchestration_routing_enforcement_plan - defines automatic collaboration routing, activation traces, expert lifecycle evidence, and durable-team thresholds.
2. codex_user_level_context_retention_canary_plan - protects cold-start context retention, canary literal placement, mojibake detection, and replay filtering.
3. codex_user_level_cross_session_durable_state_isolation_plan - isolates repo-local durable state, selectors, backend readiness, and cross-session durable artifacts.
4. comet_runtime_agile_focus_area_plan - adds Comet management records, phase checklist gates, and Monitoring return transitions.
5. implementation_plan_confirmation_gate - requires a committed active implementation-plan file before non-document implementation can start; here "confirmation gate" means a blocking checkpoint that stops execution until the user confirms the committed plan file.
6. codex_governance_session_visibility_and_plan_lock_plan - adds Chinese routing trace visibility, main-session escalation visibility, Superpowers evidence, Spec Kit boundaries, and plan locks.
7. pi_plugin_codex_user_level_sidecar_plan - provides the Pi family, Codex-to-Pi sidecar, and oh-my-pi reference-only boundary.
8. user_level_mcp_skills_browser_cli_governance_plan - provides the low-token, receipt-first governance boundary for MCP, skills, browser, OpenCLI, and CLI harness lanes.

## Non-Goals

- Do not implement runtime, checker, helper, or test changes during Stage A.
- Do not create all child implementation plans during Stage A.
- Do not install GitHub Spec Kit or run `specify init`.
- Do not start OMX, LangGraph, or a persistent durable team for this documentation package.
- Do not allow multiple sessions to write the same child implementation plan at the same time.
- Do not make this file a required cold-start read for every new session.
- Do not make this file the global parent plan or runtime control plane for unrelated implementation plans.
- Do not push to GitLab or GitHub unless the user explicitly requests remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Stage: Phase 2+ parallel-execution governance alignment
Owner session: `codex-align-complete-flow-parent-plans-20260530`, claiming the parent-index child plan to update this parent-plan family execution semantics.
Current gate: this package only synchronizes governance documents; after checker runs, local commit, and local `main` integration, it must stop at the remote publication gate.
Phase 0 note: inventory and parent-index closure has completed and entered local `main`; remote baseline `014b0bf` includes the Phase 0 publication state.
Phase 1 note: the construction safety base, ROB runtime/checker, self-retire helper, and complete-flow governance have entered local `main`; `7e47af8` makes the repository-root complete local commit flow the HOW contract for multi-session automatic local commit and local-main integration.
Phase 2+ admission: Phase 0 no longer blocks Phase 2; every eligible session may enter in Work-Conserving fashion, hotspot files serialize through hotspot leases, and local `main` writes serialize through `local-main-retire.lock`.
Remote state: local `main` currently leads the GitLab/GitHub remotes; remote publication, MR, merge, or GitHub sync still requires explicit user approval.
<!-- CURRENT_STATUS_END -->

## Execution Model

### Hierarchy Architecture

This plan uses a two-level implementation-plan structure inside this plan family. Only implementation plans whose front matter `parent_plan` points to this parent plan, or whose body explicitly lists them as part of this plan family, are sibling child plans; `parent_parallel_orchestration_index_plan` is an index-maintenance child plan, not a second-level parent. Unrelated implementation plans may have no parent plan or belong to another parent plan.

```text
Level 1: parent plan / master map
`-- multi_plan_parallel_session_orchestration_plan.md
    |-- Phase 0 / Batch 1 child: plan_inventory_registry_alignment_plan.md
    |-- Phase 0 / Batch 1 child: parent_parallel_orchestration_index_plan.md
    |   `-- note: index-maintenance child plan; it owns no lower-level implementation_plan files.
    |-- Phase 1A / Batch 1 child: complete_local_commit_flow_scheduler_reorder_buffer_plan.md
    |-- Phase 1-6 children: other sibling child implementation plans
    |-- Phase 7 / Batch 5 child: parallel_plan_docs_registry_integration_plan.md
    |-- Phase 7 / Batch 5 child: parallel_plan_checker_ci_integration_plan.md
    `-- Phase 7 / Batch 5 child: parallel_plan_openspec_comet_archive_plan.md
```

This hierarchy diagram applies only to this plan family; it is not the global hierarchy for every implementation plan under `docs_bilingual/implementation_plans/`.

`Phase`, `Stage`, and `Batch` classify this plan family's work topic, lifecycle state, and creation/integration batch; they are not global document-tree levels. `parent_plan` is an optional relationship, not a directory-wide required field. If a plan declares `parent_plan` pointing to this file, this file's Phase / Batch / parallelism / hotspot rules apply. If a plan has no `parent_plan`, or points to another parent, it is outside this parent-child structure.

### Session and Claim Rules

- Each implementation plan is the smallest claim unit. Child plans in this plan family follow this file's phase and batch rules; unrelated plans follow their own plan or global checkers.
- Session claims must declare the implementation-plan path before writes begin.
- The same implementation plan can have only one active claim at a time.
- Multiple sessions can run in parallel when they claim different implementation plans and their write scopes do not conflict or have explicit serialization; those plans do not need to share the same parent plan.
- Hotspot files such as `docs_bilingual/docs_registry.yaml`, CI manifests, shared checkers, `comet-state.sh`, `comet-guard.sh`, and parent-plan files must have an explicit owner.
- Each session owns its claimed implementation plan, worktree, branch, claim, receipt, ROB entry, local commit, and local `main` integration.
- This parent plan does not give one main session runtime control over other sessions.
- Local `main` writes must remain serial; the later target is to protect each merge with a `local-main-retire` lock, where the lock holder merges only its own ready candidate package.

### Work-Conserving Session Admission

- Do not encode a fixed per-phase session cap as governance.
- A phase admits every eligible implementation_plan/session: active status, no active claim, dependencies satisfied, clean worktree, and either a disjoint write set or an explicit hotspot lease.
- Provider pacing, CPU, memory, terminal count, failed gates, stale bases, and retire queues are resource backpressure. They throttle runtime scheduling but do not lower the governance admission rule.
- Hotspot leases and the local-main retire lock serialize shared writes; they are leases/locks, not global phase caps.
- Phase 1A has added a commit reorder-buffer rule: sessions may finish out of order; the later target is to move local `main` retirement from fixed leader ownership to session-owned self-retire protected by the `local-main-retire` lock.
- A phase must pause before crossing into the next phase if child plans have unresolved claims, dirty worktrees, failed local gates, unretired ROB entries, or unmerged local-main integration.

### Same-Machine Peer Session Local-Main Retire Target

This subsection captures the same-machine multi-session governance target. It is a governance contract for later child plans, checkers, and helpers; this Stage B document update does not yet implement runtime scripts.

#### Summary

- Replace the fixed "main Codex leader controls every retire" model with same-machine peer sessions plus serial local-main writes.
- Each session owns its own implementation plan, worktree, feature branch, claim, task receipt, ROB entry, local commit, local gates, and local-main integration attempt.
- `parent_plan` is optional metadata. It is validated only when declared; plans without it may be standalone or belong to another parent plan.
- A new session reads its target implementation plan, required registry/checker state, claim state, receipt state, and ROB state. It does not read this parent plan unless it is working on this file or on a plan governed by this file.
- Scope is same computer, same repository, multiple worktrees/sessions. Cross-computer remote locking is out of scope.
- Remote publication is still not automatic and still requires an explicit user request.

#### Governance semantic changes

- Any session may temporarily become the retire owner after it acquires the local-main retire lock.
- The retire owner merges only its own ready branch; it does not retire other sessions' branches.
- After success or failure, the retire owner must release the lock or record a clear failed/stale state.
- Parent plan files are hotspot files. If a session modifies a parent plan, it must claim that parent-plan write surface explicitly.
- Ordinary sessions do not need to read or modify a parent plan when their target implementation plan is unrelated to that parent.

#### Local-main retire lock contract

- Lock file: `.omx/locks/local-main-retire.lock`
- Planned helper: `tools/local_main_retire_lock.py`
- Planned commands:

```text
python tools/local_main_retire_lock.py acquire --root . --session-id <id> --branch <branch> --worktree <path> --entry-id <rob-entry> --ttl-minutes 120 --json
python tools/local_main_retire_lock.py release --root . --nonce <nonce> --json
python tools/local_main_retire_lock.py status --root . --json
```

Lock schema target:

```json
{
  "schema_version": 1,
  "lock_name": "local-main-retire",
  "owner_session_id": "session-a",
  "branch": "implement-x-session-a",
  "worktree": ".worktrees/implement-x-session-a",
  "entry_id": "rob-entry-id",
  "created_at": "...",
  "expires_at": "...",
  "nonce": "...",
  "status": "active"
}
```

Behavior requirements:

- Acquire uses atomic creation and fails closed when an unexpired active lock exists.
- Stale locks are not reclaimed by default; explicit `--reclaim-stale` is required before archiving the old lock and acquiring a new one.
- Release must match the stored `nonce`, preventing one session from deleting another session's lock.
- Lock files are runtime state and must not be committed to Git.

#### Self-retire local flow target

The later helper extension is `tools/complete_local_flow_to_remote_gate.py` with planned parameters:

- `--self-retire` - enables session-owned local-main retire mode.
- `--session-id <id>` - records which peer session owns this retire attempt.
- `--rob-entry-id <entry-id>` - links the merge attempt to the matching commit reorder-buffer entry.
- `--acquire-retire-lock` - requires the helper to acquire the local-main retire lock before merging.
- `--lock-ttl-minutes 120` - sets the lock expiry window for stale-lock reporting.

Required execution order:

1. Confirm the current worktree is a feature branch, not `main`.
2. Confirm the feature worktree is clean.
3. Run the feature local gate.
4. Run local MR review.
5. Acquire `local-main-retire.lock`.
6. After acquiring the lock, re-check that the primary root is clean and on local `main`.
7. Fetch and confirm local `main` is not behind `gitlab/main`.
8. Run claim, receipt, and ROB checkers.
9. Create a rollback backup ref.
10. Run `git merge --ff-only <feature-branch>`.
11. Run the post-merge local gate.
12. Update the ROB entry to `retired`, recording lock nonce, rollback ref, local main commit, and evidence.
13. Release the retire lock.
14. Stop at the remote publication gate.

#### Checker and gate targets

- `check_implementation_plan_claim_lock.py`: keep the same-plan single-active-claim rule; do not require `parent_plan` to exist.
- `check_worktree_task_receipt.py`: receipts record the session's own plan, branch, worktree, and lifecycle; do not require a parent plan.
- `check_commit_reorder_buffer.py`: add ROB field `retire_mode`, meaning the local-main retire ownership mode. Value `legacy_leader_serial` means the old fixed-leader serial merge path; value `self_retire_lock` means the peer session holding the retire lock merges its own branch. For retired `self_retire_lock` entries, require `retire_owner_session_id`, `retire_lock_nonce`, `rollback_ref`, `local_main_commit`, and non-empty evidence.
- Add `check_local_main_retire_lock.py` to validate lock JSON schema, active-lock uniqueness, and stale-lock reporting.
- Wire the new checker into OpenSpec guard and the local gate only when the corresponding runtime helper exists.

#### Verification targets for later implementation

- Two sessions acquiring `local-main-retire.lock`: first succeeds, second fails closed.
- Releasing with the wrong nonce does not release the lock.
- Stale lock cannot be reclaimed by default; `--reclaim-stale` archives the stale lock and acquires a new one.
- Implementation plans without `parent_plan` pass validation.
- A declared `parent_plan` path that does not exist fails validation.
- Two active claims for the same implementation plan fail validation.
- Two active claims for different implementation plans pass validation.
- A retired `self_retire_lock` ROB entry missing lock nonce fails validation.
- `complete_local_flow_to_remote_gate.py --self-retire --execute` acquires the lock before merge and releases it after merge.
- Merge failure releases the lock or records a clear failed/stale state; it must not silently leave an active lock behind.
- Local-main integration does not push GitLab, create MRs, or sync GitHub.

#### Assumptions

- This stage supports only same-machine multi-session / multi-worktree coordination.
- Each session retires only its own feature branch.
- Removing fixed main-session control does not remove serial protection for local `main` writes.
- Remote publication remains an explicit user-authorized step.


## Phase and Child-Plan Breakdown

### Phase 0: Inventory and Parent Orchestration

Purpose: establish the parent execution map and confirm registry health.

Candidate child plans:

1. `plan_inventory_registry_alignment_plan` - inventory current plan status, registry entries, anchors, and evidence-index health.
2. `parent_parallel_orchestration_index_plan` - maintain the parent phase map, child-plan registry, and dependency table.

Conditional follow-up: create a canary registry recovery child plan only if the inventory child plan finds a real canary registry, bilingual pairing, anchor, or evidence-index defect.

Admission: all eligible sessions may run after this parent plan is confirmed; registry and hierarchy hotspots require a single hotspot lease owner at a time.

### Phase 1: Construction Safety Base

Purpose: make parallel execution safe before runtime-heavy work begins. User-level install and update lanes, including Pi family or harness lanes, must remain receipt-first before they can be treated as active runtime surfaces.

Candidate child plans:

1. `complete_local_commit_flow_scheduler_reorder_buffer_plan` - Phase 1A early-foundation rule for ROB-style multi-session execution, hotspot fences, ready queues, and serial local-main retirement; later consumers will advance retirement from fixed leader ownership to session self-retire protected by the `local-main-retire` lock.
2. `formal_plan_confirmation_gate_runtime_plan` - enforce that chat-only plan confirmation is insufficient.
3. `portable_implementation_plan_claim_lock_plan` - implement child-plan single-active-session locking without requiring OMX or LangGraph.
4. `implementation_plan_registry_active_state_plan` - enforce active status, bilingual pairing, and docs registry consistency.
5. `main_session_escalation_visibility_plan` - add visible pending-approval/preflight surfaces for main-session escalation.

Admission: all eligible child plans may run; `docs_bilingual/docs_registry.yaml` requires one hotspot lease owner per batch.

### Phase 2: Context and UTF-8 Safety

Purpose: stabilize cold-start, replay, and mojibake boundaries before heavier orchestration automation.

Candidate child plans:

1. `context_retention_canary_literal_boundary_plan` - keep canary literals confined to startup summaries.
2. `startup_mojibake_utf8_recovery_plan` - harden mojibake detection and UTF-8 canonical recovery.
3. `session_replay_context_filtering_plan` - filter assistant/session replay surfaces so stale canary or mojibake does not re-enter prompts.
4. `launcher_payload_context_boundary_plan` - preserve launcher payload boundaries without mutating user-level config in this phase.

Admission: all eligible child plans may run; startup summary files require a hotspot lease and serialized writes.

### Phase 3: Durable State and Cross-Session Isolation

Purpose: make durable-state selection and inspection safe across repositories, worktrees, and sessions. Pi/harness state, receipts, rollback pointers, and sidecar artifacts must not leak across repository, worktree, or session boundaries.

Candidate child plans:

1. `repo_local_selector_ownership_plan` - enforce repository-local active selector ownership.
2. `durable_capability_readiness_projection_plan` - distinguish installed, enabled, selected, and ready.
3. `durable_smoke_adoption_gate_template_plan` - create the gate template and field checker before live durable smoke or apply-mode adoption.
4. `legacy_durable_residue_classification_plan` - classify stale `.omx/state` residue without auto-adoption.
5. `worktree_receipt_claim_lifecycle_plan` - define active, paused, completed, stale, and cleaned claim/receipt lifecycle.
6. `portable_no_backend_parallel_session_plan` - support Git/Python-only parallel sessions when OMX and LangGraph are unavailable.

Admission: all eligible child plans may run; `.omx/state` write scopes are serialized by repository and worktree hotspot lease.

### Phase 4: Automatic Routing and Stable Conversation Surfaces

Purpose: make collaboration routing automatic and auditable, and require user-facing routing-trace and updated-plan conversation surfaces to use Chinese field labels, Chinese explanations, and Chinese status wording. Routing and evidence records must distinguish Pi/harness sidecar evidence from final verification evidence owned by the current owner session; saved structured evidence may keep ASCII threshold tokens, blocker tokens, schema keys, file names, and CLI arguments.

Candidate child plans:

1. `chinese_routing_trace_conversation_surface_plan` - require stable user-facing `Routing trace` and `Updated Plan` labels, allow Chinese explanatory content, and preserve `Updated Plan` checklist/status semantics.
2. `routing_trace_structured_evidence_schema_plan` - keep machine-readable ASCII threshold/blocker tokens for saved evidence.
3. `prompt_independent_activation_parity_plan` - ensure routing does not depend on the user saying "parallel" or "experts".
4. `expert_lifecycle_timeout_pacing_evidence_plan` - treat timeout/stall/pacing as non-evidence and require bounded handling.
5. `langgraph_state_release_evidence_plan` - reject stale `running` state after completed LangGraph work.
6. `role_routing_fanout_write_ownership_plan` - enforce smallest-sufficient role selection and write ownership for fan-out.
7. `collaboration_evidenceguard_and_bilingual_openspec_surface_plan` - give the evidenceguard, fixtures, CI registration, and bilingual OpenSpec stable spec surface one serialized owner.

Admission: all eligible child plans may run; shared routing checkers and OpenSpec spec surfaces require hotspot leases.

### Phase 5: Comet Runtime Agile Management Loop

Purpose: implement the Comet runtime management loop after safety and visibility foundations are ready.

Candidate child plans:

1. `comet_management_record_bootstrap_plan` - create and validate management records.
2. `comet_phase_checklist_gate_plan` - require phase-specific checklist evidence before forward transition.
3. `comet_monitoring_return_transition_plan` - support Monitoring decisions that return to Open, Design, Build, or Verify.
4. `comet_superpowers_visibility_plan` - make Superpowers HOW-layer skill usage explicit in Comet phases.
5. `comet_runtime_policy_checker_alignment_plan` - align policy, OpenSpec specs, checker coverage, and integration gates.

Admission: all eligible child plans may run. `comet-state.sh` and `comet-guard.sh` require one hotspot lease owner at a time.

### Phase 6: Spec Kit Boundary

Purpose: prevent GitHub Spec Kit from becoming a competing governance layer. The same subordinate-adapter rule applies to oh-my-pi, Pi sidecar, and CLI harness references: they are reference or adapter surfaces, not project governance layers.

Candidate child plans:

1. `spec_kit_subordinate_adapter_governance_plan` - document Spec Kit as an optional subordinate adapter or template source.
2. `spec_kit_authority_guard_plan` - block `specify init --force`, `.specify/`, or governance-authority migration without a separate active plan.

Admission: all eligible child plans may run when their write sets are disjoint or their hotspots are leased.

### Phase 7: Integration, Verification, and Archive

Purpose: converge parallel work into serial local-main packages and archive completed OpenSpec work where applicable. Integration reports must state each Pi/harness lane as `reference-only`, `planned`, `on-demand`, or `active-candidate` before any runtime or user-level mutation is considered.

Candidate child plans:

1. `parallel_plan_docs_registry_integration_plan` - validate docs registry, bilingual pairs, and implementation-plan rules.
2. `parallel_plan_checker_ci_integration_plan` - validate checker, unit, and local CI coverage.
3. `parallel_plan_openspec_comet_archive_plan` - validate OpenSpec/Comet guard health and archive completed changes.

Delayed follow-up: publication readiness is not created as a Stage B child plan because remote publication is outside this scope until the user explicitly approves it.

Admission: all eligible validation sessions may prepare evidence in parallel, but Phase 7 integration hotspots and every local-main retire remain serial through their leases/locks.


## Compact Child-Plan Status Index

<!-- CHILD_PLAN_STATUS_INDEX_START -->
| Phase | Child plan | Status | Current evidence |
| --- | --- | --- | --- |
| Phase 0 | `plan_inventory_registry_alignment_plan` | implemented and integrated | `docs_bilingual/implementation_evidence/phase0_plan_inventory_registry_alignment_20260530.json`; no missing registered paths or bilingual companion paths; Phase 0 publication baseline is recorded at `014b0bf`. |
| Phase 0 | `parent_parallel_orchestration_index_plan` | implemented and continuing as index owner | Parent indexing is closed; this update uses the child plan to claim parent-family governance semantics and align later session integration to the repository-root complete local commit flow. |
| Phase 1A | `complete_local_commit_flow_scheduler_reorder_buffer_plan` | implemented and integrated | ROB runtime/checker package was integrated into local `main`; self-retire restoration is recorded at `898f9d0`; complete-flow governance alignment is recorded at `7e47af8`. |
| Phase 1 | `formal_plan_confirmation_gate_runtime_plan` | implemented and integrated | Phase 1 closure evidence remains in local git history and existing evidence index. |
| Phase 1 | `portable_implementation_plan_claim_lock_plan` | implemented and integrated | Portable claim lock is available as the baseline for single-plan single-session ownership. |
| Phase 1 | `implementation_plan_registry_active_state_plan` | implemented and integrated | Registry active-state and bilingual-pair guard behavior is covered by implementation-plan rules. |
| Phase 1 | `main_session_escalation_visibility_plan` | implemented and integrated | Main-session escalation visibility is part of the Phase 1 closure package. |
| Phase 2 | `session_replay_context_filtering_plan` | implemented and locally integrated | Legacy session replay context filtering entered local `main` at `cbc73c7`. |
| Phase 2 | `context_retention_canary_literal_boundary_plan` | implemented and locally integrated | Context-retention canary literal-boundary checking entered local `main` at `b779d51`. |
| Phase 2 | `launcher_payload_context_boundary_plan` | implemented and locally integrated | Launcher payload file-backed boundary hardening entered local `main` at `6f1ef48`. |
| Phase 2 | `startup_mojibake_utf8_recovery_plan` | implemented and locally integrated | Startup mojibake recovery source-report repair entered local `main` at `43d3ae9`. |
<!-- CHILD_PLAN_STATUS_INDEX_END -->

## Dependency and Phase 2 Admission Notes

<!-- PHASE_ADMISSION_NOTES_START -->
- Phase 0 is complete and no longer the current Phase 2 blocker; later Phase 2+ sessions only need their own implementation plan to be `status: active`, no conflicting active claim, satisfied dependencies, a clean worktree, and either a non-conflicting write set or an acquired hotspot lease.
- Phase 1 remains the safety base for later stages: plan confirmation, claim locking, registry active-state checks, ROB ordering, self-retire lock behavior, and the repository-root complete local commit flow must remain available.
- Phase 2+ child sessions run in Work-Conserving fashion; startup-summary, UTF-8/mojibake, docs registry, OpenSpec stable spec, CI manifest, and checker-schema hotspots require one explicit serialized owner.
- Local `main` integration is not fixed-main-session controlled; the session holding `local-main-retire.lock` may self-retire only its own ready candidate package.
- Remote publication is not a phase-admission requirement; unless the user explicitly requests remote publication, every session stops at the remote publication gate after local `main` integration.
<!-- PHASE_ADMISSION_NOTES_END -->

## Stage B Creation Rules

When Stage B starts, child plans must be created in batches:

- Batch 1: Phase 0 and Phase 1 child plans, including the Phase 1A complete-flow scheduler/ROB child plan as an early safety-foundation supplement.
- Batch 2: Phase 2 and Phase 3 child plans.
- Batch 3: Phase 4 child plans.
- Batch 4: Phase 5 and Phase 6 child plans.
- Batch 5: Phase 7 integration child plans.

Each child plan must include:

- YAML front matter with `doc_id`, `lang`, `status: active`, `doc_class: implementation_plan`, and bilingual companion metadata.
- CURRENT_STATUS anchors record the current stage/checkpoint, TASK_BACKLOG anchors record checkbox work items, and EVIDENCE_INDEX anchors record lightweight commit/report references; these anchors are stable HTML comments used by scripts for targeted updates.
- Explicit file ownership and hotspot serialization notes.
- Work-Conserving admission rule, hotspot lease requirements, resource backpressure notes, and validation gates for that child or phase.
- Local validation commands and expected gating behavior.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Stage A: create the English ASCII parent implementation plan.
- [x] Stage A: create the Chinese companion parent implementation plan.
- [x] Stage A: register the parent plan in `docs_bilingual/docs_registry.yaml`.
- [x] Stage A: commit the parent documentation package with a Chinese commit message.
- [x] Stage A: integrate the parent documentation package into local `main`.
- [x] Stage A: stop and ask the user to confirm this parent plan before Stage B child-plan creation.
- [x] Stage B: create Batch 1 child implementation plans for Phase 0 and Phase 1.
- [x] Stage B: create Batch 2 child implementation plans for Phase 2 and Phase 3.
- [x] Stage B: create Batch 3 child implementation plans for Phase 4.
- [x] Stage B: create Batch 4 child implementation plans for Phase 5 and Phase 6.
- [x] Stage B: create Batch 5 child implementation plans for Phase 7 integration.
- [x] Stage B parent revision: add the two-level hierarchy diagram and absorb Pi family / oh-my-pi / CLI harness reference-only boundaries into this parent plan.
- [x] Stage C: implement portable child-plan claim locking after child plans are confirmed.
- [x] Stage B Batch 1 supplement: create the Phase 1A complete-flow scheduler/ROB child plan and update complete local commit-flow governance.
- [x] Stage B parent-scope revision: narrow this parent plan semantics so it governs only this plan family and does not control unrelated implementation plans.
- [x] Stage B parent-scope revision: clarify that `parent_plan` is an optional local relationship and that new sessions do not read this file by default.
- [x] Stage B parent-scope revision: structurally record the same-machine peer session self-retire target, lock contract, checker targets, verification targets, and assumptions.
- [x] Stage B parent revision: replace fixed per-phase session caps with Work-Conserving all-eligible session admission, hotspot leases, resource backpressure language, and ROB-backed serial local-main retire.
- [x] Stage A recovery: record that the self-retire runtime source commit exists but current local `main` is missing the runtime files; stop before non-document recovery.
- [x] Stage B runtime recovery: restore self-retire runtime helper/checker behavior and integrate it into local `main` at `898f9d0`.
- [x] 2026-05-30 complete-flow alignment: align this parent-plan family and its child plans to session-owned self-retire, ROB, `local-main-retire.lock`, and the remote-publication gate after local-main integration.
- [x] Phase 0 closure: close the inventory registry alignment child plan and the parent orchestration index child plan before Phase 2 admission.
- [x] Later stages: the Phase 0 closure package has entered local `main`; Phase 2 context and UTF-8 safety child plans have started under the Work-Conserving model and several have entered local `main`.
- [x] Phase 4 parent/child governance update: extend conversation-surface coverage from routing traces to both `Routing trace` and `Updated Plan`, keep those labels stable, preserve `Updated Plan` checklist/status semantics, and preserve machine-readable ASCII tokens in saved evidence.
<!-- TASK_BACKLOG_END -->

## Acceptance Criteria

Stage A acceptance:

- English primary parent plan exists and is ASCII-only.
- Chinese companion parent plan exists.
- `docs_bilingual/docs_registry.yaml` registers the pair as `doc_class: implementation_plan` and `status: active`.
- The parent plan lists phases, candidate child plans, dependency order, Work-Conserving admission, and hotspot serialization rules.
- Stage A uses a Chinese commit message.
- Stage A integrates into local `main`.
- Stage A does not change runtime, checker, helper, or test behavior.
- The assistant stops before Stage B and asks the user to confirm this parent plan.

Stage B acceptance after later confirmation:

- Child plans are created as independent claim units.
- No child plan is left without bilingual pairing or registry entry.
- Each child plan declares file ownership, Work-Conserving admission constraints, hotspot lease requirements, and validation gates.
- No non-document implementation starts before the relevant child plan is confirmed.
- Phase 1A records scheduler/ROB governance before later multi-session runtime execution.
- This parent plan explicitly governs only this plan family; unrelated implementation plans may have no parent or belong to another parent.
- New sessions do not read this file by default unless they handle this file, its child plans, or plans listed by this file.
- The later same-machine multi-session target is for sessions to own their own commits and local `main` integration while `local-main-retire` locking keeps local `main` writes serial.
- Phase 4 child plans must write user-facing routing-trace and updated-plan examples in Chinese; internal tool names, schema keys, threshold tokens, blocker tokens, file names, and CLI arguments may remain ASCII.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-05-30 Phase 4 stable-label correction: branch `implement-routing-updated-plan-fixed-labels-20260530c` updates this parent plan and the `chinese_routing_trace_conversation_surface_plan` child plan after user correction: `Routing trace` and `Updated Plan` remain English user-facing labels, `Updated Plan` remains checklist/status-based, and Chinese explanatory content remains allowed; remote publication remains unauthorized.
- 2026-05-30 Phase 4 conversation-surface governance update: branch `chinese-routing-updated-plan-20260530` expanded coverage from routing traces to both routing traces and updated plans; its earlier label-localization wording is superseded by the stable-label correction above; remote publication remains unauthorized.
- 2026-05-30 complete-flow alignment package: branch `align-complete-flow-parent-plans-20260530` is claimed by `codex-align-complete-flow-parent-plans-20260530` through `parent_parallel_orchestration_index_plan`, and ROB entry `rob-align-complete-flow-parent-plans-20260530` records the parent-plan-family documentation package; this package aligns the parent plan and child plans that declare `parent_plan` pointing here with the repository-root complete local commit flow: session-owned self-retire, `local-main-retire.lock`, and the remote publication gate.
- 2026-05-30 Phase 0 closure package: closed `plan_inventory_registry_alignment_plan` and `parent_parallel_orchestration_index_plan` in branch `phase0-plan-index-closure-20260530`; machine-readable inventory evidence is `docs_bilingual/implementation_evidence/phase0_plan_inventory_registry_alignment_20260530.json`; Phase 2 remains blocked until this package is locally gated, locally reviewed, and merged to local `main`.
- 2026-05-30 self-retire runtime restoration: local `main` includes the restored self-retire runtime helper/checker package at `898f9d0`, replacing the earlier recovery-pending note from `b4af80f`.
- 2026-05-29 Stage A recovery package: recorded that local `main` at `b4af80f` did not contain the self-retire runtime helper/checker even though source commit `867f882` existed on `decentralize-session-self-retire-20260529`; this was later resolved by `898f9d0`.
- 2026-05-29 parent-scope revision: structurally absorbed the same-machine multi-session self-retire governance conversation, clarifying that this file remains this plan family's parent plan but does not control unrelated implementation plans; added optional local `parent_plan`, non-default new-session reading, session-owned self-retire, and `local-main-retire` lock follow-up targets.
- 2026-05-29 Phase 1 closure: Phase 1 child plans are implemented, integrated into local `main`, and verified; evidence commits include `4479593`, `e81d840`, `fb3ad75`, `54a965d`, and `e23c40b`; post-ROB local gate passed before this closure update.
- 2026-05-29 Stage B Batch 1 supplement: added the Phase 1A complete-flow scheduler/ROB child plan, updated the repository-root complete local commit-flow document, linked portable claim/receipt child plans as downstream consumers, and later integrated the ROB runtime/checker package into local `main` at `4479593`.
- 2026-05-28 Stage C local integration: portable child-plan claim locking was fast-forwarded into local `main`; post-merge local gate passed; remote publication is not approved yet.
- 2026-05-28 Stage C validation: portable child-plan claim locking passed focused tests, local gate, and local MR review on branch `implement-portable-plan-claim-lock-20260528`; local `main` integration has since completed as recorded above.
- 2026-05-28 Stage C entry: portable child-plan claim locking began through `portable_implementation_plan_claim_lock_plan`; work is isolated on branch `implement-portable-plan-claim-lock-20260528` before local-main integration.
- 2026-05-28 Stage B parent revision: added the two-level hierarchy diagram and absorbed Pi family / oh-my-pi / CLI harness reference-only boundaries from `pi_plugin_codex_user_level_sidecar_plan` and `user_level_mcp_skills_browser_cli_governance_plan`; commit recorded in local git history.
- 2026-05-28 Stage B child-plan creation package: created and registered 33 active child implementation plans with English primary and Chinese companion files; final commit is recorded in the assistant response and local git history.
- 2026-05-28 Stage A parent plan package: committed as `ac867ff` and integrated into local `main`; validation included `check_implementation_plan_rules.py --root . --json`, `check_precommit_update_archive.py --root . --json`, `tools/ci/local_gate.ps1 -StepTimeoutSeconds 600`, and `tools/ci/local_mr_review.ps1`.
<!-- EVIDENCE_INDEX_END -->
