---
doc_id: codex_skills2cli_budget_compaction_runtime_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/codex_skills2cli_budget_compaction_runtime_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/codex_skills2cli_budget_compaction_runtime_plan.md
status: active
doc_class: implementation_plan
created_at: 2026-06-26
---

# Skills2CLI 预算与上下文压缩运行时方案

## 摘要

本方案修复长会话上下文压缩后暴露的 Codex skills 上下文预算警示路径：

```text
Exceeded skills context budget of 2%. All skill descriptions were removed and 1111 additional skills were not included in the model-visible skills list.
```

执行采用 local-main-first，并拆成两个本地集成包：

1. 冻结本方案并合入本地 `main`。
2. 按冻结方案实现 live runtime、checker 与测试，再合入本地 `main`。

运行时保持 preview-first：可以诊断、路由、soft-load、生成可见性候选，但不得自动修改用户级 `config.toml`、plugin cache、远端 refs 或 standalone skills。

## 当前状态

<!-- CURRENT_STATUS_START -->

- Phase A 方案冻结包正在本地 worktree `docs/skills2cli-budget-compaction-plan` 中准备。
- Phase B runtime 实施尚未开始。
- 远端发布未授权。

<!-- CURRENT_STATUS_END -->

## 任务队列

<!-- TASK_BACKLOG_START -->

- [x] 诊断当前 budget-warning 路由和 skills 分层数量。
- [x] 将本实施方案冻结为 Phase A 本地集成包。
- [ ] 实现 `core-dev.skills-budget-triage` 路由元数据。
- [ ] 实现 budget-warning intent 检测与 standalone skill-pressure 报告。
- [ ] 扩展 checker / test，并将 runtime 包集成本地 `main`。

<!-- TASK_BACKLOG_END -->

## 证据索引

<!-- EVIDENCE_INDEX_START -->

- 基线命令：`python -X utf8 tools/skills2cli.py profile suggest --query "上下文压缩后 skills context budget 超限 1111 additional skills" --json`。
- 基线发现：`web-saas` 当前在 budget-warning query 中排在 `core-dev` 前。
- 基线命令：`python -X utf8 tools/skills2cli.py index --json`。
- 基线发现：skills 分层数量为 `user=1009`、`plugin=364`、`repo=29`、`system=5`。

<!-- EVIDENCE_INDEX_END -->

## 当前证据

- 命令 `skills2cli profile suggest --query "上下文压缩后 skills context budget 超限 1111 additional skills" --json` 当前会把 `web-saas` 排在 `core-dev` 之前，原因是 query 没有命中预算专用场景词时，历史 audit usage boost 压过了场景路由。
- 命令 `skills2cli index --json` 当前报告 `1407` 个 skills：`user` 层 `1009`，plugin 层 `364`，repo 层 `29`，system 层 `5`。
- 反复 apply `core-dev` plugin profile 不足以解决问题。plugin profile hard-load 可以降低 plugin surface，但当前预算压力主要来自 standalone user-level skills，以及 compaction 时重新注入的 model-visible skills surface。

## 设计规则

- budget、compaction、loader、skills surface 警示属于 Codex runtime / developer workflow 排障，不是 Web/SaaS 工作。
- 这些警示必须路由到 `core-dev` 和专用 `core-dev.skills-budget-triage` task module。
- audit usage evidence 只能在场景路由和安全门之后提供 boost，不得覆盖明确的 budget-warning intent。
- `full` 仍然只允许显式请求和排障场景使用，不得成为普通 warning triage 的 top-1。
- standalone user skills 与 plugin profiles 分开治理。runtime 可以生成可见性降低的 preview candidate，但 apply 必须后续显式授权、备份且可回滚。
- skills/profile helper 输出只是 workflow context，不是 native expert / subagent evidence。

## Runtime 实施内容

### Profile registry

更新 plugin-modules profile registry，新增：

- `core-dev.skills-budget-triage` - 用于 skills 预算与上下文压缩警示排障的 task module，路由词包括：
  - `skills context budget` - 英文 canonical 预算警示短语。
  - `Exceeded skills context budget` - Codex 预算警示前缀。
  - `All skill descriptions were removed` - 描述被移除的警示短语。
  - `additional skills were not included` - skills 被省略的警示短语。
  - `compaction` - 长会话上下文压缩触发词。
  - `context compacted` - 已压缩会话触发词。
  - `skill descriptions removed` - compact loader 症状。
  - `上下文压缩` - 中文上下文压缩短语。
  - `技能预算` - 中文 skill budget 短语。
  - `技能上下文预算` - 中文 skill context budget 短语。
- `skills-budget-triage` - 目标为 `core-dev` 且语义为 `soft-load` 的 scenario profile。
- 无关 profile 的负样本 - 防止 budget-warning 文本误路由到 `web-saas`、`company-ops`、`market-research`、`customer-comms` 或 `creative-content`。

### `skills2cli.py`

扩展 profile suggestion 与 audit 输出：

- 在 audit boost 前识别 budget / compaction warning query。
- 检测到 budget-warning intent 时，强约束或强 boost 到 `core-dev` / `core-dev.skills-budget-triage`。
- JSON 输出报告 `budget_warning_intent`、layer counts 和 standalone user-skill pressure。
- 如果 `core-dev` hard-load preview 已经是 `changed=false`，提示“重复 apply plugin profile 不是主要修复点”。
- 输出仍必须报告 `mutates_config=false`、`profile_apply_performed=false`、`edits_plugin_cache=false`，且不包含 raw skill bodies。

### Visibility preview

新增 preview-only standalone visibility 报告：

- 统计并摘要 user-level standalone skills。
- 区分可能常驻的 core skills 与 profile/task-specific skills。
- 只输出 JSON/Markdown 候选动作，不修改文件系统。
- 后续必须有显式 apply receipt 才能改变任何 user-level skill visibility 机制。

### Checkers 与测试

扩展 checker 覆盖：

- 中文和英文 budget-warning query 必须 top-1 选择 `core-dev`。
- selected result 必须包含 `skills-budget-triage` task-module evidence。
- `web-saas` 不得在 skills budget 或 compaction warning query 中 top-1。
- `full` 除非显式请求，否则必须 excluded。
- 当 user 层 skills 数量主导总量时，必须报告 standalone-skill pressure。
- profile suggestion 命令不得修改 config 或 plugin cache。

## 协同与执行

- Phase A 是方案冻结包，可由主会话执行，并在可用时使用只读 expert review。
- Phase B 是多切片实现，应使用最小充分协同面：
  - profile registry 更新。
  - `skills2cli.py` routing / audit / runtime 输出。
  - checker / test 更新。
  - 集成验证。
- 如果 native expert spawn 被阻塞或不可用，记录 blocker 并由主会话接管。不得把 timeout 或缺失 expert 输出当成有效证据。
- durable team 只允许在本方案冻结且存在至少两个独立写入切片后启动。一次 durable task 只使用一个 backend family。

## 测试计划

至少运行：

```powershell
python -X utf8 tools/skills2cli.py profile suggest --query "上下文压缩后 skills context budget 超限 1111 additional skills" --json
python -X utf8 tools/skills2cli.py profile suggest --query "Codex compaction exceeded skills context budget additional skills removed" --json
python -X utf8 tools/skills2cli.py audit warnings --since 2026-06-25 --limit 20 --json
python -X utf8 tools/check_skills2cli_profile_routing.py --root . --json
python -X utf8 tools/run_openspec_guard.py --root .
powershell -NoProfile -File tools/ci/local_gate.ps1
powershell -NoProfile -File tools/ci/local_mr_review.ps1
```

验收标准：

- budget / compaction warning query top-1 选择 `core-dev`。
- selected output 包含 budget-triage scenario 或 task module。
- layer counts 明确暴露 user-level standalone skills 是主要压力来源。
- 除非后续显式 apply，否则 runtime 保持 preview / advisory-only。
- Phase A 与 Phase B 两个包都在 gate 通过后进入本地 `main`。

## 非目标

- 不推送 GitLab/GitHub，不创建/更新/合并 MR，不同步远端。
- 不批量编辑 plugin cache。
- 不自动修改 `config.toml`。
- 本轮不删除、移动或禁用 user-level standalone skills。
- 不声称 profile helper 是 native expert evidence。
