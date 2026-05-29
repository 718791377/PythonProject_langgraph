## 为什么

`project_moe_agent_gui_toolchain_plan.zh-CN.md` 已经完成过一次结构重构，但仍需要完整 `/comet` 包来保留 Open / Design / Build / Verify 证据、archive deferral、顺序化任务和 readiness lane 说明。本轮继续实施该方案中的受保护卸载切片，避免后续工作把“方案结构完成”和“目标项目 GUI runtime 完成”混为一谈，同时把卸载 apply 从 plan-only blocker 推进为可验证的安全能力。

## 变更内容

- 重构并维护 `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan*.md`，使其与新版 Pi sidecar 方案族保持同级结构：目标、架构、source of truth、contract、gate、rollback、risk、自检与验证顺序。
- 维护完整 Comet/OpenSpec active-change 包：proposal、design、delta spec、tasks、management 和 `.comet.yaml`。
- 维护 Superpowers design 与 implementation-plan 记录，使本次重构和后续切片具备持久设计/执行说明。
- 明确 `D:\PythonProject_paper_suggest` 仍是 blocked / repair-lane 证据，不得误标为 ready。
- 显式记录 archive deferral：feature branch 提交后，archive 等待后续本地集成与验证决策。
- 继续实施一个有界运行时切片：`plan_project_moe_gui_uninstall.py --apply` 只删除白名单内且 hash 已验证的 Project MOE GUI 受管文件，并保留目标项目私有提示源、Agent TOML 和 `.omx/state`。

## 能力

### 新增能力

- `project-moe-agent-gui-plan-contract`：约束 Project MOE GUI 实施方案必须具备清晰的文档结构、readiness metadata、GUI runtime completion 边界、远端发布边界，以及受保护卸载 apply 行为。

### 修改能力

- 无既有 stable capability 被修改。本 change 添加的是 active document/runtime contract 上下文，stable spec 只有在后续 archive 时才会提升。

## 影响

- 受影响文档：`docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan*.md`、`docs_bilingual/operations/project_moe_gui_usage.zh-CN.md`
- 受影响代码/测试：`tools/project_moe_gui_toolchain/`、`test/project_moe_gui_toolchain.test.py`
- 受影响 OpenSpec artifacts：`openspec/changes/refine-project-moe-gui-plan-comet-structure/`
- 受影响 Superpowers artifacts：`docs/superpowers/specs/2026-05-27-project-moe-gui-plan-comet-design.md` 与 `docs/superpowers/plans/2026-05-27-refine-project-moe-gui-plan-comet-structure.md`
- 本 change 不安装依赖、不做真实目标项目适配、不推送 GitLab/GitHub、不安装 PySide6；目标项目写入仅限 fixture 测试和显式卸载 `--apply` 命令合同。

## 治理字段

- `impact_scope`: 文档方案、active OpenSpec artifacts，以及有界 Project MOE GUI uninstall-apply 工具链行为。
- `explicit_non_goals`: 目标项目适配 rollout、PySide6 安装、远端发布、user-level config mutation。
- `rollout_sequence`: feature worktree -> 受保护卸载 apply 实现 -> 文档/spec 更新 -> 本地验证 -> feature branch commit -> 本地 main 集成决策。
- `rollback_plan`: revert feature branch commit，或将本地分支重置到变更前基线。
- `validation_path`: `git diff --check`、`openspec validate`、implementation-plan checker、precommit update/archive gate、OpenSpec guard、Project MOE 定向测试、local gate、local MR review。
- `mainline_classification`: 仓库用户级编排产品线中的 Project MOE GUI 文档与工具链实施 lane。
