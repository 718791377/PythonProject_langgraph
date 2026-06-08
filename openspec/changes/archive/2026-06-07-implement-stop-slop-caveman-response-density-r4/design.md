# Design

## Boundary
This change implements repo-local code only. It does not install upstream Stop-Slop or Caveman, mutate user-level Codex configuration, or enable global compression.

## Checker
`tools/check_stop_slop_caveman_response_density.py` produces JSON diagnostics for supplied sample files or text. It maps source-inspired rules into deterministic local findings:

- throat-clearing and filler phrases
- em dash usage
- formulaic binary contrasts
- vague declaratives
- weak density and repetitive rhythm

The checker also reports protected spans so runtime rewrites can preserve code fences, inline code, URLs, paths, CLI arguments, schema keys, OpenSpec/evidence/blocker tokens, `Routing trace`, and `Updated Plan`.

## Runtime
`tools/stop_slop_caveman_runtime.py` wraps the checker:

- `analyze` reports diagnostics only.
- `rewrite --dry-run` returns a shorter proposal and never writes.
- `rewrite --apply` requires `--operator-confirmation` and an explicit file target.
- `smoke-record` writes a sanitized R4 receipt. Missing R3 install receipt writes blocked evidence, not positive smoke evidence.

## R4 receipt checker
`tools/check_stop_slop_caveman_smoke_receipts.py` accepts blocked/non-installed receipts as honest evidence and rejects positive receipts that contain writes, live actions, sensitive actions, raw private paths, or secrets.
