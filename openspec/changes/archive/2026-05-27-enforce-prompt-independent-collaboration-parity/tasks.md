## Tasks

- [x] 1. Add `tools/check_orchestration_collaboration_evidenceguard.py`.
- [x] 2. Add prompt-independent collaboration parity fixtures and structured evidence fixtures.
- [x] 3. Add unit coverage and register it in `tools/ci/ci_test_manifest.json`.
- [x] 4. Wire the checker into `tools/run_openspec_guard.py` and `tools/safety_rule_script_backing_registry.json`.
- [x] 5. Update AGENTS.md, governance docs, implementation plan, and stable OpenSpec spec.
- [x] 6. Run local validation and include this archive record with the implementation package.

## Validation Evidence

- `python tools/check_orchestration_collaboration_evidenceguard.py --root . --json` passed.
- `python test/check_orchestration_collaboration_evidenceguard.test.py` passed.
- `git diff --check` passed.
