---
doc_id: orchestration_prompt_independent_collaboration_parity_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/orchestration_prompt_independent_collaboration_parity_plan.md
translation_of: docs_bilingual/implementation_plans/orchestration_prompt_independent_collaboration_parity_plan.md
doc_class: implementation_plan
status: draft
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

| 路径 | 动作 | 责任 |
| --- | --- | --- |
| `openspec/changes/<change-id>/proposal.md` | 新建 | 定义有边界的 change 和验收标准。 |
| `openspec/changes/<change-id>/tasks.md` | 新建 | 跟踪实施完成度。 |
| `openspec/changes/<change-id>/specs/codex-user-level-orchestration-activation-policy/spec.md` | 新建 | 增加一致性与 evidenceguard 要求。 |
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

## 任务 1：OpenSpec Change 与证据契约

**文件：**
- 新建：`openspec/changes/<change-id>/proposal.md`
- 新建：`openspec/changes/<change-id>/tasks.md`
- 新建：`openspec/changes/<change-id>/specs/codex-user-level-orchestration-activation-policy/spec.md`

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
  openspec validate <change-id> --strict
  ```

  预期：change 校验通过，没有 failed requirements。

## 任务 2：提示词无关路由一致性检查器

**文件：**
- 新建：`tools/check_orchestration_prompt_independent_collaboration_parity.py`
- 新建：`test/check_orchestration_prompt_independent_collaboration_parity.test.py`
- 修改：`tools/run_openspec_guard.py`
- 修改：`tools/ci/ci_test_manifest.json`

- [ ] **步骤 1：编写失败测试**

  为同一任务增加两组 fixtures：
  - 不含显式协同短语；
  - 包含“use experts / durable_team / persistent team”。

  预期行为：两组 fixtures 的 phase、expert need、durable threshold result、persistent-team evidence state 必须一致。

- [ ] **步骤 2：实现检查器**

  检查器读取 JSON fixtures；当显式短语在没有 task-shape 差异的情况下改变 activation decision class 时，检查器失败。

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
  - 当 work 被声明 complete 时，必须存在 final close/absorb record。

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
- 修改：`tools/run_openspec_guard.py`
- 修改：`tools/ci/ci_test_manifest.json`

- [ ] **步骤 1：定义 lifecycle schema**

  为 `spawn`、`wait`、`timeout`、`result`、`close`、`absorbed` 定义必填字段：timestamp、role、agent id、可用时的 nickname、task summary、status、evidence disposition。

- [ ] **步骤 2：实现检查器**

  当 completed expert result 被引用但没有匹配的 `absorbed` event 时失败；当 timed-out expert 被用作证据时失败。

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
- 修改：`tools/run_openspec_guard.py`
- 修改：`tools/ci/ci_test_manifest.json`

- [ ] **步骤 1：增加状态 fixtures**

  增加以下 fixtures：
  - 有 active work 的合法 running thread；
  - completed thread 且 state 已 release；
  - work 已完成但仍标记为 `running` 的非法状态。

- [ ] **步骤 2：实现 release checker**

  当 handoff 或 closeout evidence 已把 thread 标记为 complete，但 repo-local LangGraph state 仍是 `running` 且没有 release marker 时失败。

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
- 修改：`docs_bilingual/docs_registry.yaml`

- [ ] **步骤 1：更新治理文本**

  增加说明：显式协同短语出现时是 routing directive，但没有这些短语不是跳过 activation check 的理由。

- [ ] **步骤 2：运行验证**

  ```powershell
  git diff --check
  openspec validate --all
  python .\tools\check_precommit_update_archive.py --root . --json
  python .\tools\run_openspec_guard.py --root .
  .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 360
  .\tools\ci\local_mr_review.ps1
  ```

  预期：全部检查通过；如存在无关外部 worktree/state 阻塞，必须如实报告，不能把它当作完成证据。

- [ ] **步骤 3：收尾证据**

  最终报告必须区分：
  - 已使用并关闭的 native experts；
  - durable/persistent team 未启动，除非证据存在；
  - timed-out experts 未被用作证据；
  - LangGraph backend ready 不等于 persistent-team runtime 正在运行。

## 验收标准

- 同一 task shape 在有/无显式协同短语时产生同一类 routing decision。
- 没有 selector、manifest、heartbeat、worker lifecycle、close/absorb 证据时，durable/persistent team 声明不能通过。
- Expert lifecycle audit 能区分 completed/absorbed result 与 timeout/non-evidence。
- LangGraph completed work 不残留 stale `running` state。
- Repository guard 与 local CI 包含新增检查。
- 面向用户的最终报告保持证据诚实，不把提示词文本当作运行时证明。
