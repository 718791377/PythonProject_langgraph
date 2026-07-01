---
doc_id: automatic_orchestration_routing_enforcement_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.md
translation_of: docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.md
version: 1.0
status: active
plan_readiness: ready-for-implementation
doc_class: implementation_plan
owner: codex-orchestration
implementation_lane: prompt_independent_collaboration_parity
last_reviewed: 2026-05-28
---

# 自动协同路由强制化实施方案

> **For agentic workers:** REQUIRED WORKFLOW: 使用完整 `/comet` 节奏处理后续代码落地；文档更新本身不等于 runtime evidence。所有任务用 checkbox 跟踪，先完成任务内验证，再进入下一任务；所有提交信息使用中文。

**Goal:** 让 Codex 会话不依赖用户是否写出“use experts / durable_team / persistent team”等短语，而是根据任务形态、风险、阶段、证据和阈值自动评估并采用最小充分协作面。

**Architecture:** 主 Codex 会话始终是 leader。activation check 读取启动上下文、能力链、任务阶段和 durable state；随后决定 main-session、native experts、`native_omx`、LangGraph durable workflow 或 persistent team 的最小充分组合；最终所有声明必须落到可审计 evidence。

**Tech Stack:** Codex startup policy、AGENTS.md、OpenSpec、Comet workflow、Python checkers、JSON/JSONL fixtures、`.omx` repo-local state、local CI、local MR review、中文提交与 local-main-first 发布流。

---

## 0. 本次复核结论

旧版文件虽然已经压缩历史内容，但仍然像“治理规则合集”：章节按 policy topic 排列，缺少新版 implementation plan 所需的 worker-ready 任务、输入输出、文件职责、验证边界和回滚路径。本版按 `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` 与 `comet_runtime_agile_focus_area_plan.zh-CN.md` 的新版结构重写为可执行方案。

| 检查项 | 结论 | 本版落点 |
| --- | --- | --- |
| 目标与非目标 | 完整 | 第 2 节 |
| experts / durable_team / persistent team 关系 | 完整 | 第 1 节 |
| Codex 如何触发自动协同 | 完整 | 第 3、4 节 |
| repo-local source of truth | 完整 | 第 5 节 |
| evidence contracts | 补齐 | 第 6 节 |
| 任务级颗粒度 | 补齐 | 第 7 节 |
| readiness gates | 补齐 | 第 8 节 |
| 验证与本地集成 | 补齐 | 第 9 节 |
| rollback / cleanup | 补齐 | 第 10 节 |
| 对现有治理方案的更新要求 | 补齐 | 第 11 节 |

当前状态判定：

- 本文是 `status: active` 的实施方案和后续 Phase 4 工作边界，不是 durable/persistent runtime evidence。
- Phase 0-3 baseline 已有历史实现与归档证据；本文仅保留其稳定边界，不再把历史归档列表放在主流程中。
- Phase 4 默认 change id 为 `enforce-prompt-independent-collaboration-parity`；P1 checker 切片通过 `tools/check_orchestration_collaboration_evidenceguard.py`、fixture pairs、guard wiring、CI registration 与 OpenSpec/spec updates 落地。
- 单文件或双语文档对重构不满足 persistent team 阈值；此类任务应由主会话直接执行，可在收尾时使用 verifier，但不能宣称 durable/persistent team 已运行。

## 1. 关系模型与命名边界

| 名称 | 本方案中的角色 | 可作为运行证据吗 | 边界 |
| --- | --- | --- | --- |
| 主 Codex 会话 | leader、集成者、证据吸收者 | 可以，作为最终责任主体 | 不被 persistent leader pane 替代 |
| native expert | leader-side 专家线程 | 只有存在 spawn / wait / result / close / absorbed audit 时可以 | skill 或 profile 调用不等于 expert |
| `native_omx` | worker-centric durable lane | 需要 selector、manifest、heartbeat、worker lifecycle | 适合 worker lifecycle、worktree isolation、mailbox flow |
| LangGraph | graph-shaped durable workflow lane | 需要 thread state、checkpoint、brief、release record | ready 不等于 running persistent team |
| persistent team | threshold-gated worker team | 需要 active selector、manifest、heartbeat、closed/absorbed record | frozen plan + 2+ 独立执行切片，或 stabilize 有 blocking issue |
| skills / plugin profiles | workflow instruction surface | 不可以 | 只改变可见过程上下文，不构成 expert evidence |
| OpenSpec / Comet | WHAT/HOW 治理流 | 是变更治理证据，不是 worker 运行证据 | 不能替代 runtime audit |

能力链必须按硬依赖解释：

```text
subagent_routing != off
  -> oh_my_codex = on
    -> langgraph = on
      -> langgraph_ready = true 时才可报告 backend_default=langgraph
```

禁止推导：

- `backend_ready=true` 不能推导 persistent team running。
- `skill invoked` 不能推导 native expert running。
- `timeout`、`stall`、`provider pacing` 不能推导 expert returned evidence。
- 用户没有写协作短语不能作为跳过 orchestration activation 的理由。

## 2. 目标与非目标

目标：

1. 在 first substantive work、resume、continue、phase change、`.omx` state detection、capability change、expert timeout/stall、2+ slices expansion 时自动运行 activation check。
2. 让同一任务在有无“use experts / durable_team / persistent team”短语时获得相同路由判断。
3. 区分 `not_needed`、`candidate`、`selected`、`running`、`complete`、`blocked`；其中 `blocked` 明确表示存在命名阻塞且不能宣称成功，避免把 readiness、计划或超时误报成完成。
4. 对 native expert 生命周期、durable/persistent evidence、LangGraph stale-running release、cold-start read order 和 write ownership 形成 checker-backed evidence。
5. 保持 local-main-first：本地验证、本地 MR review、合入本地 `main`；远端发布另需明确授权。

非目标：

- 不把每个小任务都强制变成 multi-worker execution。
- 不在 startup、read-context、boundary-freeze 或单一低风险文档任务中自动启动 persistent team。
- 不把 LangGraph 默认 ready 状态写成 persistent team 已运行。
- 不把本文档本身当成 runtime evidence。
- 不重写 native Codex、oh-my-codex、OpenSpec 或 LangGraph 的基础架构。
- 不推送 GitLab/GitHub；远端发布必须另有当前用户明确授权。

## 3. 运行时架构

```text
User request
  -> Codex leader reads startup authority and task context
  -> Orchestration activation check
  -> Capability chain and backend readiness inspection
  -> Task phase and slice count classification
  -> Evidence threshold evaluation
  -> Smallest sufficient lane decision
  -> Execution / delegation / durable workflow / main-session takeover
  -> Verification, fan-in, close, absorbed record
  -> Local commit, local gate, local MR review, local main integration
```

最小状态词：

| 状态 | 含义 | 最小证据 |
| --- | --- | --- |
| `not_needed` | 当前任务未达阈值 | trace 写明 `threshold_not_met:*` 或 task-shape reason |
| `candidate` | 可能需要协作，但尚未采用 | slice analysis、未采用原因、待满足条件 |
| `selected` | 已选择 lane | selector / preflight / ownership plan |
| `running` | worker 或 workflow 正在执行 | selector、manifest 或 thread state、heartbeat、lifecycle running |
| `complete` | 运行完成并被吸收 | result summary、close record、leader absorbed record |
| blocked（阻塞态） | 存在命名阻塞，不能继续声明成功 | 明确 blocker 名称、连续阻塞证据、且未把阻塞当完成 |

推荐 activation trace：

```text
Routing trace:
phase=<define-target|read-context|freeze-plan|execute-parallel|integrate-converge|stabilize|verify-accept>
capability_chain=<subagent_routing/oh_my_codex/langgraph state chain>
backend_default=<langgraph|native_omx|none>
backend_ready=<true|false>
experts=<none|analystxN|architect|planner|writer|verifier|blocked:<reason>|...>
durable_workflow=<not_needed|candidate|selected|running|complete|blocked>
persistent_team=<not_needed|candidate|selected|running|complete|blocked>
main_session_escalation=<not_needed|preflight|pending_approval|granted|timed_out|blocked>
approval_timeout_risk=<none|low|medium|high|expired>
approval_receipt=<none|receipt id or repo-local artifact path>
why=<task-shape, threshold, blocker, or evidence reason>
```

该 recommended activation trace 是用于用户可见性与日志/checker 稳定性的普通文本诊断行/块，不是 Codex CLI 进度面板。`Updated Plan` 才是进度面板表面；Markdown checkbox 只继续作为 implementation plan 内部任务追踪。

## 4. Codex 中的使用方式

自然语言触发示例：

```text
检查这个方案是否完整
更新这个 implementation plan 并合入本地 main
继续当前任务
使用 experts / durable_team / persistent team 协同处理
用 LangGraph 继续这个多阶段工作
```

行为规则：

- 普通单文档改写：必须运行 activation check，但通常报告 `persistent_team=not_selected:threshold_not_met:single_execution_slice`，由主会话直接执行。
- 明确 experts：若 native spawn tool 不可用，报告 `experts=blocked:platform_subagent_invocation_constraint`，不能伪造专家结果。
- 明确 `omx`：若任务没有 frozen plan + 2+ slices，报告 unmet threshold；若满足则使用 `omx-team-auto.ps1` 或对应 native_omx lane。
- 明确 LangGraph：若任务是 graph-shaped multi-phase 且 ready，选择 LangGraph；若只是单文档 edit，报告不满足 durable workflow 阈值。
- timeout / stall：只能触发 inspect、redirect、respawn、handoff 或 main-session takeover，不能写入成功结论。

## 5. Repo-local source of truth

| 文件或目录 | 职责 |
| --- | --- |
| `AGENTS.md` | 当前会话与项目级 orchestration authority surface |
| `docs_bilingual/project_startup_summary.*` | cold-start read order、canary、repository posture |
| `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.*` | activation policy、capability chain、hard directives、timeout evidence |
| `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.*` | 本实施方案和后续 Phase 4 任务边界 |
| `openspec/specs/codex-user-level-orchestration-activation-policy/spec.*` | 稳定 WHAT requirements |
| `tools/check_orchestration_activation_policy.py` | authority wording 与 forbidden reason guard |
| `tools/check_orchestration_trace_evidence.py` | trace evidence validator |
| `tools/check_orchestration_collaboration_evidenceguard.py` | prompt-independent collaboration parity、cold-start read-order evidence、durable/persistent evidenceguard、expert lifecycle audit events 与 LangGraph state release guard |
| `tools/check_capability_switch_chain.py` | capability dependency guard |
| `tools/check_role_routing_directive_evidence.py` | hard directive 与 role-routing evidence guard |
| `tools/check_expert_lifecycle_wait_pacing_evidence.py` | expert lifecycle wait/pacing guard |
| `tools/check_agent_skill_profile_surface_boundaries.py` | native agent / skill / profile 边界 guard |
| `tools/check_durable_artifact_state_surfaces.py` | durable artifact/state surface guard |
| `tools/check_effective_lane_fit_evidence.py` | backend family 与 task-fit evidence guard |
| `tools/check_fanout_write_ownership_evidence.py` | write ownership 与 one-backend-family guard |
| `tools/check_leader_session_scope_evidence.py` | main-session leader scope guard |
| `tools/run_openspec_guard.py` | 仓库级 guard 汇总入口 |
| `tools/ci/ci_test_manifest.json` | local gate 测试登记 |

## 6. Evidence contracts

### 6.1 Cold-start read-order evidence

目标：当会话声称按 cold-start read order 继续时，必须能说明读取了哪些文件、跳过哪些文件、为什么跳过。

最小字段：

```json
{
  "schema_version": 1,
  "session_id": "...",
  "trigger": "first_substantive_work|resume|continue|phase_change",
  "read_order": [
    {"order_index": 1, "path": "docs_bilingual/project_startup_summary.md", "decision": "read", "read_mode": "full_text_utf8", "needed_for_current_task": true, "reason": "startup authority"}
  ],
  "summary_counts": {"read": 1, "skipped": 0}
}
```

拒绝条件：缺少 startup summary、跳过项无 reason、声称 full read 但没有路径、读取结果包含 mojibake 且未触发恢复动作。Checker surface：`tools/check_orchestration_collaboration_evidenceguard.py` 校验已保存的 `cold_start_read_order` JSON evidence。

### 6.2 Prompt-independent activation parity

目标：相同任务在“有协作短语”和“无协作短语”两种输入下必须得到同等 routing decision。

fixture 组：

```text
test/fixtures/orchestration_prompt_independent_collaboration_parity/
  doc_update_without_collaboration_phrase.json
  doc_update_with_collaboration_phrase.json
  multi_slice_without_collaboration_phrase.json
  multi_slice_with_collaboration_phrase.json
  explicit_omx_without_threshold.json
  explicit_langgraph_single_slice.json
```

拒绝条件：把“用户没有要求 parallel/subagents”写成 skip reason；有协作短语时无视 frozen-plan 和 slice 阈值；LangGraph ready 被写成 persistent team running。Checker surface：`tools/check_orchestration_collaboration_evidenceguard.py` 校验 `test/fixtures/orchestration_prompt_independent_collaboration_parity/` 下的 prompt-independent collaboration parity fixture pairs。

### 6.3 Durable / persistent evidenceguard

目标：没有 durable 证据时，最终汇报不能宣称 durable/persistent team 已运行。

| 状态 | 必需证据 |
| --- | --- |
| `selected` | active selector、backend family、preflight 通过、ownership plan |
| `running` | selected 证据 + team manifest 或 LangGraph thread state + heartbeat/lifecycle running |
| `complete` | running 证据 + result summary + close record + leader absorbed record |
| blocked（阻塞态） | 明确 blocker 名称、连续阻塞证据、且未把阻塞结果当完成 |

拒绝条件：只有 plan、skill invocation、timeout、branch name 或 `.omx` 目录存在就声明 team ran。Checker surface：`tools/check_orchestration_collaboration_evidenceguard.py` 在接受 selected、running 或 complete team 声明前校验 durable/persistent evidenceguard records。

### 6.4 Expert lifecycle audit

目标：native expert 的每个关键事件都可审计。

JSONL 事件：

```json
{"event":"spawn","role":"verifier","task_summary":"...","scope":["..."],"non_goals":["..."]}
{"event":"wait","agent_id":"...","wait_seconds":30}
{"event":"timeout","agent_id":"...","classification":"non-evidence"}
{"event":"result","agent_id":"...","summary":"...","changed_paths":[]}
{"event":"absorbed","agent_id":"...","leader_decision":"accepted"}
{"event":"close","agent_id":"...","retention_policy":"close"}
```

拒绝条件：timeout 当结果、未 close 却声称 retention policy applied、最终报告引用未 absorbed 的结果。Checker surface：`tools/check_orchestration_collaboration_evidenceguard.py` 校验结构化 expert lifecycle audit events；`tools/check_expert_lifecycle_wait_pacing_evidence.py` 继续校验文本 run-summary evidence。

### 6.5 LangGraph state release

目标：LangGraph thread 在任务完成后不能长期残留 `running`。

最小规则：

- 完成时写入 `completed_at`（完成时间）、`final_phase`（最后 graph 阶段）、`result_summary`（已吸收结果摘要）、`released_by`（释放状态的 actor/helper）。
- 如果切换到 native_omx 或主会话接管，写入 `handoff_at`、`handoff_target`、`reason`。
- stale `running` 必须被 checker 标记为 release gap，不能作为活跃工作证据；`tools/check_orchestration_collaboration_evidenceguard.py` 校验 LangGraph state release evidence，并拒绝已完成工作仍保留 `running` 的状态。

## 7. 实施任务拆分

### Task 0：冻结 OpenSpec / Comet 边界

范围：
- 确认本次只是文档结构重构，或在后续代码落地时打开 `enforce-prompt-independent-collaboration-parity` change。
- 记录不启动 persistent team 的原因：单一双语文档对，未达到 2+ 独立执行切片。

完成标准：
- 本文档 front matter、目标、非目标、readiness 明确。
- 本地 feature worktree 有 receipt / claim。

验证：
- `openspec list --json` —— 检查 active OpenSpec change 状态，再冻结边界。
- `git status --short --branch` —— 确认 feature worktree 与分支隔离。

提交示例：`文档：冻结自动路由方案新版结构边界`

### Task 1：重写新版中文 implementation plan

范围：
- 把旧版历史规则合集改成本文结构。
- 保留核心治理语义，但删除主流程中的冗长历史归档表。
- 明确本文不是 runtime evidence。

完成标准：
- 章节顺序与新版参考方案一致。
- 所有 Task 都有范围、完成标准、验证、中文提交示例。
- 文件中不含 mojibake 文本。

验证：
- 人工检查标题结构。
- 常见 GBK/UTF-8 乱码标记与 Unicode replacement character 检查不返回正文命中。

提交示例：`文档：重写自动路由中文实施方案结构`

### Task 2：同步英文 primary

范围：
- 将中文方案同步为 ASCII English primary。
- 保持 doc_id、canonical、translation_of 和章节语义对应。

完成标准：
- 英文文件只含 ASCII 字符。
- 英文版不是旧版摘要，而是完整 companion。

验证：
- `python .\tools\check_document_pair_policy.py --root . --json` —— 验证双语配对与 ASCII English primary 要求。
- 自定义 ASCII 扫描无 non-ASCII。

提交示例：`文档：同步自动路由英文实施方案`

### Task 3：双语配对与 implementation-plan rules 验证

范围：
- 验证双语文件配对、registry 规则和 active plan 引用。

完成标准：
- document pair policy 通过。
- implementation plan rules 通过。

验证：

```powershell
python .\tools\check_document_pair_policy.py --root . --json
python .\tools\check_implementation_plan_rules.py --root . --json
```

提交示例：`文档：验证自动路由方案双语配对`

### Task 4：OpenSpec guard 与 pre-commit review

范围：
- 运行仓库 guard，确认文档结构不破坏治理规则。
- 若 unrelated residual worktree warning 出现，只记录 warning；若 error 来自本任务，则修复。

完成标准：
- `run_openspec_guard` 通过。
- `check_precommit_update_archive` 通过。

验证：

```powershell
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root .
```

提交示例：`文档：通过自动路由方案治理门禁`

### Task 5：扩展 CI manifest 已登记的 checker 单元测试覆盖

范围：
- 扩展 `tools/check_orchestration_collaboration_evidenceguard.py` 的 manifest 已登记单元测试覆盖。
- 覆盖 repository mode 成功、fixture mode 成功、durable/persistent claim、expert lifecycle audit 与 LangGraph release evidence 的失败用例。
- 当另一个 active claim 已拥有 `tools/ci/ci_test_manifest.json` 热点文件时，把覆盖放入已登记测试文件，避免写入所有权冲突。

完成标准：
- manifest 已登记的测试覆盖同时验证通过的仓库 fixture 和失败的 evidence case。
- 不引入 `tools/ci/ci_test_manifest.json` 的写入所有权冲突。
- checker 仍然可通过 `tools/run_openspec_guard.py` 调用。

验证：

```powershell
python test\check_orchestration_trace_evidence.test.py
python .\tools\check_orchestration_collaboration_evidenceguard.py --root . --json
python .\tools\run_openspec_guard.py --root .
```

提交示例：`测试：扩展协同证据守卫覆盖`

### Task 6：守卫双语 OpenSpec evidence surface

范围：
- 将 `tools/check_orchestration_collaboration_evidenceguard.py` 的 repository-mode surface 检查扩展到 `openspec/specs/codex-user-level-orchestration-activation-policy/spec.zh-CN.md`。
- 要求中文 OpenSpec companion 明确包含 prompt-independent collaboration parity、durable/persistent evidenceguard、LangGraph state release 和 checker 路径。
- 增加回归测试，证明中文 OpenSpec surface 缺失时 repository mode 会失败。

完成标准：
- 英文与中文 stable OpenSpec spec surface 都受协同证据守卫检查。
- 测试套件可在不依赖瞬时聊天上下文的情况下发现中文 OpenSpec companion surface 缺失。
- 不因文档存在本身宣称 durable/persistent runtime 已运行。

验证：

```powershell
python test\check_orchestration_trace_evidence.test.py
python .\tools\check_orchestration_collaboration_evidenceguard.py --root . --json
python .\tools\run_openspec_guard.py --root .
```

提交示例：`守卫：覆盖双语 OpenSpec 协同证据`

### Task 7：本地 CI、MR review 与本地 main 集成

范围：
- 在 feature worktree 中完成本地 gate。
- 提交后运行 local MR review。
- 合入本地 `main`，不推送远端。

完成标准：
- feature worktree clean。
- local gate 通过。
- local MR review 通过。
- 本地 `main` 包含 feature commit。

验证：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600
.\tools\ci\local_mr_review.ps1
git merge-base --is-ancestor <feature-sha> main
```

提交示例：`文档：按新版结构重写自动路由方案`

## 8. P0 / P1 readiness gates

| Gate | 进入条件 | 退出条件 |
| --- | --- | --- |
| P0 文档结构重构 | 用户要求重写 implementation plan | 双语文档新版结构完成，本地验证通过 |
| P0 evidence contract freeze | 本方案完成 | evidence contracts 可直接生成 fixtures |
| P1 checker implementation | 用户要求实现 Phase 4 | `tools/check_orchestration_collaboration_evidenceguard.py`、fixtures、unit tests、CI wiring、safety registry 与 OpenSpec/spec updates 落地 |
| P1 runtime integration | checker 通过且有 runtime 入口 | activation trace、durable guard、expert lifecycle、LangGraph release 均可审计 |

## 9. 验证计划

基础验证：

```powershell
git diff --check
python .\tools\check_document_pair_policy.py --root . --json
python .\tools\check_implementation_plan_rules.py --root . --json
python test\check_orchestration_trace_evidence.test.py
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root .
```

集成验证：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600
.\tools\ci\local_mr_review.ps1
```

人工验收：

- 文档开头有 Goal / Architecture / Tech Stack。
- 第 0 节是复核结论，不是历史流水账。
- 第 7 节任务可交给 worker 执行，无需重新决定文件、测试或提交边界。
- 方案明确“计划不等于 evidence”。
- 方案没有把 ready、selected、running、complete 混用。
- 协同证据守卫 checker 已有 CI manifest 登记的单元测试覆盖，且没有 CI manifest 热点所有权冲突。
- 协同证据守卫同时检查英文与中文 stable OpenSpec spec surface。

## 10. Rollback 与清理

- 若重构后 checker 失败且不能快速修复，回滚双语文件到进入本任务前的 feature branch base。
- 若 feature worktree 已提交但未合入本地 main，使用普通 `git reset` 或新修正提交，避免改写已合入 main 的历史。
- 若已合入本地 main 且需要撤销，使用中文 `git revert` 提交；不做 main 历史改写。
- `.omx/worktree-task-receipt.json` 和 session claim 只作为 ignored local evidence；不进入 git。
- 未获远端授权时，不推送、不建 MR、不同步 GitHub。

## 11. 对现有治理方案的更新要求

本次 P0 文档重构不要求更新 runtime policy 或 checker。进入 P1 时必须同步：

- activation policy：增加 prompt-independent parity 作为验收规则。
- OpenSpec spec：增加 evidenceguard、expert lifecycle 和 LangGraph release requirements。
- CI manifest：登记新增 checker tests。
- team-mode docs：保持“自动协作默认开启但阈值门控 team launch”的表述一致。

## 12. 风险与默认决策

| 风险 | 默认决策 | 缓解 |
| --- | --- | --- |
| 文档再次变成规则合集 | 以 task-ready 结构为主 | 每个 Task 必须有范围、完成标准、验证、提交示例 |
| 用户误以为本方案已经实现 runtime | 明确 P0/P1 gate | 每节避免写成已运行事实 |
| checker 通过但人工结构不达标 | 人工比对参考方案 | 保留 Goal、Architecture、Tech Stack、Backlog、Rollback、自检 |
| console 输出中文 mojibake | 以 UTF-8 文件为准 | 不复制 mojibake；必要时用 Python UTF-8 读取 |
| 并发 session 推进 main | 合入前重新 fetch 和检查 main | 只做 fast-forward 或中文 merge commit |

## 13. 自检清单

- [x] front matter 使用新版 implementation plan 字段。
- [x] 标题下有 agentic worker 提示。
- [x] 有 Goal、Architecture、Tech Stack 摘要。
- [x] 有复核结论和完整性检查表。
- [x] 有关系模型和命名边界。
- [x] 有 repo-local source of truth。
- [x] 有 evidence contracts。
- [x] 有任务级 Backlog，且每个任务有验证与提交示例。
- [x] 有 readiness gates、验证计划、rollback、风险与默认决策。
- [x] 英文 primary 是 ASCII-only。
- [x] `tools/check_orchestration_collaboration_evidenceguard.py` 已有 CI manifest 登记的单元测试覆盖，包括 durable complete、runtime-state 与 LangGraph release/handoff 回归用例。
- [x] stable OpenSpec spec surface 已同时覆盖英文与中文。
- [x] 本地 commit 和 merge commit 使用中文。

## 14. 参考源

- `docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` —— 新版 sidecar implementation-plan 结构参考。
- `docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md` —— 新版 Comet runtime plan 结构参考。
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md` —— activation policy 权威来源。
- `docs_bilingual/project_startup_summary.zh-CN.md` —— 冷启动 read-order 权威来源。
- `AGENTS.md` —— 项目级 orchestration 与发布流程权威来源。
