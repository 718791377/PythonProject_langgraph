# Proposal：对齐生命周期 MRD 文档栈

## 摘要

新增 canonical 白皮书和 MRD，把原能力画像参考表合并进 MRD，并更新北极星计划引用。canonical 白皮书是正式白皮书入口，MRD 是市场需求文档。

## 范围

- 新增 `docs_bilingual/whitepapers/` 作为白皮书目录；该目录保存认知叙事文档。
- 新增 `docs_bilingual/market_requirements/` 作为 MRD 目录；该目录保存市场需求文档。
- 将原 `codex_business_capability_profiles` 参考表合并到 MRD 附录 A；该附录保存 workload-to-profile 映射。
- 更新北极星计划、生命周期引用和文档注册表；文档注册表声明双语文档入口。

## 非目标

- 不实现 runtime 行为；runtime 行为是实际运行时代码或工具行为。
- 不在本 change 中创建 BRD、PRD、architecture、test、release、rollback、adoption 或 retrospective 文件。BRD 是商业需求文档，PRD 是产品需求文档，architecture 是架构设计文档，test 是测试计划，release 是发布计划，rollback 是回滚计划，adoption 是采用报告，retrospective 是复盘文档。
- 不宣称长期 durable team 目标已经实现；durable team 是持久化团队能力目标。
