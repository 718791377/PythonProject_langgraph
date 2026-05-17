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

候选输出永远是 `approval_state=preview-only`，不得修改 `config.toml`、plugin cache 或 hard-load profile。缺少 `--summary-reviewed`、30 天审计窗口、`--output` 或 `--summary-output` 时，候选生成门禁必须记录为 blocked。

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
| `module_evidence` | 按 profile module 汇总的强证据、中证据说明、弱证据和跨项目复核字段 | 生成 profile 决策候选，同时避免把中证据当作强证据 |
| `cadence_review` | late-run 与漏跑周报标记 | 防止 30 天决策摘要隐藏审计节奏偏离 |
| `recommendations` | 审计建议 | 只能作为建议，不能自动 apply |

审计脚本必须为每份生成报告计算 `field_contract` 结果。该结果记录 `status`、`passed`、必需字段、缺失字段、字段类型错误、audit-only 安全标志违规，以及会影响决策的嵌套字段违规。`audit_state` 契约必须要求 `state`、`reason`、`next_action` 与 `profile_apply_allowed`，防止报告丢失状态机上下文。`warning_triage` 契约必须要求 `requested`、`status`、`blockers`、`window_policy`、`window_ok`、`budget_warning_count` 与 `recommended_action`，防止 warning 复核报告遗漏 triage 状态、窄窗口策略或后续动作。只要 `field_contract.status != passed`，该报告就是不完整证据；必须先修脚本或重跑报告，才能进入 profile 决策。候选生成必须要求报告内嵌 `field_contract`；来自旧脚本或人工改写后缺少/过期内嵌契约的报告，必须阻断并要求重新生成。
`noise_review` 契约必须要求 `raw_noise_tokens_retained=false`、`max_noise_token_length`、`token_privacy_policy` 与脱敏后的 `explicit_skill_noise_removed`。噪声 token 在进入报告前必须先替换私有路径、secret、cookie 或 token，并截断到固定长度；如果仍检测到原始私有路径、secret 或过长 token，字段契约必须失败。

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

`--warning-triage` 是 warning 出现后的 audit-only 复核标记，必须搭配窄窗口：使用 `--days 1`，或使用显式 `--since` 覆盖 warning 时间点。如果 `--warning-triage` 搭配 `--days 7`、`--days 30` 等过宽窗口，报告必须写入 `warning_triage.status=blocked`、`warning_triage_window_not_narrow`，并保持 `audit_state.reason=warning_triage_window_too_broad`。该标记不得修改 `config.toml`、plugin cache 或 hard-load profile。

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
5. 噪声复核：列出被剔除的明显误报 token，例如 `and`、`from`、`draft`；说明它们未计入强证据。
6. 决策建议：常驻默认、项目 profile、按需 soft-load、保留 dormant、或仅留在 `full` 排障 profile。
7. 风险与恢复路径：如果禁用或移出默认 profile，写明如何恢复、使用哪个 helper（例如 `set_plugin_profile.ps1 -RestoreLatest -Apply`）、是否需要通过 `codex-ohmy` 重启/新会话。
8. 不执行清单：明确哪些动作本报告没有执行，例如未修改 `config.toml`、未编辑 plugin cache、未 hard-load apply。

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

人工记录不能覆盖脚本证据：如果人工判断与 JSON 报告冲突，30 天摘要必须同时列出冲突和处理结论。

人工记录来源路径只允许用于本地审计执行，不能作为原始证据留存。写入 `manual_evidence.invalid_notes` 或候选 source 引用前，必须先对路径做脱敏和长度限制；如果 manual evidence 仍包含原始私有路径、secret 赋值、独立 token，或标记为保留了原始来源路径，字段契约必须失败。

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

门禁规则：

- 审计脚本可以通过 `--candidate-output` 与 `--candidate-summary-output` 生成候选 JSON/Markdown，但这些输出只能作为 preview 记录；
- 候选生成必须记录门禁结果，且门禁要求 30 天审计窗口与 `--summary-reviewed`；
- 候选生成必须要求 30 天 JSON 报告与脱敏 Markdown 摘要的 source-report 路径，避免已复核候选与复核证据脱钩；
- candidate `source_reports` 写入 JSON 或 Markdown 候选记录前必须先脱敏；原始 Windows 路径、POSIX home 路径、UNC 共享路径、API key、access token、cookie 与独立 secret token 都必须被替换；
- 候选记录必须包含 `source_reports_privacy.status=passed`；如果 privacy contract 失败，候选必须保持 blocked，直到重新生成 report 路径或修复脱敏器；
- 候选生成还必须校验报告字段契约；当必需顶层字段、audit-only 安全标志、决策关键嵌套字段或内嵌 `field_contract` 本身缺失、过期或类型错误时，必须以 `field_contract:<reason>` 阻断；
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
| profile candidate 记录 | 30 天摘要复核后 preview 可回滚 profile 变更 | 候选 ID、脱敏 source-report 引用、plugin diff、rollback path、validation plan | 原始绝对用户路径、UNC 共享路径、token、cookie、原始人工记录、原始 transcript |

留存规则：

- `.tmp/*.json` 默认只作为本地临时证据，不提交 Git；
- 需要长期留证时，只提交脱敏 Markdown 摘要；
- 任何报告进入 Git 前，必须确认不含 API key、access token、cookie、私有客户名、完整本地用户目录清单；
- 任何候选记录写入或渲染前，必须确认 `source_reports_privacy.status=passed`；若出现 `raw_private_path`、`raw_secret_assignment` 或 `raw_standalone_token`，按脚本缺陷处理；
- remote publication 不得把原始 audit JSON 当成附件上传；
- 如果发现已生成的报告含敏感内容，先删除该本地报告并重跑脱敏摘要，不在同一报告上手工涂改后继续使用。

### 5.13 脚本能力边界与增强触发条件

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
- `--close-audit with-candidate` 只能在同样证据门禁通过，并且已请求 candidate output 路径时，记录 `closed-with-candidate`。
- 如果这些门禁未满足，报告必须保持 `running` 或 `ready-for-summary`，并列出 closure blockers，例如 `audit_window_shorter_than_30_days`、`summary_not_marked_reviewed`、`source_report_paths_missing` 或 `candidate_output_missing`。

停止条件：

- 如果达到 `closed-no-change`，下一步只能按需重新开新一轮 audit 或保留 soft-load，不继续追加本轮结论；
- 如果达到 `closed-with-candidate`，后续工作必须转入 profile apply 候选变更，不再把审计计划本身当成执行面；
- 如果连续两次复核只增加解释性文本、没有新增可验证规则、字段、状态或测试要求，应停止继续扩写方案，改为提交当前完善结果；
- 审计状态变化必须记录在 30 天摘要或候选变更记录中，而不是只留在聊天上下文。

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
- apply 建议，但不自动 apply。
- `test/audit_codex_skills_usage.test.py` 必须覆盖 stdout 编码、warning 解析、warning-triage 标记与窄窗口阻断、warning-triage Markdown 输出、中文 announcement、repo profile fallback、`all_known_plugins` 展开、脱敏人工记录摄取、无效人工记录校验、人工记录来源路径隐私、报告字段契约校验、缺失/过期内嵌字段契约的候选门禁阻断、source-report 路径候选门禁阻断、source-report privacy 脱敏、审计 closure-state 门禁、preview-only 候选记录生成、30 天/summary-reviewed 候选门禁阻断、候选记录 rollback/validation 字段以及候选 Markdown 不执行清单。
- 回归测试还必须覆盖 explicit skill 误报 token 的路径/secret 脱敏、长度截断，以及 `noise_review` 字段契约阻断未脱敏或缺少隐私字段的报告。
- `tools/ci/ci_test_manifest.json` 必须纳入该回归测试，保证 local/remote CI 复用同一检查。

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
| `Skipped loading` 指向无效 SKILL.md | 单个 skill 元数据错误或 vendor cache 问题 | 优先记录来源；除非用户授权，不批量改 vendor cache |

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
- 校验决策关键的 `audit_state` 嵌套字段，包括状态、原因、下一步动作与 profile apply 许可标志；
- 校验决策关键的 `warning_triage` 嵌套字段，包括状态、blockers、窄窗口策略、warning 计数与后续动作建议；
- 明确漏跑、warning 延迟 triage、日志不可读、隐私脱敏和紧急例外的恢复规则；
- 明确 30 天最终决策摘要模板；
- 明确中证据、紧急例外和误报剔除的人工记录格式；
- 明确 30 天审计后进入 hard-load/profile apply 前的候选变更门禁与回滚路径；
- 要求候选生成必须绑定 JSON 报告路径与脱敏 Markdown 摘要路径；
- 要求 candidate `source_reports` 在写入候选 JSON 或 Markdown 前必须通过隐私契约；
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
- 明确回归测试和 CI manifest 要求；
- 明确远端发布仍受 GitLab/GitHub 授权门控制。
