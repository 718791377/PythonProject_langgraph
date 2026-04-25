## MODIFIED Requirements

### Requirement: Apply 模式 SHALL 支持 launch、reuse、switch、shutdown

显式带 `-Apply` 时，helper SHALL 通过当前平台上可用的 native runtime 执行计划中的 durable-team 变更。

在 native Windows 下，这 SHALL 意味着走受支持的 Windows backend，而不是继续硬依赖 Unix `tmux`。

#### Scenario: P6 之后 `omx-team-auto.ps1 -Apply` 在 native Windows 下启动 team

- **WHEN** 操作员在 native Windows 下运行 `omx-team-auto.ps1 -Phase execute-parallel -ParallelSlices 2 -Apply`
- **THEN** helper SHALL 能通过 Windows backend 执行 launch
- **AND** 它 SHALL 继续保持 tracked-team record 合同
