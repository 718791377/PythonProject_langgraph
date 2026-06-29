## ADDED Requirements

### Requirement: PPT 可视化审阅 sidecar 生成可携带本地审阅 artifact

通用文档工具 SHALL 提供本地/离线 PPT 可视化审阅 sidecar，基于已渲染的 slide PNG 创建可携带审阅 artifact，且不修改源 PPTX。

#### Scenario: 基于 slide PNG 创建审阅 session

- **GIVEN** 一个 slide PNG 目录和可选源 PPTX 路径
- **WHEN** 操作者使用输出目录运行 PPT review tool
- **THEN** 工具 SHALL 写出 `session_manifest.json`、`comments.json`、`review_report.json` 和 `review_report.html`
- **AND** manifest SHALL 包含源输入 metadata、页数、复制后的 slide images 和输出 artifact 名称。

#### Scenario: 区域评论被规范化

- **GIVEN** 原始审阅评论包含页码、归一化 ROI、严重级别、类别、问题文字和可选建议修改
- **WHEN** 工具规范化这些评论
- **THEN** 每条评论 SHALL 包含稳定的 `slide`、`roi`、`severity`、`category`、`comment`、`suggested_fix`、`status` 与时间戳字段
- **AND** 非法 ROI 坐标 SHALL fail closed，而不是产生误导性视觉证据。

#### Scenario: 生成离线报告

- **GIVEN** 一个审阅 session 和评论
- **WHEN** HTML 报告被写出
- **THEN** 它 SHALL 只嵌入或引用本地 session 数据和 assets
- **AND** 它 SHALL NOT 依赖外部 CDN、HTTP 或 HTTPS 资源。

### Requirement: PPT 可视化审阅工具保持源文件与运行时边界

通用文档工具 SHALL 将 PPT 审阅输出、渲染 slide images 和源 deck 保持在跟踪的共享工具源码之外，除非它们被显式作为测试或示例提供。

#### Scenario: 源 deck 以只读方式被审阅

- **GIVEN** 提供了源 PPTX 路径
- **WHEN** 创建审阅 session
- **THEN** 源 PPTX SHALL 仅作为 provenance metadata 记录
- **AND** 工具 SHALL NOT 编辑、重写或向该源 PPTX 添加原生批注。
