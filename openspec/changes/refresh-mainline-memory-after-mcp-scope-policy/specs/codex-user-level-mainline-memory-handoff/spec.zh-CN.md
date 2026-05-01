## MODIFIED Requirements（修改后的需求）

### Requirement: Mainline memory handoffs SHALL identify the latest landed increment

Current mainline memory summary（当前主线记忆摘要） 在列出候选下一步动作前，SHALL 先识别最新落地的 governance、checker、tooling 或 workflow 增量。

该 handoff（交接摘要） SHALL 包含：

- 适用时列出最新归档的 OpenSpec change 名称。
- 适用时列出受影响的 script、checker 或 documentation path；这些路径用于说明增量落在哪些文件上。
- 当前 active-change 状态；active-change 是尚未归档的 OpenSpec change。
- 下一会话应重新打开设计，还是从已实现行为继续。
- 当仓库采用 GitLab-first 加 GitHub mirror workflow（GitLab 优先并镜像到 GitHub 的流程） 时，列出当前 publication-ref alignment（发布引用对齐状态）。
- 当最新落地增量新增 governance surface（治理入口） 时，列出 policy routing pointer（策略路由指针）。

#### Scenario: A new cold-start session resumes after MCP scope policy work landed

- **WHEN** 新会话在 MCP scope policy（MCP 范围策略） 与 memory-handoff archive（记忆交接归档） 工作落地后读取当前 mainline memory summary
- **THEN** summary SHALL 识别最新落地的 MCP Router scope policy 增量
- **AND** 它 SHALL 在推荐实施前说明是否存在 active OpenSpec changes
- **AND** 它 SHALL 把 MCP Router 与 Codex-direct MCP（Codex 直连 MCP） 问题路由到稳定 MCP scope policy 文档
- **AND** 它 SHALL 避免把已经落地的 replay（重放） 或 task-ownership（任务所有权） 增量描述成下一步必做实施
