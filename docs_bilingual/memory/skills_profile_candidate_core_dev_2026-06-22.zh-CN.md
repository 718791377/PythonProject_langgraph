---
doc_id: skills_profile_candidate_core_dev_2026_06_22
lang: zh-CN
status: active
doc_class: audit_evidence
translation_of: docs_bilingual/memory/skills_profile_candidate_core_dev_2026-06-22.md
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-22
audit_run_type: profile_candidate_preview
---
# Skills profile candidate core-dev 2026-06-22

This zh-CN companion is ASCII-safe to avoid Windows transport mojibake in the current evidence package. It mirrors the English preview candidate.

## Candidate identity

- Candidate ID: `skills-profile-2026-06-22-core-dev`
- Approval state: `preview-only`
- target_profile: `core-dev`
- Mutates config: `False`
- Edits plugin cache: `False`
- Hard-load apply performed by candidate generation: `False`

## Review summary

The candidate keeps `core-dev` as the conservative daily default profile and keeps other profiles available as task profiles or later hard-load selections. This file is evidence only; the actual apply authorization is recorded in the approved-to-apply receipt.

## Rollback and validation

- Rollback command: `powershell -NoProfile -File tools/skill_sources/plugin-modules/scripts/set_plugin_profile.ps1 -RestoreLatest -Apply -Json`
- Restart required after apply: `True`
- Validate with final-review, decision-record, profile-routing, plugin-module, OpenSpec, local gate, and local MR checks.

## Non-actions

- Did not edit plugin cache.
- Did not edit vendor `SKILL.md` files.
- Did not mutate remote refs.
