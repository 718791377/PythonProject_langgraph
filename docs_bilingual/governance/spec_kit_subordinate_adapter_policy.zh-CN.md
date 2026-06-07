---
doc_id: spec_kit_subordinate_adapter_policy
lang: zh-CN
status: active
doc_class: governance
translation_of: docs_bilingual/governance/spec_kit_subordinate_adapter_policy.md
---

# Spec Kit 从属适配器政策

## 权威顺序

1. Native Codex 仍是本仓库的基础执行层。
2. Comet 负责协调 OpenSpec 的 WHAT 与 Superpowers 的 HOW。
3. OpenSpec 仍是本仓库的规格权威。
4. Superpowers 仍是实现方法指导层。
5. Spec Kit 只能作为可选从属 adapter、模板来源或文档参考被引用。

除非另一个单独的 active implementation plan 明确改变该边界并通过本地门禁，否则 Spec Kit 不是本仓库的项目治理权威。

## 允许用途

- 只有在明确说明其为从属参考背景时，才可以链接 Spec Kit 文档。
- `tools/spec_kit_subordinate_runtime.py` 只能以 dry-run 模式运行：`source-refresh`、`probe`、`plan-dry-run`、`init-dry-run` 与 `self-check-dry-run`；它只输出可审查 receipt，不得调用 Spec Kit。
- 可以将 Spec Kit 模板与 OpenSpec 或 Comet 工件对比，但不得复制或转移权威。
- 任何可复用想法都必须在保留上述权威顺序的前提下，经由仓库拥有的 plan、checker 或 OpenSpec change 承接。
## 没有单独 active plan 时阻止的用途

- 运行 `specify init` 或 `specify init --force`；这些命令可能初始化或覆盖规格权威。
- 在单独 active plan 授权精确读写边界前，运行 live `specify self check`。
- 添加 `.specify/`；该路径被视为治理/runtime 接管表面，而不是普通文档目录。
- 添加根目录 `specs/`；除非由单独 plan 拥有，否则该路径被视为生成的 Spec Kit 工件表面。
- 暴露生成的 `/speckit.*` slash command、`$speckit-*` skills-mode command、`.codex/commands/*speckit*`、`.codex/skills/*speckit*`、`.github/prompts/*speckit*`、根目录 `speckit.*` 或 `speckit-*` 文件、extension、preset 或 workflow output。
- 将 Spec Kit 描述为 primary source of truth、primary governance authority，或 Comet/OpenSpec/Superpowers 的替代品。
- 仅靠提示文本将仓库工作流所有权从 OpenSpec 或 Comet 转移到 Spec Kit。
## 未来 `specify` 命令边界

未来名为 `specify` 的命令只有在单独 active implementation plan 明确列出精确命令、目标路径、预期输出、回滚路径和验证门禁时才安全。该命令必须在隔离 feature worktree 中运行，输出必须先作为从属输入审查，任何被接受的结果都必须转换到仓库拥有的 surface，例如 `docs_bilingual/`、`openspec/` 或 Superpowers planning artifact。

如果这些条件缺失，在运行命令前停止，并报告 `blocked:spec_kit_scope_not_authorized`。

## 脚本支撑

`tools/check_spec_kit_authority_guard.py` - fail-closed checker，用来扫描不安全 Spec Kit 初始化、生成的 `.specify/`、根目录 `specs/`、`/speckit.*`、`$speckit-*`、extension、preset、workflow-output 与权威接管表面；它也校验 dry-run runtime receipt。

`tools/spec_kit_subordinate_runtime.py` - dry-run-only helper，支持 `source-refresh`、`probe`、`plan-dry-run`、`init-dry-run` 与 `self-check-dry-run`；它不安装 Spec Kit、不调用 `specify`、不写入生成的 Spec Kit 表面。

`tools/run_openspec_guard.py` - 聚合 guard，在仓库本地门禁中运行 Spec Kit authority checker。

`tools/ci/ci_test_manifest.json` - 本地 CI manifest，包含 `spec_kit_authority_guard.test.py` 与 `spec_kit_subordinate_runtime.test.py`，分别覆盖 authority-guard 与 subordinate-runtime 回归测试。
