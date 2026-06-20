---
doc_id: user_level_mcp_skills_cli_runtime_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/user_level_mcp_skills_cli_runtime_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
supersedes:
  - docs_bilingual/implementation_plans/user_level_mcp_skills_discovery_facade_plan.md
---

# User-Level MCP and Skills CLI Runtime Plan

> **For agentic workers:** use `superpowers:executing-plans`; use parallel subagents only for disjoint write sets. This plan owns the real-runtime path for `mcp2cli` and `skills2cli` only.

## Goal

Promote the existing compact `mcp2cli` / `skills2cli` discovery facade from repo-local helpers and checkers into a user-level runtime plan with explicit R0-R5 evidence gates.

## Architecture

`mcp2cli` follows the upstream `knowsuchagency/mcp2cli` runtime pattern. `skills2cli` is a deliberate fork/adaptation of that CLI/skill pattern for local Codex skill discovery, not a native subagent and not an MCP server. Repo-local source remains authoritative for `tools/skills2cli.py`, `tools/mcp2cli.py`, and the installer/checker helpers; any user-level copy is an install artifact.

## Tech Stack

Python helper scripts, `uvx mcp2cli --help`, `uv tool install mcp2cli`, `npx skills add knowsuchagency/mcp2cli --skill mcp2cli`, user-level Codex home wrappers under `C:/Users/lenovo/.codex`, JSON receipts, rollback backups, redaction helpers, OpenSpec guard wiring, and local CI.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented-local
Status: R6 live-executed
Status: Stage E live-repaired
Status: Stage D R3/R4 live-executed
Stage: Stage E Codex-compatible `skills2cli` frontmatter reporting and repair runtime is implemented locally and live-executed for installed user/plugin skills. Stage D R3/R4 user-level install/update and bounded smoke evidence is now also live-executed for `mcp2cli` and `skills2cli`; R5 direct MCP or sensitive skill handoff remains gated and not executed.
Owner session: `implement-stage-d-mcp-skills-cli-live-runtime-20260621` owns the Stage D R3/R4 live-runtime evidence package; `implement-skills2cli-codex-compat-runtime-20260620` owns the Stage E frontmatter repair package; `implement-multi-plan-family-r6-live-runtime-20260611` remains the older strict parent-family R6 receipt coverage owner.
Stage D evidence: upstream `knowsuchagency/mcp2cli` was source-pinned at `e3fa0f957155da6fe8dbb981441c41b2131feda0`; `uv tool install mcp2cli` and `uvx mcp2cli --help` executed successfully; user-level `mcp2cli` and repo-derived `skills2cli` wrappers/support files were refreshed with rollback pointer `state/mcp-skills-cli/backups/20260620T191937Z`; R3 receipts are `mcp2cli-20260620T191938Z.json` and `skills2cli-20260620T191938Z.json`; R4 smoke receipts are `mcp2cli-smoke-20260620T191950Z.json` and `skills2cli-smoke-20260620T191950Z.json`.
Stage E evidence: repo runtime adds strict Codex frontmatter parsing/compatibility reports, repair helper, tests, CI manifest registration, user-level `skills2cli` support-file install, live smoke receipts, and live frontmatter repair receipts. Post-repair audit reports `invalid_total=0`; rollback manifest and sanitized receipt are stored under user-level `state/skills2cli/frontmatter-repair/`.
R6 evidence: `.omx/r6-live-runtime/receipts/` contains accepted `live-executed` evidence for lane `user-level-mcp-skills-cli-runtime`, validated by `tools/check_r6_live_runtime_receipts.py --require-coverage` and `tools/check_multi_plan_family_r6_live_runtime.py --require-coverage`.
Runtime boundary: Stage D/E mutate only approved user-level `mcp2cli` / `skills2cli` install artifacts, wrappers, receipts, rollback backups, and Codex-compatible SKILL.md metadata. They do not mutate `config.toml`, apply profiles, disable plugins, perform browser/GUI/WXWork/harness/Spec Kit actions, execute R5 direct MCP/sensitive handoff, or publish remote refs.
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-21
<!-- CURRENT_STATUS_END -->

## Source References

| Runtime lane | Reference source | Runtime role | Required pin/evidence before R3 |
| --- | --- | --- | --- |
| mcp2cli | https://github.com/knowsuchagency/mcp2cli | Upstream MCP/OpenAPI/GraphQL discovery and call CLI pattern. | Source URL, immutable ref/version, install command, wrapper path hash, update command, rollback pointer, redaction status. |
| skills2cli | https://github.com/knowsuchagency/mcp2cli plus repo-local `tools/skills2cli.py` | Fork/adaptation of the upstream low-token CLI/skill pattern for Codex skill discovery. | Repo source hash, upstream pattern ref, generated SKILL.md hash, wrapper path hash, update command, rollback pointer, redaction status. |

## Runtime Promotion Ladder

| Runtime stage | Scope | Evidence gate |
| --- | --- | --- |
| R0 project-level preflight | Inspect upstream `mcp2cli` reference, repo-local `skills2cli` source, current `CODEX_HOME`, and available `uv`/`uvx`/`npx` without installing or copying artifacts. | Source URL, source pin plan, tool availability, no install/run evidence, sanitized transcript. |
| R1 project-level fake/dry-run runtime | Run deterministic installer `plan` and simulated apply/check fixtures. | `apply_performed=false`, fake command results, no user-level state mutation, focused tests. |
| R2 reusable project-level helper/guard | Maintain repo-owned installer/checker, receipt schema, rollback backup layout, redaction contract, and CI/OpenSpec guard registration. | Helper/checker tests, CI manifest registration, OpenSpec guard wiring, docs registry entry. |
| R3 user-level install/update receipt | With explicit authorization, install/update upstream `mcp2cli`, copy repo-derived `skills2cli` wrappers/skill, and write sanitized receipts. | Completed live on 2026-06-20 for `mcp2cli` and `skills2cli`; receipts include source pin, wrapper hashes, updater commands, rollback pointer, and redaction status. |
| R4 user-level smoke runtime | Run bounded `--help` / `--version` / safe discovery smoke against installed wrappers. | Completed live on 2026-06-20; smoke receipts cover `mcp2cli --version` and `skills2cli --help` with bounded transcripts, timeout release, redaction, and rollback readiness. |
| R5 active-candidate / bounded live handoff | Run a direct MCP or skill-discovery handoff only under risk profile and sensitive-call receipt controls. | Not executed by this package; requires a separate authorization receipt, target/action allowlist, risk profile, rollback pointer, and redacted result summary. |

## Stage E Final Audit and Codex-Compatible Skills Runtime Freeze

Status: implemented-local-live-repaired
Frozen at: 2026-06-20
Implemented at: 2026-06-20
Authorization boundary: local plan update, local implementation, user-level live runtime repair, local commits, and local `main` integration are approved; remote publication remains closed.

### Problem Record

`reference_files/10.md` is the final audit input for this Stage E package. It records 286 Codex skill loading warnings:

- 285 user-level skills under `C:/Users/lenovo/.codex/skills` have frontmatter `name` values longer than the Codex-compatible 64 character limit.
- 1 plugin-cache Twilio skill has a `description` longer than the 1024 character Codex-compatible limit.

The repair target is Codex compatibility of installed skill metadata. It must not delete skills, disable plugin families, or treat low usage as proof that a capability is useless.

### Frozen Design

`skills2cli` continues to follow the upstream `mcp2cli` progressive-disclosure shape: discover compact metadata first, search by task, inspect one skill when needed, and only include sanitized full bodies when explicitly requested. It is not a native subagent, not expert evidence, and not an MCP server.

Stage E adds a repo-owned compatibility repair surface:

1. Strictly validate Codex frontmatter compatibility: frontmatter exists, `name` and `description` exist, `name <= 64`, `description <= 1024`.
2. Generate stable short names for overlong user-level skill names. The short name keeps a readable prefix and appends a deterministic hash when needed to avoid collisions.
3. Shorten overlong descriptions without editing the skill body.
4. Default to dry-run and require an explicit apply flag plus operator confirmation for live user-level mutation.
5. Before apply, back up every touched `SKILL.md`; after apply, write a rollback manifest and sanitized receipt.
6. Treat plugin-cache edits as minimal repair only. They may be overwritten by a future plugin update and must be identified separately in receipts.
7. Never mutate `C:/Users/lenovo/.codex/config.toml`, never apply a profile, and never hard-load/disable a plugin in this package.

### Execution Slices

- [x] Slice A - plan freeze: update this plan pair with the final audit problem record, repair boundaries, and verification gates; commit and integrate locally before live runtime work.
- [x] Slice B - repository runtime: enhance `tools/skills2cli.py`, add/extend compatibility fixer and checker tests, and keep all default outputs compact and redacted.
- [x] Slice C - live runtime: install/update repo-derived `skills2cli` user-level artifacts if required, run user-level smoke, run the Codex compatibility fixer against installed skills, and record sanitized receipts plus rollback pointers.

### Verification Gates

Focused gates for Stage E:

```powershell
python test/skills2cli.test.py
python test/check_codex_skills_governance.test.py
python test/user_level_mcp_skills_cli_install.test.py
python tools/check_codex_skills_governance.py --root . --json
python tools/check_user_level_mcp_skills_cli_install.py --root . --json
python tools/check_precommit_update_archive.py --root . --json
python tools/run_openspec_guard.py --root .
```

Live runtime gates for Stage E:

```powershell
python tools/skills2cli.py index --json
python tools/skills2cli.py audit warnings --since 30d --json
python tools/install_user_level_mcp_skills_cli.py check --json --require-installed
python tools/install_user_level_mcp_skills_cli.py smoke --record --operator-confirmation --json
python tools/repair_codex_skill_frontmatter.py audit --json
python tools/repair_codex_skill_frontmatter.py apply --operator-confirmation --json
```

The live repair is accepted only when the post-apply audit reports zero `name_too_long` and zero `description_too_long` items for the repaired scope, or when remaining items are explicitly listed as blocked with rollback pointers preserved.


## Real Runtime Implementation Gap

The previous discovery facade implementation was not enough to claim real runtime readiness. As of 2026-06-20, the R3/R4 portion is live-executed and the remaining gap is R5-only:

- [x] Source-pin review: upstream `knowsuchagency/mcp2cli` observed at `e3fa0f957155da6fe8dbb981441c41b2131feda0`.
- [x] R3 install/update: `tools/install_user_level_mcp_skills_cli.py apply --apply --operator-confirmation --run-external --skip-upstream-skill-install --upstream-ref e3fa0f957155da6fe8dbb981441c41b2131feda0 --json` refreshed the approved user-level artifacts and wrote rollback-backed receipts for both tools.
- [x] R4 smoke: `tools/install_user_level_mcp_skills_cli.py smoke --record --operator-confirmation --upstream-ref e3fa0f957155da6fe8dbb981441c41b2131feda0 --json` wrote `smoke-tested` receipts for `mcp2cli --version` and `skills2cli --help`.
- [x] Compatibility re-check: `tools/repair_codex_skill_frontmatter.py audit --codex-home C:/Users/lenovo/.codex --include-plugins --limit 5 --json` reported `invalid_total=0`.
- [ ] R5 direct MCP calls and sensitive skill-derived actions remain blocked behind risk profile, sensitive-call receipt, no-native-subagent-evidence wording, redaction, and rollback rules.

The upstream `npx skills add knowsuchagency/mcp2cli --skill mcp2cli` path was intentionally not executed in this package because the approved runtime surface is the repository-owned wrapper/support-file install plus receipts; executing third-party skill installation remains a separate explicit decision.

## File Ownership

This plan owns the runtime plan docs for `mcp2cli` and `skills2cli`, future installer/checker runtime receipt updates, and user-level MCP/skills CLI install tests. It does not own Browser/CLI adapters, CLI-Anything/WXWork_CLI, Codex harnesses, native agents, or MCP Router policy.

## Parallel Session Contract

One session may claim this implementation plan at a time. Other sessions may work on Browser/CLI adapters, CLI-Anything/WXWork_CLI, Codex harnesses, selector ownership, or durable smoke only if they do not edit this plan, the `mcp2cli` / `skills2cli` installer/checker/test files, docs registry, CI manifest, or OpenSpec guard wiring without a serialized hotspot lease.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Create runtime successor plan for the deleted/superseded discovery-facade source plan.
- [x] Record `knowsuchagency/mcp2cli` as upstream runtime source and `skills2cli` as an upstream-pattern fork/adaptation.
- [x] Preserve existing repo-local helper/checker/test carry-forward surfaces as R0-R2 evidence only.
- [x] Implement repo-local R4 smoke command support that records `smoke-tested` receipts for `mcp2cli` and `skills2cli` against an explicitly supplied Codex home fixture.
- [x] Extend the repo-local checker with `--require-smoke-tested` so R4 smoke receipt evidence can be required and validated through the generic receipt governance guard.
- [x] Stage E plan freeze: record `reference_files/10.md` final audit findings and freeze the `skills2cli` progressive-disclosure plus Codex-compatible skill metadata repair design.
- [x] Stage E repository runtime: implement strict `skills2cli` compatibility reporting, repair helper, tests, and checkers.
- [x] Stage E live runtime: repair installed user-level skill metadata with rollback manifest and smoke the installed `skills2cli` surface.
- [x] Stage D source pin review: pin upstream `knowsuchagency/mcp2cli` at `e3fa0f957155da6fe8dbb981441c41b2131feda0`.
- [x] Stage D R3 live runtime: refresh approved user-level `mcp2cli` / `skills2cli` artifacts and write rollback-backed install/update receipts.
- [x] Stage D R4 live runtime: run bounded wrapper smoke and write `smoke-tested` receipts for both tools.
- [ ] Stage D/R5 live handoff: keep direct MCP calls and sensitive skill-derived actions blocked until a separate authorization receipt exists.
<!-- TASK_BACKLOG_END -->

## Stage D live-runtime status

Stage D R3/R4 is now completed-live for the approved user-level wrapper/support-file surface. R5 remains pending by design and is not part of this package:

- [x] Stage D R3 source pin: upstream `mcp2cli` ref `e3fa0f957155da6fe8dbb981441c41b2131feda0`.
- [x] Stage D R3 install/update receipts: `mcp2cli-20260620T191938Z.json` and `skills2cli-20260620T191938Z.json` under user-level `state/mcp-skills-cli/receipts/`.
- [x] Stage D R3 rollback pointer: `state/mcp-skills-cli/backups/20260620T191937Z`.
- [x] Stage D R4 smoke receipts: `mcp2cli-smoke-20260620T191950Z.json` and `skills2cli-smoke-20260620T191950Z.json`.
- [x] Stage D R4 bounded smoke commands: `mcp2cli --version` returned `mcp2cli 3.2.0`; `skills2cli --help` returned the compact discovery CLI help.
- [x] Stage D boundary: no `config.toml` mutation, no profile apply, no plugin disable, no browser/GUI/WXWork/harness/Spec Kit action, no remote ref mutation.
- [ ] Stage D/R5 direct MCP call or skill action handoff remains gated behind a separate risk profile, sensitive-call authorization receipt, action scope, result redaction, and rollback evidence.

## Validation Gates

- `python tools/check_user_level_mcp_skills_cli_install.py --root . --json` - validates MCP/skills CLI install surfaces and helper plan output.
- `python tools/check_user_level_mcp_skills_cli_install.py --root . --require-user-level-installed --require-smoke-tested --json` - validates the real user-level wrapper, skill, support-file, install receipt, and R4 smoke receipt state when claiming Stage E live-repaired evidence.
- `python tools/check_implementation_plan_rules.py --root . --json` - validates implementation-plan registry, bilingual pairing, anchors, and parent links.
- `python tools/run_openspec_guard.py --root .` - validates OpenSpec workflow, governance policies, name clarity, and registered checkers.
- `python tools/check_precommit_update_archive.py --root . --json` - reviews required existing-file updates, checker/test registration, and archive readiness before commit.
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate before local integration.
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_mr_review.ps1` - runs the local MR review gate before local main integration.

## Acceptance Criteria

- The deleted/superseded `user_level_mcp_skills_discovery_facade_plan` is not restored as an active implementation plan.
- `mcp2cli` and `skills2cli` runtime ownership is represented by this active child plan.
- Existing helper/checker/test carry-forward evidence is clearly R0-R2 only unless paired with user-level receipts.
- Stage E evidence is scoped to Codex-compatible `skills2cli` frontmatter reporting, user-level `skills2cli` support-file install/smoke, and installed-skill metadata repair.
- Stage D R3/R4 is complete only because the user-level install/update and smoke receipts named above exist with rollback pointers and redacted transcripts.
- R5 runtime claims still require separate active-candidate authorization, sanitized receipts, and rollback evidence.
- Remote publication remains behind explicit approval.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-20 Stage D R3/R4 live runtime: branch `implement-stage-d-mcp-skills-cli-live-runtime-20260621` pins upstream `knowsuchagency/mcp2cli` at `e3fa0f957155da6fe8dbb981441c41b2131feda0`, runs real `uv tool install mcp2cli` and `uvx mcp2cli --help`, refreshes approved user-level wrappers/support files with rollback pointer `state/mcp-skills-cli/backups/20260620T191937Z`, writes R3 receipts `mcp2cli-20260620T191938Z.json` and `skills2cli-20260620T191938Z.json`, writes R4 receipts `mcp2cli-smoke-20260620T191950Z.json` and `skills2cli-smoke-20260620T191950Z.json`, and verifies installed skill frontmatter with `invalid_total=0`. This evidence does not execute R5 direct MCP/sensitive handoff and does not authorize remote publication.
- 2026-06-20 Stage E Codex-compatible skills runtime: branch `implement-skills2cli-codex-compat-runtime-20260620` adds `tools/codex_skill_frontmatter.py`, `tools/repair_codex_skill_frontmatter.py`, strict `skills2cli`/inventory compatibility reporting, governance checker fail-closed boundaries, installer support-file sync, and focused tests. Live runtime installed/checked repo-derived `skills2cli` user-level artifacts, ran smoke receipts, and applied frontmatter repair to installed skills; post-apply audit reports `invalid_total=0`, with rollback manifest and receipt under user-level `state/skills2cli/frontmatter-repair/`. This evidence does not mark Stage D upstream `mcp2cli` pin/install complete and does not authorize remote publication.
- 2026-06-07 R5 active-candidate gate: branch `implement-r5-runtime-governance-batch-20260607` adds shared active-candidate receipt validation for MCP/skills CLI runtime handoff. Evidence requires authorization receipt, owner lease, target/action allowlist, timeout release, redacted transcript, rollback pointer/readiness, cleanup evidence, authority decision with the exact priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`, and `remote_publication_mutated=false`. Focused validation: `python test\check_r5_active_candidate_receipts.test.py` plus lane-specific focused tests described in the OpenSpec verification report. No real user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action and no remote mutation occurs in this package.
- 2026-06-05 runtime successor plan: branch `runtime-plan-standard-20260605` creates this plan to carry `mcp2cli` / `skills2cli` real-runtime work after `user_level_mcp_skills_discovery_facade_plan` was deleted/superseded; no user-level install, smoke, direct MCP call, or live handoff is performed by that package.
- 2026-06-06 R4 repo-local smoke receipt support: branch `implement-mcp-skills-cli-runtime-r4-20260606` adds `install_user_level_mcp_skills_cli.py smoke --record --operator-confirmation`, `check_user_level_mcp_skills_cli_install.py --require-smoke-tested`, and focused tests that validate generated R4 `smoke-tested` receipts through `user_level_receipt_governance.py smoke-check` against temporary Codex-home fixtures.
<!-- EVIDENCE_INDEX_END -->
