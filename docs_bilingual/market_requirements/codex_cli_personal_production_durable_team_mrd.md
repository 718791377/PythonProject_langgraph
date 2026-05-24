---
doc_id: codex_cli_personal_production_durable_team_mrd
lang: en
canonical: docs_bilingual/market_requirements/codex_cli_personal_production_durable_team_mrd.md
translation_of: null
doc_class: market_requirements
status: draft
---

# MRD: Codex CLI Personal Production Durable Team

## Purpose

This MRD identifies target users, project types, usage scenarios, capability profiles, runtime-owner classes, and universal controls for the Codex CLI personal production durable-team platform.

It replaces the former standalone `docs_bilingual/implementation_plans/codex_business_capability_profiles.md` reference; that file was a capability-profile lookup table and is now merged into Appendix A of this MRD.


## White Paper, Research Canon, And 10-To-12-Layer Bridge

This MRD uses the same document split as the refreshed lifecycle canon:

- White paper: `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md` is the concise strategic narrative for why the platform exists, what target state it pursues, and how the 12-layer product/business lifecycle frames the platform direction.
- Governance research canon: `docs_bilingual/governance/solo_maintainable_production_persistent_team_research.md` is the evidence-heavy research document for production capability, governance, and the 10-layer runtime capability core.
- Merge policy: these two documents should not be collapsed by default. The white paper must remain readable as a directional artifact, while the research canon preserves detailed evidence, alternatives, and operating constraints.
- Bridge rule: the 10-layer core is an execution-capability decomposition; the 12-layer trunk is the market/product/business lifecycle architecture. MRD requirements must use the 12-layer trunk for market traceability and may reference the 10-layer core only when a requirement needs runtime capability ownership.

## Target Users And Project Types

- Solo maintainer: the primary operator who uses Codex CLI across multiple repositories.
- Consumer project: a downstream repository that consumes user-level runtime, templates, policies, and native subagent profiles while keeping its own source, OpenSpec artifacts, tests, and durable state.
- Domain-agent platform project: a project that configures user-facing domain agents outside Codex CLI while Codex CLI supports development, governance, checks, and releases.
- Document or content workflow project: a project that creates, transforms, reviews, publishes, or audits artifacts.

## User Problems

- Cold-start sessions need safe resume without repeated manual context explanation.
- Multiple sessions need file ownership boundaries to avoid dirty-worktree collision.
- Projects need browser, document, GUI, model-provider, and publication support without mixing business runtime truth into this platform repository.
- High-risk actions need human approval, audit records, rollback notes, and project-local evidence.

## Market Requirements

- Preserve native Codex behavior and rollback.
- Support local Git plus OpenSpec governance for later projects.
- Keep Codex CLI durable-team dependencies separate from downstream business runtime dependencies.
- Classify new workloads into abstract capability profiles before implementation starts.
- Preserve browser automation and document-processing capabilities for projects that need them.

## Target Architecture Inventory Requirements

Market requirements must now be traced to the Codex platform inventory:

- 4 virtual departments translate market pain into platform ownership: Strategy & Product, Engineering & Platform, Agent Governance, and Growth & Knowledge.
- 24 responsibility domains prevent market needs from becoming vague requests; each need must map to a domain such as CLI/UX, metrics, security, data governance, support, trust, or knowledge/review.
- 18 cross-cutting modules identify risks that cross product, engineering, operations, and governance boundaries.
- 48 core documents are the maximum serious platform document surface, not the default for every change.
- 12 governed agents are capability profiles with explicit read/write/review boundaries, not autonomous business decision makers.
- `docs_bilingual/product_lifecycle/codex_platform_inventory_map.md` is the canonical inventory-count map for these platform requirements.

For downstream one-person-company work, the MRD belongs in the downstream repository. That MRD owns local customer evidence, market segmentation, pricing signals, channel evidence, finance assumptions, product commitments, and support expectations. The downstream count reference is `docs_bilingual/product_lifecycle/one_person_company_inventory_map.md`.

The downstream operating-system target is explicit but not owned by this platform MRD: 12 layers, 5 virtual departments, 30 responsibility domains, 20 cross-cutting modules, 60 core documents, 15 governed AI agents, 15 recommended books, and a 12-document minimal startup floor. Platform requirements may provide templates and governance checks for that target, but they must not become the downstream business runtime truth.

## Tailoring Requirements

Market requirements must not force every project to create the maximum document stack. Use `docs_bilingual/product_lifecycle/lifecycle_tailoring_rules.md` to choose the minimum sufficient architecture depth. Use `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.md` as the PMI reference map: PMBOK 8 frames value delivery and tailoring, PMBOK 7 and PMBOK 6 supplement principles and process vocabulary, Process Groups provides delivery gates, Agile Practice Guide covers adaptive/hybrid work, Program Management covers related initiatives, Portfolio Management covers value/capacity trade-offs, and the PMO Practice Guide covers governance services.

- Full Codex platform scope is required when a requirement affects reusable orchestration, native subagent routing, `native_omx`, LangGraph, worktree safety, OpenSpec governance, user-level launcher policy, skill/profile governance, local-main-first publication, shared templates, durable state, release safety, or cross-project adoption.
- Whole-project lightweight scope is allowed only for private spikes, early ideas, local learning, or low-risk internal tools without external users, money, trust boundaries, sensitive data, shared runtime entrypoints, or release commitments.
- Phase-local lightweight scope is allowed when a specific discovery, metrics, growth, or retrospective phase inside a larger effort is low-risk, reversible, and has explicit expansion triggers.
- Module-level lightweight scope is allowed when a bounded documentation, research, helper, prototype, or spike module does not change runtime entrypoints, durable state, secrets, CI gates, release gates, or downstream project dependencies.
- Hybrid scope is required when market or product uncertainty is high but the eventual delivery may affect users, trust, revenue, compliance, runtime behavior, or release safety.

## Process-Group Evidence For Market Requirements

Execution-facing MRD items must state per-process-group Inputs, Tools and Techniques, and Outputs:

| Process group | Inputs | Tools and Techniques | Outputs |
| --- | --- | --- | --- |
| Initiating | Customer evidence, operator pain, market signal, support feedback, platform boundary, source lifecycle inputs | Problem framing, stakeholder analysis, value-case check, non-goal framing | Target segment candidate, priority problem, value hypothesis, authorization boundary |
| Planning | Initiation output, constraints, capacity, risk, existing lifecycle docs, source-synthesis evidence | Segmentation, positioning, interview synthesis, competitor analysis, prioritization, risk review | MRD scope, success criteria, decision thresholds, evidence plan, stop/pivot criteria |
| Executing | Approved MRD scope, templates, source evidence, stakeholder feedback | Drafting, research synthesis, requirement decomposition, profile mapping, review | Updated MRD, mapped capability profiles, target architecture links, acceptance evidence |
| Monitoring and Controlling | Draft MRD, review comments, market changes, gate output, issue log | Change control, adoption-friction review, risk review, local doc checks, diff review | Accepted changes, deferred issues, revised thresholds, validation evidence |
| Closing | Accepted MRD, final evidence, lessons, archive candidates | Closeout review, doc registry update, OpenSpec/archive sync when applicable, retrospective | Final MRD section, registry/spec sync, lessons learned, next-cycle inputs |

## Prioritization Signals

- P0 protects native Codex compatibility, session isolation, repo-local durable truth, OpenSpec guards, and rollback.
- P1 improves inspected durable routing, project templates, local model-provider adapters, and repeatable release slices.
- P2 improves local GUI control, advanced memory, richer evaluation, and broader adoption reporting.

## Appendix A: Capability Profiles Merged From The Former Reference

This reference maps concrete workload examples to abstract capability profiles for the Codex CLI personal production durable-team plan. It is a lookup table, not a runtime contract and not a claim that any workload is already implemented.

## 1. Usage Rules

- Keep concrete workload names in this reference file, not in the main production durable-team plan.
- Map each workload to one or more abstract profiles before implementation work starts.
- Treat the runtime owner class as a boundary label, not as a technology mandate.
- Keep Codex CLI durable-team dependencies separate from business runtime dependencies unless a business project explicitly owns the same dependency in its own repository.
- A local Llama model service is the only shared dependency exception in this reference; it must still be used through provider adapters with separated logs, permissions, prompts, secrets, and data boundaries.

## 2. Runtime Owner Classes

| Runtime owner class | Meaning |
| --- | --- |
| Codex-developed project | A concrete project whose source, tests, dependencies, and release artifacts live in its own repository while the Codex CLI durable team helps develop and govern it. |
| External domain-agent runtime | A user-facing domain-agent runtime outside Codex CLI; the Codex CLI durable team governs profiles, knowledge updates, release checks, regression, and recovery support rather than serving end-user conversations directly. |
| External content platform | A third-party publishing, messaging, commerce, or content platform; all publication and reply actions require approval, audit, and platform-boundary controls. |
| Local professional tool | A local desktop or specialist tool operated through guided steps, screenshots, local files, or human-in-the-loop verification. |
| Document processing pipeline | A workflow that transforms files, layouts, evidence, and generated deliverables while preserving audit and review records. |
| Shared local model service | A local Llama deployment used as a model provider through adapters; it is a model service, not workflow state or business state. |

## 3. Concrete Workload Reference Table

| Concrete workload example | Abstract capability profiles | Runtime owner class | Required universal controls | Risk level |
| --- | --- | --- | --- | --- |
| Virtual avatar selection mini-app - a frontend product for choosing character assets. | Interactive frontend product delivery; generated media asset pipeline. | Codex-developed project. | UI validation, asset versioning, release gate, rollback note. | Medium. |
| Character original-art generation workflow - a local image-generation workflow for avatar source art. | Generated media asset pipeline. | Local professional tool; shared local model service when a local model is used. | Prompt and parameter record, asset review, source and license note, approval before downstream use. | Medium. |
| Short-video generation and publishing workflow - a content creation and platform publishing workflow. | Generated media asset pipeline; platform content operations. | External content platform. | Human approval, audit ledger, platform receipt capture, retry boundary, rollback or takedown note. | High. |
| Storefront customer-message automation - a customer reply and human-handoff workflow for a commerce channel. | Customer message automation with human handoff; platform content operations. | External content platform. | Sensitive-content detection, human takeover, reply audit, escalation, secrets boundary. | High. |
| Positive-psychology or humanistic counseling domain agent - a sensitive support agent configured in an external domain-agent runtime. | External domain-agent runtime governance; customer message automation with human handoff; high-risk decision support. | External domain-agent runtime. | Crisis escalation, disclaimer, privacy boundary, human handoff, regression set, audit. | Sensitive / high. |
| Academic literature research domain agent - a citation and evidence-oriented knowledge agent configured in an external domain-agent runtime. | External domain-agent runtime governance; knowledge retrieval and citation workflows. | External domain-agent runtime. | Source citation, evidence chain, hallucination check, knowledge refresh, regression set. | Medium. |
| Engineering simulation teaching domain agent - a guided professional-tool teaching agent configured in an external domain-agent runtime. | External domain-agent runtime governance; professional tool teaching and guided operation; knowledge retrieval and citation workflows. | External domain-agent runtime; local professional tool. | Step verification, screenshot evidence, case library, risk notice, regression set. | Medium / high. |
| Solo one-person-company operations workflow - a personal operations workflow for sales, delivery, cost, and review cycles. | Solo business operations management; structured proposal and compliance document delivery. | Codex-developed project. | Audit, review cadence, customer data boundary, financial data boundary, backup. | Medium / high. |
| Personal quantitative-finance tooling - decision-support tooling for research, simulation, and risk-controlled operations. | High-risk decision support; knowledge retrieval and citation workflows; generated report pipeline. | Codex-developed project. | Paper-trading default, approval, backtest, audit, stop-loss note, no default live execution. | High / regulated. |
| Position-preserving PDF translation workflow - a layout-sensitive document transformation workflow. | Layout-sensitive document transformation. | Document processing pipeline. | OCR or text extraction record, render diff, human review, output audit, source backup. | Medium. |
| Bid or compliance package generation workflow - a structured deliverable production workflow. | Structured proposal and compliance document delivery; knowledge retrieval and citation workflows; layout-sensitive document transformation. | Document processing pipeline. | Source collection, citation, compliance checklist, approval, final version record. | High. |
| New-computer and project-template rollout workflow - a bootstrap and update workflow for new and existing development projects. | Template and project bootstrap lifecycle. | Codex-developed project. | Backup branch, manifest comparison, managed-file update, checker gate, rollback note. | Medium. |

## 4. Extension Rule

When a new concrete workload appears, add it to this table first, map it to abstract profiles, and then decide whether the Codex CLI durable team needs new shared adapters, checkers, regression fixtures, or template update support.
