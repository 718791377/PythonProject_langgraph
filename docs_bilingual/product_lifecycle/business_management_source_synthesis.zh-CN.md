# Business Management 来源库综合

本文基于对忽略目录 `D:/PythonProject_langgraph/Business Management` 与 `D:/PythonProject_langgraph/PMP` 的 2026-06-16 fresh extraction 结果，综合与本仓库相关的经营、产品、架构与交付启发。该抽取产物是本次刷新的证据，不是可替代源文件的缓存结论。本文是 `docs_bilingual/product_lifecycle/` 的综合层，不复制源书长段正文。

## Fresh Extraction 范围

本次刷新以 `2026-06-15T17:33:52Z` 重新生成的忽略态证据目录 `.omx/state/langgraph/extraction/fresh-source-lifecycle-whitepaper-pmi-refresh-20260616/` 为依据，运行 ID 为 `fresh-source-lifecycle-whitepaper-pmi-refresh-20260616`。这些产物是本次刷新的 fresh reading 证据，不替代源文件，也不是可反复套用的结论缓存。

- 清单：`fresh_source_manifest.json`
- 逐单元提取日志：`fresh_source_items.jsonl`
- 紧凑汇总：`fresh_source_synthesis.json`
- 提取脚本入口：`fresh_extract_sources.py`

54 个已记录来源全部以 `ok` 状态完成。

## 覆盖清单

### 总体覆盖

| 来源家族 | 来源数 | PDF / 页数 | EPUB / spine item | Markdown / 全文文件 | 总读取单元 | 提取文本字符数 | 空白单元 | 低文本单元 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Business Management | 31 | 22 / 6,245 | 7 / 304 | 2 / 2 | 6,551 | 14,161,228 | 642 | 832 |
| PMP | 23 | 9 / 3,035 | 2 / 58 | 12 / 12 | 3,105 | 4,330,816 | 392 | 758 |
| **合计** | **54** | **31 / 9,280** | **9 / 362** | **14 / 14** | **9,656** | **18,492,044** | **1,034** | **1,590** |

### 按格式的读取方法

| 格式 | 记录数量 | 覆盖单元 | 提取方法 | 实际含义 |
| --- | ---: | --- | --- | --- |
| PDF | 31 个文件 | 页 | 对每一页执行 PyMuPDF `get_text("text")` | 适合记录页数证据、低文本页统计，以及扫描件/图像页注意事项 |
| EPUB | 9 个文件 | OPF spine item | 使用 `ebooklib` 迭代 spine，再抽取 HTML/XHTML 文本 | 适合在不打乱原阅读顺序的前提下记录章节级覆盖 |
| Markdown | 14 个文件 | 全文件 | 直接按 UTF-8 全文读取 | 适合保留精确架构清单、标题结构与仓库术语 |

### 需要保留的覆盖说明

- 低文本复核是覆盖统计的一部分，不代表未阅读。许多低文本单元来自封面、空白页、图表页、扫描页或图片密集页。
- `Business Management/Escaping the build trap.pdf` 在 `pypdf` 文件级抽取失败后，通过 PyMuPDF 回退成功；manifest 将该证据记录为 source `S0010`。
- 低文本最集中的主要是少数扫描感较强或图片较重的 PDF，尤其是 `Business Management/Lean Analytics.pdf`（439 页，388 个低文本页）、`PMP/敏捷实践指南 = Agile practice guide.pdf`（184 页，183 个低文本页）、`PMP/项目管里知识体系指南  PMBOK指南  第6版.pdf`（812 页，301 个低文本页）和 `PMP/项目组合管理标准  第4版.pdf`（142 页，141 个低文本页）。
- 因为本文是综合产物，所以只记录计数、方法和解释，不保留原始提取文本。

## 目标架构清单证据

用户要求的两个目标架构清单，控制性来源都是本地 Markdown 架构笔记，因为它们采用 UTF-8 全文读取并保留了明确的章节标题。

| 目标 | 控制性来源 | fresh-read 证据 | 生命周期文档中保留的清单 |
| --- | --- | --- | --- |
| Codex CLI 个人开发者生产级持久化团队 | `架构 1：Codex CLI 个人开发者生产级持久化团队.md` | 10,424 字符；标题包含 `1 主干层级矩阵`、`2 虚拟部门矩阵`、`3 24 个责任域矩阵`、`4 18 个横切模块矩阵`、`5 48 个核心文档系统`、`6 12 个受治理 AI Agent` | 12 层主干、4 个虚拟部门、24 个责任域、18 个横切模块、48 个核心文档、12 个受治理 AI Agent、12 本推荐书籍 |
| 个人级生产级一人公司 | `架构 2：个人级生产级一人公司运营.md` | 18,544 字符；标题包含 `2. 12 层主干`、`3. 5 个虚拟部门`、`4. 30 个责任域`、`5. 20 个横切模块`、`6. 60 个核心文档系统`、`7. 15 个受治理 AI Agent`、`11. 最小可运行 MVP` | 12 层主干、5 个虚拟部门、30 个责任域、20 个横切模块、60 个核心文档、15 个受治理 AI Agent、15 本推荐书籍、12 份最小启动文档 |

这两份笔记定义了仓库内部要使用的精确清单数量；Business Management 与 PMP 书籍则解释这些清单应如何运行、如何裁剪、以及如何保持轻量。

## 来源家族映射

### Business Management 家族 → 经营模型与架构综合

| 来源簇 | fresh-read 代表来源 | 对生命周期的主要贡献 |
| --- | --- | --- |
| 战略、定位与商业设计 | `Good strategy, bad strategy.pdf`、`Company of One`（PDF + EPUB）、`The E-Myth Revisited.pdf`、`Working Backwards.pdf`、`Obviously Awesome.pdf`、`Traction.epub` | 诊断、指导方针、有意保持小规模、定位、渠道选择、PR/FAQ 式思考与 operating system 设计 |
| 产品发现与产品运营 | `INSPIRED.pdf`、`Continuous Discovery Habits.pdf`、`Deploy Empathy.epub`、`Escaping the build trap.pdf`、`Product Operations`（PDF + EPUB）、`The Lean Startup.pdf`、`Crossing the Chasm, 3rd Edition.pdf` | 机会发现、访谈循环、产品风险分解、产品运营赋能、MVP 纪律与采用阶段排序 |
| 指标、管理节奏与规模化 | `Lean Analytics.pdf`、`Measure What Matters.pdf`、`High Output Management.pdf`、`Scaling People.epub` | OMTM 与阶段指标、OKR 对齐、管理杠杆、规划节奏，以及一人公司或 agent-assisted 系统的规模纪律 |
| 架构、技术边界与交付设计 | `Clean Architecture.pdf`、`Clean Architecture - 架构整洁之道.pdf`、`Designing Data-Intensive Applications.pdf`、`Accelerate.pdf`、`Team Topologies.epub`、`Secure by Design`（PDF + EPUB）、`The Staff Engineer’s Path.pdf`、`Shape Up.pdf` | 依赖方向、数据与可靠性关注点、团队/API 边界、安全设计约束、资深工程判断、shaping、appetite 与交付护栏 |
| 仓库特定架构清单 | `架构 1：Codex CLI 个人开发者生产级持久化团队.md`、`架构 2：个人级生产级一人公司运营.md` | 精确目标清单、本地术语，以及通用管理建议到仓库规则之间的桥梁 |

### PMP 家族 → 交付治理与 tailoring 叠加层

| 来源簇 | fresh-read 代表来源 | 对生命周期的主要贡献 |
| --- | --- | --- |
| 核心标准与过程控制 | `PMBOK® Guide 8th Edition .pdf`、`项目管理知识体系 第七版 (PMBOK® 体系) 指南.pdf`、`项目管里知识体系指南  PMBOK指南  第6版.pdf`、`Process groups _ a practice guide.pdf`、`过程组_实践指南(ProcessGroupsPracticeGuide) .pdf` | 过程组纪律、结果导向、tailoring 决策、控制回路、风险/变更审视与收尾证据 |
| 敏捷、项目集、项目组合与 PMO 叠加 | `The Agile practice guide.pdf`、`The Standard for Program Management - Fifth Edition.epub`、`The Standard for Portfolio Management-Fourth Edition.pdf`、`Project Management Offices  a Practice Guide.epub` | 混合/敏捷交付、项目集排序、项目组合优先级、治理 operating model 与 PMO 能力映射 |
| PMBOK 8 / AI 时代解读笔记 | `PMP/PMP_MD/` 下 12 份 Markdown 笔记，以及 Joshua Parrott 中文翻译笔记 | 更贴近仓库语境的 PMBOK 8 原则、focus areas、PMO 演化、tailoring 与 AI 时代项目领导解释 |

## 有证据支撑的阅读重点

### 架构密度最高的 Business Management 来源

fresh extraction 汇总显示，以下来源最集中地支撑架构层判断：

| 来源 | 格式 | 覆盖 | 在这里的重要性 |
| --- | --- | --- | --- |
| `Designing Data-Intensive Applications.pdf` | PDF | 613 页 | 全语料中架构信号最强，支撑状态、数据、可靠性与集成推理 |
| `Secure by Design.pdf` | PDF | 400 页 | 提供安全不变量与 secure-by-default 生命周期约束 |
| `Secure by Design.epub` | EPUB | 31 个 spine item | 作为同主题 EPUB 侧的 spine 级复核 |
| `Clean Architecture.pdf` | PDF | 429 页 | 支撑边界与依赖方向纪律 |
| `Clean Architecture - 架构整洁之道.pdf` | PDF | 380 页 | 同一架构主题的中文对照来源 |
| `Team Topologies.epub` | EPUB | 29 个 spine item | 支撑 human/agent operating design 的认知负载与交互模式映射 |

### 交付密度最高的 PMP 来源

PMP 家族为显式交付与治理覆盖提供了主要证据：

| 来源 | 格式 | 覆盖 | 在这里的重要性 |
| --- | --- | --- | --- |
| `PMBOK® Guide 8th Edition .pdf` | PDF | 401 页 | 交付信号最高，适合支撑当前 PMI 生命周期重述 |
| `Process groups _ a practice guide.pdf` | PDF | 390 页 | 发起/规划/执行/监控/收尾叠加层的规范来源 |
| `过程组_实践指南(ProcessGroupsPracticeGuide) .pdf` | PDF | 409 页 | 过程组中文对照来源，治理计数也很强 |
| `The Standard for Program Management - Fifth Edition.epub` | EPUB | 16 个 spine item | 支撑项目集级排序与收益实现 |
| `项目管理知识体系 第七版 (PMBOK® 体系) 指南.pdf` | PDF | 369 页 | 支撑 PMBOK 7 绩效域的中文覆盖 |
| `Project Management Offices  a Practice Guide.epub` | EPUB | 42 个 spine item | PMO / 组织信号最强，适合治理 operating model 综合 |

## 仓库解释

1. 两份 Markdown 架构笔记提供明确目标清单，生命周期裁剪时应继续把它们当作计数权威来源。
2. Business Management 书籍提供有意控制范围、持续发现、架构边界、交付 appetite 与一人公司机制背后的经营原理。
3. PMP 标准提供执行纪律、治理词汇、tailoring 规则与收尾要求，但不替代产品判断或架构判断。
4. 仓库应继续用计数、标题与来源家族映射作为证据面，而不是把长段源文复制到跟踪文档中。
5. 未来生命周期文档如果提到架构清单、PMO 叠加层或 tailoring 逻辑，应先区分来源家族：精确计数看本地 Markdown，经营原则看 Business Management，交付治理看 PMP。

## 生命周期含义

对于 `D:/PythonProject_langgraph`，fresh-read 证据支持一种分层模型：

- **平台架构与 operating-system 真相** 来自两份本地架构笔记，以及 Business Management 中关于架构、发现、治理和有意保持小规模的来源。
- **执行纪律与交付控制** 来自 PMP 标准与 PMBOK 8 时代解读笔记。
- **仓库跟踪文档** 应继续只保留综合后的源依据，不保留原始提取文本。
