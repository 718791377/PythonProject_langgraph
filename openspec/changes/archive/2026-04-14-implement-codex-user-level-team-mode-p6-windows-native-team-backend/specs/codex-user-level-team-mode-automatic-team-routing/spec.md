## MODIFIED Requirements

### Requirement: Apply mode SHALL support launch, reuse, switch, and shutdown

When `-Apply` is provided, the helper SHALL execute the planned durable-team mutation through the native runtime available on the current platform.

On native Windows, this SHALL mean a supported native Windows backend rather than a hard Unix `tmux` dependency.

#### Scenario: `omx-team-auto.ps1 -Apply` launches a team on native Windows after P6

- **WHEN** the operator runs `omx-team-auto.ps1 -Phase execute-parallel -ParallelSlices 2 -Apply` on native Windows
- **THEN** the helper SHALL be able to execute the launch through the Windows backend
- **AND** it SHALL still preserve the tracked-team record contract
