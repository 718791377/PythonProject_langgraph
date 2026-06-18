---
doc_id: document_visual_rendering_qa_plan
doc_class: implementation_plan
status: active
change: add-document-visual-rendering-qa-20260618
base_ref: e30cd8d7448787fd086d41c135adde8ecd46698e
---

# Document Visual Rendering QA Implementation Plan

> For agentic workers: use subagent-driven-development or executing-plans to implement this plan task-by-task. Keep Stage A and Stage B as separate local-main integration packages.

**Goal:** add honest visual rendering QA for PDF/DOCX document deliverables through Poppler `pdftoppm`, Python `pdf2image`, and `soffice/libreoffice` without moving consumer state back into shared source.

**Architecture:** Stage A freezes this plan and the OpenSpec contract only. Stage B adds one orchestrator plus narrow backend helpers under the existing document pipeline scripts, with detection and tests that degrade safely when optional tools are missing.

**Tech Stack:** PowerShell pipeline scripts, Python helper scripts, OpenSpec artifacts, unittest-based repository tests, local-main-first Git workflow.

## Stage A: Freeze Plan Package

Files:

- Create `openspec/changes/add-document-visual-rendering-qa-20260618/` with proposal, design, tasks, management, and delta spec files.
- Create `docs_bilingual/implementation_plans/document_visual_rendering_qa_plan.md` and `.zh-CN.md`.
- Update `docs_bilingual/docs_registry.yaml` with the new implementation plan pair.

Steps:

1. Record dependency placement:
   - Poppler/`pdftoppm`: ignored `.local/user_level_document_tools/poppler-25.07.0-0/.../Library/bin`.
   - `pdf2image`: project virtual environment `.venv`.
   - LibreOffice/`soffice.exe`: external Windows installation, normally `C:\Program Files\LibreOffice\program\soffice.exe`.
2. Freeze backend behavior:
   - Optional backends produce `skipped` or `unavailable` evidence.
   - Strict required backends fail with structured evidence.
   - `pdf2image` is not a Poppler replacement; it depends on a Poppler backend path for reliable Windows rendering.
3. Validate Stage A:
   - `openspec validate add-document-visual-rendering-qa-20260618 --strict` - validates the Stage A OpenSpec delta contract.
   - `python .\tools\check_document_pair_policy.py --root . --base-ref main --json` - verifies bilingual document pair coverage for changed Markdown files.
   - `python .\tools\check_precommit_update_archive.py --root . --json` - checks commit readiness, archive deferral, and required registry updates.
   - `python .\tools\run_openspec_guard.py --root . --tool codex --json` - runs the full repository OpenSpec guard stack.
4. Commit Stage A with a Chinese commit subject and integrate it into local `main` through `tools/complete_local_flow_to_remote_gate.py --execute` after local gate and local MR review pass.

## Stage B: Runtime Implementation Package

Files:

- Modify `tools/user_level_document_tools/doc_pipeline/scripts/detect_tools.ps1` to report visual QA readiness for `pdftoppm`, `pdf2image`, and LibreOffice.
- Create `tools/user_level_document_tools/doc_pipeline/scripts/render_pdf_pdf2image.py` for Python `pdf2image` rendering and JSON/Markdown evidence.
- Create `tools/user_level_document_tools/doc_pipeline/scripts/export_docx_to_pdf_soffice.ps1` for LibreOffice DOCX-to-PDF conversion evidence.
- Create `tools/user_level_document_tools/doc_pipeline/scripts/visual_render_qa.ps1` as the backend orchestrator.
- Modify `tools/user_level_document_tools/doc_pipeline/scripts/run_doc_quality_check.ps1` to expose `-RunVisualQa` and optional strict backend requirements.
- Update `tools/user_level_document_tools/config/doc_pipeline_config.example.json`, `install_dependency_notes.md`, and `doc_pipeline_setup_guide.md` with sanitized, reusable visual QA guidance.
- Modify `test/user_level_document_tools.test.py` with dependency-safe behavior tests.

Tasks:

1. Write failing tests first for:
   - required new scripts exist;
   - PowerShell parser coverage includes new scripts;
   - detection JSON includes `pdftoppm`, `pdf2image`, and `LibreOffice` rows;
   - missing optional backends are reported without unhandled crashes;
   - strict backend requirements fail when a required backend is unavailable;
   - `pdftoppm` success smoke runs only when detectable.
2. Implement detection/report changes with a stable schema:
   - Detection rows use a stable schema: `backend` names the renderer, `installed` records discovery, `usable` records whether it can run now, `probe_status` stores the outcome, `path` stores the executable or package path, `version` records detected version text, and `notes` carries operator-safe diagnostics.
3. Implement `render_pdf_pdf2image.py`:
   - CLI accepts input PDF, output dir, report dir, job name, DPI, and optional Poppler path.
   - Missing package or Poppler dependency returns structured failure without traceback-only output.
4. Implement `export_docx_to_pdf_soffice.ps1`:
   - resolves `soffice.exe` from config, PATH, or common install path;
   - writes JSON/Markdown conversion evidence;
   - fails cleanly when LibreOffice is absent.
5. Implement `visual_render_qa.ps1`:
   - accepts PDF or DOCX input;
   - accepts `-Backends` and `-RequireBackends`;
   - writes visual QA JSON/Markdown summary and render artifacts under `.local/user_level_document_tools/visual_render_qa/` by default;
   - records selected, skipped, failed, and unavailable backends.
6. Wire `run_doc_quality_check.ps1` to call visual QA only when `-RunVisualQa` is supplied, preserving existing behavior by default.
7. Update setup docs and config example without introducing consumer absolute paths or tracked binary payloads.

## Validation Plan

Focused commands:

```powershell
python .\tools\ci\run_python_tests.py --root . --pattern user_level_document_tools.test.py
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\user_level_document_tools\doc_pipeline\scripts\detect_tools.ps1 -ReportDir .\.tmp\doc_tools_smoke\detect
```

Full local integration gates:

```powershell
openspec validate add-document-visual-rendering-qa-20260618 --strict
python .\tools\check_document_pair_policy.py --root . --base-ref main --json
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root . --tool codex --json
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 1500 -Json
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json
```

Environment-gated runtime smoke:

- Render a one-page PDF with `pdftoppm` when Poppler is available.
- Render the same PDF with `pdf2image` when the package imports and Poppler is available.
- Convert a minimal DOCX with LibreOffice only when `soffice.exe` is available.

## Collaboration Plan

- Stage A: leader session owns file writing and local integration; experts remain advisory because durable-team threshold is not met until the frozen plan exists.
- Stage B: use a durable/persistent team after Stage A is on local `main` because runtime and tests are two independent execution slices.
- Runtime worker owns backend scripts and orchestrator.
- Test/documentation worker owns tests, config example, and setup docs.
- Leader owns fan-in, verification, commit, local-main integration, cleanup, and remote-publication stop.

## Assumptions

- The user has confirmed optional-by-default backend behavior and strict mode for required backends.
- No remote publication is authorized.
- `D:\project` remains untouched.
- Poppler binaries, LibreOffice binaries, generated render images, and filled runtime config stay untracked.

## Current Status

<!-- CURRENT_STATUS_START -->
- Stage A: plan-freeze package is active on `add-document-visual-rendering-qa-20260618-plan`.
- Stage B: runtime implementation has not started; it must wait until Stage A is integrated into local `main`.
- Remote publication: not authorized.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Stage A: validate OpenSpec, document pairing, implementation-plan rules, local gate, and local MR review; then commit and integrate local `main`.
- Stage B runtime slice: implement detection, `pdf2image`, `soffice`, and visual QA orchestration.
- Stage B test/documentation slice: implement dependency-safe tests, setup notes, and config example updates.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- `openspec/changes/add-document-visual-rendering-qa-20260618/` - frozen Stage A OpenSpec contract.
- `test/user_level_document_tools.test.py` - Stage B focused regression surface.
- `.local/user_level_document_tools/` - ignored runtime evidence root for Stage B visual QA outputs.
<!-- EVIDENCE_INDEX_END -->
