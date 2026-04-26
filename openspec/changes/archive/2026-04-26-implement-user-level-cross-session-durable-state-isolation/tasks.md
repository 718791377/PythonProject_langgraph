## 1. Scoped Activation Source Changes

- [x] 1.1 Add session-scoped durable activation projection and classification support in `tools/langgraph_durable_orchestrator/cli.py`
- [x] 1.2 Update `tools/install-codex-user-level-team-mode.ps1` to use scoped activation or routing eligibility instead of raw legacy tracked-record presence for future-session lane selection

## 2. Native Residue Routing Fixes

- [x] 2.1 Update automatic durable routing logic so empty unmanaged native `auto-team-*` directories do not force `manual-inspection-required`
- [x] 2.2 Update inspectable durable-state logic so empty unmanaged native residue is surfaced as safe cleanup context rather than active blocking state

## 3. Spec And Helper Surface Integration

- [x] 3.1 Regenerate or sync mirrored helper behavior for the affected user-level scripts after source logic is updated
- [x] 3.2 Update user-facing docs or implementation-plan text only where behavior changed materially

## 4. Validation

- [x] 4.1 Add or update regression tests for preserved legacy LangGraph selectors and empty unmanaged native residue
- [x] 4.2 Run `openspec validate --all`
- [x] 4.3 Run `python .\\tools\\run_openspec_guard.py --root .`
