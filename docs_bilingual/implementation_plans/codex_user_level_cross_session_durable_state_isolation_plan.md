---
doc_id: codex_user_level_cross_session_durable_state_isolation_plan
lang: en
canonical: docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md
status: active
doc_class: implementation_plan
---

# Codex User-Level Cross-Session Durable State Isolation Plan

## Bilingual Alignment Status

- Completeness baseline: this English ASCII file and its Chinese companion are structurally aligned at the section-heading level.
- Chinese companion: `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md`.
- Alignment rule: keep both files active together. When wording diverges, use this English ASCII file as the implementation source of truth and update the Chinese companion in the same change.
- Current finding: both files already carry the same major heading structure; only the status note and alignment metadata needed normalization.

> Implementation status as of 2026-04-22: completed in repo source, validated in user-level mirrored helpers, and verified against the real `D:\PythonProject_OpenClaw` and `D:\PythonProject_langgraph` fixtures without mutating preserved legacy durable artifacts.

> Current implementation boundary as of 2026-05-02: keep the 2026-04-22 note as historical evidence that source and mirrored helpers exist, but do not treat it as proof that the final production-grade persistent team draft is complete. MR 1 through MR 5 are complete. MR 6 readiness review is now complete as a status-reconciliation slice: the automatic durable routing hookup already exists in the earlier P5 team-mode surfaces, so this queue must not open duplicate runtime implementation work.

## Current Bounded Implementation Queue

This queue preserves the decision made after the Phase 0 durable-state inventory: keep the final production persistent team plan as a north-star draft, and continue the active rollout through small GitLab-first MRs.

### Completed slices

- MR 1, active implementation boundary freeze: completed by `afdbd34` - documents that the active implementation line is limited to the user-level team mode plan and the cross-session durable-state isolation plan.
- MR 2, no-touch durable-state baseline: completed by `6f28c5f` - records a read-only inventory across the four local project roots without editing, moving, deleting, or activating any `.omx/state/` artifact.
- MR 3, status entrypoint hardening: completed by `6a99d7d` - adds `capability_readiness`, a per-backend status projection that distinguishes installed, enabled, selected, and ready for `native_omx` and `langgraph`.
- MR 4, activation selector safety rules: completed by `b303000` - hardens scoped selector validation so stale or cross-repository durable records remain inspectable but cannot drive automatic activation.
- MR 5, helper mirror source-of-truth rule: completed by `e1b3544` with publication closeout `e39fb21` - documents and tests that generated user-level helper mirrors are install artifacts, while repository source and each consumer repository's `.omx/state/` tree remain authoritative.
- MR 6, automatic durable routing readiness review: completed by this status-reconciliation slice - verifies that `codex-user-level-team-mode-automatic-team-routing` is the stable automatic-routing spec, `omx-team-auto.ps1` is the generated user-level automatic durable-team helper, and `test/install-codex-user-level-team-mode.test.ps1` is the test suite covering effective lane selection, selector safety, empty residue handling, and native_omx / LangGraph routing evidence.

### Completed slice detail: MR 4, activation selector safety rules

MR 4 hardens `.omx/state/selectors/active.json` - the repo-local active selector file that decides whether a future session may treat a durable backend as active. The selector must be scoped to the same repository or worktree, must not be released, and must carry a session identity before it can drive automatic activation.

MR 4 acceptance contract that is now part of the implemented baseline:

- Cross-repo selector rejection - an active selector copied from another repository must remain inspectable but must not activate LangGraph or native OMX in the current repository.
- Released selector rejection - a selector with `released_at` set must not remain active even if `routing_eligible` is still true.
- Backend-record dual-read only - `backend.json` and `codex-auto-managed-team.json` remain compatibility records for inspection, but they must not auto-route a future session unless the scoped selector is valid.
- Scoped-write preservation - helpers may write activation only under the current repository's own `.omx/state/selectors/` directory.

### Completed slice detail: MR 5, user-level mirrored helper source-of-truth rule

MR 5 documents and tests that user-level mirrored helpers are generated install artifacts, not the authoritative source of durable truth. Repository source remains under this repository, and each consumer repository keeps its own `.omx/state/` directory as its local durable truth.

MR 5 acceptance contract that is now part of the implemented baseline:

- Helper mirror provenance - generated user-level helpers must expose enough metadata or documentation for a cold-start reader to trace behavior back to repository source.
- Repo-local truth preservation - generated helpers may inspect the current repository, but they must not treat `D:\PythonProject_langgraph` as a global durable state root for other projects.
- Consumer-project isolation - `D:\PythonProject_OpenClaw`, `D:\PythonProject_CLIProxyAPI`, `D:\project`, and future projects may reuse user-level runtime and policy, but their repo-local `.omx/state/` directories remain independent.
- Install-artifact wording - docs and generated helper surfaces must call the user-level copy an install artifact, not the primary source of truth.

### Completed slice detail: MR 3, status entrypoint hardening

MR 3 should turn the already installed status surface into a cold-start-safe operator entrypoint. It must remain read-only.

Required source and helper surfaces:

- `tools/install-codex-user-level-team-mode.ps1` - the repository source script that generates user-level helper scripts and keeps installed helper behavior reproducible.
- `codex-durable-state-status.ps1` - the generated user-level read-only status script that summarizes the durable backend state for the current repository or worktree.
- `tools/langgraph_durable_orchestrator/` - the repository source directory for LangGraph compatibility projections and repo-local orchestration helpers.
- `.omx/state/langgraph/` - the repo-local LangGraph runtime-state directory that must remain project-local and must not be moved into the user-level shared venv.

MR 3 acceptance contract:

- `installed` - reports whether the relevant capability or helper is physically present, such as a generated script or shared LangGraph runtime.
- `enabled` - reports whether user-level policy currently allows that capability to be used.
- `selected` - reports whether the current repository, task, or selector chooses that backend for the current flow.
- `ready` - reports whether the installed, enabled, and selected capability also has the scoped state and prerequisites needed to start safely.
- `selected_backend` - reports the user-level backend selector, so a cold-start reader can see whether the global durable lane points at `native_omx` or `langgraph`.
- `capability_readiness` - reports per-backend readiness for `native_omx` and `langgraph`, including `user_level_selected` and `repo_state_selected` so global policy selection is not confused with repo-local tracked durable state.

MR 3 implementation patch scope:

- Keep `codex-durable-state-status.ps1` read-only; this generated status script may inspect repo-local durable state, but it must not create, edit, delete, or activate `.omx/state/` artifacts.
- Add readiness projection for `native_omx` and `langgraph`; `native_omx` is the worker-centric durable backend using generated OMX helpers, and `langgraph` is the graph-shaped durable backend using the shared LangGraph runtime plus repo-local state.
- Add tests for cold no-state, LangGraph-selected no-state, and tracked native state while the user-level selector still points at LangGraph.

MR 3 must add tests or fixtures that prove the checker can distinguish at least these cases:

- `D:\PythonProject_langgraph` fixture - preserved legacy LangGraph records are inspectable but not active routing truth when no scoped selector exists.
- `D:\PythonProject_OpenClaw` fixture - an active scoped LangGraph selector is stronger than a stale unscoped backend record, but it remains local to that repository.
- `D:\PythonProject_CLIProxyAPI` fixture - an active native OMX team state must be preserved and must not be classified as safe cleanup residue.
- `D:\project` fixture - ordinary HUD, notification, leader-nudge, or tmux hook state is not durable backend activation evidence.

### Completed slice detail: MR 6, automatic durable routing readiness review

MR 6 is a readiness-review closeout for this bounded durable-state queue, not a new runtime patch. The review confirms that the actual automatic durable routing hookup already exists in the team-mode implementation line:

- `openspec/specs/codex-user-level-team-mode-automatic-team-routing/spec.md` - the stable OpenSpec requirement file for automatic durable-team routing behavior.
- `tools/install-codex-user-level-team-mode.ps1` - the repository source script that generates user-level helper scripts, including `omx-team-auto.ps1`.
- `omx-team-auto.ps1` - the generated user-level helper that plans and, only with `-Apply`, executes native_omx or LangGraph durable routing actions.
- `test/install-codex-user-level-team-mode.test.ps1` - the PowerShell regression suite that verifies effective lane selection, selector rejection, empty residue handling, native_omx launch/reuse/switch/shutdown, and LangGraph graph-signal selection.
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - the active team-mode plan that already marks P5 automatic durable-team routing as implemented current state.

MR 6 acceptance contract that is now part of the implemented baseline:

- No duplicate hookup - this queue must not open another runtime implementation only to recreate the existing `omx-team-auto.ps1` helper behavior.
- Readiness before runtime exercise - any future live use must first name the target repository, phase, task, and operator consent boundary.
- No startup launch - even with automatic durable routing available, startup classification must not auto-launch a durable team.
- Backend-family clarity - worker-centric flows remain native_omx by default, while graph-shaped checkpoint, approval-gate, frozen-brief, or survivor-queue flows may select LangGraph.

### Next decision point after MR 6 readiness review

- Future live smoke or adoption gate: only if the user explicitly asks to exercise runtime behavior, open a separate reviewed change that runs `omx-team-auto.ps1` in a controlled target repository and records evidence without conflating that smoke with the final production-grade persistent team draft.

### Release 0.6 through R2.0 staged next-decision path

After MR 6 readiness review and the R0.6 gate definition, the next active work must stay smaller than a full durable-team runtime exercise.

Immediate next slices:

- `R0.6.0 Gate Template` - create the reusable smoke/adoption gate template before any command is run.
- `R0.6.1 Gate Field Checker` - add checker-backed enforcement that future gates declare `target_repository`, `phase`, `task`, and `operator_consent_boundary`.

Only after those two slices are landed should the roadmap proceed to:

- `R0.6.2 Read-Only State Sampling` - inspect one repository with read-only state surfaces.
- `R0.6.3 Dry-Run Routing Decision` - explain the routing decision without `-Apply`.
- `R0.6.4 Expected-Result Fixture` - capture the expected decision as a regression fixture.
- `R0.6.5 Cross-Project Read-Only Review` - repeat the read-only review on a consumer repository.

Later slices remain future work:

- `R0.7 Native OMX Adoption MVP` - future controlled native_omx adoption after R0.6 evidence exists.
- `R0.8 LangGraph Adoption MVP` - future controlled langgraph adoption for graph-shaped tasks.
- `R0.9 Lane Arbitration` - future conflict and selection rules for multiple enabled durable lanes.
- `R1.0 Personal Durable Team MVP` - future single-user, multi-project MVP.
- `R1.1 Multi-Project Consumer Rollout` - future rollout to consumer repositories without shared durable truth.
- `R1.2 Operational Hardening` - future cleanup, logging, MCP, config sentinel, and rollback hardening.
- `R2.0 Production Durable Team` - future production target, not current implementation.

Default boundary for all R0.6 slices:

- use read-only status and planning surfaces first
- do not modify `.omx/state/`; `.omx/state/` is the repo-local durable-state directory
- do not run `omx-team-auto.ps1 -Apply`; `-Apply` is the helper switch that executes the planned durable action
- do not promote the draft production durable-team plan into active implementation

### Explicit non-goals for the next decision point

- Do not implement the final `codex_cli_personal_production_durable_team_plan` draft as if it were already complete; that document remains the north-star target.
- Do not modify `C:\Users\lenovo\.codex\config.toml` - this user-level Codex config file is outside the next MR's source-of-truth scope.
- Do not delete user-level skills, Vercel plugin skills, browser automation skills, or repo-local `.omx/state/` artifacts.
- Do not merge durable state from `D:\PythonProject_OpenClaw`, `D:\PythonProject_CLIProxyAPI`, or `D:\project` into this repository.
- Do not start a durable team during this MR 6 readiness-review closeout; live durable-team exercise requires a separate explicit smoke or adoption-gate change.


## 1. Goal

Eliminate unintended cross-session interference in repo-local durable state for the user-level Codex orchestration line without mutating, deleting, or rekeying any existing active or historical session artifacts.

This plan is implementation-facing. Its purpose is to define how future sessions stop auto-inheriting stale repo-local durable selectors while existing sessions and historical records remain intact.

It should now be read as a shared fix for two layers at once:

- the user-level control surface and generated helper logic that many `PyCharm / Codex CLI` projects share on the same machine, user account, and Codex home
- the project-level repo-local state and source contract that each repository must keep as its own durable truth

This is therefore not only a user-level runtime fix. It is a shared plan for user-level activation logic plus project-level repo-local durable-state isolation.

## 2. Problem Statement

The current user-level runtime still treats the repository or worktree `.omx/state` root as the effective shared durable state scope.

That behavior is acceptable for inspection, but it is too coarse for activation.

The root problem is not only in helper routing. It sits at the boundary between:

- user-level helper logic that is shared across repositories
- project-level repo-local durable state that must remain authoritative inside each repository

Today:

- repo-local LangGraph `backend.json` can act as both an inspection summary and an implicit activation selector
- repo-local native `auto-team-*` directory presence can still influence automatic routing even when those directories are empty
- same-repo sessions can therefore inherit stale or unrelated durable state that was created by an earlier session

The result is cross-session coupling that is stronger than the intended operator model.

## 3. Repository-Grounded Failure Modes

### 3.1 `D:\PythonProject_OpenClaw` legacy fixture

Current observed state:

- a tracked LangGraph backend record exists under `.omx/state/langgraph/backend.json`
- that record points to a thread that is still in `freeze-plan`
- the paired interrupt record is `waiting_for_approval`
- the repository also contains many empty unmanaged native `auto-team-*` directories under `.omx/state/team`

Practical effect:

- automatic durable routing currently sees the tracked LangGraph thread first and treats it as the active durable lane
- empty native residue remains a latent native-lane blocker even though it is safe cleanup material rather than meaningful live state

### 3.2 `D:\PythonProject_langgraph`

Current observed state:

- no tracked LangGraph backend record is active
- the repository still contains empty unmanaged native `auto-team-*` directories

Practical effect:

- automatic durable routing can still report unmanaged native durable residue even when those directories contain no files

## 4. Non-Negotiable Safety Rules

The permanent fix must preserve the following invariants:

1. No existing file under either repository's legacy `.omx/state/` tree is edited, renamed, moved, or deleted during the immediate fix.
2. No active or historical session is auto-adopted into a new control model.
3. Existing historical LangGraph threads and native team artifacts remain inspectable.
4. Cleanup remains preview-first and limited to classes that are already defined as safe.
5. New activation logic must be additive and versioned.
6. If the runtime cannot determine a safe scoped activation target, it must fail closed rather than falling back to legacy shared selectors.

Safety-rule enforcement is not prompt-only. Every durable-state isolation rule that can affect activation, cleanup, scoped writes, cross-project reads, or publication must be registered in `tools/safety_rule_script_backing_registry.json` and must have either an executable script control or an explicit tracked gap. The aggregate checker is `tools/check_safety_rule_script_backing.py`, and `tools/run_openspec_guard.py` runs it as part of the repository guard.

## 5. Target State Architecture

The durable control surface should be split into three planes.

Within that split, one additional boundary must stay explicit:

- user-level control surfaces may inspect and route across many repositories on the same machine
- project-level artifact and activation truth must stay repo-local
- generated user-level mirrors may project or consume repo-local state, but they must not replace the repository as the source of truth

### 5.1 Artifact Plane

Keep the existing historical and runtime artifacts unchanged under:

- `.omx/state/langgraph/{threads,checkpoints,history,interrupts,store}` - repo-local LangGraph durable-state subdirectories for thread, checkpoint, history, interrupt, and store data.
- `.omx/state/team/*` - repo-local native OMX team-state directory tree.

These remain the recovery truth and the operator evidence store.

They are not the activation truth for future sessions.

### 5.2 Activation Plane

Add a new scoped selector and lease layer, for example:

- `.omx/state/selectors/active.json` - repo-local selector file that records the currently selected durable backend family.
- `.omx/state/selectors/leases/<session-scope-id>.json` - per-session selector lease file that prevents cross-session state confusion.

Only this plane may declare that a durable thread or team is active for a future session.

Minimum fields:

- `backend_family` - selector field naming the durable backend family, such as native_omx or langgraph.
- `selector_id` - selector field that gives the active selection record a stable identifier.
- `repo_root` - selector field that binds the selection to one repository root.
- `worktree_id` - selector field that distinguishes one worktree from another.
- `session_scope_id` - selector field that scopes the lease to one live session.
- `leader_session_lineage` - selector field that records the main leader session lineage.
- `acquired_at` - selector timestamp for when the lease was acquired.
- `last_heartbeat_at` - selector timestamp for the most recent lease heartbeat.
- `released_at` - selector timestamp for when the lease was released.
- `generation` - selector counter used to detect stale or superseded records.
- `routing_posture` - selector field that records the current routing posture for durable execution.

### 5.3 Inspection Plane

Keep legacy:

- `.omx/state/langgraph/backend.json` - LangGraph compatibility record for backend state inspection.
- `.omx/state/team/codex-auto-managed-team.json` - native OMX compatibility record for auto-managed team state inspection.

as read-only inspection and compatibility projections.

They may expose inspect or explicit resume pointers, but they must no longer implicitly activate durable state for unrelated future sessions.

## 6. Required Behavioral Changes

### 6.1 Empty Unmanaged Native Residue

Current behavior is too strict because any latest native team directory can be interpreted as unmanaged residue even when it is empty.

Required change:

- only non-empty unmanaged native team directories may force `manual-inspection-required`
- empty unmanaged native directories remain safe cleanup candidates
- empty directories must not block auto launch, reuse, or switch decisions

### 6.2 Legacy LangGraph Selector Dominance

Current behavior is too broad because any tracked `backend.json` with a `thread_id` can dominate future lane selection.

Required change:

- a legacy LangGraph backend record remains inspectable
- it is only eligible for automatic routing if it is explicitly marked as active or resumable by the new activation plane
- terminal, historical, or otherwise unscoped legacy records must not auto-route unrelated future sessions into LangGraph

### 6.3 Dual-Read, Scoped-Write

The new runtime model should behave as follows:

- read legacy v1 artifacts for inspection and compatibility
- write new activation state only through the scoped activation plane
- keep backend-family selection task-sensitive
- fail closed when scoped activation cannot be determined safely

## 7. Implementation Workstreams

The workstreams below must be read as a dual-layer rollout:

- repository source and repository tests define the durable-state contract
- user-level mirrors distribute that contract across shared entrypoints and helper surfaces

### 7.1 PowerShell Routing And Status Helpers

Update the user-level helper logic so that:

- empty unmanaged native residue no longer becomes a routing blocker
- legacy LangGraph backend records no longer count as active solely because `thread_id` exists
- inspectable durable state output distinguishes between:
  - legacy preserved artifacts
  - active scoped selectors
  - safe cleanup candidates
  - protected manual residue

### 7.2 LangGraph Durable Orchestrator Projection

Update the LangGraph backend projection so that:

- the backend record exposes a routing eligibility or routing posture bit
- the runtime can distinguish:
  - active resumable thread
  - historical preserved thread
  - terminal thread
  - missing or stale selector

### 7.3 Tests

Add or update tests for:

- empty unmanaged native directories do not trigger `manual-inspection-required`
- legacy `backend.json` remains inspectable but does not auto-dominate unrelated future sessions
- existing active sessions remain readable under dual-read mode
- missing scoped selector causes fail-closed behavior rather than implicit legacy activation

### 7.4 User-Level Generated Mirrors

After source changes land, regenerate or refresh the mirrored user-level helper scripts under `C:\Users\lenovo\.codex\bin` so behavior remains consistent across:

- routing policy
- durable state status
- durable state reconcile
- `omx-team-auto` - automatic durable-team launcher that reads the repo-local active selector before starting workers.
- compose-specific helper surfaces

## 8. Rollout Plan

### Phase 0: No-Touch Baseline

Before any rollout:

- capture read-only durable-state baselines for both repositories
- freeze direct filesystem cleanup of `.omx/state`
- classify all current residue as:
  - preserved active
  - preserved historical
  - safe empty
  - protected manual

### Phase 1: Source Implementation In `D:\PythonProject_langgraph`

Implement the additive scoped activation logic only in the source repository.

No user-level helper install yet.

This phase exists to keep project-level source and tests ahead of shared user-level mirrors.

### Phase 2: Validation Against Legacy Fixtures

Validate the new logic against preserved fixtures that represent:

- `OpenClaw` legacy fixture: tracked LangGraph thread plus empty native residue
- `langgraph` empty native residue only

The validation target is no false activation and no data mutation.

### Phase 3: User-Level Helper Rollout

Roll the new helper logic into the user-level generated scripts only after the source logic and tests pass.

This is the point where new sessions begin to observe the new behavior by default.

At this phase, the user-level layer is distributing a repository-defined contract. It is not redefining the repo-local durable truth.

Existing sessions also become capable of observing the new helper behavior once they re-enter routing, helper evaluation, or another configuration-read boundary.

### Phase 4: New-Session Adoption

New sessions may use the scoped activation plane immediately after rollout.

Existing live sessions keep the decision state they already hold until they reach a safe evaluation boundary, but they remain retrofit-capable on reload, restart, explicit user routing directive, or tracked durable-state detection.

### Phase 5: Later Cleanup Window

Only after the new activation model is stable:

- preview and optionally apply cleanup for empty unmanaged native residue
- keep legacy LangGraph thread artifacts preserved unless an explicit operator action archives or retires them under a later approved policy

## 9. Session Impact And Restart Policy

This implementation plan is designed so that both existing sessions and new sessions use the latest user-level configuration as much as technically possible while preserving stability for work that is already in progress.

Practical rule:

- source-only changes in `D:\PythonProject_langgraph` are not retroactive by themselves
- once a session re-enters routing, helper evaluation, or another configuration-read boundary, it should pick up the latest user-level behavior
- a session adopts the latest activation logic when it re-enters those evaluation paths, including on reload, restart, explicit user routing directive, or tracked durable-state detection
- reload, restart, or safe phase-boundary resume is only required when a live durable flow has already passed the point where its current decision state was resolved and cannot be switched safely in place

Therefore:

- new sessions should usually observe the latest activation logic immediately
- existing sessions should also move onto the latest user-level configuration at the next safe evaluation point instead of being treated as permanently excluded from it
- historical sessions remain preserved and inspectable
- existing live durable flows should still be restarted only at a safe phase boundary when an in-place switch would be unsafe

## 10. Success Criteria

This plan is complete only when all of the following are true:

1. A preserved legacy LangGraph backend record no longer auto-dominates unrelated future sessions.
2. Empty unmanaged native residue no longer blocks automatic native durable routing.
3. Existing active and historical artifacts remain readable and attributable.
4. New session-scoped activation writes are additive and versioned.
5. No direct mutation of legacy `.omx/state` is required to make the new model safe.
6. Repository source and repository tests remain the authority for the activation contract, while user-level mirrors remain only the shared execution and control surface.
7. Many `PyCharm / Codex CLI` projects on the same machine can reuse the same user-level helper layer without inheriting each other's canonical durable state.
