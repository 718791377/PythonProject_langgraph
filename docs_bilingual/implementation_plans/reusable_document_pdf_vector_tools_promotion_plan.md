---
doc_id: reusable_document_pdf_vector_tools_promotion_plan
lang: en
status: active
doc_class: implementation_plan
created_at: 2026-06-14
updated_at: 2026-06-15
---

# Reusable Document PDF Vector Tools Promotion Plan

## Summary

This active Stage A plan authorizes the local implementation slice that promotes reusable Poppler PDF helpers, document pipeline core scripts, and local vector/retrieval framework helpers into `D:\PythonProject_langgraph`.

Remote publication remains out of scope unless a later user message explicitly names GitLab or GitHub publication.

## Current Status

<!-- CURRENT_STATUS_START -->

- Stage A governance package is locally integrated at `802e458eaf5b3cdbed17e2bd419c73ecba3981c3`.
- The implementation slice is locally integrated through commit `3fe2e42409f9f103bf9c727c2047f07e3493a23d`, which added the reusable tool surfaces under `tools/user_level_document_tools/`.
- Local `main` contains the implementation and later local commits; the completion audit observed pre-closure local-main head `088045b20d3e48de470970e9a165eb9f55968d24`.
- The implementation feature branch/worktree `promote-reusable-doc-pdf-vector-tools-20260614` was cleaned after guarded local-main integration, with the completed claim preserved under `.omx/session-claims/completed/`.
- Consumer project data, real configs, permissions, source authority, output paths, and guard rules remain outside the promoted reusable framework; the promoted source contains example configuration only.
- Remote publication has not been performed and remains stopped at the remote-publication approval gate.

<!-- CURRENT_STATUS_END -->

## Scope

- Add reusable Poppler/PDF helper wrappers under `tools/user_level_document_tools/pdf_tools`.
- Add reusable document pipeline core scripts under `tools/user_level_document_tools/doc_pipeline`.
- Add a generic vector/retrieval toolkit and sanitized legacy adapters under `tools/user_level_document_tools/vector_tools`.
- Add example configuration only; real consumer configuration remains consumer-owned.
- Add regression tests and CI manifest registration for path boundaries and vector toolkit smoke behavior.

## Non-Goals

- Do not move `D:\project` data, authority sources, guard rules, permission policy, generated outputs, or consumer-specific configuration.
- Do not commit third-party Poppler binaries, vector indexes, embedding caches, or private source material.
- Do not change remote refs, GitLab MRs, or GitHub mirrors without explicit remote-publication authorization.

## Task Backlog

<!-- TASK_BACKLOG_START -->

- [x] Freeze the Stage A governance boundary in this active implementation plan pair.
- [x] Review reusable PDF/Poppler helper promotion.
- [x] Review reusable document pipeline core script promotion.
- [x] Review generic vector/retrieval framework promotion.
- [x] Verify tests, OpenSpec guard, local CI, and local MR review before local `main` integration.
- [x] Stop at the remote-publication approval gate after local integration.

<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->

- Stage A governance package: `802e458eaf5b3cdbed17e2bd419c73ecba3981c3`.
- Implementation package: `3fe2e42409f9f103bf9c727c2047f07e3493a23d`.
- Promoted reusable tool root: `tools/user_level_document_tools/`, with `pdf_tools/`, `doc_pipeline/`, `vector_tools/`, and `config/*.example.json`.
- Boundary regression test: `test/user_level_document_tools.test.py`, registered in `tools/ci/ci_test_manifest.json`; it verifies required surfaces, placeholder configs, absence of consumer absolute paths, and vector toolkit smoke behavior.
- Local gate evidence: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Root . -StepTimeoutSeconds 900 -Json` returned `ok: true` on 2026-06-15.
- Local MR review evidence: `tools/ci/local_mr_review.ps1` returned `ok: true` for the implementation branch before cleanup.
- Completion/cleanup evidence: `.omx/session-claims/completed/promote-reusable-doc-pdf-vector-tools-20260614.json` records local-main integration, rollback ref `refs/backup/local-main/20260615-082051-before-promote-reusable-doc-pdf-vector-tools-20260614`, deleted local branch, removed feature worktree, and `remote_publication_performed=false`.
- D:\project guard evidence: `guard.cmd model end` and `guard.cmd verify` returned OK after the migration work, proving protected source directories did not drift during the model operation.

<!-- EVIDENCE_INDEX_END -->

## Validation Plan

- Targeted reusable-tool regression test: `python test/user_level_document_tools.test.py` - verifies path boundaries and vector toolkit smoke behavior.
- OpenSpec change validation: `openspec validate promote-reusable-doc-pdf-vector-tools-20260614 --strict --json` - verifies the active change package.
- Repository guard: `python tools/run_openspec_guard.py --root . --tool codex --json` - verifies OpenSpec and repository policy surfaces.
- Local CI gate: `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1 -StepTimeoutSeconds 1500 -Json` - verifies the shared local/remote CI gate.
- Local MR review: `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json` - verifies clean local merge review before integration.
