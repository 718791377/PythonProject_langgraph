---
change_id: add-ppt-visual-review-tool-20260629
status: proposed
owner: codex
created_at: 2026-06-29
---

# Proposal: Add PPT Visual Review Tool

## Why

The shared document tooling can render PPTX decks and record visual QA evidence, but operators still need a local visual way to propose slide-level and region-level PPT changes without editing protected source decks or relying on cloud collaboration products.

## What Changes

- Add a local/offline PPT visual review sidecar under `tools/user_level_document_tools/viewers/ppt_review/`.
- Build review sessions from already-rendered slide PNGs and optional source PPTX provenance.
- Normalize review comments with slide number, normalized ROI, severity, category, comment, suggested fix, and status.
- Write portable artifacts: `session_manifest.json`, `comments.json`, `review_report.json`, `review_report.html`, and static viewer assets.
- Keep generated review sessions and rendered slide PNGs outside tracked source by default.

## Out of Scope

- Editing or rewriting the source PPTX.
- Writing native PowerPoint comments back into the OOXML package.
- Multi-user collaboration, accounts, permissions, or network services.
- Bundling third-party renderers or slide images as tracked source.
- Remote publication, GitLab MR creation/merge, GitHub sync, or remote ref mutation.
