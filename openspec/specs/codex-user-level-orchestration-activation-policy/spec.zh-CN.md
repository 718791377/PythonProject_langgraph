# Codex 用户级 Orchestration Activation Policy

## 目的

定义 Codex CLI 的可复用用户级 orchestration-activation policy，使新旧任务流都能重新检查、retrofit 并实际采用合适的协同面。本文是英文 primary spec 的中文 companion；每个 Requirement 与 Scenario 标题保留英文源标题，便于 `tools/check_orchestration_collaboration_evidenceguard.py` 做双语 OpenSpec heading parity 检查。

## 要求

### Requirement: Automatic collaboration SHALL be the user-level default / 自动协作必须作为用户级默认值

用户级 orchestration activation policy 必须把 automatic collaboration 定义为所有通过用户级 workflow 启动的项目与 Codex 会话的默认行为。操作员不需要重复输入 "use experts"、"use durable_team"、"use persistent team"、"parallel" 或 "subagents"，路由仍必须评估 experts、durable workflow 与 persistent team。

当任务因为范围、风险、多文档、多阶段、独立执行切片或稳定化需要而达标时，会话必须自动评估并采用 native experts、`native_omx`、LangGraph durable workflow 与 persistent team 中最小充分的协同面。

#### Scenario: Large task starts without repeated prompt reminder / 大任务启动时没有重复协同提示

- **WHEN** 新会话或恢复会话收到符合条件的多阶段或多文档任务
- **THEN** activation trace 必须评估 experts、durable workflow 与 persistent team，而不要求操作员重复协同提示
- **AND** trace 必须引用 phase、threshold、readiness、blocker 或 main-session takeover，而不是引用缺少用户提醒

#### Scenario: Native subagent invocation is platform-blocked / 原生 subagent 调用被平台阻塞

- **WHEN** native expert routing 适合当前任务，但当前 platform/tool contract 阻止直接 `spawn_agent` 调用
- **THEN** activation trace 必须报告 `experts=blocked:platform_subagent_invocation_constraint`
- **AND** 会话必须继续通过合格 durable lane、更窄的可用 expert path 或明确 main-session takeover 推进
- **AND** blocker 不得被改写成“用户没有要求 subagents”或等价缺失提醒语言

### Requirement: Generated startup instructions SHALL preserve the automatic collaboration default / 生成的启动指令必须保留自动协作默认值

生成的用户级 startup model instructions 与 `team-leader.toml` profile 必须包含 global automatic collaboration default 与具体的 platform-subagent blocker rule。

#### Scenario: Wrapped launcher emits model instructions / 包装 launcher 输出 model instructions

- **WHEN** wrapped Codex launcher 创建 file-backed model instructions payload
- **THEN** payload 必须声明 automatic collaboration 是默认行为
- **AND** payload 必须声明用户不需要重复 experts、durable_team 或 persistent team 提醒
- **AND** payload 必须保留 `platform_subagent_invocation_constraint` 作为 platform/tool blocker token

#### Scenario: Team leader profile is generated / 生成 team leader profile

- **WHEN** 用户级 installer 生成 `team-leader.toml`
- **THEN** profile 必须包含 global automatic collaboration default
- **AND** profile 必须禁止使用缺少用户提醒作为跳过 orchestration 的原因

### Requirement: The user-level installation SHALL expose an orchestration-activation policy / 用户级安装必须暴露 orchestration-activation policy

用户级安装必须为 Codex CLI 暴露一套可复用 orchestration-activation policy，并定义 activation 的任务流范围、re-check 触发器、hard routing directive，以及 thresholds 命中且没有 blocker 时的必需动作。

#### Scenario: Operator inspects the user-level activation policy / 操作员检查用户级 activation policy

- **WHEN** 操作员检查用户级 orchestration policy surfaces
- **THEN** 他必须能识别 activation posture、re-check triggers、hard directives 与 retrofit rules
- **AND** 不应只能通过 repository-local 项目文档推断这些规则

### Requirement: Existing projects and existing sessions SHALL remain orchestration-retrofit capable / 既有项目和既有会话必须保持 orchestration-retrofit 能力

用户级 orchestration policy 必须支持既有项目的新会话，以及 reload、restart、显式用户路由指令或 tracked durable-state detection 之后的既有 live session retrofit。

#### Scenario: Existing live session is explicitly told to use `omx` / 既有 live session 被明确要求使用 `omx`

- **WHEN** 用户明确告诉 Codex CLI 使用 `omx`
- **THEN** Codex CLI 必须把该指令视为 hard routing directive
- **AND** 除非存在具体 blocker，否则必须采用 orchestration path
- **AND** 如果未采用 orchestration path，必须解释具体 blocker

### Requirement: Activation traces SHALL expose full orchestration state / Activation trace 必须暴露完整 orchestration 状态

用户级 orchestration activation policy 必须要求 activation trace 报告完整当前字段集：`phase`、`capability_chain`、`backend_default`、`backend_ready`、`experts`、`durable_workflow`、`persistent_team`、`main_session_escalation`、`approval_timeout_risk`、`approval_receipt` 与 `why`。Trace vocabulary 必须区分 state meaning：`not_needed`（threshold 未满足或无需 lane）、`candidate`（具备候选资格但未采用）、`selected`（已选择但尚未运行）、`running`（durable 或 persistent execution 正在运行）、`complete`（已完成且不再活跃）与 `blocked`（因具名 blocker 或未满足 threshold 而无法继续）。

用户可见会话表面必须保留字面标签 `Routing trace` 和 `Updated Plan`。这些标签下的解释内容可以使用中文。`Routing trace` 必须是普通文本诊断行或短块，必须只有一个可见 trace 标签，必须使用完整固定 key=value 字段集，并且不得使用 `experts_now` 或 `durable_team` 等旧短字段；它不得是进度面板。如果外层 wrapper、launcher 或 runtime 已经为当前 activation 注入 `Routing trace`，assistant 正文不得为同一 activation 再输出第二个 `Routing trace` 块。`Updated Plan` 必须是用户可见进度面板，必须只有一个 CLI/tree 勾选/空方框状态清单表面，并且不得重复、嵌套或渲染为 Markdown checkbox。原生 `update_plan` render 必须是 canonical `Updated Plan` 面板；该原生面板出现后，assistant 正文不得再手写第二个 `Updated Plan` 标题、嵌套 `Updated Plan` 树节点或 Markdown checkbox 镜像。如果没有输出原生计划面板但仍需要简短进度说明，assistant 必须使用 `执行进度` 等不冲突标签，而不是冒充 `Updated Plan`。Markdown checkbox syntax 必须仅保留为 implementation-plan-internal，不得作为用户可见的 `Updated Plan` 会话表面。

仓库必须提供可执行 trace-evidence validator，检查保存的 activation trace text 是否具备 required fields、capability-chain consistency、backend readiness semantics、durable workflow 与 persistent-team vocabulary、forbidden missing-reminder reasons、expert-timeout evidence labels，以及 `why` 字段中的 durable-team threshold evidence。仓库也必须提供 `tools/check_expert_lifecycle_wait_pacing_evidence.py`，用于检查 completed-expert closure、preserved-thread exceptions、bounded wait windows、liveness/stall actions 与 provider pacing as backpressure。

Prompt-independent collaboration parity 必须由 checker 背书。仓库必须提供 `tools/check_orchestration_collaboration_evidenceguard.py` 与 fixture pairs，证明同等任务在有无协同短语时产生同等 routing decisions。该 checker 还必须验证 cold-start read-order evidence、durable/persistent evidenceguard records、structured expert lifecycle audit events、落盘 JSONL expert lifecycle audit logs，并要求 `spawn`、`wait`、`timeout`、`result`、`absorbed` 与 `close` 事件具备各自必需字段；同时还必须要求 `spawn.scope` 与 `spawn.non_goals` 是非空的非空字符串列表，`result.changed_paths` 是非空字符串列表，并验证 LangGraph state release evidence。durable/persistent evidenceguard 必须拒绝缺少 active selector、backend family、preflight、ownership plan、manifest 或 LangGraph thread state、heartbeat、close 与 leader absorption 证据的 selected、running 或 complete durable-team claims。LangGraph state release 必须拒绝 completed work 仍停留在 stale `running` state 而未记录 `completed_at`、`final_phase`、`result_summary` 与 `released_by` 的状态。

中文 OpenSpec companion 必须保留英文 primary 中每一个 `### Requirement:` 与 `#### Scenario:` 源标题，并明确记录双语 OpenSpec heading parity；`tools/check_orchestration_collaboration_evidenceguard.py` 必须在该 双语 OpenSpec heading parity 丢失时让 repository check 失败。

Registered collaboration evidenceguard fixtures 必须由 checker 背书。required fixture registry 必须覆盖 prompt-independent parity、cold-start read order、durable/persistent claim、expert lifecycle audit、main-session escalation 与 LangGraph state release；如果任何 required evidenceguard fixture 静默消失，repository-mode check 必须失败。

#### Scenario: Saved trace evidence is checked / 检查保存的 trace evidence

- **WHEN** 保存的 activation trace 被传给 repository trace-evidence validator
- **THEN** validator 必须在任何 required trace field 缺失时失败
- **AND** capability-chain dependency states 不一致时必须失败
- **AND** durable workflow 或 persistent-team state 使用不支持 vocabulary 时必须失败
- **AND** expert timeout language 没有 non-evidence、bounded-wait、respawn、durable-handoff 或 main-session-takeover 标签时必须失败
- **AND** durable workflow 或 persistent-team decisions 在 `why` 中缺少 required unmet-threshold、named-blocker 或 triggered-threshold evidence 时必须失败

#### Scenario: Prompt-independent collaboration parity evidence is checked / 检查 prompt-independent collaboration parity evidence

- **WHEN** repository evidenceguard 验证 prompt-independent collaboration fixtures
- **THEN** 对同一 task shape，有无 collaboration phrases 的配对用例必须产生相同 route fields
- **AND** 缺少 frozen-plan 或 slice thresholds 的显式 `omx` 或 `LangGraph` 指令必须报告 named blockers 或 unmet thresholds
- **AND** missing user reminders 不得出现在 routing reasons 中

#### Scenario: Durable and LangGraph completion evidence is checked / 检查 durable 与 LangGraph 完成证据

- **WHEN** 保存的 durable/persistent 或 LangGraph evidence 被检查
- **THEN** durable/persistent team claims 缺少 required selector、manifest 或 thread-state、heartbeat、close 与 leader absorption evidence 时必须失败
- **AND** completed LangGraph tasks 若 state 仍为 `running` 且没有 release fields，则必须失败



#### Scenario: Registered collaboration evidenceguard fixture coverage is checked / 检查已登记的 collaboration evidenceguard fixture 覆盖

- **WHEN** repository-mode evidenceguard check 运行
- **THEN** required fixture registry 必须包含 prompt-independent parity、cold-start read-order、durable/persistent claim、expert lifecycle audit、main-session escalation 与 LangGraph state release cases
- **AND** 如果 registered fixture directory 缺少任何 required fixture，checker 必须失败


### Requirement: Main-session escalation visibility SHALL be explicit / Main-session escalation visibility 必须显式可见

Orchestration activation policy 必须要求：在 OMX、LangGraph、durable-worker 或 shell workflow 等待主会话审批前，trace 与 saved evidence 必须显式记录 main-session escalation fields，以便 operator 能看见 main Codex CLI session 正在处理、已批准、已超时或已阻塞的 approval request。

Trace 与 saved evidence 必须包含：

- `main_session_escalation`：main Codex CLI session 的 approval lifecycle state，取值为 `not_needed`、`preflight`、`pending_approval`、`granted`、`timed_out` 或 `blocked`
- `approval_timeout_risk`：pending 或 expired approval wait 的当前风险带，取值为 `none`、`low`、`medium`、`high` 或 `expired`
- `approval_receipt`：approval request 的 repo-local proof 或 artifact reference；无需 approval 时为 `none`，否则为 repo-local receipt、interrupt、checkpoint 或 pending-approval artifact reference

Worker contexts 必须收到相同的 approval receipt 或 blocked state；approval waits 不得只停留在 worker 私有上下文中，也不得绕开 main session 的可见审批边界。

#### Scenario: Pending approval is visible before a durable wait / pending approval 在 durable wait 前可见

- **WHEN** LangGraph、OMX、durable-worker 或 shell flow 需要 main-session approval
- **THEN** saved evidence 必须记录 `main_session_escalation=pending_approval`
- **AND** 必须记录非 `none` 的 `approval_timeout_risk`
- **AND** 必须记录可追踪的 `approval_receipt`
- **AND** 必须说明 approval decision 由 main session 持有，而不是由 worker 私下持有

#### Scenario: Approval wait times out / approval wait 超时

- **WHEN** pending main-session approval 超过允许等待窗口
- **THEN** saved evidence 必须记录 `main_session_escalation=timed_out` 或 `main_session_escalation=blocked`
- **AND** 对应 approval 必须记录 `approval_timeout_risk=expired`
- **AND** 必须记录 named blocker，例如 `blocked:approval_timeout`

#### Scenario: No approval is required / 不需要 approval

- **WHEN** 当前任务不需要 privileged shell、durable workflow 或 worker approval
- **THEN** trace 必须记录 `main_session_escalation=not_needed`
- **AND** 必须记录 `approval_timeout_risk=none`
- **AND** 必须记录 `approval_receipt=none`

### Requirement: Missing user reminders SHALL NOT be a routing reason / 缺少用户提醒不得作为路由理由

Orchestration activation policy 必须禁止使用 "the user did not request parallelism"、"the user did not request subagents" 或等价 missing-reminder language 作为不使用 experts、durable workflow 或 persistent team 的原因。

#### Scenario: A small single-file task does not need a durable team / 小型单文件任务不需要 durable team

- **WHEN** 当前任务是小型单文件任务
- **THEN** trace 可以报告 `persistent_team=not_needed`
- **AND** reason 必须引用 task phase、scope、risk 或 threshold state
- **AND** 不得引用缺少用户指令作为原因

### Requirement: Expert timeout SHALL NOT be accepted as verification evidence / Expert timeout 不得被接受为验证证据

Orchestration activation policy 必须要求 final reports 区分 returned expert evidence 与 timed-out、stalled、abandoned 或 main-session-taken-over verification。仓库必须提供可执行 expert lifecycle/wait/pacing evidence checker，用来检查保存的 run-summary 或 transcript evidence。 The checker also validates saved JSON or JSONL evidence and same-agent wait/timeout/result/absorption/close/handling event linkage.

#### Scenario: A key-path expert times out / 关键路径 expert 超时

- **WHEN** 关键路径 expert 或 subagent 超时或 stall
- **THEN** 会话不得把该 lane 作为 evidence 使用
- **AND** 必须继续 bounded wait、respawn 更窄 expert、handoff 到合格 durable lane，或明确记录 main-session takeover

#### Scenario: Saved expert lifecycle and wait evidence is checked / 检查保存的 expert lifecycle 与 wait evidence

- **WHEN** 保存的 expert lifecycle 或 wait evidence 被传给 expert lifecycle/wait/pacing evidence checker
- **THEN** checker 必须在 completed expert claims 缺少 closure evidence 或 preserved-thread reason 时失败
- **AND** wait claims 缺少 bounded wait windows 或 total wait bound 时必须失败
- **AND** liveness 或 stall claims 缺少 inspect、redirect、respawn、durable-handoff 或 main-session-takeover action 时必须失败
- **AND** timeout events missing prior wait and handling event for the same `agent_id` MUST fail
- **AND** result, absorbed, or close events not linked to the same `agent_id` MUST fail unless a preserved-thread reason is explicit
- **AND** two quiet `progress_check` events without same-agent inspect, redirect, respawn, durable-handoff, or main-session-takeover action MUST fail
- **AND** provider pacing claims 若把 upstream pacing 当作禁用 orchestration 的原因而非 backpressure 标签，则必须失败

### Requirement: Existing sessions SHALL retrofit activation policy at safe boundaries / 既有会话必须在安全边界 retrofit activation policy

既有 live sessions 必须在 reload、restart、resume、continue、phase change、durable-state detection、capability-state change 或 expert timeout 后重新运行 activation checks。

#### Scenario: A legacy session is resumed / 恢复 legacy session

- **WHEN** legacy resumed session 在本仓库继续工作
- **THEN** 它必须把当前 repository governance 与 capability-chain policy 作为权威
- **AND** 不得让陈旧 runtime assumptions 覆盖当前 policy

### Requirement: First activation traces SHALL report durable-team threshold evidence / 首次 activation trace 必须报告 durable-team threshold evidence

Startup 与 first activation traces 必须包含 durable-team threshold evidence。未选择 durable team 时，trace 必须引用具体 unmet threshold；durable team 被 blocked 时必须引用 named blocker 或 unmet threshold；durable team 被 selected 或 running 时必须引用具体 trigger。

#### Scenario: First activation does not select a durable team / 首次 activation 不选择 durable team

- **WHEN** session 为 startup、resume 或 continue 输出首次 activation trace
- **AND** durable-team thresholds 未满足
- **THEN** trace 必须报告 `persistent_team=not_needed` 或 `persistent_team=blocked`
- **AND** trace 必须在 `why` 中识别 unmet durable-team threshold 或 named blocker
- **AND** 不得暗示缺少用户提醒导致 no-team decision

#### Scenario: First activation selects a durable team / 首次 activation 选择 durable team

- **WHEN** session 输出首次 activation trace
- **AND** plan 已冻结且存在两个或更多 independent execution slices，或 stabilization threshold 已满足
- **THEN** trace 必须把 durable-team lane 报告为 `selected` 或 `running`
- **AND** trace 必须在 `why` 中识别具体 threshold trigger

#### Scenario: Trace validator rejects vague durable-team decisions / Trace validator 拒绝模糊 durable-team decisions

- **WHEN** saved trace evidence 报告 `persistent_team=not_needed` 但 `why` 中没有 `threshold_not_met:*` 或等价 unmet-threshold language
- **OR** 报告 `persistent_team=blocked` 但没有 `blocked:*` 或 unmet-threshold language
- **OR** 报告 `persistent_team=selected` 或 `persistent_team=running` 但没有 `triggered_threshold:*` 或等价 trigger language
- **THEN** trace-evidence validator 必须让 trace 失败

### Requirement: Hard routing directives SHALL require adoption or named blockers / 硬路由指令必须采用或报告 named blockers

Orchestration activation policy 必须把用户对 `omx` 或 `LangGraph` 的显式请求视为当前 task flow 的 hard routing directives。条件满足时必须报告 selected/running；未采用时必须报告 named blocker 或 unmet threshold。仓库必须提供 `tools/check_role_routing_directive_evidence.py` 验证保存证据。

#### Scenario: Explicit directive is adopted / 显式指令被采用

- **WHEN** 用户显式请求 `omx` 或 `LangGraph`
- **AND** capability chain、preflight 与 task thresholds 满足
- **THEN** activation trace 必须把 requested lane 报告为 `selected` 或 `running`
- **AND** 不得停留在 explanation-only mode
- **AND** saved evidence 必须通过 role/directive checker

#### Scenario: Explicit directive is blocked / 显式指令被阻塞

- **WHEN** 用户显式请求 `omx` 或 `LangGraph`
- **AND** requested lane 无法采用
- **THEN** activation trace 必须报告 `blocked:<reason>` 或 `threshold_not_met:<reason>`
- **AND** 不得把该 directive 描述成 optional preference

### Requirement: Smallest-sufficient role selection SHALL stay trigger-based / 最小充分角色选择必须基于触发条件

Orchestration activation policy 必须为当前 phase 选择最小充分 expert role set，不得仅因为角色可用而添加角色。bounded multi-face research 必须先使用 homogeneous `analystxN` fan-out，并且只有在 analyst fan-in 暴露 architecture、execution-ordering 或 document-finalization work 后才升级。

#### Scenario: Bounded multi-face research starts analyst-first / bounded multi-face research 先从 analyst 开始

- **WHEN** 当前任务是 bounded multi-face research
- **THEN** 首轮 expert fan-out 必须使用 `analystxN`
- **AND** analyst fan-in 之前不得默认包含 architect、planner 或 writer
- **AND** saved evidence 必须通过 role/directive checker

### Requirement: Agent, skill, profile, and follow-up surfaces SHALL stay distinct / Agent、skill、profile 与 follow-up surfaces 必须保持区分

Orchestration activation policy 必须区分 native Codex subagents、workflow skills、plugin-provided skills、profile helpers、durable workers 与 LangGraph nodes。Skills 从 `SKILL.md` files 加载且不是 native subagents。Profile load 本身不得启动 durable workers，也不得满足 persistent-team thresholds。completed and absorbed expert 后的 follow-up work 必须 spawn fresh agent，除非 preservation 明确。

#### Scenario: A skill is invoked during an activation flow / activation flow 中调用 skill

- **WHEN** workflow skill 或 plugin profile 被使用
- **THEN** final evidence label 不得把该 invocation 当作 returned native expert result
- **AND** 后续 expert follow-up 必须使用 fresh agent，除非 preservation 明确

#### Scenario: Native-agent TOML schema is checked / 检查 native-agent TOML schema

- **WHEN** activation policy guard 运行 custom agent TOML schema validation
- **THEN** native-agent TOML validity 必须与 skill `SKILL.md` validity 分开评估
- **AND** 任何 present standalone agent TOML 缺少或置空 `name`、`description` 或 `developer_instructions` 字段都必须使 checker 失败

#### Scenario: Completed expert evidence requires closure or preservation / completed expert evidence 需要 closure 或 preservation

- **WHEN** run summary 表示 expert returned 且 was absorbed
- **THEN** saved evidence 也必须显示 completed-agent closure 或 explicit preserved-thread reason
- **AND** 后续 follow-up 必须 spawn fresh agent，除非 preservation 明确

### Requirement: The main Codex CLI session SHALL remain the leader / 主 Codex CLI 会话必须保持 leader

当前主 Codex CLI 会话必须保持 activation checks、role selection、worker briefs、fan-in、evidence labeling、final integration 与 release recommendations 的 leader。Orchestration 不得要求单独的 persistent leader pane，workers、skills、plugin profiles 与 LangGraph nodes 不得成为独立 release authorities。Adoption decisions 必须面向当前 task flow。

#### Scenario: Existing project resumes work / 既有项目恢复工作

- **WHEN** 既有项目或 legacy resumed session 继续某个 task flow
- **THEN** 主会话必须应用当前 repository governance 与 capability-chain policy
- **AND** local mainline 与 publication decisions 必须保持在用户授权的 leader 控制下
- **AND** saved leader/session scope evidence 必须通过 `tools/check_leader_session_scope_evidence.py`

#### Scenario: Startup or first activation does not auto-launch a durable team / startup 或首次 activation 不自动启动 durable team

- **WHEN** startup 或 first activation evidence 报告没有 durable team
- **THEN** 它必须引用具体 unmet threshold，例如 `threshold_not_met:no_frozen_plan` 或 `threshold_not_met:single_execution_slice`
- **AND** 不得宣称 Codex startup 本身自动启动 durable team

#### Scenario: Routing adoption is task-flow scoped / Routing adoption 面向 task-flow

- **WHEN** 为既有项目或新仓库决定 orchestration adoption
- **THEN** decision 必须引用当前 task-flow phase、thresholds、blockers 或 task-fit evidence
- **AND** 不得使用 repository age 或 new/existing project status 作为 adoption basis

### Requirement: Native Codex SHALL remain the base layer and durable lanes SHALL be task-fit choices / Native Codex 必须保持基础层，durable lanes 必须按任务适配选择

Native Codex 必须保持 base layer。oh-my-codex、native_omx、skills、profile helpers 与 LangGraph 必须被描述为 additive workflow 或 durable-state layers，而不是 Codex replacements。一个 durable task 一次必须只使用一个 backend family。`native_omx` 用于 worker-centric durable execution；LangGraph 用于 graph-shaped multi-phase execution、checkpoint、approval gates、frozen briefs 与 survivor queues。

#### Scenario: Effective lane differs from default backend / effective lane 不同于默认 backend

- **WHEN** LangGraph ready 但任务是 worker-centric
- **THEN** activation 可以基于 named worker-centric reason 选择 `native_omx` 作为 effective lane
- **AND** 不得在没有 explicit close 或 handoff 的情况下混用 `native_omx` worker lifecycle 与 LangGraph checkpoint state
- **AND** saved lane-fit evidence 必须通过 `tools/check_effective_lane_fit_evidence.py`

#### Scenario: LangGraph lane is selected for graph-shaped work / graph-shaped work 选择 LangGraph lane

- **WHEN** durable task 选择 LangGraph 作为 effective lane
- **THEN** evidence 必须引用 graph-shaped multi-phase execution、checkpoint-driven recovery、interrupt/resume approval gates、frozen briefs、persisted survivor queues 或等价 graph-shaped fit
- **AND** 不得只依赖 `backend_default=langgraph` 或 backend readiness 作为 task-level adoption reason

#### Scenario: Backend family switching is explicit / backend family 切换必须显式

- **WHEN** saved evidence 在一个 durable task flow 中同时提到 `native_omx` 与 LangGraph
- **THEN** evidence 必须显示 active task 使用一个 backend family，或在切换前记录 explicit close/handoff
- **AND** 如果切换 silent 或 implicit，lane-fit evidence 必须失败

### Requirement: Delegation SHALL preserve critical-path leader work / Delegation 必须保留关键路径 leader work

Delegation 必须 concrete、bounded、self-contained 且 materially advancing。Leader 必须在 delegating 前识别 immediate critical-path work，避免 duplicate work，delegated work 运行时继续 meaningful non-overlapping leader work，并且 sparingly 使用 `wait_agent`。Provider upstream pacing 必须报告为 backpressure，不得作为禁用 orchestration 的理由。

#### Scenario: A sidecar expert is running / sidecar expert 正在运行

- **WHEN** delegated sidecar work 正在进行
- **THEN** leader 必须继续 non-overlapping local work，或记录为何被 blocked
- **AND** 未经 review 与 evidence labeling，不得宣称 delegated result 已被接受

#### Scenario: Wait and pacing evidence is checked / 检查 wait 与 pacing evidence

- **WHEN** saved evidence 提到 `wait_agent`、liveness checks、stalled experts 或 provider pacing
- **THEN** expert lifecycle/wait/pacing checker 必须要求 bounded wait windows 与 total bound evidence
- **AND** 必须要求 liveness/stall handling，例如 inspect、redirect、respawn、durable handoff 或 main-session takeover
- **AND** structured lifecycle audit records MUST keep wait, timeout, result, absorption, close, and handling events tied to the same `agent_id`
- **AND** 必须拒绝把 provider pacing 用于禁用 orchestration 而非标记 backpressure 的语言

### Requirement: Delegation and leader wait discipline SHALL be script-checkable / Delegation 与 leader wait discipline 必须可脚本检查

Orchestration activation policy 必须要求 delegated expert 或 worker work concrete、bounded、self-contained、non-duplicative 且 materially advancing，同时当前主 Codex CLI 会话保持 leader。仓库必须提供 `tools/check_delegation_wait_discipline_evidence.py` 验证 delegation design、code-worker ownership、duplicate-work prevention 与 leader wait discipline。

#### Scenario: Delegation evidence is validated / 验证 delegation evidence

- **GIVEN** saved run summary 描述 delegated expert 或 worker work
- **WHEN** evidence checker 针对该 summary 运行
- **THEN** 如果 summary 缺少 immediate critical-path local work，则必须失败
- **AND** 如果 delegated task 没有被描述为 concrete、bounded、self-contained sidecar work that materially advances the task，则必须失败
- **AND** 如果缺少 duplicate-work prevention 或 non-overlapping ownership，则必须失败
- **AND** 如果 code-changing worker delegation 缺少 file/module ownership、"not alone in the codebase" instructions 或 changed-path reporting expectations，则必须失败

#### Scenario: Leader waits for delegated work / Leader 等待 delegated work

- **GIVEN** saved run summary 描述 `wait_agent` 或等价 delegated work 等待
- **WHEN** evidence checker 针对该 summary 运行
- **THEN** 如果 wait indefinite、silent 或 reflexive，则必须失败
- **AND** 必须要求等待期间存在 meaningful non-overlapping leader work，或存在清晰 critical-path blocker

### Requirement: Fan-out and write-heavy parallel execution SHALL be bounded and ownership-isolated / Fan-out 与 write-heavy parallel execution 必须有边界并隔离 ownership

Native Codex subagent use 必须保持 leader-side spawning 与 leader-owned fan-in。Raw Codex 不得被描述为默认自动 spawn specialist roles。Managed fan-out 必须保持 `agents.max_threads=6` 与 `agents.max_depth=1`，除非记录 explicit override、reason 与 approval。Write-heavy parallel execution 必须声明 file/module ownership、disjoint write sets、hotspot serialization 与 leader-owned final integration。

#### Scenario: Managed fan-out stays within defaults / managed fan-out 保持默认边界

- **WHEN** saved evidence 描述 native subagent 或 expert fan-out
- **THEN** 它必须保持在 `agents.max_threads=6` 与 `agents.max_depth=1` 内
- **OR** 必须记录 explicit override、reason 与 approval
- **AND** 必须显示 leader-side spawning 与 leader-owned fan-in，而不是 raw Codex auto-spawning specialist roles

#### Scenario: Write-heavy parallel work is ownership-isolated / write-heavy parallel work 隔离 ownership

- **WHEN** saved evidence 描述 write-heavy parallel execution 或 code-changing workers
- **THEN** 必须声明 file/module ownership 与 disjoint write sets
- **AND** 必须识别 hotspot serialization，或说明不存在 shared hotspot
- **AND** 必须识别 leader-owned final integration
- **AND** worker briefs 必须包含 not-alone/do-not-revert-or-overwrite instructions 与 changed-path reporting

#### Scenario: Overlapping write sets are serialized / overlapping write sets 必须串行化

- **WHEN** saved evidence 提到 overlapping write sets 或 shared hotspot paths
- **THEN** evidence 必须在 parallel write work 继续前显示 hotspot serialization、sequential ownership transfer 或 leader-owned merge plan
- **AND** 如果 overlapping write-heavy workers 在没有 serialization 的情况下启动，fan-out/write-ownership evidence 必须失败

### Requirement: Exploration, code-change delegation, and durable artifact persistence SHALL stay script-checkable / Exploration、code-change delegation 与 durable artifact persistence 必须可脚本检查

Read-only exploration 必须用于具体 codebase questions、symbol mapping 或 file discovery。当安全 implementation patch 已明确时，read-only exploration 不得替代 bounded code-changing worker task。当任务需要 graph phases、checkpoint gates、frozen briefs、survivor queues 或 tracked LangGraph thread state 时，必须使用 LangGraph entrypoints 与 repo-local `.omx/state/langgraph/` state。`.omx/state/selectors/active.json` 必须作为 automatic durable-team adoption 的 active selector authority。Durable artifacts、frozen briefs 与 survivor queues 必须写入 repo-local state 或 documented artifact paths。

#### Scenario: Graph-shaped checkpoint work is selected / 选择 graph-shaped checkpoint work

- **WHEN** 任务需要 checkpoint gates、frozen briefs、survivor queues 或 tracked LangGraph thread state
- **THEN** durable workflow 必须使用 LangGraph entrypoints 与 repo-local `.omx/state/langgraph/` state
- **AND** durable artifacts 必须有 documented artifact paths 或 repo-local state locations
- **AND** automatic durable-team adoption 必须引用 `.omx/state/selectors/active.json`，而不是只引用 compatibility records

#### Scenario: Exploration does not replace bounded implementation / exploration 不得替代 bounded implementation

- **GIVEN** implementation patch 明确且可安全 delegation
- **WHEN** read-only exploration evidence 被记录
- **THEN** exploration 必须 specific、well-scoped 且 read-only
- **AND** 它不得成为 code-changing implementation task 的唯一 evidence surface

#### Scenario: Durable handoff artifacts are persisted / durable handoff artifacts 必须持久化

- **WHEN** research fan-in 生成 frozen implementation brief，或 adversarial review 留下 survivor candidates
- **THEN** brief 或 survivor queue 必须持久化到 repo-local state 或 documented artifact paths
- **AND** 它必须包含 required handoff fields 或 debugger-lane follow-up evidence，而不是只存在于 transient chat context

### Requirement: Research handoff and adversarial review SHALL persist bounded handoffs / Research handoff 与 adversarial review 必须持久化 bounded handoffs

Open-ended work 必须保持 research 与 implementation 分属不同 roles。Research fan-in 后，结果必须作为 frozen implementation brief 持久化，包含 scope、non-goals、acceptance evidence、ownership boundaries 与 unresolved risks，然后才开始 implementation。`bug-finder`、`bug-rebutter` 与 `bug-judge` 必须保持 burst、read-only、leader-side roles。其 survivors 必须作为 adversarial-review survivor queue 持久化，用于 debugger-lane follow-up。

#### Scenario: Contested bug review leaves survivors / contested bug review 留下 survivors

- **WHEN** normal verification 留下 contested 或 high-volume bug candidates
- **THEN** burst bug-triad results 必须被 absorbed and closed
- **AND** unresolved survivors 必须持久化用于 debugger-lane follow-up，而不是保持 persistent bug workers 存活

### Requirement: Capability switch chains SHALL be executable-policy checked / Capability switch chains 必须由 executable policy 检查

Orchestration activation policy 必须把 capability switches 视为 strict dependency chain，并使用 `tools/check_capability_switch_chain.py` 作为当前 user-level state 的 executable policy support。`subagent_routing=off` 必须要求 higher orchestration layers 关闭，`oh_my_codex=off` 必须要求 `langgraph=off`，`durable_orchestration_backend=langgraph` 必须要求 `langgraph=on`。

#### Scenario: Activation policy guard checks switch dependencies / activation policy guard 检查 switch dependencies

- **WHEN** orchestration activation policy guard 运行
- **THEN** 它必须调用或嵌入 capability-switch dependency checker
- **AND** invalid present state combinations 必须作为 capability-chain violations 失败

### Requirement: Orchestration enforcement checkers are wired into shared CI / Orchestration enforcement checkers 必须接入 shared CI

仓库必须通过 shared local/remote CI manifest 运行现有 automatic-orchestration enforcement checker tests，并且在无需 synthetic task evidence 即可执行时，从 `tools/run_openspec_guard.py` 运行 no-input orchestration guard checks。

#### Scenario: Local gate covers existing orchestration checker tests / local gate 覆盖现有 orchestration checker tests

- **GIVEN** `tools/ci/local_gate.ps1` 被运行
- **WHEN** 它通过 `tools/ci/ci_test_manifest.json` 执行 Python unit tests
- **THEN** manifest 中必须包含 capability-switch、orchestration trace evidence、expert lifecycle/wait pacing 与 custom-agent TOML schema tests

#### Scenario: OpenSpec guard runs capability-switch chain validation / OpenSpec guard 运行 capability-switch chain validation

- **GIVEN** `tools/run_openspec_guard.py --root . --json` 被运行
- **WHEN** user-level capability state 与 repo-local backend context 可用或缺失
- **THEN** `check_capability_switch_chain.py` 必须作为 OpenSpec guard step 调用，并通过 guard payload 报告 violations 或 warnings

### Requirement: Agent skill and profile surfaces SHALL remain distinct / Agent skill 与 profile surfaces 必须保持区分

Orchestration activation policy 必须保持 native Codex agents、workflow skills、plugin-provided skills、plugin modules 与 profile helpers 是不同 surfaces，并且必须拒绝把 skill/profile invocation 当作 native subagent 或 expert-result evidence 的 evidence。

#### Scenario: Repository policy surfaces distinguish execution surfaces / repository policy surfaces 区分 execution surfaces

- **GIVEN** repository OpenSpec guard 运行
- **WHEN** 它检查 orchestration activation policy surfaces
- **THEN** policy surfaces 必须声明 native agents 从 agent TOMLs 加载，skills 从 `SKILL.md` 加载，profile helpers 只改变 visible procedural context，并且 skill/profile invocation 不是 expert evidence

#### Scenario: Evidence rejects skill or profile claims as expert evidence / evidence 拒绝 skill 或 profile 被声明为 expert evidence

- **GIVEN** saved routing report 被检查
- **WHEN** 它把 skill invocation 或 plugin profile load 声称为 expert returned result、native subagent、worker 或 durable-team evidence
- **THEN** checker 必须失败，除非它另外识别实际 expert result、durable checkpoint 或 local verification source
