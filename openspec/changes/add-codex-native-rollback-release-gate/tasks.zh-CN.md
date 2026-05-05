## 1. OpenSpec Artifacts

- [x] 1.1 创建 Codex native preservation and rollback release gate 的 proposal 和 design artifacts。
- [x] 1.2 为 team-mode controls 和 startup binding specs 增加 release-gate evidence 的 delta requirements。
- [x] 1.3 为人为维护的 OpenSpec Markdown 文件增加中文对照 artifacts。

## 2. Release Gate Template And Checker

- [x] 2.1 增加 `tools/codex_native_rollback_release_gate_template.json` —— native Codex preservation 和 rollback evidence 的 JSON release-gate template。
- [x] 2.2 增加 `tools/check_codex_native_rollback_release_gate_template.py` —— 检查 release-gate template 和 repository evidence 的静态 checker。
- [x] 2.3 将新增 checker 接入 `tools/run_openspec_guard.py` —— 聚合 OpenSpec guard 脚本。

## 3. Documentation And Validation

- [x] 3.1 更新 active user-level team-mode implementation plan，写入新的 release-gate slice。
- [x] 3.2 更新 long-term production durable-team draft，写入相同 release-gate boundary。
- [x] 3.3 运行 release-gate checker、installer rollback test、OpenSpec validation 和 aggregate OpenSpec guard。
