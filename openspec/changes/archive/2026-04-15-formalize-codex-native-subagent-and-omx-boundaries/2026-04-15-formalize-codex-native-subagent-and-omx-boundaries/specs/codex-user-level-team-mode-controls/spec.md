## ADDED Requirements

### Requirement: Generated controls SHALL expose a native-subagent limit surface
The user-level installer SHALL generate an additive control asset that exposes the managed native-subagent fan-out limits used by this workflow.

That generated asset SHALL allow the operator to inspect, and where supported manage, `agents.max_threads` and `agents.max_depth` without modifying the native `codex`, `codex.cmd`, or `codex.ps1` base entrypoints.

#### Scenario: Installer renders additive limit controls
- **WHEN** the installer renders user-level team-mode assets into a target Codex home
- **THEN** it SHALL generate a native-subagent limit control asset
- **AND** that asset SHALL keep the native Codex base entrypoints unchanged
