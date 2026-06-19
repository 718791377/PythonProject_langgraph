---
doc_id: one_person_company_cross_cutting_module_map
doc_class: product_lifecycle
status: active
package: one-person-company
generated_by: tools/generate_operations_package.py
lang: en
---
<!-- GENERATED_BY: tools/generate_operations_package.py; DO NOT EDIT BY HAND. -->
# One-Person Company Cross-Cutting Module Map
## Purpose

Defines the 20 cross-cutting modules that keep strategy, delivery, support, finance, trust, and administration aligned.
## Cross-Cutting Modules

| # | Module | Governance use |
| --- | --- | --- |
| 1 | Finance | Mapped to owner, gate, evidence, and retrospective |
| 2 | Operations | Mapped to owner, gate, evidence, and retrospective |
| 3 | Engineering management | Mapped to owner, gate, evidence, and retrospective |
| 4 | Organization design | Mapped to owner, gate, evidence, and retrospective |
| 5 | Legal and compliance | Mapped to owner, gate, evidence, and retrospective |
| 6 | Security | Mapped to owner, gate, evidence, and retrospective |
| 7 | Knowledge management | Mapped to owner, gate, evidence, and retrospective |
| 8 | Risk management | Mapped to owner, gate, evidence, and retrospective |
| 9 | Personal productivity | Mapped to owner, gate, evidence, and retrospective |
| 10 | AI agent governance | Mapped to owner, gate, evidence, and retrospective |
| 11 | Data governance | Mapped to owner, gate, evidence, and retrospective |
| 12 | Brand trust | Mapped to owner, gate, evidence, and retrospective |
| 13 | Toolchain governance | Mapped to owner, gate, evidence, and retrospective |
| 14 | SLA governance | Mapped to owner, gate, evidence, and retrospective |
| 15 | Asset and IP governance | Mapped to owner, gate, evidence, and retrospective |
| 16 | User-research governance | Mapped to owner, gate, evidence, and retrospective |
| 17 | Channel governance | Mapped to owner, gate, evidence, and retrospective |
| 18 | Exit governance | Mapped to owner, gate, evidence, and retrospective |
| 19 | Vendor governance | Mapped to owner, gate, evidence, and retrospective |
| 20 | Tax and administration governance | Mapped to owner, gate, evidence, and retrospective |
## Authority Boundary

This generated package uses tracked repository authorities refreshed from Business Management, product lifecycle, and PMP synthesis: codex_platform_inventory_map.md, one_person_company_inventory_map.md, durable_team_process_group_contract.md, lifecycle_tailoring_rules.md, pmi_project_management_reference_map.md, and the two current white papers. Stage B operationalizes those tracked authorities and does not re-extract raw PDF, EPUB, or Markdown source libraries.
## Canonical Inventory

| Inventory element | Count | Operating meaning |
| --- | --- | --- |
| Trunk layers | 12 | 0-11 twelve-layer model |
| Virtual departments | 5 | six responsibility domains per department |
| Responsibility domains | 30 | used for owner and RACI mapping |
| Cross-cutting modules | 20 | used for cross-layer risk and capability control |
| Core documents | 60 | organized as six-document families |
| Governed AI agents | 15 | each lane keeps a human gate |
| Recommended books | 15 | used as a topic map, not copied source text |
| Minimum startup documents | 12 | smallest operating set for launch |
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
