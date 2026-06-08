---
doc_id: r6_live_runtime_promotion_plan
lang: en
status: active
doc_class: implementation_plan
stage: implementation-evidence
priority_order: Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit
zh_cn_path: docs_bilingual/implementation_plans/r6_live_runtime_promotion_plan.zh-CN.md
---

# R6 Live Runtime Promotion Plan

> **For agentic workers:** use `superpowers:executing-plans` or `superpowers:subagent-driven-development` when implementing this plan. Keep Comet as the workflow control layer, OpenSpec as WHAT authority, and Superpowers as HOW authority.

## Goal

Promote the R5 checker-backed active-candidate gates into an R6 live-runtime promotion layer for the listed user-level runtime lanes while preserving the conflict-priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.

R6 means live runtime is default-discoverable and default-routable, but every sensitive external action remains fail-closed unless a current authorization receipt, owner lease, environment-provided target, rollback readiness, cleanup evidence, and redacted execution receipt are present.

## Scope

This plan covers these existing R5 plans as one governed rollout:

- `user_level_capability_receipt_rollback_redaction_plan` - governs shared authorization, rollback, and redaction receipt foundations
- `worktree_receipt_claim_lifecycle_plan` - governs worktree task receipt and claim lifecycle promotion
- `repo_local_selector_ownership_plan` - governs repo-local selector ownership and adoption evidence
- `durable_capability_readiness_projection_plan` - governs durable backend readiness projection evidence
- `langgraph_state_release_evidence_plan` - governs LangGraph state release receipt evidence
- `durable_smoke_adoption_gate_template_plan` - governs durable smoke and adoption gate templates
- `user_level_mcp_skills_cli_runtime_plan` - governs user-level MCP and skills CLI runtime handoff
- `user_level_browser_cli_adapter_boundary_plan` - governs browser/CLI adapter owner and live-action boundaries
- `user_level_cli_anything_wxwork_cli_governance_plan` - governs CLI-Anything and WXWork CLI sensitive action boundaries
- `stop_slop_caveman_response_density_runtime_plan` - governs response-density runtime and canary-safe compression activation
- `gstack_codex_delivery_loop_runtime_governance_plan` - governs gstack advisory delivery-loop runtime boundaries
- `codex_harnesses_governance_plan` - governs Codex harness candidates, jobs, and no-takeover evidence
- `spec_kit_authority_guard_plan` - governs Spec Kit authority prevention checks
- `spec_kit_subordinate_adapter_governance_plan` - governs Spec Kit subordinate adapter runtime boundaries

## Current Status
<!-- CURRENT_STATUS_START -->

- [x] Stage A plan package merged to local `main` in commit `5dd8592`.
- [x] Stage B core R6 checker/runtime/template implementation merged to local `main` through commits `b0d3e07`, `fc1c500`, and `5866f3e`.
- [x] Stage B live smoke evidence exists for template sync, user-level install smoke, Spec Kit sandbox apply, Spec Kit template apply, and Spec Kit repository apply; all recorded receipts keep `remote_publication_mutated=false`.
- [ ] This repository-apply evidence package is validating on branch `record-r6-spec-kit-repository-apply-20260609`; local gate, local MR review, and local `main` integration remain required before remote-publication approval.

<!-- CURRENT_STATUS_END -->

## Task Backlog
<!-- TASK_BACKLOG_START -->

- [x] Package 1: add bilingual R6 plan and merge it to local `main`.
- [x] Package 2: implement R6 checker/runtime/template support and validate affected gates.
- [x] Package 2: sync full reusable templates to `D:/PythonProject_General` and safe stubs to `D:/PythonProject_General_2`.
- [x] Package 2: execute user-level install smoke plus Spec Kit sandbox, repository, and template apply evidence.
- [ ] Package 2: integrate the repository-apply evidence package into local `main` and stop at the remote-publication approval gate.

<!-- TASK_BACKLOG_END -->

## Evidence Index
<!-- EVIDENCE_INDEX_START -->

- Plan package evidence: local `main` commit `5dd8592` adds this bilingual R6 implementation plan pair.
- Stage B implementation evidence: local `main` commits `b0d3e07`, `fc1c500`, and `5866f3e` added R6 runtime/checker/template support, OpenSpec gate fixtures, and template-source drift repair.
- Template and user-level smoke evidence: ignored local receipts under `.omx/r6-live-runtime/receipts/` record `user-level-install-smoke.json`, `spec-kit-sandbox-smoke.json`, and `spec-kit-template-smoke.json`; the template sync copied `0` files because both target templates already matched the source surfaces.
- Spec Kit repository apply evidence: branch `record-r6-spec-kit-repository-apply-20260609` preserves `.specify/r6-live-runtime/README.md` and `specs/r6-live-runtime/spec.md` as subordinate/no-takeover repository-apply surfaces, with `.omx/r6-live-runtime/receipts/spec-kit-repository-smoke.json` as the redacted live receipt.
- Checker evidence for the repository-apply package: `python test\spec_kit_authority_guard.test.py -v` and `python tools\check_spec_kit_authority_guard.py --root . --json` pass after allowing only the bounded R6 subordinate prefixes.
- Final local-main integration evidence will be carried by the local flow helper output for branch `record-r6-spec-kit-repository-apply-20260609`; remote publication remains unauthorized until a current user message names the remote action.

<!-- EVIDENCE_INDEX_END -->

## R6 Contract

R6 adds one promotion state above R5:

| Stage | Meaning | External action posture |
| --- | --- | --- |
| R5 active-candidate | A lane has valid active-candidate receipt evidence. | Validation only; no external action required. |
| R6 live-ready | A lane can enter live runtime routing by default. | Missing authorization or targets must produce a blocked receipt. |
| R6 live-executed | A bounded live action actually ran. | Must include redacted execution receipt, rollback/cleanup evidence, and no remote publication mutation. |

The R6 live receipt must include the R5 active fields plus:

- `receipt_type: r6-live-runtime` - identifies the receipt as an R6 live-runtime evidence record
- `live_mode: blocked | dry-run | live-ready | live-executed` - records whether the lane blocked, simulated, became ready, or actually executed
- `live_attempted: true | false` - records whether the live runtime path was entered
- `live_executed: true | false` - records whether a real bounded external action ran
- `external_side_effects: none | browser_gui | external_message | harness_job | spec_kit_apply | user_level_install | mixed` - classifies the external side-effect family, if any
- `target_env_keys`: names of environment variables used for target injection, not their raw values
- `target_env_hash`: stable hash of target material after redaction
- `execution_receipt`: redacted per-lane execution summary
- `blocked_reason`: required when `live_executed=false`
- `template_distribution`: `project-general-full | project-general-2-stub | repo-local-only | user-level`

Every R6 receipt must keep `remote_publication_mutated=false` unless the current user message explicitly authorizes remote publication.

## Template And User-Level Distribution

### Project-level common template

`D:\PythonProject_General` receives full project-level common support:

- R6 checker/helper templates that future projects may copy or hydrate.
- Default blocked receipt behavior when environment targets are absent.
- Documentation that these templates do not make consumer projects implementation locations for this orchestration repository.

### New-computer compatibility template

`D:\PythonProject_General_2` receives only compatibility stubs:

- Stub checker/README surfaces that explain R6 capability is available only after upgrading from the source repository or user-level installer.
- No default OMX, LangGraph, live harness, live browser, WXWork, or Spec Kit apply enablement.
- No `.omx/state/` runtime state copied into the template.

### User-level installation

User-level wrappers/config may be installed or updated only through receipt-backed helpers. Install/update receipts must include source path, installed path, wrapper path, smoke command, rollback pointer, owner lane, redaction status, and whether user-level state mutation was authorized.

## Environment Target Injection

Live targets must be passed by environment variables. Receipts may list variable names and hashes, but must not store raw sensitive values.

Canonical environment variable names:

- `R6_BROWSER_TARGET_URL` - provides the browser target URL for live browser smoke or action
- `R6_BROWSER_ACTION` - provides the allowed browser/GUI action name
- `R6_WXWORK_TARGET` - provides the WXWork recipient or target channel outside committed files
- `R6_WXWORK_MESSAGE_TEMPLATE` - provides the WXWork message template outside committed files
- `R6_HARNESS_CANDIDATE_ID` - selects the harness candidate id for the live job
- `R6_HARNESS_JOB_PROFILE` - selects the bounded harness job profile
- `R6_SPEC_KIT_MODE` - selects the Spec Kit apply boundary: `sandbox` means temporary directory or isolated worktree, `repository` means writable surfaces in this repository, and `template` means General/General_2 template surfaces
- `R6_SPEC_KIT_TARGET_ROOT` - provides the target root for Spec Kit live apply outside committed files
- `R6_USER_LEVEL_INSTALL_ROOT` - provides the user-level install root outside committed files

## Lane Requirements

### Capability, rollback, redaction foundation

Extend the shared receipt governance checker so R6 validates authorization, redaction, rollback, cleanup, target hashing, user-level mutation authorization, and blocked/live-executed result classification.

### Worktree receipt and selector ownership

R6 worktree and selector adoption may update local runtime receipts only inside owned repo-local state paths. Adoption must cite current owner lease and must not claim persistent-team execution without selector evidence.

### Durable readiness and LangGraph release

Durable readiness refresh and LangGraph release may run live status/release helpers only when the selected backend is ready and the receipt records the selector authority path. LangGraph state remains repo-local under `.omx/state/langgraph/`.

### Durable smoke adoption

Durable smoke may advance from read-only template smoke to live adoption only with a current lane receipt and explicit backend-family ownership. It must release or block cleanly on timeout.

### MCP/skills CLI runtime

MCP and skills CLI wrappers may be user-level installed and smoke-tested. Direct MCP calls or skill-discovery handoffs must record whether they were performed and must preserve the agent/skill/profile boundary.

### Browser/CLI adapter

Browser or GUI live action may run only with a target URL/action allowlist. Raw browser data must not be stored; receipts keep redacted summaries and target hashes.

### CLI-Anything / WXWork CLI

WXWork live send is allowed only at R6 with `R6_WXWORK_TARGET` and `R6_WXWORK_MESSAGE_TEMPLATE`. Receipts must not include message body or raw recipient. A blocked receipt is required when target or confirmation is missing.

### Stop-slop / response-density runtime

Response-density runtime may install or activate hooks only when rollback evidence and canary-preservation evidence are present. Default missing evidence blocks activation.

### gstack delivery loop

gstack remains advisory below Comet/OpenSpec/Superpowers. Live delivery-loop smoke may run, but it must not override Comet phase routing, OpenSpec WHAT authority, Superpowers HOW discipline, local-main-first gates, or remote-publication gates.

### Codex harnesses

Harness live jobs require candidate id, isolated worktree, read/write guards, no-Codex-takeover evidence, job state, changed-path report, timeout release, rollback, and cleanup evidence.

### Spec Kit authority and subordinate adapter

Spec Kit remains subordinate to harness runtime safety and cannot take over repository workflow control. R6 implements three allowed apply boundaries:

1. **Sandbox apply**: run `specify/init/apply` in a temporary directory or isolated worktree and write only the receipt back to the repository.
2. **Repository apply**: allow `.specify/` or root `specs/` in this repository only when Comet/OpenSpec explicitly owns the change and the receipt states Spec Kit is subordinate.
3. **Template apply**: allow template surfaces in `D:\PythonProject_General`; `D:\PythonProject_General_2` may receive stubs only.

## Implementation Packages

### Package 1: plan-only local integration

- Add this bilingual plan.
- Run pre-commit update/archive review.
- Run OpenSpec guard and local gates as appropriate.
- Commit and integrate into local `main` through the local-main-first helper.

### Package 2: R6 checker/runtime/template implementation

- Add/extend R6 receipt checker and templates.
- Add lane-specific runtime wrappers or live receipt modes.
- Add user-level install/smoke support.
- Sync `D:\PythonProject_General` full surfaces and `D:\PythonProject_General_2` stubs.
- Add tests and CI manifest entries.
- Commit lane-sized changes, validate, integrate into local `main`, and stop at the remote-publication approval gate.

## Acceptance Criteria

- R6 checker accepts valid blocked and live-executed receipts for all listed lanes.
- R6 checker rejects raw secrets, raw WXWork message bodies, raw browser payloads, missing owner leases, missing rollback, missing cleanup, and authority-order violations.
- Default daily runtime path produces blocked receipts rather than silent external actions when live evidence is incomplete.
- User-level install/smoke receipts can be validated without leaking raw paths or secrets.
- `D:\PythonProject_General` carries full reusable project-level templates; `D:\PythonProject_General_2` carries only safe stubs.
- Spec Kit sandbox, repository, and template apply boundaries are separately represented and checker-backed.
- Local gate and local MR review pass before local `main` integration.

## Non-goals

- This plan does not authorize remote publication.
- This plan does not make Spec Kit a Comet/OpenSpec replacement.
- This plan does not store external targets, secrets, WXWork message bodies, or raw browser data in committed files.
