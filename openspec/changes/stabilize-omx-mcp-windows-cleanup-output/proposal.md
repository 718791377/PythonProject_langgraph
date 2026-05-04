## Why

`codex-ohmy` keeps the Codex user-level orchestration layer available, including `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace`, but the current Windows cleanup path can leak normal `taskkill` success lines into a temporary Codex session when the operator later uses `/resume`. This pollutes conversation context and makes the long-term personal durable-team workflow noisy even though the cleanup itself succeeded.

## What Changes

- Add a managed Windows cleanup-output control layer for `codex-ohmy` launches so normal `taskkill` success output is suppressed or logged while errors remain visible.
- Keep `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace` enabled for full `codex-ohmy` sessions.
- Preserve the operator workflow where `codex-ohmy` starts a temporary session and the operator uses `/resume` from inside that temporary session.
- Add script-backed validation so future launcher/helper changes do not reintroduce visible benign Windows cleanup noise.
- Do not switch to MCP Router and do not require direct `codex-ohmy resume <session-id>` entry as the only supported path.

## Capabilities

### New Capabilities

- `codex-user-level-windows-cleanup-output-control`: Defines managed Windows cleanup-output suppression for user-level Codex orchestration launches while preserving direct Codex MCP tools.

### Modified Capabilities

- `codex-user-level-team-mode-startup-binding`: The startup-binding launcher gains a scoped cleanup-output quiet layer for wrapped `codex-ohmy` launches.
- `codex-user-level-mcp-scope-policy`: The policy is clarified to keep Codex-private `omx_*` MCP servers direct and enabled while cleanup noise is handled separately.

## Impact

Impact scope:

- `docs_bilingual/implementation_plans/omx_mcp_windows_cleanup_output_control_plan.md`: ASCII primary plan for the cleanup-output control rollout.
- `docs_bilingual/implementation_plans/omx_mcp_windows_cleanup_output_control_plan.zh-CN.md`: UTF-8 Chinese companion plan for the same rollout.
- `tools/install-codex-user-level-team-mode.ps1`: User-level installer and generated `codex-ohmy` launcher source; it will install a scoped Windows cleanup shim and prepend it only for wrapped launches.
- `tools/check_windows_cleanup_output_control.py`: Repository checker that validates the managed cleanup-output control contract.
- `test/install-codex-user-level-team-mode.test.ps1`: Installer test coverage for generated shim files and launcher PATH scoping.
- `test/check_windows_cleanup_output_control.test.py`: Checker tests for required source and artifact evidence.

Explicit non-goals:

- Do not disable `omx_state`, `omx_memory`, `omx_code_intel`, or `omx_trace` as the long-term fix.
- Do not make `codex-ohmy resume <session-id>` the only supported recovery path.
- Do not route Codex-private `omx_*` MCP servers through MCP Router.
- Do not edit `C:\Users\lenovo\.codex\config.toml`; this is the user-level Codex configuration file and remains operator-controlled.
- Do not suppress actionable cleanup errors, non-zero exits, authentication failures, or stack traces.

Rollout sequence:

1. Add this OpenSpec change and bilingual implementation plan.
2. Add the managed cleanup shim generation and wrapped-launch PATH scoping.
3. Add checker and tests.
4. Validate locally with installer/checker tests and OpenSpec guard.
5. Publish through the GitLab-first MR flow and sync GitHub only after GitLab main is green.
6. After merge, run the user-level installer to update `C:\Users\lenovo\.codex\bin` on the operator machine.

Rollback plan:

- Re-run the existing installer rollback path or restore from the timestamped installer backup under `C:\Users\lenovo\.codex\backups`.
- Remove the scoped shim directory from the generated `codex-ohmy` launcher PATH only by reverting this repository change and reinstalling.
- No repository durable state or MCP Router state rollback is required.

Validation path:

- `powershell -NoProfile -ExecutionPolicy Bypass -File test/install-codex-user-level-team-mode.test.ps1`: validates generated launchers, installer outputs, and rollback behavior.
- `python test/check_windows_cleanup_output_control.test.py`: validates checker behavior.
- `python tools/check_windows_cleanup_output_control.py --root . --json`: checks the repository contract directly.
- `openspec validate --all`: validates OpenSpec artifacts.
- `python tools/run_openspec_guard.py --root . --tool codex --json`: runs repository OpenSpec guard checks.
- `git diff --check`: checks patch formatting.

Mainline classification:

- Existing user-level orchestration maintenance under the active team-mode and cross-session durable-state isolation plans; this is a production-hardening step for the future personal durable-team target, not a claim that the final production-grade team is complete.
