---
doc_id: user_level_mcp_skills_discovery_facade_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/user_level_mcp_skills_discovery_facade_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
source_plan: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
---

# User-Level MCP and Skills Discovery Facade Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:executing-plans`; use `superpowers:subagent-driven-development` only when the implementation slice has a disjoint write set. This child plan is extracted from the older MCP/skills/browser/CLI source plan and must be executed through normal claim, hotspot, and local-main retire gates.

## Goal

Provide compact `skills2cli` and `mcp2cli` discovery contracts that reduce startup context and keep sensitive calls risk-gated. The repo-local MVP remains the deterministic fail-closed facade; the next implementation stage must also install upstream `knowsuchagency/mcp2cli` as the user-level `mcp2cli` runtime and fork/adapt an upstream-style `skills2cli` user-level CLI/skill surface.

## Source Extraction

Extracted from Slices 1 and 2 of `user_level_mcp_skills_browser_cli_governance_plan.md`.

This file is a decomposed child implementation plan under `multi_plan_parallel_session_orchestration_plan.md`. The source plan remains a historical and baseline-checker index; it is not the single execution package for this lane.

## Phase Placement

- Parent phase: Phase 4 automatic routing and stable session surfaces.
- Execution model: as-needed multi-phase work, with parallel sessions only when write sets are disjoint or hotspots are explicitly serialized.
- Remote publication: not authorized by this plan.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: Stage A plan refreshed for an upstream-backed user-level runtime; Stage B implementation remains pending and remote publication remains unauthorized.
Current gate: merge this docs-only governance package into local `main`, then start a separate Stage B implementation worktree. The current operator request authorizes Stage B implementation after Stage A local-main integration; it does not authorize remote publication.
Source relation: extracted from `user_level_mcp_skills_browser_cli_governance_plan.md`; the source plan remains a baseline/history index, not a direct child execution package.
Runtime boundary: existing repo-local `tools/skills2cli.py` and `tools/mcp2cli.py` stay as deterministic compact/fail-closed discovery facades. Stage B must add user-level runtime artifacts without replacing those repo-local tests or safety contracts.
Upstream reference: use `https://github.com/knowsuchagency/mcp2cli` as the authority for installing user-level `mcp2cli`: `uvx mcp2cli --help` for direct smoke, `uv tool install mcp2cli` for user-level install, and `npx skills add knowsuchagency/mcp2cli --skill mcp2cli` for the upstream agent-skill surface. Its README documents `--mcp`, `--mcp-stdio`, `--spec`, `--graphql`, `bake`, `--compact`, `--toon`, OAuth, env/file secret indirection, cache directories, and generated wrapper behavior.
Implementation target: install/wrap upstream `mcp2cli` under the user-level Codex tool boundary, then fork/adapt the upstream `mcp2cli` skill/CLI pattern into `skills2cli` so `skills2cli` remains a compact skill-discovery command backed by the installed skills ecosystem and this repository's redaction/profile-suggestion rules.
<!-- CURRENT_STATUS_END -->

## File Ownership

Future implementation may touch skills facade helpers, MCP facade helpers, risk-profile fixtures, tests, policy docs, user-level installer/wrapper generation scripts, and installation receipt helpers. It must not load full skill bodies by default, must not expose secrets in process arguments, and must keep live MCP/API calls behind receipt evidence.

A future implementation claim must list exact file ownership before edits. Workers are not alone in the codebase, must not revert other workers' changes, and must report changed paths.

## Parallel Session Contract

Can run in parallel with receipt and port plans because default discovery is read-only. Any real MCP call behavior depends on the Phase 1 receipt/redaction contract.

Shared hotspots remain serialized through the parent plan, implementation-plan claim lock, ROB entry, and local-main retire lock.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Define compact `skills2cli` index, search, show, audit, and profile-suggest JSON outputs.
- [x] Keep full skill bodies out of default output and summarize warning audits with redaction.
- [x] Define compact `mcp2cli` list, search, show, and risk profile output.
- [x] Make `mcp2cli call` fail closed for sensitive calls without authorization receipt evidence.
- [x] Keep direct Codex MCP entries direct and do not use MCP Router as the default Codex bridge.
- [x] Record routing evidence so skills and profiles are not mislabeled as native subagents.
- [x] Run focused validation for this child lane.
- [x] Update the parent evidence index and Phase 7 integration plans after implementation evidence exists.
- [ ] Stage A: record the upstream-backed user-level runtime plan and integrate it into local `main` as a docs-only governance package.
- [ ] Stage B: install or wrap upstream `knowsuchagency/mcp2cli` as user-level `mcp2cli` using `uv tool install mcp2cli` when available, with `uvx mcp2cli --help` as the non-mutating preflight and a rollback pointer for the previous wrapper/tool state.
- [ ] Stage B: install the upstream `mcp2cli` skill with `npx skills add knowsuchagency/mcp2cli --skill mcp2cli` only through a receipt-backed user-level update path; do not treat skill installation as native-subagent evidence.
- [ ] Stage B: fork/adapt the upstream `mcp2cli` skill/CLI pattern into a user-level `skills2cli` wrapper/skill that delegates to the installed skills CLI or the repo-local compact facade, preserving compact JSON, redaction, profile-suggest preview-only behavior, and no full skill bodies by default.
- [ ] Stage B: add or update tests/checkers for wrapper path existence, command smoke tests, rollback/update receipts, upstream version/help evidence, and fail-closed sensitive `mcp2cli` calls without authorization receipts.
- [ ] Stage B: document the boundary between upstream runtime `mcp2cli`, repo-local fail-closed facade `tools/mcp2cli.py`, user-level `skills2cli`, and native Codex subagents.
<!-- TASK_BACKLOG_END -->

## Validation Gates

- MCP baseline checker: `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json` verifies source-plan baseline markers and guard registration.
- Agent/skill/profile boundary checker: `python tools/check_agent_skill_profile_surface_boundaries.py --root . --json` verifies skills are not mislabeled as native agents.
- MCP scope checker: `python tools/check_mcp_router_scope_policy.py --root . --json` verifies Codex direct MCP boundaries and Router isolation.
- Whitespace check: `git diff --check` verifies the patch has no whitespace errors.
- Stage B upstream install preflight: `uvx mcp2cli --help` must succeed before mutating user-level install state; executing `uv tool install mcp2cli` must record version/source evidence.
- Stage B skill install preflight: `npx skills add knowsuchagency/mcp2cli --skill mcp2cli --list` or equivalent dry listing must identify the upstream skill before any user-level skill installation.
- Stage B wrapper smoke: `mcp2cli --version` or `mcp2cli --help`, `skills2cli --help`, compact discovery JSON, and sensitive-call fail-closed checks must pass after installation.

## Acceptance Criteria

- The lane keeps discovery, receipts, leases, or adapters separate according to its phase boundary.
- No sensitive runtime action is enabled without the required receipt, owner, rollback, and redaction evidence.
- Any checker, test, or OpenSpec change is registered in the shared guard before local main integration.
- Local main integration remains serial and remote publication remains behind explicit approval.
- User-level `mcp2cli` is sourced from upstream `knowsuchagency/mcp2cli`; the repo-local facade remains available as a deterministic safe fallback and test harness.
- User-level `skills2cli` is a deliberate fork/adaptation of the upstream `mcp2cli` skill/CLI pattern, not a misleading alias for native subagents or a full skill-body injection mechanism.
- Installation, update, rollback, and smoke-test receipts identify wrapper path, install path, source URL/version, state/cache paths, and previous-state rollback pointer.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-01: child plan created by the MCP/skills/browser/CLI decomposition package; implementation evidence is pending future claims.
- 2026-06-01: branch `implement-mcp-skills-discovery-facade-20260601` implements the compact discovery facade lane. Evidence includes `tools/skills2cli.py`, `tools/mcp2cli.py`, `tools/mcp2cli_allowed_profiles.json`, focused tests `test/skills2cli.test.py` and `test/mcp2cli.test.py`, RED/GREEN coverage for MCP risk-profile output and skill/profile routing evidence, and no live MCP/browser/user-level runtime mutation.
- 2026-06-03: Stage A plan refresh requires a separate Stage B implementation to install upstream `knowsuchagency/mcp2cli` as user-level `mcp2cli` and fork/adapt an upstream-style `skills2cli`; Stage A remains docs-only and does not install tools or mutate user-level runtime state.
<!-- EVIDENCE_INDEX_END -->
