## ADDED Requirements

### Requirement: Startup-binding release gates SHALL include native, raw, and wrapped launcher smoke evidence

在 startup-binding changes 被标记为 production-ready 之前，release gate 必须要求 native Codex entrypoint、stable raw bypass entrypoint 和 stable wrapped entrypoint 的显式本地 smoke evidence。

required release evidence 至少必须包括：

- `codex --version` —— native Codex smoke command。
- `codex-raw --version` —— stable raw bypass smoke command。
- short `codex-ohmy` help or version check —— stable wrapped launcher smoke command。

静态 repository checker 可以只验证这些 evidence fields 存在，而不在 CI 中运行已认证 Codex sessions。

#### Scenario: Wrapped launcher changes but raw bypass is not proven

- **WHEN** startup-binding release candidate 改动 `codex-ohmy` wrapper behavior
- **AND** release evidence 不包含 `codex-raw --version`
- **THEN** release 不得被标记为 production-ready
- **AND** operator 必须保留 raw bypass 作为 recovery path

#### Scenario: CI validates the release-gate template

- **WHEN** CI 运行 release-gate template checker
- **THEN** 它必须验证 native、raw bypass 和 wrapped launcher smoke evidence fields 存在
- **AND** 它不得启动 long-running Codex session
