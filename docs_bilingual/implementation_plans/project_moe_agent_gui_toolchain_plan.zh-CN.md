---
doc_id: project_moe_agent_gui_toolchain_plan
lang: zh-CN
status: draft
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md
created_at: 2026-05-20
related_docs:
  - docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.zh-CN.md
---

# 项目级 MOE Agent GUI 工具链方案

> 冷启动契约：本文定义项目级 MOE Agent 的开关状态模型和独立 PySide6 GUI 工具链。GUI 源码由 `D:\PythonProject_langgraph` 统一维护，但安装到哪个项目，就只控制哪个项目的会话状态。

## 1. 目标

为每个本地项目提供一套可复用的 MOE AI Agent 定义、开关和 GUI 控制方式，同时避免跨仓库混用项目私有 Agent、私有提示源、会话状态和 GUI 工具。

当前急需项目是 `D:\PythonProject_paper_suggest`，它需要通过 `thesis-moe-on.cmd` 与 `thesis-moe-off.cmd` 控制“论文质量要求极高的导师型 MOE Agent”。后续其他项目应能按同一结构添加自己的 MOE Agent。

## 2. 与 PySide6 通用能力方案的关系

`pyside6_cross_project_gui_capability_plan.zh-CN.md` 定义的是本地项目如何获得通用 PySide6 GUI 能力。本文范围更窄：

- 只覆盖 MOE Agent 控制面；
- 独立拥有 `project_moe_gui` 工具链命名空间；
- 不得混入通用 GUI 工具；
- 定义“GUI 安装到哪个项目，就控制哪个项目 session”的规则。

如果两份方案出现重叠，MOE Agent 控制行为以本文为准，PySide6 安装与排障通用建议以 PySide6 通用能力方案为准。

## 3. 非目标

本文不做：

- 立即实现 GUI；
- 把项目私有 `MOE.md` 全文复制到用户级配置；
- 默认把项目专属 MOE Agent 安装到 `C:\Users\lenovo\.codex\agents`；
- 第一版就创建跨项目总控台；
- 允许安装在某个项目里的 GUI 默认读取或写入其他项目的 `.omx/state`；
- 把 workflow skills、plugin profiles 或 GUI profile loading 当成 native expert evidence。

## 4. 项目级 MOE Agent TOML 标准

每个项目的 MOE Agent 默认放在目标仓库内：

```text
<project>/.codex/agents/<project-moe-agent>.toml
```

TOML 采用“固定核心字段 + 扩展字段”格式。

必填顶层字段：

```toml
name = "project-moe-agent-name"
description = "Short human-readable description."
developer_instructions = """
Project-local MOE instructions.
"""
```

推荐标准扩展区：

```toml
[project]
scope = "repo-local"
state_namespace = "project_moe"
private_prompt_source = "MOE.md"
private_prompt_policy = "do-not-copy-full-content"

[moe]
kind = "project-moe-agent"
family = "project-specific"
requires_manual_enable = true
project_default_state = ".omx/state/project_moe/project-default.json"
session_state_dir = ".omx/state/project_moe/sessions"

[dispatch]
mode = "brief-based"
forbidden = ["full-history-fork-with-custom-role"]
fallback = ["main-session-takeover", "durable-brief"]

[extensions]
# 允许放项目专属字段。
```

checker 可以先沿用现有 `name`、`description`、`developer_instructions` 校验；后续对启用 MOE GUI 工具链的项目，再逐步强制校验这些标准扩展区。

## 5. 专家派发策略

项目级 MOE Agent 禁止使用以下不兼容组合：

```text
full-history fork + specified custom role
```

必须改用以下兼容模式之一：

1. 主会话接管：leader session 读取 repo-local TOML 后直接按 MOE 规则执行审查；
2. brief-based fresh dispatch：leader 生成最小任务 brief，只把 brief 交给兼容的专家执行面；
3. durable brief：LangGraph 或 native_omx lane 读取目标项目 `.omx/state` 下的 frozen brief。

expert timeout、stalled expert 或 full-history fork 失败都不是有效证据。会话必须重试兼容 brief、切到 durable brief，或明确记录 main-session takeover。

## 6. 第一阶段：`paper_suggest` 急需命令行控制

第一阶段增强 `D:\PythonProject_paper_suggest` 已有 thesis MOE 控制。

目标行为：

- `thesis-moe-on.cmd` 开启项目默认值、所有已登记现有 session，以及后续新建 session；
- `thesis-moe-off.cmd` 关闭项目默认值、所有已登记现有 session，以及后续新建 session；
- CLI 继续支持通过 `--session-id` 做单 session 覆盖；
- 项目级 `.cmd` 操作会有意覆盖已登记 session 状态；后续 GUI 可再次单独设置某个 session。

状态布局：

```text
.omx/state/thesis_moe/project-default.json
.omx/state/thesis_moe/sessions/<session-id>.json
```

最小项目默认 JSON 契约：

```json
{
  "schema_version": 1,
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "scope": "project-default",
  "enabled": true,
  "worktree": "D:\\PythonProject_paper_suggest",
  "branch": "main",
  "updated_at": "2026-05-20T00:00:00+00:00",
  "reason": "project-on"
}
```

最小 session JSON 契约：

```json
{
  "schema_version": 1,
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "scope": "session",
  "enabled": true,
  "session_id": "session-id",
  "session_id_source": "argument",
  "raw_session_id_sha256": "sha256",
  "worktree": "D:\\PythonProject_paper_suggest",
  "branch": "main",
  "updated_at": "2026-05-20T00:00:00+00:00",
  "reason": "manual-session-on"
}
```

“已登记现有 session”指 `sessions/` 下已经存在的 JSON 记录。未写过记录的历史会话无法自动发现；它们第一次调用 `status` 或 `assert-on` 时继承项目默认值。

有效状态规则：

1. 如果存在有效 session 记录，使用 session 记录；
2. 否则使用有效项目默认值；
3. 否则 fail closed，视为关闭。

session 身份规则：

- `--session-id` 是最强身份来源，脚本或 GUI 精确控制某个已知 session 时必须优先使用它；
- 存在 `THESIS_MOE_SESSION_ID`、`CODEX_SESSION_ID`、`OPENAI_CODEX_SESSION_ID`、`OH_MY_CODEX_SESSION_ID`、`OMX_SESSION_ID`、`CODEX_SESSION` 等运行时环境变量时，可以用它们作为 session id；
- 如果没有稳定 session id，CLI 可以根据 worktree、branch 和用户生成项目本地兼容 id。该 generated id 足够支撑单个本地工作流，但不是同一 worktree、同一 branch 下多个并发会话的强隔离边界；
- GUI 必须显示 `session_id_source`，让用户区分真实 session id 与 generated 兼容 id。

推荐 CLI 表面：

```powershell
python .\tools\thesis_moe_mode.py project-on
python .\tools\thesis_moe_mode.py project-off
python .\tools\thesis_moe_mode.py project-status --json
python .\tools\thesis_moe_mode.py list-sessions --json
python .\tools\thesis_moe_mode.py on --session-id <id>
python .\tools\thesis_moe_mode.py off --session-id <id>
python .\tools\thesis_moe_mode.py status --json
python .\tools\thesis_moe_mode.py assert-on
```

命令语义：

| 命令 | 写入位置 | 效果 |
| --- | --- | --- |
| `project-on` | 项目默认值和已登记有效 session 文件 | 开启默认值和已知 session。 |
| `project-off` | 项目默认值和已登记有效 session 文件 | 关闭默认值和已知 session。 |
| `project-status --json` | 不写入 | 报告项目默认值、已登记 session 数、无效记录和状态路径。 |
| `list-sessions --json` | 不写入 | 为 GUI 和诊断列出已登记 session 记录。 |
| `on --session-id <id>` | 单个 session 文件 | 开启该 session 覆盖。 |
| `off --session-id <id>` | 单个 session 文件 | 关闭该 session 覆盖。 |
| `status --json` | 不写入 | 报告当前或显式 session 的有效状态。 |
| `assert-on` | 不写入 | 只有有效状态为开启时返回 0。 |

无效的已登记 session 文件不得阻塞项目级 on/off。脚本应报告这些文件为 skipped invalid records，并保持原文件不变。

`list-sessions --json` 只返回控制所需的脱敏标识和元数据：session id、来源、enabled、validity、status reason、branch、worktree、时间戳、reason 和 state path。它不得暴露 raw session id，不得包含私有提示词内容。

兼容要求：

- 现有 `status --json` 保持机器可读；
- 现有 session state 文件保持可读取；
- 损坏、session 不匹配或越界状态必须 fail closed。

第一阶段实施顺序：

1. 扩展 `tools/thesis_moe_mode.py`，增加项目默认状态的读取和写入 helper；
2. 新增 `project-on`、`project-off`、`project-status` 命令；
3. 让 `status` 和 `assert-on` 按“session 覆盖、项目默认值、fail-closed 关闭”的顺序计算有效状态；
4. 更新 `thesis-moe-on.cmd` 与 `thesis-moe-off.cmd`，默认调用项目级命令；
5. 更新使用说明和测试，覆盖项目默认值、已登记 session 传播和单 session 覆盖。

第一阶段不得修改论文正文、私有提示词内容、浏览器自动化或文献检索行为。

## 7. 第二阶段：独立 PySide6 项目 MOE GUI

GUI 源码由本仓库统一维护，但必须与本仓库其他 GUI 工具明确隔离。

`D:\PythonProject_langgraph` 内 source of truth 布局：

```text
tools/project_moe_gui_toolchain/
  src/project_moe_gui/
  install_project_moe_gui.py
  update_project_moe_gui.py
  check_project_moe_gui_install.py
  templates/
```

目标项目安装布局：

```text
<project>/tools/project_moe_gui/
  launcher.py
  project_moe_gui.config.json
<project>/project-moe-gui.cmd
```

隔离规则：

- MOE GUI 源码不得放入通用 `tools/gui` 目录；
- 不复用其他 GUI 工具的状态目录；
- 中央工具链不得导入项目私有 `MOE.md`；
- 默认不做跨项目扫描；
- 安装后的 GUI 只能控制从 launcher 路径或显式 `--project-root` 解析出来的项目根目录。

第一版 GUI 功能：

- 显示项目默认状态；
- 列出已登记 session 记录；
- 开启/关闭项目默认值；
- 开启/关闭选中的单个 session；
- 调用与 `.cmd` 相同的项目本地 CLI 脚本；
- 显示解析出的项目根目录和 state namespace，避免误控其他项目。

第一版 GUI 布局：

- 顶部横幅：解析出的项目根、agent name、state namespace 和当前分支；
- 项目默认卡片：有效默认状态、最后更新时间和开启/关闭按钮；
- session 表格：session id、来源、有效状态、覆盖状态、分支、更新时间、reason 和有效性；
- 操作面板：刷新、开启选中 session、关闭选中 session；如果后续 CLI 支持，再增加清除选中 session 覆盖；
- 日志面板：实际调用的 CLI 命令、退出码和简短 stdout/stderr 摘要。

第一版 GUI 不得直接编辑 JSON 文件。所有状态变更都通过项目本地 CLI 完成，避免 CLI 和 GUI 行为漂移。
GUI session 表格应通过 `list-sessions --json` 填充；如果该命令不可用，GUI 必须给出可执行错误提示，而不是在 v1 里直接扫描 `.omx/state`。

安装后的 GUI 配置：

```json
{
  "schema_version": 1,
  "toolchain": "project_moe_gui",
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "mode_cli": "tools/thesis_moe_mode.py",
  "project_root_strategy": "launcher-parent-git-root",
  "pyside6_runtime": "project-or-shared-runtime"
}
```

GUI 必须把该配置视为目标项目配置。它不得读取中央工具链状态来决定目标项目 session。

## 8. 安装与更新模型

`D:\PythonProject_langgraph` 是 GUI 工具链 source of truth。目标项目只接收安装产物。

安装/更新规则：

- 安装到 `<project>` 时只写该项目根目录内的文件；
- 更新可以刷新 launcher、配置模板和 GUI 包装文件；
- 更新不得覆盖项目私有 `MOE.md`、`.codex/agents/*.toml` 或已有 `.omx/state` 记录；
- 更新必须幂等，并报告变更文件；
- 回滚依赖目标项目自身 Git 历史，必要时结合本地 backup refs。

安装器命令表面：

```powershell
python tools/project_moe_gui_toolchain/install_project_moe_gui.py --target-project <project> --agent-name <agent> --state-namespace <namespace>
python tools/project_moe_gui_toolchain/update_project_moe_gui.py --target-project <project>
python tools/project_moe_gui_toolchain/check_project_moe_gui_install.py --target-project <project> --json
```

如果目标项目没有匹配的 `.codex/agents/<agent>.toml`，安装器必须失败；除非后续另行增加显式模板生成模式。

PySide6 runtime 可以来自有文档记录的共享 GUI runtime，也可以来自目标项目自己的虚拟环境。第一版实现必须在安装配置里记录使用哪种 runtime；如果 PySide6 不可用，必须给出可执行的错误提示。

## 9. 安全与回滚规则

实施和更新命令必须：

- 写入前打印解析出的目标项目根目录；
- 拒绝写入目标项目根目录以外的位置；
- 拒绝覆盖 `MOE.md`、`.codex/agents/*.toml` 或 `.omx/state`，除非后续另行创建显式 repair 命令；
- 在目标项目内形成可由 Git 审查的变更；
- 输出足够状态信息，让用户能看清变更的是项目默认值还是单 session 覆盖。

如果更新中途失败，重复运行安装器或更新器必须是安全的。项目状态回滚依赖目标项目 Git 历史，以及 `.omx/state` 下的状态 JSON 文件。

## 10. 校验与验收

本文档级验收：

- 英文与中文方案文件成对存在；
- 方案明确区分 MOE GUI 工具链和通用 GUI 工具；
- 方案定义项目默认值 + session override 行为；
- 方案禁止项目级 MOE Agent 使用 `full-history fork + specified custom role`。

第一阶段验收：

- `thesis-moe-on.cmd` 能开启项目默认值和已登记 session；
- `thesis-moe-off.cmd` 能关闭项目默认值和已登记 session；
- 新 session 继承项目默认值；
- 显式 `--session-id` 覆盖有效；
- `assert-on` 遵循有效状态规则。

第二阶段验收：

- GUI 安装到 `paper_suggest` 后只控制 `paper_suggest`；
- GUI 安装到第二个项目后只控制第二个项目；
- GUI 更新不覆盖目标项目私有 Agent TOML、`MOE.md` 或 state；
- GUI 操作结果与 CLI status 一致。

## 11. 下一步实施边界

本文确认后，具体实施按以下顺序推进：

1. 先在 `D:\PythonProject_paper_suggest` 实施并测试第一阶段；
2. 如果第一阶段暴露出可复用契约缺口，再回到本仓库补充项目级 MOE TOML/checker 期望；
3. 在本仓库实现独立 `project_moe_gui` 工具链；
4. 把 GUI 安装到 `paper_suggest` 作为第一个目标项目；
5. 第一个目标稳定后，再把 installer 泛化给其他项目。

命令行状态模型稳定之前，不启动 PySide6 GUI 实现。
