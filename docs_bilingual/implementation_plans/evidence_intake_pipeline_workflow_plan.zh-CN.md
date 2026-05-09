---
doc_id: evidence_intake_pipeline_workflow_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/evidence_intake_pipeline_workflow_plan.md
translation_of: docs_bilingual/implementation_plans/evidence_intake_pipeline_workflow_plan.md
doc_class: implementation_plan
status: draft
---

# Evidence Intake Pipeline 工作流方案

## 目的

本方案定义仓库内的证据接入工作流。任何本地参考资料在用于知识库接入、文档治理、白皮书、市场需求、实施方案或检索工作流之前，都必须先形成可追溯的抽取证据。

`tools/evidence_intake_pipeline.py` 是证据接入流水线脚本。它扫描本地参考资料，调用可用的 PDF、HTML、页面渲染和 OCR 适配器，生成证据记录、质量指标和摘要，同时避免把私有原始资料复制进 Git。

该流水线证明“已经抽取并记录证据”，但它本身不等于已经完成语义理解。

## 范围

该流水线是通用工具。它不是某个领域专用的参考资料阅读器，不只是 Poppler 封装，不只是 OCR 工具，也不是知识库本身。

首批本地运行使用被 Git 忽略的私有参考资料目录作为验证语料。后续项目可以使用各自的本地 source 目录和 output 目录。

## 规则

- 除非存在逐页 evidence manifest，否则不得声称每一页 PDF 都已经被正确读取。
- 除非存在逐篇 HTML evidence manifest 且抽取文本经过复核，否则不得声称已正确读取保存网页正文。
- extracted text 只能作为抽取证据，不能直接等同于语义理解证明。
- 对低质量 PDF 页面必须标记为需要 OCR、二次抽取或人工复核。
- 完整抽取文本必须保存在被忽略的本地目录，例如 `.local/evidence/local_reference/` 或 `.local/evidence/pmbok6_ocr/`。
- Git 只提交工具、测试、OpenSpec artifacts 和短小的非版权摘要。
- 不提交渲染页面图片、OCR 全文、私有 PDF、保存网页、第三方二进制、embedding 索引或向量缓存。

## 工作流

1. 运行 `python tools/evidence_intake_pipeline.py extract --source <local-reference-root> --output .local/evidence/local_reference`，扫描本地参考资料并生成被忽略的本地证据文件。
2. 复核生成的 `manifest.json`。该 manifest 记录 source 文件、抽取方法、输出路径、字符数和质量标记。
3. 复核生成的 `summary.md`。该 summary 标出低质量页面、噪声较高的 HTML 抽取和缺失工具。
4. 对图片型 PDF，运行 `python tools/evidence_intake_pipeline.py ocr-run --root . --pdf <local-pdf> --output .local/evidence/<run-name> --scope all --render-dpi 144 --json`，生成逐页渲染和 OCR 证据。
5. 只能使用经过复核的摘要更新仓库文档。不得把整本书、整篇文章或私有 source text 粘贴进提交文件。
6. 若页面或文章质量较低，必须先做 OCR、二次抽取或人工复核，再作出强读取声明。

## PDF 证据

每个 PDF 页面记录应包含页码、方法、抽取字符数、替换字符数、控制字符数、CJK 字符数、Latin 字符数、噪声比例、质量和复核标记。

`pdftotext` 是 Poppler 的 PDF 文本抽取命令。流水线在可用时用它抽取 PDF 文本。

`pdfinfo` 是 Poppler 的 PDF 元数据命令。流水线在可用时用它统计 PDF 页数。

`pdftoppm` 是 Poppler 的 PDF 页面渲染命令。需要 OCR 或视觉复核时，流水线可以用它把页面渲染成图片。

`tesseract` 是可选 OCR 命令。Tesseract 适配器应从 PATH 以及常见 Windows 安装位置发现它，例如 `C:\Program Files\Tesseract-OCR\tesseract.exe`。如果 OCR 不可用，流水线必须报告低质量扫描页需要 OCR，而不能假装这些页面已经被理解。

## OCR 语言映射

Tesseract 按语言代码安装 traineddata，并不总是按地区代码拆分。当前本地安装提供以下实用映射：

- 英语（英国）和英语（美国）使用 `eng`，即通用 English traineddata。
- 简体中文（中国大陆）使用 `chi_sim`。
- 繁体中文（中国香港）和繁体中文（中国台湾）使用 `chi_tra`，即通用 Traditional Chinese traineddata。
- 法语（法国）使用 `fra`。
- 德语（德国）使用 `deu`。
- 日语（日本）使用 `jpn`。
- 方向和文字系统检测使用 `osd`。

当 source PDF 主要是简体中文并夹杂英文缩写时，推荐 OCR language list 使用 `eng+chi_sim`。安装额外语言包是为了保留后续能力，但在单次 OCR 中加入无关语言可能降低准确率并增加运行时间。

## HTML 证据

每个保存 HTML 记录应包含文件名、标题、抽取的 visible text 路径、字符数、噪声比例和复核标记。

首版实现使用 Python 标准库 HTML parser。它会移除 script、style、noscript 和 SVG 内容，然后记录可见文本。在复核者确认这是正确 article body 之前，该结果只能称为 extracted text。

## 外部工具清点

`inventory-tools` 是只读 inventory 模式。它检查另一个本地项目目录中可复用的 document、PDF、HTML 或 OCR helper 候选，而不复制文件。

inventory 可能识别以下有用想法或候选 adapter：

- Poppler 二进制，例如 `pdftotext.exe`，它是 PDF 文本抽取命令行工具。
- 已有项目专用抽取脚本；它们可以提供模式参考，但不能盲目复制。
- 缓存的 Python 依赖；它们不是 source truth。
- 已生成输出文件；它们不是可复用 source tool。

未来若需要从其他项目复制或迁移，必须另开 OpenSpec change。

## 知识库边界

### 平台知识库

`D:\PythonProject_langgraph` 是 Codex CLI 个人生产级 durable-team 平台的 source-truth 仓库。

平台知识库可以保存工具治理、OpenSpec 规则、durable-team policy、wrapper/checker/helper 规则、跨项目开发经验和平台级 evidence manifest。

平台知识库默认不得保存 consumer project 的私有业务事实。

### 项目知识库

每个 consumer project 在自己的仓库或本地 runtime 目录中维护项目知识库。

项目知识库可以保存项目业务资料、项目级 OpenSpec artifacts、项目 durable state、测试、发布事实、项目证据和项目检索索引。

项目知识默认不得写入平台 source truth。

### 跨项目数据

跨项目数据不得隐式合并。迁移或合并前，必须使用明确 export package、只读引用、provenance tracking，并另开 OpenSpec change。

每条跨项目数据记录应包含 `source_project`、`source_path`、`source_commit`、`source_timestamp`、`scope`、`classification` 和 `provenance`。

跨项目引用默认只读，且不得写回 source project。

## 工具统一维护策略

Durable-team 平台工具的 source truth 是本仓库，尤其是 `D:\PythonProject_langgraph\tools\`。

用户级安装只应包含 thin launcher、wrapper、command shim、helper mirror 和配置指针。用户级副本是安装产物，不是 source truth。

Consumer project 应通过 `CODEX_TEAM_HOME`、`CODEX_TEAM_RUNTIME`、显式脚本路径或 helper shim 调用平台工具。`CODEX_TEAM_HOME` 指向平台仓库根目录。`CODEX_TEAM_RUNTIME` 指向被忽略的本地 runtime 和 cache 存储。

其他项目默认不复制平台工具源码。若确实需要复制，必须打开 OpenSpec change 定义 fork scope、version ownership 和 rollback strategy。

第三方二进制、OCR 模型、抽取全文、embedding 索引、vector database 缓存和项目业务数据不得作为平台 source 提交。它们应放在 `.local/`、`.runtime/`、本地安装目录或其他明确忽略的 runtime 目录。

## Adapter 方向

仓库维护的 adapter 布局如下：

- `tools/evidence_adapters/poppler_adapter.py`：Poppler adapter，负责 `pdftotext`、`pdfinfo` 和 `pdftoppm`。
- `tools/evidence_adapters/tesseract_adapter.py`：Tesseract adapter，负责 OCR 文本和 confidence 数据。
- `tools/evidence_adapters/html_visible_text_adapter.py`：HTML adapter，负责保存网页的 visible-text 抽取。
- `tools/evidence_adapters/paddleocr_adapter.py`：未来可选 PaddleOCR adapter，用于 Tesseract 质量不足时的中文和混合语言 OCR。

## 输出

默认本地输出：

- `.local/evidence/local_reference/manifest.json`：机器可读抽取 manifest。
- `.local/evidence/local_reference/summary.md`：短小的人类可读抽取摘要。
- `.local/evidence/local_reference/pdf_pages/`：被忽略的逐页 PDF 文本证据。
- `.local/evidence/local_reference/pdf_images/`：被忽略的逐页 PDF 图片证据，仅在启用渲染或 OCR 时生成。
- `.local/evidence/local_reference/pdf_ocr/`：被忽略的逐页 OCR 文本证据，仅在启用 OCR 且 OCR 可用时生成。
- `.local/evidence/local_reference/html_articles/`：被忽略的逐 HTML 抽取文本证据。
- `.local/evidence/local_reference/tool_inventory.json`：外部工具候选的只读 inventory。
- `.local/evidence/<ocr-run-name>/manifest.json`：机器可读 OCR run manifest。
- `.local/evidence/<ocr-run-name>/summary.md`：短小 OCR run 摘要。

这些文件都是本地证据 artifacts，除非明确选择提交短小的 sanitized summary，否则应保持未跟踪。

## 验证

运行：

- `python tools/evidence_intake_pipeline.py extract --root . --source <local-reference-root> --output .local/evidence/local_reference` 生成本地抽取证据。
- `python tools/evidence_intake_pipeline.py extract --root . --source <local-reference-root> --output .local/evidence/local_reference --render-pages` 生成页面图片证据。
- `python tools/evidence_intake_pipeline.py extract --root . --source <local-reference-root> --output .local/evidence/local_reference --ocr-pages` 在 OCR 工具可用时生成页面 OCR 证据。
- `python tools/evidence_intake_pipeline.py ocr-run --root . --pdf <local-pdf> --output .local/evidence/<ocr-run-name> --scope all --render-dpi 144 --json` 为单个 PDF 生成可追溯逐页 OCR 证据。
- `python tools/evidence_intake_pipeline.py inventory-tools --root <external-project-root> --output .local/evidence/local_reference/tool_inventory.json` 清点外部工具候选。
- `python tools/evidence_intake_pipeline.py check --output .local/evidence/local_reference` 验证抽取证据结构。
- `python test/evidence_intake_pipeline.test.py` 和 `python test/evidence_adapters.test.py` 运行单元测试。
