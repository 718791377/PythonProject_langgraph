## ADDED Requirements

### Requirement: Comet-tracked Project MOE GUI plan refresh
The repository SHALL keep small Comet-requested documentation updates to the Project MOE Agent GUI toolchain plan traceable without changing runtime behavior.

#### Scenario: Documentation-only Comet tweak
- **WHEN** a user asks to update `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md` according to Comet and the change is limited to documentation wording
- **THEN** the repository records the tweak with OpenSpec/Comet artifacts and keeps runtime code, target-project files, user-level Codex assets, and remote refs unchanged unless separately authorized

#### Scenario: Comet shell helper unavailable
- **WHEN** Comet shell scripts cannot run because `bash` is unavailable in the current Windows shell
- **THEN** the session records the blocker and uses OpenSpec artifacts plus repository validation gates as the traceable fallback instead of claiming that script transitions succeeded

#### Scenario: Existing ownership claim
- **WHEN** ownership precheck finds an active claim for the target implementation-plan file
- **THEN** the session reuses or classifies the existing worktree before writing and MUST NOT create a duplicate write surface for the same path
