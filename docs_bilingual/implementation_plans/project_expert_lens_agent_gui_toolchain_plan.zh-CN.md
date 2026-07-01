
---
doc_id: project_expert_lens_agent_gui_toolchain_plan
lang: zh-CN
status: active
plan_readiness: canonical-rename-ready-for-runtime-implementation
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/project_expert_lens_agent_gui_toolchain_plan.md
created_at: 2026-06-17
updated_at: 2026-06-17
source_plan: docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md
legacy_alias_policy: preserve-project-moe-compatibility
---

# 项目专家镜头智能体控制台工具链实施方案

> **给智能体执行者：**按 local-main-first 隔离流程实施。本方案把 `Project MOE` 视为历史兼容名称，不再把 MOE 解释成大模型内部的 Mixture-of-Experts。GUI 中的专家镜头选择只是路由输入，不是 native subagent、durable team 或 LangGraph 已执行的证据。

**目标：**把原 Project MOE Agent GUI 迁移为 **Project Expert Lens Agent GUI / 项目专家镜头智能体控制台**。它管理面向项目与会话的“专家镜头”，这些镜头类似智能体专家视角，由当前会话模型在下一轮消息中选择使用；它不是大模型内部混合专家架构。

**架构：**本仓库维护可复用 GUI 工具链、启动器、安装器、检查器、PySide6/QML 界面与验证夹具。目标项目保留自己的会话、状态、私有提示词和 Phase 1 CLI。GUI 只能通过目标项目 CLI 合约写入状态，并可生成交接包，供主会话、native experts、durable team、persistent team 或 LangGraph workflow 使用。

**兼容：**继续保留 `project_moe_gui`、`project-moe-gui.cmd`、`tools/project_moe_gui/`、`thesis-moe-*`、`list-lenses`、`set-lenses`、`clear-lenses` 等旧名称作为兼容别名。新增可见名称优先使用 `Project Expert Lens Agent GUI`、`project-expert-lens-gui`、`expert lens`、`expert_lenses`。

---

## 当前状态

<!-- CURRENT_STATUS_START -->

- 状态：active 方案，准备按两阶段本地优先流程落地。
- 阶段 A：记录 canonical 命名与兼容合约，登记 registry，提交并合入本地 `main`。
- 阶段 B：实施 runtime、QML、launcher、Workbench 与测试改动，再提交并合入本地 `main`。
- 远端发布：不在本轮范围内，除非用户明确要求 GitLab/GitHub 发布。

<!-- CURRENT_STATUS_END -->

## 命名模型

| 层级 | canonical 新名称 | legacy 兼容名称 |
| --- | --- | --- |
| 产品 | Project Expert Lens Agent GUI / 项目专家镜头智能体控制台 | Project MOE Agent GUI |
| 概念 | expert lens / 专家镜头 | MOE lens / MOE expert |
| 启动脚本显示 | project-expert-lens-gui | project-moe-gui |
| JSON 显示字段 | selected_expert_lenses, selected_expert_categories, effective_expert_lens_mode | selected_lenses, selected_categories, effective_lens_mode |
| 动作 | list-expert-lenses, set-expert-lenses, clear-expert-lenses | list-lenses, set-lenses, clear-lenses |

规则：

1. `MOE` 只能解释为历史项目/工具链名称，不能再解释为大模型内部 Mixture-of-Experts 实现。
2. 专家镜头是当前会话模型可调用的一种专业视角。
3. 选择专家镜头不等于证明 subagent、durable worker、persistent team 或 LangGraph workflow 已经运行。
4. 旧 Python 包名、QML bridge、运行时目录与 Phase 1 路径在完成迁移验证前必须继续兼容。

## Runtime 与 GUI 要求

1. 新增 install、update、check 的 canonical wrapper，并委托到现有实现。
2. 新增目标项目 canonical 启动器 `project-expert-lens-gui.cmd`、`project-expert-lens-gui-silent.vbs`，同时保留旧启动器。
3. 窗口标题、关闭弹窗、会话标签、Workbench 文案与 QML 文本改用 Expert Lens / 专家镜头语义。
4. 增加 expert-lens 动词的读写 action alias，同时保留旧 action token。
5. 增加 canonical JSON mirror 字段，同时保留 legacy 字段。
6. Workbench handoff target 增加 `main-session`、`native-experts`、`subagent`、`durable-team`、`persistent-team`、`langgraph-workflow`。
7. 保持旧 Python import package、QML bridge object name、runtime directory、目标项目 Phase 1 兼容路径稳定。
8. 更新测试，把 canonical 显示名称和 legacy ABI 兼容断言分开。
9. 本仓库合入本地 `main` 后，才通过安装/更新路径刷新 `D:\PythonProject_paper_suggest`，并验证新旧启动器。

## 编排边界

- GUI 控制每个项目/会话可用的专家镜头池。
- 主 Codex 会话仍是 leader，决定直接使用一个或多个镜头，还是把 brief 路由给 native experts、durable team、persistent team、native_omx 或 LangGraph。
- GUI 可以生成 handoff package 和复制提示词，但不能直接 spawn subagent、启动 durable team、启动 LangGraph workflow、调用模型 API 或修改远端发布状态。
- expert timeout、durable worker stall 或 provider pacing 都不是有效结果证据，必须通过重试、缩窄 delegation、durable handoff 或主会话接管处理。

## 任务清单

<!-- TASK_BACKLOG_START -->

- [x] 新建 canonical 双语实施方案。
- [x] 不直接改写超大 legacy 方案文件；把它保留为历史实施记录。
- [x] 在 `docs_bilingual/docs_registry.yaml` 登记 canonical 方案对。
- [x] 运行方案阶段验证并提交 Stage A。
- [x] 把 Stage A 合入本地 `main`，必要时清理方案 feature worktree。
- [x] 新增 canonical installer/updater/checker wrapper。
- [x] 在 `project_moe_gui` runtime 中增加 canonical 常量与显示标签。
- [x] 新增 canonical 目标项目启动器与 manifest 项，同时保留旧启动器。
- [x] 增加 canonical action alias 与 JSON mirror 字段。
- [x] 更新 PySide6 fallback UI 与 QML 文本为 Expert Lens / 专家镜头语义。
- [x] 更新 Workbench handoff 文案、artifact metadata 与 handoff targets。
- [x] 更新 canonical 命名与 legacy ABI 兼容测试。
- [ ] 运行 focused tests、static checks、OpenSpec guard、local gate 与 local MR review。focused runtime tests 已通过；更广泛的 gate 仍在本 worktree 中待完成。
å®æã
- [ ] 把 Stage B 合入本地 `main`，并停在远端发布门禁前。
- [ ] 如果目标项目写入权限和 sandbox 条件允许，刷新 A 项目安装并验证新旧启动器。

<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-17 Stage A 证据：canonical 计划对已登记到 registry，并已合入本地 `main`。
- 2026-06-17 Stage B focused runtime 证据：canonical wrappers、launchers、action aliases、JSON mirror fields、Workbench targets、QML wording 已在 `feature/implement-expert-lens-gui-runtime` 实现；`python test/project_moe_gui_toolchain.test.py` 已通过 108 个测试；broader gates 仍待完成。
- pending implementation evidence：Stage B broader gates、本地 main 合入、目标项目刷新仍待完成。
- 2026-06-17 Stage B focused runtime è¯æ®ï¼canonical wrappersãlaunchersãaction aliasesãJSON mirror fieldsãWorkbench targetsãQML wording å·²å¨ `feature/implement-expert-lens-gui-runtime` å®ç°ï¼`python test/project_moe_gui_toolchain.test.py` å·²éè¿ 108 ä¸ªæµè¯ï¼broader gates ä»å¾
å®æã
- pending implementation evidenceï¼Stage B broader gatesãæ¬å° main åå
¥ãç®æ é¡¹ç®å·æ°ä»å¾
å®æã

<!-- EVIDENCE_INDEX_END -->

## 验证计划

- 方案阶段：`git diff --check`，`python tools/check_implementation_plan_rules.py --root . --json`，`python tools/check_precommit_update_archive.py --root . --json`。
- runtime focused tests：`python -m unittest test.project_moe_gui_toolchain.test`。
- 本地 main 合入前 gate：`python tools/run_openspec_guard.py --root .`，`powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1 -StepTimeoutSeconds 1200`，`powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1`。
- 可选视觉验证：共享 PySide6 runtime 可用时，对 Sessions 和 Workbench 执行 GUI visual render check。

## 回滚

- Stage A 回滚：删除本方案双语文件和 docs registry 记录。
- Stage B 回滚：删除新增 canonical wrapper 与显示别名，但不得删除目标项目里现有的 managed `project_moe` 产物。
- 目标项目回滚：使用 installer manifest 与目标项目生成的 rollback notes。
