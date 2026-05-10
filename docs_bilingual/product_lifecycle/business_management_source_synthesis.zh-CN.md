# Business Management 源库综合

本文总结本地忽略目录 `D:/PythonProject_langgraph/Business Management` 对本仓库 `docs_bilingual/product_lifecycle/` 的生命周期启发。本文是综合层，不替代原书，也不复制原书正文。

## 读取覆盖

写入本综合前，已按页级或 EPUB spine item 级读取源目录。

- PDF 文件使用 PyMuPDF 逐页遍历。记录页数和低文本页，因为封面、空白页、扫描图和图片页可能没有足够可抽取文字。
- EPUB 文件按 OPF spine 顺序读取，每个 HTML/XHTML item 均抽取文字。
- Markdown 架构笔记按 UTF-8 文本读取。
- 临时抽取产物保存在 `.tmp/` 下，并由 Git 忽略。

| 源文件 | 格式 | 覆盖 | 生命周期作用 |
| --- | --- | --- | --- |
| `Accelerate.pdf` | PDF | 315 页 | 交付绩效、架构能力、管理能力和基于证据的软件改进 |
| `Clean Architecture.pdf` | PDF | 429 页 | 技术边界、依赖方向、组件原则和架构价值 |
| `Clean Architecture - 架构整洁之道.pdf` | PDF | 380 页 | Clean Architecture 概念的中文对照 |
| `Company of One.epub` | EPUB | 44 个 spine item | 有意保持小规模、可扩展个人系统、信任、小步发布和深关系 |
| `Company of One.pdf` | PDF | 209 页 | 一人公司 operating system 主题的 PDF 对照 |
| `Continuous Discovery Habits.pdf` | PDF | 197 页 | 持续产品发现、访谈节奏、机会映射和假设测试 |
| `Crossing the Chasm, 3rd Edition.pdf` | PDF | 288 页 | 滩头市场、whole product 和采用分层风险 |
| `Deploy Empathy.epub` | EPUB | 79 个 spine item | 客户访谈、研究循环、过去行为问题和反馈分析 |
| `Designing Data-Intensive Applications.pdf` | PDF | 613 页 | 可靠性、可扩展性、可维护性、数据模型、存储、分布式数据和派生数据架构 |
| `Escaping the build trap.pdf` | PDF | 199 页 | outcome-focused 产品管理、产品战略、product kata 和避免 output obsession |
| `Good strategy, bad strategy.pdf` | PDF | 144 页 | 诊断、指导方针、连贯行动、杠杆和近端目标 |
| `High Output Management.pdf` | PDF | 239 页 | 管理杠杆、经营节奏、会议、one-on-one 和产出思维 |
| `INSPIRED.pdf` | PDF | 370 页 | 产品发现、授权产品团队、value/usability/feasibility/viability 和产品风险 |
| `Lean Analytics.pdf` | PDF | 439 页 | One Metric That Matters、阶段指标、阈值线和分析纪律 |
| `Master60- 亞馬遜的逆向工法.pdf` | PDF | 38 页 | Working Backwards 摘要、PR/FAQ、客户倒推机制和叙事决策 |
| `Measure What Matters.pdf` | PDF | 306 页 | OKR、聚焦、对齐、跟踪、拉伸和 CFR 式运营节奏 |
| `Obviously Awesome.pdf` | PDF | 140 页 | 定位、竞争替代、价值主题和市场框架选择 |
| `Product Operations.epub` | EPUB | 65 个 spine item | 产品数据、客户和市场洞察、operating model、流程和产品运营规模化 |
| `Product Operations.pdf` | PDF | 346 页 | Product Operations 的 PDF 对照 |
| `Scaling People.epub` | EPUB | 24 个 spine item | 运营原则、目标/资源规划、团队发展、反馈机制和 metronome |
| `Secure by Design.epub` | EPUB | 31 个 spine item | 安全作为设计关注点、domain primitives、不变量、安全流水线和代码审查 |
| `Secure by Design.pdf` | PDF | 400 页 | Secure by Design 的 PDF 对照 |
| `Shape Up.pdf` | PDF | 133 页 | appetite、shaping、betting、scope map、circuit breaker 和交付风险控制 |
| `Team Topologies.epub` | EPUB | 29 个 spine item | cognitive load、team API、平台边界、交互模式和 Conway-aware 设计 |
| `The E-Myth Revisited.pdf` | PDF | 286 页 | business-as-system、角色分离、流程原型和 SOP 纪律 |
| `The Lean Startup.pdf` | PDF | 150 页 | build-measure-learn、MVP、validated learning、innovation accounting 和 pivot/persevere 决策 |
| `The Staff Engineer's Path.pdf` | PDF | 359 页 | 技术领导力、范围塑形、影响力、执行战略和高级工程判断 |
| `Traction.epub` | EPUB | 33 个 spine item | 渠道测试、traction goal、critical path 和增长渠道选择 |
| `Working Backwards.pdf` | PDF | 273 页 | PR/FAQ、叙事规划、机制、single-threaded ownership 和指标纪律 |
| `架构 1：Codex CLI 个人开发者生产级持久化团队.md` | Markdown | 167 行 | Codex 持久化团队架构源笔记 |
| `架构 2：个人级生产级一人公司运营.md` | Markdown | 448 行 | 个人级一人公司 operating system 源笔记 |

## 跨来源运营原则

1. **先诊断，后行动。** 战略工作必须先命名真实约束、目标客户、采用障碍和指导方针，再变成路线图或任务清单。
2. **结果优先于产出。** roadmap、OpenSpec change 和 implementation plan 必须连接到用户价值、商业价值、运营价值、信任价值或学习价值。
3. **一人系统要有意保持小。** solo operator 应优先使用轻量机制、稳定节奏、可复用模板和明确非目标，而不是组织表演。
4. **让 discovery 持续发生。** 客户访谈、支持信号、使用数据和市场证据应在大规模 build commitment 前进入产品决策。
5. **执行前先塑形。** 变更在扩大实施前，需要 appetite、边界、风险、验证证据和 circuit-breaker 规则。
6. **把架构当作长期可选性。** 边界、依赖方向、数据契约、安全不变量和 team/agent API 保护未来变更速度。
7. **衡量系统，而不是 vanity。** 使用能改变决策的 North Star 输入指标、OKR、阶段指标、交付指标和采用指标。
8. **为采用和信任而设计。** 定位、滩头市场、whole-product 支持、文档和支持循环都是产品生命周期的一部分，不是事后补丁。
9. **闭环。** retrospective、postmortem、lessons learned 和 upstream feedback 必须更新模板、checker、文档或未来战略。

## 0-8 生命周期映射

| 层级 | 源库强调点 | 仓库规则 |
| --- | --- | --- |
| 0 认知叙事 | 一人公司目的、平台叙事、类别框架和客户倒推故事 | 先解释方向为什么存在，再定义功能或团队 |
| 1 商业 | 单位经济、协作成本、有意保持小、风险降低和运营杠杆 | 判断维护成本和机会成本是否值得 |
| 2 市场与用户 | 访谈、持续发现、采用分层、定位和客户证据 | 先识别目标用户和滩头用例，再扩大范围 |
| 3 战略与北极星 | 诊断、指导方针、OKR、OMTM、产品战略和 critical path | 选择狭窄获胜条件，以及会改变决策的指标 |
| 4 产品 | PR/FAQ、product kata、机会映射、产品运营、MVP 和 usability/value/viability/feasibility 风险 | 在构建前定义用户可见行为、非目标和验收证据 |
| 5 技术 | 清晰边界、数据系统质量、安全不变量、team API、staff engineer 判断和交付能力 | 记录架构边界、数据契约、信任边界和回滚路径 |
| 6 执行 | shaping、appetite、betting、implementation slices、local-main-first gates 和交付指标 | 用小而可检查的切片执行，并保留验证、回滚和 circuit-breaker 证据 |
| 7 增长与采用 | traction channel tests、跨越鸿沟、定位、文档、信任和支持循环 | 把采用、onboarding、文档和支持纳入 release plan |
| 8 复盘与学习 | postmortem、SOP、运营节奏、产品运营学习和模板/checker 更新 | 把重复经验转化为持久文档、checker、模板或 OpenSpec spec |

## Codex 平台解释

对 `D:/PythonProject_langgraph` 来说，源库强化以下平台规则：

- 当前主 Codex 会话继续承担 accountable leader 职责；agents 和 durable lanes 是机制，不是隐藏管理权威。
- `native_omx` 和 `langgraph` 应按问题形状选择，而不是按新奇程度选择。只有当 durable execution、graph checkpoint 或 approval gate 产生可衡量价值时才使用。
- worktree isolation、local-main-first publication、OpenSpec archive 和 checker-backed safety rules 是一人平台团队的 operating-system 机制。
- product lifecycle docs 应指导决策，而不是制造 paperwork。最小充分文档集由不确定性、风险、影响和可逆性决定。
- 源库经验只有被翻译成仓库特定 policy、template、checker 或 OpenSpec spec 语言后，才成为平台事实。

## 下游项目解释

对后续消费平台的项目来说：

- 平台提供可复用机制；下游项目拥有自己的商业模型、客户证据、产品指标、架构决策、发布状态和学习循环。
- 下游项目可以用本综合判断需要哪些生命周期文档，但不能复制平台事实或 durable state。
- 如果下游经验足够通用，先记录为 upstream feedback，再通过平台 OpenSpec change 提升。
