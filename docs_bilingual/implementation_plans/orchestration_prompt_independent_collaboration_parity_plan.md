---
doc_id: orchestration_prompt_independent_collaboration_parity_plan
lang: en
canonical: docs_bilingual/implementation_plans/orchestration_prompt_independent_collaboration_parity_plan.md
translation_of: null
doc_class: implementation_plan
status: draft
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

| Path | Action | Responsibility |
| --- | --- | --- |
| `openspec/changes/<change-id>/proposal.md` | Create | Define the bounded change and acceptance criteria. |
| `openspec/changes/<change-id>/tasks.md` | Create | Track implementation completion. |
| `openspec/changes/<change-id>/specs/codex-user-level-orchestration-activation-policy/spec.md` | Create | Add parity and evidenceguard requirements. |
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

## Task 1: OpenSpec Change and Evidence Contract

**Files:**
- Create: `openspec/changes/<change-id>/proposal.md`
- Create: `openspec/changes/<change-id>/tasks.md`
- Create: `openspec/changes/<change-id>/specs/codex-user-level-orchestration-activation-policy/spec.md`

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
  openspec validate <change-id> --strict
  ```

  Expected: the change validates with no failed requirements.

## Task 2: Prompt-Independent Routing Parity Checker

**Files:**
- Create: `tools/check_orchestration_prompt_independent_collaboration_parity.py`
- Create: `test/check_orchestration_prompt_independent_collaboration_parity.test.py`
- Modify: `tools/run_openspec_guard.py`
- Modify: `tools/ci/ci_test_manifest.json`

- [ ] **Step 1: Write failing tests**

  Add fixtures for the same task in two forms:
  - without explicit collaboration phrase;
  - with "use experts / durable_team / persistent team".

  Expected behavior: both fixtures classify the same phase, expert need, durable threshold result, and persistent-team evidence state.

- [ ] **Step 2: Implement checker**

  Implement a checker that reads JSON fixtures and fails when the explicit phrase changes the activation decision class without a task-shape difference.

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
  - final close/absorb record when work is claimed complete.

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
- Modify: `tools/run_openspec_guard.py`
- Modify: `tools/ci/ci_test_manifest.json`

- [ ] **Step 1: Define lifecycle schema**

  Define required event fields for `spawn`, `wait`, `timeout`, `result`, `close`, and `absorbed`: timestamp, role, agent id, nickname when available, task summary, status, and evidence disposition.

- [ ] **Step 2: Implement checker**

  Fail when a completed expert result is cited without a matching `absorbed` event, or when a timed-out expert is used as evidence.

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
- Modify: `tools/run_openspec_guard.py`
- Modify: `tools/ci/ci_test_manifest.json`

- [ ] **Step 1: Add state fixtures**

  Add fixtures for:
  - valid running thread with active work;
  - completed thread with released state;
  - invalid completed work still marked `running`.

- [ ] **Step 2: Implement release checker**

  Fail when a thread is marked complete in handoff or closeout evidence but repo-local LangGraph state remains `running` without a release marker.

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
- Modify: `docs_bilingual/docs_registry.yaml`

- [ ] **Step 1: Update governance text**

  Add a section that says explicit collaboration phrases are routing directives when present, but their absence is not a reason to skip the activation check.

- [ ] **Step 2: Run validation**

  ```powershell
  git diff --check
  openspec validate --all
  python .\tools\check_precommit_update_archive.py --root . --json
  python .\tools\run_openspec_guard.py --root .
  .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 360
  .\tools\ci\local_mr_review.ps1
  ```

  Expected: all checks pass, or unrelated external worktree/state blockers are reported without being used as completion evidence.

- [ ] **Step 3: Closeout evidence**

  Final report must distinguish:
  - native experts used and closed;
  - durable/persistent team not launched unless evidence exists;
  - timed-out experts not used as evidence;
  - LangGraph backend readiness not equal to persistent-team runtime.

## Acceptance Criteria

- Same task shape with and without explicit collaboration phrase produces the same routing decision class.
- No durable/persistent team claim passes without selector, manifest, heartbeat, worker lifecycle, and close/absorb evidence.
- Expert lifecycle audit distinguishes completed/absorbed results from timeout/non-evidence.
- LangGraph completed work does not leave stale `running` state.
- Repository guard and local CI include the new checks.
- Final user-facing reports stay evidence-honest and do not treat prompt text as runtime proof.
