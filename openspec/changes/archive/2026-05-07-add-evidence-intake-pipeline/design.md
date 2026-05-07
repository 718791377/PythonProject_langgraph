# Design: Evidence Intake Pipeline

## Constraints

- Local reference source directories may be ignored by Git and may contain private or copyrighted material.
- The workflow may summarize extraction quality, but it must not commit copyrighted book text, private document text, or saved article bodies.
- The extraction tool must be useful on a cold-start machine with partial dependencies: it should degrade gracefully when OCR or PDF rendering tools are missing.
- The workflow must distinguish extraction evidence from semantic understanding. Generated text proves that text was extracted; it does not prove that every page was understood.

## Tool Shape

Add `tools/evidence_intake_pipeline.py`, a Python tool with these modes:

- `extract`: scan a local reference root, extract PDF page text and HTML visible text, and write ignored local evidence files.
- `inventory-tools`: inspect another local project for reusable document/PDF/HTML/OCR helper candidates without copying them.
- `check`: validate an existing evidence output directory and fail when manifests are missing or structurally invalid.

The default output directory should be `.local/evidence/local_reference/`, which is ignored by Git. The tool should allow explicit `--source` and `--output` for local experiments.

## PDF Processing

The first implementation uses available local tools in this order:

1. `pdftotext` page extraction or whole-document extraction when Poppler is available.
2. `pdftoppm` page rendering when `--render-pages` or `--ocr-pages` is requested.
3. `tesseract` OCR when `--ocr-pages` is requested and the OCR command is available.
4. A clear `needs_ocr` marker when no usable PDF text extraction or OCR path exists.

For each page record, store:

- `page_number`: the 1-based PDF page number used for traceable citation.
- `method`: the extraction or OCR method used for that page record.
- `text_output_path`: the local ignored text-evidence file for the page.
- `render_output_path`: the optional local ignored rendered image file for the page.
- `ocr_output_path`: the optional local ignored OCR text file for the page.
- `ocr_average_confidence`: the optional OCR confidence metric reported by the OCR adapter.
- `chars`: the extracted character count used as a minimum completeness signal.
- `replacement_chars`: the count of Unicode replacement characters used as an encoding-noise signal.
- `control_chars`: the count of unexpected control characters used as a corruption signal.
- `cjk_chars`: the count of CJK characters used to understand Chinese-text presence.
- `latin_chars`: the count of Latin characters used to understand English-text presence.
- `noise_ratio`: the normalized noise score used to flag suspicious extraction results.
- `quality`: the coarse quality bucket used for reviewer triage.
- `needs_review`: the boolean review flag used to prevent unsupported reading claims.

OCR is not a required dependency for this change. Future adapters can add stronger OCR engines without changing the evidence contract.

## HTML Processing

The HTML extractor uses Python standard-library parsing first. It removes `script`, `style`, `noscript`, and SVG content, then records visible text. It captures basic metadata such as title, likely author/date tokens when visible, body character count, and noise metrics.

The extractor deliberately calls the result `extracted_text`, not `verified_body`, until a reviewer confirms that it is the correct article body.

## Tool Inventory

The inventory mode scans candidate directories and reports:

- reusable scripts that mention PDF, HTML, OCR, extraction, Poppler, PyPDF, docx, xlsx, or vector ingestion;
- local third-party tool directories such as Poppler;
- whether the candidate is source code, generated output, cached dependency, binary, or project-specific artifact;
- recommendation: `consider-adapter`, `do-not-copy`, `third-party-install-instead`, or `project-specific-only`.

No files are copied by the inventory mode.

## Knowledge-Base Boundary

The platform knowledge base and project knowledge bases are separate by default. Platform evidence may describe reusable tool behavior and governance facts. Project evidence may describe project-specific business facts, project state, and project retrieval indexes.

Cross-project data must use explicit export packages or read-only references with provenance. A cross-project record should include `source_project`, `source_path`, `source_commit`, `source_timestamp`, `scope`, `classification`, and `provenance`.

## Tool Maintenance Boundary

The source truth for platform tools remains this repository. User-level helpers are install artifacts and entrypoints. Consumer projects should call tools through `CODEX_TEAM_HOME`, `CODEX_TEAM_RUNTIME`, explicit script paths, or helper shims instead of copying source code.

Third-party binaries, OCR models, extracted full text, embedding indexes, vector database caches, and project business data must remain in ignored local runtime locations.

## Adapter Direction

The first implementation can remain a single file. Later changes may split adapters into:

- `tools/evidence_adapters/poppler_adapter.py`: the Poppler adapter for `pdftotext`, `pdfinfo`, and `pdftoppm`.
- `tools/evidence_adapters/tesseract_adapter.py`: the Tesseract adapter for OCR text and confidence data.
- `tools/evidence_adapters/paddleocr_adapter.py`: the PaddleOCR adapter for Chinese and mixed-language OCR.
- `tools/evidence_adapters/html_visible_text_adapter.py`: the HTML adapter for saved-page visible-text extraction.

## Evidence Policy

The repository may commit:

- extraction tool source;
- tests;
- a small synthetic fixture;
- summary reports that do not reproduce copyrighted or private source text.

The repository must not commit:

- ignored local reference source directories;
- extracted full text of copyrighted PDFs;
- extracted full text of saved web pages unless user explicitly confirms rights and scope;
- external third-party binaries from other projects.

## Failure Semantics

The tool should fail only on structural problems in strict `check` mode. In extraction mode, it should record per-file errors and continue, so a single unreadable PDF does not erase evidence for other files.
