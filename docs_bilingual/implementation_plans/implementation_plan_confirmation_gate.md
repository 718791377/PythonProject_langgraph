---
doc_id: implementation_plan_confirmation_gate
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/implementation_plan_confirmation_gate.zh-CN.md
---

# Implementation Plan Confirmation Gate

## Purpose

Make the implementation-plan file the required confirmation artifact before non-document implementation starts.
A full plan confirmed in chat is not enough. The plan must first be written or updated as an active implementation plan in `docs_bilingual/implementation_plans/`, registered in `docs_bilingual/docs_registry.yaml`, committed, integrated into local `main`, and then shown to the user for confirmation.

## Scope Decision

- Level: project-level governance for `D:/PythonProject_langgraph`.
- Reuse shape: general rule pattern, but this implementation is dedicated to this repository until a later user-level rollout is explicitly approved.
- Stage A type: documentation and registry only.
- Stage B type: governance, checker, helper, and test changes after the user confirms this file.
- Remote publication: out of scope unless the user explicitly requests remote push or publication.

## Non-Goals

- Do not change runtime, checker, helper, or test behavior during Stage A.
- Do not treat chat-only plan approval as enough for non-document execution.
- Do not push to GitLab or GitHub as part of this plan unless the user explicitly asks for remote publication.
- Do not make user-level Codex launcher or global configuration changes in Stage B without a separate explicit user-level scope decision.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: active
Stage: Stage A documentation package
Owner session: main Codex leader session
Current gate: create and integrate this implementation plan, then stop for user confirmation
Stage B entry condition: user confirms `docs_bilingual/implementation_plans/implementation_plan_confirmation_gate.md` or its Chinese companion after local `main` integration
Last updated: 2026-05-28
<!-- CURRENT_STATUS_END -->

## Confirmation Rule to Enforce

When leaving `/plan` or otherwise moving from planning into non-document execution:

1. The assistant may discuss a full plan in chat.
2. Before any non-document implementation, the assistant must create or update a formal implementation-plan file under `docs_bilingual/implementation_plans/`.
3. The plan must use the bilingual registry pattern: English ASCII primary plus Chinese companion.
4. The plan must be registered in `docs_bilingual/docs_registry.yaml` with `doc_class: implementation_plan` and `status: active` before execution.
5. The plan update must be committed with a Chinese commit message and integrated into local `main` before implementation starts.
6. The assistant must show the implementation-plan path and wait for explicit user confirmation of that file.
7. Only after that confirmation may non-document implementation begin.

## Planned Stage B Implementation Boundary

Stage B may update only the files needed to enforce this rule:

- `docs_bilingual/governance/openspec_opsx_project_usage_policy.md` - English governance policy that will describe the formal file-confirmation gate.
- `docs_bilingual/governance/openspec_opsx_project_usage_policy.zh-CN.md` - Chinese companion policy for the same gate.
- `tools/check_plan_exit_execution_governance.py` - checker that will fail closed when non-document execution lacks formal plan-file confirmation.
- `tools/complete_local_flow_to_remote_gate.py` - helper that will stop at the confirmation gate before non-document execution.
- local tests covering the new confirmation gate
- CI or manifest registration only if the changed tests/checkers require it

Stage B must not change unrelated Comet runtime behavior, LangGraph backend behavior, or user-level launcher configuration.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Stage A: create the English ASCII primary implementation plan.
- [x] Stage A: create the Chinese companion implementation plan.
- [x] Stage A: register the plan pair in `docs_bilingual/docs_registry.yaml` as an active implementation plan.
- [ ] Stage A: commit the documentation package with a Chinese commit message.
- [ ] Stage A: integrate the documentation package into local `main`.
- [ ] Stage A: stop and ask the user to confirm this implementation-plan file before Stage B.
- [ ] Stage B: update governance docs so chat-only plan confirmation is explicitly insufficient.
- [ ] Stage B: update helpers/checkers so non-document execution requires an active, registered, committed implementation plan plus explicit file confirmation evidence.
- [ ] Stage B: add negative tests for chat-only approval and missing implementation-plan confirmation.
- [ ] Stage B: add positive tests for the formal active implementation-plan confirmation path.
- [ ] Stage B: run local verification and commit with a Chinese commit message.
- [ ] Stage B: integrate into local `main` only after the user confirms this plan file.
<!-- TASK_BACKLOG_END -->

## Acceptance Criteria

Stage A is accepted when:

- This English primary file exists and contains the stable update anchors required for implementation plans.
- The Chinese companion file exists.
- `docs_bilingual/docs_registry.yaml` registers the pair with `doc_class: implementation_plan` and `status: active`.
- The Stage A commit message is Chinese.
- The Stage A branch is integrated into local `main`.
- No runtime, checker, helper, or test implementation files are changed in Stage A.
- The assistant stops for user confirmation before Stage B.

Stage B is accepted only after later user confirmation, and then only when:

- The governance rule says chat-only plan confirmation is not enough.
- The scripted path blocks non-document implementation without formal implementation-plan confirmation.
- Tests cover both blocked and allowed paths.
- Verification evidence is fresh and recorded in the final response.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Pending Stage A commit evidence. This plan intentionally does not store a full evidence package inline.
<!-- EVIDENCE_INDEX_END -->
