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

> 截至 2026-05-02 的当前实施边界：保留 2026-04-22 的说明作为“源码和用户级 helper 已存在”的历史证据，但不要把它理解为最终 production-grade persistent team draft 已完成。MR 1 到 MR 5 已完成。MR 6 readiness review 现在作为 status-reconciliation slice 完成：automatic durable routing hookup 已经存在于更早的 P5 team-mode surfaces 中，所以本队列不得再开启重复 runtime implementation work。

## 当前有界实施队列

这条队列用于固化 Phase 0 durable-state 只读盘点后的决策：最终生产级持久化团队方案仍然只是北极星 draft，当前继续通过 GitLab-first 小步 MR 推进 active rollout。

### 已完成切片

- MR 1，当前实施边界冻结：已由 `afdbd34` 完成 - 该提交说明当前实施线只受用户级 team mode 方案和跨会话 durable-state 隔离方案约束。
- MR 2，durable-state no-touch baseline：已由 `6f28c5f` 完成 - 该提交记录四个本地项目根目录的只读盘点，且不编辑、不移动、不删除、不激活任何 `.omx/state/` artifact。
- MR 3，状态检查入口补强：已由 `6a99d7d` 完成 - 该提交增加 `capability_readiness`，也就是按 backend 区分 `native_omx` 与 `langgraph` 的 installed、enabled、selected、ready 状态投影。
- MR 4，activation selector 安全规则：已由 `b303000` 完成 - 该提交补强 scoped selector 校验，让 stale 或跨仓库 durable records 仍可 inspect，但不能驱动 automatic activation。
- MR 5，helper mirror source-of-truth 规则：已由 `e1b3544` 完成，并由 `e39fb21` 做 publication closeout - 该切片文档化并测试 generated user-level helper mirrors 是安装产物，而仓库源码以及每个消费项目自己的 `.omx/state/` 树仍然是权威来源。
- MR 6，automatic durable routing readiness review：由本次 status-reconciliation slice 完成 - 该复核确认 `codex-user-level-team-mode-automatic-team-routing` 是稳定的 automatic-routing spec，`omx-team-auto.ps1` 是生成的 user-level automatic durable-team helper，`test/install-codex-user-level-team-mode.test.ps1` 是覆盖 effective lane selection、selector safety、empty residue handling，以及 native_omx / LangGraph routing evidence 的测试套件。

### 已完成切片细节：MR 4，activation selector 安全规则

MR 4 补强 `.omx/state/selectors/active.json` - 这个 repo-local active selector 文件用于判断未来会话是否可以把某个 durable backend 当作 active。selector 必须属于同一个 repository 或 worktree，不能是 released 状态，并且必须带有 session identity，才允许驱动 automatic activation。

MR 4 验收契约现在已经纳入已实现 baseline：

- Cross-repo selector rejection - 从其他仓库复制来的 active selector 可以 inspect，但不得在当前仓库激活 LangGraph 或 native OMX。
- Released selector rejection - 即使 `routing_eligible` 仍为 true，只要 selector 已设置 `released_at`，就不能继续当成 active。
- Backend-record dual-read only - `backend.json` 和 `codex-auto-managed-team.json` 仍然是 inspection compatibility records，但除非 scoped selector 合法，否则不能自动路由未来会话。
- Scoped-write preservation - helper 只能把 activation 写入当前仓库自己的 `.omx/state/selectors/` 目录。

### 已完成切片细节：MR 5，user-level mirrored helper 的 source-of-truth 规则

MR 5 已文档化并测试：用户级 mirrored helpers 是生成出来的安装产物，不是 durable truth 的权威来源。仓库源码仍在本仓库内，每个消费项目自己的 `.omx/state/` 目录仍是它自己的本地 durable truth。

MR 5 验收契约现在已经纳入已实现 baseline：

- Helper mirror provenance - 生成到用户级的 helpers 必须通过 metadata 或文档说明，让冷启动读者能把行为追溯回仓库源码。
- Repo-local truth preservation - 生成 helper 可以 inspect 当前仓库，但不得把 `D:\PythonProject_langgraph` 当成其他项目的全局 durable state root。
- Consumer-project isolation - `D:\PythonProject_OpenClaw`、`D:\PythonProject_CLIProxyAPI`、`D:\project` 和未来项目可以复用用户级 runtime 与 policy，但它们的 repo-local `.omx/state/` 目录必须保持独立。
- Install-artifact wording - docs 与生成 helper 表面必须把用户级副本称为安装产物，而不是 primary source of truth。

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

### 已完成切片细节：MR 6，automatic durable routing readiness review

MR 6 是本有界 durable-state queue 的 readiness-review closeout，不是新的 runtime patch。复核确认真正的 automatic durable routing hookup 已经存在于 team-mode implementation line：

- `openspec/specs/codex-user-level-team-mode-automatic-team-routing/spec.md` - automatic durable-team routing 行为的稳定 OpenSpec requirement 文件。
- `tools/install-codex-user-level-team-mode.ps1` - 生成 user-level helper scripts 的仓库源码脚本，其中包括 `omx-team-auto.ps1`。
- `omx-team-auto.ps1` - 生成的 user-level helper；它会规划 native_omx 或 LangGraph durable routing actions，并且只有带 `-Apply` 时才执行。
- `test/install-codex-user-level-team-mode.test.ps1` - PowerShell regression suite；它验证 effective lane selection、selector rejection、empty residue handling、native_omx launch/reuse/switch/shutdown，以及 LangGraph graph-signal selection。
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - active team-mode plan，已经把 P5 automatic durable-team routing 标成 implemented current state。

MR 6 验收契约现在已经纳入已实现 baseline：

- No duplicate hookup - 本队列不得再开启另一个 runtime implementation 来重复实现已有的 `omx-team-auto.ps1` helper 行为。
- Readiness before runtime exercise - 任何未来 live use 都必须先明确 target repository、phase、task 和 operator consent boundary。
- No startup launch - 即使 automatic durable routing 可用，startup classification 也不得自动启动 durable team。
- Backend-family clarity - worker-centric flows 默认仍是 native_omx；graph-shaped checkpoint、approval-gate、frozen-brief 或 survivor-queue flows 才可以选择 LangGraph。

### MR 6 readiness review 之后的下一步 decision point

- Future live smoke 或 adoption gate：只有当用户明确要求 exercise runtime behavior 时，才另开一个 reviewed change，在受控 target repository 中运行 `omx-team-auto.ps1` 并记录证据；不要把这个 smoke 与最终 production-grade persistent team draft 混为一谈。

### Release 0.6 durable routing smoke/adoption gate

MR 6 readiness review 之后，下一条 active release slice 是 `R0.6 Durable Routing Smoke Gate`。

`R0.6 Durable Routing Smoke Gate` 是给未来 runtime exercise 使用的文档和验证 gate。它不能被理解成直接启动 durable team 的授权。

未来 smoke 或 adoption-gate change 必须声明：

- `target_repository` —— 目标仓库根目录，用来说明本次评估哪个仓库的 repo-local durable truth。
- `phase` —— 项目阶段，用来驱动 automatic routing thresholds。
- `task` —— 具体 validation question 或 work item。
- `operator_consent_boundary` —— 操作员授权边界，用来约束 `-Apply`、`.omx/state/` 写入、durable-team launch、shutdown 或其他 mutating actions。

这个 release slice 的默认边界：

- 先使用 read-only status 和 planning surfaces。
- 不修改 `.omx/state/`；`.omx/state/` 是 repo-local durable-state 目录。
- 不执行 `omx-team-auto.ps1 -Apply`；`-Apply` 是执行 planned durable action 的 helper 开关。
- 不把 draft production durable-team plan 提升为 active implementation。

更细的 staged next-decision path：

- `R0.6.0 Gate Template` —— 立即下一步，创建 reusable smoke/adoption gate template，在它落地前不运行任何 routing 命令。
- `R0.6.1 Gate Field Checker` —— 立即下一步，增加 checker-backed enforcement，要求 future gates 声明 `target_repository`、`phase`、`task` 和 `operator_consent_boundary`。
- `R0.6.2 Read-Only State Sampling` —— 后续只读切片，用 read-only state surfaces 检查一个 repository。
- `R0.6.3 Dry-Run Routing Decision` —— 后续 dry-run 切片，解释 routing decision，但不执行 `-Apply`。
- `R0.6.4 Expected-Result Fixture` —— 后续 fixture 切片，把预期 decision 固化成 regression fixture。
- `R0.6.5 Cross-Project Read-Only Review` —— 后续跨项目切片，在 consumer repository 上重复只读复核。
- `R0.7 Native OMX Adoption MVP` —— future controlled native_omx adoption，必须等 R0.6 evidence 存在后再进入。
- `R0.8 LangGraph Adoption MVP` —— future controlled langgraph adoption，只面向 graph-shaped tasks。
- `R0.9 Lane Arbitration` —— future conflict 和 selection rules，用于多个 durable lanes 同时 enabled 的场景。
- `R1.0 Personal Durable Team MVP` —— future 单用户、多项目 MVP。
- `R1.1 Multi-Project Consumer Rollout` —— future consumer repositories rollout，但不共享 durable truth。
- `R1.2 Operational Hardening` —— future cleanup、logging、MCP、config sentinel 和 rollback hardening。
- `R2.0 Production Durable Team` —— future production target，不是当前实现。

### 下一步 decision point 的明确非目标

- 不要把最终 `codex_cli_personal_production_durable_team_plan` draft 当成已经完成的能力来实施；它仍然只是北极星目标。
- 不要修改 `C:\Users\lenovo\.codex\config.toml` - 这个用户级 Codex 配置文件不属于下一步 MR 的 source-of-truth 范围。
- 不要删除 user-level skills、Vercel plugin skills、浏览器自动化 skills 或 repo-local `.omx/state/` artifacts。
- 不要把 `D:\PythonProject_OpenClaw`、`D:\PythonProject_CLIProxyAPI` 或 `D:\project` 的 durable state 合并到本仓库。
- 不要在本次 MR 6 readiness-review closeout 中启动 durable team；live durable-team exercise 需要单独显式的 smoke 或 adoption-gate change。
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

安全规则 enforcement 不能只靠提示词。凡是会影响 activation、cleanup、scoped writes、cross-project reads 或 publication 的 durable-state isolation 规则，都必须登记到 `tools/safety_rule_script_backing_registry.json`，并且必须有 executable script control，或者明确登记为 tracked gap。总 checker 是 `tools/check_safety_rule_script_backing.py`，并由 `tools/run_openspec_guard.py` 纳入仓库 guard。

## 5. 目标态架构

目标态应把 durable 控制面拆成三层。

在这个三层拆分之外，还必须额外固定一条边界：

- 用户级控制面可以在同一台机器上服务多个项目
- 项目级 artifact 与 activation truth 必须继续保持 repo-local
- generated user-level mirrors 可以读取或投影 repo-local state，但不能反过来取代仓库成为 source of truth

### 5.1 Artifact Plane

保留现有历史与运行态 artifact，不改变其落点：

- `.omx/state/langgraph/{threads,checkpoints,history,interrupts,store}` - 保存 thread、checkpoint、history、interrupt 与 store 数据的 repo-local LangGraph durable-state 子目录。
- `.omx/state/team/*` - repo-local native OMX team-state 目录树。

这部分继续作为 recovery truth 和 operator evidence store。

它们不再直接等同于 future session 的 activation truth。

### 5.2 Activation Plane

新增 scoped selector / lease 层，例如：

- `.omx/state/selectors/active.json` - 记录当前 selected durable backend family 的 repo-local selector 文件。
- `.omx/state/selectors/leases/<session-scope-id>.json` - 防止 cross-session state confusion 的每会话 selector lease 文件。

只有这一层可以声明某个 durable thread 或 team 对未来会话是 active 的。

最少字段应包括：

- `backend_family` - 标记 native_omx 或 langgraph 等 durable backend family 的 selector 字段。
- `selector_id` - 给 active selection record 提供稳定标识的 selector 字段。
- `repo_root` - 把 selection 绑定到单一 repository root 的 selector 字段。
- `worktree_id` - 区分不同 worktree 的 selector 字段。
- `session_scope_id` - 把 lease 约束到单一 live session 的 selector 字段。
- `leader_session_lineage` - 记录 main leader session lineage 的 selector 字段。
- `acquired_at` - 记录 lease 获取时间的 selector timestamp。
- `last_heartbeat_at` - 记录最近一次 lease heartbeat 的 selector timestamp。
- `released_at` - 记录 lease 释放时间的 selector timestamp。
- `generation` - 用于发现 stale 或 superseded records 的 selector counter。
- `routing_posture` - 记录 durable execution 当前 routing posture 的 selector 字段。

### 5.3 Inspection Plane

保留 legacy：

- `.omx/state/langgraph/backend.json` - 用于 backend state inspection 的 LangGraph compatibility record。
- `.omx/state/team/codex-auto-managed-team.json` - 用于 auto-managed team state inspection 的 native OMX compatibility record。

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
- `omx-team-auto` - 启动 workers 前读取 repo-local active selector 的 automatic durable-team launcher。
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

## 11. 共享模型服务不共享 Durable State

共享本地模型服务只允许作为 provider service 使用。它不改变 durable-state isolation。

`D:\PythonProject_langgraph\.local\models\` 是用于共享 llama 或 GGUF 文件的被忽略本地模型资产目录。它不是 repo-local durable-state directory。

`CODEX_LOCAL_MODEL_ROOT` 是共享模型根目录环境变量。它可以帮助消费方仓库发现模型文件或 endpoints，但不得指向 `.omx/state/`，也不得成为 activation truth。

消费方仓库可以调用 `local-judge-qwen` 或 `local-embed-jina` 这类 provider profiles，但每个仓库仍然拥有自己的 `.omx/state/`、OpenSpec artifacts、approval state、recovery evidence、business state 与 logs。
