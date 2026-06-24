---
doc_id: codex_platform_responsibility_raci
lang: en
doc_class: product_lifecycle
status: active
canonical_path: docs_bilingual/product_lifecycle/codex_platform_responsibility_raci.md
zh_cn_path: docs_bilingual/product_lifecycle/codex_platform_responsibility_raci.zh-CN.md
---

<!-- GENERATED_BY: tools/generate_operations_package.py; DO NOT EDIT BY HAND. -->
# Codex Platform Responsibility RACI
## Purpose

Maps the 4 virtual departments and 24 responsibility domains to accountable, consulted, and informed surfaces.
## Departments And Responsibility Domains

| # | Virtual department | Responsibility domain |
| --- | --- | --- |
| 1 | Strategy and Product Office | CEO and strategy owner |
| 2 | Strategy and Product Office | Chief of staff |
| 3 | Strategy and Product Office | Business model owner |
| 4 | Strategy and Product Office | Finance owner |
| 5 | Strategy and Product Office | Market intelligence |
| 6 | Strategy and Product Office | Customer research |
| 7 | Engineering and Platform Office | Product strategy |
| 8 | Engineering and Platform Office | PM and PRD owner |
| 9 | Engineering and Platform Office | CLI and UX owner |
| 10 | Engineering and Platform Office | Metrics owner |
| 11 | Engineering and Platform Office | CTO and architect |
| 12 | Engineering and Platform Office | Engineering manager |
| 13 | Agent Governance Office | Code quality owner |
| 14 | Agent Governance Office | DevOps owner |
| 15 | Agent Governance Office | Platform and toolchain owner |
| 16 | Agent Governance Office | Security owner |
| 17 | Agent Governance Office | Privacy and data protection owner |
| 18 | Agent Governance Office | Data governance owner |
| 19 | Growth and Knowledge Office | Agent governance owner |
| 20 | Growth and Knowledge Office | Agent evaluation owner |
| 21 | Growth and Knowledge Office | Docs owner |
| 22 | Growth and Knowledge Office | Support owner |
| 23 | Growth and Knowledge Office | Brand and trust owner |
| 24 | Growth and Knowledge Office | Knowledge and review owner |
## Authority Boundary

This generated package uses tracked repository authorities refreshed from Business Management, product lifecycle, and PMP synthesis: codex_platform_inventory_map.md, one_person_company_inventory_map.md, durable_team_process_group_contract.md, lifecycle_tailoring_rules.md, pmi_project_management_reference_map.md, and the two current white papers. Stage B operationalizes those tracked authorities and does not re-extract raw PDF, EPUB, or Markdown source libraries.
## Canonical Inventory

| Inventory element | Count | Operating meaning |
| --- | --- | --- |
| Trunk layers | 12 | 0-11 twelve-layer model |
| Virtual departments | 4 | six responsibility domains per department |
| Responsibility domains | 24 | used for owner and RACI mapping |
| Cross-cutting modules | 18 | used for cross-layer risk and capability control |
| Core documents | 48 | organized as six-document families |
| Governed AI agents | 12 | each lane keeps a human gate |
| Recommended books | 12 | used as a topic map, not copied source text |
## 12 Trunk Layers

| # | Layer | Primary question |
| --- | --- | --- |
| 0 | Cognitive narrative | Why should the platform or company exist |
| 1 | Business | Why is it worth maintaining |
| 2 | Market | Which users and segments need it |
| 3 | Strategy | What to do first and what to refuse |
| 4 | Metrics | What evidence changes decisions |
| 5 | Product | Which workflows or offers are exposed |
| 6 | Technical | How systems stay safe and evolvable |
| 7 | Organization | Who owns decisions and permissions |
| 8 | Execution | How work ships and rolls back |
| 9 | Growth | How adoption or demand compounds |
| 10 | Operations | How support and runtime health stay stable |
| 11 | Retrospective | How lessons become durable |
## Tailoring Rules

Tailoring does not delete layers from the mental model. It chooses the minimum sufficient governance depth. Every tailoring record must explain why the selected mode is not heavier or lighter and list escalation triggers.

| Mode | Use when | Lightweight scope |
| --- | --- | --- |
| Full architecture | Use for cross-stage, external-customer, revenue, compliance, security, publication, rollback, durable-state, shared-runtime, or multi-agent work. | Govern every affected layer end to end; write full evidence only for the affected risk scope. |
| Whole-project lightweight | Use only for private, reversible, low-risk exploration with no external commitment, durable-state impact, publication, sensitive data, or shared runtime. | The whole project may stay lightweight, but it still records owner, scope, validation, rollback or deletion, and learning. |
| Phase-local lightweight | Use when one discovery, metrics, growth, or retrospective phase is low risk inside a larger governed project. | Only that named phase is light; upstream and downstream gates remain explicit. |
| Module-level lightweight | Use for one bounded document family, helper, prototype, or local module that does not change trust, state, public API, CI, release, or shared runtime behavior. | Only the module is light; the surrounding project keeps its full architecture boundary. |
| Hybrid architecture | Use for most real work: start light for uncertainty, then freeze fuller controls before customer, production, revenue, trust, durable-state, or release impact. | Critical layers are full; low-risk phases or modules stay light until escalation triggers fire. |
## Inputs

- Current white paper, North Star, inventory map, PMI map, and lifecycle tailoring rules.
- Target project or platform slice risk, coupling, owner, evidence, and constraints.
- Local-main-first workflow state, OpenSpec state, validation path, and remote-publication boundary.
## Tools And Techniques

- Twelve-layer landing analysis, responsibility-domain mapping, RACI, process-group I/T/O, and tailoring scorecard.
- PMBOK 8 value and tailoring overlay, Process Groups execution grammar, Agile feedback loop, and PMO governance service when needed.
- Generator, checker, local CI, local MR review, rollback reference, and lessons learned.
## Outputs

- Bilingual governed operations-package documents, registry entries, validation reports, and changed-path evidence.
- Explicit tailoring decision, escalation triggers, owner, validation, and closeout record.
- Stop point at the remote-publication gate unless the user explicitly authorizes remote publication.
## Process Group Operating Table

| Process group | Inputs | Tools And Techniques | Outputs |
| --- | --- | --- | --- |
| Initiating | purpose, value hypothesis, stakeholder signal, scope boundary, initial risks | charter-like framing, owner mapping, non-goal review, tailoring pre-check | authorization to continue, named owner, scope boundary, initial risk log |
| Planning | approved purpose, dependencies, constraints, risk profile, acceptance target | I/T/O planning, release slicing, validation design, rollback design, role-boundary review | plan, acceptance criteria, dependency map, validation path, rollback boundary |
| Executing | approved slice, source evidence, templates, worktree state, role ownership | controlled drafting or implementation, review, testing, documentation update, bounded expert or durable-lane handoff when eligible | drafted artifact, controlled change set, validation work, changed-path evidence |
| Monitoring and Controlling | active work products, metrics, issues, review feedback, local gate output | quality checks, change control, variance review, risk response, diff review, gate reruns | issue log, change decisions, metric checks, local-gate evidence, rollback readiness |
| Closing | accepted work, final evidence, archive candidates, lessons, residual risks | closeout review, archive or sync, release-note update, retrospective, next-cycle triage | final artifact, archive or closeout record, lessons learned, next-cycle input |

## Stage B Embedded Governance Closeout

This Stage B closeout makes the nested relationship explicit: the one-person company owns business truth, and embedded Codex owns governed execution truth. Embedded Codex is not a peer business authority and must not redefine business truth.

- Codex boundary: Codex owns execution truth for agents, OpenSpec, worktrees, durable state, validation gates, local-main evidence, rollback, and release boundaries, while consuming business intent from the one-person company.
- Tailoring modes: full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, and hybrid are all scoped choices. Tailoring does not delete the twelve-layer mental model; it only changes how much evidence and ceremony is required for the chosen project, phase, module, or release slice.
- Bridge rule: the 10-layer runtime capability view is an implementation projection of the 12-layer lifecycle view. The bridge prevents runtime convenience from overriding lifecycle authority.

### Inputs

- Current business intent, execution evidence, registry entry, tailoring decision, and local-main / remote-publication boundary.
- Business truth inputs when customers, revenue, pricing, contracts, legal posture, cashflow, support, delivery commitments, or business learning are affected.
- Execution truth inputs when agent routing, OpenSpec, worktree isolation, durable state, validation, rollback, or release boundaries are affected.

### Tools And Techniques

- Apply the shared truth-boundary map before selecting full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, or hybrid mode.
- Use process-group I/T/O, RACI ownership, evidence traceability, validation gates, and escalation triggers instead of deleting layers.
- Route mixed changes through both the business gate and the Codex execution gate before local-main integration or remote publication.

### Outputs

- A scoped governance mode, updated evidence trail, linked registry entry, and explicit owner for business truth, execution truth, or mixed truth.
- A closeout decision that either stays lightweight in the declared scope, escalates to fuller architecture, or stops at the publication gate until human approval.
