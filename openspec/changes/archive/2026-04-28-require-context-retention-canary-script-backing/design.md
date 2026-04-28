## Overview

This change converts a prompt-only safety reminder into an executable repository guard. It keeps the canary prompt project-local and startup-summary-owned, while making the recovery and safety-boundary rules inspectable by scripts.

## Design Decisions

### Registry-first safety backing

`tools/safety_rule_script_backing_registry.json` records each registered safety rule. Each implemented rule must declare:

- `id` - stable kebab-case rule identifier.
- `owner_level` - `system`, `user`, or `project`.
- `status` - `implemented`, `planned`, or `tracked_gap`.
- `prompt_reminders` - repository-relative documentation paths that explain the rule.
- `script_controls` - repository-relative executable controls.
- `guard_steps` - OpenSpec guard step names when the control is run by the aggregate guard.

### Aggregate checker

`tools/check_safety_rule_script_backing.py` fails closed when:

- the registry is missing or invalid JSON
- a registered implemented rule has no prompt reminder
- a registered implemented rule has no script control
- a referenced path is missing
- a declared guard step is not referenced by `tools/run_openspec_guard.py`
- a non-implemented rule lacks tracked-gap text

### Canary recovery check

`tools/check_context_retention_canary_surface.py` already verifies that the literal canary prompt appears only in the startup summary pair. This change adds a check that each startup summary's recovery action mentions `AGENTS.md`.

That keeps `AGENTS.md` as a recovery reread target without making it a canary prompt source.

### Guard integration

`tools/run_openspec_guard.py` runs the aggregate checker in both JSON and text modes after the canary surface checker and before worktree hygiene.

## Compatibility

The change is additive. Existing callers of `tools/run_openspec_guard.py` receive one additional guard step. The new checker is read-only and does not mutate repository state.

## Risks

- The initial registry is intentionally small. Future safety rules must be registered as they are formalized.
- A missing prompt reminder or renamed checker can now fail CI, which is desired for safety-critical rules.

## Alternatives Considered

- Prompt-only documentation: rejected because it fails when context is lost.
- Adding the canary prompt to `AGENTS.md`: rejected because `AGENTS.md` is a recovery authority surface, not the literal canary prompt source.
- User-level wrapper injection: rejected because it would bloat launcher payloads and mix project-local prompts into user-level runtime surfaces.
