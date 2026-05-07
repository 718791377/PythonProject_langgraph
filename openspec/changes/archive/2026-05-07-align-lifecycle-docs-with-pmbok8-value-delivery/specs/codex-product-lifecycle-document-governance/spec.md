## MODIFIED Requirements

### Requirement: PMI References Are A Governance Overlay

The repository SHALL treat PMI project-management references as a governance overlay for delivery, tailoring, quality, risk, change control, closing, and value delivery rather than as a replacement for the product and business lifecycle.

The repository SHALL treat PMBOK 8th Edition as the primary overlay for value-delivery framing, project-canvas alignment, performance-domain thinking, AI-era project governance, hybrid delivery, and tailoring.

The repository SHALL treat PMBOK 6th Edition and Process Groups references as operational supplements for initiating, planning, executing, monitoring and controlling, closing, and input/tool/output discipline.

The repository SHALL treat PMBOK 7th Edition as a principles, performance-domain, value-delivery, and tailoring bridge.

The repository SHALL treat Agile references as adaptive and hybrid delivery supplements for uncertainty, MVP slices, feedback loops, and small reversible releases.

#### Scenario: A maintainer adds PMI guidance to lifecycle docs

- **GIVEN** the maintainer uses `PMP/` as a local private reference directory
- **WHEN** the maintainer updates repository lifecycle documentation
- **THEN** the update summarizes repository-specific mappings only
- **AND** the update states which reference is primary and which references are supplemental for that mapping
- **AND** the update does not reproduce PMI book content
- **AND** the local `PMP/` reference directory remains ignored by Git

### Requirement: Product Lifecycle Reference Defines The 0-8 Document Stack

The repository SHALL maintain a bilingual product lifecycle reference that defines the cognitive narrative, business, market, strategy, product, technical, execution, growth, and retrospective layers.

The lifecycle reference SHALL state that document completion is not the goal by itself; the document stack exists to support value identification, value alignment, value delivery, value verification, and learning.

The lifecycle reference SHALL define a lightweight project canvas or initiative canvas as an optional alignment artifact before the full stack is expanded.

#### Scenario: A maintainer asks how a white paper differs from a North Star plan

- **GIVEN** the maintainer reads the product lifecycle reference
- **WHEN** the maintainer compares document types
- **THEN** the reference explains that a white paper changes cognition and frames why the direction exists
- **AND** the reference explains that a North Star plan turns strategy into measurable direction, metrics, levers, and staged execution
- **AND** the reference explains that a project canvas can align purpose, value, stakeholders, boundaries, risks, delivery style, and outcome checks before heavier documents are expanded

## ADDED Requirements

### Requirement: Platform And Downstream Lifecycles Shall Track Value Outcomes

The platform-build lifecycle and downstream-consumption lifecycle SHALL define value outcomes in addition to delivery artifacts.

Platform-build value outcomes SHALL include operator friction reduction, cold-start continuation success, cross-session coordination quality, repo-local state safety, native Codex compatibility, and rollback evidence.

Downstream-consumption value outcomes SHALL include whether platform adoption reduces startup friction, reduces context loss, improves delivery coordination, preserves repo-local truth, and provides actionable upstream feedback.

#### Scenario: A lifecycle document describes a delivered platform or downstream slice

- **GIVEN** a lifecycle document describes an implementation or adoption slice
- **WHEN** the reader checks whether the slice succeeded
- **THEN** the document identifies the delivered artifact
- **AND** the document identifies the value outcome or adoption outcome that the artifact is meant to improve
- **AND** the document identifies feedback or retrospective evidence that can update the next slice

### Requirement: Durable-Team Plans Shall Use Value Increment Release Slices

The long-term durable-team implementation plan SHALL keep its draft status until individual release slices are promoted through OpenSpec.

Each release slice SHALL state the target repository, phase, task scope, value increment, feedback point, validation path, rollback boundary, and operator consent boundary before it is treated as release-ready.

A release slice SHALL NOT claim that the full personal production durable-team target is implemented unless the production acceptance and rollback evidence are complete.

#### Scenario: A maintainer plans a future durable-team release slice

- **GIVEN** the long-term durable-team implementation plan remains a draft
- **WHEN** the maintainer defines a release slice
- **THEN** the slice includes a value increment and feedback point, not only a task list
- **AND** the slice includes validation and rollback boundaries
- **AND** the slice can be reviewed through one OpenSpec change and one GitLab MR unless the user explicitly approves a broader batch
