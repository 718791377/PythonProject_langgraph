## 任务

- [x] 1. 新增 `tools/check_orchestration_collaboration_evidenceguard.py`。
- [x] 2. 新增提示词无关协同等价 fixture 与结构化 evidence fixture。
- [x] 3. 增加单元覆盖，并通过既有 `test/check_orchestration_trace_evidence.test.py` 纳入 `tools/ci/ci_test_manifest.json`。
- [x] 4. 将 checker 接入 `tools/run_openspec_guard.py` 与 `tools/safety_rule_script_backing_registry.json`。
- [x] 5. 更新 `AGENTS.md`、治理文档、实施方案与稳定 OpenSpec spec。
- [x] 6. 运行本地验证，并将本 archive record 纳入实施包。

## 验证证据

- `python tools/check_orchestration_collaboration_evidenceguard.py --root . --json` 已通过。
- `python test/check_orchestration_trace_evidence.test.py` 已通过。
- `git diff --check` 已通过。
