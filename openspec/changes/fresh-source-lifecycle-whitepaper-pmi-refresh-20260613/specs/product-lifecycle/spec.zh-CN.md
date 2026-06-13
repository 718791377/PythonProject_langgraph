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
