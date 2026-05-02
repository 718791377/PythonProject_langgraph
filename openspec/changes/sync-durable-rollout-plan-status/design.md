## Design

This is a status-synchronization change, not a runtime change. The repository already contains the helper mirror source-of-truth implementation evidence:

- `openspec/changes/archive/2026-04-28-formalize-helper-mirror-source-truth/` records the archived MR 5 change.
- `openspec/specs/codex-user-level-helper-mirror-source-truth/spec.md` records the stable helper mirror contract.
- `tools/install-codex-user-level-team-mode.ps1` emits `helper_mirror_source_of_truth` from generated status surfaces.
- `test/install-codex-user-level-team-mode.test.ps1` verifies helper mirror provenance in routing policy and durable-state status output.

The patch updates only status-bearing documents and the status-sync spec. It intentionally does not touch generated user-level files or repo-local durable state.
