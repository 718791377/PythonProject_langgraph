# 变更：用完整 Comet 治理重构 General 模板实施计划

## 为什么
General 与 General_2 中文实施计划需要更清晰、可冷启动执行的结构。旧文档混合历史说明、目标模板事实、Comet 澄清和 live-session context，容易导致执行边界错误。

## 变更内容
- 将 `PythonProject_General` 计划重构为 fuller governance template 计划。
- 将 `PythonProject_General_2` 计划重构为 local Git + OpenSpec + Superpowers + native subagents only 计划。
- 增加 template implementation-plan governance 的稳定 OpenSpec 要求。
- 记录本次重构的 Comet/Superpowers 设计、实施、验证和归档证据。

## 影响
不修改 consumer project，不执行远端发布。未来模板工作会更清楚地区分 Comet、OpenSpec、Superpowers、native subagents、oh-my-codex、native_omx、LangGraph、MCP scope、launcher payload 和 repo-local durable state。
