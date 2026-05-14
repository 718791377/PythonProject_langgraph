# Change: Enforce effective lane-fit evidence

## Why

The automatic orchestration routing plan requires durable lane selection to be task-fit based rather than default-backend based. Existing checks cover capability switches, hard directives, durable artifacts, and leader scope, but they do not fail saved evidence that selects `native_omx` or LangGraph without the required worker-centric or graph-shaped rationale, or that mixes backend families without an explicit close or handoff.

## What Changes

- Add a repository/evidence checker for effective durable lane fit and backend-family switching evidence.
- Wire the checker into the shared OpenSpec guard and local/remote CI manifest.
- Register the checker as script backing for the orchestration activation policy.
- Extend the stable orchestration activation spec with explicit checker-backed lane-fit requirements.
- Refresh bilingual startup and governance reminders so future sessions know the lane-fit rule is script-backed.

## Capabilities

### New Capabilities

### Modified Capabilities

- `codex-user-level-orchestration-activation-policy`: durable lane choice must be backed by task-fit evidence, and backend-family switching must be explicit.

## Impact

- Impact scope: repository governance checkers, tests, CI manifest, OpenSpec guard wiring, safety-rule registry, startup summaries, and orchestration activation policy documents.
- Explicit non-goals: no runtime durable-team launch, no user-level config mutation, no change to installed LangGraph or native OMX helpers, no remote publication.
- Rollout sequence: implement checker and tests, wire guard and CI, update policy/spec surfaces, validate, then archive as one local integration package.
- Rollback plan: revert the checker, test, guard/CI/registry wiring, and policy/spec deltas in one local commit if false positives are excessive.
- Validation path: `openspec validate enforce-effective-lane-fit-evidence --strict`, checker repository/evidence mode tests, Python test manifest, OpenSpec guard, and local gate.
- Mainline classification: existing user-level orchestration enforcement mainline under `automatic_orchestration_routing_enforcement_plan`.
