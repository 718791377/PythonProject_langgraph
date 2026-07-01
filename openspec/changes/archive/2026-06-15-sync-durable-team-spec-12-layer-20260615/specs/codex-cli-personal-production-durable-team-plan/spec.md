## MODIFIED Requirements

### Requirement: Draft Plan Defines 10-To-12-Layer Bridge And Corpus Sync Evidence

The draft production durable-team implementation plan SHALL include a visible bridge that explains the relationship between the 10-layer runtime capability core and the current 12-layer product/business lifecycle target. The core durable-team corpus -- white paper, research note, MRD, North Star plan, implementation plan, playbook, lifecycle maps, and OpenSpec specs -- SHALL state the same count authorities and SHALL identify which evidence is tracked versus ignored local extraction cache. The plan SHALL also state that draft documentation and source-reading reports are not runtime implementation evidence for a running durable or persistent team.

#### Scenario: Cold-start maintainer reads the draft plan and related corpus

- **GIVEN** a maintainer opens `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md`
- **WHEN** they look for the white paper, research model, or durable-team corpus freshness
- **THEN** the plan shows a dedicated 10-to-12-layer landing-map section before the lane-specific responsibility section
- **AND** the section identifies the 12-layer lifecycle target as the current planning frame
- **AND** the related corpus states that raw extraction caches are ignored local evidence and may be absent from a fresh worktree
- **AND** the section states that this is draft documentation only, not runtime implementation evidence
