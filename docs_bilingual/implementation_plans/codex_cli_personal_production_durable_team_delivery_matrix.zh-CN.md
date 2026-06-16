---
doc_id: codex_cli_personal_production_durable_team_delivery_matrix
lang: zh-CN
canonical: docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_delivery_matrix.md
translation_of: docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_delivery_matrix.md
doc_class: delivery_matrix
status: draft
---

# Codex CLI 个人生产级持久化团队交付矩阵

## 目的

本矩阵记录当前 durable-team 刷新如何落入已提交文档。它是交付证明面，不是运行时证明面。它不替代白皮书、治理研究稿、inventory maps、PMI map、实施方案、playbook 或 OpenSpec specs。

本文拥有：

- 将用户要求 UR1 到 UR4 映射到刷新文件；
- 展示哪些文档承载交付、追踪、桥接和过程组义务；
- 明确非目标，防止 draft 文档被误认为 running durable-team evidence。

本文不拥有 raw source text、runtime capability criteria、inventory counts 或 release approval。

## 刷新检查点

- 运行 ID：`fresh-source-lifecycle-whitepaper-pmi-refresh-20260616`
- 生成时间：`2026-06-15T17:33:52Z`
- 输出目录：`.omx/state/langgraph/extraction/fresh-source-lifecycle-whitepaper-pmi-refresh-20260616/`
- 来源：共 54 个；Business Management 31 个；PMP 23 个
- 读取单元：共 9,656 个；PDF 页 9,280 个；EPUB spine item 362 个；Markdown 全文 14 个
- 抽取字符：18,492,044
- Business Management：31 个来源 / 6,551 个单元 / 14,161,228 个字符
- PMP：23 个来源 / 3,105 个单元 / 4,330,816 个字符
- 状态：全部来源为 `ok`

本矩阵只使用已提交综合证据。raw extraction streams、逐单元文本、本地 caches 和 logs 仍是 ignored local artifacts，干净 worktree 中可能不存在。

## UR1-UR4 映射

| 用户要求 | 交付含义 | 必需证明面 |
| --- | --- | --- |
| UR1 | 根据 Business Management 和两份 architecture inventory notes 刷新产品生命周期文件。 | 生命周期地图和 inventory maps 引用当前证据边界，并指向本文说明交付覆盖。 |
| UR2 | 根据 Business Management 与生命周期文档刷新白皮书、北极星和相关文件。 | 白皮书、MRD、北极星、实施方案、playbook、bridge、traceability 与 specs 使用同一证据边界。 |
| UR3 | 解释为什么白皮书和研究稿同时存在，以及 10 层如何连接到 12 层。 | 白皮书与研究稿保持分离；`ten_to_twelve_layer_bridge.zh-CN.md` 与本文记录桥接。 |
| UR4 | 对 execution-facing flow 使用 PMI 过程组语法和裁剪规则。 | `durable_team_process_group_contract.zh-CN.md` 定义输入 / 工具与技术 / 输出，以及裁剪交接规则。 |

## 文档目标矩阵

| 目标文档 | 主要权威 | 必需刷新增量 | 证据边界声明 | 桥接依赖 | 过程组依赖 | 不得声称 |
| --- | --- | --- | --- | --- | --- | --- |
| 白皮书 | 战略叙事与 12 层生命周期框架 | 引用 20260616 证据边界并指向证明面。 | 只引用聚合综合证据；不依赖 raw cache。 | runtime findings 通过 10-to-12 bridge 落地。 | 叙事结果变成交付工作时才使用过程组契约。 | 不拥有 runtime capability criteria，也不证明 running team。 |
| 治理研究稿 | runtime/governance capability canon 与 10 层核心 | 保持 10 层标准独立，并引用共享刷新边界。 | tracked synthesis 可更新语境；raw cache 继续 ignored。 | 向 bridge 提供 runtime findings。 | 只对 execution-facing recommendations 使用过程组。 | 不替代白皮书或 lifecycle inventory。 |
| 实施方案 | 多项目实施形态 | 让 release slices 指向交付、追踪和过程组证明面。 | draft plan 不是 runtime evidence。 | 将 bridge outputs 转为阶段化职责。 | durable lane launch 前要求 I/T/O。 | 不声称完整目标已实现。 |
| Playbook | release-slice operating guidance | 将 proof-surface checks 加入未来 slice preconditions。 | slice evidence 必须 tracked 且可复现。 | 改变 layer responsibilities 前使用 bridge docs。 | slice gates 使用 process-group contract。 | 未经明确 slice rules 不授权 runtime apply。 |
| 交付矩阵 | 交付证明与 UR 覆盖 | 拥有 UR1-UR4 mapping 与 target rows。 | 使用聚合 run identity。 | 指向 bridge owner 但不替代。 | 指向 contract owner 但不替代。 | 不存储来源或批准发布。 |
| 来源追踪 | evidence chain proof | 将 source families 映射到 authority destinations。 | 拥有 tracked versus ignored evidence rule。 | 记录同一刷新如何同时影响二者但不合并。 | 向 process-group contract 提供 inputs。 | 不引用 raw source text。 |
| 过程组契约 | execution grammar proof | 为 gates 与 slices 定义输入 / 工具与技术 / 输出。 | 只按 tracked docs 验证。 | 使用 bridge 前要求 authority split review。 | 拥有 I/T/O grammar 与 tailoring handoff。 | 不证明 runtime behavior。 |
| OpenSpec specs | 验收权威 | 把证明面作为稳定治理义务。 | specs 引用 tracked docs，不引用 raw cache。 | stable specs 提到 10 层到 12 层交接。 | lifecycle spec 拥有过程组交付 gate mapping。 | 不替代 docs 或 source references。 |

## 12 层落地摘要

| 生命周期区域 | 刷新落地规则 |
| --- | --- |
| 认知叙事与商业 | 白皮书解释 durable-team 平台为何存在，以及白皮书/研究稿分离为何仍有价值。 |
| 市场、战略与指标 | MRD 与北极星把刷新转为目标用户、工作负载画像、成功指标和 guardrails。 |
| 产品与技术 | 产品生命周期、inventory maps 和实施方案把来源综合转为平台范围与架构边界。 |
| 组织与执行 | Playbook、过程组契约和 OpenSpec specs 把决策转为有 owner 的 release slices。 |
| 增长、运营与复盘 | Traceability 与 closeout records 保存学习，但不把 raw cache 变成权威。 |

runtime capability findings 可以落到多个生命周期区域。该落地不改变研究稿对 10 层 runtime/governance capability core 的权威。

## 关系规则

- 白皮书引用战略结论和生命周期影响，不引用 raw-source criteria。
- 研究稿拥有 capability criteria、official-versus-derived distinctions 和 runtime/governance decomposition。
- Bridge documents 只映射权威，不替代权威。
- 数量权威保留在 `codex_platform_inventory_map.zh-CN.md` 和 `one_person_company_inventory_map.zh-CN.md`。
- Source-run identity 与 tracked-versus-ignored evidence rules 集中在 `fresh_source_reading_evidence.zh-CN.md` 和 `durable_team_source_traceability.zh-CN.md`。

## Release-Slice 相关性

后续 OpenSpec changes 如果改变 durable-team 文档、生命周期范围或 release-slice gates，应该使用本矩阵。release slice 只有在能够命名以下内容后才可实施：

### 输入

- 受影响用户要求标签；
- 当前来源证据边界；
- 权威文档和 count maps；
- 受影响 lifecycle layers 与 OpenSpec capabilities。

### 工具与技术

- authority split review；
- 10-layer to 12-layer landing analysis；
- PMI tailoring review；
- local-main-first validation planning。

### 输出

- updated files 与 changed-path list；
- validation evidence；
- explicit non-goals；
- rollback 与 archive evidence。

## 非目标

- 不启动 runtime 或 durable-team apply mode。
- 不批准远程发布。
- 不把 raw source 或 per-unit extraction text 提交进 Git。
- 不物理合并白皮书与研究稿。
- 不声称 draft documentation 证明 production durable team 正在运行。
