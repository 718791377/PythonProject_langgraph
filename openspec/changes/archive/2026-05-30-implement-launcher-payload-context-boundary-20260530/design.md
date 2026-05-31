## Design

### Root cause

The launcher payload boundary is architectural rather than textual. Shortening prose can temporarily reduce command-line size, but the stable fix is to keep generated instruction bodies out of argv and pass only a reconstructible file reference.

### Decision 1: verify the source-of-truth generator, not installed wrappers

The checker reads `tools/install-codex-user-level-team-mode.ps1` because installed wrappers under the user-level Codex bin directory are generated artifacts. This keeps the repository source as the fix authority and avoids normalizing hand edits to installed files.

### Decision 2: require UTF-8 file-backed startup instructions

The generated startup arguments must be assembled by `Get-CodexUserLevelTeamModeStartupArgs`, which writes the generated model instructions through `Write-CodexUserLevelModelInstructionsFile` to `user-level-team-mode-model-instructions.md` and passes exactly one `model_instructions_file` override.

### Decision 3: fail closed on inline startup instruction bodies

The checker inspects the startup-argument and launcher function bodies and fails if they contain `developer_instructions=` as a command-line override or if `$DeveloperInstructions` is referenced while building `$startupArgs` instead of being passed only to the file writer.

### Data flow

1. The launcher computes generated startup instructions from persisted user-level team-mode state.
2. The startup-argument builder writes the large instruction body to a UTF-8 state file.
3. The command line receives short control arguments and one `model_instructions_file` reference.
4. The generated launcher forwards `@startupArgs @Arguments` to the native Codex executable path.

### Risks and mitigations

- Risk: A future edit reintroduces inline `developer_instructions` because it is easier to assemble. Mitigation: aggregate guard now runs the launcher payload checker.
- Risk: A future edit writes the state file with a non-UTF-8 encoding. Mitigation: checker and regression test require the UTF-8 `Set-Content` call.
- Risk: The test manifest is owned by another active session. Mitigation: place regression cases in an already registered test file and avoid editing the claimed CI manifest in this package.