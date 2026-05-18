---
doc_id: codex_skills_usage_audit_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
status: active
doc_class: implementation_plan
created_at: 2026-05-16
---

# Codex Skills Usage Audit 计划

## 1. 背景

`⚠ Exceeded skills context budget of 2%` 可能不只在 Codex 进程启动时出现。实际会话中，Codex runtime 可能在每轮请求、resume、会话重打包、skills 列表重新注入或上下文裁剪时重新计算 model-visible skills surface。因此，某个会话启动时没有看到警示，并不代表后续 turn 不会触发。

`soft-load` 不会修改启动可见 skills 列表，也不会把被 2% budget 挤掉的 skills 放回自动可见列表。它只是在当前会话内按需读取某个模块的 SKILL.md 或 reference，用普通上下文补足过程知识。因此：

- soft-load 是当前会话的补救与按需知识加载方式；
- hard-load/profile apply 才会改变下一次启动或 resume 后的 plugin/skills 可见面；
- 在缺少 usage evidence 前，不应直接把默认 profile 收缩到 `core-dev`；
- 对 `company-ops`、`market-research`、`web-saas`、`customer-comms`、`creative-content` 等模块，应先观察一个月，再决定是否常驻、按项目启用或仅按需加载。

## 2. 审计目标

本计划建立一个 30 天 audit-only 流程，用事实数据决定后续 profile apply 策略，避免误禁用仍有长期价值的 plugin skills。

审计回答四个问题：

1. 哪些 skills/plugins 在最近 30 天有强使用证据？
2. 哪些模块只是被提到，但没有被调用或读取？
3. 哪些 `2% skills context budget` 警示发生在什么时间、什么会话或什么项目上下文？
4. 哪些能力应常驻、按项目 hard-load、按需 soft-load，或仅保留在 `full` 临时排障 profile？

## 3. 证据分级

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

## 4. Audit-only 规则

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

## 5. 指定脚本

### 5.1 采集脚本

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 30 --json --output .\.tmp\skills-usage-audit-latest.json
```

默认数据源：

- `C:\Users\lenovo\.codex\sessions/**/*.jsonl` - 会话 transcript，用于识别显式 skill 声明与 SKILL.md 读取。
- `C:\Users\lenovo\.codex\logs_2.sqlite` - runtime 日志库，用于统计 skills budget warning。
- `C:\Users\lenovo\.codex\config.toml` - 用户级 plugin enabled 状态来源，仅用于 audit-only 报告。
- `C:\Users\lenovo\.codex\skills\plugin-modules\references\profiles.json` - 模块 registry，用于按 profile 聚合 plugin evidence。

### 5.2 基线快照

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 0 --baseline --json --output .\.tmp\skills-usage-baseline-2026-05-16.json
```

基线记录当前 enabled plugins、profile modules、warning counter 与 inventory summary。基线不修改 `config.toml`。

### 5.3 每周汇总

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 7 --json --output .\.tmp\skills-usage-audit-7d.json
```

### 5.4 30 天决策报告

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 30 --json --output .\.tmp\skills-usage-audit-30d.json --summary-output .\.tmp\skills-usage-audit-30d-summary.md --manual-notes .\.tmp\skills-usage-audit-notes-YYYY-MM-DD.md
```

`--summary-output` 写入脱敏 Markdown 决策摘要。它只作为复核证据，不得修改 `config.toml`、plugin cache 或 hard-load profile。

如需为后续可回滚调整预生成候选记录，应增加 `--target-profile`、`--candidate-output`、`--summary-reviewed`，并可选增加 `--candidate-summary-output`：

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 30 --json --output .\.tmp\skills-usage-audit-30d.json --summary-output .\.tmp\skills-usage-audit-30d-summary.md --summary-reviewed --target-profile core-dev --candidate-output .\.tmp\skills-profile-candidate.json --candidate-summary-output .\.tmp\skills-profile-candidate.md
```

候选输出永远是 `approval_state=preview-only`，不得修改 `config.toml`、plugin cache 或 hard-load profile。`--candidate-output` 或 `--candidate-summary-output` 必须搭配显式 `--target-profile`；脚本不得从当前 profile、文件名或普通“继续”中推断目标 profile。缺少 `--summary-reviewed`、30 天审计窗口、`--output`、`--summary-output` 或 `--target-profile` 时，候选生成门禁必须记录为 blocked。

### 5.5 Windows stdout 与回归测试

脚本必须在 Windows 非 UTF-8 控制台下仍能输出 `--json`。如果 stdout 无法编码 `⚠` 等字符，stdout 可以退化为 JSON 合法的反斜杠转义形式；但 `--output` 写入的报告文件仍必须保持 UTF-8 原文。

相关回归测试必须覆盖：

- `⚠ Exceeded skills context budget of 2%` 的 stdout fallback；
- 中文 `使用技能：` 与英文 `Using skill:` 的显式 skill announcement 识别；
- `logs_2.sqlite` 中 budget warning 的 `omitted_additional_skills` 与 `all_descriptions_removed` 提取；
- `full` profile 中 `plugins: "all_known_plugins"` 不能被拆成单个字符；
- 脚本在缺少用户级 plugin-modules profile 时，必须回退读取仓库内 `tools/skill_sources/plugin-modules/references/profiles.json`。

### 5.6 报告字段契约

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
| `log_evidence` | budget warning、7 天 warning 数、`All skill descriptions were removed`、最大 omitted skills 数和 skipped loading 证据 | 判断 warning 是否仍在会话中出现，以及严重度是否越过方案阈值 |
| `warning_triage` | warning 后复核标记、窄窗口门禁、triage 窗口内 warning 计数和后续动作建议 | 防止把周报/月报误当成 turn 级 warning triage 证据 |
| `session_evidence` | explicit skills、SKILL.md reads、helper calls、tool calls | 作为强/中/弱证据输入 |
| `manual_evidence` | 脱敏人工记录计数、无效记录校验以及中证据/例外/噪声摘要 | 保留人工复核证据，同时不留存原始 transcript |
| `noise_review` | explicit skill 噪声 token 的脱敏、截断、误报计数和强证据排除策略 | 防止误报 token、路径碎片或 mojibake 文本进入强证据或长期留存 |
| `script_capability_boundaries` | 脚本可靠覆盖项、仍需人工复核的边界、已知限制与脚本增强触发条件 | 防止把 audit helper 误当作全知事实源 |
| `output_retention` | 来自 `tools/check_skills_audit_output_retention.py` 的留存状态，包括 `.tmp/` 本地-only 策略、原始 JSON 本地-only 策略、长期证据格式和违规数量 | 防止报告隐藏原始 audit artifact 是否被误保留进 Git |
| `runtime_paths` | repo root、Codex home 和 `config.toml` 的脱敏运行路径占位符、路径类别标签，并保持 `raw_paths_retained=false` | 防止 JSON 和 Markdown 报告长期留存原始本地用户路径，同时仍说明本次审计扫描了哪些运行输入 |
| `module_evidence` | 按 profile module 汇总的强证据、中证据说明、弱证据和跨项目复核字段 | 生成 profile 决策候选，同时避免把中证据当作强证据 |
| `decision_recommendation` | 从 `module_evidence` 派生的只读决策分桶 | 让复核者看到 profile 复核、按需加载、人工复核和 dormant 模块，但不允许 profile apply |
| `cadence_review` | late-run 与漏跑周报标记 | 防止 30 天决策摘要隐藏审计节奏偏离 |
| `recommendations` | 审计建议 | 只能作为建议，不能自动 apply |

审计脚本还必须校验运行路径隐私：顶层 `root`、顶层 `codex_home`、`config_summary.config_path` 以及 `runtime_paths.root/codex_home/config_path` 都不得包含原始 Windows、POSIX home、UNC、token、cookie 或 secret 路径。报告必须用 `[REPO_ROOT]`、`[CODEX_HOME]`、`[CODEX_HOME]/config.toml` 等占位符替代原始绝对路径，并且 `runtime_paths.raw_paths_retained` 必须保持 `false`。

审计脚本必须为每份生成报告计算 `field_contract` 结果。该结果记录 `status`、`passed`、必需字段、缺失字段、字段类型错误、audit-only 安全标志违规，以及会影响决策的嵌套字段违规。`audit_state` 契约必须要求 `state`、`reason`、`next_action` 与 `profile_apply_allowed`，防止报告丢失状态机上下文。它还必须拒绝未知 audit state，拒绝 `profile_apply_allowed=true` 或其他非 false 值，并要求出现的状态 blocker 字段（`close_blockers`、`candidate_blockers`、`summary_review_blockers`、`pause_blockers` 或 `warning_triage_blockers`）必须是字符串列表。脱敏 Markdown 摘要还必须渲染 audit state 的 next action、profile apply 许可标志，以及这些字段中的 blockers；没有 blocker 时写入 `none`。`warning_triage` 契约必须要求 `requested`、`status`、`blockers`、`window_policy`、`window_ok`、`budget_warning_count`、`skipped_loading_count`、`recent_skipped_loading_samples`、`skipped_loading_review` 与 `recommended_action`，防止 warning 复核报告遗漏 triage 状态、窄窗口策略、skipped-loading 来源复核或后续动作。其值级契约还必须拒绝未知 `status`、非 `use_days_1_or_since_for_warning_triage` 的 `window_policy`、非 `none` / `record_source_and_do_not_edit_vendor_cache_without_authorization` 的 `skipped_loading_review`、非字符串或未知 blocker、`status=blocked` 但 blocker 为空、blocker 非空但 status 不是 `blocked`，以及负数 warning / skipped-loading 计数字段。只要 `field_contract.status != passed`，该报告就是不完整证据；必须先修脚本或重跑报告，才能进入 profile 决策。候选生成必须要求报告内嵌 `field_contract`；来自旧脚本或人工改写后缺少/过期内嵌契约的报告，必须阻断并要求重新生成。
`noise_review` 契约必须要求 `raw_noise_tokens_retained=false`、`max_noise_token_length`、`token_privacy_policy` 与脱敏后的 `explicit_skill_noise_removed`。噪声 token 在进入报告前必须先替换私有路径、secret、cookie 或 token，并截断到固定长度；如果仍检测到原始私有路径、secret 或过长 token，字段契约必须失败。
`script_capability_boundaries` 契约必须要求 `policy`、`reliable_coverage`、`human_review_required_for` 和 `enhancement_triggers`。这些列表必须存在且非空，避免报告暗示 audit helper 是全知事实源。
`output_retention` 契约必须要求 `status`、`ok`、`checker`、`tmp_outputs_local_only`、`raw_audit_json_local_only`、`long_term_evidence_format` 和 `violation_count`。只有留存 checker 自身通过、`.tmp/` 输出与原始 audit JSON 都标记为本地-only，且长期证据格式为 `sanitized_markdown_summary` 时，该契约才能通过。
`cadence_review` 契约必须要求 `late_run`、`missed_weekly_runs` 与 `weekly_report_review`；`missed_weekly_runs` 必须是 `null` 或非负整数，且 `late_run=true` 时必须显式记录漏跑次数。脱敏 Markdown 摘要必须在审计窗口部分渲染这些节奏字段，让 30 天复核者无需打开原始 JSON 也能看到审计节奏是否偏离。
`module_evidence` 契约必须在其进入 `decision_recommendation` 或候选生成前校验每一行。每行必须包含 module 名称、plugin 列表、strong helper 计数、strong skill-path 计数、strong total、默认候选阈值、mapped-tool 中证据计数与策略、中证据说明、弱提及、跨项目效用和 recommendation。数值计数必须是非负整数，`strong_total` 必须等于 helper calls 加 skill-path reads，plugin 元素必须是字符串，mapped tool calls 必须保持为中证据，跨项目效用必须要求人工复核，recommendation 只能使用已批准的 advisory 取值。recommendation 还必须匹配阈值规则：`strong_total >= default_candidate_threshold` 才是 profile 复核候选，`0 < strong_total < threshold` 保持按需加载，`strong_total == 0` 且存在弱提及时只能是 mentioned-only，没有强证据也没有弱提及时保持 dormant/restorable。
`decision_recommendation` 契约必须要求 advisory-only 状态、非 apply 策略、`profile_apply_allowed=false`、四个分桶列表（`profile_review_candidates`、`on_demand_soft_load`、`manual_review_medium_or_weak`、`dormant_restorable`）以及一致的 `bucket_counts`。如果分桶缺失、类型错误、包含非字符串 module 名称、允许 profile apply，或 `bucket_counts` 与实际分桶长度不一致，字段契约必须失败，不能进入 profile 决策或候选生成。
`manual_evidence.conflict_review` 契约必须要求状态、策略、冲突/例外计数、是否需要处置以及处置说明。人工 `exception` 记录和 `approved hard-load exception` 记录必须暴露为 `manual_conflict_or_exception_review_required`，避免 30 天复核者漏看与脚本证据冲突或超出脚本证据的人工判断。


### 5.7 审计节奏、留存与报告命名

为避免一个月 audit 过程中偏离，使用固定节奏。

| 时间点 | 命令 | 输出文件 | 用途 |
| --- | --- | --- | --- |
| 第 0 天 | `--days 0 --baseline` | `.tmp/skills-usage-baseline-YYYY-MM-DD.json` | 冻结初始 enabled plugins、inventory 和 warning 状态 |
| 每周 | `--days 7` | `.tmp/skills-usage-audit-7d-YYYY-MM-DD.json` | 发现会话中新增 warning 与模块使用趋势 |
| 漏跑周报补跑 | `--days 7 --late-run --missed-weekly-runs N` | `.tmp/skills-usage-audit-7d-late-YYYY-MM-DD.json` | 保留明确的节奏偏离标记，而不是伪造漏跑报告 |
| 第 30 天 | `--days 30` | `.tmp/skills-usage-audit-30d-YYYY-MM-DD.json` | 形成是否调整默认 profile 的证据包 |
| 出现 warning 后 | `--warning-triage --days 1` 或 `--warning-triage --since` | `.tmp/skills-usage-warning-triage-YYYY-MM-DD.json` | 定位 warning 是否来自当前会话重打包 |

`.tmp/` 报告默认不入 Git；如果需要长期留证，只提交经过脱敏和摘要化的 Markdown 结论，不提交完整 session transcript、token、私有路径或 vendor cache 内容。

`--warning-triage` 是 warning 出现后的 audit-only 复核标记，必须搭配窄窗口：使用 `--days 1`，或使用显式 `--since` 覆盖 warning 时间点。如果 `--warning-triage` 搭配 `--days 7`、`--days 30` 等过宽窗口，报告必须写入 `warning_triage.status=blocked`、`warning_triage_window_not_narrow`，并保持 `audit_state.reason=warning_triage_window_too_broad`。triage 报告还必须汇总 `Skipped loading` warning 数量，并记录“先记录来源、不批量改 vendor cache”的复核策略。`warning_triage.status` 只能是 `not_requested`、`blocked`、`log_source_unavailable`、`warning_found` 或 `no_warning_found_in_triage_window`；`blockers` 只能保存已知字符串 blocker，且当前只允许 `warning_triage_window_not_narrow`。该标记不得修改 `config.toml`、plugin cache 或 hard-load profile。

### 5.8 偏离控制与异常恢复

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

### 5.9 30 天决策摘要模板

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

### 5.10 人工证据与例外记录格式

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

### 5.11 Profile apply 候选变更门禁

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
- 候选生成还必须附加并渲染 `candidate_record_contract`；当候选必需字段、preview-only 安全标志、`source_reports_privacy.status=passed`、`candidate_generation_gate.allowed/blockers`、`rollback_path.restore_command` / `restart_required` 或非空 `validation_plan` 缺失或无效时，该契约必须失败，且该候选不得被当成可 apply 证据；
- `approval_state=preview-only` 只能运行 preview，不得修改 `config.toml`；
- `approved-to-apply` 必须来自用户明确授权，不能由“继续”或普通确认替代；
- apply 后必须保存 apply 前后的脱敏 diff 摘要；
- 如果 apply 后 warning 仍出现或关键能力缺失，优先按 `rollback_path` 恢复，不在同一轮中连续叠加多个 profile 改动。

### 5.12 数据最小化、脱敏与留存边界

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

### 5.13 脚本能力边界与增强触发条件

JSON 报告和脱敏 Markdown 摘要必须通过 `script_capability_boundaries` 暴露这条边界。若 `policy`、`reliable_coverage`、`human_review_required_for` 或 `enhancement_triggers` 缺失、类型错误或为空，字段契约必须失败。


`tools/audit_codex_skills_usage.py` 是审计辅助脚本，不是全知事实源。30 天报告必须同时说明“脚本已经可靠覆盖什么”和“仍需人工复核什么”。

当前脚本能力边界：

- 可以统计 `config.toml` 中 plugin enabled/disabled/unknown 状态；
- 可以统计 user/repo/plugin `SKILL.md` inventory 数量；
- 可以从 session transcript 中提取显式 skill announcement、`SKILL.md` 路径读取、profile helper 调用和 tool call 名称；
- 可以从 `logs_2.sqlite` 中提取 skills budget warning、`All skill descriptions were removed`、`additional skills` 数量与 skipped loading 样本；
- 可以按 profile module 聚合 helper 调用和 plugin skill path 读取，形成初步建议。

当前已知限制：

- `weak_plugin_mentions` 只能说明文本趋势，不能证明真实调用；
- `explicit_skills` 可能出现自然语言或示例 token 误报，必须经过噪声复核；
- `tool_call_names` 目前不等同于 plugin/module 使用，除非能映射到明确能力面；
- 日志库不可读、日志轮转或旧会话缺失时，warning 统计可能低估；
- profile module 聚合依赖 registry，registry 缺失或过期时，报告只能作为不完整证据。

触发脚本增强而不是人工绕过的条件：

- 同一类误报在两次 weekly report 中重复出现；
- 30 天摘要需要依赖某类证据，但脚本只给出 weak mention；
- `tool_call_names` 中出现可映射到 plugin/module 的稳定模式，但脚本未聚合；
- warning 发生在会话中但 `logs_2.sqlite` 无法定位，需要新增可复核的数据源；
- profile registry 与实际 enabled plugin 面不一致，导致 module evidence 明显错配。

增强脚本时必须同步更新回归测试和本计划；未补测试前，不得把新解析规则作为 30 天最终决策依据。

### 5.14 审计运行状态机与停止条件

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

### 5.15 输出留存门禁

审计输出留存现在由 `tools/check_skills_audit_output_retention.py` 提供脚本化保护，并以 `check_skills_audit_output_retention` 步骤接入 `tools/run_openspec_guard.py`。

当以下路径处于 tracked、staged、changed 或 commit-visible untracked 状态时，留存门禁必须在提交、本地集成或发布前失败：

- 任何 `.tmp/` artifact，包括即使用 `git add -f` 强制加入 Git 的 `.tmp/skills-usage-audit-30d.json`；
- 文件名以 `skills-usage-audit`、`skills-usage-baseline`、`skills-usage-warning` 或 `skills-usage-report` 开头的原始 Skills usage audit JSON，即使该文件不在 `.tmp/` 下。

长期留证必须是脱敏 Markdown 摘要，或另一种已经明确复核过的脱敏文档。原始 JSON 报告只能作为本地复现与复核工作文件。如果复核者需要持久证据，应从原始 JSON 重新生成 Markdown 摘要，完成隐私复核后提交脱敏摘要，而不是提交原始报告。

回归覆盖位于 `test/check_skills_audit_output_retention.test.py`，且必须登记到 `tools/ci/ci_test_manifest.json`。Guard JSON 聚合测试也必须包含 `check_skills_audit_output_retention`，避免 CI 可见的 guard 顺序静默丢失留存门禁。

## 6. 决策规则

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

## 7. 通过标准

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
- `test/audit_codex_skills_usage.test.py` 必须覆盖 stdout 编码、warning 解析、warning-triage 标记与窄窗口阻断、warning-triage Markdown 输出、cadence-review 字段契约与 Markdown 输出、中文 announcement、repo profile fallback、`all_known_plugins` 展开、脱敏日志 excerpt redaction marker 完整性、脱敏人工记录摄取、无效人工记录校验、人工记录来源路径隐私、报告字段契约校验、缺失/过期内嵌字段契约的候选门禁阻断、source-report 路径候选门禁阻断、source-report privacy 脱敏、审计 closure-state 门禁与 Markdown blocker 输出、preview-only 候选记录生成、30 天/summary-reviewed 候选门禁阻断、候选记录 rollback/validation 字段、不安全或不完整候选记录的 `candidate_record_contract` 阻断，以及候选 Markdown 不执行清单。
- 回归测试还必须覆盖 explicit skill 误报 token 的路径/secret 脱敏、长度截断，以及 `noise_review` 字段契约阻断未脱敏或缺少隐私字段的报告，并覆盖 `script_capability_boundaries` 字段契约阻断缺失或空边界列表的报告。
- 回归测试还必须覆盖 `decision_recommendation` 字段契约阻断缺失或非 advisory 状态、允许 profile apply、分桶不完整、分桶元素非字符串以及 `bucket_counts` 过期的报告。
- 回归测试还必须覆盖 `module_evidence` 行契约阻断字段缺失/类型错误、plugin 元素非字符串、strong 计数为负或过期、mapped-tool 证据被计为强证据、跨项目效用未要求人工复核以及 recommendation 不在允许列表中的报告。
- 回归测试还必须覆盖 `module_evidence` recommendation 与阈值不一致的报告，防止旧行把与强/弱证据计数矛盾的按需、dormant 或候选建议带入决策。
- 回归测试还必须覆盖输出留存门禁：强制加入 Git 的 `.tmp/` 原始报告、位于 `.tmp/` 之外的原始 `skills-usage-*.json` 报告必须被阻断，脱敏 Markdown 摘要必须允许。
- 回归测试还必须覆盖 `output_retention` 字段契约阻断缺失或未通过的留存状态，并要求脱敏 Markdown 摘要渲染输出留存状态与长期证据格式。
- 回归测试还必须覆盖 `manual_evidence.conflict_review` 字段契约阻断，以及人工例外 / 已批准 hard-load 例外记录在脱敏 Markdown 摘要中的渲染。
- 回归测试还必须覆盖 skipped-loading warning triage 计数、脱敏 skipped-loading 样本、缺少 skipped-loading triage 字段时的字段契约阻断、`warning_triage` status / window_policy / skipped_loading_review / blockers / 非负计数的值级契约阻断以及 Markdown 渲染。
- `tools/ci/ci_test_manifest.json` 必须纳入这些回归测试，保证 local/remote CI 复用同一检查。

每次人工复核报告时，还必须检查误报噪声：

- `explicit_skills` 中如果出现 `and`、`from`、`draft` 等明显不是 skill/profile/plugin 的通用词，不得把它们计入强证据；
- 对无法映射到当前 available skills、profile module、plugin 名称或实际 `SKILL.md` 路径的 token，只能按弱证据或待清洗噪声处理；
- 如果同类误报连续出现，应优先补脚本过滤规则和回归测试，再用该报告做 30 天 profile 决策；
- 30 天最终报告必须包含“噪声/误报复核结论”，哪怕结论是“未发现明显误报”。

## 8. Warning 分级与处理动作

| 现象 | 判断 | 处理动作 |
| --- | --- | --- |
| 启动时无 warning，但会话中出现 warning | soft-load 仍可能有效；runtime 在 turn 级重建 model-visible skills surface | 运行 `--warning-triage --days 1` 或 `--warning-triage --since ...`，记录发生 turn，不立即 hard-load apply |
| `All skill descriptions were removed` | 当前 skills surface 已严重超预算 | 下轮启动避免 `full`，使用 `core-dev` 或任务 profile；审计结束前仍不删除 plugin cache |
| `additional skills were not included` 数量持续升高 | 自动可见列表仍过大 | 根据 30 天强证据缩小默认 profile，保留 dormant 恢复路径 |
| `Skipped loading` 指向无效 SKILL.md | 单个 skill 元数据错误或 vendor cache 问题 | 先通过 `warning_triage.skipped_loading_*` 字段记录来源；除非用户授权，不批量改 vendor cache |

## 9. 与 soft-load 的关系

如果会话中再次出现 `2% skills context budget` warning，不能说明 soft-load 失败。正确解释是：runtime 仍在为当前 turn 构造 model-visible skills surface，而 soft-load 不参与这个预算面。soft-load 只解决“当前任务需要的知识如何按需读取”，不解决“全局自动可见列表过大”。

## 10. 后续动作

审计结束前，只允许生成报告和 preview profile。审计结束后，如证据支持，再新开 bounded change 或使用已批准的 profile helper 执行 hard-load apply。远端发布仍按本仓库 local-main-first 与 GitLab/GitHub 授权规则执行。

## 11. 颗粒度完成检查清单

本方案被视为“颗粒度足够”必须同时满足：

- 说明 warning 为什么可能在会话中而非启动时出现；
- 区分 soft-load、hard-load/profile apply、plugin cache 修改三类动作；
- 明确 strong / medium / weak evidence 的边界；
- 明确 7 天、30 天、warning triage 的运行节奏；
- 要求 `--warning-triage` 只能搭配 `--days 1` 或 `--since`，输出顶层 `warning_triage` 字段，并阻断过宽窗口 triage 报告；
- 明确 JSON 报告字段契约，并要求脚本输出 `field_contract` 且在候选生成时阻断不完整、缺少契约或契约过期的报告；
- 校验决策关键的 `audit_state` 嵌套字段，包括允许的状态值、原因、下一步动作、profile apply 禁止标志与 blocker 列表形状；
- 在脱敏 Markdown 摘要中渲染 audit-state 下一步动作、profile apply 许可标志与 blocker 列表；
- 校验决策关键的 `warning_triage` 嵌套字段，包括允许的状态值、blockers 字符串列表与已知 blocker 取值、blocked/blocker 一致性、固定窄窗口策略、非负 warning/skipped-loading 计数、skipped-loading 来源复核取值与后续动作建议；
- 校验决策关键的 `cadence_review` 嵌套字段，并在脱敏 Markdown 摘要中渲染 late-run 与漏跑周报状态；
- 校验决策关键的 `module_evidence` 行字段，包括字符串 plugin 列表、非负 strong/weak 计数、strong-total 一致性、mapped-tool 中证据策略、跨项目人工复核、允许的 advisory recommendation 以及 recommendation 与阈值一致性；
- 校验决策关键的 `decision_recommendation` 嵌套字段，包括 advisory-only 状态、profile apply 禁止标志、必需分桶名称、分桶元素只能是字符串以及分桶计数一致性；
- 校验决策关键的 `output_retention` 嵌套字段，包括 checker 身份、`.tmp/` 本地-only 策略、原始 audit JSON 本地-only 策略、脱敏 Markdown 长期证据格式和违规数量；
- 明确漏跑、warning 延迟 triage、日志不可读、隐私脱敏和紧急例外的恢复规则；
- 明确 30 天最终决策摘要模板；
- 明确中证据、紧急例外和误报剔除的人工记录格式；
- 明确 30 天审计后进入 hard-load/profile apply 前的候选变更门禁与回滚路径；
- 要求候选生成必须绑定 JSON 报告路径与脱敏 Markdown 摘要路径；
- 要求候选生成只接受 `summary-reviewed`、`apply-candidate` 或 `closed-with-candidate` 审计状态，阻断未就绪或已 `closed-no-change` 的审计状态；
- 要求 candidate `source_reports` 在写入候选 JSON 或 Markdown 前必须通过隐私契约；
- 要求生成的候选 JSON 和 Markdown 暴露通过的 `candidate_record_contract`，覆盖 preview-only 安全标志、门禁形状、回滚路径与验证计划完整性；
- 明确 audit 数据源的数据最小化、脱敏、留存和禁止外发边界；
- 明确 audit 脚本的能力边界、已知限制和触发脚本增强的条件；
- 明确审计运行状态机、停止条件，以及审计结束后与 profile apply 候选变更的分界；
- 通过 audit-only 脚本参数暴露 planned-state 记录，并在 Day 0 baseline 之前阻断 profile-apply 候选生成；
- 通过 audit-only 脚本参数暴露 paused-state 记录，并在暂停期间阻断 profile-apply 候选生成；
- 只有在已复核 30 天摘要仍绑定 JSON 与 Markdown source-report 路径时，才通过脚本状态暴露 `summary-reviewed`；
- 通过明确的 audit-only 脚本参数暴露 closure-state 记录，并在无法关闭时报告 blocked closure reasons，而不是静默关闭；
- 明确高频/低频/无强证据的阈值；
- 明确 explicit skill 误报噪声不得进入强证据；
- 明确 warning 分级和处理动作；
- 明确输出文件默认不入 Git，长期留证必须脱敏摘要；
- 要求 `tools/check_skills_audit_output_retention.py` 阻断 `.tmp/` artifact 与原始 `skills-usage-*.json` 报告进入 Git，同时允许脱敏 Markdown 摘要；
- 明确回归测试、OpenSpec guard 和 CI manifest 要求；
- 在 JSON 字段契约和脱敏 Markdown 摘要中暴露脚本能力边界；
- 明确远端发布仍受 GitLab/GitHub 授权门控制。
