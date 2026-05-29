## ADDED Requirements

### 需求：Project MOE Phase 1 read contract 拒绝不支持的 envelope schema

Project MOE Phase 1 readiness checker 必须拒绝 `schema_version` 与本工具链支持版本不一致的目标 Mode CLI read-contract JSON envelope。

#### 场景：不支持的 schema version fail-closed

- **GIVEN** 目标项目已满足 Phase 1 静态 readiness surface
- **AND** 其只读 Mode CLI 命令输出 `schema_version` 不等于 Project MOE GUI 工具链支持版本的 JSON envelope
- **WHEN** 操作员以 execute-read-contract 模式运行 `check_project_moe_phase1_readiness.py --json`
- **THEN** checker 报告 `ok=false`
- **AND** 返回稳定 blocker `blocked:cli_envelope_schema_version_mismatch`
- **AND** `control_mode_allowed` 保持 false。

#### 场景：static-only 模式仍然不执行目标 CLI

- **GIVEN** 目标项目的 Mode CLI 如果执行会输出不受支持的 schema version
- **WHEN** 操作员运行 `--static-only --json` readiness checker
- **THEN** checker 不执行目标 CLI
- **AND** 该运行时 schema 既不会作为控制就绪证据，也不会作为控制阻断证据。
