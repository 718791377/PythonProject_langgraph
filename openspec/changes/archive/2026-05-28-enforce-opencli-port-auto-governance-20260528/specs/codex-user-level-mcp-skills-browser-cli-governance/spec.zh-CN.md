## 新增要求

### 要求：OpenCLI 治理门禁 SHALL 要求自动端口与 codex-port 租约证据

仓库本地 OpenCLI 治理门禁 SHALL fail closed，除非 OpenCLI pre-dispatch 检查使用分配器驱动的 `--port auto`，并提供 Codex browser/OpenCLI 范围内已清洗的 `codex-port` 租约证据。

即使 browser owner 证据与授权 receipt 在其他方面有效，该 guard 也 SHALL 把硬编码 OpenCLI 端口视为不安全。

#### 场景：OpenCLI 操作缺少端口租约证据

- **WHEN** `python tools/opencli_governance.py check --action session.inspect --target tab:opencli-1 --session session-a --json` 在没有端口租约 receipt 的情况下运行
- **THEN** 该命令 SHALL fail closed
- **AND** blockers SHALL 包含 `opencli_port_lease_receipt_required`
- **AND** 输出 SHALL 报告 `dispatch_allowed=false`

#### 场景：OpenCLI 操作使用硬编码端口

- **WHEN** guard 检查带有 `--port 39300` 的操作
- **THEN** 该命令 SHALL fail closed
- **AND** blockers SHALL 包含 `opencli_port_must_be_auto`
- **AND** 输出 SHALL 报告不允许使用硬编码 OpenCLI 端口

#### 场景：OpenCLI 端口租约位于 Codex OpenCLI 范围之外

- **WHEN** guard 收到的 `codex-port` 租约 receipt 中端口不在 `39300-39499` 范围内
- **THEN** 该命令 SHALL fail closed
- **AND** blockers SHALL 包含 `opencli_port_lease_range_mismatch`
