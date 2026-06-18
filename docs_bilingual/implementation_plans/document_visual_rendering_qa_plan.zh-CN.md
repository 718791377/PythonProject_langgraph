---
doc_id: document_visual_rendering_qa_plan
lang: zh-CN
doc_class: implementation_plan
status: active
translation_of: docs_bilingual/implementation_plans/document_visual_rendering_qa_plan.md
change: add-document-visual-rendering-qa-20260618
base_ref: e30cd8d7448787fd086d41c135adde8ecd46698e
---

# 文档视觉渲染 QA 实施方案

> 面向 agentic worker：使用 subagent-driven-development 或 executing-plans 逐项执行本方案。Stage A 与 Stage B 必须保持为两个本地 main 集成包。

**目标：** 通过 Poppler `pdftoppm`、Python `pdf2image` 与 `soffice/libreoffice` 为 PDF/DOCX 文档交付物增加诚实的视觉渲染 QA，同时不把消费者状态移回共享源码。

**架构：** Stage A 只冻结本方案与 OpenSpec 契约。Stage B 在现有文档流水线脚本下增加一个编排器和窄后端 helper；检测与测试在可选工具缺失时必须安全降级。

**技术栈：** PowerShell 流水线脚本、Python helper、OpenSpec artifacts、基于 unittest 的仓库测试、本地 main 优先 Git 工作流。

## Stage A：冻结方案包

文件：

- 创建 `openspec/changes/add-document-visual-rendering-qa-20260618/`，包含 proposal、design、tasks、management 与 delta spec 文件。
- 创建 `docs_bilingual/implementation_plans/document_visual_rendering_qa_plan.md` 与 `.zh-CN.md`。
- 更新 `docs_bilingual/docs_registry.yaml`，登记新的实施方案双语文件。

步骤：

1. 记录依赖位置：
   - Poppler/`pdftoppm`：被忽略的 `.local/user_level_document_tools/poppler-25.07.0-0/.../Library/bin`。
   - `pdf2image`：项目虚拟环境 `.venv`。
   - LibreOffice/`soffice.exe`：外部 Windows 安装目录，通常为 `C:\Program Files\LibreOffice\program\soffice.exe`。
2. 冻结后端行为：
   - 可选后端输出 `skipped` 或 `unavailable` 证据。
   - 严格必需后端缺失时输出结构化失败证据。
   - `pdf2image` 不是 Poppler 替代品；在 Windows 可靠渲染时仍依赖 Poppler 后端路径。
3. 验证 Stage A：
   - `openspec validate add-document-visual-rendering-qa-20260618 --strict` - 验证 Stage A OpenSpec delta 合约。
   - `python .\tools\check_document_pair_policy.py --root . --base-ref main --json` - 验证变更 Markdown 的双语配对覆盖。
   - `python .\tools\check_precommit_update_archive.py --root . --json` - 检查提交准备度、archive 延期和必要注册更新。
   - `python .\tools\run_openspec_guard.py --root . --tool codex --json` - 运行完整仓库 OpenSpec guard 栈。
4. 使用中文提交标题提交 Stage A；local gate 与 local MR review 通过后，通过 `tools/complete_local_flow_to_remote_gate.py --execute` 合入本地 `main`。

## Stage B：Runtime 实现包

文件：

- 修改 `tools/user_level_document_tools/doc_pipeline/scripts/detect_tools.ps1`，报告 `pdftoppm`、`pdf2image` 与 LibreOffice 的视觉 QA readiness。
- 创建 `tools/user_level_document_tools/doc_pipeline/scripts/render_pdf_pdf2image.py`，负责 Python `pdf2image` 渲染与 JSON/Markdown 证据。
- 创建 `tools/user_level_document_tools/doc_pipeline/scripts/export_docx_to_pdf_soffice.ps1`，负责 LibreOffice DOCX-to-PDF 转换证据。
- 创建 `tools/user_level_document_tools/doc_pipeline/scripts/visual_render_qa.ps1`，作为后端编排器。
- 修改 `tools/user_level_document_tools/doc_pipeline/scripts/run_doc_quality_check.ps1`，暴露 `-RunVisualQa` 与可选严格后端要求。
- 更新 `tools/user_level_document_tools/config/doc_pipeline_config.example.json`、`install_dependency_notes.md` 与 `doc_pipeline_setup_guide.md`，加入脱敏、可复用的视觉 QA 指引。
- 修改 `test/user_level_document_tools.test.py`，加入依赖安全的行为测试。

任务：

1. 先写失败测试，覆盖：
   - 必需新脚本存在；
   - PowerShell parser 覆盖新脚本；
   - 检测 JSON 包含 `pdftoppm`、`pdf2image` 与 `LibreOffice` 行；
   - 可选后端缺失时无未处理崩溃；
   - 严格后端要求在必需后端不可用时失败；
   - `pdftoppm` 成功 smoke 仅在可检测到时运行。
2. 用稳定 schema 实现检测/报告变更：
   - Schema field glossary: `backend` means renderer backend; `installed` means discovery result; `usable` means runnable now; `probe_status` means probe outcome; `path` means executable or package path; `version` means detected version text; `notes` means operator-safe diagnostics.
3. 实现 `render_pdf_pdf2image.py`：
   - CLI 接受输入 PDF、输出目录、报告目录、任务名、DPI 与可选 Poppler 路径。
   - 包缺失或 Poppler 依赖缺失时返回结构化失败，不只输出 traceback。
4. 实现 `export_docx_to_pdf_soffice.ps1`：
   - 从配置、PATH 或常见安装路径解析 `soffice.exe`；
   - 写出 JSON/Markdown 转换证据；
   - LibreOffice 不存在时干净失败。
5. 实现 `visual_render_qa.ps1`：
   - 接受 PDF 或 DOCX 输入；
   - 接受 `-Backends` 与 `-RequireBackends`；
   - 默认将视觉 QA JSON/Markdown 摘要与渲染 artifact 写入 `.local/user_level_document_tools/visual_render_qa/`；
   - 记录 selected、skipped、failed 与 unavailable 后端。
6. 仅在提供 `-RunVisualQa` 时让 `run_doc_quality_check.ps1` 调用视觉 QA，默认保持现有行为。
7. 更新设置文档和配置示例，不引入消费者绝对路径或被跟踪二进制载荷。

## 验证计划

Focused 命令：

```powershell
python .\tools\ci\run_python_tests.py --root . --pattern user_level_document_tools.test.py
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\user_level_document_tools\doc_pipeline\scripts\detect_tools.ps1 -ReportDir .\.tmp\doc_tools_smoke\detect
```

完整本地集成 gate：

```powershell
openspec validate add-document-visual-rendering-qa-20260618 --strict
python .\tools\check_document_pair_policy.py --root . --base-ref main --json
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root . --tool codex --json
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 1500 -Json
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json
```

环境门控 runtime smoke：

- Poppler 可用时用 `pdftoppm` 渲染一页 PDF。
- `pdf2image` 可导入且 Poppler 可用时，用 `pdf2image` 渲染同一 PDF。
- 仅在 `soffice.exe` 可用时，用 LibreOffice 转换最小 DOCX。

## 协作计划

- Stage A：主会话负责写文件和本地集成；因为冻结方案尚未存在，专家保持 advisory，durable team 阈值未满足。
- Stage B：Stage A 合入本地 `main` 后使用 durable/persistent team，因为 runtime 与测试是两个独立执行切片。
- Runtime worker 负责后端脚本与编排器。
- 测试/文档 worker 负责测试、配置示例与设置文档。
- Leader 负责 fan-in、验证、提交、本地 main 合入、清理与远程发布门前停止。

## 假设

- 用户已经确认默认可选后端行为和严格模式。
- 未授权远程发布。
- `D:\project` 保持不被触碰。
- Poppler 二进制、LibreOffice 二进制、生成渲染图像与填充后的 runtime config 保持不被跟踪。

## 当前状态

<!-- CURRENT_STATUS_START -->
- Stage A 处于方案冻结与本地集成阶段，工作树分支为 `add-document-visual-rendering-qa-20260618-plan`。
- Stage B 运行时实现在 Stage A 合入本地 `main` 后启动。
- 远程发布未授权，集成后停在远程发布门。
<!-- CURRENT_STATUS_END -->

## 任务积压

<!-- TASK_BACKLOG_START -->
- Stage A：完成 OpenSpec 变更、方案文档、注册表更新、本地 gate 与 MR review，然后合入本地 `main`。
- Stage B：实现 `pdf2image`、`soffice` 与 `pdftoppm` 视觉渲染 QA 脚本与检测合约。
- Stage B 验证：增加单元测试、配置示例、安装文档与可用环境的门控 smoke。
<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- `openspec/changes/add-document-visual-rendering-qa-20260618/` - Stage A OpenSpec 变更证据。
- `test/user_level_document_tools.test.py` - Stage B focused 回归测试证据。
- `.local/user_level_document_tools/` - Stage B 视觉 QA 的本地忽略 runtime 缓存与输出根。
<!-- EVIDENCE_INDEX_END -->
