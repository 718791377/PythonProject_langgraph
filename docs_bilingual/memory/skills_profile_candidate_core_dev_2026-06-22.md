# Codex Skills Profile Apply Candidate

## Candidate identity

- Candidate ID: `skills-profile-2026-06-22-core-dev`
- Approval state: `preview-only`
- Generated at: `2026-06-22T10:46:28.875294+00:00`
- Record type: `codex_skills_profile_apply_candidate`

## Safety

- Mutates config: `False`
- Edits plugin cache: `False`
- Hard-load apply performed: `False`
- Explicit authorization required for apply: `True`
- Generic continue is not apply authorization: `True`
- Candidate record contract: `passed`
- Candidate record passed: `True`
- Candidate record blockers: `0`
- Candidate record required fields: `20`
- Candidate record missing fields: `0`
- Candidate record invalid-type fields: `0`
- Candidate record preview-safety violations: `0`
- Candidate record source-report-privacy violations: `0`
- Candidate record gate-shape violations: `0`
- Candidate record rollback-path violations: `0`
- Candidate record validation-plan violations: `0`
- Candidate record sanitization violations: `0`
- Candidate record approval policy: `candidate_outputs_from_this_script_must_remain_preview_only_until_a_separate_explicit_apply_change`
- Candidate record blocker details: `none`

## Source reports

- JSON report: `.tmp/skills-audit-candidate/skills-usage-audit-core-dev-preview-20260622.json`
- Markdown summary: `docs_bilingual/memory/skills_usage_audit_summary_reviewed_core_dev_2026-06-22.md`
- Manual notes: `0`
- Privacy contract: `passed`
- Privacy violations: `none`

## Candidate generation gate

- Gate status: `allowed`
- Gate allowed: `True`
- Blockers: `none`
- Summary reviewed: `True`
- Audit window at least 30 days: `True`
- Field contract: `passed`

## Current and target profile

- Current inferred profile: `custom_or_unmatched`
- Current enabled plugins: `40`
- Current manual review required: `True`
- Target profile: `core-dev`
- Target profile provided: `True`
- Target profile found in registry: `True`
- Target plugins: `10`

## Plugin diff

- Add to default: `none`
- Remove from default: `BioRender, CB Insights, Canva, Cloudflare, Cloudinary, Dow Jones Factiva, Expo, Figma, Fireflies, Gmail, Google Calendar, Google Drive, HubSpot, Hugging Face, HyperFrames by HeyGen, Notion, PitchBook, Readwise, Remotion, Sentry, Slack, Stripe, Supabase, Twilio Developer Kit, Vercel, Zotero`
- Keep enabled: `Browser, ChatGPT Apps, CodeRabbit, Codex Security, Documents, GitHub, OpenAI Developers, Presentations, Spreadsheets, Temporal`
- Unknown current enabled entries requiring review: `4`

## Evidence basis

- Strong total: `1156`
- Strong helper calls: `233`
- Strong skill path reads: `923`
- Medium evidence rationale: `mapped_tool_calls_present_manual_review_required`
- Weak plugin mentions: `58669`
- Recommendation: `candidate_for_project_or_default_profile_review`
- Warning severity: `high`

## Risk review and rollback

- Risk level: `manual_review_required`
- Possibly disabled capabilities: `BioRender, CB Insights, Canva, Cloudflare, Cloudinary, Dow Jones Factiva, Expo, Figma, Fireflies, Gmail, Google Calendar, Google Drive, HubSpot, Hugging Face, HyperFrames by HeyGen, Notion, PitchBook, Readwise, Remotion, Sentry, Slack, Stripe, Supabase, Twilio Developer Kit, Vercel, Zotero`
- Restore command: `set_plugin_profile.ps1 -RestoreLatest -Apply`
- Restart required: `True`

## Validation plan

- `preview_candidate_record`: review_candidate_json_and_sanitized_30_day_summary
- `local_checks`: python .\test\audit_codex_skills_usage.test.py && powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1
- `startup_validation`: restart_with_codex-ohmy_after_explicit_apply_authorization_only
- `warning_retest`: python .\tools\audit_codex_skills_usage.py --root . --days 1 --json --output .\.tmp\skills-usage-warning-retest.json

## Non-action list

- Did not modify user-level `config.toml`.
- Did not edit plugin/vendor cache.
- Did not perform hard-load/profile apply.
- Did not infer approval from generic continue/confirmation.
