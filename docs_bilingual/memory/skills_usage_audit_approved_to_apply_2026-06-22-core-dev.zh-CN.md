---
doc_id: skills_usage_audit_approved_to_apply_2026_06_22_core_dev
lang: zh-CN
status: active
doc_class: audit_evidence
source_plan: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
generated_at: 2026-06-22
audit_run_type: approved_to_apply_receipt
canonical: docs_bilingual/memory/skills_usage_audit_approved_to_apply_2026-06-22-core-dev.zh-CN.md
translation_of: docs_bilingual/memory/skills_usage_audit_approved_to_apply_2026-06-22-core-dev.md
---
# Skills Usage Audit approved-to-apply receipt 2026-06-22 core-dev

This zh-CN companion is ASCII-safe to avoid Windows transport mojibake in current evidence files. It mirrors the English canonical receipt.

## Authorization

- Authorization source: `current user message authorizing final human review, closure decision, and profile apply`
- Authorization time: `2026-06-22T10:51:00+00:00`
- Target profile: `core-dev`
- Apply command: `powershell -NoProfile -File tools/skill_sources/plugin-modules/scripts/set_plugin_profile.ps1 core-dev -Apply -Json`
- Preview command: `powershell -NoProfile -File tools/skill_sources/plugin-modules/scripts/set_plugin_profile.ps1 core-dev -Json`
- Rollback command: `powershell -NoProfile -File tools/skill_sources/plugin-modules/scripts/set_plugin_profile.ps1 -RestoreLatest -Apply -Json`

## Safety boundary

- Config mutation scope: `user-level Codex config plugin enabled keys only`
- Plugin cache edited: `False`
- Vendor SKILL.md edited: `False`
- Direct MCP entries edited: `False`
- Remote refs mutated: `False`
- Restart required: `True`

## Pre-apply review

- Candidate reviewed: `docs_bilingual/memory/skills_profile_candidate_core_dev_2026-06-22.md`
- Decision record: `docs_bilingual/memory/skills_usage_audit_human_review_decision_2026-06-21.md`
- Rationale: `reduce full profile warning pressure while preserving daily development, security, OpenAI, browser verification, and document capability`

## Apply result

- Apply performed: `True`
- Helper changed config: `True`
- Backup path: `[CODEX_HOME]/backups/plugin-modules-profile/20260622T105221903Z-config.toml`
- only_plugin_enabled_keys_changed: `True`
- plugin_cache_edited: `False`
- direct_mcp_entries_edited: `False`

## Apply result recorded after helper execution

- Apply performed: `True`
- Helper changed config: `True`
- Backup path: `[CODEX_HOME]/backups/plugin-modules-profile/20260622T105221903Z-config.toml`
- only_plugin_enabled_keys_changed: `True`
- plugin_cache_edited: `False`
- direct_mcp_entries_edited: `False`
- Post-apply preview changed: `False`
- Restart required: `True`
- Rollback command: `powershell -NoProfile -File tools/skill_sources/plugin-modules/scripts/set_plugin_profile.ps1 -RestoreLatest -Apply -Json`
- Apply evidence privacy: `raw helper paths redacted to CODEX_HOME placeholder; full stdout remains local-only`
