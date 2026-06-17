---
doc_id: reusable_document_pdf_vector_tools_promotion_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/reusable_document_pdf_vector_tools_promotion_plan.md
created_at: 2026-06-14
updated_at: 2026-06-18
---

# 可复用文档 PDF 向量工具提升方案

## 摘要

本 active 方案现在拆分为两段：Stage 1 先冻结确认方案与 live runtime backlog；Stage 2 再在 `D:\PythonProject_langgraph` 内执行 Poppler PDF 工具、文档处理流水线通用核心脚本、本地向量数据库/检索工具通用框架的 live runtime 确认。

除非后续用户消息明确点名 GitLab 或 GitHub 发布，否则远端发布不在本次范围内。

## 当前状态

<!-- CURRENT_STATUS_START -->

- Stage A 治理包已在本地集成，提交为 `802e458eaf5b3cdbed17e2bd419c73ecba3981c3`。
- 原始实现包已通过提交 `3fe2e42409f9f103bf9c727c2047f07e3493a23d` 本地集成，并把可复用工具表面加入 `tools/user_level_document_tools/`。
- 本 follow-up 确认包已在本地集成到 `cebc679f867af4a8fbba7fa4245c41f77c900ddf`，并记录 OpenSpec change `confirm-user-level-document-tools-runtime-20260617`。
- Stage 2 live runtime 确认从冻结后的本地 main 包创建 `implement-user-level-document-tools-runtime-20260618` 分支实施。
- local-only Poppler cache 已填充到 `.local/user_level_document_tools/poppler-25.07.0-0/` 作为运行时证据，且继续被 Git 忽略。
- `configure_doc_pipeline.ps1`、`detect_tools.ps1`、`export_pdf_to_docx_acrobat_com.ps1` 的文档流水线 PowerShell parser failures 已修复，并加入 parser 回归测试覆盖。
- 向量/检索 smoke 仍归本仓库共享工具所有，使用临时 JSONL manifest；消费者 live vector data、索引、embedding 缓存、来源权威和生成输出仍由消费者拥有。
- `D:\project` 继续作为受 guard 保护的消费者/来源对照项目；其无关 dirty files 被保留，Stage 2 未执行消费者清理。
- 未执行远端发布，当前仍停在远端发布审批门前。

<!-- CURRENT_STATUS_END -->

## 范围

- 在 `tools/user_level_document_tools/pdf_tools` 下维护可复用 Poppler/PDF 辅助 wrapper。
- 在 `tools/user_level_document_tools/doc_pipeline` 下维护可复用文档流水线核心脚本。
- 在 `tools/user_level_document_tools/vector_tools` 下维护通用向量/检索工具包和已脱敏 legacy adapter。
- 只维护示例配置；真实消费者配置仍由消费者项目拥有。
- 维护路径边界和向量工具冒烟行为回归测试，并登记到 CI manifest。

## 非目标

- 不移动 `D:\project` 数据、权威来源、guard 规则、权限策略、生成输出或消费者专用配置。
- 不提交第三方 Poppler 二进制、向量索引、embedding 缓存或私有来源材料。
- 未获明确远端发布授权前，不改变远端 ref、GitLab MR 或 GitHub 镜像。

## 任务清单

<!-- TASK_BACKLOG_START -->

- [x] 完成共享源码提升到 `tools/user_level_document_tools/`。
- [x] 在本 active implementation plan 对中冻结原始 Stage A 治理边界。
- [x] 复核可复用 PDF/Poppler 辅助工具提升、可复用文档流水线核心脚本提升，以及通用向量/检索框架提升。
- [x] 原始本地集成后停在远端发布审批门前。
- [x] Stage 1 follow-up：打开 `confirm-user-level-document-tools-runtime-20260617` 并冻结确认/运行时完成方案。
- [x] Stage 1 follow-up：验证、提交并把冻结确认方案集成到本地 `main`。
- [x] Stage 2 follow-up：执行 Poppler runtime 确认。
- [x] Stage 2 follow-up：执行文档流水线 parser/runtime 确认。
- [x] Stage 2 follow-up：执行向量/检索 smoke 确认。
- [ ] Stage 2 follow-up：验证、提交、集成到本地 `main`，并再次停在远端发布审批门前。

<!-- TASK_BACKLOG_END -->

## Stage Split

### Stage 1 冻结

- 仅包含文档与治理。
- 不声明 live runtime 已完成。
- 不清理 `D:\project` 消费者项目。
- 输出是已验证的 OpenSpec 确认包和刷新后的 implementation plan 对，并集成到本地 `main`。

### Stage 2 Live Runtime Backlog

- 填充 local-only Poppler cache：`.local/user_level_document_tools/poppler-25.07.0-0/`。
- 修复文档流水线 PowerShell parser/runtime 问题。
- 在不迁移 live vector data 的前提下确认向量/检索 smoke 行为。
- 更新 live 共享文档/config 示例；只有在取得 no-drift 证据后才更新 live `D:\project` 消费者文档。

## 证据索引

<!-- EVIDENCE_INDEX_START -->

- Stage A 治理包：`802e458eaf5b3cdbed17e2bd419c73ecba3981c3`。
- 原始实现包：`3fe2e42409f9f103bf9c727c2047f07e3493a23d`。
- 已提升可复用工具根目录：`tools/user_level_document_tools/`，包含 `pdf_tools/`、`doc_pipeline/`、`vector_tools/` 和 `config/*.example.json`。
- Stage 1 follow-up change：`openspec/changes/confirm-user-level-document-tools-runtime-20260617/` 记录确认边界和 Stage 2 runtime backlog。
- `.local/user_level_document_tools/` 是 runtime-local 且故意不跟踪；Poppler 二进制属于 live runtime 确认所需本地缓存，但不进入 Git。
- 向量数据、本地向量数据库、embedding 缓存和消费者填充配置仍由消费者项目拥有，未被提升。
- 边界回归测试：`test/user_level_document_tools.test.py`，已登记到 `tools/ci/ci_test_manifest.json`；覆盖必需表面、占位示例配置、无消费者绝对路径以及向量工具冒烟行为。
- Stage 2 runtime 证据：`.local/user_level_document_tools/poppler-25.07.0-0/` 已从 `D:\project\tools\poppler-25.07.0-0` 填充到被忽略的 worktree cache，数量为 455 个文件 / 55,664,757 字节；`test_poppler_access.ps1` 从 `.local` 报告 4/4 个 Poppler 工具可执行；所有被跟踪的 PowerShell 工具脚本 AST parser 均为 0 errors；`python test/user_level_document_tools.test.py` 覆盖必需表面、路径边界、PowerShell parser 回归和 vector JSONL validate/query smoke。
- 原始实现的本地 gate 证据：`powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Root . -StepTimeoutSeconds 900 -Json` 于 2026-06-15 返回 `ok: true`。
- 原始实现的本地 MR review 证据：`tools/ci/local_mr_review.ps1` 在清理前返回 `ok: true`。
- 原始实现的完成/清理证据：`.omx/session-claims/completed/promote-reusable-doc-pdf-vector-tools-20260614.json` 记录本地 main 集成、rollback ref `refs/backup/local-main/20260615-082051-before-promote-reusable-doc-pdf-vector-tools-20260614`、已删除本地分支、已移除 feature worktree，以及 `remote_publication_performed=false`。
- Stage 2 的 `D:\project` no-drift 证据：`git -C D:\project status --short --branch --untracked-files=all` 仍只报告既有的无关 `.codex/skills/comet-tweak/SKILL.md` 与 `.gitignore` 修改；Stage 2 未改动消费者项目文件。原始迁移 guard 证据仍为 `guard.cmd model end` 和 `guard.cmd verify` 返回 OK。

<!-- EVIDENCE_INDEX_END -->

## 验证计划

### Follow-up Confirmation Validation

Stage 1 确认包：

- `openspec validate confirm-user-level-document-tools-runtime-20260617 --strict --json` - 验证 follow-up OpenSpec 包。
- `python tools/run_openspec_guard.py --root . --tool codex --json` - 验证仓库 OpenSpec policy surfaces。
- `python tools/check_document_pair_policy.py --root . --base-ref main --json` - 验证已变更双语文档对。
- `python tools/check_precommit_update_archive.py --root . --json` - 在提交前验证 update/archive readiness。
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1 -StepTimeoutSeconds 1500 -Json` - 本地集成前验证共享 local/remote CI gate。
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json` - 本地 `main` 集成前验证 local merge review。

Stage 2 live runtime 包：

- 对 `tools/user_level_document_tools/**/*.ps1` 执行 PowerShell parser check - 证明文档流水线脚本语法可加载。
- 使用 `.local/user_level_document_tools/poppler-25.07.0-0/poppler-25.07.0/Library/bin` 运行 `tools/user_level_document_tools/*/scripts/test_poppler_access.ps1` - 证明 Poppler 可从本仓库 local cache 访问。
- `python -m unittest test/user_level_document_tools.test.py -v` - 证明共享工具边界和 vector JSONL smoke 行为。
- `D:\project` guard/no-drift 证据 - 证明消费者侧确认没有覆盖无关 dirty files 或受保护 source 目录。

- 目标可复用工具回归测试：`python test/user_level_document_tools.test.py` - 验证路径边界和 vector toolkit smoke 行为。
- OpenSpec change 验证：`openspec validate confirm-user-level-document-tools-runtime-20260617 --strict --json` - 验证当前 Stage 2 确认 change 包。
- 仓库 guard：`python tools/run_openspec_guard.py --root . --tool codex --json` - 验证 OpenSpec 和仓库 policy surfaces。
- 本地 CI gate：`powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1 -StepTimeoutSeconds 1500 -Json` - 验证共享 local/remote CI gate。
- 本地 MR review：`powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json` - 集成前验证 clean local merge review。
