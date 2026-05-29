## ADDED Requirements

### Requirement: Comet-tracked automatic routing plan refactor

The repository SHALL keep Comet-requested refactors of the automatic orchestration routing enforcement plan traceable without implying runtime enforcement has changed.

#### Scenario: Documentation-only Comet tweak

- **WHEN** a user asks to refactor `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md` according to Comet and the change is limited to documentation structure
- **THEN** the repository records the tweak with OpenSpec/Comet artifacts
- **AND** the document states that the refactor is not runtime evidence that experts, durable teams, or persistent teams ran
- **AND** runtime code, generated user-level assets, local `main`, and remote refs remain unchanged unless separately authorized

#### Scenario: Phase status is preserved

- **WHEN** the refactor updates the plan structure
- **THEN** Phase 0-3 completion status remains separate from Phase 4 planned follow-up status
- **AND** future Phase 4 implementation work remains represented as a future bounded change, not as completed by this tweak

#### Scenario: Comet shell helper unavailable

- **WHEN** Comet shell scripts cannot run because `bash` is unavailable in the current Windows shell
- **THEN** the session records the blocker and uses OpenSpec artifacts plus repository validation gates as the traceable fallback instead of claiming script transitions succeeded
