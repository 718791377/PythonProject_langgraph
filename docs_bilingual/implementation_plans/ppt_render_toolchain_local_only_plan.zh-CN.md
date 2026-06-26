---
doc_id: ppt_render_toolchain_local_only_plan
lang: zh-CN
doc_class: implementation_plan
status: active
translation_of: docs_bilingual/implementation_plans/ppt_render_toolchain_local_only_plan.md
canonical_path: docs_bilingual/implementation_plans/ppt_render_toolchain_local_only_plan.md
zh_cn_path: docs_bilingual/implementation_plans/ppt_render_toolchain_local_only_plan.zh-CN.md
---
# PPT 渲染工具链本地化方案

## 目的

冻结本仓库用于共享 PPT 制作、PPTX 转 PDF/PNG 渲染和视觉 QA 的本地治理包。该工具链服务于受保护的消费项目，例如 `D:\project`。

运行时目标是把仓库管理的 PPT 渲染工具全部放在 `D:\PythonProject_langgraph` 之下，使用显式可执行文件路径和单进程范围环境变量，不修改系统 PATH、用户 PATH、机器 PATH 或全局 pip 镜像配置。

## Stage A 边界

Stage A 只包含本双语实施方案和 `docs_bilingual/docs_registry.yaml` 注册项。它必须先合入本地 `main`，然后 Stage B 的非文档实现才能通过本地 MR 评审。

Stage A 不得添加可执行工具链 helper、测试、二进制安装器、本地 `.local/` 证据或消费项目输出文件。

## Stage B 范围

Stage B 可以在 `tools/user_level_document_tools/ppt_tools/` 增加共享源码，可以更新共享文档工具配置示例和 README，也可以扩展 `test/user_level_document_tools.test.py`。

Stage B 必须把本地二进制工具、本地渲染配置、现场 smoke deck、包清单和渲染证据排除在跟踪源码之外。这些产物应放在被忽略的本地路径，例如 `D:\PythonProject_langgraph\.local\ppt_render_tools`。

## 工具链要求

Stage B 必须提供不依赖现场二进制即可解析或测试的探针和状态标记，并能报告以下主机状态：

- Python 包可用性，包括 `pdf2image`、`python-pptx`、COM 支持包、Aspose.Slides、Pillow、NumPy、OpenCV、python-docx 和 openpyxl。
- PowerPoint COM 就绪状态，包括交互式会话状态、`PowerPoint.Application` 创建、PPTX 创建、导出、清理和进程泄漏检查。
- 通过 `auto`、`powerpoint`、`soffice` 或 `aspose` 引擎完成 PPTX 转 PDF/PNG 渲染。
- 视觉 QA 状态值：`visual_qa:pass`、`visual_qa:degraded`、`visual_qa:blocked`、`visual_qa:manual_required` 和 `visual_qa:not_applicable`。

## 安全要求

Stage B 不得修改永久环境状态。源码、示例和测试必须避免 `setx`、用户或机器 PATH 注册表编辑，以及写入 `HKCU\Environment`、`HKLM` 或机器级环境变量的路径。

如果 PowerPoint COM 因非交互桌面或 `0x80070520` 等错误被阻断，Stage B 必须把它记录为 blocked 或 fallback 证据。只有 COM 探针成功时，才允许声称 PowerPoint COM 渲染通过。

Aspose.Slides 仅作为 fallback 渲染器，除非配置了有效许可证。若出现评估水印且没有干净渲染器可用，必须分类为 degraded 或 manual-required。

## Stage B 验证计划

Stage B 必须运行用户级文档工具 focused tests、OpenSpec guard、local gate、本地 MR review，并在主机具备可用本地渲染器时记录 live smoke 证据。

预期证据包括：

- `test/user_level_document_tools.test.py` 的 focused unit test 输出；
- `python .\tools\run_openspec_guard.py --root .`；
- `.\tools\ci\local_gate.ps1 -Root .`，并使用足够的 step timeout；
- `.\tools\ci\local_mr_review.ps1 -Root . -Base main -Head HEAD`；
- 被忽略 `.local/` 路径下的 capability 和 render smoke JSON 证据。

## 本地集成与发布边界

Stage A 和 Stage B 都采用 local-main-first 集成。通过本地 gate 只授权合入本地 `main`，不授权 GitLab push、GitLab MR 创建或合并、GitHub sync、远程 ref 删除或任何远程发布动作。

## 当前状态

<!-- CURRENT_STATUS_START -->
- Stage A 已在本方案中冻结，准备先合入本地 `main`，再确认 Stage B 实现。
- Stage B 预期只增加共享跟踪源码；运行时二进制和 smoke 证据保持为本地忽略产物。
- 尚未授权远程发布。
<!-- CURRENT_STATUS_END -->

## 任务待办

<!-- TASK_BACKLOG_START -->
- Stage A：增加本双语实施方案和 docs registry 条目，验证、提交、合入本地 `main`，并停止在远程发布门前。
- Stage B：增加 PPT 渲染工具链 helper、示例、文档、测试、本地化运行证据、本地 gate、本地 MR review、本地 `main` 集成，并停止在远程发布门前。
<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- Stage A 计划证据：本实施方案双语文件、docs registry 条目、pre-commit update/archive 检查、OpenSpec guard、本地提交、rollback ref、本地 main 集成 receipt 和 completed claim。
- Stage B 计划证据：跟踪的 helper/test/doc 提交、包清单 JSON、capability probe JSON、PowerPoint COM probe JSON、smoke render JSON、focused tests、OpenSpec guard、local gate、本地 MR review、rollback ref、completed claim 和 cleanup record。
<!-- EVIDENCE_INDEX_END -->
