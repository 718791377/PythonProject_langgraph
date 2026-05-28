---
doc_id: codex_governance_session_visibility_and_plan_lock_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/codex_governance_session_visibility_and_plan_lock_plan.zh-CN.md
---

# Governance Session Visibility and Plan Lock Implementation Plan

## Purpose

Convert the chat-approved governance direction into the formal implementation-plan gate required before any non-document implementation starts.
This plan covers five related governance upgrades:

1. User-facing `Routing trace` output must be fully Chinese in conversation.
2. OMX and LangGraph escalation needs must be visible in the main session before they can quietly time out.
3. Multiple Codex sessions must be able to work in parallel only when each active `implementation_plan` is owned by at most one session.
4. Comet must make its Superpowers HOW-layer usage visible instead of leaving it implicit.
5. GitHub Spec Kit may be evaluated only as a subordinate adapter or template source, not as a competing governance layer.

## Scope Decision

- Level: project-level governance for `D:/PythonProject_langgraph`.
- Reuse shape: generic and portable scripts/docs that can later be copied to other repositories, but this implementation does not edit user-level global config.
- Current stage: Stage A documentation package only.
- Stage B type: governance, checker, helper, and tests after the user confirms this file.
- Runtime boundary: do not change OMX, LangGraph, Comet, OpenSpec, Superpowers, or Spec Kit runtime behavior during Stage A.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Non-Goals

- Do not install GitHub Spec Kit or run `specify init`.
- Do not add Spec Kit as a project governance authority.
- Do not auto-grant escalated permissions or bypass the main-session approval model.
- Do not require OMX, LangGraph, or the future Codex CLI personal production durable team for the portable multi-session lock path.
- Do not treat skill invocation as native subagent evidence.
- Do not begin Stage B non-document implementation before this active implementation plan is committed, integrated into local `main`, displayed to the user, and explicitly confirmed by the user.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: active
Stage: Stage A documentation package
Owner session: main Codex leader session
Current gate: create and integrate this implementation plan, then stop for user confirmation
Stage B entry condition: user confirms this file or its Chinese companion after local `main` integration
Last updated: 2026-05-28
<!-- CURRENT_STATUS_END -->

## Governance Decisions to Implement in Stage B

### 1. Chinese Conversation Routing Trace

- Conversation-facing routing trace must use Chinese field labels and Chinese explanatory text.
- Saved machine-checkable evidence may retain canonical ASCII tokens when they are needed by existing checkers, for example `threshold_not_met:no_frozen_plan`.
- The checker should distinguish two surfaces:
  - user-facing trace text: Chinese labels required;
  - saved evidence trace: structured tokens allowed for validation.
- The routing trace must still report the same decisions: phase, capability chain, backend default/readiness, experts, durable workflow, persistent team, and reason.

### 2. Main-Session Escalation Visibility

- OMX/LangGraph/durable-worker flows must not hide permission needs inside worker context.
- Add a visible main-session escalation preflight summary before starting likely privileged work.
- Add a local pending-approval receipt surface that records what needs main-session action without granting permission automatically.
- Add liveness language for pending approval states so the user sees that progress is blocked by a main-session approval decision.
- Keep the security boundary: only the main session can request or receive escalation approval.

### 3. Portable Implementation-Plan Session Lock

- Add a project-local, dependency-light claim model that works without OMX, LangGraph, or a durable team.
- Claim scope must include at least:
  - `implementation_plan` path;
  - `session_id`;
  - `worktree`;
  - `branch`;
  - optional OpenSpec change ids;
  - touched or intended path scopes;
  - status and timestamp.
- The checker must fail closed when two active claims target the same `implementation_plan` path.
- Different active plans may be processed in parallel when path ownership is disjoint or explicitly serialized.
- The tracked scripts/docs should be portable to another computer; local claim files may remain ignored runtime state.

### 4. Superpowers Visibility Under Comet

- Comet remains the control layer.
- OpenSpec remains the durable WHAT/spec lifecycle authority.
- Superpowers remains the HOW/methodology layer.
- Comet phase output and evidence should explicitly say which Superpowers skill was applied where relevant:
  - design: brainstorming or design-method skill evidence;
  - build: writing-plans plus executing-plans or subagent-driven-development evidence;
  - verify: finishing-a-development-branch and verification-before-completion evidence when applicable.
- The evidence must not claim that a Superpowers skill is a native subagent, durable worker, or persistent team.

### 5. Spec Kit Boundary

- Treat GitHub Spec Kit as a spec-driven-development toolkit that overlaps with planning/spec workflow.
- Do not make it a second governance layer beside Comet/OpenSpec/Superpowers.
- If later introduced, map it as a subordinate adapter, import/export bridge, or template source:
  - Comet: control layer;
  - OpenSpec: WHAT and durable spec lifecycle;
  - Superpowers: HOW and execution methodology;
  - Spec Kit: optional SDD template or adapter surface.
- Add a guardrail that forbids running `specify init --force`, adding `.specify/`, or converting governance authority without a separate active implementation plan.

## Planned Stage B Implementation Boundary

After the user confirms this plan file, Stage B may update only the files needed for the five decisions above:

- governance docs under `docs_bilingual/governance/` for routing trace language, session ownership, Comet/OpenSpec/Superpowers authority, and Spec Kit adapter boundaries;
- checker/helper scripts under `tools/` for Chinese routing trace evidence, plan claim overlap, pending escalation visibility, and Spec Kit authority prevention;
- local tests and fixture files needed to prove the checker/helper behavior;
- docs registry entries only if new documents are created.

Stage B must stop again for a separate scope decision before editing user-level launcher files, installing packages, running Spec Kit initialization, or changing external remotes.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Stage A: create the English ASCII primary implementation plan.
- [x] Stage A: create the Chinese companion implementation plan.
- [x] Stage A: register the plan pair in `docs_bilingual/docs_registry.yaml` as an active implementation plan.
- [ ] Stage A: commit the documentation package with a Chinese commit message.
- [ ] Stage A: integrate the documentation package into local `main`.
- [ ] Stage A: stop and ask the user to confirm this implementation-plan file before Stage B.
- [ ] Stage B: update orchestration activation governance so user-facing `Routing trace` is Chinese.
- [ ] Stage B: update trace checker or fixtures so Chinese conversation trace is enforced without breaking structured evidence tokens.
- [ ] Stage B: add pending-escalation receipt/preflight governance and checker coverage.
- [ ] Stage B: add portable implementation-plan claim schema and overlap checker support.
- [ ] Stage B: add tests proving same-plan active claims fail closed and different-plan claims may coexist.
- [ ] Stage B: add Comet/Superpowers visibility governance and evidence checks.
- [ ] Stage B: add Spec Kit subordinate-adapter boundary governance and guard tests.
- [ ] Stage B: run local verification and commit with a Chinese commit message.
- [ ] Stage B: integrate Stage B only after this plan file is explicitly confirmed by the user.
<!-- TASK_BACKLOG_END -->

## Acceptance Criteria

Stage A acceptance:

- English primary file exists and is ASCII-only apart from unavoidable Markdown punctuation being ASCII.
- Chinese companion file exists.
- `docs_bilingual/docs_registry.yaml` registers this pair as `doc_class: implementation_plan` and `status: active`.
- Stage A uses a Chinese commit message.
- Stage A integrates into local `main`.
- Stage A does not modify runtime, checker, helper, or test behavior.
- The assistant stops before Stage B and asks the user to confirm this file.

Stage B acceptance after later confirmation:

- Conversation-facing routing trace uses Chinese labels and Chinese explanatory language.
- Saved trace evidence still validates required routing decisions and threshold/blocker labels.
- Main-session escalation needs are summarized visibly before hidden worker waits can time out.
- Same-plan active session claims fail closed on a normal local machine without OMX/LangGraph.
- Different active implementation plans can be processed in parallel when ownership is disjoint.
- Comet evidence shows the relevant Superpowers skill usage without misclassifying it as an expert or durable worker.
- Spec Kit is documented and guarded as an optional subordinate adapter, not a governance authority.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Pending Stage A commit evidence. This plan intentionally stores only an index, not full evidence packages.
<!-- EVIDENCE_INDEX_END -->
