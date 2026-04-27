## Overview

The canary prompt is a startup-summary-owned context-loss detector. This change keeps the literal canary prompt in the bilingual startup summary pair only, while allowing other active instruction surfaces to reference the startup summary as the authoritative source.

The implementation adds a checker so the rule is not prompt-only: active repository files fail validation if they duplicate the literal canary prompt outside the allowed startup summaries, or if either startup summary stops carrying the expected prompt.

## Scope

In scope:
- startup-summary wording that declares the exclusive prompt location
- active plan wording that points to the startup-summary canary without repeating its literal prompt
- `AGENTS.md` wording that points to the startup-summary source without repeating the literal prompt
- repository checker and tests
- OpenSpec guard integration

Out of scope:
- changing the canary phrase
- scanning archived OpenSpec history as mutable policy
- injecting canary text into user-level wrapper payloads
- editing user-level skills, plugins, or `config.toml`

## Checker design

`tools/check_context_retention_canary_surface.py` scans active text files under the selected repository root.

It fails when:
- the English startup summary does not contain both halves of the startup-summary-defined canary prompt
- the Chinese startup summary does not contain both halves of the startup-summary-defined canary prompt
- another active text file contains either literal half of the canary prompt

It ignores:
- VCS and build/runtime directories such as `.git`, `.worktrees`, `.omx`, `.venv`, `node_modules`, and caches
- archived OpenSpec change history under `openspec/changes/archive/`
- binary or unsupported file types

The checker constructs the canary strings from code points so the checker source itself does not duplicate the literal prompt text as normal prose.

## Guard integration

`tools/run_openspec_guard.py` includes the checker in both JSON and text modes. Tests cover JSON aggregation so adding the step is visible in the guard contract.

## Documentation updates

`project_startup_summary.md` and `project_startup_summary.zh-CN.md` remain the only active files containing the literal canary prompt.

`AGENTS.md` keeps only a pointer to the startup-summary canary source and recovery read order.

The active team-mode plan keeps the safety-boundary rule and future checker guidance, but replaces literal canary examples with startup-summary-source references.
