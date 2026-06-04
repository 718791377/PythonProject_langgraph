# Design

## Decision

Keep the current visible canary markers unchanged for user-visible assistant responses. Change only where the literal marker text is stored:

- English startup summary: ASCII-only prose and Unicode codepoint notation.
- Chinese startup summary: the literal visible marker text remains present.
- Checkers/tests: construct marker values from codepoints, not duplicated literals.

## Enforcement

`check_context_retention_canary_surface.py` becomes path-aware:

- The English startup summary must be ASCII-only and must not contain the literal marker text or mojibake variants.
- The Chinese startup summary must contain both literal marker values and must remain UTF-8-clean.
- Other active files must not contain literal marker text, legacy ASCII marker tokens, or mojibake variants.

`check_startup_instruction_mojibake.py` keeps response/session diagnostics unchanged: canonical user-visible responses still use the visible marker pair, legacy ASCII tokens remain stale evidence, and mojibake variants fail closed.

## Verification

Run the two targeted unittest modules, both checker commands, OpenSpec validation/guard, precommit review, local gate, and local MR review before local main integration.
