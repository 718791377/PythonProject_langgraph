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

它适用于 native Codex expert routing、oh-my-codex / OMX durable workflow，以及本仓库和消费项目复用的 LangGraph durable orchestration。

## 能力链

能力链是硬依赖：

```text
subagent_routing != off
  -> oh_my_codex 可以开启
    -> langgraph 可以开启
      -> langgraph_ready 可以让 LangGraph 成为默认 durable backend
```

如果 `subagent_routing=off`，更高 orchestration layers 不可用。如果 `oh_my_codex=off`，LangGraph availability 被禁用。如果 `langgraph=on`，routing 不能为 off，且 oh-my-codex 必须为 on。

当 `subagent_routing!=off`、`oh_my_codex=on`、`langgraph=on`、`langgraph_ready=true` 时，必须报告 `backend_default=langgraph` 与 `backend_ready=true`。Backend ready 不表示 durable workflow 或 persistent team 已经运行。

## Activation 触发条件

以下情况必须重新做 activation check：

- 新会话首次实质性任务；
- session reload、Codex restart、resume 或 continue；
- 任务阶段变化；
- 任务从一个切片扩展为两个或更多 execution slices；
- 发现 `.omx` durable state；
- user-level capability state 变化；
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
why=<concrete reason>
```

不得使用“用户没有要求并行”或“用户没有要求子代理”这类缺少提醒的理由。必须用任务阶段、范围、阈值、blocker 或主会话接管来解释。

显式 `omx` 与 `LangGraph` 请求是当前 task flow 的 hard routing directives。若 capability chain、preflight 与 task thresholds 均满足，trace 必须把请求 lane 报告为 `selected` 或 `running`，不得停留在 explanation-only mode。若请求 lane 未被采用，trace 必须报告具名 blocker 或未满足阈值，例如 `blocked:backend_not_ready`、`blocked:preflight_failed`、`blocked:helper_missing`、`blocked:write_ownership_conflict` 或 `threshold_not_met:no_frozen_plan`。trace 不得把显式 directive 描述为 optional preference。

## Expert 与 durable 证据规则

Expert timeout、worker stall、upstream pacing 或 abandoned lane 都不是验证证据。

Final report 必须显式标注证据来源，例如：

- `expert returned and absorbed`；
- `expert timed out; not used as evidence`；
- `main session took over verification`；
- `durable_team blocked by <reason>`；
- `backend_default=langgraph, backend_ready=true` - 记录默认 durable backend 与 ready 证据。

保存的 activation trace 证据可用 `tools/check_orchestration_trace_evidence.py` 检查。接受本地 transcript 片段、run summary 或其他保存的 trace 证据前，应先运行该 checker。

## Team 阈值规则

不要在 startup、只读 inventory 或 plan-freeze 工作中自动启动 durable team。

Durable team selection 需要 frozen plan 加至少两个基本独立的 execution slices，或 stabilize 阶段存在具名 blocking issues。若选择 team，使用 `omx-team-auto.ps1` 等已批准自动 helper；不得只凭 compatibility records 自动接管 unmanaged teams。

在 startup 或 first activation 时，trace 必须说明哪个 durable-team 阈值未满足，例如 `threshold_not_met:no_frozen_plan` 或 `threshold_not_met:single_execution_slice`。若 durable team 被选择，trace 必须说明触发选择的具体阈值，并使用稳定 ASCII token `triggered_threshold` 表示该选择来自 frozen plan 加两个或更多独立 execution slices，或 stabilize 阶段存在具名 blocking issues。

## Surface 边界

Native Codex subagents、workflow skills、plugin-provided skills、profile helpers、durable workers 与 LangGraph nodes 是不同 execution surfaces。当前 main Codex CLI session 仍是 leader，负责 activation checks、role selection、fan-in、evidence labeling、final integration 与 release recommendations。

## 脚本控制

本政策由 `tools/check_orchestration_activation_policy.py` 与保存版 trace 证据 validator `tools/check_orchestration_trace_evidence.py` 支撑，并登记在 `tools/safety_rule_script_backing_registry.json`。仅靠提示词提醒不足以保护这个边界。


## Advanced routing enforcement boundaries??????????

Smallest-sufficient role selection ??????????????????????????????? expert role?bounded multi-face research ?? analyst-fanout-first??????? `analystxN`???? analyst fan-in ?? architecture?execution-ordering ? document-finalization work ?????? `architect`?`planner` ? `writer`?

Native Codex subagents?workflow skills?plugin-provided skills?profile helpers?durable workers ? LangGraph nodes ??? surface?skills ?? native subagents?skills ? `SKILL.md` ????? procedural instructions???????? expert evidence?profile helper ? hard-load ? soft-load ????? instructions????? durable workers????? persistent-team thresholds?completed expert ?????????? follow-up work?? spawn fresh agent??????????? thread?????? preserved-thread reason?

current main Codex CLI session ?? leader??? activation checks?role selection?worker brief quality?fan-in?evidence labeling?final integration ? release recommendations???? separate persistent leader pane ??????orchestration adoption ???? task flow?????????

Native Codex ? base layer?oh-my-codex?native_omx?skills?profile helpers ? LangGraph ? additive workflow ? durable-state layers??? Codex replacement?effective lane choice ? task fit ???worker-centric durable execution?worktree isolation?mailbox flow ? direct worker lifecycle control ?? `native_omx`?graph-shaped multi-phase execution?checkpoint-driven recovery?interrupt/resume approval gates?frozen briefs ? persisted survivor queues ?? LangGraph??? durable task ????? one backend family?backend-family switching ???? close ? handoff?

Delegation ??? concrete?bounded?self-contained sidecar work??? materially advances ????leader ??????? immediate critical-path local work????? leader action ????????? urgent blocking work ????????? duplicate work?experts ????? meaningful non-overlapping leader work??? sparingly ?? `wait_agent`?

read-only exploration ?? specific codebase questions?symbol mapping ? file discovery?? bounded code-changing worker task ?????????? read-only exploration ?? implementation patch????? graph phases?checkpoint gates?frozen briefs?survivor queues ? tracked LangGraph thread state ?????? LangGraph entrypoints ? repo-local `.omx/state/langgraph/` state?durable artifacts?frozen briefs ? survivor queues ???? repo-local state ? documented artifact paths?????? transient chat context?

????????? research ? implementation ???research fan-in ??????? frozen implementation brief??? scope?non-goals?acceptance evidence?ownership boundaries ? unresolved risks???? implementation?`bug-finder`?`bug-rebutter` ? `bug-judge` ? burst?read-only?leader-side roles?remaining candidates ???? adversarial-review survivor queue ???? debugger-lane follow-up????? bug triad ?? persistent workers?LangGraph?AutoGen ? CrewAI ? general programmable orchestration runtimes??? native Codex-subagent equivalents?

## Active selector refresh reporting

自动 durable adoption 的 repo-local selector authority 是 `.omx/state/selectors/active.json`。`.omx/state/langgraph/backend.json` 与 `.omx/state/team/codex-auto-managed-team.json` 等 compatibility records 只能作为 inspection context。若 LangGraph 已 selected 且 ready，但 active selector 缺失，status helpers 必须报告 selector refresh gap，而不是把 LangGraph 当作 unavailable，也不能静默 downgrade 到 `native_omx`。
