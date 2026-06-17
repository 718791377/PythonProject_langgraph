---
change_id: confirm-user-level-document-tools-runtime-20260617
status: proposed
owner: codex
created_at: 2026-06-17
---

# Design: User-Level Document Tool Runtime Confirmation

## Boundary

`D:\PythonProject_langgraph` owns the reusable implementation source for the document/PDF/vector tooling line. `D:\project` is a consumer/source-comparison project with its own guard, dirty-file state, protected source policy, project data, and runtime outputs.

The shared source boundary is:

- `tools/user_level_document_tools/pdf_tools/` - reusable Poppler and PDF helper scripts.
- `tools/user_level_document_tools/doc_pipeline/` - reusable document-processing pipeline core scripts.
- `tools/user_level_document_tools/vector_tools/` - generic local vector and retrieval framework helpers.
- `tools/user_level_document_tools/config/*.example.json` - sanitized example configuration files.
- `test/user_level_document_tools.test.py` - boundary and smoke regression test.

The local-only runtime boundary is:

- `.local/user_level_document_tools/poppler-25.07.0-0/` - ignored portable Poppler cache used for runtime confirmation.
- `.local/user_level_document_tools/doc_quality_reports/` - ignored local document-quality report output.
- `.local/user_level_document_tools/renders/` - ignored local rendering output.

The consumer-owned boundary remains outside shared source:

- filled consumer configs;
- vector indexes and embedding caches;
- source authority and protected material;
- generated deliverables and reports;
- `D:\project` guard state and unrelated dirty files.

## Confirmation Matrix

- **Shared source confirmed in Stage 1**
  - `tools/user_level_document_tools/pdf_tools/` - reusable PDF helper source.
  - `tools/user_level_document_tools/doc_pipeline/` - reusable document pipeline source.
  - `tools/user_level_document_tools/vector_tools/` - reusable vector/retrieval helper source.
  - `tools/user_level_document_tools/config/*.example.json` - sanitized config templates.
- **Local-only runtime assets, not tracked**
  - `.local/user_level_document_tools/poppler-25.07.0-0/` - local Poppler runtime cache.
  - `.local/user_level_document_tools/doc_quality_reports/` - local quality-report output.
  - `.local/user_level_document_tools/renders/` - local render output.
- **Not migrated**
  - `D:\project\config\...` real configs
  - vector indexes, embedding caches, and local vector DBs
  - protected source authority and generated outputs
- **Consumer protection**
  - `D:\project` remains guarded
  - unrelated dirty files block cleanup-by-assumption
  - Stage 2 may update live consumer docs only if no-drift evidence is gathered first

## Stage 1 Freeze

Stage 1 only freezes the confirmation plan and local integration boundary. It must not claim live runtime completion. It records the remaining Stage 2 backlog, validates OpenSpec/plan hygiene, commits the frozen plan package on a feature branch, and integrates it into local `main` through the existing local-main-first helper.

Durable team thresholds are not met during Stage 1 because the plan is still being frozen.

## Stage 2 Live Runtime

Stage 2 is the first phase allowed to make runtime fixes or cache population changes. After Stage 1 is integrated into local `main`, Stage 2 may split into three independent implementation slices:

1. Poppler/PDF local cache and access confirmation.
2. Document-pipeline PowerShell parser and runtime confirmation.
3. Vector/retrieval framework smoke and boundary confirmation.

When two or more of these slices are active from a frozen plan, durable-team or LangGraph-backed orchestration is eligible. The leader session remains responsible for fan-in, final verification, and local-main integration.

## D:\project Handling

`D:\project` currently has unrelated dirty files. Stage 2 must not overwrite or clean those files. Any consumer-side cleanup must use that repository's guard flow and must preserve project-owned `config`, `data/local_vector_db`, and `.project-runtime/local-vector-db` unless a later explicit plan changes those boundaries.

Active docs and operator guides may be updated to point to the shared LangGraph tool location, but archived OpenSpec changes and historical implementation plans should remain historical evidence.
