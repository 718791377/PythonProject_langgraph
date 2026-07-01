## MODIFIED Requirements

### Requirement: Draft Plan Defines 10-To-12-Layer Bridge And Corpus Sync Evidence

生产级持久化团队 draft implementation plan SHALL 包含可见桥接，说明 10 层运行时能力核心与当前 12 层产品/商业生命周期目标之间的关系。核心 durable-team 文档族，包括白皮书、研究稿、MRD、北极星计划、实施方案、playbook、生命周期地图和 OpenSpec 规格，SHALL 使用同一组数量权威，并 SHALL 标明哪些证据已经提交、哪些只是被忽略的本地 extraction cache。方案还 SHALL 声明 draft 文档与 source-reading 报告都不是正在运行的 durable 或 persistent team 的 runtime implementation evidence。

#### Scenario: 冷启动维护者阅读 draft plan 与相关文档族

- **GIVEN** 维护者打开 `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md`
- **WHEN** 维护者查找白皮书、研究模型或 durable-team 文档族新鲜度
- **THEN** 方案在 lane-specific responsibility section 之前展示专门的 10-to-12-layer landing-map section
- **AND** 该 section 标明 12 层生命周期目标是当前规划框架
- **AND** 相关文档族声明 raw extraction cache 是被忽略的本地证据，新 worktree 中可能不存在
- **AND** 该 section 声明这只是 draft documentation，不是 runtime implementation evidence
