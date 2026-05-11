## Tasks

- [x] 1. Create the OpenSpec change and scope the modified capabilities.
- [x] 2. Add bilingual orchestration activation governance policy docs.
- [x] 3. Update startup and repository instruction surfaces with activation enforcement reminders.
- [x] 4. Add checker-backed enforcement and regression tests for activation policy surfaces.
- [x] 5. Register the safety rule in the script-backing registry and OpenSpec guard.
- [x] 6. Run local validation and record results.
- [x] 7. Archive/promote stable specs when implementation validation is complete.


## Validation Evidence

- `python tools/check_orchestration_activation_policy.py --root . --json` passed.
- `python tools/run_openspec_guard.py --root . --tool codex --json` passed with 18/18 steps.
- `git diff --check` passed.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1` passed.
