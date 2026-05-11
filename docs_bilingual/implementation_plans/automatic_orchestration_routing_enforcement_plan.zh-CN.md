---
doc_id: automatic_orchestration_routing_enforcement_plan
version: 0.16
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
- 是否存在更高权威或 runtime surface blocker；
- 当前会话是否能安全本地接管。

### 2.4 expert 超时处理

关键路径 expert/subagent 超时后，不得把超时结果当作证据。必须选择以下路径之一：

1. 在有进展迹象时继续 bounded wait；
2. respawn 一个更窄、更明确的新 expert；
3. 若满足条件，用 LangGraph durable workflow / durable lane 接管；
4. 若 durable/persistent team 不适合或 preflight 阻塞，由本会话明确接管并完成缺失复核。

final report 必须区分：

- `expert returned and absorbed` - expert 结果已返回并被用作证据；
- `expert timed out; not used as evidence` - expert 未返回，不得支持最终结论；
- `main session took over verification` - leader 主会话直接完成缺失复核；
- `durable_team blocked by <reason>` - 已评估 durable 或 persistent team，但因具体原因无法启动；
- `backend_default=langgraph, backend_ready=true` - 记录 LangGraph 是默认且 ready 的 backend，并不等同于 persistent team 已启动。

## 3. Activation trace 新格式

每个新会话、session reload、Codex restart、resume、阶段变化、“继续”、expert 超时、发现 `.omx` durable state、或任务扩展到 2+ execution slices 时，必须重新做 activation check。

必填 trace 字段：

```text
Routing trace:
phase=<phase>
capability_chain=subagent:<auto|manual|off> > omx:<on|off> > langgraph:<on|off>
backend_default=<langgraph|native_omx|none>
backend_ready=<true|false>
experts=<none|analystxN|architect|writer|verifier|blocked:<reason>|...>
durable_workflow=<not_needed|candidate|selected|blocked|running>
persistent_team=<not_needed|candidate|selected|blocked|running>
why=<concrete reason>
```

规范英文文件使用 ASCII `analystxN`；中文或其他本地化文档可写成 `analyst x N` 或其他本地化形式。

## 4. 自动路由决策矩阵

| 触发场景 | Experts | Durable workflow | Persistent team | 主会话兜底 |
| --- | --- | --- | --- | --- |
| 单个低风险文件编辑 | 默认不需要，除非需要专项复核 | 不需要 | 不需要 | 本地编辑并验证 |
| 有边界的多面研究 | 先 analystxN 同质扇出 | research fan-in 后形成阶段化执行时才作为候选 | plan freeze 前不启动 | 主会话综合 fan-in |
| 跨模块架构或共享接口 | architect，必要时 security-reviewer | 候选 | 计划冻结且 2+ 独立切片后 | leader 写集成契约 |
| 大型文档重写 | 按需 analyst / writer / verifier | 多阶段或需要 checkpoint 时作为候选 | 仅在写入切片独立时 | leader-owned integration |
| 行为变化型多文件工作 | test-engineer 和 verifier | 候选 | 切片隔离后 | local gate + 主会话复核 |
| 安全、权限、密钥、支付、不可信输入 | security-reviewer | 候选 | trust boundary 映射后才可考虑 | 未复核前阻断发布 |
| 关键路径 expert 超时 | respawn 更窄 expert 或替代角色 | LangGraph-ready 且适合 checkpoint handoff 时选择 | preflight 通过才启动 | 主会话接管并声明证据来源 |

## 5. 硬路由指令与最小充分角色选择

显式 routing directive 是 activation check 的硬输入，不是软偏好。

Directive 规则：

- 用户请求 `omx`、`LangGraph`、`resume`、`continue`、`parallel`、`experts`、`durable_team` 或 `persistent team` 时，必须触发 activation check；
- 显式 `omx` 或 `LangGraph` 请求必须被视为当前 task flow 的 hard routing directive；
- 当 capability chain、preflight 与 task threshold 都满足时，会话必须实际采用被选中的 lane（`selected` 或 `running`），不得停留在 explanation-only mode；
- 如果没有采用被请求的 lane，trace 必须在 `why` 中写明具体 blocker 或未满足阈值，例如 `blocked:backend_not_ready`、`blocked:platform_subagent_invocation_constraint` 或 `threshold_not_met:no_frozen_plan`；
- `resume` 与 `continue` 会触发 retrofit 和 state re-read；它们本身不强制启动 durable team，除非阈值满足。

最小充分 expert role 选择：

| Role | 选择条件 | 默认边界 |
| --- | --- | --- |
| `analyst` | outcome、non-goals 或 acceptance target 不清；仍有两个以上主要歧义；bounded multi-face research 需要首轮 fan-out | bounded multi-face research 第一轮 analyst-only |
| `researcher` | 需要 external docs、dependency behavior、version-sensitive facts 或 official-source verification | 任务开放式开始时与 implementation 分离 |
| `architect` | 涉及两个以上 modules、trust boundaries、shared interfaces、migrations 或 non-local design decisions | bounded multi-face research 中等 analyst fan-in 后再升级 |
| `planner` | 存在两个以上 execution slices、serial hotspots、rollout ordering 或 dependency chains | architecture/context 清楚后再使用 |
| `debugger` | 存在 blocking failure、regression、reproducible defect 或 stabilization-heavy repair | stabilization lane，不作通用 executor |
| `verifier` | final acceptance、behavior-changing work、multi-file integration 或 multi-worker integration 需要验证 | multi-worker integration 后必须使用 |
| `test-engineer` | critical-path behavior changed、tests missing、flaky 或 broad regression risk | 负责 test strategy 与 evidence，不拥有产品决策 |
| `security-reviewer` | 涉及 auth、secrets、permissions、untrusted input、code execution、external trust boundaries 或 payments | 未复核前阻断 release |
| `writer` | 涉及 user-facing behavior、setup、migration、operator workflow 或 document-finalization work | bounded multi-face research 中等 analyst fan-in 后再升级 |
| `bug-finder` / `bug-rebutter` / `bug-judge` | 常规 verification 后仍有 contested、noisy 或 high-volume bug triage | burst、read-only、leader-side；持久化 survivors，而不是持久化 workers |

使用最小充分 expert 集合。不得因为角色可用就添加角色；只有触发条件存在且输出能实质推进当前阶段时才添加。

## 6. Native agents、skills、profiles 与 follow-up thread 边界

Native Codex subagents、workflow skills、plugin-provided skills 与 profile helpers 是不同 surface，不得混为一谈。

Registry 与加载规则：

- native reusable role definitions 位于 user-level agents directory 或 repo-local `.codex/agents/`；
- 每个 standalone custom agent TOML 至少必须定义 `name`、`description` 与 `developer_instructions`；
- skills 从已安装的 `SKILL.md` 文件加载，并通过 `$name` 或 AGENTS.md routing 调用；skills 不是 native subagents；
- plugin modules 与 profile helper 的 hard-load/soft-load 只改变哪些 procedural instructions 可见，本身不启动 durable workers，也不满足 persistent-team thresholds；
- launcher 或 profile surface 需要长 generated instructions 时，优先使用 `model_instructions_file` 等 file-backed reference，而不是很长的 inline `-c developer_instructions=...` payload。

Follow-up thread 规则：

- completed expert 被吸收并关闭后，如果后续仍需要 follow-up work，应 spawn fresh agent 并传入必要 context；
- 只有用户明确要求 preserve thread，或计划记录了 intentional preserved-thread reason 时，才复用 preserved thread；
- 不得把 skill invocation、plugin profile 或 preserved transcript 当成 expert result returned 的证据；证据必须来自显式 expert result、durable checkpoint、本地 verification 或 cited source。

Selector source 规则：

- 自动 durable-team routing 读取 `.omx/state/selectors/active.json` 作为 shared repo-local activation selector；
- compatibility records 可以作为上下文检查，但不能单独授权自动接管 unmanaged teams。

## 7. Leader session 与采用范围边界

当前 main Codex CLI session 仍然是 task flow 的 leader。orchestration 设计不得创建或要求一个 separate persistent leader pane 来替代当前主会话。

Leader-session 规则：

- 主会话负责 activation checks、role selection、worker brief quality、fan-in、evidence labeling、final integration 与最终用户报告；
- subagents、durable workers、skills、plugin profiles 与 LangGraph nodes 都是 leader 控制下的 execution surfaces，不是独立 release authorities；
- local mainline 或 publication decisions 仍然是用户授权的 release decisions，不是 worker 自动决策；
- 如果使用多个 workers，leader 负责冲突解决、证据充分性与最终 acceptance claims。

采用范围规则：

- orchestration decision target 是当前 task flow，而不是仓库是否 newly created；
- existing projects 的 new sessions 应自动遵循当前 user-level orchestration policy；
- existing live sessions 必须在 reload、restart、resume、continue、phase change、durable-state detection 或 capability-state change 时 retrofit；
- Codex startup itself 不会 auto-launch durable team；durable launch 仍是 session 内部后续 threshold-gated action；
- resumed legacy Codex sessions 是 compatibility-scoped：可以继续 follow-up discussion，但不能覆盖当前 repository governance 或当前 capability-chain policy。

Trace 要求：当会话在 startup 或首次 activation 中没有采用 durable workflow 或 persistent team 时，trace 必须说明哪个阈值未满足，而不是暗示 startup 完全不能使用 orchestration。

## 8. Base layer、wrapper layer 与 effective lane 选择

Native Codex 仍是 base layer。oh-my-codex、native OMX、skills、profile helpers 与 LangGraph 是围绕 Codex 增加 workflow 与 durable-state 行为的层；它们不是 Codex replacement。

Layer 与 switch 规则：

- user-level capability switches 必须按链式状态读取：当前预期状态为 `subagent_routing=auto`、`oh_my_codex=on`、`langgraph=on`；
- `langgraph=on` 要求 `oh_my_codex=on` 且 routing 可用；
- `oh_my_codex=off` 会禁用 LangGraph availability；
- `subagent_routing=off` 会禁用更高 orchestration layers；
- 当 `durable_orchestration_backend=langgraph` 且 `langgraph_ready=true` 时，LangGraph 是默认 durable backend state。

Effective lane 规则：

- default backend state 不会消除 task-level lane choice；
- worker-centric durable execution、worktree isolation、mailbox flow 与 direct worker lifecycle control 优先使用 `native_omx`；
- graph-shaped multi-phase execution、checkpoint-driven recovery、interrupt/resume approval gates、frozen briefs 与 persisted survivor queues 优先使用 LangGraph；
- effective lane choice 可以随 task flow 改变，但一个 durable task 同一时间仍只能使用一个 backend family；
- backend-family switching 仍必须显式化，并记录为 close/handoff，而不是隐藏成静默 lane change。

## 9. Durable-team 阈值映射

Durable team 启动必须受阈值约束。`backend_default=langgraph` 与 `backend_ready=true` 表示 durable backend 可用；它不表示 persistent team 必须已经运行。

阶段映射：

| 阶段 | Durable team 决策 | Worker 形态 | 必须写入 trace 的理由 |
| --- | --- | --- | --- |
| define-target | `persistent_team=not_needed` | 无 | target 与 acceptance boundary 仍在定义 |
| read-context | `persistent_team=not_needed` | 无 | context gathering 仍由 leader 或 analyst-only 完成 |
| freeze-plan | `persistent_team=not_needed` | 无 | plan 尚未冻结 |
| verify-accept | 默认 `persistent_team=not_needed` | 按需使用 verifier/test-engineer experts | acceptance verification 本身不是 multi-worker execution slice |
| execute-parallel | plan 已冻结且存在 2+ 独立 execution slices 时 `persistent_team=selected` | 2 个 `team-executor` workers；3+ slices 时扩展到 3 workers | 具名 slice 数量与所有权边界触发 team launch |
| integrate-converge | 存在 2+ 独立 integration/convergence slices 时 `persistent_team=selected` | 2 个 `team-executor` workers；leader 负责最终集成 | 具名 convergence slices 足够独立，可并行 |
| stabilize | 存在至少 1 个 blocking failure、regression 或 stabilization issue 时 `persistent_team=selected` | 默认 2 个 `debugger` workers | 具名 blocking issue 触发 debugger-lane stabilization |

首轮报告规则：

- 如果第一次 activation check 没有选择 `omx team` / durable team，trace 必须说明哪个阈值未满足；
- 如果选择了 durable team，trace 必须说明哪个阈值触发了它；
- 当阈值满足且没有 blocker 时，使用已批准的自动 durable-team launcher，例如 `omx-team-auto.ps1`，而不是 raw `omx team`；
- 不自动接管 unmanaged existing teams；必须把它们报告为需要显式 adopt 或 cleanup 的既有状态。

Bounded multi-face research 仍然是 analyst-fanout-first：第一轮使用同质 `analystxN`；默认第一轮不得混入 `architect`、`planner` 或 `writer`。只有在 analyst fan-in 显示 architecture、execution-ordering 或 document-finalization layer 后，才升级到这些角色。

## 10. Delegation 设计与 leader wait discipline

Delegation 必须缩短获得正确结果的路径；它不能变成反射式后台等待。

委派前：

- 先识别 leader 当前应本地执行的 immediate critical-path task；
- 只委派 concrete、bounded、self-contained 且能 materially advance 主任务的 sidecar work；
- 如果下一步 leader action 依赖该结果，不要把 urgent blocking work 委派出去等待；
- leader 与 experts 之间、experts 彼此之间不得 duplicate work；
- 避免在同一个 unresolved thread 上重复发起多次 delegate call，除非 follow-up 确实不同且必要。

委派执行期间：

- leader 立即继续 meaningful non-overlapping work；
- 不要在本地重做 delegated task，除非 delegated lane 已 timeout、stalled 或被明确 abandoned，并且 leader 记录 takeover；
- `wait_agent` 要 sparingly 使用，只在 leader 下一步 critical-path step 被该结果阻塞时才等待；
- worker 返回 code 或 documents 后，leader 必须快速 review、integrate 或 refine，而不是自动接受。

代码委派：

- 明确 file/module ownership 与 expected output；
- 告知 workers 他们不是代码库中唯一执行者，不得 revert 其他人的 edits；
- 要求 workers 在 final answer 中列出 changed paths；
- delegated write sets 必须保持 disjoint，除非 leader 对 hotspot 做 serializes。

## 11. Codebase exploration、code-change delegation 与 durable state surfaces

Read-only exploration、code-changing worker execution 与 durable-state persistence 具有不同的证据和所有权规则。

Exploration 与代码委派规则：

- `explorer` 风格 codebase search 用于 specific、well-scoped 的 read-only questions、symbol mapping 或 file discovery；
- 当 bounded code change 已清楚且可以安全委派时，不得用 read-only exploration 替代 implementation worker；
- 对 coding tasks，如果 worker 能在隔离 ownership area 中完成 bounded patch，优先委派 concrete code-change worker subtasks，而不是只做 read-only explorer analysis；
- 当 leader 对 critical path 已有足够本地上下文时，应本地推进，而不是委派一个会阻塞的 read-only exploration task；
- explorer results 可以用于 routing 和 briefs，但最终 implementation evidence 仍需要 local verification、tests 或经 review 的 worker patches。

LangGraph entrypoint 与 repo-local state 规则：

- 当任务需要 graph phases、checkpoint gates、frozen briefs、survivor queues 或 tracked LangGraph thread state 时，使用 LangGraph entrypoints 与 repo-local `.omx/state/langgraph/` runtime state；
- repo-local `.omx/state/langgraph/backend.json` 可作为 backend context 检查；
- `.omx/state/team/codex-auto-managed-team.json` 可作为 compatibility context 检查；
- `.omx/state/selectors/active.json` 仍是自动 durable-team adoption 的 active selector authority；
- durable artifacts、frozen briefs 与 persisted survivor queues 必须写入 repo-local state 或已记录 artifact paths，不得只保存在 transient chat context。

## 12. Expert 生命周期、bounded wait 与 provider backpressure

Expert 与 subagent 的使用必须由 leader 从启动、fan-in 到清理全程负责。

生命周期规则：

- 使用 bounded wait，不得无限等待；
- 第一个 wait window 从约 30 秒开始；
- bounded review 可延长到约 60 秒；
- 更深的 architect、verifier 或 researcher 工作可延长到约 120 秒；
- 单个 expert 的总等待时间默认控制在约 180 秒内，除非用户明确要求保留或继续该线程；
- 长时间运行的 expert 必须约每 30 秒或在重要 milestone 给出简短 progress/liveness update，包含当前步骤、已完成工作、下一步和 blocker；
- 如果连续两次 progress check 都静默，视为 stalled，并选择 inspect、redirect、respawn 更窄任务、handoff 到 durable lane，或由主会话接管；
- `wait_agent` 返回 completed 结果且 leader 吸收后，默认关闭 completed agent；
- 只有用户明确要求保留该线程时，才继续保持 completed agent 打开。

timeout、stall 或 upstream wait 都不是证据。final report 必须说明哪条 lane 提供了证据，以及哪条 lane timed out、stalled、吸收后关闭，或由主会话接管。

Provider pacing 与 backpressure 规则：

- provider proxy 有共享 upstream pacing budget：每 rolling 1-minute window 最多 10 次 true upstream provider forwards；
- 当 budget 饱和时，upstream-bound 请求等待 slot，而不是把该条件视为本地 fatal error；
- upstream pacing 本身不是避免 LangGraph、native OMX 或 native experts 的理由；
- 当多个 agent step 可能命中 provider 时，优先 local-first phases、deterministic local checks 与 bounded fan-out；
- 如果 pacing 对执行产生实质影响，报告为 `backpressure:upstream_pacing` 或等价具名条件，而不是解释成用户意图缺失。

## 13. Fan-out 上限、写入所有权与 backend-family 边界

Native expert 的使用是 leader 显式启动并由 leader 负责 fan-in。不得暗示 raw Codex 默认会自动生成 specialist roles。

Fan-out 上限：

- native subagent fan-out 必须保持有界；当前 managed defaults 为 `agents.max_threads=6` 与 `agents.max_depth=1`；
- 优先把并行 fan-out 用于 read-heavy、bounded、相互独立的工作；
- 如果下一步 critical path 依赖该结果，则该工作应由主会话本地完成，而不是交给后台阻塞等待；
- 写入型并行执行必须明确 file/module ownership、disjoint write sets、hotspot serialization 与 leader-owned final integration；
- worker 必须被告知自己不是代码库中的唯一执行者，不得 revert 或覆盖其他 active owners 的变更。

Backend-family 边界：

- 一个 durable task 同一时间只使用一个 backend family；
- backend-family switching 必须显式化，并记录在 trace 或 handoff notes 中；
- 当 LangGraph ready 且被选为默认 backend 时，如果 durable lane 使用 `native_omx`，必须给出具名理由，例如 worker-centric durable execution、worktree isolation、mailbox flow 或 direct worker lifecycle control；
- graph-shaped multi-phase execution、checkpoint-driven recovery、interrupt/resume approval gates、frozen briefs 与 persisted survivor queues 优先使用 LangGraph；
- 不得在没有关闭或显式 handoff 前一 backend family 的情况下，把 `native_omx` worker lifecycle 与 LangGraph checkpoint state 混进同一个 durable task。

开放式任务必须保持 research 与 implementation 分离：先用 analyst/research roles 做 discovery，只有在 plan、ownership 与 acceptance evidence 冻结后，才进入 executor/team execution。

## 14. Handoff、对抗复核与相邻 runtime 边界

开放式 research 与有争议的 bug review 必须有明确 handoff 边界，避免临时 expert lane 变成 unmanaged persistent workers。

Research handoff 规则：

- 任务开放式开始时，research 与 implementation 必须使用不同角色；
- research fan-in 后，先把结果持久化为 frozen implementation brief，再开始 implementation；
- implementation 应在 fresh execution context 或明确标记的 execution phase 中继续，并把 frozen brief 作为契约；
- brief 必须包含 scope、non-goals、acceptance evidence、ownership boundaries 与 unresolved risks。

对抗复核规则：

- `bug-finder`、`bug-rebutter`、`bug-judge` 是 burst-review roles，默认保持 leader-side 且 read-only；
- 仅当一次常规 verification 后仍存在争议、噪声或大批候选 bug 时，才使用它们做 contested / noisy / high-volume bug triage；
- 不把 bug triad 保持为 persistent workers；
- 剩余候选问题必须持久化为 adversarial-review survivor queue，需要修复时转入 debugger lane；
- final report 必须区分 confirmed bugs、rebutted candidates、unresolved survivors 与 debugger-lane follow-up。

Durable-state 与相邻 runtime 边界：

- 使用 `codex-durable-state-status.ps1` 作为当前仓库或 worktree 的 canonical read-only cross-backend durable-state summary；
- 不得仅凭 compatibility records 自动接管 unmanaged teams；
- 术语优先使用 OpenHands，而不是 archived OpenDevin；
- LangGraph、AutoGen、CrewAI 是通用 programmable orchestration runtimes，不等同于 native Codex-subagent equivalents；
- LangGraph graph 可以协调 phases、checkpoints、approvals 与 survivor queues，但 native Codex experts 仍必须由 leader 显式 spawn 并负责 fan-in。

## 15. Backend、workflow 与 team 语义边界

以下概念不得混用：

- `backend_default` - user-level capability state 选择的默认 durable backend。
- `backend_ready` - 已选 backend 是否 installed、enabled、selected、ready。
- `durable_workflow` - 当前任务是否应使用 checkpointed 或 graph-shaped durable execution。
- `persistent_team` - 当前任务是否应启动 multi-worker persistent team。

当 LangGraph ready 时，它就是默认 backend。小任务仍然可以是 `durable_workflow=not_needed` 且 `persistent_team=not_needed`。这表示任务不需要这些执行面，不表示 LangGraph 关闭。

## 16. 当前本地检查结论

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

## 17. Active selector 处理规则

当 `.omx/state/selectors/active.json` 缺失，但 user-level capability state 显示 `durable_orchestration_backend=langgraph` 且 `langgraph_ready=true` 时，会话不得静默降级到 `native_omx` 或 `none`。

必需行为：

1. 报告 `backend_default=langgraph` 与 `backend_ready=true`；
2. 把 `active_selector=missing` 报告为 repo-local state-refresh gap；
3. 当实现工作需要 tracked durable thread 时，通过已批准 helper 刷新或创建 selector；
4. 如果 helper 尚不存在，将其记录为实现缺口，而不是解释成 backend 不可用。

## 18. 低风险迭代与本地合入边界

对于已经确认范围内的重复低风险完善，主会话在同时满足以下条件时，可以不再逐次请求用户授权：

- 变更仅限于文档、治理文本、本地检查元数据或等价的非 runtime surface；
- 受影响文件仍在已经同意的主题边界内；
- activation check 能够说明 `experts=none`、`durable_workflow=not_needed`、`persistent_team=not_needed`；
- 目标提交后的 local gate 与 local MR review 均通过；
- feature worktree 干净，且本地 `main` 不落后于 `gitlab/main`。

在这种情况下，会话可以在同一个低风险循环中提交变更，并 fast-forward 或合并到本地 `main`。这样可以避免用户对同一类简单迭代反复授权，包括反复检查和完善本计划文件的请求。

以下动作仍然必须获得用户明确授权：

1. 推送到 GitLab 或 GitHub；
2. 创建、为发布更新、或合并 GitLab MR；
3. 从 GitLab 或本地 `main` 同步 GitHub；
4. hard reset、force push、大范围删除、或清理约定工作区以外内容等破坏性操作；
5. 范围扩展到 runtime 代码、启动器行为、CI wiring、安全边界或大范围多文件实现；
6. local gate 或 local MR review 失败后仍要集成；
7. 存在所有权冲突风险的写入型并行执行。

这个本地合入许可不会削弱发布流程。它只定义已经授权的简单迭代在本地执行时的边界；远端发布仍然是单独决策。

## 19. 更高权威与 runtime surface 阻塞边界

自动协同是默认策略，但 live execution 仍必须服从更高优先级指令、当前工具契约以及实际 runtime surface 可用性。如果某个任务按策略本应选择 expert、durable workflow 或 persistent team，但对应 surface 不能被调用，trace 必须报告具名 blocker，而不能把决策重新表述成用户偏好。

合法 blocker 示例包括：

- `blocked:platform_subagent_invocation_constraint` - 当前 live tool contract 不允许本轮会话启动 native subagent；
- `blocked:helper_missing` - 已批准的 durable 或 selector helper 尚未实现或安装；
- `blocked:preflight_failed` - lane 已被选中，但具体 preflight 检查失败；
- `blocked:write_ownership_conflict` - 写入型并行执行会与另一个 active owner 重叠；
- `blocked:backend_not_ready` - 所需 backend 尚未 installed、enabled、selected 或 ready。

必须采用的 fallback 行为：

1. 如果该 execution surface 确实不需要，报告 `not_needed` 并保持本地执行；
2. 如果该 surface 需要但被阻塞，报告 `blocked:<reason>`，并选择通过可用 surface respawn、durable handoff，或由主会话明确接管；
3. 绝不能把 platform 或 helper blocker 改写成被禁止的“用户没有要求 subagents/parallelism”；
4. final report 必须区分 `not_needed`、`selected/running`、`blocked` 和 `main_session_takeover` 证据。

因此，规范 activation trace 允许 expert blocker：

```text
experts=<none|analystxN|architect|writer|verifier|blocked:<reason>|...>
```

## 20. 实施阶段

### Phase 0 - 记录并保护计划

- 新增本双语计划。
- 忽略 `log202605111306.md` 之类的本地 transcript 日志。
- 确保 canary guard 忽略 root `.gitignore` 已忽略的本地日志，避免 ignored transcript 破坏 local gate。

### Phase 1 - Policy surfaces

- 更新 `AGENTS.md`。
- 更新 `docs_bilingual/project_startup_summary.*`。
- 新增或更新 orchestration activation policy 文档。
- 更新 team-mode 和 LangGraph runtime policy surfaces。

### Phase 2 - Script-backed enforcement

- 增加 forbidden routing reason 的 checker 覆盖。
- 增加 durable-team phase thresholds 与首轮阈值解释的 checker 覆盖。
- 增加 capability-chain consistency 的 checker 覆盖。
- 增加 expert-timeout evidence claims 的 checker 覆盖。
- 增加 completed-agent closure、bounded wait windows、liveness/stall handling 与 upstream pacing labels 的 checker 覆盖。
- 增加 fan-out bounds、写入所有权隔离、leader-side spawning 表述与 one-backend-family durable task 的 checker 覆盖。
- 增加 frozen research handoff briefs、adversarial-review survivor queues 与 adjacent-runtime terminology boundaries 的 checker 覆盖。
- 增加 hard routing directives、actual adoption versus explanation-only mode 与 smallest-sufficient role selection 的 checker 覆盖。
- 增加 native-agent versus skill/profile/plugin boundaries、custom agent TOML fields、fresh follow-up agent use 与 selector-source handling 的 checker 覆盖。
- 增加 main-session leader ownership、no separate persistent leader pane、startup non-autolaunch、task-flow scoped adoption 与 legacy-session compatibility boundaries 的 checker 覆盖。
- 增加 native Codex as base layer、oh-my-codex as wrapper/workflow layer、capability-switch chain values 与 `native_omx` / LangGraph effective lane choice 的 checker 覆盖。
- 增加 delegation design quality、critical-path local work、等待期间 non-overlapping leader work、duplicate-work prevention 与 sparse `wait_agent` use 的 checker 覆盖。
- 增加 explorer versus code-change worker boundaries、LangGraph entrypoints、repo-local `.omx/state/langgraph/` state、compatibility record usage 与 durable artifact persistence 的 checker 覆盖。
- 新增或更新 selector refresh/status helper 行为。

### Phase 3 - Runtime integration

- 确保新会话、session reload、Codex restart 和 resume 会话输出必填 trace 字段。
- 确保已有会话在 session reload、Codex restart、phase change、resume、continue、`.omx` state detection、expert timeout 时重新做 activation check。
- 确保 LangGraph-ready 会话使用 LangGraph 作为默认 durable backend。

## 21. 拟实施范围

本计划确认后，以 OpenSpec change `enforce-automatic-orchestration-routing` 落地：

1. 更新 `AGENTS.md` 的 orchestration activation 规则。
2. 更新 `docs_bilingual/project_startup_summary.*` 的冷启动提醒。
3. 更新 team-mode / LangGraph runtime 相关 governance 或 implementation plan。
4. 新增或更新 orchestration activation policy 文档。
5. 增加 checker / 测试，防止以下回归：
   - 用“用户没有要求并行/子代理”解释不启动 experts；
   - LangGraph ready 时仍把 backend 当成可选或不可用；
   - expert timeout 后把未返回结果当作验证证据；
   - routing trace 不区分 backend 常开与 persistent team 启动阈值；
   - tool/runtime blocker 被误报成用户偏好或 `not_needed`；
   - 没有 frozen plan、独立切片或具名 stabilization blocker 时选择 durable team；
   - bounded multi-face research 跳过 analyst-only 首轮 fan-out；
   - completed expert fan-in 后未被显式要求保留却仍保持打开；
   - provider upstream pacing 被报告成禁用 orchestration 的理由；
   - fan-out 未显式 override 却超过 `agents.max_threads=6` 或 `agents.max_depth=1`；
   - 写入型并行工作没有 disjoint ownership 与 leader-owned final integration；
   - 同一个 durable task 在没有显式 handoff 时混用 `native_omx` 与 LangGraph state；
   - implementation 从开放式 research 直接开始，缺少 frozen implementation brief；
   - bug triad roles 被保持为 persistent workers，而不是把 survivors 持久化到 debugger-lane queue；
   - 把 AutoGen、CrewAI 或 LangGraph 说成 native Codex-subagent equivalents；
   - 显式 `omx` 或 `LangGraph` directive 被当成 optional preference；
   - thresholds 已满足但会话停留在 explanation-only mode；
   - 没有 smallest-sufficient trigger 却添加角色；
   - skills 或 plugin profiles 被当成 native subagents 或 expert evidence；
   - custom agent TOMLs 缺少 `name`、`description` 或 `developer_instructions`；
   - follow-up work 在没有 explicit preservation reason 时复用已关闭/已完成 expert thread；
   - 仅凭 compatibility records 自动接管 unmanaged team，而不是读取 `.omx/state/selectors/active.json`；
   - orchestration decision 依赖仓库是否 newly created，而不是当前 task flow；
   - Codex startup 被当成自动 durable-team launch；
   - separate persistent leader pane 替代 main Codex session；
   - resumed legacy sessions 覆盖当前 repository governance；
   - oh-my-codex 或 LangGraph 被描述为 Codex replacement，而不是 additive layer；
   - capability switches 没有按 dependency chain 读取；
   - worker-centric durable execution 未考虑 `native_omx` lane fit 而默认进入 LangGraph；
   - graph-shaped checkpoint work 未考虑 LangGraph lane fit 而默认进入 `native_omx`；
   - leader 应本地处理的 blocking critical-path work 被委派出去；
   - leader/expert 或 expert/expert 之间 duplicate work；
   - leader 在没有尝试 non-overlapping local work 时静默等待；
   - read-only explorer work 替代了清楚的 bounded code-change worker task；
   - LangGraph checkpoint work 没有使用 LangGraph entrypoints 或 repo-local `.omx/state/langgraph/` state；
   - durable artifacts、frozen briefs 或 survivor queues 只存在于 transient chat context。
6. 评估并修复 repo-local `.omx/state/selectors/active.json` 缺失时的刷新/报告规则。

## 22. 证据与测试映射

| 规则 | 最小证据 | 候选测试/检查 |
| --- | --- | --- |
| 能力链被强制执行 | state file normalization 示例 | invalid state combinations 单元测试 |
| LangGraph ready 表示默认 backend | status output 包含 backend_default 与 backend_ready | status helper golden output 测试 |
| 不依赖用户提醒 | routing trace 不出现 forbidden reason | 静态 trace 文本 checker |
| expert timeout 不是证据 | final report 区分 timeout 与 absorbed result | log/report pattern checker |
| ignored local logs 不破坏 canary guard | 含 canary marker 的 ignored transcript 通过 guard | context-retention canary 测试 |
| active selector 缺失是 refresh gap | status 报告 selector missing 但不 downgrade backend | selector status helper 测试 |
| tool/runtime blocker 被显式报告 | trace 报告 `blocked:<reason>`，而不是用户提醒缺失 | activation trace blocker 测试 |
| reload 与 restart 触发 activation | reload/restart transcript 包含 capability chain 与 backend default | startup/reload trace smoke test |
| durable-team 阈值映射被执行 | 首次 activation trace 解释阈值满足或未满足 | durable-team threshold checker |
| bounded multi-face research analyst-first | 首轮 fan-out 是 `analystxN`，默认不含 architect/planner/writer | role-routing golden test |
| completed experts 被关闭 | completed agent 在结果吸收后关闭，除非明确要求保留 | agent lifecycle checker |
| expert waits 受 bounded 约束 | wait transcript 显示 30s/60s/120s window 与约 180s 总上限 | wait/liveness trace checker |
| provider backpressure 不禁用 orchestration | pacing 被报告为具名 backpressure，而不是 skip reason | upstream pacing trace checker |
| fan-out bounds 被执行 | trace 与 worker briefs 不超过 max_threads/max_depth，除非显式 override | fan-out bounds checker |
| 写入所有权被隔离 | worker briefs 声明 disjoint file/module ownership 与 hotspot serialization | ownership isolation checker |
| durable backend family 单任务一致 | handoff notes 显示单一 backend family，或 switching 前显式 close/handoff | backend-family consistency checker |
| research handoff 被冻结 | implementation 从包含 scope、non-goals、acceptance evidence、ownership 与 risks 的 frozen brief 开始 | frozen-brief checker |
| bug triad 不持久化 | bug-finder/rebutter/judge 结果被吸收，survivors 被排入 debugger lane | adversarial survivor queue checker |
| 相邻 runtime 术语正确 | 使用 OpenHands；AutoGen/CrewAI/LangGraph 不被描述为 native Codex-subagent equivalents | terminology checker |
| hard routing directives 被执行 | 显式 `omx`/`LangGraph` directive 导致 selected/running lane 或具名 blocker | directive adoption checker |
| thresholds 满足时禁止 explanation-only mode | chain、preflight 与 threshold 通过时 trace 显示实际采用 | adoption trace checker |
| role set 最小充分 | 所选角色能映射到触发表，且没有默认额外角色 | role-minimality checker |
| agent 与 skill surface 保持区分 | native agents 位于 agents directories；skills 从 `SKILL.md` 加载；profiles 不代表 workers | agent-skill-boundary checker |
| custom agent TOMLs 最小有效 | TOMLs 包含 `name`、`description` 与 `developer_instructions` | agent-toml schema checker |
| follow-up 默认 fresh agent | 后续工作 spawn fresh agent，或给出 explicit preserved-thread reason | follow-up-thread checker |
| selector source 具权威性 | 自动 durable routing 读取 `.omx/state/selectors/active.json`；compatibility records 仅作上下文 | selector-source checker |
| main session 保持 leader | trace 与 final report 显示 leader-owned fan-in、evidence labeling 与 integration | leader-ownership checker |
| startup 不自动拉团队 | startup trace 显示阈值满足/未满足，而不是自动 durable-team launch | startup-team-threshold checker |
| adoption 以 task-flow 为范围 | routing decision 基于当前 task phase 与 thresholds，不基于 repo 新旧 | task-flow-scope checker |
| legacy resume 仅兼容范围 | legacy sessions 不能覆盖当前 governance 或 capability-chain policy | legacy-session boundary checker |
| Native Codex 保持 base layer | 文档把 oh-my-codex/LangGraph 描述为 additive workflow layers，而不是 replacement | base-layer terminology checker |
| capability switches 链式一致 | state 使用 subagent_routing -> oh_my_codex -> langgraph 依赖顺序 | capability-switch chain checker |
| effective lane choice 基于 task fit | native_omx 与 LangGraph 选择映射到 worker-centric 或 graph-shaped criteria | lane-fit checker |
| delegation 具体且不重复 | delegated tasks 是 bounded、self-contained、materially advancing 且不重复 | delegation-design checker |
| leader 在 experts 运行时继续工作 | trace 显示 non-overlapping leader work，或等待前写明 blocker | leader-wait discipline checker |
| critical-path blocking work 保持本地 | leader 不委派 immediate blocking step，除非显式说明 handoff 理由 | critical-path delegation checker |
| explorer 与 code-change worker 边界被保留 | read-only explorer work 限于 specific mapping questions；bounded patches 使用 workers | explorer-worker-boundary checker |
| LangGraph state surfaces 被使用 | graph/checkpoint tasks 使用 LangGraph entrypoints 与 `.omx/state/langgraph/` state | langgraph-state-surface checker |
| durable artifacts 被持久化 | frozen briefs、survivor queues 与 durable artifacts 具有 repo-local state 或 documented paths | durable-artifact-persistence checker |

## 23. 风险与回滚

- 风险：小任务自动启动过多 workers。缓解：严格区分 backend-on 与 workflow/team launch thresholds。
- 风险：忽略范围过大导致真正 canary 泄漏被隐藏。缓解：canary guard 只尊重 root `.gitignore` 模式，并继续显式检查 startup summary 来源。
- 风险：final report 过度声称 expert evidence。缓解：强制 evidence source 标签。
- 风险：completed expert threads 未关闭，造成上下文或注意力泄漏。缓解：吸收结果后默认关闭 completed agents。
- 风险：upstream pacing 被误读成 orchestration 不可用。缓解：报告具名 backpressure，并优先 local-first bounded fan-out。
- 风险：并行 workers 互相覆盖。缓解：要求 disjoint ownership、hotspot serialization 与 leader-owned integration。
- 风险：backend-family state 被混用。缓解：除非记录显式 handoff，否则每个 durable task 只允许一个 backend family。
- 风险：research 结论在 implementation 中漂移。缓解：execution 前必须冻结 implementation brief。
- 风险：adversarial review lane 变成 unmanaged workers。缓解：burst roles fan-in 后关闭，只持久化 survivors queue 给 debugger-lane follow-up。
- 风险：相邻 orchestration runtimes 被误认为 native Codex subagents。缓解：执行术语与角色边界检查。
- 风险：显式 routing directive 被当成 optional preference。缓解：要求 selected/running state 或具名 blocker。
- 风险：默认启动过多 experts。缓解：执行 smallest-sufficient role selection。
- 风险：skills 或 profile helpers 被误认为 subagent evidence。缓解：强制 agent/skill/profile surface separation。
- 风险：follow-up work 复用陈旧上下文。缓解：除非 thread 被显式 preserved，否则 spawn fresh agents。
- 风险：unmanaged durable teams 被意外接管。缓解：以 active selector 为权威，compatibility records 仅作上下文。
- 风险：separate leader pane 分裂责任。缓解：保持 main session 为 leader，workers 只是 execution surfaces。
- 风险：startup 被误认为 durable-team launch。缓解：任何 team launch 前必须有 threshold evidence。
- 风险：legacy resume 携带 stale assumptions。缓解：legacy sessions 仅作为 compatibility-scoped，并重新应用当前 governance。
- 风险：wrapper layers 被描述为 Codex replacements。缓解：执行 base-layer terminology。
- 风险：effective lane choice 忽略 task fit。缓解：durable adoption 前检查 native_omx worker-centric criteria 与 LangGraph graph-shaped criteria。
- 风险：delegation 变成被动等待。缓解：要求先做 leader-side critical-path planning，并在 experts 运行时继续 non-overlapping work。
- 风险：重复工作浪费上下文并产生冲突证据。缓解：要求 non-duplicative bounded sidecar tasks 与 explicit takeover records。
- 风险：read-only exploration 延迟明显的 bounded implementation。缓解：隔离 patch 优先 code-change workers，blocking reads 保持本地。
- 风险：durable decisions 丢在 chat context 中。缓解：把 LangGraph state、frozen briefs、survivor queues 与 durable artifacts 持久化到 repo-local paths。
- 回滚：如果 enforcement 造成过多误报，可回滚 checker/runtime enforcement，同时保留本计划作为记录。

## 24. 非目标

- 不把每个小任务都强制变成 multi-worker execution。
- 不把 LangGraph official package 安装进仓库 `.venv`；仓库规则仍优先使用 user-level shared LangGraph venv。
- 不绕过 OpenSpec / local gate / local MR review。
- 不在 tmux 不可用时假装启动 pane-style persistent team。
- 不把本计划当成 runtime enforcement 已完成的证明。

## 25. 验收标准

- 新会话、session reload、Codex restart 和已有会话 resume 都能看到 capability chain 与 backend default。
- LangGraph ready 时默认 backend 报告为 `langgraph`。
- 不再出现“用户没有要求并行/子代理，所以不启动”的 trace。
- expert 超时后 final report 不会声称获得了该 expert 的验证结果。
- checker 或测试能覆盖上述至少三个关键回归。
- repo-local active selector 缺失会被报告为 selector refresh gap，而不是 LangGraph backend 不可用。
- 工具或更高权威 blocker 会被报告为 `blocked:<reason>`，而不是用户指令缺失。
- 第一次 activation 会解释 durable team 被选择的触发阈值，或说明哪个 durable-team 阈值未满足。
- Bounded multi-face research 先使用 analyst-only fan-out，除非后续 fan-in 证明需要升级。
- Completed experts 在吸收结果后关闭，除非用户明确要求保留线程。
- Expert wait 行为受 bounded 约束，liveness/stall 处理必须在 trace 或 final report 中可见。
- Provider upstream pacing 被视为 backpressure，而不是禁用 orchestration 的理由。
- Fan-out 保持在 managed bounds 内，除非记录显式 override。
- 写入型并行执行声明 disjoint ownership 与 leader-owned final integration。
- 每个 durable task 同一时间只使用一个 backend family，或在切换前记录显式 close/handoff。
- 开放式 research 必须通过 frozen implementation brief 交接后才进入 execution。
- Bug triad roles 是 burst、read-only、leader-side roles；未解决 survivors 排入 debugger-lane follow-up。
- 相邻 runtime 术语必须正确：优先使用 OpenHands，且不得把 AutoGen/CrewAI/LangGraph 描述成 native Codex-subagent equivalents。
- 显式 `omx` 或 `LangGraph` directive 会导致实际 lane adoption，或报告具名 blocker/未满足阈值。
- 当 thresholds 满足时，会话不得停留在 explanation-only mode。
- Expert roles 从最小充分触发表中选择。
- Native agents、skills、plugin profiles 与 profile helpers 不得被合并成同一种 surface。
- Follow-up work 默认使用 fresh agent，除非存在 explicit preserved-thread reason。
- 自动 durable-team routing 以 `.omx/state/selectors/active.json` 为 selector source，不仅凭 compatibility records 自动接管 unmanaged teams。
- 当前 main Codex CLI session 仍是 leader；不得用 separate persistent leader pane 替代它。
- Startup 与首次 activation 不自动启动 durable teams；它们报告阈值满足/未满足，并仅在条件满足时采用。
- Orchestration adoption 以当前 task flow 为范围，包括 existing projects 与 live-session retrofit，而不是仓库年龄。
- Native Codex 保持 base layer；oh-my-codex 与 LangGraph 是 additive workflow/durable-state layers，不是 replacements。
- Effective lane choice 区分 worker-centric `native_omx` fit 与 graph-shaped LangGraph fit，同时保持每个 durable task 一个 backend family。
- Delegated work 必须 concrete、bounded、self-contained、non-duplicative，并能 materially advance 当前阶段。
- Leader 在 experts 运行时继续 non-overlapping work，只有下一步 critical-path step 被结果阻塞时才使用 `wait_agent`。
- Read-only explorer work 用于 specific mapping questions；bounded implementation changes 优先使用具备 isolated ownership 的 code-change workers。
- LangGraph graph/checkpoint work 使用 LangGraph entrypoints 与 repo-local `.omx/state/langgraph/` state，compatibility records 仍仅作为 context。
- Durable artifacts、frozen briefs 与 survivor queues 必须持久化到 repo-local state 或 documented artifact paths。

## 26. 适用范围与权威边界

本计划是 implementation-plan 记录。只有在后续 OpenSpec change 更新 policy surfaces、helper scripts 和 checks 后，它才会变成完整 runtime contract。

权威顺序：

1. system 与 developer instructions 仍是当前 live session 的最高权威；
2. `AGENTS.md` 与 startup summaries 定义仓库启动行为；
3. governance policy documents 定义可持久化的仓库规则；
4. 本计划记录预期实施包与验收目标。

如果本计划与当前更高权威 surface 冲突，实施变更必须更新对应 surface，而不是只依赖本计划。

## 27. 状态词定义

以下术语必须一致使用：

- `installed` - 所需 runtime 或 helper 文件存在。
- `enabled` - user-level capability switches 允许该 lane。
- `selected` - user-level 或 repo-local state 选择该 lane 作为 active backend family。
- `ready` - installed、enabled、selected 且未被 preflight 阻塞。
- `running` - 具体 durable workflow 或 team execution 当前正在运行。
- `blocked` - lane 已符合候选条件或被请求，但因具名 blocker 无法继续。
- `not_needed` - 当前任务不需要该执行面。

`ready` 不等于 `running`，`not_needed` 也不等于 disabled。

## 28. 已有会话 retrofit 规则

已有会话在以下任一触发条件出现时，必须采用本策略：

- session reload 或 Codex restart；
- 用户说“继续”或要求 resume；
- 任务阶段变化；
- 任务扩展到 2+ execution slices；
- 关键路径 expert 超时或卡住；
- 发现 `.omx` durable state；
- user-level capability state 变化；
- 会话输出 orchestration trace。

retrofit 时，包括 reload 或 restart，会话必须重新读取 user-level capability state 和 repo-local backend/selector state，然后才能声明 backend 或 team 状态。上一进程缓存或旧 routing 假设不能作为充分证据。
