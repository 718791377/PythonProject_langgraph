# Design: Durable-Team Corpus And 10-To-12 Spec Synchronization

## Change

`sync-durable-team-spec-12-layer-20260615`

## Context

The current docs already separate the strategic white paper from the evidence-heavy research note, and they already explain that the 10-layer runtime model is a capability core while the 12-layer lifecycle is the repository's product/business planning frame. The remaining gap is synchronization evidence: the stable durable-team spec, its Chinese companion, and the core document family need an explicit checkpoint that says what is current, what evidence is tracked, and what is not runtime proof.

## Decisions

1. Keep the white paper and research note separate. This change only adds cross-document sync evidence; it does not collapse their lifecycle roles.
2. Treat the stable OpenSpec requirement as the acceptance authority for the implementation plan's bridge behavior.
3. Record the ignored extraction-cache limitation explicitly. Tracked documents may cite the June 2026 extraction run through reports and archive evidence, but they must not imply that the raw ignored cache is present in every worktree.
4. Keep this docs-only. No runtime, launcher, model, or remote publication behavior changes.

## File Scope

- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.*` - core draft implementation plan and 10-to-12 bridge authority.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_playbook.*` - release-slice operating playbook for the draft target.
- `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.*` - strategic white paper for the durable-team corpus.
- `docs_bilingual/market_requirements/codex_cli_personal_production_durable_team_mrd.*` - market requirements document for target users and tailoring.
- `docs_bilingual/governance/solo_maintainable_production_persistent_team_research.*` - evidence-heavy research note and merge-boundary record.
- `docs_bilingual/north_star_plan.*` - metrics and decision-threshold north-star plan.
- `openspec/specs/codex-cli-personal-production-durable-team-plan/spec.*` - stable OpenSpec acceptance authority.
- `openspec/changes/sync-durable-team-spec-12-layer-20260615/...` - active delta-spec and workflow evidence package.
- `docs/superpowers/specs/2026-06-15-durable-team-corpus-sync-design.*` - HOW-layer design artifact for this sync slice.
- `docs/superpowers/plans/2026-06-15-sync-durable-team-spec-12-layer.*` - HOW-layer execution plan for this sync slice.

## Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Over-claiming fresh extraction evidence | State that raw extraction artifacts are ignored and may be absent; cite tracked report/archive evidence only. |
| Re-opening the whitepaper/research merge question | Preserve separate roles and point to the existing merge policy. |
| Treating draft docs as runtime evidence | Repeat the no-runtime-evidence boundary in the spec and checkpoints. |
| Chinese mojibake during edits | Write files with explicit UTF-8 and run mojibake checks after edits. |

## Acceptance Evidence

- OpenSpec strict validation for this change.
- Stable and delta spec mention the 10-to-12 bridge and no-runtime-evidence boundary.
- Core durable-team document family contains the 2026-06-15 corpus sync checkpoint.
- UTF-8/mojibake checks pass for touched files.
