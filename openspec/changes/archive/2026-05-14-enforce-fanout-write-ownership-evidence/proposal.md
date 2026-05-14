# Change: Enforce fan-out and write-ownership evidence

## Why

The automatic orchestration routing plan requires native subagent fan-out to stay leader-owned and bounded. Existing checks cover role routing, delegation wait discipline, and effective durable lane fit, but they do not separately fail saved evidence that exceeds the managed fan-out limits, implies raw Codex auto-spawns specialist roles, or launches write-heavy parallel work without explicit ownership isolation, hotspot serialization, and leader-owned final integration.

## What Changes

- Add a repository/evidence checker for fan-out bounds, leader-side spawning language, and write-heavy parallel ownership evidence.
- Wire the checker into the shared OpenSpec guard and local/remote CI manifest.
- Register the checker as script backing for the orchestration activation policy.
- Extend the stable orchestration activation spec with explicit checker-backed fan-out and write-ownership requirements.
- Refresh bilingual startup and governance reminders so future sessions know the fan-out/write-ownership rule is script-backed.

## Capabilities

### New Capabilities

### Modified Capabilities

- `codex-user-level-orchestration-activation-policy`: fan-out must remain bounded and leader-owned, and write-heavy parallel execution must declare isolated ownership, hotspot serialization, and leader-owned integration.

## Impact

- Impact scope: repository governance checkers, tests, CI manifest, OpenSpec guard wiring, safety-rule registry, startup summaries, and orchestration activation policy documents.
- Explicit non-goals: no runtime durable-team launch, no user-level config mutation, no installed wrapper change, no remote publication.
- Rollout sequence: implement checker and tests, wire guard and CI, update policy/spec surfaces, validate, then archive as one local integration package.
- Rollback plan: revert the checker, test, guard/CI/registry wiring, and policy/spec deltas in one local commit if false positives are excessive.
- Validation path: `openspec validate enforce-fanout-write-ownership-evidence --strict`, checker repository/evidence mode tests, Python test manifest, OpenSpec guard, and local gate.
- Mainline classification: existing user-level orchestration enforcement mainline under `automatic_orchestration_routing_enforcement_plan`.
