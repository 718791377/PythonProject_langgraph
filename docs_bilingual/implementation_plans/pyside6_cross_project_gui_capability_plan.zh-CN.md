---
doc_id: pyside6_cross_project_gui_capability_plan
lang: zh-CN
status: draft
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md
created_at: 2026-05-20
---

# PySide6 跨项目 GUI 能力方案

> 冷启动契约：本文定义所有本地项目如何默认调用由 `D:\PythonProject_langgraph` 维护的同一个共享 PySide6 runtime，并在不污染系统 Python、不在消费项目重复安装 PySide6 的前提下，按需制作各自的桌面 GUI。新 Codex 会话读取 `AGENTS.md` 与 `docs_bilingual/project_startup_summary.md` 后即可继续实施。

## 1. 目标

把 PySide6 做成所有本地项目都可复用的 GUI 能力，并把 PySide6 运行时集中维护在本仓库的本地共享 runtime 下，避免每个项目重复安装或漂移版本。

默认运行时位置：

```text
D:\PythonProject_langgraph\.shared_runtimes\pyside6
  .venv\                    # 共享 PySide6 Python 环境，本地产物，不提交 git
  requirements-pyside6.txt   # 共享 runtime 的 PySide6 依赖声明，提交或由模板生成
  runtime.json               # runtime 元数据：Python、PySide6、Qt、创建/更新时间、维护仓库
  logs\                      # 本地诊断日志，本地产物，不提交 git
```

期望结果：

- 任意项目都能通过同一个共享 PySide6 runtime 启动或验证自己的 GUI；
- 不需要 GUI 的项目不被强制写入 PySide6 依赖；
- 消费项目默认不安装 PySide6，只保留 GUI 源码、运行契约、adapter、测试和回滚说明；
- `D:\PythonProject_langgraph` 维护共享 runtime 的 helper、模板、checker 和治理文档；
- PySide6 版本升级变成一次受治理的共享 runtime 维护动作，而不是多个项目各自漂移；
- 项目仍保留自己的业务依赖、源码树、测试、打包决策和例外覆盖权。

## 2. 非目标

本方案不做：

- 把 PySide6 安装到系统全局 Python 或用户 site-packages；
- 默认把 PySide6 安装进每个消费项目的 `.venv`；
- 把消费项目的业务依赖静默安装进共享 PySide6 runtime；
- 强制所有项目默认携带 PySide6 依赖；
- 修改 plugin/vendor cache；
- 为所有产品强制规定同一个 GUI 布局；
- 默认把每个 GUI 都打包成可执行文件；
- 把本编排仓库变成各消费项目 GUI 源码的存放位置。

## 3. 架构决策

采用三层模型：共享 PySide6 runtime、共享 helper/template/checker、消费项目 GUI adapter。

### 3.1 本仓库维护的共享 PySide6 runtime

共享 runtime 是唯一默认 PySide6 安装位置：

```text
D:\PythonProject_langgraph\.shared_runtimes\pyside6\.venv\Scripts\python.exe
```

治理规则：

- `.shared_runtimes/` 必须作为本地产物加入 `.gitignore`，不得提交 wheel、site-packages、Qt 二进制、缓存或日志；
- `requirements-pyside6.txt`、runtime 模板、provision/verify helper 和 checker 可以提交到本仓库；
- `runtime.json` 记录当前本机共享 runtime 的 Python 版本、解释器路径、PySide6 版本、Qt 版本、创建/更新时间、维护脚本版本和健康检查结果；
- 首次创建或升级共享 runtime 是本仓库的受治理维护动作，不能在消费项目 opt-in 时静默发生；
- 共享 runtime 只安装 PySide6 及经批准的 GUI runtime 级辅助包，不安装某个消费项目的业务依赖；
- 共享 runtime 不是系统全局环境；它可删除、可重建、可通过本仓库脚本重新 provision。

### 3.2 共享 helper、模板与 checker

本仓库提供并维护：

- `pyside6-gui` skill 或 workflow note；
- 共享 runtime provision / verify helper，例如后续的 `ensure-shared-pyside6-runtime.ps1`；
- 目标项目 opt-in helper，例如 `ensure-pyside6-gui.ps1`，默认使用共享 runtime；
- 跨项目运行 helper，例如后续的 `run-shared-pyside6-gui.ps1`；
- `src/<project>_gui/`、`tools/gui/`、`tests/` 项目模板；
- import-only smoke test 片段；
- PyInstaller 或 Nuitka 打包指南；
- Qt platform plugins、DPI、字体和 Windows 路径排障指南。

共享层拥有可复用知识、模板、helper 和 runtime 维护脚本；消费项目仍拥有自己的 GUI 源码和业务逻辑。

### 3.3 消费项目 GUI adapter

每个需要 GUI 的项目默认拥有：

- GUI 源码、资源文件、adapter 和测试；
- `tools/gui/pyside6_runtime_contract.json` 或等价文档，记录共享 runtime 路径和调用方式；
- `tools/gui/run_gui.ps1` 或等价 wrapper，委托到共享 runtime；
- import-only smoke tests，使用共享 runtime 验证 GUI shell 可导入；
- 业务逻辑与 GUI shell 的边界，必要时通过项目自己的 `.venv`、CLI、HTTP、本地 IPC 或 worker adapter 调用业务层；
- 可选打包脚本；
- 项目自己的 GUI 验收测试。

消费项目默认不拥有 PySide6 安装。只有当项目确实需要独立 Qt/PySide6 版本、离线分发、自包含打包或隔离实验时，才允许项目本地 `.venv` 作为显式 override。

## 4. 适用范围与触发规则

项目只在满足下列条件之一时才启用 PySide6：

| 触发条件 | 动作 |
| --- | --- |
| 用户明确要求本地 GUI、桌面 GUI、PySide6、Qt 或 Windows 桌面工具 | 对该项目启动 PySide6 opt-in 流程 |
| 项目已经存在 GUI 源码或 GUI 依赖声明 | 检查并延续该项目已有 GUI 风格 |
| 项目需要小型本地操作台、复核控制台、队列看板或本地工作流 launcher | 实施前把 PySide6 作为候选方案提出 |
| 任务只需要命令行自动化，或项目已有浏览器 UI | 不默认新增 PySide6 |

不得把本方案理解为“主动给每个项目都安装 PySide6”。默认动作是让项目调用本仓库维护的共享 PySide6 runtime；只有共享 runtime 维护任务才安装或升级 PySide6。

## 5. 默认项目布局

项目选择启用时，优先使用这个最小布局，除非项目已有更强约定：

```text
src/<project_name>_gui/
  __init__.py
  app.py
  main_window.py
tests/test_gui_import.py
tools/gui/
  pyside6_runtime_contract.json
  run_gui.ps1
  check_pyside6_env.py
  adapters/
```

`pyside6_runtime_contract.json` 初始语义：

```json
{
  "runtime_mode": "shared",
  "runtime_owner_repo": "D:\\PythonProject_langgraph",
  "runtime_root": "D:\\PythonProject_langgraph\\.shared_runtimes\\pyside6",
  "runtime_python": "D:\\PythonProject_langgraph\\.shared_runtimes\\pyside6\\.venv\\Scripts\\python.exe",
  "project_root": "<target-project-root>",
  "business_runtime_mode": "project-local-adapter",
  "visible_gui_requires_explicit_request": true,
  "packaging_requires_explicit_request": true
}
```

如果项目已经使用 `pyproject.toml` 或 requirements 文件，默认不把 PySide6 写入这些依赖面；只在项目选择 `project_local_override` 时才写入 `requirements-gui.txt`、optional extra 或 dependency group。

## 6. 共享 runtime 与项目声明模式

默认声明方式从“项目依赖 PySide6”改为“项目依赖本仓库维护的共享 PySide6 runtime 契约”。

| 场景 | 推荐声明方式 |
| --- | --- |
| 普通项目默认启用 GUI | `tools/gui/pyside6_runtime_contract.json` 记录共享 runtime 路径和调用模式 |
| 项目已有 requirements 风格 | 不默认写入 PySide6；只记录共享 runtime 契约 |
| `pyproject.toml` 项目 | 不默认写入 `[project.optional-dependencies] gui`; 只在 `project_local_override` 时写入 |
| uv / Poetry 项目 | 不默认执行 `uv add` 或 `poetry add`; 只在独立项目环境 override 时写入 |
| 需要独立 PySide6 版本 | 显式记录 `project_local_override`，再使用项目原生依赖声明面 |
| 已有 GUI 技术栈 | 延续已有 GUI 依赖风格，避免并行引入 PySide6 |

共享 runtime 版本规则：

- 原型阶段可以先在共享 runtime 的 `requirements-pyside6.txt` 使用未固定 `PySide6`；
- 一旦多个项目依赖共享 runtime，应记录当前 PySide6/Qt/Python 版本到 `runtime.json`，并优先使用版本范围或 lock 证据；
- 升级共享 runtime 必须作为本仓库维护任务执行，记录受影响项目和回滚路径；
- 不得静默跨所有项目升级 PySide6；
- 消费项目不得把共享 runtime 当前版本误当作自己的可发布依赖锁定证据。

## 7. 环境设置规则

在某个项目中编写或运行 PySide6 GUI 前：

1. 识别目标项目根目录；
2. 识别本仓库共享 PySide6 runtime 路径；
3. 验证共享 runtime 是否存在、可执行、可 import PySide6；
4. 在目标项目写入 GUI 源码、adapter、运行契约和 import smoke test；
5. 使用共享 runtime 运行 import-only smoke test；
6. 不把 PySide6 安装进目标项目 `.venv`，除非该项目明确选择 `project_local_override`；
7. 不把目标项目业务依赖安装进共享 runtime。

额外 preflight 要求：

- 共享 runtime 首次 provision 前必须确认 Python 版本、解释器架构、目标路径和包管理器；
- 如果共享 runtime 不存在，消费项目 opt-in helper 必须报告 `shared_runtime_missing`，不能静默安装；
- apply 只能在显式目标项目根目录下创建 GUI 源码、契约、wrapper 和测试；
- 不能因为系统全局解释器或某个项目 `.venv` 刚好能 import PySide6，就把共享 runtime 判断为 `shared_runtime_ready`；
- 可见 GUI 启动属于交互式桌面动作，必须由请求驱动；默认验证仍以 import-only 为主；
- 项目业务逻辑默认通过 adapter 调用项目自己的 Python 环境、CLI、HTTP、本地 IPC 或 worker，不默认由共享 runtime 直接 import 全量业务依赖。

最小共享 runtime smoke 命令：

```powershell
D:\PythonProject_langgraph\.shared_runtimes\pyside6\.venv\Scripts\python.exe -c "from PySide6.QtWidgets import QApplication; print('PySide6 shared runtime ok')"
```

目标项目 import-only smoke 应使用共享 runtime 的 Python，并把目标项目源码路径作为显式输入，而不是依赖当前 shell 的隐式环境。

Headless 或 CI 环境可以只跑 import-only 测试，不显示窗口；除非项目明确配置了 GUI-capable test runner。

## 8. 用户级 helper 契约

仓库源码中的 GUI helper，以及任何安装到用户级目录的副本，都必须采用 preview-first 行为，并默认使用共享 PySide6 runtime。

共享 runtime helper 必需能力：

- `ensure-shared-pyside6-runtime.ps1 -Mode preview|provision|verify`；
- `-RuntimeRoot` 默认 `D:\PythonProject_langgraph\.shared_runtimes\pyside6`；
- preview 不创建 `.venv`、不安装包，只报告计划；
- provision 只写入共享 runtime 目录；
- verify 只运行 import-only smoke 与版本读取；
- 输出 `runtime_root`、`runtime_python`、`python_version`、`pyside6_version`、`qt_version`、`requirements_file`、`runtime_json`、`local_only_artifacts`、`blockers`、`rollback_steps`。

项目 opt-in helper 必需输入：

- `-ProjectRoot` - 要检查或修改的目标项目根目录；
- `-Mode preview|apply` - preview 不改文件，apply 执行项目本地 GUI 文件修改；
- `-RuntimeMode shared|project-local-override`，默认 `shared`；
- 可选 `-RuntimeRoot`；
- 可选 `-CreateTemplate`；
- 可选 `-RunSmokeTest`；
- 仅在 `project-local-override` 时允许 `-DependencyStyle auto|requirements|pyproject-extra|group`、`-PythonPath`、`-PackageVersion`。

Preview 输出必须包含：

- 检测到的项目根目录，以及用于判定根目录的证据；
- 检测到的共享 runtime 路径、Python 路径、PySide6/Qt 版本或缺失原因；
- 选中的 runtime 模式；
- 将创建或修改的文件；
- 将执行的命令；
- smoke test 命令；
- 预计新增的本地-only 产物，例如项目缓存、共享 runtime 日志、build 输出或 `.venv`；
- 风险和回滚说明。

Preview 还应输出机器可读摘要，例如 JSON 字段 `project_root`、`project_root_evidence`、`runtime_mode`、`shared_runtime_root`、`shared_runtime_python`、`shared_runtime_status`、`planned_file_changes`、`planned_commands`、`local_only_artifacts`、`blockers` 和 `rollback_steps`。人类可读输出可以包裹这份摘要，但后续 checker 应消费结构化表面。

Apply 模式必须保持项目本地化：项目 helper 只能写目标项目 GUI 源码、契约、wrapper、测试和回滚说明；共享 runtime provision 必须由共享 runtime helper 单独执行。如果无法可靠识别目标项目根目录、共享 runtime 状态或可写范围，必须 fail closed。

## 9. 最小 GUI 模板契约

最小模板应创建一个小型应用，并满足：

- 有 `QApplication` 入口；
- 有 `QMainWindow` 子类；
- 有确定性的窗口标题；
- 默认不访问网络；
- 不修改全局配置；
- 默认不创建后台 daemon；
- GUI shell 与项目业务逻辑明确分离；
- 长耗时任务默认不阻塞 UI event loop；
- 项目业务逻辑错误能以用户可理解的方式显示，并保留可诊断日志；
- logging、settings 和数据目录行为必须显式且可测试。

推荐源码边界：

| 层 | 职责 |
| --- | --- |
| `app.py` | 创建 `QApplication`、设置应用元数据、启动窗口 |
| `main_window.py` | 定义布局、动作和 UI 事件接线 |
| 项目 service modules | 提供 GUI 可调用的业务逻辑 |
| `tools/gui/run_gui.ps1` | 定位共享 PySide6 runtime，并把目标项目作为显式输入运行 app |
| `tests/test_gui_import.py` | 使用共享 runtime，不显示 GUI，仅验证 GUI shell 可导入 |
| worker / service adapter | 承接长耗时任务，避免阻塞 Qt event loop |
| config / data directory adapter | 明确本地配置、缓存和数据目录，不写入仓库外未知位置 |
| logging / diagnostics adapter | 写入可诊断日志，同时避免在普通 UI 输出中泄露凭据或用户私有路径 |

## 10. Codex 执行流程

当用户在任意项目要求 PySide6 GUI 时，Codex 应该：

1. 确认目标项目根目录，并说明判定依据，例如 `.git`、`pyproject.toml`、README 或既有脚本；
2. 检查目标项目是否已有 GUI 技术栈，避免把 PySide6 与既有 GUI 框架并行引入；
3. 检查 `D:\PythonProject_langgraph\.shared_runtimes\pyside6` 共享 runtime 是否存在并可验证；
4. 如果共享 runtime 不存在，报告 `shared_runtime_missing`，把“创建/安装共享 PySide6 runtime”作为单独维护动作，不在消费项目 opt-in 中静默安装；
5. 修改文件前创建本地回滚边界，例如 feature branch 或提交计划；
6. 在目标项目新增或更新 GUI 源码、runtime contract、run helper、adapter 和 import smoke test；
7. 默认不修改目标项目依赖文件；只有选择 `project-local-override` 时才新增 PySide6 依赖声明；
8. 使用共享 runtime 运行 import-only smoke test；
9. 如 GUI 需要业务逻辑，优先通过 adapter 调用目标项目自己的 runtime、CLI、HTTP、本地 IPC 或 worker，避免把项目业务依赖装入共享 runtime；
10. 只有用户明确要求交互式验证，或任务本身已经需要可见窗口时，才启动可见 GUI；
11. 如用户要求打包，再增加打包脚本并运行打包 preflight；
12. GUI 变更保留在目标项目仓库内，除非任务明确是更新共享政策、runtime helper 或模板，否则不要写回本编排仓库。

## 11. 测试策略

共享 runtime 至少需要：

- `runtime.json` 记录 Python、PySide6、Qt 和维护脚本版本；
- 共享 runtime Python 可执行；
- `from PySide6.QtWidgets import QApplication` import smoke 通过；
- helper 能报告 runtime 缺失、版本不匹配和回滚步骤；
- `.shared_runtimes/` 保持 gitignored，本地产物不进入提交。

每个启用 GUI 的项目至少需要：

- `tools/gui/pyside6_runtime_contract.json` 或等价文档指向共享 runtime；
- GUI package 可通过共享 runtime 导入且不显示窗口；
- `tools/gui/run_gui.ps1` 或等价 run helper 能解析目标项目根目录、共享 runtime 路径和必要 adapter；
- 如果 GUI 调用业务逻辑，业务逻辑必须脱离 GUI event loop 单独可测试；
- 长耗时动作必须有 worker、thread、process、async、CLI、HTTP、本地 IPC 或其他 adapter 边界，并有取消或失败反馈策略；
- 本地配置、缓存和数据目录必须有文档或 helper 输出证据；
- 排障诊断可以被启用，但不得暴露凭据、访问 token、浏览器 profile 或无关的用户私有路径。

可选测试：

- `pytest-qt` 或同类 GUI 交互测试；
- 截图 / 人工 QA 清单；
- 共享 runtime 升级回归测试；
- 打包 preflight 测试；
- Windows shortcut / start-menu 集成测试。

## 12. 打包边界

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
- 数据目录和配置文件位置；
- 本地可执行文件的杀软误报风险；
- 可复现 build 命令和输出目录；
- 打包产物排除凭据、浏览器 profile、用户私有数据目录和无关仓库文件；
- release、签名和分发步骤必须作为区别于本地打包的单独授权处理。

## 13. 安全、回滚与授权

共享 helper 应尽量 preview-first。

无需额外远端授权即可做：

- 检查本地项目 GUI 源码和 runtime contract；
- 新增项目本地 GUI 源码、adapter、runtime contract 和 smoke tests；
- 使用已存在且已验证的共享 PySide6 runtime 运行 import-only smoke；
- 读取共享 runtime 元数据和版本信息。

需要明确批准或独立任务边界：

- 首次创建共享 PySide6 runtime；
- 安装或升级共享 runtime 内的 PySide6；
- 把 PySide6 安装进某个消费项目 `.venv`；
- 全局 Python 包安装；
- 修改用户级 Codex config；
- 编辑 plugin/vendor cache；
- 推送远端分支或发布 release；
- 修改 protected branch 设置；
- 删除约定 GUI 范围之外的项目文件；
- 改写无关项目的 dependency lock；
- 让 GUI helper 访问网络、凭据、浏览器 profile 或用户私有目录，除非任务明确需要且已说明风险；
- 在用户没有要求交互式验证时，从自动化会话启动可见 GUI 窗口。

回滚路径：

- revert 项目本地 commit 或 feature branch；
- 删除本轮新生成的 GUI 模板文件、runtime contract、adapter 和测试；
- 如果共享 runtime 维护任务失败，删除并重建 `.shared_runtimes/pyside6`，或恢复上一版 `requirements-pyside6.txt` / `runtime.json`；
- 如果项目选择了 `project-local-override` 并修改 lockfile，恢复上一版 lockfile；
- 用户级模板保持不动，除非本轮任务本身就是修改模板。

## 14. 跨项目治理

本文是共享政策。消费项目的实现必须留在消费项目自身。

规则：

- 不把消费项目 GUI 源码放进 `D:\PythonProject_langgraph`；
- 默认所有消费项目只调用 `D:\PythonProject_langgraph\.shared_runtimes\pyside6` 这一处受治理共享 runtime；
- 不创建多个匿名共享 PySide6 venv；
- 不把消费项目业务依赖安装进共享 runtime；
- 不让项目-local override 静默取代共享 runtime；
- 不为了给 GUI 腾空间而禁用 browser 或 web automation skills；
- 如果项目同时需要 GUI 和 browser automation，保持两个能力面分离；
- 项目特定 GUI 决策写入该项目自己的文档、runtime contract 或 adapter 文件；
- GUI helper 只能在显式目标项目根目录内写入模板、脚本和测试，用户级模板或共享 runtime 更新必须作为单独任务处理。

## 15. 能力状态模型

每个项目本地 GUI 能力都应该使用下列状态之一描述，避免后续会话混淆政策、共享 runtime、项目 GUI 模板、已验证运行和已打包产物：

| 状态 | 含义 | 最小证据 |
| --- | --- | --- |
| `not_applicable` | 项目不需要桌面 GUI | 记录过的决策，或没有 GUI 触发条件 |
| `candidate` | 正在评估 PySide6，但尚未采用 | 简短设计说明和备选方案 |
| `shared_runtime_declared` | 项目决定使用共享 PySide6 runtime | runtime contract 或项目文档指向 `D:\PythonProject_langgraph\.shared_runtimes\pyside6` |
| `shared_runtime_ready` | 本机共享 runtime 可用 | 共享 runtime import smoke、`runtime.json` 和版本证据 |
| `project_gui_template_ready` | 目标项目最小 GUI 源码和运行 helper 已存在 | `src/*_gui/`、`tools/gui/`、runtime contract 和 import test |
| `project_gui_verified_with_shared_runtime` | 目标项目 GUI 使用共享 runtime 通过不显示窗口的测试 | import-only 或 headless CI 证据 |
| `project_local_override_ready` | 项目因例外需要拥有自己的 PySide6 环境 | 项目依赖声明、lockfile 或 import smoke 证据，并记录 override 原因 |
| `packaged` | 用户明确要求可执行文件打包且已验证 | 打包配置、preflight 输出和回滚说明 |

不得只凭政策文本、模板、skill 或项目源码就声称项目已经 `shared_runtime_ready`、`project_gui_verified_with_shared_runtime` 或 `packaged`。这些状态必须有运行或结构化证据。

## 16. 实施切片与推进闸门

该能力必须按小步、可审查的切片实施。后续 implementation change 不应尝试一次性修改所有消费项目。

| 切片 | 目的 | 交付物 | 合入前闸门 |
| --- | --- | --- | --- |
| 0. 盘点 | 查明目标项目现有 GUI 形态和依赖管理方式 | 只读盘点记录 | 不修改项目文件 |
| 1. 共享 runtime 政策 | 发布共享 runtime 默认策略、目录、状态模型和授权边界 | 双语方案、`.shared_runtimes/` gitignore 规则、runtime 元数据 schema | docs 和治理 checker 通过 |
| 2. 共享 runtime helper | 增加 `ensure-shared-pyside6-runtime.ps1` preview/provision/verify | helper、`requirements-pyside6.txt`、`runtime.json` 模板、checker/test | preview 只读；provision 只写共享 runtime；verify import-only |
| 3. 项目 opt-in helper | 让 `ensure-pyside6-gui.ps1` 默认使用共享 runtime | runtime contract、run wrapper、GUI 模板、adapter 模板 | fixture 中验证不向项目 `.venv` 安装 PySide6 |
| 4. 消费项目 opt-in | 为一个消费项目启用 GUI | GUI shell、adapter、runtime contract、import test | 使用共享 runtime 的项目本地 gate 通过 |
| 5. 项目-local override | 仅在项目需要独立 PySide6 时启用 | 项目依赖声明、lockfile、override 说明 | override 原因、版本和回滚路径已记录 |
| 6. 打包 opt-in | 仅在用户要求时打包 | PyInstaller/Nuitka 配置、preflight 脚本 | 打包 preflight 和回滚路径已记录 |

默认推进顺序是 0 -> 1 -> 2 -> 3 -> 4。切片 5/6 是可选阶段，必须保持请求驱动。

当前本地实施状态：

- 既有 `tools/pyside6_gui_templates/`、`ensure-pyside6-gui.ps1`、`pyside6-gui` skill、`plugin-modules` soft-load、消费项目 opt-in checker、打包 opt-in checker 和 operator 使用指南，是项目-local 安装默认策略时期形成的兼容基线；
- 本文更新后，新的目标策略改为“共享 PySide6 runtime 默认、项目-local PySide6 仅作 override”；
- 后续实现必须新增或改造 checker，确保共享 runtime 缺失时不能误报项目 `shared_runtime_ready`，消费项目 opt-in 不能静默执行 PySide6 安装；
- 后续实现必须把 `.shared_runtimes/` 加入 gitignore，并增加共享 runtime provision/verify helper；
- 具体消费项目的 GUI 启用仍按具体项目和请求推进，不得把 helper、模板、skill 或 checker 存在误报为任意消费项目已经 `project_gui_verified_with_shared_runtime` 或 `packaged`；
- 实际可执行文件打包仍保持请求驱动，不得把 checker/模板存在误报为任意消费项目已经 `packaged` 或 `release_ready`。


## 17. 细颗粒度实施事项勾选清单

本清单只列具体实施事项，不把“更新本方案文件”作为实施事项。事项按实际推进顺序排列；已完成项用 `[x]`，未完成项用 `[ ]`。

- [x] 盘点已有 PySide6 GUI 基线：模板、`ensure-pyside6-gui.ps1`、`pyside6-gui` skill、operator 指南、项目 opt-in checker 与打包 opt-in checker。
- [x] 确认默认策略从“项目本地安装 PySide6”调整为“本仓库维护共享 PySide6 runtime，项目本地安装仅作为 override 例外”。
- [x] 明确共享 runtime 默认路径为 `D:\PythonProject_langgraph\.shared_runtimes\pyside6`。
- [x] 将 `.shared_runtimes/` 写入 `.gitignore`，防止 runtime 二进制、site-packages、Qt 插件、缓存或日志进入仓库。
- [x] 新增共享 runtime 依赖模板 `tools/pyside6_gui_templates/shared_runtime/requirements-pyside6.txt.template`。
- [x] 新增共享 runtime 元数据模板 `tools/pyside6_gui_templates/shared_runtime/runtime.json.template`。
- [x] 新增共享 runtime helper `tools/pyside6_gui_helpers/ensure-shared-pyside6-runtime.ps1`。
- [x] 为共享 runtime helper 实现 `preview` 模式，确保预览只读并输出计划动作。
- [x] 为共享 runtime helper 实现 `provision` 模式，确保只写入共享 runtime 根目录。
- [x] 为共享 runtime helper 实现 `verify` 模式，确保只做 import-only 验证，不启动可见 GUI。
- [x] 为共享 runtime helper 输出结构化 JSON 字段，覆盖 runtime 根目录、Python 路径、状态、计划动作、阻塞项与回滚提示。
- [x] 修改 `ensure-pyside6-gui.ps1`，新增 `-RuntimeMode shared|project-local-override`。
- [x] 将 `ensure-pyside6-gui.ps1` 默认 runtime 模式设为 `shared`。
- [x] 为 `ensure-pyside6-gui.ps1` 新增 `-RuntimeRoot`，默认指向共享 runtime 路径。
- [x] 在 shared 模式下禁止默认写入项目依赖声明或 lockfile。
- [x] 在 shared 模式下当共享 runtime 缺失时 fail closed，不静默安装到消费项目 `.venv`。
- [x] 在 shared 模式下生成项目本地 `tools/gui/pyside6_runtime_contract.json`。
- [x] 在 shared 模式下生成项目本地 GUI adapter 说明 `tools/gui/adapters/README.md`。
- [x] 更新 `tools/gui/check_pyside6_env.py` 模板，使其通过 runtime contract 与共享 runtime 做 import-only smoke，并在使用共享 runtime Python 时显式加入目标项目 `src` 到 `sys.path`。
- [x] 更新 `tools/gui/run_gui.ps1` 模板，使项目通过共享 runtime 启动 GUI。
- [x] 保留 GUI 源码、运行 helper、adapter、测试和 rollback note 在消费项目本地，不把消费项目 GUI 代码写回本仓库。
- [x] 为 `project-local-override` 增加 `-OverrideReason` 要求。
- [x] 为 `project-local-override` 保留依赖声明、lockfile 证据和回滚证据边界。
- [x] 更新 repo-local `pyside6-gui` skill，使其说明共享 runtime 默认策略、缺失 runtime 的阻塞行为和 override 例外。
- [x] 更新中英文 operator 使用指南，使 preview/apply/verify 流程与共享 runtime 默认策略一致。
- [x] 新增 `tools/check_pyside6_shared_runtime_contract.py`，检查共享 runtime helper、模板、gitignore、skill 与 CI 注册契约。
- [x] 更新 `tools/check_pyside6_gui_preview_helper_contract.py`，覆盖 shared/runtime-root/override 行为。
- [x] 更新 `tools/check_pyside6_gui_skill_contract.py`，覆盖共享 runtime 默认策略与禁止误报状态。
- [x] 更新 `tools/check_pyside6_gui_template_contract.py`，覆盖 runtime contract、adapter 与 shared runtime 模板。
- [x] 修复 `ensure-pyside6-gui.ps1` rollback note 生成中的 PowerShell 插值问题，防止出现 `System.Collections.Specialized.OrderedDictionary` 或制表符破坏的 `tools/gui/` / `tests/` 路径。
- [x] 更新 `tools/check_pyside6_operator_usage_guide.py`，覆盖 operator 指南中的共享 runtime 用法。
- [x] 更新 `tools/check_pyside6_project_opt_in_contract.py`，覆盖 shared 模式不安装 PySide6 与 override 例外。
- [x] 新增并更新 PySide6 相关 Node 测试，覆盖共享 runtime checker、模板 checker、preview helper checker、skill checker、project opt-in checker、packaging opt-in checker 与 operator 指南 checker。
- [x] 将共享 runtime checker 注册到 `tools/run_openspec_guard.py`。
- [x] 将共享 runtime checker 测试注册到 `tools/ci/ci_test_manifest.json`。
- [x] 修正 `test/run_openspec_guard_json.test.py`，确保 guard JSON 测试覆盖新增 checker。
- [x] 运行 PySide6 目标测试并确认通过。
- [x] 运行 `python tools/run_openspec_guard.py --root .` 并确认通过。
- [x] 运行 `python tools/check_precommit_update_archive.py --root . --json` 并确认通过。
- [x] 运行 `git diff --check` 并确认通过。
- [x] 运行本地 MR review gate 并确认通过。
- [x] 运行本地 CI gate 并确认通过。
- [x] 将共享 runtime 默认策略合入本地 `main`。
- [x] 清理已合入的 `implement-pyside6-shared-runtime` worktree 与本地 feature branch。
- [x] 按本轮继续实施请求，在 `D:\PythonProject_langgraph\.shared_runtimes\pyside6` provision 真实共享 PySide6 runtime；该目录仍为 gitignored 本地-only runtime。
- [x] provision 后运行共享 runtime `verify`，记录 Python 3.12.10、PySide6 6.11.1 与 Qt 6.11.1 import-only 证据，未启动可见 GUI。
- [x] provision 后生成真实 `runtime.json`，记录版本、路径、更新时间、import-only 状态和回滚步骤；该文件保留在 `.shared_runtimes/` 本地产物中，不进入 Git。
- [x] 按具体需求选择第一个消费项目，先运行 shared 模式 `preview`，确认目标项目根目录、写入范围和阻塞项；2026-05-22 已选择首个已登记消费项目并把项目专属证据记录到 memory 文件。
- [x] 在首个消费项目中运行 shared 模式 `apply`，生成 GUI shell、runtime contract、run helper、adapter、import smoke test、rollback note 与项目本地双语文档；项目专属路径、提交号和回滚证据只保存在 memory 文件中。
- [x] 在首个消费项目中通过共享 runtime 运行 import-only smoke test；证据显示 PySide6 6.11.1、Qt 6.11.1、`import_only_verified=true`，且未启动可见 GUI。
- [x] 根据首个消费项目证据修正模板，使共享 runtime Python 执行项目 import smoke 时显式加入目标项目 `src` 到 `sys.path`。
- [x] 根据首个消费项目证据修正 rollback note 生成逻辑，防止 PowerShell 将变更项序列化为 `System.Collections.Specialized.OrderedDictionary` 或破坏 `tools/gui/` / `tests/` 字面路径。
- [x] 根据首个消费项目的证据扩展项目 opt-in checker，覆盖真实 runtime contract、adapter 和 shared runtime smoke 输出；`tools/check_pyside6_project_opt_in_contract.py` 已支持 `--smoke-json`，只有 import-only smoke 成功且无 blockers 才能提升到 `project_gui_verified_with_shared_runtime`。
- [x] 根据首个消费项目证据完成跨项目 launcher 取舍判断；当前证据显示 per-project `tools/gui/run_gui.ps1` 已足够，暂不新增跨项目 `run-shared-pyside6-gui.ps1`，取舍依据已记录到 memory 文件。
- [ ] 仅在项目有独立版本、隔离或自包含打包需求时，执行 `project-local-override`，并记录 override reason、依赖/lockfile 证据和 rollback 证据。
- [ ] 仅在用户明确要求可见 GUI 验证时，执行交互式窗口验证或截图/人工 QA 清单。
- [ ] 仅在用户明确要求可执行文件时，进入 PyInstaller/Nuitka 打包 opt-in 阶段并运行 packaging preflight。



## 18. 首个消费项目证据摘要

2026-05-22 已完成首个已登记消费项目的本地 shared runtime GUI opt-in。为保持本仓库级方案的通用性，并满足 current-repo authority guard，项目专属路径、提交号、smoke 输出和回滚细节只记录在：

- `docs_bilingual/memory/pyside6_first_consumer_apply_2026-05-22.md` - 记录首个消费项目 apply 的项目专属证据；
- `docs_bilingual/memory/pyside6_first_consumer_apply_2026-05-22.zh-CN.md` - 记录同一证据的中文配套文件。

本方案只保留可复用结论：

- shared 模式可以在不向消费项目安装 PySide6 的前提下生成 GUI shell、runtime contract、run helper、adapter 说明、import smoke test、rollback note 与项目本地文档；
- 由共享 runtime Python 执行项目 import smoke 时，模板必须显式把目标项目 `src` 加入 `sys.path`；
- rollback note 生成必须使用显式格式化字符串记录变更路径，避免 PowerShell 输出 ordered dictionary 或破坏 `tools/gui/` / `tests/` 字面路径；
- 当前单一消费项目证据显示，per-project `tools/gui/run_gui.ps1` 已足够承载项目根目录、GUI 包名、可见窗口授权和 runtime contract，不需要新增跨项目 `run-shared-pyside6-gui.ps1`；
- 跨项目 launcher 仅在至少两个消费项目暴露重复 launcher 逻辑且 per-project wrapper 无法消除重复时再重开；
- 项目专属证据保留在 memory artifact，不写入本通用实施方案。

## 19. 失败模式与排障

常见失败模式必须作为项目本地问题处理，不能通过削弱共享政策解决：

| 现象 | 常见原因 | 推荐处理 |
| --- | --- | --- |
| `ModuleNotFoundError: PySide6` | 未使用共享 runtime，或共享 runtime 未 provision / 已损坏 | 确认 `D:\PythonProject_langgraph\.shared_runtimes\pyside6`，运行共享 runtime verify；不要先装进项目 venv |
| Qt platform plugin 错误 | 共享 runtime Qt plugin 路径异常，或打包产物缺少运行时文件 | 先检查共享 runtime；若是打包问题，再增加打包 preflight 证据 |
| GUI 测试在 CI 挂起 | headless 环境里运行了 event loop 或可见窗口测试 | 使用 import-only smoke，或配置 GUI-capable test runner |
| 中文文字渲染异常 | 字体 fallback 或打包缺少字体 | 记录字体选择并测试 Windows 渲染 |
| 打包 exe 被杀软警告 | one-file 可执行文件启发式误报 | 记录工具和版本，优先可复现 build，避免未经复核的二进制 |
| helper 无法识别项目根目录 | 目标检测不安全 | fail closed，并要求显式传入 `-ProjectRoot` |

## 20. 后续实施任务

剩余任务必须由具体维护请求或具体消费项目需求触发，不再把已落地的 helper、模板、checker、skill、CI 注册或本机共享 runtime provision 重复列为后续任务：

- 选择首个消费项目后，运行 shared 模式 preview/apply，并在消费项目中生成 GUI shell、runtime contract、adapter、import smoke test 和 rollback note；
- 基于真实消费项目证据扩展 opt-in checker，避免只凭模板存在就误报 `project_gui_verified_with_shared_runtime`；
- 仅在具体项目具备独立版本、隔离或自包含打包需求时，推进 `project-local-override`；
- 仅在用户请求可执行文件时，推进 PyInstaller/Nuitka 打包 opt-in 与 packaging preflight；
- 仅在用户请求可见 GUI 验证时，推进截图、人工 QA 或 `pytest-qt` 等交互测试。

当前已落地的共享面任务可复用为模板和 checker 基线，但不能被误报为任意消费项目已经 `project_gui_verified_with_shared_runtime`、`project_local_override_ready`、`packaged` 或 `release_ready`。

跨项目 launcher 取舍已在当前证据集下收口：继续使用每个消费项目生成的 `tools/gui/run_gui.ps1` 作为默认入口；只有后续第二个及以上消费项目证明存在无法由 per-project wrapper 吸收的重复 launcher 逻辑时，才重新评估 `run-shared-pyside6-gui.ps1`。

## 21. 验收标准

本方案完成的标准：

- 英文和中文方案文件存在；
- `docs_bilingual/docs_registry.yaml` 已登记该方案；
- 方案明确 `D:\PythonProject_langgraph\.shared_runtimes\pyside6` 是默认共享 PySide6 runtime；
- 方案明确 `.shared_runtimes/` 是本地产物，必须 gitignored，不提交 runtime 二进制、site-packages、Qt 插件、缓存或日志；
- 方案明确不默认全局安装 PySide6，也不默认在每个消费项目 `.venv` 中安装 PySide6；
- 方案明确消费项目默认通过 runtime contract 和 run wrapper 调用共享 runtime；
- 方案明确项目业务依赖不应静默安装进共享 runtime；
- 方案明确什么时候启用、什么时候不启用，以及什么时候允许项目-local override；
- 方案给出共享 runtime helper、项目 opt-in helper、runtime contract、最小项目布局、模板契约和 smoke test；
- 方案定义测试、打包、回滚和授权边界；
- 方案定义共享 runtime 与项目 GUI 能力状态模型，避免把政策文本误报为运行时就绪；
- 方案定义小步实施切片、每个切片的交付物和合入闸门；
- 方案包含按实施顺序排列的细颗粒度实施事项勾选清单，且区分已完成、待授权和按需触发事项；
- 方案明确目标项目发现、共享 runtime preflight、GUI/业务边界、worker/adapter 边界和配置数据路径要求；
- 方案明确结构化 helper preview 证据、可见 GUI 启动边界和打包数据排除要求；
- 方案列出关键失败模式与排障路径；
- repo-local `pyside6-gui` skill 可通过 `plugin-modules` soft-load 路由被发现，同时不 hard-load plugin、不修改用户级配置；
- 实施保持本地-only，未获得用户明确授权前不推送远端。
