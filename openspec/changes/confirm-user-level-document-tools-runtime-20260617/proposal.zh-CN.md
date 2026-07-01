---
change_id: confirm-user-level-document-tools-runtime-20260617
status: proposed
owner: codex
created_at: 2026-06-17
translation_of: openspec/changes/confirm-user-level-document-tools-runtime-20260617/proposal.md
---

# 提案：确认用户级文档工具运行时

## 原因

上一轮可复用文档/PDF/向量工具提升已经把共享源码表面移动到 `D:\PythonProject_langgraph`，但在声明 live runtime 完成之前，当前 checkout 仍需要一个明确的后续确认包。当前证据显示仍有三个运行时确认缺口：

- 仓库本地 Poppler cache `.local/user_level_document_tools/` 尚未存在；
- 三个文档流水线 PowerShell 脚本当前无法通过 parser 检查；
- `D:\project` 仍保留旧工具副本且存在无关 dirty files，因此必须作为受 guard 保护的来源/消费项目处理，而不是无保护实现位置。

## What Changes

- 将 Stage 1 冻结为仅包含文档和治理的确认包；不声明 live runtime 完成。
- 记录 Stage 2 live runtime backlog：`.local/user_level_document_tools/` 下的 Poppler 本地 cache 确认、文档流水线 PowerShell parser/runtime 确认，以及向量/检索框架 smoke 确认。
- 确认 `D:\PythonProject_langgraph\tools\user_level_document_tools` 是共享源码和运行时确认主位置，`D:\project` 仅作为受保护的来源/消费方证据。
- 声明 Poppler `.local` cache 不纳入 Git 跟踪，真实向量数据和索引不迁入共享源码。
- 在任何消费侧清理或对照工作之前，要求对 `D:\project` 执行脏文件保护。

## 非目标

- 远程发布、GitLab MR 创建/合并或 GitHub 同步。
- 将 `D:\project` 的业务数据、受保护来源材料、guard 规则或 live 向量索引移动到本仓库。
- 从 `D:\project` 迁移向量数据库、embedding、JSONL 语料或其他 live retrieval 数据。
- 清理 `D:\project` 中的无关 dirty files。
- 仅为替换旧路径名而重写 archived OpenSpec 历史或历史实施计划。
