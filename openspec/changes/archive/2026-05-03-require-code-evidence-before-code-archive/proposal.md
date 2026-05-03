## Why

Code-class OpenSpec changes must not be archived as documentation-only closeout. The MR6 readiness review exposed a process gap: a change can be archived after only OpenSpec and documentation edits even when later readers treat the queue item as code/runtime work.

## What Changes

- Add `tools/check_openspec_code_archive_evidence.py` - a repository checker that inspects current git diff evidence for newly archived OpenSpec changes.
- Allow `x_code_evidence_paths` - explicit archive metadata that points to already-landed source, executable check, CI, or test evidence when closeout happens in a separate archive-only MR.
- Wire the checker into `tools/run_openspec_guard.py` - the aggregate OpenSpec guard used locally and in GitLab CI.
- Add regression tests under `test/check_openspec_code_archive_evidence.test.py` - tests that a code-class archive without source/test evidence fails and that docs-only archives pass.
- Update OpenSpec workflow policy and safety-rule registry so the rule is enforced by script control, not only by prompt reminder.

## Non-Goals

- Do not retroactively rewrite the already merged MR6 archive history.
- Do not mutate `.omx/state/` - repo-local durable runtime state, not policy source.
- Do not edit `C:\Users\lenovo\.codex\config.toml` - user-level Codex config, outside this repository change.
- Do not change MCP Router settings.
