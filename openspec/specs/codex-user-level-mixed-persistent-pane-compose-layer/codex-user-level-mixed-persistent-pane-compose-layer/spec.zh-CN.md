# codex-user-level-mixed-persistent-pane-compose-layer Specification

## 目的

定义用户级 Codex / oh-my-codex team mode 中 mixed persistent pane compose 高级模式的显式 opt-in、manifest-driven 规范层。

## 要求

### Requirement: 用户级安装层 SHALL 定义一个 manifest-driven 的 mixed persistent pane compose layer

用户级安装层 SHALL 为 mixed persistent panes 定义一个高级的、manifest-driven 的 compose layer。

该 compose layer SHALL 明确保持在默认 operating mode 之外。

compose 资产集合至少 SHALL 包含：

- 一个用户级 compose 入口，例如 `omx-team-compose.ps1`
- 一个放在用户级资产根目录下的 compose manifest schema

#### Scenario: 操作员显式启用 advanced compose layer

- **WHEN** 操作员显式选择 mixed persistent pane compose mode
- **THEN** 用户级安装层 SHALL 暴露一个 manifest-driven 的 compose 路径
- **AND** 它 SHALL NOT 要求操作员只能通过临时拼装 pane 的方式来组装拓扑

### Requirement: compose manifest SHALL 声明 pane topology 与 ownership boundaries

compose manifest 至少 SHALL 声明：

- pane identities
- role bindings
- worktree allocation
- mailbox routing
- ownership boundaries
- checkpoint policy

#### Scenario: 操作员准备一个异构 persistent pane topology

- **WHEN** 操作员为 mixed persistent panes 准备 compose manifest
- **THEN** 该 manifest SHALL 显式描述 pane identity、worktree、mailbox 和 ownership boundaries
- **AND** 它 SHALL NOT 让写入范围或 checkpoint 职责保持隐含状态

### Requirement: mixed persistent pane compose SHALL 保持为高级 opt-in 模式

mixed persistent pane compose layer SHALL 明确保持为 opt-in 模式。

它 SHALL NOT 成为普通 routing thresholds 的默认结果。

#### Scenario: 普通自动路由评估一个常规异构任务

- **WHEN** 当前任务在没有显式 compose 调用的情况下由普通用户级 routing thresholds 处理
- **THEN** 工作流 SHALL 保持在默认 operating model 上
- **AND** 它 SHALL NOT 静默升级为 mixed persistent panes

### Requirement: leader SHALL 保持在 pane roster 之外

即使 mixed persistent panes 被启用，当前主 Codex CLI 会话也 SHALL 继续作为 leader lane。

compose layer SHALL NOT 把 leader 重新定义为一个常驻 worker pane。

#### Scenario: 操作员启动 compose mode

- **WHEN** 操作员启动 mixed persistent pane compose mode
- **THEN** 当前主 Codex CLI 会话 SHALL 保持在 pane roster 之外
- **AND** 最终路由、冲突处理和集成所有权 SHALL 继续归属于该主会话
