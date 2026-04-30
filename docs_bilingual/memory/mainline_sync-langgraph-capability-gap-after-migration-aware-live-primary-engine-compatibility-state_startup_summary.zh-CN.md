---
doc_id: mainline_sync_langgraph_capability_gap_after_migration_aware_live_primary_engine_compatibility_state_startup_summary
lang: zh-CN
status: active
doc_class: startup_summary
translation_of: docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md
---

# 主线 `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` 启动摘要

## 适用范围

这份摘要覆盖当前主线下的维护支线，重点是：

- `oh-my-codex` 的官方更新兼容
- 本地补丁重放工作流标准化
- Windows 安全的 durable-team 运维控制面延续

如果新会话要继续 updater / replay / gated checkpoint（更新器 / 重放 / 带门禁的检查点） 这一条维护线，而不是回到更宽泛的 LangGraph 历史 rollout，请先读这份摘要。

## 当前交接快照

决定下一步前，先读这一节，再读后面的旧 implementation command card。

- `automate-task-ownership-precheck-checker` —— 当前维护支线最近归档的 OpenSpec change，用来落地 checker-backed task ownership precheck 行为。
- `tools/check_session_ownership_claims.py` —— session ownership checker，现在已经支持仓库写入前的 task ownership precheck signals。
- `openspec status` —— 当前 active-change 检查命令；本次交接刷新时，它在 `main` 上显示没有 active changes。
- `main`、`gitlab/main` 与 `github/main` —— 仓库发布引用；本次交接刷新时，本地 clone 中三者都指向同一个提交 `460f813`。

当前判断：

- decision-lock plus diff-approval replay 增量已经实现
- task ownership precheck checker 增量也已经实现并归档
- 新会话不需要重新打开这两项设计讨论，除非出现新证据
- 下一步安全候选是选择一个新的小步 OpenSpec change、自动化剩余 replay smoke checks，或继续 durable-state status hardening

## 实施命令卡片

如果新会话要快速接手，先看这一张卡片。

### Do now（现在立刻做）

- 继续在 `tools/codex-official-update-patch-replay-template.ps1` 中实现已冻结的下一轮增量
- 直接实现 decision lock + diff approval（决策锁定 + diff 审批） 增量，不要重新设计整条工作流
- 把当前脚本视为已经可用的基础面，在现有行为上增量扩展

### Edit these files（改这些文件）

- `tools/codex-official-update-patch-replay-template.ps1` - 本轮增量正在扩展的 PowerShell replay-template 脚本。
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - 记录 user-level team-mode 行为的英文 active implementation plan。
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md` - active user-level team-mode implementation plan 的中文对照文件。
- 只有代码真正落地后，才把双语 Appendix C（附录 C） 文本从“planned（计划中）”改成“implemented（已实现）”

### Run these verifications（跑这些验证）

验证卡片 1 —— 正常路径

```powershell
$root = 'D:\PythonProject_langgraph\.tmp\verify-decision-lock-happy'
if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
.\tools\codex-official-update-patch-replay-template.ps1 -Stage precheck -SnapshotRoot $root
.\tools\codex-official-update-patch-replay-template.ps1 -Stage diff -SnapshotRoot $root -ApproveDiff
.\tools\codex-official-update-patch-replay-template.ps1 -Stage replay -SnapshotRoot $root -WhatIf
```

- expected result（预期结果）—— `precheck` 正常完成，`diff -ApproveDiff` 会写入审批状态，`replay` 不再因为 diff 审批门禁而被阻止
- failure triage pointer（失败排查指针）—— 先看：
- `tools/codex-official-update-patch-replay-template.ps1` - stage-gate 或 approval 行为失败时需要检查的脚本。
- `$root\checkpoint.json` - 记录已完成 stages 与 approvals 的 snapshot checkpoint 文件。
- `$root\patch-decision-table.json` - 记录 patch decisions 与人工 overrides 的 JSON decision table。

验证卡片 2 —— 缺少 `precheck` 时 replay 被阻止

```powershell
.\tools\codex-official-update-patch-replay-template.ps1 -Stage replay -SnapshotRoot 'D:\PythonProject_langgraph\.tmp\verify-missing-precheck' -WhatIf
```

- expected result（预期结果）—— 命令直接报错，提示必须先有 `precheck`
- failure triage pointer（失败排查指针）—— 先看：
- `tools/codex-official-update-patch-replay-template.ps1` - replay 错误跳过 precheck gate 时需要检查的脚本。
  - 如果该 root 已存在，再看 `<snapshot-root>\checkpoint.json`

验证卡片 3 —— 缺少 `diff` 时 replay 被阻止

```powershell
$root = 'D:\PythonProject_langgraph\.tmp\verify-missing-diff'
if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
.\tools\codex-official-update-patch-replay-template.ps1 -Stage precheck -SnapshotRoot $root
.\tools\codex-official-update-patch-replay-template.ps1 -Stage replay -SnapshotRoot $root -WhatIf
```

- expected result（预期结果）—— `replay` 直接报错，提示必须先有 `diff`
- failure triage pointer（失败排查指针）—— 先看：
- `tools/codex-official-update-patch-replay-template.ps1` - replay 错误跳过 diff gate 时需要检查的脚本。
- `$root\checkpoint.json` - 应记录 diff stage 是否完成的 snapshot checkpoint 文件。

验证卡片 4 —— diff 未审批时 replay 被阻止

```powershell
$root = 'D:\PythonProject_langgraph\.tmp\verify-unapproved-diff'
if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
.\tools\codex-official-update-patch-replay-template.ps1 -Stage precheck -SnapshotRoot $root
.\tools\codex-official-update-patch-replay-template.ps1 -Stage diff -SnapshotRoot $root
.\tools\codex-official-update-patch-replay-template.ps1 -Stage replay -SnapshotRoot $root -WhatIf
```

- expected result（预期结果）—— `replay` 直接报错，提示必须满足 `approvals.diff_review.approved = true`
- failure triage pointer（失败排查指针）—— 先看：
- `tools/codex-official-update-patch-replay-template.ps1` - replay 错误跳过 diff approval 时需要检查的脚本。
- `$root\checkpoint.json` - 应记录 diff approval state 的 snapshot checkpoint 文件。

验证卡片 5 —— 缺少 `replay` 时 test 被阻止

```powershell
$root = 'D:\PythonProject_langgraph\.tmp\verify-missing-replay'
if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
.\tools\codex-official-update-patch-replay-template.ps1 -Stage precheck -SnapshotRoot $root
.\tools\codex-official-update-patch-replay-template.ps1 -Stage diff -SnapshotRoot $root -ApproveDiff
.\tools\codex-official-update-patch-replay-template.ps1 -Stage test -SnapshotRoot $root -WhatIf
```

- expected result（预期结果）—— `test` 直接报错，提示必须先有 `replay`
- failure triage pointer（失败排查指针）—— 先看：
- `tools/codex-official-update-patch-replay-template.ps1` - test stage 错误跳过 replay 时需要检查的脚本。
- `$root\checkpoint.json` - 应记录 replay 是否完成的 snapshot checkpoint 文件。

验证卡片 6 —— 决策行 override 跨 rerun 保留

```powershell
$root = 'D:\PythonProject_langgraph\.tmp\verify-decision-row-rerun'
if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
.\tools\codex-official-update-patch-replay-template.ps1 -Stage precheck -SnapshotRoot $root
.\tools\codex-official-update-patch-replay-template.ps1 -Stage diff -SnapshotRoot $root
# 手工编辑 $root\patch-decision-table.json
.\tools\codex-official-update-patch-replay-template.ps1 -Stage diff -SnapshotRoot $root
```

- expected result（预期结果）—— 第二次跑 `diff` 之后，JSON 里的人工 override 仍然保留
- failure triage pointer（失败排查指针）—— 先看：
- `$root\patch-decision-table.json` - 应保留人工 decision overrides 的 JSON decision table。
- `$root\patch-decision-table.csv` - 生成给 reviewer 友好检查用的 CSV companion decision table。
- `tools/codex-official-update-patch-replay-template.ps1` - decision table rerun 覆盖人工选择时需要检查的脚本。

验证卡片 7 —— `decision_locked` 落地后锁定行跨 rerun 保留

```powershell
$root = 'D:\PythonProject_langgraph\.tmp\verify-decision-lock-rerun'
if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
.\tools\codex-official-update-patch-replay-template.ps1 -Stage precheck -SnapshotRoot $root
.\tools\codex-official-update-patch-replay-template.ps1 -Stage diff -SnapshotRoot $root
# 手工在 $root\patch-decision-table.json 中设置 decision_locked=true
.\tools\codex-official-update-patch-replay-template.ps1 -Stage diff -SnapshotRoot $root
```

- expected result（预期结果）—— 设置了 `decision_locked = true` 的行在 rerun 后仍被保留
- failure triage pointer（失败排查指针）—— 先看：
- `$root\patch-decision-table.json` - rerun 后仍应保留 locked rows 的 JSON decision table。
- `tools/codex-official-update-patch-replay-template.ps1` - locked decision rows 未被保留时需要检查的脚本。

### Do not touch（不要顺手改）

- 这轮增量不要顺手去改官方 npm 安装产物里的 `oh-my-codex` runtime 文件
- 除非有明确理由，否则不要把这轮工作移出 repo-local（仓库本地） 实现层
- 在真正实现前，不要重写已经冻结的 contract（契约） 面

## 接手实施速览

如果看完命令卡片后还需要上下文，再读这一节。

### 现在做到哪

- operator-surface maintenance lane（操作员控制面维护支线） 已经处于可继续状态
- `tools/codex-official-update-patch-replay-template.ps1` 已经实现
- 该脚本当前已经支持：
  - staged execution（分阶段执行）
  - checkpoint continuity（检查点续接）
  - decision-table exports（决策表导出）
  - hard stage gates（硬性阶段门禁）
- 已冻结的 decision lock + diff approval（决策锁定 + diff 审批）增量已经在 `tools/codex-official-update-patch-replay-template.ps1` 中落地

### 最新增量已落地什么

已冻结的 decision lock + diff approval（决策锁定 + diff 审批）增量已经落地到 `tools/codex-official-update-patch-replay-template.ps1`。

已落地项：

- `decision_locked` —— 决策锁定位字段，用来阻止脚本覆盖人工冻结的决策行
- `decision_lock_reason` —— 决策锁定原因字段，用来说明为什么锁住该行
- `approvals.diff_review` —— checkpoint 审批区块，用来记录 diff 审查是否显式通过
- `approved` —— 布尔字段，用来表示 diff 审查通过
- `approved_at` —— 时间字段，用来记录 diff 审查通过时间
- `approval_note` —— 审批备注字段，用来记录简短审查说明
- `-Stage diff -ApproveDiff` —— 命令形式，用来把 diff 审批写回 checkpoint manifest
- `replay requires approvals.diff_review.approved = true` —— 已落地的更严格 replay 门禁

## 从项目级启动摘要下放下来的易漂移仓库上下文

当前主线工作阶段快照：

- 初始 LangGraph 深化队列已经收口
- 更早一轮 capability-gap sync pass 也已经收口
- 当前活跃的命名仓库主线仍然是 `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`
- 该主线下当前活跃的维护支线，是 operator-surface update / diff / replay / gate（操作员控制面更新 / 差异检查 / 重放 / 门禁） 工作

为冷启动保留下来的历史 rollout 上下文：

- bounded graph-kernel rollout 已收口
- bounded primary-runtime engine rollout 已收口
- bounded compiled-invocation rollout 已收口
- bounded live-execution rollout 已收口
- generalized live-routing rollout 已收口
- subgraph persistence and state-inspection rollout 已收口
- fuller live primary-execution-engine rollout 已收口
- richer automatic runtime-policy rollout 已收口
- broader automatic runtime-policy rollout 已收口
- deeper live primary-engine rollout 已收口
- superstep live primary-engine rollout 已收口
- stateful live primary-engine rollout 已收口
- graph-resident live primary-engine boundary-state rollout 已收口
- subgraph-aware live primary-engine handoff-state rollout 已收口
- approval-aware live primary-engine resume-state rollout 已收口
- post-approval-aware-resume-state capability-gap sync pass 已收口
- recovery-aware live primary-engine provenance-state rollout 已收口
- durable-artifact-aware live primary-engine state rollout 已收口
- post-durable-artifact-aware capability-gap sync pass 已收口
- reducer-aware live primary-engine merge-state rollout 已收口
- post-reducer-aware capability-gap sync pass 已收口
- command-aware live primary-engine control-state rollout 已收口
- post-command-aware capability-gap sync pass 已收口
- runtime-aware live primary-engine context-store-state rollout 已收口
- post-runtime-aware capability-gap sync pass 已收口
- memory-aware live primary-engine semantic-state rollout 已收口
- post-memory-aware capability-gap sync pass 已收口
- migration-aware live primary-engine compatibility-state rollout 已收口

从原项目级启动摘要继承下来的当前执行优先级：

1. 同步双语 LangGraph capability-gap appendix，使其反映已验证的 post-migration-aware 状态
2. 让 startup-facing repository summaries 与已归档的 migration-aware 工作、以及当前 operator-surface 维护支线保持一致
3. 只保留真实仍未完成的 post-migration-aware gap 叙述
4. 在打开后续 LangGraph 深化主线前，先用 OpenSpec 验证收口当前 sync pass

## 本会话留下的实施背景

本会话已经完成以下 repo-local（仓库内本地） 冷启动承接面：

- 在 `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md` 中标准化了 **official update + diff check + local patch replay（官方更新 + 差异检查 + 本地补丁重放）** 工作流
- 实现了 `tools/codex-official-update-patch-replay-template.ps1`
- 给该脚本增加了分阶段执行：
  - `precheck` —— 预更新盘点阶段
  - `update` —— 官方更新阶段
  - `diff` —— 更新后审查阶段
  - `replay` —— 补丁重放阶段
  - `test` —— 回归验证阶段
  - `all` —— 端到端便捷阶段
- 增加了 checkpoint（检查点） 串接能力：
  - 最新 pointer 文件：`.tmp/official-update-patch-replay-latest.json`
  - 单轮 checkpoint manifest：`<snapshot-root>/checkpoint.json`
- 增加了冷启动产物：
  - `report.json` —— 机器可读运行摘要
  - `checklist.md` —— 人工可读运维清单
  - `patch-decision-table.md` —— Markdown 审查视图
  - `patch-decision-table.json` —— JSON 回读真源
  - `patch-decision-table.csv` —— 表格友好的导出视图
- 增加了机器可读 decision row（决策行） 状态 `decision_status`：
  - `auto_prefilled` —— 脚本自动预填的默认决策
  - `manually_overridden` —— 人工改写过的决策
  - `unresolved` —— 仍等待人工明确决策的状态
- 增加了当前已经实现的硬性阶段门禁：
  - 没有 `precheck` -> `update / diff / replay / test` 全部阻止
  - 没有 `diff` -> `replay / test` 阻止
  - 没有 `replay` -> `test` 阻止
- 更新了双语 Appendix C（附录 C） 文本，让关键术语和变量名后面都带有简短解释，而不再只是裸名字

## 已冻结、可直接进入实现的下一轮 change 详细清单

下面这些 change 已经在双语文档中冻结，并且**当前脚本里已经落地**：

- `decision_locked` —— 决策锁定位字段，用来阻止脚本覆盖人工冻结的决策行
- `decision_lock_reason` —— 决策锁定原因字段，用来说明为什么锁住该行
- `approvals.diff_review` —— checkpoint 审批区块，用来记录 diff 审查是否显式通过
- `approved` —— 布尔字段，用来表示 diff 审查通过
- `approved_at` —— 时间字段，用来记录 diff 审查通过时间
- `approval_note` —— 审批备注字段，用来记录简短审查说明
- `-Stage diff -ApproveDiff` —— 命令形式，用来把 diff 审批写回 checkpoint manifest
- `replay requires approvals.diff_review.approved = true` —— 已落地的更严格 replay 门禁

## 当前 change 准入结论

从实现与文档侧来看，这轮冻结增量已经落地并保持对齐：

- 范围已经冻结
- 中英文启动摘要已对齐
- 关键术语与变量名都带了简短解释
- 最新实现目标已经落地

这意味着：新会话如果继续这条维护支线，**不需要先重新开设计讨论**，可以直接进入后续维护或验证。

## 新会话下一步怎么做

如果新会话要继续这条维护支线，按下面顺序做：

1. 先读本文
2. 再读 `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md`
3. 如果还需要后续工作，先检查 `tools/codex-official-update-patch-replay-template.ps1` 中已落地的 decision-lock + diff-approval 行为
4. 保持双语 Appendix C 文本为 implemented（已实现）口径
5. 重新跑 smoke check（冒烟检查）：
- `precheck -> diff` - 用于验证 precheck-to-diff progression 的 smoke-check stage sequence。
   - 缺少前置阶段时 replay 的阻止逻辑
   - 缺少 replay 时 test 的阻止逻辑
   - JSON 决策行跨轮 rerun（重复运行）时的人工覆盖保留逻辑

## 重要防漂移说明

- 本会话**没有**修改官方 npm 安装产物中的 `oh-my-codex` runtime 文件
- 本会话聚焦的是 repo-local 工具脚本与 startup-facing 文档
- PowerShell 里看到中文偶尔乱码，这是终端输出编码问题，不是源文件损坏信号
