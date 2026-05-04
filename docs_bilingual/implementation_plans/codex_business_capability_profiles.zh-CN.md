---
doc_id: codex_business_capability_profiles
lang: zh-CN
canonical: docs_bilingual/implementation_plans/codex_business_capability_profiles.md
translation_of: docs_bilingual/implementation_plans/codex_business_capability_profiles.md
doc_class: implementation_reference
status: draft
---

# Codex 业务能力 Profiles 对照表

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
