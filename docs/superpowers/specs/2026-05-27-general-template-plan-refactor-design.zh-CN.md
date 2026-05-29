---
change: refactor-general-template-plans-comet
status: archived
archived-with: openspec/changes/archive/2026-05-27-refactor-general-template-plans-comet
---

# General 模板计划重构设计中文对照

## 问题
两份中文实施计划混合了历史说明、目标模板事实和 live session notes。冷启动读者难以区分 fuller governance 的 `PythonProject_General` 与 local-only 的 `PythonProject_General_2`。

## 设计决策
- `PythonProject_General` 是 fuller governance template，可以模板化 oh-my-codex、native_omx、LangGraph 兼容源码、MCP scope、launcher payload 和 gate parity。
- `PythonProject_General_2` 是 local-only template，只保留本地 Git、OpenSpec、Superpowers governance 和 native Codex subagents。
- Comet 只表示 OpenSpec + Superpowers governance，不是 subagent evidence、durable backend 或 OpenSpec 替代品。

## 文档结构
每份实施计划都写成冷启动可执行的 handoff：目标、非目标、能力边界、实施顺序、验证命令、验收标准和回滚路径。

## 验证
验证路径包括 UTF-8 clean 写入、OpenSpec validation、implementation-plan checks、OpenSpec guard、local gate 和 local MR review。
