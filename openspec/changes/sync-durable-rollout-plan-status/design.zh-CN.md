## 设计

这是一个状态同步 change，不是 runtime change。仓库已经包含 helper mirror source-of-truth 的实施证据：

- `openspec/changes/archive/2026-04-28-formalize-helper-mirror-source-truth/` 记录已归档的 MR 5 change。
- `openspec/specs/codex-user-level-helper-mirror-source-truth/spec.md` 记录稳定的 helper mirror contract。
- `tools/install-codex-user-level-team-mode.ps1` 会从生成的 status surfaces 输出 `helper_mirror_source_of_truth`。
- `test/install-codex-user-level-team-mode.test.ps1` 验证 routing policy 与 durable-state status output 中的 helper mirror provenance。

本补丁只更新带状态含义的文档和 status-sync spec。它有意不触碰生成到用户级的文件，也不触碰 repo-local durable state。
