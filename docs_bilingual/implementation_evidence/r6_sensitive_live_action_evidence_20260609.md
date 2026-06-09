# R6 Sensitive Live Action Evidence - 2026-06-09

## Summary

- Package: R6 sensitive live-action proof gate and follow-up live evidence.
- Priority order preserved: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
- Runtime support: `tools/r6_live_runtime.py run --mode live-action --env-file <local-env> --proof-receipt <redacted-proof-json>`.
- Proof-intake support: `tools/r6_live_runtime.py proof-template` writes a fail-closed proof skeleton, and `tools/r6_live_runtime.py proof-check` validates redacted proof fields without running WXWork, browser, or harness actions.
- Safety correction: Browser/WXWork/Harness `live-action` cannot become `live-executed` from environment targets alone; a redacted external execution proof receipt is required.
- Follow-up result in the current environment:
  - `user-level-browser-cli-adapter-boundary`: `live-executed` with side effect family `browser_gui`.
  - `stop-slop-caveman-response-density-runtime`: `live-executed` with side effect family `user_level_install`.
  - `user-level-cli-anything-wxwork-cli-governance` - remains `blocked`, which means the runtime recorded an unmet gate because there is no real WXWork send target and no redacted message-send proof.
  - `codex-harnesses-governance` - remains `blocked`, which means the runtime recorded an unmet gate because there is no installed/selected live harness candidate job and no guarded harness-job proof.
- Remote publication mutated: `false`.

## Term Glossary

| Term | Meaning |
| --- | --- |
| `live-executed` | Receipt mode that means a bounded live action actually ran and the receipt carries authorization, rollback, cleanup, redaction, and no-remote-mutation evidence. |
| `blocked` | Receipt mode that means the runtime entered the live path but refused to mark success because a required target, authorization, proof, rollback, or cleanup gate was missing. |
| `action_performed` | Execution proof field that means the external browser, message, harness, install, or apply action actually occurred. |
| `read_guard` | Harness proof field that means the candidate job stayed inside its allowed read scope. |
| `write_guard` | Harness proof field that means the candidate job stayed inside its allowed write scope. |
| `isolated_worktree` | Harness proof field that means the candidate job ran in an owned isolated worktree rather than taking over `main`. |
| `job_state` | Harness proof field that means the live harness job state was recorded and passed. |
| `changed_paths_report` | Harness proof field that means changed paths were reported for review and rollback. |
| `no_codex_takeover` | Harness proof field that means no sidecar, harness, or generated agent replaced Codex, native subagents, native_omx, LangGraph, `codex-ohmy`, or `apply_patch`. |

## Browser Live Execution

- Lane: `user-level-browser-cli-adapter-boundary`.
- Mode: `live-action`.
- Checker status: valid R6 `live-executed` receipt selected by coverage audit.
- Receipt: ignored local receipt `.omx/r6-live-runtime/receipts/browser-live-action-followup.json`.
- Live action summary: a local browser proof target was opened at an injected localhost URL; the page title was observed, one button was detected, and the allowlisted click action changed the output state. Raw browser payloads, cookies, and transcripts were not stored in tracked files or receipts.
- Redacted evidence hashes:
  - target env hash: `d7f6bcf950d8aab6`
  - external proof hash: `0fdeaf4d2e33e425`
  - external proof path hash: `0806bf41b7a51910`
  - target hash: `d7f6bcf950d8aab6`
- Receipt flags: `browser_action_allowlisted=true`, `raw_browser_data_stored=false`, `remote_publication_mutated=false`.

## Stop-Slop/Caveman Live Execution

- Lane: `stop-slop-caveman-response-density-runtime`.
- Mode: `user-level-install`.
- Checker status: valid R6 `live-executed` receipt selected by coverage audit.
- Receipt: ignored local receipt `.omx/r6-live-runtime/receipts/stop-slop-caveman-live-executed-followup.json`.
- User-level installation was written only below the selected isolated user-level root under local temporary evidence, not into native Codex launcher roots.
- Native Codex protection is enforced: install roots containing native `codex`, `codex-raw`, or `codex-ohmy` launchers are rejected before writing.
- Redacted evidence hashes:
  - target env hash: `9a2e9e1a1fc6dca6`
  - install root hash: `79cb2919f0eee87c`
  - installed path hash: `3097557c9be4077f`
  - wrapper path hash: `976cf665f620bc4d`
  - smoke command hash: `976cf665f620bc4d`
  - rollback pointer hash: `3097557c9be4077f`
- Receipt flags: `canary_preserved=true`, `response_density_guard.status=pass`, `user_level_state_mutation_authorized=true`, `remote_publication_mutated=false`.

## Sensitive Actions Still Blocked

The following lanes were attempted through `live-action`, which means the runtime path for externally visible browser, message, or harness side effects. They correctly remained `blocked` because the required real target and redacted execution proof were absent. Do not claim these lanes as `R6 live-executed` until their proof gates are satisfied.

### WXWork / CLI-Anything

- Lane: `user-level-cli-anything-wxwork-cli-governance`.
- Receipt: ignored local receipt `.omx/r6-live-runtime/receipts/wxwork-live-action-blocked-followup.json`.
- Current receipt mode: `blocked`, which means the runtime recorded missing proof gates instead of claiming a successful WXWork send.
- Current blocker summary: `external_execution_proof_action_performed_required`, `external_execution_proof_external_message_sent_required`, and `external_execution_proof_message_body_hash_required`.
- Required proof before `live-executed`: a real external WXWork/Enterprise WeChat send must be performed under a current operator authorization and owner lease, while retaining only message-body hash evidence and no raw recipient/body.
- Current helper posture verified by `tools/wxwork_cli_governance.py`: repo-local guard only, no process probe, no GUI control, no Enterprise WeChat API/webhook call, no message send, and no user-level Codex config mutation.
- Proof-intake hardening: `proof-template` can create the post-send proof skeleton, and `proof-check` rejects raw `message_body` or raw `recipient` fields while accepting hash-only `message_body_hash` evidence after a real send.

### Codex Harnesses

- Lane: `codex-harnesses-governance`.
- Receipt: ignored local receipt `.omx/r6-live-runtime/receipts/harness-live-action-blocked-followup.json`.
- Current receipt mode: `blocked`, which means the runtime recorded missing proof gates instead of claiming a successful harness job.
- Current blocker summary: missing `action_performed`, `read_guard`, `write_guard`, `isolated_worktree`, `job_state`, `changed_paths_report`, and `no_codex_takeover` proof; these fields are defined in the term glossary above.
- Required proof before `live-executed`: an actual selected harness candidate job with read/write guards, isolated worktree, job state, changed-path report, no Codex takeover, timeout release, rollback, and cleanup evidence.
- Current helper posture verified by `tools/run_codex_harnesses_smoke.py plan --json`: R4 read-only smoke registry only; no install, no sidecar start, no write-capable harness job, no Codex takeover.
- Proof-intake hardening: `proof-template` lists required harness proof fields, and `proof-check` validates `read_guard`, `write_guard`, `isolated_worktree`, `job_state`, `changed_paths_report`, and `no_codex_takeover` before any future `live-executed` promotion.

## Verification Commands

Fresh verification run in this follow-up session:

- `python tools\check_r6_live_runtime_receipts.py --root . --receipt-dir .omx\r6-live-runtime\receipts --require-coverage --max-age-hours 24 --json` - passed in the primary local repository, accepted all 14 R6 lanes, and selected `live-executed` evidence for Browser and Stop-Slop/Caveman.
- `python test\r6_live_runtime.test.py -v` - passed 17/17 tests after proof-intake hardening.
- `python test\check_r6_live_runtime_receipts.test.py -v` - passed 9/9 tests.
- `python tools\check_codex_harnesses_governance.py --root . --json` - passed, confirming harness governance checker posture.
- `python tools\check_user_level_cli_anything_wxwork_cli_governance.py --root . --json` - passed, confirming WXWork/CLI-Anything governance checker posture.

## Non-Claims

- WXWork has **not** been live-executed in this environment.
- Codex harness jobs have **not** been live-executed in this environment.
- No GitLab/GitHub remote publication was performed by these receipts.
