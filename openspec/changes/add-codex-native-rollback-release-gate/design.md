## Context

The repository already has three layers of protection:

- plan-level rules that keep native Codex as the permanent base layer
- OpenSpec requirements that forbid replacing native Codex entrypoint names
- installer rollback behavior validated by the PowerShell install test

The missing piece is a release gate that combines those protections into a single pre-publication checklist and machine-checkable template.

## Goals / Non-Goals

**Goals:**

- require explicit release evidence before marking user-level team-mode launcher or installer changes production-ready
- keep the gate read-only by default
- require local smoke evidence for native Codex, raw bypass, and wrapped launcher entrypoints
- require repository evidence for backup snapshots and rollback-on-error behavior
- require a config rewrite sentinel check before production release
- integrate a static checker into the aggregate OpenSpec guard

**Non-Goals:**

- run live Codex or oh-my-codex inside CI by default
- write into the real user Codex home
- mutate `C:\Users\lenovo\.codex\config.toml` - the Codex user configuration file
- change MCP Router, omx, LangGraph, or native subagent runtime behavior

## Decisions

### Decision 1: Use a template plus static checker for CI-safe enforcement

The release gate is represented as `tools/codex_native_rollback_release_gate_template.json` - a JSON template that lists required fields, evidence, protected native entrypoints, and non-mutation guards.

The checker validates that template and source evidence without launching durable runtime or writing user-level assets.

Why:

- CI and MR pipelines should be deterministic and non-mutating.
- Local release smoke checks can still be required as documented evidence without making CI depend on an authenticated Codex session.

### Decision 2: Keep local launch smoke checks explicit but not CI-mandatory

The gate requires evidence for:

- `codex --version` - local smoke command proving native Codex still launches.
- `codex-raw --version` - local smoke command proving the stable raw bypass still launches.
- `codex-ohmy` help or version check - local smoke command proving the wrapped launcher does not crash immediately.

These checks are release evidence, but the static checker does not run them in CI.

Why:

- Local Codex authentication, plugins, and Windows shell state are operator-environment facts.
- CI should not need live Codex credentials to validate repository policy.

### Decision 3: Treat missing rollback evidence as a release blocker

The release gate requires evidence that the installer creates backup snapshots and restores pre-install state after simulated partial failures.

The repository evidence is the existing `test/install-codex-user-level-team-mode.test.ps1` test plus source checks for backup and rollback functions.

Why:

- Backup documentation alone is weaker than tested rollback behavior.
- The user's requirement is version rollback, not only failure explanation.

### Decision 4: Keep native Codex names protected at both spec and gate layers

The release gate repeats the protected native names:

- `codex` - native Codex base command name.
- `codex.cmd` - Windows npm shim name for native Codex.
- `codex.ps1` - PowerShell shim name that must not be replaced by this repository.

Why:

- The spec forbids replacing them.
- The release gate makes the same rule visible to operators before publication.

## Risks / Trade-offs

- [Risk] Static template checking may be mistaken for a full release drill.
  Mitigation: keep local smoke checks and manual rollback evidence as required release fields.

- [Risk] `codex-ohmy` behavior can vary by machine profile.
  Mitigation: require local smoke evidence and keep `codex-raw` as the stable bypass.

- [Risk] The gate can become stale as launchers evolve.
  Mitigation: keep required evidence ids stable and update commands through reviewed OpenSpec changes.

## Migration Plan

1. Add the release-gate template and checker.
2. Wire the checker into `tools/run_openspec_guard.py` - the aggregate OpenSpec guard.
3. Update plan files with the new release slice.
4. Validate the existing installer rollback test still passes.
5. Validate OpenSpec artifacts and guard output.

## Open Questions

- Whether a later slice should add a manual rollback helper that restores a named backup snapshot from `C:\Users\lenovo\.codex\backups\codex-user-level-team-mode\` - the user-level backup directory for managed team-mode assets.
