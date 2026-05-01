## Overview

This change is a documentation and handoff refresh. It updates the cold-start surfaces that a new Codex session reads before implementation so they no longer point at completed replay or task-ownership work as the next action.

## Design

The refresh uses the existing handoff layering:

- `AGENTS.md` - repository instruction surface that routes MCP scope questions to the stable governance policy.
- `docs_bilingual/project_startup_summary.md` - English repository-entry startup summary that stays stable and points to drift-prone details elsewhere.
- `docs_bilingual/project_startup_summary.zh-CN.md` - Chinese companion for the repository-entry startup summary.
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` - English current-mainline memory handoff where fast-changing execution detail belongs.
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md` - Chinese companion for the current-mainline memory handoff.

The memory handoff will identify the latest landed increments first:

- `formalize-mcp-router-scope-policy` - archived OpenSpec change that introduced the MCP Router versus Codex-direct MCP scope policy.
- `codex-user-level-mcp-scope-policy` - stable OpenSpec spec that records MCP Router scope requirements.
- `refresh-mainline-memory-after-task-ownership-precheck` - archived OpenSpec change that introduced the mainline memory handoff requirement.
- current publication refs - local `main`, `gitlab/main`, and `github/main` should be checked before continuing and should be described in the memory handoff.

## Safety Boundaries

- No user-level configuration writes are allowed. In particular, `C:\Users\lenovo\.codex\config.toml` is not edited by this change.
- No MCP Router database writes are allowed. The repository can document and check policy, but the operator controls MCP Router UI and database state.
- No durable backend is started. This change does not launch native OMX, LangGraph, or a durable team.
- No runtime helper is generated. This change only updates repository documentation and OpenSpec artifacts.

## Validation

Validation is local and read-only except for normal test artifacts generated under the repository checkout:

- `openspec validate --all` - validates OpenSpec change and stable spec syntax.
- `python tools/run_openspec_guard.py --root . --json` - runs the repository guard bundle.
- `python tools/check_name_clarity_rules.py --root . --json` - verifies name explanation coverage in `docs_bilingual/` and `openspec/`.
- `git diff --check` - verifies patch formatting.
