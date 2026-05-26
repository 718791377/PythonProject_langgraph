---
doc_id: skills_usage_audit_skipped_loading_source_review_2026-05-27_0721
lang: en
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
generated_at: 2026-05-27
audit_run_type: skipped_loading_source_review
translation_of: docs_bilingual/memory/skills_usage_audit_skipped_loading_source_review_2026-05-27_0721.zh-CN.md
---

# Skills Usage Audit Skipped-Loading Source Review (2026-05-27 07:21)

This record preserves a sanitized review of `Skipped loading` and skills-budget warning sources. It records source type and next action only; it does not retain raw runtime logs, full transcripts, or vendor/plugin cache content.

## Counts

- Warning triage status: `warning_found`
- Skipped-loading count: `25`
- Recent skipped-loading samples: `20`
- Skipped-loading review: `record_source_and_do_not_edit_vendor_cache_without_authorization`
- Budget warning count: `21`
- All-descriptions-removed count: `21`
- Maximum omitted additional skills: `15`

## Sanitized samples

- `session_loop{thread_id=019e09dd-74d4-7031-ac15-70e67206eb38}:submission_dispatch{otel.name="op.dispatch.user_input" submission.id="019e6694-694c-76d2-8099-856a024bcde0" codex.op="user_input"}:turn{otel.name="session_task.turn" thread.id=019e09dd-74d4-7031-ac15-70e67206eb38 turn.id=019e6694-694c-76d2-8099-856a024bcde0 model=gpt-5.5 codex.turn.reasoning_effort=xhigh}:run_turn:run_sampling_request{turn_id=019e6694-694c-76d2-8099-856a024bcde0 model=gpt-5.5 cwd=[REDACTED_PATH] model=gpt-5.5}:stream_r[truncated]` - skipped-loading sample 1
- `session_loop{thread_id=019e09dd-74d4-7031-ac15-70e67206eb38}:submission_dispatch{otel.name="op.dispatch.user_input" submission.id="019e6694-694c-76d2-8099-856a024bcde0" codex.op="user_input"}:turn{otel.name="session_task.turn" thread.id=019e09dd-74d4-7031-ac15-70e67206eb38 turn.id=019e6694-694c-76d2-8099-856a024bcde0 model=gpt-5.5 codex.turn.reasoning_effort=xhigh}:run_turn:run_sampling_request{turn_id=019e6694-694c-76d2-8099-856a024bcde0 model=gpt-5.5 cwd=[REDACTED_PATH] model=gpt-5.5}:receivin[truncated]` - skipped-loading sample 2
- `session_loop{thread_id=019e09dd-74d4-7031-ac15-70e67206eb38}:submission_dispatch{otel.name="op.dispatch.user_input" submission.id="019e6694-694c-76d2-8099-856a024bcde0" codex.op="user_input"}:turn{otel.name="session_task.turn" thread.id=019e09dd-74d4-7031-ac15-70e67206eb38 turn.id=019e6694-694c-76d2-8099-856a024bcde0 model=gpt-5.5 codex.turn.reasoning_effort=xhigh}:run_turn:run_sampling_request{turn_id=019e6694-694c-76d2-8099-856a024bcde0 model=gpt-5.5 cwd=[REDACTED_PATH] model=gpt-5.5}:receivin[truncated]` - skipped-loading sample 3

## Review conclusion

1. The skipped-loading signals and budget warnings came from Codex runtime logging and have local paths redacted as `[REDACTED_PATH]`.
2. This record does not store raw `logs_2.sqlite`, transcripts, or plugin-cache contents.
3. Do not edit vendor/plugin cache as a response to this warning without explicit authorization.
4. If future invalid `SKILL.md` messages recur, record the source first and fix only through an approved cache or plugin-update path.
