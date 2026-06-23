---
doc_id: project_expert_lens_agent_toml_schema_compatibility_plan
lang: zh-CN
status: active
plan_readiness: frozen-for-runtime-implementation
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/project_expert_lens_agent_toml_schema_compatibility_plan.md
created_at: 2026-06-23
updated_at: 2026-06-23
related_docs:
  - docs_bilingual/implementation_plans/project_expert_lens_agent_gui_toolchain_plan.zh-CN.md
  - docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md
---

# Project Expert Lens Agent TOML Schema 兼容性实施方案

> **给 agentic workers：** REQUIRED SUB-SKILL：存在独立切片时使用 `superpowers:subagent-driven-development`；否则使用 `superpowers:executing-plans`。保持 local-main-first 隔离，停止在远端发布门禁前，不要把 expert-lens 选择当作 native subagent 或 durable team 已运行的证据。

**目标：** 修复 repo-local native agent TOML schema 不兼容导致的 Codex 警告，同时保留 `D:\PythonProject_paper_suggest` 的 Project Expert Lens GUI 行为。

**架构：** Native Codex agent TOML 必须保持 schema-compatible，只包含 Codex 支持的顶层字段。Project Expert Lens 元数据不再写入自定义 TOML 表，而是通过既有 GUI config、目标项目 CLI、wrapper、startup hook、私有提示词文件和 state path 证明。

**技术栈：** Python stdlib `tomllib`、Project Expert Lens GUI toolchain、repo-local validation scripts、unittest、PowerShell local gates、Git worktrees、本地 main 优先集成。

---

## 当前状态

<!-- CURRENT_STATUS_START -->

- 状态：active，已冻结，可进入 runtime implementation。
- Stage A：本方案双语文件加 registry 登记是 local-main-first 冻结方案包。
- Stage A 记录用户明确不批准修改用户级 plugin cache；本方案不会修复 vendor/plugin-cache 文件。
- Stage B：runtime implementation 必须更新 B 仓库 source、checker、tests，将 bundle-managed plugin-cache frontmatter 归类为 report-only，然后更新 `D:\PythonProject_paper_suggest` live artifacts。
- 远端发布：不在范围内，除非用户后续明确要求。

<!-- CURRENT_STATUS_END -->

## 问题和决策

Codex 现在会拒绝 native agent role file 中未知顶层字段。目标文件 `D:\PythonProject_paper_suggest\.codex\agents\thesis-moe-mentor.toml` 当前有合法的 `name`、`description`、`developer_instructions`，但尾部还有 `[project]`、`[moe]`、`[dispatch]`、`[extensions]` 表；第一个被拒绝的表表现为 `unknown field project`。

决策：从 native agent TOML 中移除 Project Expert Lens 自定义元数据。本次不新增新的 sidecar 文件；使用已经安装的 `tools/project_moe_gui/project_moe_gui.config.json`、目标 mode CLI、wrapper、startup hook、`.omx/state/<namespace>/...` 和 `MOE.md` 来证明 Project Expert Lens readiness。

用户在冻结本方案期间明确不批准修改用户级全局 plugin cache。因此实现路径必须只改本仓库和目标项目：受本仓库/用户控制的 repo/user/system invalid frontmatter 继续 fail closed；bundle-managed plugin-cache invalid frontmatter 在没有单独明确 vendor-cache 修复授权前，只作为 report-only warning。

## 实施任务

<!-- TASK_BACKLOG_START -->

### Task 1：冻结 implementation plan 包

**文件：**
- 新建：`docs_bilingual/implementation_plans/project_expert_lens_agent_toml_schema_compatibility_plan.md`
- 新建：`docs_bilingual/implementation_plans/project_expert_lens_agent_toml_schema_compatibility_plan.zh-CN.md`
- 修改：`docs_bilingual/docs_registry.yaml`

- [x] 创建本双语方案，frontmatter 使用 `status: active` 和 `plan_readiness: frozen-for-runtime-implementation`。
- [x] 在 `docs_bilingual/docs_registry.yaml` 中登记为 active implementation plan。
- [x] 记录本次修复不得修改用户级 plugin cache。
- [ ] 运行方案校验和本地 pre-commit/update/archive review。
- [ ] 在 runtime implementation 开始前提交方案包并合入本地 `main`。

### Task 2：让 Skills frontmatter-resolution 对 plugin-cache 安全

**文件：**
- 修改：`tools/check_skills_audit_frontmatter_resolution.py`
- 修改：`test/check_skills_audit_frontmatter_resolution.test.py`
- 必要时修改：`tools/safety_rule_script_backing_registry.json`

- [ ] repo/user/system skill frontmatter invalid entries 继续 fail-closed。
- [ ] bundle-managed plugin-cache invalid frontmatter 只作为 report-only warning，不修改 plugin cache。
- [ ] checker 输出证明 `edits_plugin_cache=false`。
- [ ] 增加回归覆盖：repo/user/system blocking invalid entries 与 plugin-cache warning-only entries。

### Task 3：让 native agent TOML 校验 fail closed

**文件：**
- 修改：`tools/check_custom_agent_toml_schema.py`
- 修改：`test/check_custom_agent_toml_schema.test.py`

- [ ] 增加 native agent 顶层 key allowlist：`name`、`description`、`developer_instructions`、`model`。
- [ ] 拒绝其他顶层 key 或表，包括 `project`、`moe`、`dispatch`、`extensions`。
- [ ] 增加回归测试，证明包含 `[project]` 的 TOML 会失败。
- [ ] 保持现有 required-field 和 allowed-model 测试通过。

### Task 4：从 Project Expert Lens scaffold/readiness 中移除自定义 TOML 表依赖

**文件：**
- 修改：`tools/project_moe_gui_toolchain/src/project_moe_gui/toolchain.py`
- 修改：`test/project_moe_gui_toolchain.test.py`

- [ ] 更新 `phase1_agent_toml_template()`，新 scaffold 的 agent TOML 只包含 native Codex-compatible 字段。
- [ ] 更新 `inspect_agent_toml()`，不再要求 `[project]`、`[moe]`、`[dispatch]` 或 `[extensions]`。
- [ ] 保留对 `agent_name`、target config、private prompt boundary、state namespace、mode CLI commands、wrappers、startup hook 的 readiness 检查。
- [ ] 把原来期望 extension sections 的测试改为：拒绝 custom TOML tables，并接受 native-only agent TOML。
- [ ] 将 GUI toolchain patch version 升到下一版。

### Task 5：修复 A 项目 live runtime

**文件：**
- 修改目标项目：`D:\PythonProject_paper_suggest\.codex\agents\thesis-moe-mentor.toml`
- 刷新 managed GUI artifacts：`D:\PythonProject_paper_suggest\tools\project_moe_gui\...`

- [ ] 从目标 agent TOML 中删除 `[project]`、`[moe]`、`[dispatch]`、`[extensions]`，不改变角色主体。
- [ ] 使用更新后的 Project Expert Lens updater/installer 刷新 `D:\PythonProject_paper_suggest`。
- [ ] 提交 A 项目改动并合入 A 项目本地 `main`。
- [ ] 保留与本任务无关的 A 项目文件，并在汇报中单独说明 dirty/untracked 文件。

### Task 6：验证并收口

**B 仓库检查：**
- [ ] `python -m unittest test.check_custom_agent_toml_schema.test` - 验证 native agent TOML schema enforcement。
- [ ] `python -m unittest test.project_moe_gui_toolchain.test` - 验证 Project Expert Lens scaffold、readiness 与 installer compatibility。
- [ ] `python -m unittest test.check_skills_audit_frontmatter_resolution.test` - 验证 plugin-cache warning-only handling 且不修改用户级 cache。
- [ ] `python tools/check_custom_agent_toml_schema.py --root D:\PythonProject_paper_suggest --user-agents-dir D:\PythonProject_paper_suggest\.codex\agents --json` - 用修正后的 checker 验证真实 A 项目 agent TOML。
- [ ] `python tools/check_agent_skill_profile_surface_boundaries.py --root . --json` - 验证 native agent、skill 与 profile 边界仍然明确。
- [ ] `python tools/run_openspec_guard.py --root .` - 验证仓库治理与 OpenSpec guard 健康。
- [ ] `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1` - 验证 shared local CI gate。
- [ ] `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1` - 在集成前验证 local MR review gate。

**A 项目检查：**
- [ ] 用 `tomllib` 读取 `thesis-moe-mentor.toml`，确认不再包含未知自定义顶层 key。
- [ ] `D:\PythonProject_paper_suggest\project-moe-gui.cmd --preflight --json` 返回 `ok`。
- [ ] `D:\PythonProject_paper_suggest\project-expert-lens-gui.cmd --preflight --json` 返回 `ok`。
- [ ] `D:\PythonProject_paper_suggest\tools\ci\local_gate.ps1` 返回 `ok`。
- [ ] A 项目 `HEAD` 等于本地 `main` 的修复提交。

<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->

- pending：Stage A 方案校验、本地提交与本地 main 集成。
- pending：Stage B 必须让 `tools/check_skills_audit_frontmatter_resolution.py` 将 plugin-cache invalid frontmatter 作为 warning-only 报告，并保持 `edits_plugin_cache=false`。
- pending：Stage B source/runtime 测试与 A 项目 live validation。

<!-- EVIDENCE_INDEX_END -->

## 编排和证据规则

- 可用时对边界清晰的 review/implementation 切片使用 subagents；吸收结果后关闭 completed agent。
- 只有在方案冻结且存在至少两个独立执行切片后才启动 durable team。若 backend/tooling 阻塞，记录 blocker 并由主会话接管。
- expert timeout、stall 或 provider pacing 不是结果证据。
- 每次本地 merge 都必须通过既有 local-main-first helper 或等价 backup ref 留下 rollback evidence。
- 本方案不推送 GitLab/GitHub，也不修改远端 refs。
