---
doc_id: codex_cli_personal_production_durable_team_delivery_matrix
lang: en
canonical: docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_delivery_matrix.md
translation_of: null
doc_class: delivery_matrix
status: draft
---

# Codex CLI Personal Production Durable Team Delivery Matrix

## Purpose

This matrix records how the current durable-team refresh lands in tracked documents. It is a delivery proof surface, not a runtime proof surface. It does not replace the white paper, governance research note, inventory maps, PMI map, implementation plan, playbook, or OpenSpec specs.

This document owns:

- mapping user requirements UR1 through UR4 to refreshed files;
- showing which documents carry delivery, traceability, bridge, and process-group obligations;
- making non-goals visible so draft documents are not mistaken for running durable-team evidence.

This document does not own raw source text, runtime capability criteria, inventory counts, or release approval.

## Refresh Checkpoint

- Run ID: `fresh-source-lifecycle-whitepaper-pmi-refresh-20260616`
- Generated at: `2026-06-15T17:33:52Z`
- Output root: `.omx/state/langgraph/extraction/fresh-source-lifecycle-whitepaper-pmi-refresh-20260616/`
- Sources: 54 total; 31 Business Management; 23 PMP
- Reading units: 9,656 total; 9,280 PDF pages; 362 EPUB spine items; 14 Markdown full documents
- Extracted characters: 18,492,044
- Business Management: 31 sources / 6,551 units / 14,161,228 chars
- PMP: 23 sources / 3,105 units / 4,330,816 chars
- Status: all sources `ok`

The matrix uses tracked synthesis only. Raw extraction streams, per-unit text, local caches, and logs remain ignored local artifacts and may be absent from a clean worktree.

## UR1-UR4 Mapping

| User requirement | Delivery meaning | Required proof surface |
| --- | --- | --- |
| UR1 | Refresh product lifecycle files from Business Management and the two architecture inventory notes. | Lifecycle maps and inventory maps cite the current evidence boundary and point here for delivery coverage. |
| UR2 | Refresh white paper, North Star, and related files from Business Management plus lifecycle docs. | White paper, MRD, North Star, implementation plan, playbook, bridge, traceability, and specs share the same evidence boundary. |
| UR3 | Explain why the white paper and research note both exist and how 10 layers connect to 12 layers. | White paper and research note remain separate; `ten_to_twelve_layer_bridge.md` and this matrix record the bridge. |
| UR4 | Apply PMI process-group grammar and tailoring rules for execution-facing flow. | `durable_team_process_group_contract.md` defines Inputs / Tools and Techniques / Outputs and tailoring handoff rules. |

## Document Target Matrix

| Target document | Primary authority | Required refresh delta | Evidence boundary statement | Bridge dependency | Process-group dependency | Must not claim |
| --- | --- | --- | --- | --- | --- | --- |
| White paper | Strategic narrative and 12-layer lifecycle frame | Cite the 20260616 evidence boundary and point to proof surfaces. | Aggregate synthesis only; no raw cache dependency. | Uses 10-to-12 bridge for runtime findings. | Uses process-group contract only when a narrative result becomes delivery work. | Does not own runtime capability criteria or prove a running team. |
| Governance research note | Runtime/governance capability canon and 10-layer core | Keep 10-layer criteria separate and cite the shared refresh boundary. | Tracked synthesis can update context; raw cache remains ignored. | Supplies runtime findings to the bridge. | Uses process groups only for execution-facing recommendations. | Does not replace the white paper or lifecycle inventory. |
| Implementation plan | Multi-project implementation shape | Point release slices to delivery, traceability, and process-group proof surfaces. | Draft plan is not runtime evidence. | Converts bridge outputs into staged responsibilities. | Requires I/T/O before durable lane launch. | Does not claim full target implementation. |
| Playbook | Release-slice operating guidance | Add proof-surface checks to future slice preconditions. | Slice evidence must be tracked and reproducible. | Uses bridge docs before changing layer responsibilities. | Uses process-group contract for slice gates. | Does not authorize runtime apply without explicit slice rules. |
| Delivery matrix | Delivery proof and UR coverage | Owns UR1-UR4 mapping and target rows. | Uses aggregate run identity. | Points to bridge owner but does not replace it. | Points to contract owner but does not replace it. | Does not store sources or approve release. |
| Source traceability | Evidence chain proof | Maps source families to authority destinations. | Owns tracked versus ignored evidence rule. | Records whitepaper/research shared refresh without merging them. | Provides inputs to process-group contract. | Does not quote raw source text. |
| Process-group contract | Execution grammar proof | Defines Inputs / Tools and Techniques / Outputs for gates and slices. | Validates against tracked docs only. | Requires authority split review before bridge use. | Owns I/T/O grammar and tailoring handoff. | Does not prove runtime behavior. |
| OpenSpec specs | Acceptance authority | Require proof surfaces as stable governance obligations. | Specs cite tracked docs, not raw cache. | Stable specs mention 10-layer to 12-layer handoff. | Lifecycle spec owns process-group delivery gate mapping. | Does not replace docs or source references. |

## 12-Layer Landing Summary

| Lifecycle zone | Refresh landing rule |
| --- | --- |
| Cognitive narrative and business | White paper explains why the durable-team platform exists and why the whitepaper/research split remains useful. |
| Market, strategy, and metrics | MRD and North Star translate the refresh into target users, workload profiles, success metrics, and guardrails. |
| Product and technical | Product lifecycle, inventory maps, and implementation plan translate source synthesis into platform scope and architecture boundaries. |
| Organization and execution | Playbook, process-group contract, and OpenSpec specs convert decisions into owned release slices. |
| Growth, operations, and retrospective | Traceability and closeout records preserve learning without turning raw cache into authority. |

Runtime capability findings may land in multiple lifecycle zones. That landing does not change the research note's authority over the 10-layer runtime/governance capability core.

## Relationship Rules

- The white paper cites strategic conclusions and lifecycle implications, not raw-source criteria.
- The research note owns capability criteria, official-versus-derived distinctions, and runtime/governance decomposition.
- Bridge documents map authorities; they do not replace those authorities.
- Count authority remains in `codex_platform_inventory_map.md` and `one_person_company_inventory_map.md`.
- Source-run identity and tracked-versus-ignored evidence rules are centralized in `fresh_source_reading_evidence.md` and `durable_team_source_traceability.md`.

## Release-Slice Relevance

Future OpenSpec changes SHOULD use this matrix when they change durable-team documentation, lifecycle scope, or release-slice gates. A release slice is ready to implement only after it can name:

### Inputs

- affected user requirement labels;
- current source evidence boundary;
- authority documents and count maps;
- affected lifecycle layers and OpenSpec capabilities.

### Tools And Techniques

- authority split review;
- 10-layer to 12-layer landing analysis;
- PMI tailoring review;
- local-main-first validation planning.

### Outputs

- updated files and changed-path list;
- validation evidence;
- explicit non-goals;
- rollback and archive evidence.

## Non-Goals

- No runtime launch or durable-team apply mode.
- No remote publication approval.
- No raw source or per-unit extraction text in Git.
- No physical merge of the white paper and research note.
- No claim that draft documentation proves a production durable team is running.
