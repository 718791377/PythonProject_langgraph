---
doc_id: skills_usage_audit_skipped_loading_source_review_2026-05-25_1240
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-05-25
audit_run_type: skipped_loading_source_review
---

# Skills Usage Audit skipped-loading ?????2026-05-25 12:40?

??????? `Skipped loading` / skills-budget ?? warning ???????????????????????????????? vendor/plugin cache?

## ??

- warning triage status?`warning_found`
- skipped_loading_count?`25`
- recent_skipped_loading_samples?`20`
- skipped_loading_review?`record_source_and_do_not_edit_vendor_cache_without_authorization`
- budget_warning_count?`22`
- all_descriptions_removed_count?`21`
- max_omitted_additional_skills?`15`

## ????

- `session_loop{thread_id=019e09dd-74d4-7031-ac15-70e67206eb38}:submission_dispatch{otel.name="op.dispatch.user_input" submission.id="019e5d5f-9f7c-7390-8d8c-60cf399f2a1a" codex.op="user_input"}:turn{otel.name="session_task.turn" thread.id=019e09dd-74d4-7031-ac15-70e67206eb38 turn.id=019e5d5f-9f7c-7390-8d8c-60cf399f2a1a model=gpt-5.5 codex.turn.reasoning_effort=xhigh}:run_turn:run_sampling_request{turn_id=019e5d5f-9f7c-7390-8d8c-60cf399f2a1a model=gpt-5.5 cwd=[REDACTED_PATH] model=gpt-5.5}:stream_r[truncated]` - 脱敏 skipped-loading 样本 1
- `session_loop{thread_id=019e09dd-74d4-7031-ac15-70e67206eb38}:submission_dispatch{otel.name="op.dispatch.user_input" submission.id="019e5d5f-9f7c-7390-8d8c-60cf399f2a1a" codex.op="user_input"}:turn{otel.name="session_task.turn" thread.id=019e09dd-74d4-7031-ac15-70e67206eb38 turn.id=019e5d5f-9f7c-7390-8d8c-60cf399f2a1a model=gpt-5.5 codex.turn.reasoning_effort=xhigh}:run_turn:run_sampling_request{turn_id=019e5d5f-9f7c-7390-8d8c-60cf399f2a1a model=gpt-5.5 cwd=[REDACTED_PATH] model=gpt-5.5}:stream_r[truncated]` - 脱敏 skipped-loading 样本 2
- `session_loop{thread_id=019e09dd-74d4-7031-ac15-70e67206eb38}:submission_dispatch{otel.name="op.dispatch.user_input" submission.id="019e5d5f-9f7c-7390-8d8c-60cf399f2a1a" codex.op="user_input"}:turn{otel.name="session_task.turn" thread.id=019e09dd-74d4-7031-ac15-70e67206eb38 turn.id=019e5d5f-9f7c-7390-8d8c-60cf399f2a1a model=gpt-5.5 codex.turn.reasoning_effort=xhigh}:run_turn:run_sampling_request{turn_id=019e5d5f-9f7c-7390-8d8c-60cf399f2a1a model=gpt-5.5 cwd=[REDACTED_PATH] model=gpt-5.5}:receivin[truncated]` - 脱敏 skipped-loading 样本 3

## ????

1. ?? skipped-loading ? budget warning ??? Codex runtime ????????? `[REDACTED_PATH]` ???????
2. ????????????? `logs_2.sqlite`??? transcript ? plugin cache ???
3. ? vendor/plugin cache ?????????????????????????????
4. ??????? invalid `SKILL.md` ????????????????????????????
