---
change: fix-canary-ascii-marker-mojibake-20260529
status: archived
archived-with: openspec/changes/archive/2026-05-29-fix-canary-ascii-marker-mojibake-20260529
---

# Canary ASCII Marker Mojibake Design

## Goal

Make the live context-retention canary visible marker robust against Windows console and launcher/payload encoding boundaries without weakening startup-summary-only placement enforcement.

## Summary

The canonical files are clean, but the former non-ASCII marker can be corrupted when rendered through legacy code-page boundaries. The fix changes only the canonical visible marker class to ASCII while retaining the old marker values as invalid legacy evidence in checker internals.

## Decisions

1. Keep the startup summary pair as the only literal marker source.
2. Use ASCII-only canonical marker text in that pair.
3. Assemble marker constants from fragments in checker and test source so the literal marker text does not appear outside the startup summary pair.
4. Keep historical non-ASCII markers and generated legacy-encoding variants as fail-closed invalid evidence for repository surfaces and response/session diagnostics.

## Acceptance Evidence

- `python test/check_context_retention_canary_surface.test.py`
- `python test/check_startup_instruction_mojibake.test.py`
- `python tools/check_context_retention_canary_surface.py --root . --json`
- `python tools/check_startup_instruction_mojibake.py --root . --json`
- `python tools/run_openspec_guard.py --root .`
