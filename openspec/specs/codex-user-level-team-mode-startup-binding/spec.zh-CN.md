# codex-user-level-team-mode-startup-binding Specification

## 目的

定义 user-level team-mode startup binding、PowerShell wrapper、native bypass、backup rollback 和 release smoke evidence 的要求。

## Requirements

### Requirement: The installer SHALL generate a PowerShell startup-binding launcher

installer 必须生成 launcher script，用来读取持久化 user-level team-mode state，并为 PowerShell-based `codex` launches 计算 Codex CLI runtime overrides。

launcher 必须保留 native Codex executable path，而不是替换它。

#### Scenario: Startup-binding assets are generated into the target Codex home

- **WHEN** installer 为 startup binding 运行
- **THEN** 它必须在 target Codex home 下生成 launcher asset
- **AND** launcher 必须知道如何调用 native Codex command path 且不递归

### Requirement: The installer SHALL add a managed PowerShell profile block without replacing the native executable

installer 必须向选定 PowerShell profile path 加入 managed block，该 block 定义 wrapped `codex` function 和 raw `codex-native` bypass function。

它不得修改 npm-installed `codex`、`codex.cmd` 或 `codex.ps1` files。

#### Scenario: A new PowerShell session loads the startup binding

- **WHEN** PowerShell session 加载 managed profile block
- **THEN** 调用 `codex` 必须通过 generated launcher
- **AND** 调用 `codex-native` 必须直接进入 native Codex command
- **AND** native Codex installation files 必须保持不变

### Requirement: The launcher SHALL map `oh_my_codex` state to startup behavior

launcher 必须从 persisted state file 读取 `oh_my_codex`，并把它映射为 Codex CLI runtime overrides。

最低要求：

- `oh_my_codex=on` —— 保持 omx startup behavior enabled。
- `oh_my_codex=off` —— 为 wrapped launch 禁用 omx-specific startup behavior。

#### Scenario: Wrapped launch runs in native mode when omx is off

- **WHEN** wrapped `codex` launch 看到 `oh_my_codex=off`
- **THEN** 它必须为本次 launch 禁用 omx-specific MCP startup surfaces
- **AND** 它必须使用 native-mode developer-instruction preset

### Requirement: The launcher SHALL map `subagent_routing` state to multi-agent availability

launcher 必须从 persisted state file 读取 `subagent_routing`，并把它映射为 Codex CLI routing behavior。

最低要求：

- `auto` —— 保持 multi-agent available，并使用 automatic-routing instructions。
- `manual` —— 保持 multi-agent available，并使用 manual-routing instructions。
- `off` —— 为 wrapped launch 禁用 multi-agent。

#### Scenario: Wrapped launch disables multi-agent in no-routing mode

- **WHEN** wrapped `codex` launch 看到 `subagent_routing=off`
- **THEN** 它必须传入等价的 `--disable multi_agent`
- **AND** 它必须使用 no-routing developer-instruction preset

### Requirement: Startup-binding installation SHALL be covered by backup snapshots and rollback

installer 必须把 PowerShell profile path 和 startup-binding launcher assets 放入同一个 timestamped backup-and-rollback transaction；该 transaction 与其他 team-mode assets 使用同一套机制。

#### Scenario: A partial startup-binding install restores the previous profile content

- **WHEN** startup-binding installation 在写入 profile 或 launcher 后失败
- **THEN** installer 必须恢复之前的 PowerShell profile content
- **AND** 它必须把 startup-binding assets 恢复或删除到 pre-install state
- **AND** 它必须保留 backup metadata 供 diagnostics 使用

### Requirement: Startup-binding surfaces SHALL avoid duplicating project canary prompts

Startup-binding、launcher 和 repository instruction surfaces 不得在 project startup summary pair 之外重复 project-level context-retention canary prompt。

它们可以指向 project startup summary 作为 source of truth，也可以描述 cold-start recovery path。

#### Scenario: Launcher or instruction text refers to context-loss recovery

- **WHEN** startup-binding 或 repository instruction text 记录 context-loss recovery
- **THEN** 它必须让读者参考 project startup summary 中的 canary prompt
- **AND** 它不得在 launcher payloads、generated wrappers 或 `AGENTS.md` 中嵌入 literal canary prompt text

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
