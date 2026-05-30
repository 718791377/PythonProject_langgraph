---
doc_id: self_retiring_peer_session_local_main_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/self_retiring_peer_session_local_main_plan.md
stage: Stage B runtime/checker recovery
priority: early-foundation
confirmation_required: true
---

# 对等会话自退休本地 main 集成实施方案（中文对照版）

## 目标

允许每个 Codex session 自己负责自己的 implementation plan、feature branch 或 worktree、验证、提交和本地 `main` 合入尝试，不再要求固定的 main-controller session。
本地 `main` 的实际写入仍然必须通过仓库本地 nonce 锁串行化。

## 范围决策

- 层级：本仓库的项目级治理与 runtime/checker 实现。
- 父方案：不要求父方案；本方案刻意保持独立，因为不是每个 implementation plan 都属于同一个父级方案族。
- 关联方案：`complete_local_commit_flow_scheduler_reorder_buffer_plan` - 提供本方案扩展的 ROB 状态与退休元数据。
- 关联方案：`multi_plan_parallel_session_orchestration_plan` - 继续作为一个可选方案族存在，不是所有方案的全局冷启动父方案。
- 远端发布：除非用户明确要求远端发布，否则不在范围内。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: active
Stage: Stage B runtime/checker recovery
Owner session: `recover-self-retire-runtime-stageb-20260529` on branch `recover-self-retire-runtime-stageb-20260529`
Current gate: validate the restored runtime/checker/test package, commit with a Chinese message, run local MR review and local gate, merge to local `main`, then stop at the remote publication gate.
Source commit: `867f882`; Stage A was integrated on local `main` at `655882c` before this runtime recovery.
Last updated: 2026-05-29
<!-- CURRENT_STATUS_END -->

## 语义术语

| 术语 | 含义 |
| --- | --- |
| `self_retire_lock` | retire mode，表示产出该候选包的对等 session 在写本地 `main` 前获取了仓库本地 local-main 锁，而不是由固定控制会话代为退休。 |
| `retire_mode` | ROB 字段，用于记录 retired entry 使用旧的控制会话串行退休，还是使用对等 session 自退休。 |
| `retire_owner_session_id` | ROB 字段，用于记录被允许退休自身候选包的 session 身份。 |
| `retire_lock_nonce` | ROB 字段，用于保存 local-main retire lock 返回的 nonce，证明退休 session 曾持有该锁。 |
| `local-main-retire.lock` | 仓库本地锁文件，用于在多个对等 session 之间串行化本地 `main` 写入。 |

## 文件归属

- `tools/local_main_retire_lock.py` - 实现本地 `main` 集成锁的 acquire、status、stale-reclaim 和 nonce release。
- `tools/check_local_main_retire_lock.py` - 验证 active lock schema；stale lock 只警告，没有 lock 时应通过。
- `tools/complete_local_flow_to_remote_gate.py` - 增加对等 session 自退休参数，并在本地 `main` 写入前后包裹锁。
- `tools/commit_reorder_buffer.py` - 在 ROB entry 自退休时记录 `retire_mode`、`retire_owner_session_id` 和 `retire_lock_nonce`。
- `tools/check_commit_reorder_buffer.py` - 验证 retired ROB entry 上的自退休元数据。
- `tools/run_openspec_guard.py` - 将 local-main retire-lock checker 纳入仓库 guard。
- `tools/check_local_flow_scripted_enforcement.py` - 验证 lock helper、checker、治理文件和测试保持接线。
- `tools/safety_rule_script_backing_registry.json` - 记录对等 session 本地 main 退休的脚本化安全覆盖。
- `test/check_local_main_retire_lock.test.py` - 覆盖 lock acquire、deny、nonce mismatch、stale reclaim 和 release。
- `test/check_commit_reorder_buffer.test.py` - 覆盖 ROB 自退休元数据。
- `test/check_implementation_plan_rules.test.py` - 覆盖可选父方案和声明缺失父方案两类规则。
- `test/check_local_flow_scripted_enforcement.test.py` - 覆盖新增 lock 的脚本化治理接线。
- `test/run_openspec_guard_json.test.py` - 覆盖新增 checker 的 guard 注册。
- `tools/ci/ci_test_manifest.json` - 将 local-main retire-lock 聚焦测试登记到本地 Python 测试清单。
- `docs_bilingual/docs_registry.yaml` - 登记本双语 implementation plan。
- 仓库根目录完整本地提交流程文档 - 记录无固定控制 session 的对等执行模型和串行 local-main 锁。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] 创建本 active 英文主版 implementation plan 和中文对照版，确保实现有已确认的治理表面。
- [x] 在 `docs_bilingual/docs_registry.yaml` 登记本双语 implementation plan。
- [x] 实现 `tools/local_main_retire_lock.py`，包含 acquire、status、release、nonce、TTL 和 stale reclaim。
- [x] 实现 `tools/check_local_main_retire_lock.py`，使 stale lock 只警告、无 lock 时通过。
- [x] 扩展 `tools/complete_local_flow_to_remote_gate.py`，增加对等 session `--self-retire`、`--session-id`、`--rob-entry-id`、`--acquire-retire-lock` 和 `--lock-ttl-minutes` 控制。
- [x] 扩展 ROB helper/checker，支持 `retire_mode`、`retire_owner_session_id` 和 `retire_lock_nonce`。
- [x] 将 local-main retire-lock checker 接入 OpenSpec guard 和本地脚本化治理 checker。
- [x] 增加聚焦测试并登记到本地 CI manifest。
- [x] 更新治理文档，说明父方案可选，local-main 写入通过锁由对等 session 自退休。
- [x] 更新 Phase 并行治理，使每个 eligible child plan 都可并行入场，不再使用固定 2/3/4/6 Phase cap。
- [x] 扩展脚本化检查和测试，使 work-conserving admission 有 checker 支撑。
- [x] 提交前运行聚焦测试、本地 CI manifest 测试和 OpenSpec guard。
- [ ] 使用中文提交信息提交，运行提交后的 local MR review 和 local gate，合入本地 `main`，并停在远端发布门。
<!-- TASK_BACKLOG_END -->

## 验收清单

- [x] 对等 session 可以获取 local-main retire lock；另一个 session 在锁有效时会被拒绝。
- [x] 对等 session 不能释放其他 session 的锁，因为 release 必须带匹配 nonce。
- [x] stale lock reclaim 必须使用显式 operator 控制标志。
- [x] ROB retired entry 可以记录 `retire_mode=self_retire_lock`，并用 `retire_owner_session_id` 表示 session-owner 证据、用 `retire_lock_nonce` 表示 lock-token 证据。
- [x] 完整本地流程 helper 可以在本地 `main` 写入前获取锁，在 `finally` 中释放锁，并在成功 merge 后记录 ROB 自退休证据。
- [x] implementation-plan checker 允许缺省 `parent_plan`，并拒绝不安全或声明但缺失的 `parent_plan` 路径。
- [x] 文档不再暗示所有本地 `main` 集成都必须由一个固定 main session 控制。

## 已完成证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-05-29 对等 session 自退休实现提交前验证：聚焦测试已通过，本地 CI manifest 已通过，local-main retire-lock checker 已通过，commit ROB checker 已通过，implementation-plan checker 已通过，本地脚本化治理 checker 已通过，precommit update/archive checker 已通过，OpenSpec guard 使用 `--skip-validate` 已通过；local MR review 和 local gate 仍是提交后门禁。
<!-- EVIDENCE_INDEX_END -->