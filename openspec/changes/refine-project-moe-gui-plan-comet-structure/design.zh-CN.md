## 设计

### 选择的方式

本次采用完整 Comet 文档重构，而不是 tweak。目标文件是长期实施方案，会驱动后续工具链实现，因此需要可追溯的 OpenSpec 产物、delta spec、设计记录、实施计划和明确的归档延期记录。

### 结构决策

方案按 `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` 的新版结构组织：

1. 复核结论与 readiness 元数据；
2. 关系模型与命名边界；
3. 目标与非目标；
4. 运行时架构与使用方式；
5. repo-local source of truth；
6. 目标项目安装产物与 manifest；
7. CLI / GUI / JSON contract；
8. 安全、隐私、rollback 与卸载；
9. readiness lanes；
10. 有序实施事项、验证计划、相关文档更新要求、风险与自检。

同时复用 `comet_runtime_agile_focus_area_plan.zh-CN.md` 的控制语义：

- management record 是阶段证据，不是装饰性说明；
- 阶段门禁需要 checklist 证据与清晰的 Monitoring 决策；
- Monitoring 回退是跨阶段控制回路，不是第六阶段；
- 实施工作用切片加事项级 checkbox 表达；
- 文件职责、本地集成顺序和证据留存必须明确。

### 关键边界决策

- 方案保持 `status: draft`，因为它不是运行时完成声明。
- `plan_readiness` 只表示结构已就绪、可以进入实现切片，不表示 GUI 控制已经 ready。
- 目标项目继续拥有 Agent TOML、私有提示源、Phase 1 CLI 与 `.omx/state`。
- 本仓库继续拥有共享 GUI 工具链源码、模板、checker 和 installer。
- GUI 永远不直接编辑目标状态 JSON；它只能调用目标项目 CLI contract。
- 既有 `D:\PythonProject_paper_suggest` 证据保持 blocked / repair-lane，直到未来 readiness checker 证明其可以进入 Ready Lane。
- 本 change 的中文支撑 artifacts 必须是合法 UTF-8 中文，不能是乱码或问号占位。

### 验证设计

本次是文档与方案结构重构，验证重点是：

- Markdown / diff hygiene；
- OpenSpec change 有效性；
- implementation plan frontmatter / structure guard；
- precommit update/archive gate 与 archive deferral；
- 仓库 OpenSpec guard；
- commit 后 local gate 与 local MR review。

### Comet 脚本限制

当前 Windows shell 不暴露可用 `bash`，而 Comet runtime 脚本是 `.sh`。因此 `.comet.yaml` 记录 `comet_script_state: blocked:bash_not_found_on_windows`，并以 OpenSpec artifacts、管理记录、任务清单和仓库 guard 作为 fallback evidence。不得声称 `comet-state.sh` 或 `comet-guard.sh` 已通过。
