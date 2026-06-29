---
doc_id: ppt_visual_review_tool_plan
lang: en
doc_class: implementation_plan
status: active
zh_cn_path: docs_bilingual/implementation_plans/ppt_visual_review_tool_plan.zh-CN.md
change: add-ppt-visual-review-tool-20260629
base_ref: 7c18096e5d0835d504dc6d38875ef88c2e2bd4e8
stage: frozen-governance-package
---

# PPT Visual Review Tool Implementation Plan

> Operator note: execute this as a two-package local-main-first rollout. Stage A is this governance plan plus registry entry. Stage B is the runtime tool, OpenSpec delta, tests, local gates, and local `main` integration. Remote publication is out of scope unless explicitly authorized later.

## Goal

Deploy a reusable local/offline tool that lets an operator review rendered PPT slide PNGs visually, draw rectangular regions of interest (ROI), record modification suggestions, and export normalized JSON evidence that downstream PPT remediation tools can consume.

The tool does **not** mutate PPTX files. It creates a sidecar review session from already-rendered slide images and writes review artifacts under a consumer-owned output directory such as `.local/`, `intermediate/`, or `result/`.

## Current external-option review

- Microsoft PowerPoint add-ins support task-pane and content add-ins across Windows, Mac, iPad, and browser, but they require an Office add-in runtime and are designed to operate inside/alongside PowerPoint rather than as a portable evidence artifact for local pipelines. See Microsoft Learn, "PowerPoint add-ins": https://learn.microsoft.com/en-us/office/dev/add-ins/powerpoint/powerpoint-add-ins
- Label Studio has a mature image bounding-box model through `RectangleLabels`; its result coordinates are designed around image ROI export. It is suitable for server/team annotation workflows, but it introduces a larger service/configuration surface than this local stdlib-only repository needs. See https://labelstud.io/tags/rectanglelabels.html
- VGG Image Annotator (VIA) demonstrates that a small, browser-only annotation tool can run offline from local HTML and export/import JSON annotations. This is the closest architectural precedent for the selected approach. See https://www.robots.ox.ac.uk/~vgg/software/via/
- CVAT and similar annotation platforms are strong for large-scale computer-vision labeling, but are heavier than the acceptance target: this repository needs a disposable operator review sidecar, not a persistent annotation platform.

Decision: implement a repository-owned, stdlib-only static HTML/JS viewer plus Python session builder. Reuse the proven "offline browser + JSON ROI" pattern, but keep schema, guardrails, and output boundaries aligned with the shared document-tool pipeline.

## Stage A: governance freeze package

Files:

- `docs_bilingual/implementation_plans/ppt_visual_review_tool_plan.md` - English canonical implementation plan for the PPT visual review tool.
- `docs_bilingual/implementation_plans/ppt_visual_review_tool_plan.zh-CN.md` - Chinese companion implementation plan for the PPT visual review tool.
- `docs_bilingual/docs_registry.yaml` - Repository document registry entry for the bilingual plan pair.

Acceptance:

1. Plan explicitly freezes:
   - input boundary: rendered slide PNGs and optional PPTX provenance only;
   - output boundary: consumer-owned output directory only;
   - non-goal: no PPTX mutation, no remote service, no Office add-in deployment;
   - handoff schema: normalized comments with slide number, severity, category, ROI, comment, suggested fix, status, author, timestamp.
2. Registry contains the bilingual plan pair.
3. Stage A branch is docs-only and `docs_bilingual/` first.
4. Local validation runs:
   - `python .\tools\check_document_pair_policy.py --root . --base-ref main --json` - Validates bilingual Markdown pairing for the Stage A diff.
   - `python .\tools\check_precommit_update_archive.py --root . --json` - Validates pre-commit update/archive readiness.
   - `python .\tools\run_openspec_guard.py --root . --tool codex --json` - Runs repository OpenSpec and governance guard checks.
5. Stage A is committed and integrated into local `main` using `tools/complete_local_flow_to_remote_gate.py --stage governance-confirmation --implementation-plan docs_bilingual/implementation_plans/ppt_visual_review_tool_plan.md --execute`.
6. The Stage B receipt/claim records the Stage A commit, `governance_package_merged_to_local_main=true`, and the current user's implementation confirmation before non-document implementation is integrated.

## Stage B: runtime implementation package

Files:

- `tools/user_level_document_tools/viewers/ppt_review/ppt_review_tool.py` - Python CLI/session builder and comment normalizer.
- `tools/user_level_document_tools/viewers/ppt_review/__init__.py` - Package marker for the PPT review viewer module.
- `tools/user_level_document_tools/viewers/ppt_review/__main__.py` - Module entrypoint for running the review tool with python -m.
- `tools/user_level_document_tools/viewers/ppt_review/static/ppt_review_viewer.html` - Offline browser UI shell for slide review.
- `tools/user_level_document_tools/viewers/ppt_review/static/app.js` - Offline viewer interaction and JSON import/export logic.
- `tools/user_level_document_tools/viewers/ppt_review/static/styles.css` - Offline viewer styling.
- `tools/user_level_document_tools/viewers/ppt_review/README.md` - Operator usage notes for the PPT review tool.
- `tools/user_level_document_tools/viewers/__init__.py` - Shared viewer package marker.
- `test/user_level_document_tools.test.py` - Regression test surface for shared document tools.
- `openspec/changes/add-ppt-visual-review-tool-20260629/` - OpenSpec change package for the Stage B runtime work.

Runtime behavior:

1. Python CLI builds a review session:
   - `--slides-dir` points to rendered slide PNGs;
   - `--input` records optional PPTX provenance only;
   - `--output-dir` receives copied slide images, `session_manifest.json`, `comments.json`, `review_report.json`, `review_report.html`, and static viewer assets;
   - `--comments-json` imports existing review comments or viewer-export JSON.
2. Static viewer:
   - loads local PNG files;
   - draws normalized rectangle ROI overlays;
   - records severity/category/comment/suggested-fix;
   - imports and exports the same JSON schema accepted by the Python CLI.
3. Schema and validation:
   - severities: `info`, `low`, `medium`, `high`, `critical`;
   - compatibility aliases may normalize `minor -> low`, `major -> high`, `warning -> medium`, `error -> high`;
   - ROI uses normalized `x`, `y`, `w`, `h` floats in `[0, 1]`;
   - invalid or out-of-bounds imported ROI fails closed rather than being silently clamped.
4. Output safety:
   - default behavior rejects output directories inside tracked shared-tool source;
   - `--allow-source-output` exists only for intentional test fixtures.
5. Local/offline constraint:
   - no remote API calls;
   - no heavyweight dependency beyond Python stdlib and browser-native HTML/CSS/JS;
   - no mutation of source PPTX.

## Stage B tests

Focused tests must cover:

- required files and static assets exist;
- no consumer/project absolute paths in tracked shared-tool source;
- CLI `--help`;
- manifest/session generation from PNGs;
- comment normalization and bad ROI rejection;
- viewer export schema accepted by backend;
- viewer severity options match backend severity contract;
- viewer import has fail-closed ROI validation rather than silent clamping;
- CLI success path with `--comments-json`;
- CLI error path for missing slide directory or malformed comment JSON;
- static viewer assets are copied into generated sessions.

## Validation and integration

Run from the Stage B worktree after the Stage A governance package is on local `main` and the implementation receipt is confirmed:

```powershell
python test\user_level_document_tools.test.py -k ppt_review
python -m py_compile tools\user_level_document_tools\viewers\ppt_review\ppt_review_tool.py
openspec validate add-ppt-visual-review-tool-20260629 --strict
python .\tools\run_openspec_guard.py --root .
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Root . -StepTimeoutSeconds 3600 -Json
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json
```

After validation, integrate locally:

```powershell
python .\tools\complete_local_flow_to_remote_gate.py --root D:\PythonProject_langgraph --worktree D:\PythonProject_langgraph\.worktrees\add-ppt-visual-review-tool-20260629 --branch add-ppt-visual-review-tool-20260629 --stage implementation --implementation-plan docs_bilingual/implementation_plans/ppt_visual_review_tool_plan.md --local-gate-step-timeout-seconds 3600 --execute
```

Stop at the remote-publication gate.

## Collaboration plan

- Leader owns Stage A governance freeze, Stage B fan-in, verification, commit, local-main integration, and remote-publication boundary.
- Researcher role reviews existing solutions and confirms the selected local/offline pattern.
- Test-engineer/verifier roles review schema round-trip and gate evidence where thread capacity allows.
- Durable/persistent execution is eligible after Stage A because Stage B has at least two slices: runtime/static viewer and tests/OpenSpec/gates. If platform thread limits prevent additional workers, record main-session takeover and retain existing expert findings as review evidence.

## Current status

<!-- CURRENT_STATUS_START -->
- Stage A governance plan is being frozen on branch `docs/add-ppt-visual-review-tool-plan-20260629`.
- Stage B implementation already has a worktree at `.worktrees/add-ppt-visual-review-tool-20260629` and must be rebased onto the Stage A local `main` commit before final integration.
- Remote publication is not authorized.
<!-- CURRENT_STATUS_END -->

## Task backlog

<!-- TASK_BACKLOG_START -->
- Stage A: validate the bilingual plan pair and registry update, commit the docs-only package, and integrate it into local `main`.
- Stage B: rebase the runtime branch onto the Stage A local `main` commit and record implementation confirmation in the receipt/claim.
- Stage B: repair expert-identified issues: BOM-free OpenSpec delta files, backend/viewer schema alignment, fail-closed ROI import, source-output guard, and missing tests.
- Stage B: run focused tests, OpenSpec validation, OpenSpec guard, local gate, local MR review, then integrate into local `main`.
<!-- TASK_BACKLOG_END -->

## Evidence index

<!-- EVIDENCE_INDEX_START -->
- `docs_bilingual/docs_registry.yaml` - Repository document registry entry for the bilingual plan pair.
- `docs_bilingual/implementation_plans/ppt_visual_review_tool_plan.md` - English canonical implementation plan for the PPT visual review tool.
- `docs_bilingual/implementation_plans/ppt_visual_review_tool_plan.zh-CN.md` - Chinese companion implementation plan for the PPT visual review tool.
- `test/user_level_document_tools.test.py` - Regression test surface for shared document tools.
<!-- EVIDENCE_INDEX_END -->
