---
doc_id: project_moe_agent_gui_toolchain_plan
lang: zh-CN
status: active
plan_readiness: full-comet-structure-ready-for-implementation-slicing
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md
created_at: 2026-05-20
updated_at: 2026-06-01
last_reviewed_at: 2026-06-01
scope: project_moe_agent_gui_only
implementation_lane: ready_bootstrap_repair_lanes
comet_change: refine-project-moe-gui-plan-comet-structure
related_docs:
  - docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.zh-CN.md
  - docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md
  - docs_bilingual/memory/project_moe_paper_suggest_static_readiness_evidence_2026-05-24.zh-CN.md
---

# 项目级 MOE Agent GUI 工具链实施方案（完整 Comet 重构版）

> **For agentic workers:** REQUIRED SUB-SKILL：优先使用 `$comet` 控制层进入 OpenSpec/Comet change，再使用 `superpowers:writing-plans` / `superpowers:executing-plans` 逐任务执行。所有实施事项使用 checkbox 跟踪；每个事项完成后先运行对应局部验证，再进入下一项。若 Comet bash 脚本在当前 Windows 环境不可用，必须记录 blocker 与 archive deferral，不得伪造 `comet-state.sh` / `comet-guard.sh` 通过。

**Goal:** 为每个本地目标项目提供可复用、可安装、可回滚的项目级 MOE Agent 控制面：目标项目保留自己的 MOE Agent、私有提示源、Phase 1 CLI 与 `.omx/state/<namespace>/`；本仓库维护统一的 readiness checker、安装器、PySide6 GUI shell、launcher 模板和验证夹具。

**Architecture:** 本仓库提供 Project MOE GUI toolchain；目标项目提供 Phase 1 JSON CLI contract；GUI 只通过目标项目 CLI 读取与写入状态，不直接编辑目标项目 JSON。目标项目按 Ready / Ready-candidate / Bootstrap / Repair 四条 lane 进入不同处理路径，未通过 readiness 前不得启用真实 GUI 控制。

**Tech Stack:** OpenSpec / Comet trace、Python CLI/checker、PySide6 shared runtime、Windows `.cmd` / PowerShell launcher、repo-local `.omx/state`、JSON contract、manifest/hash gate、local-first Git flow。

---

## 0. 本次完整 Comet 重构结论

本文从“状态说明 + 零散任务清单”重构为“可执行实施方案 + Comet 追踪证据 + readiness lane 合同”。它与 `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` 采用同级组织方式，但不复用 Pi sidecar 的运行时边界。

| 检查项 | 结论 | 落点 |
| --- | --- | --- |
| Comet / OpenSpec 追踪 | 已补齐 | 第 3、14、15 节；`openspec/changes/refine-project-moe-gui-plan-comet-structure/` |
| 目标 / 非目标 | 已补齐 | 第 2 节 |
| Project MOE / GUI / 目标项目边界 | 已补齐 | 第 1、4、6、7 节 |
| Ready / Bootstrap / Repair lane | 已补齐 | 第 13 节 |
| Phase 1 CLI / readiness contract | 已补齐 | 第 9 节 |
| Phase 2 PySide6 GUI contract | 已补齐 | 第 10 节 |
| A/B 验证路线 | 已确认 | 第 0、1、13、14、15 节 |
| JSON state model | 已补齐 | 第 11 节 |
| 安全、隐私、回滚、卸载 | 已补齐 | 第 12 节 |
| 实施事项颗粒度 | 已重排 | 第 14 节 |
| 验证与本地/远端边界 | 已补齐 | 第 15 节 |

状态解释：

- `status: active`：本文是当前可执行实施方案；它不等于 Project MOE GUI 运行时能力已经全部完成。
- `plan_readiness: full-comet-structure-ready-for-implementation-slicing`：结构、边界、任务颗粒度已满足继续切分代码实施的入口要求。
- `D:\PythonProject_paper_suggest`：A 仍是 Phase 1 owner，不在 B 重新实现一套 A 业务 Phase 1。A 本地 `main` 已有 Phase 1、install/update receipt 与 rollback refs；但当前 GUI preflight 可用性必须以最新 0.2.23 更新后的重新验证为准。
- 2026-06-01 决策：A=`D:\PythonProject_paper_suggest` 保留为真实 Phase 1 owner，B=`D:\PythonProject_langgraph` 保留为 Phase 2 toolchain source of truth；修复 worktree dry-run 路线已收敛为 A 本地 main 真实安装/更新验证路线。不得为了验证方便在 B 重新实现一套完整 A 业务 Phase 1 来替代目标项目证据。
- 2026-06-01 证据：旧 worktree `paper_suggest-thesis-moe-phase1` 已判定为陈旧证据，不再作为 A 现状；新 A 修复 worktree `D:\PythonProject_langgraph\.worktrees\paper_suggest-moe-phase1-repair-20260601` 提交 `560da0e 功能：修复论文 MOE 阶段一就绪契约`。
- 2026-06-01 隐私边界：A 的 `MOE.md` 是 ignored/private 文件，仅为 readiness validation 被复制到 A 修复 worktree；不得提交、不得复制全文到 B 文档或工具链。
- 2026-06-01 readiness 证据：A 修复 worktree static-only 输出 `ok=true / readiness_status=static-ready-candidate / adaptation_lane=ready-candidate / control_mode_allowed=false`，其中 `readiness_status` 表示 Phase 1 契约分类，`adaptation_lane` 表示后续处理 lane，`control_mode_allowed=false` 表示只能展示或 dry-run；execute-read-contract 输出 `ok=true / token=ok / readiness_status=ready / adaptation_lane=ready / control_mode_allowed=true`，其中 `token=ok` 是稳定机器可读成功 token，`control_mode_allowed=true` 表示在具备 receipt 与 rollback 证据后可进入受控安装/控制路径，已校验 `project-status`、`list-sessions`、`status`、`assert-on`。
- 2026-06-01 A 本地 main 证据：A 已集成 `560da0e 功能：修复论文 MOE 阶段一就绪契约`、`c6b92ae 功能：安装论文 Project MOE GUI 控制面`、`ce23931 修复：使用共享运行时启动论文 Project MOE GUI`。回滚 refs 为 `refs/backup/local-main/20260601-125126-before-thesis-moe-phase1-repair-20260601` 和 `refs/backup/local-main/20260601-215213-before-project-moe-gui-runtime-entry-update`。
- 2026-06-01 Phase 2 证据：B toolchain `0.2.22` 修复目标 launcher 的 runtime 入口：按配置的 `runtime_python` 重新执行，使用 `PROJECT_MOE_GUI_RUNTIME_REEXEC` 防止递归，并设置 `PYTHONUTF8=1`。已安装 preflight payload 记录 `launcher_runtime_python` 与 `launcher_runtime_reexec`。
- 2026-06-01 纠偏证据：发现 A 已安装 `toolchain_source_root` 仍指向已删除的 B feature worktree，导致 A launcher preflight 返回 `blocked:phase1_readiness_gate_unavailable / No module named 'project_moe_gui'`；旧的“launcher preflight ok”只能视为历史证据，不能代表当前可用状态。
- 2026-06-01 Phase 2 修复切片：B toolchain `0.2.23` 将目标安装配置写入稳定 source root `D:\PythonProject_langgraph\tools\project_moe_gui_toolchain`，新增 `toolchain_source_root` 存在性/import checker，并允许 updater 修复 manifest 仍匹配但 source root 失效的可恢复安装状态。
- 2026-06-01 验收边界：A 仍是 Ready Lane 目标，但必须在 0.2.23 更新 A managed artifacts 并重新获得 install check、readiness 与 launcher preflight `token=ok` 后，才能重新声称“当前 GUI preflight 可用”；可见 GUI 启动仍是显式交互动作，并需要 `--allow-visible`。
- 2026-06-01 scaffold apply 切片：B toolchain `0.2.24` 新增受保护的 `scaffold_project_moe_phase1.py --apply`。它只在项目证据与干净 Git dirty-state 检查通过后创建缺失的 Bootstrap Lane 文件，拒绝覆盖既有私有提示源或 operator surfaces，并且在后续 readiness 返回 Ready Lane 之前保持 GUI 控制禁用。
- 当前 Comet change 是 `refine-project-moe-gui-plan-comet-structure`。如果 bash 不可用，只能用 OpenSpec artifacts、repo-local guard 与本地验证作为 fallback evidence。

就地字段解释：

- `readiness_status` 表示目标项目 Phase 1 契约的最终 readiness 分类；`static-ready-candidate` 表示只读静态检查已满足候选条件但尚未执行目标 CLI 读契约，`ready` 表示读契约已通过。
- `adaptation_lane` 表示目标项目后续处理 lane；`ready-candidate` 只能继续验证，`ready` 才允许进入安装或 GUI 控制的下一步。
- `control_mode_allowed` 表示 GUI 写入/控制是否允许；`false` 只能展示或 dry-run，`true` 仍需安装 receipt、rollback pointer 与目标项目验收后才代表可实际操作。
- `token=ok` 是目标 CLI 或安装器返回的稳定机器可读结果 token，用于避免仅凭自然语言判断成功。
- `blockers=[]` 表示当前 dry-run 没有阻断项；它不是实际安装完成证据。
- `launcher_runtime_python` 记录实际运行已安装 launcher 的解释器；`launcher_runtime_reexec=true` 证明通过 ambient Python 启动时已经重新进入配置的共享 PySide6 runtime。

## 1. 关系模型与命名边界

| 名称 | 角色 | Source of truth | 边界 |
| --- | --- | --- | --- |
| Project MOE Agent | 目标项目自己的专家型 Agent | `<project>/.codex/agents/*.toml` | 不安装到 user-level agents 作为共享 Agent |
| 私有提示源 | 目标项目私有约束、导师要求、领域规则 | `<project>/MOE.md` 或等价文件 | checker 只校验路径与存在性，不复制全文 |
| Phase 1 CLI | 目标项目 MOE 状态读写入口 | `<project>/tools/<mode>_moe_mode.py` | GUI 必须通过 CLI 读写，不直接改 JSON |
| Phase 2 GUI | 本仓库维护的 PySide6 控制面 | `tools/project_moe_gui_toolchain/` | 安装后只控制被安装的目标项目 |
| Readiness checker | 安装/控制前只读 gate | 本仓库工具链 | 只输出 go/no-go 与 blockers，不授权写目标项目 |
| `.omx/state/<namespace>/` | 目标项目 MOE 状态 | 目标项目 repo-local state | 不跨项目扫描，不写其他项目 |

### 1.1 MOE 专家、subagent 与 skills 边界

- MOE 专家是专家镜头 / 路由语义，例如盲审专家、导师质询专家、AIGC 风险专家、创新性把关专家；它描述“按什么专业视角判断”，不是独立执行载体。
- subagent / native agent 是执行载体或角色线程，例如 Codex 内置角色、用户级 agent TOML、项目本地 `.codex/agents/*.toml`。一个 subagent 可以内含多个 MOE 专家镜头，主会话也可以直接使用 MOE 专家镜头。
- 因此 MOE 专家与 subagent 是可组合矩阵关系，不是同义词，也不是互斥关系；不能把“调用了 MOE 镜头”写成 native subagent evidence。
- 调用 MOE 专家不要求专门 skills。`MOE.md`、agent TOML 或主会话上下文即可承载 MOE 调度规则；skills 只可作为可选 workflow 封装，且 skill/profile invocation 不能替代 native expert evidence。

默认命名：

- 工具链命名空间：`project_moe_gui`
- 状态命名空间示例：`thesis_moe`
- 目标项目 launcher 示例：`project-moe-gui.cmd`
- 目标项目 CLI 示例：`tools/thesis_moe_mode.py`

## 2. 目标与非目标

目标：

1. 为目标项目提供项目默认 MOE 开关、单 session override、状态读取和 fail-closed 断言。
2. 为 GUI 提供统一 JSON contract，使 PySide6 控制面能显示项目默认状态、session 列表、readiness blocker、写入结果和错误 token。
3. 让缺少 Phase 1 的项目走 Bootstrap Lane，只输出缺口清单与 scaffold dry-run 计划。
4. 让已有 Phase 1 但不完整的项目走 Repair Lane，明确修复项后再允许 GUI 控制。
5. 让完全满足 readiness gate 的项目进入 Ready Lane，允许安装和使用 GUI。
6. 把安装、更新、回滚、卸载和验证全部做成 manifest/receipt 可追踪流程。

非目标：

- 不用 GUI 绕过目标项目 Phase 1 readiness gate。
- 不复制目标项目私有 `MOE.md` 全文。
- 不把项目专属 MOE Agent 默认安装到 `C:\Users\lenovo\.codex\agents`。
- 不做跨项目总控制台，也不默认扫描所有项目。
- 不让 GUI 直接编辑 `.omx/state` JSON。
- 不把 workflow skills、plugin profiles 或 GUI profile loading 当成 native expert evidence。
- 未获明确远端授权前，不推 GitLab/GitHub、不开 MR、不合并远端、不同步镜像。

## 3. Comet / OpenSpec 工作边界

本方案的完整 Comet 边界：

| Phase | 本次文件 | 规则 |
| --- | --- | --- |
| Open | `proposal.md`、`.openspec.yaml` | 定义 why/what/scope/non-goals/rollback/validation |
| Design | `design.md`、`docs/superpowers/specs/*design.md`、delta spec | 固化结构选择、lane 模型、contract 边界 |
| Build | 本文、`docs/superpowers/plans/*`、`tasks.md` | 执行方案重构与有界工具链切片，并勾选任务 |
| Verify | `git diff --check`、`openspec validate`、repo guard、precommit gate | 不把未运行的脚本声明为通过 |
| Archive | 后续单独执行 | 若本地分支尚未合入或 Comet bash 不可用，必须写明 archive deferral |

当前策略：

- 初始切片是文档/方案重构；当前延续切片包含 Project MOE GUI toolchain 的有界 runtime 实现与目标项目 readiness 证据收敛。
- 下一步验证路线是“修 A 的真实 Phase 1，再用 B 的 Phase 2 安装验证”，不是在 B 复制 A 的业务 Phase 1。
- 在 A readiness checker 输出 `control_mode_allowed=true` 之前，不安装 PySide6 GUI 到 A、不启动真实 GUI 控制、不写 user-level 目录。
- 用户已授权本地 feature 提交与本地 `main` 合入；远端发布仍需用户后续明确指令。

### 3.1 Comet 管理记录、阶段门禁与 Monitoring 语义

本方案采用新版 Comet runtime-control 结构，但 Project MOE GUI 仍然是 Project MOE 工具链方案，不是 Comet runtime 本体实现。需要复用的语义如下：

| 概念 | 本方案中的强制解释 |
| --- | --- |
| 管理记录 | `management.md` 是 Open、Design、Build、Verify、Archive 与 Monitoring 的阶段证据账本，不是装饰性备注；它证明当前阶段为什么可以前进。 |
| 阶段门禁 | 只有当前阶段 checklist 完成，且 Monitoring 为 `clear` / `continue` 时，前进 transition 才有效；如果 Windows 上 Comet bash 脚本不可用，只能记录文件态证据，不能声称脚本 transition 已通过。 |
| Monitoring 回路 | Monitoring 是跨阶段控制回路，不是第六个 Comet phase；回退决策只能映射到 `return-open`、`return-design`、`return-build` 或 `return-verify`，并保留明确原因和既有 artifacts。 |
| 证据留存 | 验证输出、归档延期、worktree receipt、changed-path 摘要必须保存在仓库本地 artifacts 中，不能只留在聊天记录里。 |
| 授权边界 | 本地 feature 工作与本地 `main` 合入遵循 local-first 规则；远端发布、目标项目写入、批准流程外的破坏性清理和范围扩大必须再次获得用户明确授权。 |

### 3.2 完整 `/comet` 结构对齐清单

目标结构必须与新版 Pi sidecar 方案同级，同时继承 Comet runtime 方案的控制语义：

| 参考结构 | Project MOE GUI 对应落点 |
| --- | --- |
| 复核结论 | 第 0 节记录 readiness、draft 状态以及仍未实现的能力。 |
| 关系 / 命名边界 | 第 1 节分离目标项目 MOE Agent、私有提示源、Phase 1 CLI、Phase 2 GUI、checker 与 state namespace。 |
| 运行时架构与使用方式 | 第 4-5 节定义 operator、launcher、GUI、CLI 与目标状态之间的交互。 |
| Source of truth | 第 6 节规定共享工具链源码在本仓库，目标状态在目标项目。 |
| 安装产物 / receipt | 第 7 节定义目标项目 managed files 与 manifest 要求。 |
| CLI / JSON / 状态契约 | 第 9-11 节定义读写命令、envelope、状态文件、有效状态优先级和稳定失败 token。 |
| Readiness gates | 第 13 节定义 Ready、Ready-candidate、Bootstrap 与 Repair lane。 |
| 实施 backlog | 第 14 节使用有序切片、事项级 checkbox、文件职责、集成顺序和证据留存规则。 |
| 验证 / 回滚 / 自检 | 第 12、15、17、18 节定义安全、回滚、验证、风险和完成标准。 |

## 4. 运行时架构

```text
Operator / Codex session
  -> target project startup/readiness check
  -> target project Phase 1 CLI JSON contract
  -> Project MOE GUI launcher installed in target project
  -> PySide6 GUI shell from this repository's toolchain
  -> target project .omx/state/<namespace>/ JSON files
```

核心规则：

- GUI 启动先定位目标项目根目录，再运行 readiness checker。
- readiness checker 只读；它可以执行安全的 JSON 读取命令，但不得修改目标项目。
- 写入命令只允许通过目标项目 Phase 1 CLI：`project-on`、`project-off`、`on --session-id`、`off --session-id`。
- 写入后 GUI 必须重新读取状态，不信任本地 UI 预测值。
- 目标项目 dirty、CLI contract 不完整、wrapper 不安全、startup hook 缺失、私有提示源越界时 fail closed。

## 5. Codex / GUI / 目标项目使用方式

Codex 操作意图示例：

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

GUI 启动示例：

```powershell
<project>\project-moe-gui.cmd
python <project>\tools\project_moe_gui\launcher.py --project-root <project>
```

GUI 必须显示：项目根、branch、agent name、state namespace、readiness lane、项目默认状态、session 列表、最近写入摘要、错误 token、建议动作。

## 6. Repo-local source of truth

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

配套治理与验证：

```text
docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md
openspec/changes/<project-moe-change>/
tests/project-moe-gui/
```

职责分离：

- `install_project_moe_gui.py`：复制/生成目标项目 GUI managed artifacts，并写 install manifest。
- `update_project_moe_gui.py`：读取 manifest 后受控更新 managed artifacts。
- `check_project_moe_gui_install.py`：验证目标项目安装状态和 hash。
- `check_project_moe_phase1_readiness.py`：只读检查目标项目 Phase 1 是否达到 GUI 控制前提。
- `scaffold_project_moe_phase1.py`：Bootstrap Lane dry-run 计划器；默认不写目标项目。

## 7. 目标项目安装产物与 manifest

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
  "installed_at": "2026-05-27T00:00:00Z",
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
- 安装器不得默认生成 `.codex/agents/*.toml`；除非用户显式调用 scaffold 命令并确认目标路径。

## 8. 目标项目 Agent TOML 与私有提示源标准

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

## 9. Phase 1 CLI / readiness contract

Phase 1 是目标项目自己的最小 MOE 状态接口。

| 命令 | 写入 | 语义 |
| --- | --- | --- |
| `project-on --json` | 是 | 开启项目默认值，并传播到非手动 session |
| `project-off --json` | 是 | 关闭项目默认值，并传播到非手动 session |
| `project-status --json` | 否 | 报告项目默认值、session counts、无效记录和路径摘要 |
| `list-sessions --json` | 否 | 返回脱敏 session 列表 |
| `on --session-id <id> --json` | 是 | 写入单 session 手动开启 override |
| `off --session-id <id> --json` | 是 | 写入单 session 手动关闭 override |
| `status --json` | 否 | 计算当前或显式 session 的有效状态 |
| `assert-on --json` | 否 | 有效状态开启时返回成功，否则返回稳定 blocker |

readiness checker 必查：

- Git dirty 状态：运行 `git status --porcelain --untracked-files=all` 时设置 `GIT_OPTIONAL_LOCKS=0`。
- Agent TOML 必填字段与标准扩展区。
- 私有提示源路径存在且不越界。
- CLI 读取命令 envelope、`effective_source`、session counts、列表结构和隐私字段。
- 写入命令 surface 是否声明 `atomic_write`、`lock_status`、`audit_path`、`no_op`、`before`、`after`、`changed_paths`。
- `.cmd` wrapper 是否只转发受控命令、强制 `--json`、禁止任意 `%*` 透传和 shell 串联。
- startup / resume / continue / reload / phase change 检查点是否会读取 `status --json`。

## 10. Phase 2 PySide6 GUI contract

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

## 11. JSON contract 与状态模型

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
  "generated_at": "2026-05-27T00:00:00Z",
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
  "updated_at": "2026-05-27T00:00:00Z",
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
  "first_seen_at": "2026-05-27T00:00:00Z",
  "last_seen_at": "2026-05-27T00:00:00Z",
  "updated_at": "2026-05-27T00:00:00Z",
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
| `assert-on` 发现关闭 | 1 | `disabled` / `blocked:moe_disabled` |
| 参数错误 | 2 | `usage_error` |
| 状态损坏或 schema 不匹配 | 3 | `state_corrupt` / `blocked:unsupported_schema_version` |
| 路径、ownership、dirty preflight 阻断 | 4 | `blocked:unsafe_target_root` / `blocked:dirty_unowned_files` |
| 依赖或配置缺失 | 5 | `blocked:missing_agent_toml` / `blocked:missing_mode_cli` |
| 状态锁异常 | 6 | `blocked:state_lock_timeout` / `blocked:stale_state_lock` |

## 12. 安全、隐私、回滚与卸载

安全规则：

- 所有目标路径必须 resolve 后仍在目标项目根内。
- symlink / junction / path traversal 必须 fail closed。
- 写入使用临时文件 + atomic rename。
- 并发写入必须有 lock；疑似 stale lock 只报告 blocker，不自动覆盖。
- GUI 不展示 raw session id、私有提示全文、provider secrets、完整环境变量或完整 stderr。

回滚规则：

- 目标项目安装前必须记录 manifest 和 rollback pointer。
- 更新前必须比较 managed file hash。
- 回滚只还原 GUI managed artifacts，不删除项目私有 Agent TOML、`MOE.md` 或 `.omx/state`。
- 卸载默认 dry-run，仅输出 `planned_deletes`，不删除目标项目文件。
- `--apply` 仅在 manifest 路径白名单和 managed file hash 检查全部通过后才受支持；它只删除 Project MOE GUI 受管产物，返回 `delete_executed=true`，并保留 `MOE.md`、`.codex/agents/*.toml` 和 `.omx/state`。
- 如果 manifest 中存在白名单外路径、hash 缺失或不匹配，或 managed entry 不是文件，卸载必须在删除任何文件前 fail closed。

远端规则：

- 本方案实施和目标项目适配默认只做本地 Git commit。
- 未获得明确“推送远端 / GitLab / GitHub”授权前，不推送、不开 MR、不合并远端、不同步镜像。

## 13. Ready / Bootstrap / Repair lane gates

| Lane | 进入条件 | GUI 控制 | 输出 |
| --- | --- | --- | --- |
| Ready Lane | Phase 1 CLI、wrapper、startup hook、Agent TOML、私有提示源、dirty preflight 全通过 | 允许 | `control_mode_allowed=true` |
| Ready-candidate | static-only 全通过，但没有执行目标 CLI | 禁止 | `control_mode_allowed=false`，需执行读契约验证 |
| Bootstrap Lane | 目标项目缺少 Phase 1 | 禁止 | 缺口清单、scaffold dry-run、operator next steps |
| Repair Lane | 目标项目有 Phase 1 候选但存在 blocker | 禁止 | blocker 分组、修复顺序、下一步动作 |

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

`D:\PythonProject_paper_suggest` 当前归类：Ready Lane，但当前已安装 GUI preflight 曾因 stale `toolchain_source_root` 指向已删除 feature worktree 而阻断。A 必须更新到 B toolchain `0.2.23` 并重新通过 install check、readiness 与 launcher preflight，才可重新视为“当前 GUI preflight 可用”。

A 已完成的收敛顺序：

1. 修复 A Agent TOML 标准段与 wrapper / CLI JSON 安全边界。
2. 补齐 startup activation hook（启动/恢复/继续/重载/阶段变化时运行 `status --json` 的激活检查入口），并验证 `project-status`、`list-sessions`、`status`、`assert-on`。
3. 将 A Phase 1 修复集成为 `560da0e`。
4. 将 B 的 Project MOE GUI 安装到 A，并将安装集成为 `c6b92ae`。
5. 修复 B 已安装 launcher 的 runtime 入口，把 A 更新到 toolchain `0.2.22`，并将 A launcher 更新集成为 `ce23931`。
6. 发现 stale `toolchain_source_root` 会让 install check 误报正常但 launcher preflight 失败。
7. 在 B toolchain `0.2.23` 增加稳定 source-root 写入、source-root checker 与 updater 自修复逻辑。
8. 后续必须重新更新 A managed artifacts 并重新运行 install check、readiness、已安装 launcher preflight 与 A 测试；这解锁受保护 GUI 使用，但不表示已启动可见 GUI 窗口。

## 14. 实施事项清单（按顺序，细颗粒度）

### 14.1 已完成或已有基础

- [x] 明确 Project MOE GUI 与通用 PySide6 能力方案的边界。
- [x] 明确 GUI source of truth 在本仓库，目标项目状态 source of truth 在目标项目。
- [x] 明确目标项目安装产物与 managed manifest 模型。
- [x] 明确 GUI 不直接编辑状态 JSON，只调用目标项目 CLI。
- [x] 明确 Ready / Ready-candidate / Bootstrap / Repair lane。
- [x] 明确 `D:\PythonProject_paper_suggest` 不能因存在 Phase 1 候选就直接进入 GUI 控制。
- [x] 明确下一步路线：先修 A 的真实 Phase 1 contract，再用 B 的 Phase 2 dry-run、安装和 GUI 验收；不在 B 重新实现完整 A 业务 Phase 1 替代目标项目证据。
- [x] 明确 MOE 专家、subagent 与 skills 的边界：MOE 是专家镜头，subagent 是执行载体，skills 是可选 workflow 封装。
- [x] 明确 Comet bash 不可用时不得伪造脚本状态。
- [x] 将本文重构为完整 Comet 可执行方案结构。
- [x] 将 Comet 管理记录、阶段门禁、Monitoring 回退、证据留存和授权边界语义补入本文。

### 14.2 实施切片

#### Slice 0：方案与 OpenSpec 证据收口

- [x] 复用既有 OpenSpec change `refine-project-moe-gui-plan-comet-structure`，不新开无关重复 change。
- [x] 保留 `status: active`，并用 `plan_readiness` 表示可进入实现切片，不表示运行时已完成。
- [x] 保持中英文 implementation-plan 成对同步。
- [x] 如实在 `.comet.yaml` 记录 Windows Comet bash 不可用。
- [x] 将本 change 下损坏的中文 OpenSpec / Superpowers 支撑 artifacts 替换为合法 UTF-8 中文文本。
- [x] 更新 `tasks.md` / `tasks.zh-CN.md`，让本次完整 `/comet` 结构化通过具备显式证据。
- [x] 支撑 artifacts 修复后重新运行 OpenSpec validate 与仓库 guard。

#### Slice 1：Phase 1 readiness checker 与 schema

- [x] 定义 `check_project_moe_phase1_readiness.py --json` envelope。
- [x] 新增 `ready`、`ready-candidate`、`bootstrap`、`repair` 四类 fixture 项目。
- [x] 新增负向 fixture：缺 Agent TOML、TOML 无效、缺私有提示源、私有提示源越界、缺 CLI、CLI schema 不支持、目标根目录 dirty。
- [x] 确保 static-only 模式永不执行目标项目 CLI。
- [x] 确保 read-contract 模式只执行安全读命令。
- [x] 确保 readiness 输出包含 lane、blockers、warnings、checked files、脱敏路径和 `control_mode_allowed`。
- 证据（2026-05-28）：`harden-moe-readiness-output-contract-20260528` 已补齐显式 `warnings`、`checked_files` 与 `redacted_paths` 证据字段，并覆盖 ready/static-only 回归断言。
- 证据（2026-05-28）：当前 schema 加固 OpenSpec change 增加了用于不支持 CLI envelope schema 的稳定 fail-closed blocker；对应回归测试证明 readiness 会保持阻断；既有 fixture 继续覆盖 ready、ready-candidate、bootstrap、repair、static-only 和 read-contract 命令边界。

#### Slice 2：Bootstrap 与 Repair lane 工具

- [x] 固化 `scaffold_project_moe_phase1.py --dry-run --json` 输出。
- [x] 默认只生成 bootstrap actions，不写目标文件。
- [x] 只有在目标 ownership 和 dirty-state 检查通过后，才提供显式 `--apply` 路径。
- 证据（2026-06-01）：toolchain `0.2.24` 新增受保护 scaffold `--apply`；回归测试证明 clean target 只创建缺失 Phase 1 文件、dirty target 在写入前 fail closed、既有私有提示源 / agent surface 不会被覆盖。
- [x] 为部分实现 Phase 1 的项目输出 repair-lane report。
- [x] 在新 checker 证据证明之前，保持 `D:\PythonProject_paper_suggest` 为 repair-lane；只有产生真实 Ready Lane 证据后才晋级。

#### Slice 3：目标安装、更新、卸载与回滚 manifest

- [x] 在 `<project>/tools/project_moe_gui/` 下实现安装产物生成。
- [x] 生成 `<project>/project-moe-gui.cmd` 作为窄 launcher，不允许任意命令透传。
- [x] 写入 `project_moe_gui.install-manifest.json`，包含 source commit、managed files、hashes、target root、agent name、namespace、readiness result 和 rollback pointer。
- [x] 通过 manifest hash 与 source version 比较实现 update。
- [x] 通过 manifest 只删除自身 owned managed files 实现受保护 uninstall apply。
- [x] 覆盖或删除任何 managed target artifact 前，先依赖 manifest hash / receipt / rollback hint 形成本地可追溯证据。
- [x] 安装/更新目标项目时写入稳定 `toolchain_source_root`，不把 feature worktree 路径固化进目标项目长期配置。
- [x] `check_project_moe_gui_install.py` fail-closed 校验 `toolchain_source_root` 是否存在且可 import `project_moe_gui`。
- [x] `update_project_moe_gui.py` 可修复 manifest 仍匹配但 `toolchain_source_root` 已失效的可恢复安装状态。

#### Slice 4：Phase 2 PySide6 GUI shell

- [x] 实现 launcher preflight：目标根选择、readiness check、read-contract check、fail-closed blocker 展示。
- [x] 实现项目默认状态卡片。
- [x] 实现 session 表格，并脱敏 session identifier 与生命周期字段。
- [x] 通过目标 CLI 实现项目默认 on/off。
- [x] 通过目标 CLI 实现选中 session on/off。
- [x] 写入期间禁用同 scope 控件，并在每次写入后刷新状态。
- [x] 展示 stable failure token、简短解释、建议动作和脱敏 stdout/stderr 摘要。

#### Slice 5：治理、文档与 checker 集成

以下是常驻治理规则，不再作为“未完成实施项”使用空 checkbox 表示：

- 新增 checker 时同步注册到仓库 guard 和 CI manifest。
- 只在共享 runtime 与 launcher 边界变化时更新 PySide6 跨项目能力方案。
- 只在 MOE GUI 状态、readiness 与 installer 行为变化时更新 Project MOE 专属文档。
- 不把 workflow skills、plugin profiles 或 GUI profile loading 写成 native-expert evidence。
- 私有提示源只引用，不复制正文。

本切片已完成的专属文档/checker 收口：

- [x] 将 stale `toolchain_source_root` 风险写入 Project MOE 专属方案。
- [x] 将长期治理规则从待办 checkbox 中拆出，避免被误读为未完成产品功能。
- [x] 为 source-root checker 与 updater 自修复补充回归测试。

#### Slice 6：目标项目验收与推广

- [x] 判定旧 A worktree `paper_suggest-thesis-moe-phase1` 为陈旧证据，不再作为当前 A 现状。
- [x] 从 A 当前 `main` 派生新的修复 worktree：`D:\PythonProject_langgraph\.worktrees\paper_suggest-moe-phase1-repair-20260601`。
- [x] 保持 A 的 `MOE.md` 为 ignored/private 文件，仅在 A 修复 worktree 本地用于 readiness validation，不提交、不复制全文到 B。
- [x] 在 A 修复 worktree 修复 Agent TOML 扩展段：`[project]`、`[moe]`、`[dispatch]`、`[extensions]`。
- [x] 在 A 修复 worktree 修复 wrapper JSON/安全边界：`thesis-moe-on.cmd` 与 `thesis-moe-off.cmd` 收敛为单条 JSON CLI 调用，去除噪声、等待与暂停。
- [x] 在 A 修复 worktree修复 `list-sessions` CLI contract 与 session row stable token，并为 corrupt-state token 增加稳定归一化。
- [x] 提交 A 修复分支：`560da0e 功能：修复论文 MOE 阶段一就绪契约`。
- [x] 记录 A 修复后的 static-only readiness 证据：`ok=true / static-ready-candidate / ready-candidate / control_mode_allowed=false`。
- [x] 记录 A 修复后的 read-contract readiness 证据：`ok=true / token=ok / ready / control_mode_allowed=true`。
- [x] A readiness 输出 `control_mode_allowed=true` 后，记录 B 的 Phase 2 installer dry-run 证据：`ok=true / token=ok / blockers=[] / mode=dry-run`。
- [x] 补齐 A 的 startup activation hook（启动/恢复/继续/重载/阶段变化时运行 `status --json` 的激活检查入口），并针对 A 本地 `main` 重新运行 readiness。
- [x] installer dry-run 无 blocker 后，记录 A 的真实安装 receipt 与 rollback pointer。
- [x] 记录写入 fixture 证据：project on/off、session on/off、no-op、invalid record skip、lock timeout、atomic write。
- [x] 只有产生新的 Ready Lane 证据后，才允许该目标项目进入受保护 GUI 控制；可见 GUI 启动仍是显式交互验收动作。

### 14.3 文件职责图

| 路径族 | Owner | 规则 |
| --- | --- | --- |
| `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan*.md` | 本方案 change | 双语方案源文件，必须成对更新。 |
| `openspec/changes/refine-project-moe-gui-plan-comet-structure/` | 当前 Comet/OpenSpec change | proposal、design、tasks、management record、delta spec 与 archive deferral 证据。 |
| `docs/superpowers/specs/*project-moe-gui*` 与 `docs/superpowers/plans/*project-moe-gui*` | 当前 Comet/Superpowers change | 本次重构的 HOW 证据；若存在中文配对，必须是合法 UTF-8 中文文本。 |
| `tools/project_moe_gui_toolchain/` | 后续实现切片 | 共享 checker、installer、updater、launcher templates、PySide6 GUI shell 与 tests。 |
| `<target>/.codex/agents/*.toml`、`<target>/MOE.md`、`<target>/tools/*_moe_mode.py`、`<target>/.omx/state/<namespace>/` | 目标项目 | 目标项目 owned；本仓库只能按 contract 检查或调用 CLI，不能静默接管或修改。 |

### 14.4 本地集成顺序与证据留存

以下是每次实施必须遵守的本地集成常驻规则，不再作为方案剩余产品功能计数：

- 从当前本地 `main` 创建 feature branch 或 feature worktree。
- 主目录保持在本地 `main`，不要变成 feature workspace。
- 只有 precommit update/archive review 通过后才提交。
- 本地 `main` 合入前运行 local gate 和 local MR review。
- feature 分支干净且用户已授权本地集成边界后，才合入本地 `main`。
- 远端发布保持独立；除非当前用户消息明确批准远端发布，否则不推 GitLab/GitHub。
- 留存证据：命令输出摘要、changed paths、worktree receipt、如已创建则记录 rollback ref、如无法 archive 则记录 archive deferral reason。

### 14.5 不得跳过的执行规则

以下是持续执行规则，不用空 checkbox 表示“尚未实施”：

- 每次目标项目写入前先确认 dirty/ownership preflight。
- 每次新增 checker 同步注册到仓库 guard。
- 每次完成 OpenSpec change 后要 archive；若 Comet bash 不可用，必须记录归档延期原因字段和归档后续动作字段。
- 字段解释：`x_archive_deferred_reason` 记录“为什么本轮不能立即归档”的稳定原因；`x_archive_follow_up` 记录“下一次由谁、在什么条件下继续归档”的后续动作。
- 每次本地提交前运行 precommit update/archive review。
- 每次本地 main 合入前运行 local gate 与 local MR review。
- 如果 expert、durable worker、GUI action 或目标 CLI 超时，必须视为缺失证据；只能重试、缩小范围、转交合格 durable lane，或记录主会话显式接管。

## 15. 验证计划

feature 分支验证：

```powershell
git diff --check
openspec validate refine-project-moe-gui-plan-comet-structure
python .\tools\check_implementation_plan_rules.py --root . --json
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root .
```

提交后、本地 main 合入前：

```powershell
.\tools\ci\local_gate.ps1
.\tools\ci\local_mr_review.ps1
```

如果 Comet bash 脚本不可用，验证报告必须明确说明，并使用 OpenSpec validate、仓库 guard、本地 CI 与 local MR review 作为证据，不得伪造 `comet-state.sh` 证据。

目标项目 readiness 验证：

- static-only 模式不得执行目标 CLI。
- no-exec-cli 模式不得产生目标状态副作用。
- 执行读契约模式必须检查 `project-status`、`list-sessions`、`status`、`assert-on`。
- 2026-06-01 对 A 修复 worktree 已执行的命令：
  - static-only A readiness 证据：`python .\tools\project_moe_gui_toolchain\check_project_moe_phase1_readiness.py --target-project D:\PythonProject_langgraph\.worktrees\paper_suggest-moe-phase1-repair-20260601 --agent-name thesis-moe-mentor --state-namespace thesis_moe --mode-cli tools/thesis_moe_mode.py --on-wrapper thesis-moe-on.cmd --off-wrapper thesis-moe-off.cmd --json --static-only`
  - execute-read-contract A readiness 证据：`python .\tools\project_moe_gui_toolchain\check_project_moe_phase1_readiness.py --target-project D:\PythonProject_langgraph\.worktrees\paper_suggest-moe-phase1-repair-20260601 --agent-name thesis-moe-mentor --state-namespace thesis_moe --mode-cli tools/thesis_moe_mode.py --on-wrapper thesis-moe-on.cmd --off-wrapper thesis-moe-off.cmd --json`
  - B Phase 2 installer dry-run 证据：`python .\tools\project_moe_gui_toolchain\install_project_moe_gui.py --target-project D:\PythonProject_langgraph\.worktrees\paper_suggest-moe-phase1-repair-20260601 --agent-name thesis-moe-mentor --state-namespace thesis_moe --mode-cli tools/thesis_moe_mode.py --dry-run --json`
- 2026-06-01 对 A 修复 worktree 已记录的结果：
  - A 修复提交：`560da0e 功能：修复论文 MOE 阶段一就绪契约`。
  - static-only：`ok=true / static-ready-candidate / ready-candidate / control_mode_allowed=false`。
  - execute-read-contract：`ok=true / token=ok / ready / control_mode_allowed=true`。
  - installer dry-run：`ok=true / token=ok / blockers=[] / planned_writes=4`。
- 字段含义：`static-ready-candidate` 是只读静态候选，`ready` 是读契约通过，`control_mode_allowed=true` 只代表可进入受控安装/控制路径，`planned_writes=4` 只代表 dry-run 将创建 4 个受管文件而非已经写入。
- A 本地 `main` 真实安装/更新后新增记录结果：
  - A 提交：`560da0e` Phase 1 修复、`c6b92ae` GUI 安装、`ce23931` 共享 runtime launcher 更新。
  - install/update check：`ok=true / status=up_to_date / installed_toolchain_version=0.2.22 / target_toolchain_version=0.2.22 / runtime_status=import_ok / blockers=[]`。
  - readiness recheck：`ok=true / readiness_status=ready / adaptation_lane=ready / control_mode_allowed=true / git_status.dirty=false`。
  - 已安装 launcher preflight：`ok=true / token=ok / pyside6_status=import_ok / launcher_runtime_reexec=true`。
  - 目标项目测试：`python -m unittest discover -s test -p "test_thesis_moe_mode.py"` => `Ran 6 tests ... OK`。
  - 可见 GUI 启动：本次未执行。
- 写入 fixture 已在 `test/project_moe_gui_toolchain.test.py` 覆盖 project on/off、session on/off、manual override 保留、invalid record skip、no-op、lock timeout、atomic write。

人工验收：

- 文档结构与新版本 Pi sidecar 方案同级：目标、架构、source of truth、contract、gates、rollback、风险、自检齐全。
- `D:\PythonProject_paper_suggest` 只在真实安装 preflight 证据基础上标记为 Ready Lane，不写成“已启动可见 GUI”或“已完成人工交互验收”。
- 没有把 GUI 控制权扩展到未安装目标项目。
- 没有把私有提示源全文或 raw session id 纳入本仓库文档。

## 16. 对相关治理 / 方案的更新要求

后续进入代码实现时，需要同步检查：

- `pyside6_cross_project_gui_capability_plan.zh-CN.md`：只同步通用 PySide6 runtime、共享 venv、GUI packaging/launcher 规则，不混入 MOE 私有状态逻辑。
- `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md`：只作为新版结构参考，不继承 Pi sidecar runtime 边界。
- OpenSpec stable specs：只有实现完成并归档后才提升 stable spec。
- 本仓库 guard：新增 checker、fixture 或 CI gate 时必须注册。
- 目标项目文档：只在目标项目适配 worktree 中更新，不在本仓库伪造目标项目 ready 状态。

## 17. 风险与默认决策

| 风险 | 默认决策 |
| --- | --- |
| 为验证方便在 B 复制 A 的业务 Phase 1 | 禁止作为 A 的替代证据；只能把 B fixture 当 checker/installer 回归，不当真实目标项目验收 |
| 目标项目已有 Phase 1 但不完整 | 进入 Repair Lane，不允许 GUI 控制 |
| 目标 CLI 读命令可能有副作用 | 先用 `--static-only` / `--no-exec-cli` |
| session id 只能 generated | GUI 标低置信度，不当作强隔离身份 |
| 手动 session override 与项目默认冲突 | session 优先，GUI 显示冲突，不自动修复 |
| manifest hash 不匹配 | update/uninstall fail closed |
| Comet bash 不可用 | 记录 blocker 和 archive deferral，不伪造通过 |
| 远端落后本地 main | 可报告 remote lag；未授权不推送 |

## 18. 自检清单

- [x] 本文采用完整 Comet 实施方案结构。
- [x] 保留 `status: active`，并用 `plan_readiness` 区分结构就绪与运行时完成。
- [x] 明确 GUI source of truth 在本仓库，目标项目状态 source of truth 在目标项目。
- [x] 明确 GUI 不直接编辑 JSON。
- [x] 明确 Ready / Ready-candidate / Bootstrap / Repair lane。
- [x] 明确 `D:\PythonProject_paper_suggest` 的历史安装证据与当前 stale source-root 阻断状态，要求 0.2.23 更新后重新验收 preflight。
- [x] 明确私有提示源只引用不复制。
- [x] 明确安装、更新、卸载、rollback 的 managed artifact 边界。
- [x] 明确受保护卸载 `--apply` 只能删除白名单内且 hash 已验证的受管文件。
- [x] 明确验证命令和本地 main / 远端发布边界。
- [x] 明确 Comet 管理记录、阶段门禁、Monitoring 回退语义和证据留存。
- [x] 明确实施切片、文件职责图和本地集成顺序。
- [ ] 后续代码实现完成并完成 A/B 验收后归档对应 OpenSpec change。
  - 延期（2026-06-01）：本次 scaffold `--apply` 是本地工具链补齐切片；归档仍延期到当前本地集成包完成验证，并由 operator 明确选择 Project MOE GUI 已完成 change set 的 OpenSpec 归档范围。
- [x] 目标项目真实 Ready Lane 证据生成后，再允许受保护 GUI 控制。

## 19. 参考源

- `docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md`：新版可执行方案结构参考。
- `docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md`：Comet 管理记录、阶段门禁、Monitoring 回退和证据留存语义参考。
- `docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.zh-CN.md`：通用 PySide6 runtime 与跨项目 GUI 能力边界。
- `openspec/changes/refresh-project-moe-gui-plan-comet/`：上一轮 Project MOE GUI 文档事实链更新 trace。
- `openspec/changes/restructure-project-moe-gui-plan-modern/`：上一轮结构重构 trace。
- `docs_bilingual/memory/project_moe_paper_suggest_static_readiness_evidence_2026-05-24.md` 与 `.zh-CN.md`：`D:\PythonProject_paper_suggest` static-only readiness 证据。
