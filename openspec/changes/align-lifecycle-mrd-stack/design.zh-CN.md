# Design：生命周期 MRD 文档栈对齐

## 文档位置

`docs_bilingual/whitepapers/` 是白皮书目录；它保存认知叙事文档。

`docs_bilingual/market_requirements/` 是 MRD 目录；它保存市场需求文档及其附录。

`docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` 继续作为北极星与实施桥接计划；本 change 不重命名它。

## 合并决策

原能力画像文件会物理合并进 MRD，并在逻辑上保持为附录 A。这样可以简化冷启动阅读，同时保留查询表结构。
