# codex-user-level-team-mode-automatic-team-routing Specification

## 目的

TBD - 由归档变更 `implement-codex-user-level-team-mode-p5-automatic-team-routing` 时创建。归档后补全 Purpose。

## 要求

### Requirement: 安装器 SHALL 生成 automatic durable-team routing helper

安装器 SHALL 在目标 Codex home 中生成一个附加式的用户级 durable-team routing helper。

生成的资产至少 SHALL 包含：

- `bin/omx-team-auto.ps1`

该 helper SHALL 保持 additive-only，并且 SHALL 调用解析后的原生 `omx` 命令路径，而不是替换原生可执行文件。

#### Scenario: 在临时 Codex home 中生成 P5 helper

- **WHEN** 安装器针对一个显式目标 Codex home 运行
- **THEN** 它 SHALL 生成 `bin/omx-team-auto.ps1`
- **AND** 它 SHALL 让该 helper 继续处于现有备份与回滚事务中

### Requirement: helper SHALL 输出可检查的 automatic durable-team routing plan

`omx-team-auto.ps1` SHALL 在真正修改状态之前输出结构化 routing plan。

该 plan 至少 SHALL 包含：

- 当前 mode 与 capability flags
- 请求的 phase
- 期望的 durable team 形态（如果有）
- 已跟踪的 team record（如果有）
- 决策：`no-team`、`launch`、`reuse`、`switch`、`shutdown` 或 `manual-inspection-required`

#### Scenario: execute-parallel planning 选择保守 worker swarm

- **WHEN** 操作员运行 `omx-team-auto.ps1 -Phase execute-parallel -ParallelSlices 2 -Task "implement rollout X" -Json`
- **THEN** 它 SHALL 报告一个 durable-team 决策
- **AND** 它 SHALL 推导出等价于 `2:team-executor` 的团队形态

#### Scenario: verify-accept planning 不保留 durable team

- **WHEN** 操作员运行 `omx-team-auto.ps1 -Phase verify-accept -Task "final sign-off" -Json`
- **THEN** 它 SHALL 返回 `no-team` 或 `shutdown` 类决策
- **AND** 它 SHALL 不推导新的 durable worker launch

### Requirement: automatic routing SHALL 只管理被跟踪的 repo-local teams

该 helper SHALL 使用如下 repo-local tracked-team record：

- `.omx/state/team/codex-auto-managed-team.json`

只有当 tracked record 存在，且记录中的 team 在当前仓库 team state root 中仍然存在时，helper 才 SHALL 自动管理该 team。

默认情况下，它 SHALL NOT 自动接管一个未托管的既有 team。

#### Scenario: 未托管的现有 team 不会被自动接管

- **WHEN** 仓库中存在最新 team 目录，但不存在 tracked-team record
- **THEN** helper SHALL 返回 `manual-inspection-required` 或等价的安全非变更决策
- **AND** 它 SHALL NOT 自动 shutdown、reuse 或 switch 那个未托管 team

### Requirement: Apply mode SHALL 支持 launch、reuse、switch 与 shutdown

当显式提供 `-Apply` 时，helper SHALL 通过原生 `omx` CLI 执行计划中的 durable-team 变更。

至少：

- `launch` SHALL 调用 `omx team <workerspec> "<task>"`
- `reuse` SHALL 调用 `omx team api create-task`
- `switch` SHALL 关闭被跟踪 team，并启动新的目标 team
- `shutdown` SHALL 关闭被跟踪 team，并清除 tracked-team record

在原生 Windows 上，这 SHALL 表示使用受支持的原生 Windows backend，而不是硬依赖 Unix `tmux`。

#### Scenario: reuse 将工作派发到 tracked team

- **WHEN** 被跟踪 team 与期望的 worker role 和 worker count 匹配
- **AND** 操作员运行 `omx-team-auto.ps1 -Apply`
- **THEN** helper SHALL 通过 `omx team api create-task` 路由新任务
- **AND** 它 SHALL 保留 tracked-team record

#### Scenario: phase 变化触发 debug-team switch

- **WHEN** 当前被跟踪 team 是 development swarm
- **AND** 操作员运行 `omx-team-auto.ps1 -Phase stabilize -BlockingIssues 2 -Apply`
- **THEN** helper SHALL 关闭该 development swarm
- **AND** 它 SHALL 启动等价于 `omx team 2:debugger "<task>"` 的 team
- **AND** 它 SHALL 更新 tracked-team record

#### Scenario: `omx-team-auto.ps1 -Apply` 在原生 Windows 上通过 P6 backend 启动 team

- **WHEN** 操作员在原生 Windows 上运行 `omx-team-auto.ps1 -Phase execute-parallel -ParallelSlices 2 -Apply`
- **THEN** helper SHALL 能通过 Windows backend 执行 launch
- **AND** 它 SHALL 继续保持 tracked-team record 合同

### Requirement: automatic durable routing 必须从已启用 capability 中按任务流选择 effective lane

automatic durable routing 必须从当前已启用的 orchestration capability set 中，按每条任务流选择 effective lane。

当任务流更适合另一条已启用 lane 时，不应要求 operator 先做一次全局 backend-family 切换。

#### Scenario: LangGraph 已启用时，worker-centric 任务流仍选择 native_omx

- **WHEN** 分层 capability set 同时启用了 oh-my-codex durable features 与 LangGraph
- **AND** 当前任务流更适合 worker-centric durable execution
- **THEN** automatic durable routing 层必须把 `native_omx` 选为 effective lane
- **AND** 不应要求先全局关闭 LangGraph capability

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


### Requirement: Durable routing smoke gates SHALL use a script-backed template before runtime exercise / durable routing smoke gate 必须在 runtime exercise 前使用脚本背书模板

Durable routing smoke gates SHALL use a reviewed repository-local template before any later dry-run, read-only sampling, or adoption exercise claims to evaluate automatic durable routing.

在任何后续 dry-run、read-only sampling 或 adoption exercise 声称评估 automatic durable routing 之前，durable routing smoke gate 必须使用已经 review 的 repository-local 模板。

The template SHALL remain read-only and SHALL describe, at minimum:

该模板必须保持只读，并且至少描述：

- `target_repository` —— 拥有 source、OpenSpec artifacts 和 repo-local durable state 的仓库根目录。
- `phase` —— 驱动 durable routing thresholds 的项目阶段。
- `task` —— 正在评估的具体 work item 或 validation question。
- `operator_consent_boundary` —— planning 与 mutation action 之间的显式授权边界。
- `routing_mode` —— field that states whether the exercise stays read-only, runs as dry-run, or may apply only after explicit consent；该字段说明 exercise 是 read-only、dry-run，还是经显式授权后可 apply。
- `mutation_allowed` —— 布尔授权标记；本 release 的默认值必须是 false。
- `validation_path` —— 证明 future exercise 结果所需的 commands、checks 或 evidence。
- `rollback_path` —— future exercise 配置错误或需要撤销时的 recovery steps。

The template SHALL be checked by an executable repository checker and by the OpenSpec guard. The checker SHALL include read-only positive and negative fixture coverage for the template shape, missing required fields, apply mode without mutation consent, and missing read-only guards. The checker SHALL NOT launch a durable team, run `omx-team-auto.ps1 -Apply`, or write `.omx/state/`.

模板必须由可执行的 repository checker 和 OpenSpec guard 校验。该 checker 必须包含只读正向和负向 fixture 覆盖，用于验证模板形状、缺少必填字段、未授权 mutation consent 的 apply mode，以及缺少 read-only guards 的情况。该 checker 不得 launch durable team，不得运行 `omx-team-auto.ps1 -Apply`，也不得写入 `.omx/state/`。

#### Scenario: Guard validates the smoke gate template without mutating durable state / guard 在不修改 durable state 的情况下验证 smoke gate 模板

- **WHEN** the repository OpenSpec guard runs / repository OpenSpec guard 运行
- **THEN** it SHALL execute the durable routing smoke gate template checker / 它必须执行 durable routing smoke gate template checker
- **AND** the checker SHALL validate the required template fields and descriptions / checker 必须验证模板必填字段和字段说明
- **AND** the checker SHALL validate read-only self-test fixtures, including negative fixtures for unsafe adoption-gate shapes / checker 必须验证只读 self-test fixtures，包括 unsafe adoption-gate shapes 的负向 fixtures
- **AND** the checker SHALL remain read-only / checker 必须保持只读
- **AND** it SHALL NOT launch native_omx, launch LangGraph, or mutate `.omx/state/` / 它不得 launch native_omx、launch LangGraph 或修改 `.omx/state/`

#### Scenario: Future smoke gate starts from explicit consent boundaries / future smoke gate 从显式授权边界开始

- **WHEN** a future R0.6.x smoke gate copies or references the reviewed template / future R0.6.x smoke gate 复制或引用已 review 的模板
- **THEN** the future gate SHALL declare `target_repository`, `phase`, `task`, `operator_consent_boundary`, `routing_mode`, `mutation_allowed`, `validation_path`, and `rollback_path` / future gate 必须声明 `target_repository`、`phase`、`task`、`operator_consent_boundary`、`routing_mode`、`mutation_allowed`、`validation_path` 和 `rollback_path`；these fields describe the target, phase, task, consent boundary, routing mode, mutation flag, validation path, and rollback path controls
- **AND** `mutation_allowed` SHALL remain false unless a reviewed change and the operator explicitly authorize mutation / 除非 reviewed change 和 operator 显式授权 mutation，否则 `mutation_allowed` 必须保持 false
