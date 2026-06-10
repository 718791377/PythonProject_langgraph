# WXWork R6 Live Execution Evidence - 2026-06-10

## Summary

- Lane: `user-level-cli-anything-wxwork-cli-governance`.
- Status: R6 `live-executed` implemented and checker-validated.
- Priority order preserved: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
- Live action: one bounded WXWork.exe visual-control proof sent one ordinary timestamped test message, then used the visible right-click member menu to generate the mention token before sending the second timestamped test message.
- Direct paste of the mention string: `false`; proof intake and receipt checker reject direct-paste mention evidence.
- Remote publication mutated: `false`.

## Redaction Boundary

Tracked evidence is hash-only/status-only. This document does not contain raw group names, raw member names, message bodies, private paths, screenshots, or transcripts. Local ignored evidence under `.omx/` may contain human-confirmable screenshots and preview files, but tracked files reference only hashes and status flags.

## Hash Evidence

| Evidence field | Value |
| --- | --- |
| proof file sha256 | `a80e4df7cc97d97f04b032f0be792375be8e64057a7b8f7833cecff9937e0cc7` |
| proof accepted hash | `1857d222d49d786c` |
| proof path hash | `f6d96ab6f6035b22` |
| receipt path hash | `f737086c9b9404db` |
| target env hash | `9e488910d57c8d95` |
| target group hash | `sha256:grp:6737a1c9e5e3b61a` |
| target member hash | `sha256:mbr:5d8e8fa79c7560f2` |
| ordinary message hash | `sha256:8695e74a8321233b3f50197d6dda8e2c1b213636fceb7fcbcc9b5efc78348c4d` |
| mention message hash | `sha256:dbc7242c620bcf8775c0f1dcdd5ecb944cabfc4545935f36102a7529967015be` |
| combined message body hash | `sha256:19f164771d1dde7c21dbfc6558fe6e9b45e7f076faff69228e3e56b81ac04c44` |
| visual confirmation hash | `sha256:19d754187cdc65c7614b5746b33bc3aa1f2c8627587089277a31eb13f4150a47` |
| CLI-Anything preview inspect hash | `sha256:6c41326240635d7115a92bd2f81f177cdd20bade31f7a83ee7ad94577ac92358` |
| CLI-Anything preview HTML hash | `sha256:499a7ee44a3be59fdddca3922c3ad4f97b6949caa9e87dc7d2c8d2f7be69225b` |
| human-confirmable aggregate hash | `sha256:cc33f22ac802b53a28a0026612adc5e0b1f6e199f63b78a6ad4e1c0d55f9d973` |

## Required Flags

- `cli_anything_visual_rendering_verified=true` - confirms the CLI-Anything preview/rendering layer validated the bounded proof surface.
- `visual_control_verified=true` - confirms the live proof used visual GUI control instead of transcript-only evidence.
- `ordinary_message_sent=true` - confirms the ordinary timestamped test message send step completed.
- `right_click_member_performed=true` - confirms the member was opened through the visible right-click menu path.
- `mention_menu_selected=true` - confirms the visible mention menu item generated the mention token.
- `mention_message_sent=true` - confirms the second timestamped mention test message send step completed.
- `external_message_sent=true` - records that the bounded proof had an external message side effect.
- `direct_paste_mention_used=false` - records that direct paste of the mention string was not used and remains rejected.
- `evidence_artifact_included=false` - records that tracked receipt data excludes screenshots or raw preview artifacts.
- `message_body_included=false` - records that tracked receipt data excludes raw message body text.
- `recipient_included=false` - records that tracked receipt data excludes raw group or member identifiers.
- `remote_publication_mutated=false` - records that no GitLab/GitHub remote publication state was changed.

## Verification Commands

Fresh local verification for this evidence package:

- `cli-hub previews inspect --json .omx\wxwork-r6-live\preview\final-send` - passed and wrote an ignored local inspect artifact.
- `cli-hub previews html .omx\wxwork-r6-live\preview\final-send -o .omx\wxwork-r6-live\preview\final-send\cli-hub-preview.html` - passed and wrote an ignored local HTML preview artifact.
- `python tools
6_live_runtime.py proof-check --root . --lane wxwork-cli --proof-receipt .omx\wxwork-r6-live\proofs\wxwork-live-proof-20260610.json --json` - passed with no blockers.
- `python tools
6_live_runtime.py run --root . --lane wxwork-cli --mode live-action --env-file .omx\wxwork-r6-live\wxwork-r6-live.env --proof-receipt .omx\wxwork-r6-live\proofs\wxwork-live-proof-20260610.json --receipt-out .omx
6-live-runtime
eceipts\wxwork-live-executed-20260610.json --json` - passed and wrote an ignored `live-executed` receipt.
- `python tools\check_r6_live_runtime_receipts.py --root . --lane wxwork-cli --receipt .omx
6-live-runtime
eceipts\wxwork-live-executed-20260610.json --json` - passed with `r6_live_valid=true` and no errors.

## Non-Claims

- This package does not install or publish a general WXWork_CLI product integration.
- This package does not mutate user-level Codex config.
- This package does not mutate GitLab, GitHub, or any remote publication ref.
- This package does not commit screenshots, raw recipients, or raw message bodies.
