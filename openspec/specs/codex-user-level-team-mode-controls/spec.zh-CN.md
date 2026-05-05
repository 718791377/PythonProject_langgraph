# codex-user-level-team-mode-controls Specification

## 目的

定义用户级 team-mode 控制资产、控制状态与兼容派生视图的生成要求。

## 要求

### Requirement: 生成出来的 controls 必须区分“已启用 capability layers”和“effective execution lane”

生成出来的用户级 controls 必须区分：

- 哪些 orchestration capability layers 已启用
- 某条任务流当前实际使用哪条 effective execution lane

不能把这两个概念继续压缩成同一个字段。

#### Scenario: 操作员检查用户级 control 输出

- **WHEN** 操作员检查生成出来的用户级 control surfaces
- **THEN** 这些 surface 必须区分已启用 capability layers 与当前 effective lane
- **AND** 不得为了每一条任务流的 lane 差异都要求 operator 先切一次全局 backend

### Requirement: Release gates SHALL prove native Codex preservation and rollback evidence before production marking

在 user-level team-mode installer、launcher 或 publication slice 被标记为 production-ready 之前，仓库必须提供 release gate，要求 native Codex preservation、backup snapshots、rollback behavior 和 config rewrite sentinel status 的 evidence。

release gate 默认必须保持 read-only，除非另一个 reviewed change 和 explicit operator consent 允许，否则不得安装到真实 user Codex home。

release gate 必须保护这些 native Codex entrypoint names：

- `codex` —— native Codex base command name。
- `codex.cmd` —— Windows npm shim for native Codex。
- `codex.ps1` —— PowerShell shim name that must not be replaced by this repository。

#### Scenario: A release candidate lacks rollback evidence

- **WHEN** release candidate 改动 user-level team-mode installer 或 launcher behavior
- **AND** 没有 release-gate evidence 记录 backup snapshot 和 rollback validation
- **THEN** release 不得被标记为 production-ready
- **AND** operator 必须继续使用 stable native Codex 或 raw bypass entrypoints

#### Scenario: A release gate is checked in CI

- **WHEN** aggregate OpenSpec guard 在 CI 或本地验证中运行
- **THEN** 它必须验证 release-gate template 和静态 repository evidence
- **AND** 它不得修改 `C:\Users\lenovo\.codex\config.toml` 或任何真实 user-level Codex asset

### Requirement: Release gates SHALL keep manual rollback evidence explicit

release gate 必须包含 manual rollback path field，用来指向 backup snapshot evidence 或 documented restore steps。

它必须区分 automatic rollback-on-error evidence 和 manual version rollback evidence。

#### Scenario: Backup snapshots exist but manual rollback is undocumented

- **WHEN** installer 已经存在 backup snapshot behavior
- **AND** release gate 缺少 manual rollback path 或 restore evidence
- **THEN** release 必须继续阻塞 production marking
- **AND** 该 gap 必须记录为 release hardening task，不得静默接受
