---
doc_id: codex_business_capability_profiles
lang: en
canonical: docs_bilingual/implementation_plans/codex_business_capability_profiles.md
translation_of: null
doc_class: implementation_reference
status: draft
---

# Codex Business Capability Profiles

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
