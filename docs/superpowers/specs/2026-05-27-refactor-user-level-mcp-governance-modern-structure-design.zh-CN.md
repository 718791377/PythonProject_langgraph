---
change: refactor-user-level-mcp-governance-modern-structure
status: archived
created_at: 2026-05-27
translation_of: docs/superpowers/specs/2026-05-27-refactor-user-level-mcp-governance-modern-structure-design.md
archived-with: openspec/changes/archive/2026-06-03-refactor-user-level-mcp-governance-modern-structure
---

# 用户级 MCP/Skills/Browser/CLI 治理的新版结构设计

## 背景

目标方案需要对齐 Pi sidecar 方案与 Comet runtime 敏捷关注领域方案所代表的新方案家族。本次重构是结构性文档改造，必须保留仓库 checker 要求的全部治理 marker。

## 选定方式

采用完整 Comet 文档重构。围绕关系边界、运行时架构、repo-local source of truth、receipts、state contracts、management record、phase gates、slices、task backlog、本地集成、acceptance、evidence、rollback 与 risks 重建双语方案对。

## 拒绝方案

- 仅更新元数据：不足以改变旧式正文结构。
- 直接 runtime implementation：缺少 lane-specific OpenSpec changes 与用户级 receipts，不安全。
- 远端发布：不属于本地文档集成范围。

## 验证设计

运行 document pair checker、implementation-plan checker、MCP/skills/browser/CLI baseline checker、precommit update/archive review、OpenSpec guard、local gate 与 local MR review。
