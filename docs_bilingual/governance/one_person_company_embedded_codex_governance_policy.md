---
doc_id: one_person_company_embedded_codex_governance_policy
doc_class: governance
status: active
canonical_path: docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.md
zh_cn_path: docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.zh-CN.md
---
# One-Person Company Embedded Codex Governance Policy

## Purpose

This policy defines how the Codex CLI personal production durable team is embedded inside a personal production one-person-company operating system. The Codex team is an embedded platform-governance capability, not a peer authority that competes with company business truth.

## Related Documents

- `docs_bilingual/whitepapers/personal_production_one_person_company_operations_whitepaper.md` - downstream business-operating white paper that consumes the embedded Codex governance boundary.
- `docs_bilingual/north_star/personal_production_one_person_company_operations_north_star.md` - business North Star that counts mixed loops only after both gates pass.
- `docs_bilingual/implementation_plans/embedded_codex_governance_in_one_person_company_plan.md` - implementation plan that records the canonical naming and embedded-governance closeout.
- `docs_bilingual/docs_registry.yaml` - registry authority for this policy and the generated operations-package body documents.
- `docs_bilingual/operations_packages/codex_cli_durable_team/` and `docs_bilingual/operations_packages/one_person_company/` - separated package directories that may share canonical filenames while preserving truth ownership.

## Governance Relationship

```text
one-person-company operating system
|- business governance: customers, revenue, pricing, contracts, support, delivery, cashflow
|- embedded Codex governance: agents, OpenSpec, worktrees, durable state, validation gates, release gates
`- shared governance ledgers: risk, decisions, metrics, evidence, review, permissions, human review
```

Core rules:

- The one-person company owns business truth: customer evidence, revenue, contracts, support, legal posture, and cashflow are not decided by Codex platform documents.
- The Codex durable team owns execution truth: expert routing, agent permissions, tool calls, code changes, worktrees, local `main`, repo-local durable state, validation gates, and release boundaries are governed by Codex execution policy.
- Mixed matters require two gates: any change that affects both customers, revenue, compliance, or commitments and code, agents, runtime, or release state must pass the business gate and the Codex execution gate.
- AI agents do not own final commitment rights: pricing, contracts, releases, customer promises, finance promises, refunds, and legal commitments require human confirmation.

## Shared Ledger Contract

The following ledgers may be shared at project level if every record carries the scope fields below:

```yaml
scope: business | codex | mixed
truth_owner: founder | codex-operator | human-review
evidence_source: customer | revenue | repo | runtime | agent | legal
decision_right: human | delegated-draft-only
linked_docs: []
```

Recommended shared ledgers:

| Ledger | Shared use |
| --- | --- |
| `decision-log.md` | One decision log with `business`, `codex`, or `mixed` scope. |
| `risk-register.md` | One risk register with business, platform, and mixed risk classes. |
| `learning-log.md` | One learning log separating customer, operations, and platform learning. |
| `experiment-log.md` | One experiment log separating market, product, and agent or automation experiments. |
| `data-dictionary.md` | One dictionary with business data, telemetry, and agent-state sections. |
| `tracking-plan.md` | One tracking plan with business events and platform execution events. |
| `backup-restore.md` | One recovery manual with business data, repository, and durable-state sections. |
| `agent-role-map.md` | One role map separating business agents and Codex execution agents. |
| `agent-permissions.md` | One permission matrix split by tool, data, and approval right. |
| `human-review-checklist.md` | One human-review checklist covering business commitments and Codex execution gates. |
| `monthly-review.md` | One monthly review for business-loop quality and platform-execution quality. |

## Same Name, Separate Truth

Some documents may use the same canonical filename in both package directories. The filename expresses shared semantics; the content remains package-specific truth.

| Canonical filename | One-person-company truth | Codex durable-team truth |
| --- | --- | --- |
| `vision.md` | Company vision. | Platform capability vision. |
| `strategy.md` | Market and revenue strategy. | Platform evolution strategy. |
| `business-model.md` | Customer and revenue model. | Productivity and cost model. |
| `pricing.md` | Customer pricing. | Platform cost or packaging assumptions. |
| `unit-economics.md` | Customer economics. | Automation and execution economics. |
| `user-segments.md` | Customers and buyers. | Developers and project types. |
| `market-map.md` | Business market. | Tool and platform alternatives. |
| `north-star.md` | Business-loop throughput. | Orchestration and delivery reliability. |
| `metrics.md` | Business metrics. | Execution and governance metrics. |
| `prd.md` | Customer product PRD. | Platform capability PRD. |
| `tech-stack.md` | Business runtime dependencies. | Codex tooling dependencies. |
| `privacy-policy.md` | Customer privacy commitment. | Tool, log, and state-data handling. |

## Separate Files With Unified Semantics

These files must not be merged into one fact file, but they must use compatible vocabulary and linked evidence:

| Codex document | One-person-company document | Unified semantic |
| --- | --- | --- |
| `thesis.md` | `thesis.md` | Why the system exists, who it serves, and what it refuses. |
| `agent-governance.md` | `agent-governance.md` | What agents may do, may not do, and when human review is required. |
| `agent-evaluation.md` | `agent-governance.md` / `human-review-checklist.md` | Agent quality, failure modes, and acceptance gates. |
| `agent-failure-modes.md` | `risk-register.md` | Agent risk classes and responses. |
| `architecture.md` | `automation-map.md` | System structure and automation structure. |
| `adr.md` | `decision-log.md` | Architecture and business decisions using a common record grammar. |
| `module-boundaries.md` | `tool-stack.md` / `api-dependency-map.md` | Module, tool, and external dependency boundaries. |
| `delivery-plan.md` | `roadmap.md` / `quarterly-plan.md` | Delivery plan and business roadmap. |
| `observability.md` | `funnel-dashboard.md` / `metrics.md` | Runtime observability and business dashboards. |
| `security-policy.md` | `legal-checklist.md` / `compliance-checklist.md` | Security and compliance controls. |
| `access-control.md` | `agent-permissions.md` | Access, operation, and approval rights. |
| `incident-response.md` | `support-playbook.md` / `feedback-triage.md` | Incident response and customer feedback response. |
| `support-playbook.md` | `customer-success-playbook.md` / `support-playbook.md` | Platform support and customer support. |
| `cli-ux.md` | `onboarding.md` / `service-blueprint.md` | Operator experience and customer or service experience. |
| `changelog.md` | `roadmap.md` / `monthly-review.md` | Change record and operating review. |
| `postmortem.md` | `learning-log.md` | Incident retrospective and business learning. |
| `template-library.md` | `content-calendar.md` / `landing-page.md` | Platform templates and market content assets. |

## Non-Mixable Truth

Business-governed only:

- `offer.md` - records the customer-facing promise and value package.
- `finance-model.md` - owns revenue, cost, runway, and viability assumptions.
- `cashflow.md` - tracks cash timing, obligations, and survival constraints.
- `contract-template.md` - governs customer or partner contract language.
- `terms-of-service.md` - governs customer-facing service terms and commitments.
- `sales-playbook.md` - governs sales motion, qualification, and human-approved promises.
- `customer-success-playbook.md` - governs customer success outcomes and relationship cadence.
- `refund-policy.md` - governs refund rules, exception handling, and customer remedies.
- `legal-checklist.md` - governs legal review triggers and required human confirmation.
- `compliance-checklist.md` - governs regulatory, privacy, and compliance review triggers.

Codex-governed only:

- `architecture.md` - records platform system structure and technical boundaries.
- `adr.md` - records architecture decisions and execution tradeoffs.
- `module-boundaries.md` - records code, tool, and integration boundaries.
- `observability.md` - records runtime telemetry and delivery reliability controls.
- `agent-governance.md` in the Codex package
- `agent-evaluation.md` - governs Agent quality checks and acceptance evidence.
- `agent-failure-modes.md` - governs Agent failure classes and mitigations.
- `access-control.md` - governs platform access, operation, and approval rights.
- `incident-response.md` - governs platform incidents and recovery actions.
- `delivery-plan.md` - governs code delivery, validation gates, and release boundaries.

## Required Wording

Use this wording in downstream documents:

> In a personal production one-person-company operating system, the Codex CLI personal production durable team is an embedded execution and governance capability. It governs AI agents, code delivery, durable execution, validation, release boundaries, and repo-local durable state. The one-person-company operating system governs customers, revenue, finance, legal commitments, support, market work, and business learning. The two systems share risk, decision, evidence, retrospective, and human-review semantics, but they must not mix business truth with platform truth.
