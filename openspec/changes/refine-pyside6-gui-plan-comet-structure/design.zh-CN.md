## 设计

### 选择的方案

采用完整 Comet 文档重构，而不是 tweak。PySide6 方案约束后续跨项目 runtime 和消费项目 GUI 工作，因此后续维护者需要一份不依赖聊天历史的可执行方案。

### 结构决策

方案采用与 `pi_plugin_codex_user_level_sidecar_plan.*` 相同的结构族：

1. 复核结论和 readiness metadata；
2. 关系模型与命名边界；
3. 目标与非目标；
4. 运行时架构和使用方式；
5. repo-local source of truth；
6. 共享 runtime 产物和 helper contract；
7. JSON/runtime 状态模型；
8. 门禁、回滚、风险和自检；
9. 有序实施事项和本地集成顺序。

方案也吸收 `comet_runtime_agile_focus_area_plan.*` 的控制语义：

- management record 是阶段证据，不是装饰；
- phase gate 需要明确 checklist 证据；
- Monitoring 是跨阶段控制回路，不是第六阶段；
- 文件所有权、证据留存和本地集成顺序必须显式。

### 关键边界决策

- 方案继续保持 `status: draft`；`plan_readiness` 记录结构 readiness。
- 共享 runtime readiness 不等于消费项目 GUI readiness。
- 消费项目拥有自己的 GUI 源码、adapter、测试、文档和 runtime contract。
- `project-local-override`、可见 GUI 验证和打包继续保持显式触发门。
- 当前工作不安装 PySide6，也不写入任何消费项目。

### 验证设计

验证聚焦 Markdown hygiene、OpenSpec validity、implementation-plan registry 与文本健康、precommit update/archive review、OpenSpec guard、local gate 和 local MR review。

### Comet 脚本限制

当前 Windows shell 可能没有可用 `bash`，而 Comet runtime 脚本是 `.sh`。因此 `.comet.yaml` 记录 `comet_script_state: blocked:bash_not_found_on_windows`；验证依赖 OpenSpec 和仓库 gate，不声称运行过的 Comet script transition 已通过。
