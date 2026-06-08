# Verification Report

Change: `ascii-only-english-startup-canary-source`
Date: 2026-06-04

## Scope

This report verifies the split startup canary source rule:

- English startup summary remains ASCII-only and uses Unicode codepoint indirection.
- Chinese startup summary remains the literal visible marker source.
- Canary placement, startup mojibake, and bilingual document-pair checkers enforce the split.

## Commands run

- `python test\check_context_retention_canary_surface.test.py` - verifies canary-surface checker regression behavior.
  - Result: pass, 16 tests.
- `python test\check_startup_instruction_mojibake.test.py` - verifies startup mojibake checker regression behavior.
  - Result: pass, 10 tests.
- `python test\check_document_pair_policy.test.py` - verifies bilingual document-pair policy regression behavior.
  - Result: pass, 6 tests.
- `python tools\check_context_retention_canary_surface.py --root . --json` - checks repository canary placement and response-evidence rules.
  - Result: pass, `ok: true`.
- `python tools\check_startup_instruction_mojibake.py --root . --json` - checks startup and instruction authority surfaces for mojibake.
  - Result: pass, `ok: true`.
- `python tools\check_document_pair_policy.py --root . --json` - checks changed bilingual authority documents for pairing and ASCII English primaries.
  - Result: pass, `ok: true`.
- `openspec validate ascii-only-english-startup-canary-source --type change --strict --json` - validates the active OpenSpec change structure before archive.
  - Result: pass, `valid: true`.

## Archive decision

The stable English and Chinese canary-surface specs were updated as complete stable specs before archive. The active change delta spec remained an OpenSpec delta artifact, so archive used `openspec archive ascii-only-english-startup-canary-source --skip-specs -y` to skip automatic spec overwrite and preserve the manually synchronized stable spec files.

Archive path: `openspec/changes/archive/2026-06-04-ascii-only-english-startup-canary-source/`.

Next gates after archive:

- `python .\tools\run_openspec_guard.py --root .` - runs the repository OpenSpec and governance guard sequence.
- `python .\tools\check_precommit_update_archive.py --root . --json` - checks precommit update/archive readiness before committing.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- feature commit
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs the local merge-simulation and branch review gate.
- project local-flow helper for local `main` integration and remote-publication gate stop
