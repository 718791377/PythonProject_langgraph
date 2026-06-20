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
Stage: Stage E Codex-compatible `skills2cli` frontmatter reporting and repair runtime is implemented locally and live-executed for installed user/plugin skills.
Owner session: `implement-skills2cli-codex-compat-runtime-20260620` owns the Stage E implementation package; `implement-multi-plan-family-r6-live-runtime-20260611` remains the older strict parent-family R6 receipt coverage owner.
Stage E evidence: repo runtime adds strict Codex frontmatter parsing/compatibility reports, repair helper, tests, CI manifest registration, user-level `skills2cli` support-file install, live smoke receipts, and live frontmatter repair receipts. Post-repair audit reports `invalid_total=0`; rollback manifest and sanitized receipt are stored under user-level `state/skills2cli/frontmatter-repair/`.
R6 evidence: `.omx/r6-live-runtime/receipts/` contains accepted `live-executed` evidence for lane `user-level-mcp-skills-cli-runtime`, validated by `tools/check_r6_live_runtime_receipts.py --require-coverage` and `tools/check_multi_plan_family_r6_live_runtime.py --require-coverage`.
Runtime boundary: Stage E mutates only the approved user-level `skills2cli` install artifacts and SKILL.md frontmatter metadata with backups/rollback receipts; it does not mutate `config.toml`, apply profiles, disable plugins, perform browser/GUI/WXWork/harness/Spec Kit actions, or publish remote refs.
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-20
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
| R3 user-level install/update receipt | With explicit authorization, install/update upstream `mcp2cli`, copy repo-derived `skills2cli` wrappers/skill, and write sanitized receipts. | `installed-user-level` receipt per tool, source/package/ref pin, wrapper path hash, updater command, rollback pointer, redaction status. |
| R4 user-level smoke runtime | Run bounded `--help` / `--version` / safe discovery smoke against installed wrappers. | `smoke-tested` receipt, bounded command transcript, timeout release, redaction, rollback readiness. |
| R5 active-candidate / bounded live handoff | Run a direct MCP or skill-discovery handoff only under risk profile and sensitive-call receipt controls. | `active-candidate` receipt, risk profile, sensitive-call authorization when needed, action scope, rollback pointer, redacted result summary. |

## Real Runtime Implementation Gap

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


The previous discovery facade implementation is not enough to claim real runtime readiness. Required later work:

- Execute `tools/install_user_level_mcp_skills_cli.py apply --apply --operator-confirmation ...` only after explicit authorization and source pin review.
- Capture separate install/update receipts for `mcp2cli` and `skills2cli`, including wrapper hashes, source hashes, updater commands, rollback backup paths, and redaction status.
- Smoke installed wrappers with bounded `mcp2cli --help` or `--version` and `skills2cli --help` / safe discovery commands.
- Keep direct MCP calls and sensitive skill-derived actions behind risk profile, sensitive-call receipt, no-native-subagent-evidence wording, redaction, and rollback rules.

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
<!-- TASK_BACKLOG_END -->

## Stage D pending runtime work

These items remain pending by design and are not blockers for the completed Stage E frontmatter-repair package. They require a separate explicit live-runtime decision before execution:

- Stage D real runtime: pin the upstream `mcp2cli` version/ref and install/update it at real user level with R3 receipt, wrapper hash, updater command, rollback pointer, and redaction evidence.
- Stage D real runtime: install/update the repo-derived `skills2cli` wrapper and SKILL.md with R3 receipt, source hash, updater command, rollback pointer, and redaction evidence.
- Stage D real runtime: run bounded R4 help/version/safe-discovery smoke for both wrappers and record `smoke-tested` receipts.
- Stage D real runtime: gate any R5 direct MCP call or skill action handoff behind risk profile, sensitive-call authorization receipt, action scope, result redaction, and rollback evidence.

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
- Existing helper/checker/test carry-forward evidence is clearly R0-R2 only, not proof of broad R3/R4/R5 real runtime completion.
- Stage E evidence is scoped to Codex-compatible `skills2cli` frontmatter reporting, user-level `skills2cli` support-file install/smoke, and installed-skill metadata repair; it does not complete the broader Stage D upstream `mcp2cli` runtime lane.
- Later Stage D or R5 runtime claims require sanitized receipts and rollback evidence.
- Remote publication remains behind explicit approval.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-20 Stage E Codex-compatible skills runtime: branch `implement-skills2cli-codex-compat-runtime-20260620` adds `tools/codex_skill_frontmatter.py`, `tools/repair_codex_skill_frontmatter.py`, strict `skills2cli`/inventory compatibility reporting, governance checker fail-closed boundaries, installer support-file sync, and focused tests. Live runtime installed/checked repo-derived `skills2cli` user-level artifacts, ran smoke receipts, and applied frontmatter repair to installed skills; post-apply audit reports `invalid_total=0`, with rollback manifest and receipt under user-level `state/skills2cli/frontmatter-repair/`. This evidence does not mark Stage D upstream `mcp2cli` pin/install complete and does not authorize remote publication.
- 2026-06-07 R5 active-candidate gate: branch `implement-r5-runtime-governance-batch-20260607` adds shared active-candidate receipt validation for MCP/skills CLI runtime handoff. Evidence requires authorization receipt, owner lease, target/action allowlist, timeout release, redacted transcript, rollback pointer/readiness, cleanup evidence, authority decision with the exact priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`, and `remote_publication_mutated=false`. Focused validation: `python test\check_r5_active_candidate_receipts.test.py` plus lane-specific focused tests described in the OpenSpec verification report. No real user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action and no remote mutation occurs in this package.
- 2026-06-05 runtime successor plan: branch `runtime-plan-standard-20260605` creates this plan to carry `mcp2cli` / `skills2cli` real-runtime work after `user_level_mcp_skills_discovery_facade_plan` was deleted/superseded; no user-level install, smoke, direct MCP call, or live handoff is performed by that package.
- 2026-06-06 R4 repo-local smoke receipt support: branch `implement-mcp-skills-cli-runtime-r4-20260606` adds `install_user_level_mcp_skills_cli.py smoke --record --operator-confirmation`, `check_user_level_mcp_skills_cli_install.py --require-smoke-tested`, and focused tests that validate generated R4 `smoke-tested` receipts through `user_level_receipt_governance.py smoke-check` against temporary Codex-home fixtures.
<!-- EVIDENCE_INDEX_END -->
