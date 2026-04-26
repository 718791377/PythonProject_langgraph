## Why

The current user-level durable orchestration surfaces still let repo-local durable artifacts influence future sessions too broadly.

In practice, a preserved LangGraph `backend.json` can still dominate automatic durable routing for unrelated later sessions, and empty unmanaged native `auto-team-*` directories can still trigger `manual-inspection-required` even when they contain no recovery data. That behavior couples sessions more tightly than intended and conflicts with the user-level orchestration policy that existing live sessions remain retrofit-capable rather than being trapped by stale repo-local selectors.

## What Changes

- Add a session-scoped durable activation model that separates activation truth from legacy repo-local durable artifacts.
- Preserve existing `.omx/state/langgraph/*` and `.omx/state/team/*` artifacts as historical and inspectable artifact state rather than silently treating them as the default activation source for later sessions.
- Narrow native unmanaged-residue blocking so that empty unmanaged native team directories remain safe cleanup candidates but no longer block automatic launch, reuse, or switch decisions.
- Add LangGraph routing eligibility projection so that historical or terminal tracked backend records remain inspectable without automatically dominating future unrelated sessions.
- Update inspectable durable-state reporting to distinguish preserved legacy artifacts, active scoped selectors, safe empty residue, and protected manual residue.

## Capabilities

### New Capabilities
- `codex-user-level-session-scoped-durable-activation`: add a versioned scoped selector and lease plane so future durable activation is session-aware instead of being inferred only from legacy repo-local artifacts

### Modified Capabilities
- `codex-user-level-team-mode-automatic-team-routing`: route from scoped activation state and ignore empty unmanaged native residue as a launch blocker
- `codex-user-level-inspectable-team-state-surface`: expose scoped activation, preserved legacy durable artifacts, and source-attributed legacy-versus-active classification
- `codex-user-level-durable-state-cleanup-and-reconciliation`: keep cleanup narrow while preserving legacy artifacts and distinguishing safe empty residue from protected or active state under the new activation model

## Impact

- impact_scope:
  - `tools/install-codex-user-level-team-mode.ps1` - installer/helper source that projects scoped activation behavior into user-level team-mode scripts.
  - `tools/langgraph_durable_orchestrator/cli.py` - repo-local LangGraph durable-state CLI source for routing eligibility and inspection output.
  - generated helper mirrors under `C:\Users\lenovo\.codex\bin`
  - `test/install-codex-user-level-team-mode.test.ps1` - regression test coverage for generated team-mode helper behavior.
  - relevant bilingual implementation and governance docs after behavior lands
- explicit_non_goals:
  - do not delete, rename, or rewrite existing legacy durable artifacts under repository `.omx/state/`
  - do not auto-adopt historical LangGraph threads or unmanaged native team residue into a new active session
  - do not collapse `native_omx` and `langgraph` into one backend family
  - do not change the global capability-switch semantics for `subagent_routing`, `oh_my_codex`, or `langgraph`
- rollout_sequence:
  - add source-level scoped activation and legacy-classification logic first
  - validate against legacy fixture states preserved from `D:\PythonProject_OpenClaw` and from `D:\PythonProject_langgraph`
  - refresh generated user-level helper mirrors only after source and tests pass
  - keep cleanup of empty unmanaged native residue as a later optional maintenance step
- rollback_plan:
  - revert source and generated-helper changes
  - preserve all legacy durable artifacts untouched
  - fall back to the current legacy activation behavior if the scoped activation plane proves unsafe
- validation_path:
  - targeted tests for empty unmanaged native residue and legacy LangGraph selector behavior
  - `openspec validate --all` - official OpenSpec validation command for all specs and active changes.
  - `python .\\tools\\run_openspec_guard.py --root .` - repository guard that aggregates OpenSpec and governance checks.
- mainline_classification:
  - new mainline candidate for additive user-level durable-state isolation and session-scoped activation

Legacy fixture references to `D:\PythonProject_OpenClaw` in this proposal are migration-context inputs only. They do not redefine the old repository as an active implementation authority for the current orchestration line.
