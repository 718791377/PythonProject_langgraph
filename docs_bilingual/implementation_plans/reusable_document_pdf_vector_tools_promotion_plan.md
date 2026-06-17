---
doc_id: reusable_document_pdf_vector_tools_promotion_plan
lang: en
status: active
doc_class: implementation_plan
created_at: 2026-06-14
updated_at: 2026-06-17
---

# Reusable Document PDF Vector Tools Promotion Plan

## Summary

This plan is now a post-promotion confirmation plan. Stage 1 freezes the migration boundary and live-runtime confirmation backlog; Stage 2 performs the live runtime confirmation for reusable Poppler PDF helpers, document pipeline core scripts, and local vector/retrieval framework helpers in `D:\PythonProject_langgraph`.

Remote publication remains out of scope unless a later user message explicitly names GitLab or GitHub publication.

## Current Status

<!-- CURRENT_STATUS_START -->

- Stage A governance package is locally integrated at `802e458eaf5b3cdbed17e2bd419c73ecba3981c3`.
- The original implementation slice is locally integrated through commit `3fe2e42409f9f103bf9c727c2047f07e3493a23d`, which added the reusable tool surfaces under `tools/user_level_document_tools/`.
- This follow-up confirmation package freezes the remaining live-runtime backlog under OpenSpec change `confirm-user-level-document-tools-runtime-20260617`.
- Current pre-Stage-2 evidence: `.local/user_level_document_tools/poppler-25.07.0-0/` is not present yet, three `doc_pipeline` PowerShell scripts fail parser checks, and `D:\project` still contains old tool copies plus unrelated dirty files.
- Stage 1 does not claim live runtime completion; it freezes the implementation boundary and the Stage 2 verification plan.
- Consumer project data, real configs, permissions, source authority, output paths, guard rules, vector indexes, and embedding caches remain outside the promoted reusable framework.
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

- [x] Complete shared-source promotion into `tools/user_level_document_tools/`.
- [x] Freeze the original Stage A governance boundary in this active implementation plan pair.
- [x] Review reusable PDF/Poppler helper promotion, reusable document pipeline core script promotion, and generic vector/retrieval framework promotion.
- [x] Stop at the remote-publication approval gate after original local integration.
- [x] Stage 1 follow-up: open `confirm-user-level-document-tools-runtime-20260617` and freeze the confirmation/runtime-completion plan.
- [ ] Stage 1 follow-up: validate, commit, and integrate the frozen confirmation plan into local `main`.
- [ ] Stage 2 follow-up: execute Poppler runtime confirmation.
- [ ] Stage 2 follow-up: execute document-pipeline parser/runtime confirmation.
- [ ] Stage 2 follow-up: execute vector/retrieval smoke confirmation.
- [ ] Stage 2 follow-up: validate, commit, integrate into local `main`, and stop again at the remote-publication approval gate.

<!-- TASK_BACKLOG_END -->

## Stage Split

### Stage 1 Freeze

- Documentation and governance only.
- No live runtime completion claim.
- No consumer cleanup in `D:\project`.
- Output is a validated OpenSpec confirmation package and refreshed implementation plan pair integrated into local `main`.

### Stage 2 Live Runtime Backlog

- Populate the local-only Poppler cache under `.local/user_level_document_tools/poppler-25.07.0-0/`.
- Fix PowerShell parser/runtime issues in the document pipeline scripts.
- Confirm vector/retrieval smoke behavior without migrating live vector data.
- Update live shared docs/config examples and only update live `D:\project` consumer docs after no-drift evidence is gathered.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->

- Stage A governance package: `802e458eaf5b3cdbed17e2bd419c73ecba3981c3`.
- Original implementation package: `3fe2e42409f9f103bf9c727c2047f07e3493a23d`.
- Promoted reusable tool root: `tools/user_level_document_tools/`, with `pdf_tools/`, `doc_pipeline/`, `vector_tools/`, and `config/*.example.json`.
- Stage 1 follow-up change: `openspec/changes/confirm-user-level-document-tools-runtime-20260617/` records the confirmation boundary and Stage 2 runtime backlog.
- `.local/user_level_document_tools/` is runtime-local and intentionally untracked; Poppler binaries belong there for live runtime confirmation but not in Git.
- Vector data, local vector databases, embedding caches, and consumer-filled configs remain consumer-owned and were not promoted.
- Boundary regression test: `test/user_level_document_tools.test.py`, registered in `tools/ci/ci_test_manifest.json`; it verifies required surfaces, placeholder configs, absence of consumer absolute paths, and vector toolkit smoke behavior.
- Current runtime-gap evidence gathered before Stage 1: `.local/user_level_document_tools/poppler-25.07.0-0/` missing; PowerShell parser failures in `configure_doc_pipeline.ps1`, `detect_tools.ps1`, and `export_pdf_to_docx_acrobat_com.ps1`; `D:\project` dirty files `.codex/skills/comet-tweak/SKILL.md` and `.gitignore` must not be overwritten.
- Local gate evidence for the original implementation: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Root . -StepTimeoutSeconds 900 -Json` returned `ok: true` on 2026-06-15.
- Local MR review evidence for the original implementation: `tools/ci/local_mr_review.ps1` returned `ok: true` before cleanup.
- Completion/cleanup evidence for the original implementation: `.omx/session-claims/completed/promote-reusable-doc-pdf-vector-tools-20260614.json` records local-main integration, rollback ref `refs/backup/local-main/20260615-082051-before-promote-reusable-doc-pdf-vector-tools-20260614`, deleted local branch, removed feature worktree, and `remote_publication_performed=false`.
- `D:\project` guard evidence from the original migration: `guard.cmd model end` and `guard.cmd verify` returned OK after the migration work, proving protected source directories did not drift during that model operation.

<!-- EVIDENCE_INDEX_END -->

## Validation Plan

### Follow-up Confirmation Validation

Stage 1 confirmation package:

- `openspec validate confirm-user-level-document-tools-runtime-20260617 --strict --json` - verifies the follow-up OpenSpec package.
- `python tools/run_openspec_guard.py --root . --tool codex --json` - verifies repository OpenSpec policy surfaces.
- `python tools/check_document_pair_policy.py --root . --base-ref main --json` - verifies bilingual document pair hygiene for changed docs.
- `python tools/check_precommit_update_archive.py --root . --json` - verifies pre-commit update/archive readiness before committing.
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1 -StepTimeoutSeconds 1500 -Json` - verifies the shared local/remote CI gate before local integration.
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json` - verifies local merge review before local `main` integration.

Stage 2 live runtime package:

- PowerShell parser check over `tools/user_level_document_tools/**/*.ps1` - proves the document pipeline scripts are syntactically loadable.
- `tools/user_level_document_tools/*/scripts/test_poppler_access.ps1` with `.local/user_level_document_tools/poppler-25.07.0-0/poppler-25.07.0/Library/bin` - proves Poppler is accessible from this repository's local cache.
- `python -m unittest test/user_level_document_tools.test.py -v` - proves shared-tool boundary and vector JSONL smoke behavior.
- `D:\project` guard/no-drift evidence - proves consumer-side confirmation did not overwrite unrelated dirty files or protected source directories.

- Targeted reusable-tool regression test: `python test/user_level_document_tools.test.py` - verifies path boundaries and vector toolkit smoke behavior.
- OpenSpec change validation: `openspec validate promote-reusable-doc-pdf-vector-tools-20260614 --strict --json` - verifies the active change package.
- Repository guard: `python tools/run_openspec_guard.py --root . --tool codex --json` - verifies OpenSpec and repository policy surfaces.
- Local CI gate: `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1 -StepTimeoutSeconds 1500 -Json` - verifies the shared local/remote CI gate.
- Local MR review: `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json` - verifies clean local merge review before integration.
