# codex-cli-personal-production-durable-team-plan 规格增量

## ADDED Requirements

### Requirement: 共享本地模型资产迁移必须单独成文

生产级持久化团队文档 SHALL 包含一份单独的本地 llama 与 GGUF 模型资产迁移方案，用于说明 `D:\PythonProject_langgraph` 这个编排仓库如何集中管理被 Git 忽略的模型资产，同时让消费方仓库通过显式 provider profile 调用这些资产。

#### Scenario: 维护者迁移本地 GGUF 文件

- **GIVEN** 维护者希望把 GGUF 模型文件移动到编排仓库目录树下
- **WHEN** 维护者阅读迁移方案
- **THEN** 方案识别被 Git 忽略的模型资产目录、Git 卫生检查、provider profiles、验证命令和回滚指引
- **AND** 方案声明真实 GGUF 模型文件不得提交到普通 Git

### Requirement: 本地模型 Provider 是服务而不是 Durable Truth

生产级持久化团队文档 SHALL 声明 `local-judge-qwen` 与 `local-embed-jina` 这类本地模型 provider 只是共享服务，SHALL NOT 成为 durable truth、approval authority 或 backend routing selector。

#### Scenario: OpenClaw 启动共享本地模型服务

- **GIVEN** OpenClaw 启动或调用由 `D:\PythonProject_langgraph` 管理的模型服务
- **WHEN** 服务处理请求
- **THEN** OpenClaw state、Codex durable-team state、approval state、customer data 与 provider logs 保持隔离

### Requirement: 生产级持久化团队实施必须有 Playbook 层

生产级持久化团队方案 SHALL 指向一份 playbook，把 draft 目标转换为包含前置条件、文件范围、禁止范围、命令、证据、验证与回滚指引的 release slices。

#### Scenario: 冷启动维护者恢复实施

- **GIVEN** 维护者没有之前的对话上下文
- **WHEN** 维护者打开 playbook
- **THEN** 维护者可以识别下一个 release slice、对应 OpenSpec requirement、允许修改的文件范围、验证命令，以及是否允许 runtime apply mode

### Requirement: Expert Fan-Out 与 Stalled Subagent 处理必须显式化

team-mode plan SHALL 声明有界多面研究从同质 analyst fan-out 开始，并声明未完成 subagent 必须先诊断，再决定跳过或关闭。

#### Scenario: 一个 specialist subagent 尚未完成

- **GIVEN** analyst fan-in 已完成，但一个 specialist subagent 仍在运行
- **WHEN** leader 准备最终答复
- **THEN** leader 先记录该 subagent 是仍在 active、blocked 还是 suspected stalled
- **AND** leader 决定继续等待、缩小范围并重启、带记录关闭，或在明确披露限制后本地继续处理
