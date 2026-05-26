---
doc_id: project_moe_agent_gui_toolchain_plan
lang: zh-CN
status: draft
plan_readiness: structure-aligned-ready-for-implementation
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md
created_at: 2026-05-20
updated_at: 2026-05-26
last_reviewed_at: 2026-05-26
scope: project_moe_agent_gui_only
implementation_lane: ready_bootstrap_repair_lanes
related_docs:
  - docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.zh-CN.md
  - docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md
---

# 项目级 MOE Agent GUI 工具链实施方案（新版结构，待继续实现）

> **For agentic workers:** REQUIRED SUB-SKILL：优先使用 `superpowers:executing-plans` 或等价的本地计划执行流程；涉及 OpenSpec/Comet 时先确认 active change、`.comet.yaml` 和 archive deferral。所有实现步骤用 checkbox 追踪；每个任务完成后先运行该任务列出的局部验证，再进入下一项。

**Goal:** 为每个本地项目提供可复用的项目级 MOE Agent 开关、会话状态和独立 PySide6 GUI 控制面；GUI 源码由 `D:\PythonProject_langgraph` 统一维护，但安装到哪个目标项目，就只读取/控制哪个目标项目的 MOE 状态。

**Architecture:** 本仓库维护 `project_moe_gui` 工具链、安装器、readiness checker 和模板；目标项目保留自己的 `.codex/agents/*.toml`、私有 `MOE.md`、`.omx/state/<namespace>/` 和本地 CLI。GUI 不直接编辑状态 JSON，而是通过目标项目本地 CLI 的 JSON contract 做只读刷新和受控写入。

**Tech Stack:** Codex repo-local tools、OpenSpec/Comet trace、Python CLI/checker、PySide6 shared runtime、Windows `.cmd` launcher、目标项目 `.codex/agents`、repo-local `.omx/state`、JSON contract、readiness gates、local-first Git flow。

---

## 0. 本次复核结论

本文已从旧版“累积型状态说明”改为新版“可执行实施方案”结构，对齐 `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` 的组织方式，但不复用 Pi sidecar 的运行时边界。

完整性结论：

| 检查项 | 结论 | 本方案落点 |
| --- | --- | --- |
| 命名与职责边界 | 已补齐 | 第 1、2、4 节 |
| GUI 与目标项目隔离 | 已补齐 | 第 3、5、6、9 节 |
| Phase 1 CLI / readiness contract | 已补齐 | 第 8、10、12 节 |
| Phase 2 PySide6 GUI contract | 已补齐 | 第 9、13 节 |
| Ready / Bootstrap / Repair lane | 已补齐 | 第 12 节 |
| 安全、隐私、回滚、卸载 | 已补齐 | 第 11、14 节 |
| 实施任务粒度 | 已重排 | 第 13 节 |
| 验证与验收 | 已重排 | 第 14、17 节 |

状态说明：

- `status: draft` 表示本文仍是实施方案，不是全局 active 治理政策，也不声称所有运行时能力已完成。
- `plan_readiness: structure-aligned-ready-for-implementation` 表示结构已对齐新版方案，可继续作为后续实现入口。
- 当前已知真实项目证据：`D:\PythonProject_paper_suggest` 具备 Phase 1 surface 候选，但 2026-05-24 的 static-only readiness 结果仍是 `blocked / repair-lane / control_mode_allowed=false`；不能把它视为 GUI 可直接控制的 ready 项目。
- 本次 Comet trace 位于 `openspec/changes/restructure-project-moe-gui-plan-modern/`。当前 Windows shell 缺少可用 `bash`，所以不得声称 `comet-state.sh` / `comet-guard.sh` 已成功执行；用 OpenSpec artifacts 与仓库 gate 作为可追溯 fallback。

## 1. 关系模型与命名边界

| 名称 | 角色 | Source of truth | 边界 |
| --- | --- | --- | --- |
| Project MOE Agent | 目标项目自己的专家型 Agent | `<project>/.codex/agents/*.toml` | 不安装到用户级 agent 目录作为默认共享 Agent。 |
| 私有提示源 | 项目自己的私有约束、导师要求或领域规则 | `<project>/MOE.md` 或项目内等价文件 | GUI / 安装器只校验路径和存在性，不复制全文。 |
| Phase 1 CLI | 目标项目的 MOE 状态读写入口 | `<project>/tools/<mode>_moe_mode.py` | GUI 必须通过它读写状态，不直接改 JSON。 |
| Phase 2 GUI | 本仓库维护的 PySide6 控制面 | `tools/project_moe_gui_toolchain/` | 安装后只控制被安装的目标项目。 |
| readiness checker | 安装/控制前的只读 gate | 本仓库工具链 | 可输出 go/no-go，不授权写目标项目。 |
| `.omx/state/<namespace>/` | 目标项目 MOE 状态 | 目标项目 repo-local state | 不跨项目扫描，不写其他项目。 |

命名默认：

- 工具链命名空间：`project_moe_gui`。
- 默认状态命名空间示例：`thesis_moe`。
- 目标项目 launcher 示例：`project-moe-gui.cmd`。
- 目标项目 CLI 示例：`tools/thesis_moe_mode.py`。

## 2. 目标与非目标

目标：

1. 为目标项目提供项目级 MOE 默认开关、单 session override、状态读取和 fail-closed 判定。
2. 为 GUI 提供统一 JSON contract，使 PySide6 控制面可以显示项目默认状态、session 列表、readiness blocker 和写入结果。
3. 让没有 Phase 1 的项目走 Bootstrap Lane，只输出缺口清单和脚手架计划，不直接控制。
4. 让已有 Phase 1 但不完整的项目走 Repair Lane，明确修复项后再允许 GUI 控制。
5. 让已满足所有 readiness gate 的项目进入 Ready Lane，允许安装和使用 GUI。

非目标：

- 不用 GUI 绕过目标项目 Phase 1 readiness gate。
- 不复制目标项目私有 `MOE.md` 全文。
- 不把项目专属 MOE Agent 默认安装到 `C:\Users\lenovo\.codex\agents`。
- 不做跨项目总控台或跨项目默认扫描。
- 不让 GUI 直接编辑 `.omx/state` JSON。
- 不把 workflow skills、plugin profiles 或 GUI profile loading 当成 native expert evidence。
- 不在未授权情况下推送 GitLab/GitHub 或写入目标项目远端。

## 3. 运行时架构

```text
Operator / Codex session
  -> target project startup/readiness check
  -> target project Phase 1 CLI JSON contract
  -> Project MOE GUI launcher installed in that target project
  -> PySide6 GUI shell from this repository's toolchain
  -> controlled project-local .omx/state/<namespace>/ JSON files
```

核心规则：

- GUI 启动先定位目标项目根目录，再运行 readiness checker。
- readiness checker 只读；它可以执行安全的 JSON 读取命令，但不得修改目标项目。
- 写入命令只允许通过目标项目 Phase 1 CLI：`project-on`、`project-off`、`on --session-id`、`off --session-id`。
- 写入后 GUI 必须重新读取状态，不信任本地 UI 预测值。
- 如果目标项目 dirty、CLI contract 不完整、wrapper 不安全、startup hook 缺失或私有提示源越界，则 fail closed。

## 4. Codex / GUI / 目标项目使用方式

Codex 操作意图：

```text
检查这个项目是否可以启用 Project MOE GUI
为这个项目生成 Project MOE Bootstrap Lane 缺口清单
打开当前项目的 MOE GUI
将当前项目 MOE 默认开启
关闭选中的 session MOE override
```

目标项目 CLI 表面：

```powershell
python .\tools\thesis_moe_mode.py project-on --json
python .\tools\thesis_moe_mode.py project-off --json
python .\tools\thesis_moe_mode.py project-status --json
python .\tools\thesis_moe_mode.py list-sessions --json
python .\tools\thesis_moe_mode.py on --session-id <id> --json
python .\tools\thesis_moe_mode.py off --session-id <id> --json
python .\tools\thesis_moe_mode.py status --json
python .\tools\thesis_moe_mode.py assert-on --json
```

GUI 使用方式：

```powershell
<project>\project-moe-gui.cmd
python <project>\tools\project_moe_gui\launcher.py --project-root <project>
```

GUI 必须显示：项目根、agent name、state namespace、当前分支、readiness lane、项目默认状态、session 列表、最近写入摘要、错误 token 和建议动作。

## 5. Repo-local source of truth

本仓库维护：

```text
tools/project_moe_gui_toolchain/
  src/project_moe_gui/
  install_project_moe_gui.py
  update_project_moe_gui.py
  check_project_moe_gui_install.py
  check_project_moe_phase1_readiness.py
  scaffold_project_moe_phase1.py
  templates/
```

配套治理与验证文件：

```text
docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md
openspec/changes/<project-moe-change>/
tests / fixtures for readiness, installer, launcher, GUI shell, uninstall planning
```

职责分离：

- `install_project_moe_gui.py`：复制/生成目标项目 GUI managed artifacts，并写 install manifest。
- `update_project_moe_gui.py`：读取 manifest 后受控更新 managed artifacts。
- `check_project_moe_gui_install.py`：验证目标项目安装状态和 hash。
- `check_project_moe_phase1_readiness.py`：只读检查目标项目 Phase 1 是否达到 GUI 控制前提。
- `scaffold_project_moe_phase1.py`：Bootstrap Lane dry-run 计划器；默认不写目标项目。

## 6. 目标项目安装产物与 receipt

目标项目安装布局：

```text
<project>/tools/project_moe_gui/
  launcher.py
  project_moe_gui.config.json
  project_moe_gui.install-manifest.json
<project>/project-moe-gui.cmd
```

manifest 最小字段：

```json
{
  "schema_version": 1,
  "tool": "project_moe_gui",
  "status": "installed",
  "installed_at": "2026-05-26T00:00:00Z",
  "source_repo": "D:/PythonProject_langgraph",
  "source_commit": "<git sha>",
  "target_project": "<project>",
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "managed_files": [],
  "readiness_status": "ready|ready-candidate|blocked",
  "control_mode_allowed": false,
  "rollback_pointer": null,
  "secrets_recorded": false
}
```

规则：

- 没有 manifest 时，项目只能是 `not-installed`。
- manifest hash 不匹配时，update/uninstall 必须 fail closed。
- 安装器不得默认生成私有 `MOE.md` 正文；如需 scaffold，只创建占位说明并要求人工填充。
- 安装器不得默认生成 `.codex/agents/*.toml`，除非用户明确调用 scaffold 命令并确认目标路径。

## 7. 目标项目 Agent TOML 与私有提示源标准

推荐 TOML：

```toml
name = "thesis-moe-mentor"
description = "Project-local MOE mentor for thesis-quality review."
developer_instructions = """
Use the project-local private prompt source by reference. Do not copy full private content into shared tooling.
"""

[project]
scope = "repo-local"
state_namespace = "thesis_moe"
private_prompt_source = "MOE.md"
private_prompt_policy = "do-not-copy-full-content"

[moe]
kind = "project-moe-agent"
family = "project-specific"
requires_manual_enable = true
project_default_state = ".omx/state/thesis_moe/project-default.json"
session_state_dir = ".omx/state/thesis_moe/sessions"

[dispatch]
mode = "brief-based"
forbidden = ["full-history-fork-with-custom-role"]
fallback = ["main-session-takeover", "durable-brief"]

[extensions]
# Project-specific fields are allowed here.
```

私有提示源规则：

- 必须位于目标项目内。
- 不得指向 `.codex/agents/`、`.omx/state/`、`tools/project_moe_gui/` 或 GUI managed artifacts。
- readiness checker 只检查路径、存在性和边界，不读取/复制全文。

## 8. Phase 1 CLI / readiness contract

Phase 1 是目标项目自己的最小 MOE 状态接口。

必须支持：

| 命令 | 写入 | 语义 |
| --- | --- | --- |
| `project-on --json` | 是 | 开启项目默认值，并传播到非手动 session。 |
| `project-off --json` | 是 | 关闭项目默认值，并传播到非手动 session。 |
| `project-status --json` | 否 | 报告项目默认值、session counts、无效记录和路径摘要。 |
| `list-sessions --json` | 否 | 返回脱敏 session 列表。 |
| `on --session-id <id> --json` | 是 | 写入单 session 手动开启 override。 |
| `off --session-id <id> --json` | 是 | 写入单 session 手动关闭 override。 |
| `status --json` | 否 | 计算当前或显式 session 的有效状态。 |
| `assert-on --json` | 否 | 只有有效状态开启时返回成功。 |

readiness checker 必查：

- Git dirty 状态；运行 `git status --porcelain --untracked-files=all` 时设置 `GIT_OPTIONAL_LOCKS=0`。
- Agent TOML 必填字段和标准扩展区。
- 私有提示源路径存在且不越界。
- CLI 读取命令 envelope、`effective_source`、session counts、列表结构和隐私字段。
- 写入命令 surface 是否声明 `atomic_write`、`lock_status`、`audit_path`、`no_op`、`before`、`after`、`changed_paths`。
- `.cmd` wrapper 是否只转发受控命令，是否强制 `--json`，是否禁止任意 `%*` 透传和 shell 串联。
- startup / resume / continue / reload / phase change 检查点是否会读取 `status --json`。

## 9. Phase 2 PySide6 GUI contract

GUI v1 必须包含：

- 顶部项目上下文：目标项目根、branch、agent name、state namespace、readiness lane。
- 项目默认卡片：有效默认状态、最后更新时间、开启/关闭按钮。
- session 表格：脱敏 session id、source、confidence、enabled、effective_enabled、validity、lifecycle status、branch、worktree、first/last seen、reason 摘要。
- 操作面板：刷新、开启项目默认、关闭项目默认、开启选中 session、关闭选中 session。
- 日志面板：实际调用命令、exit code、stable token、stdout/stderr 脱敏摘要。

GUI 行为规则：

- 刷新只调用只读命令，不触发写入、迁移或安装。
- 写入期间禁用同一 scope 的按钮并显示 loading。
- 写入完成后重新读取状态。
- 空 session 列表不能被解释为 MOE 已关闭。
- 错误展示必须包含 stable token、简短说明和建议动作。
- 状态徽标必须同时使用文字和颜色，不得只靠红/绿表达。

## 10. JSON contract 与状态模型

统一 envelope：

```json
{
  "schema_version": 1,
  "command": "status",
  "ok": true,
  "token": "ok",
  "exit_code": 0,
  "message": "short human message",
  "project_root": "<project>",
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "generated_at": "2026-05-26T00:00:00Z",
  "warnings": [],
  "errors": []
}
```

项目默认 state：

```json
{
  "schema_version": 1,
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "scope": "project-default",
  "enabled": true,
  "worktree": "D:/PythonProject_paper_suggest",
  "branch": "main",
  "updated_at": "2026-05-26T00:00:00Z",
  "reason": "project-on"
}
```

session state：

```json
{
  "schema_version": 1,
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "scope": "session",
  "enabled": true,
  "session_id": "redacted-or-hash",
  "session_id_source": "argument|environment|generated",
  "session_confidence": "high|medium|low",
  "override_origin": "manual-session|project-propagated",
  "worktree": "D:/PythonProject_paper_suggest",
  "branch": "main",
  "first_seen_at": "2026-05-26T00:00:00Z",
  "last_seen_at": "2026-05-26T00:00:00Z",
  "updated_at": "2026-05-26T00:00:00Z",
  "reason": "manual-session-on"
}
```

有效状态计算：

1. 有效 session override 优先。
2. 否则使用有效项目默认值。
3. 否则 fail closed，视为关闭。

失败 token：

| 场景 | exit code | token |
| --- | ---: | --- |
| 成功读写 | 0 | `ok` |
| `assert-on` 发现关闭 | 1 | `disabled` 或 `blocked:moe_disabled` |
| 参数错误 | 2 | `usage_error` |
| 状态损坏或 schema 不匹配 | 3 | `state_corrupt` / `blocked:unsupported_schema_version` |
| 路径、ownership 或 dirty preflight 阻断 | 4 | `blocked:unsafe_target_root` / `blocked:dirty_unowned_files` |
| 依赖或配置缺失 | 5 | `blocked:missing_agent_toml` / `blocked:missing_mode_cli` |
| 状态锁异常 | 6 | `blocked:state_lock_timeout` / `blocked:stale_state_lock` |

## 11. 安全、隐私、回滚与卸载

安全规则：

- 所有目标路径必须 resolve 后仍在目标项目根内。
- symlink / junction / path traversal 必须 fail closed。
- 写入使用临时文件 + atomic rename。
- 并发写入必须有 lock，疑似 stale lock 只报告 blocker，不自动覆盖。
- GUI 不展示 raw session id、私有提示全文、provider secrets、完整环境变量或完整 stderr。

回滚规则：

- 目标项目安装前必须记录 manifest 和 rollback pointer。
- 更新前必须比较 managed file hash。
- 回滚只还原 GUI managed artifacts，不删除项目私有 Agent TOML、`MOE.md` 或 `.omx/state`。
- 卸载默认 dry-run，仅输出 `planned_deletes`。
- `--apply` 在未实现前必须稳定返回 `blocked:uninstall_apply_not_supported`，且 `delete_executed=false`。

远端规则：

- 本方案实施和目标项目适配默认只做本地 Git commit。
- 未获得明确“推送远端 / GitLab / GitHub”授权前，不推送、不开 MR、不合并远端、不同步镜像。

## 12. Ready / Bootstrap / Repair lane gates

| Lane | 进入条件 | GUI 控制 | 输出 |
| --- | --- | --- | --- |
| Ready Lane | Phase 1 CLI、wrapper、startup hook、Agent TOML、私有提示源、dirty preflight 全通过 | 允许 | `control_mode_allowed=true` |
| Ready-candidate | static-only 全通过，但没有执行目标 CLI | 禁止 | `control_mode_allowed=false`，需执行读契约验证 |
| Bootstrap Lane | 目标项目缺少 Phase 1 | 禁止 | 缺口清单、scaffold dry-run、operator next steps |
| Repair Lane | 目标项目有 Phase 1 候选但存在 blocker | 禁止 | blocker 分组、修复顺序、下一步动作 |

`D:\PythonProject_paper_suggest` 当前归类：Ready Lane 候选，但最新证据仍是 blocked / Repair Lane；只有 readiness checker 正式输出 ready 后才允许真实 GUI 安装和控制。

readiness payload 必须包含：

```json
{
  "readiness_status": "ready|ready-candidate|blocked",
  "adaptation_lane": "ready|ready-candidate|bootstrap|repair",
  "control_mode_allowed": false,
  "bootstrap_required": false,
  "repair_required": true,
  "static_surface_blocking_codes": [],
  "remediation_plan": []
}
```

## 13. 实施任务拆分

### 13.1 已完成或已有基础

- [x] 明确 Project MOE GUI 与通用 PySide6 能力方案的边界。
- [x] 明确目标项目安装产物和 managed manifest 模型。
- [x] 明确 GUI 不直接编辑状态 JSON，只调用目标项目 CLI。
- [x] 明确 Ready / Bootstrap / Repair lane。
- [x] 明确 `D:\PythonProject_paper_suggest` 不能因存在 Phase 1 候选就直接进入 GUI 控制。
- [x] 明确 Comet bash 不可用时不得伪造脚本状态。
- [x] 将本文重构为新版可执行方案结构。

### 13.2 下一批实现顺序

- [ ] 固化 `check_project_moe_phase1_readiness.py` 的输出 schema 与 fixture。
- [ ] 固化 `scaffold_project_moe_phase1.py --dry-run --json` 的 Bootstrap Lane payload。
- [ ] 固化目标项目 wrapper readiness gate：强制 `--json`、禁止任意 `%*` 透传、禁止 shell 串联。
- [ ] 固化 Agent TOML 标准扩展区 readiness gate。
- [ ] 固化私有提示源路径 readiness gate。
- [ ] 固化 `assert-on --json` 只读断言 gate。
- [ ] 固化 GUI launcher preflight：先 readiness，再目标 CLI 读命令。
- [ ] 固化 GUI shell 的项目默认卡片、session 表格、错误 token 和写入后刷新。
- [ ] 固化安装/更新/卸载 managed manifest 与 hash gate。
- [ ] 在真实目标项目进入 Ready Lane 前，先记录 static-only 和执行读契约两类证据。

### 13.3 不得跳过的执行规则

- 每次目标项目写入前先确认 dirty/ownership preflight。
- 每次新增 checker 同步注册到仓库 guard。
- 每次完成 OpenSpec change 后要 archive；如果 Comet bash 不可用，必须记录 `x_archive_deferred_reason` 和 `x_archive_follow_up`。
- 每次本地提交前运行 precommit update/archive review。

## 14. 验证计划

局部验证：

```powershell
git diff --check
openspec validate <change-name>
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root .
.\tools\ci\local_mr_review.ps1
```

合入本地 main 前：

```powershell
.\tools\ci\local_gate.ps1
```

目标项目 readiness 验证：

- static-only 模式不得执行目标 CLI。
- no-exec-cli 模式不得产生目标状态副作用。
- 执行读契约模式必须检查 `project-status`、`list-sessions`、`status`、`assert-on`。
- 写入 fixture 必须覆盖 project on/off、session on/off、manual override 保留、invalid record skip、no-op、lock timeout、atomic write。

人工验收：

- 文档结构与新版 Pi sidecar 方案同级：目标、架构、source of truth、contract、gates、rollback、风险、自检齐全。
- 没有把 `D:\PythonProject_paper_suggest` 错写成 ready。
- 没有把 GUI 控制权扩展到未安装目标项目。
- 没有把私有提示源全文或 raw session id 纳入本仓库文档。

## 15. 对相关治理/方案的更新要求

当本方案后续进入代码实现时，需要同步检查：

- `pyside6_cross_project_gui_capability_plan.zh-CN.md`：只同步通用 PySide6 runtime、共享 venv、GUI packaging/launcher 规则，不混入 MOE 私有状态逻辑。
- OpenSpec stable specs：只有实现完成并归档后才提升 stable spec。
- 本仓库 guard：新增 checker、fixture 或 CI gate 时必须注册。
- 目标项目文档：只有在目标项目适配 worktree 中更新，不在本仓库替目标项目伪造 ready 状态。

## 16. 风险与默认决策

| 风险 | 默认决策 |
| --- | --- |
| 目标项目已有 Phase 1 但不完整 | 进入 Repair Lane，不允许 GUI 控制。 |
| 目标 CLI 读命令可能有副作用 | 先用 `--static-only` / `--no-exec-cli`。 |
| session id 只能 generated | GUI 标低置信度，不当作强隔离身份。 |
| 手动 session override 与项目默认冲突 | session 优先，GUI 显示冲突，不自动修复。 |
| manifest hash 不匹配 | update/uninstall fail closed。 |
| Comet bash 不可用 | 记录 blocker 和 archive deferral，不伪造通过。 |
| 远端落后本地 main | 可报告 remote lag；未授权不推送。 |

## 17. 自检清单

- [x] 本文已经采用新版实施方案结构。
- [x] 保留 `status: draft`，并用 `plan_readiness` 区分结构就绪与运行时完成。
- [x] 明确 GUI source of truth 在本仓库，目标项目状态 source of truth 在目标项目。
- [x] 明确 GUI 不直接编辑 JSON。
- [x] 明确 Ready / Bootstrap / Repair lane。
- [x] 明确 `D:\PythonProject_paper_suggest` 当前仍不是 GUI ready。
- [x] 明确私有提示源只引用不复制。
- [x] 明确安装、更新、卸载、rollback 的 managed artifact 边界。
- [x] 明确验证命令和本地 main / 远端发布边界。
- [ ] 后续代码实现完成后归档对应 OpenSpec change。
- [ ] 目标项目真实 Ready Lane 证据生成后，再允许 GUI 控制。

## 18. 参考源

- `docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md`：新版可执行方案结构参考。
- `docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.zh-CN.md`：通用 PySide6 runtime 与跨项目 GUI 能力边界。
- `openspec/changes/refresh-project-moe-gui-plan-comet/`：上一轮 Project MOE GUI 文档事实链更新 trace。
- `openspec/changes/restructure-project-moe-gui-plan-modern/`：本轮结构重构 trace。
- `docs_bilingual/memory/project_moe_paper_suggest_static_readiness_evidence_2026-05-24.md` 与 `.zh-CN.md`：`D:\PythonProject_paper_suggest` static-only readiness 证据。
