---
doc_id: multi_plan_parallel_session_orchestration_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
---

# 多方案并行会话编排实施方案

## 目的

创建父级编排方案，用于把六份既有 implementation_plan 重构为更小、可认领、可并行的工作包。
目标执行模型如下：

- 一个父方案负责阶段顺序、依赖、集成门禁和 session 上限；
- 每个子 `implementation_plan` 负责一个可执行切片；
- 同一个子 `implementation_plan` 同一时间只能有一个 active session claim；
- 不同子方案在写入范围不冲突或已明确串行化时可以并行；
- 本地 `main` 集成始终串行，并由主会话负责。

## 范围决策

- 层级：项目级治理，适用于 `D:/PythonProject_langgraph`。
- 复用形态：通用、可迁移的模式，后续可复制到其他仓库；但 Stage A 不修改用户级全局配置。
- 当前阶段：Stage A，只创建父级文档包。
- Stage B 类型：用户确认本父方案后，创建子 implementation_plan。
- Stage C 及以后：通过子方案实施 plan lock、routing、durable-state、context-retention、Comet runtime 和 Spec Kit 边界工作。
- 远端发布：不在范围内，除非用户明确要求远端发布。

## 覆盖的来源方案

本父方案协调以下既有方案，但不替代它们的详细内容：

1. automatic_orchestration_routing_enforcement_plan - 定义自动协同路由、activation trace、expert 生命周期证据和 durable-team 阈值。
2. codex_user_level_context_retention_canary_plan - 保护冷启动上下文保留、canary 字面量位置、乱码检测和 replay 过滤。
3. codex_user_level_cross_session_durable_state_isolation_plan - 隔离 repo-local durable state、selector、backend readiness 和跨 session durable artifact。
4. comet_runtime_agile_focus_area_plan - 增加 Comet management record、阶段勾选门禁和 Monitoring 回退 transition。
5. implementation_plan_confirmation_gate - 要求非文档实现开始前必须有已提交的 active implementation-plan 文件；这里的 confirmation gate 指阻塞检查点，必须等用户确认已提交的方案文件后才能继续执行。
6. codex_governance_session_visibility_and_plan_lock_plan - 增加中文 routing trace 可视化、主会话提权可视化、Superpowers 证据、Spec Kit 边界和 plan lock。

## 非目标

- Stage A 不实现 runtime、checker、helper 或测试变更。
- Stage A 不一次性创建所有子 implementation_plan。
- 不安装 GitHub Spec Kit，也不运行 `specify init`。
- 不为本文档包启动 OMX、LangGraph 或持久化团队。
- 不允许多个 session 同时写同一个子 implementation_plan。
- 除非用户明确要求远端发布，否则不推送 GitLab 或 GitHub。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：active
阶段：Stage A 父级方案文档包
责任会话：主 Codex leader 会话
当前门禁：创建并合入本父级 implementation plan，然后停止等待用户确认
Stage B 进入条件：本地 `main` 合入后，用户明确确认本父方案或英文主版
最后更新：2026-05-28
<!-- CURRENT_STATUS_END -->

## 执行模型

### Session 与 Claim 规则

- 每个子 implementation_plan 是最小认领单元。
- session claim 必须在写入开始前声明子 implementation_plan 路径。
- 同一个子 implementation_plan 同一时间只能有一个 active claim。
- 多个 session 只有在认领不同子方案时才允许并行。
- `docs_bilingual/docs_registry.yaml`、CI manifest、共享 checker、`comet-state.sh` 和 `comet-guard.sh` 等热点文件必须在每个批次中有明确 owner。
- 主 Codex leader 会话负责 fan-in、验证、本地 `main` 集成和发布建议。
- 即使实施 session 并行，本地 `main` 集成也保持串行。

### 默认并行度

- 每阶段默认最多 4 个并行 session。
- 每阶段突发上限最多 6 个并行 session。
- 当写入范围重叠时，阶段必须降低并行度。
- 如果子方案存在未关闭 claim、脏 worktree、失败本地门禁或未合入的本地 main 集成，不得进入下一阶段。

## 阶段与子方案拆分

### Phase 0：盘点与父级编排

目的：建立父级执行地图并确认 registry 健康状态。

候选子方案：

1. `plan_inventory_registry_alignment_plan` - 盘点当前方案状态、registry、锚点和 evidence index 健康度。
2. `parent_parallel_orchestration_index_plan` - 维护父级阶段图、子方案登记表和依赖表。
3. `canary_plan_registry_recovery_plan` - 决定 context-retention canary 方案是否以及如何补登记或修复。

并行度：本父方案确认后最多 3 个 session。

### Phase 1：施工安全底座

目的：在 runtime-heavy 工作开始前，先让并行执行安全。

候选子方案：

1. `formal_plan_confirmation_gate_runtime_plan` - 强制“仅对话确认 plan 不足以进入实现”。
2. `portable_implementation_plan_claim_lock_plan` - 实现不依赖 OMX 或 LangGraph 的子方案单 active session 锁。
3. `implementation_plan_registry_active_state_plan` - 强制 active 状态、双语配对和 docs registry 一致。
4. `main_session_escalation_visibility_plan` - 增加主会话可见的待授权和提权预检表面。

并行度：最多 4 个 session；`docs_bilingual/docs_registry.yaml` 每批只能一个 session 拥有。

### Phase 2：上下文与 UTF-8 安全

目的：在更重的 orchestration 自动化之前，稳定冷启动、replay 和乱码边界。

候选子方案：

1. `context_retention_canary_literal_boundary_plan` - 将 canary 字面量限制在 startup summary。
2. `startup_mojibake_utf8_recovery_plan` - 加固乱码检测与 UTF-8 canonical recovery。
3. `session_replay_context_filtering_plan` - 过滤 assistant/session replay 表面，避免 stale canary 或乱码重新进入 prompt。
4. `launcher_payload_context_boundary_plan` - 保持 launcher payload 边界，本阶段不修改用户级配置。

并行度：最多 4 个 session；startup summary 文件串行。

### Phase 3：Durable State 与跨 Session 隔离

目的：确保 durable-state 选择和检查在跨仓库、worktree、session 时安全。

候选子方案：

1. `repo_local_selector_ownership_plan` - 强制 repository-local active selector 归属。
2. `durable_capability_readiness_projection_plan` - 区分 installed、enabled、selected 和 ready。
3. `legacy_durable_residue_classification_plan` - 对陈旧 `.omx/state` residue 分类，但不自动接管。
4. `worktree_receipt_claim_lifecycle_plan` - 定义 active、paused、completed、stale 和 cleaned claim/receipt 生命周期。
5. `portable_no_backend_parallel_session_plan` - 在没有 OMX 和 LangGraph 时支持 Git/Python-only 并行 session。

并行度：最多 5 个 session；`.omx/state` 写入按仓库或 worktree 串行。

### Phase 4：自动路由与中文可视化

目的：让协同路由自动、可审计，并在对话中面向中文展示。

候选子方案：

1. `chinese_routing_trace_conversation_surface_plan` - 要求用户可见 routing trace 使用中文字段名和中文说明。
2. `routing_trace_structured_evidence_schema_plan` - 为保存版证据保留机器可读 ASCII 阈值和 blocker token。
3. `prompt_independent_activation_parity_plan` - 确保路由不依赖用户是否说出“并行”或“专家”。
4. `expert_lifecycle_timeout_pacing_evidence_plan` - 将 timeout、stall 和 pacing 视为非证据，并要求有界处理。
5. `langgraph_state_release_evidence_plan` - 拒绝 LangGraph 工作完成后仍保留 stale `running` 状态。
6. `role_routing_fanout_write_ownership_plan` - 强制最小充分角色选择和 fan-out 写入归属。

并行度：最多 6 个 session；共享 routing checker 串行。

### Phase 5：Comet Runtime 敏捷管理循环

目的：在安全与可视化基础稳定后，实现 Comet runtime 管理循环。

候选子方案：

1. `comet_management_record_bootstrap_plan` - 创建并验证 management record。
2. `comet_phase_checklist_gate_plan` - 前进 transition 前要求阶段勾选证据。
3. `comet_monitoring_return_transition_plan` - 支持 Monitoring 决策回退到 Open、Design、Build 或 Verify。
4. `comet_superpowers_visibility_plan` - 让 Comet 阶段显式展示 Superpowers HOW-layer skill 使用。
5. `comet_runtime_policy_checker_alignment_plan` - 对齐 policy、OpenSpec specs、checker 覆盖和集成门禁。

并行度：最多 4 个 session。`comet-state.sh` 和 `comet-guard.sh` 同一时间只能一个 owner。

### Phase 6：Spec Kit 边界

目的：防止 GitHub Spec Kit 成为竞争性治理层。

候选子方案：

1. `spec_kit_subordinate_adapter_governance_plan` - 将 Spec Kit 文档化为可选从属 adapter 或模板来源。
2. `spec_kit_authority_guard_plan` - 没有单独 active plan 时阻止 `specify init --force`、`.specify/` 或治理权威迁移。

并行度：最多 2 个 session。

### Phase 7：集成、验证与归档

目的：把并行工作收敛为串行本地 main 包，并在适用时归档已完成 OpenSpec 工作。

候选子方案：

1. `parallel_plan_docs_registry_integration_plan` - 验证 docs registry、双语配对和 implementation-plan rules。
2. `parallel_plan_checker_ci_integration_plan` - 验证 checker、unit 和 local CI 覆盖。
3. `parallel_plan_openspec_comet_archive_plan` - 验证 OpenSpec/Comet guard 健康，并归档已完成变更。
4. `parallel_plan_publication_readiness_plan` - 准备发布建议；没有明确授权时不做远端发布。

并行度：验证可以并行，但本地 `main` 合入保持串行。

## Stage B 创建规则

进入 Stage B 后，子方案按批次创建：

- Batch 1：Phase 0 和 Phase 1 子方案。
- Batch 2：Phase 2 和 Phase 3 子方案。
- Batch 3：Phase 4 子方案。
- Batch 4：Phase 5 和 Phase 6 子方案。
- Batch 5：Phase 7 集成子方案。

每个子方案必须包含：

- YAML front matter，含 `doc_id`、`lang`、`status: active`、`doc_class: implementation_plan` 和双语 companion 元数据。
- CURRENT_STATUS 锚点记录当前阶段和检查点，TASK_BACKLOG 锚点记录复选框任务项，EVIDENCE_INDEX 锚点记录轻量 commit/report 引用；这些锚点是脚本用于局部更新的稳定 HTML 注释。
- 明确文件归属和热点文件串行说明。
- 该子方案或阶段的最大并行 session 数。
- 本地验证命令和预期门禁行为。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Stage A：创建英文 ASCII 父级 implementation plan。
- [x] Stage A：创建中文对照父级 implementation plan。
- [x] Stage A：在 `docs_bilingual/docs_registry.yaml` 登记父方案。
- [ ] Stage A：使用中文提交信息提交父级文档包。
- [ ] Stage A：把父级文档包合入本地 `main`。
- [ ] Stage A：停止并要求用户确认本父方案后再进入 Stage B 子方案创建。
- [ ] Stage B：为 Phase 0 和 Phase 1 创建 Batch 1 子 implementation_plan。
- [ ] Stage B：为 Phase 2 和 Phase 3 创建 Batch 2 子 implementation_plan。
- [ ] Stage B：为 Phase 4 创建 Batch 3 子 implementation_plan。
- [ ] Stage B：为 Phase 5 和 Phase 6 创建 Batch 4 子 implementation_plan。
- [ ] Stage B：为 Phase 7 集成创建 Batch 5 子 implementation_plan。
- [ ] Stage C：子方案确认后，实现 portable child-plan claim lock。
- [ ] 后续阶段：每阶段最多 6 个并行 session 执行子方案，并串行合入本地 main。
<!-- TASK_BACKLOG_END -->

## 验收标准

Stage A 验收条件：

- 英文主版父方案存在且为 ASCII-only。
- 中文对照父方案存在。
- `docs_bilingual/docs_registry.yaml` 将这对文件登记为 `doc_class: implementation_plan` 和 `status: active`。
- 父方案列出阶段、候选子方案、依赖顺序、session 上限和热点文件串行规则。
- Stage A 使用中文提交信息。
- Stage A 合入本地 `main`。
- Stage A 不修改 runtime、checker、helper 或测试行为。
- assistant 在 Stage B 前停止并要求用户确认本父方案。

Stage B 后续确认后的验收条件：

- 子方案被创建为独立认领单元。
- 没有子方案缺少双语配对或 registry 登记。
- 每个子方案声明文件归属、session 上限和验证门禁。
- 相关子方案未确认前，不开始非文档实现。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 等待 Stage A 提交证据。本方案只保存轻量证据索引。
<!-- EVIDENCE_INDEX_END -->
