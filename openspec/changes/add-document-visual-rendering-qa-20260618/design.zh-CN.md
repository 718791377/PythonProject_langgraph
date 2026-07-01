---
change_id: add-document-visual-rendering-qa-20260618
status: proposed
owner: codex
created_at: 2026-06-18
---

# 设计：文档视觉渲染 QA

## 运行时边界

`D:\PythonProject_langgraph` 仍然是共享文档工具源码权威。`D:\project` 仍然是消费者/来源对照项目，本变更不得修改它。

运行时依赖位置固定如下：

- Poppler 与 `pdftoppm.exe` 位于被忽略的本地缓存，当前为 `D:\PythonProject_langgraph\.local\user_level_document_tools\poppler-25.07.0-0\poppler-25.07.0\Library\bin`。
- Python `pdf2image` 安装到文档流水线使用的项目虚拟环境，当前为 `D:\PythonProject_langgraph\.venv`。
- LibreOffice `soffice.exe` 安装在仓库外，通常为 `C:\Program Files\LibreOffice\program\soffice.exe`。

任何第三方应用载荷都不进入 Git 跟踪。

## 后端契约

Stage B runtime 应提供一个视觉 QA 编排器，接受 PDF 与 DOCX 输入，并把证据写入被忽略的 `.local/user_level_document_tools/` 输出根。

默认后端行为：

1. 对 PDF 输入，`pdftoppm` 是 Poppler 基线渲染器，可用时优先使用。
2. `pdf2image` 是可选 Python 渲染器，并必须报告它在 Windows 可靠渲染时仍依赖 Poppler 后端路径。
3. 对 DOCX 输入，`soffice/libreoffice` 是可选 DOCX 转 PDF fallback；转换后再使用选定 PDF 渲染器。
4. 缺失的可选后端输出 `skipped` 或 `unavailable` 证据，不得伪装为视觉 QA 成功。
5. 严格模式接受指定必需后端，任一必需后端不可用时失败。

## 证据契约

Stage B 应写出：

- 包含 `pdftoppm`、`pdf2image` 与 `LibreOffice` 行的检测报告；
- 视觉 QA JSON 报告，包含尝试后端、选定后端、跳过后端、失败原因、渲染文件数量与输出路径；
- 供操作者审阅的 Markdown 摘要；
- 位于被忽略 `.local/user_level_document_tools/visual_render_qa/` 下的渲染输出。

现有 `.local/user_level_document_tools/doc_quality_reports/` 报告根可继续保存摘要。现有 `.local/user_level_document_tools/renders/` 根仍可作为旧 Poppler 渲染输出位置。

## 实现切片

Stage A 合入本地 `main` 后，Stage B 至少有两个基本独立切片，因此满足 durable team 执行条件：

1. Runtime 后端切片：检测更新、`pdf2image` 渲染 helper、`soffice` DOCX 转 PDF wrapper、视觉 QA 编排器。
2. 测试/文档切片：依赖缺失测试、条件化成功 smoke、安装说明与配置示例。

主会话负责最终 fan-in、验证、本地提交、本地 `main` 合入，以及远程发布门前停止。

## 验证

基线测试必须在没有 `pdf2image` 或 LibreOffice 的机器上通过。后端实际存在时可以运行环境门控 smoke。验证必须包括 OpenSpec 检查、文档工具 focused 测试、本地 CI gate、本地 MR review，以及本地 main 集成 helper 证据。
