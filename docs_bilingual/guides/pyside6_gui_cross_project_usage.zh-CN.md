---
doc_id: pyside6_gui_cross_project_usage
lang: zh-CN
status: active
doc_class: guide
translation_of: docs_bilingual/guides/pyside6_gui_cross_project_usage.md
created_at: 2026-05-21
---

# PySide6 GUI 跨项目操作指南

本指南说明如何通过本仓库的 `plugin-modules`、`pyside6-gui` 和 `soft-load` 为消费项目启用本地桌面 GUI。默认不改变当前 plugin profile，不会安装 PySide6 到消费项目，不会编辑 `config.toml`，不会启用 plugin bundle，也不会默认启动可见 GUI。

默认运行时是本仓库维护的共享 PySide6 runtime：

```text
D:\PythonProject_langgraph\.shared_runtimes\pyside6
```

## 1. 适用场景

当项目需要本地桌面 GUI、PySide6、Qt、Windows 桌面工具或小型操作台时使用本指南。不得只凭本指南宣称项目已经 `shared_runtime_ready`、`project_gui_verified_with_shared_runtime`、`packaged` 或 `release_ready`。

## 2. soft-load PySide6 模块

从编排仓库运行模块加载器，并传入模块名和仓库根目录：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\skill_sources\plugin-modules\scripts\load_module.ps1 pyside6-gui -RepoRoot <orchestration-repo> -Json
```

操作要求：

- 只读取当前任务需要的 `skill_docs`；
- 把 `missing_hints` 当作 blocker；
- 消费项目根目录必须和 `<orchestration-repo>` 分离；
- 返回的 `mode` 应保持为 `soft-load`。

soft-load 不会安装 PySide6，不会编辑 `config.toml`，不会启用 plugin bundle，不会启动可见 GUI，也不会打包可执行文件。

## 3. 共享 runtime 验证与创建

在消费项目 apply 前先验证共享 runtime：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\pyside6_gui_helpers\ensure-shared-pyside6-runtime.ps1 -Mode verify -RuntimeRoot D:\PythonProject_langgraph\.shared_runtimes\pyside6 -Json
```

如果返回 `shared_runtime_missing`，创建 runtime 是单独的维护动作：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\pyside6_gui_helpers\ensure-shared-pyside6-runtime.ps1 -Mode provision -RuntimeRoot D:\PythonProject_langgraph\.shared_runtimes\pyside6 -Json
```

provision 只允许写入 `.shared_runtimes/pyside6`，从 `requirements-pyside6.txt` 安装 PySide6，写入 `runtime.json`，并执行 import-only 验证；不得安装消费项目业务依赖。

## 4. preview 消费项目

读取必要 `skill_docs` 后，对明确的消费项目根目录运行 preview：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot <consumer-project> -Mode preview -RuntimeMode shared -DependencyStyle auto -CreateTemplate -Json
```

preview 必须只读。重点检查：

- `project_root` 和 `project_root_evidence`；
- `runtime_mode`、`shared_runtime_root`、`shared_runtime_python` 和 `shared_runtime_status`；
- `package_manager` 和 `dependency_style`；
- `planned_file_changes` 与 `planned_commands`；
- `local_only_artifacts`、`blockers` 和 `rollback_steps`。

如果无法确认安全 `ProjectRoot`，如果共享 runtime 需要先创建，或者 planned writes 会离开目标项目根目录，必须停止。

## 5. 共享 runtime 项目 opt-in apply

preview 复核后再 apply：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot <consumer-project> -Mode apply -RuntimeMode shared -CreateTemplate -Json
```

apply 必须保持项目本地化。shared 模式只创建 GUI 源码、`tools/gui/pyside6_runtime_contract.json`、`tools/gui/run_gui.ps1`、`tools/gui/check_pyside6_env.py`、`tools/gui/adapters/README.md`、import smoke test 和 `docs/pyside6_gui_rollback.md`。shared 模式不得创建 `requirements-gui.txt`，不得修改 `pyproject.toml`，不得把 PySide6 安装进消费项目。

成功输出应包含 `applied_file_changes` 和 `rollback_note`。

## 6. project-local-override 边界

只有当目标项目确实需要独立 PySide6 版本、隔离打包 runtime、离线分发或自包含分发时，才允许 `project-local-override`：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot <consumer-project> -Mode apply -RuntimeMode project-local-override -DependencyStyle auto -OverrideReason "<why this project needs its own PySide6>" -CreateTemplate -Json
```

该例外可以更新 `requirements-gui.txt`、`pyproject.toml` 或 dependency group，但必须有 override reason、版本或 lockfile 复核证据以及 rollback evidence。

## 7. 可见 GUI 与打包边界

可见 GUI 启动是交互式桌面动作。只有用户明确要求交互式验证，或任务本身确实需要可见窗口时，才允许启动可见 GUI。自动化检查不得调用 `.show()`、`app.exec()` 或 `Start-Process` 创建可见窗口。

打包是独立阶段。请求可执行文件打包时，必须先为一个明确工具收集项目本地 packaging opt-in 证据，通常是 PyInstaller 或 Nuitka。preflight 需要记录 Qt platform plugin、resource、icon、dpi、Chinese font、startup log、data directory、antivirus、reproducible build、output directory、数据排除和 rollback。release、签名和分发仍需要单独批准。

## 8. 状态报告

只能基于证据报告状态：

- `candidate`：正在评估 PySide6；
- `shared_runtime_declared`：消费项目已有 runtime contract；
- `shared_runtime_ready`：共享 runtime 已有 `runtime.json` 和 import smoke 证据；
- `project_gui_template_ready`：GUI 源码、run helper、adapter、runtime contract、rollback note 和 import test 已存在；
- `project_gui_verified_with_shared_runtime`：已经通过共享 runtime 运行 import-only 测试；
- `project_local_override_ready`：有文档化 override 以及 dependency/lockfile evidence；
- `packaged`：显式 packaging preflight 通过。

不得只根据 policy、guide、skill、helper 或 template 文本推断 `shared_runtime_ready`、`project_gui_verified_with_shared_runtime`、`project_local_override_ready`、`packaged` 或 `release_ready`。
