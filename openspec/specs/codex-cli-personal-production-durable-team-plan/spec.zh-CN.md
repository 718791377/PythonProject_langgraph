# Codex CLI 个人开发者生产级持久化团队方案规格

## 目的

跟踪 Codex CLI 个人开发者生产级持久化团队 implementation plan draft 的稳定需求，但不宣称完整 production durable-team runtime 已经实现。

## Requirements

### Requirement: Draft Plan Includes Ten-Layer Landing Map

生产级持久化团队 draft implementation plan SHALL 包含可见的十层框架落地映射，列出每一层、解释其生产含义，并说明该层如何落到当前用户级加项目级方案中。

#### Scenario: 冷启动维护者阅读 draft plan

- **GIVEN** 维护者打开 `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md`
- **WHEN** 维护者查找白皮书十层模型
- **THEN** 方案在 lane-specific responsibility section 之前展示专门的 ten-layer landing-map section
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
