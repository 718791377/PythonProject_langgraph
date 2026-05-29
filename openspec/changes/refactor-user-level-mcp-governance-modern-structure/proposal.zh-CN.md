# 提案：将用户级 MCP/skills/browser/CLI 治理方案重构为新版结构

## 为什么

目标实施方案已经具备完整 Comet 元数据，但正文仍偏旧式长清单。用户要求按 Pi sidecar 方案与 Comet runtime 敏捷关注领域方案的新结构重构，因此文档需要以一致顺序呈现关系边界、运行时架构、repo-local source of truth、receipts、状态契约、管理记录、阶段门禁、实施切片、任务 backlog、本地集成顺序、验收标准、证据与风险。

## 做什么

- 将中文方案重组为 `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` 与 `comet_runtime_agile_focus_area_plan.zh-CN.md` 使用的新版实施方案结构。
- 同步英文 companion，保持相同结构。
- 保留 `skills2cli`、`mcp2cli`、browser automation、`chrome-devtools-mcp`、CDP Bridge、OpenCLI、CLI-Anything、`wecom-cli`、Token/risk priority、port registry、authorization receipts、update receipts 与 readiness gates 的既有治理内容。
- 补充明确的 Comet runtime state contract、management record template、phase gate matrix、monitoring return semantics、implementation slices、task backlog 与 evidence checklist。

## 非目标

- 不实现或安装用户级 wrappers。
- 不修改 `C:\Users\lenovo\.codex` runtime state。
- 不改变 live MCP、browser、OpenCLI、CLI-Anything 或 WXWork 行为。
- 不推送 GitLab 或 GitHub。

## 影响

- 仅重构双语方案文档。
- 新增 OpenSpec 与 Superpowers 证据，以证明完整 Comet workflow。
- 无 runtime side effects。

## 回滚

通过 revert 本地 feature commit 或在本地合入前 reset feature branch 到 `{base}` 回滚。用户级 runtime state 未被修改。
