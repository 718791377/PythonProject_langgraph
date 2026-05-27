# Design：receipt redaction guard

## 方案

使用一个确定性的 Python helper 提供三类 fail-closed 检查：

- `auth-check` 校验单任务 authorization receipts。
- `update-check` 校验 update receipts、smoke evidence、owner lane 与 rollback pointer。
- `redact-check` 检测 raw sensitive payloads。

该 helper 只返回脱敏 JSON，不执行 live operation。

