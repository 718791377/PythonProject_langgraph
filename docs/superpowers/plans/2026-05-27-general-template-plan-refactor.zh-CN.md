---
change: refactor-general-template-plans-comet
design-doc: docs/superpowers/specs/2026-05-27-general-template-plan-refactor-design.md
base-ref: ab5e1c1
archived-with: openspec/changes/archive/2026-05-27-refactor-general-template-plans-comet
---

# General 模板计划重构实施计划中文对照

> **给 agentic workers：** 这个变更是单切片文档重构，使用 `superpowers:executing-plans` 即可；不需要 native subagent fan-out。

**目标：** 重构两份中文 General 模板实施计划，使它们 decision-complete、UTF-8 clean，并与完整 Comet 治理对齐。

**架构：** 保持 `PythonProject_General` 与 `PythonProject_General_2` 两个能力层级分离；用 OpenSpec 记录长期可复用要求，用两份计划作为 operator-facing handoff。

## 任务
- [x] 建立 Comet/OpenSpec archive evidence 与稳定 spec。
- [x] 重构 General_2 local-only 实施计划。
- [x] 重构 General fuller-governance 实施计划。
- [x] 运行本地验证并提交本地 Git 仓库。
