# Document Pipeline Core

Reusable Word COM, Acrobat, Poppler, and contact-sheet helpers parameterized for consumer projects.

## Runtime confirmation

Use `scripts/configure_doc_pipeline.ps1` to create a local-only
`config/doc_pipeline/doc_pipeline_config.json` in the current checkout or
consumer project. That real config is intentionally ignored in this repository;
the tracked template remains `../config/doc_pipeline_config.example.json`.

For this repository's live confirmation, pass the Poppler bin directory under:

```text
.local/user_level_document_tools/poppler-25.07.0-0/poppler-25.07.0/Library/bin
```

Then run `scripts/detect_tools.ps1` and `scripts/test_poppler_access.ps1`.
Reports are written under `.local/user_level_document_tools/doc_quality_reports/`
and are not committed.

## PPT render helpers

PPTX-specific capability and render probes live in `../ppt_tools/`. The document-pipeline visual renderer still owns generic PDF raster evidence; PPT helpers call or classify that evidence when a PPTX has first been converted to PDF/PNG.
