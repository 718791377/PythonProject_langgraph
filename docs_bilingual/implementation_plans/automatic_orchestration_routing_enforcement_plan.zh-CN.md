---
doc_id: automatic_orchestration_routing_enforcement_plan
version: 0.22
status: active
owner: codex-orchestration
date: 2026-05-27
---

# 自动协同路由强制化实施计划

## 0. 本次完整 `/comet` 重构结论

本版本把原来按历史时间和问题追加形成的长文档，重构为类似以下两份新版实施方案的结构：

- `docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` - 作为用户级 sidecar 方案的新式结构参考。
- `docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md` - 作为 Comet runtime 治理方案的新式结构参考。

重构目标不是改变自动协同路由规则，而是把规则、证据契约、实施切片、验证命令、回滚路径和本地集成顺序变成更容易执行、复核和继续实施的 implementation-ready 文档。

当前结论：

- 本文仍是 `status: active` 的自动协同路由 baseline。
- Phase 0-3 baseline 已完成并归档，继续作为历史完成证据和稳定规则来源。
- Phase 4 `enforce-prompt-independent-collaboration-parity` 仍是 planned follow-up，不因本文重构而被视为已实现。
- 本次文档重构是 documentation-only，不新增 runtime checker，不启动 durable team / persistent team，不创建 LangGraph durable workflow，也不构成 native expert 已运行的证据。
- 若终端渲染中文为乱码，应以 UTF-8 读取的源文件为准，不得把乱码复制回仓库。

## 1. 目标

- 让 Codex 主会话在所有用户级工作流中自动执行 orchestration activation check，而不是依赖用户显式写“使用 experts / durable_team / persistent team”。
- 区分 policy expectation、runtime capability、实际采用状态和可审计证据，避免把 backend ready、技能调用、提示词短语或 timeout 误当作 worker 运行证明。
- 让 `native experts`、`native_omx`、LangGraph durable workflow、persistent team 的采用逻辑具备脚本化 guard、fixture、CI 和本地 MR review 证据。
- 为后续 Phase 4 提供固定 change id、文件地图、证据契约、过程组式执行模型和任务级 backlog。
- 保持本仓库是 Codex 用户级编排产品线的 source of truth；用户级生成文件和安装产物只能是同步结果，不是本计划的权威源。

## 2. 非目标

- 不把每个小任务都强制变成 multi-worker execution。
- 不把 skills、plugin profiles、profile helpers 或 workflow prompts 当成 native Codex experts。
- 不在 startup、read-context、boundary-freeze 或单文件低风险修改中自动启动 durable/persistent team。
- 不把 `backend_default=langgraph` 或 `backend_ready=true` 解释成 persistent team 已运行。
- 不绕过 OpenSpec、pre-commit update/archive check、local gate 或 local MR review。
- 不把本文档本身当作 durable/persistent runtime evidence。
- 不推送 GitLab/GitHub；远端发布必须另有当前用户明确授权。

## 3. 权威边界与状态词

### 3.1 文档状态

| 状态 | 含义 | 不能推导为 |
| --- | --- | --- |
| `active` | 当前和未来会话必须遵守的规则与验收清单 | 某个 runtime worker 已启动或完成 |
| `complete` | 某个受边界约束的实施切片已完成并有验证证据 | 后续缺口不再存在 |
| `planned follow-up` | 已定义范围、证据和任务，但尚未实施 | checker、fixtures 或 runtime 行为已落地 |
| `documentation-only` | 只更新文档、计划或记录 | 运行时状态已改变 |

### 3.2 Capability chain

能力开关必须按硬依赖链解释：

```text
subagent_routing != off
  -> oh_my_codex = on
    -> langgraph = on
      -> langgraph_ready = true 时可报告 backend_default=langgraph
```

规则：

- `subagent_routing=off` 时，`oh_my_codex` 与 `langgraph` 必须视为 off。
- `oh_my_codex=off` 时，`langgraph` 必须视为 off。
- `langgraph=on` 要求 `oh_my_codex=on` 且 routing 可用。
- `backend_default=langgraph` 只说明默认 durable backend 可用，不说明当前 task 已采用 durable workflow 或 persistent team。

### 3.3 Workflow 与 team 状态

| 状态 | 最小含义 | 最小证据 |
| --- | --- | --- |
| `not_needed` | 当前任务未达阈值 | activation trace 写明 `threshold_not_met:*` 或 task shape 理由 |
| `candidate` | 可能需要 durable/workers，但尚未启动 | plan/slice 分析、未启动原因 |
| `selected` | 已选择 backend 或 team lane | active selector、preflight、ownership plan |
| `running` | worker 或 workflow 正在执行 | selector、manifest、heartbeat、lifecycle running 记录 |
| `complete` | 运行已完成并被 leader 吸收 | running 证据 + result summary + close/absorbed record |
| `blocked` | 含义：阻塞且不能继续声明成功 | 阻塞原因名称（例如 `backend_not_ready`）、连续阻塞证据、未把阻塞当完成 |

## 4. 运行时治理原则

- Codex 主会话始终是 leader：负责 activation check、角色选择、worker brief、fan-in、证据标注、本地集成和最终汇报。
- Native Codex 是 base layer；oh-my-codex、native_omx、LangGraph、skills 和 profile helpers 是 additive workflow/runtime surfaces。
- 显式 `omx` 或 `LangGraph` 是 hard routing directive；如果不采用，必须写明 named blocker 或 unmet threshold。
- 缺少用户短语不是跳过 collaboration 的理由；有短语也不能跳过 frozen plan、证据守卫或 worker ownership。
- Expert timeout、stall、provider pacing、quiet wait 都是 non-evidence；不能被最终报告引用为已完成结果。
- Research 和 implementation 在开放式任务中保持角色分离；research fan-in 后先冻结 implementation brief，再进入执行。
- Durable task 默认一次只使用一个 backend family；切换 backend 必须记录 close 或 explicit handoff。

## 5. Activation trace 契约

触发时机：

- first substantive work
- reload / restart / resume / continue
- phase change
- `.omx` durable-state detection
- capability-state change
- expert timeout / stall
- 任务扩展到 2+ execution slices
- 用户显式要求 `experts`、`parallel`、`omx`、`LangGraph`、`durable_team` 或 `persistent team`

推荐最小 trace：

```text
Routing trace:
phase=<define-target|read-context|freeze-plan|execute-parallel|integrate-converge|stabilize|verify-accept>
capability_chain=subagent_routing:<auto|manual|off> > oh_my_codex:<on|off> > langgraph:<on|off>
backend_default=<langgraph|native_omx|none>
backend_ready=<true|false|unknown>
experts=<none|analystxN|architect|planner|writer|verifier|blocked:<reason>|...>
durable_workflow=<not_needed|candidate|selected|running|complete|blocked>
persistent_team=<not_selected|not_needed|candidate|selected|running|complete|blocked>
why=<task-shape, threshold, blocker, or evidence reason>
```

禁止理由：

- “用户没有要求并行/子代理”。
- “没有写 experts / durable_team / persistent team，所以不评估”。
- “LangGraph ready，所以 persistent team 已运行”。
- “skill/profile 已调用，所以 native expert 已运行”。

## 6. 自动路由决策矩阵

| 触发场景 | Experts | Durable workflow | Persistent team | 主会话动作 |
| --- | --- | --- | --- | --- |
| 单个低风险文档文件 | 默认不需要；可在收尾使用 verifier | 不需要 | 不需要 | 本地编辑、检查、提交 |
| 大型文档重写 | 可用 writer/verifier；多面研究先 analyst-only | 需要 checkpoint 或 frozen brief 时作为 candidate | 只有 2+ 独立写入切片且 plan 冻结后 | leader-owned integration |
| 有边界的多面研究 | analystxN 首轮同质 fan-out | fan-in 后若进入多阶段实施再评估 | plan 冻结前不启动 | 综合研究、冻结 brief |
| 跨模块架构/接口 | architect，必要时 security-reviewer | candidate | frozen plan + 2+ slices 后 candidate | 写接口和所有权契约 |
| 行为变化型多文件工作 | test-engineer + verifier | candidate | 2+ 独立执行切片时 selected | 本地集成和测试 |
| blocking regression | debugger | 可用 survivor queue | stabilize 阶段 1+ blocking issue 可启动 2 debugger | 收敛修复 |
| 远端发布/合并 | verifier / release reviewer | 通常不需要 | 通常不需要 | 遵守 local-main-first 和远端授权门禁 |

## 7. Durable-team 阈值映射

| 阶段 | Durable / persistent team 决策 | 必须写入 trace 的理由 |
| --- | --- | --- |
| `define-target` | 不启动 | 目标与验收边界未冻结 |
| `read-context` | 不启动；可用 bounded analyst | 上下文读取还不是执行切片 |
| `freeze-plan` | 不启动 | 计划尚未冻结 |
| `execute-parallel` | 2+ mostly independent slices 后 candidate/selected | frozen plan、ownership、disjoint write sets |
| `integrate-converge` | 2+ workers 的结果需要合入时可 selected | leader-owned final integration |
| `stabilize` | 1+ blocking issue 可启动 debugger lane | blocker 证据和收敛目标 |
| `verify-accept` | 不新启动 team；可用 verifier | 收尾验证，不扩大写入面 |

## 8. Expert 生命周期与等待纪律

Native expert lifecycle 必须由 leader 负责：

1. `spawn`：记录 role、agent id、nickname（如有）、task summary、scope、non-goals、ownership。
2. `wait`：使用 bounded wait；初始约 30 秒，review 可到约 60 秒，深度 architect/verifier/research 可到约 120 秒，总等待默认约 180 秒。
3. `timeout/stall/provider_pacing_wait`：标记 non-evidence，并选择 inspect、redirect、respawn narrower task、handoff durable lane 或主会话接管。
4. `result`：只有实际返回的结果才可进入 fan-in。
5. `absorbed`：最终报告引用 result 前，必须记录 leader 已吸收。
6. `close`：completed expert 被吸收后默认关闭；后续需要新工作时重新 spawn。

写入型 worker 必须收到：

- 文件/模块 ownership。
- 不得 revert 或覆盖他人变更。
- 需要报告 changed paths。
- 由 leader 进行最终集成。

## 9. Native agents、skills、profiles 与 follow-up thread 边界

| Surface | 来源 | 可作为 expert evidence 吗 |
| --- | --- | --- |
| Native Codex subagent | user-level 或 repo-local agent TOML | 可以，但必须有 spawn/wait/result/close/absorbed audit |
| Skill | `SKILL.md` | 不可以；它是 workflow instruction surface |
| Plugin profile/helper | plugin 或 profile surface | 不可以；只改变可见过程上下文 |
| LangGraph node | repo-local durable workflow | 不是 native expert；按 LangGraph state evidence 审计 |
| OMX durable worker | native_omx lane | 不是 native expert；按 selector/manifest/heartbeat/lifecycle 审计 |

Follow-up work 默认新建 fresh agent/thread，并传递必要上下文；只有用户明确要求保留线程时才复用。

## 10. Effective lane 选择

| Lane | 适用 | 不适用 |
| --- | --- | --- |
| 主会话本地执行 | 单文件、小范围、低风险、critical path 清楚 | 需要长时间并行或 worker ownership 分离时 |
| Native experts | bounded review、research、debug、verification | 没有可审计 spawn/result 的场景 |
| `native_omx` | worker-centric durable execution、worktree isolation、mailbox flow、直接 worker lifecycle control | 图状阶段、checkpoint approval gates 为主时 |
| LangGraph | graph-shaped multi-phase execution、checkpoint recovery、approval gates、frozen briefs、survivor queues | 简单单切片文档修改 |
| Persistent team | plan 已冻结且有 2+ 独立执行切片，或 stabilize 有 blocking issues | startup、read-context、单文件 edit、证据不足时 |

## 11. 文件职责图

| 文件/目录 | 职责 |
| --- | --- |
| `AGENTS.md` | 当前会话启动与 orchestration authority surface |
| `docs_bilingual/project_startup_summary.*` | cold-start read order、canary 与 repository posture |
| `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.*` | activation policy、capability chain、hard directives、timeout evidence |
| `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.*` | 本 active baseline 与后续 Phase 4 实施计划 |
| `openspec/specs/codex-user-level-orchestration-activation-policy/spec.md` | 稳定 OpenSpec 能力要求 |
| `tools/check_orchestration_activation_policy.py` | activation policy 文本和 forbidden reason guard |
| `tools/check_orchestration_trace_evidence.py` | trace evidence validator |
| `tools/check_capability_switch_chain.py` | capability dependency chain guard |
| `tools/check_role_routing_directive_evidence.py` | hard directive 与 role-routing evidence guard |
| `tools/check_agent_skill_profile_surface_boundaries.py` | native agent / skill / profile 边界 guard |
| `tools/check_expert_lifecycle_wait_pacing_evidence.py` | expert wait/pacing evidence guard |
| `tools/check_delegation_wait_discipline_evidence.py` | delegation 和 wait discipline guard |
| `tools/check_durable_artifact_state_surfaces.py` | durable artifact/state surface guard |
| `tools/check_effective_lane_fit_evidence.py` | backend family 与 task-fit evidence guard |
| `tools/check_fanout_write_ownership_evidence.py` | fan-out、写入 ownership 与 one-backend-family guard |
| `tools/check_leader_session_scope_evidence.py` | main-session leader 和 no separate persistent leader pane guard |
| `tools/run_openspec_guard.py` | 仓库级 OpenSpec / governance guard 汇总入口 |
| `tools/ci/ci_test_manifest.json` | local gate 测试登记 |

## 12. 已完成 baseline

### 12.1 Phase 0-3 完成状态

| Phase | 状态 | 已完成结果 |
| --- | --- | --- |
| Phase 0：记录并保护计划 | complete | 注册本 active implementation plan；忽略本地 transcript；保持 canary guard 与 `.gitignore` 一致 |
| Phase 1：Policy surfaces | complete | 更新 `AGENTS.md`、startup summary、activation policy、team-mode、quick-reference 与 LangGraph policy surfaces |
| Phase 2：Script-backed enforcement | complete for planned baseline | 增加 capability chain、trace evidence、expert timeout、role routing、surface boundary、leader scope、delegation、durable artifact、lane fit、fan-out ownership 等 checkers/tests |
| Phase 3：Runtime integration | implemented as source-of-truth and generated-template enforcement | 生成式用户级 team-mode templates 携带全局自动协同默认规则；LangGraph-ready 会话必须报告默认 backend |

### 12.2 已归档实施切片

| 归档路径 | 用途 |
| --- | --- |
| `openspec/changes/archive/2026-05-11-enforce-automatic-orchestration-routing/` | 自动协同路由 baseline。 |
| `openspec/changes/archive/2026-05-11-enforce-active-selector-status-helper/` | active selector 状态 helper。 |
| `openspec/changes/archive/2026-05-12-enforce-hard-routing-directive-adoption/` | hard routing directive adoption。 |
| `openspec/changes/archive/2026-05-13-enforce-capability-switch-chain/` | capability switch chain。 |
| `openspec/changes/archive/2026-05-13-enforce-custom-agent-toml-schema/` | custom agent TOML schema。 |
| `openspec/changes/archive/2026-05-13-enforce-expert-lifecycle-wait-pacing-evidence/` | expert lifecycle wait/pacing evidence。 |
| `openspec/changes/archive/2026-05-13-enforce-orchestration-trace-evidence-validator/` | orchestration trace evidence validator。 |
| `openspec/changes/archive/2026-05-13-extend-orchestration-activation-checker-coverage/` | activation checker coverage extension。 |
| `openspec/changes/archive/2026-05-14-enforce-agent-skill-profile-surface-boundaries/` | agent / skill / profile surface boundaries。 |
| `openspec/changes/archive/2026-05-14-enforce-delegation-wait-discipline/` | delegation wait discipline。 |
| `openspec/changes/archive/2026-05-14-enforce-durable-artifact-state-surfaces/` | durable artifact and state surfaces。 |
| `openspec/changes/archive/2026-05-14-enforce-effective-lane-fit-evidence/` | effective lane-fit evidence。 |
| `openspec/changes/archive/2026-05-14-enforce-fanout-write-ownership-evidence/` | fan-out write ownership evidence。 |
| `openspec/changes/archive/2026-05-14-enforce-leader-session-scope-evidence/` | leader session scope evidence。 |
| `openspec/changes/archive/2026-05-14-enforce-orchestration-checker-ci-coverage/` | orchestration checker CI coverage。 |
| `openspec/changes/archive/2026-05-14-enforce-role-directive-routing-evidence/` | role directive routing evidence。 |
| `openspec/changes/archive/2026-05-15-harden-global-automatic-collaboration-default/` | global automatic collaboration default hardening。 |

### 12.3 已完成但仍需保持的边界

- Native `spawn_agent` 仍受 live platform/tool contract 约束；阻塞时写 `experts=blocked:platform_subagent_invocation_constraint`。
- LangGraph ready 不等于 persistent team running。
- 用户级安装产物需要 installer refresh 才能同步 source-template 变化。
- 每个具体任务仍需 activation trace、threshold evidence 和适用的 checker-backed evidence。

## 13. Phase 4 实施包定义

Phase 4 不重开 Phase 0-3；它只处理提示词无关协同一致性、evidenceguard、expert lifecycle audit、LangGraph release 和 cold-start read-order evidence 缺口。

| 项 | 决定 |
| --- | --- |
| Change id | `enforce-prompt-independent-collaboration-parity` |
| 推荐分支 | `enforce-prompt-independent-collaboration-parity` |
| 推荐 worktree | `.worktrees/enforce-prompt-independent-collaboration-parity` |
| 目标 | 证明自动协同由 task shape / threshold / blocker 决定，不由用户是否写协同短语决定 |
| 必须新增证据面 | prompt-independent fixtures、cold-start read-order ledger、durable/persistent evidenceguard、expert lifecycle JSONL、LangGraph stale-running release checker |
| 非目标 | 不把 skills/profile 当 expert；不 startup auto-launch team；不把 backend ready 当 team running |
| 验收出口 | 新检查器接入 `tools/run_openspec_guard.py` 与 `tools/ci/ci_test_manifest.json`，local gate 与 local MR review 通过 |

## 14. 过程组式运营模型

| 过程组 | 输入 | 工具与技术 | 输出 |
| --- | --- | --- | --- |
| 启动 | 会话复盘、当前治理政策、用户对自动协同的确认、已归档 Phase 0-3 | 问题框定、证据缺口分析、非目标审查 | OpenSpec proposal、验收标准、明确的非声明边界 |
| 规划 | OpenSpec change、文件地图、checker 模式、fixture 要求 | 切片拆分、owner mapping、test-first design、timeout budget review | 冻结实施计划、独立任务、验证矩阵 |
| 执行 | 冻结计划、feature worktree、OpenSpec delta、测试夹具 | TDD、Python checkers、JSON/JSONL fixtures、guard wiring、bounded expert review | 检查器、测试、治理文档更新、changed-path list |
| 监控与控制 | 测试输出、guard 输出、routing fixtures、lifecycle records | Diff review、OpenSpec guard、local CI、verifier review、缺陷分诊 | 已接受修复、被拒绝的虚假声明、剩余风险清单 |
| 收尾 | 通过的 gates、干净分支、docs registry、OpenSpec archive 候选 | 本地 MR review、archive 决策、经验教训 | merge-ready 分支、archive 或延期证据、后续 backlog |

## 15. Evidence contracts

### 15.1 Cold-start read-order evidence

当会话声称按 cold-start read order 继续时，必须生成结构化 evidence。建议 fixture 路径：

```text
test/fixtures/cold_start_read_order_evidence/
  valid_single_file_doc_update.json
  valid_task_specific_skip_with_reason.json
  invalid_missing_startup_summary.json
  invalid_skipped_file_without_reason.json
  invalid_activation_trace_only.json
  invalid_read_order_used_as_runtime_evidence.json
```

最小字段：

| 字段 | 用途 |
| --- | --- |
| `case_id` | 标识当前 fixture。 |
| `trigger` | 记录触发 cold-start read-order evidence 的原因。 |
| `read_order_source.path` | 指向 read order 的权威来源。 |
| `startup_summary_pair.english_primary` | 记录英文 startup summary 主文件。 |
| `startup_summary_pair.chinese_companion` | 记录中文伴随文件。 |
| `startup_summary_pair.utf8_explicit_read` | 证明使用 UTF-8 读取而非复制乱码。 |
| `read_order_evidence.items[]` | 保存逐项 read ledger。 |
| `order_index` | 记录 read-order 顺序。 |
| `path` | 记录被读取或跳过的文件路径。 |
| `decision=read|skipped` | 记录该项是读取还是跳过。 |
| `read_mode` | 字段含义：记录读取模式，例如 `full_text_utf8`、`task_relevant_sections` 或 `not_applicable`。 |
| `needed_for_current_task` | 标明该项是否为当前任务必要上下文。 |
| `reason` | 解释读取或跳过原因。 |
| `summary_counts.read` | 统计 read 项。 |
| `summary_counts.skipped` | 统计 skipped 项。 |
| `summary_counts.read_order_total_considered` | 统计本次纳入判断的 read-order 总数。 |
| `openspec_list` | 记录 `openspec list --json` 结果。 |
| `worktree_preflight.local_main_not_behind_gitlab_main` | 证明本地 main 不落后。 |
| `worktree_preflight.feature_worktree` | 记录 feature worktree 路径。 |
| `activation_trace_ref.present` | 证明 activation trace 单独存在。 |
| `runtime_evidence_refs.native_experts|durable_team|persistent_team` | 记录实际 runtime evidence 引用，空数组表示未使用。 |
| `evidence_boundary=context_reading_only_not_expert_or_team_runtime_evidence` | 防止把读取证据误当 worker 运行证据。 |

失败条件：

- 缺少 startup summary 读取记录。
- 跳过 read-order 项但没有 reason。
- 只有 activation trace，没有 read-order ledger。
- 当 `summary_counts.read + summary_counts.skipped != read_order_total_considered` 时失败。
- 把 read-order evidence 声称为 expert/durable/persistent runtime evidence。

### 15.2 Prompt-independent activation parity

成对 fixture 必须共享 `task_shape_id`，只允许 `prompt_features.explicit_collaboration_phrase` 不同：

```text
test/fixtures/orchestration_prompt_independent_collaboration_parity/
  same_task_without_phrase.json
  same_task_with_phrase.json
```

比较字段：

| 字段 | 用途 |
| --- | --- |
| `expected_decision.phase` | 比较任务阶段判断。 |
| `expected_decision.experts_now` | 比较 expert need 决策。 |
| `expected_decision.durable_workflow` | 比较 durable workflow 决策。 |
| `expected_decision.persistent_team_threshold` | 比较 persistent team 阈值结果。 |
| `expected_decision.backend_default` | 比较默认 durable backend。 |
| `expected_decision.claim_boundary` | 比较证据声明边界。 |

通过条件：同一 `task_shape_id` 的有短语/无短语 fixtures 在上述字段上相同。显式短语只能让 trace 标注 `directive_seen=true`，不能把未达阈值的任务宣称为 `persistent_team=running`。

### 15.3 Durable / persistent evidenceguard

| 声明状态 | 最小证据 |
| --- | --- |
| `not_needed` | activation trace 说明未达阈值，例如 `threshold_not_met:single_execution_slice` |
| `candidate` | frozen plan 或切片分析，以及为何尚未启动 |
| `selected` | active selector、backend family、preflight 通过记录、worker ownership plan |
| `running` | active selector、team manifest、worker heartbeat、worker lifecycle `started/running` 记录 |
| `complete` | `running` 所需证据 + closed agent record + result summary + leader absorbed record |
| `blocked` | 含义：阻塞状态需要阻塞原因名称（例如 `preflight_failed`）、最近三次阻塞证据、未把阻塞结果当完成 |

建议 fixtures：

```text
test/fixtures/durable_persistent_evidence_guard/
  invalid_running_missing_heartbeat/
  valid_complete_team/
```

### 15.4 Expert lifecycle audit

建议 JSONL 路径：`.omx/state/experts/lifecycle.jsonl`，测试夹具使用同名相对路径。

每行最小字段：

| 字段 | 用途 |
| --- | --- |
| `event=spawn|wait|timeout|stall|provider_pacing_wait|result|close|absorbed` | 记录生命周期事件类型。 |
| `timestamp` | 记录事件发生时间。 |
| `agent_id` | 绑定同一 expert 的事件流。 |
| `role` | 记录 expert 角色。 |
| `nickname` | 可空；最终报告使用昵称时必须存在。 |
| `task_summary` | 记录委派任务摘要。 |
| `status` | 记录事件状态。 |
| `evidence_disposition` | 区分 accepted evidence 与 non-evidence。 |

顺序要求：

1. `spawn` 必须先于同一 `agent_id` 的其他事件。
2. `result` 被最终报告引用时，必须有同一 `agent_id` 的 `absorbed`。
3. `timeout/stall/provider_pacing_wait` 只能产生 non-evidence disposition。
4. `close` 后不得继续写同一 `agent_id` 的新 `result`；需要继续时必须新 `spawn`。

### 15.5 LangGraph state release

repo-local LangGraph state 不得在完成后无解释地残留 `running`。

最小字段：

| 字段 | 用途 |
| --- | --- |
| `thread_id` | 标识 LangGraph thread。 |
| `workflow_id` | 标识 durable workflow。 |
| `status=running|complete|released|closed|blocked` | 记录状态枚举。 |
| `active_work` | 标记是否仍有活动工作。 |
| `last_heartbeat_at` | 记录最近 heartbeat。 |
| `completion_marker` | 记录完成标记。 |
| `release_marker` | 记录释放标记。 |
| `continue_reason` | 解释仍为 running 的原因。 |

失败条件：closeout evidence 表示完成，但 `status=running` 且 `release_marker=null` 且 `continue_reason` 为空。

通过条件：

- active work 仍在运行且 heartbeat 新鲜；或
- work 已完成，state 为 `complete/released/closed`；或
- state 仍 `running`，但有 release deferral 与未完成 work 证据。

## 16. 实施切片

### Slice 0：OpenSpec change 与证据契约冻结

- [ ] 新建 `openspec/changes/enforce-prompt-independent-collaboration-parity/proposal.md`。
- [ ] 新建 `openspec/changes/enforce-prompt-independent-collaboration-parity/tasks.md`。
- [ ] 新建 `openspec/changes/enforce-prompt-independent-collaboration-parity/specs/codex-user-level-orchestration-activation-policy/spec.md`。
- [ ] 运行 `openspec validate enforce-prompt-independent-collaboration-parity --strict`。

### Slice 1：Cold-start read-order evidence guard

- [ ] 新建 `tools/check_cold_start_read_order_evidence.py`。
- [ ] 新建 `test/check_cold_start_read_order_evidence.test.py`。
- [ ] 新建 `test/fixtures/cold_start_read_order_evidence/` 下正反例。
- [ ] 接入 `tools/run_openspec_guard.py` 与 `tools/ci/ci_test_manifest.json`。

### Slice 2：Prompt-independent collaboration parity checker

- [ ] 新建 `tools/check_orchestration_prompt_independent_collaboration_parity.py`。
- [ ] 新建 `test/check_orchestration_prompt_independent_collaboration_parity.test.py`。
- [ ] 新建 `test/fixtures/orchestration_prompt_independent_collaboration_parity/` 成对 fixtures。
- [ ] 验证同一 task shape 有/无短语的 routing decision class 一致。

### Slice 3：Durable / persistent evidenceguard

- [ ] 新建 `tools/check_durable_persistent_evidence_guard.py`。
- [ ] 新建 `test/check_durable_persistent_evidence_guard.test.py`。
- [ ] 新建 `test/fixtures/durable_persistent_evidence_guard/invalid_running_missing_heartbeat/`。
- [ ] 新建 `test/fixtures/durable_persistent_evidence_guard/valid_complete_team/`。

### Slice 4：Expert lifecycle audit

- [ ] 新建 `tools/check_expert_lifecycle_audit.py`。
- [ ] 新建 `test/check_expert_lifecycle_audit.test.py`。
- [ ] 新建 `test/fixtures/expert_lifecycle_audit/valid_absorbed_result/lifecycle.jsonl`。
- [ ] 新建 `test/fixtures/expert_lifecycle_audit/invalid_timeout_as_evidence/lifecycle.jsonl`。

### Slice 5：LangGraph state release checker

- [ ] 新建 `tools/check_langgraph_state_release.py`。
- [ ] 新建 `test/check_langgraph_state_release.test.py`。
- [ ] 新建 `test/fixtures/langgraph_state_release/valid_active_running/`。
- [ ] 新建 `test/fixtures/langgraph_state_release/valid_released_complete/`。
- [ ] 新建 `test/fixtures/langgraph_state_release/invalid_completed_still_running/`。

### Slice 6：文档、guard wiring 与收尾

- [ ] 修改 `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md`。
- [ ] 修改 `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md`。
- [ ] 修改本计划英文主版和中文伴随版。
- [ ] 按需更新 `docs_bilingual/docs_registry.yaml`。
- [ ] 运行聚焦测试、OpenSpec guard、local gate 与 local MR review。

## 17. 任务级执行 Backlog

### Task A：冻结 Phase 4 OpenSpec WHAT

**输入**：本文第 13-16 节、已归档 Phase 0-3、activation policy stable spec。
**工具与技术**：OpenSpec proposal、delta spec、strict validation。
**输出**：`enforce-prompt-independent-collaboration-parity` active change，明确 scope/non-goals/acceptance。

### Task B：实现 cold-start read-order evidence guard

**输入**：startup summary read order、worktree policy、fixture schema。
**工具与技术**：TDD、JSON schema-like validation、negative fixtures。
**输出**：checker、unit test、fixtures、guard/CI wiring。

### Task C：实现提示词无关一致性 checker

**输入**：同一 task shape 的有短语/无短语 prompts。
**工具与技术**：fixture grouping、decision field comparison、fail-closed diagnostics。
**输出**：parity checker 和成对 fixtures。

### Task D：实现 durable/persistent evidenceguard

**输入**：selector、manifest、heartbeat、lifecycle、closed/absorbed records。
**工具与技术**：repo-local state fixture traversal、claim-state matrix validation。
**输出**：缺证据时拒绝 running/complete 声明的 checker。

### Task E：实现 expert lifecycle audit

**输入**：expert lifecycle JSONL、final report refs、timeout/stall/provider pacing records。
**工具与技术**：事件顺序校验、引用完整性校验、non-evidence disposition guard。
**输出**：spawn/wait/timeout/result/close/absorbed 审计 checker。

### Task F：实现 LangGraph release checker

**输入**：repo-local `.omx/state/langgraph/` fixtures、completion/release markers。
**工具与技术**：state transition invariant、fresh heartbeat 判断、release deferral 判断。
**输出**：stale running fail-closed checker。

### Task G：治理文档、验证与本地集成

**输入**：已通过聚焦测试的 checkers、治理文本差异、OpenSpec tasks。
**工具与技术**：`git diff --check`、`openspec validate --all`、pre-commit update/archive check、OpenSpec guard、local gate、local MR review。
**输出**：merge-ready 分支、干净 worktree、本地 main integration package。

## 18. 验证计划

聚焦验证：

```powershell
python .\test\check_cold_start_read_order_evidence.test.py
python .\tools\check_cold_start_read_order_evidence.py --root . --json
python .\test\check_orchestration_prompt_independent_collaboration_parity.test.py
python .\tools\check_orchestration_prompt_independent_collaboration_parity.py --root . --json
python .\test\check_durable_persistent_evidence_guard.test.py
python .\tools\check_durable_persistent_evidence_guard.py --root . --json
python .\test\check_expert_lifecycle_audit.test.py
python .\tools\check_expert_lifecycle_audit.py --root . --json
python .\test\check_langgraph_state_release.test.py
python .\tools\check_langgraph_state_release.py --root . --json
```

集成验证：

```powershell
git diff --check
openspec validate --all
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root .
python .\tools\check_implementation_plan_rules.py --root . --json
.\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600
.\tools\ci\local_mr_review.ps1
```

本次 documentation-only 重构的最小验证：

```powershell
git diff --check
python .\tools\check_implementation_plan_rules.py --root . --json
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root .
```

## 19. 本地集成顺序

- [ ] 从当前本地 `main` 创建 feature worktree。
- [ ] 确认本地 `main` 不落后于 `gitlab/main`。
- [ ] 只在 feature worktree 修改目标文件。
- [ ] 运行最小验证；若改动触达 checker/runtime，再运行完整 local gate。
- [ ] 运行 pre-commit update/archive check。
- [ ] 提交中文 commit message。
- [ ] feature worktree 保持干净。
- [ ] 合入本地 `main`。
- [ ] 不做远端 push / MR / mirror，除非用户另行明确授权。

## 20. 完成复核清单

- [ ] 文档结构符合新版 implementation plan 风格：复核结论、目标、非目标、原则、状态契约、文件职责、切片、任务 backlog、验证、集成、风险。
- [ ] Phase 0-3 与 Phase 4 状态没有混淆。
- [ ] 本文没有宣称 durable/persistent team 已运行。
- [ ] 显式协同短语只作为 directive signal，不作为 task-shape 阈值替代物。
- [ ] Native expert、skill、profile、LangGraph node、OMX worker 的证据边界清楚。
- [ ] 每个 Phase 4 checker 都有目标文件、fixtures、失败条件和验证命令。
- [ ] 所有提交信息使用中文。

## 21. 验收标准

- `AGENTS.md` / startup summary / activation policy 中的自动协同规则可以从本文映射到具体 checker 或 evidence contract。
- 同一 task shape 在有/无显式协同短语时产生同一类 routing decision。
- Cold-start read-order evidence 能证明已读文件、跳过理由、OpenSpec 状态、worktree/session preflight 和 evidence boundary。
- 没有 selector、manifest、heartbeat、lifecycle、closed/absorbed 证据时，durable/persistent running/complete 声明不能通过。
- Expert result 只有在 `absorbed` 后才能被最终报告引用；timeout/stall/provider pacing 永远不是完成证据。
- LangGraph completed work 不残留 stale `running` state；若仍 running，必须有 active work、heartbeat 和 continue reason。
- 新增 checker 接入 `tools/run_openspec_guard.py` 和 `tools/ci/ci_test_manifest.json`。
- 本地验证、local gate 和 local MR review 通过后才合入本地 `main`。

## 22. 需要保留的证据

- 本计划文件及英文主版/中文伴随版的 diff。
- OpenSpec change proposal、tasks、delta spec 与 archive/deferral 记录。
- 新增 checkers 与 tests 的输出。
- `tools/run_openspec_guard.py` 输出。
- `tools/ci/local_gate.ps1` 与 `tools/ci/local_mr_review.ps1` 输出。
- Feature worktree clean status。
- 本地 `main` 合入记录。

## 23. 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 小任务过度启动 workers | 严格区分 backend ready 与 team launch threshold |
| 把文档阅读证据误当 runtime evidence | `evidence_boundary` 必填并由 checker 拒绝误用 |
| 把 skills/profile 当 expert | 只接受 native spawn/wait/result/close/absorbed audit |
| LangGraph running 状态误报 | 要求 heartbeat、active work、continue reason 或 release marker |
| checker 过度依赖 chat transcript | 以结构化 fixtures 和 repo-local state 为主，transcript 只做 claim source |
| 并行写入互相覆盖 | 要求 ownership、disjoint write sets、hotspot serialization 与 leader-owned final integration |
| 上游 pacing 被误判为失败或成功 | 标记 provider backpressure，继续 bounded wait 或主会话接管，不作为结果证据 |

## 24. 回滚规则

- 文档重构回滚：`git revert <commit>`，不删除历史 OpenSpec archive。
- Phase 4 checker 误报：先从 `tools/run_openspec_guard.py` 临时移除对应 checker，并保留 fixtures 用于修复；不得删除治理要求或放行虚假 team 声明。
- LangGraph release checker 误伤真实 running work：补充 heartbeat freshness、active work 和 release deferral fixture，再恢复 guard。
- Expert lifecycle checker 误判：补齐 `final_report_refs.json` 与 lifecycle JSONL 的引用关系，不把 timeout 改成 success。
- 远端发布不在本文默认回滚范围；需要另行用户授权。

## 25. 参考源

- `AGENTS.md` - 仓库与用户级 Codex instruction surface。
- `docs_bilingual/project_startup_summary.md` - 英文 cold-start read order 与 repository posture。
- `docs_bilingual/project_startup_summary.zh-CN.md` - 中文 companion 与 UTF-8/canary 边界。
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` - 英文 activation policy 权威文本。
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md` - 中文 activation policy companion。
- `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md` - worktree/session/mainline safety policy。
- `docs_bilingual/governance/openspec_usage_convention.md` - OpenSpec 使用约定。
- `docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` - 新版 implementation plan 结构参考。
- `docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md` - Comet runtime 方案结构参考。
