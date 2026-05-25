---
doc_id: orchestration_prompt_independent_collaboration_parity_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/orchestration_prompt_independent_collaboration_parity_plan.md
translation_of: docs_bilingual/implementation_plans/orchestration_prompt_independent_collaboration_parity_plan.md
doc_class: implementation_plan
status: draft
last_reviewed: 2026-05-25
---

# 提示词无关的协同执行一致性实施计划

> **给 agentic workers：** 实施本计划时必须使用 `subagent-driven-development` 按任务执行。所有步骤使用 checkbox（`- [ ]`）跟踪。除非存在 selector、manifest、heartbeat、worker lifecycle、close/absorb 证据，否则不得声称 durable team 或 persistent team 已运行。

**目标：** 让自动协同做到证据诚实且与提示词短语无关：同一任务无论用户是否写出“use experts / durable_team / persistent team”，都必须得到同一类路由评估。

**架构：** 围绕 activation trace、expert lifecycle、durable/persistent team 声明和 LangGraph 完成/释放状态建立 checker-backed evidence contract。native experts 仍是 leader-side burst roles；`native_omx` 与 LangGraph 保持不同 durable backend family；durable-team 声明必须由 repo-local 证据支持，而不是由提示词文本支持。

**技术栈：** Python 仓库检查器与测试、repo-local `.omx/state/` 证据夹具、OpenSpec stable specs、`docs_bilingual/governance/*`、`tools/ci/local_gate.ps1` 本地 CI、`tools/ci/local_mr_review.ps1` 本地 MR 审查。

---

## 当前会话发现

本 session 中两条用户指令的业务范围相同。其中一条显式包含“use experts / durable_team / persistent team”，另一条没有。最终文档结果已经对齐，但会话证据不能严格证明“没有这句话”的指令独立产生了同一条协同执行路径。仓库政策已经要求自动协同不得依赖这句话，因此缺口不是再写提示词提醒，而是补上可执行的一致性 guard 和 lifecycle audit surface。

本计划是未来实施计划，不是运行时证据。它不能证明当前已有 durable team 或 persistent team 正在运行。

## 2026-05-25 颗粒度复核结论

本计划需要更新。原稿已经覆盖主要方向，但还不够 implementation-ready，主要缺口如下：

1. 曾使用未固定变更标识的 OpenSpec 路径，执行者无法直接落地。
2. 四类 checker 的输入夹具、输出字段、失败语义和通过语义不够明确。
3. 没有把“prompt phrase 只能改变 hard directive 标记，不能改变 task-shape 阈值判断”写成可测试契约。
4. durable/persistent evidenceguard 没有区分 `selected`、`running`、`complete`、`not_needed`、`blocked` 的证据需求。
5. expert lifecycle 只列出事件名，没有定义 JSONL 事件字段、引用关系和 timeout-as-evidence 的失败条件。
6. LangGraph `running` 释放规则缺少 thread/workflow/job 三类 state surface 的最小字段。
7. 验证矩阵没有明确每个新增工具应接入 `tools/run_openspec_guard.py`、`tools/ci/ci_test_manifest.json` 和本地 MR review 的顺序。

本次修订把这些缺口补成可执行颗粒度。它仍是实施计划，不是运行时证据；不能证明当前已有 durable team 或 persistent team 正在运行。

## 范围

范围内：

- 提示词无关的路由一致性 fixtures。
- durable/persistent team evidenceguard。
- expert lifecycle audit：`spawn / wait / timeout / result / close / absorbed`。
- LangGraph state 完成/释放检查，避免 work 已提交后仍残留 `running`。
- timeout 与 provider pacing 作为 non-evidence 的处理。
- 文档与 guard wiring 更新。

范围外：

- 替代 native Codex subagents。
- 把 skills 或 plugin profiles 当作 native experts。
- 在 startup 阶段自动启动 durable teams。
- 未经用户明确授权的远端发布。

## 计划文件地图

后续实施时使用固定 OpenSpec change id，避免占位符：

- change id：`enforce-prompt-independent-collaboration-parity`
- 推荐实现分支：`enforce-prompt-independent-collaboration-parity`
- 推荐 worktree：`.worktrees/enforce-prompt-independent-collaboration-parity`

| 路径 | 动作 | 责任 |
| --- | --- | --- |
| `openspec/changes/enforce-prompt-independent-collaboration-parity/proposal.md` | 新建 | 定义有边界的 change、非目标和验收标准。 |
| `openspec/changes/enforce-prompt-independent-collaboration-parity/tasks.md` | 新建 | 跟踪实施完成度。 |
| `openspec/changes/enforce-prompt-independent-collaboration-parity/specs/codex-user-level-orchestration-activation-policy/spec.md` | 新建 | 增加提示词无关一致性、evidenceguard、lifecycle audit、LangGraph release 要求。 |
| `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` | 修改 | 解释提示词无关的自动协同与证据边界。 |
| `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md` | 修改 | 中文伴随更新。 |
| `tools/check_orchestration_prompt_independent_collaboration_parity.py` | 新建 | 校验有/无显式短语的路由一致性 fixtures。 |
| `tools/check_durable_persistent_evidence_guard.py` | 新建 | 缺少 selector/manifest/heartbeat/worker 证据时拒绝 durable/persistent 声明。 |
| `tools/check_expert_lifecycle_audit.py` | 新建 | 校验 expert lifecycle audit 记录。 |
| `tools/check_langgraph_state_release.py` | 新建 | 检测完成/释放后仍残留的 stale `running` 状态。 |
| `test/check_orchestration_prompt_independent_collaboration_parity.test.py` | 新建 | 一致性检查器单元测试。 |
| `test/check_durable_persistent_evidence_guard.test.py` | 新建 | evidenceguard 单元测试。 |
| `test/check_expert_lifecycle_audit.test.py` | 新建 | lifecycle audit 单元测试。 |
| `test/check_langgraph_state_release.test.py` | 新建 | LangGraph release 检查单元测试。 |
| `test/fixtures/orchestration_prompt_independent_collaboration_parity/` | 新建 | 有/无显式协同短语的成对 fixtures。 |
| `test/fixtures/durable_persistent_evidence_guard/` | 新建 | durable/persistent claim 与证据夹具。 |
| `test/fixtures/expert_lifecycle_audit/` | 新建 | expert lifecycle JSONL 夹具。 |
| `test/fixtures/langgraph_state_release/` | 新建 | LangGraph state 夹具。 |
| `tools/run_openspec_guard.py` | 修改 | 将新检查器接入 guard sequence。 |
| `tools/ci/ci_test_manifest.json` | 修改 | 注册新单元测试。 |
| `docs_bilingual/docs_registry.yaml` | 修改 | 注册本计划和必要的新治理伴随文档。 |

## 过程组式运营模型

| 过程组 | 输入 | 工具与技术 | 输出 |
| --- | --- | --- | --- |
| 启动 | 会话复盘、当前治理政策、用户对自动协同的要求 | 问题框定、证据缺口分析、非目标审查 | change proposal、验收标准、明确的非声明边界 |
| 规划 | OpenSpec change、文件地图、当前 checker 模式、fixture 要求 | 切片拆分、owner mapping、test-first design、timeout budget review | 冻结实施计划、独立任务、验证矩阵 |
| 执行 | 冻结计划、worktree、OpenSpec delta、测试 | TDD、Python checkers、JSON fixtures、本地 guard wiring、必要时的 bounded expert review | 检查器、测试、文档更新、changed-path list |
| 监控与控制 | 测试输出、guard 输出、路由 fixtures、lifecycle records | Diff review、OpenSpec guard、local CI、expert verifier review、缺陷分诊 | 已接受修复、被拒绝的虚假声明、剩余风险清单 |
| 收尾 | 通过的 gates、干净分支、更新的 docs registry、完成后的 OpenSpec archive 候选 | 收尾审查、本地 MR review、archive 决策、经验教训 | merge-ready 分支、archive 或延期证据、后续 backlog |

## 证据契约

### Activation parity fixture contract

成对 fixture 必须共享同一个 `task_shape_id`，只允许 `prompt_features.explicit_collaboration_phrase` 不同。建议路径：

```text
test/fixtures/orchestration_prompt_independent_collaboration_parity/
  same_task_without_phrase.json
  same_task_with_phrase.json
```

最小 JSON 字段：

```json
{
  "case_id": "same_product_lifecycle_refresh_without_phrase",
  "task_shape_id": "product_lifecycle_refresh_business_pmp_multi_doc",
  "prompt_features": {
    "explicit_collaboration_phrase": false,
    "explicit_omx_directive": false,
    "explicit_langgraph_directive": false
  },
  "expected_decision": {
    "phase": "read-context-or-execute-parallel",
    "experts_now": "candidate_or_selected",
    "durable_workflow": "candidate_or_selected_when_threshold_met",
    "persistent_team_threshold": "requires_frozen_plan_and_2plus_slices",
    "backend_default": "langgraph",
    "claim_boundary": "do_not_claim_team_without_evidence"
  }
}
```

通过条件：同一 `task_shape_id` 的 fixtures 在 `phase`、`experts_now`、`durable_workflow`、`persistent_team_threshold`、`backend_default`、`claim_boundary` 上一致。显式短语只能让 trace 标注 `directive_seen=true`，不能让原本不达阈值的 task 被宣称为 persistent team 已运行。

失败条件：显式短语导致 `persistent_team=running`、跳过 frozen plan、跳过 evidenceguard、把 timeout 当证据、或改变 backend family 而没有 task-fit 理由。

### Durable/persistent evidenceguard contract

durable/persistent 声明的证据按状态分层：

| 声明状态 | 最小证据 |
| --- | --- |
| `not_needed` | activation trace 说明未达阈值，例如 `threshold_not_met:single_execution_slice`。 |
| `candidate` | frozen plan 或切片分析，以及为何尚未启动。 |
| `selected` | active selector、backend family、preflight 通过记录、worker ownership plan。 |
| `running` | active selector、team manifest、worker heartbeat、worker lifecycle `started/running` 记录。 |
| `complete` | `running` 所需证据，加 closed agent record、result summary、leader absorbed record。 |
| `blocked` | blocker 名称、最近三次阻塞证据、未把阻塞结果当完成。 |

建议 fixture 结构：

```text
test/fixtures/durable_persistent_evidence_guard/
  invalid_running_missing_heartbeat/
    transcript.json
    .omx/state/selectors/active.json
    .omx/state/team/manifest.json
  valid_complete_team/
    transcript.json
    .omx/state/selectors/active.json
    .omx/state/team/manifest.json
    .omx/state/team/worker-heartbeats/worker-1.json
    .omx/state/team/lifecycle.jsonl
    .omx/state/team/closed-agents/worker-1.json
    .omx/state/team/absorbed-results.jsonl
```

### Expert lifecycle audit contract

每个 expert lifecycle record 使用 JSONL，建议路径：`.omx/state/experts/lifecycle.jsonl` 或测试夹具中的同名路径。每行最小字段：

```json
{
  "event": "spawn",
  "timestamp": "2026-05-25T00:00:00+08:00",
  "agent_id": "agent-001",
  "role": "verifier",
  "nickname": "Bernoulli",
  "task_summary": "review routing parity checker fixtures",
  "status": "started",
  "evidence_disposition": "not_evidence_yet"
}
```

事件顺序要求：

1. `spawn` 必须先于同一 `agent_id` 的 `wait`、`timeout`、`result`、`close`、`absorbed`。
2. `result` 被最终报告引用时，必须存在同一 `agent_id` 的 `absorbed`。
3. `timeout`、`stall`、`provider_pacing_wait` 只能产生 non-evidence disposition。
4. `close` 后不得继续写入新的 `result`，除非新 `spawn` 使用新的 `agent_id`。

### LangGraph state release contract

repo-local LangGraph state 不得在完成后无解释地残留 `running`。建议最小 state：

```json
{
  "thread_id": "lg-thread-001",
  "workflow_id": "prompt-independent-parity",
  "status": "running",
  "active_work": true,
  "last_heartbeat_at": "2026-05-25T00:00:00+08:00",
  "completion_marker": null,
  "release_marker": null,
  "continue_reason": "worker still processing task 2"
}
```

失败条件：`completion_marker` 存在或 closeout evidence 表示完成，但 `status=running` 且 `release_marker=null` 且 `continue_reason` 为空。

通过条件：

- active work 仍在运行且 heartbeat 新鲜；或
- work 已完成，state 为 `complete/released/closed`；或
- state 仍为 `running`，但有明确 release deferral 与未完成 work 证据。

## 任务 1：OpenSpec Change 与证据契约

**文件：**
- 新建：`openspec/changes/enforce-prompt-independent-collaboration-parity/proposal.md`
- 新建：`openspec/changes/enforce-prompt-independent-collaboration-parity/tasks.md`
- 新建：`openspec/changes/enforce-prompt-independent-collaboration-parity/specs/codex-user-level-orchestration-activation-policy/spec.md`

- [ ] **步骤 1：创建 OpenSpec proposal**

  proposal 必须说明：自动协同由任务阈值触发，不由提示词短语触发。proposal 必须命名四类 evidence contract：提示词无关一致性、durable/persistent evidenceguard、expert lifecycle audit、LangGraph state release。

- [ ] **步骤 2：增加规范性要求**

  增加以下要求：
  - 同一 task shape 的有短语/无短语 fixtures 必须产生同一类 activation decision；
  - durable/persistent team 声明必须具备 selector、manifest、heartbeat、worker lifecycle、close/absorb 证据；
  - expert timeout 是 non-evidence；
  - submit/close 后 LangGraph `running` 状态必须完成或释放。

- [ ] **步骤 3：验证 change**

  运行：

  ```powershell
  openspec validate enforce-prompt-independent-collaboration-parity --strict
  ```

  预期：change 校验通过，没有 failed requirements。

## 任务 2：提示词无关路由一致性检查器

**文件：**
- 新建：`tools/check_orchestration_prompt_independent_collaboration_parity.py`
- 新建：`test/check_orchestration_prompt_independent_collaboration_parity.test.py`
- 新建：`test/fixtures/orchestration_prompt_independent_collaboration_parity/same_task_without_phrase.json`
- 新建：`test/fixtures/orchestration_prompt_independent_collaboration_parity/same_task_with_phrase.json`
- 修改：`tools/run_openspec_guard.py`
- 修改：`tools/ci/ci_test_manifest.json`

- [ ] **步骤 1：编写失败测试**

  为同一任务增加两组 fixtures：
  - 不含显式协同短语；
  - 包含“use experts / durable_team / persistent team”。

  预期行为：两组 fixtures 的 phase、expert need、durable threshold result、persistent-team evidence state 必须一致。

- [ ] **步骤 2：实现检查器**

  检查器读取 JSON fixtures，按 `task_shape_id` 分组，并比较 `expected_decision.phase`、`experts_now`、`durable_workflow`、`persistent_team_threshold`、`backend_default`、`claim_boundary`。当显式短语在没有 task-shape 差异的情况下改变 activation decision class 时，检查器失败。失败输出必须包含 `case_id`、`task_shape_id`、字段名、左值与右值。

- [ ] **步骤 3：注册 guard 与测试**

  将检查器加入 `tools/run_openspec_guard.py`，并把测试文件加入 `tools/ci/ci_test_manifest.json`。

- [ ] **步骤 4：运行聚焦测试**

  ```powershell
  python .\test\check_orchestration_prompt_independent_collaboration_parity.test.py
  python .\tools\check_orchestration_prompt_independent_collaboration_parity.py --root . --json
  ```

  预期：测试与检查器均通过。

## 任务 3：Durable/Persistent Evidenceguard

**文件：**
- 新建：`tools/check_durable_persistent_evidence_guard.py`
- 新建：`test/check_durable_persistent_evidence_guard.test.py`
- 新建：`test/fixtures/durable_persistent_evidence_guard/invalid_running_missing_heartbeat/`
- 新建：`test/fixtures/durable_persistent_evidence_guard/valid_complete_team/`
- 修改：`tools/run_openspec_guard.py`
- 修改：`tools/ci/ci_test_manifest.json`

- [ ] **步骤 1：编写失败测试**

  增加 negative fixtures：transcript 声称 `durable_team=running` 或 `persistent_team=running`，但缺少一个或多个必要证据文件。检查器必须让这些 fixtures 失败。

- [ ] **步骤 2：实现证据校验**

  要求以下证据：
  - active selector；
  - team manifest；
  - worker heartbeat；
  - worker lifecycle record；
  - 当 work 被声明 complete 时，必须存在 closed agent record、result summary 与 final close/absorb record。

- [ ] **步骤 3：运行聚焦测试**

  ```powershell
  python .\test\check_durable_persistent_evidence_guard.test.py
  python .\tools\check_durable_persistent_evidence_guard.py --root . --json
  ```

  预期：虚假 durable/persistent 声明 fail closed；有效证据 fixtures 通过。

## 任务 4：Expert Lifecycle Audit

**文件：**
- 新建：`tools/check_expert_lifecycle_audit.py`
- 新建：`test/check_expert_lifecycle_audit.test.py`
- 新建：`test/fixtures/expert_lifecycle_audit/valid_absorbed_result/lifecycle.jsonl`
- 新建：`test/fixtures/expert_lifecycle_audit/invalid_timeout_as_evidence/lifecycle.jsonl`
- 修改：`tools/run_openspec_guard.py`
- 修改：`tools/ci/ci_test_manifest.json`

- [ ] **步骤 1：定义 lifecycle schema**

  为 `spawn`、`wait`、`timeout`、`result`、`close`、`absorbed` 定义必填字段：timestamp、role、agent id、可用时的 nickname、task summary、status、evidence disposition。

- [ ] **步骤 2：实现检查器**

  当 completed expert result 被 `final_report_refs.json` 引用但没有匹配的 `absorbed` event 时失败；当 timed-out/stalled/provider-paced expert 被用作 accepted evidence 时失败；当 `close` 之后同一 `agent_id` 又出现新 `result` 时失败。

- [ ] **步骤 3：运行聚焦测试**

  ```powershell
  python .\test\check_expert_lifecycle_audit.test.py
  python .\tools\check_expert_lifecycle_audit.py --root . --json
  ```

  预期：完整 lifecycle fixtures 通过；timeout-as-evidence fixtures 失败。

## 任务 5：LangGraph 完成与释放状态

**文件：**
- 新建：`tools/check_langgraph_state_release.py`
- 新建：`test/check_langgraph_state_release.test.py`
- 新建：`test/fixtures/langgraph_state_release/valid_active_running/`
- 新建：`test/fixtures/langgraph_state_release/valid_released_complete/`
- 新建：`test/fixtures/langgraph_state_release/invalid_completed_still_running/`
- 修改：`tools/run_openspec_guard.py`
- 修改：`tools/ci/ci_test_manifest.json`

- [ ] **步骤 1：增加状态 fixtures**

  增加以下 fixtures：
  - 有 active work 的合法 running thread；
  - completed thread 且 state 已 release；
  - work 已完成但仍标记为 `running` 的非法状态。

- [ ] **步骤 2：实现 release checker**

  当 handoff 或 closeout evidence 已把 thread 标记为 complete，但 repo-local LangGraph state 仍是 `running` 且没有 release marker 或 continue reason 时失败。active running state 必须具备 active work、fresh heartbeat 与继续执行理由。

- [ ] **步骤 3：运行聚焦测试**

  ```powershell
  python .\test\check_langgraph_state_release.test.py
  python .\tools\check_langgraph_state_release.py --root . --json
  ```

  预期：stale running state 失败；有 live work 的 active running state 通过。

## 任务 6：文档、验证与收尾

**文件：**
- 修改：`docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md`
- 修改：`docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md`
- 修改：`docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.md`
- 修改：`docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md`
- 修改：`docs_bilingual/docs_registry.yaml`

- [ ] **步骤 1：更新治理文本**

  增加说明：显式协同短语出现时是 routing directive，但没有这些短语不是跳过 activation check 的理由。

- [ ] **步骤 2：运行验证**

  ```powershell
  git diff --check
  openspec validate --all
  python .\tools\check_precommit_update_archive.py --root . --json
  python .\tools\run_openspec_guard.py --root .
  .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600
  .\tools\ci\local_mr_review.ps1
  ```

  预期：全部检查通过；如存在无关外部 worktree/state 阻塞，必须如实报告，不能把它当作完成证据。

- [ ] **步骤 3：收尾证据**

  最终报告必须区分：
  - 已使用并关闭的 native experts；
  - durable/persistent team 未启动，除非证据存在；
  - timed-out experts 未被用作证据；
  - LangGraph backend ready 不等于 persistent-team runtime 正在运行。

## 验证矩阵

| 需求 | 验证命令 | 必须失败的反例 | 必须通过的正例 |
| --- | --- | --- | --- |
| 有/无协同短语 routing parity | `python .\tools\check_orchestration_prompt_independent_collaboration_parity.py --root . --json` | 短语导致 `persistent_team=running` | 同一 task shape 决策字段一致 |
| durable/persistent evidenceguard | `python .\tools\check_durable_persistent_evidence_guard.py --root . --json` | running 缺 heartbeat | complete 具备 selector、manifest、heartbeat、lifecycle、closed、absorbed |
| expert lifecycle audit | `python .\tools\check_expert_lifecycle_audit.py --root . --json` | timeout 被 final report 引用为证据 | result 被 absorbed 后再引用 |
| LangGraph release | `python .\tools\check_langgraph_state_release.py --root . --json` | completed 仍 running 且无 release marker | active running 有 heartbeat，或 completed 已 released |
| guard wiring | `python .\tools\run_openspec_guard.py --root .` | checker 未注册 | guard 输出包含新增 checker |
| CI manifest | `.\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` | 测试未注册 | local gate 执行新增测试 |

## 风险与回滚

- 风险：checker 过度依赖 chat transcript 文本。缓解：以结构化 fixture 和 repo-local state 为主，transcript 只作为 claim source。
- 风险：把 LangGraph backend ready 误判成 persistent team running。缓解：backend readiness 与 team evidence 分离。
- 风险：阻塞真实 running work。缓解：允许 active running state 通过，但要求 heartbeat、active work 和 continue reason。
- 风险：误把 skills/profile 当 expert。缓解：expert lifecycle 只接受 native spawn/wait/result/close/absorbed 事件。
- 回滚：若新增 checker 误报，先从 `tools/run_openspec_guard.py` 临时移除该 checker，并保留测试夹具用于修复；不得删除治理要求或把虚假 team 声明放行。

## 验收标准

- 同一 task shape 在有/无显式协同短语时产生同一类 routing decision。
- 没有 selector、manifest、heartbeat、worker lifecycle、closed agent record、close/absorb 证据时，durable/persistent team 运行声明不能通过。
- Expert lifecycle audit 能区分 completed/absorbed result 与 timeout/stall/provider pacing non-evidence。
- LangGraph completed work 不残留 stale `running` state；如仍 running，必须有 active work、heartbeat 和 continue reason。
- Repository guard 与 local CI 包含新增检查。
- 面向用户的最终报告保持证据诚实，区分 policy expectation、actual evidence、blocked/non-evidence、main-session takeover，不把提示词文本当作运行时证明。
- 本计划本身不宣称 durable/persistent team 已运行；只有后续执行产生的 repo-local evidence 才能支撑该声明。
