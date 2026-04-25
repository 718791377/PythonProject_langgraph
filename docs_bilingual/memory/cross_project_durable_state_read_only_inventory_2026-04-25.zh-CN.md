---
doc_id: cross_project_durable_state_read_only_inventory_2026-04-25
lang: zh-CN
canonical: docs_bilingual/memory/cross_project_durable_state_read_only_inventory_2026-04-25.zh-CN.md
translation_of: docs_bilingual/memory/cross_project_durable_state_read_only_inventory_2026-04-25.md
status: active
doc_class: memory
created_at: 2026-04-25
source_plan: docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md
---

# 跨项目 Durable State 只读盘点 - 2026-04-25

## 范围

本文是当前 durable-state isolation rollout 的 Phase 0 no-touch baseline。

已扫描的项目根目录：

- `D:\PythonProject_langgraph`
- `D:\PythonProject_OpenClaw`
- `D:\PythonProject_CLIProxyAPI`
- `D:\project`

采集规则：

- 只读扫描。
- 没有编辑、移动、重命名或删除任何 `.omx/state` 文件或目录。
- 本次盘点没有启动 durable team。
- 本文只记录结构、数量、少量安全的枚举类 JSON 字段，以及 JSON 顶层 key。
- 本文不复制 durable artifact 正文、prompt、event log、worker mailbox 或 secret。

## Baseline 摘要

| 项目根目录 | 扫描时 Git 状态 | `.omx/state` 状态 | Activation 状态 | 分类 |
| --- | --- | --- | --- | --- |
| `D:\PythonProject_langgraph` | Git worktree 位于 `docs/freeze-active-implementation-boundary`，`afdbd34cc7ee` | 存在：11 个文件、313 个目录、161330 bytes、305 个空目录 | 没有 `.omx/state/selectors/active.json`；存在 LangGraph backend record，字段显示 `backend=langgraph`、`phase=define-target`、`status=running` | preserved historical LangGraph record，加 safe empty native residue |
| `D:\PythonProject_OpenClaw` | Git worktree 位于 `main`，`947a1fa03007` | 存在：21 个文件、62 个目录、282441 bytes、52 个空目录 | 存在 active scoped selector，`backend_family=langgraph`；LangGraph backend 字段显示 `phase=freeze-plan`、`status=resumed`、`routing_posture=active_scoped_selector` | preserved active LangGraph selector / artifacts，加 safe empty native residue |
| `D:\PythonProject_CLIProxyAPI` | Git worktree 位于 `main`，`066290149602` | 存在：43 个文件、15 个目录、105601 bytes、2 个空目录 | 存在 active scoped selector，`backend_family=native_omx`；managed team record 字段显示 `phase=stabilize`、`worker_count=2`、`worker_role=debugger` | preserved active native OMX team state |
| `D:\project` | 不是 Git worktree | 存在：4 个文件、0 个目录、2986 bytes | 没有 selector、LangGraph 或 team state | 只有 protected manual / user-level OMX UI state |

## 单项目发现

### `D:\PythonProject_langgraph`

关键观察：

- `.omx/state/langgraph/backend.json` 存在；本轮应把它视为 preserved historical 或 inspectable LangGraph record。
- `.omx/state/langgraph/threads`、`checkpoints`、`history` 各有 1 个文件。
- `.omx/state/langgraph/interrupts` 与 `store` 存在，但为空目录。
- `.omx/state/selectors/active.json` 不存在。
- `.omx/state/selectors/leases` 存在，但为空。
- `.omx/state/team` 下有 300 个空的 `auto-team-*` 目录，以及一个 `.fake-counter` 文件。
- `.omx/state/team/codex-auto-managed-team.json` 不存在。

分类：

- preserved historical：LangGraph backend、thread、checkpoint、history 文件。
- safe empty：空的 `auto-team-*` 目录、空的 selector leases 目录、空的 LangGraph interrupt/store 目录。
- protected manual：`.fake-counter`；Phase 0 是 no-touch，所以本阶段不删除。

直接含义：

- 新 activation logic 不能让 preserved LangGraph backend record 自动主导无关未来会话。
- native durable routing 应能忽略空的 unmanaged `auto-team-*` residue。

### `D:\PythonProject_OpenClaw`

关键观察：

- `.omx/state/selectors/active.json` 存在，字段显示 `backend_family=langgraph`、`routing_eligible=true`、`routing_posture=active_scoped_selector`。
- `.omx/state/selectors/leases` 有 1 个 lease 文件。
- `.omx/state/langgraph/backend.json` 存在，字段显示 `backend=langgraph`、`phase=freeze-plan`、`status=resumed`、`routing_posture=active_scoped_selector`。
- LangGraph artifact 目录数量：
  - `threads`：2 个文件
  - `checkpoints`：2 个文件
  - `history`：1 个文件
  - `interrupts`：2 个文件
  - `store`：空目录
- `.omx/state/team` 下有 51 个空的 `auto-team-*` 目录，以及一个 `.fake-counter` 文件。
- `.omx/state/team/codex-auto-managed-team.json` 不存在。

分类：

- preserved active：scoped LangGraph selector、lease、backend record 与 LangGraph artifacts。
- safe empty：空的 `auto-team-*` 目录和空的 LangGraph store 目录。
- protected manual：`.fake-counter`；Phase 0 是 no-touch，所以本阶段不删除。

直接含义：

- `D:\PythonProject_OpenClaw` 不只是 historical fixture；它当前存在 active scoped LangGraph selector。未来 activation logic 必须区分 active scoped selector 与 stale unscoped residue。

### `D:\PythonProject_CLIProxyAPI`

关键观察：

- `.omx/state/selectors/active.json` 存在，字段显示 `backend_family=native_omx`、`phase=stabilize`、`routing_eligible=true`、`routing_posture=active_scoped_selector`。
- `.omx/state/selectors/leases` 有 1 个 lease 文件。
- `.omx/state/team/codex-auto-managed-team.json` 存在，字段显示 `phase=stabilize`、`team_name=diagnose-cliproxyapi-auth-file`、`worker_count=2`、`worker_role=debugger`。
- `.omx/state/team/diagnose-cliproxyapi-auth-file` 非空，并包含 team runtime 文件。
- 没有发现 `.omx/state/langgraph` backend 或 LangGraph artifact 目录。

分类：

- preserved active：scoped native OMX selector、lease、managed-team record 与非空 team runtime 目录。
- safe empty：managed team tree 内部只有嵌套的空 approvals/claims 目录。
- protected manual：非空 team runtime state；本阶段不编辑。

直接含义：

- durable-state isolation 必须保留 active native OMX team，不能把所有 `.omx/state/team` 树都当成 cleanup residue。

### `D:\project`

关键观察：

- 根目录存在，但不是 Git worktree。
- `.omx/state` 只有 4 个文件：HUD、notification、leader nudge 与 tmux hook state。
- 没有发现 `.omx/state/selectors`、`.omx/state/langgraph` 或 `.omx/state/team`。

分类：

- 只有 protected manual / user-level UI state。
- 没有发现 durable activation selector。
- 没有发现 native team 或 LangGraph durable artifact plane。

直接含义：

- 后续 helper 不能因为这个根目录存在普通 OMX UI state，就推断它已经选择了 durable backend。

## 跨项目结论

1. 四个扫描根目录不是同一种状态：
   - `D:\PythonProject_OpenClaw` 有 active scoped LangGraph state。
   - `D:\PythonProject_CLIProxyAPI` 有 active scoped native OMX team state。
   - `D:\PythonProject_langgraph` 有 preserved LangGraph records 和大量空 native residue，但没有 active selector。
   - `D:\project` 只有普通 UI / hook state。
2. 空的 native `auto-team-*` 目录在 `D:\PythonProject_langgraph` 与 `D:\PythonProject_OpenClaw` 中都存在；但 `D:\PythonProject_CLIProxyAPI` 的非空 team state 是 active，必须保留。
3. 新 routing 必须优先看 scoped selectors 与 leases，而不是让 legacy backend file 自动主导。
4. legacy 或 inspectable backend record 仍然是有价值的证据，但不能自动激活无关未来会话。
5. Phase 1 可以继续实施，而且不需要删除或重写任何 legacy `.omx/state` artifact。

## Phase 1 Contract 输入

下一阶段实现应把这些规则写入 source 和 tests：

- 空的 `auto-team-*` 目录属于 safe-empty residue，不能阻塞 native durable routing。
- 非空 managed team record 仍然是 preserved active state。
- 带 live lease 的 scoped selector 比 legacy backend record 更强。
- 普通 HUD / notification / tmux state 不是 durable backend activation 证据。
- repo-local `.omx/state` 仍然只对该仓库自己是 source of truth。

