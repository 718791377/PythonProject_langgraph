# 任务：增加文档视觉渲染 QA

## Stage A：冻结方案

- [x] 确认 Poppler `pdftoppm`、Python `pdf2image` 与 LibreOffice `soffice.exe` 的安装/使用位置。
- [x] 创建 OpenSpec change 与双语 design/proposal/task artifacts。
- [x] 在 `docs_bilingual/implementation_plans/` 下创建双语实施方案。
- [x] 在 runtime 修改前定义可选后端与严格后端行为。
- [x] 验证、提交并将 Stage A 方案冻结包合入本地 `main`。

## Stage B：实现 live runtime

- [x] 更新检测逻辑，报告 `pdftoppm`、`pdf2image`、`LibreOffice` 与视觉 QA readiness。
- [x] 增加 `pdf2image` PDF 渲染 helper，并输出结构化 JSON/Markdown 证据。
- [x] 增加 `soffice/libreoffice` DOCX 转 PDF fallback wrapper，并输出结构化证据。
- [x] 增加视觉渲染 QA 编排器，并接入文档质量检查流程。
- [x] 增加依赖缺失降级、严格后端失败、条件化成功 smoke 测试。
- [x] 更新安装/依赖说明与脱敏配置示例。
- [ ] 验证、提交并将 Stage B runtime 包合入本地 `main`。
