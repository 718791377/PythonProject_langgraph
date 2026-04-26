---
doc_id: codex_user_level_cross_session_durable_state_isolation_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md
status: active
doc_class: implementation_plan
---

# Codex 用户级跨会话 Durable State 隔离实施方案

## 双语对齐状态

- 完整度基准：英文 ASCII 主版与本中文对照版在主要章节结构上已经对齐。
- 英文主版：`docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md`。
- 对齐规则：两份文件保持 active 状态；如果实施语义发生变化，先以英文 ASCII 主版为 source of truth，再在同一变更中更新中文对照版。
- 当前检查结论：两份文件已经拥有相同的主要 heading 结构；本轮只补充双语对齐元数据。

> 截至 2026-04-22 的实施状态：仓库源代码已完成，用户级 mirrored helpers 已完成验证，并且已经针对真实 `D:\PythonProject_OpenClaw` 与 `D:\PythonProject_langgraph` fixture 做过复核；整个过程未改写任何被保留的 legacy durable artifact。

> 截至 2026-04-26 的当前实施边界：保留 2026-04-22 的说明作为“源码和用户级 helper 已存在”的历史证据，但不要把它理解为当前小步 rollout 已经全部完成。MR 1 到 MR 3 已完成，MR 4 是下一步 active implementation slice。

## 当前有界实施队列

这条队列用于固化 Phase 0 durable-state 只读盘点后的决策：最终生产级持久化团队方案仍然只是北极星 draft，当前继续通过 GitLab-first 小步 MR 推进 active rollout。

### 已完成切片

- MR 1，当前实施边界冻结：已由 `afdbd34` 完成 - 该提交说明当前实施线只受用户级 team mode 方案和跨会话 durable-state 隔离方案约束。
- MR 2，durable-state no-touch baseline：已由 `6f28c5f` 完成 - 该提交记录四个本地项目根目录的只读盘点，且不编辑、不移动、不删除、不激活任何 `.omx/state/` artifact。
- MR 3，状态检查入口补强：已由 `6a99d7d` 完成 - 该提交增加 `capability_readiness`，也就是按 backend 区分 `native_omx` 与 `langgraph` 的 installed、enabled、selected、ready 状态投影。

### 下一步切片：MR 4，activation selector 安全规则

MR 4 补强 `.omx/state/selectors/active.json` - 这个 repo-local active selector 文件用于判断未来会话是否可以把某个 durable backend 当作 active。selector 必须属于同一个 repository 或 worktree，不能是 released 状态，并且必须带有 session identity，才允许驱动 automatic activation。

MR 4 验收契约：

- Cross-repo selector rejection - 从其他仓库复制来的 active selector 可以 inspect，但不得在当前仓库激活 LangGraph 或 native OMX。
- Released selector rejection - 即使 `routing_eligible` 仍为 true，只要 selector 已设置 `released_at`，就不能继续当成 active。
- Backend-record dual-read only - `backend.json` 和 `codex-auto-managed-team.json` 仍然是 inspection compatibility records，但除非 scoped selector 合法，否则不能自动路由未来会话。
- Scoped-write preservation - helper 只能把 activation 写入当前仓库自己的 `.omx/state/selectors/` 目录。

### 已完成切片细节：MR 3，状态检查入口补强

MR 3 应把已经安装存在的 status surface 补强为冷启动安全的 operator entrypoint。它必须继续保持只读。

必须覆盖的源码与 helper 表面：

- `tools/install-codex-user-level-team-mode.ps1` - 仓库内用于生成用户级 helper 脚本的源脚本，保证已安装 helper 的行为可以从仓库源码复现。
- `codex-durable-state-status.ps1` - 生成到用户级目录的只读状态脚本，用于汇总当前仓库或 worktree 的 durable backend 状态。
- `tools/langgraph_durable_orchestrator/` - 仓库内 LangGraph compatibility projection 和 repo-local orchestration helper 的源码目录。
- `.omx/state/langgraph/` - 仓库本地 LangGraph runtime-state 目录，必须保持项目本地化，不能移动到用户级共享 venv。

MR 3 验收契约：

- `installed` - 报告相关能力或 helper 是否物理存在，例如生成脚本或共享 LangGraph runtime 是否已经安装。
- `enabled` - 报告用户级 policy 当前是否允许使用该能力。
- `selected` - 报告当前仓库、任务或 selector 是否为当前 flow 选择了该 backend。
- `ready` - 报告该能力在 installed、enabled、selected 之外，是否还满足 scoped state 和安全启动前置条件。
- `selected_backend` - 报告用户级 backend selector，让冷启动读者能看出全局 durable lane 当前指向 `native_omx` 还是 `langgraph`。
- `capability_readiness` - 按 backend 报告 `native_omx` 和 `langgraph` 的 readiness，并包含 `user_level_selected` 与 `repo_state_selected`，避免把全局 policy 选择和 repo-local tracked durable state 混在一起。

MR 3 实施补丁范围：

- `codex-durable-state-status.ps1` - 继续保持只读；这个生成的状态脚本可以 inspect repo-local durable state，但不得创建、编辑、删除或激活 `.omx/state/` artifact。
- `native_omx` - 基于生成 OMX helpers 的 worker-centric durable backend；MR 3 为它增加 readiness projection。
- `langgraph` - 基于共享 LangGraph runtime 与 repo-local state 的 graph-shaped durable backend；MR 3 为它增加 readiness projection。
- 测试覆盖 cold no-state、LangGraph-selected no-state，以及“用户级 selector 仍指向 LangGraph 但仓库已有 tracked native state”的情况。


MR 3 必须增加测试或 fixture，证明 checker 至少能区分这些情况：

- `D:\PythonProject_langgraph` fixture - preserved legacy LangGraph record 可以 inspect，但在没有 scoped selector 时不能作为 active routing truth。
- `D:\PythonProject_OpenClaw` fixture - active scoped LangGraph selector 强于 stale unscoped backend record，但它仍然只属于该仓库本地。
- `D:\PythonProject_CLIProxyAPI` fixture - active native OMX team state 必须保留，不能被归类为 safe cleanup residue。
- `D:\project` fixture - 普通 HUD、notification、leader-nudge 或 tmux hook state 不是 durable backend activation 证据。

### MR 4 之后的后续切片

- MR 5，user-level mirrored helper 的 source-of-truth 规则：文档化并测试“用户级 helper 是安装产物”，而仓库源码和每个仓库自己的 `.omx/state/` 目录才是权威真相。
- MR 6，自动 durable routing 接入：只有在 MR 3 到 MR 5 证明 status 与 selector 行为安全后，才把 `native_omx` 和 `langgraph` 的选择接入真实 task-flow 阈值。

### 下一步切片的明确非目标

- 不要把最终 `codex_cli_personal_production_durable_team_plan` draft 当成已经完成的能力来实施；它仍然只是北极星目标。
- 不要修改 `C:\Users\lenovo\.codex\config.toml` - 这个用户级 Codex 配置文件不属于下一步 MR 的 source-of-truth 范围。
- 不要删除 user-level skills、Vercel plugin skills、浏览器自动化 skills 或 repo-local `.omx/state/` artifacts。
- 不要把 `D:\PythonProject_OpenClaw`、`D:\PythonProject_CLIProxyAPI` 或 `D:\project` 的 durable state 合并到本仓库。
- 不要在 MR 3 启动 durable team；状态入口补强只做 inspect。


## 1. 目标

在**不修改、不删除、不重写**任何现有活跃会话或历史会话 durable artifact 的前提下，消除 repo-local durable state 对后续无关会话的意外干扰。

本方案是 implementation plan，不是运维清理手册。它关注的是如何让未来新会话不再误继承旧的 repo-local durable selector，同时保留现有会话与历史记录。

现在应把它理解成一份同时修复两层边界的共享方案：

- 一层是同一 machine / user / Codex home 下，多个 `PyCharm / Codex CLI` 项目共用的用户级控制面与 generated helper logic
- 另一层是每个仓库必须继续保留为权威面的 repo-local durable state 与 repo-local source contract

因此，本方案不只是用户级运行时修复；它也是“用户级 activation logic + 项目级 repo-local durable-state isolation”共同组成的实施方案。

## 2. 问题定义

当前用户级运行时仍然把 repository 或 worktree 的 `.omx/state` 视为有效共享 durable state 根。

这个粒度对于 inspect 足够，但对于 activation 太粗。

根因不只是 helper routing 过宽，而是两层边界被混在了一起：

- 用户级 helper logic 是跨项目共享的
- 项目级 repo-local durable state 才应该是单仓库内的权威真相

现在的问题是：

- repo-local LangGraph `backend.json` 同时承担了 inspection summary 和隐式 activation selector 两种职责
- repo-local native `auto-team-*` 目录即使是空目录，也可能继续影响自动路由判断
- 同一 repo 下的新会话可能因为旧 selector 或 residue 而继承到并不属于自己的 durable state

## 3. 已确认的仓库级故障形态

### 3.1 `D:\PythonProject_OpenClaw` 历史 legacy fixture

当前已确认：

- `.omx/state/langgraph/backend.json` 存在 tracked LangGraph backend record
- 它指向的 thread 仍停在 `freeze-plan`
- 对应 interrupt 为 `waiting_for_approval`
- 同时 `.omx/state/team` 下存在大量空的 unmanaged `auto-team-*` 目录

实际影响：

- 当前自动 durable 路由优先看到 tracked LangGraph thread，并把它当成 active durable lane
- 空的 native residue 虽然只是 safe cleanup material，但仍是潜在 native-lane blocker

### 3.2 `D:\PythonProject_langgraph`

当前已确认：

- 没有 active 的 tracked LangGraph backend record
- 但仍保留空的 unmanaged native `auto-team-*` 目录

实际影响：

- 自动 durable 路由仍可能把这些空目录识别成 unmanaged native durable residue

## 4. 不可破坏的安全规则

永久修复必须同时满足以下约束：

1. 两个仓库 legacy `.omx/state/` 下的现有文件在 immediate fix 阶段不得被编辑、移动、重命名或删除。
2. 任何活跃会话或历史会话都不得被自动接管到新控制模型里。
3. 现有历史 LangGraph threads 和 native team artifacts 必须继续可 inspect。
4. cleanup 仍然坚持 preview-first，且只允许当前已定义为 safe 的类别。
5. 新 activation 逻辑必须是 additive 且 versioned。
6. 当运行时无法安全确定 scoped activation target 时，必须 fail closed，而不是退回到 legacy shared selector。

## 5. 目标态架构

目标态应把 durable 控制面拆成三层。

在这个三层拆分之外，还必须额外固定一条边界：

- 用户级控制面可以在同一台机器上服务多个项目
- 项目级 artifact 与 activation truth 必须继续保持 repo-local
- generated user-level mirrors 可以读取或投影 repo-local state，但不能反过来取代仓库成为 source of truth

### 5.1 Artifact Plane

保留现有历史与运行态 artifact，不改变其落点：

- `.omx/state/langgraph/{threads,checkpoints,history,interrupts,store}`
- `.omx/state/team/*`

这部分继续作为 recovery truth 和 operator evidence store。

它们不再直接等同于 future session 的 activation truth。

### 5.2 Activation Plane

新增 scoped selector / lease 层，例如：

- `.omx/state/selectors/active.json`
- `.omx/state/selectors/leases/<session-scope-id>.json`

只有这一层可以声明某个 durable thread 或 team 对未来会话是 active 的。

最少字段应包括：

- `backend_family`
- `selector_id`
- `repo_root`
- `worktree_id`
- `session_scope_id`
- `leader_session_lineage`
- `acquired_at`
- `last_heartbeat_at`
- `released_at`
- `generation`
- `routing_posture`

### 5.3 Inspection Plane

保留 legacy：

- `.omx/state/langgraph/backend.json`
- `.omx/state/team/codex-auto-managed-team.json`

但仅作为只读 inspection / compatibility projection。

它们可以继续提供 inspect 或 explicit resume pointer，但不能再隐式激活无关未来会话的 durable state。

## 6. 必须发生的行为变化

### 6.1 空的 Unmanaged Native Residue

当前行为过严，因为任意最新 native team 目录都可能被视为 unmanaged residue，即使它其实是空目录。

必须改成：

- 只有**非空** unmanaged native team 目录才允许触发 `manual-inspection-required`
- 空的 unmanaged native 目录继续保留为 safe cleanup candidate
- 空目录不得继续阻塞 auto launch / reuse / switch

### 6.2 Legacy LangGraph Selector 误主导

当前行为过宽，因为只要 tracked `backend.json` 中存在 `thread_id`，就可能主导未来 lane 选择。

必须改成：

- legacy LangGraph backend record 继续可 inspect
- 只有当它被新 activation plane 明确标记为 active 或 resumable 时，才参与自动路由
- terminal、historical、unscoped 的 legacy record 不得自动把无关未来会话拖进 LangGraph

### 6.3 Dual-Read / Scoped-Write

新运行时应满足：

- legacy v1 artifact 继续可读，用于 inspect 和兼容
- 新 activation state 只通过 scoped activation plane 写入
- backend-family 选择仍然是 task-sensitive 的
- 当 scoped activation 无法安全判定时，必须 fail closed

## 7. 实施工作流

下面这些工作流必须按“双层 rollout”来理解：

- 仓库源码与仓库测试先定义 durable-state contract
- 用户级 mirrored helpers 再把这份 contract 分发到共享入口和共享 control surface

### 7.1 PowerShell Routing / Status Helpers

更新用户级 helper 逻辑，使其满足：

- 空 unmanaged native residue 不再成为 routing blocker
- legacy LangGraph backend record 不再因为 `thread_id` 存在就被视为 active
- inspectable durable state 输出能明确区分：
  - legacy preserved artifacts
  - active scoped selectors
  - safe cleanup candidates
  - protected manual residue

### 7.2 LangGraph Durable Orchestrator Projection

更新 LangGraph backend projection，使其显式暴露 routing eligibility 或 routing posture。

运行时必须能区分：

- active resumable thread
- historical preserved thread
- terminal thread
- missing 或 stale selector

### 7.3 Tests

增加或更新以下测试：

- 空 unmanaged native 目录不会触发 `manual-inspection-required`
- legacy `backend.json` 继续可 inspect，但不会自动主导无关未来会话
- 现有活跃会话在 dual-read 模式下继续可读
- 缺少 scoped selector 时会 fail closed，而不是隐式回退到 legacy activation

### 7.4 User-Level Mirrored Helpers

源码逻辑改完后，要同步刷新 `C:\Users\lenovo\.codex\bin` 下的 mirrored helper scripts，保证以下入口行为一致：

- routing policy
- durable state status
- durable state reconcile
- `omx-team-auto`
- compose 相关 helper

## 8. Rollout 计划

### Phase 0: No-Touch Baseline

在任何 rollout 前：

- 对两个仓库先做 read-only durable-state baseline
- 冻结直接对 `.omx/state` 的人工文件系统清理
- 把当前 residue 分类成：
  - preserved active
  - preserved historical
  - safe empty
  - protected manual

### Phase 1: 在 `D:\PythonProject_langgraph` 中实现源码改动

先只在 source repo 中实现 additive scoped activation 逻辑。

此阶段不做 user-level helper install。

这样做的目的，是先让项目级 source / tests 站稳，再去刷新用户级共享镜像。

### Phase 2: 用 Legacy Fixtures 做验证

针对以下 fixture 验证新逻辑：

- `OpenClaw` 的历史 legacy fixture：tracked LangGraph thread + 空 native residue
- `langgraph` 的空 native residue

验证目标是：

- 不出现 false activation
- 不发生 data mutation

### Phase 3: User-Level Helper Rollout

只有在 source logic 和 tests 都通过后，才把新 helper 逻辑发布到 user-level generated scripts。

从这一阶段开始，新会话会默认观察到新行为。

在这个阶段，用户级层做的是“分发仓库已定义好的 contract”，而不是重新定义 repo-local durable truth。

已有会话在重新进入 routing、helper evaluation 或其他配置读取边界后，也应能够观察到新的 helper 行为。

### Phase 4: New-Session Adoption

rollout 后，新会话可以立即采用 scoped activation plane。

现有 live session 会先保持自己已经持有的决策状态，直到进入安全的评估边界；但它们仍然可以在 reload、restart、explicit user routing directive 或 tracked durable-state detection 时 retrofit 到新逻辑。

### Phase 5: 后续 Cleanup Window

只有在新 activation model 稳定后，才允许：

- preview / apply 空 unmanaged native residue 的 cleanup
- 继续保留 legacy LangGraph thread artifact，除非后续另有明确批准的 archive / retire 策略

## 9. 会话影响与重启策略

本方案的目标，是让已有会话和新会话都在技术可行的范围内尽量采用最新的 user-level 配置，同时保持正在进行中的工作稳定运行。

实际规则是：

- 仅修改 `D:\PythonProject_langgraph` 源码本身，并不会自动追溯改写已在运行中的决策状态
- 当某个会话重新进入 routing、helper evaluation 或其他配置读取边界时，它应当尽量读取并采用最新的 user-level 行为
- 会话在重新进入这些评估路径时就会采用最新 activation logic，这包括 reload、restart、explicit user routing directive，或 tracked durable-state detection
- 只有当某个 live durable flow 已经越过当前决策状态的解析点、无法安全原地切换时，才需要通过 reload、restart 或 safe phase-boundary resume 来采用新逻辑

因此：

- 新会话通常应立即观察到最新的 activation logic
- 已有会话也应在下一次安全的评估边界切换到最新的 user-level 配置，而不应被表述成永久无法采用新配置
- historical sessions 继续保留并可 inspect
- 对仍在执行中的 durable flow，只有在原地切换不安全时，才应等待安全的 phase boundary 再重启

## 10. 完成判据

只有同时满足以下条件，本方案才算落地：

1. preserved legacy LangGraph backend record 不再自动主导无关未来会话。
2. 空 unmanaged native residue 不再阻塞 automatic native durable routing。
3. 现有 active / historical artifacts 继续可读、可归因、可 inspect。
4. 新的 session-scoped activation writes 是 additive 且 versioned 的。
5. 不需要直接修改 legacy `.omx/state`，也能使未来模型安全运行。
6. 仓库源码与仓库测试继续作为 activation contract 的权威面，而 user-level mirrors 只作为共享执行面和共享控制面。
7. 同一台机器上的多个 `PyCharm / Codex CLI` 项目可以共用同一套用户级 helper layer，但不会互相继承 canonical durable state。
