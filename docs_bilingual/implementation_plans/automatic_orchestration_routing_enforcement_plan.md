---
doc_id: automatic_orchestration_routing_enforcement_plan
lang: en
canonical: docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.md
translation_of: null
version: 1.0
status: active
plan_readiness: ready-for-implementation
doc_class: implementation_plan
owner: codex-orchestration
implementation_lane: prompt_independent_collaboration_parity
last_reviewed: 2026-05-27
---

# Automatic Orchestration Routing Enforcement Implementation Plan

> **For agentic workers:** REQUIRED WORKFLOW: use the full `/comet` cadence for later code implementation. Updating this document is not runtime evidence. Track all implementation tasks with checkboxes, run each task-level validation before moving on, and use Chinese commit messages.

**Goal:** Make Codex sessions evaluate collaboration from task shape, risk, phase, evidence, and thresholds rather than from whether the user typed phrases such as "use experts", "durable_team", or "persistent team".

**Architecture:** The main Codex session remains the leader. The activation check reads startup authority, capability chain, task phase, and durable state; then it chooses the smallest sufficient surface among main-session work, native experts, `native_omx`, LangGraph durable workflow, and persistent team; every final claim must map to auditable evidence.

**Tech Stack:** Codex startup policy, AGENTS.md, OpenSpec, Comet workflow, Python checkers, JSON/JSONL fixtures, repo-local `.omx` state, local CI, local MR review, Chinese commits, and local-main-first publication.

---

## 0. Review conclusion

The previous version compressed historical content, but it still read like a governance rule bundle. It was organized by policy topic and did not provide the worker-ready tasks, inputs, outputs, file ownership, validation boundaries, and rollback path expected from the newer implementation-plan structure. This version rewrites the plan in the same execution-ready style as `pi_plugin_codex_user_level_sidecar_plan.md` and `comet_runtime_agile_focus_area_plan.md`.

| Check | Verdict | Location |
| --- | --- | --- |
| Goals and non-goals | Complete | Section 2 |
| Expert / durable team / persistent team relationship | Complete | Section 1 |
| Codex activation behavior | Complete | Sections 3 and 4 |
| Repo-local source of truth | Complete | Section 5 |
| Evidence contracts | Filled | Section 6 |
| Task-level granularity | Filled | Section 7 |
| Readiness gates | Filled | Section 8 |
| Validation and local integration | Filled | Section 9 |
| Rollback and cleanup | Filled | Section 10 |
| Required governance updates | Filled | Section 11 |

Current status:

- This document is an active implementation plan and Phase 4 boundary, not durable or persistent runtime evidence.
- Phase 0-3 baseline work has historical implementation and archive evidence; this plan keeps the stable boundary without keeping long archive tables in the main flow.
- The default Phase 4 change id is `enforce-prompt-independent-collaboration-parity`; its P1 checker slice lands through `tools/check_orchestration_collaboration_evidenceguard.py`, fixture pairs, guard wiring, CI registration, and OpenSpec/spec updates.
- A single bilingual document-pair rewrite does not meet the persistent-team threshold; the main session should perform it directly and may use a verifier at close, but must not claim that a durable or persistent team ran.

## 1. Relationship model and naming boundary

| Name | Role in this plan | Runtime evidence | Boundary |
| --- | --- | --- | --- |
| Main Codex session | Leader, integrator, evidence absorber | Yes, as final accountable actor | Never replaced by a persistent leader pane |
| Native expert | Leader-side specialist thread | Only with spawn / wait / result / close / absorbed audit | Skill or profile invocation is not an expert |
| `native_omx` | Worker-centric durable lane | Requires selector, manifest, heartbeat, and worker lifecycle | Best for worker lifecycle, worktree isolation, and mailbox flow |
| LangGraph | Graph-shaped durable workflow lane | Requires thread state, checkpoints, briefs, and release records | Ready does not mean persistent team running |
| Persistent team | Threshold-gated worker team | Requires active selector, manifest, heartbeat, closed and absorbed records | Requires frozen plan plus 2+ independent execution slices, or stabilize with blocking issue |
| Skills / plugin profiles | Workflow instruction surface | No | They only change visible process context |
| OpenSpec / Comet | WHAT/HOW governance flow | Change-governance evidence, not worker runtime evidence | Cannot replace runtime audit |

Capability switches are interpreted as a dependency chain:

```text
subagent_routing != off
  -> oh_my_codex = on
    -> langgraph = on
      -> langgraph_ready = true allows backend_default=langgraph
```

Forbidden inferences:

- `backend_ready=true` does not imply persistent team running.
- `skill invoked` does not imply native expert running.
- `timeout`, `stall`, and `provider pacing` do not imply expert result evidence.
- Missing user collaboration phrases are not a valid reason to skip orchestration activation.

## 2. Goals and non-goals

Goals:

1. Run activation checks on first substantive work, resume, continue, phase change, `.omx` state detection, capability change, expert timeout or stall, and expansion to 2+ slices.
2. Produce the same routing decision for equivalent tasks with or without explicit collaboration phrases.
3. Separate `not_needed`, `candidate`, `selected`, `running`, `complete`, and `blocked` so readiness, plans, and timeouts are not reported as completion.
4. Make native expert lifecycle, durable/persistent evidence, LangGraph stale-running release, cold-start read order, and write ownership checker-backed.
5. Preserve local-main-first publication: local validation, local MR review, local `main` integration, and remote publication only after explicit authorization.

Non-goals:

- Do not force every small task into multi-worker execution.
- Do not auto-launch a persistent team during startup, read-context, boundary-freeze, or single low-risk document work.
- Do not report LangGraph ready as persistent team running.
- Do not treat this plan as runtime evidence.
- Do not rewrite the foundations of native Codex, oh-my-codex, OpenSpec, or LangGraph.
- Do not push GitLab or GitHub without a separate explicit remote-publication authorization.

## 3. Runtime architecture

```text
User request
  -> Codex leader reads startup authority and task context
  -> Orchestration activation check
  -> Capability chain and backend readiness inspection
  -> Task phase and slice count classification
  -> Evidence threshold evaluation
  -> Smallest sufficient lane decision
  -> Execution / delegation / durable workflow / main-session takeover
  -> Verification, fan-in, close, absorbed record
  -> Local commit, local gate, local MR review, local main integration
```

Minimum state words:

| State | Meaning | Minimum evidence |
| --- | --- | --- |
| `not_needed` | Current task does not meet threshold | Trace names `threshold_not_met:*` or task-shape reason |
| `candidate` | Collaboration may be needed but is not adopted yet | Slice analysis, adoption blocker, next required condition |
| `selected` | Lane has been selected | Selector / preflight / ownership plan |
| `running` | Worker or workflow is executing | Selector, manifest or thread state, heartbeat, lifecycle running |
| `complete` | Work completed and was absorbed | Result summary, close record, leader absorbed record |
| `blocked` | Cannot claim success | Named blocker, repeated blocking evidence, no completion claim |

Recommended activation trace:

```text
Routing trace:
phase=<define-target|read-context|freeze-plan|execute-parallel|integrate-converge|stabilize|verify-accept>
capability_chain=subagent_routing:<auto|manual|off> > oh_my_codex:<on|off> > langgraph:<on|off>
backend_default=<langgraph|native_omx|none>
backend_ready=<true|false|unknown>
experts=<none|analystxN|architect|planner|writer|verifier|blocked:<reason>|...>
durable_workflow=<not_needed|candidate|selected|running|complete|blocked>
persistent_team=<not_selected|not_needed|candidate|selected|running|complete|blocked>
why=<task-shape, threshold, blocker, or evidence reason>
```

## 4. Codex usage

Natural-language triggers:

```text
Check whether this plan is complete
Update this implementation plan and merge it into local main
Continue the current task
Use experts / durable_team / persistent team collaboration
Use LangGraph to continue this multi-phase work
```

Behavior rules:

- Ordinary single-document rewrite: run activation, usually report `persistent_team=not_selected:threshold_not_met:single_execution_slice`, and execute in the main session.
- Explicit experts: if native spawn is not exposed, report `experts=blocked:platform_subagent_invocation_constraint`; do not fabricate expert results.
- Explicit `omx`: if the task lacks a frozen plan plus 2+ slices, report the unmet threshold; if satisfied, use `omx-team-auto.ps1` or the matching native_omx lane.
- Explicit LangGraph: select it for graph-shaped multi-phase work when ready; for a single document edit, report that the durable workflow threshold is not met.
- Timeout or stall: inspect, redirect, respawn, hand off, or take over in the main session; never record success from silence.

## 5. Repo-local source of truth

| File or directory | Responsibility |
| --- | --- |
| `AGENTS.md` | Session and project orchestration authority surface |
| `docs_bilingual/project_startup_summary.*` | Cold-start read order, canary, repository posture |
| `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.*` | Activation policy, capability chain, hard directives, timeout evidence |
| `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.*` | This implementation plan and Phase 4 boundary |
| `openspec/specs/codex-user-level-orchestration-activation-policy/spec.*` | Stable WHAT requirements |
| `tools/check_orchestration_activation_policy.py` | Authority wording and forbidden reason guard |
| `tools/check_orchestration_trace_evidence.py` | Trace evidence validator |
| `tools/check_orchestration_collaboration_evidenceguard.py` | prompt-independent collaboration parity, cold-start read-order evidence, durable/persistent evidenceguard, expert lifecycle audit events, and LangGraph state release guard |
| `tools/check_capability_switch_chain.py` | Capability dependency guard |
| `tools/check_role_routing_directive_evidence.py` | Hard directive and role-routing guard |
| `tools/check_expert_lifecycle_wait_pacing_evidence.py` | Expert lifecycle wait and pacing guard |
| `tools/check_agent_skill_profile_surface_boundaries.py` | Native agent / skill / profile boundary guard |
| `tools/check_durable_artifact_state_surfaces.py` | Durable artifact and state surface guard |
| `tools/check_effective_lane_fit_evidence.py` | Backend family and task-fit guard |
| `tools/check_fanout_write_ownership_evidence.py` | Write ownership and one-backend-family guard |
| `tools/check_leader_session_scope_evidence.py` | Main-session leader scope guard |
| `tools/run_openspec_guard.py` | Repository guard aggregator |
| `tools/ci/ci_test_manifest.json` | Local gate test registry |

## 6. Evidence contracts

### 6.1 Cold-start read-order evidence

Goal: when a session claims it followed cold-start read order, it must show what it read, what it skipped, and why.

Minimum shape:

```json
{
  "schema_version": 1,
  "session_id": "...",
  "trigger": "first_substantive_work|resume|continue|phase_change",
  "read_order": [
    {"order_index": 1, "path": "docs_bilingual/project_startup_summary.md", "decision": "read", "read_mode": "full_text_utf8", "needed_for_current_task": true, "reason": "startup authority"}
  ],
  "summary_counts": {"read": 1, "skipped": 0}
}
```

Reject when startup summary is missing, skipped items lack reasons, full-read claims lack paths, or mojibake is observed without recovery. Checker surface: `tools/check_orchestration_collaboration_evidenceguard.py` validates saved `cold_start_read_order` JSON evidence.

### 6.2 Prompt-independent activation parity

Goal: equivalent tasks must produce equivalent routing decisions with or without explicit collaboration phrases.

Fixture set:

```text
test/fixtures/orchestration_prompt_independent_collaboration_parity/
  doc_update_without_collaboration_phrase.json
  doc_update_with_collaboration_phrase.json
  multi_slice_without_collaboration_phrase.json
  multi_slice_with_collaboration_phrase.json
  explicit_omx_without_threshold.json
  explicit_langgraph_single_slice.json
```

Reject when a missing user phrase is used as the skip reason, collaboration phrases bypass frozen-plan and slice thresholds, or LangGraph ready is reported as persistent team running. Checker surface: `tools/check_orchestration_collaboration_evidenceguard.py` validates prompt-independent collaboration parity fixture pairs under `test/fixtures/orchestration_prompt_independent_collaboration_parity/`.

### 6.3 Durable / persistent evidenceguard

Goal: final reports cannot claim durable or persistent teams ran without durable evidence.

| State | Required evidence |
| --- | --- |
| `selected` | Active selector, backend family, passed preflight, ownership plan |
| `running` | Selected evidence plus team manifest or LangGraph thread state plus heartbeat/lifecycle running |
| `complete` | Running evidence plus result summary, close record, and leader absorbed record |
| `blocked` | Named blocker, repeated blocking evidence, and no completion claim |

Reject plans, skill invocations, timeouts, branch names, or a bare `.omx` directory as proof that a team ran. Checker surface: `tools/check_orchestration_collaboration_evidenceguard.py` validates durable/persistent evidenceguard records before a selected, running, or complete team claim is accepted.

### 6.4 Expert lifecycle audit

Goal: every native expert lifecycle event is auditable.

JSONL events:

```json
{"event":"spawn","role":"verifier","task_summary":"...","scope":["..."],"non_goals":["..."]}
{"event":"wait","agent_id":"...","wait_seconds":30}
{"event":"timeout","agent_id":"...","classification":"non-evidence"}
{"event":"result","agent_id":"...","summary":"...","changed_paths":[]}
{"event":"absorbed","agent_id":"...","leader_decision":"accepted"}
{"event":"close","agent_id":"...","retention_policy":"close"}
```

Reject timeouts as results, missing close records when close policy should apply, or final reports that cite results before absorption. Checker surface: `tools/check_orchestration_collaboration_evidenceguard.py` validates structured expert lifecycle audit events; `tools/check_expert_lifecycle_wait_pacing_evidence.py` continues to validate text run-summary evidence.

### 6.5 LangGraph state release

Goal: completed LangGraph threads must not remain stale `running` records.

Minimum rules:

- On completion, write `completed_at` (completion timestamp), `final_phase` (last graph phase), `result_summary` (absorbed outcome), and `released_by` (actor or helper that released the state).
- On handoff to native_omx or main-session takeover, write `handoff_at`, `handoff_target`, and `reason`.
- Stale `running` is a release gap and cannot serve as active-work evidence; `tools/check_orchestration_collaboration_evidenceguard.py` validates LangGraph state release evidence and rejects completed work that remains `running`.

## 7. Implementation tasks

### Task 0: Freeze OpenSpec / Comet boundary

Scope:
- Confirm whether the current work is documentation-only or, for later code work, open `enforce-prompt-independent-collaboration-parity`.
- Record why persistent team is not launched: one bilingual document pair, not 2+ independent slices.

Done when:
- Front matter, goals, non-goals, and readiness are explicit.
- The feature worktree has receipt and claim records.

Validation:
- `openspec list --json` - inspect active OpenSpec change state before freezing the boundary.
- `git status --short --branch` - confirm the feature worktree and branch are isolated.

Commit message example: Chinese message in the zh-CN companion, equivalent to docs: freeze automatic routing plan new-structure boundary.

### Task 1: Rewrite the Chinese implementation plan

Scope:
- Replace the historical rule bundle with this structure.
- Preserve core governance meaning while removing long archive tables from the main flow.
- State clearly that this plan is not runtime evidence.

Done when:
- Section order matches the newer reference plans.
- Every task has scope, done criteria, validation, and a Chinese commit example.
- The file contains no mojibake text.

Validation:
- Manual heading review.
- Mojibake sentinel check for common GBK/UTF-8 garble markers and the Unicode replacement character returns no body hits.

Commit message example: Chinese message in the zh-CN companion, equivalent to docs: rewrite automatic routing Chinese plan structure.

### Task 2: Sync the English primary

Scope:
- Mirror the Chinese plan as an ASCII English primary.
- Keep doc_id, canonical, translation metadata, and section semantics aligned.

Done when:
- The English file is ASCII-only.
- It is a full companion, not an old summary.

Validation:
- `python .\tools\check_document_pair_policy.py --root . --json` - verify bilingual pairing and ASCII English primary requirements.
- Custom ASCII scan has no non-ASCII characters.

Commit message example: Chinese message in the zh-CN companion, equivalent to docs: sync automatic routing English plan.

### Task 3: Validate bilingual pairing and plan rules

Scope:
- Validate bilingual pairing, registry rules, and active plan references.

Done when:
- Document pair policy passes.
- Implementation plan rules pass.

Validation:
```powershell
python .\tools\check_document_pair_policy.py --root . --json
python .\tools\check_implementation_plan_rules.py --root . --json
```

Commit message example: Chinese message in the zh-CN companion, equivalent to docs: validate automatic routing bilingual pair.

### Task 4: Run OpenSpec guard and pre-commit review

Scope:
- Run repository guards.
- Fix task-owned errors; record unrelated residual worktree warnings without expanding scope.

Done when:
- `run_openspec_guard` passes.
- `check_precommit_update_archive` passes.

Validation:
```powershell
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root .
```

Commit message example: Chinese message in the zh-CN companion, equivalent to docs: pass automatic routing governance gates.

### Task 5: Expand checker unit tests in CI manifest coverage

Scope:
- Expand the manifest-registered orchestration test coverage for `tools/check_orchestration_collaboration_evidenceguard.py`.
- Cover repository-mode success, fixture-mode success, evidence-mode failure cases for durable/persistent claims, expert lifecycle audit, and LangGraph release records.
- Keep the coverage inside a test file already registered by `tools/ci/ci_test_manifest.json` when another active claim owns the CI manifest hotspot.

Done when:
- The manifest-registered test coverage validates both passing repository fixtures and failing evidence cases.
- No write-ownership conflict is introduced on `tools/ci/ci_test_manifest.json`.
- The checker remains callable through `tools/run_openspec_guard.py`.

Validation:
```powershell
python test\check_orchestration_trace_evidence.test.py
python .\tools\check_orchestration_collaboration_evidenceguard.py --root . --json
python .\tools\run_openspec_guard.py --root .
```

Commit message example: Chinese message in the zh-CN companion, equivalent to test: expand orchestration collaboration evidenceguard coverage.

### Task 6: Local CI, local MR review, and local main integration

Scope:
- Run local gate in the feature worktree.
- Commit, run local MR review, and merge into local `main`.
- Do not push remote.

Done when:
- Feature worktree is clean.
- Local gate passes.
- Local MR review passes.
- Local `main` contains the feature commit.

Validation:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600
.\tools\ci\local_mr_review.ps1
git merge-base --is-ancestor <feature-sha> main
```

Commit message example: Chinese message in the zh-CN companion, equivalent to docs: rewrite automatic routing plan in the new structure.

## 8. P0 / P1 readiness gates

| Gate | Entry condition | Exit condition |
| --- | --- | --- |
| P0 document restructure | User asks to rewrite this implementation plan | Bilingual document pair uses the new structure and validates locally |
| P0 evidence contract freeze | This plan is complete | Evidence contracts are fixture-ready |
| P1 checker implementation | User requests Phase 4 implementation | `tools/check_orchestration_collaboration_evidenceguard.py`, fixtures, unit tests, CI wiring, safety registry, and OpenSpec/spec updates land |
| P1 runtime integration | Checkers pass and runtime entry points exist | Activation trace, durable guard, expert lifecycle, and LangGraph release are auditable |

## 9. Validation plan

Base validation:

```powershell
git diff --check
python .\tools\check_document_pair_policy.py --root . --json
python .\tools\check_implementation_plan_rules.py --root . --json
python test\check_orchestration_trace_evidence.test.py
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root .
```

Integration validation:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600
.\tools\ci\local_mr_review.ps1
```

Manual acceptance:

- The document starts with Goal / Architecture / Tech Stack.
- Section 0 is a review conclusion, not a historical timeline.
- Section 7 can be handed to a worker without new decisions about files, tests, or commit boundaries.
- The plan says "plan is not evidence".
- The plan does not confuse ready, selected, running, and complete.
- The collaboration evidenceguard checker is covered by manifest-registered unit tests without CI-manifest hotspot ownership conflict.

## 10. Rollback and cleanup

- If checkers fail after the rewrite and the issue is not quickly fixable, restore the bilingual pair to the feature-branch base.
- If the feature branch is committed but not merged, use a new fix commit or local reset; avoid rewriting `main`.
- If the branch is merged and must be undone, use a Chinese `git revert` commit; do not rewrite `main` history.
- `.omx/worktree-task-receipt.json` and session claims are ignored local evidence and must not enter git.
- Without remote authorization, do not push, open MRs, or sync GitHub.

## 11. Required updates to existing governance

This P0 document restructure does not require runtime policy or checker edits. P1 must update:

- Activation policy: add prompt-independent parity as an acceptance rule.
- OpenSpec spec: add evidenceguard, expert lifecycle, and LangGraph release requirements.
- CI manifest: register new checker tests.
- Team-mode docs: keep "automatic collaboration default, threshold-gated team launch" wording consistent.

## 12. Risks and default decisions

| Risk | Default decision | Mitigation |
| --- | --- | --- |
| The document becomes a rule bundle again | Keep task-ready structure primary | Every task needs scope, done criteria, validation, and commit example |
| User thinks the plan is already runtime implementation | Use P0/P1 gates | Avoid wording planned work as running fact |
| Checkers pass but structure is not acceptable | Manual comparison with reference plans | Keep Goal, Architecture, Tech Stack, Backlog, Rollback, self-check |
| Console renders Chinese as mojibake | Trust UTF-8 source files | Do not copy mojibake; use Python UTF-8 reads when needed |
| Concurrent session advances main | Re-fetch and inspect main before merge | Use fast-forward or Chinese merge commit only |

## 13. Self-checklist

- [ ] Front matter uses the newer implementation-plan fields.
- [ ] The title is followed by an agentic worker note.
- [ ] Goal, Architecture, and Tech Stack summaries exist.
- [ ] Review conclusion and completeness table exist.
- [ ] Relationship model and naming boundary exist.
- [ ] Repo-local source of truth exists.
- [ ] Evidence contracts exist.
- [ ] Task-level backlog exists, and every task has validation and commit example.
- [ ] Readiness gates, validation plan, rollback, risks, and defaults exist.
- [ ] English primary is ASCII-only.
- [ ] `tools/check_orchestration_collaboration_evidenceguard.py` has CI-manifest-registered unit coverage.
- [ ] Local commit and merge commit use Chinese.

## 14. References

- `docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.md` - newer sidecar implementation-plan structure reference.
- `docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.md` - newer Comet runtime plan structure reference.
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` - activation policy authority.
- `docs_bilingual/project_startup_summary.md` - cold-start read-order authority.
- `AGENTS.md` - project-level orchestration and publication authority.
