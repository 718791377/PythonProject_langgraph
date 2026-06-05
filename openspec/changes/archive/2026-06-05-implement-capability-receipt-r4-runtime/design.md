# Design: R4 Capability Receipt Runtime Governance

The implementation extends the existing deterministic `user_level_receipt_governance` helper rather than adding a new runtime runner. The helper remains read-only: it loads JSON receipts, validates required fields, emits sanitized hash-first summaries, and reports that it does not mutate user-level state, run external tools, or read browser data.

R4 support is represented by a new smoke receipt contract. A valid smoke receipt must identify the tool/lane, declare `runtime_stage` as R4 or `smoke-tested`, point to prior install receipt evidence, use a bounded read-only smoke type (`help`, `version`, `status`, `safe-discovery`, or `read-only`), show a passing smoke result, include timeout release evidence, carry rollback readiness plus a rollback pointer, and pass redaction checks for command transcript evidence. Any write/live marker fails closed.

Rollback evidence is represented by a separate receipt validation command. It validates dry-run/apply receipt fields and requires explicit operator authorization for apply receipts, while still not executing rollback commands. This gives later runtime lanes a reusable receipt format for rollback executor evidence without allowing this slice to mutate user-level runtime state.
