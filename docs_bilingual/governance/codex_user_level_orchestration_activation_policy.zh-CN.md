---
doc_id: codex_user_level_orchestration_activation_policy
lang: zh-CN
doc_class: governance
status: active
translation_of: docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md
---

# Codex 用户级 Orchestration Activation Policy

## 目的

本政策把自动 orchestration routing 固化为可执行的用户级行为，而不是要求操作者在每个提示词里重复提醒。

它适用于 native Codex expert routing、oh-my-codex / OMX durable workflow，以及本仓库和复用此用户级 runtime 的消费项目中的 LangGraph durable orchestration。

## 全局默认规则

自动协同是所有项目、所有通过用户级 workflow 启动的 Codex 会话的默认行为。操作者不需要在每个请求里重复“use experts”、“use durable_team”、“use persistent team”、“parallel” 或 “subagents”等提醒，orchestration routing 也必须生效。

对任何因范围、风险、多文档工作、多阶段 workflow、独立执行切片或 stabilization 需求而满足协同阈值的任务，会话必须自动评估并采用最小充分协同面：native experts、`native_omx`、LangGraph durable workflow 或 persistent team。

如果 native `spawn_agent` 调用被当前 platform/tool contract 阻止，必须报告 `experts=blocked:platform_subagent_invocation_constraint`，并继续使用合格 durable lane、可用时重开更窄 expert，或明确记录 main-session takeover。不得把该 blocker 改写成“用户没有要求 subagents”或任何 missing-reminder reason。

## 能力链

能力链是硬依赖：

```text
subagent_routing != off
  -> oh_my_codex 可以开启
    -> langgraph 可以开启
      -> langgraph_ready 可以让 LangGraph 成为默认 durable backend
```

如果 `subagent_routing=off`，更高 orchestration layers 不可用。以可执行规则表达，`subagent_routing=off` requires `oh_my_codex=off` and `langgraph=off`。如果 `oh_my_codex=off`，LangGraph availability 被禁用，并且 `oh_my_codex=off` requires `langgraph=off`。如果 `langgraph=on`，routing 不能为 off，且 oh-my-codex 必须为 on。

如果 `durable_orchestration_backend=langgraph`，则 `langgraph=on`、`oh_my_codex=on` 与 `subagent_routing!=off` 必须同时成立。该 dependency chain 由 `tools/check_capability_switch_chain.py` 检查；checker 会读取 user-level capability state，并可选读取 repo-local `.omx/state/langgraph/backend.json` 上下文。

当 `subagent_routing!=off`、`oh_my_codex=on`、`langgraph=on`、`langgraph_ready=true` 时，必须报告 `backend_default=langgraph` 与 `backend_ready=true`。Backend ready 不表示 durable workflow 或 persistent team 已经运行。

## Activation 触发条件

以下情况必须运行 activation check：

- 新会话首次实质性任务；
- session reload、Codex restart、resume 或 continue；
- 任务阶段变化；
- 任务从一个 slice 扩展为两个或更多 execution slices；
- 发现 `.omx` durable-state；
- user-level capability-state 变化；
- 关键路径 expert timeout 或 stall；
- 用户显式请求 `omx`、`LangGraph`、`parallel`、`experts`、`durable_team` 或 `persistent team`。

## 必填 trace 字段

Activation trace 必须包含：

```text
phase=<phase>
capability_chain=subagent:<auto|manual|off> > omx:<on|off> > langgraph:<on|off>
backend_default=<langgraph|native_omx|none>
backend_ready=<true|false>
experts=<none|analystxN|architect|writer|verifier|blocked:<reason>|...>
durable_workflow=<not_needed|candidate|selected|blocked|running>
persistent_team=<not_needed|candidate|selected|blocked|running>
main_session_escalation=<not_needed|preflight|pending_approval|granted|timed_out|blocked>
approval_timeout_risk=<none|low|medium|high|expired>
approval_receipt=<none|receipt id or repo-local artifact path>
why=<concrete reason>
```

用户可见会话表面必须保留字面标签 `Routing trace` 和 `Updated Plan`。这些标签下的解释内容可以使用中文。`Updated Plan` 必须继续是复选框/状态清单表面，不得被替换为纯自然语言段落。保存版结构化 evidence 继续保留 canonical field name、threshold token 和 blocker token，以保持 checker 兼容。

Main-session escalation visibility 必须显式可见：在任何 OMX、LangGraph、durable-worker 或 shell flow 等待主会话审批前，trace 必须暴露 `main_session_escalation`、`approval_timeout_risk` 和 `approval_receipt`。`main_session_escalation` 的状态为 `not_needed`、`preflight`、`pending_approval`、`granted`、`timed_out` 或 `blocked`；`approval_timeout_risk` 的状态为 `none`、`low`、`medium`、`high` 或 `expired`；`approval_receipt` 在无需审批时为 `none`，否则必须指向 repo-local receipt、interrupt、checkpoint 或 pending-approval artifact path。Worker context 必须收到同一个 receipt 或 blocked state，不得把 approval wait 隐藏在 main session 之外。

不得使用“用户没有要求并行”或“用户没有要求子代理”等 missing-reminder reasons。必须用任务阶段、范围、阈值、blocker 或 main-session takeover 作为原因。

显式 `omx` 与 `LangGraph` 请求是当前 task flow 的 hard routing directives。若 capability chain、preflight 与 task thresholds 均满足，trace 必须把所选 lane 报告为 `selected` 或 `running`，不得停留在 explanation-only mode。若请求 lane 未被采用，trace 必须报告具名 blocker 或未满足阈值，例如 `blocked:backend_not_ready`、`blocked:preflight_failed`、`blocked:helper_missing`、`blocked:write_ownership_conflict` 或 `threshold_not_met:no_frozen_plan`。trace 不得把显式 directive 描述为 optional preference。已保存的 hard-directive adoption evidence 由 `tools/check_role_routing_directive_evidence.py` 检查。

## Expert 与 durable 证据规则

Expert timeout、stalled workers、upstream pacing 或 abandoned lanes 都不是 verification evidence。Provider pacing 是 backpressure，不是禁用 orchestration 的理由。Completed experts 在结果被吸收后必须关闭，除非用户显式要求保留线程，或计划记录了 preserved-thread reason。Waits 必须使用 bounded windows 和可见 total bound；stalled 或 quiet experts 必须 inspect、redirect、respawn、durable handoff，或由 main-session takeover。 Structured lifecycle evidence must keep wait, timeout, result, absorption, closure, and handling events tied to the same `agent_id`; timeout requires prior bounded wait and a handling event for that agent, two quiet `progress_check` events require handling, and `provider_pacing` must be classified as `backpressure` without disabling LangGraph, OMX, subagents, experts, or orchestration.

Final report 必须显式标注证据来源，例如：

- `expert returned and absorbed`；
- `expert timed out; not used as evidence`；
- `main session took over verification`；
- `durable_team blocked by <reason>`；
- `backend_default=langgraph, backend_ready=true` - 记录默认 durable backend 与 ready 证据。

保存的 activation trace evidence 可用 `tools/check_orchestration_trace_evidence.py` 检查。该 checker 校验必填 trace 字段、capability-chain dependency 一致性、backend readiness 语义、durable workflow 与 persistent-team 词汇、禁止的 missing-reminder reasons、expert timeout 标签，以及 `why` 中的 durable-team threshold evidence。接受本地 transcript 片段、run summary 或其他保存版 trace evidence 前，应先运行该 checker。Expert lifecycle、wait、liveness 与 provider pacing evidence 可用 `tools/check_expert_lifecycle_wait_pacing_evidence.py` 检查；该 checker 强制 completed-agent closure 或 explicit preservation、fresh-agent follow-up、bounded wait windows、stall handling actions，以及 upstream pacing 只能作为 backpressure，不能作为禁用 orchestration 的理由。

Prompt-independent collaboration parity、cold-start read-order evidence、durable/persistent evidenceguard records、expert lifecycle audit events 与 LangGraph state release 由 `tools/check_orchestration_collaboration_evidenceguard.py` 统一检查。该 checker 使用 fixture pairs 证明有无协作短语的等价 prompt 会得到相同 routing decision；缺少 active selector、manifest 或 thread state、heartbeat、close、leader absorption evidence 时拒绝 durable/persistent team 声明；任务已完成但 LangGraph 仍残留 stale `running` 时也会失败，除非写入 `completed_at`、`final_phase`、`result_summary` 与 `released_by`。结构化 LangGraph state-release evidence 也可由 `tools/check_durable_artifact_state_surfaces.py` 接受：completed thread state 不得保留 `running` 等 active statuses，released 或 closed state 必须包含 `released_at` 与 `released_by`，backend-family handoff 必须包含 `handoff_at`、`handoff_target` 与 `reason`，之后另一个 durable backend family 才可被视为安全 continuation surface。

## Team 阈值规则

不要在 startup、read-only inventory 或 plan-freeze 工作中自动启动 durable teams。

Durable team selection 需要 frozen plan 加至少两个 mostly independent execution slices，或 stabilize 阶段存在具名 blocking issues。若选择 team，使用 `omx-team-auto.ps1` 等已批准 automatic helper；不得只凭 compatibility records 自动接管 unmanaged teams。

在 startup 或 first activation 时，trace 必须说明哪个 durable-team threshold 未满足，例如 `threshold_not_met:no_frozen_plan` 或 `threshold_not_met:single_execution_slice`。若 durable lane 被 blocked，trace 必须说明具名 blocker 或未满足阈值。若 durable team 被 selected 或 running，trace 必须说明 concrete threshold triggered，建议使用稳定 ASCII token，例如 `triggered_threshold:frozen_plan_with_2+_independent_slices`，或使用等价的 frozen-plan / stabilize blocking-issues 语言。保存版 trace-evidence validator 会在 `why` 字段强制检查这些标签，避免 “small task” 或 “using team now” 这类模糊理由通过。

## Surface 边界

Native Codex subagents、workflow skills、plugin-provided skills、profile helpers、durable workers 与 LangGraph nodes 是不同 execution surfaces。当前 main Codex CLI session 仍是 leader，负责 activation checks、role selection、fan-in、evidence labeling、final integration 与 release recommendations。

## Advanced routing enforcement boundaries

Native agents, skills, and profile helpers are distinct orchestration surfaces。Native reusable role definitions live in user-level or repo-local agents directories；Native Codex subagents、workflow skills、plugin-provided skills、plugin modules、profile helpers、durable workers 与 LangGraph nodes 是 separate surfaces。Skills are loaded from installed `SKILL.md` files，并路由 procedural instructions，但它们本身不算 expert evidence。Skill invocation, plugin profile loading, or profile helper hard-load/soft-load is not expert evidence。Profile helper 的 hard-load 或 soft-load 只改变可见 instructions；它不会启动 durable workers，也不满足 persistent-team thresholds。Completed expert 被吸收并关闭后，如需 follow-up work，默认 spawn fresh agent，除非用户显式要求保留线程，或计划记录了 preserved-thread reason。该边界的保存版 evidence 由 `tools/check_agent_skill_profile_surface_boundaries.py` 与 `tools/check_expert_lifecycle_wait_pacing_evidence.py` 进行 checker-backed 校验。

Smallest-sufficient role selection 是强制规则。只有触发条件存在且输出能实质推进当前阶段时，才添加 expert role。bounded multi-face research 仍采用 analyst-fanout-first，首轮使用同质 `analystxN`；只有在 analyst fan-in 显示 architecture、execution-ordering 或 document-finalization work 后，才升级到 `architect`、`planner` 或 `writer`。已保存的 role-routing evidence 由 `tools/check_role_routing_directive_evidence.py` 检查。

Native Codex subagents、workflow skills、plugin-provided skills、profile helpers、durable workers 与 LangGraph nodes 是 separate surfaces。skills 不是 native subagents：skills 从 `SKILL.md` 文件加载并路由 procedural instructions，但它们本身不算 expert evidence。Profile helper 的 hard-load 或 soft-load 只改变可见 instructions；它不会启动 durable workers，也不满足 persistent-team thresholds。Completed expert 被吸收并关闭后，如需 follow-up work，默认 spawn fresh agent，除非用户显式要求保留线程，或计划记录了 preserved-thread reason。该边界的保存版 evidence 由 `tools/check_expert_lifecycle_wait_pacing_evidence.py` 进行 checker-backed 校验。

Standalone native-agent TOMLs 与 user-level agents directory 或 repo-local `.codex/agents/` 中的每个 custom agent TOML 必须通过 `tools/check_custom_agent_toml_schema.py`：每个存在的 TOML 必须可解析，并定义非空 top-level `name`、`description` 与 `developer_instructions`。Native-agent TOML schema is checked separately from skill `SKILL.md` validation，以保持 native agents、skills 与 plugin profiles 的 surface 边界。

current main Codex CLI session remains the leader。它负责 activation checks、role selection、worker brief quality、fan-in、evidence labeling、final integration 与 release recommendations。不得用 separate persistent leader pane 替代它。Orchestration adoption 的作用域是当前 task flow，而不是仓库新旧。

Leader session and task-flow scope evidence 由 `tools/check_leader_session_scope_evidence.py` 检查。该 checker 要求 evidence 显示 current main Codex CLI session remains the leader，并负责 leader-owned fan-in、evidence labeling、final integration 与 release recommendations；它会拒绝 separate persistent leader pane 替代主会话；它把 startup non-autolaunch 作为强制边界，除非 startup or first activation 引用具体未满足或已触发的 durable-team threshold；它要求 task-flow scoped adoption，而不是基于仓库新旧 routing；并要求 legacy resumed sessions are compatibility-scoped，不能覆盖 current repository governance 或 capability-chain policy。reload, restart, resume, continue 与 durable-state detection evidence 必须显示 activation check rerun。

### Session replay context filtering

Session replay context filtering is the required boundary before a resumed legacy session, compacted transcript, or replayed thread fragment can re-enter prompts as current authority. Replay inputs include assistant-visible transcript messages, tool/function output, raw startup-summary copies, and old runtime workaround text recovered from `/resume` context. Filtered outputs must separate accepted assistant-visible context, filtered replay fragments, and blocked authority candidates.

The filter must drop or block stale canary text, mojibake, raw startup-summary copies, and stale MCP assumptions before any prompt-authority handoff. tool/function output is diagnostic evidence only and must not become current authority. Current authority remains `AGENTS.md`, the UTF-8 startup summary pair, and current repository governance documents. For one old thread with an MCP startup problem, use a per-invocation override such as `-c "mcp_servers.omx_code_intel.enabled=false"`; that workaround is one-launch compatibility handling and must not become a permanent edit to user-level `config.toml` or a global disablement of `omx_*` MCP servers.

Saved replay-filtering evidence is checked by `tools/session_replay_context_filtering.py`. The checker reports `accepted_context_items`, `filtered_context_items`, `blocked_authority_items`, and `replay_diagnostics`, and fails closed when stale replay content would re-enter prompts as current authority.

Native Codex remains the base layer。oh-my-codex、native_omx、skills、profile helpers 与 LangGraph 是 additive workflow 或 durable-state layers，不是 Codex replacements。Effective lane choice 基于 task fit：worker-centric durable execution、worktree isolation、mailbox flow 或 direct worker lifecycle control 优先使用 `native_omx`；graph-shaped multi-phase execution、checkpoint-driven recovery、interrupt/resume approval gates、frozen briefs 或 persisted survivor queues 优先使用 LangGraph。每个 durable task 同一时间只使用 one backend family，backend-family switching 需要 explicit close or handoff。已保存的 lane-fit evidence 由 `tools/check_effective_lane_fit_evidence.py` 检查；它要求 native_omx worker-centric fit、LangGraph graph-shaped fit、default-backend-not-enough evidence，以及 backend-family switching 前的 explicit close/handoff。

Delegation 必须是 concrete、bounded、self-contained sidecar work，并且 materially advances 主任务。leader 必须在委派前识别 immediate critical-path local work；当下一步 leader action 依赖结果时，不要把 urgent blocking work 委派出去；避免 duplicate work；experts 运行时继续 meaningful non-overlapping leader work；并且 sparingly 使用 `wait_agent`。代码修改 worker brief 必须包含 file/module ownership 或 disjoint write sets，告知 worker 他们不是代码库中唯一执行者、不得 revert 其他 edits，并要求 final answer 列出 changed paths。已保存的 delegation 与 wait evidence 由 `tools/check_delegation_wait_discipline_evidence.py` 检查。
Fan-out and write-heavy parallel execution are bounded and ownership-isolated. Native subagent fan-out must use leader-side spawning with leader-owned fan-in and stay within `agents.max_threads=6` and `agents.max_depth=1` unless an explicit override, reason, and approval are recorded. Raw Codex does not auto-spawn specialist roles. Prefer parallel fan-out for read-heavy, bounded, independent work. Write-heavy parallel execution requires file/module ownership, disjoint write sets, hotspot serialization or a no-shared-hotspot statement, leader-owned final integration, not alone in the codebase worker instructions, must not revert or overwrite instructions, and changed-path reporting. Saved fan-out/write-ownership evidence is checked by `tools/check_fanout_write_ownership_evidence.py`.

read-only exploration 只用于 specific codebase questions、symbol mapping 与 file discovery。当 implementation patch 清晰且安全时，它不得替代 bounded code-changing worker task。需要 graph phases、checkpoint gates、frozen briefs、survivor queues 或 tracked LangGraph thread state 时，必须使用 LangGraph entrypoints 与 repo-local `.omx/state/langgraph/` state。`.omx/state/selectors/active.json` 仍是 automatic durable-team adoption 的 active selector authority；compatibility records 只能作为 context。durable artifacts、frozen briefs 与 survivor queues 必须写入 repo-local state 或 documented artifact paths，不能只存在于 transient chat context。已保存的 durable artifact/state-surface evidence 由 `tools/check_durable_artifact_state_surfaces.py` 检查。

Open-ended work 必须保持 research 与 implementation 角色分离。Research fan-in 必须先冻结为 frozen implementation brief，包含 scope、non-goals、acceptance evidence、ownership boundaries 与 unresolved risks，然后才能开始 implementation。`bug-finder`、`bug-rebutter` 与 `bug-judge` 是 burst、read-only、leader-side roles；剩余候选必须持久化为 adversarial-review survivor queue，交给 debugger-lane follow-up，而不是让 bug triad 成为 persistent workers。LangGraph、AutoGen 与 CrewAI 是 general programmable orchestration runtimes，不是 native Codex-subagent equivalents。

## Script control

本政策由 `tools/check_orchestration_activation_policy.py`、`tools/check_capability_switch_chain.py`、保存版 trace evidence validator `tools/check_orchestration_trace_evidence.py`、role/directive evidence checker `tools/check_role_routing_directive_evidence.py`、leader/session scope evidence checker `tools/check_leader_session_scope_evidence.py`、expert lifecycle/wait/pacing evidence checker `tools/check_expert_lifecycle_wait_pacing_evidence.py`、delegation/wait discipline evidence checker `tools/check_delegation_wait_discipline_evidence.py`、durable artifact/state-surface evidence checker `tools/check_durable_artifact_state_surfaces.py`、repo-local selector ownership checker `tools/check_repo_local_selector_ownership.py`、agent/skill/profile surface checker `tools/check_agent_skill_profile_surface_boundaries.py`、effective lane-fit evidence checker `tools/check_effective_lane_fit_evidence.py` 与 native custom-agent TOML schema checker `tools/check_custom_agent_toml_schema.py` 支撑，并登记在 `tools/safety_rule_script_backing_registry.json`。仅靠提示词提醒不足以保护这个边界。

## Active selector refresh reporting

自动 durable adoption 的 repo-local selector authority 是 `.omx/state/selectors/active.json`。`.omx/state/langgraph/backend.json` 与 `.omx/state/team/codex-auto-managed-team.json` 等 compatibility records 只能作为 inspection context。`tools/check_repo_local_selector_ownership.py` 会验证 active selector 与 selector leases 属于当前 repository/worktree root，对 cross-repository selector adoption fail closed，并把 stale selectors 视为 no-auto-adoption，除非先刷新。若 LangGraph 已 selected 且 ready，但 active selector 缺失，status helpers 必须报告 selector refresh gap，而不是把 LangGraph 当作 unavailable，也不能静默 downgrade 到 `native_omx`。
