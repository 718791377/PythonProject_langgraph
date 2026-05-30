---
doc_id: multi_plan_parallel_session_orchestration_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
---

# 多方案并行会话编排实施方案

## 目的

创建本方案族的父级编排方案，用于把本文件覆盖的既有 implementation_plan 重构为更小、可认领、可并行的工作包。本文件不是 `docs_bilingual/implementation_plans/` 目录下所有方案的全局父方案。
目标执行模型如下：

- 本父方案只负责其方案族内部的阶段顺序、依赖、集成门禁和 Work-Conserving 准入、hotspot lease；
- 每个相关子 `implementation_plan` 负责一个可执行切片；
- 同一个 `implementation_plan` 同一时间只能有一个 active session claim；
- 不同方案在写入范围不冲突或已明确串行化时可以并行，即使它们不属于同一个父方案；
- 本地 `main` 写入始终串行；后续目标是由拿到 `local-main-retire` lock 的 session 合入自己的 ready branch，而不是固定主会话总控。

## 范围决策

- 层级：项目级治理，适用于 `D:/PythonProject_langgraph`。
- 复用形态：通用、可迁移的模式，后续可复制到其他仓库；但 Stage A 不修改用户级全局配置。
- 当前阶段：Stage A，只创建父级文档包。
- Stage B 类型：用户确认本父方案后，创建本方案族子 implementation_plan。
- Stage C 及以后：通过本方案族子方案实施 plan lock、routing、durable-state、context-retention、Comet runtime 和 Spec Kit 边界工作。
- 父子范围：本父方案只协调 front matter 中 `parent_plan` 指向本文件，或正文明确列为本方案族来源、拆分对象、集成对象的 implementation_plan。
- 无关方案：其他 implementation_plan 不因位于 `docs_bilingual/implementation_plans/` 目录下而自动成为本父方案的子方案；它们可以无父方案，也可以属于其他父方案。
- 新会话读取：新 session 不默认读取本文件；只有处理本文件、其子方案、任务清单、证据索引或本文件 Phase / Batch 中列出的相关方案时才需要读取。
- 远端发布：不在范围内，除非用户明确要求远端发布。

## 覆盖的来源方案

本父方案协调以下本方案族内既有方案，但不替代它们的详细内容；未列入且未声明 `parent_plan` 指向本文件的方案不受本父方案约束：

1. automatic_orchestration_routing_enforcement_plan - 定义自动协同路由、activation trace、expert 生命周期证据和 durable-team 阈值。
2. codex_user_level_context_retention_canary_plan - 保护冷启动上下文保留、canary 字面量位置、乱码检测和 replay 过滤。
3. codex_user_level_cross_session_durable_state_isolation_plan - 隔离 repo-local durable state、selector、backend readiness 和跨 session durable artifact。
4. comet_runtime_agile_focus_area_plan - 增加 Comet management record、阶段勾选门禁和 Monitoring 回退 transition。
5. implementation_plan_confirmation_gate - 要求非文档实现开始前必须有已提交的 active implementation-plan 文件；这里的 confirmation gate 指阻塞检查点，必须等用户确认已提交的方案文件后才能继续执行。
6. codex_governance_session_visibility_and_plan_lock_plan - 增加中文 routing trace 可视化、主会话提权可视化、Superpowers 证据、Spec Kit 边界和 plan lock。
7. pi_plugin_codex_user_level_sidecar_plan - 提供 Pi family、Codex -> Pi sidecar 与 oh-my-pi reference-only 边界。
8. user_level_mcp_skills_browser_cli_governance_plan - 提供 MCP、skills、browser、OpenCLI 与 CLI harness 的低 token、receipt-first 治理边界。

## 非目标

- Stage A 不实现 runtime、checker、helper 或测试变更。
- Stage A 不一次性创建所有子 implementation_plan。
- 不安装 GitHub Spec Kit，也不运行 `specify init`。
- 不为本文档包启动 OMX、LangGraph 或持久化团队。
- 不允许多个 session 同时写同一个子 implementation_plan。
- 不把本文件作为所有新 session 的冷启动必读文件。
- 不把本文件作为无关 implementation_plan 的全局父方案或运行时控制面。
- 除非用户明确要求远端发布，否则不推送 GitLab 或 GitHub。

## 当前状态

<!-- CURRENT_STATUS_START -->
阶段：Phase 2+ 并行执行治理对齐
责任会话：`codex-align-complete-flow-parent-plans-20260530`，认领父级索引维护子方案来更新本父方案族的执行语义。
当前门禁：本次只同步治理文档；完成 checker、本地提交和本地 `main` 合入后，必须停在远端发布门。
Phase 0 说明：盘点与父级索引收口已完成并进入本地 `main`，远端基线 `014b0bf` 已包含 Phase 0 发布状态。
Phase 1 说明：施工安全底座、ROB runtime/checker、自退休 helper 和完整提交流程治理已进入本地 `main`；`7e47af8` 使《完整提交流程.md》成为多 session 自动本地提交与合入的 HOW 层契约。
Phase 2+ 准入：Phase 0 不再阻塞 Phase 2；所有 eligible session 都可以按 Work-Conserving 规则并行进入，热点文件通过 hotspot lease 串行化，本地 `main` 写入通过 `local-main-retire.lock` 串行化。
远端状态：本地 `main` 当前领先 GitLab/GitHub 远端；远端发布、MR、merge 或 GitHub sync 仍必须等待用户显式授权。
<!-- CURRENT_STATUS_END -->

## 执行模型

### 层级架构图

本方案采用本方案族内部的二层级 implementation-plan 结构。只有 front matter 中 `parent_plan` 指向本父方案，或正文明确列入本方案族的 implementation plans，才是本父方案的同级子方案；`parent_parallel_orchestration_index_plan` 是索引维护子方案，不是二级父方案。无关 implementation_plan 可以没有父方案，也可以属于其他父方案。

```text
一级：父方案 / 总地图
└─ multi_plan_parallel_session_orchestration_plan.zh-CN.md
   ├─ Phase 0 / Batch 1 子方案：plan_inventory_registry_alignment_plan.zh-CN.md
   ├─ Phase 0 / Batch 1 子方案：parent_parallel_orchestration_index_plan.zh-CN.md
   │  └─ 说明：这是索引维护子方案，不拥有下级 implementation_plan 文件。
   ├─ Phase 1A / Batch 1 子方案：complete_local_commit_flow_scheduler_reorder_buffer_plan.zh-CN.md
   ├─ Phase 1-6 子方案：其他同级 child implementation plans
   ├─ Phase 7 / Batch 5 子方案：parallel_plan_docs_registry_integration_plan.zh-CN.md
   ├─ Phase 7 / Batch 5 子方案：parallel_plan_checker_ci_integration_plan.zh-CN.md
   └─ Phase 7 / Batch 5 子方案：parallel_plan_openspec_comet_archive_plan.zh-CN.md
```

本层级图只适用于本方案族，不代表 `docs_bilingual/implementation_plans/` 目录下所有 implementation_plan 的全局层级。

`Phase`、`Stage`、`Batch` 用于表示本方案族内部的工作主题、生命周期状态和创建/集成批次，不是全目录文档树层级。`parent_plan` 是可选关系，不是目录强制字段；如果某方案声明 `parent_plan` 指向本文件，则它受本文件的 Phase / Batch / 并行度 / 热点文件规则约束；如果某方案没有 `parent_plan`，或 `parent_plan` 指向其他文件，则不受本文件父子结构约束。

### Session 与 Claim 规则

- 每个 implementation_plan 是最小认领单元；本方案族子方案遵循本文件的阶段和批次规则，无关方案只遵循自己的方案或全局 checker。
- session claim 必须在写入开始前声明 implementation_plan 路径。
- 同一个 implementation_plan 同一时间只能有一个 active claim。
- 多个 session 只要认领不同 implementation_plan，且写入范围不冲突或已明确串行化，就可以并行；这些方案不必属于同一个父方案。
- `docs_bilingual/docs_registry.yaml`、CI manifest、共享 checker、`comet-state.sh`、`comet-guard.sh` 和父方案文件等热点文件必须有明确 owner。
- 每个 session 自己负责自己认领的 implementation_plan、worktree、branch、claim、receipt、ROB entry、本地提交和本地 `main` 合入。
- 本父方案不代表某个主 session 对其他 session 的运行时控制权。
- 本地 `main` 写入必须串行；后续目标是通过 `local-main-retire` lock 保护每次合入，拿到锁的 session 只合入自己已 ready 的候选包。

### Work-Conserving 会话准入

- 不再把固定 Phase 数量 cap 写成治理硬上限。
- 一个 Phase 应准入每个 eligible implementation_plan/session：状态为 active、没有 active claim、依赖满足、worktree 干净，并且写集互不冲突或已取得明确 hotspot lease。
- provider pacing、CPU、内存、终端数量、失败 gate、main 落后和 retire queue 堆积属于 resource backpressure；它们只做运行时节流，不改变“所有 eligible session 都可入场”的治理原则。
- hotspot lease 和 local-main retire lock 用来串行化共享写入；它们是 lease/lock，不是全局 Phase 数量 cap。
- Phase 1A 已增加提交重排序缓冲规则：session 可以乱序完成；后续目标是把 local `main` retire 从固定 leader 串行执行改为 `local-main-retire` lock 保护的 session-owned self-retire。
- 如果子方案存在未关闭 claim、脏 worktree、失败本地门禁、未退休 ROB entry 或未合入的本地 main 集成，不得进入下一阶段。

### 同机 Peer Session 自主合入本地 main 目标模型

本小节记录同机多 session 治理目标。它是后续子方案、checker 和 helper 的治理契约；本次 Stage B 文档更新不直接实现 runtime 脚本。

#### 摘要

- 将固定“main Codex leader 控制所有 retire”的模型，改为同机 peer session 自主执行 + 本地 `main` 写入串行保护。
- 每个 session 自己负责自己的 implementation plan、worktree、feature branch、claim、task receipt、ROB entry、本地提交、本地门禁和本地 `main` 合入尝试。
- `parent_plan` 是可选元数据。只有声明时才校验；没有该字段的方案可以是独立方案，也可以属于其他父方案。
- 新 session 读取自己的目标 implementation plan、必要 registry/checker 状态、claim 状态、receipt 状态和 ROB 状态；除非处理本文件或本文件治理的方案，否则不读取本父方案。
- 范围只覆盖同一台电脑、同一仓库、多 worktree/session；跨电脑远端锁不在范围内。
- 远端发布仍不自动执行，仍需用户明确请求。

#### 治理语义调整

- 任意 session 拿到 local-main retire lock 后，都可以临时成为本次 retire owner。
- retire owner 只合入自己的 ready branch，不替其他 session retire。
- 合入成功或失败后，retire owner 必须释放锁，或记录明确的 failed/stale 状态。
- 父方案文件是热点文件。session 修改父方案时，必须明确认领该父方案写入面。
- 普通 session 处理无关 implementation_plan 时，不需要读取或修改某个父方案。

#### 本地 main retire 锁契约

- 锁文件：`.omx/locks/local-main-retire.lock`
- 计划 helper：`tools/local_main_retire_lock.py`
- 计划命令：

```text
python tools/local_main_retire_lock.py acquire --root . --session-id <id> --branch <branch> --worktree <path> --entry-id <rob-entry> --ttl-minutes 120 --json
python tools/local_main_retire_lock.py release --root . --nonce <nonce> --json
python tools/local_main_retire_lock.py status --root . --json
```

锁结构目标：

```json
{
  "schema_version": 1,
  "lock_name": "local-main-retire",
  "owner_session_id": "session-a",
  "branch": "implement-x-session-a",
  "worktree": ".worktrees/implement-x-session-a",
  "entry_id": "rob-entry-id",
  "created_at": "...",
  "expires_at": "...",
  "nonce": "...",
  "status": "active"
}
```

行为要求：

- 获取锁必须使用原子创建；存在未过期 active 锁时 fail closed。
- stale 锁默认不自动抢占；必须显式使用 `--reclaim-stale`，先归档旧锁再获取新锁。
- 释放锁必须匹配锁内 `nonce`，避免一个 session 误删另一个 session 的锁。
- 锁文件属于 runtime state，不进入 Git 提交。

#### 自主 retire 本地流程目标

后续 helper 扩展目标是 `tools/complete_local_flow_to_remote_gate.py`，计划参数包括：

- `--self-retire` - 启用 session 自主合入本地 main 的 retire 模式。
- `--session-id <id>` - 记录本次 retire 尝试归属的 peer session。
- `--rob-entry-id <entry-id>` - 关联对应的提交重排序缓冲 entry。
- `--acquire-retire-lock` - 要求 helper 在合入前先获取 local-main retire lock。
- `--lock-ttl-minutes 120` - 设置锁过期窗口，用于 stale lock 报告。

固定执行顺序：

1. 确认当前 worktree 是 feature branch，不是 `main`。
2. 确认 feature worktree clean。
3. 运行 feature local gate。
4. 运行 local MR review。
5. 获取 `local-main-retire.lock`。
6. 拿到锁后重新确认 primary root clean 且位于本地 `main`。
7. fetch 并确认本地 `main` 不落后 `gitlab/main`。
8. 运行 claim / receipt / ROB checker。
9. 创建 rollback backup ref。
10. 执行 `git merge --ff-only <feature-branch>`。
11. 运行 post-merge local gate。
12. 将 ROB entry 更新为 `retired`，记录 lock nonce、rollback ref、local main commit 和 evidence。
13. 释放 retire lock。
14. 停在远端发布门。

#### Checker 与 Gate 目标

- `check_implementation_plan_claim_lock.py`：保留同一方案单 active claim 规则；不要求必须存在 `parent_plan`。
- `check_worktree_task_receipt.py`：receipt 记录 session 自己负责的 plan、branch、worktree 和 lifecycle；不要求父方案。
- `check_commit_reorder_buffer.py`：新增 ROB 字段 `retire_mode`，用于说明本地 main retire 由谁负责；`legacy_leader_serial` 表示旧的固定 leader 串行合入路径，`self_retire_lock` 表示拿到 retire lock 的 peer session 合入自己的 branch。当 `self_retire_lock` entry 为 retired 时，要求 `retire_owner_session_id`、`retire_lock_nonce`、`rollback_ref`、`local_main_commit` 与非空 evidence。
- 新增 `check_local_main_retire_lock.py`：校验锁 JSON schema、active lock 唯一性和 stale lock 报告。
- 只有对应 runtime helper 存在后，才把新 checker 接入 OpenSpec guard 与 local gate。

#### 后续实现验证目标

- 两个 session 同时获取 `local-main-retire.lock`：第一个成功，第二个 fail closed。
- 使用错误 nonce release：不得释放锁。
- stale 锁默认不能抢占；使用 `--reclaim-stale` 后归档 stale 锁并获取新锁。
- 没有 `parent_plan` 的 implementation plan：通过校验。
- 声明了 `parent_plan` 但路径不存在：checker 失败。
- 两个 active claim 指向同一个 implementation plan：checker 失败。
- 两个 active claim 指向不同 implementation plan：checker 通过。
- `self_retire_lock` 模式的 retired ROB entry 缺少 lock nonce：checker 失败。
- `complete_local_flow_to_remote_gate.py --self-retire --execute` 在合入前获取锁、合入后释放锁。
- 合入失败时必须释放锁或记录明确 failed/stale 状态，不能静默遗留 active lock。
- local-main 合入流程不得 push GitLab、不得创建 MR、不得同步 GitHub。

#### 假设

- 本阶段只支持同机多 session / 多 worktree 协调。
- 每个 session 只 retire 自己的 feature branch。
- 去掉固定主会话总控，不等于去掉本地 `main` 写入串行保护。
- 远端发布仍是用户明确授权步骤。


## 阶段与子方案拆分

### Phase 0：盘点与父级编排

目的：建立父级执行地图并确认 registry 健康状态。

候选子方案：

1. `plan_inventory_registry_alignment_plan` - 盘点当前方案状态、registry、锚点和 evidence index 健康度。
2. `parent_parallel_orchestration_index_plan` - 维护父级阶段图、子方案登记表和依赖表。

条件后续：只有当 inventory 子方案发现 canary registry、双语配对、锚点或 evidence index 存在真实缺陷时，才创建 canary registry recovery 子方案。

准入规则：本父方案确认后，所有 eligible session 均可并行；registry 与层级维护热点同一时间只能有一个 hotspot lease owner。

### Phase 1：施工安全底座

目的：在 runtime-heavy 工作开始前，先让并行执行安全。用户级安装和更新通道，包括 Pi family 或 harness 通道，必须先满足 receipt-first，才能被视为 active runtime surface。

候选子方案：

1. `complete_local_commit_flow_scheduler_reorder_buffer_plan` - Phase 1A 早期安全底座，定义 ROB 风格多 session 执行、热点 fence、ready queue 和 local main 串行 retire；后续消费者将把 retire 从固定 leader 模型推进到 `local-main-retire` lock 保护的 session self-retire。
2. `formal_plan_confirmation_gate_runtime_plan` - 强制“仅对话确认 plan 不足以进入实现”。
3. `portable_implementation_plan_claim_lock_plan` - 实现不依赖 OMX 或 LangGraph 的子方案单 active session 锁。
4. `implementation_plan_registry_active_state_plan` - 强制 active 状态、双语配对和 docs registry 一致。
5. `main_session_escalation_visibility_plan` - 增加主会话可见的待授权和提权预检表面。

准入规则：所有 eligible 子方案均可并行；`docs_bilingual/docs_registry.yaml` 每批只能由一个 hotspot lease owner 写入。

### Phase 2：上下文与 UTF-8 安全

目的：在更重的 orchestration 自动化之前，稳定冷启动、replay 和乱码边界。

候选子方案：

1. `context_retention_canary_literal_boundary_plan` - 将 canary 字面量限制在 startup summary。
2. `startup_mojibake_utf8_recovery_plan` - 加固乱码检测与 UTF-8 canonical recovery。
3. `session_replay_context_filtering_plan` - 过滤 assistant/session replay 表面，避免 stale canary 或乱码重新进入 prompt。
4. `launcher_payload_context_boundary_plan` - 保持 launcher payload 边界，本阶段不修改用户级配置。

准入规则：所有 eligible 子方案均可并行；startup summary 文件必须取得 hotspot lease 并串行写入。

### Phase 3：Durable State 与跨 Session 隔离

目的：确保 durable-state 选择和检查在跨仓库、worktree、session 时安全。Pi/harness state、receipt、rollback pointer 与 sidecar artifact 不得跨 repository、worktree 或 session 泄漏。

候选子方案：

1. `repo_local_selector_ownership_plan` - 强制 repository-local active selector 归属。
2. `durable_capability_readiness_projection_plan` - 区分 installed、enabled、selected 和 ready。
3. `durable_smoke_adoption_gate_template_plan` - 在 live durable smoke 或 apply-mode adoption 前创建 gate template 和字段 checker。
4. `legacy_durable_residue_classification_plan` - 对陈旧 `.omx/state` residue 分类，但不自动接管。
5. `worktree_receipt_claim_lifecycle_plan` - 定义 active、paused、completed、stale 和 cleaned claim/receipt 生命周期。
6. `portable_no_backend_parallel_session_plan` - 在没有 OMX 和 LangGraph 时支持 Git/Python-only 并行 session。

准入规则：所有 eligible 子方案均可并行；`.omx/state` 写入按仓库和 worktree hotspot lease 串行化。

### Phase 4：自动路由与稳定会话表面

目的：让协同路由自动、可审计，并确保对话中面向用户展示的固定标签保持为 `Routing trace` 和 `Updated Plan`。标签下的解释内容可以使用中文；`Updated Plan` 必须保持复选框/状态清单语义，不能退化为纯段落。Routing 与 evidence 记录必须区分 Pi/harness sidecar evidence 和由当前 owner session 负责的最终 verification evidence；保存版结构化 evidence 可继续保留 ASCII 阈值、blocker token、schema key、文件名和命令参数。

候选子方案：

1. `chinese_routing_trace_conversation_surface_plan` - 要求用户可见的 `Routing trace` 与 `Updated Plan` 标签保持稳定，允许中文解释内容，并保留 `Updated Plan` 复选框/状态清单语义。
2. `routing_trace_structured_evidence_schema_plan` - 为保存版证据保留机器可读 ASCII 阈值和 blocker token。
3. `prompt_independent_activation_parity_plan` - 确保路由不依赖用户是否说出“并行”或“专家”。
4. `expert_lifecycle_timeout_pacing_evidence_plan` - 将 timeout、stall 和 pacing 视为非证据，并要求有界处理。
5. `langgraph_state_release_evidence_plan` - 拒绝 LangGraph 工作完成后仍保留 stale `running` 状态。
6. `role_routing_fanout_write_ownership_plan` - 强制最小充分角色选择和 fan-out 写入归属。
7. `collaboration_evidenceguard_and_bilingual_openspec_surface_plan` - 让 evidenceguard、fixtures、CI 注册和双语 OpenSpec stable spec surface 由一个 owner 串行处理。

准入规则：所有 eligible 子方案均可并行；共享 routing checker 和 OpenSpec spec surface 必须通过 hotspot lease 串行化。

### Phase 5：Comet Runtime 敏捷管理循环

目的：在安全与可视化基础稳定后，实现 Comet runtime 管理循环。

候选子方案：

1. `comet_management_record_bootstrap_plan` - 创建并验证 management record。
2. `comet_phase_checklist_gate_plan` - 前进 transition 前要求阶段勾选证据。
3. `comet_monitoring_return_transition_plan` - 支持 Monitoring 决策回退到 Open、Design、Build 或 Verify。
4. `comet_superpowers_visibility_plan` - 让 Comet 阶段显式展示 Superpowers HOW-layer skill 使用。
5. `comet_runtime_policy_checker_alignment_plan` - 对齐 policy、OpenSpec specs、checker 覆盖和集成门禁。

准入规则：所有 eligible 子方案均可并行。`comet-state.sh` 和 `comet-guard.sh` 同一时间只能有一个 hotspot lease owner。

### Phase 6：Spec Kit 边界

目的：防止 GitHub Spec Kit 成为竞争性治理层。同样的 subordinate-adapter 规则也适用于 oh-my-pi、Pi sidecar 与 CLI harness 引用：它们只能是 reference 或 adapter surface，不是项目治理层。

候选子方案：

1. `spec_kit_subordinate_adapter_governance_plan` - 将 Spec Kit 文档化为可选从属 adapter 或模板来源。
2. `spec_kit_authority_guard_plan` - 没有单独 active plan 时阻止 `specify init --force`、`.specify/` 或治理权威迁移。

准入规则：写集互不冲突或已取得 hotspot lease 的所有 eligible 子方案均可并行。

### Phase 7：集成、验证与归档

目的：把并行工作收敛为串行本地 main 包，并在适用时归档已完成 OpenSpec 工作。集成报告必须在考虑任何 runtime 或用户级变更前声明每个 Pi/harness lane 的状态：`reference-only`、`planned`、`on-demand` 或 `active-candidate`。

候选子方案：

1. `parallel_plan_docs_registry_integration_plan` - 验证 docs registry、双语配对和 implementation-plan rules。
2. `parallel_plan_checker_ci_integration_plan` - 验证 checker、unit 和 local CI 覆盖。
3. `parallel_plan_openspec_comet_archive_plan` - 验证 OpenSpec/Comet guard 健康，并归档已完成变更。

延后后续：publication readiness 不作为 Stage B 子方案创建，因为远端发布不在本次范围内，除非用户明确批准。

准入规则：所有 eligible 验证 session 都可以并行准备证据，但 Phase 7 集成热点和每次 local-main retire 必须通过 lease/lock 串行化。
## 紧凑子方案状态索引

<!-- CHILD_PLAN_STATUS_INDEX_START -->
| Phase | 子方案 | 状态 | 当前证据 |
| --- | --- | --- | --- |
| Phase 0 | `plan_inventory_registry_alignment_plan` | 功能分支内已收口，等待本地合入 | `docs_bilingual/implementation_evidence/phase0_plan_inventory_registry_alignment_20260530.json`；未发现缺失登记路径或缺失双语 companion 路径。 |
| Phase 0 | `parent_parallel_orchestration_index_plan` | 功能分支内已收口，等待本地合入 | 父方案当前状态、Phase 0/Phase 1 证据、依赖说明和 Phase 2 准入文本已通过稳定锚点更新。 |
| Phase 1A | `complete_local_commit_flow_scheduler_reorder_buffer_plan` | 已实现并合入 | ROB runtime/checker 包已合入本地 `main`；后续 self-retire runtime 恢复记录在 `898f9d0`。 |
| Phase 1 | `formal_plan_confirmation_gate_runtime_plan` | 已实现并合入 | Phase 1 收口证据保留在本地 git 历史和现有证据索引中。 |
| Phase 1 | `portable_implementation_plan_claim_lock_plan` | 已实现并合入 | Portable claim lock 已作为单方案单会话归属的基础能力。 |
| Phase 1 | `implementation_plan_registry_active_state_plan` | 已实现并合入 | Registry active-state 与双语配对门禁由 implementation-plan rules 覆盖。 |
| Phase 1 | `main_session_escalation_visibility_plan` | 已实现并合入 | 主会话提权可视化已属于 Phase 1 收口包。 |
<!-- CHILD_PLAN_STATUS_INDEX_END -->

## 依赖与 Phase 2 准入说明

<!-- PHASE_ADMISSION_NOTES_START -->
- Phase 0 已完成，不再作为 Phase 2 的当前阻塞门；后续 Phase 2+ session 只需确认自己的 implementation plan 为 `status: active`、没有其他 active claim、依赖满足、worktree 干净，且写集不冲突或已取得 hotspot lease。
- Phase 1 仍是后续阶段的安全底座：plan confirmation、claim locking、registry active-state checks、ROB ordering、self-retire lock 和《完整提交流程.md》必须保持可用。
- Phase 2+ 子 session 按 Work-Conserving 规则并行运行；startup summary、UTF-8/mojibake、docs registry、OpenSpec stable spec、CI manifest、checker schema 等热点文件必须由明确 owner 串行写入。
- 本地 `main` 合入不是固定 main session 总控；持有 `local-main-retire.lock` 的 session 只可自退休自己拥有且已 ready 的候选包。
- 远端发布不是 Phase 准入条件；除非用户明确要求远端发布，否则所有 session 在本地 `main` 合入后停止在远端发布门。
<!-- PHASE_ADMISSION_NOTES_END -->


## Stage B 创建规则

进入 Stage B 后，子方案按批次创建：

- Batch 1：Phase 0 和 Phase 1 子方案，并把 Phase 1A complete-flow 调度器/ROB 子方案作为早期安全底座补充。
- Batch 2：Phase 2 和 Phase 3 子方案。
- Batch 3：Phase 4 子方案。
- Batch 4：Phase 5 和 Phase 6 子方案。
- Batch 5：Phase 7 集成子方案。

每个子方案必须包含：

- YAML front matter，含 `doc_id`、`lang`、`status: active`、`doc_class: implementation_plan` 和双语 companion 元数据。
- CURRENT_STATUS 锚点记录当前阶段和检查点，TASK_BACKLOG 锚点记录复选框任务项，EVIDENCE_INDEX 锚点记录轻量 commit/report 引用；这些锚点是脚本用于局部更新的稳定 HTML 注释。
- 明确文件归属和热点文件串行说明。
- 该子方案或阶段的 Work-Conserving 准入规则、hotspot lease 要求、resource backpressure 说明和验证门禁。
- 本地验证命令和预期门禁行为。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Stage A：创建英文 ASCII 父级 implementation plan。
- [x] Stage A：创建中文对照父级 implementation plan。
- [x] Stage A：在 `docs_bilingual/docs_registry.yaml` 登记父方案。
- [x] Stage A：使用中文提交信息提交父级文档包。
- [x] Stage A：把父级文档包合入本地 `main`。
- [x] Stage A：停止并要求用户确认本父方案后再进入 Stage B 子方案创建。
- [x] Stage B：为 Phase 0 和 Phase 1 创建 Batch 1 子 implementation_plan。
- [x] Stage B：为 Phase 2 和 Phase 3 创建 Batch 2 子 implementation_plan。
- [x] Stage B：为 Phase 4 创建 Batch 3 子 implementation_plan。
- [x] Stage B：为 Phase 5 和 Phase 6 创建 Batch 4 子 implementation_plan。
- [x] Stage B：为 Phase 7 集成创建 Batch 5 子 implementation_plan。
- [x] Stage B 父方案修订：加入二层级架构图，并吸收 Pi family / oh-my-pi / CLI harness reference-only 边界到父级编排方案。
- [x] Stage C：子方案确认后，实现 portable child-plan claim lock。
- [x] Stage B Batch 1 补充：创建 Phase 1A complete-flow 调度器/ROB 子方案，并更新完整本地提交流程治理。
- [x] Stage B 父方案范围修订：收窄本文件父方案语义，明确它只约束本方案族，不控制无关 implementation_plan。
- [x] Stage B 父方案范围修订：明确 `parent_plan` 是可选局部关系，新 session 不默认读取本文件。
- [x] Stage B 父方案范围修订：结构化记录同机 peer session self-retire 目标、锁契约、checker 目标、验证目标和假设。
- [x] Stage B 父方案修订：将固定 Phase 数量 cap 替换为 Work-Conserving all-eligible session admission、hotspot lease、resource backpressure 语言和 ROB 支撑的串行 local-main retire。
- [x] Stage A 恢复：记录 self-retire runtime 来源提交存在，但当时本地 `main` 缺少 runtime 文件；非文档恢复前必须停止等待确认。
- [x] Stage B runtime 恢复：恢复 self-retire runtime helper/checker 行为，并在 `898f9d0` 合入本地 `main`。
- [x] Phase 0 收口：在 Phase 2 准入前收口 inventory registry alignment 子方案和 parent orchestration index 子方案。
- [x] 后续阶段：Phase 0 收口包已经合入本地 `main`；Phase 2 context 与 UTF-8 safety 子方案已按 Work-Conserving 模型启动，部分包已进入本地 `main`。
- [x] Phase 4 父子方案治理更新：把会话表面覆盖从 routing trace 扩展到 `Routing trace` 与 `Updated Plan`，保持这两个标签稳定，保留 `Updated Plan` 复选框/状态清单语义，并保留保存版 evidence 的机器可读 ASCII token。
<!-- TASK_BACKLOG_END -->

## 验收标准

Stage A 验收条件：

- 英文主版父方案存在且为 ASCII-only。
- 中文对照父方案存在。
- `docs_bilingual/docs_registry.yaml` 将这对文件登记为 `doc_class: implementation_plan` 和 `status: active`。
- 父方案列出阶段、候选子方案、依赖顺序、Work-Conserving 准入、hotspot lease和热点文件串行规则。
- Stage A 使用中文提交信息。
- Stage A 合入本地 `main`。
- Stage A 不修改 runtime、checker、helper 或测试行为。
- assistant 在 Stage B 前停止并要求用户确认本父方案。

Stage B 后续确认后的验收条件：

- 子方案被创建为独立认领单元。
- 没有子方案缺少双语配对或 registry 登记。
- 每个子方案声明文件归属、Work-Conserving 准入、hotspot lease和验证门禁。
- 相关子方案未确认前，不开始非文档实现。
- Phase 1A 在后续多 session runtime 执行前先记录 scheduler/ROB 治理。
- 本父方案明确只约束本方案族；无关 implementation_plan 可以无父方案或属于其他父方案。
- 新 session 不默认读取本文件，除非处理本文件、其子方案或正文列出的相关方案。
- 后续同机多 session 目标是 session 自主负责自己的提交和本地 `main` 合入，并用 `local-main-retire` lock 保持本地 `main` 写入串行。
- Phase 4 子方案必须保持面向用户的 `Routing trace` 与 `Updated Plan` 固定标签；解释内容可以使用中文；`Updated Plan` 必须保留复选框/状态清单语义；内部工具名、schema key、阈值 token、blocker token、文件名和 CLI 参数可保持 ASCII。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-05-30 Phase 4 固定标签修正：分支 `implement-routing-updated-plan-fixed-labels-20260530c` 更新本父方案与 `chinese_routing_trace_conversation_surface_plan` 子方案；`Routing trace` 与 `Updated Plan` 保持英文用户可见标签，`Updated Plan` 保持复选框/状态清单语义，中文解释内容仍允许；远端发布仍未授权。
- 2026-05-30 Phase 4 会话表面治理更新：分支 `chinese-routing-updated-plan-20260530` 曾把会话表面覆盖从 routing trace 扩展到 updated plan；其中“固定标签应替换为中文标题”的旧表述已由上一条固定标签修正取代；远端发布仍未授权。
- 2026-05-30 完整提交流程对齐包：分支 `align-complete-flow-parent-plans-20260530` 由 `codex-align-complete-flow-parent-plans-20260530` 认领 `parent_parallel_orchestration_index_plan`，ROB entry `rob-align-complete-flow-parent-plans-20260530` 记录父方案族文档候选包；本包把父方案和声明 `parent_plan` 指向本文件的子方案统一对齐到《完整提交流程.md》的 session-owned self-retire、`local-main-retire.lock` 和远端发布门模型。
- 2026-05-30 Phase 0 收口包：在分支 `phase0-plan-index-closure-20260530` 收口 `plan_inventory_registry_alignment_plan` 和 `parent_parallel_orchestration_index_plan`；机器可读盘点证据为 `docs_bilingual/implementation_evidence/phase0_plan_inventory_registry_alignment_20260530.json`；在本包完成本地门禁、local MR review 并合入本地 `main` 前，Phase 2 仍保持阻塞。
- 2026-05-30 self-retire runtime 恢复：本地 `main` 已在 `898f9d0` 包含恢复后的 self-retire runtime helper/checker 包，替代早先 `b4af80f` 的待恢复说明。
- 2026-05-29 Stage A 恢复文档包：记录当时本地 `main`=`b4af80f` 尚未包含 self-retire runtime helper/checker，虽然来源提交 `867f882` 存在于 `decentralize-session-self-retire-20260529`；该问题随后已由 `898f9d0` 解决。
- 2026-05-29 父方案范围修订：结构化吸收同机多 session 自主合入治理对话，明确本文件仍是本方案族父方案，但不控制无关 implementation_plan；新增 `parent_plan` 可选局部生效、新 session 非默认读取、session-owned self-retire 与 `local-main-retire` lock 后续目标。
- 2026-05-29 Phase 1 收口：Phase 1 子方案均已实现、合入本地 `main` 并完成验证；证据提交包括 `4479593`、`e81d840`、`fb3ad75`、`54a965d` 和 `e23c40b`；ROB 合入后 local gate 已通过。
- 2026-05-29 Stage B Batch 1 补充：新增 Phase 1A complete-flow 调度器/ROB 子方案，更新 `完整提交流程.md`，并把 portable claim / receipt 子方案标为下游消费者；随后 ROB runtime/checker 包已在 `4479593` 合入本地 `main`。
- 2026-05-28 Stage C 本地集成：portable child-plan claim lock 已快进合入本地 `main`；合入后 local gate 通过；远端发布尚未授权。
- 2026-05-28 Stage C 验证：portable child-plan claim lock 在 `implement-portable-plan-claim-lock-20260528` 分支通过聚焦测试、local gate 和 local MR review；随后已按上一条记录串行合入本地 `main`。
- 2026-05-28 Stage C 进入：通过 `portable_implementation_plan_claim_lock_plan` 开始实施 portable child-plan claim lock；本轮工作在 `implement-portable-plan-claim-lock-20260528` 分支隔离完成后再合入本地 `main`。
- 2026-05-28 Stage B 父方案修订：加入二层级架构图，并从 `pi_plugin_codex_user_level_sidecar_plan` 与 `user_level_mcp_skills_browser_cli_governance_plan` 吸收 Pi family / oh-my-pi / CLI harness reference-only 边界；commit 记录在本地 git 历史中。
- 2026-05-28 Stage B 子方案创建包：创建并登记 33 个 active 子 implementation_plan 的英文主版和中文对照版；最终 commit 记录在 assistant 回复和本地 git 历史中。
- 2026-05-28 Stage A 父级方案包：已用 `ac867ff` 提交并合入本地 `main`；验证包括 `check_implementation_plan_rules.py --root . --json`、`check_precommit_update_archive.py --root . --json`、`tools/ci/local_gate.ps1 -StepTimeoutSeconds 600` 和 `tools/ci/local_mr_review.ps1`。
<!-- EVIDENCE_INDEX_END -->
