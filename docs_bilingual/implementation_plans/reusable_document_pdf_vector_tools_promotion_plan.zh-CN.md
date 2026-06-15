---
doc_id: reusable_document_pdf_vector_tools_promotion_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/reusable_document_pdf_vector_tools_promotion_plan.md
created_at: 2026-06-14
updated_at: 2026-06-15
---

# 可复用文档 PDF 向量工具提升方案

## 摘要

本 active Stage A 方案授权本地实现切片：把可复用 Poppler PDF 辅助工具、文档处理流水线核心脚本，以及本地向量/检索框架辅助工具提升到 `D:\PythonProject_langgraph`。

除非后续用户消息明确点名 GitLab 或 GitHub 发布，否则远端发布不在本次范围内。

## 当前状态

<!-- CURRENT_STATUS_START -->

- Stage A 治理包已在本地集成，提交为 `802e458eaf5b3cdbed17e2bd419c73ecba3981c3`。
- 实现切片已通过提交 `3fe2e42409f9f103bf9c727c2047f07e3493a23d` 本地集成，并把可复用工具表面加入 `tools/user_level_document_tools/`。
- 本地 `main` 已包含该实现及后续本地提交；完成审计观察到的收口前本地 main head 为 `088045b20d3e48de470970e9a165eb9f55968d24`。
- 实现 feature 分支/worktree `promote-reusable-doc-pdf-vector-tools-20260614` 已在受保护的本地 main 集成后清理，完成 claim 已保存在 `.omx/session-claims/completed/`。
- 消费者项目数据、真实配置、权限、来源权威、输出路径和 guard 规则仍留在提升后的通用框架之外；已提升源码只包含示例配置。
- 未执行远端发布，当前仍停在远端发布审批门前。

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
- [x] 复核可复用 PDF/Poppler 辅助工具提升。
- [x] 复核可复用文档流水线核心脚本提升。
- [x] 复核通用向量/检索框架提升。
- [x] 本地 `main` 集成前验证测试、OpenSpec guard、本地 CI 和 local MR review。
- [x] 本地集成后停在远端发布审批门前。

<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->

- Stage A 治理包：`802e458eaf5b3cdbed17e2bd419c73ecba3981c3`（`治理：登记可复用文档PDF向量工具方案`）。
- 实现包：`3fe2e42409f9f103bf9c727c2047f07e3493a23d`（`提升可复用文档PDF向量工具`）。
- 已提升可复用工具根目录：`tools/user_level_document_tools/`，包含 `pdf_tools/`、`doc_pipeline/`、`vector_tools/` 和 `config/*.example.json`。
- 边界回归测试：`test/user_level_document_tools.test.py`，已登记到 `tools/ci/ci_test_manifest.json`；覆盖必需表面、占位示例配置、无消费者绝对路径以及向量工具冒烟行为。
- 本地 gate 证据：`powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Root . -StepTimeoutSeconds 900 -Json` 于 2026-06-15 返回 `ok: true`。
- 本地 MR review 证据：`tools/ci/local_mr_review.ps1` 在清理前对实现分支返回 `ok: true`。
- 完成/清理证据：`.omx/session-claims/completed/promote-reusable-doc-pdf-vector-tools-20260614.json` 记录了本地 main 集成、rollback ref `refs/backup/local-main/20260615-082051-before-promote-reusable-doc-pdf-vector-tools-20260614`、已删除本地分支、已移除 feature worktree，以及 `remote_publication_performed=false`。
- D:\project guard 证据：迁移工作后 `guard.cmd model end` 和 `guard.cmd verify` 均返回 OK，证明模型操作期间受保护源目录未漂移。

<!-- EVIDENCE_INDEX_END -->

## 验证计划

- 可复用工具目标回归测试：`python test/user_level_document_tools.test.py` - 验证路径边界和向量工具冒烟行为。
- OpenSpec 变更验证：`openspec validate promote-reusable-doc-pdf-vector-tools-20260614 --strict --json` - 验证 active 变更包。
- 仓库 guard：`python tools/run_openspec_guard.py --root . --tool codex --json` - 验证 OpenSpec 和仓库策略表面。
- 本地 CI 门禁：`powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1 -StepTimeoutSeconds 1500 -Json` - 验证本地/远端共用 CI gate。
- 本地 MR review：`powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json` - 验证集成前的本地合并复核。
