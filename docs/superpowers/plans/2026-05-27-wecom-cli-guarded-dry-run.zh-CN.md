---
change: implement-wecom-cli-guarded-dry-run
design-doc: docs/superpowers/specs/2026-05-27-wecom-cli-guarded-dry-run-design.zh-CN.md
status: archived-with-local-implementation
---

# 计划：wecom-cli 受治理 dry-run

- [x] 新增 `tools/wecom_cli_governance.py`。
- [x] 新增 `test/wecom_cli_governance.test.py`。
- [x] 在 `tools/ci/ci_test_manifest.json` 登记测试。
- [x] 扩展 baseline checker，要求 helper 和测试登记存在。
- [x] 更新双语实施方案与 OpenSpec stable spec。
- [x] 用 targeted tests、OpenSpec guard、local gate 和 local MR review 验证。
