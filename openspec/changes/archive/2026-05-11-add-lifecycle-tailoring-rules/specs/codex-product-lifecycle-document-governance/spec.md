# codex-product-lifecycle-document-governance Delta

## ADDED Requirements

### Requirement: Lifecycle Tailoring Rules Define Full And Lightweight Architecture Use

The repository SHALL define explicit lifecycle tailoring rules for when to use the full 12-layer target architecture and when to use a lightweight architecture. The rules SHALL distinguish whole-project lightweight tailoring, phase-local lightweight tailoring, module-level lightweight tailoring, and escalation back to fuller governance.

#### Scenario: A maintainer chooses governance depth for a lifecycle-guided change

- **GIVEN** the maintainer reads the product lifecycle tailoring guidance
- **WHEN** the work affects money, users, trust, compliance, security, data, runtime entrypoints, release safety, cross-project templates, durable state, shared interfaces, or long-lived platform behavior
- **THEN** the guidance requires a full architecture path for the affected scope
- **AND** the guidance may still allow unaffected low-risk phases or modules to stay lightweight when their boundaries and rollback evidence are explicit

#### Scenario: A maintainer uses a lightweight path safely

- **GIVEN** the requested work is a small local note, low-risk internal tool, one-off spike, reversible documentation experiment, or early idea without external users, money, trust boundary, compliance impact, or durable-state change
- **WHEN** the maintainer selects a lightweight path
- **THEN** the guidance states whether the whole project, a local phase, or a module is lightweight
- **AND** it records Inputs, Tools and Techniques, and Outputs for the tailoring decision
- **AND** it defines escalation triggers if risk, uncertainty, coupling, adoption, release impact, or stakeholder impact grows
