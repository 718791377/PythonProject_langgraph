## ADDED Requirements / 新增需求

### Requirement: Durable routing smoke gates SHALL declare the target, phase, task, and consent boundary / durable routing smoke gate 必须声明目标、阶段、任务和授权边界

在任何 live durable routing smoke test 或 adoption gate exercise automatic routing behavior 之前，被 review 的 change 必须声明四个 gate fields：

- `target_repository` —— 目标仓库根目录，用来说明本次 exercise 的 source、OpenSpec artifacts 和 repo-local durable state 属于哪个仓库。
- `phase` —— 项目阶段，用来驱动 routing thresholds，例如 read-context、verify-accept、execute-parallel、integrate-converge 或 stabilize。
- `task` —— 具体任务或验证问题，用来说明 routing plan 到底在评估什么。
- `operator_consent_boundary` —— 操作员授权边界，用来区分 read-only planning 与 `-Apply`、`.omx/state/` 写入或 durable-team launch 等变更动作。

除非 reviewed change 和 operator 显式授权 mutation，否则默认 consent boundary 必须是 read-only。

#### Scenario: A future smoke gate stays read-only until consent is explicit / 未来 smoke gate 在显式授权前保持只读

- **WHEN** 一个 reviewed change 声明 durable routing smoke gate，但没有显式 mutation consent
- **THEN** routing exercise 必须限制为 dry-run planning 或 read-only inspection
- **AND** 不得运行 `omx-team-auto.ps1 -Apply`
- **AND** 不得写入 `.omx/state/`
- **AND** 不得 launch 或 shutdown durable team

#### Scenario: A future adoption gate names its repository and task before runtime exercise / 未来 adoption gate 在 runtime exercise 前说明仓库和任务

- **WHEN** 未来 adoption gate 准备 exercise automatic durable routing
- **THEN** 它必须先识别 `target_repository`、`phase`、`task` 和 `operator_consent_boundary`
- **AND** routing result 必须解释为什么对该 task flow 选择或拒绝 `native_omx`、`langgraph` 或 no durable team
