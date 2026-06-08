
---
doc_id: r6_live_runtime_promotion_plan
lang: zh-CN
status: active
stage: plan-confirmed
priority_order: Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit
translation_of: docs_bilingual/implementation_plans/r6_live_runtime_promotion_plan.md
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

WXWork live send 只允许在 R6 且 `R6_WXWORK_TARGET` 与 `R6_WXWORK_MESSAGE_TEMPLATE` 存在时执行。Receipt 不得包含消息正文或原始收件人。缺少目标或确认时必须写 blocked receipt。

### Stop-slop / response-density runtime

Response-density runtime 只有在 rollback evidence 与 canary-preservation evidence 存在时才能安装或激活 hook。缺少证据时默认 blocked。

### gstack delivery loop

gstack 仍是 Comet/OpenSpec/Superpowers 之下的 advisory 层。可以运行 live delivery-loop smoke，但不得覆盖 Comet phase routing、OpenSpec WHAT authority、Superpowers HOW discipline、本地 main-first gate 或远端发布 gate。

### Codex harnesses

Harness live job 需要 candidate id、isolated worktree、read/write guard、no-Codex-takeover evidence、job state、changed-path report、timeout release、rollback 与 cleanup evidence。

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
