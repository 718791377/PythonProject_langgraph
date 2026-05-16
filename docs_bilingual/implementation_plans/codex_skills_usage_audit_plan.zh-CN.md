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
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 30 --json --output .\.tmp\skills-usage-audit-30d.json
```

### 5.5 Windows stdout 与回归测试

脚本必须在 Windows 非 UTF-8 控制台下仍能输出 `--json`。如果 stdout 无法编码 `⚠` 等字符，stdout 可以退化为 JSON 合法的反斜杠转义形式；但 `--output` 写入的报告文件仍必须保持 UTF-8 原文。

相关回归测试必须覆盖：

- `⚠ Exceeded skills context budget of 2%` 的 stdout fallback；
- 中文 `使用技能：` 与英文 `Using skill:` 的显式 skill announcement 识别；
- `logs_2.sqlite` 中 budget warning 的 `omitted_additional_skills` 与 `all_descriptions_removed` 提取；
- `full` profile 中 `plugins: "all_known_plugins"` 不能被拆成单个字符；
- 脚本在缺少用户级 plugin-modules profile 时，必须回退读取仓库内 `tools/skill_sources/plugin-modules/references/profiles.json`。

## 6. 决策规则

30 天后按以下规则决策：

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
- explicit skill 使用计数；
- SKILL.md 读取计数；
- profile helper 调用计数；
- 按 plugin/module 聚合的 evidence；
- apply 建议，但不自动 apply。
- `test/audit_codex_skills_usage.test.py` 必须覆盖 stdout 编码、warning 解析、中文 announcement、repo profile fallback 与 `all_known_plugins` 展开。
- `tools/ci/ci_test_manifest.json` 必须纳入该回归测试，保证 local/remote CI 复用同一检查。

## 8. 与 soft-load 的关系

如果会话中再次出现 `2% skills context budget` warning，不能说明 soft-load 失败。正确解释是：runtime 仍在为当前 turn 构造 model-visible skills surface，而 soft-load 不参与这个预算面。soft-load 只解决“当前任务需要的知识如何按需读取”，不解决“全局自动可见列表过大”。

## 9. 后续动作

审计结束前，只允许生成报告和 preview profile。审计结束后，如证据支持，再新开 bounded change 或使用已批准的 profile helper 执行 hard-load apply。远端发布仍按本仓库 local-main-first 与 GitLab/GitHub 授权规则执行。
