## ADDED Requirements

### Requirement: Governance plan SHALL preserve complete Comet phase evidence

The user-level MCP, skills, browser automation, and CLI harness governance implementation plan SHALL describe the complete Comet `Open -> Design -> Build -> Verify -> Archive` workflow when the operator explicitly requests a complete `/comet` refactor.

The plan SHALL NOT describe the current governance-plan execution model as tweak-only when the active change is full workflow.

#### Scenario: Complete Comet framing is required

- **WHEN** the Chinese governance implementation plan is reviewed after the full Comet refactor
- **THEN** its frontmatter SHALL identify `comet_workflow: full`
- **AND** its phase model SHALL include `open-design-build-verify-archive`
- **AND** its body SHALL include explicit Open, Design, Build, Verify, and Archive gates

#### Scenario: Runtime implementation remains out of scope

- **WHEN** the full Comet refactor is applied to the document
- **THEN** it SHALL preserve the existing rule that actual user-level installs, live browser automation, and WXWork GUI automation require separate governed evidence
- **AND** it SHALL NOT mark unfinished lanes as `active`
