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

## 0. 当前状态与本次复核结论

复核日期：2026-05-23。

结论：原方案的架构边界、状态模型、安全规则和阶段门基本完整，但缺少“按事项粒度”的实施进度清单，容易让后续会话无法判断哪些内容已经落地、哪些仍只是方案。本次补齐第 11 节的实施进度勾选清单，并把第 13 节改成基于当前事实的后续实施边界。

状态说明：本文继续保持 `status: draft`。这里的 draft 表示它不是全局 active 治理政策，也不表示全部运行时能力已经完成。Phase 2A 本仓库中央 installer/checker/updater、Phase 2B fixture-safe GUI shell 与 Phase 2C 双 fixture install/check/update/status 隔离证据已确认合入本地 `main`；本仓库已新增 Phase 1 CLI 读取契约 fixture gate、GUI 写入命令输出契约 fixture gate、写入命令 `atomic_write` / `lock_status` fail-closed fixture gate、项目默认值、session override、无效记录、旧记录兼容和 no-op 状态行为 fixture gate，以及只读 Phase 1 readiness checker fixture gate。真实目标项目 Phase 1 CLI 状态模型仍未完成，所以本文继续保持 `draft`。

当前已知本地事实：

- Phase 2A 已合入本仓库本地 `main`：`3e4e819c73c78472d948e68d5352085dcac6551d`（`实现项目 MOE GUI 第二阶段安装器`）。
- Phase 2B 已合入本仓库本地 `main`：`47187a7da4b167341cf0a8fc01db415db601fe92`。
- 本次后续变更新增 Phase 1 CLI 读取契约 fixture 支撑：installer/checker 会在安装前校验 `project-status`、`list-sessions`、`status` 的统一 envelope、`effective_source`、session counts、列表结构与私有字段泄露，避免真实目标项目 Phase 1 尚未落地时 GUI 误接入不完整 CLI。
- 本次后续变更继续新增 GUI 写入命令输出契约 fixture 支撑：GUI 执行 `project-on`、`project-off`、`session-on` 或 `session-off` 后，必须校验 `before`、`after`、`changed_scope`、`changed_paths`、`skipped_invalid_records`、`lock_status`、`audit_path`、`atomic_write`、`no_op`、scope 匹配、原子写入声明、锁状态安全和私有字段泄露，契约不完整时 fail closed。
- 本次后续变更还新增 Phase 1 状态行为 fixture 支撑：项目级 on/off 只传播到项目管理的 session，不覆盖 `manual-session`；单 session override 优先于项目默认值；重复写入返回 `no_op = true`；无效 JSON 记录被分类为 stable token 并跳过，legacy 记录继续兼容读取。
- 本次后续变更新增 `check_project_moe_phase1_readiness.py` 只读 readiness checker：在不写目标项目的前提下检查 dirty Git 状态、Agent TOML、私有 `MOE.md`、CLI 读取契约、CLI 写命令 surface、`thesis-moe-on/off.cmd` wrapper 和 startup hook；该 checker 只提供目标写入前的 go/no-go 证据。
- 这些事实只表示本仓库 fixture 与契约验证支撑已落地；不表示 `D:\PythonProject_paper_suggest` 已完成 Phase 1，也不表示真实目标项目 GUI 已可操作。
- 未获得远端发布授权前，GitLab/GitHub 不属于本文自动执行范围。

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

项目接入与模板生成边界：

- 新项目接入默认走“先校验已有 Agent TOML，再安装 GUI”的路径；安装器不得在默认模式下自动生成 `.codex/agents/*.toml`；
- 后续如增加模板生成，必须是显式命令，例如 `scaffold-project-moe-agent --target-project <project> --agent-name <agent> --state-namespace <namespace> --dry-run --json`，且默认 dry run；
- 模板生成只能创建骨架 TOML、空的项目私有提示源占位说明和操作者文档，不得生成长篇 `developer_instructions` 伪内容，不得复制其他项目 `MOE.md`；
- `agent_name` 必须与 TOML 顶层 `name`、安装配置、manifest 和 state namespace 绑定校验；名称冲突或 namespace 已被其他 agent 使用时 fail closed；
- `state_namespace` 必须是项目内唯一、可作为目录名的稳定标识；不得包含路径分隔符、空白控制字符或 shell 特殊语义；
- 接入检查器必须验证必填顶层字段、推荐扩展区、私有提示源路径、dispatch 策略、scope、state 路径和 schema 版本；失败返回稳定 token 与修复建议；
- 项目私有 `MOE.md` 可以由目标项目自行维护，但 scaffold/install/update 都不得读取其全文来生成用户级配置或中央工具链缓存。

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
  "override_origin": "manual-session",
  "raw_session_id_sha256": "sha256",
  "worktree": "D:\\PythonProject_paper_suggest",
  "branch": "main",
  "first_seen_at": "2026-05-20T00:00:00+00:00",
  "last_seen_at": "2026-05-20T00:00:00+00:00",
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

session 生命周期与陈旧记录规则：

- `status --json` 或 `assert-on` 在能识别当前 session id 时，可以 best-effort 更新该 session 记录的 `last_seen_at`；该更新不得改变 `enabled`；
- 首次创建 session 记录时写入 `first_seen_at`，之后普通 on/off 不得覆盖它；
- `list-sessions --json` 必须派生 `lifecycle_status`，至少包含 `active`、`stale`、`invalid`、`orphan_candidate`；该字段仅用于展示和筛选，不直接改变有效状态；
- `stale` 表示 `last_seen_at` 超过配置阈值或无法确认会话仍在活动；第一版默认只标记，不自动删除、不自动关闭；
- `orphan_candidate` 表示记录关联的 worktree、branch 或 session source 已无法确认；它必须进入 GUI 的无效/需复核分组，不能被项目级 on/off 静默修复；
- 第一版不实现自动 pruning、归档、tombstone 或清理 session state；如后续需要，必须新增显式 `prune-sessions --dry-run` / `--apply` 之类命令、审计记录和回滚规则；
- generated 兼容 id 的记录必须在 GUI 中显示较低置信度，避免操作者误以为它是强隔离真实 session。

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

项目级传播与手动 session 覆盖规则：

- `project-on` / `project-off` 默认更新项目默认值，并只传播到 `override_origin = "project-propagated"` 或没有显式手动来源的有效 session 记录；
- `on --session-id <id>` / `off --session-id <id>` 写入 `override_origin = "manual-session"`，表示操作者显式设置过该 session；
- 项目级命令不得静默覆盖 `override_origin = "manual-session"` 的记录；如后续确实需要批量覆盖，必须新增显式参数，例如 `--include-manual-overrides`，并在 dry run 与 JSON 输出中列出将被覆盖的 session；
- 当 session 记录只是因为项目级传播而存在时，GUI 应显示“跟随项目默认值传播”，避免用户误认为它是手动例外；
- 如果项目默认值与手动 session 覆盖冲突，`effective_source = "session"`，并在 `status --json` / GUI 中显示冲突提示，但不自动修复；
- 清除手动覆盖不属于第一阶段必需命令；若后续增加 `clear-session-override`，必须回到继承项目默认值，而不是删除审计历史。

`list-sessions --json` 只返回控制所需的脱敏标识和元数据：session id、来源、enabled、validity、lifecycle status、status reason、branch、worktree、first seen、last seen、时间戳、reason 和 state path。它不得暴露 raw session id，不得包含私有提示词内容。

状态兼容与迁移：

- 现有 `thesis_moe_mode.py` 已写出的 session 记录即使还没有 `scope` 或 `state_namespace`，只要原有必填字段有效，也必须继续可读；
- 项目级命令重写有效旧 session 记录时，应补入 `scope = "session"` 与 `state_namespace = "thesis_moe"`；
- 项目级命令应保留已有 `created_at`，并更新 `updated_at` 与 `reason`；
- 无效或损坏的旧记录不得在普通 on/off 操作中自动修复；如确实需要修复，后续必须另行创建显式 repair 命令。

失败模式与退出码契约：

| 场景 | 退出码 | 稳定 token |
| --- | ---: | --- |
| 成功读取或写入 | 0 | `ok` |
| `assert-on` 发现有效状态为关闭 | 1 | `disabled` |
| 命令参数无效或不支持该命令 | 2 | `usage_error` |
| 损坏或不匹配状态阻止有效状态计算 | 3 | `state_corrupt`、`schema_version_mismatch`、`blocked:unsupported_schema_version`、`agent_name_mismatch`、`session_mismatch`、`worktree_mismatch`、`branch_mismatch` |
| 目标根目录、路径或命令调用不安全，或 ownership preflight 拒绝 | 4 | `blocked:unsafe_target_root`、`blocked:path_outside_project`、`blocked:path_traversal`、`blocked:unsafe_symlink_or_junction`、`blocked:command_invocation_unsafe`、`blocked:ownership_precheck_failed`、`blocked:dirty_unowned_files` |
| 缺少依赖、启动器配置无效或必需项目文件缺失 | 5 | `blocked:missing_agent_toml`、`blocked:missing_mode_cli`、`blocked:pyside6_unavailable`、`blocked:python_runtime_unavailable`、`blocked:launcher_config_invalid` |
| 并发写入锁不可获得或疑似过期锁需要人工确认 | 6 | `blocked:state_lock_timeout`、`blocked:stale_state_lock` |

CLI 和 GUI 输出应同时包含面向人的说明和稳定机器可读 token。GUI 代码应基于 token 分支，不依赖本地化自然语言。

CLI JSON 输出契约：

- 所有 `--json` 命令返回统一 envelope：`schema_version`、`command`、`ok`、`token`、`exit_code`、`message`、`project_root`、`agent_name`、`state_namespace`、`generated_at`、`warnings`、`errors`；
- `status --json` 额外返回：`effective_enabled`、`effective_source`（`session`、`project-default`、`fail-closed`）、`session_id`、`session_id_source`、`session_confidence`、`lifecycle_status`、`project_default_enabled`、`session_override_enabled`、`state_path`；
- `project-status --json` 额外返回：`project_default`、`registered_session_count`、`valid_session_count`、`invalid_session_count`、`stale_session_count`、`orphan_candidate_count`、`state_paths`、`cli_contract`；
- `list-sessions --json` 返回：`sessions` 数组、`counts`、`redaction_policy` 和 `source_paths`；每行 session 只允许包含脱敏 session id、source、confidence、enabled、effective_enabled、validity、lifecycle_status、status reason、branch、worktree、first seen、last seen、updated at、reason 摘要和 state path；
- 写入命令的 JSON 输出必须包含 `before`、`after`、`changed_scope`、`changed_paths`、`skipped_invalid_records`、`lock_status`、`audit_path`、`atomic_write` 和 `no_op`；
- 失败 JSON 必须包含稳定 `token`、`remediation_hint` 和可选的脱敏 `details`；不得把私有提示词、raw session id、论文正文、原始环境变量值或完整 stderr 直接塞进 JSON。

兼容要求：

- 现有 `status --json` 保持机器可读；
- 现有 session state 文件保持可读取；
- 损坏、session 不匹配或越界状态必须 fail closed。

会话自动生效与启动钩子规则：

- `project-on` / `project-off` 只负责写入项目与 session 状态；它们本身不能让已经打开的 Codex 会话跨进程即时改变模型上下文，必须配套目标项目的启动/恢复检查面；
- `paper_suggest` 第一阶段必须在目标项目的 `AGENTS.md`、等价 startup summary 或 launcher helper 中增加短规则：在首个实质任务、`resume` / `continue`、reload / restart、phase change 或用户显式询问 MOE 状态时，读取 `python .\tools\thesis_moe_mode.py status --json`，需要强制开启时再使用 `assert-on`；
- 新会话启动时先继承项目默认值；已有会话在下一次触发上述检查点时重新读取有效状态；不得宣称 `.cmd` 能即时注入已经打开会话的历史上下文；
- 当有效状态为 enabled 时，会话按 `.codex/agents/thesis-moe-mentor.toml` 与项目私有 `MOE.md` 的摘要化/引用规则启用严苛导师型审查；当状态为 disabled 或 fail-closed 时，不加载私有提示全文；
- 如果启动钩子缺失、CLI 缺失或返回 blocker token，会话必须报告 named blocker，例如 `blocked:missing_moe_activation_hook` 或 `blocked:missing_mode_cli`，而不是默默认为 MOE 已启用；
- GUI 显示的项目与 session 状态必须来自同一 `status` / `project-status` / `list-sessions` JSON 合约，不能维护第二套状态。

第一阶段实施顺序：

1. 扩展 `tools/thesis_moe_mode.py`，增加项目默认状态的读取和写入 helper；
2. 新增 `project-on`、`project-off`、`project-status` 命令；
3. 让 `status` 和 `assert-on` 按“session 覆盖、项目默认值、fail-closed 关闭”的顺序计算有效状态；
4. 更新 `thesis-moe-on.cmd` 与 `thesis-moe-off.cmd`，默认调用项目级命令；
5. 更新目标项目 `AGENTS.md`、startup summary 或 launcher helper，让新会话和已有会话在激活检查点重新读取 MOE 状态；
6. 更新使用说明和测试，覆盖项目默认值、已登记 session 传播、单 session 覆盖和会话自动生效链路。

第一阶段不得修改论文正文、私有提示词内容、浏览器自动化或文献检索行为。

第一阶段写入目标项目前的 preflight：

- 在 `D:\PythonProject_paper_suggest` 内运行 `git status --short --branch`，如果存在会被本次任务触碰的无关 dirty 或未跟踪文件，必须先停止；
- 如果目标项目提供 ownership precheck，先运行，例如 `python .\tools\check_session_ownership_claims.py --root . --precheck-task "thesis MOE project-default session toggle" --target-path tools/thesis_moe_mode.py --json`；
- 编辑前确认 `.codex/agents/thesis-moe-mentor.toml`、`tools/thesis_moe_mode.py`、`thesis-moe-on.cmd`、`thesis-moe-off.cmd` 和使用说明文件存在；
- 测试通过后，在目标项目内创建普通本地 Git commit；没有单独远端发布请求时，不推送或发布目标项目变更。

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
  project_moe_gui.install-manifest.json
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

第一版 GUI 交互与可访问性规则：

- 所有状态徽标必须同时使用文字和颜色表达，例如 `项目默认：开启`、`session 覆盖：关闭`、`无效记录`，不得只靠红/绿颜色；
- on/off 按钮必须明确 scope：`开启项目默认值`、`关闭项目默认值`、`开启选中 session`、`关闭选中 session`；
- 刷新只读取 `project-status --json` 和 `list-sessions --json`，不得触发写入、迁移或安装；
- 执行写入命令期间，同一 scope 的按钮禁用并显示 loading 状态；命令完成后重新读取状态，而不是相信本地 UI 预测值；
- 错误必须显示稳定 token、简短说明和建议动作；同时保留 stdout/stderr 摘要供复制，但不显示私有内容；
- session 表格必须支持空状态、无效记录状态和加载失败状态；空状态不得被误读为“MOE 已关闭”；
- 表格至少支持按更新时间排序和按有效性筛选；排序/筛选只作用于已返回的脱敏行，不重新扫描 `.omx/state`；
- 必须支持键盘操作：刷新、切换项目默认值、切换选中 session、复制错误摘要；默认焦点不得落在危险写入按钮上；
- 高对比或系统主题下仍能辨认状态、按钮禁用状态和错误横幅；
- 任何 GUI 本地化文本不得成为机器判断依据；代码分支只能依赖 CLI JSON 字段和 stable token。

安装后的 GUI 配置：

```json
{
  "schema_version": 1,
  "toolchain": "project_moe_gui",
  "toolchain_version": "0.1.0",
  "cli_contract": "project-moe-cli-v1",
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "mode_cli": "tools/thesis_moe_mode.py",
  "project_root_strategy": "launcher-parent-git-root",
  "pyside6_runtime": "project-or-shared-runtime",
  "python_runtime_strategy": "project-venv-then-shared-gui-runtime",
  "python_utf8": true
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

安装器和更新器应支持 `--dry-run --json`。dry run 只计算目标项目根、将写入或更新的文件、跳过的私有文件、需要的迁移动作和 rollback hint，不实际写入。真实写入必须在输出中明确标记 `mode = "apply"`；无变化时输出 `no_op = true`，不得为了制造提交而重写文件。

如果目标项目没有匹配的 `.codex/agents/<agent>.toml`，安装器必须失败；除非后续另行增加显式模板生成模式。

PySide6 runtime 可以来自有文档记录的共享 GUI runtime，也可以来自目标项目自己的虚拟环境。第一版实现必须在安装配置里记录使用哪种 runtime；如果 PySide6 不可用，必须给出可执行的错误提示。

### 8.1 版本、兼容与升级策略

`schema_version = 1` 是第一版可支持的目标项目配置与状态契约。`toolchain_version` 表示由本仓库维护的 GUI 工具链版本或发布标识，`cli_contract` 表示安装后的 GUI 期望目标项目本地 CLI 暴露的稳定命令契约。安装、更新和检查命令必须在 JSON 输出中报告至少以下字段：`installed_toolchain_version`、`target_toolchain_version`、`config_schema_version`、`cli_contract`、`migration_actions` 和 `rollback_hint`。

兼容策略：

- v1 reader 必须忽略未知的额外字段，避免后续小版本增加字段时导致旧工具直接失效；
- v1 writer 在重写配置或状态时，应在可行范围内保留未知字段，只更新自己拥有的字段；
- 遇到缺失、低于 1、非整数或高于当前支持范围且不兼容的 `schema_version` 时，必须 fail closed，并输出稳定 token `blocked:unsupported_schema_version`；
- 同一 `schema_version` 内的新增字段迁移必须幂等、可重复运行、仅作用于目标项目内文件；
- 迁移不得读取、复制或覆盖 `MOE.md`、`.codex/agents/*.toml`、私有提示词全文或已有 `.omx/state` 内容，除非后续另建显式 repair/change；
- 不自动降级。需要降级时，必须由用户显式要求，并通过目标项目 Git 历史、backup refs 或安装 receipt 指向的旧版本进行回滚；
- 如果中央工具链版本较新但目标项目 CLI 仍缺少 `project-moe-cli-v1` 必需命令，GUI 应报告 `blocked:missing_mode_cli` 或更具体的 CLI contract token，而不是直接扫描或修改状态文件。

升级验收要求：

- `check_project_moe_gui_install.py --json` 必须能区分 `up_to_date`、`upgrade_available`、`migration_required`、`blocked:unsupported_schema_version` 和 `blocked:missing_mode_cli`；
- `update_project_moe_gui.py` 在写入前必须输出将修改的安装产物列表，写入后输出更新 receipt；
- 更新 receipt 至少包含目标项目根、旧/新 `toolchain_version`、`schema_version`、变更文件、跳过的私有文件、执行时间和 rollback hint；
- 任何迁移失败不得被当作成功启用 MOE Agent 的证据。

### 8.2 Runtime 与 launcher 契约

GUI 源码由本仓库维护，但启动 runtime 必须在目标项目侧可解释、可诊断、可替换。第一版 launcher 不得依赖操作者当前 shell 的偶然 `PATH` 或全局 Python 包状态：

- `project-moe-gui.cmd` 应从安装配置解析目标项目根，并优先使用目标项目已记录的 Python runtime；没有项目 runtime 时才使用文档化的共享 GUI runtime；
- launcher 不得永久修改用户级 `PATH`、`PYTHONPATH`、pip 配置或系统环境变量；如需临时环境变量，只能作用于当前子进程；
- Windows 启动器必须启用 UTF-8 安全输出，例如设置当前子进程的 `PYTHONUTF8=1` 或等价方式，避免中文路径、中文状态 token 或日志乱码；
- GUI 子进程调用项目本地 CLI 时必须传入解析后的 `--project-root` 或等价上下文，不能依赖当前工作目录碰巧正确；
- 如果 Python runtime 不存在或不可执行，返回 `blocked:python_runtime_unavailable`；如果配置文件缺失关键字段或路径越界，返回 `blocked:launcher_config_invalid`；
- launcher 日志只记录解析步骤、runtime 路径类别、退出码、stdout/stderr 摘要和 stable token；不得记录私有提示词、raw session id、论文正文或原始环境变量值；
- `check_project_moe_gui_install.py --json` 必须验证 launcher、config、Python runtime、PySide6 可导入性和项目本地 CLI contract；失败时给出可执行修复建议。

### 8.3 安装产物清单与所有权边界

目标项目内必须有安装产物清单，用来区分“中央工具链可管理的安装产物”和“目标项目私有文件”。第一版推荐清单路径：

```text
<project>/tools/project_moe_gui/project_moe_gui.install-manifest.json
```

清单至少记录：

- `schema_version`、`toolchain`、`toolchain_version`、`source_repo`、`source_commit`；
- `target_project_root`、`agent_name`、`state_namespace`、`installed_at`、`updated_at`；
- `managed_files`：安装器拥有并可在更新时重写的文件，例如 launcher、GUI 包装文件和配置模板；
- `protected_project_files`：安装器必须视为只读的文件，例如 `MOE.md`、`.codex/agents/*.toml`、论文正文、私有提示源和 `.omx/state`；
- 每个 managed file 的相对路径、sha256、写入原因和上一版本 hash；
- `last_dry_run` 与 `last_apply_receipt` 的摘要或路径。

所有权规则：

- 更新器只能自动修改清单里的 `managed_files`；如果某个 managed file 在目标项目内被人工改动且 hash 不匹配，必须报告 `blocked:managed_file_modified` 或进入显式三方合并/repair 流程，不得直接覆盖；
- 清单缺失时，`check_project_moe_gui_install.py --json` 报告 `migration_required` 或 `blocked:launcher_config_invalid`，由显式 install/update 重新生成；GUI 启动不得隐式生成；
- 卸载、清理、删除清单、删除 launcher 或删除 audit/session state 不属于第一版自动行为；后续如需实现，必须另建显式 uninstall/cleanup 命令、dry run、验收和回滚规则；
- 清单不得复制项目私有提示词、raw session id、论文正文或审计日志内容。

## 9. 安全与回滚规则

实施和更新命令必须：

- 写入前打印解析出的目标项目根目录；
- 拒绝写入目标项目根目录以外的位置；
- 拒绝覆盖 `MOE.md`、`.codex/agents/*.toml` 或 `.omx/state`，除非后续另行创建显式 repair 命令；
- 在目标项目内形成可由 Git 审查的变更；
- 输出足够状态信息，让用户能看清变更的是项目默认值还是单 session 覆盖。
- 在输出中区分实现文件写入、状态文件写入、安装/更新写入和只读 status 命令，方便操作者审计实际变化。

如果更新中途失败，重复运行安装器或更新器必须是安全的。项目状态回滚依赖目标项目 Git 历史，以及 `.omx/state` 下的状态 JSON 文件。

### 9.1 状态写入原子性与并发控制

MOE 控制面可能被多个 Codex session、命令行 wrapper 和 GUI 同时调用。第一版必须用简单、可审计、跨进程有效的本地文件策略避免并发写坏状态：

- 每次写入项目默认值、session 覆盖或审计日志前，先获取 state namespace 级别的锁文件，例如 `.omx/state/<state_namespace>/.lock`；
- 锁文件内容只保存操作元数据：pid、command、normalized session id、target state path、created_at 和 lock timeout，不写私有提示词或 raw session id；
- 获取锁必须有短超时和重试退避；超时后返回 `blocked:state_lock_timeout`，不得继续写入；
- 检测到疑似过期锁时只报告 `blocked:stale_state_lock` 和 lock 文件路径，不自动删除，除非后续另行创建显式 repair/unlock 命令；
- JSON 状态写入必须采用临时文件 + flush/fsync + 原子 replace，同一目录内完成，避免半写文件；
- `list-sessions --json`、`status --json` 和 `project-status --json` 默认只读，不应持有写锁；如果发现正在写入，可短暂重试或报告状态正在变化；
- GUI 必须串行化本进程内按钮动作：一个 on/off 操作完成前禁用同一 scope 的重复按钮，避免本地 GUI 自己制造并发写；
- 并发冲突、锁超时或原子替换失败都不是“已启用/已关闭”的证据，必须在 CLI/GUI 和审计摘要中暴露稳定 token。

### 9.2 预览、应用与操作者确认边界

为了避免 GUI 或 wrapper 在错误项目中静默写入，第一版必须区分只读检查、dry run 预览和真实应用：

- `check_project_moe_gui_install.py` 永远只读；它可以报告 `up_to_date`、`upgrade_available` 或 blocker，但不得写入；
- install/update 命令的 `--dry-run --json` 输出必须列出 `planned_writes`、`planned_skips`、`planned_migrations`、`target_project_root`、`state_namespace`、`agent_name` 和 `rollback_hint`；
- install/update 的真实写入必须要求显式 apply 语义，例如命令名本身是 install/update 且输出 `mode = "apply"`，或后续实现增加 `--apply`；不得让 `check` 或 GUI 启动动作隐式安装；
- `project-on`、`project-off`、`on --session-id`、`off --session-id` 可以作为明确写入命令直接执行，但必须在 JSON 中报告 before/after effective state、changed scope 和 `no_op`；
- GUI 首次连接某个目标项目时必须显示目标项目根、agent name、state namespace 和当前分支；用户点击 on/off 前，按钮标签必须明确是项目默认值还是单 session；
- GUI 不得在窗口打开、刷新 session 表格或读取状态时自动执行安装、更新、迁移、on/off 或 repair；
- no-op 操作应返回成功 token `ok` 与 `no_op = true`，并写入审计摘要或 stdout 摘要，方便确认没有真实状态变化；
- 任何需要删除、清理、unlock、repair、retention pruning 或卸载 GUI 产物的行为都不属于第一版隐式动作，必须后续另建显式命令和验收规则。

### 9.3 路径解析与命令调用安全边界

目标项目路径、安装产物路径和 GUI 调用 CLI 的命令行都必须作为安全边界处理。第一版不得依赖字符串前缀或 shell 拼接来判断安全性：

- `--target-project`、`--project-root`、`mode_cli`、manifest 里的 managed/protected 路径都必须先做规范化和真实路径解析；解析后的路径必须仍位于目标项目根目录内；
- 拒绝 `..` 路径穿越、绝对路径注入、UNC 路径越界、Windows drive 切换、符号链接或 junction 指向项目外部的 managed file；
- 对于允许存在的项目内符号链接或 junction，必须在检查输出中显式标记 `link_target_status`；如果目标不可验证则 fail closed；
- GUI 调用项目本地 CLI 时必须使用 argv/list 形式的子进程调用，不得把用户输入、session id、路径或 reason 拼接进 shell 字符串；
- 命令日志可以显示脱敏后的 argv 摘要，但不得记录 raw session id、原始 reason 中的私有内容或未经规范化的用户输入；
- `reason`、session id 和 agent name 必须作为数据字段校验长度、字符集和 JSON 序列化安全性；不得把它们当作路径片段或 shell 片段；
- 任何路径解析越界、路径穿越、外部 link 目标或不安全命令调用都必须返回稳定 blocker token，不得降级为普通 `usage_error`。

## 10. 审计日志、隐私与保留边界

MOE 控制工具对状态变更动作应写入轻量本地审计记录：

```text
.omx/state/<state_namespace>/audit/<yyyy-mm-dd>.jsonl
```

每条审计记录只包含操作元数据：timestamp、command、stable token、exit code、project root、branch、适用时的 normalized session id、state path、changed scope 和 reason。审计记录不得包含 `MOE.md` 内容、`developer_instructions`、raw session id、原始环境变量值、论文正文、paper 内容或浏览器/文献检索载荷。

隐私与保留规则：

- 只保留 `raw_session_id_sha256`，不保留 raw session id；
- 项目私有提示词和文档必须留在目标项目内；
- 安装或更新 GUI 时不得把审计日志复制到 `D:\PythonProject_langgraph`；
- 状态变更的审计写入应是 best-effort：如果审计日志写入失败，必须报告错误 token，不得静默改状态；
- retention pruning 是后续显式功能，第一版不得删除 audit 或 session state。

## 11. 实施切片与测试矩阵

第一阶段目标项目推荐文件所有权：

- `tools/thesis_moe_mode.py`：状态模型、命令表面、有效状态和列表输出；
- `thesis-moe-on.cmd` 与 `thesis-moe-off.cmd`：项目级默认值包装入口；
- `docs_bilingual/operations/thesis_moe_mode_usage.zh-CN.md`：操作者用法和失败模式；
- `AGENTS.md` 或目标项目等价 startup summary / launcher helper：会话激活检查点与 MOE 状态读取规则；
- `tests/test_thesis_moe_mode.py` 或目标项目既有测试位置：覆盖项目默认值、session 覆盖、列表输出、无效记录、旧记录兼容和会话激活链路。

第二阶段本仓库推荐文件所有权：

- `tools/project_moe_gui_toolchain/src/project_moe_gui/`：GUI 实现；
- `tools/project_moe_gui_toolchain/install_project_moe_gui.py`：目标项目安装；
- `tools/project_moe_gui_toolchain/update_project_moe_gui.py`：幂等更新；
- `tools/project_moe_gui_toolchain/check_project_moe_gui_install.py`：安装产物 checker；
- `tools/project_moe_gui_toolchain/check_project_moe_phase1_readiness.py`：目标项目写入前只读 readiness checker；
- `docs_bilingual/operations/project_moe_gui_usage.zh-CN.md`：操作者文档。

### 11.1 实施进度勾选清单

本清单按具体事项排序，事项不等于实施切片。阶段级勾选只表示该阶段的完成定义已经整体满足；事项级勾选只表示该事项已有本地仓库证据或已由本文方案明确固化。不要把某个阶段下的未勾选事项理解为“本方案未完善”，它只表示该事项尚缺目标项目证据、GUI 证据或跨项目验收证据。

阶段级汇总：

| 阶段 | 阶段勾选 | 当前状态 | 不易误解的说明 |
| --- | --- | --- | --- |
| Phase 1：目标项目命令行状态模型 | [ ] | 待目标项目实施/验证 | 未勾选是因为 `D:\PythonProject_paper_suggest` 侧 CLI、wrapper、startup hook 和测试证据尚未由本仓库确认；本仓库已补充读取契约、写入契约、原子/锁状态、状态行为 fixture gate 和只读 readiness checker，但真实目标项目仍未完成。 |
| Phase 2A：本仓库中央安装器、checker 与 updater | [x] | 已完成并合入本地 `main` | 已有本仓库本地提交 `3e4e819c73c78472d948e68d5352085dcac6551d` 与 local gate 证据。 |
| Phase 2B：PySide6 GUI 本体 | [x] | fixture-safe GUI shell 已完成并合入本地 `main` | 覆盖 import-safe shell、view model、写入后重读、同 scope pending 禁用、键盘/高对比语义和显式可见窗口边界；真实可见窗口/QTest 证据仍属于后续操作证据，不阻塞本仓库 fixture-safe 完成定义。 |
| Phase 2C：跨项目复用与目标安装 | [x] | 双 fixture contract 已闭环 | 两个隔离 fixture 项目已经通过相同 install/check/update/status contract、项目 A/B 隔离，以及 update 保留私有 Agent TOML / `MOE.md` / state；真实目标项目安装仍需要目标项目 Phase 1 完成与单独授权。 |

#### 文档与架构契约

- [x] 定义项目级 MOE Agent GUI 工具链目标和非目标。
- [x] 定义与 PySide6 通用 GUI 能力方案的边界。
- [x] 定义项目级 MOE Agent TOML 必填字段。
- [x] 定义推荐扩展区：`project`、`moe`、`dispatch`、`extensions`。
- [x] 定义新项目接入时默认校验已有 Agent TOML，而不是默认生成私有 Agent。
- [x] 定义模板生成必须显式 dry run 且不得复制其他项目 `MOE.md`。
- [x] 定义禁止 `full-history fork + specified custom role` 的派发边界。
- [x] 定义 main-session takeover、brief-based fresh dispatch 与 durable brief 三种兼容路径。

#### Phase 1：目标项目命令行状态模型

- [ ] 在 `D:\PythonProject_paper_suggest` 做只读 dirty/ownership preflight。
- [x] 在本仓库提供 `check_project_moe_phase1_readiness.py` 只读 readiness checker，用 fixture 覆盖 clean target 通过、dirty target 与缺失 wrapper fail closed。
- [ ] 确认目标项目已有 `.codex/agents/<project-moe-agent>.toml` 且字段符合本方案。
- [ ] 确认目标项目私有提示源 `MOE.md` 只在目标项目内维护。
- [ ] 实现或核验 `tools/thesis_moe_mode.py project-on`。
- [ ] 实现或核验 `tools/thesis_moe_mode.py project-off`。
- [ ] 实现或核验 `tools/thesis_moe_mode.py project-status --json`。
- [x] 在本仓库安装器/checker fixture 中校验 `project-status --json` 的统一 envelope、CLI contract、默认值字段和 session 计数字段。
- [ ] 实现或核验 `tools/thesis_moe_mode.py list-sessions --json`。
- [x] 在本仓库安装器/checker fixture 中校验 `list-sessions --json` 的 sessions 数组、counts 对象、行级 session 标识、enabled/effective 字段和 stable token。
- [ ] 实现或核验 `tools/thesis_moe_mode.py on/off --session-id <id>`。
- [ ] 实现或核验 `tools/thesis_moe_mode.py status --json` 与 `assert-on`。
- [x] 在本仓库安装器/checker fixture 中校验 `status --json` 的 boolean `effective_enabled`、受支持 `effective_source` 和 raw/private 字段 fail-closed。
- [x] 在本仓库状态行为 fixture 中覆盖项目默认值、session override、无效记录、旧记录兼容和 no-op 测试；这不代表真实目标项目测试已完成。
- [x] 在本仓库测试中覆盖目标 CLI 读取契约不完整时安装前 fail closed：缺失 `effective_source`、缺失 session counts、暴露 raw/private 字段。
- [x] 在本仓库 GUI shell fixture 中覆盖目标 CLI 写入契约不完整时 fail closed：缺失 `changed_paths`、写入 scope 不匹配、暴露 raw/private 字段。
- [x] 在本仓库 GUI shell fixture 中覆盖 state lock、atomic write、lock timeout 与 stale lock blocker fail-closed 测试：缺失 `atomic_write`、`atomic_write=false`、`lock_timeout` / stale lock blocker 均不得被 GUI 当成有效写入结果。
- [ ] 接入 `thesis-moe-on.cmd` 与 `thesis-moe-off.cmd`。
- [ ] 在目标项目 startup / launcher / AGENTS 等入口加入 MOE 状态读取检查点。
- [ ] 编写或更新目标项目操作者文档。
- [ ] 目标项目本地 gate / smoke test 通过并留下证据。

#### Phase 2A：本仓库中央安装器、checker 与 updater

- [x] 建立 `tools/project_moe_gui_toolchain/` 工具链目录。
- [x] 建立 `tools/project_moe_gui_toolchain/src/project_moe_gui/` 包边界。
- [x] 实现 `install_project_moe_gui.py`。
- [x] 实现 `check_project_moe_gui_install.py`。
- [x] 实现 `update_project_moe_gui.py`。
- [x] 实现安装 manifest 与 managed/protected 文件边界。
- [x] 实现缺少 Agent TOML 时 fail closed。
- [x] 实现 dry run 不写目标项目文件。
- [x] 实现 apply 写入目标项目安装产物与 manifest。
- [x] 实现 hash mismatch fail closed。
- [x] 实现 path traversal / unsafe target blocker。
- [x] 编写 `docs_bilingual/operations/project_moe_gui_usage.zh-CN.md`。
- [x] 编写 `test/project_moe_gui_toolchain.test.py`。
- [x] 将测试注册到 `tools/ci/ci_test_manifest.json`。
- [x] Phase 2A 本地 gate 通过并合入本仓库本地 `main`。

#### Phase 2B：PySide6 GUI 本体

- [x] 定义 import-safe GUI shell 入口、窗口结构描述和受控可见启动边界。
- [x] 实现目标项目配置读取：`project_moe_gui.config.json`。
- [x] 实现顶部横幅 view model：项目根、agent name、state namespace、当前分支。
- [x] 实现项目默认状态卡片 view model。
- [x] 实现 session 表格 view model 和空状态 / 无效状态 / 加载失败状态。
- [x] 实现刷新动作计划，且刷新只读。
- [x] 实现项目默认值 on/off 动作计划，scope 文案明确。
- [x] 实现选中 session on/off 动作计划，scope 文案明确。
- [x] GUI 调 CLI 必须使用 argv/list，不使用 shell 字符串拼接。
- [x] GUI shell 不直接写 `.omx/state` JSON。
- [x] GUI shell view model 显示 stable token、简短说明和脱敏 stdout/stderr 摘要。
- [x] 写入命令执行期间禁用同一 scope 按钮并重新读取状态。
- [x] 支持键盘操作和高对比/系统主题可辨认状态。
- [x] 补充 import-only fixture GUI 测试与可见窗口显式启动边界；headless Qt / QTest / 手动视觉验证仍作为后续真实 GUI 证据。
- [x] 将 GUI shell fixture 测试纳入本仓库 local gate 已注册的 `project_moe_gui_toolchain.test.py`。

#### Phase 2C：跨项目复用与目标安装

- [x] 在至少一个 fixture 项目验证完整 install/check/update/status 流程。
- [x] 在第二个 fixture 或真实项目验证相同 contract。
- [x] 确认 GUI 安装到项目 A 只控制项目 A。
- [x] 确认 GUI 安装到项目 B 只控制项目 B。
- [x] 确认 update 不覆盖目标项目私有 Agent TOML、`MOE.md` 或 state。
- [x] 明确目标项目真实安装前的 dirty/ownership preflight。
- [x] 明确真实目标项目远端发布仍由目标项目自己的发布流程控制。
- [x] 记录跨项目复用验收证据并决定是否把本文 `status` 从 `draft` 提升为更高状态：由于真实目标项目 Phase 1 CLI 尚未完成，本文暂时继续保持 `draft`。

最小测试矩阵：

| 范围 | 必需证据 |
| --- | --- |
| 项目默认值 | `project-on`、`project-off`、`project-status --json` 和新 session 继承。 |
| session 覆盖 | 显式 `--session-id` 的 on/off 优先于项目默认值。 |
| session 列表 | `list-sessions --json` 返回脱敏、有效、GUI 可用的行。 |
| 无效状态 | 损坏或不匹配状态会被报告，且不会自动修复。 |
| GUI 安装 | 缺少 Agent TOML 时安装失败，且只写目标项目内文件。 |
| GUI 操作 | GUI 操作结果与 CLI `status --json` 和 `project-status --json` 一致。 |
| 并发写入 | 两个命令同时写同一 namespace 时，一个成功，另一个等待后成功或返回稳定 lock token；不会产生半写 JSON。 |
| dry run / no-op | install/update dry run 不写文件；重复启用或关闭输出 `no_op = true`，且不制造无意义文件差异。 |
| Runtime/launcher | launcher 不依赖偶然 `PATH`，UTF-8 输出正常；缺少 Python runtime、PySide6 或坏配置时返回稳定 blocker token。 |
| 安装产物清单 | 更新只触碰清单声明的 managed files；私有文件保持只读；hash 不匹配时 fail closed。 |
| 路径与命令安全 | 路径穿越、项目外 link 目标和 shell 拼接式命令调用被拒绝；GUI 调 CLI 使用 argv/list。 |
| GUI 可用性 | 状态徽标有文字语义，错误横幅显示 stable token，刷新只读，按钮 scope 明确，键盘可操作。 |
| session 生命周期 | `last_seen_at` 只更新活动观测，不改变 enabled；stale/orphan 只标记不清理；generated id 显示低置信度。 |
| 会话自动生效 | 新会话继承项目默认值；已有会话在 resume/continue/reload/phase change 等检查点重新读取 `status --json`；缺失 hook 或 CLI 时显示 blocker。 |
| JSON 输出契约 | `status`、`project-status`、`list-sessions` 和写入命令都返回统一 envelope、稳定 token、脱敏字段和 GUI 所需计数。 |
| 新项目接入 | 默认校验已有 Agent TOML；模板生成必须显式 dry run；不得复制其他项目 `MOE.md` 或生成伪私有提示。 |
| 覆盖冲突 | 项目级传播不覆盖手动 session override；冲突时以 session 为准并显式显示 effective source。 |

测试执行与 CI 注册规则：

- 本仓库工具链测试必须使用临时目录或 fixture 项目模拟目标项目结构，不得在普通单元测试中直接写 `D:\PythonProject_paper_suggest`；
- 目标项目真实冒烟测试必须是显式手动或集成测试步骤，且先运行目标项目 dirty/ownership preflight；
- CLI JSON 契约必须有 contract fixture，覆盖成功、失败、no-op、lock timeout、invalid state、stale/orphan 和 manual override conflict；
- 安装/update/check 测试必须验证 dry run 不写文件、apply 写 manifest、hash mismatch fail closed、路径穿越 fail closed；
- PySide6 GUI 测试优先使用 headless Qt / QTest / pytest-qt 等可自动化方式；如果当前环境没有 GUI runtime，则保留 CLI/installer 测试通过，并把 GUI 视觉验证列为手动证据；
- 截图或视觉快照只能作为辅助证据，不得替代 CLI JSON contract 和状态文件断言；
- 新增测试、checker 或工具入口必须注册到本仓库 `tools/ci/ci_test_manifest.json` 或共享 local gate 调用链，避免只在本地手跑；
- 目标项目侧测试应在目标项目自身提交中注册到该项目测试入口；本仓库不得假设其他项目 CI 自动覆盖这些脚本。

实施阶段门与回滚点：

| 阶段 | go/no-go 条件 | 回滚点 |
| --- | --- | --- |
| Phase 0：只读盘点 | 目标项目 dirty/ownership preflight 通过，已有 Agent TOML、CLI、wrapper、文档路径确认。 | 不写文件；无需回滚。 |
| Phase 1A：CLI 状态模型 | fixture 测试覆盖 JSON envelope、project default、session override、lock、invalid state；目标项目本地测试通过。 | 目标项目 Git commit 前可直接丢弃工作区；commit 后用目标项目 Git 回退。 |
| Phase 1B：`paper_suggest` wrapper 接入 | `thesis-moe-on/off.cmd` 调用项目级命令；真实项目冒烟测试通过；不推送远端。 | 回退目标项目 wrapper 与 CLI commit；保留审计日志作为本地事实。 |
| Phase 2A：本仓库安装器/checker | 临时 fixture 项目验证 dry run/apply/manifest/hash/path blocker；local gate 注册通过。 | 回退本仓库 feature commit；目标 fixture 可删除。 |
| Phase 2B：PySide6 GUI | headless GUI 自动化或手动视觉证据满足可用性规则；GUI 不直接写 JSON。 | 删除或回退目标项目 managed install artifacts；不得删除 `.omx/state`。 |
| Phase 2C：跨项目复用 | 至少两个不同 fixture 或真实项目通过相同 contract；无跨项目状态泄漏。 | 回退安装产物；保留项目私有 Agent TOML 和私有提示源。 |

每个阶段的完成定义：

- 对应阶段的 contract、测试、文档和操作者命令已更新；
- 本阶段引入的新 checker/test 已注册到本仓库或目标项目的测试入口；
- 工作区干净，提交信息说明阶段和回滚方式；
- 未获得远端发布指令时，不推送 GitLab/GitHub，也不修改目标项目远端。

## 12. 校验与验收

本文档级验收：

- 英文与中文方案文件成对存在；
- 方案明确区分 MOE GUI 工具链和通用 GUI 工具；
- 方案定义项目默认值 + session override 行为；
- 方案禁止项目级 MOE Agent 使用 `full-history fork + specified custom role`；
- 方案定义状态写入的锁、原子写入、并发失败 token 和 GUI 串行化边界；
- 方案定义 check、dry run、apply、no-op 与 GUI 操作者确认边界；
- 方案定义 runtime/launcher 解析、UTF-8 输出、环境变量边界和缺失依赖 blocker；
- 方案定义安装产物清单、managed/protected 文件所有权和卸载/清理非目标边界；
- 方案定义路径规范化、符号链接/junction、路径穿越和命令调用安全边界；
- 方案定义 GUI 状态徽标、错误横幅、刷新语义、按钮 scope、空状态和键盘可访问性；
- 方案定义 session 生命周期、last seen、stale/orphan 标记和 pruning 非目标边界；
- 方案定义新会话与已有会话在启动/恢复/继续/阶段变化检查点读取 MOE 状态的自动生效链路；
- 方案定义 CLI JSON envelope、状态字段、计数字段、写入结果字段和失败脱敏字段；
- 方案定义新项目接入、scaffold dry run、Agent TOML/namespace 校验和私有提示源边界；
- 方案定义项目级传播、手动 session override、冲突展示和清除覆盖非目标边界；
- 方案定义测试 fixture、contract 测试、GUI 自动化/手动证据边界和 CI 注册规则；
- 方案定义 Phase 0/1/2 阶段门、go/no-go 条件、完成定义和回滚点。

第一阶段验收：

- `thesis-moe-on.cmd` 能开启项目默认值和已登记 session；
- `thesis-moe-off.cmd` 能关闭项目默认值和已登记 session；
- 新 session 继承项目默认值；
- 已打开 session 在 resume/continue/reload/phase change 等激活检查点重新读取 MOE 状态；
- 显式 `--session-id` 覆盖有效；
- `assert-on` 遵循有效状态规则。

第二阶段验收：

- GUI 安装到 `paper_suggest` 后只控制 `paper_suggest`；
- GUI 安装到第二个项目后只控制第二个项目；
- GUI 更新不覆盖目标项目私有 Agent TOML、`MOE.md` 或 state；
- GUI 操作结果与 CLI status 一致。

## 13. 下一步实施边界

当前后续实施应按“目标项目 CLI 先闭环、GUI 先 fixture 化、真实项目安装后置”的顺序推进：

1. 若要控制 `D:\PythonProject_paper_suggest` 真实会话，必须先在目标项目完成 Phase 1：CLI 状态模型、`list-sessions --json`、`status --json`、`assert-on`、`thesis-moe-on/off.cmd` 和目标项目启动检查点。
2. 若当前没有目标项目写入授权，本仓库可以继续做只读 readiness checker 与 fixture/mock 目标项目验证，不得直接写 `paper_suggest` 真实 `.omx/state` 或 wrapper。
3. Phase 2B GUI 本体只能通过目标项目 CLI 改状态，不得直接编辑 JSON；若目标 CLI 缺失，GUI 必须显示 blocker，而不是降级扫描或写状态文件。
4. Phase 2C 已在本仓库 fixture 层闭环：两个隔离 fixture 已通过相同 contract；本仓库又补充 Phase 1 读取契约 fixture gate、GUI 写入命令输出契约 fixture gate、写入命令原子写入/锁状态 fixture gate、项目默认值/session override/无效记录/legacy/no-op 状态行为 fixture gate，以及只读 readiness checker，真实项目安装仍取决于后续目标项目授权和 Phase 1 就绪性。
5. 本文暂不从 `draft` 提升：Phase 2B、fixture 级 Phase 2C、本仓库 Phase 1 读取契约 gate、GUI 写入命令输出契约 gate、写入命令 atomic/lock gate、状态行为 gate 与只读 readiness checker 已有本地证据，但真实目标项目 Phase 1 CLI / wrapper / startup checkpoint 仍未完成。

阶段门规则：

- Phase 1 只有在命令行测试证明项目默认值、已登记 session 传播、session 覆盖、无效记录跳过和旧记录可读后才算完成。
- Phase 2A 已在本仓库本地 `main` 完成；但它只覆盖中央 installer/checker/updater，不解除 Phase 1 对真实 GUI 的前置要求。
- Phase 2B 可以在本仓库 fixture 模式下启动；真实目标项目 GUI 安装仍要求 Phase 1 CLI contract 已就绪。
- 任何新增到本仓库的 GUI 源码、checker 或测试，都应作为单独本地变更实施并走本仓库 local gate。
- 远端发布不属于本文自动授权范围，必须继续遵守本仓库发布流程。
