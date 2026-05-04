## Why

The user-level durable-team roadmap is moving from documentation-only planning toward R0.6 smoke gates for automatic routing. Future smoke gates need a reviewed, machine-readable template before any dry-run or live exercise can claim that routing, consent, validation, and rollback boundaries were declared.

## What Changes

- Add a repository-local durable routing smoke gate template for future R0.6.x changes.
- Add a checker that validates the template structure and required field descriptions.
- Wire the checker into the OpenSpec guard so a cold-start session can verify the template without relying on prompt memory.
- Keep this release read-only: no durable team launch, no `.omx/state/` writes, and no `omx-team-auto.ps1 -Apply` execution.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-team-mode-automatic-team-routing`: adds a script-backed template contract for durable routing smoke gates before later dry-run or adoption exercises.

## Impact

- impact_scope: `tools/durable_routing_smoke_gate_template.json`, `tools/check_durable_routing_smoke_gate_template.py`, `tools/run_openspec_guard.py`, and this OpenSpec change.
- explicit_non_goals: no durable runtime activation, no native_omx team launch, no LangGraph thread launch, no MCP Router changes, no user-level `config.toml` edits, and no `.omx/state/` mutation.
- rollout_sequence: create the template, add the checker, wire the checker into the guard, validate locally, then publish through GitLab-first review.
- rollback_plan: revert this change to remove the template, checker, and guard step; no runtime state cleanup is needed because this change is read-only.
- validation_path: run the new checker, `openspec validate --all`, `python .\tools\run_openspec_guard.py --root . --tool codex --json`, and `git diff --check`.
- mainline_classification: existing user-level team-mode and durable-state mainline, specifically R0.6.0 Durable Routing Smoke Gate Template.
