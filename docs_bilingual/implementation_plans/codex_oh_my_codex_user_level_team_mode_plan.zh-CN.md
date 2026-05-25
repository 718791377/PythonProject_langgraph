---
doc_id: codex_oh_my_codex_user_level_team_mode_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md
status: active
doc_class: implementation_plan
---

# Codex / oh-my-codex 用户级团队模式方案（中文对照版）

> 说明
>
> - 英文 ASCII 主版：`docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md`
> - 2026-04-25 完整度检查结论：英文 ASCII 主版更完整，中文文件原先是“中文摘要 + 附录 C 摘录”。
> - 本文件现在作为中文对照版维护：所有实施判断以英文 ASCII 主版为完整基准；中文文件必须至少保持相同的主要章节与附录结构，并说明每个章节的实施语义。
> - 在新的统一口径下，这份方案应理解为：**兼顾用户级共享控制面与项目级 repo-local 承接边界**的共享 implementation plan。
> - 它服务于同一 machine / user / Codex home 下所有 `PyCharm / Codex CLI` 项目共用的 user-level team mode，同时要求每个仓库继续保留自己的 repo-local source、repo-local durable state、OpenSpec 与测试作为项目级权威面。

## 双语对齐状态

- 对齐基准：英文 ASCII 主版是完整结构基准与实施 source of truth。
- 中文定位：本文是中文对照版，不再是仅供阅读的摘要稿。
- 当前范围：本文保留既有中文实施摘录与附录 C 中文细节，同时补齐英文主版的完整结构索引，确保冷启动会话知道英文主版中每一部分都需要纳入实施判断。
- 后续规则：任何新增英文章节必须同步更新本文件的中文结构索引；任何改变实施语义的英文段落必须同步补充中文说明。

## 完整结构对照索引

以下索引与英文 ASCII 主版的主要章节和附录对齐。冷启动模型实施时，应先按本索引确认范围，再回到英文 ASCII 主版读取完整细节。

1. 目标：定义 user-level team mode 的目标、共享边界与生产级使用预期。
2. 范围：区分用户级共享控制面、项目级 repo-local source、durable state 与测试权威面。
3. 输入：以现有 OpenSpec、governance 文档、runtime helper 和已验证行为为输入。
4. 角色分层：区分 persistent panes、leader-side native subagents、burst review roles、heterogeneous orchestration 与 automatic role routing。
5. `team-executor` 与 `team-leader`：明确 persistent worker 与当前主 Codex CLI leader session 的边界。
6. 推荐项目阶段：覆盖 define target、read context、freeze plan、execute parallel、integrate、stabilize、verify accept，以及 P0-P7 映射。
7. 推荐调用节奏：覆盖早期、中期、后期、research-to-implementation handoff、hybrid orchestration、adversarial bug review、默认姿态和 restart matrix。
8. 多 worktree 防冲突规则：一 worker 一 worktree 一分支，冻结 ownership，热点文件串行，leader 负责集成。
9. 可复用团队模板：default development、high-throughput implementation、debug/stabilization、hybrid orchestration 与 opt-in mixed compose。
10. Operator control surface、共享用户级资产与项目边界：明确 leader commands、runtime state、mailbox、worktree notes、installed assets、backup 与 rollback。
11. Windows 前置条件：覆盖 Windows native backend 方向与 startup leader protocol 状态。
12. 全局使用规则：覆盖 provider budget、何时不用/启动/switch `omx team`、native Codex base layer、research/implementation 分工、homogeneous persistent teams、heterogeneous orchestration、adversarial review、hard routing directives、retrofit-capable sessions、debugging mode、mixed compose 与 rollback。
13. 实施顺序：按小步、可验证、可回滚的顺序推进 user-level team mode 能力。
14. 验收标准：以可运行命令、状态可检查、跨项目边界不破坏为验收核心。
15. 最终建议：保留当前主 Codex CLI session 为 leader，把持久化 worker/team 作为受控执行层。
16. LangGraph 方向：把 LangGraph 作为 additive durable backend，明确术语与后续深化方向。
17. Backend selection：区分 `native_omx` 与 `langgraph` backend family，定义 capability switches 和 long-running collaborative parallel execution。
18. 附录 A：官方 LangGraph 能力差距，作为后续深化与能力 gap sync 的依据。
19. 附录 B：稳定用户级命令名，确保 `codex-ohmy` / `codex-raw` 等入口语义稳定。
20. 附录 C：官方更新、差异检查与本地补丁重放标准流程；本文件保留该附录的中文细化内容。

## 当前中文摘录

### 用户级安全边界：脚本控制 + 提示词提醒

当前 `experts / durable_team / persistent team` 方案不得只依赖模型记住提示词。

所有系统级、用户级、项目级安全边界都必须同时具备：

- 脚本控制 - 可执行 checker、受保护 helper、CI gate 或生成式 launcher 逻辑；即使冷启动模型没有任何上一轮会话上下文，也必须默认 fail closed。
- prompt reminder - `project_startup_summary.*` and implementation plan text; `AGENTS.md` is only a recovery reread target, not the literal canary prompt source.

这条规则对以下行为尤其重要：

- `experts` 自动路由 - 必须由阈值、checker 或 routing trace 约束，不能只靠提示词判断。
- `durable_team` 启动 - 必须由计划冻结和独立切片检查保护，不能只靠模型记忆。
- `persistent team` 状态 - 必须由 repo-local `.omx/state/` scope 和 backend-family 规则保护，不能跨项目混用。
- local-main-first 发布、safe cleanup、state mutation 和 activation selector - 必须有脚本 gate 或明确记录为未落地 gap。

下一步实施切片应把这条规则提升为用户级 safety-boundary registry 和总 checker：

- `tools/check_safety_rule_script_backing.py` - aggregate checker for registered safety rules, script controls, prompt reminders, guard steps, and tracked gaps.
- `tools/safety_rule_script_backing_registry.json` - registry for each safety rule owner layer, prompt reminder location, executable control, guard step, and implementation status.
- `codex-safety-rule-script-backing.ps1` - future optional user-level mirrored helper for running the aggregate checker from consumer projects without making user-level state the source of truth.

总 checker 属于用户级能力，因为它要保护跨项目复用的 Codex / OMX / LangGraph 行为。一般提示词提醒文本仍属于项目级，因为每个仓库拥有自己的 `AGENTS.md`、startup summary、durable truth 和恢复阅读顺序。上下文保留哨兵更窄：它的字面提示词只能放在 `docs_bilingual/project_startup_summary.md` 与 `docs_bilingual/project_startup_summary.zh-CN.md`。

启动摘要还必须携带上下文保留哨兵。其他 active instruction surface，包括 `AGENTS.md`、用户级 startup summary、implementation plan、生成式 wrapper 和 launcher payload，可以指向 startup summary 的哨兵来源，但不得重复字面开头/结尾短语。

哨兵约定是：

- startup summary 定义可见自检信号，用来判断模型在 `/resume`、compaction 或长上下文压力之后是否仍理解冷启动权威。
- 如果模型在本应读取 startup summary 后的完整 assistant 回复没有输出该哨兵，则视为可能上下文丢失；如果刚读完就缺失，也应同时视为可能读取路径或编码失败。
- Recovery action: reread `AGENTS.md`, reread `docs_bilingual/project_startup_summary.*` through an explicit UTF-8 path, follow the startup read order, and then reread only the files required for the current task.

用户级 canary checker 不负责把哨兵提示词注入 wrapper payload，也不作为 response gate。它在收到 response text、response file 或 session JSONL evidence 时，只检查用户可见 assistant 回复，并过滤 tool output、compaction summary、reasoning、developer/system payload 与 startup-summary 文件读取输出；然后报告 `missing_canary` 或 `mojibake_canary` 诊断和冷启动恢复指令。

已经实现：

- 在 migration-aware live primary-engine compatibility-state rollout 已归档之后，这一节必须按**已验证的当前状态**来描述用户级 LangGraph surface，而不是继续把已经落地的能力写成未来计划。
- fully realized 的 LangGraph-native orchestration runtime 仍然强于当前本地用户级集成，但当前实现面已经足够宽，因此本附录应明确区分三类状态：已经实现、已经可用但仍偏 MVP、以及仍在方案或增量改造阶段。

- `subagent_routing`、`oh_my_codex`、`langgraph` 的分层用户级 capability switches
- repo-local LangGraph runtime state，位置在 `.omx/state/langgraph/`
- 用户级入口脚本与 backend-aware activation surfaces
- LangGraph 作为 Codex / oh-my-codex 之下的 additive durable backend，而不是替代性 runtime
- 一个受限但完整的七阶段 LangGraph durable shell，以及面向当前已支持 loop family 的 graph-native conditional routing 与 quality-gated loop posture
- LangGraph loop projection 字段，例如 `active_loop`、`iteration_count`、`iteration_budget`、`last_gate_verdict`、`stop_reason`
- reusable subgraph-library contracts 与 active-subgraph projection
- command-driven control flow、explicit parent handoff 与 command-aware resume posture
- additive streaming / debug observability 以及 bounded latest-event projection
- runtime-context 与 injected-store projection surfaces
- durable memory-store 与 semantic-memory projection surfaces
- graph-migration 与 thread-compatibility guard posture
- multi-interrupt approval-queue posture 与 explicit resume mapping
- replay、time-travel 与 bounded update-state recovery controls，以及 source attribution
- 已落地稳定的 frozen implementation brief 工件，包含 `brief_id`、`thread_id`、`source_evidence_refs`、`frozen_at`
- 已落地稳定的 judge-approved survivor queue 工件，包含队列元数据、survivor count 与只读 inspect pointers
- inspectable durable-state 已能投影 LangGraph artifact presence 与 artifact 级摘要状态
- reducer-backed merge channels、single-writer protection，以及面向 LangGraph durable threads 的 reducer-aware fan-in / fan-out projection
- 一个受限但已落地的 graph-kernel layer，能够把七阶段 durable shell 映射为面向 `StateGraph` 的 node / transition posture，并保持 repo-local inspectability
- 一个受限但已落地的 primary-runtime engine layer，能够投影 compiled-engine identity 与 execution posture，同时保持当前用户级 operator model 兼容
- 一个受限但已落地的 compiled-invocation layer，能够投影 live compiled-path identity、invoke posture 与 invocation helper surfaces，同时保持当前 operator model 不被打碎
- 一个受限但已落地的 live-execution layer，能够请求或报告 compiled graph execution posture，同时保持 repo-local compatibility 与当前 operator surface 不被打碎
- 一个受限但已落地的 generalized live-routing layer，能够在保留七阶段 operator shell 的前提下投影 graph-native route selection 与 loop posture
- 官方 subgraph persistence-mode defaults 与 bounded subgraph-state inspection posture 已经落地，并且已经接入 reusable-subgraph helper surfaces
- 一个 fuller live `StateGraph` primary execution-engine layer 也已经落地，能够通过当前 user-level helper surfaces 投影 richer execution path、resulting phase / status 与 bounded primary execution semantics
- 一个 bounded richer automatic runtime-policy layer 也已经落地，能够暴露 inspectable 的 migration-handling posture 与 safe resolved-queue auto-resume behavior，同时保持 manual-first 默认值
- 一个更宽但仍 bounded 的 automatic runtime-policy layer 也已经落地，除了上述能力之外，还覆盖 safe recovery continuation 与 stale-interrupt clearing，同时保持 inspectable、additive 与 manual-first 默认值
- 一个 deeper live primary-engine layer 也已经落地，能够通过当前 user-level helper surfaces 投影多步 phase / node path、显式 stop boundary，以及 recursion-limit-aware 的 deeper execution posture
- 一个 superstep-aware 的 live primary-engine layer 也已经落地，能够走过一条 bounded 的多节点 compiled graph path，并通过当前 user-level helper surfaces 投影 node / phase visit trace、superstep count 与 bounded boundary posture
- 一个 stateful live primary-engine layer 也已经落地，能够把 next-hop 决策与 transition log 放进 graph-native execution state，同时保持七阶段 operator shell 与当前 durable artifacts 不变
- 一个 graph-resident live primary-engine boundary-state layer 也已经落地，能够把 interrupt、recovery 与 terminal boundary posture 放进 graph-native engine state，而不是在 compiled execution 之前就短路处理
- 一个 subgraph-aware live primary-engine handoff-state layer 也已经落地，能够把 active-subgraph、source-subgraph、target-subgraph 与 parent-handoff continuation posture 放进 live-engine state，而不只是依赖相邻 projection surface
- 一个 approval-aware live primary-engine resume-state layer 也已经落地，能够把 queue posture、pending/resolved count、current interrupt identity 与 resume-map keys 放进 live-engine state，而不只是依赖相邻 approval projection surface
- 一个 recovery-aware live primary-engine provenance-state layer 也已经落地，能够把 recovery action、recovery target identity、source-record provenance、recoverable field touches 与 history-target availability 放进 live-engine state，而不只是依赖相邻 replay / recovery projection surface
- 一个 durable-artifact-aware live primary-engine state layer 也已经落地，能够把 artifact_state_kind、implementation brief 的 presence / identity、brief source-evidence ref count、survivor queue 的 presence / queue_kind，以及 survivor count 放进 live-engine state，而不只是依赖相邻 artifact projection surface
- 一个 reducer-aware live primary-engine merge-state layer 也已经落地，能够把 reducer compatibility、fanout state、invalid multi-writer posture、merge-channel updates、channel item counts，以及 reducer source attribution 放进 live-engine state，而不只是依赖相邻 reducer projection surface
- 一个 command-aware live primary-engine control-state layer 也已经落地，能够把 transition kind、update keys、goto target、graph scope、source-subgraph / target-subgraph attribution、parent-handoff target、resume posture，以及 resume-payload keys 放进 live-engine state，而不只是依赖相邻 command projection surface
- 一个 runtime-aware live primary-engine context-store-state layer 也已经落地，能够把 context schema、runtime-context 的 presence / keys / kind hints、store configuration posture、store access expectation，以及 store kind 放进 live-engine state，而不只是依赖相邻 runtime injection projection surface
- 一个 memory-aware live primary-engine semantic-state layer 也已经落地，能够把 memory-store configuration、memory-store kind、memory namespaces、semantic-memory enablement、semantic-store kind，以及 semantic namespaces 放进 live-engine state，而不只是依赖相邻 memory projection surface

已经可用，但仍偏 MVP：

- 当前这条 lane 仍然是通过 Python sidecar 与 repo-local state 来持久化和投影 LangGraph durable posture，而不是已经拥有一个完全泛化的官方 `StateGraph` runtime kernel
- 多个 operator surface 仍然刻意保持为 bounded contract projection，而不是 raw full-fidelity 的 engine-native traces
- 与 `native_omx` 的 backend-family coexistence 仍然保持 explicit 且 manual-first

仍在方案或增量改造阶段：

- 超出当前 bounded primary execution semantics 与 helper-projected execution path 的后续 live-engine 深化
- 超出当前 reusable-library contract set 与当前 bounded persistence / inspection posture 的后续 subgraph / lane 扩展
- 超出当前 bounded migration-handling、safe resolved-queue、safe recovery continuation 与 stale-interrupt clearing posture 的后续 automatic-policy 扩展
- 超出当前 memory-aware semantic-state handling、runtime-aware context-store handling、command-aware control handling、reducer-aware merge handling、durable-artifact-aware handling、recovery-aware provenance-state handling、approval-aware resume-state handling 与 bounded stop-boundary posture 的后续 live-engine 扩展

因此，这里的正确表述应当是：

- 当前用户级 LangGraph lane 已经是真实可用能力
- 但它还不是 fully realized 的 LangGraph-native orchestration runtime
- 文档应把它描述为“implemented surface 已经比较宽、但仍未 fully realized”的 additive durable backend，而不是继续把已经落地的能力写成未来计划

### Release train overlay after P0-P7 / P0-P7 之后的小版本发布轨道

P0-P7 implementation batches 已经是 implemented baseline。后续不要重开已完成的 P batches，而应使用更小的 release slices。

当前 release interpretation：

- `R0 Governance Baseline` —— 治理底座 release label，覆盖 startup、OpenSpec guard、worktree isolation、session ownership、MCP scope 和 safety-rule script backing。
- `R0.5 Inspectable Durable State` —— 可检查 durable state release label，覆盖 `codex-durable-state-status.ps1` 这类只读状态 helper。
- `R0.6 Durable Routing Smoke Gate` —— 下一小版本，用于 automatic routing 的 dry-run 或 read-only validation，不直接 exercise runtime mutation。
- `R0.7 Native OMX Adoption MVP` —— 未来小版本，用于在一个低风险 worker-centric task 中受控采用 `native_omx`。
- `R0.8 LangGraph Adoption MVP` —— 未来小版本，用于在带 checkpoint、approval、frozen brief 或 survivor queue 信号的 graph-shaped task 中受控采用 `langgraph`。
- `R1.0 Personal Durable Team MVP` —— 未来小版本，用于第一个可多项目复用的个人 durable-team MVP。
- `R2.0 Production Durable Team` —— 未来完整目标，包含更强 memory、recovery、GUI 和 graph-native orchestration surfaces。

Release 0.6 是 MR 1 到 MR 6 完成后的唯一默认下一步。它只是 gate definition 和 validation slice，不是写状态授权。

未来每个 Release 0.6 smoke 或 adoption-gate change 都必须声明：

- `target_repository` —— 目标仓库根目录，说明本次评估的 source、OpenSpec artifacts 和 repo-local durable state 属于哪里。
- `phase` —— 项目阶段，用来驱动 routing thresholds。
- `task` —— 具体 validation question 或 work item。
- `operator_consent_boundary` —— 操作员授权边界，用来区分 read-only planning 与 `-Apply`、`.omx/state/` 写入或 durable-team launch 等变更动作。

Release 0.6 默认边界：

- 只允许 dry-run 或 read-only inspection。
- 不执行 `omx-team-auto.ps1 -Apply`；`-Apply` 是执行 planned durable action 的 helper 开关。
- 不写 `.omx/state/`；`.omx/state/` 是 repo-local durable-state 目录。
- 不启动或关闭 `omx team`；`omx team` 是 durable worker-team runtime 命令。

更细 release ladder：

- `R0.6.0 Gate Template` —— 模板切片，用来定义 smoke/adoption gate 文档形状和必填字段。
- `R0.6.1 Gate Field Checker And Codex Native Rollback Gate` —— checker 切片，用来在 future gate change 缺少必填字段时失败，并在 native Codex 或 rollback evidence 缺失时阻止 production marking。
- `R0.6.2 Read-Only State Sampling` —— 只读采样切片，用来对一个 target repository 运行 status-only durable-state sampling。
- `R0.6.3 Dry-Run Routing Decision` —— dry-run 判断切片，用来解释 no-team、native_omx 或 langgraph decision，但不 apply。
- `R0.6.4 Expected-Result Fixture` —— fixture 切片，用来把预期 dry-run decisions 固化为 regression evidence。
- `R0.6.5 Cross-Project Read-Only Review` —— 跨项目只读复核切片，用来证明 consumer repositories 不会继承本仓库 durable truth。

R0.6.1 Codex native rollback gate evidence：

- `codex --version` —— 本地 smoke command，用来证明 native Codex entrypoint 仍可启动。
- `codex-raw --version` —— 本地 smoke command，用来证明 stable raw bypass 仍可用。
- `codex-ohmy --version` 或 `codex-ohmy --help` —— 本地 smoke command，用来证明 wrapped launcher 不会立即失败。
- `test/install-codex-user-level-team-mode.test.ps1` —— PowerShell regression test，用来在临时目录证明 backup snapshot 和 rollback-on-error behavior。
- `tools/codex_native_rollback_release_gate_template.json` —— JSON template，用来记录 production marking 前必需的 release evidence。
- `tools/check_codex_native_rollback_release_gate_template.py` —— 静态 checker，用来验证 template 和 source evidence，且不修改 user-level Codex assets。

- `R0.7.0 Low-Risk Target Selection` —— 选择切片，用来指定一个足够安全的 repository 和 task。
- `R0.7.1 Native OMX Dry-Run Stability` —— dry-run 稳定性切片，用来在 apply mode 之前证明 native_omx selection 稳定。
- `R0.7.2 Explicit Apply Consent` —— 授权切片，用来记录 `-Apply` 前必须具备的精确 operator approval。
- `R0.7.3 Lifecycle Record Check` —— 生命周期切片，用来验证 launch、reuse、shutdown 和 tracked-record reporting。
- `R0.7.4 Restart Recovery Check` —— 重启恢复切片，用来确认冷启动会话能安全 inspect native_omx state。
- `R0.7.5 Native OMX Closeout Archive` —— 收尾归档切片，用来归档 evidence 并避免留下 unmanaged active team residue。
- `R0.8.0 Graph-Shaped Task Selection` —— 选择切片，要求 checkpoint、approval gate、frozen brief、survivor queue 或等价 graph signal。
- `R0.8.1 Checkpoint Smoke` —— checkpoint 切片，用来证明 state 可以保存和恢复。
- `R0.8.2 Approval Gate Smoke` —— approval 切片，用来证明 execution 可以暂停等待 operator decision。
- `R0.8.3 Frozen Brief Smoke` —— handoff 切片，用来证明 research 可以冻结成 implementation brief。
- `R0.8.4 Survivor Queue Smoke` —— triage 切片，用来证明 reviewed bug survivors 可以进入 debugger-lane work。
- `R0.8.5 LangGraph Closeout Archive` —— 收尾归档切片，用来归档 evidence，同时不把 langgraph 变成无关 future tasks 的默认选择。
- `R0.9 Lane Arbitration` —— 决策层切片，用来在多 lane 同时 enabled 时选择 native_omx、langgraph 或 no durable team。
- `R1.0 Personal Durable Team MVP` —— MVP 切片，用来形成第一个单用户、多项目可用版本。
- `R1.1 Multi-Project Consumer Rollout` —— consumer rollout 切片，用来推广到其他项目，同时保持 repo-local durable truth。
- `R1.2 Operational Hardening` —— hardening 切片，用来处理 logging、MCP scope、config sentinel、helper mirror、cleanup 和 rollback。
- `R2.0.0 Production Readiness Standard` —— 准入切片，用来冻结 production acceptance criteria。
- `R2.0.1 Durable Memory Model` —— memory 切片，用来定义 durable memory boundaries 和 retention rules。
- `R2.0.2 Crash Recovery` —— recovery 切片，用来证明 interrupted work 可以安全 inspect 和 resume。
- `R2.0.3 Graph-Native Orchestration` —— graph 切片，只在有充分理由时提升 graph-shaped orchestration。
- `R2.0.4 Security And Secrets Boundary` —— security 切片，用来保护 credentials、permissions 和 untrusted inputs。
- `R2.0.5 Performance And Concurrency Test` —— scale 切片，用来测试 worker count、provider pacing 和 long-running stability。
- `R2.0.6 Operator Dashboard` —— observability 切片，用来给 operator 一个清晰 status surface。
- `R2.0.7 Multi-Project Maintenance Strategy` —— maintenance 切片，用来定义跨 repositories 的长期维护策略。
- `R2.0.8 Production Release And Rollback` —— release 切片，只在 rollback evidence 存在后标记 production release。

## 附录 C：`官方更新 + 差异检查 + 本地补丁重放` 标准流程

这一节给出当前仓库建议采用的标准维护顺序。目标不是长期 fork 官方安装产物，而是：

- **官方 npm 安装产物尽量保持接近上游**
- **Windows 安全包装层、用户级提示层、测试层尽量下放到本地**
- **只有运行时语义级问题才继续直接重打到官方安装产物里**

配套可执行模板：

- `tools/codex-official-update-patch-replay-template.ps1` - 用于官方 update、diff、replay 与 test stages 的仓库维护模板。
- 只读预览：
- `.\tools\codex-official-update-patch-replay-template.ps1 -Stage precheck -Json` - 以 JSON 输出 precheck report 的只读盘点命令。
- 分阶段执行：
- `-Stage precheck` - 收集 pre-update inventory 与 checkpoint state 的 stage flag。
- `-Stage update` - 刷新官方 npm-installed OMX package 的 stage flag。
- `-Stage diff` - 对比 upstream files 与 local patch decisions 的 stage flag。
- `-Stage replay` - 重放保留的 local patches 并重新生成 wrappers 的 stage flag。
- `-Stage test` - 运行 post-replay validation 的 stage flag。
- `-Stage all` - 运行完整维护 sequence 的 stage flag。
- checkpoint 串接：
  - `precheck` —— 预更新盘点阶段，默认会新建一份 checkpoint 根目录
  - `update / diff / replay / test` —— 后续维护阶段，默认会自动续接最近一次 checkpoint，除非显式传入 `-SnapshotRoot`
  - 当前 pointer 文件：`<repo>/.tmp/official-update-patch-replay-latest.json` —— 最新轮次定位文件，用来告诉后续阶段应续接哪个 checkpoint 根目录
  - 当前 checkpoint manifest：`<snapshot-root>/checkpoint.json` —— 单轮状态清单文件，用来记录阶段历史与生成产物路径
  - 阶段门禁：
    - 没有记录到 `precheck` -> `update / diff / replay / test` 全部会被阻止；`precheck` 是建立基线盘点的起始阶段
    - 没有记录到 `diff` -> `replay / test` 会被阻止；`diff` 是刷新补丁决策产物的审查阶段
    - 没有记录到 `replay` -> `test` 会被阻止；`replay` 是真正应用补丁后的重放阶段
- 自动生成的运维产物：
  - `report.json` —— 当前 checkpoint 的机器可读运行摘要文件
  - `checklist.md` —— 当前 checkpoint 的人工阅读检查清单文件
  - `patch-decision-table.md` —— Markdown 决策视图文件，用于人工阅读与审查
  - `patch-decision-table.json` —— JSON 决策主表文件，当前作为机器可读回读文件
  - `patch-decision-table.csv` —— CSV 决策导出文件，当前作为表格友好的导出视图而不是规范回读文件
- patch 分类表行为：
  - `final_decision` —— 最终决策字段，当前会自动预填默认推荐动作
  - `decision_reason` —— 决策理由字段，当前会自动预填默认说明
  - `decision_status` —— 机器可读决策状态字段，用来标记该行仍是自动结果还是已经被人工处理
    - `auto_prefilled` —— 自动预填状态，表示该行仍采用脚本生成的默认推荐
    - `manually_overridden` —— 人工覆盖状态，表示审查者主动修改了自动生成的决策
    - `unresolved` —— 未决状态，表示该行仍等待人工给出明确决策
  - 当前默认启发式：
    - `runtime.js` —— 已安装团队运行时文件 -> `replay`，表示运行时补丁默认继续走重放路径
    - `windows-worker-controller.js` —— Windows worker 控制器文件 -> `replay`，表示控制器侧启动与 IO 补丁默认继续走重放路径
    - `worker-bootstrap.js` —— worker 指令引导文件 -> `replay`，表示当前操作层默认仍先走重放，但长期仍是优先下放候选
    - `user_level_surface` —— 本地用户级 wrapper / skill / 提示层 -> `move-down`，表示优先放在官方安装产物之外
- 一条示例重放路径：
  - `.\tools\codex-official-update-patch-replay-template.ps1 -Stage replay` —— replay 阶段命令，用来应用保留补丁并重生成用户级层

### 附录 C：已落地的 decision-lock 与 diff-approval 补充项

下面这些内容已经落地到 `tools/codex-official-update-patch-replay-template.ps1`，当前应理解为已经实现的 operator-surface 行为。

- patch decision row 现在包含：
  - `decision_locked` —— 决策锁定位字段，用来告诉脚本不要再覆盖这条人工冻结的决策
  - `decision_lock_reason` —— 决策锁定原因字段，用来说明为什么要锁住这条决策
- 锁定语义：
  - 当 `decision_locked = true` 时，重新生成 decision row 会保留人工冻结的决策字段，而不是再次自动回填；`decision_locked` 因此是“禁止自动刷新该行”开关
- decision table 的权威读取顺序：
  - `patch-decision-table.json` —— JSON 决策主表文件，作为回读真源
  - `patch-decision-table.csv` 与 `patch-decision-table.md` —— 导出视图文件，继续作为审查输出，而不是规范回读面
- checkpoint manifest 现在包含 approval 投影：

  - `checkpoint manifest` —— checkpoint 状态清单文件，位于 `<snapshot-root>/checkpoint.json`，现在包含 diff 审批区块
  - `approvals.diff_review` —— diff 审批区块，用来记录 diff 阶段是否已经被显式审查通过
  - `approved` —— 审批布尔字段，用来记录 diff 审查是否已通过
  - `approved_at` —— 审批时间字段，用来记录 diff 审查通过的时间
  - `approval_note` —— 审批备注字段，用来记录简短的审查说明

```json
{
  "approvals": {
    "diff_review": {
      "approved": false,
      "approved_at": "",
      "approval_note": ""
    }
  }
}
```

- operator 控制面现在包含：
  - `-Stage diff -ApproveDiff` —— diff 审批命令形式，用来把 diff 阶段标记为“已审查并通过”
- replay 门禁已经收紧：
  - `replay` —— 补丁重放阶段，需要 `precheck`；`precheck` 是创建 checkpoint 与建立基线盘点的起始阶段
  - `replay` 需要 `diff`；`diff` 是刷新决策产物并供人工审查的差异阶段
  - `replay` 需要 `approvals.diff_review.approved = true`；`approvals.diff_review.approved` 是 manifest 中表示“diff 已被显式审查通过”的字段

### C.1 先把四层边界分清

1. **官方安装层**
   - 例：`C:\Users\lenovo\AppData\Roaming\npm\node_modules\oh-my-codex\`
2. **用户级包装层**
   - 例：`C:\Users\lenovo\.codex\bin\`
3. **用户级提示 / skill / playbook 层**
   - 例：
- `C:\Users\lenovo\.codex\skills\worker\SKILL.md` - 在 npm package 外生成或维护的 user-level worker skill instructions。
- `C:\Users\lenovo\.codex\state\user-level-team-mode-model-instructions.md` - team-mode workers 使用的 user-level model-instructions payload。
4. **仓库内 source-of-truth 层**
   - 例：
- `tools/install-codex-user-level-team-mode.ps1` - 重新生成 user-level wrappers 与 team-mode artifacts 的 installer script。
- `tools/openclaw-omx-*.mjs` - legacy OMX compatibility fixes 的仓库 patch scripts。
- `test/install-codex-user-level-team-mode.test.ps1` - team-mode installer 的 PowerShell test suite。

后面的所有判断都按这四层来做。

### C.2 更新前必须先做什么

#### 1）记录当前版本和安装根

先读，不要改：

```powershell
npm root -g
npm ls -g oh-my-codex @openai/codex --depth=0
git -C D:\PythonProject_langgraph rev-parse HEAD
```

至少把下面几项记下来：

- 当前全局 `oh-my-codex` 版本
- 当前全局 `@openai/codex` 版本
- 当前官方安装根目录
- 当前本地补丁仓库 commit

#### 2）先快照当前已打补丁的官方文件

最少要留存：

- `dist/team/runtime.js` - update 前需要 snapshot 的 upstream team runtime file。
- `dist/team/windows-worker-controller.js` - update 前需要 snapshot 的 upstream Windows worker controller file。
- `dist/team/worker-bootstrap.js` - update 前需要 snapshot 的 upstream worker bootstrap file。

并且先做一次 marker 盘点：

```powershell
$npmRoot = npm root -g
$omxRoot = Join-Path $npmRoot 'oh-my-codex'
Get-ChildItem (Join-Path $omxRoot 'dist\\team') -Recurse -File |
  Select-String -Pattern 'OPENCLAW_' |
  Select-Object Path, LineNumber, Line
```

这一步的意义是：更新后才能准确判断某个 patch 是**被上游吸收了**、**需要重写**、还是**仍需原样重放**。

#### 3）先确认本地包装层本来就是健康的

至少只读检查这些是否已经存在：

- `omx-team-send-message.ps1` - 用于安全发送 worker mailbox messages 的 local wrapper。
- `omx-team-claim-task.ps1` - 用于 claim team task 的 local wrapper。
- `omx-team-transition-task-status.ps1` - 用于改变 task lifecycle status 的 local wrapper。
- `omx-team-release-task-claim.ps1` - 用于释放 task claim 的 local wrapper。
- `omx-team-report-progress.ps1` - 用于报告 worker progress 的 local wrapper。
- `omx-team-complete-task.ps1` - 用于标记 task complete 的 local wrapper。
- `omx-team-fail-task.ps1` - 用于标记 task failed 的 local wrapper。

如果这些在更新前就已经缺失或过旧，先修本地生成层，再做官方更新；不要把“更新前已有问题”误判成“上游更新带来的问题”。

#### 4）避免在半更新状态下新起 durable team

经验规则：

- 已经启动的旧会话通常不会立刻被改写
- 但**新 worker 启动**如果正好落在“官方文件已更新、本地补丁还没重放”的窗口，就容易进入混合状态

所以标准做法是：

- 更新窗口内不要新起 durable team
- 等“官方更新 + 补丁重放 + 本地包装层重生成”全部完成后，再起新的 durable worker

### C.3 官方更新时怎么做

先走官方路径，**不要一上来就重放本地补丁**。

当前建议顺序：

```powershell
npm install -g @openai/codex oh-my-codex
omx setup
```

如果安装过程跳过了脚本，或者需要刷新 OMX 本身：

```powershell
omx update
```

### C.4 更新后先比对什么

顺序必须固定，先看结构，再看功能重叠，最后才决定重放。

#### 第一轮：先看文件 / API 形状有没有变

先确认这几个目标还在不在、有没有改名、有没有大改结构：

- `dist/team/runtime.js` - 用于检查 file 与 API shape drift 的 upstream team runtime file。
- `dist/team/windows-worker-controller.js` - 用于检查 file 与 API shape drift 的 upstream Windows worker controller file。
- `dist/team/worker-bootstrap.js` - 用于检查 file 与 API shape drift 的 upstream worker bootstrap file。
- 本地 patch 脚本依赖的导出名 / 片段锚点

如果文件位置或关键锚点已经变了，先修 replay 脚本，不要直接盲打补丁。

#### 第二轮：先看上游有没有已经覆盖本地功能

优先检查这些能力是否已经被官方直接提供：

- Windows worker 生命周期安全入口
- worker 完成 / 失败提示是否已经更安全
- Windows stdin close / prompt 处理
- startup status seed
- worktree writable roots
- prompt-controller detach / teardown
- worker bootstrap 是否已经不再鼓励手写 raw `omx team api --input ...`

如果上游已经原生支持，**优先删本地 patch，改用官方实现**。

#### 第三轮：给每个本地 patch 明确分类

更新后每个 patch 都必须归入四类之一：

1. **drop**
   - 上游已解决，直接删除本地 patch
2. **move-down**
   - 行为仍需要，但应下放到 wrapper / skill / playbook / test
3. **rebase**
   - 问题还在，但 patch 需要适配新的上游代码形状
4. **replay**
   - 上游没动到关键逻辑，本地 patch 仍需继续重打

### C.5 哪些补丁优先下放到包装层

优先下放的是**不改变官方运行时语义、只是在改善 Windows 使用面**的东西。

#### 1）PowerShell 安全包装层

这些应长期保留在本地生成层，而不是重打进官方源码：

- `omx-team-send-message.ps1` - 用于发送 worker mailbox messages 的 local wrapper。
- `omx-team-mailbox-list.ps1` - 用于列出 worker mailbox messages 的 local wrapper。
- `omx-team-mailbox-mark-delivered.ps1` - 用于标记 mailbox messages delivered 的 local wrapper。
- `omx-team-claim-task.ps1` - 用于 claim team task 的 local wrapper。
- `omx-team-transition-task-status.ps1` - 用于改变 task lifecycle status 的 local wrapper。
- `omx-team-release-task-claim.ps1` - 用于释放 task claim 的 local wrapper。
- `omx-team-report-progress.ps1` - 用于报告 worker progress 的 local wrapper。
- `omx-team-complete-task.ps1` - 用于标记 task complete 的 local wrapper。
- `omx-team-fail-task.ps1` - 用于标记 task failed 的 local wrapper。

#### 2）提示词 / playbook / wait 策略

这些优先留在本地：

- worker playbook
- user-level model instructions
- 动态 wait window / progress check-in 文案
- wrapper-first 示例
- 不鼓励手写 raw JSON PowerShell 命令的指导

#### 3）raw 示例隐藏 / 抽象层

凡是只是在做这些事的 patch，都优先往下放：

- 隐藏 raw `omx team api --input ...` 示例
- 把 Windows one-liner 改成 wrapper 示例
- 把 closure flow 讲成 wrapper-first

这类逻辑优先放在：

- 本地 wrapper 文档
- worker skill
- 生成出来的 model instructions
- 安装与回归测试

#### 4）更新流程自身的自动化

以下内容全部应留在仓库层：

- diff 检查脚本
- patch replay 脚本
- 安装器
- 测试
- 双语文档

### C.6 哪些补丁仍需要重打到官方安装产物里

目前仍需要直接 patch 官方安装产物的，是那些**包装层事后无法补救的运行时问题**。

#### 1）运行时语义级 patch

这类在当前架构下仍需优先重打到官方安装产物：

- `runtime.js` 里的 prompt-controller detach / teardown 行为
- `runtime.js` 里的 Windows worktree writable-root 修复
- `runtime.js` 里的 startup evidence / launch readiness 相关修复
- `windows-worker-controller.js` 里的 stdin close / prompt 处理
- `windows-worker-controller.js` 里的 startup status seed
- `windows-worker-controller.js` 里的 debug-root / observability 修复

原因很简单：这些问题发生在 worker 启动、IO、teardown、worktree 权限阶段，wrapper 在外层补不了。

#### 2）仍由官方 `worker-bootstrap.js` 直接发给 worker 的内建指令

即使本地已经有 wrapper-first 包装层，如果上游仍然在 `worker-bootstrap.js` 中直接发出这些不安全示例，就仍需要重打：

- raw `omx team api --input ...` 示例
- Windows 不安全 / 不兼容的 shell 示例
- 没有指向 `report-progress / complete-task / fail-task` 高层 wrapper 的完成态提示

这里的判断标准不是“理论上能不能下放”，而是：

- **如果当前坏示例仍是上游 bootstrap 直接吐给 worker 的，就还得 patch 上游**
- **只有当上游提供稳定 hook，或者本地 skill / prompt 已经能稳定覆盖时，才真正下放**

### C.7 当前仓库建议的 replay 优先级

每次官方更新后，按下面顺序处理：

1. **先重放关键运行时 patch**
- `runtime.js` - 当前建议优先重放的关键 runtime patch target。
- `windows-worker-controller.js` - 当前建议优先重放的 Windows worker controller patch target。
2. **再重放 worker bootstrap 安全 patch**
- `worker-bootstrap.js` - worker bootstrap 安全 patch 的 replay target。
3. **再重生成本地用户级包装层**
   - 重新运行 `tools/install-codex-user-level-team-mode.ps1`
4. **再跑本地测试**
   - 重点是 `test/install-codex-user-level-team-mode.test.ps1`
5. **最后做一次聚焦的 Windows durable-worker smoke test**
   - worker 能启动
   - worker 不会立即死亡
   - task 能从 `in_progress` 收敛到 `completed`

### C.8 什么叫这轮更新真正完成

必须同时满足：

- 官方更新成功
- 更新后差异检查完成
- 每个 patch 都被明确标成 `drop / move-down / rebase / replay`
- 仍需保留的官方安装产物 patch 已重放
- 本地 wrapper 层已重生成
- 测试通过
- 至少有一条聚焦的 Windows durable-worker smoke 路径通过

这才叫：

- **官方更新 + 差异检查 + 本地补丁重放**

## 24. Expert Fan-Out 与 Stalled Subagent 处理

有界多面研究必须先使用同质 analyst fan-out。`analyst` 是第一轮用于独立研究面、歧义发现和 acceptance target 澄清的角色。

除非任务已经越过研究阶段，明确进入设计或执行排序，否则不要一开始就混用 `analyst / architect / planner` fan-out。应在 analyst fan-in 后再升级：

- `architect` - 当 analyst fan-in 显示存在跨模块设计、共享接口、信任边界、迁移或非局部架构决策时使用。
- `planner` - 当 analyst fan-in 显示存在两个以上执行切片、串行热点、rollout ordering 或 dependency chains 时使用。
- `writer` - 当 analyst fan-in 显示工作已经进入文档定稿，而不是研究本身时使用。

未完成的 subagent 必须先诊断，再决定跳过或关闭。Leader 必须记录：

- `role` - 被分配的 subagent 角色。
- `prompt_scope` - 给 subagent 的有界 prompt 或文件范围。
- `wait_windows` - 已经使用过的等待窗口及持续时间。
- `last_signal` - subagent 最后可观察到的 progress、result 或 silence。
- `suspected_cause` - 判断 subagent 是仍在工作、startup-blocked、tool-blocked、provider-blocked，还是 stalled。
- `action_taken` - 继续等待、缩小范围并重启、带原因关闭，或披露限制后由本地继续。
- `result_used` - 最终答复是否使用、排除或替换了该 subagent 的结果。

Leader MUST NOT 在未完成这个诊断步骤前，就默认“本地读取 + 部分 fan-in 已足够”。如果关闭仍在运行的 subagent，closeout note 必须说明为什么没有该结果也安全，或者还剩什么限制。
