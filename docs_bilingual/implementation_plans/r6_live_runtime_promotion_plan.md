---
doc_id: r6_live_runtime_promotion_plan
lang: en
status: active
doc_class: implementation_plan
stage: implementation-evidence
priority_order: Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit
zh_cn_path: docs_bilingual/implementation_plans/r6_live_runtime_promotion_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
---

# R6 Live Runtime Promotion Plan

> **For agentic workers:** use `superpowers:executing-plans` or `superpowers:subagent-driven-development` when implementing this plan. Keep Comet as the workflow control layer, OpenSpec as WHAT authority, and Superpowers as HOW authority.

## Goal

Promote the R5 checker-backed active-candidate gates into an R6 live-runtime promotion layer for the listed user-level runtime lanes while preserving the conflict-priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.

R6 means live runtime is default-discoverable and default-routable, but every sensitive external action remains fail-closed unless a current authorization receipt, owner lease, environment-provided target, rollback readiness, cleanup evidence, and redacted execution receipt are present.

## Scope

This plan originally covered these existing R5 plans as one governed rollout, and Stage G now extends completion checks to the full strict parent-plan family:

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
- [x] Stage B core R6 checker/runtime/template implementation merged to local `main` through commits `b0d3e07`, `fc1c500`, `5866f3e`, `6393796`, and `d3d57d0`.
- [x] Stage B live smoke evidence exists for template sync, user-level install smoke, Spec Kit sandbox apply, Spec Kit template apply, and Spec Kit repository apply; all recorded receipts keep `remote_publication_mutated=false`.
- [x] The Spec Kit repository-apply evidence package was integrated to local `main` in commit `d3d57d0` and the feature worktree/branch was cleaned; remote publication remains unauthorized.
- [x] Stage C coverage audit implementation now adds checker/runtime coverage evidence for all 14 R6 lanes: repo-local/default-safe lanes live-execute without external side effects, while browser/WXWork/harness/user-level-install/Spec Kit lanes default to blocked receipts when environment targets are absent.

- [x] Stage D sensitive live-action follow-up records Browser and Stop-Slop/Caveman as R6 `live-executed` with redacted receipts, while WXWork and Codex harnesses remain fail-closed `blocked` because no real send target or live harness job proof is present.
- [x] Stage E proof-intake hardening adds `proof-template` and `proof-check` runtime commands. `proof-template` writes a fill-after-real-action JSON skeleton without running external tools, and `proof-check` validates a redacted proof before the existing `run --mode live-action --proof-receipt ...` path can mark WXWork or harness evidence as `live-executed`.
- [x] Stage F bounded harness live-job evidence adds `tools/run_codex_harnesses_smoke.py r6-live-proof` and records Codex harnesses as R6 `live-executed` with a redacted isolated-worktree proof; the later Stage H family audit accepts WXWork as R6 `live-executed` through its redacted 2026-06-10 proof receipt.


- [x] Stage G full-family R6 completion plan package is complete for the strict `multi_plan_parallel_session_orchestration_plan` family. It expands this plan from the original 14 R6 runtime lanes to every active child, explicitly mentioned source, and successor-owned migration source under the parent plan.
- [x] Stage H implementation package adds checker/runtime coverage that classifies each family plan as direct R6 evidence, successor-owned migration source, governance/checker-runtime-only, or no-live-runtime-scope. Existing valid `live-executed` receipts are reused; the full-family checker currently accepts 53 family members with 14 direct R6 lanes and no stale status findings.
- [x] Stage I closeout records the strict parent-family R6 completion on top of local `main` commit `72c657a`; all direct lanes remain `live-executed`, successor-owned migration sources remain deleted but covered, and remote publication remains gated until a current message explicitly names the remote action.
<!-- CURRENT_STATUS_END -->

## Task Backlog
<!-- TASK_BACKLOG_START -->

- [x] Package 1: add bilingual R6 plan and merge it to local `main`.
- [x] Package 2: implement R6 checker/runtime/template support and validate affected gates.
- [x] Package 2: sync full reusable templates to `D:/PythonProject_General` and safe stubs to `D:/PythonProject_General_2`.
- [x] Package 2: execute user-level install smoke plus Spec Kit sandbox, repository, and template apply evidence.
- [x] Package 2: integrate the repository-apply evidence package into local `main` and stop at the remote-publication approval gate.
- [x] Package 3: add R6 lane coverage audit tooling that compares current receipt files against all 14 lanes and fails when a lane lacks default executable evidence.
- [x] Package 3: extend the R6 runtime with a default `run-all` batch mode that emits one valid R6 receipt per lane without silent external side effects.
- [x] Package 3: record Stage C receipt evidence for all 14 lanes; external browser/WXWork/harness/user-level-install/Spec Kit actions remain blocked when environment targets are absent, while the blocked receipts are current, redacted, and checker-accepted.

- [x] Package 4: run and record sensitive live-action follow-up evidence; accept Browser and Stop-Slop/Caveman live-executed proof, and retain WXWork/Harness blocked receipts until real proof gates exist.
- [x] Package 5: add fail-closed proof-intake templates and proof validation for WXWork and Codex harnesses so future real live proof can be checked without storing raw recipient, message, browser, or harness payloads.
- [x] Package 6: implement and execute a bounded repo-local Codex harness proof job that runs in a temporary isolated Git worktree, rolls back/cleans up, then promotes `codex-harnesses-governance` to R6 `live-executed` through `proof-check` and `run --mode live-action`.


- [x] Package 7: update this R6 plan for strict parent-family scope, successor-owned migration sources, and full-family live-runtime classification before implementation.
- [x] Package 8: implement the full-family R6 checker/runtime reconciliation, update stale plan statuses, validate all direct R6 lane receipts, and integrate into local `main`.
- [x] Package 9: record R6 full-family closeout status and evidence in the parent plan and this R6 promotion plan, then validate and merge the closeout package to local `main`.
<!-- TASK_BACKLOG_END -->

## Evidence Index
<!-- EVIDENCE_INDEX_START -->

- Plan package evidence: local `main` commit `5dd8592` adds this bilingual R6 implementation plan pair.
- Stage B implementation evidence: local `main` commits `b0d3e07`, `fc1c500`, and `5866f3e` added R6 runtime/checker/template support, OpenSpec gate fixtures, and template-source drift repair.
- Template and user-level smoke evidence: ignored local receipts under `.omx/r6-live-runtime/receipts/` record `user-level-install-smoke.json`, `spec-kit-sandbox-smoke.json`, and `spec-kit-template-smoke.json`; the template sync copied `0` files because both target templates already matched the source surfaces.
- Spec Kit repository apply evidence: local `main` commit `6393796` preserves `.specify/r6-live-runtime/README.md` and `specs/r6-live-runtime/spec.md` as subordinate/no-takeover repository-apply surfaces, with `.omx/r6-live-runtime/receipts/spec-kit-repository-smoke.json` as the redacted live receipt.
- Spec Kit repository apply stabilization evidence: local `main` commit `d3d57d0` fixes the durable-routing smoke command guard so worktree paths ending in `-apply` do not count as apply authorization while true `--apply`/`-Apply`/`/apply` flags still fail closed.
- Checker evidence for the repository-apply package: `python test\spec_kit_authority_guard.test.py -v`, `python tools\check_spec_kit_authority_guard.py --root . --json`, `python test\check_durable_routing_smoke_receipts.test.py -v`, full `tools\ci\local_gate.ps1`, and `tools\ci\local_mr_review.ps1` passed before local `main` integration.
- Stage C coverage audit seed: current receipt inventory finds live-executed receipts for `spec-kit-authority-guard`, `spec-kit-subordinate-adapter-governance`, and `user-level-mcp-skills-cli-runtime` only. Missing current receipt coverage remains for the other 11 lanes until Package 3 lands.
- Stage C implementation evidence: `tools/check_r6_live_runtime_receipts.py` now supports `--receipt-dir` and `--require-coverage`; `tools/r6_live_runtime.py run-all` writes one Stage C receipt per lane with no browser/GUI, external message, harness job, user-level install, Spec Kit apply, or remote publication mutation by default.
- Stage C receipt evidence: `python tools\r6_live_runtime.py run-all --root . --json` and `python tools\check_r6_live_runtime_receipts.py --root . --receipt-dir .omx\r6-live-runtime\receipts --require-coverage --json` accepted all 14 lanes. Machine-readable evidence: `docs_bilingual/implementation_evidence/r6_live_runtime_stage_c_coverage_evidence_20260609.json`; human-readable summaries: `docs_bilingual/implementation_evidence/r6_live_runtime_stage_c_coverage_evidence_20260609.md` and `docs_bilingual/implementation_evidence/r6_live_runtime_stage_c_coverage_evidence_20260609.zh-CN.md`.
- Stage C template sync evidence: `python tools\r6_live_runtime.py sync-templates --root . --general-root D:\PythonProject_General --general2-root D:\PythonProject_General_2 --update-managed --json` refreshed managed template files only, reported `remote_publication_mutated=false`, and preserved General_2 as a stub-only surface.
- Remote publication remains unauthorized until a current user message names the remote action.
- Stage D sensitive live-action follow-up evidence - `live-executed` means a bounded live action ran with proof, and `blocked` means the runtime recorded an unmet proof gate: `.omx/r6-live-runtime/receipts/browser-live-action-followup.json` and `.omx/r6-live-runtime/receipts/stop-slop-caveman-live-executed-followup.json` are current valid `live-executed` receipts selected by `tools/check_r6_live_runtime_receipts.py --require-coverage`; `.omx/r6-live-runtime/receipts/wxwork-live-action-blocked-followup.json` and `.omx/r6-live-runtime/receipts/harness-live-action-blocked-followup.json` remain valid `blocked` receipts because real WXWork message-send proof and real guarded harness-job proof are absent. Human-readable evidence: `docs_bilingual/implementation_evidence/r6_sensitive_live_action_evidence_20260609.md` and `.zh-CN.md`.
- Stage E proof-intake hardening evidence - `tools/r6_live_runtime.py proof-template` is the fail-closed template generator for a future real external proof file, and `tools/r6_live_runtime.py proof-check` is the redaction and required-field validator for that proof file. Tests: `python test\r6_live_runtime.test.py -v` passes 18/18 and covers accepted redacted WXWork/harness proofs plus rejection of raw WXWork body or recipient material.
- Stage F bounded harness live-job evidence - `tools/run_codex_harnesses_smoke.py r6-live-proof` now runs one bounded local harness job in a temporary isolated Git worktree and writes a redacted proof. `tools/r6_live_runtime.py proof-check` accepts that proof only when candidate id, job profile, read/write guards, isolated worktree, job state, changed-path report, timeout release, rollback, cleanup, and no-Codex-takeover evidence pass. The follow-up receipt `.omx/r6-live-runtime/receipts/harness-live-job-live-executed-20260609.json` validates as R6 `live-executed` for `codex-harnesses-governance`; proof hash `e0f71f0789945588`, candidate hash `47ab92541ddbb827`, remote publication mutated `false`. WXWork was still `blocked` at Stage F and is later accepted by Stage H through `.omx/r6-live-runtime/receipts/wxwork-live-executed-20260610.json`.
- Stage H full-family checker evidence - `tools/check_multi_plan_family_r6_live_runtime.py` classifies the strict parent family and delegates direct-lane evidence to `tools/check_r6_live_runtime_receipts.py --require-coverage`. Current validation with receipt directory `D:\PythonProject_langgraph\.omx\r6-live-runtime\receipts` reports `ok=true`, `family_members=53`, `direct_r6_lane=14`, `successor_owned_migration_source=2`, `governance_checker_runtime=29`, `no_live_runtime_scope=8`, `stale_status_findings=0`, `restored_deleted_migration_sources=0`, and `remote_publication_mutated=false`. The WXWork successor lane is accepted through `.omx/r6-live-runtime/receipts/wxwork-live-executed-20260610.json` with only hashes/redacted proof metadata committed.
- Stage I closeout evidence - `python -B tools\check_multi_plan_family_r6_live_runtime.py --root . --receipt-dir D:\PythonProject_langgraph\.omx\r6-live-runtime\receipts --require-coverage --json` reports `ok=true`, `family_members=53`, `direct_r6_lane=14`, `successor_owned_migration_source=2`, `governance_checker_runtime=29`, `no_live_runtime_scope=8`, `stale_status_findings=0`, and `coverage_ok=true`; focused tests `test\test_check_multi_plan_family_r6_live_runtime.py` and `test\run_openspec_guard_json.test.py` pass.
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

WXWork live send is allowed only at R6 with `R6_WXWORK_TARGET` and `R6_WXWORK_MESSAGE_TEMPLATE`. Receipts must not include message body or raw recipient. A blocked receipt is required when target or confirmation is missing. `proof-template` and `proof-check` provide a two-step proof-intake path: first create a skeleton for the post-send proof, then validate only hashes and status fields before promotion to `live-executed`.

### Stop-slop / response-density runtime

Response-density runtime may install or activate hooks only when rollback evidence and canary-preservation evidence are present. Default missing evidence blocks activation.

### gstack delivery loop

gstack remains advisory below Comet/OpenSpec/Superpowers. Live delivery-loop smoke may run, but it must not override Comet phase routing, OpenSpec WHAT authority, Superpowers HOW discipline, local-main-first gates, or remote-publication gates.

### Codex harnesses

Harness live jobs require candidate id, isolated worktree, read/write guards, no-Codex-takeover evidence, job state, changed-path report, timeout release, rollback, and cleanup evidence. `proof-template` and `proof-check` make those proof fields explicit before a harness receipt can be promoted from `blocked` to `live-executed`.

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


## Stage G: Full Parent-Family R6 Completion Scope

This stage broadens the rollout from the original 14 direct R6 lane profiles to the full strict family governed by `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`. Strict family membership means:

- an English primary implementation plan declares `parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`; or
- the parent plan explicitly names the plan as a source, split, migration, integration, or child target.

The implementation package must not restore deleted migration-source plans. Deleted source plans such as `user_level_mcp_skills_discovery_facade_plan` and `user_level_mcp_skills_browser_cli_governance_plan` are covered only through their successor owners, especially `user_level_mcp_skills_cli_runtime_plan`, `user_level_browser_cli_adapter_boundary_plan`, `user_level_cli_anything_wxwork_cli_governance_plan`, and `codex_harnesses_governance_plan`.

Each family plan must receive exactly one completion classification:

| Classification | Meaning | Required evidence |
| --- | --- | --- |
| `direct-r6-lane` | The plan maps to a known R6 lane in `tools/check_r6_live_runtime_receipts.py`. | Accepted `live-executed` receipt, or accepted sensitive-lane blocked/ready policy only when the family completion plan explicitly allows it. |
| `successor-owned-migration-source` | The plan was a temporary migration source or deleted source plan and is no longer an execution owner. | Successor plan path, successor R6 lane, and no restoration of the deleted source plan. |
| `governance-checker-runtime` | The plan implements repository-local governance, checker, guard, helper, CI, or evidence runtime rather than an external side-effect lane. | Checker/helper/local-gate evidence and no missing external action requirement. |
| `no-live-runtime-scope` | The plan is an index, archive, parent, or documentation-only scope that should not run live runtime. | Explicit rationale and no false R6 execution claim. |

Authority priority remains mandatory for every classification and receipt:

```text
Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit
```

Spec Kit evidence remains subordinate and cannot satisfy Comet, OpenSpec, Superpowers, gstack, or harness runtime safety evidence by itself. Harness evidence cannot bypass harness runtime safety. gstack evidence remains advisory and cannot override Comet/OpenSpec/Superpowers or local-main-first gates.

External-action lane policy for this stage is reuse-first: existing valid `live-executed` receipts under `.omx/r6-live-runtime/receipts/` are accepted. A real browser, WXWork, harness, Spec Kit apply, or user-level install action is rerun only when the checker reports the lane as missing, stale, invalid, or blocked and the needed target/authorization evidence is available. Receipts remain hash-only/redacted and must keep `remote_publication_mutated=false`.

## Package 8: Full-Family Checker And Runtime Reconciliation

The implementation package adds `tools/check_multi_plan_family_r6_live_runtime.py` plus focused tests. The checker:

- discovers strict family members from front matter and parent-plan references;
- reports missing plan files as `successor-owned-migration-source` only when an active successor is known;
- requires all direct R6 lanes accepted by `tools/check_r6_live_runtime_receipts.py --require-coverage`;
- rejects stale child-plan wording that says R5-only, blocked, or pending when accepted R6 evidence exists;
- preserves deleted migration-source boundaries instead of recreating deleted files;
- emits JSON with counts, classifications, missing evidence, authority-priority status, and remote-publication mutation status;
- is wired into `tools/run_openspec_guard.py` and CI manifest coverage as a repository guard surface.

## Non-goals

- This plan does not authorize remote publication.
- This plan does not make Spec Kit a Comet/OpenSpec replacement.
- This plan does not store external targets, secrets, WXWork message bodies, or raw browser data in committed files.
