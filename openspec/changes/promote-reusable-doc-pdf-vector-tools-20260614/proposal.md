# Change: Promote Reusable Document, PDF, and Vector Tools

## Why

`D:/project` has working Poppler, document quality, and local vector/retrieval helpers that are useful beyond one tender workspace. Keeping reusable executors only inside the tender project encourages accidental copying of project-specific paths, data rules, guard rules, and output roots.

## What Changes

- Add a reusable tool surface under `tools/user_level_document_tools/`.
- Promote Poppler discovery and PDF inspection/rendering helpers.
- Promote the document pipeline core as parameterized scripts for Word COM, Acrobat, Poppler, and contact-sheet checks.
- Add a generic vector/retrieval framework plus sanitized legacy adapters that require explicit consumer config.
- Cache portable Poppler locally under ignored `.local/` for observation, not as tracked source.

## Non-Goals

- Do not move `D:/project` data, filled configs, permissions, source authority, output paths, or guard rules.
- Do not delete or replace existing `D:/project` scripts during the observation period.
- Do not track third-party Poppler binaries as repository source.
- Do not push GitLab or GitHub.
