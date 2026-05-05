# 后续项目消费平台能力生命周期

本文适用于后续使用 Codex CLI durable-team 平台的项目。下游项目可以使用共享用户级 runtime、templates、subagent profiles、OpenSpec practices 和 checkers，但必须拥有自己的 project truth。

## Non-Negotiable Boundary

下游项目不得把 `D:\PythonProject_langgraph\.omx/state/` 当成自己的 durable truth。该路径是平台仓库状态目录。每个下游项目都必须在自己的仓库内拥有自己的 `.omx/state/` 目录。

## 0. 认知叙事层

问题：这个下游项目为什么存在？

推荐文件：

- `README.md` 是项目总览；它解释这个项目是什么以及如何开始。
- `docs_bilingual/project_startup_summary.md` 是 ASCII 冷启动摘要；它帮助新的 Codex 会话理解项目。
- `docs_bilingual/project_startup_summary.zh-CN.md` 是同一启动摘要的 UTF-8 中文对照版。

小项目规则：除非项目需要外部对齐、融资、公开解释或长期战略叙事，否则单独白皮书是可选的。

## 1. 商业层

问题：这个下游项目是否值得做？

推荐文件：

- `docs_bilingual/business/brd.md` 是项目 BRD；它解释该项目的商业价值、成本、用户价值和回报预期。
- `docs_bilingual/business/brd.zh-CN.md` 是项目 BRD 的 UTF-8 中文对照版。

小项目规则：如果没有商业决策，可以在 `README.md` 中写简短价值说明。

## 2. 市场与用户层

问题：谁需要这个项目，在哪些场景需要？

推荐文件：

- `docs_bilingual/market/mrd.md` 是项目 MRD；它解释目标用户、使用场景、痛点和替代方案。
- `docs_bilingual/market/mrd.zh-CN.md` 是项目 MRD 的 UTF-8 中文对照版。
- `docs_bilingual/user_research/` 是用户研究目录；它可以保存访谈、观察和反馈证据。

小项目规则：如果用户只有仓库所有者自己，一份简短场景列表可以替代完整 MRD。

## 3. 战略与北极星层

问题：这个项目的成功意味着什么？

推荐文件：

- `docs_bilingual/north_star_plan.md` 是项目北极星 Plan；它定义该项目的主成功指标、输入指标和杠杆。
- `docs_bilingual/north_star_plan.zh-CN.md` 是同一计划的 UTF-8 中文对照版。

小项目规则：项目可以使用一页北极星说明替代完整战略计划。

## 4. 产品层

问题：这个项目应该做什么？

推荐文件：

- `docs_bilingual/prd.md` 是项目 PRD；它定义用户故事、功能、优先级、流程和验收标准。
- `docs_bilingual/prd.zh-CN.md` 是项目 PRD 的 UTF-8 中文对照版。
- `docs_bilingual/user_journey.md` 是用户旅程；它展示用户端到端路径。
- `docs_bilingual/user_journey.zh-CN.md` 是用户旅程的 UTF-8 中文对照版。

小项目规则：简单开发者工具可以把产品范围直接写进 OpenSpec proposal。

## 5. 技术层

问题：这个下游项目如何实现自己的系统？

推荐文件：

- `docs_bilingual/technical/trd.md` 是项目技术设计；它解释技术选择、架构和权衡。
- `docs_bilingual/technical/trd.zh-CN.md` 是技术设计的 UTF-8 中文对照版。
- `docs_bilingual/technical/api_spec.md` 是项目 API 规格；当存在 API 时，它定义接口输入、输出、错误和权限。
- `docs_bilingual/technical/api_spec.zh-CN.md` 是 API 规格的 UTF-8 中文对照版。
- `src/` 是项目源码目录；它包含该项目拥有的业务或应用代码。
- `tests/` 是项目测试目录；它包含该项目拥有的测试。

重要分离：

- Codex 平台 `PySide6` 是 Codex tooling 的本地 GUI 控制中心依赖。
- 下游项目 `PySide6` 依赖只有在该项目声明并拥有时，才是 business runtime dependency。
- 同样分离适用于 `SQLite`、`Redis`、`promptfoo` 和 `jina-embeddings`；不能因为平台使用它们，就自动把它们变成业务依赖。

## 6. 执行层

问题：这个项目如何交付变更？

推荐文件：

- `openspec/config.yaml` 是项目 OpenSpec 配置；它把 OpenSpec workflow 绑定到本仓库。
- `openspec/changes/<change-id>/proposal.md` 是项目本地 OpenSpec proposal；它解释为什么需要某个项目变更。
- `openspec/changes/<change-id>/design.md` 是项目本地 OpenSpec design；它解释该项目变更如何实现。
- `openspec/changes/<change-id>/tasks.md` 是项目本地 OpenSpec task list；它跟踪项目工作。
- `openspec/changes/<change-id>/*.zh-CN.md` 是同一项目 change artifacts 的 UTF-8 中文对照文件。

Codex 平台使用方式：

- 使用原生 `subagent` 处理当前 Codex 会话内有边界的专家工作。
- 只有当项目存在已冻结计划并且有两个以上基本独立执行切片时，才使用 `native_omx`。
- 只有当项目需要 graph phases、checkpoint recovery、approval gates 或 survivor queues 时，才使用 `langgraph`。

## 7. 发布、增长与采用层

问题：这个项目如何发布并持续改进？

推荐文件：

- `docs_bilingual/release_plan.md` 是发布计划；它定义 rollout、release gates 和沟通方式。
- `docs_bilingual/release_plan.zh-CN.md` 是发布计划的 UTF-8 中文对照版。
- `docs_bilingual/rollback_plan.md` 是回滚计划；它定义如何回到安全版本。
- `docs_bilingual/rollback_plan.zh-CN.md` 是回滚计划的 UTF-8 中文对照版。
- `CHANGELOG.md` 是项目变更日志；它记录用户可见和 operator 可见的变化。
- `docs_bilingual/metrics.md` 是指标文档；它定义项目成功和质量指标。
- `docs_bilingual/metrics.zh-CN.md` 是指标文档的 UTF-8 中文对照版。

小项目规则：本地自用项目在真正有用户或自动化之前，可以合并 release 和 rollback notes。

## 8. 复盘与上游反馈层

问题：这个项目哪些经验应该留在本地，哪些应该反馈给平台？

推荐文件：

- `docs_bilingual/lessons_learned.md` 是项目经验教训文档；它记录本地可复用经验。
- `docs_bilingual/lessons_learned.zh-CN.md` 是经验教训文档的 UTF-8 中文对照版。
- `docs_bilingual/upstream_feedback.md` 是平台反馈文档；它记录可能改进 `D:\PythonProject_langgraph` 的经验。
- `docs_bilingual/upstream_feedback.zh-CN.md` 是平台反馈文档的 UTF-8 中文对照版。

上游规则：下游项目经验只有在平台仓库通过平台 OpenSpec change 接受后，才会变成平台规则。

## Minimal Downstream Project Checklist

每个下游项目至少应该拥有：

- `AGENTS.md` 作为项目级 Codex 指令文件。
- `docs_bilingual/project_startup_summary.md` 作为 ASCII 冷启动摘要。
- `docs_bilingual/project_startup_summary.zh-CN.md` 作为 UTF-8 中文冷启动摘要对照版。
- `openspec/` 作为项目本地 OpenSpec 治理树。
- `.omx/state/` 作为项目本地 durable state 目录；仅在使用 durable lanes 时需要。
- `.gitignore` 作为项目忽略文件；它用于忽略缓存、状态、生成产物和本地密钥。

平台可以提供 templates 和 helpers，但项目仍然拥有自己的 requirements、state、releases 和 lessons。
