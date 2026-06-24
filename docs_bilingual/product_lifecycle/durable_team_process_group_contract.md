---
doc_id: durable_team_process_group_contract
lang: en
doc_class: product_lifecycle
status: draft
canonical_path: docs_bilingual/product_lifecycle/durable_team_process_group_contract.md
zh_cn_path: docs_bilingual/product_lifecycle/durable_team_process_group_contract.zh-CN.md
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

## I/T/O Terminology And Applicability Checklist

`Inputs / Tools and Techniques / Outputs`, `Inputs / Tools & Techniques / Outputs`, and the equivalent Chinese labels in the zh-CN companion are equivalent labels for this corpus. New English tables SHOULD prefer `Inputs / Tools and Techniques / Outputs`; audits MAY match `Tools & Techniques` as an abbreviation.

| Document or surface | I/T/O requirement | Reason |
| --- | --- | --- |
| `product_business_document_lifecycle.*` | Required at each lifecycle layer. | It is the 0-11 / 12-layer execution grammar authority. |
| `codex_durable_team_platform_build_lifecycle.*` | Required at each platform-build layer. | It turns the general lifecycle into the Codex platform build flow. |
| `codex_platform_inventory_map.*` and `one_person_company_inventory_map.*` | Required as inventory-level summaries and process gates. | They own architecture count authority and must show how counts enter execution. |
| `pmi_project_management_reference_map.*` and `lifecycle_tailoring_rules.*` | Required for PMI overlay and tailoring decisions. | They decide full, lightweight, phase-local, module-level, or hybrid governance. |
| `durable_team_process_group_contract.*` | Required and canonical. | This file owns the durable-team process-group contract. |
| `durable_team_source_traceability.*` and `ten_to_twelve_layer_bridge.*` | Required for handoff sections that drive execution. | They connect source evidence and 10-layer runtime findings to 12-layer work. |
| `fresh_source_reading_evidence.*` and `business_management_source_synthesis.*` | Not required for every section; required only when they hand off to execution. | They are evidence boundary and synthesis surfaces, not delivery procedures. |
| White paper, research note, MRD, North Star, implementation plan, playbook, and OpenSpec specs | Required when a section describes execution, release, validation, rollout, or closeout. | Narrative sections may delegate to this contract; execution sections must be inspectable. |

## Contract Inputs

| Input | Required when |
| --- | --- |
| Current source synthesis from `one-person-company-pmi-refresh-stageb-20260619` | The slice cites Business Management, PMP, lifecycle, white paper, or research refresh evidence. |
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

## One-Person-Company Execution Contract Addendum

One-person-company execution-facing sections use the same process-group grammar as durable-team refreshes. A lightweight business loop may compress the artifact set, but it still names Inputs, Tools and Techniques, and Outputs for the affected layer, phase, or module. The contract is local to the risk surface: expand the layer carrying customer, revenue, trust, support, compliance, release, or governed-agent risk first; expand the whole project only when coupling becomes systemic.

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
