# Codex CLI 持久化团队平台建设生命周期

本文适用于在 `D:\PythonProject_langgraph` 中建设 Codex CLI 个人开发者生产级持久化团队平台；这是 Codex 编排源码仓库。本文不描述下游业务项目如何管理自己的产品工作。

## Scope

平台建设生命周期覆盖可复用的用户级和仓库级编排能力：

- `subagent` 是 Codex 原生专家委托层；它处理有边界的读取、设计、审查、实现和验证切片。
- `native_omx` 是 worker-centric durable backend lane；它只在计划冻结并且存在两个以上基本独立执行切片后使用。
- `langgraph` 是图式 checkpoint 和 approval-gate backend lane；它只在需要图阶段、checkpoint 恢复、interrupt gate 或 survivor queue 时使用。
- `OpenSpec` 是仓库治理工作流；它记录 durable proposal、design、tasks、stable specs 和 archive。
- `D:\PythonProject_General_2` 是本地项目模板目录；它初始化后续项目，但不把后续项目变成平台实现位置。


## PMI ?????

`docs_bilingual/product_lifecycle/pmi_project_management_reference_map.zh-CN.md` ? UTF-8 ?? PMI ???????? PMI ????????????????????? PMI ?????

????????? PMI ????

- PMBOK ? value ? principles ?? value delivery?tailoring depth?governance boundaries?success criteria ? quality gates?
- Process Groups ?? OpenSpec ? GitLab-first delivery gates??? proposal ????design ? tasks ??????checker-backed monitoring????? archive ????
- Agile guidance ??????MVP?????? hybrid work?????????

???????????????????? 0-8 ???????????????

## 0. 认知叙事层

问题：为什么个人开发者需要生产级持久化团队？

平台文件：

- `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md` 是未来 ASCII 白皮书；它应该解释为什么单次 chat session 不足以支撑生产工作。
- `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.zh-CN.md` 是未来 UTF-8 中文对照版；它为中文维护者承载同一论证。

平台输出：一份持久叙事，说明这是生产基础设施项目，而不是 prompt collection。

## 1. 商业层

问题：这个平台是否值得长期维护？

平台文件：

- `docs_bilingual/business/codex_cli_durable_team_brd.md` 是未来 ASCII 商业需求文档；它应该估算生产力提升、维护成本、模型成本和风险降低。
- `docs_bilingual/business/codex_cli_durable_team_brd.zh-CN.md` 是未来 UTF-8 中文对照版；它承载同一商业决策。

平台输出：决定该平台是否值得持续维护 release gates、templates 和本地 tooling。

## 2. 市场与用户层

问题：哪些开发者工作流需要该平台？

平台文件：

- `docs_bilingual/market/codex_cli_durable_team_mrd.md` 是未来 ASCII 市场需求文档；它应该描述个人开发者和小团队的用户分层、痛点和采用场景。
- `docs_bilingual/market/codex_cli_durable_team_mrd.zh-CN.md` 是未来 UTF-8 中文对照版；它承载同一市场需求。
- `docs_bilingual/references/codex_business_capability_mapping.md` 是 ASCII 抽象能力映射；它把具体 workload examples 映射到抽象 capability profiles。
- `docs_bilingual/references/codex_business_capability_mapping.zh-CN.md` 是 UTF-8 中文对照版；它承载同一映射。

平台输出：稳定的抽象 capability profiles，而不是一次性业务名称列表。

## 3. 战略与北极星层

问题：长期目标是什么，如何衡量进展？

平台文件：

- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` 是 ASCII 北极星 plan；它定义十层框架、release train 和长期 durable-team 目标。
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` 是 UTF-8 中文对照版，也是当前同一北极星 plan 的主要讨论面。

候选北极星指标：

- 冷启动接续成功率；它表示新 Codex 会话在最少重复用户解释下安全接续项目任务的比例。

输入指标：

- OpenSpec guard 通过率。
- merge request pipeline 通过率。
- context-retention reload 事件数。
- multi-session collision 事件数。
- rollback 成功率。
- 用户手动重复补充上下文次数。

平台输出：平台投入具有可衡量方向。

## 4. 产品层

问题：平台应该暴露哪些控制面？

平台文件：

- `docs_bilingual/product/codex_cli_durable_team_prd.md` 是未来 ASCII PRD；它应该定义用户可见命令、启动行为、角色路由、状态检查、发布门和模板更新流程。
- `docs_bilingual/product/codex_cli_durable_team_prd.zh-CN.md` 是未来 UTF-8 中文对照版；它承载同一 PRD。
- `AGENTS.md` 是项目级 Codex 指令面；它告诉 Codex 如何处理本仓库。
- `docs_bilingual/project_startup_summary.md` 是 ASCII 冷启动摘要；它告诉新会话如何恢复上下文。
- `docs_bilingual/project_startup_summary.zh-CN.md` 是 UTF-8 中文冷启动摘要对照版。

平台输出：显式的 operator workflows 和 acceptance criteria。

## 5. 技术层

问题：如何在不破坏原生 Codex 的前提下实现平台？

平台文件：

- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md` 是 ASCII MCP 范围策略；它决定哪些 MCP server 属于 Codex direct config、MCP Router 或都不属于。
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md` 是 UTF-8 中文 MCP 范围策略对照版。
- `docs_bilingual/governance/langgraph_user_level_runtime_policy.md` 是 ASCII LangGraph runtime 策略；它定义官方 LangGraph runtime 应放在哪里。
- `docs_bilingual/governance/langgraph_user_level_runtime_policy.zh-CN.md` 是 UTF-8 中文 LangGraph runtime 策略对照版。
- `tools/langgraph_durable_orchestrator/` 是 repo-local LangGraph 兼容源码目录；它是源代码，不是 durable state。
- `.omx/state/langgraph/` 是 repo-local LangGraph durable state 目录；它不得移动到用户级共享 runtime。

平台输出：技术契约和 checker-backed boundaries。

## 6. 执行层

问题：平台变更如何安全交付？

平台文件：

- `openspec/changes/<change-id>/proposal.md` 是 ASCII OpenSpec 提案；它解释为什么需要某个具体平台变更。
- `openspec/changes/<change-id>/design.md` 是 ASCII OpenSpec 设计；它解释该平台变更如何实现。
- `openspec/changes/<change-id>/tasks.md` 是 ASCII OpenSpec 任务清单；它跟踪该 change 的完成状态。
- `openspec/changes/<change-id>/*.zh-CN.md` 是同一 change artifacts 的 UTF-8 中文对照文件。
- `tools/run_openspec_guard.py` 是 OpenSpec guard 脚本；它验证官方 refresh、仓库规则和 clean-git 预期。

平台输出：带显式验证证据的小步 GitLab-first MR。

## 7. 增长与采用层

问题：平台如何扩展到多个项目，同时不共享 repo-local truth？

平台文件：

- `D:\PythonProject_General_2\START_HERE.cmd` 是 Windows 双击模板启动器；它初始化或检查本地项目。
- `D:\PythonProject_General_2\TEMPLATE_MANIFEST.md` 是模板清单；它解释哪些文件属于本地项目模板。
- `docs_bilingual/templates/template_update_policy.md` 是未来 ASCII 模板更新策略；它应解释已初始化项目如何接收后续模板更新。
- `docs_bilingual/templates/template_update_policy.zh-CN.md` 是未来 UTF-8 中文模板更新策略对照版。

平台输出：下游项目可以采用平台，但不会变成平台实现仓库。

## 8. 复盘与学习层

问题：哪些平台经验应该变成规则、checker 或模板？

平台文件：

- `docs_bilingual/memory/mainline_memory_summary.md` 是 ASCII 主线记忆摘要；它在重大变更后捕获 durable context。
- `docs_bilingual/memory/mainline_memory_summary.zh-CN.md` 是 UTF-8 中文记忆摘要对照版。
- `docs_bilingual/governance/` 是治理目录；它保存应该跨越单次对话长期有效的规则。
- `tools/check_*.py` 脚本是 checker 文件；它们在不只依赖 prompt 的情况下执行治理规则。

平台输出：重复失败被沉淀为脚本、policy、OpenSpec specs 或模板更新。

## Release Slicing Rule

一个平台 MR 通常只应该修改一个层级或一个控制面。好的例子包括：新增一份 lifecycle reference、新增一个 checker、归档一个 OpenSpec change、细化一个 release gate 或更新一条模板规则。
