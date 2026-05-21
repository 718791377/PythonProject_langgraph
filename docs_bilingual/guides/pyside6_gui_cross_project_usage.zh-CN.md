---
doc_id: pyside6_gui_cross_project_usage
lang: zh-CN
status: active
doc_class: guide
translation_of: docs_bilingual/guides/pyside6_gui_cross_project_usage.md
created_at: 2026-05-21
---

# PySide6 GUI 跨项目 operator 使用指南

本指南说明 operator 如何在消费项目中使用仓库本地的 `plugin-modules` `pyside6-gui` soft-load 模块，而不改变当前 plugin profile、不安装 PySide6，并且默认不启动可见桌面窗口。

## 1. 适用场景

当某个项目需要本地桌面 GUI、PySide6、Qt、Windows 桌面工具或小型本地 operator console，并且当前只需要任务级指导而不是持久改变 plugin profile 时，使用本指南。

不得把本指南当作任意消费项目已经 `env_ready`、`verified`、`packaged` 或 `release_ready` 的证据。这些状态必须来自该消费项目自己的项目本地证据。

## 2. soft-load PySide6 模块

从编排仓库运行模块加载器，并同时传入模块名和编排仓库根目录：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\skill_sources\plugin-modules\scripts\load_module.ps1 pyside6-gui -RepoRoot <orchestration-repo> -Json
```

operator 应该这样处理输出：

- 只读取返回的 `skill_docs` 中与当前 PySide6 任务相关的文件；
- 如果 `missing_hints` 非空，先把它当作阻断项处理；
- 保持消费项目根目录和 `<orchestration-repo>` 分离；
- 确认返回的 `mode` 仍然是 `soft-load`。

soft-load 命令有意保持只读边界：不会安装 PySide6，不会编辑 `config.toml`，不会启用 plugin bundle，不会启动可见 GUI 窗口，也不会打包可执行文件。它也不会把被省略的 skills 重新放回启动可见列表。如果后续确实需要 live plugin tools，应单独 preview hard-load 变更，并且只在获得明确 operator 授权后 apply。

## 3. preview 目标消费项目

读取必要的 `skill_docs` 后，对显式消费项目根目录运行 preview helper：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot <consumer-project> -Mode preview -DependencyStyle auto -CreateTemplate -Json
```

preview 模式必须保持只读。任何 apply 前都要复核这些 JSON 字段：

- `project_root` - 确认准确的消费项目根目录；
- `project_root_evidence` - 说明为什么信任该根目录；
- `python_path` 与 `python_version` - 标识项目本地解释器证据；
- `package_manager` 与 `dependency_style` - 显示选中的项目原生依赖声明面；
- `planned_file_changes` - 列出将要变更的依赖、模板、helper、测试和回滚说明文件；
- `planned_commands` - 列出仍处于计划状态的安装或 smoke-test 命令；
- `local_only_artifacts` - 列出 `.venv`、build 输出或 cache 目录等本地产物；
- `blockers` - apply 前必须为空；
- `rollback_steps` - 必须说明如何撤销项目本地变更。

如果 preview 不能识别安全的 `ProjectRoot`、依赖风格与现有 GUI 依赖冲突，或计划写入离开显式目标项目根目录，必须停止。

## 4. 只在 opt-in 复核后 apply

只有 operator 已经复核并批准消费项目根目录、依赖风格、文件变更和回滚路径之后，才允许 apply：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot <consumer-project> -Mode apply -DependencyStyle auto -CreateTemplate -Json
```

apply 必须保持项目本地化。它可以在 `<consumer-project>` 内创建或更新依赖声明、GUI 模板文件、`tools/gui/` helper、import smoke tests 和 `docs/pyside6_gui_rollback.md`。它不得把消费项目 GUI 源码写进 `<orchestration-repo>`，也不得修改无关项目。

成功的 apply 输出应该包含 `applied_file_changes` 与 `rollback_note`。不得只凭 apply 就报告 `env_ready`；运行时就绪需要项目本地 PySide6 import 或 lockfile 证据。

## 5. 仅在需要时安装、运行和验证

只有当前任务确实需要本地执行时，才把 PySide6 安装到目标消费项目自己的 `.venv` 或明确批准的项目本地 Python 环境。默认验证路径是 import-only smoke tests。

可见 GUI 启动属于交互式桌面动作。只有用户明确要求交互式验证，或任务本身已经需要可见窗口时，才启动可见 GUI 窗口。自动化检查不得调用 `.show()`、`app.exec()` 或 `Start-Process` 创建可见窗口，除非已经获得该授权。

## 6. 打包 opt-in 边界

打包是独立于 GUI opt-in 的阶段。soft-load 模块、preview helper、apply helper、模板或 checker 的存在，都不代表消费项目已经 `packaged`。

当用户请求可执行文件打包时，先为一个明确批准的工具收集项目本地打包 opt-in 证据，通常是 PyInstaller 或 Nuitka。打包 preflight 必须记录 Qt platform plugin 处理、资源和图标路径、DPI 和字体行为、启动日志、数据目录行为、杀软误报风险、可复现 build 命令、输出目录、数据排除和回滚步骤。release、signing、distribution 仍然需要区别于本地打包的单独授权。

## 7. 状态报告

只能在具备证据时使用这些状态：

- `candidate`：正在评估 PySide6；
- `declared`：依赖声明面已更新；
- `template_ready`：GUI 源码、运行 helper 和 import test 已存在；
- `env_ready`：有项目本地 import 或 lockfile 证据；
- `verified`：项目本地 import-only 或 headless tests 已通过；
- `packaged`：显式打包 preflight 已成功。

不得只根据政策、指南、skill、helper 或模板文本推断 `env_ready`、`verified`、`packaged` 或 `release_ready`。
