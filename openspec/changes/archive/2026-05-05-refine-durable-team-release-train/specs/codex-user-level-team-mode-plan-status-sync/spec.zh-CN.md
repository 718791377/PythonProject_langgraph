## ADDED Requirements / 新增需求

### Requirement: Release-train roadmap slices SHALL remain bounded before production durable-team claims / production durable-team 声明之前，release-train roadmap slices 必须保持有界

在仓库把任何 production durable-team target 当成 active implementation 之前，roadmap 必须把路径拆成有界 release slices。

默认情况下，每个 release slice 都必须有一个可独立 review 的 OpenSpec change，并且必须说明 validation path、rollback path、target repository、task scope 和 operator consent boundary。

除非 reviewed change 和 operator 明确授权 mutation，否则 roadmap slice 不得暗示可以修改 `.omx/state/`、运行 `omx-team-auto.ps1 -Apply` 或启动 `omx team`。

#### Scenario: A future session chooses the next slice after R0.6 planning / 未来会话在 R0.6 planning 之后选择下一条 slice

- **WHEN** 未来会话在 R0.6 durable routing smoke gate roadmap 细化后继续
- **THEN** 它必须优先选择最小的未完成 subrelease，例如 `R0.6.0 Gate Template` 或 `R0.6.1 Gate Field Checker`
- **AND** 它不得直接跳到 `R2.0 Production Durable Team`
- **AND** 除非某条具体 reviewed release slice 提升了其中一部分，否则它必须保持 production durable-team plan 的 draft status

#### Scenario: A roadmap slice reaches runtime exercise / roadmap slice 进入 runtime exercise

- **WHEN** 未来 release slice 准备进行 runtime exercise
- **THEN** 该 slice 必须先声明 operator consent boundary
- **AND** 在明确授权出现之前，它必须保持 read-only inspection 作为默认姿态
