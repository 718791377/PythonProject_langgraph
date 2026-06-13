---
doc_id: recent_manual_workflow_packaging_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/recent_manual_workflow_packaging_plan.md
source_prompt: reference_files/5.md
---

# 近期重复手工工作流打包方案

> **给 agentic workers：** 使用 `superpowers:executing-plans`。本方案把 `reference_files/5.md` 固化为项目级、证据优先、脱敏的工作流打包流程；弱证据不得提升为用户级安装或定时自动化。

## 目标

读取最近 30 天（不足则使用可用历史）的 Codex 工作、memory/rollout 摘要、Chronicle 发现信号和已有 skills/agents/automations inventory，识别值得打包的重复手工流程，输出短名单，并只创建高置信、缺口明确、窄而可验证的资产。

## 架构

新增 repo-local skill 作为人工/agent 可复用 playbook，新增 CLI 报告脚本作为自动化发现面。脚本只读取本仓库与用户级 inventory 的脱敏聚合信息，不提交原始会话、原始日志或私有路径全文。Chronicle 如未安装或不可用，必须记录 `not_enabled`，不得伪造外部发现证据。

## 技术栈

Markdown implementation plan、repo-local `.agents/skills`、Python CLI、Git history、`docs_bilingual/memory`、`docs_bilingual/implementation_plans`、用户级 skills/agents inventory、local gate、local MR review、本地 main 优先合入流程。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: planned
Stage: plan committed before implementation.
Owner session: `implement-recent-manual-workflow-packaging-20260613`.
Source prompt: `reference_files/5.md`.
Runtime boundary: project-level source-of-truth skill, CLI, and sanitized memory output; user-level wrapper/config is recorded only as a future candidate; no user-level install, no scheduled task, no Chronicle mutation, no remote publication.
Last updated: 2026-06-13
<!-- CURRENT_STATUS_END -->

## 证据顺序

1. 最近 Codex sessions 与任务摘要：优先使用本仓库 Git commit 主题、已提交 memory、implementation plan 当前状态和可运行审计脚本的聚合输出。
2. Codex Memories 与 rollout summaries：读取 `docs_bilingual/memory/` 下的周报、收尾证据、主线摘要和相关 memory 文档。
3. Chronicle：只用于发现；当前机器如果没有 Chronicle 命令或数据目录，记录为 `not_enabled`。
4. Existing skills、custom agents、automations：读取 repo-local 与 user-level skills/agents inventory，避免重复创建已有能力。

## 候选准入规则

候选必须同时满足：

- 至少发生两次，或明显会复发且重复成本高；
- 输入稳定、步骤可复现、输出或停止条件清楚；
- 会显著提升速度、质量、一致性或可靠性；
- 现有 skill、custom agent 或 automation 没有充分覆盖。

不满足以上规则时只能进入 `skip` 或 `needs_more_evidence`，不能创建资产。

## 用户级 / 项目级封装判断

| 封装层级 | 本轮决策 | 理由 | 交付物 |
| --- | --- | --- | --- |
| 项目级通用 | 立即实现 | 需要读取本仓库 Git、memory、implementation plans、OpenSpec/local gate 证据；本仓库是 source of truth，最适合先沉淀可测试规则。 | repo-local skill、Python CLI、脱敏 memory 短名单、方案证据。 |
| 用户级候选 | 只记录候选，不直接安装 | 该流程跨项目可复用，但用户级 wrapper/config 必须依赖已稳定的项目级 CLI，并需要单独授权、rollback 与 smoke。 | 在短名单中输出 `extend-user-level-wrapper` 候选与后续安装条件。 |
| 不封装 | 本轮跳过 | custom subagent 已由现有 analyst/planner/writer/verifier 覆盖；scheduler、Chronicle 写入和外部动作会扩大权限与隐私面。 | 在短名单 `deliberately skipped` 中记录原因。 |

判定规则：默认先项目级；只有当同一工作流跨两个以上项目复用、输入不依赖单仓库私有结构、CLI 输出已脱敏且具备 rollback/smoke 证据时，才提升为用户级 wrapper/config；任何外部动作或定时执行都需要单独方案与授权。

## 输出形式选择

| 推荐形式 | 使用条件 | 本轮默认 |
| --- | --- | --- |
| Skill | 可复用工作流/playbook，适合人工或 agent 按步骤执行 | 对本方案本身创建项目级 repo-local skill |
| Custom subagent | 边界清晰的专家角色或调查任务，适合委派 | 跳过；现有 analyst/planner/writer/verifier 已覆盖 |
| Automation | 定期检查、报告、提醒或监控 | 创建手动 CLI；不创建 scheduler |
| Extend existing | 已有资产覆盖大部分需求，只需扩展 | 如发现重叠优先扩展 |
| Skip | 一次性、敏感、证据弱或太宽泛 | 必须显式记录原因 |

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] 读取 `reference_files/5.md`。
- [x] 非破坏性盘点已有 audit、skills、agents 与 memory 表面。
- [x] 新增双语 implementation plan，并记录用户级/项目级封装判断。
- [ ] 提交方案 commit，运行本地门禁并合入 local `main`。
- [ ] 新增项目级 repo-local skill 与 CLI。
- [ ] 生成脱敏短名单 memory，并记录用户级 wrapper/config 候选条件。
- [ ] 运行实现门禁，提交实现 commit，并合入 local `main`。
<!-- TASK_BACKLOG_END -->

## 实施切片

### Slice 1：方案冻结

- [x] 读取 `reference_files/5.md`。
- [x] 非破坏性盘点已有 audit、skills、agents 与 memory 表面。
- [x] 新增本双语 implementation plan。
- [ ] 提交方案 commit，运行本地门禁并合入 local `main`。

### Slice 2：Skill 与 CLI

- [ ] 新增 `.agents/skills/recent-workflow-packaging/SKILL.md`。
- [ ] 新增 `tools/report_recent_manual_workflow_candidates.py`。
- [ ] CLI 支持 `--root`、`--days`、`--output`、`--json`。
- [ ] CLI 输出短名单、已创建/扩展、刻意跳过、需更多证据四类信息。
- [ ] CLI 对 Chronicle 不可用时输出 `Chronicle: not_enabled`。

### Slice 3：证据输出与验证

- [ ] 生成 `docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.md`。
- [ ] 生成 `docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.zh-CN.md`。
- [ ] 运行脚本 smoke、precommit update/archive、OpenSpec guard、local gate、local MR review。
- [ ] 提交实现 commit，合入 local `main`，停止在远端发布门禁。

## 验收标准

- 脚本能在无 Chronicle 环境中成功生成脱敏 Markdown 与 JSON。
- 短名单每项包含 repeated workflow、supporting evidence/dates、frequency/confidence、recommended form、why worth/not worth creating。
- 本轮创建的缺口资产只有项目级 repo-local skill 与手动 CLI 自动化；用户级 wrapper/config 只记录候选条件，未授权用户级安装和 scheduler。
- 所有新增文件通过本地 precommit/update/archive 检查、OpenSpec guard、local gate 与 local MR review。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- Pending implementation evidence: shortlist memory will be generated in Slice 3 after the CLI exists.
<!-- EVIDENCE_INDEX_END -->

## 非目标

- 不读取或提交原始 Codex transcripts、原始 runtime logs 或 raw Chronicle 数据。
- 不修改 `C:\Users\lenovo\.codex\config.toml`、用户级 skill 安装或 native agent TOML。
- 不自动发送外部消息、不操作浏览器/GUI、不发布远端。
- 不把低置信候选扩展成宽泛“大而全”技能。
