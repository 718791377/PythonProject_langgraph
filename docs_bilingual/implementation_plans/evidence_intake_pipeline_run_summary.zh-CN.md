---
doc_id: evidence_intake_pipeline_run_summary
lang: zh-CN
canonical: docs_bilingual/implementation_plans/evidence_intake_pipeline_run_summary.md
translation_of: docs_bilingual/implementation_plans/evidence_intake_pipeline_run_summary.md
doc_class: implementation_plan
status: draft
---

# Evidence Intake Pipeline 运行摘要

## 运行范围

本摘要记录 evidence intake pipeline 的本地证据运行结果。它不复现 source PDF 页面、OCR 全文、渲染图片或保存网页正文。

这些运行使用的本地私有参考资料目录都被 Git 忽略。它们包含 source PDF、保存网页、渲染页面图片、OCR 文本文件和机器可读 manifest。

## 纯文本参考资料抽取结果

第一次完整 text-only run 扫描了 7 个 PDF 文件和 12 个顶层保存 HTML 页面。

PDF 文本抽取使用 Poppler 的 `pdftotext` 完成了 2,753 页。`pdftotext` 是 Poppler 的 PDF 文本抽取命令行工具。

text-only run 标记了 284 页 PDF 为低质量或需要复核。这些页面需要 OCR、二次抽取或人工复核，之后才能作出强逐页读取声明。

HTML 抽取使用 Python 标准库 HTML parser 生成了 12 条 visible-text 记录。这些记录只是 extracted text，在复核前不能等同于已验证 article body。

## PMBOK 第六版逐页 OCR 结果

后续的 page-level OCR evidence run 处理了本地 PMBOK 第六版中文 PDF。该 PDF 是本地参考资料，不提交进仓库。

本地被忽略输出目录：`.local/evidence/pmbok6_ocr/`。

运行参数：

- Scope：`all`。
- 页数：812。
- Render DPI：144。
- 本 source PDF 使用的 OCR language list：`eng+chi_sim`。
- 语言选择理由：该 source PDF 主要是简体中文，并夹杂英文缩写。其他已安装语言包可用于未来 source，但本次未加入单次 OCR，以避免不必要的变慢和识别噪声。

计数：

- 请求页数：812。
- 已渲染页数：812。
- OCR 完成页数：812。
- blocked 页数：0。
- failed 页数：0。
- 需要复核页数：16。

置信度指标：

- 带置信度指标的页数：812。
- 平均置信度：90.503。
- 最低置信度：44.374。
- 最高置信度：95.421。
- 置信度低于 60 的页面：2 页，第 74 页和第 540 页。
- 标记为需要复核的页面：第 6、36、38、74、88、210、432、576、578、598、650、674、676、710、810、811 页。

该 OCR run 已完成请求页集。低置信度页面和被标记为需要复核的页面，仍需要二次 OCR 或人工复核，之后才能对这些页面作出强语义声明。

### 2026-05-09 flagged page review

在发布后复核中，人工查看了本地渲染页图、增强 contact sheet、OCR 文本以及 `pdftotext` 输出。复核对象包括低于 60 置信度的第 74、540 页，以及全部标记为需要复核的第 6、36、38、74、88、210、432、576、578、598、650、674、676、710、810、811 页。

复核结论：这些页面的复核信号主要来自空白或近空白页面、版权水印页、分隔/背面页、仅页脚页，或 Tesseract/`pdftotext` 把水印和页脚识别成少量噪声字符。未发现需要在仓库中提交的源 PDF 页面、OCR 全文、渲染图片或第三方二进制。低置信度第 74、540 页不应被当作正文语义已可靠识别；它们在本次摘要中的状态是“已人工复核为非正文/噪声主导页面”。

逐页记录：

| 页码 | 触发原因 | 复核结论 |
| --- | --- | --- |
| 6 | 需要复核 | 版权水印页；OCR 为空，视觉复核显示水印文本，不作为正文语义页。 |
| 36 | 需要复核 | 版权水印/页脚页；OCR 仅识别 `XXX`，不作为正文语义页。 |
| 38 | 需要复核 | 版权水印页；OCR 为空，不作为正文语义页。 |
| 74 | 低置信度且需要复核 | 近空白/页脚页；OCR 只产生少量噪声字符，不作为正文语义页。 |
| 88 | 需要复核 | 近空白/页脚页；视觉复核未见可依赖正文。 |
| 210 | 需要复核 | 近空白/页脚页；OCR 只产生少量噪声字符。 |
| 432 | 需要复核 | 近空白/页脚页；OCR 为空。 |
| 540 | 低置信度 | 近空白/页脚页；OCR 主要是噪声和页码，不作为正文语义页。 |
| 576 | 需要复核 | 近空白/页脚页；OCR 为空。 |
| 578 | 需要复核 | 近空白/页脚页；视觉复核未见可依赖正文。 |
| 598 | 需要复核 | 分隔/页脚页；OCR 仅识别“第二部分 - 标准”类页脚/分隔信息。 |
| 650 | 需要复核 | 分隔/页脚页；OCR 仅识别页码和“第二部分 - 标准”类页脚信息。 |
| 674 | 需要复核 | 近空白/页脚页；OCR 为空。 |
| 676 | 需要复核 | 近空白/淡水印页；OCR 为空。 |
| 710 | 需要复核 | 近空白/页脚页；OCR 为空。 |
| 810 | 需要复核 | 版权水印页；OCR 为空，不作为正文语义页。 |
| 811 | 需要复核 | 空白/封底内侧类页面；OCR 为空。 |

## OCR 工具安装结果

Tesseract OCR 可用路径：`C:\Program Files\Tesseract-OCR\tesseract.exe`。当前 Windows 用户 `Path` 已包含 `C:\Program Files\Tesseract-OCR`，因此新打开的用户终端可以直接运行 `tesseract`。

已安装或已验证的 Tesseract language data：

- `eng`：通用 English，用于英语（英国）和英语（美国）需求。
- `chi_sim`：简体中文。
- `chi_tra`：繁体中文，用于中国香港和中国台湾繁体中文需求。
- `fra`：法语。
- `deu`：德语。
- `jpn`：日语。
- `kor`：韩语。
- `lat`：拉丁语。它也可辅助识别汉语拼音这类拉丁字母文本，但中文转拼音仍需要单独的 transliteration 工具。
- `rus`：俄语。
- `ara`：阿拉伯语。
- `osd`：方向和文字系统检测。

Tesseract 标准 traineddata 不把英语拆成单独的 en-GB 和 en-US 包，不把繁体中文拆成单独的 zh-HK 和 zh-TW 包，也不提供独立的汉语拼音 OCR 语言包。上述通用语言/文字系统包是 Tesseract 的实际映射。

## 本地证据位置

text-only extraction manifest 位于 `.local/evidence/local_reference/manifest.json`。

text-only 人类可读摘要位于 `.local/evidence/local_reference/summary.md`。

外部工具 inventory 位于 `.local/evidence/local_reference/tool_inventory.json`。

PMBOK OCR manifest 位于 `.local/evidence/pmbok6_ocr/manifest.json`。

PMBOK OCR 人类可读本地摘要位于 `.local/evidence/pmbok6_ocr/summary.md`。

PMBOK OCR 逐页文本文件位于 `.local/evidence/pmbok6_ocr/pdf_ocr/`，保持被忽略状态。

PMBOK 渲染页面图片位于 `.local/evidence/pmbok6_ocr/pdf_images/`，保持被忽略状态。

## 外部项目 inventory 结果

inventory 以只读模式扫描了一个外部本地项目目录。该目录不是本仓库的 source truth。

发现的有用候选：

- `tools/doc_pipeline/scripts/find_poppler.ps1`：定位 Poppler 工具的 PowerShell helper；它是候选 adapter 模式，不是要盲目复制的文件。
- `tools/doc_pipeline/scripts/render_pdf_poppler.ps1`：通过 Poppler 渲染 PDF 页面的 PowerShell helper；它是候选 adapter 模式，不是要盲目复制的文件。
- `tools/poppler-25.07.0-0/poppler-25.07.0/Library/bin/pdftotext.exe`：第三方 Poppler 二进制；应作为本地安装工具处理，不作为仓库 source 提交。
- `intermediate/.../extract_sources.py`：项目专用抽取脚本；它们可以提供模式参考，但不应作为 source truth 复制。

Adapter 迁移已经在本仓库 `tools/evidence_adapters/` 下实现。第三方二进制仍然是本地安装依赖。

## 读取声明边界

本次运行证明本地文件已经存在抽取和 OCR 证据。它不证明每页或每篇文章都已经完成语义理解。

未来 lifecycle、white paper、market-requirements 或 implementation-plan 更新可以把本次运行作为抽取和 OCR 证据引用。对低置信度或被标记为需要复核的页面，仍需要二次 OCR 或人工复核后才能作出强声明。
