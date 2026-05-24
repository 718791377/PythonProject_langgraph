# Proposal: Enforce Startup Instruction Mojibake Scan

## Why

The canary-specific checker now catches corrupted canary markers, but the live startup payload can still preserve other mojibake text in `AGENTS.md` or the governance files that define startup/orchestration authority. A broader script-level check is needed so lossy replacement text such as `???`, Unicode replacement characters, or known legacy-encoding renderings of startup terms cannot remain in active instruction surfaces.

## What Changes

- Add `tools/check_startup_instruction_mojibake.py` to scan active startup and instruction authority surfaces with explicit UTF-8 reads.
- Fail closed on Unicode replacement characters, question-mark replacement runs, and generated legacy-encoding variants of key Chinese startup/orchestration terms.
- Wire the checker into `tools/run_openspec_guard.py` and the local CI unittest manifest.
- Add regression tests for AGENTS mojibake, governance question-mark replacement runs, and startup summary replacement characters.
- Repair the existing corrupted fan-out/write-ownership line in the Chinese orchestration activation governance document.

## Impact

- Affects startup/instruction authority checks and CI guard coverage.
- Does not duplicate the literal canary prompt outside the startup summary pair.
- Keeps the checker scoped to startup and instruction authority surfaces rather than historical memory notes or archived artifacts.

## Validation

- `python test/check_startup_instruction_mojibake.test.py` - runs the new unittest coverage for mojibake detection
- `python tools/check_startup_instruction_mojibake.py --root . --json` - checks active startup and instruction authority surfaces
- `python tools/run_openspec_guard.py --root . --json` - verifies the guard includes the new checker step
- `openspec validate --all` - validates stable specs and archived change artifacts
