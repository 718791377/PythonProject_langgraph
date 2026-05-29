# 变更：加固 Project MOE Phase 1 Readiness 输出契约

## 为什么

Project MOE GUI 方案仍有一个未关闭的 Phase 1 readiness schema 事项：readiness 检查器输出必须显式暴露 adaptation lane、blockers、warnings、checked files、脱敏路径以及 `control_mode_allowed`。其中部分值已经存在，但机器可读契约尚未提供显式的 `warnings`、`checked_files` 和 `redacted_paths` 字段。

## 改什么

- 给 Phase 1 readiness JSON payload 增加显式 `warnings`、`checked_files` 和 `redacted_paths` 字段。
- 保持既有 lane、blocker 和 control-mode 字段语义稳定。
- 为 Ready Lane 目标增加输出契约回归覆盖。
- 只有在测试证据存在后，才更新 Project MOE GUI 实施方案清单。

## 范围

- `tools/project_moe_gui_toolchain/src/project_moe_gui/toolchain.py` - 实现增量 readiness 证据字段。
- `test/project_moe_gui_toolchain.test.py` - 覆盖 ready 与 static-only readiness 输出契约。
- `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md` - 记录英文实施方案清单证据。
- `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md` - 记录中文实施方案清单证据。
- 本 OpenSpec 变更包。

## 非目标

- 不写入任何真实目标项目。
- 不为 `D:\PythonProject_paper_suggest` 或其他目标项目启用 GUI 控制。
- 不修改目标 Mode CLI 写命令。
- 不推送 GitLab/GitHub。

## 发布步骤

1. 创建本 OpenSpec 包和本地治理记录。
2. 增加 readiness 输出契约字段。
3. 增加定向回归断言。
4. 根据证据更新实施方案清单。
5. 运行定向测试、OpenSpec validation、仓库 guard、本地 gate 和本地 MR review。
6. 本地证据通过后合入本地 `main`。

## 回滚

- 回滚 feature branch 或本地 `main` 合入提交。
- 如果本地 `main` 已移动，使用集成前创建的 rollback ref。
- 本切片不会改变外部目标项目状态。

## 验证

- `python test\project_moe_gui_toolchain.test.py` - 运行定向 Project MOE GUI toolchain 回归套件。
- `openspec validate harden-moe-readiness-output-contract-20260528 --strict` - 验证 active OpenSpec delta。
- `python .\tools\check_precommit_update_archive.py --root . --json` - 执行提交前 update/archive review。
- `python .\tools\run_openspec_guard.py --root .` - 运行仓库 OpenSpec guard。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - 运行共享本地 CI gate。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - 运行本地 MR review gate。
