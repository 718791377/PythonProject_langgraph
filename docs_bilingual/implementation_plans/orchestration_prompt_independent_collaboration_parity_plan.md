---
doc_id: orchestration_prompt_independent_collaboration_parity_plan
lang: en
canonical: docs_bilingual/implementation_plans/orchestration_prompt_independent_collaboration_parity_plan.md
translation_of: null
doc_class: implementation_plan
status: draft
last_reviewed: 2026-05-25
---

# Prompt-Independent Collaboration Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development` when this plan is implemented task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Do not claim a durable or persistent team ran unless selector, manifest, heartbeat, worker lifecycle, and close/absorb evidence exist.

**Goal:** Make automatic collaboration evidence-honest and prompt-independent: the same task must receive the same routing evaluation whether or not the user writes "use experts / durable_team / persistent team".

**Architecture:** Add a checker-backed evidence contract around activation traces, expert lifecycle events, durable/persistent team claims, and LangGraph completion/release state. Keep native experts as leader-side burst roles, keep `native_omx` and LangGraph as distinct durable backend families, and require durable-team claims to be backed by repo-local evidence rather than prompt text.

**Tech Stack:** Python repository checkers and tests, repo-local `.omx/state/` evidence fixtures, OpenSpec stable specs, `docs_bilingual/governance/*`, local CI via `tools/ci/local_gate.ps1`, local MR review via `tools/ci/local_mr_review.ps1`.

---

## Current Session Finding

Two user instructions had the same business scope. One included the explicit phrase "use experts / durable_team / persistent team"; the other did not. The final document result is now aligned, but the session evidence does not prove that the no-phrase instruction independently produced the same collaboration path. The repository policy already says automatic collaboration must not depend on that phrase, so the missing piece is an executable parity guard and lifecycle audit surface.

This plan is a future implementation plan, not runtime evidence. It does not prove that a durable team or persistent team is running.

## 2026-05-25 Granularity Review Conclusion

This plan needed refinement. The previous draft covered the major direction, but was not implementation-ready because:

1. It used placeholder paths such as `openspec/changes/unfixed-change-id/...`.
2. The four checker input fixtures, output fields, failure semantics, and pass semantics were underspecified.
3. It did not encode "the prompt phrase may only mark a hard directive, not change the task-shape threshold decision" as a testable contract.
4. Durable/persistent evidenceguard did not distinguish evidence needs for `selected`, `running`, `complete`, `not_needed`, and `blocked`.
5. Expert lifecycle listed event names without defining JSONL fields, result references, and timeout-as-evidence failures.
6. LangGraph `running` release rules lacked minimum fields for thread/workflow/job state surfaces.
7. The verification matrix did not specify how each new tool is wired into `tools/run_openspec_guard.py`, `tools/ci/ci_test_manifest.json`, and local MR review.

This revision turns those gaps into executable granularity. It is still an implementation plan, not runtime evidence; it does not prove that a durable team or persistent team is currently running.

## Scope

In scope:

- Prompt-independent routing parity fixtures.
- Durable/persistent team evidence guard.
- Expert lifecycle audit records for `spawn / wait / timeout / result / close / absorbed`.
- LangGraph state completion/release checks so `running` does not remain after submitted work is complete.
- Timeout and provider-pacing treatment as non-evidence.
- Documentation and guard wiring updates.

Out of scope:

- Replacing native Codex subagents.
- Treating skills or plugin profiles as native experts.
- Auto-launching durable teams at startup.
- Remote publication without explicit user approval.

## Planned File Map

Use this fixed OpenSpec change id for later implementation:

- change id: `enforce-prompt-independent-collaboration-parity`
- recommended implementation branch: `enforce-prompt-independent-collaboration-parity`
- recommended worktree: `.worktrees/enforce-prompt-independent-collaboration-parity`

| Path | Action | Responsibility |
| --- | --- | --- |
| `openspec/changes/enforce-prompt-independent-collaboration-parity/proposal.md` | Create | Define the bounded change, non-goals, and acceptance criteria. |
| `openspec/changes/enforce-prompt-independent-collaboration-parity/tasks.md` | Create | Track implementation completion. |
| `openspec/changes/enforce-prompt-independent-collaboration-parity/specs/codex-user-level-orchestration-activation-policy/spec.md` | Create | Add prompt-independent parity, evidenceguard, lifecycle audit, and LangGraph release requirements. |
| `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` | Modify | Explain prompt-independent collaboration and evidence boundaries. |
| `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md` | Modify | Chinese companion update. |
| `tools/check_orchestration_prompt_independent_collaboration_parity.py` | Create | Validate phrase/no-phrase routing parity fixtures. |
| `tools/check_durable_persistent_evidence_guard.py` | Create | Reject durable/persistent claims without selector/manifest/heartbeat/worker evidence. |
| `tools/check_expert_lifecycle_audit.py` | Create | Validate expert lifecycle audit records. |
| `tools/check_langgraph_state_release.py` | Create | Detect stale `running` state after completion/release. |
| `test/check_orchestration_prompt_independent_collaboration_parity.test.py` | Create | Unit tests for parity checker. |
| `test/check_durable_persistent_evidence_guard.test.py` | Create | Unit tests for evidenceguard. |
| `test/check_expert_lifecycle_audit.test.py` | Create | Unit tests for lifecycle audit. |
| `test/check_langgraph_state_release.test.py` | Create | Unit tests for LangGraph release checks. |
| `test/fixtures/orchestration_prompt_independent_collaboration_parity/` | Create | Paired fixtures with and without explicit collaboration phrases. |
| `test/fixtures/durable_persistent_evidence_guard/` | Create | Durable/persistent claim and evidence fixtures. |
| `test/fixtures/expert_lifecycle_audit/` | Create | Expert lifecycle JSONL fixtures. |
| `test/fixtures/langgraph_state_release/` | Create | LangGraph state fixtures. |
| `tools/run_openspec_guard.py` | Modify | Wire the new checkers into the guard sequence. |
| `tools/ci/ci_test_manifest.json` | Modify | Register new unit tests. |
| `docs_bilingual/docs_registry.yaml` | Modify | Register this plan and any new governance companions if needed. |

## Process-Group Operating Model

| Process group | Inputs | Tools and Techniques | Outputs |
| --- | --- | --- | --- |
| Initiating | Session retrospective, current governance policy, user requirement for automatic collaboration | Problem framing, evidence gap analysis, non-goal review | Change proposal, acceptance criteria, explicit non-claims |
| Planning | OpenSpec change, file map, current checker patterns, fixture requirements | Slice decomposition, owner mapping, test-first design, timeout budget review | Frozen implementation plan, disjoint tasks, validation matrix |
| Executing | Frozen plan, worktree, OpenSpec delta, tests | TDD, Python checkers, JSON fixtures, local guard wiring, bounded expert review when useful | Checkers, tests, docs updates, changed-path list |
| Monitoring and Controlling | Test output, guard output, routing fixtures, lifecycle records | Diff review, OpenSpec guard, local CI, expert verifier review, defect triage | Accepted fixes, rejected false claims, residual risk list |
| Closing | Passing gates, clean branch, updated docs registry, archived OpenSpec when complete | Closeout review, local MR review, archive decision, lessons learned | Merge-ready branch, archive or deferral evidence, follow-up backlog |

## Evidence Contracts

### Activation Parity Fixture Contract

Paired fixtures must share the same `task_shape_id`; only `prompt_features.explicit_collaboration_phrase` may differ. Recommended paths:

```text
test/fixtures/orchestration_prompt_independent_collaboration_parity/
  same_task_without_phrase.json
  same_task_with_phrase.json
```

Minimum JSON fields:

```json
{
  "case_id": "same_product_lifecycle_refresh_without_phrase",
  "task_shape_id": "product_lifecycle_refresh_business_pmp_multi_doc",
  "prompt_features": {
    "explicit_collaboration_phrase": false,
    "explicit_omx_directive": false,
    "explicit_langgraph_directive": false
  },
  "expected_decision": {
    "phase": "read-context-or-execute-parallel",
    "experts_now": "candidate_or_selected",
    "durable_workflow": "candidate_or_selected_when_threshold_met",
    "persistent_team_threshold": "requires_frozen_plan_and_2plus_slices",
    "backend_default": "langgraph",
    "claim_boundary": "do_not_claim_team_without_evidence"
  }
}
```

Pass condition: fixtures with the same `task_shape_id` agree on `phase`, `experts_now`, `durable_workflow`, `persistent_team_threshold`, `backend_default`, and `claim_boundary`. The explicit phrase may only mark `directive_seen=true`; it must not allow a below-threshold task to be reported as an already-running persistent team.

Fail condition: the explicit phrase causes `persistent_team=running`, skips frozen plan, skips evidenceguard, treats timeout as evidence, or changes backend family without a task-fit reason.

### Durable/Persistent Evidenceguard Contract

Evidence requirements are state-specific:

| Claimed state | Minimum evidence |
| --- | --- |
| `not_needed` | Activation trace explains the unmet threshold, such as `threshold_not_met:single_execution_slice`. |
| `candidate` | Frozen plan or slice analysis, plus why it has not started. |
| `selected` | Active selector, backend family, passed preflight record, worker ownership plan. |
| `running` | Active selector, team manifest, worker heartbeat, worker lifecycle `started/running` record. |
| `complete` | All `running` evidence plus closed agent record, result summary, and leader absorbed record. |
| `blocked` | Blocker name, evidence for three repeated blocks, and no use of blocked output as completion evidence. |

Recommended fixture structure:

```text
test/fixtures/durable_persistent_evidence_guard/
  invalid_running_missing_heartbeat/
    transcript.json
    .omx/state/selectors/active.json
    .omx/state/team/manifest.json
  valid_complete_team/
    transcript.json
    .omx/state/selectors/active.json
    .omx/state/team/manifest.json
    .omx/state/team/worker-heartbeats/worker-1.json
    .omx/state/team/lifecycle.jsonl
    .omx/state/team/closed-agents/worker-1.json
    .omx/state/team/absorbed-results.jsonl
```

### Expert Lifecycle Audit Contract

Each expert lifecycle record uses JSONL. Recommended path: `.omx/state/experts/lifecycle.jsonl`, or the same path inside a test fixture. Minimum fields per line:

```json
{
  "event": "spawn",
  "timestamp": "2026-05-25T00:00:00+08:00",
  "agent_id": "agent-001",
  "role": "verifier",
  "nickname": "Bernoulli",
  "task_summary": "review routing parity checker fixtures",
  "status": "started",
  "evidence_disposition": "not_evidence_yet"
}
```

Event ordering requirements:

1. `spawn` must precede `wait`, `timeout`, `result`, `close`, and `absorbed` for the same `agent_id`.
2. A `result` referenced by the final report must have an `absorbed` event for the same `agent_id`.
3. `timeout`, `stall`, and `provider_pacing_wait` may only produce a non-evidence disposition.
4. No new `result` may appear after `close` unless a fresh `spawn` uses a new `agent_id`.

### LangGraph State Release Contract

Repo-local LangGraph state must not remain unexplained `running` after completion. Minimum state:

```json
{
  "thread_id": "lg-thread-001",
  "workflow_id": "prompt-independent-parity",
  "status": "running",
  "active_work": true,
  "last_heartbeat_at": "2026-05-25T00:00:00+08:00",
  "completion_marker": null,
  "release_marker": null,
  "continue_reason": "worker still processing task 2"
}
```

Fail condition: `completion_marker` exists, or closeout evidence says work is complete, but `status=running`, `release_marker=null`, and `continue_reason` is empty.

Pass condition:

- Active work is still running with a fresh heartbeat; or
- work is completed and state is `complete/released/closed`; or
- state remains `running` with explicit release deferral and unfinished-work evidence.

## Task 1: OpenSpec Change and Evidence Contract

**Files:**
- Create: `openspec/changes/enforce-prompt-independent-collaboration-parity/proposal.md`
- Create: `openspec/changes/enforce-prompt-independent-collaboration-parity/tasks.md`
- Create: `openspec/changes/enforce-prompt-independent-collaboration-parity/specs/codex-user-level-orchestration-activation-policy/spec.md`

- [ ] **Step 1: Create the OpenSpec proposal**

  Write a proposal that states: automatic collaboration is mandatory by task threshold, not by prompt phrase. The proposal must name four evidence contracts: prompt-independent parity, durable/persistent evidenceguard, expert lifecycle audit, and LangGraph state release.

- [ ] **Step 2: Add normative requirements**

  Add requirements that:
  - phrase/no-phrase fixtures with the same task shape must produce the same activation decision class;
  - durable/persistent team claims require selector, manifest, heartbeat, worker lifecycle, and close/absorb evidence;
  - expert timeout is non-evidence;
  - LangGraph `running` state must be released or completed after submit/close.

- [ ] **Step 3: Validate the change**

  Run:

  ```powershell
  openspec validate enforce-prompt-independent-collaboration-parity --strict
  ```

  Expected: the change validates with no failed requirements.

## Task 2: Prompt-Independent Routing Parity Checker

**Files:**
- Create: `tools/check_orchestration_prompt_independent_collaboration_parity.py`
- Create: `test/check_orchestration_prompt_independent_collaboration_parity.test.py`
- Create: `test/fixtures/orchestration_prompt_independent_collaboration_parity/same_task_without_phrase.json`
- Create: `test/fixtures/orchestration_prompt_independent_collaboration_parity/same_task_with_phrase.json`
- Modify: `tools/run_openspec_guard.py`
- Modify: `tools/ci/ci_test_manifest.json`

- [ ] **Step 1: Write failing tests**

  Add fixtures for the same task in two forms:
  - without explicit collaboration phrase;
  - with "use experts / durable_team / persistent team".

  Expected behavior: both fixtures classify the same phase, expert need, durable threshold result, and persistent-team evidence state.

- [ ] **Step 2: Implement checker**

  Implement a checker that reads JSON fixtures, groups by `task_shape_id`, and compares `expected_decision.phase`, `experts_now`, `durable_workflow`, `persistent_team_threshold`, `backend_default`, and `claim_boundary`. It fails when the explicit phrase changes the activation decision class without a task-shape difference. Failure output must include `case_id`, `task_shape_id`, field name, left value, and right value.

- [ ] **Step 3: Register guard and tests**

  Add the checker to `tools/run_openspec_guard.py` and the test file to `tools/ci/ci_test_manifest.json`.

- [ ] **Step 4: Run focused tests**

  ```powershell
  python .\test\check_orchestration_prompt_independent_collaboration_parity.test.py
  python .\tools\check_orchestration_prompt_independent_collaboration_parity.py --root . --json
  ```

  Expected: tests and checker pass.

## Task 3: Durable/Persistent Evidenceguard

**Files:**
- Create: `tools/check_durable_persistent_evidence_guard.py`
- Create: `test/check_durable_persistent_evidence_guard.test.py`
- Create: `test/fixtures/durable_persistent_evidence_guard/invalid_running_missing_heartbeat/`
- Create: `test/fixtures/durable_persistent_evidence_guard/valid_complete_team/`
- Modify: `tools/run_openspec_guard.py`
- Modify: `tools/ci/ci_test_manifest.json`

- [ ] **Step 1: Write failing tests**

  Add negative fixtures where a transcript claims `durable_team=running` or `persistent_team=running` but lacks one or more required evidence files. The checker must fail these fixtures.

- [ ] **Step 2: Implement evidence validation**

  Require evidence for:
  - active selector;
  - team manifest;
  - worker heartbeat;
  - worker lifecycle record;
  - closed agent record, result summary, and final close/absorb record when work is claimed complete.

- [ ] **Step 3: Run focused tests**

  ```powershell
  python .\test\check_durable_persistent_evidence_guard.test.py
  python .\tools\check_durable_persistent_evidence_guard.py --root . --json
  ```

  Expected: false durable/persistent claims fail closed; valid evidence fixtures pass.

## Task 4: Expert Lifecycle Audit

**Files:**
- Create: `tools/check_expert_lifecycle_audit.py`
- Create: `test/check_expert_lifecycle_audit.test.py`
- Create: `test/fixtures/expert_lifecycle_audit/valid_absorbed_result/lifecycle.jsonl`
- Create: `test/fixtures/expert_lifecycle_audit/invalid_timeout_as_evidence/lifecycle.jsonl`
- Modify: `tools/run_openspec_guard.py`
- Modify: `tools/ci/ci_test_manifest.json`

- [ ] **Step 1: Define lifecycle schema**

  Define required event fields for `spawn`, `wait`, `timeout`, `result`, `close`, and `absorbed`: timestamp, role, agent id, nickname when available, task summary, status, and evidence disposition.

- [ ] **Step 2: Implement checker**

  Fail when a completed expert result is referenced by `final_report_refs.json` without a matching `absorbed` event, when a timed-out/stalled/provider-paced expert is used as accepted evidence, or when the same `agent_id` emits a new `result` after `close`.

- [ ] **Step 3: Run focused tests**

  ```powershell
  python .\test\check_expert_lifecycle_audit.test.py
  python .\tools\check_expert_lifecycle_audit.py --root . --json
  ```

  Expected: complete lifecycle fixtures pass; timeout-as-evidence fixtures fail.

## Task 5: LangGraph Completion and Release State

**Files:**
- Create: `tools/check_langgraph_state_release.py`
- Create: `test/check_langgraph_state_release.test.py`
- Create: `test/fixtures/langgraph_state_release/valid_active_running/`
- Create: `test/fixtures/langgraph_state_release/valid_released_complete/`
- Create: `test/fixtures/langgraph_state_release/invalid_completed_still_running/`
- Modify: `tools/run_openspec_guard.py`
- Modify: `tools/ci/ci_test_manifest.json`

- [ ] **Step 1: Add state fixtures**

  Add fixtures for:
  - valid running thread with active work;
  - completed thread with released state;
  - invalid completed work still marked `running`.

- [ ] **Step 2: Implement release checker**

  Fail when a thread is marked complete in handoff or closeout evidence but repo-local LangGraph state remains `running` without a release marker or continue reason. Active running state must have active work, a fresh heartbeat, and a continue reason.

- [ ] **Step 3: Run focused tests**

  ```powershell
  python .\test\check_langgraph_state_release.test.py
  python .\tools\check_langgraph_state_release.py --root . --json
  ```

  Expected: stale running state fails; active running state with live work passes.

## Task 6: Documentation, Validation, and Closeout

**Files:**
- Modify: `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md`
- Modify: `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md`
- Modify: `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.md`
- Modify: `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md`
- Modify: `docs_bilingual/docs_registry.yaml`

- [ ] **Step 1: Update governance text**

  Add a section that says explicit collaboration phrases are routing directives when present, but their absence is not a reason to skip the activation check.

- [ ] **Step 2: Run validation**

  ```powershell
  git diff --check
  openspec validate --all
  python .\tools\check_precommit_update_archive.py --root . --json
  python .\tools\run_openspec_guard.py --root .
  .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600
  .\tools\ci\local_mr_review.ps1
  ```

  Expected: all checks pass, or unrelated external worktree/state blockers are reported without being used as completion evidence.

- [ ] **Step 3: Closeout evidence**

  Final report must distinguish:
  - native experts used and closed;
  - durable/persistent team not launched unless evidence exists;
  - timed-out experts not used as evidence;
  - LangGraph backend readiness not equal to persistent-team runtime.

## Verification Matrix

| Requirement | Verification command | Required failing counterexample | Required passing example |
| --- | --- | --- | --- |
| Routing parity with/without collaboration phrase | `python .\tools\check_orchestration_prompt_independent_collaboration_parity.py --root . --json` | Phrase causes `persistent_team=running` | Same task shape has identical decision fields |
| Durable/persistent evidenceguard | `python .\tools\check_durable_persistent_evidence_guard.py --root . --json` | Running claim lacks heartbeat | Complete has selector, manifest, heartbeat, lifecycle, closed, absorbed |
| Expert lifecycle audit | `python .\tools\check_expert_lifecycle_audit.py --root . --json` | Timeout is referenced as evidence | Result is absorbed before final reference |
| LangGraph release | `python .\tools\check_langgraph_state_release.py --root . --json` | Completed still running with no release marker | Active running has heartbeat, or completed is released |
| Guard wiring | `python .\tools\run_openspec_guard.py --root .` | Checker not registered | Guard output includes new checker |
| CI manifest | `.\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` | Test not registered | Local gate runs the new tests |

## Risks and Rollback

- Risk: checker depends too heavily on chat transcript text. Mitigation: use structured fixtures and repo-local state as primary evidence; transcript is only the claim source.
- Risk: LangGraph backend ready is mistaken for persistent team running. Mitigation: separate backend readiness from team evidence.
- Risk: real running work is blocked. Mitigation: allow active running state with heartbeat, active work, and continue reason.
- Risk: skills/profiles are mistaken for experts. Mitigation: expert lifecycle accepts only native spawn/wait/result/close/absorbed events.
- Rollback: if a new checker is too noisy, temporarily remove it from `tools/run_openspec_guard.py` while preserving fixtures for repair; do not delete the governance requirement or allow false team claims.

## Acceptance Criteria

- Same task shape with and without explicit collaboration phrase produces the same routing decision class.
- No durable/persistent running claim passes without selector, manifest, heartbeat, worker lifecycle, closed agent record, and close/absorb evidence.
- Expert lifecycle audit distinguishes completed/absorbed results from timeout/stall/provider pacing non-evidence.
- LangGraph completed work does not leave stale `running` state; if still running, it has active work, heartbeat, and continue reason.
- Repository guard and local CI include the new checks.
- Final user-facing reports distinguish policy expectation, actual evidence, blocked/non-evidence, and main-session takeover; prompt text is never treated as runtime proof.
- This plan itself does not claim a durable/persistent team has run; only later repo-local evidence can support that claim.
