---
doc_id: skills_usage_audit_warning_manual_review_2026-05-22
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
source_report: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-05-22.zh-CN.md
generated_at: 2026-05-22
audit_run_type: warning_triage_manual_review
audit_window_days: 1
followup_run: true
---

# Skills Usage Audit warning triage 人工复核（2026-05-22）

## 复核范围

- 来源报告：`docs_bilingual/memory/skills_usage_audit_warning_triage_2026-05-22.zh-CN.md`。
- 原始 JSON：`.tmp/skills-usage-audit-warning-triage-2026-05-22-followup.json`，本地临时保留，不进入 Git。
- 原始 stdout：`.tmp/skills-usage-audit-warning-triage-2026-05-22-followup.stdout.txt`，本地临时保留，不进入 Git。
- 临时 summary：`.tmp/skills-usage-audit-warning-triage-2026-05-22-followup-summary.md`，本地临时保留，不进入 Git。
- 本轮复核只确认 warning 来源、严重度、脱敏与 audit-only 边界，不执行 profile apply。

## 关键字段复核

- `audit_state.state`: `running`
- `audit_state.reason`: `audit_window_shorter_than_30_days`
- `profile_apply_allowed`: `False`
- `field_contract.status`: `passed`
- `output_retention.status`: `passed`
- `precommit_update_archive.status`: `passed`
- `warning_triage.status`: `warning_found`
- `warning_triage.window_ok`: `True`
- `warning_triage.budget_warning_count`: `36`
- `warning_triage.skipped_loading_count`: `36`
- `warning_severity.level`: `high`
- `max_omitted_additional_skills`: `15`

## 人工判断

1. 本轮告警不是“启动时 soft-load 是否生效”的直接否定证据；它说明会话中 runtime 重新注入或重打包 skills surface 时仍可能触发 2% budget 限制。
2. `warning_found` 与 `high` 严重度成立，但仍处于 30 天观察期，不能把单日或短期告警直接解释为“core-dev 以外 skills 都无用”。
3. skipped-loading 样本应按 runtime 预算裁剪事件处理，不应在没有明确 vendor 文件格式错误证据时手改 plugin cache。
4. 当前正确动作是继续 audit-only：记录周报、窄窗口 warning triage、人工复核和后续 30 天汇总；profile apply 必须等 summary-reviewed 与 preview-only candidate 完成后再由用户授权。

## 脱敏与留存复核

- 本长期证据不保留 raw JSON、stdout、session transcript 或本地绝对路径。
- `.tmp/` 输出仅用于本地调试与即时复核，不进入 Git。
- 未记录 secret、cookie、access token、API key。
- 未修改 `config.toml`、plugin cache、vendor `SKILL.md` 或 hard-load profile。

## 后续动作

- 继续按真实日历完成 30 天 usage audit 观察期。
- 会话中再次出现 budget warning 时继续运行 1 天或 `--since` 窄窗口 warning triage。
- 30 天期满后生成最终 JSON 与脱敏 Markdown summary，完成 summary-reviewed 后再决定是否生成 preview-only profile candidate。