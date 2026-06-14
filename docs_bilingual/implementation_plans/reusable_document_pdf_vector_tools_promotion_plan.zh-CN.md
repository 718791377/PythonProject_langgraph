---
doc_id: reusable_document_pdf_vector_tools_promotion_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/reusable_document_pdf_vector_tools_promotion_plan.md
created_at: 2026-06-14
updated_at: 2026-06-14
---

# 可复用文档 PDF 向量工具提升方案

## 摘要

本 active Stage A 方案授权本地实现切片：把可复用 Poppler PDF 辅助工具、文档处理流水线核心脚本，以及本地向量/检索框架辅助工具提升到 `D:\PythonProject_langgraph`。

除非后续用户消息明确点名 GitLab 或 GitHub 发布，否则远端发布不在本次范围内。

## 当前状态

<!-- CURRENT_STATUS_START -->

- Stage A 治理包在代码/工具切片复核前记录可复用工具边界。
- 实现切片必须把消费者项目数据、真实配置、权限、来源权威、输出路径和 guard 规则留在被消费项目内，不进入提升后的通用框架。
- Feature 分支为 `promote-reusable-doc-pdf-vector-tools-20260614`。
- 预期本地暂停点是合入本地 `main` 后停在远端发布审批门前。

<!-- CURRENT_STATUS_END -->

## 范围

- 在 `tools/user_level_document_tools/pdf_tools` 下添加可复用 Poppler/PDF 辅助 wrapper。
- 在 `tools/user_level_document_tools/doc_pipeline` 下添加可复用文档流水线核心脚本。
- 在 `tools/user_level_document_tools/vector_tools` 下添加通用向量/检索工具包和已脱敏 legacy adapter。
- 只添加示例配置；真实消费者配置仍由消费者项目拥有。
- 添加路径边界和向量工具冒烟行为回归测试，并登记到 CI manifest。

## 非目标

- 不移动 `D:\project` 数据、权威来源、guard 规则、权限策略、生成输出或消费者专用配置。
- 不提交第三方 Poppler 二进制、向量索引、embedding 缓存或私有来源材料。
- 未获明确远端发布授权前，不改变远端 ref、GitLab MR 或 GitHub 镜像。

## 任务清单

<!-- TASK_BACKLOG_START -->

- [x] 在本 active implementation plan 对中冻结 Stage A 治理边界。
- [ ] 复核可复用 PDF/Poppler 辅助工具提升。
- [ ] 复核可复用文档流水线核心脚本提升。
- [ ] 复核通用向量/检索框架提升。
- [ ] 本地 `main` 集成前验证测试、OpenSpec guard、本地 CI 和 local MR review。
- [ ] 本地集成后停在远端发布审批门前。

<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->

- Pending implementation evidence: feature branch `promote-reusable-doc-pdf-vector-tools-20260614` 将在本地集成前记录 local gate 和 local MR review 证据。

<!-- EVIDENCE_INDEX_END -->

## 验证计划

- 可复用工具目标回归测试：`python test/user_level_document_tools.test.py` - 验证路径边界和向量工具冒烟行为。
- OpenSpec 变更验证：`openspec validate promote-reusable-doc-pdf-vector-tools-20260614 --strict --json` - 验证 active 变更包。
- 仓库 guard：`python tools/run_openspec_guard.py --root . --tool codex --json` - 验证 OpenSpec 和仓库策略表面。
- 本地 CI 门禁：`powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1 -StepTimeoutSeconds 1500 -Json` - 验证本地/远端共用 CI gate。
- 本地 MR review：`powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json` - 验证集成前的本地合并复核。
