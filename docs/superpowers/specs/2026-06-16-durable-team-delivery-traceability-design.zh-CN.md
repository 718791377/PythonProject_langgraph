---
change: add-durable-team-delivery-traceability-matrices-20260616
status: draft
translation_of: docs/superpowers/specs/2026-06-16-durable-team-delivery-traceability-design.md
---

# 设计：持久化团队交付与追踪证明面

## 目标

为 durable-team 语料新增三类紧凑证明面：交付矩阵、来源追踪、过程组契约。

## 方案

这些证明面放在既有权威文档旁边，不替代白皮书、研究稿、inventory maps、PMI map、实施方案、playbook 或 OpenSpec specs。它们通过把 UR1 到 UR4 映射到文件、证据边界、桥接规则和过程组 gate，使本轮刷新可审计。

## 决策

- 使用表格优先的文档，让冷启动维护者可以快速扫描。
- 以 `fresh-source-lifecycle-whitepaper-pmi-refresh-20260616` 作为当前来源证据边界。
- raw extraction streams 不进入 Git。
- 白皮书与研究稿继续物理分离。
- 只在 execution-facing gates、layers 和 release slices 中强制 Inputs / Tools and Techniques / Outputs。

## 文件所有权

- 交付矩阵：`docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_delivery_matrix.*`
- 来源追踪：`docs_bilingual/product_lifecycle/durable_team_source_traceability.*`
- 过程组契约：`docs_bilingual/product_lifecycle/durable_team_process_group_contract.*`
- 治理链接：docs registry，以及 durable-team 与 lifecycle OpenSpec specs。

## 验收

- 新文件均为双语文档对。
- 英文主文件只含 ASCII。
- 证明面只引用聚合证据。
- 归档前 OpenSpec validation 与文档检查通过。
