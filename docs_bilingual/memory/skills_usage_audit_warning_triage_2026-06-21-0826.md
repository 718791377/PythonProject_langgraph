---
doc_id: skills_usage_audit_warning_triage_2026_06_21_0826
lang: en
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
generated_at: 2026-06-21
canonical: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-21-0826.md
translation_of: docs_bilingual/memory/skills_usage_audit_warning_triage_2026-06-21-0826.zh-CN.md
---
# Skills Usage Audit Warning Triage 2026-06-21 08:26 CST

This record preserves sanitized post-final warning-triage evidence after fresh live-session `2% skills context budget` warnings. Raw JSON, generated stdout, transcripts, runtime logs, warning excerpts, thread IDs, request IDs, response IDs, call IDs, token counters, and full runtime context remain local-only and are not committed.

## Triage window

- Since argument: `1d`
- Approximate command time: `2026-06-21 08:26 CST`
- Warning triage requested: `True`
- Window policy: `event_triggered_narrow_window`
- Window OK: `True`
- Blockers: `none`

## Warning signals

- Aggregate budget-warning count: `998`
- Aggregate skipped-loading count: `1881`
- Aggregate all-descriptions-removed count: `200`
- Maximum omitted additional skills: `16`
- `sessions_jsonl` budget/skipped/all-removed: `291` / `621` / `96`
- `logs_2.sqlite` budget/skipped/all-removed: `707` / `1260` / `104`
- Highest severity: `high`
- Recommended triage action: continue review-pending monitoring; do not edit plugin cache, hard-load profiles, or `config.toml` without explicit later authorization.

## Redaction enhancement evidence

This run follows a runtime redaction hardening pass for `tools/skills2cli.py audit warnings`:

- call IDs are replaced with `[REDACTED_ID]`;
- response IDs are replaced with `[REDACTED_ID]`;
- UUID-shaped runtime identifiers are replaced with `[REDACTED_ID]`;
- assignment-style runtime identifiers such as request, thread, session, submission, turn, and connection IDs are replaced with `[REDACTED_ID]`;
- token counter fields are replaced with `[REDACTED_TOKEN_COUNT]`;
- private paths and secrets continue to be replaced with `[REDACTED_PATH]` and `[REDACTED_SECRET]`.

Raw excerpts are intentionally not copied into this evidence record. The only long-term retained evidence is aggregate counts and the redaction contract above.

## Manual/source review conclusion

- New post-final warnings were found, so the monitoring item remains active.
- Skipped-loading pressure is source evidence only; it does not authorize vendor/plugin cache edits.
- The final 30-day summary remains `human_review_pending`.
- Candidate generation remains `not_requested`.
- Profile apply remains `not_authorized`.

## Non-actions

- Did not mark the final summary as `summary-reviewed`.
- Did not generate candidate JSON or candidate Markdown.
- Did not run profile apply.
- Did not edit Codex `config.toml`, plugin cache, hard-load profiles, user-level wrappers, or user-level runtime settings.
- Did not commit raw JSON, stdout, transcripts, runtime logs, warning excerpts, thread IDs, request IDs, response IDs, call IDs, or token counters.
- Did not mutate remote refs.
