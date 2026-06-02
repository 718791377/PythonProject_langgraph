---
doc_id: pyside6_cross_project_gui_capability_plan
lang: zh-CN
status: draft
plan_readiness: full-comet-structure-ready-for-maintenance-slicing
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md
created_at: 2026-05-20
updated_at: 2026-06-02
comet_change: refine-pyside6-gui-plan-comet-structure
related_docs:
  - docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md
  - docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md
  - docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md
  - docs_bilingual/memory/pyside6_first_consumer_apply_2026-05-22.zh-CN.md
  - docs_bilingual/memory/pyside6_explicit_trigger_gates_2026-05-22.zh-CN.md
---

# PySide6 跨项目 GUI 能力方案（完整 Comet 重构版）

> **For agentic workers:** 本方案结构性变更应使用 `$comet` 控制层；必须与英文主文件 `pyside6_cross_project_gui_capability_plan.md` 成对维护。不得把共享 PySide6 runtime、helper、模板或 skill 的存在误报为任意消费项目已经 GUI-ready。

**目标：** 由 `D:\PythonProject_langgraph` 维护一个共享 PySide6 runtime，同时允许每个消费项目保留自己的 GUI 源码、adapter、测试、文档和按需打包决策。

**架构：** 本仓库维护共享 runtime、helper、template 与 checker；消费项目通过显式 runtime contract 和项目本地 wrapper 调用共享 runtime；默认不向消费项目静默安装 PySide6。

**技术栈：** Windows PowerShell helper、Python 3.12 共享虚拟环境、PySide6/Qt、JSON runtime contract、import-only smoke test、repo-local checker、OpenSpec/Comet 证据、本地 main 优先 Git 流程。

---

## 0. 本次完整 Comet 重构结论

原方案方向正确，但仍是旧版长文结构。本版改成与新版 Pi sidecar 方案和 Comet runtime 方案一致的可执行方案结构：复核结论、关系模型、目标/非目标、工作边界、运行时架构、source-of-truth、契约、状态模型、门禁、实施事项、验证计划、回滚、风险与自检。

本方案继续保持 `status: draft`。这里的 `draft` 表示它是能力与实施方案，不是全局强制治理政策；但不表示共享 runtime 基线不存在。当前已经落地或记录的事实包括：

- 默认共享 runtime 根目录是 `D:\PythonProject_langgraph\.shared_runtimes\pyside6`；
- `.shared_runtimes/` 是本地-only 且已 gitignore；
- 本机共享 runtime 已 provision，并以 import-only 方式验证 Python 3.12.10、PySide6 6.11.1、Qt 6.11.1；
- repo-local helper、template、`pyside6-gui` skill、operator 文档和 checker 已按共享 runtime 默认行为更新；
- 首个已登记消费项目已经完成 shared-mode opt-in 和 import-only smoke 证据；项目专属路径和提交号保留在 memory artifact，不写入本通用方案；
- 默认启动入口仍是每个消费项目生成的 `tools/gui/run_gui.ps1`；跨项目 launcher 只有在至少两个消费项目证明存在 per-project wrapper 无法吸收的重复 launcher 逻辑后才重新评估。

剩余高影响动作均为显式触发门：

- 项目本地 PySide6 override；
- 可见 GUI 验证、截图或人工 QA；
- PyInstaller/Nuitka 可执行文件打包。

泛化的“继续”“继续实施方案”不授权这些高影响动作；必须有具名目标项目和明确理由。

## 1. 关系模型与命名边界

| 名称 | 本方案中的角色 | 所有者 | 边界 |
| --- | --- | --- | --- |
| `D:\PythonProject_langgraph` | 共享 GUI runtime 与治理仓库 | 本仓库 | 维护可复用 helper、template、checker、文档和共享 runtime 维护脚本。 |
| `.shared_runtimes/pyside6` | 本地-only 共享 PySide6 runtime | 本仓库在本机维护 | 包含 `.venv`、runtime 元数据、日志和包产物；不得提交。 |
| 消费项目 | 需要本地桌面 GUI 的项目 | 消费项目 | 拥有 GUI 源码、adapter、测试、文档、项目 wrapper 和推广证据。 |
| `pyside6-gui` skill | Codex 路由和说明表面 | 本仓库 | 说明如何使用共享 runtime；不是 native subagent，也不是 readiness 证据。 |
| `ensure-shared-pyside6-runtime.ps1` | 共享 runtime preview/provision/verify helper | 本仓库 | 只能创建或验证共享 runtime 根目录。 |
| `ensure-pyside6-gui.ps1` | 消费项目 opt-in helper | 本仓库 | `apply` 只写目标项目 GUI 文件；默认 `shared` 模式。 |
| `project-local-override` | 显式例外模式 | 消费项目，在本仓库 guardrail 下使用 | 仅用于独立版本、隔离、离线分发、自包含打包或实验需求。 |
| 打包 | 可选 executable build | 消费项目 | 需要显式触发和 packaging preflight；不属于默认 shared-runtime opt-in。 |

## 2. 目标与非目标

目标：

1. 为本地项目提供可复用 PySide6 能力，同时不污染系统 Python 或每个项目 `.venv`。
2. 由本仓库维护共享 runtime，并通过 repo-local 脚本可重建。
3. 消费项目 GUI 代码仍保留在消费项目本地。
4. preview/apply/verify 行为通过 JSON 摘要机器可读。
5. 当目标项目根、共享 runtime 或可写范围不明确时 fail closed。
6. 可见 GUI 和打包副作用保留显式门禁。

非目标：

- 默认不安装 PySide6 到系统 Python 或用户 site-packages；
- 默认不把 PySide6 静默安装进每个消费项目；
- 不把消费项目业务依赖安装进共享 PySide6 runtime；
- 不为所有项目强制同一种 GUI 布局或设计语言；
- 不修改 plugin/vendor cache；
- 默认不打包可执行文件；
- 不把消费项目 GUI 源码存放到本仓库；
- 当前用户消息未明确授权远端发布前，不推送 GitLab/GitHub。

## 3. Comet / OpenSpec 工作边界

本次重构使用完整 Comet/OpenSpec 记录，因为本方案约束后续跨项目 runtime 行为。当前 change 仅限文档和证据结构：

- 更新中英文实施方案对；
- 为方案 contract 创建 OpenSpec change 包；
- 创建 Superpowers design 与 implementation-plan 记录；
- 不安装 PySide6，不写消费项目，不启动可见 GUI，不打包可执行文件，不修改用户级配置。

### 3.1 Comet 管理记录、阶段门禁与 Monitoring 语义

- Open：确认为什么方案需要完整可执行结构，以及成功标准是什么。
- Design：确认关系模型、runtime 所有权、消费项目所有权、状态模型和显式触发门。
- Build：重写中英文方案对和支持 artifact。
- Verify：运行文档、OpenSpec、precommit、本地 gate 和本地 MR review 证据。
- Archive：等本地集成证据记录后，再显式归档当前 active change。
- Monitoring：跨阶段控制回路。如果验证发现目标项目边界、runtime claim 或 artifact 配对缺口，应按需回退到 Open/Design/Build。Monitoring 不是第六阶段。

如果当前 Windows shell 不能运行 Comet `.sh` 脚本，必须记录 blocker，并使用 OpenSpec/repository gate 作为替代证据；不得声称未运行的 Comet script transition 已通过。

### 3.2 完整 `/comet` 结构对齐清单

- [x] 复核结论与状态解释。
- [x] 关系模型与命名边界。
- [x] 目标与非目标。
- [x] Comet/OpenSpec 工作边界。
- [x] 运行时架构。
- [x] Codex/helper/消费项目使用模型。
- [x] Repo-local source of truth。
- [x] 共享 runtime 产物与 receipt 期望。
- [x] Helper CLI/PowerShell/JSON contract。
- [x] Runtime contract 与状态 schema。
- [x] 安全、隐私、回滚和授权规则。
- [x] 能力与 readiness 状态门。
- [x] 有序细颗粒度实施事项。
- [x] 文件职责图。
- [x] 本地集成顺序与证据留存。
- [x] 验证计划、相关文档规则、风险与自检。

## 4. 运行时架构

```text
Codex request / operator request
  -> pyside6-gui skill 或直接 helper 选择
  -> repo-local helper preview
  -> shared runtime preflight
  -> 生成或检查消费项目文件
  -> 通过共享 runtime 做 import-only smoke
  -> 可选显式 visible GUI 或 packaging gate
```

默认共享 runtime：

```text
D:\PythonProject_langgraph\.shared_runtimes\pyside6
  .venv\
    Scripts\python.exe
  requirements-pyside6.txt
  runtime.json
  logs\
```

设计规则：

- 共享 runtime 可删除、可重建、本地-only；
- `runtime.json` 记录解释器、Python 版本、PySide6 版本、Qt 版本、helper 版本、时间戳、import-only 健康状态和回滚/移除步骤；
- 共享 runtime provision 是本仓库维护任务，不是消费项目 opt-in 的静默副作用；
- 消费项目业务依赖仍留在消费项目 runtime，通过 adapter、CLI、HTTP、IPC 或 worker 边界访问。

## 5. Codex / Helper / 消费项目使用方式

自然语言触发示例：

```text
给这个项目做一个本地 PySide6 GUI。
让这个项目使用共享 PySide6 runtime。
预览 <project-root> 的 GUI opt-in。
验证 PySide6 GUI import smoke test。
把这个 GUI 打包成可执行文件。  # 显式 packaging gate
运行可见 GUI 验证。             # 显式交互 gate
```

默认执行：

1. 识别目标项目根目录；
2. 验证 `D:\PythonProject_langgraph\.shared_runtimes\pyside6` 存在且可以 import PySide6；
3. 运行项目 opt-in preview；
4. 在当前任务授权范围内，仅 apply 目标项目 GUI 文件；
5. 通过共享 runtime 运行 import-only smoke；
6. 消费项目证据记录在消费项目或 memory artifact，不写入本通用方案；
7. 未显式请求前停在可见 GUI 和打包之前。

## 6. Repo-local source of truth

本仓库预期可复用表面：

```text
.codex/skills/pyside6-gui/SKILL.md
tools/pyside6_gui_helpers/ensure-shared-pyside6-runtime.ps1
tools/pyside6_gui_helpers/ensure-pyside6-gui.ps1
tools/pyside6_gui_templates/
tools/check_pyside6_shared_runtime_contract.py
tools/check_pyside6_gui_preview_helper_contract.py
tools/check_pyside6_gui_skill_contract.py
tools/check_pyside6_gui_template_contract.py
tools/check_pyside6_operator_usage_guide.py
tools/check_pyside6_project_opt_in_contract.py
tools/check_pyside6_packaging_opt_in_contract.py
docs_bilingual/memory/pyside6_first_consumer_apply_2026-05-22.md
docs_bilingual/memory/pyside6_explicit_trigger_gates_2026-05-22.md
```

消费项目拥有：

```text
src/<project_name>_gui/
tests/test_gui_import.py
tools/gui/pyside6_runtime_contract.json
tools/gui/run_gui.ps1
tools/gui/check_pyside6_env.py
tools/gui/adapters/
描述项目专属 GUI 用法的 docs 或 notes
```

## 7. 共享 runtime 产物与 receipt

最小共享 runtime 元数据：

```json
{
  "schema_version": 1,
  "runtime_mode": "shared",
  "runtime_owner_repo": "D:/PythonProject_langgraph",
  "runtime_root": "D:/PythonProject_langgraph/.shared_runtimes/pyside6",
  "runtime_python": "D:/PythonProject_langgraph/.shared_runtimes/pyside6/.venv/Scripts/python.exe",
  "python_version": "3.12.x",
  "pyside6_version": "6.x",
  "qt_version": "6.x",
  "import_only_verified": true,
  "visible_gui_verified": false,
  "packaging_verified": false,
  "created_at": "<iso8601>",
  "updated_at": "<iso8601>",
  "rollback_steps": [
    "移除本地-only runtime root。",
    "如有需要，通过本仓库 helper 重新 provision。"
  ]
}
```

Runtime receipt 不得包含 API key、业务数据、除 runtime path 以外的私有项目路径或大段日志。

## 8. Helper CLI / PowerShell / JSON contract

共享 runtime helper：

```powershell
tools/pyside6_gui_helpers/ensure-shared-pyside6-runtime.ps1 `
  -Mode preview|provision|verify `
  -RuntimeRoot D:\PythonProject_langgraph\.shared_runtimes\pyside6 `
  -Json
```

项目 opt-in helper：

```powershell
tools/pyside6_gui_helpers/ensure-pyside6-gui.ps1 `
  -ProjectRoot <target-project-root> `
  -Mode preview|apply `
  -RuntimeMode shared|project-local-override `
  -RuntimeRoot D:\PythonProject_langgraph\.shared_runtimes\pyside6 `
  -CreateTemplate `
  -RunSmokeTest `
  -Json
```

必需 helper 输出字段：

| Field | Purpose |
| --- | --- |
| project_root | resolved target project root that the helper may inspect or write. |
| project_root_evidence | evidence used to prove the target root, such as Git root, marker files, or explicit input. |
| runtime_mode | selected runtime mode: shared default or project-local-override exception. |
| shared_runtime_root | repository-maintained shared runtime directory. |
| shared_runtime_python | Python executable inside the shared runtime. |
| shared_runtime_status | shared runtime preflight result, such as ready, missing, stale, or blocked. |
| planned_file_changes | target-project files that preview/apply would create or modify. |
| planned_commands | commands the helper would run during apply or smoke verification. |
| local_only_artifacts | local artifacts that must remain untracked, such as logs, caches, runtime folders, or build output. |
| blockers | fail-closed reasons that prevent apply or verification. |
| rollback_steps | concrete cleanup steps for generated project or runtime files. |
| smoke_test_command | import-only verification command using the selected runtime. |
| visible_gui_requires_explicit_request | boolean gate that prevents interactive windows from launching by default. |
| packaging_requires_explicit_request | boolean gate that prevents executable packaging from running by default. |

Fail-closed 条件：

- 无法证明目标项目根目录；
- `shared` 模式下共享 runtime 缺失；
- helper 将写出 `ProjectRoot`；
- `shared` 模式下会把 PySide6 安装进消费项目 `.venv`；
- project-local override 缺少 `OverrideReason`；
- 未显式触发就要运行可见 GUI 或打包。

## 9. Runtime contract 与状态模型

默认消费项目 contract：

```json
{
  "schema_version": 1,
  "runtime_mode": "shared",
  "runtime_owner_repo": "D:/PythonProject_langgraph",
  "runtime_root": "D:/PythonProject_langgraph/.shared_runtimes/pyside6",
  "runtime_python": "D:/PythonProject_langgraph/.shared_runtimes/pyside6/.venv/Scripts/python.exe",
  "project_root": "<target-project-root>",
  "business_runtime_mode": "project-local-adapter",
  "import_only_smoke": "required",
  "visible_gui_requires_explicit_request": true,
  "packaging_requires_explicit_request": true,
  "project_local_override_reason": null,
  "visual_dependencies": [],
  "license_manifest_path": null
}
```

能力状态：

| 状态 | 含义 | 晋升证据 |
| --- | --- | --- |
| `documented` | 方案和治理存在。 | 双语方案和 registry。 |
| `repo_helper_ready` | helper/template/checker 存在。 | repo guard 和定向测试通过。 |
| `shared_runtime_ready` | 本机共享 runtime 可以 import PySide6。 | 共享 runtime `verify` 输出和 `runtime.json`。 |
| `project_previewed` | 目标项目 preview 无 blockers。 | 无 blockers 的 preview JSON。 |
| `project_gui_scaffolded` | 目标项目已有生成的 GUI 文件。 | 项目 diff 和 contract 文件。 |
| `project_gui_verified_with_shared_runtime` | 通过共享 runtime 做 import-only smoke。 | `import_only_verified=true` 的 smoke JSON。 |
| `project_local_override_ready` | 目标项目有获批独立 runtime。 | override reason、依赖/lock 证据、rollback。 |
| `visible_gui_verified` | 已有意进行交互 GUI 检查。 | 截图、人工 QA 清单或 GUI-capable test 证据。 |
| `packaged` | 已有意构建可执行/安装产物。 | packaging preflight 和 build receipt。 |

不得从 `shared_runtime_ready` 直接跳到 `visible_gui_verified` 或 `packaged`。

## 10. 安全、隐私、回滚与授权

安全规则：

- 先 preview，再 apply。
- 项目 opt-in 只写显式目标项目根目录内的文件。
- 不修改用户级 Codex config 或 plugin cache。
- 不把消费项目业务数据复制到本仓库。
- 不提交 `.shared_runtimes/`、`.venv`、Qt 二进制、wheel、cache、截图、日志或打包输出，除非后续方案明确定义脱敏证据 artifact。
- 可见 GUI 和打包具有副作用，需要当前任务显式授权。

回滚：

- 共享 runtime 回滚：删除 `.shared_runtimes/pyside6`，如有需要重新运行 provision。
- 消费项目 shared-mode 回滚：根据项目 rollback note 移除生成的 GUI 源码、`tools/gui/`、测试、文档和 contract。
- Project-local override 回滚：根据 override 证据移除依赖声明和 lockfile 变更。
- 打包回滚：移除本地 build/dist 产物并恢复为打包修改过的配置。

## 11. Ready / Bootstrap / Repair lane gates

| Lane | 进入条件 | 允许动作 | 退出证据 |
| --- | --- | --- | --- |
| Ready | 共享 runtime 存在，且项目 preview 无 blockers。 | Apply GUI scaffold，运行 import-only smoke。 | `project_gui_verified_with_shared_runtime`。 |
| Bootstrap | 共享 runtime 缺失或过旧，且本仓库维护动作已授权。 | 仅 provision 或 verify `.shared_runtimes/pyside6`。 | `shared_runtime_ready`。 |
| Repair | 已有项目 GUI 或 runtime contract 不一致。 | 读取、诊断、提出有界修复；目标 ownership 明确后才写。 | 修复后的 preview/smoke 证据。 |
| Override | 项目有不使用共享 runtime 的具体理由。 | 创建项目本地依赖记录和 smoke 路径。 | Override reason、lock 证据、rollback。 |
| Packaging | 用户明确要求可执行/安装产物。 | 运行 packaging preflight 和 build。 | Packaging receipt 和 rollback 证据。 |

## 12. 实施事项清单（按顺序，细颗粒度）

本清单只列具体实施事项，不把“更新本方案文件”本身列为实施事项。

### 12.1 已完成或已有基础

- [x] 盘点已有 PySide6 GUI 基线：template、helper、skill、operator 文档、project opt-in checker、packaging opt-in checker。
- [x] 将默认策略从项目本地安装 PySide6 改为本仓库维护共享 PySide6 runtime。
- [x] 明确默认共享 runtime 路径为 `D:\PythonProject_langgraph\.shared_runtimes\pyside6`。
- [x] 将 `.shared_runtimes/` 写入 `.gitignore`。
- [x] 新增共享 runtime requirements 与 metadata template。
- [x] 新增 `ensure-shared-pyside6-runtime.ps1`。
- [x] 实现共享 runtime `preview`、`provision`、`verify` 模式。
- [x] 为共享 runtime 状态、blockers、planned actions 和 rollback 输出结构化 JSON。
- [x] 为项目 opt-in helper 增加 `-RuntimeMode shared|project-local-override`。
- [x] 将项目 opt-in 默认设为 `shared`。
- [x] 增加 `-RuntimeRoot` 并默认指向共享 runtime 路径。
- [x] 在 shared 模式禁止写依赖声明。
- [x] 在 shared 模式下共享 runtime 缺失时 fail closed。
- [x] 在 shared 模式生成 `tools/gui/pyside6_runtime_contract.json`。
- [x] 在 shared 模式生成 `tools/gui/adapters/README.md`。
- [x] 更新 import-only smoke template，使共享 runtime Python 执行时显式加入目标 `src` 到 `sys.path`。
- [x] 更新项目 `tools/gui/run_gui.ps1` template，使项目通过共享 runtime 启动 GUI。
- [x] 保留消费项目 GUI 源码、adapter、测试、helper 和 rollback note 在消费项目本地。
- [x] 为 `project-local-override` 要求 `-OverrideReason`。
- [x] 为 override 保留依赖/lockfile 和 rollback 证据边界。
- [x] 更新 repo-local `pyside6-gui` skill，说明共享 runtime 默认行为。
- [x] 更新中英文 operator 使用指南，使 preview/apply/verify 与共享 runtime 默认策略一致。
- [x] 新增并注册 PySide6 shared runtime contract checker。
- [x] 扩展 helper、template、skill、operator、project opt-in 和 packaging checker。
- [x] 修复 rollback note 生成逻辑，避免 PowerShell 把 ordered dictionary 序列化进路径列表。
- [x] 将 PySide6 检查注册到 repository guard 和 CI manifest。
- [x] 为共享 runtime 基线运行 PySide6 定向测试、OpenSpec guard、precommit gate、本地 MR review 和本地 CI。
- [x] 将共享 runtime 默认策略合入本地 `main`。
- [x] 在 `.shared_runtimes/pyside6` provision 真实本地共享 runtime。
- [x] 以 import-only 证据验证本地共享 runtime。
- [x] 完成首个已登记消费项目 shared-mode opt-in 和 import-only smoke 证据。
- [x] 将首个消费项目证据记录在 memory artifact，而不是本通用方案。
- [x] 判定 per-project `tools/gui/run_gui.ps1` 当前足够；除非后续至少两个消费项目证明重复 launcher 逻辑无法被项目 wrapper 吸收，否则不新增跨项目 launcher。

### 12.2 剩余显式触发门

- [ ] 仅对具名项目且有独立版本、隔离、离线分发、自包含打包或实验需求时执行 `project-local-override`；记录 override reason、依赖/lock 证据和 rollback。
- [ ] 仅在用户明确要求交互窗口、截图复核、人工 QA 或 GUI-capable test runner 时执行可见 GUI 验证。
- [ ] 仅在用户明确要求可执行文件或安装包，并且 packaging preflight 通过时执行 PyInstaller/Nuitka 打包。

### 12.3 维护 backlog

- [ ] 只有至少两个消费项目证明 per-project wrapper 无法吸收重复 launcher 逻辑时，才重新打开跨项目 launcher 决策。
- [ ] 有意升级 PySide6/Qt/Python 时新增脱敏共享 runtime upgrade receipt。
- [ ] 超过一个项目依赖共享 runtime 后，新增 consumer-project compatibility notes。
- [ ] 将重复失败模式提升为 checker，而不是依赖聊天提醒。

## 13. 实施切片

### Slice 0：方案与 OpenSpec 证据收口

- 范围：维护本双语方案对和 OpenSpec/Comet 支持 artifact。
- 完成标准：方案结构完整、OpenSpec validate 通过、本地 gate 通过。

### Slice 1：共享 runtime 维护

- 范围：provision、verify、upgrade 或 rebuild `.shared_runtimes/pyside6`。
- 完成标准：`runtime.json` 与 import-only verify 证据更新。

### Slice 2：消费项目 shared-mode opt-in

- 范围：对一个具名目标项目 preview/apply/smoke。
- 完成标准：目标项目有 contract、wrapper、GUI shell、测试、rollback note 和 import-only smoke 证据。

### Slice 3：project-local override

- 范围：消费项目独立 runtime。
- 完成标准：reason、依赖/lock 证据、smoke 和 rollback 证据存在。

### Slice 4：可见 GUI 验证

- 范围：交互启动或截图/人工 QA。
- 完成标准：显式请求和 GUI 证据已记录。

### Slice 5：packaging opt-in

- 范围：PyInstaller/Nuitka 或其他打包路径。
- 完成标准：packaging preflight、build receipt、artifact 排除和 rollback 证据存在。

## 14. 文件职责图

| 路径 | 所有者 | 说明 |
| --- | --- | --- |
| `docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md` | 本仓库 | 英文主方案。 |
| `docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.zh-CN.md` | 本仓库 | 中文配套方案。 |
| `openspec/changes/refine-pyside6-gui-plan-comet-structure/` | 本次 change | 仅承载方案 contract 证据。 |
| `docs/superpowers/specs/2026-05-27-pyside6-gui-plan-comet-design.md` | 本次 change | Design record。 |
| `docs/superpowers/plans/2026-05-27-refine-pyside6-gui-plan-comet-structure.md` | 本次 change | Execution record。 |
| `.shared_runtimes/pyside6/` | 本机 | ignored runtime artifact，不提交。 |
| `tools/pyside6_gui_helpers/` | 本仓库 | 可复用 helper source。 |
| 消费项目 `src/*_gui/`、`tools/gui/`、`tests/test_gui_import.py` | 消费项目 | 仅在具名 consumer opt-in 时写入。 |

## 15. 本地集成顺序与证据留存

1. 使用专用 feature worktree 与 branch。
2. 保持主目录在本地 `main`。
3. 中英文方案对成对更新。
4. 创建成对文件时，OpenSpec 与 Superpowers 支持 artifact 也保持双语。
5. 运行 `git diff --check`。
6. 运行 `openspec validate refine-pyside6-gui-plan-comet-structure --strict`。
7. 运行 `python .\tools\check_implementation_plan_rules.py --root . --json`。
8. 运行 `python .\tools\check_precommit_update_archive.py --root . --json`。
9. 运行 `python .\tools\run_openspec_guard.py --root .`。
10. 用中文 commit message 提交。
11. 本地 `main` 集成前运行 local CI 和 local MR review。
12. 合入本地 `main` 前创建本地 rollback backup ref。
13. 仅在本地证据干净后合入本地 `main`。
14. 通过 cleanup helper 清理已合入的 feature worktree 和本地 branch。
15. 当前用户消息未明确授权 GitLab/GitHub 发布前，停在远端发布门之前。

## 16. 验证计划

- git diff --check - checks whitespace and patch hygiene.
- openspec validate refine-pyside6-gui-plan-comet-structure --strict - validates the active OpenSpec change.
- python .\tools\check_implementation_plan_rules.py --root . --json - checks implementation-plan registry and bilingual text health.
- python .\tools\check_precommit_update_archive.py --root . --json - enforces update/archive review before commit.
- python .\tools\run_openspec_guard.py --root . - runs the repository OpenSpec and governance guard.
- powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 300 - runs the shared local CI gate.
- powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 - runs the local MR review gate before local main integration.

未来消费项目 opt-in 还应追加目标项目 preview JSON 和 import-only smoke JSON。可见 GUI 和打包必须追加显式请求证据和 receipt。

## 17. 对相关治理 / 方案的更新要求

以下内容发生变化时，必须同步相关 docs 或 checker：

- 共享 runtime root 或 layout；
- helper CLI 参数或 JSON schema；
- 默认 runtime mode；
- project-local override 条件；
- 可见 GUI 授权边界；
- packaging artifact 处理方式；
- 消费项目证据留存规则；
- `pyside6-gui` 的 skill/profile 路由规则。

除非另有单独获批方案，本方案不得修改全局 Codex config、plugin cache 或用户级 launcher 行为。

## 18. 风险与默认决策

| 风险 | 默认决策 | 缓解 |
| --- | --- | --- |
| 共享 runtime 漂移影响多个项目。 | 升级视为本仓库维护 change。 | Runtime receipt、import-only smoke、consumer compatibility notes。 |
| 消费项目误把 PySide6 安装到本地。 | 默认 shared 模式禁止依赖写入。 | Helper/checker fail closed。 |
| 可见 GUI 阻塞自动化。 | 默认不启动可见 GUI。 | 显式交互 gate。 |
| 打包提交大文件。 | 打包 opt-in，local artifact 默认排除。 | Packaging preflight 与 rollback receipt。 |
| 方案文本被误解成 runtime readiness。 | 使用显式能力状态。 | 没有 smoke/receipt 证据不得晋升。 |
| 过早建设跨项目 launcher。 | 默认继续使用 per-project wrapper。 | 只有两个以上消费项目重复证据后才重开。 |

## 19. 自检清单

- [x] 方案已经改成新版 Comet 可执行结构。
- [x] 方案保持英文和中文文件成对维护。
- [x] 方案保留共享 runtime 路径和 local-only 规则。
- [x] 方案明确默认不全局安装 PySide6，也不安装到每个项目。
- [x] 方案区分共享 runtime readiness 与消费项目 GUI readiness。
- [x] 方案把 project-local override、可见 GUI 和打包保留为显式触发门。
- [x] 方案包含按顺序排列的细颗粒度实施事项。
- [x] 方案包含验证、回滚、风险和证据留存规则。
- [x] 方案不授权远端发布。

## 20. 参考源

- docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md - 最接近的 GUI 相关完整 Comet 可执行方案结构参考。
- docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md - 新版 sidecar 方案结构，用作 contract 和 gate 参考。
- docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md - Comet management record 与 Monitoring 语义参考。
- docs_bilingual/memory/pyside6_first_consumer_apply_2026-05-22.zh-CN.md - 首个消费项目 shared-mode apply 证据。
- docs_bilingual/memory/pyside6_explicit_trigger_gates_2026-05-22.zh-CN.md - override、可见 GUI、打包的显式高影响门证据。
