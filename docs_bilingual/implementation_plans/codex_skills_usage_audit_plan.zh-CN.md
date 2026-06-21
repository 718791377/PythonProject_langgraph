---
doc_id: codex_skills_usage_audit_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
translation_of: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
status: active
doc_class: implementation_plan
created_at: 2026-05-16
last_reviewed: 2026-06-21
plan_readiness: final-review-pending
implementation_lane: audit_only_profile_decision_support
related_docs:
  - docs_bilingual/implementation_plans/codex_user_level_skills_governance_and_profiles_plan.zh-CN.md
  - docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md
  - docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md
runtime_sources:
  - tools/audit_codex_skills_usage.py
  - tools/skills2cli.py
  - tools/check_skills_audit_output_retention.py
  - tools/check_skills_audit_final_review_state.py
  - tools/check_skills_audit_final_review_precheck.py
  - tools/check_skills_audit_cadence_contract.py
  - tools/check_precommit_update_archive.py
---
# Codex Skills Usage Audit 计划

> **给 agentic workers：** 本方案是 audit-only 实施方案。使用最小充分的本地实施面，所有 profile 变更都必须保持 preview-only；任何报告在作为证据前都必须通过字段契约。除非后续任务获得明确 apply 授权，否则不得编辑 Codex `config.toml`、plugin cache 或 hard-load profile。

**Goal：** 通过 30 天、基于证据的审计，判断 Codex skills/plugin 使用情况与实时 `2% skills context budget` warning 压力，确保默认 profile 决策安全、可逆、不是靠猜测。

**Architecture：** 仓库内 Python 审计脚本读取用户级 Codex sessions、runtime logs、用户级 plugin 状态、profile registries、manual notes 与仓库 gate 输出；生成本地 JSON 报告、脱敏 Markdown 摘要、preview-only candidate records 与 embedded field contracts。Retention 与 pre-commit gate 防止原始审计产物或不完整报告成为提交证据。

**Tech Stack：** Python audit CLI、JSON report schema、sanitized Markdown renderer、SQLite runtime-log reader、Codex session JSONL reader、profile registry reader、manual-note parser、privacy redactor、output-retention checker、pre-commit update/archive checker、CI manifest、OpenSpec guard。

---

## 0. 复核结论

本方案状态为 active，并继续保持 audit-only。本次 Comet 结构重构不授权 hard-load/profile apply，也不改变实施边界：现有脚本、checker、report contract、retention 与 candidate-preview 规则仍是执行层 source of truth。本次重构将治理原则、运行时/数据源架构、CLI 契约、字段契约、实施切片、任务级 backlog、本地集成、验收证据和长期监控事项拆开，便于后续按 /comet 方式执行与复核。

`soft-load` 后 Codex 启动阶段 warning 消失，是启动压力改善的有用证据，但不能证明 live-turn skills-budget warning 不会再次出现。会话中 warning 必须通过审计脚本 triage，而不是删除 plugin cache 或过早收缩默认 profile。

节奏定稿：原始 30 天观察窗口锁定为 2026-05-16 至 2026-06-15。标准计划内审计运行次数为 Day 0 baseline 1 次、每 7 天 weekly evidence 4 次、Day 30 final evidence 1 次。Warning triage 是事件触发流程，不设固定重复次数。2026-06-15 之后的任何新增运行都只属于 post-final monitoring evidence，不得延长原始审计窗口，也不得授权 profile apply。

完整性复核：

| 检查项 | 结论 | 本方案落点 |
| --- | --- | --- |
| 会话中 warning 解释 | 完整 | 第 3、10 节 |
| soft-load / hard-load / vendor cache 边界 | 完整 | 第 3、10 节 |
| 证据分级与决策阈值 | 完整 | 第 4 节 |
| audit-only 安全与禁止自动 apply | 完整 | 第 3、10 节 |
| JSON 报告字段契约 | 完整 | 第 7 节 |
| 隐私、留存与输出门禁 | 完整 | 第 9 节 |
| 候选 preview 与 rollback path | 完整 | 第 10 节 |
| 具体实施 backlog | 完整 | 第 12 节 |
| 长期监控事项 | 按设计保持未闭环 | 第 17 节 |

## 1. 目标与非目标

本计划建立一个 30 天 audit-only 流程，用事实数据决定后续 profile apply 策略，避免误禁用仍有长期价值的 plugin skills。

审计回答四个问题：

1. 哪些 skills/plugins 在最近 30 天有强使用证据？
2. 哪些模块只是被提到，但没有被调用或读取？
3. 哪些 `2% skills context budget` 警示发生在什么时间、什么会话或什么项目上下文？
4. 哪些能力应常驻、按项目 hard-load、按需 soft-load，或仅保留在 `full` 临时排障 profile？

非目标：

- 30 天审计期间不执行 hard-load profile apply。
- 审计报告运行过程中不修改用户级 Codex `config.toml`。
- 不为降低 warning 压力批量编辑 vendor/plugin `SKILL.md`。
- 不把 disabled plugins 视为 deleted；dormant 能力必须保留可恢复路径。
- 不把弱提及或静态 registry 条目当成 apply 证据。
- 不发布原始 audit JSON、原始 transcripts、私有路径或 vendor cache 内容。

## 2. Comet workflow 映射

本方案把 Comet 作为控制模型，但不把审计流程变成 profile-apply workflow。

| Comet 关注领域 | 审计解释 | 退出证据 |
| --- | --- | --- |
| Open / Initiating | 冻结审计目标：skills-budget warning 压力与 usage evidence。 | Baseline command、data-source list、audit-only safety statement。 |
| Design / Planning | 定义证据分级、字段契约、隐私边界与决策阈值。 | 本方案与双语 companion。 |
| Build / Executing | 以小步本地分支实施或细化 audit script/checkers/tests。 | 本地提交、测试、field contracts 与 guard outputs。 |
| Verify / Controlling | 运行 reports、retention checks、precommit update/archive checks、CI 与 local MR review。 | 通过的 report field contract 与 gate outputs。 |
| Archive / Closing | 真实观察期结束后关闭审计或进入 candidate gate。 | `closed-no-change` 或 preview-only profile candidate evidence。 |
| Monitoring | 处理 live warnings、漏跑 weekly reports、隐私失败与例外。 | 窄窗口 triage report、cadence markers、pause/closure blockers 或 rollback plan。 |

Monitoring 不是第六个实施阶段，而是控制回路：当 evidence、privacy、warning pressure 或 cadence 变化时，它可以把审计返回到 planning 或 execution。

## 3. Runtime 治理原则

`⚠ Exceeded skills context budget of 2%` 可能不只在 Codex 进程启动时出现。实际会话中，Codex runtime 可能在每轮请求、resume、会话重打包、skills 列表重新注入或上下文裁剪时重新计算 model-visible skills surface。因此，某个会话启动时没有看到警示，并不代表后续 turn 不会触发。

`soft-load` 不会修改启动可见 skills 列表，也不会把被 2% budget 挤掉的 skills 放回自动可见列表。它只是在当前会话内按需读取某个模块的 SKILL.md 或 reference，用普通上下文补足过程知识。因此：

- soft-load 是当前会话的补救与按需知识加载方式；
- hard-load/profile apply 才会改变下一次启动或 resume 后的 plugin/skills 可见面；
- 在缺少 usage evidence 前，不应直接把默认 profile 收缩到 `core-dev`；
- 对 `company-ops`、`market-research`、`web-saas`、`customer-comms`、`creative-content` 等模块，应先观察一个月，再决定是否常驻、按项目启用或仅按需加载。

30 天审计期内默认不执行 `set_plugin_profile.ps1 <module> -Apply`。允许：

- `load_module.ps1 <module> -Json` soft-load；
- `set_plugin_profile.ps1 <module> -Json` preview；
- 读取 inventory 与 session/log 数据；
- 生成本地 audit report。

禁止：

- 为降低 warning 直接删除 plugin cache；
- 批量改写 vendor/plugin `SKILL.md`；
- 未经明确批准执行 hard-load apply；
- 把 30 天内无强证据的能力解释成“无用”；
- 把 disabled plugin 解释成删除。disabled 只能表示 dormant，可恢复。

如果会话中再次出现 `2% skills context budget` warning，不能说明 soft-load 失败。正确解释是：runtime 仍在为当前 turn 构造 model-visible skills surface，而 soft-load 不参与这个预算面。soft-load 只解决“当前任务需要的知识如何按需读取”，不解决“全局自动可见列表过大”。

## 4. 证据模型

### 3.1 强证据

强证据可直接支持保留或 profile 化：

- assistant 明确声明 `使用技能：xxx` 或 `Using skill: xxx`；
- 会话读取了某个 `SKILL.md`；
- 调用了 plugin helper，例如 `load_module.ps1 <module>` 或 `set_plugin_profile.ps1 <module>`；
- 调用了 plugin/MCP/tool surface；
- 日志中出现明确 budget warning，并能定位到对应会话或 turn。

### 3.2 中证据

中证据说明任务可能需要能力，但不能单独作为常驻依据：

- 用户明确要求某个 plugin 能力，例如 Gmail、Slack、Twilio、Figma、Vercel、Cloudflare、Notion；
- 任务内容明显属于某个 profile 模块，例如 `web-saas`、`company-ops`、`market-research`、`customer-comms`、`creative-content`；
- 某项目历史说明要求保留 browser/web 能力。

### 3.3 弱证据

弱证据只用于趋势参考，不能单独用于 profile apply 决策：

- 文档或日志中单纯出现 plugin 名称；
- 模型讨论过 plugin，但没有实际读取、调用或声明使用；
- 静态 registry 中列出 plugin 名称。

30 天后按以下规则决策。所有阈值都以强证据为主，弱证据只能做辅助解释。

| 量化项 | 默认阈值 | 说明 |
| --- | --- | --- |
| 高频强证据 | 30 天内 `strong_helper_calls + strong_skill_path_reads >= 10`，或连续两周每周 >= 3 | 可进入默认 profile 候选，但仍需确认是否跨项目通用 |
| 低频强证据 | 30 天内 1-9 次强证据 | 保留 soft-load / hard-load profile，不默认常驻 |
| 项目特定强证据 | 强证据集中在单一项目、单一目录或单一任务类型 | 放入项目 profile 或任务 profile，不扩大到全局默认 |
| warning 严重度高 | 7 天内 `budget_warning_count >= 3`，或出现 `All skill descriptions were removed` | 优先调整默认 profile 或避免 full profile 常驻 |
| warning 严重度中 | 30 天内有 warning，但 7 天内少于 3 次 | 保持审计，结合当时任务判断是否需要 hard-load profile |
| 无强证据 | 30 天内 0 次强证据 | 不删除，只从默认候选中移除并保留恢复路径 |

| 证据 | 决策 |
| --- | --- |
| 高频强证据，且跨项目通用 | 常驻默认 profile |
| 低频强证据，但业务关键 | 不常驻，保留 module soft-load 与 hard-load profile |
| 项目特定强证据 | 项目 profile，例如 `browser`、`web-saas`、`company-ops` |
| 只有中证据 | 保留模块，不进入默认常驻 |
| 只有弱证据 | 不作为 apply 依据 |
| 30 天无强证据但属于战略能力 | dormant，不删除，保留恢复路径 |
| 30 天无强证据且非战略能力 | 从默认 profile 移出，但只通过 hard-load preview/apply 控制 |

## 5. Runtime 与数据源架构

运行时职责：

- `tools/audit_codex_skills_usage.py` 负责收集证据并输出 JSON/Markdown 报告。
- `tools/skills2cli.py audit warnings` 提供紧凑、脱敏的前台 warning triage，同时读取 session JSONL 与 `logs_2.sqlite`；它是只读 helper，不修改 Codex config、plugin cache、hard-load profiles 或 skill bodies。
- `tools/check_skills_audit_output_retention.py` 证明原始 audit artifacts 保持 local-only。
- `tools/check_skills_audit_final_review_state.py` 以只读方式验证最终人工复核、关闭、候选与 apply 门禁状态，不修改 config 或 profiles。
- `tools/check_skills_audit_final_review_precheck.py` 验证 final-summary noise 与 manual-conflict 项的机器级预检查证据，同时保持 human-review、candidate 与 profile-apply gate 关闭。
- `tools/check_skills_audit_cadence_contract.py` 验证已锁定的重复次数、weekly 频率、原始结束日期、事件触发 warning-triage 规则和 post-final monitoring-only 边界。
- `tools/check_precommit_update_archive.py` 证明本地提交前已检查 existing-file update review 与 OpenSpec archive gates。
- `tools/run_openspec_guard.py` 聚合仓库级 guard 证据。
- `test/` 下测试与 `tools/ci/ci_test_manifest.json` 条目保证 audit 行为可复现。

审计 helper 是证据采集器，不是 apply engine。它可以准备 preview-only records 和 recommendations，但不得修改 Codex config、plugin cache 或 hard-load profiles。

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 30 --json --output .\.tmp\skills-usage-audit-latest.json
```

默认数据源：

- `C:\Users\lenovo\.codex\sessions/**/*.jsonl` - 会话 transcript，用于识别显式 skill 声明、SKILL.md 读取，以及紧凑 `skills2cli` triage 所需的前台 warning 文本。
- `C:\Users\lenovo\.codex\logs_2.sqlite` - runtime 日志库，用于统计 skills budget warning；`skills2cli audit warnings` 将它作为第二个脱敏来源读取，避免 live-turn warning 只出现在 runtime 日志时被漏掉。
- `C:\Users\lenovo\.codex\config.toml` - 用户级 plugin enabled 状态来源，仅用于 audit-only 报告。
- `C:\Users\lenovo\.codex\skills\plugin-modules\references\profiles.json` - 模块 registry，用于按 profile 聚合 plugin evidence。

## 6. CLI 契约与审计节奏命令

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 0 --baseline --json --output .\.tmp\skills-usage-baseline-2026-05-16.json
```

基线记录当前 enabled plugins、profile modules、warning counter 与 inventory summary。基线不修改 `config.toml`。


规范化审计节奏契约：

| 事项 | 锁定值 | 执行含义 |
| --- | --- | --- |
| 观察窗口 | `2026-05-16` 至 `2026-06-15` | 原始 30 天审计窗口已经关闭，后续 monitoring run 不得延长该窗口。 |
| 计划内重复次数 | 总计 `6` 次计划内审计运行 | Day 0 baseline 1 次、weekly evidence 4 次、Day 30 final evidence 1 次。 |
| 计划内重复频率 | Day 0 运行 1 次，之后每 7 天运行 weekly evidence，Day 30 再运行 1 次 | Weekly evidence 日期为 2026-05-23、2026-05-30、2026-06-06、2026-06-13；final evidence 日期为 2026-06-15。 |
| Warning triage 频率 | 仅事件触发 | 只有出现新的 `2% skills context budget` warning 后，才运行窄窗口 triage；不设固定重复次数。 |
| Post-final 运行 | 只作为 monitoring evidence | 2026-06-15 之后的运行只能更新 review-pending evidence 或 warning triage，不能重开 30 天窗口，也不能授权 profile apply。 |
| Apply 边界 | cadence 本身不授权 apply | profile apply 仍必须等待后续明确 `approved-to-apply` 授权。 |

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 7 --json --output .\.tmp\skills-usage-audit-7d.json
```

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 30 --json --output .\.tmp\skills-usage-audit-30d.json --summary-output .\.tmp\skills-usage-audit-30d-summary.md --manual-notes .\.tmp\skills-usage-audit-notes-YYYY-MM-DD.md
```

`--summary-output` 写入脱敏 Markdown 决策摘要。它只作为复核证据，不得修改 `config.toml`、plugin cache 或 hard-load profile。

如需为后续可回滚调整预生成候选记录，应增加 `--target-profile`、`--candidate-output`、`--summary-reviewed`，并可选增加 `--candidate-summary-output`：

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 30 --json --output .\.tmp\skills-usage-audit-30d.json --summary-output .\.tmp\skills-usage-audit-30d-summary.md --summary-reviewed --target-profile core-dev --candidate-output .\.tmp\skills-profile-candidate.json --candidate-summary-output .\.tmp\skills-profile-candidate.md
```

候选输出永远是 `approval_state=preview-only`，不得修改 `config.toml`、plugin cache 或 hard-load profile。`--candidate-output` 或 `--candidate-summary-output` 必须搭配显式 `--target-profile`；脚本不得从当前 profile、文件名或普通“继续”中推断目标 profile。缺少 `--summary-reviewed`、30 天审计窗口、`--output`、`--summary-output` 或 `--target-profile` 时，候选生成门禁必须记录为 blocked。

脚本必须在 Windows 非 UTF-8 控制台下仍能输出 `--json`。如果 stdout 无法编码 `⚠` 等字符，stdout 可以退化为 JSON 合法的反斜杠转义形式；但 `--output` 写入的报告文件仍必须保持 UTF-8 原文。

相关回归测试必须覆盖：

- `⚠ Exceeded skills context budget of 2%` 的 stdout fallback；
- 中文 `使用技能：` 与英文 `Using skill:` 的显式 skill announcement 识别；
- `logs_2.sqlite` 中 budget warning 的 `omitted_additional_skills` 与 `all_descriptions_removed` 提取；
- `skills2cli audit warnings --since ... --json` 必须分别报告 `sessions_jsonl` 与 `logs_2.sqlite` 来源，汇总 warning 计数，脱敏私有路径与 secret，并保持 `raw_log_paths_retained=false` 与 `raw_skill_bodies_retained=false`；
- `full` profile 中 `plugins: "all_known_plugins"` 不能被拆成单个字符；
- 脚本在缺少用户级 plugin-modules profile 时，必须回退读取仓库内 `tools/skill_sources/plugin-modules/references/profiles.json`。

为避免一个月 audit 过程中偏离，使用固定节奏。该节奏现在已经锁定为已关闭的原始审计窗口，而不是可无限延长的循环。

| 节奏项 | 日期或触发条件 | 重复次数 | 命令 | 输出文件 | 用途 |
| --- | --- | ---: | --- | --- | --- |
| Day 0 baseline | 2026-05-16 | 1 | `--days 0 --baseline` | `.tmp/skills-usage-baseline-YYYY-MM-DD.json` | 冻结初始 enabled plugins、inventory 和 warning 状态 |
| Weekly audit | 2026-05-23、2026-05-30、2026-06-06、2026-06-13 | 4 | `--days 7` | `.tmp/skills-usage-audit-7d-YYYY-MM-DD.json` | 发现会话中新增 warning 与模块使用趋势 |
| 漏跑周报补跑 | 仅在漏跑 weekly run 时触发 | 事件触发，不设固定次数 | `--days 7 --late-run --missed-weekly-runs N` | `.tmp/skills-usage-audit-7d-late-YYYY-MM-DD.json` | 保留明确的节奏偏离标记，而不是伪造漏跑报告 |
| Day 30 final audit | 2026-06-15 | 1 | `--days 30` | `.tmp/skills-usage-audit-30d-YYYY-MM-DD.json` | 形成是否调整默认 profile 的证据包 |
| Warning triage | 每次新的 `2% skills context budget` warning 之后 | 事件触发，每个新 warning 对应一次窄窗口运行 | `--warning-triage --days 1` 或 `--warning-triage --since` | `.tmp/skills-usage-warning-triage-YYYY-MM-DD.json` | 定位 warning 是否来自当前会话重打包 |
| Final human review | Day 30 summary 已存在之后 | 1 次决策复核 | 复核脱敏 final summary 与 decision template | 如产生决策，只提交脱敏 review record | 选择 `summary-reviewed + closed-no-change`、`summary-reviewed + preview-only candidate` 或 `review-pending + continue monitoring` |

因此，标准计划内审计重复次数固定为 6 次：1 次 baseline、4 次 weekly、1 次 final 30-day run。最终人工复核是单独决策步骤，不是另一轮审计运行。Warning triage 与漏跑补跑属于异常/事件触发路径，不分配固定重复次数。

原始审计结束日期固定为 2026-06-15。该日期之后的运行仅属于 post-final monitoring：可以更新 review-pending evidence 或 warning-triage evidence，但不得移动原始结束日期、重启 30 天计时、标记 summary-reviewed、生成 profile candidate，或在没有后续明确决策时执行 profile apply。

`.tmp/` 报告默认不入 Git；如果需要长期留证，只提交经过脱敏和摘要化的 Markdown 结论，不提交完整 session transcript、token、私有路径或 vendor cache 内容。

`--warning-triage` 是 warning 出现后的 audit-only 复核标记，必须搭配窄窗口：使用 `--days 1`，或使用显式 `--since` 覆盖 warning 时间点。如果 `--warning-triage` 搭配 `--days 7`、`--days 30` 等过宽窗口，报告必须写入 `warning_triage.status=blocked`、`warning_triage_window_not_narrow`，并保持 `audit_state.reason=warning_triage_window_too_broad`。triage 报告还必须汇总 `Skipped loading` warning 数量，暴露有界且已脱敏的 skipped-loading 样本摘录，并记录“先记录来源、不批量改 vendor cache”的复核策略。`warning_triage.status` 只能是 `not_requested`、`blocked`、`log_source_unavailable`、`warning_found` 或 `no_warning_found_in_triage_window`；`blockers` 只能保存已知字符串 blocker，且当前只允许 `warning_triage_window_not_narrow`。该标记不得修改 `config.toml`、plugin cache 或 hard-load profile。

一个月 audit 期间，如果执行节奏或数据源异常，按下表处理，避免把不完整数据误当成最终结论。

| 偏离或异常 | 恢复动作 | 不允许的动作 |
| --- | --- | --- |
| 漏跑一周汇总 | 立即补跑 `--days 7`，并在报告摘要中标记 `late_run: true` | 为补齐节奏而伪造历史报告 |
| warning 出现后未及时 triage | 补跑 `--days 1`；如已超过 24 小时，再补跑覆盖 warning 时间点的 `--since` | 只凭记忆判断 soft-load 是否失效 |
| `logs_2.sqlite` 不可读或缺失 | 报告中保留 `log_evidence.available=false`，改用 session transcript 做辅助说明 | 把 0 个 warning 当成“没有发生 warning” |
| session transcript 不完整或包含隐私内容 | 只提交聚合字段和脱敏摘要；必要时保留本地 `.tmp/` 原始 JSON | 提交完整会话记录、token 或私有路径 |
| 报告缺少字段契约中的关键字段 | 先修脚本或重跑报告，再进入 profile 决策 | 用缺字段报告决定 hard-load/profile apply |
| explicit skill 误报噪声含路径碎片、secret 或长 mojibake 文本 | 修脚本脱敏、截断并补回归测试；重跑报告确认 `noise_review` 契约通过 | 把原始噪声 token 留进长期报告或按强证据计数 |
| 审计期中确有紧急任务需要某 plugin | 允许对该任务 soft-load 或 preview；如必须 hard-load，单独取得明确授权并记录例外 | 借紧急任务提前结束 30 天审计 |

第 30 天不能只提交原始 JSON。必须形成一份可人工复核的脱敏 Markdown 摘要，至少包含：

1. 审计窗口：起止时间、是否漏跑周报、是否有 late run。
2. 当前配置面：enabled/disabled/unknown plugin 数量、`current_profile.inferred_profile`、精确 module 匹配，以及是否需要人工复核。
3. Warning 结论：30 天 warning 总数、7 天 warning 总数、最高严重度、是否出现 `All skill descriptions were removed`。
4. 证据表：按 module 列出强证据次数、`medium_evidence_rationale`、弱证据次数、`cross_project_utility` 和 recommendation。
5. 噪声复核：列出被剔除的明显误报 token，例如 `and`、`from`、`draft`；说明它们未计入强证据；同时展示 `raw_noise_tokens_retained`、`max_noise_token_length` 与 `token_privacy_policy`，让人工复核者不打开原始 JSON 也能确认噪声 token 隐私门禁。 Markdown 摘要必须渲染一组有上限的脱敏样本列表；如果没有被剔除 token，必须显示 `none`。
6. 决策建议：渲染只用于复核的分桶，包括默认/项目 profile 复核候选、按需 soft-load 模块、中证据/弱证据人工复核模块、保留 dormant 但可恢复模块，或仅留在 `full` 排障 profile；这些分桶只是 review input，不得执行 profile apply。
7. 人工冲突复核：渲染人工记录是否包含例外或已批准 hard-load 例外、冲突/例外数量、人工记录不能覆盖脚本证据的策略，以及进入 profile 决策前必须完成的处置。
8. 风险与恢复路径：如果禁用或移出默认 profile，写明如何恢复、使用哪个 helper（例如 `set_plugin_profile.ps1 -RestoreLatest -Apply`）、是否需要通过 `codex-ohmy` 重启/新会话。
9. 不执行清单：明确哪些动作本报告没有执行，例如未修改 `config.toml`、未编辑 plugin cache、未 hard-load apply。

只有这份摘要与 JSON 报告字段契约同时满足，才允许进入后续 hard-load/profile apply 讨论。

脚本主要采集强证据和日志证据；中证据、业务关键性、项目特定性与紧急例外需要人工补充。人工记录必须使用脱敏 Markdown，建议存放在 `.tmp/skills-usage-audit-notes-YYYY-MM-DD.md`，默认不提交 Git。若需要进入长期证据包，只摘录脱敏摘要。

每条人工记录至少包含：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `time` | 是 | 记录时间或任务发生时间 |
| `project` | 是 | 项目名或仓库名；不能写入敏感客户信息 |
| `task_type` | 是 | 例如 `web-saas`、`company-ops`、`customer-comms`、`creative-content` |
| `requested_capability` | 是 | 用户明确要求或任务明显需要的能力 |
| `evidence_level` | 是 | `medium`、`exception` 或 `noise_removed` |
| `reason` | 是 | 为什么该能力有业务意义，或为什么某 token 被判定为误报 |
| `action_taken` | 是 | `none`、`soft-load`、`preview`、`approved hard-load exception` |
| `restore_or_followup` | 否 | 后续如何恢复、复核或补脚本过滤 |

人工记录不能覆盖脚本证据：如果人工判断与 JSON 报告冲突，或记录了 `exception` / `approved hard-load exception`，JSON 报告必须设置 `manual_evidence.conflict_review.status=manual_conflict_or_exception_review_required`，30 天摘要必须列出冲突/例外数量、非覆盖策略和需要完成的处置。

人工记录来源路径只允许用于本地审计执行，不能作为原始证据留存。写入 `manual_evidence.invalid_notes` 或候选 source 引用前，必须先对路径做脱敏和长度限制；如果 manual evidence 仍包含原始私有路径、secret 赋值、独立 token，或标记为保留了原始来源路径，字段契约必须失败。脱敏 Markdown 摘要也必须展示 `source_paths_retained`、`max_path_length` 与 `path_privacy_policy`，让人工复核者不打开原始 JSON 也能确认人工记录来源路径隐私门禁。

## 7. JSON 报告字段契约

`--json` 与 `--output` 生成的报告必须至少包含以下顶层字段。字段缺失时，该报告不得用于 profile 决策。

| 字段 | 用途 | 决策影响 |
| --- | --- | --- |
| `schema_version` | 报告结构版本 | 后续脚本按版本兼容解析 |
| `generated_at` | 报告生成时间 | 判断报告是否过期 |
| `audit_state` | 审计状态机状态、原因、下一步动作和 profile apply 许可标志 | 防止不完整或暂停中的审计状态进入 profile 决策 |
| `audit_window` | `since` / `until` / `days` | 防止用错误窗口做 30 天决策 |
| `safety` | 是否修改配置、plugin cache、hard-load apply | 必须全部证明 audit-only |
| `config_summary` | enabled / disabled / unknown plugins，以及 `current_profile` 推断 | 判断当前 profile 面是否过大，以及是否精确匹配已知 module |
| `inventory_summary` | user/repo/plugin skills 数量 | 判断 2% budget 压力来源 |
| `log_evidence` | budget warning、7 天 warning 数、脱敏的最近 budget-warning 样本摘录、`All skill descriptions were removed`、最大 omitted skills 数和 skipped loading 证据 | 判断 warning 是否仍在会话中出现，以及严重度是否越过方案阈值，同时避免复核者必须打开原始日志数据库 |
| `warning_severity` | 由 `log_evidence` 派生的 warning 压力等级、原因和处理动作 | 作为 profile 决策关键字段，防止只看 warning 计数而漏判 `full`/过大 profile 风险 |
| `warning_triage` | warning 后复核标记、窄窗口门禁、triage 窗口内 warning 计数和后续动作建议 | 防止把周报/月报误当成 turn 级 warning triage 证据 |
| `session_evidence` | explicit skills、SKILL.md reads、helper calls、tool calls | 作为强/中/弱证据输入 |
| `manual_evidence` | 脱敏人工记录计数、无效记录校验以及中证据/例外/噪声摘要 | 保留人工复核证据，同时不留存原始 transcript |
| `noise_review` | explicit skill 噪声 token 的脱敏、截断、误报计数和强证据排除策略 | 防止误报 token、路径碎片或 mojibake 文本进入强证据或长期留存 |
| `script_capability_boundaries` | 脚本可靠覆盖项、仍需人工复核的边界、已知限制与脚本增强触发条件 | 防止把 audit helper 误当作全知事实源 |
| `output_retention` | 来自 `tools/check_skills_audit_output_retention.py` 的留存状态，包括 `.tmp/` 本地-only 策略、原始 JSON 本地-only 策略、长期证据格式和违规数量 | 防止报告隐藏原始 audit artifact 是否被误保留进 Git |
| `precommit_update_archive` | 来自 `tools/check_precommit_update_archive.py` 的提交前更新/归档门禁状态，包括既有文件更新复核、已完成 OpenSpec 归档、错误数、warning 数、变更路径数和 active change 复核数 | 防止审计报告脱离提交前必须先检查已有文件是否需要更新或归档的仓库规则 |
| `runtime_paths` | repo root、Codex home 和 `config.toml` 的脱敏运行路径占位符、路径类别标签，并保持 `raw_paths_retained=false` | 防止 JSON 和 Markdown 报告长期留存原始本地用户路径，同时仍说明本次审计扫描了哪些运行输入 |
| `module_evidence` | 按 profile module 汇总的强证据、中证据说明、弱证据和跨项目复核字段 | 生成 profile 决策候选，同时避免把中证据当作强证据 |
| `decision_recommendation` | 从 `module_evidence` 派生的只读决策分桶 | 让复核者看到 profile 复核、按需加载、人工复核和 dormant 模块，但不允许 profile apply |
| `cadence_review` | late-run 与漏跑周报标记 | 防止 30 天决策摘要隐藏审计节奏偏离 |
| `recommendations` | 审计建议 | 只能作为建议，不能自动 apply |

审计脚本还必须校验运行路径隐私：顶层 `root`、顶层 `codex_home`、`config_summary.config_path` 以及 `runtime_paths.root/codex_home/config_path` 都不得包含原始 Windows、POSIX home、UNC、token、cookie 或 secret 路径。报告必须用 `[REPO_ROOT]`、`[CODEX_HOME]`、`[CODEX_HOME]/config.toml` 等占位符替代原始绝对路径，并且 `runtime_paths.raw_paths_retained` 必须保持 `false`。

审计脚本必须为每份生成报告计算 `field_contract` 结果。该结果记录 `status`、`passed`、必需字段、缺失字段、字段类型错误、audit-only 安全标志违规，以及会影响决策的嵌套字段违规。`audit_state` 契约必须要求 `state`、`reason`、`next_action` 与 `profile_apply_allowed`，防止报告丢失状态机上下文。它还必须拒绝未知 audit state，拒绝 `profile_apply_allowed=true` 或其他非 false 值，并要求出现的状态 blocker 字段（`close_blockers`、`candidate_blockers`、`summary_review_blockers`、`pause_blockers` 或 `warning_triage_blockers`）必须是字符串列表。脱敏 Markdown 摘要还必须渲染 audit state 的 next action、profile apply 许可标志，以及这些字段中的 blockers；没有 blocker 时写入 `none`。`warning_triage` 契约必须要求 `requested`、`status`、`blockers`、`window_policy`、`window_ok`、`budget_warning_count`、`skipped_loading_count`、`recent_skipped_loading_samples`、`recent_skipped_loading_sample_excerpts`、`skipped_loading_review` 与 `recommended_action`，防止 warning 复核报告遗漏 triage 状态、窄窗口策略、脱敏 skipped-loading 样本、skipped-loading 来源复核或后续动作。其值级契约还必须拒绝未知 `status`、非 `use_days_1_or_since_for_warning_triage` 的 `window_policy`、非 `none` / `record_source_and_do_not_edit_vendor_cache_without_authorization` 的 `skipped_loading_review`、非字符串或未知 blocker、`status=blocked` 但 blocker 为空、blocker 非空但 status 不是 `blocked`、负数 warning / skipped-loading 计数字段，以及未脱敏、非字符串或含私有路径/secret/token 的 skipped-loading 样本摘录。只要 `field_contract.status != passed`，该报告就是不完整证据；必须先修脚本或重跑报告，才能进入 profile 决策。候选生成必须要求报告内嵌 `field_contract`；来自旧脚本或人工改写后缺少/过期内嵌契约的报告，必须阻断并要求重新生成。
`log_evidence` 契约必须要求 `budget_warning_count`、`last_7d_budget_warning_count`、`recent_budget_warning_samples` 与 `recent_budget_warning_sample_excerpts`。计数字段必须是非负整数；每条保留的 budget-warning 摘录必须是已脱敏字符串，不得包含原始私有路径、secret 赋值、cookie/access-token 值或独立 secret token。脱敏 Markdown 摘要与默认人类可读 stdout 必须渲染样本数量和有界摘录；没有样本时显示 `none`，让复核者不打开 `logs_2.sqlite` 也能确认 warning 形态。

`warning_severity` 契约必须要求 `level`、`reason` 与 `recommended_action`。`level` 只能是 `unknown`、`high`、`medium` 或 `none`；`reason` 与 `recommended_action` 必须是已脱敏字符串，不得包含原始私有路径、secret 赋值、cookie/access-token 值或独立 secret token。脱敏 Markdown 摘要与默认人类可读 stdout 必须渲染 severity 等级、原因与处理动作，其中 Markdown 必须显式渲染 `Severity recommended action`；字段契约必须单独暴露 `warning_severity_violations`，候选生成或 profile 决策不得使用缺失、非法等级或未脱敏的 warning severity 报告。

默认 human stdout 和脱敏 Markdown 摘要都必须渲染 `field_contract` 细节，不能只显示 `status`。至少要显示 `passed`、blocker 数量、必需字段数量、缺失字段数量、类型错误数量、是否要求内嵌契约，以及 safety、audit_state、log_evidence、warning_severity、warning_triage、cadence_review、manual_evidence、noise_review、script_capability_boundaries、output_retention、precommit_update_archive、runtime_paths、module_evidence、decision_recommendation 与 embedded field contract 等违规分组计数。这样当审计报告在命令行或摘要复核中失败或被阻断时，复核者不打开原始 JSON 也能定位是哪一组契约缺口。
`noise_review` 契约必须要求 `raw_noise_tokens_retained=false`、`max_noise_token_length`、`token_privacy_policy` 与脱敏后的 `explicit_skill_noise_removed`。噪声 token 在进入报告前必须先替换私有路径、secret、cookie 或 token，并截断到固定长度；如果仍检测到原始私有路径、secret 或过长 token，字段契约必须失败。
`script_capability_boundaries` 契约必须要求 `policy`、`reliable_coverage`、`human_review_required_for` 和 `enhancement_triggers`。这些列表必须存在且非空，避免报告暗示 audit helper 是全知事实源。
`output_retention` 契约必须要求 `status`、`ok`、`checker`、`tmp_outputs_local_only`、`raw_audit_json_local_only`、`long_term_evidence_format` 和 `violation_count`。只有留存 checker 自身通过、`.tmp/` 输出与原始 audit JSON 都标记为本地-only，且长期证据格式为 `sanitized_markdown_summary` 时，该契约才能通过。

`precommit_update_archive` 契约必须要求 `status`、`ok`、`checker`、`before_local_git_commit`、`review_existing_files_for_required_updates`、`archive_completed_openspec_changes_before_commit`、`error_count`、`warning_count`、`changed_path_count` 和 `active_change_review_count`。只有提交前更新/归档 checker 自身通过，且报告明确既有文件更新复核和已完成 OpenSpec 归档门禁均启用时，该契约才能通过；checker 失败或不可用时，本轮 audit 报告不得作为可提交证据。
`cadence_review` 契约必须要求 `late_run`、`missed_weekly_runs` 与 `weekly_report_review`；`missed_weekly_runs` 必须是 `null` 或非负整数，且 `late_run=true` 时必须显式记录漏跑次数。脱敏 Markdown 摘要必须在审计窗口部分渲染这些节奏字段，让 30 天复核者无需打开原始 JSON 也能看到审计节奏是否偏离。
`module_evidence` 契约必须在其进入 `decision_recommendation` 或候选生成前校验每一行。每行必须包含 module 名称、plugin 列表、strong helper 计数、strong skill-path 计数、strong total、默认候选阈值、mapped-tool 中证据计数与策略、中证据说明、弱提及、跨项目效用和 recommendation。数值计数必须是非负整数，`strong_total` 必须等于 helper calls 加 skill-path reads，plugin 元素必须是字符串，mapped tool calls 必须保持为中证据，跨项目效用必须要求人工复核，recommendation 只能使用已批准的 advisory 取值。recommendation 还必须匹配阈值规则：`strong_total >= default_candidate_threshold` 才是 profile 复核候选，`0 < strong_total < threshold` 保持按需加载，`strong_total == 0` 且存在弱提及时只能是 mentioned-only，没有强证据也没有弱提及时保持 dormant/restorable。
`decision_recommendation` 契约必须要求 advisory-only 状态、非 apply 策略、`profile_apply_allowed=false`、四个分桶列表（`profile_review_candidates`、`on_demand_soft_load`、`manual_review_medium_or_weak`、`dormant_restorable`）以及一致的 `bucket_counts`。如果分桶缺失、类型错误、包含非字符串 module 名称、允许 profile apply，或 `bucket_counts` 与实际分桶长度不一致，字段契约必须失败，不能进入 profile 决策或候选生成。
`manual_evidence.conflict_review` 契约必须要求状态、策略、冲突/例外计数、是否需要处置以及处置说明。人工 `exception` 记录和 `approved hard-load exception` 记录必须暴露为 `manual_conflict_or_exception_review_required`，避免 30 天复核者漏看与脚本证据冲突或超出脚本证据的人工判断。




`script_capability_boundaries` 契约还必须包含 stable tool-call alias registry。该 registry 必须暴露 `policy`、`evidence_level`、`counts_as_strong_evidence`、`plugin_aliases` 与 `module_aliases`；其中 `evidence_level` 必须固定为 `medium`，`counts_as_strong_evidence` 必须为 `false`。JSON 报告与脱敏 Markdown 摘要都必须渲染 registry policy 和 alias targets，使 30 天复核者不打开原始 JSON 也能看见哪些稳定 tool 名称被聚合为中证据。每个 alias target 都必须包含非空 alias 列表，且 alias registry 只能作为复核证据，不能作为 profile apply 证据。

## 8. 审计状态机与停止条件

为了避免一个月 audit 执行过程中反复漂移，审计本身必须有明确状态。状态只描述 audit 流程，不等同于 plugin/profile 已 apply。

| 状态 | 含义 | 允许动作 | 禁止动作 |
| --- | --- | --- | --- |
| `planned` | 方案已写好，但 Day 0 baseline 还未生成 | 复核方案、运行 baseline preview | 宣称已有 30 天证据 |
| `running` | Day 0 baseline 已生成，正在收集 30 天证据 | 周报、warning triage、manual notes、脚本修复 | hard-load apply，除非单独明确授权 |
| `paused` | 数据源缺失、隐私问题或脚本缺陷导致审计暂停 | 修复数据源、补测试、重跑报告 | 用暂停期间缺失数据做最终决策 |
| `ready-for-summary` | 已到第 30 天且字段契约、周报、triage、manual notes 基本齐全 | 生成 30 天脱敏 Markdown 摘要 | 直接修改默认 profile |
| `summary-reviewed` | 30 天摘要已人工复核并处理噪声/冲突 | 创建 profile apply 候选变更门禁 | 跳过 rollback/validation 计划 |
| `apply-candidate` | 已形成候选变更记录，仍处于 preview-only 或等待批准 | preview、风险复核、请求明确授权 | 把普通“继续”解释为 apply 授权 |
| `closed-no-change` | 30 天证据不足以调整默认 profile | 保留 dormant/soft-load 路径，关闭本轮审计 | 继续为了“凑结果”延长同一轮审计 |
| `closed-with-candidate` | 本轮审计结束，并产生待批准候选变更 | 进入单独 profile apply change | 在审计计划文件中直接执行配置变更 |

脚本必须能记录 closure 状态，但不能因此执行任何 profile apply：

- `--planned-audit` 用于在 Day 0 baseline 尚未生成前记录 `planned`，并以 `audit_state_planned` 阻断 profile-apply 候选生成。它只用于把 baseline 前的计划状态显式化。
- `--pause-audit data-source-missing|privacy-review|script-defect` 用于记录 `paused`，并以 `audit_state_paused` 阻断 profile-apply 候选生成。它只能把数据源缺失、隐私复核或脚本缺陷导致的审计中断显式化；后续必须先修复原因并重跑报告。
- `--summary-reviewed` 在 30 天窗口满足且同时存在 `--output` 与 `--summary-output` source-report 路径时，如果没有请求 candidate 或 closure，记录 `summary-reviewed`。如果 source-report 路径缺失，报告保持 `ready-for-summary` 并记录 `source_report_paths_missing`。
- `--close-audit no-change` 只能在 30 天窗口已满足、存在 `--summary-reviewed`，并且同时存在 `--output` 与 `--summary-output` source-report 路径时，记录 `closed-no-change`。
- `--close-audit with-candidate` 只能在同样证据门禁通过、已请求 candidate output 路径，并且存在 `--target-profile` 时，记录 `closed-with-candidate`。
- 如果这些门禁未满足，报告必须保持 `running` 或 `ready-for-summary`，并列出 closure blockers，例如 `audit_window_shorter_than_30_days`、`summary_not_marked_reviewed`、`source_report_paths_missing`、`candidate_output_missing` 或 `target_profile_missing`。

停止条件：

- 如果达到 `closed-no-change`，下一步只能按需重新开新一轮 audit 或保留 soft-load，不继续追加本轮结论；
- 如果达到 `closed-with-candidate`，后续工作必须转入 profile apply 候选变更，不再把审计计划本身当成执行面；
- 如果连续两次复核只增加解释性文本、没有新增可验证规则、字段、状态或测试要求，应停止继续扩写方案，改为提交当前完善结果；
- 审计状态变化必须记录在 30 天摘要或候选变更记录中，而不是只留在聊天上下文。

## 9. 隐私、留存与输出门禁

usage audit 会读取用户级 Codex 会话、日志和配置状态，因此必须把“可读数据”和“可留存数据”分开管理。

| 数据源 | 可读取目的 | 可留存内容 | 禁止留存或外发内容 |
| --- | --- | --- | --- |
| `sessions/**/*.jsonl` | 识别显式 skill 声明、`SKILL.md` 读取和 helper 调用 | 聚合计数、脱敏任务类型、脱敏项目名 | 完整 transcript、用户私密输入、token、密钥、客户信息 |
| `logs_2.sqlite` | 统计 budget warning、skipped loading、warning 时间点 | warning 计数、时间窗口、脱敏 message excerpt | 完整日志库、含路径/账号/密钥的原始消息 |
| `config.toml` | 读取 plugin enabled/disabled/unknown 状态 | plugin 状态摘要、profile 名称 | 完整用户级配置、认证信息、非本任务相关设置 |
| 人工记录文件 | 读取脱敏后的中证据、例外与误报剔除记录 | 解析后的字段、聚合计数、脱敏且限长的 invalid-note 来源占位符 | 原始本地记录路径、原始人工记录文件、secret、客户信息、原始 transcript |
| plugin/vendor cache | 统计 `SKILL.md` inventory 或定位 invalid skill | skill 数量、路径类别、invalid skill 摘要 | vendor 文件全文、批量复制的 SKILL.md 内容 |
| `.tmp/` audit report | 本地临时复核 | 本地 JSON、脱敏 Markdown 摘要 | 未脱敏报告提交 Git 或发送远端 |
| 运行路径（`root`、`codex_home`、`config_path`） | 脚本执行期间定位审计输入 | `[REPO_ROOT]`、`[CODEX_HOME]` 等占位符和路径类别字段 | 原始本地用户目录、UNC 共享、home 路径或完整 user-level config 路径 |
| profile candidate 记录 | 30 天摘要复核后 preview 可回滚 profile 变更 | 候选 ID、脱敏 source-report 引用、plugin diff、rollback path、validation plan | 原始绝对用户路径、UNC 共享路径、token、cookie、原始人工记录、原始 transcript |

留存规则：

- 任何报告中留存的运行路径必须只使用占位符和类别标签；原始仓库路径、用户 home、Codex home 或 user-level `config.toml` 路径不得进入 JSON、Markdown 或候选记录；
- `.tmp/*.json` 默认只作为本地临时证据，不提交 Git；
- 需要长期留证时，只提交脱敏 Markdown 摘要；
- 任何报告进入 Git 前，必须确认不含 API key、access token、cookie、私有客户名、完整本地用户目录清单；
- 脱敏后的日志 `message_excerpt` 截断时必须保留完整 `[REDACTED_PATH]` 与 `[REDACTED_SECRET]` 标记，不得只留 `[RE`、`[REDACTED_` 等含义不明的局部标记碎片；
- 任何候选记录写入或渲染前，必须确认 `source_reports_privacy.status=passed`；若出现 `raw_private_path`、`raw_secret_assignment` 或 `raw_standalone_token`，按脚本缺陷处理；
- remote publication 不得把原始 audit JSON 当成附件上传；
- 如果发现已生成的报告含敏感内容，先删除该本地报告并重跑脱敏摘要，不在同一报告上手工涂改后继续使用。

每次 `docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md` 相关实现准备提交本地 Git 仓库前，必须先运行并在审计报告中暴露 `tools/check_precommit_update_archive.py` 的结果。该门禁用于把“先检查已有文件是否需要更新和 archive，更新和 archive 之后才能提交本地 git 仓库”变成脚本可见证据，而不是只留在聊天上下文。

报告字段要求：

- 顶层必须包含 `precommit_update_archive`；
- `precommit_update_archive.status` 只能是 `passed`、`failed` 或 `unavailable`；
- `before_local_git_commit` 必须为 `true`，表示该检查属于提交前门禁；
- `review_existing_files_for_required_updates` 必须为 `true`，表示提交前已检查既有文件是否需要同步更新；
- `archive_completed_openspec_changes_before_commit` 必须为 `true`，表示已完成 OpenSpec change 必须先归档或记录明确延期归档；
- `error_count`、`warning_count`、`changed_path_count` 和 `active_change_review_count` 必须是非负整数；
- 如果 checker 失败或不可用，`field_contract` 必须失败，并阻断把该 audit 报告当作本地提交证据。

脱敏 Markdown 摘要必须渲染：

- 提交前更新/归档门禁状态；
- checker 路径；
- 错误数；
- 既有文件更新复核是否启用；
- OpenSpec 归档门禁是否启用；
- 变更路径数与 active change 复核数。

该门禁不自动修改文件、不自动 archive，也不替代人工判断；它只负责在提交前 fail closed，提示本轮必须先完成更新、归档或记录合规延期理由。

审计输出留存现在由 `tools/check_skills_audit_output_retention.py` 提供脚本化保护，并以 `check_skills_audit_output_retention` 步骤接入 `tools/run_openspec_guard.py`。

当以下路径处于 tracked、staged、changed 或 commit-visible untracked 状态时，留存门禁必须在提交、本地集成或发布前失败：

- 任何 `.tmp/` artifact，包括即使用 `git add -f` 强制加入 Git 的 `.tmp/skills-usage-audit-30d.json`；
- 文件名以 `skills-usage-audit`、`skills-usage-baseline`、`skills-usage-warning` 或 `skills-usage-report` 开头的原始 Skills usage audit JSON，即使该文件不在 `.tmp/` 下。

长期留证必须是脱敏 Markdown 摘要，或另一种已经明确复核过的脱敏文档。原始 JSON 报告只能作为本地复现与复核工作文件。如果复核者需要持久证据，应从原始 JSON 重新生成 Markdown 摘要，完成隐私复核后提交脱敏摘要，而不是提交原始报告。

回归覆盖位于 `test/check_skills_audit_output_retention.test.py`，且必须登记到 `tools/ci/ci_test_manifest.json`。Guard JSON 聚合测试也必须包含 `check_skills_audit_output_retention`，避免 CI 可见的 guard 顺序静默丢失留存门禁。

## 10. Profile candidate gate 与 rollback

30 天审计结束后，即使证据支持调整默认 profile，也不能直接 apply。必须先形成一份候选变更门禁记录，用来把“审计结论”转换为“可回滚的配置变更”。

候选变更记录至少包含：

| 字段 | 说明 |
| --- | --- |
| `candidate_id` | 候选变更编号，例如 `skills-profile-2026-06-core-dev-plus-browser` |
| `source_reports` | 30 天 JSON 报告、脱敏 Markdown 摘要、人工记录摘要的脱敏引用 |
| `source_reports_privacy` | 证明候选记录不再包含原始私有路径或密钥的契约结果 |
| `current_profile` | 当前默认 profile 与 enabled plugins 摘要 |
| `target_profile` | 候选目标 profile，或需要新增/修改的 profile 名称 |
| `plugin_diff` | 将新增、移出默认、保持 dormant 的 plugin/module 列表 |
| `evidence_basis` | 每个变更项对应的强证据、中证据、战略保留或 warning 压力 |
| `risk_review` | 可能误禁用的能力、受影响项目、恢复成本 |
| `rollback_path` | 恢复旧 profile 的 helper 命令、所需重启/新会话说明 |
| `validation_plan` | preview、local check、启动验证和 warning 复测步骤 |
| `approval_state` | `preview-only`、`approved-to-apply`、`applied`、`rolled-back` |
| `candidate_record_contract` | 候选记录自身形状、preview-only 安全标志、隐私契约、回滚路径、验证计划与候选门禁结构的自校验结果 |

门禁规则：

- 审计脚本可以通过 `--candidate-output` 与 `--candidate-summary-output` 生成候选 JSON/Markdown，但这些输出只能作为 preview 记录；
- 候选生成必须记录门禁结果，且门禁要求 30 天审计窗口与 `--summary-reviewed`；
- 候选生成必须要求 30 天 JSON 报告与脱敏 Markdown 摘要的 source-report 路径，避免已复核候选与复核证据脱钩；
- 候选生成必须要求显式 `--target-profile`；如果缺失，audit state 保持 `ready-for-summary`，记录 `target_profile_missing`，并且任何候选 preview 都必须保持 blocked，不得抛出无结构异常或暗示存在可用目标；
- 候选生成必须要求报告 `audit_state.state` 已进入候选就绪状态：`summary-reviewed`、`apply-candidate` 或 `closed-with-candidate`；`planned`、`paused`、`running`、`ready-for-summary` 与 `closed-no-change` 都必须阻断候选生成，避免普通 summary 参数或已关闭无变更审计被误解释为 profile apply 候选授权；
- candidate `source_reports` 写入 JSON 或 Markdown 候选记录前必须先脱敏；原始 Windows 路径、POSIX home 路径、UNC 共享路径、API key、access token、cookie 与独立 secret token 都必须被替换；
- 候选记录必须包含 `source_reports_privacy.status=passed`；如果 privacy contract 失败，候选必须保持 blocked，直到重新生成 report 路径或修复脱敏器；
- 候选 Markdown 摘要必须渲染 source-report privacy 状态与 violations/blockers；没有违规时写入 `none`，保证 preview 记录可复核且不暴露原始 source 路径；
- 候选生成还必须校验报告字段契约；当必需顶层字段、audit-only 安全标志、决策关键嵌套字段或内嵌 `field_contract` 本身缺失、过期或类型错误时，必须以 `field_contract:<reason>` 阻断；
- 候选生成还必须附加并渲染 `candidate_record_contract`；当候选必需字段、preview-only 安全标志、`source_reports_privacy.status=passed`、`candidate_generation_gate.allowed/blockers`、`rollback_path.restore_command` / `restart_required` 或非空 `validation_plan` 缺失或无效时，该契约必须失败，且该候选不得被当成可 apply 证据。候选 Markdown 必须渲染候选契约的通过标志、blocker 数、必需/缺失/类型错误字段计数、preview-safety 违规数、source-report-privacy 违规数、gate-shape 违规数、rollback-path 违规数、validation-plan 违规数、sanitization 违规数、approval policy 与有界 blocker 细节，让复核者不打开原始 JSON 也能诊断被阻断的候选记录；
- `approval_state=preview-only` 只能运行 preview，不得修改 `config.toml`；
- `approved-to-apply` 必须来自用户明确授权，不能由“继续”或普通确认替代；
- apply 后必须保存 apply 前后的脱敏 diff 摘要；
- 如果 apply 后 warning 仍出现或关键能力缺失，优先按 `rollback_path` 恢复，不在同一轮中连续叠加多个 profile 改动。

| 现象 | 判断 | 处理动作 |
| --- | --- | --- |
| 启动时无 warning，但会话中出现 warning | soft-load 仍可能有效；runtime 在 turn 级重建 model-visible skills surface | 运行 `--warning-triage --days 1` 或 `--warning-triage --since ...`，记录发生 turn，不立即 hard-load apply |
| `All skill descriptions were removed` | 当前 skills surface 已严重超预算 | 下轮启动避免 `full`，使用 `core-dev` 或任务 profile；审计结束前仍不删除 plugin cache |
| `additional skills were not included` 数量持续升高 | 自动可见列表仍过大 | 根据 30 天强证据缩小默认 profile，保留 dormant 恢复路径 |
| `Skipped loading` 指向无效 SKILL.md | 单个 skill 元数据错误或 vendor cache 问题 | 先通过 `warning_triage.skipped_loading_*` 字段记录来源；除非用户授权，不批量改 vendor cache |

审计结束前，只允许生成报告和 preview profile。审计结束后，如证据支持，再新开 bounded change 或使用已批准的 profile helper 执行 hard-load apply。远端发布仍按本仓库 local-main-first 与 GitLab/GitHub 授权规则执行。

## 11. 实施切片

### Slice 1：审计来源清单与基线冻结
范围：
- [x] 实现审计 CLI、数据源读取、inventory 统计、JSON 输出、Markdown 输出与 Windows 安全 stdout。
完成标准：
- [x] Day 0 baseline 可在不修改 Codex config 或 plugin cache 的前提下生成。
测试：
- [x] CLI smoke、profile-registry fallback 与 stdout encoding 已覆盖。

### Slice 2：会话 warning triage 与 warning severity
范围：
- [x] 统计 budget warning 与 skipped-loading warning，强制窄窗口 warning triage，并计算 warning severity。
完成标准：
- [x] 过宽 triage window 被阻断，脱敏 warning excerpts 被渲染。
测试：
- [x] warning 解析、skipped-loading 解析、triage 阻断与 severity 渲染已覆盖。

### Slice 3：字段契约、隐私契约与留存门禁
范围：
- [x] 校验报告字段、audit-only safety、runtime path privacy、output retention 与 pre-commit update/archive 状态。
完成标准：
- [x] 不完整、不安全、过期或泄露隐私的报告不能成为 profile-decision evidence。
测试：
- [x] field-contract、privacy、output-retention 与 pre-commit gate 测试已覆盖。

### Slice 4：证据聚合与 candidate preview
范围：
- [x] 聚合 module evidence、manual evidence、noise review、decision buckets、audit states 与 preview-only candidate records。
完成标准：
- [x] reviewed 30-day evidence package 存在前，candidate generation 被阻断。
测试：
- [x] module-evidence、manual-evidence、decision-recommendation、audit-state 与 candidate-contract 测试已覆盖。

### Slice 5：长期监控周期
范围：
- [x] 跑完 2026-05-16 至 2026-06-15 的真实 30 天观察期。
- [x] 锁定标准重复次数与频率：Day 0 1 次、weekly 4 次、Day 30 1 次，warning triage 仅作为事件触发的一次性窄窗口运行。
- [ ] 完成最终人工复核，并且仅在明确选择时生成可选 preview-only candidate。
完成标准：
- [x] 已为关闭的 30 天窗口生成 final JSON 与脱敏 Markdown evidence，且通过 embedded contracts。
- [ ] final summary 已被标记为 `summary-reviewed` 并记录决策，或明确保持 `human_review_pending` 并追加 post-final monitoring evidence。
测试：
- [x] 日历窗口关闭时验证最终观察期证据。
- [ ] candidate generation 或 closure 前验证人工复核决策证据。

## 12. 任务级执行 Backlog

本清单只记录本方案对应的脚本、门禁、输出、测试和审计运行事项；每个事项按实施顺序排列，并用勾选项标记完成状态。

### Task 1：审计脚本基础能力

- [x] 新增 `tools/audit_codex_skills_usage.py` 审计脚本。
- [x] 支持 `--root` 指定仓库根目录。
- [x] 支持 `--days` 指定相对审计窗口。
- [x] 支持 `--since` 指定绝对起始时间。
- [x] 支持 `--baseline` 生成基线快照。
- [x] 支持 `--json` 输出机器可读报告。
- [x] 支持 `--output` 写入 JSON 报告。
- [x] 支持 `--summary-output` 写入脱敏 Markdown 摘要。
- [x] 支持读取 Codex session JSONL transcript。
- [x] 支持读取 `logs_2.sqlite` runtime 日志。
- [x] 支持读取用户级 `config.toml` plugin 状态。
- [x] 支持读取用户级 plugin profile registry。
- [x] 支持用户级 registry 缺失时回退仓库内 registry。
- [x] 支持统计 user / repo / plugin skills inventory。
- [x] 支持 Windows 非 UTF-8 stdout 下安全输出 JSON。

### Task 2：Skills 使用证据采集

- [x] 识别 assistant 显式 skill announcement。
- [x] 支持中文 skill announcement。
- [x] 识别 `SKILL.md` 路径读取证据。
- [x] 识别 profile helper 调用证据。
- [x] 识别 tool call 名称。
- [x] 按 profile module 聚合证据。
- [x] 过滤 `and`、`from`、`draft` 等显式 skill 误报。
- [x] 对无法映射到 known skill / plugin / profile 的 explicit skill token 降级处理。
- [x] 记录被剔除的噪声 token。
- [x] 对噪声 token 做路径与 secret 脱敏。
- [x] 对噪声 token 做长度截断。
- [x] 输出 `noise_review`。
- [x] 校验 `noise_review` 隐私字段。

### Task 3：Warning 与日志证据

- [x] 统计 skills budget warning 总数。
- [x] 统计最近 7 天 warning 次数。
- [x] 提取 `All skill descriptions were removed` 信号。
- [x] 提取 omitted additional skills 数量。
- [x] 提取 skipped-loading 样本。
- [x] 脱敏 warning message excerpt。
- [x] 保留 `[REDACTED_PATH]` 与 `[REDACTED_SECRET]` 标记完整性。
- [x] 日志库缺失时仍保持 `log_evidence` 结构。
- [x] 输出最近 budget-warning 样本数量。
- [x] 输出有界脱敏 warning 样本摘录。
- [x] 校验 `log_evidence` 必需字段。
- [x] 校验 warning 计数字段为非负整数。
- [x] 校验 warning excerpt 不含私有路径、secret、cookie 或 token。

### Task 4：Warning triage

- [x] 支持 `--warning-triage`。
- [x] 要求 warning triage 只能使用 `--days 1` 或 `--since` 窄窗口。
- [x] 过宽窗口时阻断 warning triage。
- [x] 输出顶层 `warning_triage`。
- [x] 输出 triage status。
- [x] 输出 triage blockers。
- [x] 输出固定 window policy。
- [x] 输出 warning / skipped-loading 计数。
- [x] 输出 skipped-loading 来源复核动作。
- [x] 输出 triage recommended action。
- [x] 校验 `warning_triage.status` 合法值。
- [x] 校验 blockers 类型与取值。
- [x] 校验 blocked 状态与 blockers 一致性。
- [x] 校验 skipped-loading 样本脱敏。
- [x] 在 Markdown 摘要渲染 warning triage。
- [x] 在 stdout 渲染 warning triage。
- [x] `skills2cli audit warnings --since ... --json` 同时汇总 `sessions_jsonl` 与 `logs_2.sqlite` 的只读脱敏 warning 来源。
- [x] `skills2cli audit warnings` 输出 per-source counts、raw-retention 安全标志，以及两个解释过的 pressure fields：`all_descriptions_removed_count` - 所有 skill descriptions 被移出 model-visible context 的次数；`max_omitted_additional_skills` - warning 文本中观察到的最大 additional-skill omission 数。

### Task 5：Warning severity

- [x] 增加 `warning_severity`。
- [x] 支持 severity level：`unknown`、`high`、`medium`、`none`。
- [x] 输出 severity reason。
- [x] 输出 severity recommended action。
- [x] 根据 warning 阈值计算 severity。
- [x] 日志不可用时输出 `unknown` severity。
- [x] 校验 `warning_severity.level` 合法值。
- [x] 校验 severity reason 与 recommended action 已脱敏。
- [x] 单独暴露 `warning_severity_violations`。
- [x] stdout 渲染 severity 等级、原因和处理动作。
- [x] Markdown 摘要渲染 severity 等级与原因。
- [x] Markdown 摘要显式渲染 `Severity recommended action`。

### Task 6：字段契约与安全契约

- [x] 定义报告顶层必需字段。
- [x] 输出 `field_contract`。
- [x] 校验顶层字段缺失。
- [x] 校验顶层字段类型。
- [x] 校验 audit-only safety。
- [x] 校验报告未修改 config。
- [x] 校验报告未编辑 plugin cache。
- [x] 校验报告未执行 hard-load apply。
- [x] 校验 `audit_state` 嵌套字段。
- [x] 校验 `log_evidence` 嵌套字段。
- [x] 校验 `warning_severity` 嵌套字段。
- [x] 校验 `warning_triage` 嵌套字段。
- [x] 校验 `cadence_review` 嵌套字段。
- [x] 校验 `manual_evidence` 嵌套字段。
- [x] 校验 `noise_review` 嵌套字段。
- [x] 校验 `module_evidence` 行字段。
- [x] 校验 `decision_recommendation` 嵌套字段。
- [x] 校验 `output_retention` 嵌套字段。
- [x] 校验 `precommit_update_archive` 嵌套字段。
- [x] 候选生成要求报告内嵌 `field_contract`。
- [x] 缺失或过期内嵌契约时阻断候选生成。
- [x] stdout 渲染 field contract 细节。
- [x] Markdown 摘要渲染 field contract 细节。

### Task 7：隐私、脱敏与留存

- [x] 脱敏 runtime root。
- [x] 脱敏 Codex home。
- [x] 脱敏 config path。
- [x] 输出 `[REPO_ROOT]` 与 `[CODEX_HOME]` 占位符。
- [x] 输出 `runtime_paths.raw_paths_retained=false`。
- [x] 校验报告不含原始私有路径。
- [x] 校验报告不含 secret 赋值。
- [x] 校验报告不含独立 token。
- [x] 脱敏人工记录来源路径。
- [x] 脱敏候选 source report 路径。
- [x] 将 `.tmp/*.json` 作为本地临时输出处理。
- [x] 将脱敏 Markdown 摘要作为长期留证格式。

### Task 8：Module evidence 与决策建议

- [x] 按 profile module 汇总 strong evidence。
- [x] 汇总 medium evidence rationale。
- [x] 汇总 weak evidence。
- [x] 增加 cross-project utility 人工复核字段。
- [x] 增加 module recommendation。
- [x] 校验 strong_total 一致性。
- [x] 校验 plugin 列表元素类型。
- [x] 校验 mapped tool call 只能作为 medium evidence。
- [x] 建立 stable tool-call alias registry。
- [x] 输出 alias registry policy。
- [x] 输出 alias target 摘要。
- [x] 定义高频强证据阈值。
- [x] 定义低频强证据阈值。
- [x] 定义项目特定强证据规则。
- [x] 定义无强证据处理规则。
- [x] 输出 `decision_recommendation`。
- [x] 保持 `decision_recommendation` 为 advisory-only。
- [x] 禁止 `decision_recommendation` 直接触发 profile apply。
- [x] 输出默认/项目 profile 复核候选分桶。
- [x] 输出按需 soft-load 分桶。
- [x] 输出人工复核分桶。
- [x] 输出 dormant / restorable 分桶。
- [x] stdout 渲染分桶计数与样本。
- [x] Markdown 摘要渲染决策分桶。

### Task 9：人工证据与例外

- [x] 支持 `--manual-notes`。
- [x] 定义人工记录字段格式。
- [x] 支持 `medium` 人工证据。
- [x] 支持 `exception` 人工证据。
- [x] 支持 `noise_removed` 人工证据。
- [x] 解析人工记录。
- [x] 校验无效人工记录。
- [x] 脱敏人工记录内容。
- [x] 脱敏人工记录来源路径。
- [x] 输出 `manual_evidence`。
- [x] 输出 `manual_evidence.conflict_review`。
- [x] 冲突或例外时要求人工处置。
- [x] Markdown 摘要渲染人工冲突/例外复核。
- [x] 字段契约阻断缺失 conflict review。

### Task 10：审计状态机

- [x] 定义 `planned` 状态。
- [x] 定义 `running` 状态。
- [x] 定义 `paused` 状态。
- [x] 定义 `ready-for-summary` 状态。
- [x] 定义 `summary-reviewed` 状态。
- [x] 定义 `apply-candidate` 状态。
- [x] 定义 `closed-no-change` 状态。
- [x] 定义 `closed-with-candidate` 状态。
- [x] 支持 `--planned-audit`。
- [x] planned 状态阻断候选生成。
- [x] 支持 `--pause-audit data-source-missing`。
- [x] 支持 `--pause-audit privacy-review`。
- [x] 支持 `--pause-audit script-defect`。
- [x] paused 状态阻断候选生成。
- [x] 支持 `--summary-reviewed`。
- [x] summary-reviewed 要求 source report 路径。
- [x] 支持 `--close-audit no-change`。
- [x] 支持 `--close-audit with-candidate`。
- [x] close-audit 不满足门禁时输出 closure blockers。
- [x] stdout 渲染 audit-state blockers。
- [x] Markdown 摘要渲染 audit-state next action、profile apply allowed 与 blockers。

### Task 11：候选变更门禁

- [x] 支持 `--candidate-output`。
- [x] 支持 `--candidate-summary-output`。
- [x] 支持 `--target-profile`。
- [x] 候选生成要求 30 天窗口。
- [x] 候选生成要求 `--summary-reviewed`。
- [x] 候选生成要求 JSON source report 路径。
- [x] 候选生成要求 Markdown source report 路径。
- [x] 候选生成要求显式 target profile。
- [x] 候选生成只接受候选就绪 audit state。
- [x] 阻断 `planned` 状态候选。
- [x] 阻断 `paused` 状态候选。
- [x] 阻断 `running` 状态候选。
- [x] 阻断 `ready-for-summary` 状态候选。
- [x] 阻断 `closed-no-change` 状态候选。
- [x] 候选记录保持 `approval_state=preview-only`。
- [x] 候选记录包含 `candidate_id`。
- [x] 候选记录包含 `source_reports`。
- [x] 候选记录包含 `source_reports_privacy`。
- [x] 候选记录包含 `current_profile`。
- [x] 候选记录包含 `target_profile`。
- [x] 候选记录包含 `plugin_diff`。
- [x] 候选记录包含 `evidence_basis`。
- [x] 候选记录包含 `risk_review`。
- [x] 候选记录包含 `rollback_path`。
- [x] 候选记录包含 `validation_plan`。
- [x] 候选记录包含 `candidate_record_contract`。
- [x] 候选 contract 校验 preview-only 安全。
- [x] 候选 contract 校验 source-report privacy。
- [x] 候选 contract 校验 rollback path。
- [x] 候选 contract 校验 validation plan。
- [x] 候选 Markdown 渲染不执行清单。
- [x] 候选 Markdown 渲染 contract blocker 细节。

### Task 12：审计节奏与恢复规则

- [x] 支持 `--late-run`。
- [x] 支持 `--missed-weekly-runs`。
- [x] 输出 `cadence_review`。
- [x] 校验 late-run 时必须记录漏跑次数。
- [x] Markdown 摘要渲染 late-run。
- [x] Markdown 摘要渲染 missed weekly runs。
- [x] 支持 7 天周报运行节奏。
- [x] 支持 30 天决策报告运行节奏。
- [x] 新增 `tools/check_skills_audit_cadence_contract.py`。
- [x] 验证标准计划内重复次数：Day 0 baseline 1 次、weekly run 4 次、Day 30 final run 1 次。
- [x] 验证 weekly evidence 日期：2026-05-23、2026-05-30、2026-06-06、2026-06-13。
- [x] 验证原始审计结束日期：2026-06-15。
- [x] 验证 warning triage 是事件触发流程且不设固定重复次数。
- [x] 验证 post-final 运行只属于 monitoring evidence，不能授权 profile apply。
- [x] 将 cadence checker 接入 `tools/run_openspec_guard.py`。
- [x] 将 cadence checker 登记到 `tools/safety_rule_script_backing_registry.json`。
- [x] 增加 `test/check_skills_audit_cadence_contract.test.py`。
- [x] 将 cadence 测试登记到 `tools/ci/ci_test_manifest.json`。
- [x] Guard JSON 聚合测试覆盖 cadence checker。
- [x] 支持 warning 延迟 triage 恢复路径。
- [x] 日志不可读时避免把 0 warning 当成无 warning。
- [x] 隐私脱敏失败时支持暂停并重跑。
- [x] 紧急例外通过人工记录和明确授权处理。

### Task 13：输出、人类可读摘要与 stdout

- [x] JSON 报告输出审计窗口。
- [x] JSON 报告输出 enabled plugins summary。
- [x] JSON 报告输出 inventory summary。
- [x] JSON 报告输出 budget warning 统计。
- [x] JSON 报告输出 explicit skill 统计。
- [x] JSON 报告输出 `SKILL.md` 读取统计。
- [x] JSON 报告输出 profile helper 调用统计。
- [x] JSON 报告输出 module evidence。
- [x] JSON 报告输出 script capability boundaries。
- [x] Markdown 摘要输出审计窗口。
- [x] Markdown 摘要输出配置面摘要。
- [x] Markdown 摘要输出 warning 结论。
- [x] Markdown 摘要输出证据表。
- [x] Markdown 摘要输出噪声复核。
- [x] Markdown 摘要输出决策建议。
- [x] Markdown 摘要输出人工冲突复核。
- [x] Markdown 摘要输出风险与恢复路径。
- [x] Markdown 摘要输出不执行清单。
- [x] stdout 输出 audit state。
- [x] stdout 输出 audit state blockers。
- [x] stdout 输出 log evidence 可用性。
- [x] stdout 输出 warning 样本数量与摘录。
- [x] stdout 输出 warning severity。
- [x] stdout 输出 audit-only safety。
- [x] stdout 输出 runtime path privacy。
- [x] stdout 输出 cadence review。
- [x] stdout 输出 warning triage。
- [x] stdout 输出 manual evidence。
- [x] stdout 输出 noise review。
- [x] stdout 输出 script capability boundaries。
- [x] stdout 输出 alias registry。
- [x] stdout 输出 decision recommendation。
- [x] stdout 输出 field contract 细节。
- [x] stdout 输出 output retention 门禁。
- [x] stdout 输出 precommit update/archive 门禁。

### Task 14：输出留存门禁

- [x] 新增 `tools/check_skills_audit_output_retention.py`。
- [x] 阻断 tracked / staged / changed `.tmp/` artifact。
- [x] 阻断强制加入 Git 的 `.tmp/skills-usage-audit-*.json`。
- [x] 阻断 `.tmp/` 外原始 `skills-usage-*.json`。
- [x] 允许脱敏 Markdown 摘要。
- [x] 输出 checker 状态。
- [x] 输出 `.tmp/` local-only 策略。
- [x] 输出 raw audit JSON local-only 策略。
- [x] 输出 long-term evidence format。
- [x] 输出 violation count。
- [x] 接入 `tools/run_openspec_guard.py`。
- [x] 增加 `test/check_skills_audit_output_retention.test.py`。
- [x] 将 retention 测试登记到 CI manifest。
- [x] Guard JSON 聚合测试覆盖 retention gate。
- [x] audit 报告字段契约要求 `output_retention`。
- [x] Markdown 摘要渲染输出留存状态。

### Task 15：提交前更新/归档门禁

- [x] 新增并接入 `tools/check_precommit_update_archive.py`。
- [x] 提交前检查已有文件是否需要更新。
- [x] 提交前检查已完成 OpenSpec 是否需要归档。
- [x] 输出 changed path 数。
- [x] 输出 active change 复核数。
- [x] 输出 error count。
- [x] 输出 warning count。
- [x] audit 报告嵌入 `precommit_update_archive`。
- [x] field contract 要求 `precommit_update_archive`。
- [x] checker 失败时阻断报告作为提交证据。
- [x] Markdown 摘要渲染提交前更新/归档门禁状态。
- [x] stdout 渲染提交前更新/归档门禁状态。
- [x] 增加对应测试。
- [x] 登记到 CI manifest / guard 流程。

### Task 16：测试与 CI 覆盖

- [x] 增加 `test/audit_codex_skills_usage.test.py`。
- [x] 覆盖 stdout 编码。
- [x] 覆盖 warning 解析。
- [x] 覆盖 warning triage。
- [x] 覆盖 cadence review。
- [x] 覆盖 repo profile fallback。
- [x] 覆盖 `all_known_plugins` 展开。
- [x] 覆盖日志脱敏。
- [x] 覆盖人工记录。
- [x] 覆盖字段契约。
- [x] 覆盖候选门禁。
- [x] 覆盖候选记录 contract。
- [x] 覆盖 candidate Markdown 非变更行为。
- [x] 覆盖 decision recommendation。
- [x] 覆盖 output retention。
- [x] 覆盖 precommit update/archive。
- [x] 覆盖 skipped-loading triage。
- [x] 覆盖 warning severity。
- [x] `tools/ci/ci_test_manifest.json` 已包含相关测试。


### Task 17：真实观察期与最终复核节奏

- [x] 完成真实 30 天 usage audit 观察期：2026-05-16 至 2026-06-15。
- [x] 固定标准计划内重复次数：Day 0 baseline 1 次、weekly audit 4 次、Day 30 final audit 1 次。
- [x] 固定标准频率：审计期内每 7 天运行一次 weekly `--days 7`，第 30 天运行一次 final `--days 30`。
- [x] 固定原始审计结束日期：2026-06-15。
- [x] 明确 warning triage 是事件触发流程，不设固定次数；每次新的 warning 只运行一次窄窗口 triage。
- [x] 明确 2026-06-15 之后的运行属于 post-final monitoring，不得延长原始 30 天审计窗口。
- [x] 生成最终 30 天 evidence package，并以脱敏 Markdown 长期留证。
- [ ] 人工复核最终 30 天 evidence package。
- [ ] 明确 closure 决策：`closed-no-change`、`review-pending + continue monitoring` 或 `summary-reviewed + preview-only candidate`。
- [ ] 如选择 candidate 路径，必须先明确 `target_profile`，并且只生成 preview-only candidate。

## 13. 本地集成顺序

- [ ] 主目录存在无关脏改时，必须使用隔离 feature worktree。
- [ ] 本地集成前保持 feature branch 干净。
- [ ] 每次本地提交前运行 `python tools/check_precommit_update_archive.py --root . --json`。
- [ ] 编辑本方案文档对后运行 implementation-plan 与 document-pair 检查。
- [ ] 声称仓库 guard 健康前运行 `python tools/run_openspec_guard.py --root .`。
- [ ] feature branch 已提交且干净后运行 `tools/ci/local_mr_review.ps1`。
- [ ] 合入本地 `main` 前运行 `tools/ci/local_gate.ps1`。
- [ ] 本地证据干净后才 fast-forward 本地 `main`。
- [ ] 除非当前用户消息明确授权远端发布，否则不推送 GitLab/GitHub。

## 14. 验收标准与验证

审计脚本每次运行必须输出：

- 审计窗口；
- enabled plugins summary；
- budget warning 次数与最近样本；
- warning triage 状态、窄窗口策略和 warning 后续动作建议；
- explicit skill 使用计数；
- SKILL.md 读取计数；
- profile helper 调用计数；
- 按 plugin/module 聚合的 evidence；
- 脚本能力边界：可靠覆盖项、人工复核需求与增强触发条件；
- apply 建议，但不自动 apply。
- `tools/check_skills_audit_output_retention.py` 的输出留存状态，证明 `.tmp/` artifact 与原始 Skills usage JSON 没有被保留进 Git。
- `tools/check_skills_audit_final_review_state.py` 的最终复核状态，证明当前审计仍处于 `review-pending + continue monitoring`、`summary-reviewed + closed-no-change` 或 `summary-reviewed + preview-only candidate` 中的哪一种，同时在后续明确 `approved-to-apply` receipt 前保持 profile apply 被阻断。
- `tools/check_skills_audit_final_review_precheck.py` 的最终复核预检查状态，证明 noise/manual-conflict 脚本级预检查有证据支撑，同时不标记 summary reviewed、不生成 candidates、不 apply profiles。
- `tools/check_skills_audit_cadence_contract.py` 的 cadence contract 状态，证明原始观察窗口仍为 2026-05-16 至 2026-06-15，计划内审计运行仍固定为 6 次，weekly evidence 日期保持固定，warning triage 仍为事件触发，post-final 运行仍只属于 monitoring evidence。
- `tools/check_precommit_update_archive.py` 的提交前更新/归档状态，证明本轮提交前既有文件更新复核与 OpenSpec 归档门禁已经通过。
- 默认人类可读 stdout 也必须渲染 audit state、audit state blockers、enabled plugins 已匹配/未匹配摘要、current profile 推断、inventory summary、log evidence 可用性、budget warning 最近样本数量、有界脱敏 budget-warning 样本摘录与 7 天计数、warning severity 等级、原因与处理动作、all-descriptions-removed / omitted-additional-skills 压力指标、audit-only safety 的 `audit_only` / `mutates_config` / `edits_plugin_cache` / `hard_load_apply_performed` 标志、runtime path privacy 的 `raw_paths_retained=false`、占位符路径与 `privacy_policy`、cadence review 的 late-run / missed-weekly-runs / weekly-report-review 状态、warning triage 状态、warning triage 窗口策略、warning/skipped-loading 计数、脱敏 skipped-loading 样本摘录、skipped-loading 复核动作、warning triage 后续动作建议与 blockers、explicit skill 使用总数与唯一 skill 数、SKILL.md 读取次数、profile helper 调用次数、`noise_review` 状态、剔除噪声 token 数、`raw_noise_tokens_retained=false`、`max_noise_token_length` 与 `token_privacy_policy`、`manual_evidence` 文件请求/读取数、有效/无效记录数、`raw_notes_retained=false`、`source_paths_retained=false`、`max_path_length`、人工记录隐私策略与来源路径隐私策略、`manual_evidence.conflict_review` 状态、冲突/例外数量、是否需要处置与处置说明、脚本能力边界计数、stable tool-call alias registry 的 policy/evidence level/strong-evidence 禁止标志、alias target 数量和有界 target 摘要、decision recommendation 的 advisory-only / profile-apply 禁止标志、四个决策分桶计数与有界分桶样本、recommendations 条数与前几条建议、字段契约状态/passed/blocker/含 `warning_severity` 的违规分组计数、输出留存门禁状态/checker/violation/local-only 细节和提交前更新/归档门禁状态/checker/提交前标志/既有文件更新复核/OpenSpec 归档复核/变更计数细节，确保非 JSON 运行也能安全复核。
- `test/audit_codex_skills_usage.test.py` 必须覆盖 stdout 编码、warning 解析、warning-triage 标记与窄窗口阻断、warning-triage Markdown 输出、cadence-review 字段契约与 Markdown 输出、中文 announcement、repo profile fallback、`all_known_plugins` 展开、脱敏日志 excerpt redaction marker 完整性、脱敏人工记录摄取、无效人工记录校验、人工记录来源路径隐私、报告字段契约校验、缺失/过期内嵌字段契约的候选门禁阻断、source-report 路径候选门禁阻断、source-report privacy 脱敏、审计 closure-state 门禁与 Markdown blocker 输出、preview-only 候选记录生成、30 天/summary-reviewed 候选门禁阻断、候选记录 rollback/validation 字段、不安全或不完整候选记录的 `candidate_record_contract` 阻断，以及候选 Markdown 不执行清单。
- 回归测试还必须覆盖 `skills2cli audit warnings --since ... --json` 的双来源汇总、private path/secret 脱敏、`raw_log_paths_retained=false` 与 `raw_skill_bodies_retained=false`。
- 回归测试还必须覆盖 explicit skill 误报 token 的路径/secret 脱敏、长度截断，以及 `noise_review` 字段契约阻断未脱敏或缺少隐私字段的报告，并覆盖 `script_capability_boundaries` 字段契约阻断缺失或空边界列表的报告。
- 回归测试还必须覆盖 `decision_recommendation` 字段契约阻断缺失或非 advisory 状态、允许 profile apply、分桶不完整、分桶元素非字符串以及 `bucket_counts` 过期的报告。
- 回归测试还必须覆盖 `module_evidence` 行契约阻断字段缺失/类型错误、plugin 元素非字符串、strong 计数为负或过期、mapped-tool 证据被计为强证据、跨项目效用未要求人工复核以及 recommendation 不在允许列表中的报告。
- 回归测试还必须覆盖 `module_evidence` recommendation 与阈值不一致的报告，防止旧行把与强/弱证据计数矛盾的按需、dormant 或候选建议带入决策。
- 回归测试还必须覆盖输出留存门禁：强制加入 Git 的 `.tmp/` 原始报告、位于 `.tmp/` 之外的原始 `skills-usage-*.json` 报告必须被阻断，脱敏 Markdown 摘要必须允许。
- 回归测试还必须覆盖最终复核状态 checker：允许 pending continuation 在无 candidate/apply 时继续，阻断 `summary-reviewed` 前出现 candidate artifacts，要求 reviewed summary 带显式 outcome，并保持 profile apply 未授权。
- 回归测试还必须覆盖 cadence contract checker：锁定的 6 次运行节奏应通过，缺少固定重复次数说明应失败，错误 final end date 应失败，缺少 post-final monitoring-only 证据应失败。
- 回归测试还必须覆盖提交前更新/归档门禁：报告必须嵌入 `precommit_update_archive` 状态，字段契约必须阻断缺失、未通过或未启用既有文件更新复核 / OpenSpec 归档门禁的报告，脱敏 Markdown 摘要必须渲染该门禁状态。
- 回归测试还必须覆盖 `output_retention` 字段契约阻断缺失或未通过的留存状态，并要求脱敏 Markdown 摘要渲染输出留存状态与长期证据格式。
- 回归测试还必须覆盖 `manual_evidence.conflict_review` 字段契约阻断，以及人工例外 / 已批准 hard-load 例外记录在脱敏 Markdown 摘要中的渲染。
- 回归测试还必须覆盖 skipped-loading warning triage 计数、脱敏 skipped-loading 样本、缺少 skipped-loading triage 字段时的字段契约阻断、`warning_triage` status / window_policy / skipped_loading_review / blockers / 非负计数的值级契约阻断以及 Markdown 渲染。
- 回归测试还必须覆盖 `warning_severity` 字段契约：缺少 `level` / `reason` / `recommended_action`、非法 severity level、以及 severity 文本包含原始私有路径、secret 或独立 token 时必须阻断；默认 stdout 与脱敏 Markdown 摘要必须渲染 `warning_severity` 违规分组计数。
- `tools/ci/ci_test_manifest.json` 必须纳入这些回归测试，保证 local/remote CI 复用同一检查。

每次人工复核报告时，还必须检查误报噪声：

- `explicit_skills` 中如果出现 `and`、`from`、`draft` 等明显不是 skill/profile/plugin 的通用词，不得把它们计入强证据；
- 对无法映射到当前 available skills、profile module、plugin 名称或实际 `SKILL.md` 路径的 token，只能按弱证据或待清洗噪声处理；
- 如果同类误报连续出现，应优先补脚本过滤规则和回归测试，再用该报告做 30 天 profile 决策；
- 30 天最终报告必须包含“噪声/误报复核结论”，哪怕结论是“未发现明显误报”。

## 15. 需要保留的证据

- [ ] 更新后的英文 canonical plan 与中文 companion。
- [ ] 本地 `git diff` 证明除 checker 要求的相关文件外，只修改本方案文档对。
- [ ] `check_implementation_plan_rules` 输出。
- [ ] `check_document_pair_policy` 输出。
- [ ] `check_precommit_update_archive` 输出。
- [ ] `run_openspec_guard` 输出。
- [ ] local MR review 输出。
- [ ] local gate 输出。
- [ ] feature branch commit hash 与最终本地 `main` hash。
- [ ] 如使用一次性 worktree，保存 worktree cleanup receipt。

## 16. 风险与缓解

- [ ] 风险：把 live warning 误判为 `soft-load` 失败。缓解：运行窄窗口 warning triage 并复核 runtime rebuild 语境。
- [ ] 风险：证据不足时过早收缩 profile。缓解：要求 30 天证据、reviewed summary 与 preview-only candidate gate。
- [ ] 风险：低频但有用插件被误判无用。缓解：分类为 on-demand 或 project-scoped，而不是删除。
- [ ] 风险：原始 transcripts、paths 或 secrets 进入 Git。缓解：retention checker、redaction contract 与 sanitized Markdown 长期留证。
- [ ] 风险：人工例外覆盖脚本证据。缓解：要求 conflict review 与明确处置后才能进入 profile 决策。
- [ ] 风险：candidate preview 被误当成 apply 授权。缓解：`approval_state=preview-only` 与显式 `approved-to-apply` gate。
- [ ] 风险：提交前忽略已完成但仍 active 的 OpenSpec changes。缓解：precommit update/archive checker 进入 audit report 与 commit flow。

## 17. 当前未闭环监控事项

原始 30 天审计窗口已经关闭。下面将已完成的日历观察事项与仍需处理的 post-final review / monitoring 事项分开记录。

- [x] 完成真实 30 天 usage audit 观察期：2026-05-16 至 2026-06-15。
- [x] 在审计期内生成本地 7 天周报证据。
- [x] 在 30 天期满后生成最终 JSON 报告，并将原始 JSON 仅保留在本地 `.tmp/`。
- [x] 在 30 天期满后生成最终脱敏 Markdown 摘要。
- [x] 将原始审计结束日期锁定为 2026-06-15。
- [x] 将标准计划内运行次数锁定为 6 次：Day 0 baseline 1 次、weekly run 4 次、Day 30 final run 1 次。
- [x] 记录 warning triage 是事件触发流程，不设固定重复次数。
- [x] 脚本化最终复核状态 checker 已验证当前 pending/closed/candidate/apply-gate 状态。
- [x] 脚本化最终复核预检查 checker 已验证 noise/manual-conflict 机器证据，同时保持 final human-review 与 apply gate 未关闭。
- [x] 脚本化 cadence contract checker 已验证重复次数、weekly 节奏、结束日期、warning-triage 频率与 post-final 边界。
- [ ] 人工复核最终 30 天摘要。
- [ ] 将最终摘要标记为 `summary-reviewed`，或明确记录 `review-pending + continue monitoring`。
- [x] 收口 `reference_files/10.md` 中 invalid `SKILL.md` runtime repair loop：post-repair audit 报告 `invalid_total=0`。
- [x] 收口 `mcp2cli` / `skills2cli` R3/R4 user-level runtime evidence loop：install/update receipts、smoke receipts 与 rollback pointer 均已存在。
- [ ] 处理最终摘要中的噪声误报。
- [ ] 处理最终摘要中的人工冲突或例外。
- [ ] 判断本轮审计是否进入 `closed-no-change`。
- [ ] 如果证据支持变更，生成 profile apply candidate。
- [ ] 为 candidate 指定明确 `target_profile`。
- [ ] 生成 candidate JSON preview。
- [ ] 生成 candidate Markdown preview。
- [ ] 复核 candidate rollback path。
- [ ] 复核 candidate validation plan。
- [x] 增加 `skills2cli audit warnings` 作为 post-final 紧凑只读 warning 来源，同时覆盖 session JSONL 与 `logs_2.sqlite`。
- [ ] post-final 阶段每次新的 `2% skills context budget` warning 后运行窄窗口 warning triage。
- [ ] 对新的 post-final warning triage 结果做人工复核。
- [ ] 对新的 post-final skipped-loading 样本做来源复核。
- [ ] 获得明确 `approved-to-apply` 授权前不执行 profile apply。
- [ ] 如未来获授权执行 profile apply，保存 apply 前后脱敏 diff。
- [ ] 如 apply 后 warning 仍出现，按 rollback path 回滚。
- [ ] 如 apply 后关键能力缺失，按 rollback path 回滚。

## 18. 颗粒度完成清单

只有同时满足以下条件，本方案才算达到足够颗粒度：

- 说明 warning 为什么可能出现在 live turn，而不只出现在启动阶段；
- 区分 soft-load、hard-load/profile apply 与 plugin cache edit；
- 定义强/中/弱证据边界；
- 定义 7 天、30 天和 warning-triage 节奏；
- 要求 `--warning-triage` 使用 `--days 1` 或 `--since`，记录顶层 `warning_triage` 字段，并阻断过宽窗口 triage 报告；
- 定义 JSON 报告字段契约，要求脚本暴露 `field_contract`，并在 candidate generation 时阻断不完整、缺少契约或过期契约的报告；
- 校验决策关键 `audit_state` 嵌套字段，包括允许状态值、原因、下一步动作、profile apply 禁止标志和 blocker list 形状；
- 在脱敏 Markdown 摘要中渲染 audit-state next action、profile-apply allowance 与 blocker 列表；
- 校验决策关键 `log_evidence` 嵌套字段，包括非负 budget-warning 计数、最近 budget-warning 样本计数，以及不保留原始路径、secret、cookie、access token 或独立 token 的有界脱敏样本摘录；
- 校验决策关键 `warning_severity` 嵌套字段，包括必需 `level` / `reason` / `recommended_action`、允许的 `unknown` / `high` / `medium` / `none` 等级，以及不保留原始路径、secret、cookie、access token 或独立 token 的脱敏 reason/action 文本；
- 默认人类可读 stdout 与脱敏 Markdown 摘要渲染 `field_contract` passed 状态、blocker 数量、required/missing/invalid-type 字段计数、embedded-contract 要求，以及包含 `warning_severity` 的嵌套 violation-group 计数，使复核者不依赖原始 JSON 也能定位契约缺口；
- 校验决策关键 `warning_triage` 嵌套字段，包括允许状态、仅字符串且已知的 blocker 值、blocked/blocker 一致性、固定窄窗口策略、非负 warning/skipped-loading 计数、脱敏 skipped-loading 样本摘录、skipped-loading 来源复核值与 recommended action；
- 校验决策关键 `cadence_review` 嵌套字段，并在脱敏 Markdown 摘要中渲染 late-run 与 missed-weekly-run 状态；
- 校验决策关键 `module_evidence` 行字段，包括字符串 plugin 列表、非负 strong/weak 计数、strong-total 一致性、mapped-tool 中证据策略、人工 cross-project 复核、允许的 advisory recommendations 与 recommendation-threshold 一致性；
- 校验决策关键 `decision_recommendation` 嵌套字段，包括 advisory-only 状态、profile-apply 禁止标志、必需 bucket 名称、bucket entry 必须为字符串，以及 bucket-count 一致性；
- 校验决策关键 `output_retention` 嵌套字段，包括 checker identity、`.tmp/` local-only 策略、raw audit JSON local-only 策略、sanitized Markdown 长期证据格式和 violation count；
- 校验决策关键 `precommit_update_archive` 嵌套字段，包括 checker identity、pre-commit gate flag、existing-file update review、completed OpenSpec archive gate、error count、warning count、changed path count 与 active change review count；
- 定义 missed run、delayed warning triage、unreadable logs、privacy sanitization 与 urgent exceptions 的恢复规则；
- 定义最终 30 天决策摘要模板；
- 定义 medium evidence、urgent exceptions 与 removed false positives 的人工记录格式；
- 在任何 post-audit hard-load/profile apply 之前定义 candidate change gate 与 rollback path；
- 要求 candidate generation 始终绑定 JSON report path 与脱敏 Markdown summary path；
- 要求 candidate generation 只接受 `summary-reviewed`、`apply-candidate` 或 `closed-with-candidate` audit state，并阻断 not-ready 或 `closed-no-change` 状态；
- 要求 candidate `source_reports` 在写入 candidate JSON 或 Markdown 前通过 privacy contract；
- 要求生成的 candidate JSON 与 Markdown 暴露 passing `candidate_record_contract`，覆盖 preview-only 安全标志、gate shape、rollback path、validation-plan 完整性、sanitization 与 source-report privacy；candidate Markdown 必须显示非 JSON 复核所需的同一组有界 contract counts 与 blocker 细节；
- 定义 audit data source 的数据最小化、脱敏、留存与不外发边界；
- 定义审计脚本能力边界、已知限制与触发脚本增强的条件；
- 在 JSON 字段契约与脱敏 Markdown 摘要中暴露这些脚本能力边界；
- 定义审计运行状态机、停止条件，以及 audit closure 与 profile apply candidate changes 之间的边界；
- 通过 audit-only 脚本标志暴露 planned-state 记录，并在 Day 0 baseline 存在前阻断 profile-apply candidate；
- 通过 audit-only 脚本标志暴露 paused-state 记录，并在 paused 状态阻断 profile-apply candidate；
- 仅当 reviewed 30-day summary 仍绑定 JSON 与 Markdown source-report paths 时，才暴露 `summary-reviewed` 脚本状态；
- 通过显式 audit-only 脚本标志暴露 closure-state 记录，并报告 blocked closure reasons，而不是静默关闭；
- 定义 frequent、low-frequency 与 no-strong-evidence 情况的阈值；
- 声明 explicit-skill false-positive noise 不得进入 strong evidence；
- 定义 warning severity 与处理动作；
- 声明 `.tmp/` output 默认不提交，长期证据必须脱敏；
- 要求 `tools/check_skills_audit_output_retention.py` 阻断 `.tmp/` artifacts 和 raw `skills-usage-*.json` reports 进入 Git，同时允许脱敏 Markdown 摘要；
- 要求 `tools/check_skills_audit_final_review_state.py` 在未来 continuation、closure 或 candidate decision 前验证最终复核、关闭、candidate 与 apply-gate 状态；
- 要求 `tools/check_precommit_update_archive.py` 状态进入 audit JSON 字段契约与 Markdown 摘要，阻断未检查 existing-file update review 或已完成 OpenSpec changes 未归档的报告；
- 声明 regression-test、OpenSpec guard 与 CI manifest 要求；
- 声明远端发布仍需 GitLab/GitHub 授权门禁。
