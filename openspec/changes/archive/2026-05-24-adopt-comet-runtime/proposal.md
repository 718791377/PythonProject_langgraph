## Why

The operator explicitly approved moving beyond governance into the runtime adoption steps that the Comet/OpenSpec/Superpowers policy previously gated: install `@rpamis/comet`, run `comet init`, and update user-level Codex configuration.

This change makes that mutation auditable by defining the write scope, backups, rollback plan, and validation path before changing global npm or `C:\Users\lenovo\.codex`.

## What Changes

- Install `@rpamis/comet` from npm as the Comet CLI provider for the local machine.
- Run Comet initialization for the Codex/OpenSpec/Superpowers workflow after backing up user-level Codex configuration and relevant skill/config surfaces.
- Update user-level `.codex` configuration only through a minimal, reversible patch needed for Comet/Codex workflow adoption.
- Record version, command output, changed paths, backup paths, and validation results in this OpenSpec change.
- Keep consumer repositories and their `.omx/state` directories out of scope.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `codex-user-level-comet-controlled-openspec-superpowers`: Adds runtime adoption requirements for explicit approval, backups, scoped user-level mutation, validation, and rollback evidence.

## Impact

- Affected user-level runtime: global npm package area for `@rpamis/comet`.
- Affected user-level Codex surface: `C:\Users\lenovo\.codex\config.toml` and any Comet-selected Codex skill directories.
- Affected repository artifacts: this OpenSpec change, runtime evidence notes, and any project-local Comet files if `comet init` selects project scope.
- Non-goals: no remote publication, no consumer-project state mutation, no unscoped overwrite of existing `.codex/skills`, and no force deletion of existing user-level configuration.
