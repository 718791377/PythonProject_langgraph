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
Status: active; this plan is the runtime successor to the deleted/superseded `user_level_mcp_skills_discovery_facade_plan`. Repo-local helpers/checkers/tests now include R4 smoke receipt support, but real default user-level runtime promotion is still not performed by local validation.
Runtime boundary: this package does not mutate the real default user-level `CODEX_HOME` during tests or local gates. R4 evidence in this package is fixture-backed: `tools/install_user_level_mcp_skills_cli.py smoke --record --operator-confirmation --codex-home <temp-home>` runs bounded read-only wrapper smoke against an explicitly supplied Codex home that already has R3-style update receipts and wrappers, then writes separate `smoke-tested` receipts for `mcp2cli` and `skills2cli`.
R4 helper evidence: `tools/check_user_level_mcp_skills_cli_install.py --require-smoke-tested --codex-home <home>` now requires valid R4 smoke receipts, and each receipt is compatible with `tools/user_level_receipt_governance.py smoke-check`.
Runtime gap: real live user-level R3/R4 work still requires explicit live authorization, source pin review, actual user-level install/update receipts, live bounded smoke receipts, rollback evidence, and redaction evidence. R5 direct MCP calls or skill action handoffs remain gated by risk profile, sensitive-call receipt, action scope, result redaction, and rollback evidence.
Carry-forward evidence: existing surfaces are `tools/mcp2cli.py`, `tools/skills2cli.py`, `tools/install_user_level_mcp_skills_cli.py`, `tools/check_user_level_mcp_skills_cli_install.py`, `tools/user_level_receipt_governance.py`, `test/mcp2cli.test.py`, `test/skills2cli.test.py`, and `test/user_level_mcp_skills_cli_install.test.py`.
Companion refresh note: the zh-CN companion remains the Chinese companion while preserving runtime tokens; no remote publication is authorized by this plan.
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
- [ ] Stage D live runtime: pin upstream `mcp2cli` version/ref and install/update it at real user level with R3 receipt, wrapper hash, updater command, rollback pointer, and redaction evidence after explicit live authorization.
- [ ] Stage D live runtime: install/update repo-derived `skills2cli` wrapper and SKILL.md at real user level with R3 receipt, source hash, updater command, rollback pointer, and redaction evidence after explicit live authorization.
- [ ] Stage D live runtime: run bounded R4 help/version/safe-discovery smoke for both real user-level wrappers using the implemented `smoke` command and record live `smoke-tested` receipts.
- [ ] Stage D live runtime: gate any R5 direct MCP call or skill action handoff behind risk profile, sensitive-call authorization receipt, action scope, result redaction, and rollback evidence.
<!-- TASK_BACKLOG_END -->

## Validation Gates

- `python tools/check_user_level_mcp_skills_cli_install.py --root . --json` - validates MCP/skills CLI install surfaces and helper plan output.
- `python tools/check_implementation_plan_rules.py --root . --json` - validates implementation-plan registry, bilingual pairing, anchors, and parent links.
- `python tools/run_openspec_guard.py --root .` - validates OpenSpec workflow, governance policies, name clarity, and registered checkers.
- `python tools/check_precommit_update_archive.py --root . --json` - reviews required existing-file updates, checker/test registration, and archive readiness before commit.
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate before local integration.
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_mr_review.ps1` - runs the local MR review gate before local main integration.

## Acceptance Criteria

- The deleted/superseded `user_level_mcp_skills_discovery_facade_plan` is not restored as an active implementation plan.
- `mcp2cli` and `skills2cli` runtime ownership is represented by this active child plan.
- Existing helper/checker/test carry-forward evidence is clearly R0-R2 only, not proof of R3/R4/R5 real runtime completion.
- Later R3/R4/R5 runtime claims require sanitized receipts and rollback evidence.
- Remote publication remains behind explicit approval.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-05 runtime successor plan: branch `runtime-plan-standard-20260605` creates this plan to carry `mcp2cli` / `skills2cli` real-runtime work after `user_level_mcp_skills_discovery_facade_plan` was deleted/superseded; no user-level install, smoke, direct MCP call, or live handoff is performed by that package.
- 2026-06-06 R4 repo-local smoke receipt support: branch `implement-mcp-skills-cli-runtime-r4-20260606` adds `install_user_level_mcp_skills_cli.py smoke --record --operator-confirmation`, `check_user_level_mcp_skills_cli_install.py --require-smoke-tested`, and focused tests that validate generated R4 `smoke-tested` receipts through `user_level_receipt_governance.py smoke-check` against temporary Codex-home fixtures.
<!-- EVIDENCE_INDEX_END -->
