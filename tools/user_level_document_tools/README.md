# User-Level Document Tooling

Reusable executors and discovery helpers promoted from `<source-project-root>` for cross-project use.

Tracked source contains portable scripts, examples, and tests. Consumer projects keep their own data, configuration, permissions, source-authority rules, output roots, and guards.

## Layout

- `pdf_tools/` - Poppler discovery, access checks, PDF information, and rendering helpers.
- `doc_pipeline/` - Word COM, Acrobat, Poppler, and contact-sheet quality-check helpers.
- `vector_tools/` - generic manifest, health, and retrieval framework plus sanitized legacy adapters.
- `config/` - example-only configuration templates.

## Local Poppler cache

For live runtime confirmation in this shared repository, portable Poppler is
stored under the ignored local path:

```text
.local/user_level_document_tools/poppler-25.07.0-0/
```

It is intentionally not tracked because existing evidence-intake requirements keep third-party binaries as local install dependencies rather than repository source.

Consumer projects may reuse these scripts, but they keep their own filled
configs, source-authority rules, outputs, vector indexes, embedding caches, and
runtime reports. The shared repository only owns the reusable executors and
example configuration.
