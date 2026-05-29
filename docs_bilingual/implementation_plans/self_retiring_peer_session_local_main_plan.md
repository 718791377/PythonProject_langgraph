---
doc_id: self_retiring_peer_session_local_main_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/self_retiring_peer_session_local_main_plan.zh-CN.md
stage: Stage C runtime/checker implementation
priority: early-foundation
confirmation_required: true
---

# Self-Retiring Peer Session Local Main Integration Plan

## Goal

Allow each Codex session to own its own implementation plan, feature branch or worktree, validation, commit, and local `main` integration attempt without requiring a fixed main-controller session.
Local `main` mutation remains serial through a repository-local nonce lock.

## Scope Decision

- Level: project-level governance and runtime/checker implementation for this repository.
- Parent plan: none required. This plan is intentionally standalone because not every implementation plan belongs to the same parent family.
- Related plan: `complete_local_commit_flow_scheduler_reorder_buffer_plan` - supplies ROB state and retirement metadata that this plan extends.
- Related plan: `multi_plan_parallel_session_orchestration_plan` - remains one optional plan family, not a global cold-start parent for all plans.
- Remote publication: out of scope unless the user explicitly requests remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: active
Stage: pre-commit validation passed; local MR review and local gate remain post-commit gates
Owner session: current Codex session that owns branch `decentralize-session-self-retire-20260529`
Current gate: commit the runtime/checker/docs package with a Chinese message, run post-commit local MR review and local gate, then integrate to local `main` and stop at the remote publication gate
Last updated: 2026-05-29
<!-- CURRENT_STATUS_END -->

## Semantic Terms

| Term | Meaning |
| --- | --- |
| `self_retire_lock` | Retire mode indicating that the producing peer session, not a fixed controller session, acquired the repository-local local-main lock before mutating local `main`. |
| `retire_mode` | ROB field that records whether a retired entry used legacy controller-owned serial retirement or peer-session self-retirement. |
| `retire_owner_session_id` | ROB field that records the session identity allowed to retire its own package. |
| `retire_lock_nonce` | ROB field that stores the nonce returned by the local-main retire lock and proves the retiring session held the lock. |
| `local-main-retire.lock` | Repository-local lock file that serializes local `main` writes across peer sessions. |

## File Ownership

- `tools/local_main_retire_lock.py` - implements acquire, status, stale-reclaim, and nonce release for local `main` integration locking.
- `tools/check_local_main_retire_lock.py` - validates the active lock schema and reports stale locks without treating absence of a lock as failure.
- `tools/complete_local_flow_to_remote_gate.py` - gains peer-session self-retirement arguments and wraps local `main` mutation with the lock.
- `tools/commit_reorder_buffer.py` - records `retire_mode`, `retire_owner_session_id`, and `retire_lock_nonce` when a ROB entry is self-retired.
- `tools/check_commit_reorder_buffer.py` - validates the self-retirement metadata on retired ROB entries.
- `tools/run_openspec_guard.py` - runs the local-main retire-lock checker as part of the repository guard.
- `tools/check_local_flow_scripted_enforcement.py` - verifies that the lock helper, checker, policies, and tests remain wired.
- `tools/safety_rule_script_backing_registry.json` - records script-backed safety coverage for peer-session local-main retirement.
- `test/check_local_main_retire_lock.test.py` - covers lock acquire, denial, nonce mismatch, stale reclaim, and release.
- `test/check_commit_reorder_buffer.test.py` - covers ROB self-retirement metadata.
- `test/check_implementation_plan_rules.test.py` - covers optional parent plans and missing declared parent plans.
- `test/check_local_flow_scripted_enforcement.test.py` - covers script-backed enforcement wiring for the new lock.
- `test/run_openspec_guard_json.test.py` - covers guard registration for the new checker.
- `tools/ci/ci_test_manifest.json` - registers the focused local-main retire-lock test in the local Python test manifest.
- `docs_bilingual/docs_registry.yaml` - registers this bilingual implementation plan pair.
- Repository-root complete local commit-flow document - documents the no-fixed-controller peer-session execution model and serial local-main lock.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Create this active English primary implementation plan and Chinese companion so implementation has a confirmed governance surface.
- [x] Register this implementation plan pair in `docs_bilingual/docs_registry.yaml`.
- [x] Implement `tools/local_main_retire_lock.py` with acquire, status, release, nonce, TTL, and stale reclaim behavior.
- [x] Implement `tools/check_local_main_retire_lock.py` so stale locks warn and absent locks pass.
- [x] Extend `tools/complete_local_flow_to_remote_gate.py` with peer-session `--self-retire`, `--session-id`, `--rob-entry-id`, `--acquire-retire-lock`, and `--lock-ttl-minutes` controls.
- [x] Extend ROB helper/checker support for `retire_mode`, `retire_owner_session_id`, and `retire_lock_nonce`.
- [x] Wire the local-main retire-lock checker into the OpenSpec guard and local scripted-enforcement checker.
- [x] Add focused tests and local CI manifest registration.
- [x] Update governance documents to state that parent plans are optional and local-main writes are peer-session self-retired through the lock.
- [x] Run focused tests, local CI manifest tests, and OpenSpec guard before commit.
- [ ] Commit with a Chinese message, run post-commit local MR review and local gate, integrate into local `main`, and stop at the remote publication gate.
<!-- TASK_BACKLOG_END -->

## Acceptance Checklist

- [x] A peer session can acquire the local-main retire lock and another session is denied while it is active.
- [x] A peer session cannot release another session's lock because release requires the matching nonce.
- [x] Stale lock reclaim requires an explicit operator-controlled flag.
- [x] ROB retired entries can record `retire_mode=self_retire_lock` with `retire_owner_session_id` session-owner evidence and `retire_lock_nonce` lock-token evidence.
- [x] The complete local flow helper can acquire the lock before local `main` mutation, release it in a `finally` block, and record ROB self-retirement evidence after a successful merge.
- [x] The implementation-plan checker allows missing `parent_plan` and rejects unsafe or missing declared `parent_plan` paths.
- [x] Documentation no longer implies that all local `main` integration must be controlled by one fixed main session.

## Completed Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-05-29 self-retiring peer-session implementation pre-commit validation: focused tests passed, local CI manifest passed, local-main retire-lock checker passed, commit ROB checker passed, implementation-plan checker passed, local scripted-enforcement checker passed, precommit update/archive checker passed, and OpenSpec guard passed with `--skip-validate`; local MR review and local gate remain post-commit gates.
<!-- EVIDENCE_INDEX_END -->