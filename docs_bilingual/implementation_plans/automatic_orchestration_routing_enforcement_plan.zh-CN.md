---
doc_id: automatic_orchestration_routing_enforcement_plan
version: 0.8
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

## 5. Durable-team 阈值映射

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

## 6. Expert 生命周期、bounded wait 与 provider backpressure

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

## 7. Backend、workflow 与 team 语义边界

以下概念不得混用：

- `backend_default` - user-level capability state 选择的默认 durable backend。
- `backend_ready` - 已选 backend 是否 installed、enabled、selected、ready。
- `durable_workflow` - 当前任务是否应使用 checkpointed 或 graph-shaped durable execution。
- `persistent_team` - 当前任务是否应启动 multi-worker persistent team。

当 LangGraph ready 时，它就是默认 backend。小任务仍然可以是 `durable_workflow=not_needed` 且 `persistent_team=not_needed`。这表示任务不需要这些执行面，不表示 LangGraph 关闭。

## 8. 当前本地检查结论

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

## 9. Active selector 处理规则

当 `.omx/state/selectors/active.json` 缺失，但 user-level capability state 显示 `durable_orchestration_backend=langgraph` 且 `langgraph_ready=true` 时，会话不得静默降级到 `native_omx` 或 `none`。

必需行为：

1. 报告 `backend_default=langgraph` 与 `backend_ready=true`；
2. 把 `active_selector=missing` 报告为 repo-local state-refresh gap；
3. 当实现工作需要 tracked durable thread 时，通过已批准 helper 刷新或创建 selector；
4. 如果 helper 尚不存在，将其记录为实现缺口，而不是解释成 backend 不可用。

## 10. 低风险迭代与本地合入边界

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

## 11. 更高权威与 runtime surface 阻塞边界

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

## 12. 实施阶段

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
- 新增或更新 selector refresh/status helper 行为。

### Phase 3 - Runtime integration

- 确保新会话、session reload、Codex restart 和 resume 会话输出必填 trace 字段。
- 确保已有会话在 session reload、Codex restart、phase change、resume、continue、`.omx` state detection、expert timeout 时重新做 activation check。
- 确保 LangGraph-ready 会话使用 LangGraph 作为默认 durable backend。

## 13. 拟实施范围

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
   - provider upstream pacing 被报告成禁用 orchestration 的理由。
6. 评估并修复 repo-local `.omx/state/selectors/active.json` 缺失时的刷新/报告规则。

## 14. 证据与测试映射

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

## 15. 风险与回滚

- 风险：小任务自动启动过多 workers。缓解：严格区分 backend-on 与 workflow/team launch thresholds。
- 风险：忽略范围过大导致真正 canary 泄漏被隐藏。缓解：canary guard 只尊重 root `.gitignore` 模式，并继续显式检查 startup summary 来源。
- 风险：final report 过度声称 expert evidence。缓解：强制 evidence source 标签。
- 风险：completed expert threads 未关闭，造成上下文或注意力泄漏。缓解：吸收结果后默认关闭 completed agents。
- 风险：upstream pacing 被误读成 orchestration 不可用。缓解：报告具名 backpressure，并优先 local-first bounded fan-out。
- 回滚：如果 enforcement 造成过多误报，可回滚 checker/runtime enforcement，同时保留本计划作为记录。

## 16. 非目标

- 不把每个小任务都强制变成 multi-worker execution。
- 不把 LangGraph official package 安装进仓库 `.venv`；仓库规则仍优先使用 user-level shared LangGraph venv。
- 不绕过 OpenSpec / local gate / local MR review。
- 不在 tmux 不可用时假装启动 pane-style persistent team。
- 不把本计划当成 runtime enforcement 已完成的证明。

## 17. 验收标准

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

## 18. 适用范围与权威边界

本计划是 implementation-plan 记录。只有在后续 OpenSpec change 更新 policy surfaces、helper scripts 和 checks 后，它才会变成完整 runtime contract。

权威顺序：

1. system 与 developer instructions 仍是当前 live session 的最高权威；
2. `AGENTS.md` 与 startup summaries 定义仓库启动行为；
3. governance policy documents 定义可持久化的仓库规则；
4. 本计划记录预期实施包与验收目标。

如果本计划与当前更高权威 surface 冲突，实施变更必须更新对应 surface，而不是只依赖本计划。

## 19. 状态词定义

以下术语必须一致使用：

- `installed` - 所需 runtime 或 helper 文件存在。
- `enabled` - user-level capability switches 允许该 lane。
- `selected` - user-level 或 repo-local state 选择该 lane 作为 active backend family。
- `ready` - installed、enabled、selected 且未被 preflight 阻塞。
- `running` - 具体 durable workflow 或 team execution 当前正在运行。
- `blocked` - lane 已符合候选条件或被请求，但因具名 blocker 无法继续。
- `not_needed` - 当前任务不需要该执行面。

`ready` 不等于 `running`，`not_needed` 也不等于 disabled。

## 20. 已有会话 retrofit 规则

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
