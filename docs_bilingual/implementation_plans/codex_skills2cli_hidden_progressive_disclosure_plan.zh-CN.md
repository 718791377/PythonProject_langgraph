---
doc_id: codex_skills2cli_hidden_progressive_disclosure_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/codex_skills2cli_hidden_progressive_disclosure_plan.md
translation_of: docs_bilingual/implementation_plans/codex_skills2cli_hidden_progressive_disclosure_plan.md
status: active
doc_class: implementation_plan
change: implement-skills2cli-hidden-progressive-disclosure
created_at: 2026-06-30
plan_readiness: implemented-local-runtime
implementation_lane: local-main-first
---

# Skills2CLI 隐藏库渐进披露计划

> 给 agentic workers：当前主 Codex CLI 会话保持 leader。只有在执行切片互不重叠时才使用 native experts 或 durable lane；skill/profile helper 调用只是流程上下文，不是 native expert 证据。

**目标：** 在不把隐藏库整体恢复到 model-visible skills 列表的前提下，让 Codex 能按任务需要发现并只读加载隐藏的 standalone user skills，并使用真实使用证据生成可见性调整建议。

**架构：** Phase A 冻结这份 OpenSpec-backed 方案。Phase B 扩展 `skills2cli`，增加 hidden-skill index/search/show/load、usage event、visibility recommendation，以及一天最多一次、用户手动触发、receipt-backed 的 `apply-recommendations`。

**技术栈：** Python `skills2cli.py`、用户级 Codex state 目录下的 JSONL usage events、receipt-backed standalone user-skill 移动、OpenSpec、本地 CI、本地 MR review。

---

## 当前状态

<!-- CURRENT_STATUS_START -->

- 本方案已完成 `implement-skills2cli-hidden-progressive-disclosure` 的本地 runtime 实施，其 OpenSpec change 已在本地归档。
- 用户已锁定默认策略：
  - hidden skill 加载边界：只读 soft-load；
  - 动态可见性调整：高置信自动选择，但只能在用户手动触发命令后执行；
  - 渐进披露检索范围：当前可见 skills 加上 `skills2cli` 隐藏库。
- 2026-06-30 观察到的隐藏库基线：`C:\Users\lenovo\.codex\state\skills2cli\visibility-disabled` 下有 989 个隐藏 `SKILL.md`。
- `grill-me` 存在于隐藏库，目录名为 `mattpocock-skills-skills-productivity-grill-me-skill-md`。
- `stop-slop` 不是当前已安装 skill 名称；先作为 alias 指向 `ai-slop-cleaner`。
- Runtime 实施和归档均为本地范围；未授权远端发布。

<!-- CURRENT_STATUS_END -->

## 1. 意图与安全边界

隐藏库是可回滚的可见性库，不是垃圾目录。隐藏 skill 可以通过只读取一个选中的 `SKILL.md` 注入当前任务上下文来使用，而不必恢复为全局可见。

非目标：

- 不恢复全部隐藏 skills。
- 不编辑 plugin cache 或 vendor `SKILL.md`。
- 不编辑 `C:\Users\lenovo\.codex\config.toml`。
- 不把 hidden skill loading 当作 native expert 或 subagent 证据。
- 不后台或定时运行 promote/demote。
- 本实施流程不推送 GitLab/GitHub。

所有 hidden 和 recommendation 命令必须输出安全标志：

- `mutates_config=false` - no Codex config mutation.
- `edits_plugin_cache=false` - no plugin or vendor cache mutation.
- `profile_apply_performed=false` - no profile apply or hard-load action.
- `global_restore_performed=false` - no global hidden-library restore.

## 2. Hidden skill 渐进披露 runtime

给 `skills2cli` 增加 `hidden` 命令组：

```powershell
skills2cli hidden index --json
skills2cli hidden search <query> --json
skills2cli hidden suggest --query "<task summary>" --json
skills2cli hidden show <hidden_skill_id> --json
skills2cli hidden load <hidden_skill_id> --json
```

行为：

- `hidden index`、`hidden search`、`hidden suggest`、`hidden show` 只返回紧凑元数据。
- `hidden load` 返回一个选中 `SKILL.md` 的内容，并记录 usage event。
- 如果 body 超过 CLI body limit，`hidden load` 返回 chunk 和 `next_chunk_command`。
- `visibility_state=hidden` - means the candidate remains in the hidden library and was not restored globally; Hidden commands still search both visible skills and hidden skills.
- soft-load 期间 runtime 不得把 hidden skills 放回 `C:\Users\lenovo\.codex\skills`。

初始 alias：

- `grill-me` -> `mattpocock-skills-skills-productivity-grill-me-skill-md`
- `stop-slop`、`deslop`、`anti-slop` -> `ai-slop-cleaner`

## 3. 使用证据与可见性建议

每次 `hidden load` 向以下文件写入一条 JSONL event：

```text
C:\Users\lenovo\.codex\state\skills2cli\usage-events.jsonl
```

Event 字段：

- `schema_version` - usage-event schema version.
- `event_id` - unique usage-event id.
- `timestamp` - hidden soft-load timestamp.
- `event_type=hidden_load` - marks the record as hidden skill soft-load.
- `hidden_skill_id` - stable hidden-library skill id.
- `frontmatter_name` - skill name parsed from YAML frontmatter.
- `query_hash` - hash of the triggering query or task text.
- `matched_alias` - alias that matched the hidden skill.
- `confidence` - routing confidence for the hidden skill.
- `batch_id` - optional batch id for related usage events.
- `body_sha256` - hash of the returned body or chunk.
- `body_bytes` - byte size of the returned body or chunk.
- `raw_paths_retained=false` - no raw local paths retained in usage events.

新增 recommendation 命令：

```powershell
skills2cli visibility recommend --days 30 --json
skills2cli visibility apply-recommendations --receipt <recommendation_id> --apply --operator-confirmation --json
```

建议规则：

- promote candidate：30 天 hidden load 次数至少 10 次，或连续两周每周至少 3 次，或未来 operator 显式 pin。
- demote candidate：当前可见 standalone user skill 在窗口内 0 次强使用证据，且不是 protected/core，并且可以移动到 visibility library。
- keep-soft-load：hidden skill 最近有 1 到 9 次 load，但未达到 promote 阈值。

Apply 规则：

- operator 必须手动调用 `apply-recommendations`；系统可以提醒，但不允许后台自动触发。
- apply 每个本机日期最多执行一次。
- 每次最多移动 3 个 standalone user skills。
- 每次移动前写 rollback receipt，并在每个移动后更新 receipt。
- 任一移动失败立即停止并报告 partial state。

<!-- TASK_BACKLOG_START -->

- [x] 冻结双语 implementation plan。
- [x] 创建 OpenSpec proposal/design/tasks/management/spec 包。
- [x] 在 docs registry 中登记双语方案。
- [x] 验证 Phase A 并合入本地 main。
- [x] 实现 hidden progressive disclosure runtime。
- [x] 增加 usage events 与人工 recommendation apply runtime。
- [x] 验证 Phase B、归档 OpenSpec 并合入本地 main。

<!-- TASK_BACKLOG_END -->

## 4. 实施切片

Phase A 方案冻结切片：

- 创建本双语方案。
- 创建 OpenSpec proposal、design、tasks、management 与 delta spec。
- 在 `docs_bilingual/docs_registry.yaml` 注册方案。
- 验证并把 plan-freeze package 合入本地 `main`。

Phase B runtime 切片：

- 实现 hidden index/search/show/load 与 alias routing。
- 实现 JSONL usage events 与 visibility recommendations。
- 实现用户手动触发、一天一次、rollback-receipt backed 的 `apply-recommendations`。
- 增加测试与 checker 覆盖。
- archive OpenSpec change，并把 runtime package 合入本地 `main`。

## 5. 验收标准

- `skills2cli hidden search grill-me --json` 找到隐藏库中的 `grill-me` adapter。
- `skills2cli hidden search stop-slop --json` 通过 alias 解析到 `ai-slop-cleaner`。
- `skills2cli hidden load <id> --json` 返回一个 skill body，写入 usage event，且不恢复为全局可见。
- `skills2cli visibility recommend --days 30 --json` 输出 promote、keep-soft-load、demote buckets 和脱敏证据。
- `skills2cli visibility apply-recommendations --receipt <id> --apply --operator-confirmation --json` 是 manual-only、一天一次、最多 3 个移动，并有 rollback receipt。
- 每次本地 `main` 集成前通过本地验证、OpenSpec guard、本地 CI 与 local MR review。

## 证据索引

<!-- EVIDENCE_INDEX_START -->

- `openspec/changes/archive/2026-06-30-implement-skills2cli-hidden-progressive-disclosure/` - 本方案的 archived OpenSpec change。
- `tools/skills2cli.py` - runtime 实现目标。
- `test/skills2cli.test.py` - hidden 命令与 recommendation 行为的聚焦测试目标。
- `docs_bilingual/docs_registry.yaml` - 双语方案登记。

<!-- EVIDENCE_INDEX_END -->
