## ADDED Requirements

### Requirement: Platform White Paper And MRD Are First-Class Lifecycle Documents

仓库必须为 Codex CLI 个人开发者生产级持久化团队平台维护 first-class 双语白皮书和 MRD，然后才能把下游 implementation plans 视为完整生命周期覆盖。first-class 双语文档是正式维护的英文主版和中文对照版。

#### Scenario: A maintainer follows the lifecycle stack

- **GIVEN** 维护者阅读平台生命周期文档
- **WHEN** 维护者需要认知叙事和市场需求
- **THEN** 维护者能在 `docs_bilingual/whitepapers/` 找到 canonical 白皮书；该目录是白皮书目录
- **AND** 维护者能在 `docs_bilingual/market_requirements/` 找到 MRD；该目录是市场需求文档目录
- **AND** 具体 workload-to-profile 映射位于 MRD 附录，而不是独立 implementation-plan reference。workload-to-profile 映射是具体工作负载到抽象能力画像的映射
