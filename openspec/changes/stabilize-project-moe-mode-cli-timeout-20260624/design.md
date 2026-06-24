# Design: Project MOE Mode CLI Timeout Budget

## Context

Project MOE GUI validation executes target Mode CLI commands from two local surfaces: `toolchain.run_cli()` for readiness/read-contract checks and `gui_shell.run_cli_json()` for GUI read/write/readback actions. Both paths should stay bounded, but the old 20 second value was fixed in code and became flaky under full-suite Windows load.

## Goals / Non-Goals

**Goals:**

- Provide a shared default timeout budget with enough headroom for loaded local gates.
- Keep the budget bounded and deterministic.
- Let tests and operators override the budget without editing source.
- Apply the same rule to read-contract and GUI write/readback paths.

**Non-Goals:**

- No automatic retries.
- No process killing.
- No target project state model changes.
- No change to timeout error tokens; `blocked:mode_cli_timeout` remains the failure classification when the configured budget is exceeded.

## Decisions

### Decision 1: Use a 60 second default budget

The previous 20 second budget was the observed bottleneck during full-suite execution. A 60 second default remains bounded while giving Windows process startup and Python import overhead enough headroom under load.

Alternative considered: increasing the local gate step timeout only. That would not fix the per-Mode-CLI subprocess timeout and would still allow false `blocked:mode_cli_timeout` results inside the test file.

### Decision 2: Use `PROJECT_MOE_GUI_MODE_CLI_TIMEOUT_SECONDS` for overrides

The env var is local to this GUI toolchain, can be scoped to a test or operator shell, and avoids persistent global configuration. Invalid, empty, zero, and negative values fall back to the default.

Alternative considered: adding a config-file field. That would broaden target-project config surface and is unnecessary for this stability slice.

### Decision 3: Duplicate the tiny helper in both entry modules

`toolchain.py` and `gui_shell.py` are used in different execution contexts. A tiny helper in each module avoids adding a new import dependency or changing packaging boundaries during a hotfix.

Alternative considered: create a new shared module. That is cleaner long term but broader than needed to unblock the local gate.

## Risks / Trade-offs

- Longer default timeout can make real hangs take longer to report. Mitigation: the budget remains finite and can be lowered through the env var in focused diagnostics.
- Env parsing mistakes could create unbounded waits. Mitigation: parse as float and reject non-positive values.
- GUI write/readback uses multiple subprocess calls. Mitigation: regression coverage records every write/readback subprocess timeout and verifies one shared budget.

## Migration Plan

1. Add regression tests for env override, default budget, and GUI write/readback consistency.
2. Replace hard-coded 20 second values with helper calls.
3. Run focused and full Project MOE toolchain tests.
4. Integrate through the local-main helper after local gate and local MR review.

## Open Questions

None for this stabilization slice.
