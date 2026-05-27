## ADDED Requirements

### Requirement: Post-plan execution SHALL start with a docs_bilingual governance package
When a confirmed `/plan` exits into execution and the next task is not documentation-only, the repository SHALL create or update the local governance package before runtime or code implementation begins.

The package SHALL update `docs_bilingual/` first, using the most suitable document class and directory. Existing `docs_bilingual/` files SHALL be updated before creating a new file when they can cleanly carry the decision. The repository SHALL NOT treat `implementation_plans/` as the only valid `docs_bilingual/` destination.

OpenSpec artifacts and `docs/` artifacts SHALL be derived from the `docs_bilingual/` decision. The repository SHALL update `openspec/` only when durable capability, spec lifecycle, structural governance, or stable requirement evidence is needed. It SHALL update `docs/` only when Superpowers runtime artifacts or the `docs/` directory contract itself need changes.

#### Scenario: Non-documentation implementation follows `/plan`
- **WHEN** the user asks the session to implement a confirmed plan for a non-documentation-only task
- **THEN** the session SHALL first update the appropriate `docs_bilingual/` governance, guide, memory, product-lifecycle, or implementation-plan surface
- **AND** it SHALL complete the local governance package through local `main` integration before code or runtime implementation continues

#### Scenario: docs_bilingual update does not imply OpenSpec or docs files
- **WHEN** a `docs_bilingual/` update fully captures the local governance decision
- **THEN** the session SHALL NOT create `openspec/` or `docs/` artifacts only because `docs_bilingual/` changed
- **AND** any additional `openspec/` or `docs/` file SHALL be justified by the task content itself

### Requirement: Post-plan governance flow SHALL be enforced by local range checks
The repository SHALL keep a script-backed range check for post-`/plan` non-document execution. The check SHALL require the first commit in a non-document execution range to be a docs-only local governance package that touches `docs_bilingual/` first.

Local MR review SHALL run that range check before local `main` integration. The aggregate OpenSpec guard SHALL run a static local-flow checker that verifies the range checker, complete local-flow helper, policy documents, and CI test registrations remain wired.

#### Scenario: Non-document execution branch skips the governance package
- **WHEN** a feature branch contains non-document changes and the first commit does not update `docs_bilingual/`
- **THEN** `tools/check_plan_exit_execution_governance.py` SHALL fail for that range
- **AND** `tools/ci/local_mr_review.ps1` SHALL block local integration
