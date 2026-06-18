## ADDED Requirements

### Requirement: 文档视觉渲染 QA 如实报告后端状态

通用文档流水线 SHALL 如实报告 Poppler `pdftoppm`、Python `pdf2image` 与 `soffice/libreoffice` 的视觉渲染 QA 后端可用性和使用情况。

#### Scenario: 可选后端不可用

- **GIVEN** 某个视觉 QA 后端未安装或无法解析
- **WHEN** 共享文档流水线检测或尝试视觉 QA
- **THEN** 它 SHALL 将该后端记录为 `unavailable` 或 `skipped`
- **AND** 它 SHALL NOT 宣称该后端产生了视觉验证证据。

#### Scenario: 严格要求某个后端

- **GIVEN** 调用方要求一个或多个指定视觉 QA 后端
- **WHEN** 任一必需后端不可用
- **THEN** 视觉 QA 命令 SHALL 失败，并用结构化证据命名缺失后端
- **AND** 任何生成报告 SHALL 区分严格失败与可选跳过。

#### Scenario: 视觉渲染成功

- **GIVEN** 请求的视觉 QA 后端可用
- **WHEN** 流水线渲染 PDF 或已转换为 PDF 的 DOCX
- **THEN** 它 SHALL 写出 JSON 与 Markdown 证据，命名选定后端、输出路径、渲染文件数量与任何被跳过的替代后端。

### Requirement: 视觉 QA 运行时依赖不进入跟踪源码

通用文档流水线 SHALL 将视觉 QA 运行时依赖和生成的渲染 artifact 保持在 Git 跟踪源码之外。

#### Scenario: 本地运行时依赖已配置

- **GIVEN** Poppler、`pdf2image` 或 LibreOffice 已安装在机器上
- **WHEN** 共享工具使用这些依赖
- **THEN** Poppler 可来自被忽略的 `.local` 缓存，`pdf2image` 可来自项目虚拟环境，LibreOffice 可来自 Windows 程序安装路径
- **AND** 第三方应用载荷与生成的渲染文件 SHALL NOT 作为仓库源码被跟踪。
