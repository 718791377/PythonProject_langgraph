## 1. Tests first

- [x] 1.1 Add response/session canary tests for missing, mojibake, canonical, and tool-output filtering cases.
- [x] 1.2 Add startup mojibake response/session tests for corrupted canary evidence.

## 2. Checker implementation

- [x] 2.1 Extend `check_context_retention_canary_surface.py` with `--response-text`, `--response-file`, `--session-jsonl`, `--turn-id`, and `--latest-assistant` evidence modes.
- [x] 2.2 Extend `check_startup_instruction_mojibake.py` with matching response/session evidence mode for canary mojibake diagnostics.
- [x] 2.3 Ensure session parsing filters non-user-visible context sources and does not treat startup-summary tool output as satisfying the canary.

## 3. Governance updates

- [x] 3.1 Update the startup summary pair to describe the canary purpose, UTF-8 source rule, and recovery behavior without turning it into a response gate.
- [x] 3.2 Update implementation/governance references so checker behavior is parameterized diagnostic evidence, not prompt injection.
- [x] 3.3 Update the OpenSpec delta/spec text for session evidence diagnostics.

## 4. Verification

- [x] 4.1 Run targeted checker unit tests.
- [x] 4.2 Run OpenSpec validation for this change.
- [x] 4.3 Run repository OpenSpec guard.
