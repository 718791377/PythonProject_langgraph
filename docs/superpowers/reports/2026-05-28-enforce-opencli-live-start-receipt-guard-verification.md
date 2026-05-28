# Verification: Enforce OpenCLI live-start receipt guard

## Scope verified

- `tools/opencli_governance.py start` validates install receipt, owner lease, and port lease evidence.
- Repo-local MVP still does not start OpenCLI when evidence is complete.
- Output remains redacted and path-hashed.

## Evidence

- Targeted unit test: `python test\cdp_bridge_governance.test.py`.
- OpenSpec guard: `python tools/run_openspec_guard.py --root . --json`.
- Local CI gate: `powershell -NoProfile -File tools/ci/local_gate.ps1 -Json`.
- Local MR review: `powershell -NoProfile -File tools/ci/local_mr_review.ps1 -Json`.

## Control decision

Control decision `continue` means the current evidence is sufficient to proceed without returning to an earlier Comet phase; the slice satisfies the plan and can be integrated into local `main`. Remote publication remains outside this approval.
