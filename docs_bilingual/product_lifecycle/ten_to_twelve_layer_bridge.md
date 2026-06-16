---
doc_id: ten_to_twelve_layer_bridge
lang: en
canonical: docs_bilingual/product_lifecycle/ten_to_twelve_layer_bridge.md
translation_of: null
doc_class: product_lifecycle
status: draft
---

# 10-To-12 Layer Bridge

This bridge explains why the research note and the white paper remain separate and how their layer models connect.

## Relationship

- The research note uses a 10-layer runtime/governance decomposition to study what a solo-maintainable persistent team must do at execution time.
- The white paper uses the repository 12-layer product/business lifecycle to explain why the Codex CLI durable-team platform should exist and how it becomes governable.
- They should not be physically merged now because they have different audiences, review paths, and downstream references.

## Bridge Table

The table is a bridge-time aggregation. It does not replace the research note's canonical 10-layer runtime list; it groups adjacent runtime concerns so each concern can land in the appropriate 12-layer lifecycle document, owner, and gate.

| 10-layer research model | 12-layer lifecycle landing zones | Bridge rule |
| --- | --- | --- |
| Interaction and execution | Product, Execution, Operations | Convert runtime interaction capability into product promises, execution workflow, and operating runbooks |
| Team orchestration | Organization, Execution | Convert worker/leader coordination into responsibility domains, agent governance, and execution gates |
| Agent state persistence | Technical, Operations | Convert state fields into architecture contracts and operational recovery evidence |
| Task-flow persistence | Technical, Execution, Operations | Convert workflow state into plans, checkpoints, resumption rules, and runbooks |
| Memory and context | Cognitive narrative, Technical, Operations | Convert memory capability into cold-start narrative, context-store design, and retention operations |
| Retrieval and knowledge | Metrics, Technical, Growth | Convert retrieval into evidence metrics, source maps, and reusable learning loops |
| Quality/evaluation | Metrics, Execution, Retrospective | Convert evaluation into acceptance gates, regression checks, and lessons learned |
| Security/governance | Technical, Organization, Operations | Convert security constraints into trust boundaries, approvals, and operating controls |
| Observability/audit | Metrics, Execution, Operations, Retrospective | Convert observability into metric guardrails, trace evidence, and closure records |
| Control center / operator surface | Cognitive narrative, Organization, Operations | Convert control surfaces into recoverable operator workflows and authority boundaries |

## Added 12-Layer Context

The 12-layer lifecycle adds four business-facing trunks that the 10-layer runtime research does not own directly: cognitive narrative, business, market, and growth. Those trunks explain purpose, value, adoption, and learning.

## Bridge Execution Grammar

Use this process-group style whenever a 10-layer runtime finding is converted into 12-layer lifecycle work.

### Inputs

- The research-note layer, capability gap, source evidence, maturity finding, or runtime risk being bridged.
- The target lifecycle mode: Codex CLI durable-team platform or downstream one-person-company operating system.
- Fresh-source evidence boundary, inventory-count authority, affected layer owners, and current OpenSpec or delivery state.
- Constraints from security, durable state, operator authority, release safety, budget, and downstream project ownership.

### Tools And Techniques

- Bridge-time aggregation: group adjacent runtime concerns without renaming the canonical research model.
- Landing-zone allocation: choose which 12-layer lifecycle layers receive the runtime finding.
- Authority split review: keep runtime capability authority in the research note, narrative authority in the white paper, count authority in the inventory maps, PMI authority in the PMI reference map, and execution grammar in the lifecycle documents.
- Tailoring review: decide whether the result needs full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, or hybrid governance.
- I/T/O expansion: if the bridged result drives execution, expand it into Inputs, Tools and Techniques, and Outputs in the receiving lifecycle document or OpenSpec change.

### Outputs

- A named 12-layer landing zone for the runtime finding.
- Updated lifecycle, white-paper, research-note, North Star, or OpenSpec references without merging their responsibilities.
- A tailoring decision and execution grammar for the affected scope.
- Traceable evidence showing which model is being used and which document owns the result.

## Governance Rule

Use the 10-layer model when evaluating runtime capability completeness, state, orchestration, memory, auditability, and operator control. Use the 12-layer model when deciding whether the platform or a downstream one-person company has enough business, market, product, delivery, operations, and learning evidence. If a document cites both, state which model is being used and which lifecycle layer receives the result.

Count authority remains in `codex_platform_inventory_map.md` and `one_person_company_inventory_map.md`. Runtime capability authority remains in `solo_maintainable_production_persistent_team_research.md`. Narrative authority remains in `codex_cli_personal_production_durable_team_whitepaper.md`. This bridge owns only the mapping between those authorities.
