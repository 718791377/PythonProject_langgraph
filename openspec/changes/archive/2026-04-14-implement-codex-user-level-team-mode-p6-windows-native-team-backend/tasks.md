## 1. OpenSpec Artifacts

- [x] 1.1 Create the `implement-codex-user-level-team-mode-p6-windows-native-team-backend` proposal, design, and capability specs.
- [x] 1.2 Record the split between the already-completed P5 routing layer and the new P6 runtime-backend layer.

## 2. Runtime Backend

- [x] 2.1 Add backend abstraction under `omx team`.
- [x] 2.2 Implement the first native Windows backend.
- [x] 2.3 Keep repo-local `.omx/state/team/...` semantics stable across backends.

## 3. Validation

- [x] 3.1 Validate native Windows launch, status, and shutdown without WSL2.
- [x] 3.2 Validate `omx-team-auto.ps1 -Apply` launch/status plus failed-shutdown record preservation on the Windows backend.
- [x] 3.3 Run `openspec validate --all` and `python .\tools\run_openspec_guard.py --root .`.
