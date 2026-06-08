# Change: Implement Stop-Slop/Caveman Response Density R4

## Why
The active implementation plan requires a project-level response-density checker, guarded rewrite runtime, and R4 smoke receipt evidence before this lane can claim runtime readiness.

## What Changes
- Add a deterministic Stop-Slop/Caveman checker for slop markers, response density, and protected conversation/technical spans.
- Add a guarded runtime with `analyze`, `rewrite --dry-run`, protected `rewrite --apply --operator-confirmation`, and bounded `smoke-record`.
- Add a fail-closed R4 smoke receipt checker that accepts honest blocked receipts but counts only safe smoke-tested receipts as positive R4 evidence.
- Register tests, aggregate guard wiring, safety registry entries, and implementation-plan evidence.

## Impact
- No user-level install, hook, MCP shrink, or always-on compression is enabled.
- R4 smoke evidence remains bounded to explicit receipt files and safe help/status/dry-run rewrite actions.
- Remote publication remains out of scope without explicit approval.
