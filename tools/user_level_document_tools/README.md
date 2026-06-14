# User-Level Document Tooling

Reusable executors and discovery helpers promoted from `<source-project-root>` for cross-project use.

Tracked source contains portable scripts, examples, and tests. Consumer projects keep their own data, configuration, permissions, source-authority rules, output roots, and guards.

## Layout

- `pdf_tools/` - Poppler discovery, access checks, PDF information, and rendering helpers.
- `doc_pipeline/` - Word COM, Acrobat, Poppler, and contact-sheet quality-check helpers.
- `vector_tools/` - generic manifest, health, and retrieval framework plus sanitized legacy adapters.
- `config/` - example-only configuration templates.

## Local Poppler cache

For the first observation pass, portable Poppler copied from `<source-project-root>` is stored under the ignored local path:

```text
.local/user_level_document_tools/poppler-25.07.0-0/
```

It is intentionally not tracked because existing evidence-intake requirements keep third-party binaries as local install dependencies rather than repository source.
