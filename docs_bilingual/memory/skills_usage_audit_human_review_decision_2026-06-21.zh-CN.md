---
doc_id: skills_usage_audit_human_review_decision_2026_06_21
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-21
last_reviewed: 2026-06-22
audit_run_type: human_review_decision_record
canonical: docs_bilingual/memory/skills_usage_audit_human_review_decision_2026-06-21.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_human_review_decision_2026-06-21.md
---
# Skills Usage Audit human review decision 2026-06-21 / updated 2026-06-22

This zh-CN companion is ASCII-safe to avoid Windows transport mojibake in current evidence files. It mirrors the English canonical decision record.

## Decision fields

- Outcome: `summary-reviewed + preview-only candidate`
- Summary review state: `summary-reviewed`
- Candidate generation state: `preview-only`
- Profile apply state: `approved-to-apply`
- target_profile: `core-dev`
- Candidate review notes: `core-dev is accepted as conservative daily default; full is too warning-heavy and other profiles remain on-demand.`
- Rollback path review notes: `set_plugin_profile.ps1 -RestoreLatest -Apply is the primary rollback path after the helper backup.`
- Validation plan review notes: `Run final-review, decision-record, profile-routing, plugin-module, OpenSpec, local gate, and local MR checks.`
- approved-to-apply receipt: `docs_bilingual/memory/skills_usage_audit_approved_to_apply_2026-06-22-core-dev.md`

## Evidence basis

- Final 30-day summary: `docs_bilingual/memory/skills_usage_audit_30d_summary_2026-06-15-1059.md`
- Reviewed summary candidate evidence: `docs_bilingual/memory/skills_usage_audit_summary_reviewed_core_dev_2026-06-22.md`
- Preview candidate JSON: `docs_bilingual/memory/skills_profile_candidate_core_dev_2026-06-22.json`
- Preview candidate Markdown: `docs_bilingual/memory/skills_profile_candidate_core_dev_2026-06-22.md`
- Human decision-record checker: `tools/check_skills_audit_human_review_decision_record.py`

## Review result

The final 30-day summary is reviewed for this closeout. `core-dev` is selected as the daily default candidate because `full` has high warning pressure and the daily task pattern is repository development, governance, CI, security, OpenAI, browser verification, and document work. `web-saas` has higher broad evidence but remains task-scoped rather than the daily default. Other profiles remain available as task profiles or later hard-load selections.

## Gate status

- Candidate output is preview-only and does not mutate config.
- Profile apply is authorized by the operator in the current session and recorded in the approved-to-apply receipt.
- Plugin cache and vendor `SKILL.md` files are not edited.
- Raw session content, raw runtime log content, warning details, private paths, secrets, and token counters are not retained in this record.

## Next action

Apply `core-dev` through the guarded profile helper, save backup and rollback evidence, restart Codex later through `codex-ohmy`, and continue warning monitoring after restart.

## Non-actions

- Did not delete capabilities or plugin cache.
- Did not edit vendor `SKILL.md` files.
- Did not mutate remote refs.
