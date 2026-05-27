# Receipt redaction guard 实施计划

- [x] 新增 `tools/user_level_receipt_governance.py`，提供 `auth-check`、`update-check`、`redact-check`、`template`。
- [x] 新增单元测试，覆盖必填字段、未来 expiry、smoke/rollback evidence、路径 hash、敏感 payload 检测。
- [x] 注册到 `tools/ci/ci_test_manifest.json`。
- [x] 更新双语实施方案与稳定 OpenSpec spec。
- [x] 通过 focused tests、baseline checker、OpenSpec guard、local gate、local MR review 验证。

