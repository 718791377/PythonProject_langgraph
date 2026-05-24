## Context

`@rpamis/comet` version `0.2.7` is published on npm with the description `OpenSpec + Superpowers dual-star development workflow` and a `comet` binary entry.

The Comet README says `comet init` can install OpenSpec skills, Superpowers skills, Comet skills, guard/automation scripts, and `docs/superpowers/` working directories. It also says initialization may ask for AI platform, install scope, and skill language.

Because this repository already has official OpenSpec skills, oh-my-codex policy, user-level Codex MCP config, and repository guard surfaces, runtime adoption must be staged and reversible.

## Write Scope

Allowed writes for this change:

- global npm install or update of `@rpamis/comet`;
- backup files under `C:\Users\lenovo\.codex\backups\comet-adoption-<timestamp>\`;
- minimal `C:\Users\lenovo\.codex\config.toml` patch needed for this machine's Comet/Codex adoption;
- Comet-generated Codex/OpenSpec/Superpowers skills only when `comet init` explicitly reports the target and skip/overwrite behavior;
- repository-local evidence updates inside `openspec/changes/adopt-comet-runtime/`.

Disallowed writes:

- no writes to consumer repositories outside `D:\PythonProject_langgraph`;
- no remote Git operations;
- no force overwrite of user-level skills unless `comet init` or an explicit command reports an overwrite choice and the backup has already been captured;
- no deletion of existing `.codex` content.

## Backup Plan

Before mutation:

1. Create a timestamped backup directory under `C:\Users\lenovo\.codex\backups\`.
2. Copy `C:\Users\lenovo\.codex\config.toml` to that backup directory.
3. Capture listings of user-level `.codex/skills`, `.codex/prompts`, `.codex/agents`, `.codex/hooks.json`, and npm global Comet state when available.
4. Record npm package version and Comet CLI version after install.

## Rollback Plan

Rollback steps:

1. Restore `config.toml` from the timestamped backup.
2. Remove or move aside Comet-generated files identified in the evidence record.
3. If the global package must be reverted, run `npm uninstall -g @rpamis/comet` or reinstall the previous recorded version when one existed.
4. Re-run `comet doctor --json` when available, Codex configuration sanity checks, and repository OpenSpec checks.

## Execution Plan

1. Query npm metadata and record version.
2. Install `@rpamis/comet` globally.
3. Run `comet --version`, `comet --help`, and `comet init --help` to discover exact local command behavior.
4. Create backups and runtime evidence files.
5. Run `comet init` with the least destructive non-interactive options available; prefer skip-existing behavior unless a later interactive prompt proves an overwrite is required.
6. Apply the minimal user-level Codex config update.
7. Run `comet status --json`, `comet doctor --json --scope auto`, and repository checks.

## Open Questions

- Whether `comet init --yes --skip-existing --json` selects project scope or global scope on this machine.
- Whether Comet requires any Codex config changes beyond project trust entries and installed skills.
- Whether user-level skill updates should be committed to any repository artifact or treated only as runtime state with evidence.
