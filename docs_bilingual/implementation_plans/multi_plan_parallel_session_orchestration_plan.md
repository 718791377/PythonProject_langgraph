---
doc_id: multi_plan_parallel_session_orchestration_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
---

# Multi-Plan Parallel Session Orchestration Plan

## Purpose

Create the parent orchestration plan for rebuilding six existing implementation plans into smaller, claimable work packages.
The target execution model is:

- one parent plan owns phase order, dependencies, integration gates, and session limits;
- each child `implementation_plan` owns one executable slice;
- one child `implementation_plan` may have only one active session claim at a time;
- different child plans may run in parallel when their write ownership is disjoint or explicitly serialized;
- local `main` integration remains serial and leader-owned.

## Scope Decision

- Level: project-level governance for `D:/PythonProject_langgraph`.
- Reuse shape: generic and portable pattern that can later be copied to other repositories, but this Stage A does not edit user-level global config.
- Current stage: Stage A documentation package only.
- Stage B type: create child implementation plans after the user confirms this parent plan.
- Stage C and later: implement plan locking, routing, durable-state, context-retention, Comet runtime, and Spec Kit boundary work through child plans.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Source Plans Covered

This parent plan coordinates the following existing plans without replacing their detailed content:

1. automatic_orchestration_routing_enforcement_plan - defines automatic collaboration routing, activation traces, expert lifecycle evidence, and durable-team thresholds.
2. codex_user_level_context_retention_canary_plan - protects cold-start context retention, canary literal placement, mojibake detection, and replay filtering.
3. codex_user_level_cross_session_durable_state_isolation_plan - isolates repo-local durable state, selectors, backend readiness, and cross-session durable artifacts.
4. comet_runtime_agile_focus_area_plan - adds Comet management records, phase checklist gates, and Monitoring return transitions.
5. implementation_plan_confirmation_gate - requires a committed active implementation-plan file before non-document implementation can start; here "confirmation gate" means a blocking checkpoint that stops execution until the user confirms the committed plan file.
6. codex_governance_session_visibility_and_plan_lock_plan - adds Chinese routing trace visibility, main-session escalation visibility, Superpowers evidence, Spec Kit boundaries, and plan locks.

## Non-Goals

- Do not implement runtime, checker, helper, or test changes during Stage A.
- Do not create all child implementation plans during Stage A.
- Do not install GitHub Spec Kit or run `specify init`.
- Do not start OMX, LangGraph, or a persistent durable team for this documentation package.
- Do not allow multiple sessions to write the same child implementation plan at the same time.
- Do not push to GitLab or GitHub unless the user explicitly requests remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: active
Stage: Stage A parent-plan documentation package
Owner session: main Codex leader session
Current gate: create and integrate this parent implementation plan, then stop for user confirmation
Stage B entry condition: user confirms this parent plan or its Chinese companion after local `main` integration
Last updated: 2026-05-28
<!-- CURRENT_STATUS_END -->

## Execution Model

### Session and Claim Rules

- Each child implementation plan is the smallest claim unit.
- A session claim must name the child implementation plan path before write work starts.
- A child implementation plan may have only one active claim at a time.
- Multiple sessions may run in parallel only when they claim different child plans.
- Hotspot files such as `docs_bilingual/docs_registry.yaml`, CI manifests, shared checkers, `comet-state.sh`, and `comet-guard.sh` must have an explicit owner for each batch.
- The main Codex leader session owns fan-in, validation, local `main` integration, and release recommendation.
- Local `main` integration is serial even when implementation sessions are parallel.

### Default Parallelism

- Default maximum parallel sessions per phase: 4.
- Burst maximum parallel sessions per phase: 6.
- A phase may use fewer sessions when write scopes overlap.
- A phase must pause before crossing into the next phase if child plans have unresolved claims, dirty worktrees, failed local gates, or unmerged local-main integration.

## Phase and Child-Plan Breakdown

### Phase 0: Inventory and Parent Orchestration

Purpose: establish the parent execution map and confirm registry health.

Candidate child plans:

1. `plan_inventory_registry_alignment_plan` - inventory current plan status, registry entries, anchors, and evidence-index health.
2. `parent_parallel_orchestration_index_plan` - maintain the parent phase map, child-plan registry, and dependency table.
3. `canary_plan_registry_recovery_plan` - decide whether and how the context-retention canary plan should be registered or repaired.

Parallelism: up to 3 sessions after this parent plan is confirmed.

### Phase 1: Construction Safety Base

Purpose: make parallel execution safe before runtime-heavy work begins.

Candidate child plans:

1. `formal_plan_confirmation_gate_runtime_plan` - enforce that chat-only plan confirmation is insufficient.
2. `portable_implementation_plan_claim_lock_plan` - implement child-plan single-active-session locking without requiring OMX or LangGraph.
3. `implementation_plan_registry_active_state_plan` - enforce active status, bilingual pairing, and docs registry consistency.
4. `main_session_escalation_visibility_plan` - add visible pending-approval/preflight surfaces for main-session escalation.

Parallelism: up to 4 sessions, with `docs_bilingual/docs_registry.yaml` owned by one session per batch.

### Phase 2: Context and UTF-8 Safety

Purpose: stabilize cold-start, replay, and mojibake boundaries before heavier orchestration automation.

Candidate child plans:

1. `context_retention_canary_literal_boundary_plan` - keep canary literals confined to startup summaries.
2. `startup_mojibake_utf8_recovery_plan` - harden mojibake detection and UTF-8 canonical recovery.
3. `session_replay_context_filtering_plan` - filter assistant/session replay surfaces so stale canary or mojibake does not re-enter prompts.
4. `launcher_payload_context_boundary_plan` - preserve launcher payload boundaries without mutating user-level config in this phase.

Parallelism: up to 4 sessions, with startup summary files serialized.

### Phase 3: Durable State and Cross-Session Isolation

Purpose: make durable-state selection and inspection safe across repositories, worktrees, and sessions.

Candidate child plans:

1. `repo_local_selector_ownership_plan` - enforce repository-local active selector ownership.
2. `durable_capability_readiness_projection_plan` - distinguish installed, enabled, selected, and ready.
3. `legacy_durable_residue_classification_plan` - classify stale `.omx/state` residue without auto-adoption.
4. `worktree_receipt_claim_lifecycle_plan` - define active, paused, completed, stale, and cleaned claim/receipt lifecycle.
5. `portable_no_backend_parallel_session_plan` - support Git/Python-only parallel sessions when OMX and LangGraph are unavailable.

Parallelism: up to 5 sessions, with `.omx/state` write scopes serialized by repository/worktree.

### Phase 4: Automatic Routing and Chinese Visibility

Purpose: make collaboration routing automatic, auditable, and Chinese-facing in conversation.

Candidate child plans:

1. `chinese_routing_trace_conversation_surface_plan` - require Chinese user-facing routing trace labels and explanations.
2. `routing_trace_structured_evidence_schema_plan` - keep machine-readable ASCII threshold/blocker tokens for saved evidence.
3. `prompt_independent_activation_parity_plan` - ensure routing does not depend on the user saying "parallel" or "experts".
4. `expert_lifecycle_timeout_pacing_evidence_plan` - treat timeout/stall/pacing as non-evidence and require bounded handling.
5. `langgraph_state_release_evidence_plan` - reject stale `running` state after completed LangGraph work.
6. `role_routing_fanout_write_ownership_plan` - enforce smallest-sufficient role selection and write ownership for fan-out.

Parallelism: up to 6 sessions, with shared routing checkers serialized.

### Phase 5: Comet Runtime Agile Management Loop

Purpose: implement the Comet runtime management loop after safety and visibility foundations are ready.

Candidate child plans:

1. `comet_management_record_bootstrap_plan` - create and validate management records.
2. `comet_phase_checklist_gate_plan` - require phase-specific checklist evidence before forward transition.
3. `comet_monitoring_return_transition_plan` - support Monitoring decisions that return to Open, Design, Build, or Verify.
4. `comet_superpowers_visibility_plan` - make Superpowers HOW-layer skill usage explicit in Comet phases.
5. `comet_runtime_policy_checker_alignment_plan` - align policy, OpenSpec specs, checker coverage, and integration gates.

Parallelism: up to 4 sessions. `comet-state.sh` and `comet-guard.sh` must have one owner at a time.

### Phase 6: Spec Kit Boundary

Purpose: prevent GitHub Spec Kit from becoming a competing governance layer.

Candidate child plans:

1. `spec_kit_subordinate_adapter_governance_plan` - document Spec Kit as an optional subordinate adapter or template source.
2. `spec_kit_authority_guard_plan` - block `specify init --force`, `.specify/`, or governance-authority migration without a separate active plan.

Parallelism: up to 2 sessions.

### Phase 7: Integration, Verification, and Archive

Purpose: converge parallel work into serial local-main packages and archive completed OpenSpec work where applicable.

Candidate child plans:

1. `parallel_plan_docs_registry_integration_plan` - validate docs registry, bilingual pairs, and implementation-plan rules.
2. `parallel_plan_checker_ci_integration_plan` - validate checker, unit, and local CI coverage.
3. `parallel_plan_openspec_comet_archive_plan` - validate OpenSpec/Comet guard health and archive completed changes.
4. `parallel_plan_publication_readiness_plan` - prepare release recommendation without remote publication unless explicitly approved.

Parallelism: validation may be parallel, but local `main` merge remains serial.

## Stage B Creation Rules

When Stage B starts, child plans must be created in batches:

- Batch 1: Phase 0 and Phase 1 child plans.
- Batch 2: Phase 2 and Phase 3 child plans.
- Batch 3: Phase 4 child plans.
- Batch 4: Phase 5 and Phase 6 child plans.
- Batch 5: Phase 7 integration child plans.

Each child plan must include:

- YAML front matter with `doc_id`, `lang`, `status: active`, `doc_class: implementation_plan`, and bilingual companion metadata.
- CURRENT_STATUS anchors record the current stage/checkpoint, TASK_BACKLOG anchors record checkbox work items, and EVIDENCE_INDEX anchors record lightweight commit/report references; these anchors are stable HTML comments used by scripts for targeted updates.
- Explicit file ownership and hotspot serialization notes.
- Maximum parallel session count for that child or phase.
- Local validation commands and expected gating behavior.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Stage A: create the English ASCII parent implementation plan.
- [x] Stage A: create the Chinese companion parent implementation plan.
- [x] Stage A: register the parent plan in `docs_bilingual/docs_registry.yaml`.
- [ ] Stage A: commit the parent documentation package with a Chinese commit message.
- [ ] Stage A: integrate the parent documentation package into local `main`.
- [ ] Stage A: stop and ask the user to confirm this parent plan before Stage B child-plan creation.
- [ ] Stage B: create Batch 1 child implementation plans for Phase 0 and Phase 1.
- [ ] Stage B: create Batch 2 child implementation plans for Phase 2 and Phase 3.
- [ ] Stage B: create Batch 3 child implementation plans for Phase 4.
- [ ] Stage B: create Batch 4 child implementation plans for Phase 5 and Phase 6.
- [ ] Stage B: create Batch 5 child implementation plans for Phase 7 integration.
- [ ] Stage C: implement portable child-plan claim locking after child plans are confirmed.
- [ ] Later stages: run child-plan work with at most six parallel sessions per phase and serial local-main integration.
<!-- TASK_BACKLOG_END -->

## Acceptance Criteria

Stage A acceptance:

- English primary parent plan exists and is ASCII-only.
- Chinese companion parent plan exists.
- `docs_bilingual/docs_registry.yaml` registers the pair as `doc_class: implementation_plan` and `status: active`.
- The parent plan lists phases, candidate child plans, dependency order, session limits, and hotspot serialization rules.
- Stage A uses a Chinese commit message.
- Stage A integrates into local `main`.
- Stage A does not change runtime, checker, helper, or test behavior.
- The assistant stops before Stage B and asks the user to confirm this parent plan.

Stage B acceptance after later confirmation:

- Child plans are created as independent claim units.
- No child plan is left without bilingual pairing or registry entry.
- Each child plan declares file ownership, session limit, and validation gates.
- No non-document implementation starts before the relevant child plan is confirmed.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Pending Stage A commit evidence. This plan stores only a lightweight evidence index.
<!-- EVIDENCE_INDEX_END -->
