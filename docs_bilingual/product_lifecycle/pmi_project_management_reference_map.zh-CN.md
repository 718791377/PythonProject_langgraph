# PMI 项目管理参考映射

本文把 PMI 项目管理参考资料映射到本仓库的生命周期文档。本文不复制 PMI 书籍正文，只总结这些参考资料如何被裁剪到 Codex 平台治理和下游项目使用。

## Reference Boundary

- `PMP/` 是 PMI PDF 文件的本地私有参考目录；它被 Git 忽略，不能提交进仓库。
- `PMBOK Guide` 用作项目管理中的 value、principles、tailoring、quality 和 governance 参考。
- `Process Groups: A Practice Guide` 用作 delivery-gate 参考，覆盖 initiating、planning、executing、monitoring and controlling 和 closing。
- `Agile Practice Guide` 用作 adaptive delivery 参考，覆盖 uncertainty、MVP slices、feedback loops 和 hybrid work。

这些参考资料是叠加层。它们不替代白皮书、BRD、MRD、北极星 Plan、PRD、技术设计、implementation plans、OpenSpec 或仓库 checker。

## Relationship To The 0-8 Lifecycle

| 0-8 层级 | 产品/商业目的 | PMI 叠加层 |
| --- | --- | --- |
| 0 认知叙事 | 解释方向为什么存在 | PMBOK 的 value orientation 帮助叙事绑定 outcomes |
| 1 商业 | 判断是否值得做 | PMBOK 的 success criteria 和 benefits thinking 帮助定义价值 |
| 2 市场 | 识别用户和需求 | Agile discovery 和 feedback loops 帮助降低不确定性 |
| 3 战略 | 定义北极星和杠杆 | PMBOK tailoring 帮助按风险选择治理深度 |
| 4 产品 | 定义产品范围和行为 | Agile lifecycle selection 帮助选择 predictive、adaptive 或 hybrid planning |
| 5 技术 | 定义实现架构 | PMBOK quality、risk 和 procurement 思想用于技术门禁 |
| 6 执行 | 交付工作 | Process Groups 直接映射 OpenSpec 和 GitLab-first delivery |
| 7 增长 | 扩大采用和效用 | Agile inspection and adaptation 支持迭代采用 |
| 8 复盘 | 学习并改进 | process closing 和 lessons learned 变成 archive 和 governance updates |

## Process Groups To OpenSpec And GitLab Gates

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

- 仍需要 discovery，但交付仍必须通过 OpenSpec、checker 和 GitLab gates。
- 先做小型 spike，然后再冻结 predictive delivery plan。

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
