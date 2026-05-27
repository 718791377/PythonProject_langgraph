# Project MOE GUI 计划完整 Comet 重构设计

## 背景

Project MOE Agent GUI 计划是长期实施方案。上一轮已经把它推向可执行方案风格；初始切片将它正式收口为完整 Comet / OpenSpec change。本延续切片再新增一项有界工具链行为：受保护卸载 `--apply`。

## 设计目标

- 让目标方案在脱离聊天历史的情况下也能作为可执行实施计划阅读。
- 保留 Project MOE 专属边界，而不是套用 Pi sidecar 的运行时边界。
- 明确 readiness 不等于 GUI 控制已就绪。
- 明确 Windows 上 Comet bash 不可用时的 fallback evidence。
- 对齐新版 Comet runtime 方案中的管理记录、阶段门禁、Monitoring 回退和证据留存语义。
- 仅允许卸载 apply 删除 manifest 声明、固定白名单内且 hash 已验证的 GUI 受管文件，同时保留目标项目私有表面。

## 结构选择

目标方案使用与 `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` 同级的组织方式：

- status / readiness / change 元数据；
- 复核结论；
- 关系模型与命名边界；
- goals / non-goals；
- runtime architecture；
- repo-local source of truth；
- target install artifacts and manifest；
- CLI / GUI / JSON contracts；
- safety / privacy / rollback；
- readiness gates；
- ordered implementation items；
- verification / governance updates / risks / self-check。

同时补入 `comet_runtime_agile_focus_area_plan.zh-CN.md` 的控制语义：

- management record 是阶段证据；
- phase gate 必须有 checklist 与 Monitoring 证据；
- Monitoring return 不是第六阶段，而是回到 Open / Design / Build / Verify 的控制回路；
- 实施 backlog 需要切片、事项级 checkbox、文件职责图、本地集成顺序和证据留存规则。

## 不变边界与受保护卸载边界

- 不安装 PySide6。
- 不向真实目标项目投放或适配；测试 fixture 中只验证受管安装产物的删除行为。
- 不创建或修改 user-level 目录。
- 不把 `D:\PythonProject_paper_suggest` 标记为 ready。
- 不复制目标项目私有提示源。
- 不伪造 Comet bash 脚本执行证据。
- `--apply` 仅可删除固定 Project MOE GUI 受管产物白名单中的文件。
- 除 manifest 自身外的受管文件必须保有匹配 hash；白名单外路径、缺失 hash、hash 不匹配或目录条目都必须在删除前阻断。
- `MOE.md`、`.codex/agents/*.toml` 与 `.omx/state` 永不作为卸载删除对象。

## 验证策略

验证同时覆盖文档/治理证据与有界运行时行为：

- `git diff --check`；
- `openspec validate refine-project-moe-gui-plan-comet-structure --strict`；
- `python .\tools\check_implementation_plan_rules.py --root . --json`；
- `python .\tools\check_precommit_update_archive.py --root . --json`；
- `python .\tools\run_openspec_guard.py --root .`；
- `python test\project_moe_gui_toolchain.test.py`，覆盖受保护卸载 apply 成功与 fail-closed 路径；
- commit 后运行 local gate 与 local MR review。
