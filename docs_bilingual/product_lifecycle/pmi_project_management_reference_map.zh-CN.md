# PMI 项目管理参考映射

本文把 PMI 项目管理参考资料映射到本仓库的生命周期文档。本文不复制 PMI 书籍正文，只总结这些参考资料如何被裁剪到 Codex 平台治理和下游项目使用。

## Reference Boundary

- `PMP/` 是 PMI PDF、EPUB 与 Markdown 笔记的本地私有参考目录；它被 Git 忽略，不能提交进仓库。
- `PMBOK Guide` 用作项目管理中的 value、principles、tailoring、quality 和 governance 参考。
- `Process Groups: A Practice Guide` 用作 delivery-gate 参考，覆盖 initiating、planning、executing、monitoring and controlling 和 closing。
- `Agile Practice Guide` 用作 adaptive delivery 参考，覆盖 uncertainty、MVP slices、feedback loops 和 hybrid work。

这些参考资料是叠加层。它们不替代白皮书、BRD、MRD、北极星 Plan、PRD、技术设计、implementation plans、OpenSpec 或仓库 checker。同一边界也适用于 `Business Management/` 源库：产品和管理来源用于启发生命周期裁剪，但仓库只记录综合后的 operating rules。

## 本地 PMP 来源覆盖

本次刷新只读取本地 `PMP/` 文件。fresh extraction evidence 于 `2026-06-18T18:37:58Z` 在 `.omx/state/langgraph/extraction/business_pmp_20260619/` 重新生成，并记录 23 个 PMP 家族来源：9 个 PDF / 3,035 页、2 个 EPUB / 58 个 spine item、12 个 Markdown 全文笔记，共 3,105 个 PMP 读取单元和 4,330,816 个抽取字符。仓库只记录以下覆盖摘要与治理映射综合。

| 本地参考资料 | 格式 | 覆盖量 | 主要治理用途 |
| --- | --- | ---: | --- |
| `PMBOK® Guide 8th Edition .pdf` | PDF | 401 页 | 主要价值、绩效域、AI 时代、裁剪与治理叠加层 |
| PMBOK 第 7 版中文 PDF | PDF | 369 页 | 原则、价值交付、系统思维、裁剪与绩效域 |
| PMBOK 第 6 版中文 PDF | PDF | 812 页并复核低文本页 | 输入 / 工具与技术 / 输出词汇与知识领域补充 |
| `Process groups _ a practice guide.pdf` | PDF | 390 页 | 启动、规划、执行、监控与控制、收尾交付门模型 |
| 中文 `ProcessGroupsPracticeGuide` PDF | PDF | 409 页并复核低文本页 | 过程组交付门中文伴随来源 |
| `The Agile practice guide.pdf` | PDF | 188 页 | 自适应、MVP、反馈循环与混合交付指导 |
| 中文敏捷实践指南 PDF | PDF | 184 页并复核低文本页 | 自适应与混合交付中文伴随来源 |
| `The Standard for Program Management - Fifth Edition.epub` | EPUB | 16 个 spine item | 多个相关倡议的项目集级对齐 |
| `The Standard for Portfolio Management-Fourth Edition.pdf` | PDF | 140 页 | 组合选择、优先级、容量与价值平衡叠加层 |
| 中文项目组合管理标准 PDF | PDF | 142 页并复核低文本页 | 项目组合治理中文伴随来源 |
| `Project Management Offices a Practice Guide.epub` | EPUB | 42 个 spine item | PMO 职能、治理服务、赋能与监督模式 |
| `PMP_MD/*.md` | Markdown | 12 篇本地文章 | PMBOK 8 与 AI 时代项目管理解读笔记 |

## PMI 官方 Web 新鲜度复核

本次刷新也在 2026-06-18 复核了 PMI 公开 standards 页面，避免把私有本地目录当成唯一新鲜度信号。本地抽取仍是内容证据边界；公开复核只记录当前 catalog metadata。

| PMI 公开来源 | 2026-06-18 复核到的官方目录状态 | 仓库决策 |
| --- | --- | --- |
| <https://www.pmi.org/standards/pmbok> | `PMBOK Guide` 已列为第 8 版，408 页，发布日期为 2025 年 11 月，并有 2025 年 12 月 22 日发布的第二次印刷勘误。 | 把 PMBOK 第 8 版作为当前项目管理主叠加层；PMBOK 第 7 版和第 6 版只作为连续性与 I/T/O 补充。 |
| <https://www.pmi.org/standards/process-groups> | `Process Groups: A Practice Guide` 列为 370 页，发布日期为 2022 年 11 月，并描述五个过程组以及带输入、工具与技术、输出的 49 个过程。 | 用作生命周期层级和交付门的面向执行过程组语法。 |
| <https://www.pmi.org/standards/agile> | `Agile Practice Guide` 列为 210 页，发布日期为 2017 年 10 月，并有第三次、第四次印刷勘误。 | 在更新的官方敏捷指南被加入本地并重新抽取前，保持为 agile/adaptive 补充。 |
| <https://www.pmi.org/standards/program-management-fifth-edition> | `The Standard for Program Management - Fifth Edition` 列为 PMI Standard，247 页，发布日期为 2024 年 3 月。 | 将本地第 5 版 EPUB 作为当前项目集级协调来源。 |
| <https://www.pmi.org/standards/for-portfolio-management> | `The Standard for Portfolio Management - Fourth Edition` 列为 PMI Standard，189 页，发布日期为 2017 年 11 月。 | 保持项目组合治理作为优先级、容量与价值平衡叠加层。 |
| <https://www.pmi.org/standards/pmo> | `Project Management Offices: A Practice Guide` 列为 PMI Practice Guide，331 页，发布日期为 2025 年 2 月。 | 用作 PMO 治理服务与赋能叠加层，尤其适用于多个倡议需要共享标准或监督时。 |

官方目录页数可能不同于本地抽取页数，因为本地 source package、front matter、印刷/导出格式或 EPUB spine 边界不同。出现差异时，用本地抽取证明本地来源已读取，用 PMI 公开页面记录当前 catalog metadata。

## 按文档类型裁剪 PMI 叠加层矩阵

不同文档类型应使用不同深度的 PMI 叠加层。不要在每份文档里重复所有 PMI 版本；只选择当前决策所需的最小权威。

| 仓库文档或层级 | 主要 PMI 叠加层 | 旧版或伴随来源用途 | 停止条件 |
| --- | --- | --- | --- |
| 白皮书 | PMBOK 第 8 版的价值、治理、裁剪与 AI 时代 framing；Process Groups 只作为高层交付纪律 | 除非平台边界依赖，不在叙事中展开 PMBOK 第 6 版 I/T/O 细节 | 到战略 framing 为止，并链接 lifecycle/PMI maps 承接执行细节 |
| 研究稿 | runtime/governance evidence 优先；只有在把能力发现翻译成受治理执行时才使用 PMI | PMBOK 第 6 版可澄清 I/T/O 词汇；PMBOK 第 7 版可澄清原则；必须标注官方来源与仓库推导的区别 | 当问题变成产品叙事或生命周期数量权威时停止 |
| 生命周期层级文档 | Process Groups 作为执行语法；PMBOK 第 8 版作为价值/裁剪叠加层 | PMBOK 第 6 版支持详细输入、工具与技术、输出；译本只支持术语澄清 | 一旦该层已有清晰 I/T/O 与控制门，就停止展开旧版 |
| 北极星计划 | PMBOK 第 8 版和第 7 版的价值/绩效思维；项目组合只用于容量与价值取舍 | Process Groups 只作为运营节奏和证据门 | 在指标战略变成完整项目管理手册前停止 |
| 裁剪规则 | PMBOK 第 8 版裁剪、Agile 自适应/混合指导、Process Groups gates | PMBOK 第 6 版 I/T/O 语法与旧版用于澄清执行措辞 | 当裁剪结果和升级触发器已经明确时停止 |
| OpenSpec / implementation plans | Process Groups + 仓库 local-main-first gates | PMBOK 第 6 版 I/T/O 措辞可用于 plan sections；只有协调范围需要时才加入 PMO/项目集/项目组合 | 当 proposal、design、tasks、verification、rollback 与 archive evidence 足够时停止 |
| 下游一人公司文档 | PMBOK 第 8 版价值/裁剪与 Agile feedback loops | 只有在多倡议、治理服务或容量取舍存在时才使用 PMO/项目集/项目组合叠加 | 在把 enterprise governance 导入单一低风险 owner workflow 前停止 |

## 旧版展开规则

旧版 PMI 与伴随译本只有在带来具体执行收益时才展开：I/T/O 词汇、知识领域连续性、翻译澄清或历史比较。当 PMBOK 第 8 版已经覆盖治理点，并且该文档不是在定义执行语法时，应引用 PMBOK 第 8 版和当前 lifecycle 权威，而不是并列铺开 PMBOK 第 6/7/8 版。

## Agile、项目集、项目组合与 PMO 的进入/退出规则

- Agile guidance 在存在不确定性、反馈循环、MVP 切片或混合规划时进入；它不覆盖 PMBOK 第 8 版作为主要治理叠加层的地位。
- 项目集治理在多个相关倡议需要协调收益、依赖或 roadmap alignment 时进入。
- 项目组合治理在多个竞争倡议需要价值、容量、风险或投资取舍时进入。
- PMO 实践在需要共享治理服务、标准、赋能功能或监督模式时进入。
- 单一仓库、单一维护者、单一发布切片和低风险本地 workflow 默认不导入项目集、项目组合或 PMO ceremony。
- 当协调问题已经关闭，剩余工作变成有清晰 owner 和 rollback evidence 的有界项目、阶段或模块时，退出较重叠加层。

## 最新优先权威规则

本仓库使用本地 `PMP/` 来源集中“最新且可读的官方/准官方资料”作为各知识家族的主要依据。旧版本与伴随译本只用于解释词汇、历史连续性、翻译和过程细节。

| 知识家族 | 本次刷新的主要依据 | 补充或历史用途 |
| --- | --- | --- |
| 项目管理知识体系 | `PMBOK® Guide 8th Edition .pdf` | PMBOK 第7版补充原则与价值交付连续性；PMBOK 第6版补充过程词汇与 I/T/O 结构 |
| 过程组执行语法 | `Process groups _ a practice guide.pdf` | 中文 ProcessGroups PDF 仅在抽取文本足够可读时作为术语伴随参考 |
| 敏捷与混合交付 | 本地英文 `The Agile practice guide.pdf` | 中文敏捷 PDF 因 fresh extraction 显示低文本极高，只作为伴随参考；只有把更新官方指南加入 `PMP/` 并重新抽取后，才能更新本规则 |
| 项目集治理 | `The Standard for Program Management - Fifth Edition.epub` | 早期项目集概念若后续加入，只作为历史连续性补充 |
| 项目组合治理 | 本地 `The Standard for Portfolio Management-Fourth Edition.pdf` | 中文项目组合 PDF 因 fresh extraction 显示低文本极高，只作为伴随参考 |
| PMO 治理服务 | `Project Management Offices a Practice Guide.epub` | 早期 PMO 实践资料若后续加入，只作为补充 |

低文本伴随 PDF 不作为本仓库主要权威来源。当公开 PMI 目录或本地来源集变化时，应先把新来源加入 `PMP/`，重新执行 PDF 按页、EPUB 按 spine item、Markdown 全文抽取，再更新本映射和生命周期规则。

## 面向每一层的过程组式运行叠加层

当某个生命周期层会影响执行时，应采用相同的过程组纪律编写：

| 过程组 | 输入 | 工具与技术 | 输出 |
| --- | --- | --- | --- |
| 启动 | 目的、价值假设、授权、干系人信号、范围边界、初始风险 | 类 charter framing、干系人识别、问题 framing、价值理由检查 | 该层或变更是否存在的决策、owner、范围边界、初始风险日志 |
| 规划 | 已批准目的、上游层输出、约束、裁剪后的治理深度、风险日志 | 分解、验收标准、验证设计、发布/回滚规划、owner 映射、沟通规划 | 工作计划、I/T/O checklist、验收标准、验证路径、发布/回滚边界、沟通计划 |
| 执行 | 已批准计划、来源证据、模板、worktree/ownership 状态、Agent 边界 | 起草、实现、评审、测试、受控 Agent 委派、文档更新 | 草稿、代码、测试、模板、文档、Agent 工作产物、评审意见、受控实现工件 |
| 监控与控制 | 活跃工作产物、指标、问题、评审反馈、本地 gate 输出、CI 证据 | 质量检查、变更控制、偏差复核、风险响应、diff review、gate 重跑 | 问题日志、变更决策、指标检查、本地 gate 证据、CI 证据、验收差异、回滚准备 |
| 收尾 | 已验收工作、最终证据、归档候选、经验教训、剩余风险 | 收尾复核、归档/同步、发布说明更新、复盘、下一周期分流 | 最终工件、OpenSpec 归档或项目收尾、稳定规格/文档同步、经验教训、下一周期输入 |

## PMBOK 第8版主要叠加层

本仓库将 PMBOK 第8版作为主要项目管理叠加层。主要叠加层是用于 framing value delivery、project-canvas alignment、performance domains、AI-era project governance、hybrid delivery 和 tailoring 的参考。它不替代仓库自己的文档栈。

补充叠加层的职责更窄：

- `PMBOK 第6版` 是过程和知识领域补充；它帮助把 lifecycle layers 转成 inputs、tools and techniques、outputs 和 control gates。
- `Process Groups: A Practice Guide` 是 delivery-gate supplement；它把 initiating、planning、executing、monitoring and controlling、closing 映射到 OpenSpec 和 local-main-first work。
- `PMBOK 第7版` 是 principles 和 value-delivery supplement；它桥接 principles、performance domains、system thinking 和 tailoring。
- `Agile Practice Guide` 是 adaptive 和 hybrid delivery supplement；它指导 MVP slices、feedback loops、iteration 和 reversible releases。

仓库只使用这些来源的结构，不复制正文。本地读取审计可以记录哪些本地文件可读，但 lifecycle documents 只写 repository-specific mappings。

## Relationship To The 0-11 / 12 层生命周期

| 0-11 层级 | 产品/商业目的 | PMI 叠加层 |
| --- | --- | --- |
| 0 认知层 | 解释方向为什么存在 | PMBOK 价值导向帮助叙事连接 outcome |
| 1 商业层 | 判断是否值得做 | 成功标准和收益思维帮助定义价值 |
| 2 市场层 | 识别用户和需求 | Agile discovery 和 feedback loops 帮助降低不确定性 |
| 3 战略层 | 定义如何获胜以及拒绝什么 | tailoring 帮助按风险选择治理深度 |
| 4 指标层 | 定义证据和决策阈值 | measurement 和 performance-domain 思维让进展可检查 |
| 5 产品层 | 定义产品范围和行为 | Agile lifecycle selection 帮助决定预测式、适应式或混合式规划 |
| 6 技术层 | 定义实现架构 | quality、risk、procurement 和 stakeholder constraints 支撑技术门禁 |
| 7 组织层 | 定义 owner、角色和批准 | stakeholder、resource 和 governance domains 澄清责任 |
| 8 执行层 | 交付工作 | Process Groups 直接映射到 OpenSpec 和 local-main-first delivery |
| 9 增长层 | 扩大采用和有用性 | Agile inspection and adaptation 支持迭代采用 |
| 10 运营层 | 保持已发布工作可支持 | quality、risk、issue 和 change-control practices 支持运行期运营 |
| 11 复盘层 | 学习和改进 | process closing 和 lessons learned 变成 archive 与治理更新 |

## 项目画布与绩效域映射

`project_canvas.md` 是轻量项目画布文件；它在团队展开完整 lifecycle stack 之前，对齐 purpose、value、stakeholders、boundaries、risks、delivery style 和 outcome checks。

对本仓库来说，PMBOK 第8版的 performance-domain thinking 映射到以下治理关注点：

| 绩效关注点 | 仓库映射 |
| --- | --- |
| Governance | 用户权威、OpenSpec changes、local-main-first review、release consent 和 checker-backed safety rules |
| Scope | 平台仓库边界、下游项目边界和 non-goals |
| Schedule | Release slices、current mainline、phase gates 和 closeout timing |
| Finance | GitLab runner minutes、provider pacing budget、本地模型成本、operator attention 和 maintenance time |
| Stakeholders | user/operator、main Codex leader session、subagents、durable workers、downstream project maintainers 和 reviewers |
| Resources | worktrees、wrappers、user-level helpers、本地模型、MCP tools 和 repo-local state directories |
| Risk | cross-session collision、stale main、state leakage、lane mis-selection、hidden automation 和 rollback failure |

## Process Groups To OpenSpec And Local-Main-First Gates

| PMI 过程组 | Codex 平台交付门 | 仓库文件和动作 |
| --- | --- | --- |
| Initiating | 判断是否打开 change | `openspec/changes/<change-id>/proposal.md` 是 OpenSpec proposal，用来说明为什么需要某个 change |
| Planning | 冻结设计和执行范围 | `openspec/changes/<change-id>/design.md` 是 OpenSpec design；`tasks.md` 是跟踪执行的任务清单 |
| Executing | 实施已规划工作 | 按已接受 tasks 修改 source、documentation、templates 或 checker files |
| Monitoring and controlling | 验证并控制变更 | `tools/run_openspec_guard.py` 是 OpenSpec guard 脚本；`tools/ci/local_gate.ps1` 和 `tools/ci/local_mr_review.ps1` 是本地 review gates；使用 GitLab pipeline 时，它是后续 clean-environment confirmation |
| Closing | 归档并学习 | `openspec archive` 是 archive command，用来把完成的 changes 移入 `openspec/changes/archive/` 并同步 stable specs |

## Predictive, Adaptive, And Hybrid Use

适合 predictive-style gate 的情况：

- Requirements 清晰。
- 风险足够高，需要显式 release 或 rollback evidence。
- change 修改 governance、templates、runtime entrypoints 或 checker behavior。

适合 adaptive-style slice 的情况：

- Requirements 不清楚。
- 锁定 design 前需要 user 或 operator feedback。
- 最安全的下一步是 spike、MVP 或小型 documentation experiment。

适合 hybrid approach 的情况：

- 仍需要 discovery，但交付仍必须通过 OpenSpec、checker 和 local-main-first gates。
- 先做小型 spike，然后再冻结 predictive delivery plan。

使用 `lifecycle_tailoring_rules.zh-CN.md` 记录 predictive、adaptive 或 hybrid 工作究竟采用完整架构、整个项目轻量、阶段局部轻量，还是模块级轻量。裁剪决策本身应在执行前写明输入、工具与技术、输出。

当多个相关倡议、共享容量、跨项目价值取舍或治理服务出现时，项目集、项目组合和 PMO 式 oversight 开始相关。此时不要把整个项目判定为轻量；应保持项目集或组合级决策面显式存在，并只在风险允许时对有边界模块或阶段做轻量化。

## Codex Execution Mode Mapping

| 工作条件 | 推荐 Codex 模式 | 原因 |
| --- | --- | --- |
| 单个清晰切片 | 主会话或一个原生 `subagent` | 保持执行轻量 |
| 有边界的多面研究 | 先并行多个 analyst `subagent` 调用 | 在升级到 architecture 或 planning 前保持研究同质化 |
| 已冻结计划且有两个以上独立切片 | `native_omx` durable team | 只有满足阈值时才使用 worker-centric durable execution |
| checkpoint、approval gate、survivor queue 或 graph phase | `langgraph` backend lane | 只有任务需要图式恢复时才使用 graph-shaped recovery |

## Minimal Project Governance Files

下游项目默认不需要完整平台栈。只有当风险或复杂度需要时，才增加项目管理文件：

- `project_charter.md` 是项目章程；它说明目标、范围、成功标准和关键干系人。
- `risk_register.md` 是风险登记册；它跟踪风险、影响、概率、应对方式和负责人。
- `issue_log.md` 是问题日志；它记录 active blockers 和 resolution status。
- `release_plan.md` 是发布计划；它定义 rollout、release gates 和沟通方式。
- `rollback_plan.md` 是回滚计划；它定义如何回到已知安全状态。
- `lessons_learned.md` 是经验教训文档；它记录交付或事故后的可复用经验。

小型本地项目可以合并这些文件，但高风险项目应该显式保留它们。

## Platform Rule

Codex 平台仓库可以定义共享 lifecycle references、templates、checkers 和 role policies。它不得成为下游项目的 repo-local durable truth。下游项目拥有自己的 OpenSpec tree、durable state、release state 和 lessons learned。

## 一人公司 PMI 运行叠加层

对于下游一人公司运营系统，PMI 用于决定执行纪律，而不是引入企业级仪式。

| PMI 来源家族 | 进入触发器 | 一人公司用法 | 退出规则 |
| --- | --- | --- | --- |
| PMBOK 第 8 版 | 任何真实项目、offer、release、受治理 Agent 工作流或业务运行循环需要价值与裁剪纪律 | 用价值交付、project canvas、绩效关注点、AI 时代工作、混合交付和裁剪作为主叠加层 | 当循环私有、可逆、低风险且无外部承诺时，退出到轻量 note |
| Process Groups | 任何执行流产生交付物、承诺、验证、发布、支持或收尾证据 | 按启动 / 规划 / 执行 / 监控与控制 / 收尾写输入 / 工具与技术 / 输出 | 受影响层已有 owner、验证、风险、回滚/停止和学习证据时停止扩展 |
| Agile Practice Guide | discovery、原型、访谈、MVP、渠道测试或不确定产品/市场工作 | 在冻结预测式交付计划前使用适应式反馈循环 | 触达客户、收入、信任、合规或发布影响前冻结更强控制 |
| 项目集标准 | 多个相关 initiative 需要协同收益、依赖、顺序或能力增量 | 只有相关 initiative 必须一起管理时，才把 solo operator 路线图视为项目集 | 当工作回到单一有边界项目或模块时退出 |
| 项目组合标准 | 竞争性投入需要在价值、容量、runway、风险或业务线之间取舍 | 用项目组合思维做优先级和 stop/pivot 决策 | 当只剩一个有清晰 owner 和预算的 active bet 时退出 |
| PMO 实践指南 | 标准、评审、模板、节奏、赋能或监督成为重复性服务 | 使用 solo PMO / chief-of-staff 服务层，而不是新增部门 | 当一次性循环不再需要共享治理服务时退出 |

运行规则是先局部轻量。扩展真正承载风险的层级、阶段、模块或 release slice；只有耦合变成系统性时，才扩展整个项目。
