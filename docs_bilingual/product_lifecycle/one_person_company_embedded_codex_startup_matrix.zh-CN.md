---
doc_id: one_person_company_embedded_codex_startup_matrix
lang: zh-CN
doc_class: product_lifecycle
status: active
canonical_path: docs_bilingual/product_lifecycle/one_person_company_embedded_codex_startup_matrix.md
zh_cn_path: docs_bilingual/product_lifecycle/one_person_company_embedded_codex_startup_matrix.zh-CN.md
translation_of: docs_bilingual/product_lifecycle/one_person_company_embedded_codex_startup_matrix.md
---
# 一人公司内嵌 Codex 启动矩阵

## 目的

本矩阵把 Codex CLI 个人开发者生产级持久化团队定位为一人公司运营系统内的内嵌平台治理能力。一人公司拥有业务真相，Codex 拥有执行真相，共享台账只连接证据，不合并权威。

每条共享或混合记录必须包含：

- scope: business | codex | mixed
- truth_owner: founder | codex-operator | human-review
- evidence_source: customer | revenue | repo | runtime | agent | legal
- decision_right: human | delegated-draft-only
- linked_docs

只要客户、收入或合规事项同时影响代码、Agent 或 runtime，就必须执行 two-gate：同时通过 business gate 和 Codex execution gate。

## 启动矩阵

| 一人公司启动文档 | 内嵌 Codex 启动文档 | 共享台账 | scope | truth_owner | evidence_source | decision_right | two-gate 触发器 | 升级说明 | linked_docs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `company-thesis.md` | `thesis.md` | `decision-log.md` | business 或 codex | founder 或 codex-operator | customer 或 repo | human | 业务定位变化同时影响执行架构。 | 影响发布承诺时进入 human-review。 | linked_docs |
| `offer.md` | `delivery-plan.md` | `decision-log.md` | mixed | human-review | customer, revenue, repo | human | offer、价格或支持承诺需要代码、Agent 或发布变更。 | 业务门批准承诺，Codex 执行门批准交付路径。 | linked_docs |
| `roadmap.md` | `delivery-plan.md` | `monthly-review.md` | mixed | human-review | customer, revenue, repo, runtime | human | 路线图承诺依赖仓库或 runtime 交付。 | 客户承诺和 local-main evidence 分开记录。 | linked_docs |
| `risk-register.md` | `risk-register.md` | `risk-register.md` | business | founder | customer, legal, revenue | human | 业务风险映射到平台风险。 | 共享台账中分 business、codex、mixed 子行。 | linked_docs |
| `agent-governance.md` | `agent-governance.md` | `agent-permissions.md` | codex | codex-operator | agent, repo, runtime | delegated-draft-only | Agent 权限可能影响客户可见行为。 | 最终承诺升级到 human-review。 | linked_docs |
| `support-playbook.md` | `incident-response.md` | `human-review-checklist.md` | mixed | human-review | customer, runtime, repo | human | 客户支持问题需要代码、runtime 或 Agent 缓解。 | 业务门拥有客户响应，Codex 执行门拥有修复证据。 | linked_docs |
| `finance-model.md` | `observability.md` | `tracking-plan.md` | mixed | human-review | revenue, runtime, repo | human | 成本、收入或容量模型依赖 runtime 证据。 | 平台指标不得重定义收入真相。 | linked_docs |
| `backup-restore.md` | `backup-restore.md` | `backup-restore.md` | mixed | human-review | legal, repo, runtime | human | 恢复同时涉及业务记录和 repo-local durable state。 | 业务数据和 Codex durable state 分节恢复。 | linked_docs |
| `monthly-review.md` | `monthly-review.md` | `monthly-review.md` | mixed | human-review | customer, revenue, repo, runtime, agent | human | 月度复盘合并业务学习与执行证据。 | 结论必须标记为 business、codex 或 mixed。 | linked_docs |

## 过程组用法

### 输入

- 一人公司启动文档和 Codex 12 文档启动顺序。
- 带 scope、truth_owner、evidence_source、decision_right、linked_docs 的共享台账。
- 当前项目裁剪模式和 local-main evidence。

### 工具与技术

- 写入事实前先分类为 business、codex 或 mixed。
- 业务真相写入 founder 拥有的业务文件。
- 执行真相写入 Codex 平台治理文件。
- 混合事项执行 two-gate：business gate 加 Codex execution gate。

### 输出

- Codex 作为内嵌能力而不是平级业务权威的启动地图。
- 可按 scope 和 truth_owner 审计的共享台账。
- human-review 和 delegated-draft-only Agent 工作的清晰升级说明。
