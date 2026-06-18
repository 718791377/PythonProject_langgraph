# Tasks: Fix OMX Windows Native Team Runtime

## Stage A: Freeze plan

- [x] Create the OpenSpec change and bilingual proposal/design/task/management artifacts.
- [x] Create the canonical bilingual implementation plan under `docs_bilingual/implementation_plans/`.
- [x] Freeze the four-layer model and Windows runtime backend vocabulary.
- [x] Freeze readiness versus operational launchability acceptance criteria.
- [x] Correct the active team-mode plan so P6 is reopened as a runtime target rather than claimed complete.
- [ ] Validate, commit, and integrate this Stage A package into local `main`.

## Stage B: Implement live runtime

- [ ] Add failing tests for native OMX false-ready readiness projection on Windows without tmux or live runtime evidence.
- [ ] Add failing tests for Windows backend selection and `omx-team-auto.ps1 -Apply` preflight fail-closed behavior.
- [ ] Add runtime fields: `runtime_backend`, `preflight_passed`, `operational_ready`, and `blockers`.
- [ ] Implement the native Windows prompt/process controller backend or fail closed with named blockers until the controller can launch.
- [ ] Wire automatic helper launch/reuse/switch/shutdown through operational preflight.
- [ ] Add lifecycle evidence for launch, status, await, resume, shutdown, and cross-project cwd operation.
- [ ] Validate, commit, and integrate Stage B into local `main`, then stop at the remote-publication gate.
