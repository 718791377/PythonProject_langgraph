---
doc_id: skills_usage_audit_summary_reviewed_core_dev_2026_06_22
lang: zh-CN
status: active
doc_class: audit_evidence
translation_of: docs_bilingual/memory/skills_usage_audit_summary_reviewed_core_dev_2026-06-22.md
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-22
audit_run_type: summary_reviewed_profile_candidate_evidence
---
# Skills usage audit summary-reviewed core-dev evidence 2026-06-22

This zh-CN companion is ASCII-safe to avoid Windows transport mojibake in the current evidence package. It mirrors the English reviewed summary evidence.

## Audit state

- Audit state: `closed-with-candidate`
- Summary review state: `summary-reviewed`
- Candidate generation state: `preview-only`
- Profile apply allowed by summary: `False`
- target_profile: `core-dev`

## Review result

The reviewed evidence supports `core-dev` as the conservative daily default profile because `full` has high warning pressure while `core-dev` keeps daily repository development, governance, CI, security, OpenAI, browser verification, and document capability. Other profiles remain available as task profiles, soft-load modules, or later hard-load selections.

## Boundaries

- This summary evidence does not mutate config.
- Candidate generation is preview-only.
- Profile apply is recorded separately through the approved-to-apply receipt.
- Plugin cache and vendor `SKILL.md` files are not edited.
- Raw session transcripts, raw runtime logs, private paths, secrets, and token counters are not retained.

## Validation

- Field contract: `passed`
- Output retention: `passed`
- Pre-commit update/archive gate: `passed`
- Final review state: `summary-reviewed`
- Human review decision record: `summary_reviewed_preview_only_candidate`
