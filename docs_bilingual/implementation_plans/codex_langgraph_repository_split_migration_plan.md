---
doc_id: codex_langgraph_repository_split_migration_plan
lang: en
status: active
doc_class: implementation_plan
---

# Codex / LangGraph Repository Split Migration Plan

## Goal

Move the Codex user-level orchestration line out of `D:\PythonProject_OpenClaw` into a new primary repository root at `D:\PythonProject_langgraph` without losing execution context, OpenSpec authority, or the current mainline.

## Source Of Truth Rule

After migration begins:

- `D:\PythonProject_langgraph` becomes the only source of truth for Codex `subagent / omx / langgraph` user-level orchestration work.
- `D:\PythonProject_OpenClaw` must stop accepting new implementation work for that line.
- `D:\PythonProject_OpenClaw` may keep temporary bridge or redirect notes only until cleanup is complete.

## Migration Boundary

Move to the new repository:

- user-level Codex or oh-my-codex orchestration code
- LangGraph durable orchestrator code
- user-level installer and wrapper generation code
- direct tests for the user-level Codex orchestration line
- user-level bilingual plan documents
- user-level OpenSpec specs and change history for that line

Keep in `D:\PythonProject_OpenClaw`:

- OpenClaw runtime and service code
- OpenClaw repository startup and runtime governance that remains OpenClaw-specific
- OpenClaw-facing LangGraph transformation planning for the OpenClaw project itself
- WeCom, local-control, retention, search-chain, and OpenClaw application concerns that are not part of the user-level Codex orchestration product

## Planned Move Set

Primary code:

- `tools/install-codex-user-level-team-mode.ps1` - installer script for user-level team-mode launchers and support artifacts.
- `tools/langgraph_durable_orchestrator/` - repo-local source tree for LangGraph durable orchestrator compatibility code.
- `tools/openclaw-omx-windows-bootstrap-fix.mjs` - Windows bootstrap fix script for legacy OpenClaw/OMX setup compatibility.

Primary tests:

- `test/install-codex-user-level-team-mode.test.ps1` - PowerShell tests for the user-level team-mode installer.
- `test/run-install-codex-user-level-team-mode-test.cmd` - Windows command wrapper that runs the installer test suite.
- `test/langgraph_durable_orchestrator_*.test.py` - Python tests for LangGraph durable orchestrator modules.
- `test/openclaw-omx-windows-bootstrap-fix.test.mjs` - Node.js test for the Windows bootstrap fix script.

Primary bilingual plans:

- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - English active plan for user-level Codex team-mode behavior.
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md` - Chinese companion for the user-level team-mode plan.

Primary OpenSpec specs:

- `openspec/specs/codex-user-level-*` - stable OpenSpec specs for user-level Codex orchestration capabilities.
- `openspec/specs/langgraph-durable-orchestration-backend/` - stable OpenSpec spec for the LangGraph durable orchestration backend.

Primary OpenSpec changes:

- active:
- `openspec/changes/implement-langgraph-reusable-subgraph-library/` - active change for the reusable LangGraph subgraph library.
- archived user-level orchestration history:
- `openspec/changes/archive/*codex-user-level*` - archived changes related to user-level Codex capabilities.
- `openspec/changes/archive/*langgraph*` - archived changes related to LangGraph capabilities.
- `openspec/changes/archive/*omx*` - archived changes related to OMX durable workflow capabilities.
- `openspec/changes/archive/*team-mode*` - archived changes related to team-mode behavior.

## Anti-Drift Controls

1. Migration manifest first.
   - Freeze the move set and destination mapping before copying files.
2. Startup summary first in the new repository.
   - The new repository must get its own startup entry and explicit current mainline.
3. OpenSpec history moves with the code.
   - Do not migrate only implementation files.
4. Single active mainline location.
   - New implementation for the orchestration line happens only in `D:\PythonProject_langgraph`.
5. Old repository becomes bridge-only before cleanup.
   - Add redirect notes in OpenClaw before deleting moved content there.
6. Cleanup happens only after verification.
   - The old repository is cleaned only after the new repository passes validation.

## Execution Order

1. Create `D:\PythonProject_langgraph`.
2. Initialize git and OpenSpec there.
3. Create repository startup entry, `AGENTS.md`, and migration marker files there.
4. Copy the move set from `D:\PythonProject_OpenClaw`.
5. Rebuild the new repository as the primary orchestration workspace.
6. Run validation in the new repository.
7. Add redirect notes in `D:\PythonProject_OpenClaw`.
8. Remove moved orchestration content from `D:\PythonProject_OpenClaw`.

## Validation

The new repository must pass at least:

- `openspec validate --all` - official OpenSpec CLI validation command for all specs and changes.
- `python .\tools\run_openspec_guard.py --root .` - repository guard command that aggregates OpenSpec and governance checks.
- Python LangGraph durable orchestrator tests
- PowerShell installer integration tests

## Current Mainline To Continue After Migration

The current mainline that must continue in the new repository is:

- `implement-langgraph-reusable-subgraph-library` - active OpenSpec change id for the reusable LangGraph subgraph library.

This mainline must be treated as the first post-migration implementation target.
