---
doc_id: durable_team_source_traceability
lang: zh-CN
canonical: docs_bilingual/product_lifecycle/durable_team_source_traceability.md
translation_of: docs_bilingual/product_lifecycle/durable_team_source_traceability.md
doc_class: product_lifecycle
status: draft
---

# 持久化团队来源追踪

## 目的

本追踪索引记录 fresh source evidence 如何影响 durable-team 文档族，同时不存储 raw extracted text。它是 evidence-chain proof surface，不是 source archive。

本文拥有：

- source run identity；
- tracked versus ignored evidence rules；
- source-family to authority mapping；
- 白皮书、研究稿、生命周期文档、实施文档和 OpenSpec specs 的 update triggers。

## 来源运行身份

| 字段 | 值 |
| --- | --- |
| Run ID | `one-person-company-pmi-refresh-stageb-20260619` |
| Generated at | `2026-06-18T18:37:58Z` |
| Output root | `.omx/state/langgraph/extraction/business_pmp_20260619/` |
| Total sources | 54 |
| Total reading units | 9,656 |
| Total extracted characters | 18,492,044 |
| Business Management | 31 sources / 6,551 units / 14,161,228 chars |
| PMP | 23 sources / 3,105 units / 4,330,816 chars |
| Format split | 31 PDFs / 9,280 pages；9 EPUBs / 362 spine items；14 Markdown full documents |
| Status | all sources `ok` |

## 证据边界

| 证据类别 | Git 状态 | 允许用途 |
| --- | --- | --- |
| 聚合计数与 manifests | 通过 summary docs 记录，可本地再生成 | 标识覆盖范围与新鲜度。 |
| 综合映射与结论 | 跟踪在 lifecycle、matrix 与 spec docs 中 | 驱动文档更新与验收检查。 |
| Raw extraction text 与 per-unit streams | ignored local cache | 不提交、不引用、不要求其作为冷启动权威。 |
| Local logs 与 temporary caches | ignored local cache | 仅用于本地 refresh verification。 |

Tracked docs 可以引用聚合事实和 paraphrased synthesis，但不得依赖 ignored raw cache 作为 repository authority。

## 追踪链

```text
local source roots
  -> fresh extraction run one-person-company-pmi-refresh-stageb-20260619
  -> manifest, report, and synthesis summary
  -> fresh_source_reading_evidence.zh-CN.md
  -> source traceability and delivery matrix
  -> white paper / research note / lifecycle maps / implementation docs / OpenSpec specs
```

## 来源到权威映射

| 来源家族或综合桶 | 权威目的地 | 为什么落在这里 | UR 支持 |
| --- | --- | --- | --- |
| Business Management strategy、product、metrics、operations synthesis | 白皮书、MRD、北极星、产品生命周期、inventory maps | 这些来源解释平台为何存在、服务谁、如何保持小而可治理、如何度量。 | UR1, UR2 |
| Business Management 架构笔记 1 | `codex_platform_inventory_map.zh-CN.md` 与 durable-team plan | 它是 Codex platform target 的数量权威：12 层、4 部门、24 责任域、18 模块、48 文档、12 agents、12 books。 | UR1, UR3 |
| Business Management 架构笔记 2 | `one_person_company_inventory_map.zh-CN.md` 与 downstream handoff rules | 它是一人公司 target 的数量权威：12 层、5 部门、30 责任域、20 模块、60 文档、15 agents、15 books、12 startup docs。 | UR1, UR2 |
| PMP value-delivery 与 tailoring synthesis | PMI map、lifecycle tailoring rules、process-group contract | 它提供 governance overlay、tailoring choices 与 I/T/O execution grammar。 | UR4 |
| 仓库治理中的 runtime capability synthesis | 研究稿、10-to-12 bridge、implementation plan | 它保留 10 层 runtime/governance core，并把 findings 映射到 12 层生命周期。 | UR3 |
| Refresh-only evidence delta | Delivery matrix、traceability index、process-group contract | 它证明哪些文件刷新、当前 evidence boundary 是什么，而不继续膨胀权威文档。 | UR1, UR2, UR3, UR4 |

## 更新触发矩阵

| 触发 | 第一更新目标 | 后续目标 |
| --- | --- | --- |
| Platform story、boundary、target user 或 paradigm shift 改变 | 白皮书 | MRD、北极星、delivery matrix、stable specs |
| Runtime capability criteria、evidence basis 或 decomposition 改变 | 研究稿 | 10-to-12 bridge、implementation plan、stable specs |
| Count authority 改变 | 受影响目标的 inventory map | 白皮书、MRD、lifecycle docs、delivery matrix |
| PMI、tailoring 或 process-group authority 改变 | PMI map 与 process-group contract | Lifecycle tailoring rules、playbook、OpenSpec lifecycle spec |
| Refresh-only source evidence 改变 | Fresh evidence index、source traceability、delivery matrix | 只有综合结论改变时才更新 authority docs |
| Release-slice gate 或 implementation workflow 改变 | Playbook 与 OpenSpec specs | Implementation plan、process-group contract、validation reports |

## 白皮书与研究稿关系

白皮书与研究稿不物理合并。

- 白皮书：战略叙事、目的、价值、采纳，以及 12 层产品/商业生命周期框架。
- 研究稿：证据密集的 runtime/governance canon、production capability criteria 与 10 层 runtime core。
- 本追踪索引记录同一次 source refresh 如何同时影响二者，但不折叠其职责。

## 10 层到 12 层交接

runtime findings 的 canonical 位置仍是 10 层研究稿。生命周期落地和 planning translation 通过 `ten_to_twelve_layer_bridge.zh-CN.md`、lifecycle maps 与 OpenSpec specs 完成。数量权威仍在 inventory maps。

当文档同时引用两个模型时，必须说明哪个模型对该 claim 具有权威，以及结果落到哪个 12-layer lifecycle zone。

## 引用纪律

- 使用 aggregate counts、source-family names 与 synthesized claims。
- 当 claim 来自当前 refresh 而非稳定仓库权威时，标注为 synthesis-derived。
- 不复现长篇来源段落。
- 不引用或要求 ignored raw extraction streams。
- 如果未来 refresh 改变计数或综合结论，应先重新抽取并更新本文件，再更新下游结论。

## 输出到过程组契约

当工作变成 execution-facing 时，traceability outputs 成为 process-group inputs：

### 输入

- current source run identity；
- source-to-authority mapping；
- update trigger classification；
- affected authority documents。

### 工具与技术

- evidence-boundary review；
- source-family landing analysis；
- authority split review；
- tracked-doc-only validation。

### 输出

- approved update target list；
- evidence caveats；
- downstream delivery matrix rows；
- 必要时的 OpenSpec 或 playbook updates。

## 非目标

- 本文件不存储 source text。
- 本文件不替代 source books 或 repository authority documents。
- 本文件不证明 runtime implementation。
- 本文件不批准 remote publication。

## Product lifecycle Markdown reread

本轮还通过 `one-person-company-pmi-refresh-stageb-product-lifecycle-20260619` 全文读取 `docs_bilingual/product_lifecycle/` 下 26 个 Markdown 文档，共 310,349 个字符，全部 `ok`。该证据用于证明在更新白皮书、一人公司北极星、生命周期地图和裁剪规则前，当前生命周期文档本身已被重新读取。
