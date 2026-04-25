# codex-user-level-team-mode-controls Specification

## 目的

定义用户级 team-mode 控制资产、控制状态与兼容派生视图的生成要求。

## 要求

### Requirement: 生成出来的 controls 必须区分“已启用 capability layers”和“effective execution lane”

生成出来的用户级 controls 必须区分：

- 哪些 orchestration capability layers 已启用
- 某条任务流当前实际使用哪条 effective execution lane

不能把这两个概念继续压缩成同一个字段。

#### Scenario: 操作员检查用户级 control 输出

- **WHEN** 操作员检查生成出来的用户级 control surfaces
- **THEN** 这些 surface 必须区分已启用 capability layers 与当前 effective lane
- **AND** 不得为了每一条任务流的 lane 差异都要求 operator 先切一次全局 backend
