# PPT Visual Review Tool

Local/offline helper for proposing visual PPT changes from rendered slide PNGs.

## What it does

- Keeps the source `.pptx` read-only; it never edits or writes back to the deck.
- Builds a review session from slide PNG files produced by the shared PPT render helpers.
- Normalizes region comments with page number, severity, category, normalized ROI, comment text, and suggested fix.
- Writes `session_manifest.json`, `comments.json`, `review_report.json`, `review_report.html`, and a copied static browser viewer.
- Accepts review JSON exported by the static viewer through `--comments-json` and normalizes it into the backend comment schema.

## Typical use

```powershell
python tools/user_level_document_tools/viewers/ppt_review/ppt_review_tool.py `
  --input <deck.pptx> `
  --slides-dir <rendered-slide-png-dir> `
  --output-dir <local-review-output> `
  --comments-json <optional-review-comments.json> `
  --open
```

## Interactive review workflow

1. Render the source deck to slide PNG files with the shared PPT render helper.
2. Open `viewer_static/ppt_review_viewer.html` from a generated review session, or open the tracked static viewer and load the slide PNG files manually.
3. Draw rectangular findings on the slide images and fill severity, category, issue text, and suggested fix.
4. Export the viewer JSON.
5. Re-run this CLI with `--comments-json <viewer-export.json>` to normalize the comments into `comments.json` and `review_report.json`.
6. Inspect `review_report.html`; `--open` opens this generated report, not the interactive annotation viewer.

Consumer projects should place generated review sessions under ignored local output directories such as `intermediate/`, `result/`, or `.local/` according to their own guard rules. The CLI rejects output paths inside tracked `tools/user_level_document_tools` source unless `--allow-source-output` is deliberately supplied for a test fixture.

## Boundaries

- This is a review/comment sidecar, not a PPT editor.
- It is single-user local/offline in this version.
- PowerPoint native comment write-back, accounts, permissions, and multi-user collaboration are future work.
