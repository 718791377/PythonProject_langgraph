## 1. Open / Design 产物

- [x] 1.1 创建完整 Comet/OpenSpec change `refine-project-moe-gui-plan-comet-structure`。
- [x] 1.2 记录 proposal、design、management checklist 与 `.comet.yaml`。
- [x] 1.3 将 Windows bash 不可用记录为 Comet 脚本状态 blocker，而不是伪造 transition。
- [x] 1.4 创建 delta spec `project-moe-agent-gui-plan-contract`。

## 2. Superpowers 产物

- [x] 2.1 创建设计文档 `docs/superpowers/specs/2026-05-27-project-moe-gui-plan-comet-design.md`。
- [x] 2.2 创建实施计划 `docs/superpowers/plans/2026-05-27-refine-project-moe-gui-plan-comet-structure.md`。

## 3. 文档重构

- [x] 3.1 将 `project_moe_agent_gui_toolchain_plan.md` 与 `.zh-CN.md` 重写为完整 Comet 可执行方案结构。
- [x] 3.2 保留 Project MOE 专属 contract：Phase 1 / Phase 2、Ready / Bootstrap / Repair lanes、目标安装边界、JSON state contract 与隐私规则。
- [x] 3.3 增加明确的 readiness 元数据与自检清单。
- [x] 3.4 对齐 `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` 的结构：复核结论、关系模型、目标/非目标、运行时架构、source of truth、安装产物、CLI/JSON/state contract、门禁、回滚、风险和自检。
- [x] 3.5 对齐 `comet_runtime_agile_focus_area_plan.zh-CN.md` 的语义：管理记录、阶段门禁、Monitoring 回退、实施切片、文件职责图、本地集成顺序和证据留存。
- [x] 3.6 修复本 change 下的中文 OpenSpec / Superpowers 支撑 artifacts，避免乱码或问号占位。

## 4. 验证

- [x] 4.1 运行 `git diff --check`。
- [x] 4.2 运行 `openspec validate refine-project-moe-gui-plan-comet-structure`。
- [x] 4.3 运行 `python .\tools\check_implementation_plan_rules.py --root . --json`。
- [x] 4.4 运行 `python .\tools\check_precommit_update_archive.py --root . --json`。
- [x] 4.5 运行 `python .\tools\run_openspec_guard.py --root .`。
- [x] 4.6 保持 feature worktree 干净后提交本地 feature 分支。
- [ ] 4.7 commit 后运行 `.\tools\ci\local_mr_review.ps1`。
