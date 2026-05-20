---
doc_id: pyside6_cross_project_gui_capability_plan
lang: zh-CN
status: draft
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md
created_at: 2026-05-20
---

# PySide6 跨项目 GUI 能力方案

> 冷启动契约：本文定义所有本地项目如何在不共享可变 Python 环境的前提下，按需使用 PySide6 制作自己的桌面 GUI。新 Codex 会话读取 `AGENTS.md` 与 `docs_bilingual/project_startup_summary.md` 后即可继续实施。

## 1. 目标

把 PySide6 做成所有本地项目都可复用的 GUI 能力，同时保持项目隔离、可复现、可回滚和版本可控。

期望结果：

- 任意项目都能快速按需启用 PySide6 GUI；
- 不需要 GUI 的项目不被强制安装 PySide6；
- 用户级 Codex skills、模板和 helper 脚本负责指导设置；
- 每个项目保留自己的依赖声明、虚拟环境、源码树、测试和打包决策。

## 2. 非目标

本方案不做：

- 把 PySide6 安装到系统全局 Python；
- 强制所有项目默认携带 PySide6 依赖；
- 修改 plugin/vendor cache；
- 为所有产品强制规定同一个 GUI 布局；
- 默认把每个 GUI 都打包成可执行文件。

## 3. 架构决策

采用两层模型。

### 3.1 用户级共享能力

用户级可以提供：

- `pyside6-gui` skill 或 workflow note；
- 可复用 setup helper，例如 `ensure-pyside6-gui.ps1`；
- `src/<project>_gui/`、`tools/gui/`、`tests/` 项目模板；
- smoke test 片段；
- PyInstaller 或 Nuitka 打包指南；
- Qt platform plugins、DPI、字体和 Windows 路径排障指南。

共享层不能被当作各项目的运行时依赖所有者。

### 3.2 项目级隔离依赖

每个需要 GUI 的项目自己拥有：

- 自己的 `.venv` 或明确记录的 Python 环境；
- 包含 PySide6 的 `requirements-gui.txt`、dependency extra 或 dependency group；
- GUI 源码；
- 资源文件；
- import smoke tests；
- 可选打包脚本；
- 项目自己的 GUI 验收测试。

## 4. 默认项目布局

项目选择启用时，优先使用这个最小布局：

```text
requirements-gui.txt
src/<project_name>_gui/
  __init__.py
  app.py
  main_window.py
tests/test_gui_import.py
tools/gui/
  run_gui.ps1
  check_pyside6_env.py
```

`requirements-gui.txt` 初始内容：

```text
PySide6
```

如果项目已经使用 `pyproject.toml`，优先使用 dependency extra 或 dependency group，而不是额外 requirements 文件。

## 5. 环境设置规则

在某个项目中编写或运行 PySide6 GUI 前：

1. 识别目标项目根目录和 Python 环境；
2. 优先使用项目自己的 `.venv`；
3. 只把 PySide6 安装到该环境；
4. 把依赖写入该项目依赖文件；
5. 运行 import smoke test；
6. 不修改其他项目环境。

最小 smoke 命令：

```powershell
.\.venv\Scripts\python.exe -c "from PySide6.QtWidgets import QApplication; print('PySide6 ok')"
```

## 6. Codex 执行流程

当用户在任意项目要求 PySide6 GUI 时，Codex 应该：

1. 确认目标项目根目录；
2. 检查现有依赖风格（`requirements*.txt`、`pyproject.toml`、`poetry.lock`、`uv.lock` 等）；
3. 选择该项目原生依赖声明方式；
4. 新增或更新 GUI 依赖声明；
5. 只有当前需要本地执行时，才把 PySide6 安装到项目环境；
6. 创建或更新 GUI 源码；
7. 增加 import smoke test；
8. 运行 smoke test；
9. 如用户要求打包，再增加打包脚本并运行打包 preflight；
10. GUI 变更保留在目标项目仓库内，除非任务明确是更新共享政策或模板，否则不要写回本编排仓库。

## 7. 打包边界

打包是单独的按需阶段。不能因为有 GUI 就默认打包可执行文件。

请求打包时，项目必须选择并记录一种工具：

- PyInstaller；
- Nuitka；
- 另一个明确批准的本地打包工具。

打包检查必须覆盖：

- Qt platform plugin 可用性；
- 资源路径；
- 图标路径；
- Windows DPI 行为；
- 中文字体渲染；
- 启动日志；
- 数据目录和配置文件位置。

## 8. 安全与回滚

共享 helper 应尽量 preview-first。

无需额外远端授权即可做：

- 检查本地项目依赖文件；
- 新增项目本地 GUI 依赖声明；
- 新增项目本地 GUI 源码和 smoke tests；
- 当用户正在该项目工作且本地执行确有需要时，安装到该项目 `.venv`。

需要明确批准：

- 全局 Python 包安装；
- 修改用户级 Codex config；
- 编辑 plugin/vendor cache；
- 推送远端分支或发布 release；
- 修改 protected branch 设置；
- 删除约定 GUI 范围之外的项目文件。

## 9. 后续实施任务

后续 implementation change 可以新增：

- 用户级 `pyside6-gui` skill 指引；
- `ensure-pyside6-gui.ps1` helper；
- `check_pyside6_env.py` 模板；
- `run_gui.ps1` 模板；
- 最小 PySide6 main-window 模板；
- 打包 preflight 模板；
- skills/profile helper 文档中的跨项目使用说明。

## 10. 验收标准

本方案完成的标准：

- 英文和中文方案文件存在；
- `docs_bilingual/docs_registry.yaml` 已登记该方案；
- 方案明确区分用户级共享能力和项目级依赖；
- 方案明确不默认全局安装 PySide6；
- 方案给出最小项目布局和 smoke test；
- 实施保持本地-only，未获得用户明确授权前不推送远端。
