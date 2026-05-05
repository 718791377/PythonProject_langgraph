## Context

仓库现在已经有三层保护：

- plan-level rules：把 native Codex 保持为 permanent base layer。
- OpenSpec requirements：禁止替换 native Codex entrypoint names。
- installer rollback behavior：通过 PowerShell install test 验证。

缺口是：还没有一个 release gate，把这些保护合并成一个发布前 checklist 和可机器检查的 template。

## Goals / Non-Goals

**Goals:**

- 在 user-level team-mode launcher 或 installer changes 被标记为 production-ready 之前，要求显式 release evidence。
- gate 默认 read-only。
- 要求 native Codex、raw bypass 和 wrapped launcher entrypoints 的本地 smoke evidence。
- 要求 backup snapshots 和 rollback-on-error behavior 的 repository evidence。
- production release 前要求 config rewrite sentinel check。
- 将静态 checker 接入 aggregate OpenSpec guard。

**Non-Goals:**

- 默认不在 CI 中运行 live Codex 或 oh-my-codex。
- 不写入真实 user Codex home。
- 不修改 `C:\Users\lenovo\.codex\config.toml` —— Codex 用户配置文件。
- 不改变 MCP Router、omx、LangGraph 或 native subagent runtime behavior。

## Decisions

### Decision 1: 用 template 加静态 checker 实现 CI-safe enforcement

release gate 表示为 `tools/codex_native_rollback_release_gate_template.json` —— 这是列出 required fields、evidence、protected native entrypoints 和 non-mutation guards 的 JSON template。

checker 只验证 template 和源码证据，不启动 durable runtime，也不写 user-level assets。

原因：

- CI 和 MR pipelines 应该 deterministic 且 non-mutating。
- 本地 release smoke checks 仍可作为文档化证据被要求，但不让 CI 依赖已登录的 Codex session。

### Decision 2: 本地启动 smoke checks 必须明确，但不作为 CI 默认动作

gate 要求以下 evidence：

- `codex --version` —— 证明 native Codex 仍能启动的本地 smoke command。
- `codex-raw --version` —— 证明 stable raw bypass 仍能启动的本地 smoke command。
- `codex-ohmy` help 或 version check —— 证明 wrapped launcher 不会立即崩溃的本地 smoke command。

这些 checks 是 release evidence，但静态 checker 不在 CI 里运行它们。

原因：

- 本地 Codex authentication、plugins 和 Windows shell state 属于 operator environment facts。
- CI 不应该为了验证 repository policy 而需要 live Codex credentials。

### Decision 3: 缺失 rollback evidence 必须作为 release blocker

release gate 要求 evidence，证明 installer 会创建 backup snapshots，并在模拟 partial failure 后恢复 pre-install state。

repository evidence 是现有 `test/install-codex-user-level-team-mode.test.ps1` 测试，以及 source checks 对 backup 和 rollback functions 的检查。

原因：

- 只写 backup documentation 弱于已测试的 rollback behavior。
- 用户要求的是 version rollback，而不只是 failure explanation。

### Decision 4: native Codex names 同时在 spec 和 gate 层受保护

release gate 重复列出 protected native names：

- `codex` —— native Codex base command name。
- `codex.cmd` —— Windows npm shim for native Codex。
- `codex.ps1` —— PowerShell shim name that must not be replaced by this repository。

原因：

- spec 已禁止替换它们。
- release gate 让同一规则在 publication 前对 operator 可见。

## Risks / Trade-offs

- [Risk] 静态 template checking 可能被误认为完整 release drill。
  Mitigation: 保持 local smoke checks 和 manual rollback evidence 为 required release fields。

- [Risk] `codex-ohmy` behavior 会受机器 profile 影响。
  Mitigation: 要求 local smoke evidence，并保持 `codex-raw` 作为 stable bypass。

- [Risk] 随着 launchers 演进，gate 可能过期。
  Mitigation: 保持 required evidence ids 稳定，并通过 reviewed OpenSpec changes 更新 commands。

## Migration Plan

1. 增加 release-gate template 和 checker。
2. 将 checker 接入 `tools/run_openspec_guard.py` —— 聚合 OpenSpec guard。
3. 更新方案文件，写入新的 release slice。
4. 验证现有 installer rollback test 仍然通过。
5. 验证 OpenSpec artifacts 和 guard output。

## Open Questions

- 后续 slice 是否需要增加一个 manual rollback helper，用来从 `C:\Users\lenovo\.codex\backups\codex-user-level-team-mode\` —— managed team-mode assets 的用户级备份目录中恢复指定 snapshot。
