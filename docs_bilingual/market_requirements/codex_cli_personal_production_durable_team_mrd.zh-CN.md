---
doc_id: codex_cli_personal_production_durable_team_mrd
lang: zh-CN
canonical: docs_bilingual/market_requirements/codex_cli_personal_production_durable_team_mrd.md
translation_of: docs_bilingual/market_requirements/codex_cli_personal_production_durable_team_mrd.md
doc_class: market_requirements
status: draft
---

# MRD：Codex CLI 个人开发者生产级持久化团队

## 目的

本文是 Codex CLI 个人开发者生产级持久化团队平台的 MRD。MRD 是市场需求文档，用来识别目标用户、项目类型、使用场景、能力画像、运行归属类型和通用控制要求。

本文替代原独立文件 `docs_bilingual/implementation_plans/codex_business_capability_profiles.zh-CN.md`；该文件原本是能力画像查询表，现在合并到本文附录 A。能力画像查询表是把具体 workload 映射到抽象 capability profile 的表格。

## 目标用户与项目类型

- solo maintainer：单人维护者，是跨多个仓库使用 `Codex CLI` 的主要操作者。
- consumer project：消费项目，是复用 user-level runtime、templates、policies 和 native subagent profiles 的下游仓库，同时保留自己的源码、OpenSpec artifacts、测试和 durable state。
- domain-agent platform project：领域 Agent 平台项目，是在 Codex CLI 外部承载最终用户领域 Agent 的项目，Codex CLI 负责辅助开发、治理、检查和发布。
- document or content workflow project：文档或内容工作流项目，是创建、转换、审查、发布或审计 artifacts 的项目。

## 用户问题

- cold-start sessions 需要安全接续，而不是反复要求用户手工解释上下文。cold-start sessions 是没有旧上下文的新会话。
- 多个会话需要文件归属边界，避免 dirty-worktree collision。dirty-worktree collision 是多个会话同时污染同一个 Git 工作区。
- 项目需要 browser、document、GUI、model-provider 和 publication support，同时不能把业务运行真相混进 Codex 平台仓库。browser 是浏览器自动化能力，document 是文档处理能力，GUI 是图形界面能力，model-provider 是模型服务能力，publication support 是发布辅助能力。
- 高风险动作需要 human approval、audit records、rollback notes 和 project-local evidence。human approval 是人工审批，audit records 是审计记录，rollback notes 是回滚说明，project-local evidence 是项目本地证据。

## 市场需求

- 平台必须保留 native Codex 功能并保持可回退。native Codex 是原生 Codex CLI 能力。
- 平台必须支持后续项目使用 local Git 加 OpenSpec governance。local Git 是本地 Git 仓库，OpenSpec governance 是 OpenSpec 治理流程。
- 平台必须隔离 Codex CLI durable-team dependencies 和 downstream business runtime dependencies。Codex CLI durable-team dependencies 是编排团队自身依赖，downstream business runtime dependencies 是下游业务运行依赖。
- 平台必须在 implementation work 开始前，把新 workload 分类到 abstract capability profiles。implementation work 是实施工作，abstract capability profiles 是抽象能力画像。
- 平台必须为需要的项目保留 browser automation 和 document-processing capabilities。browser automation 是浏览器自动化，document-processing capabilities 是文档处理能力。

## 优先级信号

- P0 requirements 保护 native Codex compatibility、session isolation、repo-local durable truth、OpenSpec guards 和 rollback。P0 requirements 是最高优先级需求。
- P1 requirements 改进 inspected durable routing、project templates、local model-provider adapters 和 repeatable release slices。P1 requirements 是下一优先级需求。
- P2 requirements 改进 local GUI control、advanced memory、richer evaluation 和 broader adoption reporting。P2 requirements 是较后优先级需求。

## 附录 A：从原参考文件合并来的能力画像

本参考文件用于把具体 workload example 映射到 Codex CLI 个人开发者生产级持久化团队方案中的抽象 capability profiles。它是查询表，不是 runtime contract，也不表示这些 workload 已经实现。

## 1. 使用规则

- 具体 workload 名称保留在本参考文件中，不写进生产级持久化团队主方案正文。
- 每个 workload 在开始 implementation work 前，必须先映射到一个或多个 abstract profiles。
- Runtime owner class 是边界标签，不是强制技术选型。
- Codex CLI durable-team dependencies 必须和 business runtime dependencies 隔离；除非业务项目在自己的仓库中显式拥有同名依赖，否则不能混用。
- local Llama model service 是本参考文件里的唯一共享依赖例外；即便如此，也必须通过 provider adapters 使用，并隔离 logs、permissions、prompts、secrets 和 data boundaries。

## 2. Runtime Owner Classes

| Runtime owner class | 含义 |
| --- | --- |
| Codex-developed project | 具体项目的源码、测试、依赖和 release artifacts 位于自己的仓库，Codex CLI durable team 负责辅助开发和治理。 |
| External domain-agent runtime | 位于 Codex CLI 之外的最终用户 domain-agent runtime；Codex CLI durable team 负责 profiles、knowledge updates、release checks、regression 和 recovery support，不直接承载最终用户对话。 |
| External content platform | 第三方发布、消息、商业或内容平台；所有发布和回复动作都需要 approval、audit 和 platform-boundary controls。 |
| Local professional tool | 本地桌面或专业工具，通过 guided steps、screenshots、local files 或 human-in-the-loop verification 使用。 |
| Document processing pipeline | 转换 files、layouts、evidence 和 generated deliverables 的工作流，同时保留 audit 和 review records。 |
| Shared local model service | 通过 adapter 使用的 local Llama deployment；它是 model provider，不是 workflow state 或 business state。 |

## 3. 具体 Workload 对照表

| Concrete workload example | Abstract capability profiles | Runtime owner class | Required universal controls | Risk level |
| --- | --- | --- | --- | --- |
| 制作供用户挑选 Live2D 虚拟形象的微信小程序 - 面向用户选择角色资产的前端产品。 | Interactive frontend product delivery; generated media asset pipeline. | Codex-developed project. | UI validation、asset versioning、release gate、rollback note。 | Medium. |
| 使用秋叶 ComfyUI 生成适合 Live2D 虚拟形象原画 - 本地图像生成 workflow，用于生成角色源图。 | Generated media asset pipeline. | Local professional tool；使用本地模型时也属于 shared local model service。 | Prompt and parameter record、asset review、source and license note、approval before downstream use。 | Medium. |
| 自动生成并发布抖音视频 - 内容生成与平台发布 workflow。 | Generated media asset pipeline; platform content operations. | External content platform. | Human approval、audit ledger、platform receipt capture、retry boundary、rollback or takedown note。 | High. |
| 自动回复抖音店铺客户消息 - 商业渠道的客户回复与人工接管 workflow。 | Customer message automation with human handoff; platform content operations. | External content platform. | Sensitive-content detection、human takeover、reply audit、escalation、secrets boundary。 | High. |
| 基于积极心理学/人本主义心理学的情感/心理咨询领域 Agent - 配置在 external domain-agent runtime 中的敏感支持型 agent。 | External domain-agent runtime governance; customer message automation with human handoff; high-risk decision support. | External domain-agent runtime. | Crisis escalation、disclaimer、privacy boundary、human handoff、regression set、audit。 | Sensitive / high. |
| 论文文献查询领域 Agent - 配置在 external domain-agent runtime 中的 citation 和 evidence-oriented knowledge agent。 | External domain-agent runtime governance; knowledge retrieval and citation workflows. | External domain-agent runtime. | Source citation、evidence chain、hallucination check、knowledge refresh、regression set。 | Medium. |
| ANSYS 仿真软件使用教学领域 Agent - 配置在 external domain-agent runtime 中的 guided professional-tool teaching agent。 | External domain-agent runtime governance; professional tool teaching and guided operation; knowledge retrieval and citation workflows. | External domain-agent runtime; local professional tool. | Step verification、screenshot evidence、case library、risk notice、regression set。 | Medium / high. |
| 个人级生产级一人公司运营 workflow - 面向 sales、delivery、cost 和 review cycles 的个人运营工作流。 | Solo business operations management; structured proposal and compliance document delivery. | Codex-developed project. | Audit、review cadence、customer data boundary、financial data boundary、backup。 | Medium / high. |
| 个人级生产级量化金融交易工具 - 用于 research、simulation 和 risk-controlled operations 的 decision-support tooling。 | High-risk decision support; knowledge retrieval and citation workflows; generated report pipeline. | Codex-developed project. | Paper-trading default、approval、backtest、audit、stop-loss note、no default live execution。 | High / regulated. |
| PDF 翻译原位置文字替换 workflow - 版式敏感 document transformation workflow。 | Layout-sensitive document transformation. | Document processing pipeline. | OCR or text extraction record、render diff、human review、output audit、source backup。 | Medium. |
| 实质投标/资料生成任务 - 结构化 deliverable production workflow。 | Structured proposal and compliance document delivery; knowledge retrieval and citation workflows; layout-sensitive document transformation. | Document processing pipeline. | Source collection、citation、compliance checklist、approval、final version record。 | High. |
| 新电脑和项目模板 rollout workflow - 面向新开发机和既有项目的 bootstrap/update workflow。 | Template and project bootstrap lifecycle. | Codex-developed project. | Backup branch、manifest comparison、managed-file update、checker gate、rollback note。 | Medium. |

## 4. 扩展规则

当新的 concrete workload 出现时，先把它加入本表，映射到 abstract profiles，再判断 Codex CLI durable team 是否需要新增 shared adapters、checkers、regression fixtures 或 template update support。
