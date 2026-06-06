---
doc_id: multi_plan_parallel_session_orchestration_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
---

# 多方案并行会话编排实施方案

## 目的

创建本方案族的父级编排方案，用于把本文件覆盖的既有 implementation_plan 重构为更小、可认领、可并行的工作包。本文件不是 `docs_bilingual/implementation_plans/` 目录下所有方案的全局父方案。
目标执行模型如下：

- 本父方案只负责其方案族内部的阶段顺序、依赖、集成门禁和 Work-Conserving 准入、hotspot lease；
- 每个相关子 `implementation_plan` 负责一个可执行切片；
- 同一个 `implementation_plan` 同一时间只能有一个 active session claim；
- 不同方案在写入范围不冲突或已明确串行化时可以并行，即使它们不属于同一个父方案；
- 本地 `main` 写入始终串行；后续目标是由拿到 `local-main-retire` lock 的 session 合入自己的 ready branch，而不是固定主会话总控。

## 范围决策

- 层级：项目级治理，适用于 `D:/PythonProject_langgraph`。
- 复用形态：通用、可迁移的模式，后续可复制到其他仓库；但 Stage A 不修改用户级全局配置。
- 当前阶段：Stage A，只创建父级文档包。
- Stage B 类型：用户确认本父方案后，创建本方案族子 implementation_plan。
- Stage C 及以后：通过本方案族子方案实施 plan lock、routing、durable-state、context-retention、Comet runtime 和 Spec Kit 边界工作。
- 父子范围：本父方案只协调 front matter 中 `parent_plan` 指向本文件，或正文明确列为本方案族来源、拆分对象、集成对象的 implementation_plan。
- 无关方案：其他 implementation_plan 不因位于 `docs_bilingual/implementation_plans/` 目录下而自动成为本父方案的子方案；它们可以无父方案，也可以属于其他父方案。
- 新会话读取：新 session 不默认读取本文件；只有处理本文件、其子方案、任务清单、证据索引或本文件 Phase / Batch 中列出的相关方案时才需要读取。
- 远端发布：不在范围内，除非用户明确要求远端发布。

## 覆盖的来源方案

本父方案协调以下本方案族内既有方案，但不替代它们的详细内容；未列入且未声明 `parent_plan` 指向本文件的方案不受本父方案约束：

1. automatic_orchestration_routing_enforcement_plan - 定义自动协同路由、activation trace、expert 生命周期证据和 durable-team 阈值。
2. codex_user_level_context_retention_canary_plan - 保护冷启动上下文保留、canary 字面量位置、乱码检测和 replay 过滤。
3. codex_user_level_cross_session_durable_state_isolation_plan - 隔离 repo-local durable state、selector、backend readiness 和跨 session durable artifact。
4. comet_runtime_agile_focus_area_plan - 增加 Comet management record、阶段勾选门禁和 Monitoring 回退 transition。
5. implementation_plan_confirmation_gate - 要求非文档实现开始前必须有已提交的 active implementation-plan 文件；这里的 confirmation gate 指阻塞检查点，必须等用户确认已提交的方案文件后才能继续执行。
6. codex_governance_session_visibility_and_plan_lock_plan - 增加中文 routing trace 可视化、主会话提权可视化、Superpowers 证据、Spec Kit 边界和 plan lock。
7. pi_plugin_codex_user_level_sidecar_plan - 提供 Pi family、Codex -> Pi sidecar 与 oh-my-pi reference-only 边界。
8. user_level_mcp_skills_browser_cli_governance_plan - MCP、skills、browser、OpenCLI 与 CLI harness governance 的 source-to-decompose；其 lane 会被提取到分阶段子方案，而不是作为单一直接子方案挂入父方案。
9. prompt_canary_canonical_visible_marker_restore_plan - Restores the startup-summary-defined canonical visible canary to the operator-confirmed non-ASCII marker pair and blocks marker copies from model-readable session context.

## 非目标

- Stage A 不实现 runtime、checker、helper 或测试变更。
- Stage A 不一次性创建所有子 implementation_plan。
- 不安装 GitHub Spec Kit，也不运行 `specify init`。
- 不为本文档包启动 OMX、LangGraph 或持久化团队。
- 不允许多个 session 同时写同一个子 implementation_plan。
- 不把本文件作为所有新 session 的冷启动必读文件。
- 不把本文件作为无关 implementation_plan 的全局父方案或运行时控制面。
- 除非用户明确要求远端发布，否则不推送 GitLab 或 GitHub。

## 当前状态

<!-- CURRENT_STATUS_START -->
Stage: Stage C runtime promotion governance 已针对三个重建 lane implemented-local；validation 与 local-main integration 是当前 gate。
Owner session: main Codex leader 拥有本 Stage C package 的 serialized shared hotspots：parent plan、child plans、stable spec、checker/test updates、docs registry references、CI manifest references、safety registry references 与 OpenSpec guard wiring。
Current gate: 运行 focused runtime-promotion checker tests、precommit/archive review、OpenSpec guard、shared local gate 与 local MR review；之后通过 local-main-first helper 合入，并停在 remote-publication approval gate。
Runtime promotion result: CLI-Anything/WXWork_CLI、Browser/CLI adapters 与 Codex harnesses 现在共享明确的 R0 project-level preflight、R1 project-level fake/dry-run runtime、R2 reusable project-level helper/guard、R3 user-level install/update receipt、R4 user-level smoke runtime、R5 active-candidate / bounded live handoff gates。本包不 install、start、enable、smoke-run 或 live-run 任何 runtime。
MCP/skills CLI carry-forward: `user_level_mcp_skills_discovery_facade_plan` is a deleted/superseded source plan, not an active child plan. Runtime ownership is now `user_level_mcp_skills_cli_runtime_plan`; existing `skills2cli` and `mcp2cli` helpers/checkers/tests are R0-R2 carry-forward surfaces only until R3/R4/R5 receipts are produced. The upstream runtime source remains `knowsuchagency/mcp2cli`, with install markers `uvx mcp2cli --help`, `uv tool install mcp2cli`, and `npx skills add knowsuchagency/mcp2cli --skill mcp2cli`.
Remote state: 本 implementation package 不授权 remote publication。
Canary position follow-up: Stage A records first-visible start and last-visible end for complete user-visible assistant responses; runtime/checker work follows in Stage B.
<!-- CURRENT_STATUS_END -->

## 执行模型

### 层级架构图

本方案采用本方案族内部的二层级 implementation-plan 结构。只有 front matter 中 `parent_plan` 指向本父方案，或正文明确列入本方案族的 implementation plans，才是本父方案的同级子方案；`parent_parallel_orchestration_index_plan` 是索引维护子方案，不是二级父方案。无关 implementation_plan 可以没有父方案，也可以属于其他父方案。

```text
一级：父方案 / 总地图
└─ multi_plan_parallel_session_orchestration_plan.zh-CN.md
   ├─ Phase 0 / Batch 1 子方案：plan_inventory_registry_alignment_plan.zh-CN.md
   ├─ Phase 0 / Batch 1 子方案：parent_parallel_orchestration_index_plan.zh-CN.md
   │  └─ 说明：这是索引维护子方案，不拥有下级 implementation_plan 文件。
   ├─ Phase 1A / Batch 1 子方案：complete_local_commit_flow_scheduler_reorder_buffer_plan.zh-CN.md
   ├─ Phase 1-6 子方案：其他同级 child implementation plans
   |-- Phase 2 follow-up child: prompt_canary_canonical_visible_marker_restore_plan.md
   ├─ Phase 7 / Batch 5 子方案：parallel_plan_docs_registry_integration_plan.zh-CN.md
   ├─ Phase 7 / Batch 5 子方案：parallel_plan_checker_ci_integration_plan.zh-CN.md
   └─ Phase 7 / Batch 5 子方案：parallel_plan_openspec_comet_archive_plan.zh-CN.md
```

本层级图只适用于本方案族，不代表 `docs_bilingual/implementation_plans/` 目录下所有 implementation_plan 的全局层级。

`Phase`、`Stage`、`Batch` 用于表示本方案族内部的工作主题、生命周期状态和创建/集成批次，不是全目录文档树层级。`parent_plan` 是可选关系，不是目录强制字段；如果某方案声明 `parent_plan` 指向本文件，则它受本文件的 Phase / Batch / 并行度 / 热点文件规则约束；如果某方案没有 `parent_plan`，或 `parent_plan` 指向其他文件，则不受本文件父子结构约束。

### Session 与 Claim 规则

- 每个 implementation_plan 是最小认领单元；本方案族子方案遵循本文件的阶段和批次规则，无关方案只遵循自己的方案或全局 checker。
- session claim 必须在写入开始前声明 implementation_plan 路径。
- 同一个 implementation_plan 同一时间只能有一个 active claim。
- 多个 session 只要认领不同 implementation_plan，且写入范围不冲突或已明确串行化，就可以并行；这些方案不必属于同一个父方案。
- `docs_bilingual/docs_registry.yaml`、CI manifest、共享 checker、`comet-state.sh`、`comet-guard.sh` 和父方案文件等热点文件必须有明确 owner。
- 每个 session 自己负责自己认领的 implementation_plan、worktree、branch、claim、receipt、ROB entry、本地提交和本地 `main` 合入。
- 本父方案不代表某个主 session 对其他 session 的运行时控制权。
- 本地 `main` 写入必须串行；后续目标是通过 `local-main-retire` lock 保护每次合入，拿到锁的 session 只合入自己已 ready 的候选包。

### Work-Conserving 会话准入

- 不再把固定 Phase 数量 cap 写成治理硬上限。
- 一个 Phase 应准入每个 eligible implementation_plan/session：状态为 active、没有 active claim、依赖满足、worktree 干净，并且写集互不冲突或已取得明确 hotspot lease。
- provider pacing、CPU、内存、终端数量、失败 gate、main 落后和 retire queue 堆积属于 resource backpressure；它们只做运行时节流，不改变“所有 eligible session 都可入场”的治理原则。
- hotspot lease 和 local-main retire lock 用来串行化共享写入；它们是 lease/lock，不是全局 Phase 数量 cap。
- Phase 1A 已增加提交重排序缓冲规则：session 可以乱序完成；后续目标是把 local `main` retire 从固定 leader 串行执行改为 `local-main-retire` lock 保护的 session-owned self-retire。
- 如果子方案存在未关闭 claim、脏 worktree、失败本地门禁、未退休 ROB entry 或未合入的本地 main 集成，不得进入下一阶段。

### 同机 Peer Session 自主合入本地 main 目标模型

本小节记录同机多 session 治理目标。它是后续子方案、checker 和 helper 的治理契约；本次 Stage B 文档更新不直接实现 runtime 脚本。

#### 摘要

- 将固定“main Codex leader 控制所有 retire”的模型，改为同机 peer session 自主执行 + 本地 `main` 写入串行保护。
- 每个 session 自己负责自己的 implementation plan、worktree、feature branch、claim、task receipt、ROB entry、本地提交、本地门禁和本地 `main` 合入尝试。
- `parent_plan` 是可选元数据。只有声明时才校验；没有该字段的方案可以是独立方案，也可以属于其他父方案。
- 新 session 读取自己的目标 implementation plan、必要 registry/checker 状态、claim 状态、receipt 状态和 ROB 状态；除非处理本文件或本文件治理的方案，否则不读取本父方案。
- 范围只覆盖同一台电脑、同一仓库、多 worktree/session；跨电脑远端锁不在范围内。
- 远端发布仍不自动执行，仍需用户明确请求。

#### 治理语义调整

- 任意 session 拿到 local-main retire lock 后，都可以临时成为本次 retire owner。
- retire owner 只合入自己的 ready branch，不替其他 session retire。
- 合入成功或失败后，retire owner 必须释放锁，或记录明确的 failed/stale 状态。
- 父方案文件是热点文件。session 修改父方案时，必须明确认领该父方案写入面。
- 普通 session 处理无关 implementation_plan 时，不需要读取或修改某个父方案。

#### 本地 main retire 锁契约

- 锁文件：`.omx/locks/local-main-retire.lock`
- 计划 helper：`tools/local_main_retire_lock.py`
- 计划命令：

```text
python tools/local_main_retire_lock.py acquire --root . --session-id <id> --branch <branch> --worktree <path> --entry-id <rob-entry> --ttl-minutes 120 --json
python tools/local_main_retire_lock.py release --root . --nonce <nonce> --json
python tools/local_main_retire_lock.py status --root . --json
```

锁结构目标：

```json
{
  "schema_version": 1,
  "lock_name": "local-main-retire",
  "owner_session_id": "session-a",
  "branch": "implement-x-session-a",
  "worktree": ".worktrees/implement-x-session-a",
  "entry_id": "rob-entry-id",
  "created_at": "...",
  "expires_at": "...",
  "nonce": "...",
  "status": "active"
}
```

行为要求：

- 获取锁必须使用原子创建；存在未过期 active 锁时 fail closed。
- stale 锁默认不自动抢占；必须显式使用 `--reclaim-stale`，先归档旧锁再获取新锁。
- 释放锁必须匹配锁内 `nonce`，避免一个 session 误删另一个 session 的锁。
- 锁文件属于 runtime state，不进入 Git 提交。

#### 自主 retire 本地流程目标

后续 helper 扩展目标是 `tools/complete_local_flow_to_remote_gate.py`，计划参数包括：

- `--self-retire` - 启用 session 自主合入本地 main 的 retire 模式。
- `--session-id <id>` - 记录本次 retire 尝试归属的 peer session。
- `--rob-entry-id <entry-id>` - 关联对应的提交重排序缓冲 entry。
- `--acquire-retire-lock` - 要求 helper 在合入前先获取 local-main retire lock。
- `--lock-ttl-minutes 120` - 设置锁过期窗口，用于 stale lock 报告。

固定执行顺序：

1. 确认当前 worktree 是 feature branch，不是 `main`。
2. 确认 feature worktree clean。
3. 运行 feature local gate。
4. 运行 local MR review。
5. 对 `--self-retire` 执行 ROB entry 前置硬门：entry 必须存在、`state=ready`、session/branch/implementation plan 匹配，且 `precommit_update_archive`、`local_gate`、`local_mr_review` 均为 `passed`。; gate condition: these fields prove the package is eligible before local-main mutation.
6. 获取 `local-main-retire.lock`。
7. 拿到锁后重新确认 primary root clean 且位于本地 `main`。
8. fetch 并确认本地 `main` 不落后 `gitlab/main`。
9. 运行 claim / receipt / ROB checker。
10. 创建 rollback backup ref。
11. 执行 `git merge --ff-only <feature-branch>`。
12. 运行 post-merge local gate。
13. 将 ROB entry 更新为 `retired`，记录 lock nonce、rollback ref、local main commit 和 evidence。
14. 释放 retire lock。
15. 停在远端发布门。

#### Checker 与 Gate 目标

- `check_implementation_plan_claim_lock.py`：保留同一方案单 active claim 规则；不要求必须存在 `parent_plan`。
- `check_worktree_task_receipt.py`：receipt 记录 session 自己负责的 plan、branch、worktree 和 lifecycle；不要求父方案。
- `check_commit_reorder_buffer.py`：新增 ROB 字段 `retire_mode`，用于说明本地 main retire 由谁负责；`legacy_leader_serial` 表示旧的固定 leader 串行合入路径，`self_retire_lock` 表示拿到 retire lock 的 peer session 合入自己的 branch。当 `self_retire_lock` entry 为 retired 时，要求 `retire_owner_session_id`、`retire_lock_nonce`、`rollback_ref`、`local_main_commit` 与非空 evidence。
- 新增 `check_local_main_retire_lock.py`：校验锁 JSON schema、active lock 唯一性和 stale lock 报告。
- 只有对应 runtime helper 存在后，才把新 checker 接入 OpenSpec guard 与 local gate。

#### 后续实现验证目标

- 两个 session 同时获取 `local-main-retire.lock`：第一个成功，第二个 fail closed。
- 使用错误 nonce release：不得释放锁。
- stale 锁默认不能抢占；使用 `--reclaim-stale` 后归档 stale 锁并获取新锁。
- 没有 `parent_plan` 的 implementation plan：通过校验。
- 声明了 `parent_plan` 但路径不存在：checker 失败。
- 两个 active claim 指向同一个 implementation plan：checker 失败。
- 两个 active claim 指向不同 implementation plan：checker 通过。
- `self_retire_lock` 模式的 retired ROB entry 缺少 lock nonce：checker 失败。
- `complete_local_flow_to_remote_gate.py --self-retire --execute` 在获取锁、创建 rollback ref 或合入前先执行 ROB entry 前置硬门。
- 缺少 ROB entry、entry 非 ready、session/branch/implementation plan 不匹配或必要 gate 未通过时，不得 acquire lock，不得创建 rollback ref，不得 merge。
- `complete_local_flow_to_remote_gate.py --self-retire --execute` 在前置硬门通过后获取锁、合入后释放锁。
- 合入失败时必须释放锁或记录明确 failed/stale 状态，不能静默遗留 active lock。
- local-main 合入流程不得 push GitLab、不得创建 MR、不得同步 GitHub。

#### 假设

- 本阶段只支持同机多 session / 多 worktree 协调。
- 每个 session 只 retire 自己的 feature branch。
- 去掉固定主会话总控，不等于去掉本地 `main` 写入串行保护。
- 远端发布仍是用户明确授权步骤。


## Phase 2 Follow-up: Canonical Visible Canary Restore

| Phase 2 follow-up | `prompt_canary_canonical_visible_marker_restore_plan` | response-position follow-up planned | Restored startup-summary-defined visible canary semantics; next package hardens first-visible start and last-visible end in complete user-visible assistant responses. |

This follow-up is a serialized hotspot package. It touches startup summaries, `AGENTS.md`, canary checkers, session replay filtering, tests, and the stable canary OpenSpec spec, so it must not run in parallel with other canary-surface writer sessions.

## MCP / Skills / Browser / CLI 提取模型

`user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md` 被视为 source-to-decompose，而不是一个直接子 implementation plan。它的 lane 会重组为分阶段子方案，以便在写集安全时按多阶段、多会话执行。

| 来源切片 | 提取后的子方案 | 父方案阶段 | 并行规则 | Hotspot |
| --- | --- | --- | --- | --- |
| Slice 7 及敏感门禁 | `user_level_capability_receipt_rollback_redaction_plan` | Phase 1 | 未编辑共享 receipt helper 前，可与 port/discovery 工作并行。 | receipt helper、redaction schema、rollback evidence |
| Slice 3-4 及 OpenCLI lease | `user_level_port_browser_owner_isolation_plan` | Phase 3 | port 与 browser-owner 文件互斥时，可与 receipt/discovery 工作并行。 | port registry、browser owner registry、cleanup rules |
| Slice 1-2 | `user_level_mcp_skills_discovery_facade_plan` | Phase 4 | 低风险 discovery 可并行；sensitive call 等待 receipt evidence。 | skills facade、MCP facade、risk profile fixtures |
| Slice 5-6 | `user_level_browser_cli_adapter_boundary_plan` | Phase 6 | adapter lane 仅在写集互斥且不执行 live sensitive action 时可并行。 | adapter guard、browser/GUI authorization、WeCom guard |
| Slice 8 | 既有 Phase 7 集成方案 | Phase 7 | evidence collection 可并行；registry、OpenSpec 与 local-main retire 保持串行。 | docs registry、stable specs、CI manifest、local-main lock |

旧来源方案继续保留 baseline marker 和 implementation-state 历史，供 `check_user_level_mcp_skills_browser_cli_baseline.py` 使用。未来 runtime 实现必须认领拥有对应 lane 的提取后子方案。

## Real Runtime Gap Ledger

| Lane | Active runtime owner plan | Current implemented level | Missing real runtime layer |
| --- | --- | --- | --- |
| Codex harnesses | `codex_harnesses_governance_plan` | governance/checker/test, R0-R2 | Pi/oh-my-pi sidecar, harness job runtime, executable read/write guards, R3/R4/R5 receipts |
| Browser/CLI adapters | `user_level_browser_cli_adapter_boundary_plan` | adapter guard/checker/test, R0-R2 | install/start/probe chrome-devtools-mcp, cdp-bridge-mcp, OpenCLI; R4 smoke and R5 live handoff |
| CLI-Anything/WXWork_CLI | `user_level_cli_anything_wxwork_cli_governance_plan` | CLI-Anything/WXWork_CLI guard/checker/test, R0-R2 | install/run CLI-Anything, fork/adapt/run WXWork_CLI, control WXWork.exe, R4 smoke, R5 send/action handoff |
| Durable smoke/adoption | `durable_smoke_adoption_gate_template_plan` | template/checker/fixture, R0-R2 | real durable smoke runner, apply-mode adoption, live adoption execution receipts |
| Receipt/rollback/redaction | `user_level_capability_receipt_rollback_redaction_plan` | governance helper/checker/test, R0-R2 | install/update/smoke/live receipt writer extensions and rollback executor receipts |
| Selector ownership | `repo_local_selector_ownership_plan` | selector ownership checker/guard plus R4 `smoke-tested` helper/receipt | R5 active adoption handoff remains gated behind current operator authorization and backend-family ownership evidence |
| Worktree receipt/claim lifecycle | `worktree_receipt_claim_lifecycle_plan` | lifecycle validation/checker, R0-R2 | active -> ready -> merged-local-main -> completed -> cleaned state advancement helper |
| Capability readiness projection | `durable_capability_readiness_projection_plan` | readiness checker/fixture, R0-R2 | runtime probe/refresh of installed/enabled/selected/ready projections |
| LangGraph state release | `langgraph_state_release_evidence_plan` | state-release checker/fixture, R0-R2 | LangGraph thread close/release/handoff runtime helper and receipts |
| MCP/skills CLI | `user_level_mcp_skills_cli_runtime_plan` | existing mcp2cli/skills2cli helper/checker/test carry-forward, R0-R2 | real user-level mcp2cli install, skills2cli install/update, R4 wrapper smoke, R5 direct MCP/skill handoff receipts |

## Runtime Promotion Ladder Matrix

本次包只更新 runtime promotion ladder 的治理、checker、测试与稳定 OpenSpec 要求；本包不安装、不启动、不启用、不执行 smoke，也不 live-run CLI-Anything、WXWork_CLI、browser adapter、Pi、oh-my-pi 或任何 harness runtime。

| Runtime stage | 治理层级 | 含义 | 并行/session 规则 | 进入下一阶段前证据 |
| --- | --- | --- | --- | --- |
| R0 project-level preflight | 项目级 | 非变异 source、环境、路径、风险与 lane-readiness 盘点。 | 每个 implementation_plan 同一时间一个 session；父方案、docs registry、CI manifest、safety registry、稳定 OpenSpec 是串行 hotspot。 | source URLs、source pin plan、retrieved_at、no install/run evidence、已脱敏 preflight transcript。 |
| R1 project-level fake/dry-run runtime | 项目级 | 用 deterministic fixture 或 dry-run 证明 guard 行为，不产生真实 GUI/browser/Pi 副作用。 | lane session 只有在测试/checker 写入集不重叠时并行；共享 fixture schema 需要 lease。 | dry-run/fake receipt、no live process/browser/Pi mutation、focused tests。 |
| R2 reusable project-level helper/guard | 可复用项目级 | repo-local helper/guard pattern 可被其他项目复用，但仍不是用户级全局安装。 | helper/checker ownership 归所属 child implementation_plan；共享 receipt/redaction primitives 串行。 | reusable schema、redaction contract、rollback model、local gate、changed-path report。 |
| R3 user-level install/update receipt | 用户级 | 只有具备显式授权、immutable pin、install/update receipt、smoke command、updater command、rollback pointer、owner lane evidence 后，才可记录 installed-user-level。 | 用户级 install/update path 是全局 hotspot，需要显式 operator authorization 且同时只有一个 installer session。 | installed-user-level receipt、source pin、path hashes、smoke plan、update plan、rollback pointer、无 raw secret/private path output。 |
| R4 user-level smoke runtime | 用户级 | smoke-tested runtime 只证明已安装 wrapper 可以响应安全 help/status/read-only probe。 | smoke run 需要所属 child plan claim；适用时还要 owner/global lease。 | smoke-tested receipt、bounded command transcript、timeout release、redaction evidence、rollback readiness。 |
| R5 active-candidate / bounded live handoff | 用户级 active-candidate | 只有 R4 之后，且有当前 operator authorization、owner/global lease、target/action allowlist、expiry、timeout release、rollback 与 redaction evidence，才可 one-task live handoff。 | 同一 target 的 live handoff 不得并行；target owner/global lease 串行化。 | active-candidate receipt、lease id、authorization receipt、action scope、rollback pointer、changed-path 或 action report、post-run cleanup evidence。 |

Lane-specific R5 约束：

- CLI-Anything/WXWork_CLI：WXWork_CLI 的 send action allowed only at R5；必须有 global WXWork lease、explicit operator authorization、target/action allowlist、message redaction、ephemeral message handling、timeout release 与 rollback/stop evidence。更早阶段保持 no-send 与 no-message-content。
- Browser/CLI adapters：chrome-devtools-mcp、CDP Bridge 与 OpenCLI 的 sensitive actions 必须有 owner lease + authorization receipt；R4 只允许 help/status/read-only smoke，R5 才是 one-task bounded live handoff。
- Codex harnesses：Pi/oh-my-pi 只能作为 sidecar active-candidate；不得替代 Codex、native subagents、native_omx、LangGraph、codex-ohmy、apply_patch 或 local-main-first gates。

状态标记是累积且精确的：R3 记录 `installed-user-level`，R4 记录 `smoke-tested`，R5 记录 `active-candidate`。缺少对应 marker evidence 的 lane 必须停留在该 runtime stage 以下。

## 阶段与子方案拆分

### Phase 0：盘点与父级编排

目的：建立父级执行地图并确认 registry 健康状态。

候选子方案：

1. `plan_inventory_registry_alignment_plan` - 盘点当前方案状态、registry、锚点和 evidence index 健康度。
2. `parent_parallel_orchestration_index_plan` - 维护父级阶段图、子方案登记表和依赖表。

条件后续：只有当 inventory 子方案发现 canary registry、双语配对、锚点或 evidence index 存在真实缺陷时，才创建 canary registry recovery 子方案。

准入规则：本父方案确认后，所有 eligible session 均可并行；registry 与层级维护热点同一时间只能有一个 hotspot lease owner。

### Phase 1：施工安全底座

目的：在 runtime-heavy 工作开始前，先让并行执行安全。用户级安装和更新通道，包括 Pi family 或 harness 通道，必须先满足 receipt-first，才能被视为 active runtime surface。

候选子方案：

1. `complete_local_commit_flow_scheduler_reorder_buffer_plan` - Phase 1A 早期安全底座，定义 ROB 风格多 session 执行、热点 fence、ready queue 和 local main 串行 retire；后续消费者将把 retire 从固定 leader 模型推进到 `local-main-retire` lock 保护的 session self-retire。
2. `formal_plan_confirmation_gate_runtime_plan` - 强制“仅对话确认 plan 不足以进入实现”。
3. `portable_implementation_plan_claim_lock_plan` - 实现不依赖 OMX 或 LangGraph 的子方案单 active session 锁。
4. `implementation_plan_registry_active_state_plan` - 强制 active 状态、双语配对和 docs registry 一致。
5. `main_session_escalation_visibility_plan` - 增加主会话可见的待授权和提权预检表面。
6. `user_level_capability_receipt_rollback_redaction_plan` - 在任何 MCP/browser/CLI lane 成为 active runtime 前，提取 authorization receipt、update receipt、rollback pointer 与 redaction gate。

准入规则：所有 eligible 子方案均可并行；`docs_bilingual/docs_registry.yaml` 每批只能由一个 hotspot lease owner 写入。

### Phase 2：上下文与 UTF-8 安全

目的：在更重的 orchestration 自动化之前，稳定冷启动、replay 和乱码边界。

候选子方案：

1. `context_retention_canary_literal_boundary_plan` - 将 canary 字面量限制在 startup summary。
2. `startup_mojibake_utf8_recovery_plan` - 加固乱码检测与 UTF-8 canonical recovery。
3. `session_replay_context_filtering_plan` - 过滤 assistant/session replay 表面，避免 stale canary 或乱码重新进入 prompt。
4. `launcher_payload_context_boundary_plan` - 保持 launcher payload 边界，本阶段不修改用户级配置。

准入规则：所有 eligible 子方案均可并行；startup summary 文件必须取得 hotspot lease 并串行写入。

### Phase 3：Durable State 与跨 Session 隔离

目的：确保 durable-state 选择和检查在跨仓库、worktree、session 时安全。Pi/harness state、receipt、rollback pointer 与 sidecar artifact 不得跨 repository、worktree 或 session 泄漏。

候选子方案：

1. `repo_local_selector_ownership_plan` - 强制 repository-local active selector 归属。
2. `durable_capability_readiness_projection_plan` - 区分 installed、enabled、selected 和 ready。
3. `durable_smoke_adoption_gate_template_plan` - 在 live durable smoke 或 apply-mode adoption 前创建 gate template 和字段 checker。
4. `legacy_durable_residue_classification_plan` - 对陈旧 `.omx/state` residue 分类，但不自动接管。
5. `worktree_receipt_claim_lifecycle_plan` - 定义 active、paused、completed、stale 和 cleaned claim/receipt 生命周期。
6. `portable_no_backend_parallel_session_plan` - 在没有 OMX 和 LangGraph 时支持 Git/Python-only 并行 session。
7. `user_level_port_browser_owner_isolation_plan` - 提取 `codex-port`、port lease、`pending_bind`、`registry_revision` 与 browser owner isolation。

准入规则：所有 eligible 子方案均可并行；`.omx/state` 写入按仓库和 worktree hotspot lease 串行化。

### Phase 4：自动路由与稳定会话表面

目的：让协同路由自动、可审计，并锁定操作者确认的三类会话表面边界。`Routing trace` 保持普通文本诊断行，使用固定标签加 `key=value` 字段；`Updated Plan` 保持用户可见进度面板，统一由 CLI/tree 风格的 `✔` 与 `□` 状态标记呈现；Markdown checkbox 语法只继续用于 implementation plan 文件内部任务追踪，不再作为用户可见 `Updated Plan` 表面。Routing 与 evidence 记录必须区分 Pi/harness sidecar evidence 和由当前 owner session 负责的最终 verification evidence；保存版结构化 evidence 可继续保留 ASCII 阈值、blocker token、schema key、文件名和命令参数。

候选子方案：

1. `chinese_routing_trace_conversation_surface_plan` - 要求用户可见的 `Routing trace` 与 `Updated Plan` 标签保持稳定，允许中文解释内容，保持 `Routing trace` 为普通文本 `key=value` 诊断行，保持 `Updated Plan` 为树状 `✔`/`□` 进度面板，并把 Markdown checkbox 仅留给 implementation plan 内部任务追踪。
2. `routing_trace_structured_evidence_schema_plan` - 为保存版证据保留机器可读 ASCII 阈值和 blocker token，同时记录结构化 trace evidence/checker 数据并不是 Codex CLI 进度面板 API。
3. `prompt_independent_activation_parity_plan` - 确保路由不依赖用户是否说出“并行”或“专家”。
4. `expert_lifecycle_timeout_pacing_evidence_plan` - 将 timeout、stall 和 pacing 视为非证据，并要求有界处理。
5. `langgraph_state_release_evidence_plan` - 拒绝 LangGraph 工作完成后仍保留 stale `running` 状态。
6. `role_routing_fanout_write_ownership_plan` - 强制最小充分角色选择和 fan-out 写入归属。
7. `collaboration_evidenceguard_and_bilingual_openspec_surface_plan` - 让 evidenceguard、fixtures、CI 注册和双语 OpenSpec stable spec surface 由一个 owner 串行处理。
8. `user_level_mcp_skills_discovery_facade_plan` - 提取 compact `skills2cli` 与 `mcp2cli` discovery/risk-gated call surface，默认不加载完整 skill bodies。

准入规则：所有 eligible 子方案均可并行；共享 routing checker 和 OpenSpec spec surface 必须通过 hotspot lease 串行化。

### Phase 5：Comet Runtime 敏捷管理循环

目的：在安全与可视化基础稳定后，实现 Comet runtime 管理循环。

候选子方案：

1. `comet_management_record_bootstrap_plan` - 创建并验证 management record。
2. `comet_phase_checklist_gate_plan` - 前进 transition 前要求阶段勾选证据。
3. `comet_monitoring_return_transition_plan` - 支持 Monitoring 决策回退到 Open、Design、Build 或 Verify。
4. `comet_superpowers_visibility_plan` - 让 Comet 阶段显式展示 Superpowers HOW-layer skill 使用。
5. `comet_runtime_policy_checker_alignment_plan` - 对齐 policy、OpenSpec specs、checker 覆盖和集成门禁。

准入规则：所有 eligible 子方案均可并行。`comet-state.sh` 和 `comet-guard.sh` 同一时间只能有一个 hotspot lease owner。

### Phase 6：Spec Kit 边界

目的：防止 GitHub Spec Kit 成为竞争性治理层。同样的 subordinate-adapter 规则也适用于 oh-my-pi、Pi sidecar 与 CLI harness 引用：它们只能是 reference 或 adapter surface，不是项目治理层。

候选子方案：

1. `spec_kit_subordinate_adapter_governance_plan` - 将 Spec Kit 文档化为可选从属 adapter 或模板来源。
2. `spec_kit_authority_guard_plan` - 没有单独 active plan 时阻止 `specify init --force`、`.specify/` 或治理权威迁移。
3. `user_level_browser_cli_adapter_boundary_plan` - 将 chrome-devtools-mcp、CDP Bridge、OpenCLI、CLI-Anything 与 `wecom-cli` 等 browser/CLI harness adapter 提取为 subordinate/on-demand surface。

准入规则：写集互不冲突或已取得 hotspot lease 的所有 eligible 子方案均可并行。

### Phase 7：集成、验证与归档

目的：把并行工作收敛为串行本地 main 包，并在适用时归档已完成 OpenSpec 工作。集成报告必须在考虑任何 runtime 或用户级变更前声明每个 Pi/harness lane 的状态：`reference-only`、`planned`、`on-demand` 或 `active-candidate`。

候选子方案：

1. `parallel_plan_docs_registry_integration_plan` - 验证 docs registry、双语配对、implementation-plan rules，以及新提取 MCP/skills/browser/CLI 子方案登记。
2. `parallel_plan_checker_ci_integration_plan` - 验证 checker、unit、local CI 覆盖，以及 MCP baseline/receipt/browser/adapter guard 注册。
3. `parallel_plan_openspec_comet_archive_plan` - 验证 OpenSpec/Comet guard 健康，记录来源方案提取，并仅在 stable spec 与 deferral 同步后归档已完成变更。

延后后续：publication readiness 不作为 Stage B 子方案创建，因为远端发布不在本次范围内，除非用户明确批准。

准入规则：所有 eligible 验证 session 都可以并行准备证据，但 Phase 7 集成热点和每次 local-main retire 必须通过 lease/lock 串行化。
## 紧凑子方案状态索引

<!-- CHILD_PLAN_STATUS_INDEX_START -->
| Phase | 子方案 | 状态 | 当前证据 |
| --- | --- | --- | --- |
| Phase 0 | `plan_inventory_registry_alignment_plan` | 功能分支内已收口，等待本地合入 | `docs_bilingual/implementation_evidence/phase0_plan_inventory_registry_alignment_20260530.json`；未发现缺失登记路径或缺失双语 companion 路径。 |
| Phase 0 | `parent_parallel_orchestration_index_plan` | 功能分支内已收口，等待本地合入 | 父方案当前状态、Phase 0/Phase 1 证据、依赖说明和 Phase 2 准入文本已通过稳定锚点更新。 |
| Phase 1 | `formal_plan_confirmation_gate_runtime_plan` | 已实现并合入 | Phase 1 收口证据保留在本地 git 历史和现有证据索引中。 |
| Phase 1 | `portable_implementation_plan_claim_lock_plan` | 已实现并合入 | Portable claim lock 已作为单方案单会话归属的基础能力。 |
| Phase 1 | `implementation_plan_registry_active_state_plan` | 已实现并合入 | Registry active-state 与双语配对门禁由 implementation-plan rules 覆盖。 |
| Phase 1 | `main_session_escalation_visibility_plan` | 已实现并合入 | 主会话提权可视化已属于 Phase 1 收口包。 |
| Phase 1A | `complete_local_commit_flow_scheduler_reorder_buffer_plan` | ROB retire preflight hard gate implemented and locally integrated | Governance package `a259d91` and runtime hard gate `7087b31` verify self-retire ROB metadata before lock acquisition, rollback ref creation, or merge. |
| Phase 2 | `session_replay_context_filtering_plan` | implemented and locally integrated | Legacy session replay context filtering entered local `main` at `cbc73c7`. |
| Phase 2 | `context_retention_canary_literal_boundary_plan` | implemented and locally integrated | Context-retention canary literal-boundary checking entered local `main` at `b779d51`. |
| Phase 2 | `launcher_payload_context_boundary_plan` | implemented and locally integrated | Launcher payload file-backed boundary hardening entered local `main` at `6f1ef48`. |
| Phase 2 | `startup_mojibake_utf8_recovery_plan` | implemented and locally integrated | Startup mojibake recovery source-report repair entered local `main` at `43d3ae9`. |
| Phase 2 follow-up | `prompt_canary_canonical_visible_marker_restore_plan` | implementation-complete local candidate | Restored startup-summary-defined canonical visible canary semantics, legacy ASCII classification, and replay/model-context blocking; final repository gates precede local `main` integration. |
| Phase 5 | `comet_management_record_bootstrap_plan` | implemented and locally integrated | Local `main` includes closeout commit `8b8bfd6`; management records, checklist gates, monitoring return state, safe paths, and archive evidence are covered by focused Comet runtime tests. |
| Phase 5 | `comet_runtime_policy_checker_alignment_plan` | implemented and locally integrated | Local `main` includes closeout commit `3335b67`; stable specs, policy checker, runtime tests, and CI registration are aligned. |
| Phase 5 | `comet_monitoring_return_transition_plan` | implemented and locally integrated | Local `main` includes closeout commit `05d22bd`; return transitions and monitoring blocked/needs-decision gates are verified. |
| Phase 5 | `comet_superpowers_visibility_plan` | implemented and locally integrated | Local `main` includes closeout commit `407e5eb`; Comet/OpenSpec WHAT and Superpowers HOW evidence boundaries are explicit. |
| Phase 5 | `comet_phase_checklist_gate_plan` | implemented and locally integrated | Local `main` includes closeout commit `4b6033a`; phase checklist gate regression coverage is recorded. |
| Phase 6 | `spec_kit_subordinate_adapter_governance_plan` | admissible and unclaimed | May enter Stage C after explicit child-plan confirmation; Phase 5 closeout and fixed ROB preflight gate remove the current sequential blocker. |
| Phase 6 | `spec_kit_authority_guard_plan` | admissible and unclaimed | May enter Stage C after explicit child-plan confirmation; write scopes and hotspots remain serialized by claim/lease rules. |
| Phase 1 | `user_level_capability_receipt_rollback_redaction_plan` | implemented-local | Receipt helper hotspot closed: authorization/update schemas, hash-first rollback output, explicit local-only authorized raw path evidence, redaction fail-closed tests, and Phase 6 handoff gates are in the local integration package. |
| Phase 3 | `user_level_port_browser_owner_isolation_plan` | implemented-local；已具备仓库 local-main-first 集成候选条件 | 已确认既有范围、`pending_bind`、revision、cleanup 与 sanitized-receipt 控制；CDP Bridge 和 OpenCLI consumer 现在使用 `owner_lease_ambiguous` 拒绝 owner lease 歧义。 |
| Phase 4 | `user_level_mcp_skills_discovery_facade_plan` | implemented-local | Compact `skills2cli` / `mcp2cli` discovery facade 已实现：skill discovery 摘要化/脱敏，MCP risk-profile 输出、sensitive call receipt gate、direct-MCP bridge policy evidence 与聚焦 RED/GREEN 测试均已覆盖。 |
| Phase 6 | `user_level_browser_cli_adapter_boundary_plan` | implemented-local；已具备仓库 local-main-first 集成候选条件 | Adapter boundary 子 lane 已脚本化：chrome-devtools-mcp、CDP Bridge、OpenCLI、CLI-Anything 与 `wecom-cli` 继续保持 on-demand/reference-only，并由 receipt、owner、lease、dry-run 与 no-live-runtime gates 约束。 |
<!-- CHILD_PLAN_STATUS_INDEX_END -->

## 依赖与 Phase 2 准入说明

<!-- PHASE_ADMISSION_NOTES_START -->
- Phase 0 已完成，不再作为 Phase 2 的当前阻塞门；后续 Phase 2+ session 只需确认自己的 implementation plan 为 `status: active`、没有其他 active claim、依赖满足、worktree 干净，且写集不冲突或已取得 hotspot lease。
- Phase 1 仍是后续阶段的安全底座：plan confirmation、claim locking、registry active-state checks、ROB ordering、self-retire lock 和《完整提交流程.md》必须保持可用。
- Phase 2+ 子 session 按 Work-Conserving 规则并行运行；startup summary、UTF-8/mojibake、docs registry、OpenSpec stable spec、CI manifest、checker schema 等热点文件必须由明确 owner 串行写入。
- 本地 `main` 合入不是固定 main session 总控；持有 `local-main-retire.lock` 的 session 只可自退休自己拥有且已 ready 的候选包。
- 远端发布不是 Phase 准入条件；除非用户明确要求远端发布，否则所有 session 在本地 `main` 合入后停止在远端发布门。
<!-- PHASE_ADMISSION_NOTES_END -->


## Stage B 创建规则

进入 Stage B 后，子方案按批次创建：

- Batch 1：Phase 0 和 Phase 1 子方案，并把 Phase 1A complete-flow 调度器/ROB 子方案作为早期安全底座补充。
- Batch 2：Phase 2 和 Phase 3 子方案。
- Batch 3：Phase 4 子方案。
- Batch 4：Phase 5 和 Phase 6 子方案。
- Batch 5：Phase 7 集成子方案。

每个子方案必须包含：

- YAML front matter，含 `doc_id`、`lang`、`status: active`、`doc_class: implementation_plan` 和双语 companion 元数据。
- CURRENT_STATUS 锚点记录当前阶段和检查点，TASK_BACKLOG 锚点记录复选框任务项，EVIDENCE_INDEX 锚点记录轻量 commit/report 引用；这些锚点是脚本用于局部更新的稳定 HTML 注释。
- 明确文件归属和热点文件串行说明。
- 该子方案或阶段的 Work-Conserving 准入规则、hotspot lease 要求、resource backpressure 说明和验证门禁。
- 本地验证命令和预期门禁行为。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Stage A：创建英文 ASCII 父级 implementation plan。
- [x] Stage A：创建中文对照父级 implementation plan。
- [x] Stage A：在 `docs_bilingual/docs_registry.yaml` 登记父方案。
- [x] Stage A：使用中文提交信息提交父级文档包。
- [x] Stage A：把父级文档包合入本地 `main`。
- [x] Stage A：停止并要求用户确认本父方案后再进入 Stage B 子方案创建。
- [x] Stage B：为 Phase 0 和 Phase 1 创建 Batch 1 子 implementation_plan。
- [x] Stage B：为 Phase 2 和 Phase 3 创建 Batch 2 子 implementation_plan。
- [x] Stage B：为 Phase 4 创建 Batch 3 子 implementation_plan。
- [x] Stage B：为 Phase 5 和 Phase 6 创建 Batch 4 子 implementation_plan。
- [x] Stage B：为 Phase 7 集成创建 Batch 5 子 implementation_plan。
- [x] Stage B 父方案修订：加入二层级架构图，并吸收 Pi family / oh-my-pi / CLI harness reference-only 边界到父级编排方案。
- [x] Stage C：子方案确认后，实现 portable child-plan claim lock。
- [x] Stage B Batch 1 补充：创建 Phase 1A complete-flow 调度器/ROB 子方案，并更新完整本地提交流程治理。
- [x] Stage B 父方案范围修订：收窄本文件父方案语义，明确它只约束本方案族，不控制无关 implementation_plan。
- [x] Stage B 父方案范围修订：明确 `parent_plan` 是可选局部关系，新 session 不默认读取本文件。
- [x] Stage B 父方案范围修订：结构化记录同机 peer session self-retire 目标、锁契约、checker 目标、验证目标和假设。
- [x] Stage B 父方案修订：将固定 Phase 数量 cap 替换为 Work-Conserving all-eligible session admission、hotspot lease、resource backpressure 语言和 ROB 支撑的串行 local-main retire。
- [x] Stage A 恢复：记录 self-retire runtime 来源提交存在，但当时本地 `main` 缺少 runtime 文件；非文档恢复前必须停止等待确认。
- [x] Stage B runtime 恢复：恢复 self-retire runtime helper/checker 行为，并在 `898f9d0` 合入本地 `main`。
- [x] Phase 0 收口：在 Phase 2 准入前收口 inventory registry alignment 子方案和 parent orchestration index 子方案。
- [x] 后续阶段：Phase 0 收口包已经合入本地 `main`；Phase 2 context 与 UTF-8 safety 子方案已按 Work-Conserving 模型启动，部分包已进入本地 `main`。
- [x] Phase 4 父子方案治理更新：把会话表面覆盖从 routing trace 扩展到 `Routing trace` 与 `Updated Plan`，保持这两个标签稳定，保留 `Updated Plan` 复选框/状态清单语义，并保留保存版 evidence 的机器可读 ASCII token。
- [x] Phase 4 最终收口：确认全部 Phase 4 子方案已实现、已本地验证、已合入本地 `main`，并停在远端发布门。
- [x] Phase 1A hardening：将 `--self-retire` ROB entry 校验从 post-merge metadata 记录提升为合入前硬门。
- [x] Stage B decomposition：把 MCP/skills/browser/CLI 来源 lane 提取为分阶段子 implementation_plan，而不是把旧来源方案直接挂成父方案子方案。
- [x] Stage B decomposition：更新 Phase 7 集成子方案，使其覆盖提取后 MCP lane 的 docs registry、checker/CI 与 OpenSpec/Comet archive 职责。
- [x] Stage B follow-up: create and register the Phase 2 prompt-canary canonical visible marker restore child plan before runtime/checker implementation.
- [x] Stage C runtime promotion：为 CLI-Anything/WXWork_CLI、Browser/CLI adapters 与 Codex harnesses 加入共享 R0-R5 runtime ladder，且不 install、start、enable、smoke-run 或 live-run 任何 runtime。
- [x] Stage D real-runtime classification: update ten runtime lanes, add `user_level_mcp_skills_cli_runtime_plan`, and mark all real install/start/smoke/live execution as pending future runtime work.
- [x] Stage A follow-up: record canary response-position contract in parent/child plans before runtime/checker work.
- [ ] Stage B follow-up: update startup summaries, stable spec, diagnostics, and tests to enforce first-visible start and last-visible end.
<!-- TASK_BACKLOG_END -->

## 验收标准

Stage A 验收条件：

- 英文主版父方案存在且为 ASCII-only。
- 中文对照父方案存在。
- `docs_bilingual/docs_registry.yaml` 将这对文件登记为 `doc_class: implementation_plan` 和 `status: active`。
- 父方案列出阶段、候选子方案、依赖顺序、Work-Conserving 准入、hotspot lease和热点文件串行规则。
- Stage A 使用中文提交信息。
- Stage A 合入本地 `main`。
- Stage A 不修改 runtime、checker、helper 或测试行为。
- assistant 在 Stage B 前停止并要求用户确认本父方案。

Stage B 后续确认后的验收条件：

- 子方案被创建为独立认领单元。
- 没有子方案缺少双语配对或 registry 登记。
- 每个子方案声明文件归属、Work-Conserving 准入、hotspot lease和验证门禁。
- 相关子方案未确认前，不开始非文档实现。
- Phase 1A 在后续多 session runtime 执行前先记录 scheduler/ROB 治理。
- 本父方案明确只约束本方案族；无关 implementation_plan 可以无父方案或属于其他父方案。
- 新 session 不默认读取本文件，除非处理本文件、其子方案或正文列出的相关方案。
- 后续同机多 session 目标是 session 自主负责自己的提交和本地 `main` 合入，并用 `local-main-retire` lock 保持本地 `main` 写入串行。
- `--self-retire` 缺少有效 ready ROB entry 时必须 fail before merge，不能把 ROB retire metadata 当作 post-merge best-effort。
- Phase 4 子方案必须保持已确认的会话表面分工：`Routing trace` 是固定标签加 `key=value` 字段的普通文本诊断行；`Updated Plan` 是用户可见的树状 `✔`/`□` 进度面板；Markdown `- [x]` / `- [ ]` checkbox 只保留在 implementation plan 文件内部做任务追踪。解释内容可以使用中文；内部工具名、schema key、阈值 token、blocker token、文件名和 CLI 参数可保持 ASCII。
- Stage C runtime promotion 验收：父方案与三个子方案必须要求 R0 project-level preflight、R1 project-level fake/dry-run runtime、R2 reusable project-level helper/guard、R3 `installed-user-level`、R4 `smoke-tested`、R5 `active-candidate`，同时声明本包不 install/start/enable/smoke/live-run runtime。

## 证据索引

- 2026-06-06 canary response-position Stage A package: branch `plan-hardcode-canary-response-position-20260606` records parent/child-plan first-visible start and last-visible end contract; runtime/checker work remains Stage B.
<!-- EVIDENCE_INDEX_START -->
- 2026-06-05 Stage D real-runtime classification package: branch `runtime-plan-standard-20260605` updates ten runtime lanes, creates `user_level_mcp_skills_cli_runtime_plan` as the active mcp2cli/skills2cli runtime successor, records deleted source-plan boundaries, and keeps all real install/start/smoke/live work pending future runtime implementation.
- 2026-06-05 Stage C runtime promotion package：branch `runtime-promotion-plan-20260605` 加入共享 R0-R5 runtime promotion ladder，更新三个 child plans、stable spec、checker markers 与 tests，并把实际 install/start/enable/smoke/live runtime work 留在本包之外。
- 2026-06-01 progress-surface boundary confirmation：分支 `document-progress-surface-boundary-20260601` 记录操作者确认的分工：`Routing trace` 保持普通文本 `key=value` 诊断行；`Updated Plan` 是唯一用户可见进度面板，使用树状 `✔`/`□`；Markdown checkbox 继续作为 implementation plan 内部任务追踪模式。
- 2026-05-31 ROB retire preflight implementation: 分支 `harden-rob-retire-preflight-20260531` 已新增 self-retire ROB 前置硬门、focused RED/GREEN 覆盖和 CI manifest 登记；更广本地门禁仍需在 local-main 集成前运行。
- 2026-05-31 ROB retire 前置硬门治理：发现 `--self-retire` 缺少对应 ROB entry 时，旧 helper 会在 fast-forward merge 后才因 retire metadata 报错；本次重开 Phase 1A hardening，要求 ROB entry ready 与 gate 状态在 acquire lock / rollback ref / merge 前 fail closed。
- 2026-05-31 Phase 4 最终收口：分支 `close-phase4-final-20260531` 同步父方案与全部 Phase 4 子方案状态，确认所有 Phase 4 checklist 已关闭，过期的本地集成门已替换为远端发布门，并且 Phase 5 已可准入但不代表授权远端发布。
- 2026-05-30 Phase 4 固定标签修正：分支 `implement-routing-updated-plan-fixed-labels-20260530c` 更新本父方案与 `chinese_routing_trace_conversation_surface_plan` 子方案；`Routing trace` 与 `Updated Plan` 保持英文用户可见标签，`Updated Plan` 保持复选框/状态清单语义，中文解释内容仍允许；远端发布仍未授权。
- 2026-05-30 Phase 4 会话表面治理更新：分支 `chinese-routing-updated-plan-20260530` 曾把会话表面覆盖从 routing trace 扩展到 updated plan；其中“固定标签应替换为中文标题”的旧表述已由上一条固定标签修正取代；远端发布仍未授权。
- 2026-05-30 完整提交流程对齐包：分支 `align-complete-flow-parent-plans-20260530` 由 `codex-align-complete-flow-parent-plans-20260530` 认领 `parent_parallel_orchestration_index_plan`，ROB entry `rob-align-complete-flow-parent-plans-20260530` 记录父方案族文档候选包；本包把父方案和声明 `parent_plan` 指向本文件的子方案统一对齐到《完整提交流程.md》的 session-owned self-retire、`local-main-retire.lock` 和远端发布门模型。
- 2026-05-30 Phase 0 收口包：在分支 `phase0-plan-index-closure-20260530` 收口 `plan_inventory_registry_alignment_plan` 和 `parent_parallel_orchestration_index_plan`；机器可读盘点证据为 `docs_bilingual/implementation_evidence/phase0_plan_inventory_registry_alignment_20260530.json`；在本包完成本地门禁、local MR review 并合入本地 `main` 前，Phase 2 仍保持阻塞。
- 2026-05-30 self-retire runtime 恢复：本地 `main` 已在 `898f9d0` 包含恢复后的 self-retire runtime helper/checker 包，替代早先 `b4af80f` 的待恢复说明。
- 2026-05-29 Stage A 恢复文档包：记录当时本地 `main`=`b4af80f` 尚未包含 self-retire runtime helper/checker，虽然来源提交 `867f882` 存在于 `decentralize-session-self-retire-20260529`；该问题随后已由 `898f9d0` 解决。
- 2026-05-29 父方案范围修订：结构化吸收同机多 session 自主合入治理对话，明确本文件仍是本方案族父方案，但不控制无关 implementation_plan；新增 `parent_plan` 可选局部生效、新 session 非默认读取、session-owned self-retire 与 `local-main-retire` lock 后续目标。
- 2026-05-29 Phase 1 收口：Phase 1 子方案均已实现、合入本地 `main` 并完成验证；证据提交包括 `4479593`、`e81d840`、`fb3ad75`、`54a965d` 和 `e23c40b`；ROB 合入后 local gate 已通过。
- 2026-05-29 Stage B Batch 1 补充：新增 Phase 1A complete-flow 调度器/ROB 子方案，更新 `完整提交流程.md`，并把 portable claim / receipt 子方案标为下游消费者；随后 ROB runtime/checker 包已在 `4479593` 合入本地 `main`。
- 2026-05-28 Stage C 本地集成：portable child-plan claim lock 已快进合入本地 `main`；合入后 local gate 通过；远端发布尚未授权。
- 2026-05-28 Stage C 验证：portable child-plan claim lock 在 `implement-portable-plan-claim-lock-20260528` 分支通过聚焦测试、local gate 和 local MR review；随后已按上一条记录串行合入本地 `main`。
- 2026-05-28 Stage C 进入：通过 `portable_implementation_plan_claim_lock_plan` 开始实施 portable child-plan claim lock；本轮工作在 `implement-portable-plan-claim-lock-20260528` 分支隔离完成后再合入本地 `main`。
- 2026-05-28 Stage B 父方案修订：加入二层级架构图，并从 `pi_plugin_codex_user_level_sidecar_plan` 与 `user_level_mcp_skills_browser_cli_governance_plan` 吸收 Pi family / oh-my-pi / CLI harness reference-only 边界；commit 记录在本地 git 历史中。
- 2026-05-28 Stage B 子方案创建包：创建并登记 33 个 active 子 implementation_plan 的英文主版和中文对照版；最终 commit 记录在 assistant 回复和本地 git 历史中。
- 2026-05-28 Stage A 父级方案包：已用 `ac867ff` 提交并合入本地 `main`；验证包括 `check_implementation_plan_rules.py --root . --json`、`check_precommit_update_archive.py --root . --json`、`tools/ci/local_gate.ps1 -StepTimeoutSeconds 600` 和 `tools/ci/local_mr_review.ps1`。
- 2026-05-31 Phase 5 final closeout and Phase 6 admission: local `main` includes all Phase 5 Comet runtime closeout commits (`8b8bfd6`, `3335b67`, `05d22bd`, `407e5eb`, `4b6033a`) plus ROB retire preflight hardening (`a259d91`, `7087b31`). Post-merge `tools/ci/local_gate.ps1` passed, the ROB entry retired with `self_retire_lock`, and the feature worktree was cleaned with preserved claim evidence. Phase 6 child plans are admissible next, while non-document implementation still requires explicit child-plan confirmation and serialized ownership.
- 2026-06-01 MCP/skills/browser/CLI decomposition: package id `decompose-mcp-control-plane-20260601` means this isolated documentation update; it treats `user_level_mcp_skills_browser_cli_governance_plan` as source-to-decompose, creates four extracted child plans, and updates Phase 7 integration plans. This package authorizes no user-level install, live browser start, GUI automation, sensitive MCP call, or remote publication.
- 2026-06-01 receipt/rollback/redaction implementation: branch `implement-capability-receipt-rollback-redaction-20260601` implements the Phase 1 extracted receipt lane by closing the `tools/user_level_receipt_governance.py` hotspot, adding explicit local-only authorized raw path evidence, keeping default output hash-first, extending focused regression coverage, updating Phase 7 handoff evidence, and keeping remote publication behind the explicit approval gate.
- 2026-06-01 port/browser-owner isolation implementation: 分支 `implement-port-browser-owner-isolation-20260601` 确认既有 `codex-port` 范围顺序、`pending_bind`、单调 registry revision、owner class 隔离、cleanup 保护、sanitized receipt 与 OpenCLI `--port auto` 控制；向 CDP Bridge 和 OpenCLI consumer 增加 `owner_lease_ambiguous` fail-closed 门禁；扩展 RED/GREEN 聚焦回归覆盖；并保持远端发布在显式授权门之后。

- 2026-06-01 discovery-facade implementation: 分支 `implement-mcp-skills-discovery-facade-20260601` 实现 Phase 4 提取出的 compact `skills2cli` / `mcp2cli` lane，新增 MCP risk-profile 输出、direct-MCP/no-default-Router evidence、skill/profile 非 native-subagent 的 routing evidence 与聚焦测试；远端发布仍未授权。
- 2026-06-01 browser/CLI adapter boundary implementation: 分支 `implement-user-level-browser-cli-adapter-boundary-20260601` 关闭提取后的 Phase 6 adapter boundary lane；本包脚本化 implemented-local 子方案状态，确认 chrome-devtools-mcp/CDP Bridge/OpenCLI/CLI-Anything/`wecom-cli` 的 on-demand 或 reference-only 门禁，并保持 live browser/GUI/install/cookie/runtime mutation 不在本地包范围内。
- 2026-06-02 prompt-canary 状态对账：同步父方案中文索引与四个 Phase 2 子方案状态；本地 `main` ancestry 确认 `cbc73c7`、`b779d51`、`6f1ef48`、`43d3ae9` 均已包含；远端发布未授权。
- 2026-06-02 prompt-canary canonical restore plan package: branch `plan-restore-nonascii-canary-20260602` records a confirmed Phase 2 follow-up child plan, keeps marker literals out of non-startup plans, and requires model-readable session context to block restored canonical marker copies before implementation.


## Stage A：CLI-Anything / Browser Adapter / Codex Harnesses 拆分

2026-06-04，本父方案将原 `user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md` 与 `user_level_mcp_skills_discovery_facade_plan.zh-CN.md` 的混合内容拆成三个子方案。Stage A 只做 docs-only 方案重建与参考源登记，不安装工具、不启动 GUI/browser runtime，也不删除旧方案；旧 checker 仍在 Stage B 迁移 checker/tests/OpenSpec wiring 前读取旧方案。

| 治理 lane | 子 implementation_plan | 项目级治理 | 参考源 | 并行规则 |
| --- | --- | --- | --- | --- |
| CLI-Anything / WXWork_CLI | `user_level_cli_anything_wxwork_cli_governance_plan` | 先跑通 receipt-backed GUI control guard，再考虑用户级提升 | `https://github.com/HKUDS/CLI-Anything`；WXWork_CLI 通过 CLI-Anything 控制 `WXWork.exe` | 同一时间只能有一个 session 认领该 implementation_plan。 |
| Browser / CLI adapters | `user_level_browser_cli_adapter_boundary_plan` | 先跑通 adapter guard 与 owner/port lease，再提升 wrapper | `https://github.com/ChromeDevTools/chrome-devtools-mcp`；`https://github.com/Unagi-cq/cdp-bridge-mcp`；`https://github.com/jackwener/OpenCLI` | 范围仅限 chrome-devtools-mcp、cdp-bridge-mcp/CDP Bridge、OpenCLI；不包含 CLI-Anything/WXWork_CLI 或 harnesses。 |
| Codex harnesses | `codex_harnesses_governance_plan` | 先 fork Codex harness model，Pi/oh-my-pi 只作为参考与 sidecar runtime candidate | `https://blog.can.ac/2026/02/12/the-harness-problem`；`https://github.com/can1357/oh-my-pi`；`https://pi.dev/`；`https://pi.dev/packages` | 只有该 lane 使用 harnesses 名称，不替代 Codex、native_omx、LangGraph 或 `codex-ohmy`。 |

Stage B 迁移 checker/test/spec 后，删除 `user_level_mcp_skills_discovery_facade_plan.*` 与 `user_level_mcp_skills_browser_cli_governance_plan.*`。

- 2026-06-04 Stage B implementation: split checkers/tests/spec wiring now back three child lanes; old mixed source plans are deleted from active docs registry and filesystem; remote publication remains closed.
<!-- EVIDENCE_INDEX_END -->


Stage B harness source marker: The Harness Problem https://blog.can.ac/2026/02/12/the-harness-problem; oh-my-pi https://github.com/can1357/oh-my-pi; Pi https://pi.dev/; Pi packages https://pi.dev/packages.
