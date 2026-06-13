---
doc_id: recent_manual_workflow_packaging_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/recent_manual_workflow_packaging_plan.zh-CN.md
source_prompt: reference_files/5.md
---

# Recent Manual Workflow Packaging Plan

> **For agentic workers:** use `superpowers:executing-plans`. This plan turns `reference_files/5.md` into a repo-local, evidence-first, redacted workflow-packaging process; weak evidence must not become user-level installs or scheduled automation.

## Goal

Review recent work from the last 30 days, or all available history if shorter, using Codex work evidence, memory/rollout summaries, Chronicle discovery signals, and existing skills/agents/automations inventory. Produce a compact shortlist and create only high-confidence, narrow, missing assets.

## Architecture

Add a repo-local skill as the reusable playbook and a CLI report as the repeatable discovery surface. The script reads sanitized aggregate signals from this repository and user-level inventory, but does not commit raw sessions, raw logs, or full private paths. If Chronicle is unavailable, it records `not_enabled` instead of fabricating external evidence.

## Tech Stack

Markdown implementation plans, repo-local `.agents/skills`, Python CLI, Git history, `docs_bilingual/memory`, `docs_bilingual/implementation_plans`, user-level skills/agents inventory, local gate, local MR review, and the local-main-first integration workflow.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented
Stage: project-level runtime implemented and integrated into local `main`; remote publication pending explicit approval.
Owner session: `implement-recent-manual-workflow-packaging-20260613`.
Source prompt: `reference_files/5.md`.
Runtime boundary: project-level source-of-truth skill, CLI, and sanitized memory output; user-level wrapper/config is recorded only as a future candidate; no user-level install, no scheduled task, no Chronicle mutation, no remote publication.
Last updated: 2026-06-13
<!-- CURRENT_STATUS_END -->

## Evidence Order

1. Recent Codex sessions and task summaries: prefer repository Git commit subjects, committed memory, implementation-plan status, and aggregate outputs from runnable audit scripts.
2. Codex Memories and rollout summaries: read weekly summaries, closeout evidence, mainline summaries, and related memory docs under `docs_bilingual/memory/`.
3. Chronicle: discovery only; if no command or data directory exists on this machine, record `not_enabled`.
4. Existing skills, custom agents, and automations: inspect repo-local and user-level skills/agents inventory to avoid duplicates.

## Candidate Gate

A candidate is actionable only when it:

- occurred at least twice, or is clearly likely to recur and costly to repeat;
- has stable inputs, a repeatable procedure, and a clear output or stopping condition;
- would materially improve speed, quality, consistency, or reliability;
- is not already adequately covered by an existing skill, custom agent, or automation.

Anything that fails the gate must be recorded as `skip` or `needs_more_evidence`, not created.


## User-Level / Project-Level Packaging Decision

| Level | Decision for this run | Reason | Deliverable |
| --- | --- | --- | --- |
| Project-level reusable | Implement now | The workflow reads this repository's Git history, memory, implementation plans, OpenSpec evidence, and local gates. This repository is the source of truth and is the safest place to test the rules first. | Repo-local skill, Python CLI, sanitized memory shortlist, and plan evidence. |
| User-level candidate | Record only; do not install now | The workflow is reusable across projects, but a user-level wrapper/config must depend on the stabilized project CLI and needs separate approval, rollback, and smoke evidence. | Emit an `extend-user-level-wrapper` candidate and its future install conditions in the shortlist. |
| Do not package | Skip this run | Existing analyst/planner/writer/verifier roles already cover custom subagent needs; scheduler, Chronicle writes, and external actions would expand privilege and privacy scope. | Record the reason under `deliberately skipped`. |

Default rule: package at project level first. Promote to a user-level wrapper/config only when the same workflow is useful across at least two projects, does not depend on one repository's private structure, the CLI output is sanitized, and rollback/smoke evidence exists. Any external action or scheduled execution requires a separate plan and explicit authorization.

## Form Selection

| Form | Use when | This run default |
| --- | --- | --- |
| Skill | Reusable workflow/playbook for a human or agent to follow | Create the repo-local skill for this workflow |
| Custom subagent | Bounded specialist role or investigation suitable for delegation | Skip; existing analyst/planner/writer roles cover it |
| Automation | Scheduled or recurring check, report, reminder, or monitor | Create a manual CLI; no scheduler |
| Extend existing | Existing asset covers most of the need | Prefer extension if overlap appears |
| Skip | One-off, sensitive, weakly evidenced, or too broad | Record the reason explicitly |

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Read `reference_files/5.md`.
- [x] Inspect existing audit, skills, agents, and memory surfaces non-destructively.
- [x] Add the bilingual implementation plan and record the user-level/project-level packaging decision.
- [x] Commit the plan, run local gates, and merge into local `main`.
- [x] Add the project-level repo-local skill and CLI.
- [x] Generate sanitized memory shortlist and record user-level wrapper/config candidate conditions.
- [x] Run targeted implementation verification, commit the implementation, and merge into local `main`.
<!-- TASK_BACKLOG_END -->

## Implementation Slices

### Slice 1: Freeze the plan

- [x] Read `reference_files/5.md`.
- [x] Inspect existing audit, skills, agents, and memory surfaces non-destructively.
- [x] Add this bilingual implementation plan.
- [x] Commit the plan, run local gates, and merge into local `main`.

### Slice 2: Skill and CLI

- [x] Add `.agents/skills/recent-workflow-packaging/SKILL.md`.
- [x] Add `tools/report_recent_manual_workflow_candidates.py`.
- [x] Support `--root`, `--days`, `--output`, and `--json`.
- [x] Emit shortlist, created/extended, deliberately skipped, and needs-more-evidence sections.
- [x] Emit `Chronicle: not_enabled` when Chronicle is unavailable.

### Slice 3: Evidence output and verification

- [x] Generate `docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.md`.
- [x] Generate `docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.zh-CN.md`.
- [x] Run script smoke, precommit update/archive, document pair policy, implementation-plan rules, diff check, and local MR review; record full local-gate timeout attempts.
- [x] Commit the implementation, merge into local `main`, and stop at the remote-publication gate.

## Acceptance Criteria

- The script can generate redacted Markdown and JSON when Chronicle is unavailable.
- Each shortlist item includes repeated workflow, supporting evidence/dates, frequency/confidence, recommended form, and why it is or is not worth creating.
- The only missing assets created in this run are the project-level repo-local skill and manual CLI automation; user-level wrapper/config is recorded only as a future candidate, and no user-level install or scheduler is authorized.
- All new files pass targeted local checks and local MR review; full local gate timeout is explicitly recorded and was not claimed as a fresh pass.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Project-level skill: `.agents/skills/recent-workflow-packaging/SKILL.md`.
- Manual CLI: `tools/report_recent_manual_workflow_candidates.py`.
- Sanitized shortlist: `docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.md`.
- Chinese shortlist companion: `docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.zh-CN.md`.
- Local smoke JSON: `.omx/test-artifacts/recent_manual_workflow_packaging_shortlist_2026-06-13.json` (local-only evidence).
- Plan commit merged to local `main`: `5ba4deafdcbe804a318b9a3c5e0deb5b4c66fd96`.
- Runtime commit merged to local `main`: `ca5adf1a1b13db3cb6dd72625e45905446ceb81a`.
- Targeted validation passed: `py_compile`, CLI JSON smoke, `check_document_pair_policy.py`, `check_implementation_plan_rules.py`, `check_precommit_update_archive.py`, `git diff --check`, and `tools/ci/local_mr_review.ps1`.
- Full `tools/ci/local_gate.ps1` was attempted in the feature worktree with 45s and 300s per-step timeouts; both attempts timed out before completion, so integration used the guarded `--skip-local-gate` path.
- Local MR review passed before integration; rollback ref: `refs/backup/local-main/20260613-122119-before-implement-recent-manual-workflow-packaging`.
<!-- EVIDENCE_INDEX_END -->

## Non-Goals

- Do not read or commit raw Codex transcripts, raw runtime logs, or raw Chronicle data.
- Do not modify `C:\Users\lenovo\.codex\config.toml`, user-level skill installs, or native agent TOMLs.
- Do not send external messages, operate browser/GUI surfaces, or publish remotes.
- Do not inflate low-confidence candidates into broad catch-all skills.
