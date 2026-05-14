# Design

The shared local/remote CI path is `tools/ci/local_gate.ps1`, which delegates repository-level policy verification to `tools/run_openspec_guard.py` and unit tests through `tools/ci/ci_test_manifest.json`.

This change keeps evidence validators with required `--trace` or `--evidence` inputs covered through unit tests, while adding the no-input capability-switch checker directly to the OpenSpec guard. That avoids requiring synthetic runtime traces in the guard while still making the checker and fixtures part of the normal gate.
