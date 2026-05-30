## Why

The wrapped user-level Codex launcher already generates rich startup instructions for automatic orchestration. Passing that body inline as a `developer_instructions` command-line override risks Windows command-line length failures and can also carry encoding-sensitive text through the wrong transport boundary.

## What Changes

- Add a repository checker that proves generated launcher startup instructions are written to a UTF-8 state file and passed through one short `model_instructions_file` override.
- Register the checker in the aggregate OpenSpec guard and the script-backed safety-rule registry.
- Add regression coverage for the current repository and for failure cases that remove the file reference, inline developer instructions, remove UTF-8 writes, or bypass the startup-argument builder.
- Promote the startup-binding spec requirement for file-backed launcher instruction transport.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-team-mode-startup-binding`: startup launcher payload transport now requires a file-backed model-instructions reference instead of inline generated instruction bodies.

## Impact

- Impact scope: launcher payload checker, aggregate guard registration, safety-rule registry, targeted tests, and startup-binding OpenSpec specification.
- Explicit non-goals: no user-level config mutation, no installed wrapper hand-editing, no remote publication, and no persistent team launch.
- Rollout sequence: add checker and tests, validate the existing installer behavior, archive this OpenSpec change in the same local package, run local gates, commit, then merge to local `main` only.
- Rollback plan: revert this local feature commit to remove the checker, tests, guard registration, safety-rule entry, and spec promotion.
- Validation path: run focused compile/tests/checker commands, OpenSpec validation, repository guard, precommit update/archive review, local gate, and local MR review.