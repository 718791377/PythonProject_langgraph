---
doc_id: evidence_intake_pipeline_workflow_plan
lang: en
canonical: docs_bilingual/implementation_plans/evidence_intake_pipeline_workflow_plan.md
zh_cn: docs_bilingual/implementation_plans/evidence_intake_pipeline_workflow_plan.zh-CN.md
doc_class: implementation_plan
status: draft
---

# Evidence Intake Pipeline Workflow Plan

## Purpose

This plan defines the repository-local evidence intake workflow used before local reference material is allowed to support knowledge-base ingestion, document governance, white papers, market requirements, implementation plans, or retrieval workflows.

`tools/evidence_intake_pipeline.py` is the evidence intake pipeline script. It scans local reference material, calls available PDF, HTML, rendering, and OCR adapters, creates evidence records, records quality metrics, and writes summaries without copying private source material into Git.

The pipeline proves extraction evidence. It does not prove semantic understanding by itself.

## Scope

The pipeline is general. It is not a domain-specific reference reader, not only a Poppler wrapper, not only an OCR tool, and not a knowledge base.

The first local runs used ignored private reference directories as validation corpora. Future projects may use their own local source directories and output directories.

## Rules

- Do not claim that every PDF page was correctly read unless a per-page evidence manifest exists.
- Do not claim that saved web-page bodies were correctly read unless a per-HTML evidence manifest exists and the extracted text has been reviewed.
- Treat extracted text as evidence of extraction, not proof of semantic understanding.
- Mark low-quality PDF pages for OCR, second-pass extraction, or human review.
- Keep full extracted reference text under ignored local directories such as `.local/evidence/local_reference/` or `.local/evidence/pmbok6_ocr/`.
- Commit only tools, tests, OpenSpec artifacts, and short non-copyrighted summaries.
- Do not commit rendered page images, OCR full text, private source PDFs, saved web pages, third-party binaries, or embedding/vector caches.

## Workflow

1. Run `python tools/evidence_intake_pipeline.py extract --source <local-reference-root> --output .local/evidence/local_reference` to scan local reference material and generate ignored local evidence files.
2. Review the generated `manifest.json`. This manifest records source files, extraction methods, output paths, character counts, and quality flags.
3. Review the generated `summary.md`. This summary identifies low-quality pages, noisy HTML extractions, and missing tools.
4. For an image-heavy PDF, run `python tools/evidence_intake_pipeline.py ocr-run --root . --pdf <local-pdf> --output .local/evidence/<run-name> --scope all --render-dpi 144 --json` to generate page-level render and OCR evidence.
5. Use only reviewed summaries to update repository documents. Do not paste full book, article, or private source text into committed files.
6. If a page or article is low quality, use OCR, second-pass extraction, or human review before making a strong reading claim.

## PDF Evidence

Each PDF page record should include page number, method, extracted character count, replacement-character count, control-character count, CJK character count, Latin character count, noise ratio, quality, and review flag.

`pdftotext` is the Poppler text-extraction command. The pipeline uses it when available to extract PDF text.

`pdfinfo` is the Poppler metadata command. The pipeline uses it when available to count PDF pages.

`pdftoppm` is the Poppler page-rendering command. The pipeline can use it when page images are needed for OCR or visual review.

`tesseract` is an optional OCR command. The Tesseract adapter should discover `tesseract` from PATH and from standard Windows install locations such as `C:\Program Files\Tesseract-OCR\tesseract.exe`. If OCR is unavailable, the pipeline must report that low-quality scanned pages need OCR rather than pretending the pages were understood.

## OCR Language Mapping

Tesseract language data is installed by language code, not always by locale code. The current local installation provides these practical mappings:

- English United Kingdom and English United States use `eng`, the generic English traineddata package.
- Simplified Chinese for mainland China uses `chi_sim`.
- Traditional Chinese for Hong Kong and Taiwan uses `chi_tra`, the generic Traditional Chinese traineddata package.
- French for France uses `fra`.
- German for Germany uses `deu`.
- Japanese for Japan uses `jpn`.
- Orientation and script detection uses `osd`.

When a source PDF is mainly Simplified Chinese with English acronyms, `eng+chi_sim` is the preferred OCR language list. Installing additional languages preserves future capability, but adding unrelated languages to a single OCR pass may reduce accuracy and increase runtime.

## HTML Evidence

Each saved HTML record should include file name, title, extracted visible text path, character count, noise ratio, and review flag.

The first implementation uses Python standard-library HTML parsing. It removes script, style, noscript, and SVG content, then records visible text. The result is called extracted text until a reviewer confirms that it is the correct article body.

## External Tool Inventory

`inventory-tools` is the read-only inventory mode. It inspects another local project directory for reusable document, PDF, HTML, or OCR helper candidates without copying them.

The inventory may identify useful ideas or candidate adapters, especially:

- Poppler binaries such as `pdftotext.exe`, which is a PDF text-extraction command-line tool.
- Existing project-specific extraction scripts, which may show patterns but should not be copied blindly.
- Cached Python dependencies, which should not be copied as source truth.
- Generated output files, which are not reusable source tools.

Any future copy or migration from another project must use a separate OpenSpec change.

## Knowledge-Base Boundaries

### Platform Knowledge Base

`D:\PythonProject_langgraph` is the platform source-truth repository for the Codex CLI personal production durable-team platform.

The platform knowledge base may store tool governance, OpenSpec rules, durable-team policy, wrapper/checker/helper rules, cross-project development lessons, and platform-level evidence manifests.

The platform knowledge base must not store private business facts from consumer projects by default.

### Project Knowledge Bases

Each consumer project owns its own project knowledge base under that project's repository or local runtime directory.

A project knowledge base may store project business material, project-level OpenSpec artifacts, project durable state, tests, release facts, project evidence, and project retrieval indexes.

Project knowledge must not be written into platform source truth by default.

### Cross-Project Data

Cross-project data must not be merged implicitly. Use explicit export packages, read-only references, provenance tracking, and a separate OpenSpec change before migration or merge.

Each cross-project data record should include `source_project`, `source_path`, `source_commit`, `source_timestamp`, `scope`, `classification`, and `provenance`.

Cross-project references are read-only by default and must not write back to the source project.

## Tool Maintenance Strategy

The source truth for durable-team platform tools is this repository, especially `D:\PythonProject_langgraph\tools\`.

User-level installs should contain only thin launchers, wrappers, command shims, helper mirrors, and configuration pointers. User-level copies are install artifacts, not source truth.

Consumer projects should call platform tools through `CODEX_TEAM_HOME`, `CODEX_TEAM_RUNTIME`, explicit script paths, or helper shims. `CODEX_TEAM_HOME` points to the platform repository root. `CODEX_TEAM_RUNTIME` points to ignored local runtime and cache storage.

Other projects should not copy platform tool source by default. If copying is required, open an OpenSpec change that defines fork scope, version ownership, and rollback strategy.

Third-party binaries, OCR models, extracted full text, embedding indexes, vector database caches, and project business data must not be committed as platform source. Store them under `.local/`, `.runtime/`, local installation directories, or other explicitly ignored runtime directories.

## Adapter Direction

The repository-maintained adapter layout is:

- `tools/evidence_adapters/poppler_adapter.py`: the Poppler adapter for `pdftotext`, `pdfinfo`, and `pdftoppm`.
- `tools/evidence_adapters/tesseract_adapter.py`: the Tesseract adapter for OCR text and confidence data.
- `tools/evidence_adapters/html_visible_text_adapter.py`: the HTML adapter for saved-page visible-text extraction.
- `tools/evidence_adapters/paddleocr_adapter.py`: a future optional PaddleOCR adapter for Chinese and mixed-language OCR if Tesseract quality is insufficient.

## Outputs

Default local outputs:

- `.local/evidence/local_reference/manifest.json`: machine-readable extraction manifest.
- `.local/evidence/local_reference/summary.md`: short human-readable extraction summary.
- `.local/evidence/local_reference/pdf_pages/`: ignored per-page PDF text evidence.
- `.local/evidence/local_reference/pdf_images/`: ignored per-page PDF image evidence, generated only when rendering or OCR is enabled.
- `.local/evidence/local_reference/pdf_ocr/`: ignored per-page OCR text evidence, generated only when OCR is enabled and available.
- `.local/evidence/local_reference/html_articles/`: ignored per-HTML extracted text evidence.
- `.local/evidence/local_reference/tool_inventory.json`: read-only inventory of external tool candidates.
- `.local/evidence/<ocr-run-name>/manifest.json`: machine-readable OCR run manifest.
- `.local/evidence/<ocr-run-name>/summary.md`: short OCR run summary.

These files are local evidence artifacts and should remain untracked unless a short sanitized summary is explicitly selected for Git.

## Validation

Run:

- `python tools/evidence_intake_pipeline.py extract --root . --source <local-reference-root> --output .local/evidence/local_reference` to generate local extraction evidence.
- `python tools/evidence_intake_pipeline.py extract --root . --source <local-reference-root> --output .local/evidence/local_reference --render-pages` to generate page image evidence.
- `python tools/evidence_intake_pipeline.py extract --root . --source <local-reference-root> --output .local/evidence/local_reference --ocr-pages` to generate page OCR evidence when OCR tools are available.
- `python tools/evidence_intake_pipeline.py ocr-run --root . --pdf <local-pdf> --output .local/evidence/<ocr-run-name> --scope all --render-dpi 144 --json` to generate traceable page-level OCR evidence for one PDF.
- `python tools/evidence_intake_pipeline.py inventory-tools --root <external-project-root> --output .local/evidence/local_reference/tool_inventory.json` to inventory external tool candidates.
- `python tools/evidence_intake_pipeline.py check --output .local/evidence/local_reference` to validate extraction evidence structure.
- `python test/evidence_intake_pipeline.test.py` and `python test/evidence_adapters.test.py` to run unit tests.
