## ADDED Requirements / 新增需求

### Requirement: Legacy Resumed Sessions SHALL Remain Compatibility-Scoped / 旧会话必须保持兼容范围

仓库工作流必须将 legacy resumed Codex sessions（旧恢复会话）视为 compatibility-scoped sessions（兼容范围会话）。

旧会话是较早的 Codex `/resume` thread，可能保留当前治理状态之前的 stale context（陈旧上下文）、stale MCP assumptions（陈旧 MCP 假设）或 stale launcher behavior（陈旧启动器行为）。

旧会话可以临时继续使用，但不得覆盖当前仓库文件、当前本地 Git 状态、active OpenSpec state 或 session-ownership claims。

#### Scenario: Old resumed session disagrees with current repository state / 旧会话与当前仓库状态不一致

- **GIVEN** 旧会话包含 stale instructions 或 stale MCP assumptions
- **WHEN** 该会话用于跟进讨论
- **THEN** 必须以当前仓库文件和当前本地 Git 状态为权威
- **AND** 旧会话不得在未重新验证 startup summaries、OpenSpec state、Git state 和 session-ownership claims 的情况下认领新的治理实施

#### Scenario: Old resumed session needs a scoped workaround / 旧会话需要限定范围 workaround

- **GIVEN** 旧会话由于 stale runtime 或 MCP state 无法启动
- **WHEN** 操作者希望继续该旧 thread
- **THEN** 可以使用 per-invocation compatibility override（单次启动兼容覆盖）
- **AND** 除非未来获批的治理变更另有规定，该覆盖不得变成永久全局配置变更
