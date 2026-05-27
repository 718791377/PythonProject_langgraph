## 1. Open / Design Artifacts

- [x] 1.1 创建完整 Comet/OpenSpec change `refine-pyside6-gui-plan-comet-structure`。
- [x] 1.2 记录 proposal、design、management checklist、`.openspec.yaml` 和 `.comet.yaml`。
- [x] 1.3 将 Windows bash 不可用记录为 Comet script-state blocker，而不是伪造 transition 证据。
- [x] 1.4 创建 delta spec `pyside6-cross-project-gui-plan-contract`。

## 2. Superpowers Artifacts

- [x] 2.1 创建 design doc `docs/superpowers/specs/2026-05-27-pyside6-gui-plan-comet-design.md`。
- [x] 2.2 创建 implementation plan `docs/superpowers/plans/2026-05-27-refine-pyside6-gui-plan-comet-structure.md`。

## 3. Document Refactor

- [x] 3.1 将 PySide6 英文和中文方案对重写为完整 Comet 可执行方案结构。
- [x] 3.2 保留 PySide6 特定事实：共享 runtime 路径、本地-only runtime、消费项目所有权、per-project wrapper 默认策略和显式触发门。
- [x] 3.3 对齐 Pi sidecar 方案结构：复核结论、关系模型、目标/非目标、运行时架构、source of truth、contract、gate、rollback、risk 和 self-check。
- [x] 3.4 对齐 Comet runtime 语义：management record、phase gate、Monitoring return、implementation slice、文件职责图、本地集成顺序和证据留存。

## 4. Verification

- [x] 4.1 运行 `git diff --check`。
- [x] 4.2 运行 `openspec validate refine-pyside6-gui-plan-comet-structure --strict`。
- [x] 4.3 运行 `python .\tools\check_implementation_plan_rules.py --root . --json`。
- [x] 4.4 运行 `python .\tools\check_precommit_update_archive.py --root . --json`。
- [x] 4.5 运行 `python .\tools\run_openspec_guard.py --root .`。
- [x] 4.6 提交后运行 local gate 和 local MR review。
