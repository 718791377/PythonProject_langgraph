---
doc_id: codex_cli_personal_production_durable_team_minimum_startup_documents
lang: zh-CN
doc_class: product_lifecycle
status: active
canonical_path: docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_minimum_startup_documents.md
zh_cn_path: docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_minimum_startup_documents.zh-CN.md
translation_of: docs_bilingual/product_lifecycle/codex_cli_personal_production_durable_team_minimum_startup_documents.md
---
# Codex CLI 个人开发者生产级持久化团队最小启动文档

## 目的

本文定义一人公司项目内嵌 Codex 执行能力的最小平台治理启动集。它不是业务启动清单，而是用于启动 Agent、worktree、durable state、验证门、发布门、证据、回滚和复盘的执行治理基线。

## 12 个文档固定顺序

1. `thesis.md` - Explain why the embedded Codex platform-governance capability exists and what it refuses to own.
2. `architecture.md` - Define execution architecture, worktree boundaries, durable state, and authority boundaries.
3. `agent-governance.md` - Define what agents may do, draft, escalate, or never decide.
4. `agent-role-map.md` - Map agent roles to operating responsibilities and evidence expectations.
5. `agent-permissions.md` - Define tool, data, approval, and human-review permissions.
6. `delivery-plan.md` - Define how Codex work moves through planning, validation gates, release gates, and local-main evidence.
7. `observability.md` - Define runtime, repo, worktree, and agent evidence signals.
8. `risk-register.md` - Record platform, business, and mixed operating risks with scoped ownership.
9. `human-review-checklist.md` - Define human review before customer commitments, release gates, and irreversible actions.
10. `decision-log.md` - Record decisions with scope, truth owner, evidence source, decision right, and linked docs.
11. `backup-restore.md` - Define recovery for repo, runtime, durable state evidence, and rollback paths.
12. `monthly-review.md` - Drive recurring platform and business learning review.

## 过程组用法

### 输入

- 已冻结的一人公司业务边界和当前项目范围。
- 仓库状态、worktree 状态、durable state、本地 main 状态和回滚证据。
- Agent 角色目录、权限矩阵、验证门、人审规则和发布边界。

### 工具与技术

- 按上方固定顺序读取 12 个文档，再授权 Codex 执行真相。
- 本地集成前执行 local-main-first 检查。
- 客户承诺、合同承诺、发布批准、财务承诺以及混合事项必须人审。
- Codex 执行真相和业务真相分开治理，同时通过共享台账关联。

### 输出

- 可启动的内嵌 Codex 平台治理基线。
- 带 scope、truth_owner、evidence_source、decision_right 和 linked_docs 的决策、风险、人审、恢复和月度复盘记录。
- Codex 团队可以执行代码和运行时工作，但不接管客户、收入、合同、法务或现金流真相的证据。

## 裁剪说明

当项目影响客户、收入、合规、代码、Agent、runtime、durable state 或发布边界时，采用完整 12 文档集。极小内部实验可以保留顺序但降低每份文档的填写深度，不删除文档；必须记录为什么轻量化仍然安全。
