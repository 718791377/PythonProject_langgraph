---
doc_id: reusable_document_pdf_vector_tools_promotion_plan
lang: en
status: active
doc_class: implementation_plan
created_at: 2026-06-14
updated_at: 2026-06-14
---

# Reusable Document PDF Vector Tools Promotion Plan

## Summary

This active Stage A plan authorizes the local implementation slice that promotes reusable Poppler PDF helpers, document pipeline core scripts, and local vector/retrieval framework helpers into `D:\PythonProject_langgraph`.

Remote publication remains out of scope unless a later user message explicitly names GitLab or GitHub publication.

## Current Status

<!-- CURRENT_STATUS_START -->

- Stage A governance package records the reusable-tool boundary before the code/tooling slice is reviewed.
- The implementation slice must keep consumer project data, real configs, permissions, source authority, output paths, and guard rules outside the promoted reusable framework.
- The feature branch is `promote-reusable-doc-pdf-vector-tools-20260614`.
- The expected local pause point is local `main` integration followed by the remote-publication approval gate.

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
- [ ] Review reusable PDF/Poppler helper promotion.
- [ ] Review reusable document pipeline core script promotion.
- [ ] Review generic vector/retrieval framework promotion.
- [ ] Verify tests, OpenSpec guard, local CI, and local MR review before local `main` integration.
- [ ] Stop at the remote-publication approval gate after local integration.

<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->

- Pending implementation evidence: feature branch `promote-reusable-doc-pdf-vector-tools-20260614` will record local gate and local MR review evidence before local integration.

<!-- EVIDENCE_INDEX_END -->

## Validation Plan

- Targeted reusable-tool regression test: `python test/user_level_document_tools.test.py` - verifies path boundaries and vector toolkit smoke behavior.
- OpenSpec change validation: `openspec validate promote-reusable-doc-pdf-vector-tools-20260614 --strict --json` - verifies the active change package.
- Repository guard: `python tools/run_openspec_guard.py --root . --tool codex --json` - verifies OpenSpec and repository policy surfaces.
- Local CI gate: `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1 -StepTimeoutSeconds 1500 -Json` - verifies the shared local/remote CI gate.
- Local MR review: `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json` - verifies clean local merge review before integration.
