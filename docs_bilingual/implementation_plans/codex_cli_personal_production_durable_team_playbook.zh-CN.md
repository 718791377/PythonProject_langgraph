---
doc_id: codex_cli_personal_production_durable_team_playbook
lang: zh-CN
canonical: docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_playbook.md
translation_of: docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_playbook.md
doc_class: implementation_plan
status: draft
---

# Codex CLI 个人开发者生产级持久化团队 Playbook

## 目的

本 playbook 把个人开发者生产级持久化团队 draft 目标拆成冷启动维护者可以照着执行的 release slices。Draft 目标解释架构；本 playbook 解释下一步如何做。

## 固定规则

- OpenSpec - 用于结构性仓库变更的规格驱动治理工具。
- native Codex - Codex CLI 原生能力基线，必须继续作为底层能力保留。
- `C:\Users\lenovo\.codex\config.toml` - 用户级 Codex 配置文件；没有操作者明确同意不得修改。
- `native_omx`、`omx team` 和 LangGraph runtime apply mode - 运行时变更入口；只有 release slice 明确允许时才能启动。
- `.omx/state/` - 每个仓库自己的 repo-local durable state 目录，不能跨项目共享。
- local GGUF model files - 本地大模型二进制文件，必须排除在普通 Git 之外。


## 权威栈与同构链接

本 playbook 是执行程序文件。它不替代权威计数地图、白皮书、研究正本或 PMI 裁剪文件；每个 release slice 在改变架构、治理深度或运行时行为之前，都必须回链到相关权威文件。


- Codex 持久化团队平台目标：12 层主干层级、4 个虚拟部门、24 个责任域、18 个横切模块、48 个核心文档、12 个受治理 AI Agent、12 本推荐书籍。权威清单是 `docs_bilingual/product_lifecycle/codex_platform_inventory_map.zh-CN.md`。
- 一人公司经营系统目标：12 层主干层级、5 个虚拟部门、30 个责任域、20 个横切模块、60 个核心文档、15 个受治理 AI Agent、15 本推荐书籍、12 个最小启动文档。权威清单是 `docs_bilingual/product_lifecycle/one_person_company_inventory_map.zh-CN.md`。
- 白皮书与研究正本：`docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.zh-CN.md` 保持战略叙事角色，`docs_bilingual/governance/solo_maintainable_production_persistent_team_research.zh-CN.md` 保持证据密集的运行时/治理研究正本角色。除非后续受治理变更证明其中一个生命周期角色已经失效，否则不要物理合并。
- 10 层到 12 层桥接：使用 `docs_bilingual/product_lifecycle/ten_to_twelve_layer_bridge.zh-CN.md` 把 10 层运行时研究模型映射到 12 层产品/商业生命周期模型。
- PMI 裁剪：当 release slice 需要过程组式的输入、工具与技术、输出，或需要在完整架构、整个项目轻量、阶段局部轻量、模块级轻量与混合治理之间作决定时，使用 `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.zh-CN.md` 与 `docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.zh-CN.md`。

## Release Slice 模板

每个 release slice 必须定义：

- `goal` - 本切片要实现的目标。
- `non_goals` - 本切片不得做的事情。
- `preconditions` - 开始前必须满足的状态。
- `file_scope` - 允许修改的文件或目录。
- `forbidden_scope` - 禁止修改的文件或目录。
- `commands` - 必须运行的命令。
- `evidence` - 证明切片有效的证据。
- `rollback` - 撤销本切片的方法。
- `runtime_apply_allowed` - 是否允许 runtime mutation。

## R0.6.x 只读 Gate 切片

### R0.6.2 Read-Only State Sampling

目标：采样一个目标仓库的 durable status，不启动团队，也不写 durable state。

允许范围：status scripts、read-only reports、documentation 与 fixtures。

禁止范围：`.omx/state/`、真实用户级 Codex 配置与 OpenClaw business state。

是否允许 runtime apply：否。

### R0.6.3 Dry-Run Routing Decision

目标：解释 no-team、`native_omx` 或 `langgraph` 的选择原因，但不启动 durable team。

允许范围：dry-run decision helpers、fixtures 与 documentation。

禁止范围：worker launch、LangGraph checkpoint mutation 与 automatic team apply。

是否允许 runtime apply：否。

### R0.6.4 Expected-Result Fixture

目标：为预期 dry-run decision 创建 regression fixtures。

允许范围：fixture files、checker logic 与 documentation。

是否允许 runtime apply：否。

### R0.6.5 Cross-Project Read-Only Review

目标：证明消费方仓库状态不会泄漏到编排仓库。

允许范围：inventory reports、fixture descriptions 与 read-only checkers。

是否允许 runtime apply：否。

## 本地模型资产迁移切片

目标：文档化并在后续实施把本地 llama 与 GGUF 模型资产集中管理在 `D:\PythonProject_langgraph` 下，同时允许 OpenClaw 通过 provider profiles 启动或调用这些服务。

前置条件：

- 两个仓库都必须通过 `git status --short --branch` 这个 dirty-work 检查命令确认 clean。
- 复制模型文件前，必须已有 `.local/`、`.runtime/`、`*.gguf` 与 `*.GGUF` 这些 Git ignore 规则。
- 修改 OpenClaw 接线前，必须先文档化 provider profiles。

允许范围：

- migration plan - 迁移方案文档。
- provider policy - provider 边界治理文档。
- profile templates - profile 模板。
- health-check design - 健康检查设计。
- documentation - 文档。

禁止范围：

- real GGUF files - 真实大模型文件。
- `.omx/state/` - 仓库本地 durable state 目录。
- OpenClaw domain-agent state - OpenClaw 领域 Agent 状态。
- user-level Codex configuration - 用户级 Codex 配置。

是否允许 runtime apply：本 documentation slice 不允许；后续本地迁移只有在操作者明确动作后才允许复制被 Git 忽略的文件。

证据：

- `git check-ignore -v` - 解释模型路径命中哪条 ignore 规则的 Git 命令输出。
- `git status --short --branch` - 模型复制后证明仓库 clean 的 Git 状态命令输出。
- provider profile health-check report - 后续允许 runtime testing 时的 provider 健康检查报告。

回滚：

- tracked 文档和脚本变更通过 Git revert 回滚。
- ignored 本地模型文件需要由操作者手动移动或删除。

## Expert Routing Playbook

有界多面研究先运行同质 analyst fan-out。只有 analyst fan-in 显示需要架构设计或执行排序时，才使用 architect 或 planner。

没有完成的 subagent 不得被静默跳过。必须记录 role、prompt scope、wait windows、last signal、suspected cause、action taken，以及是否使用了它的结果。

## 验证

发布 release slice 前运行：

- `openspec validate --all` - 验证所有 active 与 stable OpenSpec specs 的命令。
- `python .\tools\run_openspec_guard.py --root . --tool codex --json` - 聚合仓库 OpenSpec 与治理检查的命令。
- `python .\tools\check_name_clarity_rules.py --root . --json` - 检查脚本、路径、命令、变量、profile 与 role 是否有简短解释的命令。
- `git diff --check` - 检查空白符问题的 Git 命令。
