---
doc_id: complete_local_commit_flow_scheduler_reorder_buffer_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/complete_local_commit_flow_scheduler_reorder_buffer_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
stage: Stage B child plan
phase: 1
phase_label: Phase 1A
batch: 1
priority: early-foundation
confirmation_required: true
---

# 完整本地提交流程调度器重排序缓冲实施方案（中文对照）

> 面向 agentic worker：本子方案经用户确认后，实施时必须使用 superpowers:executing-plans 或 superpowers:subagent-driven-development；任务使用复选框跟踪。

## 目标

通过允许 session 在隔离 worktree 中并行执行、但要求 ROB 风格串行 retire 到本地 `main`，让多 session 本地提交流程变得安全。
当拥有候选包的 session 持有仓库本地 local-main retire lock 时，退休执行者可以是该 session 自己。

## 来源方案

- multi_plan_parallel_session_orchestration_plan
- `完整提交流程.md` - 记录完整本地提交流程的 ROB 并发治理规则。 中的完整本地提交流程治理
- portable_no_backend_parallel_session_plan
- worktree_receipt_claim_lifecycle_plan

## 范围决策

- 层级：`D:/PythonProject_langgraph` 项目级治理和后续 runtime/checker 规划。
- 父方案：`docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md`。
- 批次：Stage B Batch 1 补充子方案。
- 阶段：Phase 1A，归入 Phase 1 施工安全底座。
- 状态：本文件是 active 子 implementation_plan。本包只创建治理方案；runtime/checker 实现必须等待后续用户确认。
- 远端发布：不在本子方案范围内，除非用户明确要求远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
Stage: Phase 1A follow-up active. This pass implements automatic local `main` integration after implementation authorization plus passing local gates, default safe cleanup, and a mandatory stop at the remote publication gate.
Owner session: `automate-local-main-integration-20260601`.
Current gate: focused tests and scripted governance checks now cover completed claim/receipt recording, default `cleanup_integrated_worktree.py --execute` cleanup, `--preserve-carrier`, and the remote-publication gate. Before final closure, run precommit/update-archive, OpenSpec guard, local gate, and local MR review, then invoke `complete_local_flow_to_remote_gate.py --execute` from the primary root so the target feature worktree can be removed safely.
<!-- CURRENT_STATUS_END -->

## 文件归属

当前文档治理包拥有：

- `完整提交流程.md` - 记录完整本地提交流程的 ROB 并发治理规则。
- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md` - 记录父方案 Phase 1A 位置和调度依赖。
- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md` - 同步中文父方案对照版。
- `docs_bilingual/implementation_plans/complete_local_commit_flow_scheduler_reorder_buffer_plan.md` - 定义本子方案英文主版。
- `docs_bilingual/implementation_plans/complete_local_commit_flow_scheduler_reorder_buffer_plan.zh-CN.md` - 定义本子方案中文对照版。
- `docs_bilingual/docs_registry.yaml` - 登记本双语子方案。

runtime/checker 实现拥有：

- `tools/commit_reorder_buffer.py` - 后续管理 ROB entry 预测、入队、状态、退休和 flush。
- `tools/check_commit_reorder_buffer.py` - 后续验证 ROB 就绪、热点 fence 和退休证据。
- `tools/local_main_retire_lock.py` - 使用 nonce lock 串行化对等 session 本地 main 写入。
- `tools/check_local_main_retire_lock.py` - 验证 active lock schema 和 stale-lock 状态。
- `tools/complete_local_flow_to_remote_gate.py` - 在本地 main 写入前后 acquire/release lock，并记录 ROB 自退休证据。
- local CI 或 local MR review 接线
- ROB entry 状态、热点 fence、串行 retire 的聚焦测试

## 热点串行规则

以下热点同一时间只能由一个 session 拥有：

- 完整本地提交流程政策
- 父级编排方案中英文对
- docs registry
- 后续 ROB helper/checker 脚本
- claim 与 receipt lifecycle schema 表面

## 调度模型

本子方案把调度器和 CPU 提交原则转换为仓库治理：

- Work-Conserving admission：每个 eligible session 在 claim、dependency、hotspot lease、resource backpressure 和 local-main retire gate 允许时均可入场。
- Reorder Buffer：候选包在进入 local `main` 前先缓冲。
- Out-of-order execution：写集互不重叠的 session 可以乱序完成。
- In-order retirement：local `main` 集成必须串行执行，lock owner 是执行退休的 session。
- Scoreboarding / Tomasulo 就绪判断：依赖、claim、receipt、写集和 gate 共同决定 entry 是否 ready。
- Load/store queue 与 memory fence：共享治理文件和 schema 表面强制串行化。
- Branch prediction / speculation：session 开始前预测写集和依赖；预测失败则 blocked、flushed、split 或 requeued。
- Backpressure / priority aging：gate 失败或 retire queue 堆积时降低并发，长期 ready entry 必须显式暴露。
- Checkpoint / rollback：每次 retire 都需要 rollback ref 和 evidence。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] 把本子方案放入 Phase 1A，而不是靠后的阶段或新增 Phase 8。
- [x] 更新 `完整提交流程.md`，加入 ROB 风格多 session 执行和串行 retire 规则。
- [x] 更新父级编排方案中英文对，加入 Phase 1A 子方案和 Batch 1 补充状态。
- [x] 在 `docs_bilingual/docs_registry.yaml` 登记本双语子方案。
- [x] 把 portable no-backend session 和 worktree receipt lifecycle 方案标为下游消费者。
- [x] 本地 main 合入后先确认本子方案，再进入 runtime/checker 实现。
- [x] 定义 ROB entry schema 和非 Git 运行态目录，默认 `.omx/commit-rob/`。
- [x] 实现 `tools/commit_reorder_buffer.py` 命令：`predict`、`enqueue`、`status`、`retire`、`flush`。
- [x] 实现 `tools/check_commit_reorder_buffer.py`，检查 claim 唯一性、热点 fence、ready entry 可 retire 和 retired evidence。
- [x] 增加聚焦测试：互不重叠 ready entry、热点冲突、分支预测失败、gate 失败和 backpressure。
- [x] runtime helper 实现后，把 checker 接入 local gate 或 local MR review。
- [x] 扩展 `retire_mode=self_retire_lock`、`retire_owner_session_id` 和 `retire_lock_nonce` 字段。
- [x] 增加仓库本地 local-main retire-lock helper 和 checker。
- [x] 更新完整本地流程 helper，使拥有候选包的 session 在持有 local-main lock 时自退休 ready package。
- [x] 将固定 Phase 级并行上限替换为 work-conserving all-eligible session admission。
- [x] 增加 checker/test 覆盖，防止后续治理重新把 2/3/4/6 Phase cap 写成硬上限。
- [x] 重新打开 hardening：记录 `--self-retire` 缺少 ROB entry 不能在 merge 后才失败。
- [x] 在 `complete_local_flow_to_remote_gate.py` 中增加 ROB entry 读取与 `preflight_self_retire_rob_entry(...)`。
- [x] 缺少 ROB entry 时必须在 acquire lock、rollback ref 和 merge 前 fail closed。
- [x] `state != ready` 时必须在 acquire lock、rollback ref 和 merge 前 fail closed。
- [x] session、branch 或 implementation plan 与 ROB entry 不匹配时必须在 merge 前 fail closed。
- [x] `precommit_update_archive`、`local_gate` 或 `local_mr_review` 未通过时必须在 merge 前 fail closed。; gate condition: these fields record required pre-merge evidence.
- [x] ready entry 成功路径仍允许 merge 后记录 `self_retire_lock` retired metadata。
- [x] 增加聚焦测试并登记/运行相关 checker。
- [x] Automatic local `main` integration: implementation authorization plus passing local gates is sufficient; no extra local-merge confirmation is required when the guarded helper can complete the flow.
- [x] Default safe cleanup: `complete_local_flow_to_remote_gate.py --execute` records completed claim/receipt evidence, closes the remote-publication gate, and runs `cleanup_integrated_worktree.py --execute` unless `--preserve-carrier` is explicit.
- [x] User-level default: installer/startup instruction surfaces now carry the same project-template default while keeping remote publication as a separate explicit approval gate.
<!-- TASK_BACKLOG_END -->

## 验证门禁

除非后续经确认的更新给出更窄且有理由的命令列表，否则本地 `main` 合入前运行：

```powershell
python tools/check_precommit_update_archive.py --root . --json
python tools/check_implementation_plan_rules.py --root . --json
python tools/check_local_flow_scripted_enforcement.py --root . --json
```

如果当前分支可用，还应在本地 main 合入前运行 shared local gate 和 local MR review。

## 验收标准

- `完整提交流程.md` - 记录完整本地提交流程的 ROB 并发治理规则，说明 ROB 缓冲、乱序执行、串行 retire、热点 fence、分支预测失败处理、backpressure、rollback evidence，以及通过 local-main lock 执行对等 session 自退休。
- 父方案把本子方案列入 Phase 1A / Batch 1 补充安全底座工作。
- portable no-backend 与 receipt lifecycle 方案引用本方案作为上游调度契约。
- 英文主版保持 ASCII-only，中文对照版已登记。
- 不要求一个固定控制 session 负责每次 local-main retirement；每个 session 可在 lock 和 gate 允许时退休自己的 ready package。
- `--self-retire` 在缺少 ready ROB entry、owner 不匹配或必要 gate 未通过时，必须在 acquire lock、rollback ref 和 merge 前失败。
- 不把固定 Phase 级 2/3/4/6 session cap 视为治理硬上限；每个 eligible child plan 都可入场，只有 claim、hotspot、resource-backpressure 和 local-main retire lock 会串行化工作。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-01 automatic local integration follow-up: updated `complete_local_flow_to_remote_gate.py` to record completed claim/receipt evidence, close the remote-publication gate, and call `cleanup_integrated_worktree.py --execute` by default unless `--preserve-carrier` is explicit; added focused tests for default cleanup and carrier preservation; updated project and user-level instruction/checker surfaces.

- 2026-05-31 ROB retire preflight implementation: 已新增 `preflight_self_retire_rob_entry(...)`、`REQUIRED_SELF_RETIRE_GATES` 与 `test/check_complete_local_flow_self_retire_preflight.test.py`；RED 证明旧 helper 可能先改动本地 `main` 或接受不匹配 metadata，随后 focused GREEN 已通过，等待更广验证。
- 2026-05-31 ROB retire 前置硬门重开：确认旧 helper 会把 ROB retire metadata 放在 merge 后记录；本次要求先校验 ready ROB entry、owner 和 gate 状态，再允许本地 `main` 变更。
- 2026-05-30 完整提交流程对齐：`7e47af8` 已把《完整提交流程.md》更新为多 session 自动本地提交与本地 `main` 合入的 HOW 层契约；本次父方案族对齐包把下游子方案的固定 leader 串行语义替换为 session-owned self-retire。
- 2026-05-29 runtime/checker 实现：新增 `tools/commit_reorder_buffer.py`、`tools/check_commit_reorder_buffer.py`、聚焦测试、local gate manifest 登记和 OpenSpec guard 接线；聚焦测试、Python manifest、precommit/update-archive、OpenSpec guard JSON、local MR review 与 local gate 已通过；已在 `4479593` 合入本地 `main`，rollback ref 为 `refs/backup/local-main/20260529-1259-before-complete-flow-rob-runtime`，合入后 local gate 已通过，ROB entry 已 retired。
- 2026-05-29 文档治理包：创建 active Phase 1A 子方案，并更新 complete-flow、父方案和消费者方案引用；已在 `ebe5f69` 合入本地 `main`，随后才进入 runtime/checker 实现。
- 2026-05-29 self-retire 扩展：增加 lock-backed peer-session local-main retirement 语义，并链接到 `self_retiring_peer_session_local_main_plan`；等待最终本地验证和集成证据。
<!-- EVIDENCE_INDEX_END -->
