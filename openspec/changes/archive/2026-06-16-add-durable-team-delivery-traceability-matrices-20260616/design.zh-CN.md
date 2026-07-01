# 设计：持久化团队交付、追踪与过程组证明面

## 背景

fresh source run `fresh-source-lifecycle-whitepaper-pmi-refresh-20260616` 生成于 `2026-06-15T17:33:52Z`，记录 54 个来源、9,656 个读取单元和 18,492,044 个抽取字符。Git 跟踪文档只能引用聚合与综合证据；原始抽取文本继续保留在本地忽略态 cache 中。

上一轮语料同步已经澄清 10 层运行时/治理能力核心与 12 层产品/商业生命周期规划框架。本切片新增证明面，使维护者无需继续膨胀每一份既有权威文档，也能审计交付范围、证据边界和执行语法。

## 决策

1. 新增三份小型证明面，而不是继续扩写白皮书、研究稿、实施方案和 playbook。
2. 明确权威拆分：白皮书拥有战略叙事，研究稿拥有 runtime/governance 能力标准，inventory maps 拥有数量权威，PMI/lifecycle maps 拥有裁剪与过程组语法。
3. 使用 UR1 到 UR4 作为跨文档用户要求标签。
4. 所有证明面保持 docs-only。它们只证明文档治理，不证明 runtime 已经实现。
5. 手动同步稳定 OpenSpec 规格，并把 active delta specs 作为受治理变更证据。

## 文件范围

- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_delivery_matrix.*` - 将 UR1 到 UR4 映射到交付文档、数量与责任证据。
- `docs_bilingual/product_lifecycle/durable_team_source_traceability.*` - 记录 fresh source run 身份、来源计数和 Git 跟踪/忽略证据边界。
- `docs_bilingual/product_lifecycle/durable_team_process_group_contract.*` - 定义“输入 / 工具与技术 / 输出”语法适用的位置。
- 仍引用上一轮证据边界的 active durable-team corpus docs
- `docs_bilingual/docs_registry.yaml` - 注册新增双语证明面，便于检索与治理。
- `openspec/specs/codex-cli-personal-production-durable-team-plan/spec.*` - 将交付矩阵和桥接要求纳入稳定 durable-team plan contract。
- `openspec/specs/codex-product-lifecycle-document-governance/spec.*` - 将追踪与过程组证明要求纳入稳定 document-governance contract。
- 本 OpenSpec 变更包与 Superpowers 证据 artifacts

## 风险与缓解

| 风险 | 缓解 |
| --- | --- |
| 证明面被误认为 runtime evidence | 反复声明这些文档只是 draft/documentation evidence，不是 running durable-team proof。 |
| raw cache 变成权威依赖 | 每个新增证明面都写明 tracked 与 ignored evidence。 |
| 白皮书与研究稿角色被混同 | 在 traceability 与 delivery matrix 中保留关系和不合并规则。 |
| 过程组词汇变成所有地方的重型仪式 | 只对 execution-facing layers、gates 和 slices 强制 Inputs / Tools and Techniques / Outputs。 |
| 中文 companion 漂移 | 双语成对写入，并运行 pair/mojibake checks。 |

## 验收证据

- 新双语证明面存在并已登记。
- 活跃文档以 `fresh-source-lifecycle-whitepaper-pmi-refresh-20260616` 和 `2026-06-15T17:33:52Z` 作为当前证据边界。
- 稳定和增量 OpenSpec requirement 提到 delivery、traceability 与 process-group proof surfaces。
- 验证命令通过，或记录明确 follow-up blocker。
