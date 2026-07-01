# Delta: Product Lifecycle Fresh Source Evidence

## ADDED Requirements

### Requirement: Fresh source reading evidence for lifecycle refreshes

凡是声称使用 Business Management 或 PMP/PMI evidence 刷新的 lifecycle、whitepaper、research 与 North Star 文档，在更新 tracked conclusions 前 SHALL 记录 fresh extraction run。

#### Scenario: PDF source is included
- **WHEN** local PDF source 属于 refresh 范围
- **THEN** extraction evidence 逐页记录 status row
- **AND** 记录每个 page 或 file fallback 使用 `pypdf` 还是 PyMuPDF/fitz

#### Scenario: EPUB source is included
- **WHEN** local EPUB source 属于 refresh 范围
- **THEN** extraction evidence 按 spine item 记录 status row
- **AND** 显式记录 skipped navigation 或 non-content items

#### Scenario: Markdown source is included
- **WHEN** local Markdown source 属于 refresh 范围
- **THEN** extraction evidence 记录 full-document reading status、hash、modified time 与 character count

### Requirement: Whitepaper and research relationship preservation

Codex durable-team whitepaper 与 solo-maintainable production persistent team research note SHALL 保持分离，除非后续 governed change 证明其中一个不再有独立 lifecycle role。

#### Scenario: 10-layer and 12-layer models both appear
- **WHEN** tracked documents 同时提到两个模型
- **THEN** 它们把 10-layer model 标识为 runtime/governance research view
- **AND** 把 12-layer model 标识为 product/business lifecycle view
- **AND** 提供 bridge，而不是把两个模型视为矛盾。

### Requirement: PMI tailoring and execution grammar authority

凡是使用 PMI evidence 刷新的 lifecycle、whitepaper、research 与 North Star 文档，SHALL 区分 strategic narrative 与 execution grammar，并显式记录完整架构、整个项目轻量、阶段局部轻量、模块级轻量和混合治理的裁剪规则。

#### Scenario: Execution-facing lifecycle layer is updated
- **WHEN** 某个 lifecycle layer 或 delivery gate 会驱动执行
- **THEN** 接收方文档写明输入、工具与技术、输出
- **AND** 记录受影响范围采用完整架构、整个项目轻量、阶段局部轻量、模块级轻量，还是混合模式

#### Scenario: PMI editions and practice guides are referenced
- **WHEN** 文档引用 PMBOK、Process Groups、Agile、项目集、项目组合或 PMO 来源
- **THEN** 文档说明 primary overlay 与 supplemental role
- **AND** 只有当旧版能提供执行词汇、连续性、翻译澄清或历史比较时才展开旧版
- **AND** 写明 Agile、项目集、项目组合与 PMO 叠加层的进入和退出条件。

### Requirement: Bilingual UTF-8 document integrity

本变更更新的英文与 zh-CN 成对文档 SHALL 保持相同治理决策，并 SHALL NOT 留下 mojibake 或 replacement-marker 新增内容。

#### Scenario: zh-CN document is touched
- **WHEN** zh-CN tracked document 被更新
- **THEN** changed text 是有效 UTF-8 中文或有意保留的技术术语
- **AND** 不保留新增的 three ASCII question marks 或 replacement-character 文本
- **AND** 如果存在成对文档，英文新增治理规则必须有 zh-CN 对应内容。
