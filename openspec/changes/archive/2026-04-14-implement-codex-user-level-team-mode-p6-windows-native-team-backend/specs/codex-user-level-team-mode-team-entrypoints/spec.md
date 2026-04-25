## MODIFIED Requirements

### Requirement: The installer SHALL generate user-level OMX team entrypoint assets

The installer SHALL continue to generate additive user-level team entrypoint assets into the target Codex home.

The generated wrappers SHALL remain usable on native Windows and SHALL NOT assume that Unix `tmux` is the only supported execution backend.

#### Scenario: Use a generated team entrypoint on native Windows after P6

- **WHEN** the operator runs a generated wrapper such as `omx-team-dev.ps1` on native Windows
- **THEN** the wrapper SHALL remain valid
- **AND** it SHALL route into a supported native Windows execution backend when the runtime provides one
