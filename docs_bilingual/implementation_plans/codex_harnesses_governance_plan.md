---
doc_id: codex_harnesses_governance_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/codex_harnesses_governance_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
supersedes:
  - docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.md
  - docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
---

# Codex Harnesses Governance Plan

> **For agentic workers:** use `superpowers:executing-plans`. This plan is the only child plan in this split that owns the word `harnesses`; CLI-Anything/WXWork_CLI and Browser/CLI adapters are not harnesses.

## Goal

Fork a Codex-specific harnesses governance model from the listed harness/Pi references while keeping Codex as the primary controller. The refreshed model treats Codex harnesses as a candidate-registry-driven runtime boundary rather than a Pi-only wrapper: candidates can be Pi runtime packages, oh-my-pi sidecars, team-architecture factories, discipline-agent layers, or terminal agent runtimes, but every candidate must remain subordinate to the current Codex leader, local-main-first publication gates, and checker-backed read/write guards.

## Architecture

Project-level governance lands first in this repository as docs, guard contracts, tests, state schemas, and candidate-registry requirements. Reusable project-level helpers come next. User-level runtime surfaces are allowed only after project-level guards pass and receipts prove candidate pin, license posture, install/update evidence, read-only smoke, rollback, redaction, sensitive-command policy, and no takeover of Codex launchers or durable lanes.

## Tech Stack

Codex CLI, Git worktrees, JSON job state, Python guard/checker scripts, OpenSpec, docs registry, candidate registry, Pi reference runtime, oh-my-pi reference UX, revfactory/harness team-factory reference patterns, ohmyopenagent discipline-agent reference patterns, snow-cli terminal-agent runtime reference patterns, and user-level Codex state only after receipt-backed promotion.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented-local; Stage B source-ledger/checker/spec migration is complete; Stage C runtime-promotion ladder is documented and checker-backed; Stage D real-runtime implementation is planned but not executed; the 2026-06-07 R4 local checker/runtime tooling is now candidate-registry-driven across five reference candidates; remote publication remains closed.
Runtime boundary: Codex harnesses are governance wrappers around future harness jobs; they do not replace Codex, native subagents, native_omx, LangGraph, codex-ohmy, apply_patch, or local-main-first publication gates. This package does not install Pi/oh-my-pi, clone or vendor revfactory/harness, copy ohmyopenagent or snow-cli code/config, start any sidecar, run a real harness job, or mark the lane installed-user-level/smoke-tested/active-candidate. Runtime promotion remains not installed/started/enabled in this package.
Runtime gap: real runtime work still requires a selected candidate install/update path, executable write-capable harness job runner, R3 install/update receipts, positive R4 read-only smoke receipts, and R5 bounded live handoff receipts with isolated worktree evidence. Current R4 helper/checker work is honest local candidate-registry tooling only; it does not install, start, or live-run Pi/oh-my-pi, revfactory/harness, ohmyopenagent, snow-cli, or any newly referenced runtime.
Implementation evidence: `tools/check_codex_harnesses_governance.py` now requires all seven source ledger rows plus candidate-registry markers, candidate ids, adapter kinds, source pin, retrieved_at, license note, rollback pointer, no Codex takeover, unpinned Pi packages rejection, read guard, write guard, job state, isolated worktree, changed-path report markers, R0-R5 runtime promotion markers, and `authority_decision`. `tools/run_codex_harnesses_smoke.py` and `tools/check_codex_harnesses_smoke_receipts.py` now emit and validate five candidate-registry R4 receipt shapes.
Companion refresh note: the zh-CN companion is updated in the same local package to record the same reference sources and next Checker + Runtime requirements while preserving runtime tokens; no runtime behavior changed.
Priority update: 2026-06-07 records Codex harnesses as subordinate runtime-safety governance below Comet, OpenSpec/Superpowers, and gstack advisory ordering; harness guards outrank Spec Kit only for runtime safety.
<!-- CURRENT_STATUS_END -->

## Conflict Priority

Codex harnesses govern candidate runtime safety, job receipts, read/write guards, sidecar boundaries, and no-Codex-takeover evidence. They do not control Comet phase routing, OpenSpec WHAT authority, Superpowers HOW discipline, gstack advisory delivery-loop sequencing, implementation-plan claims, local-main-first gates, or remote-publication gates. When harness guards conflict with Spec Kit templates or probes, harness safety wins for runtime permission, write scope, receipts, rollback, timeout, and cleanup. Future checker/runtime work must emit `authority_decision` for each candidate allow/block/active-candidate result and must explain whether the decision came from Comet, OpenSpec/Superpowers, gstack advisory ordering, harness runtime safety, or Spec Kit subordinate-template status.

## Source Ledger

| Reference | URL | Source pin | retrieved_at | License note | Rollback pointer | What this Codex fork may reuse | What it must not do |
| --- | --- | --- | --- | --- | --- | --- | --- |
| The Harness Problem | https://blog.can.ac/2026/02/12/the-harness-problem | source pin: URL snapshot | retrieved_at: 2026-06-04 | license note: article reference only | rollback pointer: remove derived harness rules | reliability ideas, recoverable editing, explicit failure surfacing | copy unknown code or bypass repo guards |
| oh-my-pi | https://github.com/can1357/oh-my-pi | source pin: `d9f5a8c7ac770b91d75d6df52459bd16042936fe` on `main` as observed 2026-06-06 | retrieved_at: 2026-06-04 and refreshed 2026-06-06 | license note: inspect upstream license before reuse | rollback pointer: remove sidecar helper copy and candidate receipt | sidecar UX, update/rollback concepts, Pi-oriented runtime ergonomics, hash-anchored edit ideas | replace Codex launcher or own provider secrets |
| Pi | https://pi.dev/ | source pin: docs version or snapshot required before runtime implementation | retrieved_at: 2026-06-04 | license note: docs reference only | rollback pointer: remove Pi runtime assumptions | Pi runtime/RPC reference and future smoke source | mutate current worktree without one-task authorization |
| Pi packages | https://pi.dev/packages | source pin: package version required for each candidate | retrieved_at: 2026-06-04 | license note: package license must be recorded per package | rollback pointer: remove package candidate and receipt | package discovery/update reference and package pin model | install packages without pin/receipt/rollback evidence |
| revfactory/harness | https://github.com/revfactory/harness | source pin: `b8fb858ea9209d6b0d9000e551d3dedbbacb88aa` on `main` as observed 2026-06-06 | retrieved_at: 2026-06-06 | license note: GitHub reports Apache-2.0; keep reference-only unless a later change explicitly vendors code | rollback pointer: remove team-factory candidate and derived pattern rows | team-architecture factory, domain-specific agent-team design, specialized-agent/skill generation, pipeline/fan-out/expert-pool/supervisor patterns | import its agent definitions wholesale or let generated teams replace Codex leader routing |
| ohmyopenagent | https://github.com/ymymssss/ohmyopenagent | source pin: `4b923aaa7e7660a57623a2cf59fd92e47fced772` on default branch `feat-zh-cn-system-prompts` as observed 2026-06-06 | retrieved_at: 2026-06-06 | license note: GitHub reports NOASSERTION/Other; reference-only, no code or config copying without later license review | rollback pointer: remove discipline-agent candidate and derived prompt-boundary rows | discipline agents, intent gate, hash-anchored edit discipline, tool/MCP/skill boundary ideas, uninstall/rollback posture | copy prompts/configs or treat its governance package as installed runtime |
| snow-cli | https://github.com/MayDay-wpf/snow-cli | source pin: `f1846e27b655832f52b1e51c190a12b58219cc71` on `main` as observed 2026-06-06 | retrieved_at: 2026-06-06 | license note: GitHub reports NOASSERTION/Other; reference-only, no code or config copying without later license review | rollback pointer: remove terminal-agent candidate and derived CLI-runtime rows | terminal agent runtime, sub-agent config, hooks/MCP, sensitive-command governance, headless/async task governance, multi-provider CLI ergonomics | run as a sidecar, mutate user config, or execute sensitive commands without explicit future authorization |

## Codex Harness Redesign From The Expanded Source Set

| Source family | Governance lesson | Codex harness decision |
| --- | --- | --- |
| The Harness Problem + oh-my-pi | Harness reliability depends on hash-anchored edits, recoverable edit records, explicit failures, update receipts, rollback, and job-state visibility. | Every runtime candidate needs immutable source/package pins, hash/path receipt material, rollback pointer, timeout release, explicit failure states, and changed-path reporting. |
| Pi + Pi packages | Runtime/package ecosystems require version pinning, install/update receipts, smoke commands, package license capture, and rollback before promotion. | R3 is not a generic install flag; it is an installed-user-level receipt for a selected candidate id and package/source pin. R4 smoke-tested evidence must point to that R3 receipt. |
| revfactory/harness | A harness can be a team-architecture factory that generates domain-specific agent teams and skills, not just a package runner. | The registry must model factory/team-pattern candidates and require generated-team outputs to stay advisory until Codex leader accepts them. |
| ohmyopenagent | Discipline agents and intent gates can protect edits, tool choice, MCP boundaries, and rollback/uninstall behavior. | The registry must model discipline-layer candidates separately from runtime runners and require intent-gate/read-write-guard evidence before any write-capable handoff. |
| snow-cli | Terminal agent runtimes need sub-agent config, hooks, MCP integration, sensitive-command policy, and headless/async task governance. | The registry must model terminal-runtime candidates with sensitive-command allowlists, hook policy, async/headless lifecycle state, and no user-config mutation by default. |

Candidate registry means a machine-checkable list of possible harness candidates with stable `candidate_id`, `source_url`, `source_pin`, `license_note`, `adapter_kind`, `runtime_stage`, `allowed_actions`, `guard_profile`, `rollback_pointer`, and `receipt_paths`. It prevents future Checker + Runtime work from hard-coding Pi/oh-my-pi as the only eligible runtime family.

## Implemented R4 Candidate Registry Tooling

The 2026-06-07 R4 local package implements candidate-registry-driven checker and smoke-receipt tooling without installing or starting any candidate runtime. The local registry used by `tools/run_codex_harnesses_smoke.py` and validated by `tools/check_codex_harnesses_smoke_receipts.py` includes:

| candidate_id | adapter_kind | source_url | R4 local posture |
| --- | --- | --- | --- |
| `pi-runtime` | `package-runtime` | `https://pi.dev/` and `https://pi.dev/packages` | blocked without an R3 install/update receipt; passing smoke is read-only only. |
| `oh-my-pi-sidecar` | `sidecar-ux` | `https://github.com/can1357/oh-my-pi` | blocked without an R3 install/update receipt; no sidecar start or Codex takeover. |
| `revfactory-harness-team-factory` | `team-factory` | `https://github.com/revfactory/harness` | reference-only team-factory candidate; generated teams remain advisory under Codex leader ownership. |
| `ohmyopenagent-discipline-layer` | `discipline-layer` | `https://github.com/ymymssss/ohmyopenagent` | reference-only discipline-layer candidate; no prompt/config copying before license review. |
| `snow-cli-terminal-agent-runtime` | `terminal-agent-runtime` | `https://github.com/MayDay-wpf/snow-cli` | reference-only terminal-agent-runtime candidate; no user config mutation, hooks, or sensitive commands. |

Each R4 receipt shape must carry `candidate_id`, `adapter_kind`, `guard_profile`, `source_url`, `source_pin`, `license_note`, `sensitive_command_policy`, `hook_policy`, `async/headless` lifecycle evidence via `async_headless_lifecycle_state`, and `authority_decision`. The authority decision records the runtime-safety priority order Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit and distinguishes blocked receipts from `allow-read-only-smoke` receipts.

## R0-R4 Revision Impact

The earlier R4-before implementation remains valid as local governance evidence, but it is too narrow for the expanded source set. Before any real Checker + Runtime implementation proceeds, R0-R4 must be reinterpreted as candidate-registry-driven:

- R0 must collect all seven source rows and reject candidates without source pin, retrieved_at, license note, and rollback pointer.
- R1 must use fake/dry-run fixtures per candidate kind: package runtime, sidecar UX, team-factory, discipline layer, and terminal agent runtime.
- R2 must expose reusable registry/schema/checker helpers, not Pi-only field names.
- R3 must record installed-user-level receipts per selected candidate id and refuse NOASSERTION/Other references for code copying or config vendoring.
- R4 must run read-only smoke/status probes through the selected candidate adapter and accept blocked receipts only as honest non-smoke-tested evidence.

No existing R4 local smoke receipt is retroactively promoted to real runtime evidence by this refresh.

## Governance Level Split

| Stage | Governance level | Allowed work | Promotion gate |
| --- | --- | --- | --- |
| 0 | project-level | source ledger, candidate registry, taxonomy, no-takeover policy | docs/OpenSpec gate |
| 1 | project-level | candidate-state schema, read-only guard, write guard, fake runtime fixtures | focused tests and local gate |
| 2 | reusable project-level | portable harness guard/checker pattern for other repos | examples and redaction checks |
| 3 | user-level | selected candidate install-record, update-record, rollback-plan, smoke plan | explicit user authorization and passing project-level guard |
| 4 | user-level active-candidate | bounded read-only smoke or sidecar/terminal/factory status probe | isolated worktree, job state, no takeover, changed-path report |

## Runtime Promotion Ladder

This lane uses the shared R0-R5 ladder and remains not installed/started/enabled in this package.

| Runtime stage | Level | Codex harnesses scope | Evidence gate |
| --- | --- | --- | --- |
| R0 project-level preflight | project-level | Refresh the source ledger for The Harness Problem, oh-my-pi, Pi, Pi packages, revfactory/harness, ohmyopenagent, and snow-cli; inspect package/runtime/factory/discipline/terminal assumptions without installing or running any candidate. | Source URLs, source pin, retrieved_at, license note, rollback pointer, no Codex takeover, candidate registry entry. |
| R1 project-level fake/dry-run runtime | project-level | Run fake candidate job fixtures and deterministic read guard/write guard checks only. | Fake Pi job or fake candidate job state, read guard, write guard, no live runtime, no Codex launcher mutation. |
| R2 reusable project-level helper/guard | reusable project-level | Keep reusable harness guard/checker schemas for candidate registry, job state, isolated worktree, changed-path report, redaction, sensitive-command policy, hook policy, async/headless policy, and rollback. | Guard schema, local tests, local gate, changed-path report. |
| R3 user-level install/update receipt | user-level | Record selected candidate install/update only after explicit authorization, immutable source/package pin, install/update receipt, smoke command, updater command, rollback pointer, owner lane, and path hashes. | `installed-user-level` receipt, candidate id, package/source pin, no unpinned Pi packages or unpinned registry candidates, no launcher takeover. |
| R4 user-level smoke runtime | user-level | Run bounded read-only candidate smoke or status probe through `tools/run_codex_harnesses_smoke.py` or its future registry-driven replacement; no write-capable harness job. | `smoke-tested` receipt validated by `tools/check_codex_harnesses_smoke_receipts.py` or future registry checker, read guard, job state, timeout release, redaction, rollback readiness; missing R3 install receipts produce blocked receipts that are not smoke-tested. |
| R5 active-candidate / bounded live handoff | user-level active-candidate | Active candidate may run one bounded harness job only under Codex leader ownership. | `active-candidate` receipt, isolated worktree, read guard, write guard, job state, no Codex takeover, changed-path report, rollback/cleanup evidence. |

A Codex harnesses active sidecar must not replace Codex, native subagents, native_omx, LangGraph, codex-ohmy, apply_patch, local-main-first publication gates, or the current main Codex CLI leader session.

## R4 Scope Implemented And Remaining Real Runtime Requirements

The 2026-06-07 local package implements the checker/runtime receipt surfaces below, while leaving real user-level install, real sidecar/terminal/factory start, write-capable harness jobs, and R5 live handoff unimplemented:

1. `tools/check_codex_harnesses_governance.py` and tests require all seven source URLs, source pins, retrieved_at values, license notes, rollback pointers, candidate-registry markers, five `candidate_id` values, and five `adapter_kind` values.
2. `tools/run_codex_harnesses_smoke.py` exposes an R4 local candidate registry with `pi-runtime`, `oh-my-pi-sidecar`, `revfactory-harness-team-factory`, `ohmyopenagent-discipline-layer`, and `snow-cli-terminal-agent-runtime`.
3. `tools/check_codex_harnesses_smoke_receipts.py` requires R4 smoke receipts to include `candidate_id`, `adapter_kind`, `guard_profile`, `source_pin`, `license_note`, `sensitive_command_policy`, `hook_policy`, `async/headless` lifecycle evidence, and `authority_decision`.
4. Keep NOASSERTION/Other references (`ohmyopenagent`, `snow-cli`) reference-only until a later license review explicitly permits copying; Apache-2.0 reference patterns (`revfactory/harness`) still require a later vendoring decision before code copy.
5. Preserve Codex leader ownership: generated teams, discipline agents, hooks, MCP surfaces, and terminal sub-agents can advise or run bounded jobs only after Codex-selected guards pass.
6. Ensure every R5 live handoff has owner lease, isolated worktree, read/write guard, changed-path report, timeout release, rollback pointer, cleanup evidence, and no remote publication mutation.

## Stage D Pending Runtime Work List

- Stage D real runtime: implement candidate-registry-backed install/update receipt with pinned source/package, rollback pointer, license posture, and no-Codex-takeover evidence.
- Stage D real runtime: implement harness job runner receipts with executable read/write guards, isolated worktree evidence, changed-path reporting, cleanup, sensitive-command policy, hook policy, async/headless state, and rollback.
- Stage D real runtime: run bounded R4 read-only smoke/status through a registry-backed runner and record a `smoke-tested` receipt before any R5 active-candidate handoff.
- Stage D real runtime: gate any R5 live harness job behind current operator authorization, owner lease, target/action allowlist, timeout release, and post-run cleanup evidence.
- Stage D Checker + Runtime: require `authority_decision` on candidate allow/block/active-candidate receipts and enforce the priority order Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit.

## File Ownership

This child plan owns Codex harness governance docs, future `codex_harnesses_governance` checker/guard, source ledgers, candidate registry schemas, job-state schemas, and read-only/write guard tests. It does not own CLI-Anything, WXWork_CLI, chrome-devtools-mcp, cdp-bridge-mcp, or OpenCLI.

## Parallel Session Contract

One session may claim this implementation plan at a time. A separate session may work on CLI-Anything/WXWork_CLI or Browser/CLI adapters only when it does not edit this plan, future harness checker/tests, docs registry, CI manifest, or shared OpenSpec hotspots without a serialized lease.

## Real Runtime Implementation Gap

This plan is not complete at the real-runtime level. The implemented-local package covers governance, checker, test, source-ledger, and R0-R2 dry-run contracts only. A later runtime package must provide:

- Candidate registry entries for each selected source family with source pin, package/version pin when applicable, license record, adapter kind, install/update command, rollback pointer, and sanitized install/update receipt.
- A harness job runtime that records job id, candidate id, isolated worktree, requested read/write scope, read guard result, write guard result, sensitive-command policy, hooks policy, async/headless lifecycle state, changed paths, timeout, cleanup, and rollback evidence.
- R3 receipt material for installed-user-level state, R4 smoke-tested read-only sidecar/status/job fixture, and R5 active-candidate bounded live handoff evidence.
- Proof that Codex remains the leader and no sidecar, generated team, discipline agent, terminal CLI, or hook replaces Codex launchers, native subagents, native_omx, LangGraph, `codex-ohmy`, `apply_patch`, or local-main-first gates.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Stage A: state that only this lane is called Codex harnesses.
- [x] Stage A: record The Harness Problem, oh-my-pi, Pi, and Pi packages reference links.
- [x] Stage A: state no Codex takeover, no replacement of native Codex/OMX/LangGraph/apply_patch, and no live Pi execution.
- [x] Stage B: add source ledger requirements for source pin, retrieved_at, license note, and rollback pointer.
- [x] Stage B: add checker/spec coverage for no Codex takeover, no unpinned Pi packages, read guard, write guard, job state, isolated worktree, and changed-path report.
- [x] Stage B: wire checker/tests into CI manifest, safety registry, and OpenSpec guard.
- [x] Stage C runtime promotion: add R0-R5 Codex harnesses ladder, fake Pi job dry-run boundary, installed-user-level/smoke-tested/active-candidate markers, and no-takeover active sidecar gates.
- [x] R4 local smoke receipt tooling: add `tools/run_codex_harnesses_smoke.py`, `tools/check_codex_harnesses_smoke_receipts.py`, and `codex_harnesses_smoke_receipts.test.py`; blocked receipts are accepted but remain not smoke-tested.
- [x] 2026-06-06 source refresh: record revfactory/harness, ohmyopenagent, and snow-cli as reference-only sources; redesign the next runtime direction as candidate-registry-driven; record Checker + Runtime follow-up requirements without implementing them.
- [x] 2026-06-07 conflict-priority refresh: record harnesses below Comet/OpenSpec/Superpowers/gstack and above Spec Kit only for runtime safety; require future `authority_decision` evidence without implementing scripts.
- [x] 2026-06-07 R4 candidate-registry checker/runtime: update governance checker, smoke runner, smoke receipt checker, tests, stable spec, and safety registry to require all seven sources, five candidates, five adapter kinds, R4 receipt policy fields, and `authority_decision` while keeping real install/start/live handoff unimplemented.
<!-- TASK_BACKLOG_END -->

## Stage B Closure Notes

- Stage B adds `codex_harnesses_governance` checker coverage for the harness-only lane.
- R4 adds `codex_harnesses_smoke_receipts` checker coverage for bounded smoke receipts, including blocked receipts that do not count as smoke-tested.
- Source refresh now requires source URL, source pin/ref, retrieved_at, license note, and rollback pointer.
- Sidecar output remains non-actionable without read guard, write guard, job state, isolated worktree, and changed-path report evidence.
- CI manifest, safety registry, and OpenSpec guard wiring now reference the split harness checker.

## Stage E / R4 Candidate Registry Notes

- The added references no longer sit only in prose: the R4 governance checker and smoke receipt checker now require the expanded registry evidence.
- `revfactory/harness` adds the `revfactory-harness-team-factory` candidate id and `team-factory` adapter kind.
- `ohmyopenagent` adds the `ohmyopenagent-discipline-layer` candidate id and `discipline-layer` adapter kind.
- `snow-cli` adds the `snow-cli-terminal-agent-runtime` candidate id and `terminal-agent-runtime` adapter kind with hooks, MCP, sensitive-command, and async/headless governance.
- This package changes local checker/runner/test/spec surfaces only: no user-level install, sidecar start, package copy, user config mutation, write-capable harness job, active-candidate handoff, or remote publication occurs here.

## Acceptance Criteria

- Codex harnesses is a distinct lane from CLI-Anything/WXWork_CLI and Browser/CLI adapters.
- All seven reference links are recorded with source pin, retrieved_at, license note, and rollback pointer.
- The R4 local candidate registry includes `pi-runtime`, `oh-my-pi-sidecar`, `revfactory-harness-team-factory`, `ohmyopenagent-discipline-layer`, and `snow-cli-terminal-agent-runtime`.
- The R4 local adapter kinds include `package-runtime`, `sidecar-ux`, `team-factory`, `discipline-layer`, and `terminal-agent-runtime`.
- Pi/oh-my-pi is reference or user-level sidecar candidate only, never the Codex launcher.
- revfactory/harness, ohmyopenagent, and snow-cli remain reference-only until a later Checker + Runtime package explicitly implements candidate-registry checks and runtime adapters.
- No user-level runtime is active without receipt, pin, smoke, rollback, redaction, license posture, sensitive-command policy, and no-takeover evidence.
- Any future write-capable harness path requires isolated worktree ownership and changed-path reporting.
- Codex harnesses runtime promotion is explicit: R0/R1/R2 remain project-level or reusable project-level; R3 requires `installed-user-level`; R4 requires `smoke-tested`; R5 requires `active-candidate`, isolated worktree, job state, read/write guards, changed-path report, and no Codex takeover.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-07 R4 candidate-registry checker/runtime evidence: `tools/check_codex_harnesses_governance.py`, `tools/run_codex_harnesses_smoke.py`, `tools/check_codex_harnesses_smoke_receipts.py`, `test/check_codex_harnesses_governance.test.py`, and `test/codex_harnesses_smoke_receipts.test.py` now require all seven source rows, the five candidate ids, the five adapter kinds, R4 receipt fields, `async/headless` lifecycle evidence, and `authority_decision`; blocked receipts remain not smoke-tested, and no install/start/live harness job occurs.
- 2026-06-07 conflict-priority refresh: this docs-only package records Codex harnesses as subordinate runtime-safety governance below Comet/OpenSpec/Superpowers/gstack and above Spec Kit only for runtime safety; Checker + Runtime implementation remains deferred.
- 2026-06-06 source refresh evidence: this docs-only package adds `https://github.com/revfactory/harness`, `https://github.com/ymymssss/ohmyopenagent`, and `https://github.com/MayDay-wpf/snow-cli` to the source ledger, records observed source pins/license posture, and changes the next Checker + Runtime requirement to candidate-registry-driven design; no Checker + Runtime implementation, install, sidecar start, live harness job, or Codex takeover occurs.
- 2026-06-06 R4 local tooling evidence: `tools/run_codex_harnesses_smoke.py`, `tools/check_codex_harnesses_smoke_receipts.py`, and `codex_harnesses_smoke_receipts.test.py` implement bounded read-only smoke receipt generation and validation; absent R3 install receipts produce blocked receipts that are accepted as evidence but are not smoke-tested; no Pi/oh-my-pi install, sidecar start, live harness job, active-candidate handoff, or Codex takeover occurs.
- 2026-06-05 real-runtime gap update: branch `runtime-plan-standard-20260605` reclassifies Pi/oh-my-pi sidecar, harness job runner, executable read/write guards, and R3/R4/R5 receipts as pending Stage D runtime work; no runtime is installed, started, smoked, or live-run.
- 2026-06-05 Stage C runtime promotion evidence: branch `runtime-promotion-plan-20260605` records R0-R5 promotion gates for Codex harnesses, keeps Pi/oh-my-pi sidecar runtime not installed/started/enabled, and checker-backs no-takeover active sidecar constraints.
- 2026-06-04 Stage B implementation evidence: `tools/check_codex_harnesses_governance.py` and `test/check_codex_harnesses_governance.test.py` verify the harness-only lane, source ledger, no-takeover boundary, read/write guards, job state, isolated worktree, changed-path report, and no unpinned Pi packages.
<!-- EVIDENCE_INDEX_END -->
