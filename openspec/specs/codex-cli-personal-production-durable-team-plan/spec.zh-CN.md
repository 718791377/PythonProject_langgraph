# Codex CLI 个人开发者生产级持久化团队方案规格

## 目的

跟踪 Codex CLI 个人开发者生产级持久化团队 implementation plan draft 的稳定需求，但不宣称完整 production durable-team runtime 已经实现。

## Requirements

### Requirement: Draft Plan Defines 10-To-12-Layer Bridge And Corpus Sync Evidence

生产级持久化团队 draft implementation plan SHALL 包含可见桥接，说明 10 层运行时能力核心与当前 12 层产品/商业生命周期目标之间的关系。核心 durable-team 文档族，包括白皮书、研究稿、MRD、北极星计划、实施方案、playbook、生命周期地图和 OpenSpec 规格，SHALL 使用同一组数量权威，并 SHALL 标明哪些证据已经提交、哪些只是被忽略的本地 extraction cache。方案还 SHALL 声明 draft 文档与 source-reading 报告都不是正在运行的 durable 或 persistent team 的 runtime implementation evidence。

#### Scenario: 冷启动维护者阅读 draft plan 与相关文档族

- **GIVEN** 维护者打开 `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md`
- **WHEN** 维护者查找白皮书、研究模型或 durable-team 文档族新鲜度
- **THEN** 方案在 lane-specific responsibility section 之前展示专门的 10-to-12-layer landing-map section
- **AND** 该 section 标明 12 层生命周期目标是当前规划框架
- **AND** 相关文档族声明 raw extraction cache 是被忽略的本地证据，新 worktree 中可能不存在
- **AND** 该 section 声明这只是 draft documentation，不是 runtime implementation evidence

### Requirement: Shared Local Model Assets Migration Is Documented Separately

生产级持久化团队 documentation SHALL 包含一份单独的本地 llama 与 GGUF 模型资产迁移方案，用于说明 `D:\PythonProject_langgraph` 如何集中管理被 Git 忽略的模型资产，同时让 consumer repositories 通过显式 provider profiles 调用它们。

#### Scenario: 维护者迁移本地 GGUF 文件

- **GIVEN** 维护者希望把 GGUF 模型文件移动到 orchestration repository tree 下
- **WHEN** 维护者阅读迁移方案
- **THEN** 方案识别 ignored model asset directories、Git hygiene checks、provider profiles、validation commands 与 rollback guidance
- **AND** 方案声明真实 GGUF 模型文件不得提交到普通 Git

### Requirement: Local Model Providers Are Services And Not Durable Truth

生产级持久化团队 documentation SHALL 声明 `local-judge-qwen` 和 `local-embed-jina` 这类本地模型 providers 只是 shared services，SHALL NOT 成为 durable truth、approval authority 或 backend routing selectors。

#### Scenario: OpenClaw starts a shared local model service

- **GIVEN** OpenClaw 启动或调用由 `D:\PythonProject_langgraph` 管理的模型服务
- **WHEN** 服务处理请求
- **THEN** OpenClaw state、Codex durable-team state、approval state、customer data 与 provider logs 保持隔离

### Requirement: Production Durable-Team Implementation Has A Playbook Layer

生产级持久化团队方案 SHALL 指向一份 playbook，把 draft target 转换为包含 preconditions、file scopes、forbidden scopes、commands、evidence、validation 与 rollback guidance 的 release slices。

#### Scenario: 冷启动维护者恢复实施

- **GIVEN** 维护者没有之前的对话上下文
- **WHEN** 维护者打开 playbook
- **THEN** 维护者可以识别下一个 release slice、它的 OpenSpec requirement、允许的 file scope、validation commands，以及是否允许 runtime apply mode

### Requirement: Expert Fan-Out And Stalled Subagent Handling Are Explicit

team-mode plan SHALL 声明有界多面研究从 homogeneous analyst fan-out 开始，并声明 unfinished subagents 必须先诊断，再决定跳过或关闭。

#### Scenario: One specialist subagent has not completed

- **GIVEN** analyst fan-in 已完成，但 specialist subagent 仍在运行
- **WHEN** leader 准备最终答复
- **THEN** leader 先记录该 subagent 是 still active、blocked，还是 suspected stalled
- **AND** leader 决定继续等待、缩小范围并重启、带记录关闭，或披露限制后本地继续处理

### Requirement: 持久化团队语料必须维护交付、追踪和过程组证明面

生产级持久化团队文档语料 SHALL 维护显式证明面，用于记录交付覆盖、来源追踪以及过程组式执行语法。交付矩阵 SHALL 将用户要求 UR1 到 UR4 映射到已刷新的文档与非目标。来源追踪索引 SHALL 标识当前 fresh-reading 运行、已跟踪与被忽略证据的边界，以及来源家族到权威文档的映射。过程组契约 SHALL 定义何时必须为面向执行的生命周期层级、交付门和发布切片写明“输入 / 工具与技术 / 输出”。

这些证明面 SHALL 只作为文档治理证据。它们 SHALL NOT 被当作持久化或常驻团队已经实现、已被选择、正在运行或已获 apply mode 批准的运行时证据。

#### Scenario: 维护者在来源刷新后审计持久化团队语料

- **GIVEN** 维护者打开持久化团队白皮书、研究稿、实施方案、playbook、生命周期地图或 OpenSpec 规格
- **WHEN** 维护者需要确认哪一项用户要求、来源运行或执行语法规则支撑了刷新结论
- **THEN** 语料指向交付矩阵、来源追踪索引和过程组契约
- **AND** 这些证明面标识当前来源运行，而不要求 Git 中存在原始抽取缓存
- **AND** 这些证明面保留白皮书与研究稿的分工，以及 10 层到 12 层的桥接关系
- **AND** 这些证明面声明 draft 文档不证明运行中的持久化团队 runtime
