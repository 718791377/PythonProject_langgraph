# codex-user-level-mainline-memory-handoff 规范

## Purpose

定义 current mainline memory summaries 如何让冷启动交接与最新落地的 governance、checker 或 tooling 增量保持一致。

## ADDED Requirements

### Requirement: Mainline memory handoffs SHALL identify the latest landed increment

Current mainline memory summary 在列出候选下一步动作前，SHALL 先识别最新落地的 governance、checker、tooling 或 workflow 增量。

该 handoff SHALL 包含：

- 适用时列出最新归档的 OpenSpec change 名称
- 适用时列出受影响的 script、checker 或 documentation path
- 当前 active-change 状态
- 下一会话应重新打开设计，还是从已实现行为继续

#### Scenario: A new cold-start session resumes after a checker-backed increment landed

- **WHEN** 新冷启动会话读取 current mainline memory summary
- **THEN** summary SHALL 识别最新落地的 checker-backed 增量
- **AND** 它 SHALL 说明是否存在 active OpenSpec changes
- **AND** 它 SHALL 列出安全的下一步选择，不暗示较早已完成增量仍需实现
