---
doc_id: durable_team_process_group_contract
lang: zh-CN
canonical: docs_bilingual/product_lifecycle/durable_team_process_group_contract.md
translation_of: docs_bilingual/product_lifecycle/durable_team_process_group_contract.md
doc_class: product_lifecycle
status: draft
---

# 持久化团队过程组契约

## 目的

本契约定义 durable-team 文档刷新与未来 release slices 的过程组执行语法。它告诉维护者什么时候必须写输入、工具与技术、输出，以及每一类必须包含什么。

本文拥有 durable-team 文档交付的 I/T/O contract。它不替代 PMI references、lifecycle tailoring rules、OpenSpec specs 或 runtime evidence。

## PMI 框架

- PMBOK 8 是当前规划的主要 value-delivery 与 tailoring overlay。
- Process Groups 提供执行语法：启动、规划、执行、监控、收尾。
- PMBOK 6 的 I/T/O 词汇只在产出执行 artifacts 时作为支持词汇。
- Agile guidance 支持探索性、MVP、反馈驱动和 hybrid slices。
- Program、portfolio 与 PMO references 提供 sequencing、value balance、governance services 与 reusable standards。

## 顶层契约

每个 durable-team refresh 或 implementation slice 只要影响 execution、release gates、durable-lane selection、runtime behavior、documentation authority、validation、rollback 或 closeout，就必须识别输入、工具与技术、输出。

Docs-only slices 如果改变未来 delivery rules 或 acceptance criteria，也使用本契约。完成本契约不是 runtime implementation evidence。

## I/T/O 术语与适用清单

`Inputs / Tools and Techniques / Outputs`、`Inputs / Tools & Techniques / Outputs` 与中文 `输入 / 工具与技术 / 输出` 在本文档族中是等价标签。新的英文表格 SHOULD 优先使用 `Inputs / Tools and Techniques / Outputs`；审计时 MAY 把 `Tools & Techniques` 作为缩写匹配。

| 文档或证明面 | I/T/O 要求 | 原因 |
| --- | --- | --- |
| `product_business_document_lifecycle.*` | 每个 lifecycle layer 必须使用。 | 它是 0-11 / 12 层执行语法权威。 |
| `codex_durable_team_platform_build_lifecycle.*` | 每个平台建设层必须使用。 | 它把通用生命周期转成 Codex 平台建设流程。 |
| `codex_platform_inventory_map.*` 与 `one_person_company_inventory_map.*` | 必须提供清单级摘要和过程门。 | 它们拥有架构数量权威，必须说明这些数量如何进入执行。 |
| `pmi_project_management_reference_map.*` 与 `lifecycle_tailoring_rules.*` | PMI 叠加和裁剪决策必须使用。 | 它们判断 full、whole-project lightweight、phase-local、module-level 或 hybrid governance。 |
| `durable_team_process_group_contract.*` | 必须使用，且本文是 canonical。 | 本文拥有 durable-team 过程组契约。 |
| `durable_team_source_traceability.*` 与 `ten_to_twelve_layer_bridge.*` | 驱动执行的交接部分必须使用。 | 它们把来源证据和 10 层 runtime findings 连接到 12 层工作。 |
| `fresh_source_reading_evidence.*` 与 `business_management_source_synthesis.*` | 不要求每节都使用；只有交接到执行时必须使用。 | 它们是证据边界和综合面，不是交付流程。 |
| 白皮书、研究稿、MRD、北极星、实施方案、playbook 与 OpenSpec specs | 当 section 描述 execution、release、validation、rollout 或 closeout 时必须使用。 | 叙事 section 可以委派给本契约；执行 section 必须可检查。 |

## 契约输入

| 输入 | 何时必需 |
| --- | --- |
| 来自 `one-person-company-pmi-refresh-stageb-20260619` 的当前 source synthesis | slice 引用 Business Management、PMP、lifecycle、white paper 或 research refresh evidence。 |
| 当前白皮书 | slice 改变 narrative、platform purpose、lifecycle framing 或 adoption logic。 |
| 当前治理研究稿 | slice 改变 runtime capability criteria、layer decomposition 或 governance evidence。 |
| 10-to-12 bridge 与 lifecycle maps | slice 把 runtime findings 映射到 product/business lifecycle zones。 |
| Inventory/count authority docs | slice 重复或改变 architecture counts。 |
| Implementation plan 与 playbook | slice 改变 release order、file scope、validation 或 rollback。 |
| OpenSpec artifacts | slice 改变 repository structure、specs、governance 或 acceptance behavior。 |
| Local validation state | slice 准备 commit、archive、local-main integration 或 remote publication。 |

## 工具与技术

| 技术 | 用途 |
| --- | --- |
| Synthesis review | 判断 claim 是 source-refresh-derived，还是已经属于 stable repository authority。 |
| Authority split review | 保持 white paper、research note、inventory maps、PMI map 与 OpenSpec 职责分离。 |
| 10-layer to 12-layer landing analysis | 决定 runtime finding 落到哪个 lifecycle layer。 |
| Tailoring review | 选择 full architecture、whole-project lightweight、phase-local lightweight、module-level lightweight 或 hybrid governance。 |
| Local-main-first discipline | 规划 local validation、local MR review、local integration、rollback 与 remote-publication stop point。 |
| Tracked-doc-only validation | 只用已提交 docs 与允许的 summaries 验证 claim，不使用 ignored raw cache。 |
| Variance and change-impact review | 决定 slice 可以收尾、必须回到 design/build，还是必须开 follow-up change。 |

## 输出

| 输出 | 含义 |
| --- | --- |
| Strategic narrative delta | 带 evidence boundary 的 white paper、MRD 或 North Star 更新。 |
| Capability/governance delta | Research note、bridge、implementation plan 或 spec 更新。 |
| Delivery matrix row | UR-to-file coverage 与 non-goals。 |
| Traceability entry | Source-family to authority mapping 与 evidence boundary。 |
| Tailoring decision | Full、whole-project lightweight、phase-local lightweight、module-level lightweight 或 hybrid。 |
| Validation evidence | Commands、reports、changed paths 与 residual risk。 |
| Closeout evidence | OpenSpec archive、stable spec sync、rollback reference、local-main status 与 lessons learned。 |

## 过程组表

| 过程组 | 输入 | 工具与技术 | 输出 | durable-team gate question | UR coverage |
| --- | --- | --- | --- | --- | --- |
| 启动 | 用户请求、当前来源证据边界、受影响权威文档、非目标 | Value framing、scope split、authority split review、OpenSpec proposal | Change proposal、success criteria、constraints、no-runtime boundary | 这是 documentation、runtime 还是 remote-publication work？ | UR1, UR2, UR3, UR4 |
| 规划 | Proposal、design context、traceability chain、inventory maps、PMI map、lifecycle tailoring rules | 10-to-12 landing analysis、tailoring review、release and rollback planning、validation planning | Design、tasks、implementation plan、expected proof surfaces | 计划是否冻结，execution slices 是否独立？ | UR1, UR3, UR4 |
| 执行 | Approved tasks、file ownership、current branch、proof-surface targets | Main-session integration、bounded expert fan-out、tracked-doc-only edits、local checks | Updated docs、specs、registry、proof surfaces、changed-path list | 写入是否隔离，raw caches 是否排除？ | UR1, UR2, UR3, UR4 |
| 监控 | Diff、validation output、risk list、checker results、subagent fan-in | Variance review、risk/change impact assessment、rework decision、OpenSpec strict validation | Pass/fail evidence、fix list、return decision 或 closeout readiness | 证据是否证明 claim，且没有过度声称 runtime status？ | UR2, UR3, UR4 |
| 收尾 | Verification report、completed tasks、stable spec delta、archive checklist、local integration plan | Archive、stable spec sync、local-main-first gates、lessons learned、rollback record | Archived change、verification report、commit、local-main state、follow-up queue | 更新了什么、什么仍是 draft、remote approval stop 在哪里？ | UR1, UR2, UR3, UR4 |

## 裁剪结果

| 结果 | 使用条件 | 全项目还是局部 |
| --- | --- | --- |
| Full architecture | scope 改变 reusable orchestration、trust、durable state、release safety、cross-project templates、launcher policy、CI gates 或 runtime behavior。 | 对受影响 architecture layers 完整，不必覆盖每个 downstream business module。 |
| Whole-project lightweight | 整个项目 private、reversible、low-risk、local-only，且没有 shared runtime、sensitive data、release promise 或 external users。 | 整个项目可以 lightweight。 |
| Phase-local lightweight | Discovery、metrics、growth 或 retrospective work 是较大治理工作内部的有界阶段。 | 只有该 phase lightweight。 |
| Module-level lightweight | 有界 doc、helper、research note 或 spike 不改变 entrypoints、state、secrets、CI、releases 或 dependencies。 | 只有该 module lightweight。 |
| Hybrid | 不确定性仍高，但后续交付可能影响 production、users、trust、revenue、compliance、runtime behavior 或 release safety。 | 先轻量；release 前扩展受影响层级。 |

## Durable-Team 特定契约规则

- 任何 process-group step 都不得把 raw extraction cache 当成 tracked authority。
- 任何 process-group step 都不得声称白皮书和研究稿已经合并。
- 同时使用两个 layer models 的 execution artifact 必须说明哪个模型对哪个 claim 具有权威。
- 每个 closeout 必须识别已经更新了什么、什么仍是 draft、什么仍是 future-state。
- Durable-team launch 仍要求 frozen plan 加至少两个基本独立 execution slices，或带 blocking issues 的 stabilize threshold。
- LangGraph 或 `native_omx` runtime apply mode 需要明确 slice permission 与当前证据；documentation contracts alone 不授权 apply mode。

## 交接到实施与发布

当更新影响 execution 的 implementation plans、playbooks 或 OpenSpec changes 时，先使用本契约。release slice 应只复制相关 I/T/O 行和裁剪决策，而不是复制整份文档。

### 输入

- delivery matrix row；
- source traceability entry；
- authority split decision；
- affected OpenSpec requirement。

### 工具与技术

- slice planning；
- validation command selection；
- rollback planning；
- branch and publication gate review。

### 输出

- implementable tasks；
- validation report；
- archive-ready OpenSpec package；
- remote-publication gate 的明确停止点，除非用户批准远程动作。

## 非目标

- 本契约不复现 PMI source content。
- 本契约不证明 runtime implementation。
- 本契约不替代 OpenSpec validation。
- 本契约不授权 remote publication。

## 一人公司执行契约补充

一人公司中凡是涉及执行的章节，同样使用过程组语法。轻量业务循环可以压缩制品集，但仍要为受影响层级、阶段或模块命名输入、工具与技术、输出。契约只扩展到真实风险面：先扩展承载客户、收入、信任、支持、合规、发布或受治理 Agent 风险的层级；只有耦合系统化时才扩展整个项目。
