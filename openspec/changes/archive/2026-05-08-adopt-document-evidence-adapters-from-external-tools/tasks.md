# Tasks: Adopt Document Evidence Adapters From External Tools

## 1. Artifacts

- [x] 1.1 Create proposal, design, spec, and tasks artifacts.
- [x] 1.2 Add bilingual companion artifacts for repository governance checks.

## 2. Adapter implementation

- [x] 2.1 Add `tools/evidence_adapters/` with common, Poppler, Tesseract, and HTML visible-text adapters.
- [x] 2.2 Refactor `tools/evidence_intake_pipeline.py` to call the adapters.
- [x] 2.3 Add options for explicit Poppler bin directory and environment-based discovery.
- [x] 2.4 Preserve existing manifest fields and backwards-compatible extract behavior.

## 3. Tests and validation

- [x] 3.1 Add adapter unit tests for discovery, confidence parsing, and missing-tool behavior.
- [x] 3.2 Update the local CI manifest so relevant tests run in `local_gate`.
- [x] 3.3 Run OpenSpec validation, repository guard, local gate, and `git diff --check`.
