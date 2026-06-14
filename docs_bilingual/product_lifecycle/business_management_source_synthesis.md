# Business Management Source Library Synthesis

This document summarizes repository-relevant lessons from the fresh extraction run over the ignored local source roots `D:/PythonProject_langgraph/Business Management` and `D:/PythonProject_langgraph/PMP`. It is a synthesis layer for `docs_bilingual/product_lifecycle/`. It does not replace the source books, and it does not reproduce long copyrighted passages.

## Fresh Extraction Scope

This refresh is grounded in the ignored artifacts under `.omx/state/langgraph/extraction/fresh-source-lifecycle-whitepaper-pmi-refresh-20260614/` freshly regenerated at `2026-06-14T10:48:53Z` with run ID `fresh-source-lifecycle-whitepaper-pmi-refresh-20260614`. These artifacts are evidence for this refresh, not a substitute for the source files and not a reusable conclusion cache.

- Manifest: `fresh_source_manifest.json`
- Per-unit extraction log: `fresh_source_items.jsonl`
- Compact rollup: `fresh_source_synthesis.json`
- Extractor entrypoint: `fresh_extract_sources.py`

All 54 recorded sources completed with status `ok`.

## Coverage Inventory

### Aggregate coverage

| Family | Sources | PDFs / pages | EPUBs / spine items | Markdown / full-text files | Total read units | Extracted text chars | Blank units | Low-text units |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Business Management | 31 | 22 / 6,245 | 7 / 304 | 2 / 2 | 6,551 | 14,161,228 | 642 | 832 |
| PMP | 23 | 9 / 3,035 | 2 / 58 | 12 / 12 | 3,105 | 4,330,816 | 392 | 758 |
| **Total** | **54** | **31 / 9,280** | **9 / 362** | **14 / 14** | **9,656** | **18,492,044** | **1,034** | **1,590** |

### Intake method by format

| Format | Recorded count | Unit of coverage | Extraction method | Practical interpretation |
| --- | ---: | --- | --- | --- |
| PDF | 31 files | Page | `pypdf` page extraction with PyMuPDF fallback when needed | Suitable for page-count evidence, low-text-page tracking, and scanned/image-heavy caveats |
| EPUB | 9 files | OPF spine item | `ebooklib` spine iteration plus HTML/XHTML text extraction | Suitable for chapter/spine coverage without flattening the original reading order |
| Markdown | 14 files | Full file | Full UTF-8 text read | Suitable for exact architecture inventories, headings, and repository-local terminology |

### Coverage caveats worth preserving

- Low-text review is part of coverage accounting, not proof of missing reading. Many low-text units are covers, blanks, diagrams, scans, or image-dominant pages.
- `Business Management/Escaping the build trap.pdf` failed `pypdf` at file level and succeeded through the PyMuPDF fallback; the manifest records this as source `S0010`.
- The highest low-text concentration sits in a few scanned or image-heavy PDFs, especially `Business Management/Lean Analytics.pdf` (439 pages, 388 low-text), `PMP/Agile Practice Guide Chinese companion PDF` (184 pages, 183 low-text), `PMP/PMBOK 6 Chinese companion PDF` (812 pages, 301 low-text), and `PMP/Portfolio Management Standard Chinese companion PDF` (142 pages, 141 low-text).
- Because this document is a synthesis artifact, it records counts, methods, and interpretations rather than reproducing raw extraction text.

## Target Architecture Inventory Evidence

The two local Markdown architecture notes are the controlling source for the requested target inventories because they were read as full UTF-8 files and preserve explicit section headings.

| Target | Controlling source | Fresh-read evidence | Inventory carried into lifecycle docs |
| --- | --- | --- | --- |
| Codex CLI personal production durable team | `Architecture note 1 (Codex CLI personal production durable team).md` | 10,424 chars; headings include `1 trunk-layer matrix`, `2 virtual-department matrix`, `3 matrix of 24 responsibility domains`, `4 matrix of 18 cross-cutting modules`, `5 system of 48 core documents`, `6 twelve governed AI agents` | 12 trunk layers, 4 virtual departments, 24 responsibility domains, 18 cross-cutting modules, 48 core documents, 12 governed AI agents, 12 recommended books |
| Personal production one-person company | `Architecture note 2 (personal production one-person company).md` | 18,544 chars; headings include `2 twelve-layer trunk`, `3 five virtual departments`, `4 thirty responsibility domains`, `5 twenty cross-cutting modules`, `6 system of 60 core documents`, `7 fifteen governed AI agents`, `11 minimum runnable MVP` | 12 trunk layers, 5 virtual departments, 30 responsibility domains, 20 cross-cutting modules, 60 core documents, 15 governed AI agents, 15 recommended books, 12 minimal startup documents |

These two notes define the repository-specific inventory counts. The book and PMP sources explain how to operate those inventories, tailor them, and keep them lightweight.

## Source-Family Mapping

### Business Management family -> operating model and architecture synthesis

| Source cluster | Representative fresh-read sources | Main lifecycle contribution |
| --- | --- | --- |
| Strategy, positioning, and business design | `Good strategy, bad strategy.pdf`, `Company of One` (PDF + EPUB), `The E-Myth Revisited.pdf`, `Working Backwards.pdf`, `Obviously Awesome.pdf`, `Traction.epub` | Diagnosis, guiding policy, intentional smallness, positioning, channel choice, PR/FAQ-style thinking, and operating-system design |
| Product discovery and product operations | `INSPIRED.pdf`, `Continuous Discovery Habits.pdf`, `Deploy Empathy.epub`, `Escaping the build trap.pdf`, `Product Operations` (PDF + EPUB), `The Lean Startup.pdf`, `Crossing the Chasm, 3rd Edition.pdf` | Opportunity discovery, interview loops, product risk framing, product-ops enablement, MVP discipline, and adoption-segment sequencing |
| Metrics, management cadence, and scaling | `Lean Analytics.pdf`, `Measure What Matters.pdf`, `High Output Management.pdf`, `Scaling People.epub` | OMTM and stage metrics, OKR alignment, managerial leverage, planning cadence, and scaling discipline for a one-person or agent-assisted system |
| Architecture, technical boundaries, and delivery design | `Clean Architecture.pdf`, `Clean Architecture - Chinese edition.pdf`, `Designing Data-Intensive Applications.pdf`, `Accelerate.pdf`, `Team Topologies.epub`, `Secure by Design` (PDF + EPUB), `The Staff Engineer's Path.pdf`, `Shape Up.pdf` | Dependency direction, data and reliability concerns, team/API boundaries, secure design constraints, staff-level judgment, shaping, appetite, and delivery guardrails |
| Repository-specific architecture inventory | `Architecture note 1 (Codex CLI personal production durable team).md`, `Architecture note 2 (personal production one-person company).md` | Exact target inventories, local terminology, and the bridge between generic management advice and repository policy |

### PMP family -> delivery governance and tailoring overlay

| Source cluster | Representative fresh-read sources | Main lifecycle contribution |
| --- | --- | --- |
| Core standards and process control | `PMBOK 8th Edition.pdf`, `PMBOK 7 Chinese edition.pdf`, `PMBOK 6 Chinese edition.pdf`, `Process groups _ a practice guide.pdf`, `Process Groups Practice Guide Chinese edition.pdf` | Process-group discipline, outcome framing, tailoring decisions, control loops, risk/change review, and closure evidence |
| Agile, program, portfolio, and PMO overlays | `The Agile practice guide.pdf`, `The Standard for Program Management - Fifth Edition.epub`, `The Standard for Portfolio Management-Fourth Edition.pdf`, `Project Management Offices  a Practice Guide.epub` | Hybrid/agile delivery, program sequencing, portfolio prioritization, governance operating model, and PMO capability mapping |
| PMBOK 8 / AI-era interpretation notes | 12 Markdown notes under `PMP/PMP_MD/`, plus the Joshua Parrott translation note | Repository-friendly interpretation of PMBOK 8 principles, focus areas, PMO evolution, tailoring, and AI-era project leadership |

## Evidence-Backed Reading Highlights

### Architecture-heavy Business Management sources

The fresh extraction totals show where architecture guidance is most concentrated:

| Source | Format | Coverage | Why it matters here |
| --- | --- | --- | --- |
| `Designing Data-Intensive Applications.pdf` | PDF | 613 pages | Strongest architecture signal in the corpus; supports state, data, reliability, and integration reasoning |
| `Secure by Design.pdf` | PDF | 400 pages | Security invariants and secure-by-default lifecycle constraints |
| `Secure by Design.epub` | EPUB | 31 spine items | EPUB companion with the same theme for spine-level verification |
| `Clean Architecture.pdf` | PDF | 429 pages | Boundary and dependency-direction discipline |
| `Clean Architecture - Chinese edition.pdf` | PDF | 380 pages | Chinese companion for the same architecture concepts |
| `Team Topologies.epub` | EPUB | 29 spine items | Cognitive-load and interaction-mode mapping for human/agent operating design |

### Delivery-heavy PMP sources

The PMP family contributes most of the explicit delivery and governance coverage:

| Source | Format | Coverage | Why it matters here |
| --- | --- | --- | --- |
| `PMBOK 8th Edition.pdf` | PDF | 401 pages | Highest delivery signal; useful for current PMI lifecycle reframing |
| `Process groups _ a practice guide.pdf` | PDF | 390 pages | Canonical initiating/planning/executing/monitoring-closing overlay |
| `Process Groups Practice Guide Chinese edition.pdf` | PDF | 409 pages | Chinese process-groups companion with strong governance counts |
| `The Standard for Program Management - Fifth Edition.epub` | EPUB | 16 spine items | Program-level sequencing and benefits realization |
| `PMBOK 7 Chinese edition.pdf` | PDF | 369 pages | Chinese PMBOK 7 performance-domain support |
| `Project Management Offices  a Practice Guide.epub` | EPUB | 42 spine items | Strongest PMO/organization signal for governance-operating-model synthesis |

## Repository Interpretation

1. The two Markdown architecture notes supply the explicit target inventories; they should remain the authoritative count source for lifecycle tailoring.
2. Business Management books supply the operating principles behind intentional scope, discovery, architecture boundaries, delivery appetite, and one-person-company mechanisms.
3. PMP standards supply execution discipline, governance vocabulary, tailoring rules, and close-out expectations, but they do not replace product or architecture judgment.
4. The repository should keep using counts, headings, and source-family mappings as evidence surfaces instead of copying long source text into tracked docs.
5. When future lifecycle docs mention architecture inventories, PMO overlays, or tailoring logic, they should cite the relevant source family first: local Markdown for exact counts, Business Management for operating principles, PMP for delivery governance.

## Lifecycle Implication

For `D:/PythonProject_langgraph`, the fresh-read evidence supports a split model:

- **Platform architecture and operating-system truth** come from the two local architecture notes plus Business Management sources on architecture, discovery, governance, and intentional smallness.
- **Execution discipline and delivery control** come from PMP standards and PMBOK-8-era interpretation notes.
- **Tracked repository docs** should continue to summarize source-backed implications, not preserve raw extraction text.
