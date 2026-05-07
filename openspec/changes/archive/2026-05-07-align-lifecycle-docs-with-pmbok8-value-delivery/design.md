## Context

A local reading audit extracted text from seven PDF files and twelve main HTML pages under the local private `PMP/` reference tree. The audit confirmed that the PMBOK 8th Edition PDF, the English Process Groups guide, and the English Agile Practice Guide are the most reliable sources. Several Chinese PDF extracts are usable for structure only because of OCR or encoding noise.

The repository should not reproduce PMI text. It should translate the usable structure into repository-specific governance language.

## Goals / Non-Goals

Goals:

- Make PMBOK 8th Edition the primary lifecycle overlay for value delivery, project canvas, performance domains, AI-era project governance, and tailoring.
- Keep PMBOK 6th Edition and Process Groups as the operational supplement for initiating, planning, executing, monitoring and controlling, closing, and input/tool/output thinking.
- Keep PMBOK 7th Edition as the principles, performance-domain, value-delivery, and tailoring bridge.
- Keep Agile guidance as the adaptive and hybrid delivery supplement for MVP slices, feedback loops, and small MR releases.
- Keep platform-build and downstream-consumption lifecycles separate.
- Add a lightweight Codex platform project canvas without requiring every small change to expand the full lifecycle.

Non-goals:

- Do not copy PMI book content into the repository.
- Do not convert the repository into a traditional PMP template repository.
- Do not change runtime launchers, MCP configuration, Codex wrappers, `native_omx`, or `langgraph` behavior.
- Do not claim the long-term durable-team draft is implemented.
- Do not use low-text or OCR-polluted extracts as precise quotation sources.

## Decisions

### Decision 1: Use PMBOK 8th Edition as the primary overlay, not as a replacement lifecycle

The repository will describe PMBOK 8th Edition as the primary overlay for value delivery and project governance. It will not replace the existing white paper, MRD, North Star plan, PRD, technical design, implementation plan, OpenSpec, or checker structure.

Why:

- The existing 0-8 lifecycle is already aligned with this repository's document model.
- PMBOK 8th Edition adds value-delivery and project-canvas language that can strengthen the lifecycle without replacing it.

### Decision 2: Treat Project Canvas as a lightweight alignment artifact

A Codex platform project canvas will be added as a one-page alignment document. It will sit between the startup summary and long implementation plans.

Why:

- Cold-start readers need a compact view of purpose, value, boundaries, stakeholders, risks, delivery style, and outcomes.
- A canvas reduces the chance that maintainers expand all lifecycle documents before the initiative is ready.

### Decision 3: Preserve process-group thinking as execution support

Process Groups and PMBOK 6th Edition guidance will be mapped to OpenSpec and GitLab-first delivery gates, but only as an execution support model.

Why:

- The process-group model is useful for input/tool/output discipline and closeout gates.
- It should not override PMBOK 8th Edition's value-delivery framing or the repository's OpenSpec workflow.

### Decision 4: Make tailoring a governance-system decision

Tailoring will cover governance depth, document depth, role collaboration depth, validation depth, release evidence, rollback evidence, and retrospective depth.

Why:

- This repository frequently handles small read-only reviews, medium documentation changes, runtime hardening, and cross-project durable-state work.
- Those tasks need different governance depth instead of one mandatory paperwork stack.

### Decision 5: Keep AI-era responsibility explicit

The white paper and platform lifecycle will state that AI can accelerate research, drafting, candidate planning, state summarization, and verification support, while the human operator and main leader session remain responsible for value judgment, risk trade-offs, approvals, and release responsibility.

Why:

- This matches the repository's rules that native Codex remains the base layer and automated durable teams require thresholds and consent.
- It prevents hidden automation from being mistaken for governance.

## Risks / Trade-offs

- Risk: The update could become a broad PMI summary. Mitigation: keep every addition repository-specific and avoid reproducing PMI content.
- Risk: Project canvas could be mistaken as mandatory paperwork. Mitigation: document it as lightweight and optional for small changes.
- Risk: More lifecycle language could imply runtime maturity. Mitigation: keep the durable-team implementation plan marked as draft and state that this change does not implement runtime features.

## Migration Plan

1. Create OpenSpec proposal, design, spec, and tasks for the documentation alignment.
2. Update the PMI reference map and product lifecycle documents.
3. Add the Codex platform project canvas pair.
4. Update the white paper and durable-team plan with value-delivery and release-slice language.
5. Run OpenSpec and document governance checks.
6. Commit locally and ask for release approval before publishing to GitLab.

## Open Questions

- Whether future work should turn performance-domain outcome checks into checker-backed templates.
- Whether downstream project templates should include a blank adoption canvas by default or only document it as an optional artifact.
