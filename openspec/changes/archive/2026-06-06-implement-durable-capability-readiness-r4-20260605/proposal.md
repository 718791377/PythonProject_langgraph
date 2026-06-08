# Change: Implement Durable Capability Readiness R4 Runtime Refresh

## Why
The readiness projection already distinguishes `installed`, `enabled`, `selected`, and `ready`, but `codex-durable-state-status.ps1` does not yet persist an explicit smoke-tested repo-local projection receipt.

## What Changes
- Add explicit `-RefreshReadiness` to `codex-durable-state-status.ps1`.
- Keep default status read-only and mutation-free.
- Write `.omx/state/readiness/durable-capability-readiness-projection.json` only on explicit refresh.
- Record source, selector, install/version evidence, blockers, and non-adoption booleans.

## Non-Goals
- Do not install or upgrade LangGraph.
- Do not launch native_omx, LangGraph, or a persistent team.
- Do not push or mutate remote refs.

## Verification
- `python .\test\check_capability_switch_chain.test.py` - exercises the capability readiness receipt checker unit coverage.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\test\install-codex-user-level-team-mode.test.ps1` - verifies the generated status helper, default read-only behavior, and explicit refresh receipt write path.
- `python tools/check_capability_switch_chain.py --root . --json` - validates the current user-level capability switch chain and optional readiness projection evidence.
- `python tools/run_openspec_guard.py --root .` - runs the repository OpenSpec and governance guard suite.
- local gate and local MR review before local main integration.
