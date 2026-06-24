# Tasks: Prevent Codex npm EPERM Cleanup Warnings

## Stage 1: Freeze plan package

- [x] Create the OpenSpec change for Windows Codex npm lock preflight.
- [x] Freeze the design boundary around `tools/codex-official-update-patch-replay-template.ps1`.
- [x] Write the Superpowers implementation plan for runtime and test slices.
- [x] Record management checklist and monitoring decision.
- [ ] Validate and integrate the Stage 1 freeze package into local `main`.

## Stage 2: Live runtime implementation

- [ ] Add Windows lock preflight parameters, process inventory, and report fields to the official update template.
- [ ] Add npm cleanup EPERM warning classification without masking non-zero npm failures.
- [ ] Update generated checklist guidance for lock preflight and manual leftover cleanup.
- [ ] Extend fake npm/process-inventory PowerShell regression coverage.
- [ ] Run focused tests, OpenSpec guard, local gate, and local MR review.
- [ ] Integrate the Stage 2 runtime package into local `main` and stop at the remote-publication gate.
