## Overview

This change is a documentation and handoff refresh. It does not alter runtime orchestration, durable-state selection, OpenSpec guard logic, or publication workflow behavior.

The key design choice is to keep stable repository-entry facts in `docs_bilingual/project_startup_summary.md` while moving drift-prone current-progress details into the current mainline memory summary.

## Current State

The repository has no active OpenSpec changes and the latest mainline work has landed through `automate-task-ownership-precheck-checker`. The current mainline memory summary still opens with older operator-surface replay work, which remains valid but is no longer the latest landed increment.

## Target State

The current mainline memory summary should state, early and explicitly, that:

- `tools/check_session_ownership_claims.py` - checker that now supports task ownership precheck signals before writes.
- `automate-task-ownership-precheck-checker` - latest archived OpenSpec change that landed the checker-backed task ownership precheck increment.
- `openspec status` - command used to confirm there are no active OpenSpec changes before selecting a new increment.
- `doc-refresh-mainline-memory-task-ownership` - current feature branch for this memory refresh work.

The summary should list safe next choices instead of presenting the earlier replay increment as the only active target.

## Boundaries

In scope:
- Update current mainline memory summaries.
- Add OpenSpec artifacts and a stable requirement for current-mainline handoff freshness.

Out of scope:
- Runtime code changes.
- Durable team launch or backend selection.
- Consumer project modification.
- GitLab/GitHub publication automation.

## Validation

This change relies on existing repository validation:

- `openspec validate --all` - OpenSpec structural validation.
- `python tools/run_openspec_guard.py --root . --json` - aggregate repository guard.
- `git diff --check` - whitespace validation.
