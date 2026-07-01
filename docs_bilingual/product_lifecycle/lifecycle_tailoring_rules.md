---
doc_id: lifecycle_tailoring_rules
lang: en
doc_class: product_lifecycle
status: draft
canonical_path: docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.md
zh_cn_path: docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.zh-CN.md
---

# Lifecycle Tailoring Rules

This document defines how to tailor the 12-layer lifecycle for the two target architecture modes:

- Codex CLI personal production durable team: 12 trunk layers + 4 virtual departments + 24 responsibility domains + 18 cross-cutting modules + 48 core documents + 12 governed AI agents + 12 recommended books.
- Personal production one-person-company operating system: 12 trunk layers + 5 virtual departments + 30 responsibility domains + 20 cross-cutting modules + 60 core documents + 15 governed AI agents + 15 recommended books + 12 minimal startup documents.

It is a governance overlay for `product_business_document_lifecycle.md`, `codex_durable_team_platform_build_lifecycle.md`, `codex_project_consumption_lifecycle.md`, and `pmi_project_management_reference_map.md`.

The rule is source-backed by the local `Business Management/` and `PMP/` synthesis. The local references were read as PDF pages, EPUB spine items, and Markdown full text; this document records only repository-specific operating rules and does not reproduce source-book text.

## Source Evidence Boundary

This tailoring rule is refreshed from the Stage B evidence run `one-person-company-pmi-refresh-stageb-20260619` (`2026-06-18T18:37:58Z`), covering 54 local sources and 9,656 page/spine/full-document units. It supersedes outdated extraction wording for this refresh and keeps raw extracted text in ignored local cache only. Use `fresh_source_reading_evidence.md` for the current evidence index.

## Tailoring Principle

Tailoring means choosing the minimum sufficient governance system for the risk and uncertainty of the work. It does not mean deleting layers from the mental model.

All work still uses the same 12-layer map. Tailoring decides:

- which layers need full documents;
- which layers can be summarized in a canvas, issue, OpenSpec artifact, or short note;
- which approvals, checks, reviews, releases, rollback evidence, and retrospectives are required;
- whether the whole project, one phase, one gate, or one module can remain lightweight.

## Process-Group Tailoring Gate

Use this gate before opening a large documentation stack, launching durable workers, selecting LangGraph, publishing a release, or deciding that a small change can stay lightweight.

### Inputs

- Target mode: Codex platform target or one-person-company target.
- Work type: new product, platform runtime change, project template change, documentation-only update, spike, experiment, local internal tool, customer-facing change, payment or trust-impacting change, compliance-sensitive change, or long-lived architecture change.
- Affected lifecycle layers, responsibility domains, cross-cutting modules, core documents, and governed agents.
- Risk and uncertainty: money, users, trust, security, privacy, legal/compliance, data, availability, cost, migration, release, rollback, and stakeholder risk.
- Coupling: shared interfaces, runtime entrypoints, durable state, cross-project templates, public APIs, or downstream project dependencies.
- Current evidence: source synthesis, user evidence, metrics, OpenSpec state, Git state, test evidence, operations incidents, and lessons learned.
- Constraints: time budget, CI minutes, provider pacing budget, operator attention, model/tool availability, and approval limits.

### Tools And Techniques

- Tailoring scorecard: classify impact as full, release-slice, phase-local lightweight, module-level lightweight, or whole-project lightweight.
- Risk and uncertainty matrix: separate high-risk clear work from high-uncertainty discovery work.
- Predictive/adaptive/hybrid selection: use predictive gates for clear high-risk delivery, adaptive slices for exploration, and hybrid flow when discovery must later pass delivery gates.
- Scope-boundary review: decide whether lightening applies to the entire project, only one phase, only one module, or only one documentation gate.
- Architecture-boundary review: check dependency direction, data ownership, trust boundaries, interface stability, rollback path, and state ownership.
- Governance-depth review: choose required approvals, OpenSpec artifacts, local CI, local MR review, remote confirmation, release notes, rollback, and retrospective.
- Escalation review: define which signals force expansion from lightweight to fuller governance.

### Outputs

- Tailoring decision record: full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, or hybrid.
- Minimum sufficient document set for the selected scope.
- Explicit list of expanded layers and summarized layers.
- Required approvals, reviews, validation, release, rollback, and retrospective evidence.
- Escalation triggers and owner for re-tailoring.
- Decision to continue, stop, run a spike, split scope, or expand governance.

## PMI Overlay By Tailoring Outcome

Tailoring also decides how much PMI overlay is needed. The overlay can be applied to the whole project, a phase, a module, or a release slice; it does not have to be all-or-nothing.

| Tailoring outcome | PMI overlay | Execution rule |
| --- | --- | --- |
| Full architecture | PMBOK 8 value/tailoring plus Process Groups, with PMBOK 6 I/T/O detail where execution artifacts are produced; add Agile, program, portfolio, or PMO overlays when their entry triggers are present | Consider all 12 layers and write full evidence for affected layers; do not create every document immediately unless the affected risk scope requires it |
| Whole-project lightweight | Minimal project canvas plus a small process-group note; PMI remains implicit except for validation, risk, and closing evidence | Allowed only for private, reversible, low-risk work with no external users, money, sensitive data, durable state, shared runtime, or release commitment |
| Phase-local lightweight | Use I/T/O only for that phase and define upstream/downstream gates; keep high-risk adjacent phases on fuller governance | The whole project is not lightweight; only the named phase is reduced |
| Module-level lightweight | Use a module scope note, owner, validation, rollback/deletion path, and learning note | The surrounding project keeps full architecture boundaries; the module may not change trust, durable state, public API, shared runtime, or release safety without re-tailoring |
| Hybrid | Start with adaptive Agile-style discovery and lightweight I/T/O, then freeze predictive Process Groups before production, release, customer, trust, durable-state, or shared-runtime change | Lighten discovery first; expand the affected layer/module when risk becomes real; expand whole project only when coupling becomes systemic |

The default question is not "full or light for everything?" The default question is: which exact scope is light, which exact scope remains full, and which signal forces expansion.

## When To Use The Full Architecture

Use the full architecture for the affected scope when any of these triggers are true:

- The work is a new product, new commercial offer, major business pivot, or long-lived platform.
- The work affects money, external users, customer commitments, payments, trust, safety, legal/compliance, security, privacy, or regulated decision support.
- The work changes data ownership, durable state, persistence, secrets, permissions, authentication, authorization, or audit evidence.
- The work changes runtime entrypoints, wrappers, launchers, MCP placement, shared helpers, project templates, OpenSpec governance, CI gates, release gates, or rollback behavior.
- The work creates or changes shared interfaces, API contracts, cross-project templates, agent permissions, durable-worker behavior, or graph checkpoints.
- The work has broad adoption impact, public documentation impact, customer support impact, or high cost of rollback.
- Multiple modules, teams, agents, repositories, or external systems must coordinate.

Full architecture does not always mean writing all 48 or 60 documents immediately. It means all 12 layers are explicitly considered, and the affected layers receive full evidence, ownership, validation, release, rollback, and learning coverage.

## When Whole-Project Lightweight Architecture Is Allowed

Whole-project lightweight architecture is allowed only when all of these are true:

- The project is an early idea, private spike, local learning exercise, or small internal tool.
- There are no external users, customer commitments, revenue promises, payment flows, legal/compliance exposure, production data, sensitive data, or trust boundaries.
- The result is reversible or disposable.
- No shared runtime entrypoint, durable state, cross-project template, public API, CI gate, release gate, or downstream project dependency changes.
- One owner can understand the whole system and rollback path without hidden coordination.

The minimum output is usually a short canvas, scope note, acceptance note, validation note, and lessons-learned note. If code is changed, keep technical and execution evidence even when the rest of the project stays lightweight.

## When Phase-Local Lightweight Architecture Is Allowed

Phase-local lightweight architecture is allowed when the project overall needs fuller governance, but a specific phase is low-risk or still exploratory.

Examples:

- Discovery phase can use interview notes, opportunity maps, and prototype feedback before a full PRD is frozen.
- Metrics phase can start with a simple North Star note before the tracking plan and data dictionary exist.
- Growth phase can run a small channel test before a full growth operating model is justified.
- Retrospective phase can start with a short lessons note when no incident, customer impact, or policy change occurred.

Phase-local lightening must state which phase is lightweight, which upstream and downstream layers it touches, and what evidence will trigger expansion.

## When Module-Level Lightweight Architecture Is Allowed

Module-level lightweight architecture is allowed inside an otherwise full-governed project when a module is bounded, reversible, and low-risk.

Allowed examples:

- A documentation-only appendix inside a full platform release.
- A local-only helper script that does not change launcher behavior, shared state, secrets, or CI gates.
- A prototype UI component that is not released, not customer-facing, and not coupled to production data.
- A non-authoritative research summary that feeds a later MRD or strategy review.

Module-level lightening must preserve the full project's architecture boundaries. The lightweight module still needs an owner, scope boundary, validation note, rollback or deletion path, and learning note.

## When Hybrid Architecture Is Required

Use a hybrid path when uncertainty is high but the final delivery risk is also high.

Hybrid flow:

1. Start adaptive: spike, prototype, discovery interview, document experiment, or proof of concept.
2. Record lightweight Inputs, Tools and Techniques, Outputs for the spike.
3. Freeze a predictive plan before production change, platform publication, customer commitment, durable state change, or remote release.
4. Expand only the affected layers first.
5. Expand to project-wide full governance if coupling, adoption, support, compliance, or rollback risk becomes systemic.

Hybrid is the default for AI-era project work that starts unclear but may become a real platform, product, customer, revenue, trust, or operations system.

## Escalation Triggers

Escalate from lightweight to fuller governance when any of these become true:

- A spike becomes production code.
- A local tool becomes shared template, launcher, CI gate, or reusable helper.
- A document note becomes market promise, product commitment, governance rule, or stable spec.
- A module begins touching secrets, identity, permissions, personal data, customer data, money, legal/compliance, or release state.
- A single owner can no longer review the whole impact.
- Rollback becomes expensive, ambiguous, or dependent on external parties.
- User, customer, operator, or stakeholder feedback creates new obligations.
- Repeated incidents or support questions show the lightweight path is no longer sufficient.

Escalation should first expand the affected layer, phase, or module. Expand the whole project only when the coupling is systemic.

## Minimum Document Sets By Tailoring Outcome

| Outcome | Minimum sufficient documents or records |
| --- | --- |
| Whole-project lightweight | `project_canvas.md`, scope/non-goal note, validation note, owner note, lessons note |
| Phase-local lightweight | Phase note with Inputs / Tools and Techniques / Outputs, dependency note, evidence trigger, next-gate decision |
| Module-level lightweight | Module scope note, owner, boundary, validation, rollback or deletion path, learning note |
| Platform release slice | OpenSpec proposal/design/tasks, touched lifecycle-layer notes, technical and organization evidence, test/release/rollback evidence, archive and lessons |
| Full Codex platform architecture | White paper, MRD, North Star plan, strategy/metrics/product/technical/organization/execution/growth/operations/retrospective coverage for the affected platform target |
| Full one-person-company architecture | 12 minimal startup documents first, then expanded BRD/MRD/strategy/metrics/product/technical/organization/execution/growth/operations/retrospective documents as revenue, customer, compliance, delivery, and operations evidence grows |

## Codex Platform Tailoring

For `D:\PythonProject_langgraph`, full architecture is required for changes that affect reusable orchestration behavior, native subagent routing, `native_omx`, LangGraph, worktree safety, OpenSpec governance, user-level launcher policy, skill/profile governance, local-main-first publication, or shared templates.

An ordinary documentation-only OpenSpec change may stay release-slice sized, but it must still record the changed layer, source evidence, validation evidence, and archive evidence.

Do not launch a durable team just because the full architecture is referenced. Durable team launch still requires a frozen plan plus at least two mostly independent execution slices.

## One-Person-Company Tailoring

For a downstream one-person-company operating system, do not start by creating all 60 documents. Start with the 12 minimal startup documents:

`thesis.md`, `business-model.md`, `offer.md`, `pricing.md`, `user-segments.md`, `growth-model.md`, `finance-model.md`, `ops-playbook.md`, `metrics.md`, `risk-register.md`, `agent-governance.md`, and `monthly-review.md`.

Expand to fuller governance when the business gains paying customers, repeatable delivery, support obligations, financial complexity, compliance exposure, sensitive data, external partners, recurring incidents, or agent automation beyond low-risk support.

## Tailoring Review Cadence

Review tailoring at these gates:

- before opening or expanding a major OpenSpec change;
- before committing to a public or customer-facing release;
- before launching durable workers or graph orchestration;
- before changing shared runtime, durable state, secrets, permissions, or release gates;
- after incidents, failed validation, repeated support questions, or major strategy changes;
- during retrospective closing.

The closing output should state whether the next cycle remains lightweight, expands a layer/module, or returns to a smaller governance footprint.

## One-Person Company PMI Tailoring Matrix

For the one-person-company operating system, decide the tailoring scope before expanding documents. The decision is local to the affected risk surface unless coupling becomes systemic.

| Mode | Use when | Scope rule | Minimum I/T/O evidence |
| --- | --- | --- | --- |
| Full architecture for affected scope | Customer-visible release, payment, sensitive data, compliance, repeated delivery, support obligation, external commitment, broad agent automation, or material revenue/risk | Expand the affected layer, phase, module, or release slice first; expand the whole project only when coupling is systemic | Initiating value case, planning controls, executing validation, monitoring guardrails, closing learning |
| Whole-project lightweight | The whole project is private, reversible, low-risk, local-only, one-owner, no users, no money, no sensitive data, no support promise, no shared runtime, no release commitment | The whole project may stay light | Compact canvas, stop condition, owner, validation note, learning note |
| Phase-local lightweight | Discovery, interview, prototype, content exploration, or metric exploration is low-risk inside a larger governed project | Only the named phase is light | Phase Inputs / Tools and Techniques / Outputs plus trigger to expand |
| Module-level lightweight | A bounded module is reversible and does not change trust, durable state, customer promise, public API, support, or release safety | Only the module is light | Module scope, owner, validation, rollback or deletion path, learning note |
| Hybrid | Discovery is uncertain but later delivery may affect production, users, revenue, trust, compliance, runtime behavior, or release safety | Start light; freeze full controls before external impact | Discovery I/T/O first, then predictive process-group I/T/O for affected delivery layers |

The default is not full-for-everything or light-for-everything. The default is local lightness with explicit escalation triggers.

## Stage B Embedded Governance Closeout

This Stage B closeout makes the nested relationship explicit: the one-person company owns business truth, and embedded Codex owns governed execution truth. Embedded Codex is not a peer business authority and must not redefine business truth.

- Shared boundary: business truth defines customers, revenue, pricing, contracts, legal posture, cashflow, support, delivery commitments, and business learning; execution truth defines agents, OpenSpec, worktrees, durable state, validation gates, local-main evidence, rollback, and release boundaries.
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
