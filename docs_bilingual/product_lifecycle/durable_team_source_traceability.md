---
doc_id: durable_team_source_traceability
lang: en
canonical: docs_bilingual/product_lifecycle/durable_team_source_traceability.md
translation_of: null
doc_class: product_lifecycle
status: draft
---

# Durable-Team Source Traceability

## Purpose

This traceability index records how the fresh source evidence informs the durable-team document family without storing raw extracted text. It is an evidence-chain proof surface, not a source archive.

This document owns:

- source run identity;
- tracked versus ignored evidence rules;
- source-family to authority mapping;
- update triggers for white paper, research note, lifecycle documents, implementation docs, and OpenSpec specs.

## Source Run Identity

| Field | Value |
| --- | --- |
| Run ID | `one-person-company-pmi-refresh-stageb-20260619` |
| Generated at | `2026-06-18T18:37:58Z` |
| Output root | `.omx/state/langgraph/extraction/business_pmp_20260619/` |
| Total sources | 54 |
| Total reading units | 9,656 |
| Total extracted characters | 18,492,044 |
| Business Management | 31 sources / 6,551 units / 14,161,228 chars |
| PMP | 23 sources / 3,105 units / 4,330,816 chars |
| Format split | 31 PDFs / 9,280 pages; 9 EPUBs / 362 spine items; 14 Markdown full documents |
| Status | all sources `ok` |

## Evidence Boundary

| Evidence class | Git status | Allowed use |
| --- | --- | --- |
| Aggregate counts and manifests | Tracked by summary docs, may be regenerated locally | Identify coverage and freshness. |
| Synthesized mappings and conclusions | Tracked in lifecycle, matrix, and spec docs | Drive document updates and acceptance checks. |
| Raw extraction text and per-unit streams | Ignored local cache | Do not commit, quote, or require for cold-start authority. |
| Local logs and temporary caches | Ignored local cache | Use only during local refresh verification. |

Tracked docs may cite aggregate facts and paraphrased synthesis. They must not depend on the ignored raw cache as repository authority.

## Traceability Chain

```text
local source roots
  -> fresh extraction run one-person-company-pmi-refresh-stageb-20260619
  -> manifest, report, and synthesis summary
  -> fresh_source_reading_evidence.md
  -> source traceability and delivery matrix
  -> white paper / research note / lifecycle maps / implementation docs / OpenSpec specs
```

## Source-To-Authority Mapping

| Source family or synthesis bucket | Authority destination | Why it lands there | UR support |
| --- | --- | --- | --- |
| Business Management strategy, product, metrics, and operations synthesis | White paper, MRD, North Star, product lifecycle, inventory maps | These sources explain why the platform exists, who it serves, how it stays small, and how it is measured. | UR1, UR2 |
| Business Management architecture note 1 | `codex_platform_inventory_map.md` and durable-team plan | It is the count authority for the Codex platform target: 12 layers, 4 departments, 24 domains, 18 modules, 48 docs, 12 agents, 12 books. | UR1, UR3 |
| Business Management architecture note 2 | `one_person_company_inventory_map.md` and downstream handoff rules | It is the count authority for the one-person-company target: 12 layers, 5 departments, 30 domains, 20 modules, 60 docs, 15 agents, 15 books, 12 startup docs. | UR1, UR2 |
| PMP value-delivery and tailoring synthesis | PMI map, lifecycle tailoring rules, process-group contract | It supplies governance overlay, tailoring choices, and I/T/O execution grammar. | UR4 |
| Runtime capability synthesis from repository governance | Research note, 10-to-12 bridge, implementation plan | It preserves the 10-layer runtime/governance core and maps findings into the 12-layer lifecycle. | UR3 |
| Refresh-only evidence delta | Delivery matrix, traceability index, process-group contract | It proves which files were refreshed and which evidence boundary is current without over-expanding authority docs. | UR1, UR2, UR3, UR4 |

## Update Trigger Matrix

| Trigger | First update target | Follow-on targets |
| --- | --- | --- |
| Platform story, boundary, target user, or paradigm shift changes | White paper | MRD, North Star, delivery matrix, stable specs |
| Runtime capability criteria, evidence basis, or decomposition changes | Research note | 10-to-12 bridge, implementation plan, stable specs |
| Count authority changes | Inventory map for the affected target | White paper, MRD, lifecycle docs, delivery matrix |
| PMI, tailoring, or process-group authority changes | PMI map and process-group contract | Lifecycle tailoring rules, playbook, OpenSpec lifecycle spec |
| Refresh-only source evidence changes | Fresh evidence index, source traceability, delivery matrix | Authority docs only when synthesized conclusions actually change |
| Release-slice gate or implementation workflow changes | Playbook and OpenSpec specs | Implementation plan, process-group contract, validation reports |

## White Paper Versus Research Note Relationship

The white paper and research note are not physically merged.

- White paper: strategic narrative, purpose, value, adoption, and 12-layer product/business lifecycle frame.
- Research note: evidence-heavy runtime/governance canon, production capability criteria, and 10-layer runtime core.
- This traceability index records how one source refresh informs both without collapsing their responsibilities.

## 10-Layer To 12-Layer Handoff

Runtime findings remain canonical in the 10-layer research note. Lifecycle landing and planning translation happen through `ten_to_twelve_layer_bridge.md`, lifecycle maps, and OpenSpec specs. Count authority remains in the inventory maps.

When a document cites both models, it must say which model is authoritative for the claim and which 12-layer lifecycle zone receives the result.

## Citation Discipline

- Use aggregate counts, source-family names, and synthesized claims.
- Mark claims as synthesis-derived when they come from the current refresh rather than stable repository authority.
- Do not reproduce long source passages.
- Do not quote or require ignored raw extraction streams.
- If a future refresh changes counts or synthesis, rerun the extraction and update this file before updating downstream conclusions.

## Outputs To Process-Group Contract

Traceability outputs become process-group inputs when work becomes execution-facing:

### Inputs

- current source run identity;
- source-to-authority mapping;
- update trigger classification;
- affected authority documents.

### Tools And Techniques

- evidence-boundary review;
- source-family landing analysis;
- authority split review;
- tracked-doc-only validation.

### Outputs

- approved update target list;
- evidence caveats;
- downstream delivery matrix rows;
- OpenSpec or playbook updates when needed.

## Non-Goals

- This file does not store source text.
- This file does not replace source books or repository authority documents.
- This file does not prove runtime implementation.
- This file does not approve remote publication.

## Product Lifecycle Markdown Reread

This refresh also read 26 Markdown documents under `docs_bilingual/product_lifecycle/` as full documents through `one-person-company-pmi-refresh-stageb-product-lifecycle-20260619`, for 297,871 characters and all `ok` status. This proves the current lifecycle documents themselves were reread before updating the white paper, one-person-company North Star, lifecycle maps, and tailoring rules.
