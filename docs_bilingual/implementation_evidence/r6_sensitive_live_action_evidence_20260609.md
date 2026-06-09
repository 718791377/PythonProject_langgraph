# R6 Sensitive Live Action Evidence - 2026-06-09

## Summary

- Package: R6 sensitive live-action support and Stop-Slop/Caveman live execution.
- Priority order preserved: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
- Runtime support added: `tools/r6_live_runtime.py run --mode live-action --env-file <local-env> --proof-receipt <redacted-proof-json>`.
- Safety correction: Browser/WXWork/Harness `live-action` cannot become `live-executed` from environment targets alone; a redacted external execution proof receipt is required.
- Stop-Slop/Caveman result: `live-executed` with side effect family `user_level_install`.
- Browser/WXWork/Harness result in this environment: still fail-closed, meaning the runtime refuses to mark a sensitive action as accepted when proof is missing, with `blocked` meaning the receipt records an unmet gate instead of successful live execution because no real target/proof input was present.
- Remote publication mutated: `false`.

## Stop-Slop/Caveman Live Execution

- Lane: `stop-slop-caveman-response-density-runtime`.
- Mode: `user-level-install`.
- Checker status: valid R6 receipt.
- User-level installation was written only below the selected isolated user-level root.
- Native Codex protection is now enforced: install roots containing native `codex`, `codex-raw`, or `codex-ohmy` launchers are rejected before writing.
- Redacted evidence hashes:
  - receipt path hash: `0dd315d03e0311c8`
  - target env hash: `482fbdffc289f365`
  - install root hash: `16a2ea60066dd693`
  - installed path hash: `6b9311abd8fc030f`
  - wrapper path hash: `4e8866e0019bfa51`
  - env file hash: `8b3dac5c257dc058`

## Remaining Sensitive Live Actions

The following lanes were attempted through `live-action`, which means the runtime path for externally visible browser, message, or harness side effects, but correctly remained `blocked`, meaning the receipt recorded an unmet execution gate, because real targets and redacted proof receipts were missing:

- `user-level-browser-cli-adapter-boundary` - browser CLI adapter boundary lane that requires allowlisted browser-action proof before live execution can be accepted.
- `user-level-cli-anything-wxwork-cli-governance` - WXWork CLI governance lane that requires redacted external-message proof before live execution can be accepted.
- `codex-harnesses-governance` - harness governance lane that requires guarded harness-job proof before live execution can be accepted.

Required proof before any of those lanes can be accepted as `live-executed`:

- Browser proof must show an allowlisted browser action happened and raw browser data was not stored.
- WXWork proof must show an external message was sent while retaining only message hash evidence, not body or raw recipient.
- Harness proof must show read/write guards, isolated worktree, job state, changed-path report, no Codex takeover, and timeout/cleanup evidence.

## Verification Commands

- `python test\r6_live_runtime.test.py -v` - verifies the R6 runtime unit behavior for live-ready, live-action, install, and Spec Kit modes.
- `python test\check_r6_live_runtime_receipts.test.py -v` - verifies receipt-checker acceptance and rejection cases for R6 runtime evidence.
- `python tools\r6_live_runtime.py run --root . --lane browser-cli-adapter --mode live-action --json` - demonstrates that browser live-action remains blocked without required redacted proof.
- `python tools\r6_live_runtime.py run-all --root . --json` - regenerates the default safe R6 receipt set for all governed lanes.
- `python tools\check_r6_live_runtime_receipts.py --root . --receipt-dir .omx\r6-live-runtime\receipts --require-coverage --max-age-hours 24 --json` - checks recent receipt coverage across all R6 lanes.
