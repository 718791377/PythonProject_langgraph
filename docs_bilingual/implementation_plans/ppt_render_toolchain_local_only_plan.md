---
doc_id: ppt_render_toolchain_local_only_plan
lang: en
doc_class: implementation_plan
status: active
canonical_path: docs_bilingual/implementation_plans/ppt_render_toolchain_local_only_plan.md
zh_cn_path: docs_bilingual/implementation_plans/ppt_render_toolchain_local_only_plan.zh-CN.md
---
# PPT Render Toolchain Local-Only Plan

## Purpose

Freeze the repository-local governance package for the shared PPT authoring, PPTX-to-PDF/PNG rendering, and visual QA toolchain needed by guarded consumer projects such as `D:\project`.

The runtime objective is to keep all repository-managed PPT render tooling under `D:\PythonProject_langgraph`, use explicit executable paths and process-scoped environment only, and avoid system PATH, user PATH, machine PATH, or global pip mirror mutation.

## Stage A Boundary

Stage A is this bilingual implementation plan plus its `docs_bilingual/docs_registry.yaml` entry. It must land on local `main` before Stage B non-document implementation is accepted by local MR review.

Stage A must not add executable toolchain helpers, tests, binary installers, local `.local/` evidence, or consumer-project output files.

## Stage B Scope

Stage B may add shared source under `tools/user_level_document_tools/ppt_tools/`, update shared document-tool configuration examples and READMEs, and extend `test/user_level_document_tools.test.py`.

Stage B must keep local binary tools, local renderer configs, live smoke decks, package inventory, and render evidence out of tracked source. Those artifacts belong under ignored local paths such as `D:\PythonProject_langgraph\.local\ppt_render_tools`.

## Toolchain Requirements

Stage B must provide dependency-free probes and status markers that can report the actual host state for:

- Python package availability, including `pdf2image`, `python-pptx`, COM support packages, Aspose.Slides, Pillow, NumPy, OpenCV, python-docx, and openpyxl.
- PowerPoint COM readiness, including interactive-session state, `PowerPoint.Application` creation, PPTX creation, export, cleanup, and leaked-process checks.
- PPTX-to-PDF/PNG rendering through `auto`, `powerpoint`, `soffice`, or `aspose` engines.
- Visual QA status values: `visual_qa:pass`, `visual_qa:degraded`, `visual_qa:blocked`, `visual_qa:manual_required`, and `visual_qa:not_applicable`.

## Safety Requirements

Stage B must not mutate permanent environment state. Source, examples, and tests must avoid `setx`, user or machine PATH registry edits, and code paths that write `HKCU\Environment`, `HKLM`, or machine-level environment variables.

If PowerPoint COM is blocked by a non-interactive desktop or an error such as `0x80070520`, Stage B must report that as blocked or fallback evidence. It must not claim PowerPoint COM render success unless the COM probe succeeds.

Aspose.Slides is a fallback renderer unless a valid license is configured. Evaluation watermark evidence must be classified as degraded or manual-required when no clean renderer is available.

## Stage B Verification Plan

Stage B must run focused tests for the user-level document tools, OpenSpec guard, local gate, local MR review, and live smoke evidence where the host has usable local renderers.

Expected evidence includes:

- focused unit test output for `test/user_level_document_tools.test.py`;
- `python .\tools\run_openspec_guard.py --root .`;
- `.\tools\ci\local_gate.ps1 -Root .` with a sufficient step timeout;
- `.\tools\ci\local_mr_review.ps1 -Root . -Base main -Head HEAD`;
- capability and render-smoke JSON evidence under ignored `.local/` paths.

## Local Integration And Publication Boundary

Stage A and Stage B use local-main-first integration. Passing local gates authorizes local `main` integration only. It does not authorize GitLab push, GitLab MR creation or merge, GitHub sync, remote ref deletion, or any remote publication action.

## Current Status

<!-- CURRENT_STATUS_START -->
- Stage A is frozen in this plan and will be merged to local `main` before Stage B implementation confirmation.
- Stage B implementation is expected to add shared tracked source only; runtime binaries and smoke evidence remain local ignored artifacts.
- Remote publication is not authorized.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Stage A: add this bilingual implementation plan and docs registry entry, validate, commit, merge to local `main`, and stop before remote publication.
- Stage B: add PPT render toolchain helpers, examples, docs, tests, local-only runtime evidence, local gate, local MR review, local `main` integration, and stop before remote publication.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Stage A planned evidence: this implementation plan pair, docs registry entry, pre-commit update/archive check, OpenSpec guard, local commit, rollback ref, local-main integration receipt, and completed claim.
- Stage B planned evidence: tracked helper/test/doc commit, package inventory JSON, capability probe JSON, PowerPoint COM probe JSON, smoke render JSON, focused tests, OpenSpec guard, local gate, local MR review, rollback ref, completed claim, and cleanup record.
<!-- EVIDENCE_INDEX_END -->
