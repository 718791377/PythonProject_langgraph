# Proposal: Enforce Startup Canary Mojibake Detection

## Why

The startup-summary canary text is correctly stored in UTF-8, but a Windows launcher or payload-injection boundary can still present a mojibake variant of the same prompt in the live session. When that happens, `AGENTS.md` remains clean on disk, yet the operator sees corrupted startup instructions and the assistant may copy the corrupted canary back into responses.

The current canary checker validates placement and duplication, but it does not fail when the startup summary, `AGENTS.md`, or another active text surface contains a mojibake variant of the canary. This leaves a gap between the canonical files and the runtime instruction surface.

## What Changes

- Clarify `AGENTS.md` recovery guidance: if injected startup instructions are garbled, treat the UTF-8 startup summaries as canonical and do not copy corrupted sentinel text.
- Extend `tools/check_context_retention_canary_surface.py` to detect generated mojibake variants of the start/end canary markers in active repository text.
- Add tests proving the checker fails when `AGENTS.md` or startup summaries contain a mojibake canary variant.
- Keep the literal canary prompt confined to the startup summary pair.

## Capabilities

### Modified Capabilities

- `codex-user-level-context-retention-canary-surface`: add mojibake variant detection to the executable canary surface check.

## Impact

- Affects `AGENTS.md`, canary checker, checker tests, and OpenSpec change artifacts.
- Does not change the literal canary prompt source or duplicate it into `AGENTS.md`.
- Does not change launcher runtime behavior directly; it adds fail-closed repository evidence so launcher/payload corruption is not silently accepted.

## Validation

- `python test/check_context_retention_canary_surface.test.py` - runs canary-surface regression tests.
- `python tools/check_context_retention_canary_surface.py --root . --json` - validates active canary placement and mojibake detection.
- `openspec validate --all` - validates the active OpenSpec change and stable specs.
