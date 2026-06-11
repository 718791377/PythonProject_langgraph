
---
doc_id: r6_live_runtime_promotion_plan
lang: zh-CN
status: active
doc_class: implementation_plan
stage: implementation-evidence
priority_order: Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit
translation_of: docs_bilingual/implementation_plans/r6_live_runtime_promotion_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
---

# R6 真实 Live Runtime 提升方案

> **给 agentic workers：**实现本方案时使用 `superpowers:executing-plans` 或 `superpowers:subagent-driven-development`。Comet 仍是工作流控制层，OpenSpec 仍是 WHAT 权威，Superpowers 仍是 HOW 权威。

## 目标

把已列出的 R5 checker-backed active-candidate gate 提升为 R6 live-runtime promotion 层，同时保持冲突治理优先级：`Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。

R6 的含义是：live runtime 默认可被发现和路由，但任何敏感外部动作仍然必须在当前授权 receipt、owner lease、环境变量目标、rollback readiness、cleanup evidence 与脱敏 execution receipt 齐全时才执行；否则必须 fail-closed 并记录 blocked receipt。

## 范围

本方案覆盖以下既有 R5 方案：

- `user_level_capability_receipt_rollback_redaction_plan` - 约束共享授权、回滚与脱敏 receipt 基础
- `worktree_receipt_claim_lifecycle_plan` - 约束 worktree task receipt 与 claim 生命周期提升
- `repo_local_selector_ownership_plan` - 约束 repo-local selector ownership 与 adoption evidence
- `durable_capability_readiness_projection_plan` - 约束 durable backend readiness projection evidence
- `langgraph_state_release_evidence_plan` - 约束 LangGraph state release receipt evidence
- `durable_smoke_adoption_gate_template_plan` - 约束 durable smoke 与 adoption gate template
- `user_level_mcp_skills_cli_runtime_plan` - 约束用户级 MCP 与 skills CLI runtime handoff
- `user_level_browser_cli_adapter_boundary_plan` - 约束 browser/CLI adapter owner 与 live-action 边界
- `user_level_cli_anything_wxwork_cli_governance_plan` - 约束 CLI-Anything 与 WXWork CLI 敏感动作边界
- `stop_slop_caveman_response_density_runtime_plan` - 约束 response-density runtime 与 canary-safe compression activation
- `gstack_codex_delivery_loop_runtime_governance_plan` - 约束 gstack advisory delivery-loop runtime 边界
- `codex_harnesses_governance_plan` - 约束 Codex harness candidate、job 与 no-takeover evidence
- `spec_kit_authority_guard_plan` - 约束 Spec Kit authority prevention checker
- `spec_kit_subordinate_adapter_governance_plan` - 约束 Spec Kit subordinate adapter runtime 边界


## 当前状态
<!-- CURRENT_STATUS_START -->

- [x] Stage A 方案包已在提交 `5dd8592` 合入本地 `main`。
- [x] Stage B 核心 R6 checker/runtime/template 实现已通过提交 `b0d3e07`、`fc1c500`、`5866f3e`、`6393796` 和 `d3d57d0` 合入本地 `main`。
- [x] Stage B live smoke 证据已覆盖模板同步、用户级安装 smoke、Spec Kit sandbox apply、Spec Kit template apply 与 Spec Kit repository apply；所有 receipt 均保持 `remote_publication_mutated=false`。
- [x] Spec Kit repository-apply 证据包已在提交 `d3d57d0` 合入本地 `main`，对应 feature worktree/branch 已清理；远端发布仍未授权。
- [x] Stage C coverage audit 实现现在为全部 14 个 R6 lane 增加 checker/runtime 覆盖证据：repo-local/default-safe lane 在无外部副作用下 live-execute，browser/WXWork/harness/user-level-install/Spec Kit lane 在缺少环境目标时默认生成 blocked receipt。

- [x] Stage D 敏感 live-action follow-up - `live-executed` means bounded live action ran with proof，`blocked` means runtime recorded an unmet proof gate：已记录 Browser 与 Stop-Slop/Caveman 为带脱敏 receipt 的 R6 `live-executed`；WXWork 与 Codex harnesses 因缺少真实发送目标或 live harness job proof，继续 fail-closed 为 `blocked`。

- [x] Stage E proof-intake hardening 增加 `proof-template` 与 `proof-check` runtime 命令。`proof-template` 只写入真实动作后的填充骨架且不运行外部工具；`proof-check` 在既有 `run --mode live-action --proof-receipt ...` 路径把 WXWork 或 harness 证据提升为 `live-executed` 之前，先校验 proof 是否已脱敏且字段齐全。

- [x] Stage F 有界 harness live-job 证据新增 `tools/run_codex_harnesses_smoke.py r6-live-proof`，并以脱敏隔离 worktree proof 将 Codex harnesses 记录为 R6 `live-executed`。WXWork 在出现真实 message-send proof 前继续 fail-closed 为 `blocked`。


- [x] Stage G full-family R6 completion scope covers the strict `multi_plan_parallel_session_orchestration_plan` family: active children, parent-named sources, and successor-owned migration sources.
- [x] Stage H full-family checker/runtime reconciliation is implemented: current checker accepts 53 family members, 14 direct R6 lanes, 2 successor-owned migration sources, and 0 stale status findings.

<!-- CURRENT_STATUS_END -->

## 任务积压
<!-- TASK_BACKLOG_START -->

- [x] Package 1：新增双语 R6 方案并合入本地 `main`。
- [x] Package 2：实现 R6 checker/runtime/template 支持并验证受影响门禁。
- [x] Package 2：同步完整可复用模板到 `D:/PythonProject_General`，同步安全 stub 到 `D:/PythonProject_General_2`。
- [x] Package 2：执行用户级安装 smoke，以及 Spec Kit sandbox、repository、template apply 证据。
- [x] Package 2：将 repository-apply 证据包合入本地 `main`，并停在远端发布审批门禁。
- [x] Package 3：新增 R6 lane coverage audit 工具，把当前 receipt 文件与全部 14 个 lane 对齐，缺少默认可执行证据时失败。
- [x] Package 3：扩展 R6 runtime，加入默认 `run-all` 批处理模式，为每个 lane 生成一个有效 R6 receipt，且不静默执行外部副作用。
- [x] Package 3：记录全部 14 个 lane 的 Stage C receipt 证据；browser/WXWork/harness/user-level-install/Spec Kit 等外部动作在缺少环境目标时保持 blocked，blocked receipt 是当前的、已脱敏的、并通过 checker。

- [x] Package 4：运行并记录敏感 live-action follow-up 证据；接受 Browser 与 Stop-Slop/Caveman 的 live-executed proof，并在真实 proof gate 出现前保留 WXWork/Harness blocked receipts。

- [x] Package 5：为 WXWork 与 Codex harnesses 增加 fail-closed proof-intake 模板与 proof 校验，未来真实 live proof 可在不保存 raw recipient、message、browser 或 harness payload 的前提下通过门禁。

- [x] Package 6：实现并执行一个有界 repo-local Codex harness proof job；该 job 在临时隔离 Git worktree 中运行，随后 rollback/cleanup，并通过 `proof-check` 与 `run --mode live-action` 将 `codex-harnesses-governance` 提升为 R6 `live-executed`。


- [x] Package 7: update this R6 plan for strict parent-family scope, successor-owned migration sources, and full-family live-runtime classification.
- [x] Package 8: implement full-family R6 checker/runtime reconciliation, update stale plan status, validate every direct R6 lane receipt, and prepare local `main` integration.

<!-- TASK_BACKLOG_END -->

## 证据索引
<!-- EVIDENCE_INDEX_START -->

- 方案包证据：本地 `main` 提交 `5dd8592` 新增本双语 R6 implementation plan。
- Stage B 实现证据：本地 `main` 提交 `b0d3e07`、`fc1c500`、`5866f3e` 已加入 R6 runtime/checker/template 支持、OpenSpec 门禁夹具与模板源漂移修复。
- 模板与用户级 smoke 证据：忽略的本地 receipt 位于 `.omx/r6-live-runtime/receipts/`，包括 `user-level-install-smoke.json`、`spec-kit-sandbox-smoke.json`、`spec-kit-template-smoke.json`；模板同步复制 `0` 个文件，因为两个目标模板已与源表面对齐。
- Spec Kit repository apply 证据：本地 `main` 提交 `6393796` 保留 `.specify/r6-live-runtime/README.md` 与 `specs/r6-live-runtime/spec.md` 作为从属/no-takeover 的 repository-apply 表面，redacted live receipt 为 `.omx/r6-live-runtime/receipts/spec-kit-repository-smoke.json`。
- Spec Kit repository apply 稳定化证据：本地 `main` 提交 `d3d57d0` 修复 durable-routing smoke command guard，使以 `-apply` 结尾的 worktree 路径不会被误判为 apply 授权，同时真实 `--apply`/`-Apply`/`/apply` flag 仍 fail closed。
- repository-apply 包 checker 证据：本地 `main` 集成前，`python test\spec_kit_authority_guard.test.py -v`、`python tools\check_spec_kit_authority_guard.py --root . --json`、`python test\check_durable_routing_smoke_receipts.test.py -v`、完整 `tools\ci\local_gate.ps1` 与 `tools\ci\local_mr_review.ps1` 均通过。
- Stage C coverage audit 种子：当前 receipt inventory 只发现 `spec-kit-authority-guard`、`spec-kit-subordinate-adapter-governance` 与 `user-level-mcp-skills-cli-runtime` 的 live-executed receipt。其余 11 个 lane 仍缺少当前 receipt 覆盖，需等待 Package 3 落地。
- Stage C 实现证据：`tools/check_r6_live_runtime_receipts.py` 现在支持 `--receipt-dir` 与 `--require-coverage`；`tools/r6_live_runtime.py run-all` 会为每个 lane 写入一个 Stage C receipt，默认不执行 browser/GUI、外部消息、harness job、用户级安装、Spec Kit apply 或远端发布变更。
- Stage C receipt 证据：`python tools\r6_live_runtime.py run-all --root . --json` 与 `python tools\check_r6_live_runtime_receipts.py --root . --receipt-dir .omx\r6-live-runtime\receipts --require-coverage --json` 已接受全部 14 个 lane。机器可读证据：`docs_bilingual/implementation_evidence/r6_live_runtime_stage_c_coverage_evidence_20260609.json`；人工可读摘要：`docs_bilingual/implementation_evidence/r6_live_runtime_stage_c_coverage_evidence_20260609.md` 与 `docs_bilingual/implementation_evidence/r6_live_runtime_stage_c_coverage_evidence_20260609.zh-CN.md`。
- Stage C 模板同步证据：`python tools\r6_live_runtime.py sync-templates --root . --general-root D:\PythonProject_General --general2-root D:\PythonProject_General_2 --update-managed --json` 仅刷新受管模板文件，报告 `remote_publication_mutated=false`，并保持 General_2 为 stub-only 表面。
- 远端发布仍未授权；除非当前用户消息明确点名远端动作，否则不推送 GitLab/GitHub、不创建或更新远端 MR。

- Stage D 敏感 live-action follow-up 证据 - `live-executed` means bounded live action ran with proof，`blocked` means runtime recorded an unmet proof gate：`.omx/r6-live-runtime/receipts/browser-live-action-followup.json` 与 `.omx/r6-live-runtime/receipts/stop-slop-caveman-live-executed-followup.json` 是当前有效且被 `tools/check_r6_live_runtime_receipts.py --require-coverage` 选中的 `live-executed` receipt；`.omx/r6-live-runtime/receipts/wxwork-live-action-blocked-followup.json` 与 `.omx/r6-live-runtime/receipts/harness-live-action-blocked-followup.json` 因缺少真实 WXWork message-send proof 与真实 guarded harness-job proof，仍为有效 `blocked` receipt。人工可读证据：`docs_bilingual/implementation_evidence/r6_sensitive_live_action_evidence_20260609.md` 与 `.zh-CN.md`。

- Stage E proof-intake hardening 证据：`tools/r6_live_runtime.py proof-template` 是未来真实外部 proof 文件的 fail-closed 模板生成器，`tools/r6_live_runtime.py proof-check` 是该 proof 文件的脱敏与必需字段校验器。测试：`python test\r6_live_runtime.test.py -v` 通过 18/18，并覆盖已脱敏 WXWork/harness proof 的接受路径，以及 raw WXWork body 或 recipient 材料的拒绝路径。
- Stage F 有界 harness live-job 证据：`tools/run_codex_harnesses_smoke.py r6-live-proof` 现在会在临时隔离 Git worktree 中运行一个有界本地 harness job，并写入脱敏 proof。`tools/r6_live_runtime.py proof-check` 只有在 candidate id、job profile、read/write guards、isolated worktree、job state、changed-path report、timeout release、rollback、cleanup 与 no-Codex-takeover evidence 均通过时才接受该 proof。follow-up receipt `.omx/r6-live-runtime/receipts/harness-live-job-live-executed-20260609.json` 已作为 `codex-harnesses-governance` 的 R6 `live-executed` receipt 通过验证；proof hash `e0f71f0789945588`，candidate hash `47ab92541ddbb827`，`remote_publication_mutated=false`。WXWork 在出现真实外部 message-send proof 前继续保持 `blocked`。


- Stage H full-family checker evidence: `tools/check_multi_plan_family_r6_live_runtime.py` classifies the strict parent family and delegates direct-lane evidence to `tools/check_r6_live_runtime_receipts.py --require-coverage`. Current validation with receipt directory `D:\PythonProject_langgraph\.omx\r6-live-runtime\receipts` reports `ok=true`, `family_members=53`, `direct_r6_lane=14`, `successor_owned_migration_source=2`, `governance_checker_runtime=29`, `no_live_runtime_scope=8`, `stale_status_findings=0`, `restored_deleted_migration_sources=0`, and `remote_publication_mutated=false`. WXWork is accepted through `.omx/r6-live-runtime/receipts/wxwork-live-executed-20260610.json` with hash-only/redacted proof metadata.

<!-- EVIDENCE_INDEX_END -->
## R6 契约

R6 在 R5 之上增加一个提升状态：

| 阶段 | 含义 | 外部动作姿态 |
| --- | --- | --- |
| R5 active-candidate | lane 有有效 active-candidate receipt。 | 只验证，不要求外部动作。 |
| R6 live-ready | lane 可以默认进入 live runtime routing。 | 缺少授权或目标时必须产生 blocked receipt。 |
| R6 live-executed | 一个有界 live 动作实际运行。 | 必须包含脱敏 execution receipt、rollback/cleanup 证据，且不变更远端发布状态。 |

R6 live receipt 必须包含 R5 active 字段，并增加：

- `receipt_type: r6-live-runtime` - 标识该 receipt 是 R6 live-runtime 证据记录
- `live_mode: blocked | dry-run | live-ready | live-executed` - 记录 lane 是阻塞、模拟、ready 还是已真实执行
- `live_attempted: true | false` - 记录是否进入 live runtime 路径
- `live_executed: true | false` - 记录是否运行了真实有界外部动作
- `external_side_effects: none | browser_gui | external_message | harness_job | spec_kit_apply | user_level_install | mixed` - 分类外部副作用类型
- `target_env_keys` - 记录用于目标注入的环境变量名，不保存原始值
- `target_env_hash` - 记录脱敏目标材料的稳定 hash
- `execution_receipt` - 记录按 lane 脱敏的执行摘要
- `blocked_reason` - 当 `live_executed=false` 时必填，用于解释缺少哪个授权、目标或回滚条件
- `template_distribution` - 记录该 receipt 对应的分发层，取值为 `project-general-full | project-general-2-stub | repo-local-only | user-level`

除非当前用户消息明确授权远端发布，否则每个 R6 receipt 必须保持 `remote_publication_mutated=false`。

## 模板与用户级分发

### 项目级通用模板

`D:\PythonProject_General` 获得完整项目级通用支持：

- R6 checker/helper/template，供未来项目复制或 hydrate。
- 缺少环境变量目标时默认写 blocked receipt。
- 文档必须说明这些模板不会把消费项目变成本编排仓库的实现位置。

### 新电脑兼容模板

`D:\PythonProject_General_2` 只获得兼容 stub：

- stub checker/README 表面，说明 R6 能力只有从源仓库或用户级 installer 升级后才可用。
- 默认不启用 OMX、LangGraph、live harness、live browser、WXWork 或 Spec Kit apply。
- 不复制 `.omx/state/` runtime state。

### 用户级安装

用户级 wrapper/config 只能通过 receipt-backed helper 安装或更新。install/update receipt 必须包含 source path、installed path、wrapper path、smoke command、rollback pointer、owner lane、redaction status，以及 user-level state mutation 是否已授权。

## 环境变量目标注入

Live 目标必须通过环境变量传入。Receipt 只能列出变量名与 hash，不得保存敏感原始值。

规范环境变量名：

- `R6_BROWSER_TARGET_URL` - 提供 live browser smoke/action 的目标 URL
- `R6_BROWSER_ACTION` - 提供允许的 browser/GUI action 名称
- `R6_WXWORK_TARGET` - 在提交文件之外提供 WXWork 收件人或目标频道
- `R6_WXWORK_MESSAGE_TEMPLATE` - 在提交文件之外提供 WXWork 消息模板
- `R6_HARNESS_CANDIDATE_ID` - 选择 live job 的 harness candidate id
- `R6_HARNESS_JOB_PROFILE` - 选择有界 harness job profile
- `R6_SPEC_KIT_MODE` - 选择 Spec Kit apply 边界：`sandbox` 表示临时目录或隔离 worktree，`repository` 表示本仓库可写表面，`template` 表示 General/General_2 模板表面
- `R6_SPEC_KIT_TARGET_ROOT` - 在提交文件之外提供 Spec Kit live apply 目标根目录
- `R6_USER_LEVEL_INSTALL_ROOT` - 在提交文件之外提供用户级安装根目录

## 各 Lane 要求

### Capability / rollback / redaction 基础

扩展共享 receipt governance checker，使 R6 校验授权、脱敏、rollback、cleanup、target hash、用户级 mutation 授权，以及 blocked/live-executed 结果分类。

### Worktree receipt 与 selector ownership

R6 worktree 和 selector adoption 只能在已拥有的 repo-local state 路径中更新本地 runtime receipt。Adoption 必须引用当前 owner lease，且不得在没有 selector evidence 时声称 persistent-team execution。

### Durable readiness 与 LangGraph release

Durable readiness refresh 与 LangGraph release 只有在 selected backend ready 且 receipt 记录 selector authority path 时才能运行 live status/release helper。LangGraph state 仍固定在 `.omx/state/langgraph/`。

### Durable smoke adoption

Durable smoke 只有在当前 lane receipt 和明确 backend-family ownership 存在时，才能从 read-only template smoke 前进到 live adoption。Timeout 必须 clean release 或 blocked。

### MCP/skills CLI runtime

MCP 与 skills CLI wrapper 可以进行用户级安装与 smoke。直接 MCP 调用或 skill-discovery handoff 必须记录是否实际执行，并保持 agent/skill/profile 边界。

### Browser/CLI adapter

Browser 或 GUI live action 只能在 target URL/action allowlist 下运行。不得保存 raw browser data；receipt 只保存脱敏摘要与目标 hash。

### CLI-Anything / WXWork CLI

WXWork live send 只允许在 R6 且 `R6_WXWORK_TARGET` 与 `R6_WXWORK_MESSAGE_TEMPLATE` 存在时执行。Receipt 不得包含消息正文或原始收件人。缺少目标或确认时必须写 blocked receipt。`proof-template` 与 `proof-check` 提供两步 proof-intake 路径：先为发送后的 proof 创建骨架，再只验证 hash 与状态字段，最后才允许提升为 `live-executed`。

### Stop-slop / response-density runtime

Response-density runtime 只有在 rollback evidence 与 canary-preservation evidence 存在时才能安装或激活 hook。缺少证据时默认 blocked。

### gstack delivery loop

gstack 仍是 Comet/OpenSpec/Superpowers 之下的 advisory 层。可以运行 live delivery-loop smoke，但不得覆盖 Comet phase routing、OpenSpec WHAT authority、Superpowers HOW discipline、本地 main-first gate 或远端发布 gate。

### Codex harnesses

Harness live job 需要 candidate id、isolated worktree、read/write guard、no-Codex-takeover evidence、job state、changed-path report、timeout release、rollback 与 cleanup evidence。`proof-template` 与 `proof-check` 会把这些 proof 字段显式化，harness receipt 只有通过该 proof 校验后才能从 `blocked` 提升为 `live-executed`。

### Spec Kit authority 与 subordinate adapter

Spec Kit 仍低于 harness runtime safety，不能成为仓库治理权威。R6 实现三种允许的 apply 边界：

1. **Sandbox apply**：在临时目录或隔离 worktree 中运行 `specify/init/apply`，只把 receipt 写回仓库。
2. **Repository apply**：只有当 Comet/OpenSpec 显式拥有该 change 且 receipt 声明 Spec Kit 从属时，才允许本仓库出现 `.specify/` 或根目录 `specs/`。
3. **Template apply**：允许 `D:\PythonProject_General` 出现模板表面；`D:\PythonProject_General_2` 只能获得 stub。

## 实施包

### Package 1：plan-only 本地集成

- 添加本双语方案。
- 运行 pre-commit update/archive review。
- 按需运行 OpenSpec guard 与本地 gate。
- 提交并通过 local-main-first helper 合入本地 `main`。

### Package 2：R6 checker/runtime/template 实现

- 新增/扩展 R6 receipt checker 与模板。
- 新增 lane-specific runtime wrapper 或 live receipt mode。
- 新增 user-level install/smoke 支持。
- 同步 `D:\PythonProject_General` 完整表面与 `D:\PythonProject_General_2` stub。
- 添加测试与 CI manifest 条目。
- 按 lane 粒度提交，验证后合入本地 `main`，并停在远端发布审批门禁。

## 验收标准

- R6 checker 接受所有列出 lane 的有效 blocked 与 live-executed receipt。
- R6 checker 拒绝 raw secrets、raw WXWork message body、raw browser payload、缺失 owner lease、缺失 rollback、缺失 cleanup、authority-order 违规。
- 默认日常 runtime 路径在 live evidence 不完整时产生 blocked receipt，而不是静默外部动作。
- User-level install/smoke receipt 可验证，且不泄露 raw path 或 secret。
- `D:\PythonProject_General` 携带完整可复用项目级模板；`D:\PythonProject_General_2` 只携带安全 stub。
- Spec Kit sandbox、repository、template apply 边界分别存在并由 checker 支撑。
- 本地 `main` 集成前 local gate 与 local MR review 通过。

## 非目标

- 本方案不授权远端发布。
- 本方案不让 Spec Kit 替代 Comet/OpenSpec。
- 本方案不把外部目标、secret、WXWork message body 或 raw browser data 写入已提交文件。

## 2026-06-09 Stage F：Codex Harness R6 live-executed

- [x] Package 6 运行有界 repo-local Codex harness proof job：`tools/run_codex_harnesses_smoke.py r6-live-proof` 在临时隔离 Git worktree 中执行 bounded local harness job，并记录 read/write guard、isolated worktree、job state、changed-path report、timeout release、rollback、cleanup 与 no-Codex-takeover proof。
- [x] `tools/r6_live_runtime.py proof-check` 对 harness proof 强制要求 candidate id、job profile、timeout release、rollback 与 cleanup；缺失任一字段时 fail closed。
- [x] `codex-harnesses-governance` 已通过 redacted proof 提升为 R6 `live-executed`；proof hash `e0f71f0789945588`，candidate hash `47ab92541ddbb827`，`remote_publication_mutated=false`。
- [ ] `user-level-cli-anything-wxwork-cli-governance` 仍保持 `blocked`，直到出现真实 WXWork message-send proof 且不包含 raw recipient/body。


## 2026-06-11 Stage G full-family R6 scope

This zh-CN companion records the same Stage G decision as the English primary without duplicating sensitive target values. The R6 rollout now covers the strict `multi_plan_parallel_session_orchestration_plan` family, including active child plans, explicitly named migration/source plans, and successor-owned deleted migration sources.

Completion classifications are `direct-r6-lane`, `successor-owned-migration-source`, `governance-checker-runtime`, and `no-live-runtime-scope`. The implementation checker must assign exactly one classification to every family member and must preserve the priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.

External-action policy is reuse-first: existing valid `live-executed` receipts are reused, and real browser/WXWork/harness/Spec Kit/user-level install actions rerun only when checker evidence is missing, stale, invalid, or blocked and current authorization/target proof exists. Receipts remain hash-only/redacted and must keep `remote_publication_mutated=false`.

Package 8 now adds `tools/check_multi_plan_family_r6_live_runtime.py`, focused tests, stale-status detection, successor-owned migration-source handling, OpenSpec guard wiring, and full-family JSON evidence before local-main integration.
