## ADDED Requirements

### Requirement: canonical implementation-plan 文档必须区分当前实现现实与未来方向
当一份 canonical implementation-plan 文档同时承担 operator-facing 状态图职责时，它必须明确区分“当前实现现实”和“可选未来方向”，而不能把它们混成一层 roadmap 表述。

#### Scenario: 一份方案文档同时包含已实现与未来章节
- **WHEN** 一份 canonical implementation-plan 文档同时包含当前表面和未来扩展
- **THEN** 它必须显式标明这些状态的区别
- **AND** 不得把纯 future item 写得像它已经属于当前默认 operator path
