# 设计：用户级 MCP/skills/browser/CLI 治理的新版结构

## 摘要

本设计将目标方案从按 lane 展开的旧式清单转换为 Pi sidecar 与 Comet runtime 方案所采用的新型实施方案结构。此次重构仅修改文档，并保留全部既有治理语义。

## 选定结构

1. 复核结论。
2. 关系模型与命名边界。
3. 目标与非目标。
4. 运行时架构与 Codex 使用模型。
5. Repo-local source of truth。
6. 用户级产物与 receipt 契约。
7. Token/risk、端口、授权、更新与证据脱敏治理。
8. `skills2cli`、`mcp2cli`、browser automation、`chrome-devtools-mcp`、CDP Bridge、OpenCLI、CLI-Anything 与 `wecom-cli` 的能力 lane 契约。
9. Comet runtime state、management record、phase gates 与 monitoring returns。
10. Implementation slices、任务级 backlog、本地集成顺序、验收标准、证据、回滚与风险。

## 决策

- 保持 implementation-state 事实：repo-local helpers 与 guards 可以已实现，但用户级 lane 必须等 wrapper、smoke、receipt 与 rollback 证据齐全后才能标为 active。
- Pi sidecar 细节继续委托给 `pi_plugin_codex_user_level_sidecar_plan.*`。
- 明确 Comet runtime 治理，方便后续切片决定继续、回退早期阶段、延迟 archive 或新开 change。
- 本变更不处理 local-main-first 之外的远端发布。

## 风险与缓解

- 风险：结构重写可能遗漏旧有必需 marker。缓解：保留 checker marker 并运行 baseline checker。
- 风险：宽泛方案可能被误读为 runtime 已安装。缓解：重申非目标与 readiness gates。
- 风险：之前已经完成的 active OpenSpec change 仍处于 active。缓解：本 change 携带明确 archive deferral，把更广泛 archive cleanup 留给独立集成决策。

## 验收

- 双语方案对齐 Pi sidecar / Comet runtime 新版结构。
- 既有 lane 语义与 checker markers 仍保留。
- OpenSpec validation、baseline checker、document pair policy、precommit archive review、OpenSpec guard、local gate 与 local MR review 通过。
