# codex-evidence-intake-pipeline 规格

## 目的

本规格定义仓库维护的 evidence intake pipeline。该流水线把本地参考文件转换成可追溯的抽取、渲染、OCR 和质量证据，同时避免提交私有 source material 或大型生成 artifacts。

## Requirements

### Requirement: Evidence Intake Uses Repository-Maintained Adapters

仓库必须维护用于 PDF 文本抽取、PDF 页面渲染、OCR 和保存 HTML 可见文本抽取的 document evidence adapters，而不是依赖从外部项目复制来的脚本。

#### Scenario: External document tooling is adopted

- **GIVEN** 外部本地项目包含 Poppler 或 document pipeline helpers
- **WHEN** 本仓库采纳这些 helpers 中可复用的行为
- **THEN** 该行为必须实现为 `tools/evidence_adapters/` 下的仓库维护 adapter source
- **AND** 第三方二进制必须保持为本地安装依赖，而不是 tracked repository source
- **AND** 不得把外部项目的项目专用绝对路径复制进默认行为

### Requirement: Evidence Adapters Degrade Gracefully When Tools Are Missing

Evidence intake pipeline 必须记录结构化 missing-tool evidence，而不是静默失败或声称页面已经被理解。

#### Scenario: OCR or rendering tools are unavailable

- **GIVEN** 当前机器不可用 `pdftoppm` 或 `tesseract`
- **WHEN** evidence pipeline 请求渲染或 OCR
- **THEN** manifest 必须记录缺失工具，并把受影响页面标记为需要复核
- **AND** pipeline 不得声称已经生成 OCR 文本或置信度

#### Scenario: Tesseract is installed in a standard Windows location outside PATH

- **GIVEN** Tesseract OCR 安装在 `C:\Program Files\Tesseract-OCR\tesseract.exe`
- **AND** 当前进程 PATH 无法解析 `tesseract`
- **WHEN** Tesseract adapter 发现 OCR 工具
- **THEN** 它必须找到标准 Windows 安装路径
- **AND** OCR run 不得错误报告 Tesseract 缺失

### Requirement: Page-Level OCR Runs Are Traceable And Scoped

Evidence intake pipeline 必须支持 page-level OCR evidence run，包含明确页范围、逐页渲染图片证据、OCR 文本证据、置信度指标和质量标记，并把这些内容保存在被忽略的本地证据目录。

#### Scenario: A maintainer requests OCR for every page of a PDF

- **GIVEN** 本地 PDF 可用，并且 maintainer 请求全页 OCR
- **WHEN** 执行 OCR evidence run
- **THEN** run manifest 必须记录请求页集
- **AND** 每个请求页必须有 page record，包含 render status、OCR status、可用时的 confidence 和 review flags
- **AND** 大型渲染图片和 OCR 全文必须保持为被忽略的本地 artifacts

### Requirement: OCR Completion Claims Require Evidence Or Explicit Failure Records

除非 evidence run 为某页生成了 page-level OCR output 和 quality metrics，否则仓库不得声称该 PDF 页面已被正确 OCR 读取。

#### Scenario: OCR tooling is missing or a page fails

- **GIVEN** OCR 工具缺失，或某页渲染/OCR 命令失败
- **WHEN** evidence run 写入 manifest
- **THEN** 受影响页面必须以具体原因为 blocked 或 failed
- **AND** summary 必须说明该页集 OCR 未完成
- **AND** 下游 lifecycle 或 white-paper 更新不得把该页当作已完整读取
