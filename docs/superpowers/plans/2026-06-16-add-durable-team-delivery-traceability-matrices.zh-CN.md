---
change: add-durable-team-delivery-traceability-matrices-20260616
design-doc: docs/superpowers/specs/2026-06-16-durable-team-delivery-traceability-design.md
base-ref: 46b8e38441b09a4ae1892d28e833b7a3c3d5466d
translation_of: docs/superpowers/plans/2026-06-16-add-durable-team-delivery-traceability-matrices.md
---

# 持久化团队交付追踪证明面实施计划

> **给 agentic workers：** 必须使用 superpowers:subagent-driven-development 或 superpowers:executing-plans 按任务执行。步骤使用 checkbox 语法追踪。

**目标：** 为 durable-team 文档刷新新增双语证明面与受治理引用。

**架构：** 本变更为 docs-only。新证明面把 UR1 到 UR4 映射到既有权威文档和 OpenSpec specs，同时保留 raw-cache 与 runtime 边界。

**技术栈：** Markdown、OpenSpec、仓库文档检查器、local-main-first validation。

---

## Task 1: 新增证明面文档

**Files:**
- Create: `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_delivery_matrix.md`
- Create: `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_delivery_matrix.zh-CN.md`
- Create: `docs_bilingual/product_lifecycle/durable_team_source_traceability.md`
- Create: `docs_bilingual/product_lifecycle/durable_team_source_traceability.zh-CN.md`
- Create: `docs_bilingual/product_lifecycle/durable_team_process_group_contract.md`
- Create: `docs_bilingual/product_lifecycle/durable_team_process_group_contract.zh-CN.md`

- [x] Step 1: 新增包含 UR1-UR4 与 document target rows 的 delivery matrix。
- [x] Step 2: 新增包含 source run identity 与 evidence boundary 的 source traceability index。
- [x] Step 3: 新增包含 Inputs / Tools and Techniques / Outputs 的 process-group contract。

## Task 2: 登记并连接证明面

**Files:**
- Modify: `docs_bilingual/docs_registry.yaml`
- Modify: `openspec/specs/codex-cli-personal-production-durable-team-plan/spec.md`
- Modify: `openspec/specs/codex-cli-personal-production-durable-team-plan/spec.zh-CN.md`
- Modify: `openspec/specs/codex-product-lifecycle-document-governance/spec.md`
- Modify: `openspec/specs/codex-product-lifecycle-document-governance/spec.zh-CN.md`

- [x] Step 1: 登记新的双语 docs。
- [x] Step 2: 为 delivery、traceability 与 process-group proof surfaces 增加稳定规格要求。
- [x] Step 3: 在 active OpenSpec change 下增加匹配的 delta specs。

## Task 3: 刷新 active corpus evidence references

**Files:** `docs_bilingual/` 下的 active durable-team 与 product-lifecycle docs。

- [x] Step 1: 将上一轮 20260614 evidence boundary 替换为 `fresh-source-lifecycle-whitepaper-pmi-refresh-20260616` 与 `2026-06-15T17:33:52Z`。
- [x] Step 2: 在 core corpus 需要当前 checkpoint 的位置增加简短 proof-surface handoff note。
- [x] Step 3: 保持已归档 OpenSpec history 不变。

## Task 4: 验证与归档

- [ ] Step 1: 对本 change 运行 OpenSpec strict validation。
- [ ] Step 2: 运行双语文档对、implementation-plan、name、mojibake、precommit、local gate 与 local MR review 检查。
- [ ] Step 3: 新增 verification reports 并归档 OpenSpec change。
