## Why

The context-retention canary is intended to remain a model-visible signal that the model read, understood, and retained the repository cold-start authority. Two recent resumed sessions showed failures immediately after cold-start reading: one omitted the canary and one copied mojibake canary text from a non-UTF-8 console rendering.

The current static guard correctly keeps the literal canary prompt confined to the startup summary pair, but it does not define a checker path for user-provided response or session evidence, and the governance wording can be misread as a response gate or wrapper injection requirement.

## What Changes

- Clarify that the canary is a context-retention and correct-reading signal, not a response gate, wrapper injector, or durable-state payload.
- Require explicit UTF-8 canonical startup-summary reads before adopting canary text; terminal mojibake is diagnostic evidence only.
- Extend canary and mojibake checkers with parameterized response/session evidence modes that inspect only user-visible assistant replies and filter out tool-output/context copies.
- Update bilingual startup/governance/implementation guidance and targeted tests.

## Impact

- Affected docs: startup summary pair, context canary governance/implementation guidance, launcher/encoding governance where relevant.
- Affected scripts: `tools/check_context_retention_canary_surface.py` and `tools/check_startup_instruction_mojibake.py`.
- Affected tests: canary and mojibake checker tests.
- Non-goals: no response gate, no launcher injection of the literal canary, no duplication of the literal canary outside startup summaries, no mutation of historical session JSONL files.

## Rollout and Validation

- Rollout sequence: add failing tests, implement checker parameters, update governance docs, run targeted tests and repository guard.
- Rollback plan: revert checker/session-mode additions and documentation updates; static canary placement behavior remains as the fallback.
- Validation path: targeted unit tests, `openspec validate refine-context-canary-session-diagnostics --strict`, and `python .\tools\run_openspec_guard.py --root .`.
- Mainline classification: bounded follow-up under `codex-user-level-context-retention-canary-surface`, related to current orchestration startup governance.
