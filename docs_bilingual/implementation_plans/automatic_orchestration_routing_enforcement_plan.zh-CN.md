---
doc_id: automatic_orchestration_routing_enforcement_plan
version: 0.1
status: draft
owner: codex-orchestration
date: 2026-05-11
---

# 自动协同路由强制化实施计划

## 1. 背景

本仓库的用户级 orchestration 规则已经要求 Codex 主会话自动判断是否使用 native experts、durable workflow、persistent team、`native_omx` 和 LangGraph，而不是等待用户在每次任务里显式写“尽可能多使用 experts / durable_team / persistent team”。

近期日志复盘暴露了三个问题：

1. routing trace 曾把“不启动并行/子代理”的原因写成“用户没有要求并行/子代理”。这是错误理由。
2. expert/subagent 超时后，日志中存在“继续推进”和“后来结果已吸收”之间证据链不够清晰的问题。
3. LangGraph 已经在 user-level 状态中 installed/enabled/selected/ready，但当前任务 trace 容易把“backend 是否常开”和“任务是否需要 team”混在一起。

## 2. 用户确认的硬规则

### 2.1 能力依赖链

能力链必须是硬依赖，而不是软偏好：

```text
subagent_routing 开启/可用
  -> 才允许 oh-my-codex / OMX 开启
    -> 才允许 LangGraph 开启
      -> LangGraph ready 时作为默认 durable backend 常开
```

规则化表达：

```text
if subagent_routing == off:
    oh_my_codex = off
    langgraph = off

if oh_my_codex == off:
    langgraph = off

if langgraph == on:
    require subagent_routing != off
    require oh_my_codex == on

if durable_orchestration_backend == langgraph:
    require langgraph == on
```

### 2.2 LangGraph 默认 backend 常开

当 user-level 状态满足以下条件：

```text
subagent_routing != off
oh_my_codex = on
langgraph = on
langgraph_ready = true
```

则 LangGraph 是默认 durable backend。任务复杂度只决定是否启动 durable workflow / persistent team，不决定 LangGraph backend 是否启用。

### 2.3 自动协同不依赖用户提示

禁止把以下内容作为不使用 experts / durable_team / persistent team 的理由：

```text
用户没有要求并行
用户没有要求子代理
用户没有写 experts/durable_team/persistent team
```

正确判断依据：

- 任务阶段；
- 是否是 bounded multi-face research；
- 是否跨模块、跨接口、跨信任边界；
- 是否存在 2+ 独立执行切片；
- 计划是否已冻结；
- backend / preflight 是否 ready；
- 当前会话是否能安全本地接管。

### 2.4 expert 超时处理

关键路径 expert/subagent 超时后，不得把超时结果当作证据。必须选择以下路径之一：

1. 在有进展迹象时继续 bounded wait；
2. respawn 一个更窄、更明确的新 expert；
3. 若满足条件，用 LangGraph durable workflow / durable lane 接管；
4. 若 durable/persistent team 不适合或 preflight 阻塞，由本会话明确接管并完成缺失复核。

final report 必须区分：

- `expert returned and absorbed`；
- `expert timed out; not used as evidence`；
- `main session took over verification`；
- `durable_team blocked by <reason>`；
- `backend_default=langgraph, backend_ready=true` - 记录 LangGraph 是默认且 ready 的 backend，并不等同于 persistent team 已启动。

## 3. Activation trace 新格式

每个新会话、resume、阶段变化、“继续”、expert 超时、发现 `.omx` durable state、或任务扩展到 2+ execution slices 时，必须重新做 activation check。

建议 trace 字段：

```text
Routing trace:
phase=<phase>
capability_chain=subagent:<auto|manual|off> > omx:<on|off> > langgraph:<on|off>
backend_default=<langgraph|native_omx|none>
backend_ready=<true|false>
experts=<none|analyst×N|architect|writer|verifier|...>
durable_workflow=<not_needed|candidate|selected|blocked|running>
persistent_team=<not_needed|candidate|selected|blocked|running>
why=<concrete reason>
```

## 4. 当前本地检查结论

2026-05-11 本地只读检查显示：

```text
C:\Users\lenovo\.codex\state\user-level-team-mode.json:
  subagent_routing = auto
  oh_my_codex = on
  langgraph = on
  durable_orchestration_backend = langgraph
  langgraph_ready = true

C:\Users\lenovo\.codex\venvs\langgraph-py312:
  exists
  langgraph importable
  langgraph_cli available

D:\PythonProject_langgraph\.omx\state\langgraph\backend.json:
  backend = langgraph
  status = running

D:\PythonProject_langgraph\.omx\state\selectors\active.json:
  missing at inspection time
```

解释：user-level LangGraph backend 已可用且应视为默认常开；repo-local active selector 缺失是需要治理/辅助脚本修复的状态刷新问题，不能被解释成 LangGraph backend 不可用。

## 5. 拟实施范围

本计划确认后，以 OpenSpec change `enforce-automatic-orchestration-routing` 落地：

1. 更新 `AGENTS.md` 的 orchestration activation 规则。
2. 更新 `docs_bilingual/project_startup_summary.*` 的冷启动提醒。
3. 更新 team-mode / LangGraph runtime 相关 governance 或 implementation plan。
4. 新增或更新 orchestration activation policy 文档。
5. 增加 checker / 测试，防止以下回归：
   - 用“用户没有要求并行/子代理”解释不启动 experts；
   - LangGraph ready 时仍把 backend 当成可选或不可用；
   - expert timeout 后把未返回结果当作验证证据；
   - routing trace 不区分 backend 常开与 persistent team 启动阈值。
6. 评估并修复 repo-local `.omx/state/selectors/active.json` 缺失时的刷新/报告规则。

## 6. 非目标

- 不把每个小任务都强制变成 multi-worker execution。
- 不把 LangGraph official package 安装进仓库 `.venv`；仓库规则仍优先使用 user-level shared LangGraph venv。
- 不绕过 OpenSpec / local gate / local MR review。
- 不在 tmux 不可用时假装启动 pane-style persistent team。

## 7. 验收标准

- 新会话和已有会话 resume 都能看到 capability chain 与 backend default。
- LangGraph ready 时默认 backend 报告为 `langgraph`。
- 不再出现“用户没有要求并行/子代理，所以不启动”的 trace。
- expert 超时后 final report 不会声称获得了该 expert 的验证结果。
- checker 或测试能覆盖上述至少三个关键回归。
