# 设计：Skills2CLI Routing 契约硬化

## Phase A 边界

Phase A 是 plan-freeze package。它只允许更新 OpenSpec artifacts、双语 implementation plan 与本地 worktree receipts。它不得修改 runtime code、`profiles.json`、helper scripts、checker logic、tests、user-level installed copies、`config.toml` 或 plugin cache files。

## Phase B 目标

Phase B 实现冻结后的 follow-up contract：

1. 为 routing、activation、governance 与 evidence scope 增加正交 schema fields；
2. 在保持 on-disk nested registry layout 的同时，把 `profile.task_module` 定义成一等逻辑语义；
3. 对 top-level profiles、scenario profiles 与 task modules 做 fail-closed positive scenario quality checks；
4. 增加行为测试，证明 `profile suggest` 与 `load_module` 不修改 `config.toml`、plugin cache，也不 apply profiles；
5. 为 `full` 增加显式 eligibility gate，使 warning pressure 与 audit evidence 只能影响排序，不能授予 eligibility；
6. 为 repo 与 installed `skills2cli.py`、`skills2cli_profile_registry_contract.py`、`profiles.json` 增加 install artifact surface reporting。

## 契约模型

`load_policy` 保留为 compatibility field。新的 registry entries 还必须暴露：

- `routing_scope`：`default_candidate`、`focused_candidate` 或 `explicit_only`；
- `activation_scope`：`soft_load_only` 或 `top_level_hard_load_preview`；
- `governance_scope`：`cross_project`、`repo_local_only` 或 `troubleshooting_only`；
- `evidence_scope`：`workflow_context_only`。

checker 必须验证兼容字段 `load_policy` 与这些正交字段映射一致。

## Task-module identity

Task module 的 canonical logical ID 是 `qualified_name=<profile>.<task_module>`。局部 `task_module` name 只在所属 top-level profile 内有效。Task modules 只是 soft-load guidance，不得定义独立 `hard_load`，不得成为 hard-load target，只有存在显式 inheritance marker 时才可以继承父 profile hints。

## Full-profile eligibility

`full` 与 `troubleshooting` scenario 都是 explicit-only。如果 `explicit_full_request=false`，`full` 不得成为 selected profile，只能出现在 `excluded_candidates` 并带 eligibility reason。如果 `explicit_full_request=true`，选择结果必须包含 `why_full_selected`，其值只能是：`explicit_all_plugins`、`explicit_broad_discovery` 或 `explicit_missing_plugin_capability`。

## 安全与证据

所有 suggestion 与 soft-load surfaces 继续保持 advisory。它们必须暴露 safety flags 与行为级证据，证明没有发生 profile apply、没有修改 config、没有修改 plugin cache，也没有产生 native expert evidence。远端发布不在本流程范围内。
