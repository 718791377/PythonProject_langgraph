---
doc_id: pyside6_first_consumer_apply_2026_05_22
lang: zh-CN
status: active
doc_class: implementation_evidence
translation_of: docs_bilingual/memory/pyside6_first_consumer_apply_2026-05-22.md
---

# PySide6 首个消费项目 apply 证据 - 2026-05-22

目标消费项目：`D:\PythonProject_OpenClaw`。

## 变更内容

- 新增项目本地 GUI 包 `src/pythonproject_openclaw_gui/`。
- 新增 `tools/gui/pyside6_runtime_contract.json`、`tools/gui/run_gui.ps1`、`tools/gui/check_pyside6_env.py` 和 adapter 指南。
- 新增 `tests/test_gui_import.py` 与 `docs/pyside6_gui_rollback.md`。
- 新增 OpenClaw 双语操作文档：`docs_bilingual/operations/pyside6_shared_runtime_gui.md` 与 `.zh-CN.md`。
- 未修改 OpenClaw 依赖文件和 lockfile；默认模式仍为共享 runtime。

## 验证结果

- 共享 runtime Python：`D:\PythonProject_langgraph\.shared_runtimes\pyside6\.venv\Scripts\python.exe`。
- import-only smoke：`tools/gui/check_pyside6_env.py --project-root D:\PythonProject_OpenClaw --json` 返回 `import_only_verified=true`。
- 版本：Python 3.12.10、PySide6 6.11.1、Qt 6.11.1。
- 额外 import-only 测试：显式设置 `PYTHONPATH` 后，`test_gui_import.test_gui_package_imports_without_visible_window()` 通过。
- OpenClaw 本地 main 集成后，本地 gate、本地 MR review 和 OpenSpec guard 均通过。

## Git 证据

- `b2380c9`：启用 OpenClaw 共享 runtime PySide6 GUI 壳。
- `8ddf273`：集成主目录后修正 runtime contract 的 `project_root`。
- `986b827`：修复 OpenClaw PySide6 中文操作文档编码。
- 首次快进本地 main 前的回滚 ref：`refs/backups/local-main-before-pyside6-shared-gui-20260522070544`。
- 未执行远端发布。

## 边界

- 未启动可见 GUI。
- 未新增 OpenClaw 本地 PySide6 依赖或 lockfile。
- project-local override 和可执行文件打包仍是未实施的按需 opt-in 阶段。