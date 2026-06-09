# R6 Sensitive Live Action Evidence - 2026-06-09

## Summary

- Package: R6 sensitive live-action proof gate, proof intake, and bounded harness live-job evidence.
- Priority order preserved: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
- Runtime support: `tools/r6_live_runtime.py run --mode live-action --proof-receipt <redacted-proof-json>`.
- Proof-intake support: `tools/r6_live_runtime.py proof-template` writes a fail-closed proof skeleton, and `tools/r6_live_runtime.py proof-check` validates redacted proof fields without running WXWork, browser, or harness actions.
- Harness proof runtime support: `tools/run_codex_harnesses_smoke.py r6-live-proof` runs one bounded repo-local harness job in a temporary isolated Git worktree, records only redacted/hash proof material, rolls back the job worktree, removes the temporary worktree, and does not mutate remote publication.
- Safety correction: Browser/WXWork/Harness `live-action` cannot become `live-executed` from environment targets alone; a redacted external execution proof receipt is required.
- Follow-up result in the current environment:
  - `user-level-browser-cli-adapter-boundary`: `live-executed` with side effect family `browser_gui`.
  - `stop-slop-caveman-response-density-runtime`: `live-executed` with side effect family `user_level_install`.
  - `codex-harnesses-governance`: `live-executed` with side effect family `harness_job`, using a bounded local proof job in an isolated temporary Git worktree.
  - `user-level-cli-anything-wxwork-cli-governance`: remains `blocked`, because there is no real WXWork send target and no redacted message-send proof.
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
| `timeout_release` | Harness proof field that means the bounded job released on timeout boundaries and did not leave a hidden worker running. |
| `rollback` | Harness proof field that means the temporary job changes were rolled back to a clean state. |
| `cleanup` | Harness proof field that means temporary job resources were removed. |
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

## Codex Harnesses Bounded Live Execution

- Lane: `codex-harnesses-governance`.
- Mode: `r6-live-proof` followed by `r6_live_runtime.py run --mode live-action`.
- Checker status: valid R6 `live-executed` receipt for the single harness lane; the receipt validator reports `r6_live_valid=true` and `external_side_effects=harness_job`.
- Receipt: ignored local receipt `.omx/r6-live-runtime/receipts/harness-live-job-live-executed-20260609.json`.
- Proof: ignored local proof `.omx/r6-live-runtime/proofs/harness-live-job-proof-20260609.json`.
- Live action summary: the harness proof runner created a temporary clean Git repository, created an isolated detached worktree for one bounded local harness job, wrote one proof marker inside that isolated worktree, collected a changed-path report, rolled back and removed the temporary worktree, and left the source repository clean. The receipt records only hashes and status fields; raw temporary paths are not stored in tracked files.
- Redacted evidence hashes:
  - candidate id hash: `47ab92541ddbb827`
  - proof hash: `e0f71f0789945588`
  - proof path hash: `a5e65db4805d61a8`
  - receipt path hash: `5fc44be576ded575`
  - target env hash: `d36d4a6a4aa244b4`
- Receipt/proof flags: `read_guard.status=pass`, `write_guard.status=pass`, `isolated_worktree.status=pass`, `job_state.status=pass`, `changed_paths_report.status=pass`, `timeout_release.status=pass`, `rollback.status=pass`, `cleanup.status=pass`, `no_codex_takeover=true`, `active_sidecar_took_over_codex=false`, `remote_publication_mutated=false`.
- Scope limitation: this is a bounded repo-local harness job proof. It does not install Pi, oh-my-pi, revfactory/harness, ohmyopenagent, snow-cli, or any user-level harness runtime; it does not start a sidecar; and it does not replace Codex launchers, native subagents, native_omx, LangGraph, `codex-ohmy`, or `apply_patch`.

## Sensitive Action Still Blocked: WXWork / CLI-Anything

- Lane: `user-level-cli-anything-wxwork-cli-governance`.
- CLI-Anything install update: the user-level CLI-Anything side is now installed and smoke-tested separately; see `docs_bilingual/implementation_evidence/cli_anything_user_level_install_evidence_20260609.md`.
- Installed CLI-Anything evidence: `cli-anything-hub==0.3.0`, `cli-hub --help`, ignored install receipt `.omx/cli-anything/cli-anything.lock.json`, `install_performed=true`, `network_fetch_performed=true`, `user_level_config_mutated=false`.
- WXWork_CLI handoff: WXWork_CLI integration is delegated to `D:\PythonProject_OpenClaw` / PythonProject_OpenClaw; this repository package still does not install/start/control WXWork_CLI or send WXWork messages.
- Receipt: ignored local receipt `.omx/r6-live-runtime/receipts/wxwork-live-action-blocked-followup.json`.
- Current receipt mode: `blocked`, which means the runtime recorded missing proof gates instead of claiming a successful WXWork send.
- Current blocker summary: `external_execution_proof_action_performed_required`, `external_execution_proof_external_message_sent_required`, and `external_execution_proof_message_body_hash_required`.
- Required proof before `live-executed`: a real external WXWork/Enterprise WeChat send must be performed under a current operator authorization and owner lease, while retaining only message-body hash evidence and no raw recipient/body.
- Current helper posture verified by `tools/wxwork_cli_governance.py`: repo-local guard only, no process probe, no GUI control, no Enterprise WeChat API/webhook call, no message send, and no user-level Codex config mutation.
- Proof-intake hardening: `proof-template` can create the post-send proof skeleton, and `proof-check` rejects raw `message_body` or raw `recipient` fields while accepting hash-only `message_body_hash` evidence after a real send.

## Verification Commands

Fresh verification run in this follow-up session:

- `python test\codex_harnesses_smoke_receipts.test.py -v` - passed 7/7 tests and covers `r6-live-proof` bounded isolated-worktree proof generation.
- `python test\r6_live_runtime.test.py -v` - passed 18/18 tests and covers stricter harness proof intake requiring candidate id, job profile, timeout release, rollback, and cleanup evidence.
- `python tools\run_codex_harnesses_smoke.py r6-live-proof --root <temp-clean-git-root> --candidate-id pi-runtime --job-profile bounded-local-write --proof-out <ignored-proof> --json` - passed and reported `runs_harness_job=true`, `runs_write_capable_harness_job=true`, no Codex replacement, no local-main gate bypass, no user-level mutation, no remote publication mutation, and redacted proof hashes only.
- `python tools\r6_live_runtime.py proof-check --root . --lane codex-harnesses --proof-receipt <ignored-proof> --json` - passed and accepted the redacted harness proof.
- `python tools\r6_live_runtime.py run --root . --lane codex-harnesses --mode live-action --proof-receipt <ignored-proof> --receipt-out <ignored-receipt> --json` - passed and wrote a `live-executed` R6 harness receipt.
- `python tools\check_r6_live_runtime_receipts.py --root . --lane codex-harnesses --receipt <ignored-receipt> --json` - passed and validated the R6 harness receipt.
- `python test\check_r6_live_runtime_receipts.test.py -v` - remains part of the focused R6 checker validation surface.
- `python tools\check_codex_harnesses_governance.py --root . --json` and `python tools\check_user_level_cli_anything_wxwork_cli_governance.py --root . --json` remain the lane-governance validation surfaces.

## Non-Claims

- WXWork has **not** been live-executed in this environment.
- No user-level Pi, oh-my-pi, revfactory/harness, ohmyopenagent, snow-cli, or other harness runtime was installed or started by this package.
- No GitLab/GitHub remote publication was performed by these receipts.
