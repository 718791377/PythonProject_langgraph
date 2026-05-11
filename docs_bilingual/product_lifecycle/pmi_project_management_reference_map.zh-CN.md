# PMI 项目管理参考映射

本文把 PMI 项目管理参考资料映射到本仓库的生命周期文档。本文不复制 PMI 书籍正文，只总结这些参考资料如何被裁剪到 Codex 平台治理和下游项目使用。

## Reference Boundary

- `PMP/` 是 PMI PDF 文件的本地私有参考目录；它被 Git 忽略，不能提交进仓库。
- `PMBOK Guide` 用作项目管理中的 value、principles、tailoring、quality 和 governance 参考。
- `Process Groups: A Practice Guide` 用作 delivery-gate 参考，覆盖 initiating、planning、executing、monitoring and controlling 和 closing。
- `Agile Practice Guide` 用作 adaptive delivery 参考，覆盖 uncertainty、MVP slices、feedback loops 和 hybrid work。

这些参考资料是叠加层。它们不替代白皮书、BRD、MRD、北极星 Plan、PRD、技术设计、implementation plans、OpenSpec 或仓库 checker。同一边界也适用于 `Business Management/` 源库：产品和管理来源用于启发生命周期裁剪，但仓库只记录综合后的 operating rules。

## 本地 PMP 来源覆盖

本次刷新只读取本地 `PMP/` 文件；不需要联网检索。仓库只记录以下覆盖摘要与治理映射综合。

| 本地参考资料 | 格式 | 覆盖量 | 主要治理用途 |
| --- | --- | ---: | --- |
| `PMBOK Guide 8th Edition .pdf` | PDF | 401 页 | 主要价值、绩效域、AI 时代、裁剪与治理叠加层 |
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

## 面向每一层的过程组式运行叠加层

当某个生命周期层会影响执行时，应采用相同的过程组纪律编写：

| 过程组 | 生命周期用途 | 期望证据 |
| --- | --- | --- |
| 启动 | 判断该层或该变更是否应该存在 | 目的、价值假设、授权、干系人、范围边界与初始风险 |
| 规划 | 判断如何完成该层或该变更 | 输入、裁剪后的治理深度、验收标准、风险应对、验证、发布、回滚、owner 映射与沟通 |
| 执行 | 产出该层交付物或交付增量 | 草稿、代码、测试、模板、文档、Agent 工作、评审意见与受控实现工件 |
| 监控与控制 | 在工作进行中检查并控制 | 指标检查、质量检查、问题日志、变更控制决策、本地 gate 证据、CI 证据与验收差异 |
| 收尾 | 完成、归档、学习或有意识停止 | 最终工件、OpenSpec 归档或项目收尾、稳定规格/文档同步、经验教训与下一轮输入 |


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
| Monitoring and controlling | 验证并控制变更 | `tools/run_openspec_guard.py` 是 OpenSpec guard 脚本；GitLab pipeline 是 review-time CI gate |
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
