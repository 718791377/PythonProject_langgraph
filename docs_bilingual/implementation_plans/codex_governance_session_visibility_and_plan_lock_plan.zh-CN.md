---
doc_id: codex_governance_session_visibility_and_plan_lock_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/codex_governance_session_visibility_and_plan_lock_plan.md
---

# 治理会话可视化与实施方案锁实施方案

## 目的

把对话中已经确认的治理方向固化为正式 implementation_plan 门禁产物，再允许后续非文档实现。
本方案覆盖五项相关治理升级：

1. 对话中面向用户的会话表面必须保留固定字面标签 `Routing trace` 和 `Updated Plan`；解释内容可以使用中文，`Updated Plan` 必须继续是复选框/状态清单表面。
2. OMX 与 LangGraph 的提权需求必须在主会话中更直观地展示，不能在用户未注意时静默超时。
3. 多个 Codex session 可以并行处理不同实施方案，但同一个 `implementation_plan` 同一时间只能由一个 session 处理。
4. Comet 必须让 Superpowers 作为 HOW 方法层的使用证据可见，而不是隐式发生。
5. GitHub Spec Kit 只能作为从属适配层或模板来源评估，不能成为与 Comet/OpenSpec/Superpowers 并列的治理层。

## 范围决策

- 层级：项目级治理，适用于 `D:/PythonProject_langgraph`。
- 复用形态：规则和脚本按通用、可迁移方向设计，后续可复制到其他仓库；但本次不修改用户级全局配置。
- 当前阶段：Stage A，只创建文档包。
- Stage B 类型：用户确认本文件后，才允许修改治理、checker、helper 和测试。
- runtime 边界：Stage A 不改变 OMX、LangGraph、Comet、OpenSpec、Superpowers 或 Spec Kit 的运行时行为。
- 远端发布：不在本方案范围内，除非用户之后明确要求远端发布。

## 非目标

- 不安装 GitHub Spec Kit，也不运行 `specify init`。
- 不把 Spec Kit 添加为项目治理权威。
- 不自动授予提权权限，也不绕过主会话审批模型。
- 不要求 portable 多会话锁依赖 OMX、LangGraph 或未来的“Codex CLI 个人开发者生产级持久化团队”。
- 不把 skill 调用当成 native subagent 证据。
- 在本 active implementation plan 提交、合入本地 `main`、展示给用户并被用户明确确认前，不开始 Stage B 非文档实现。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：active
阶段：Stage A 已合入文档包
责任会话：主 Codex leader 会话
当前门禁：等待用户明确确认本 implementation plan 后再进入 Stage B
Stage B 进入条件：本地 `main` 合入后，用户明确确认本文件或英文主版
最后更新：2026-05-28
<!-- CURRENT_STATUS_END -->

## Stage B 需要落实的治理决策

### 1. 稳定的会话表面标签

- 对话中展示给用户的路由决策必须保留字面标签 `Routing trace`；解释内容可以使用中文。
- 对话中展示给用户的计划进度必须保留字面标签 `Updated Plan`，并保留复选框/状态清单语义，不得改成纯段落。
- 保存给 checker 的机器可解析证据可以保留必要的 ASCII token，例如 `threshold_not_met:no_frozen_plan`。
- checker 应区分两个表面：
  - 用户可见会话文本：要求固定标签 `Routing trace` 和 `Updated Plan`；
  - 保存版证据 trace：允许结构化 token 以便验证。
- `Routing trace` 仍必须报告同一组决策：阶段、能力链、默认后端/就绪状态、专家、持久化工作流、持久化团队和原因。

### 2. 主会话提权可视化

- OMX、LangGraph 或 durable worker 流程不得把权限需求隐藏在 worker 上下文里。
- 在启动可能需要提权的工作前，增加主会话可见的提权预检摘要。
- 增加本地待授权收据表面，用来记录需要主会话处理的事项，但不自动授予权限。
- 增加待授权状态的存活提示语言，让用户看到当前进度被主会话授权决策阻塞。
- 保持安全边界：只有主会话可以请求或接收提权批准。

### 3. 可迁移 implementation_plan 会话锁

- 增加项目本地、轻依赖的 claim 模型；它必须在没有 OMX、LangGraph 或持久化团队时也能运行。
- claim 范围至少包括：
  - `implementation_plan` 路径；
  - `session_id`；
  - `worktree`；
  - `branch`；
  - 可选 OpenSpec change id；
  - 已触碰或计划触碰的路径范围；
  - 状态和时间戳。
- checker 必须在两个 active claim 指向同一个 `implementation_plan` 时 fail closed。
- 不同 active plan 在路径归属不冲突或已明确串行化时，可以并行处理。
- 被跟踪的脚本和文档应可迁移到另一台电脑；本地 claim 文件可以继续作为 ignored runtime state。

### 4. Comet 下的 Superpowers 可见性

- Comet 仍然是控制层。
- OpenSpec 仍然是 durable WHAT/spec lifecycle 权威。
- Superpowers 仍然是 HOW/方法论层。
- Comet 阶段输出和证据应明确说明相关阶段实际应用了哪个 Superpowers skill：
  - design：brainstorming 或设计方法 skill 证据；
  - build：writing-plans 加 executing-plans 或 subagent-driven-development 证据；
  - verify：适用时记录 finishing-a-development-branch 与 verification-before-completion 证据。
- 证据不得宣称 Superpowers skill 是 native subagent、durable worker 或 persistent team。

### 5. Spec Kit 边界

- 将 GitHub Spec Kit 视为与 planning/spec workflow 有重叠的 spec-driven-development toolkit。
- 不把它变成 Comet/OpenSpec/Superpowers 之外的第二套治理层。
- 如果后续引入，只能映射为从属 adapter、导入/导出桥或模板来源：
  - Comet：控制层；
  - OpenSpec：WHAT 与 durable spec lifecycle；
  - Superpowers：HOW 与执行方法论；
  - Spec Kit：可选 SDD 模板或适配表面。
- 增加 guardrail，禁止在没有单独 active implementation plan 的情况下运行 `specify init --force`、添加 `.specify/` 或转换治理权威。

## 计划中的 Stage B 实施边界

用户确认本方案文件后，Stage B 只允许更新落实上述五项决策所必需的文件：

- `docs_bilingual/governance/` 下与路由跟踪语言、会话归属、Comet/OpenSpec/Superpowers 权威和 Spec Kit adapter 边界有关的治理文档；
- `tools/` 下与中文路由证据、plan claim 重叠、待提权可视化和 Spec Kit 权威阻断有关的 checker/helper；
- 证明 checker/helper 行为所需的本地测试和 fixture；
- 只有在创建新文档时，才更新 docs registry。

Stage B 在修改用户级 launcher、安装包、运行 Spec Kit 初始化或改变外部远端前，必须再次停止并要求单独范围决策。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Stage A：创建英文 ASCII 主版 implementation plan。
- [x] Stage A：创建中文对照 implementation plan。
- [x] Stage A：在 `docs_bilingual/docs_registry.yaml` 中登记为 active implementation plan。
- [x] Stage A：使用中文提交信息提交文档包。
- [x] Stage A：把文档包合入本地 `main`。
- [ ] Stage A：停止并要求用户确认本 implementation_plan 文件后再进入 Stage B。
- [ ] Stage B：更新 orchestration activation 治理，使用户可见 `Routing trace` 和 `Updated Plan` 标签保持稳定，同时允许中文解释内容。
- [ ] Stage B：更新 trace/checker fixture，使本地化标签替换和纯段落 `Updated Plan` 输出 fail closed，且不破坏结构化证据 token。
- [ ] Stage B：增加待提权收据/预检治理和 checker 覆盖。
- [ ] Stage B：增加 portable implementation-plan claim schema 与重叠 checker 支持。
- [ ] Stage B：增加测试，证明同一 plan 的 active claims 会 fail closed，不同 plan 可以共存。
- [ ] Stage B：增加 Comet/Superpowers 可见性治理和证据检查。
- [ ] Stage B：增加 Spec Kit 从属 adapter 边界治理和 guard 测试。
- [ ] Stage B：运行本地验证，并使用中文提交信息提交。
- [ ] Stage B：只有在用户明确确认本方案文件后，才合入 Stage B。
<!-- TASK_BACKLOG_END -->

## 验收标准

Stage A 验收条件：

- 英文主版文件存在，且除 Markdown 所需符号外保持 ASCII 内容。
- 中文对照文件存在。
- `docs_bilingual/docs_registry.yaml` 将这对文件登记为 `doc_class: implementation_plan` 和 `status: active`。
- Stage A 使用中文提交信息。
- Stage A 合入本地 `main`。
- Stage A 不修改 runtime、checker、helper 或测试行为。
- assistant 在 Stage B 前停止并要求用户确认本文件。

Stage B 后续确认后的验收条件：

- 对话中用户可见的 routing 输出保留字面标签 `Routing trace`；计划进度输出保留字面标签 `Updated Plan` 和复选框/状态清单语义；解释语言可以使用中文。
- 保存版 trace 证据仍能验证必要的路由决策与阈值/blocker 标签。
- 主会话中可以在隐藏 worker 等待超时前看到提权需求摘要。
- 同一个 implementation_plan 的 active session claim 在普通本地机器上、没有 OMX/LangGraph 时也会 fail closed。
- 不同 active implementation plan 在归属不冲突时可以并行处理。
- Comet 证据会显示相关 Superpowers skill 的使用，但不把它误归类为 expert 或 durable worker。
- Spec Kit 被文档和 guard 约束为可选从属 adapter，而不是治理权威。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-05-28 Stage A 正式方案包：已用 `2429f3c` 提交并合入本地 `main`；验证包括 `check_implementation_plan_rules.py --root . --json`、`check_precommit_update_archive.py --root . --json`、`tools/ci/local_gate.ps1 -StepTimeoutSeconds 600` 和 `tools/ci/local_mr_review.ps1`。
<!-- EVIDENCE_INDEX_END -->
