# 任务

## 1. RED 测试
- [x] 增加 focused tests，覆盖 checker findings、受保护片段、runtime analyze/rewrite/apply guard 和 R4 smoke receipts。
- [x] 运行 focused test，确认生产代码存在前测试失败。

## 2. Runtime 与 checkers
- [x] 实现 `tools/check_stop_slop_caveman_response_density.py`。
- [x] 实现 `tools/stop_slop_caveman_runtime.py`。
- [x] 实现 `tools/check_stop_slop_caveman_smoke_receipts.py`。

## 3. 登记与文档
- [x] 在 `tools/ci/ci_test_manifest.json` 登记 focused tests。
- [x] 在 `tools/run_openspec_guard.py` 登记 checker wiring。
- [x] 在 `tools/safety_rule_script_backing_registry.json` 登记 safety-rule backing。
- [x] 更新双语实施方案的状态、任务和证据。

## 4. 验证与本地集成
- [x] 运行 focused tests 和 smoke checker/runner 证据。
- [x] 运行 OpenSpec validation、OpenSpec guard 和 precommit update/archive review。
- [x] 归档完成的 OpenSpec change，并重新验证。
- [ ] 使用中文 subject 提交，运行 local gate 和 local MR review。
- [ ] 合入本地 `main`，清理已集成 worktree/branch，并停在远端发布门口。
