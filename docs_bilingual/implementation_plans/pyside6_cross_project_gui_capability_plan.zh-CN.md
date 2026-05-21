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
- 默认把每个 GUI 都打包成可执行文件；
- 把本编排仓库变成各消费项目 GUI 源码的存放位置。

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

共享层只拥有可复用知识和模板，不能拥有各项目的运行时依赖，也不能一次性批量修改所有项目。

### 3.2 项目级隔离依赖

每个需要 GUI 的项目自己拥有：

- 自己的 `.venv` 或明确记录的 Python 环境；
- 包含 PySide6 的 `requirements-gui.txt`、dependency extra 或 dependency group；
- GUI 源码；
- 资源文件；
- import smoke tests；
- 可选打包脚本；
- 项目自己的 GUI 验收测试。

## 4. 适用范围与触发规则

项目只在满足下列条件之一时才启用 PySide6：

| 触发条件 | 动作 |
| --- | --- |
| 用户明确要求本地 GUI、桌面 GUI、PySide6、Qt 或 Windows 桌面工具 | 对该项目启动 PySide6 opt-in 流程 |
| 项目已经存在 GUI 源码或 GUI 依赖声明 | 检查并延续该项目已有 GUI 风格 |
| 项目需要小型本地操作台、复核控制台、队列看板或本地工作流 launcher | 实施前把 PySide6 作为候选方案提出 |
| 任务只需要命令行自动化，或项目已有浏览器 UI | 不默认新增 PySide6 |

不得把本方案理解为“主动给每个项目都安装 PySide6”。

## 5. 默认项目布局

项目选择启用时，优先使用这个最小布局，除非项目已有更强约定：

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

## 6. 依赖声明模式

选择一种符合项目现状的依赖声明方式；除非项目本来就有依赖镜像规则，否则不要在多个依赖面重复声明 PySide6。

| 项目风格 | 推荐声明方式 |
| --- | --- |
| 普通 pip / requirements | `requirements-gui.txt` 中写入 `PySide6` 或经复核的版本范围 |
| `pyproject.toml` optional dependencies | `[project.optional-dependencies] gui = ["PySide6"]` |
| dependency groups | 使用 `gui` dependency group |
| uv 管理项目 | 使用项目原生 `uv add --optional gui PySide6` 或等价记录命令 |
| Poetry 管理项目 | 使用项目原生 optional dependency 或 group |
| 已有 GUI 技术栈 | 延续已有 GUI 依赖风格，避免并行约定 |

版本规则：

- 原型阶段可以先用未固定的 `PySide6`；
- 提交到项目工作流后，优先使用版本范围或项目包管理器生成的 lockfile；
- 不得静默跨所有项目统一升级 PySide6。

## 7. 环境设置规则

在某个项目中编写或运行 PySide6 GUI 前：

1. 识别目标项目根目录和 Python 环境；
2. 优先使用项目自己的 `.venv`；
3. 只把 PySide6 安装到该环境；
4. 把依赖写入该项目依赖文件；
5. 运行 import smoke test；
6. 不修改其他项目环境。

额外 preflight 要求：

- 安装前必须确认项目的 Python 版本、解释器架构和包管理器；
- 如果项目还没有虚拟环境，preview 必须先给出明确的环境创建命令和目标路径；
- apply 只能在显式目标项目根目录下创建新环境，除非用户提供并批准外部 `-PythonPath`；
- 不能因为某个全局解释器刚好能 import PySide6，就把项目状态判断为 `env_ready`；
- 可见 GUI 启动属于交互式桌面动作，必须由请求驱动；默认验证仍以 import-only 为主。

最小 smoke 命令：

```powershell
.\.venv\Scripts\python.exe -c "from PySide6.QtWidgets import QApplication; print('PySide6 ok')"
```

Headless 或 CI 环境可以只跑 import-only 测试，不显示窗口；除非项目明确配置了 GUI-capable test runner。

## 8. 用户级 helper 契约

仓库源码中的 `ensure-pyside6-gui.ps1` helper，以及任何安装到用户级目录的副本，都必须采用 preview-first 行为。

必需输入：

- `-ProjectRoot` - 要检查或修改的目标项目根目录
- `-Mode preview|apply` - preview 不改文件，apply 执行项目本地修改
- 可选 `-DependencyStyle auto|requirements|pyproject-extra|group`
- 可选 `-PythonPath`
- 可选 `-PackageVersion`
- 可选 `-CreateTemplate`
- 可选 `-RunSmokeTest`

Preview 输出必须包含：

- 检测到的项目根目录，以及用于判定根目录的证据；
- 检测到的 Python 环境、Python 版本和包管理器；
- 选中的依赖声明方式；
- 将创建或修改的文件；
- 将执行的安装命令；
- smoke test 命令；
- 预计新增的本地-only 产物，例如 `.venv`、build 输出或缓存；
- 风险和回滚说明。

Preview 还应输出机器可读摘要，例如 JSON 字段 `project_root`、`project_root_evidence`、`python_path`、`python_version`、`package_manager`、`dependency_style`、`planned_file_changes`、`planned_commands`、`local_only_artifacts`、`blockers` 和 `rollback_steps`。人类可读输出可以包裹这份摘要，但后续 checker 应消费结构化表面。

Apply 模式必须保持项目本地化；如果无法可靠识别目标项目根目录、依赖管理方式或可写范围，必须 fail closed。

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
| `tools/gui/run_gui.ps1` | 定位项目 venv 并运行 app |
| `tests/test_gui_import.py` | 不显示 GUI，仅验证可导入 |
| worker / service adapter | 承接长耗时任务，避免阻塞 Qt event loop |
| config / data directory adapter | 明确本地配置、缓存和数据目录，不写入仓库外未知位置 |
| logging / diagnostics adapter | 写入可诊断日志，同时避免在普通 UI 输出中泄露凭据或用户私有路径 |

## 10. Codex 执行流程

当用户在任意项目要求 PySide6 GUI 时，Codex 应该：

1. 确认目标项目根目录，并说明判定依据，例如 `.git`、`pyproject.toml`、README 或既有脚本；
2. 检查现有依赖风格（`requirements*.txt`、`pyproject.toml`、`poetry.lock`、`uv.lock` 等）；
3. 选择该项目原生依赖声明方式；
4. 检查是否已有 GUI 技术栈，避免把 PySide6 与既有 GUI 框架并行引入；
5. 修改文件前创建本地回滚边界，例如 feature branch 或提交计划；
6. 新增或更新 GUI 依赖声明；
7. 只有当前需要本地执行时，才把 PySide6 安装到项目环境；
8. 创建或更新 GUI 源码，并保持 GUI shell、业务服务、配置数据路径和 worker 边界分离；
9. 增加 import smoke test；
10. 运行 smoke test；
11. 只有用户明确要求交互式验证，或任务本身已经需要可见窗口时，才启动可见 GUI；
12. 如用户要求打包，再增加打包脚本并运行打包 preflight；
13. GUI 变更保留在目标项目仓库内，除非任务明确是更新共享政策或模板，否则不要写回本编排仓库。

## 11. 测试策略

每个启用 GUI 的项目至少需要：

- 依赖文件在选定依赖面包含 PySide6；
- 项目环境内 `from PySide6.QtWidgets import QApplication` import smoke 通过；
- GUI package 可导入且不显示窗口；
- `tools/gui/run_gui.ps1` 或等价 run helper 能解析项目根目录和 Python 路径；
- 如果 GUI 调用业务逻辑，业务逻辑必须脱离 GUI event loop 单独可测试；
- 长耗时动作必须有 worker、thread、process 或 async 边界，并有取消或失败反馈策略；
- 本地配置、缓存和数据目录必须有文档或 helper 输出证据；
- 排障诊断可以被启用，但不得暴露凭据、访问 token、浏览器 profile 或无关的用户私有路径。

可选测试：

- `pytest-qt` 或同类 GUI 交互测试；
- 截图 / 人工 QA 清单；
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
- 删除约定 GUI 范围之外的项目文件；
- 改写无关项目的 dependency lock；
- 让 GUI helper 访问网络、凭据、浏览器 profile 或用户私有目录，除非任务明确需要且已说明风险；
- 在用户没有要求交互式验证时，从自动化会话启动可见 GUI 窗口。

回滚路径：

- revert 项目本地 commit 或 feature branch；
- 移除项目本地 GUI 依赖声明；
- 删除本轮新生成的 GUI 模板文件；
- 如果 lockfile 被修改，恢复上一版 lockfile；
- 用户级模板保持不动，除非本轮任务本身就是修改模板。

## 14. 跨项目治理

本文是共享政策。消费项目的实现必须留在消费项目自身。

规则：

- 不把消费项目 GUI 源码放进 `D:\PythonProject_langgraph`；
- 不假设一个项目的 PySide6 版本适合另一个项目；
- 不让多个项目 GUI 共用同一个可变 venv；
- 不为了给 GUI 腾空间而禁用 browser 或 web automation skills；
- 如果项目同时需要 GUI 和 browser automation，保持两个能力面分离；
- 项目特定 GUI 决策写入该项目自己的文档或依赖文件；
- GUI helper 只能在显式目标项目根目录内写入模板、脚本和测试，用户级模板更新必须作为单独任务处理。

## 15. 能力状态模型

每个项目本地 GUI 能力都应该使用下列状态之一描述，避免后续会话混淆政策、依赖声明、已安装运行时和已打包产物：

| 状态 | 含义 | 最小证据 |
| --- | --- | --- |
| `not_applicable` | 项目不需要桌面 GUI | 记录过的决策，或没有 GUI 触发条件 |
| `candidate` | 正在评估 PySide6，但尚未采用 | 简短设计说明和备选方案 |
| `declared` | 项目已选择 PySide6 并记录依赖 | dependency file、extra 或 group 已更新 |
| `env_ready` | PySide6 已安装在项目环境内 | import smoke 输出或 lockfile 证据 |
| `template_ready` | 最小 GUI 源码和运行 helper 已存在 | `src/*_gui/`、`tools/gui/` 和 import test |
| `verified` | 项目本地测试在不显示窗口的情况下通过 | import-only 或 headless CI 证据 |
| `packaged` | 用户明确要求可执行文件打包且已验证 | 打包配置、preflight 输出和回滚说明 |

不得只凭政策文本就声称项目已经 `env_ready`、`verified` 或 `packaged`。这些状态必须有项目本地证据。

## 16. 实施切片与推进闸门

该能力必须按小步、可审查的切片实施。后续 implementation change 不应尝试一次性修改所有消费项目。

| 切片 | 目的 | 交付物 | 合入前闸门 |
| --- | --- | --- | --- |
| 0. 盘点 | 查明目标项目现有 GUI 形态和依赖管理方式 | 只读盘点记录 | 不修改项目文件 |
| 1. 政策与模板 | 发布共享政策和最小模板 | 双语方案、模板文件、smoke test 示例 | docs 和模板 checker 通过 |
| 2. Preview helper | 增加 `ensure-pyside6-gui.ps1` preview 模式 | 带人类可读和 JSON `preview` 输出的 helper，不做 apply 修改 | preview 快照已复核，结构化 schema 已被 checker 消费 |
| 3. Apply helper | 允许受控的项目本地修改 | helper `apply` 模式，生成回滚说明 | 在一次性 fixture 中完成 dry-run 与 apply 测试 |
| 4. 项目 opt-in | 为一个消费项目启用 GUI | 依赖声明、GUI shell、import test | 项目本地 gate 通过 |
| 5. 打包 opt-in | 仅在用户要求时打包 | PyInstaller/Nuitka 配置、preflight 脚本 | 打包 preflight 和回滚路径已记录 |

默认推进顺序是 0 -> 1 -> 2 -> 3 -> 4。切片 5 是可选阶段，必须保持请求驱动。

当前本地实施状态：

- 切片 0/1 的共享政策与最小模板已由 `tools/pyside6_gui_templates/` 承载；
- 模板契约由 `tools/check_pyside6_gui_template_contract.py` 和 `test/check_pyside6_gui_template_contract.test.py` 验证；
- 切片 2 的 preview helper 源码已由 `tools/pyside6_gui_helpers/ensure-pyside6-gui.ps1` 承载；
- 切片 3 的受控 `apply` 模式已在 `tools/pyside6_gui_helpers/ensure-pyside6-gui.ps1` 中实现，覆盖 fail-closed 目标根目录检查、依赖声明面更新、模板生成、结构化 `applied_file_changes`，以及 `docs/pyside6_gui_rollback.md` 回滚说明生成；
- preview/apply helper 契约由 `tools/check_pyside6_gui_preview_helper_contract.py` 和 `test/check_pyside6_gui_preview_helper_contract.test.py` 验证，覆盖 preview 只读、一次性 apply fixture 写入，以及不安全根目录 fail-closed；
- CI manifest 已登记两个 PySide6 契约测试，`tools/run_openspec_guard.py` 已运行两个 checker；
- repo-local `pyside6-gui` skill 源文件已由 `.codex/skills/pyside6-gui/SKILL.md` 承载，用于未来会话路由；是否安装或复制到用户级目录仍属于单独的用户级部署决策；
- `plugin-modules` profile helper 已暴露 `pyside6-gui` soft-load 模块，可通过 repo-local `repo:` hint 解析 skill、preview/apply helper、模板和打包 preflight 模板，同时不安装 PySide6、不编辑 `config.toml`、不启用 plugin bundle、不启动可见 GUI、不打包可执行文件；
- `tools/check_plugin_modules_skill.py` 和 `test/check_plugin_modules_skill.test.py` 验证 `pyside6-gui` 模块的 repo-local hint 契约与 hard-load no-op 边界；
- skill 契约由 `tools/check_pyside6_gui_skill_contract.py` 和 `test/check_pyside6_gui_skill_contract.test.py` 验证，`tools/run_openspec_guard.py` 会运行该 checker；
- 切片 4 消费项目 opt-in 证据检查已由 `tools/check_pyside6_project_opt_in_contract.py` 和 `test/check_pyside6_project_opt_in_contract.test.py` 承载；该 checker 验证目标项目根证据、单一经复核 PySide6 依赖声明面、GUI 源码边界、import-only smoke test 行为、run/env helper、回滚说明，以及不得把政策/模板/skill 存在误报为 `env_ready`、`verified` 或 `packaged` 的规则；
- `tools/run_openspec_guard.py` 与 `tools/ci/ci_test_manifest.json` 已登记消费项目 opt-in checker，后续 guard 和 CI 会持续验证共享 opt-in 契约；
- 具体消费项目的切片 4 启用仍按具体项目和请求推进，不得把 helper、模板、skill 或 checker 存在误报为任意消费项目已经 `env_ready`、`template_ready` 或 `verified`；
- 切片 5 打包 opt-in 证据检查已由 `tools/check_pyside6_packaging_opt_in_contract.py` 和 `test/check_pyside6_packaging_opt_in_contract.test.py` 承载；该 checker 要求先通过项目 opt-in 基线、只选择一个打包工具（`PyInstaller` 或 `Nuitka`）、具备打包 preflight 证据、数据排除证据、回滚证据、可复现 build/output-directory 证据，以及 release/signing/distribution 单独授权边界；
- `tools/pyside6_gui_templates/packaging/pyside6_packaging_preflight.ps1.template` 已补充可复现 build 命令、生成产物、输出目录、杀软风险记录、回滚步骤、数据排除和单独发布授权等结构化字段；`tools/run_openspec_guard.py` 与 `tools/ci/ci_test_manifest.json` 已登记打包 opt-in checker；
- 实际可执行文件打包仍保持请求驱动，不得把 checker/模板存在误报为任意消费项目已经 `packaged` 或 `release_ready`。

## 17. 失败模式与排障

常见失败模式必须作为项目本地问题处理，不能通过削弱共享政策解决：

| 现象 | 常见原因 | 推荐处理 |
| --- | --- | --- |
| `ModuleNotFoundError: PySide6` | PySide6 未安装到当前项目 venv | 确认 Python 路径，只安装到项目 venv，再跑 import smoke |
| Qt platform plugin 错误 | Qt plugin 路径或打包产物缺少运行时文件 | 检查项目 venv / package 输出，增加打包 preflight 证据 |
| GUI 测试在 CI 挂起 | headless 环境里运行了 event loop 或可见窗口测试 | 使用 import-only smoke，或配置 GUI-capable test runner |
| 中文文字渲染异常 | 字体 fallback 或打包缺少字体 | 记录字体选择并测试 Windows 渲染 |
| 打包 exe 被杀软警告 | one-file 可执行文件启发式误报 | 记录工具和版本，优先可复现 build，避免未经复核的二进制 |
| helper 无法识别项目根目录 | 目标检测不安全 | fail closed，并要求显式传入 `-ProjectRoot` |

## 18. 后续实施任务

后续剩余 implementation change 可以新增：

- repo-local `pyside6-gui` skill 源文件的可选用户级安装或复制；该动作必须等到明确的用户级部署决策之后再做；
- 跨项目 operator 示例，说明如何在消费项目中调用 `plugin-modules` 的 `pyside6-gui` soft-load 模块而不改变 plugin profile；
- 在具体目标项目采用 PySide6 之后，继续扩展消费项目 opt-in checker 对包管理器 lockfile 行为的覆盖；
- 在具体消费项目请求可执行文件打包之后，继续扩展打包 opt-in checker 对目标项目 lockfile/build-output 的断言。

已落地的共享面任务包括最小 GUI 模板、`check_pyside6_env.py` 与 `run_gui.ps1` 模板、打包 preflight 模板、`ensure-pyside6-gui.ps1` preview/apply 模式、回滚说明生成，以及一次性 apply-mode fixture 覆盖。

## 19. 验收标准

本方案完成的标准：

- 英文和中文方案文件存在；
- `docs_bilingual/docs_registry.yaml` 已登记该方案；
- 方案明确区分用户级共享能力和项目级依赖；
- 方案明确不默认全局安装 PySide6；
- 方案明确什么时候启用、什么时候不启用；
- 方案给出 requirements、`pyproject.toml`、dependency group 和已有 managed project 的依赖声明方式；
- 方案给出最小项目布局、helper 契约、模板契约和 smoke test；
- 方案定义测试、打包、回滚和授权边界；
- 方案定义项目本地 PySide6 能力状态模型，避免把政策文本误报为运行时就绪；
- 方案定义小步实施切片、每个切片的交付物和合入闸门；
- 方案明确目标项目发现、安装前置条件、GUI/业务边界、worker 边界和配置数据路径要求；
- 方案明确结构化 helper preview 证据、可见 GUI 启动边界和打包数据排除要求；
- 方案列出关键失败模式与排障路径；
- repo-local `pyside6-gui` skill 可通过 `plugin-modules` soft-load 路由被发现，同时不 hard-load plugin、不修改用户级配置；
- 实施保持本地-only，未获得用户明确授权前不推送远端。
