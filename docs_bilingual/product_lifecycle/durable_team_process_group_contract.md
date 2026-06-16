---
doc_id: durable_team_process_group_contract
lang: en
canonical: docs_bilingual/product_lifecycle/durable_team_process_group_contract.md
translation_of: null
doc_class: product_lifecycle
status: draft
---

# Durable-Team Process-Group Contract

## Purpose

This contract defines the process-group execution grammar for durable-team documentation refreshes and future release slices. It tells maintainers when to write Inputs, Tools and Techniques, and Outputs, and what each category must contain.

This document owns the I/T/O contract for durable-team documentation delivery. It does not replace PMI references, lifecycle tailoring rules, OpenSpec specs, or runtime evidence.

## PMI Framing

- PMBOK 8 is the primary value-delivery and tailoring overlay for current planning.
- Process Groups provide execution grammar: Initiating, Planning, Executing, Monitoring and Controlling, and Closing.
- PMBOK 6 I/T/O vocabulary is supporting vocabulary only where execution artifacts are produced.
- Agile guidance supports exploratory, MVP, feedback-driven, and hybrid slices.
- Program, portfolio, and PMO references inform sequencing, value balance, governance services, and reusable standards.

## Top-Level Contract

Every durable-team refresh or implementation slice SHALL identify Inputs, Tools and Techniques, and Outputs when it affects execution, release gates, durable-lane selection, runtime behavior, documentation authority, validation, rollback, or closeout.

Documentation-only slices still use this contract when they change future delivery rules or acceptance criteria. Completing this contract is not runtime implementation evidence.

## Contract Inputs

| Input | Required when |
| --- | --- |
| Current source synthesis from `fresh-source-lifecycle-whitepaper-pmi-refresh-20260616` | The slice cites Business Management, PMP, lifecycle, white paper, or research refresh evidence. |
| Current white paper | The slice changes narrative, platform purpose, lifecycle framing, or adoption logic. |
| Current governance research note | The slice changes runtime capability criteria, layer decomposition, or governance evidence. |
| 10-to-12 bridge and lifecycle maps | The slice maps runtime findings into product/business lifecycle zones. |
| Inventory/count authority docs | The slice repeats or changes architecture counts. |
| Implementation plan and playbook | The slice changes release order, file scope, validation, or rollback. |
| OpenSpec artifacts | The slice changes repository structure, specs, governance, or acceptance behavior. |
| Local validation state | The slice is preparing commit, archive, local-main integration, or remote publication. |

## Tools And Techniques

| Technique | Use |
| --- | --- |
| Synthesis review | Check whether a claim is source-refresh-derived or already stable repository authority. |
| Authority split review | Keep white paper, research note, inventory maps, PMI map, and OpenSpec responsibilities separate. |
| 10-layer to 12-layer landing analysis | Decide which lifecycle layer receives a runtime finding. |
| Tailoring review | Choose full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, or hybrid governance. |
| Local-main-first discipline | Plan local validation, local MR review, local integration, rollback, and remote-publication stop point. |
| Tracked-doc-only validation | Verify claims against committed docs and allowed summaries, not ignored raw cache. |
| Variance and change-impact review | Decide whether the slice can close, must return to design/build, or must open a follow-up change. |

## Outputs

| Output | Meaning |
| --- | --- |
| Strategic narrative delta | White paper, MRD, or North Star update with evidence boundary. |
| Capability/governance delta | Research note, bridge, implementation plan, or spec update. |
| Delivery matrix row | UR-to-file coverage and non-goals. |
| Traceability entry | Source-family to authority mapping and evidence boundary. |
| Tailoring decision | Full, whole-project lightweight, phase-local lightweight, module-level lightweight, or hybrid. |
| Validation evidence | Commands, reports, changed paths, and residual risk. |
| Closeout evidence | OpenSpec archive, stable spec sync, rollback reference, local-main status, and lessons learned. |

## Process Group Table

| Process group | Inputs | Tools and Techniques | Outputs | Durable-team gate question | UR coverage |
| --- | --- | --- | --- | --- | --- |
| Initiating | User request, current source evidence boundary, affected authority docs, non-goals | Value framing, scope split, authority split review, OpenSpec proposal | Change proposal, success criteria, constraints, no-runtime boundary | Is this documentation, runtime, or remote-publication work? | UR1, UR2, UR3, UR4 |
| Planning | Proposal, design context, traceability chain, inventory maps, PMI map, lifecycle tailoring rules | 10-to-12 landing analysis, tailoring review, release and rollback planning, validation planning | Design, tasks, implementation plan, expected proof surfaces | Is the plan frozen and are execution slices independent? | UR1, UR3, UR4 |
| Executing | Approved tasks, file ownership, current branch, proof-surface targets | Main-session integration, bounded expert fan-out, tracked-doc-only edits, local checks | Updated docs, specs, registry, proof surfaces, changed-path list | Are writes isolated and are raw caches excluded? | UR1, UR2, UR3, UR4 |
| Monitoring and Controlling | Diff, validation output, risk list, checker results, subagent fan-in | Variance review, risk/change impact assessment, rework decision, OpenSpec strict validation | Pass/fail evidence, fix list, return decision or closeout readiness | Does evidence prove the claim without over-claiming runtime status? | UR2, UR3, UR4 |
| Closing | Verification report, completed tasks, stable spec delta, archive checklist, local integration plan | Archive, stable spec sync, local-main-first gates, lessons learned, rollback record | Archived change, verification report, commit, local-main state, follow-up queue | What was updated, what remains draft, and where does remote approval stop? | UR1, UR2, UR3, UR4 |

## Tailoring Outcomes

| Outcome | Use when | Whole project or local? |
| --- | --- | --- |
| Full architecture | The scope changes reusable orchestration, trust, durable state, release safety, cross-project templates, launcher policy, CI gates, or runtime behavior. | Full for affected architecture layers; not necessarily every downstream business module. |
| Whole-project lightweight | The entire project is private, reversible, low-risk, local-only, and has no shared runtime, sensitive data, release promise, or external users. | Whole project may stay lightweight. |
| Phase-local lightweight | Discovery, metrics, growth, or retrospective work is bounded inside a larger governed effort. | Only the phase stays lightweight. |
| Module-level lightweight | A bounded doc, helper, research note, or spike does not change entrypoints, state, secrets, CI, releases, or dependencies. | Only that module stays lightweight. |
| Hybrid | Uncertainty remains high but later delivery may affect production, users, trust, revenue, compliance, runtime behavior, or release safety. | Start light; expand affected layers before release. |

## Durable-Team Specific Contract Rules

- No process-group step may treat raw extraction cache as tracked authority.
- No process-group step may claim the white paper and research note have merged.
- Any execution artifact that uses both layer models must name which model is authoritative for which claim.
- Every closeout must identify what was updated, what remains draft, and what remains future-state.
- Durable-team launch still requires a frozen plan plus at least two mostly independent execution slices, or a stabilization threshold with blocking issues.
- LangGraph or `native_omx` runtime apply mode requires explicit slice permission and current evidence; documentation contracts alone do not authorize apply mode.

## Handoff To Implementation And Release

Use this contract before updating implementation plans, playbooks, or OpenSpec changes that affect execution. A release slice should copy only the relevant I/T/O rows and tailoring decision instead of duplicating this whole document.

### Inputs

- delivery matrix row;
- source traceability entry;
- authority split decision;
- affected OpenSpec requirement.

### Tools And Techniques

- slice planning;
- validation command selection;
- rollback planning;
- branch and publication gate review.

### Outputs

- implementable tasks;
- validation report;
- archive-ready OpenSpec package;
- explicit stop point at the remote-publication gate unless remote action is approved.

## Non-Goals

- This contract does not reproduce PMI source content.
- This contract does not prove runtime implementation.
- This contract does not replace OpenSpec validation.
- This contract does not authorize remote publication.
