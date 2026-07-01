---
change_id: confirm-user-level-document-tools-runtime-20260617
status: proposed
owner: codex
created_at: 2026-06-17
translation_of: openspec/changes/confirm-user-level-document-tools-runtime-20260617/design.md
---

# 设计：用户级文档工具运行时确认

## 边界

`D:\PythonProject_langgraph` 拥有文档/PDF/向量工具线的可复用实现源码。`D:\project` 是消费/来源对照项目，拥有自己的 guard、dirty-file 状态、受保护来源策略、项目数据和运行时输出。

共享源码边界是：

- `tools/user_level_document_tools/pdf_tools/` - 可复用 Poppler 与 PDF 辅助脚本。
- `tools/user_level_document_tools/doc_pipeline/` - 可复用文档处理流水线核心脚本。
- `tools/user_level_document_tools/vector_tools/` - 通用本地向量与检索框架辅助工具。
- `tools/user_level_document_tools/config/*.example.json` - 已脱敏示例配置文件。
- `test/user_level_document_tools.test.py` - 边界与 smoke 回归测试。

本地运行时边界是：

- `.local/user_level_document_tools/poppler-25.07.0-0/` - 用于 runtime 确认的 ignored portable Poppler cache。
- `.local/user_level_document_tools/doc_quality_reports/` - ignored 本地文档质量报告输出。
- `.local/user_level_document_tools/renders/` - ignored 本地渲染输出。

消费方拥有的边界仍在共享源码之外：

- 填充后的消费方配置；
- 向量索引和 embedding 缓存；
- 来源权威和受保护材料；
- 生成的交付物与报告；
- `D:\project` guard 状态和无关 dirty files。

## 确认矩阵

- **Stage 1 确认的共享源码**
  - `tools/user_level_document_tools/pdf_tools/` - 可复用 PDF helper 源码。
  - `tools/user_level_document_tools/doc_pipeline/` - 可复用文档流水线源码。
  - `tools/user_level_document_tools/vector_tools/` - 可复用向量/检索 helper 源码。
  - `tools/user_level_document_tools/config/*.example.json` - 已脱敏配置模板。
- **本地运行时资产，不纳入 Git 跟踪**
  - `.local/user_level_document_tools/poppler-25.07.0-0/` - 本地 Poppler runtime cache。
  - `.local/user_level_document_tools/doc_quality_reports/` - 本地质量报告输出。
  - `.local/user_level_document_tools/renders/` - 本地渲染输出。
- **不迁移**
  - `D:\project\config\...` 中的真实配置
  - 向量索引、embedding 缓存和本地向量数据库
  - 受保护来源权威和生成输出
- **消费方保护**
  - `D:\project` 仍受 guard 保护
  - 无关 dirty files 会阻止基于假设的清理
  - Stage 2 只有在先收集 no-drift 证据后，才可以更新 live consumer docs

## Stage 1 冻结

Stage 1 只冻结确认计划和本地集成边界，不声明 live runtime 完成。它记录剩余 Stage 2 backlog，验证 OpenSpec/计划卫生，在 feature 分支提交冻结计划包，并通过既有 local-main-first helper 集成到本地 `main`。

Stage 1 期间 durable team 阈值尚未满足，因为计划仍在冻结。

## Stage 2 Live Runtime

Stage 2 是第一次允许执行 runtime 修复或 cache 填充变更的阶段。Stage 1 集成到本地 `main` 后，Stage 2 可拆成三个独立实现切片：

1. Poppler/PDF 本地 cache 和访问确认。
2. 文档流水线 PowerShell parser 和运行时确认。
3. 向量/检索框架 smoke 和边界确认。

当冻结计划中有两个或更多切片同时活跃时，可以采用 durable-team 或 LangGraph-backed 编排。主会话仍负责 fan-in、最终验证和本地 main 集成。

## D:\project 处理

`D:\project` 当前有无关 dirty files。Stage 2 不得覆盖或清理这些文件。任何消费侧清理都必须使用该仓库的 guard 流程，并保留项目拥有的 `config`、`data/local_vector_db` 和 `.project-runtime/local-vector-db`，除非后续明确计划改变这些边界。

可更新活文档和操作指南，使其指向共享 LangGraph 工具位置；但 archived OpenSpec changes 和历史实施计划应保留为历史证据。
