---
doc_id: self_retiring_peer_session_local_main_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/self_retiring_peer_session_local_main_plan.md
stage: Stage A recovery governance package
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
状态：active
阶段：Stage A 恢复治理文档包
责任会话：`recover-self-retire-runtime-20260529`
当前门禁：合入本文档更新后停止，等待用户确认再恢复 runtime。
Runtime 状态：`867f882` 是来源提交；当前本地 `main`=`b4af80f` 缺少 retire lock helper/checker。
最后更新：2026-05-29
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
- [x] 创建 active 英文主版和中文对照版。
- [x] 在 `docs_bilingual/docs_registry.yaml` 登记本双语 implementation plan。
- [x] Stage A 恢复：记录 `867f882` 为来源提交，但当前本地 `main` 缺少 runtime 文件。
- [ ] Stage B 恢复：重新应用 `tools/local_main_retire_lock.py`。
- [ ] Stage B 恢复：重新应用 `tools/check_local_main_retire_lock.py`。
- [ ] Stage B 恢复：扩展 `tools/complete_local_flow_to_remote_gate.py` 的 self-retire 参数。
- [ ] Stage B 恢复：扩展 ROB helper/checker 的 retire metadata。
- [ ] Stage B 恢复：接入 guard/checker，增加聚焦测试和 CI manifest 登记。
- [ ] Stage B 恢复：运行门禁，合入本地 `main`，并停在远程发布门。
<!-- TASK_BACKLOG_END -->

## 验收清单

- [ ] Stage B 恢复后，peer session 可以获取 local-main retire lock，并拒绝并发竞争者。
- [ ] Stage B 恢复后，release 必须匹配 nonce，不能释放其他 session 的锁。
- [ ] Stage B 恢复后，stale reclaim 必须显式授权。
- [ ] Stage B 恢复后，ROB retired entry 能记录 `retire_mode=self_retire_lock`（表示持锁会话合入自己的分支）和 nonce 证据（一次性锁令牌）。
- [ ] 文档不再暗示所有本地 `main` 集成都必须由固定 main session 控制。

## 已完成证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-05-29 Stage A 恢复文档包：当前本地 `main`=`b4af80f` 缺少 self-retire runtime 文件；`867f882` 是恢复来源；Stage B runtime 恢复必须等待用户确认。
- 2026-05-29 来源分支验证：`decentralize-session-self-retire-20260529` 中的聚焦测试曾通过，但不能视为当前 main 已具备 runtime 的证据。
<!-- EVIDENCE_INDEX_END -->
