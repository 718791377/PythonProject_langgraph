---
doc_id: fresh_source_reading_evidence
lang: en
canonical: docs_bilingual/product_lifecycle/fresh_source_reading_evidence.md
translation_of: null
doc_class: product_lifecycle
status: draft
---

# Fresh Source Reading Evidence Index

This index records the current fresh-reading evidence boundary for the lifecycle, white paper, research note, North Star, and one-person-company operations refresh.

## Business Management And PMP Extraction

- Run ID: `one-person-company-pmi-refresh-stageb-20260619`
- Generated at: `2026-06-18T18:37:58Z`
- Output root: `.omx/state/langgraph/extraction/business_pmp_20260619/`
- Source roots: `D:/PythonProject_langgraph/Business Management` and `D:/PythonProject_langgraph/PMP`
- Sources: 54 total; 31 Business Management; 23 PMP
- Units: 9,656 total; 9,280 PDF pages; 362 EPUB spine items; 14 Markdown full documents
- Extracted characters: 18,492,044
- Blank units / low-text units: 1,034 / 1,590
- Status: all sources `ok`

| Family | Sources | Units | Characters | Format coverage |
| --- | ---: | ---: | ---: | --- |
| Business Management | 31 | 6,551 | 14,161,228 | 22 PDFs / 6,245 pages; 7 EPUBs / 304 spine items; 2 Markdown full files |
| PMP | 23 | 3,105 | 4,330,816 | 9 PDFs / 3,035 pages; 2 EPUBs / 58 spine items; 12 Markdown full files |

## Product Lifecycle Markdown Fresh Read

- Run ID: `one-person-company-pmi-refresh-stageb-product-lifecycle-20260619`
- Generated at: `2026-06-18T20:40:36Z`
- Source root: `docs_bilingual/product_lifecycle/`
- Markdown documents: 26
- Full-document units: 26
- Extracted characters: 310,349
- Status: all documents `ok`

## Commit Boundary

The manifest and reports may be cited by tracked docs. Raw `fresh_source_items.jsonl` and local extraction manifests are ignored local evidence and must not be committed.

## Refresh Rule

Do not update the above counts from memory or previous cache. Rerun `tools/fresh_extract_sources.py` over the local source roots, reread lifecycle Markdown when lifecycle docs are part of the input set, and update this index with the new run IDs.
