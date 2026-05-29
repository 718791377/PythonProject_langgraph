# Verification: Enforce OpenCLI live-start receipt guard

## Scope verified

- `tools/opencli_governance.py start` 校验 install receipt、owner lease 与 port lease evidence。
- 证据齐全时 repo-local MVP 仍不启动 OpenCLI。
- 输出继续保持 redacted 与 path-hashed。

## Evidence

- Targeted unit test: `python test\cdp_bridge_governance.test.py`。
- OpenSpec guard: `python tools/run_openspec_guard.py --root . --json`。
- Local CI gate: `powershell -NoProfile -File tools/ci/local_gate.ps1 -Json`。
- Local MR review: `powershell -NoProfile -File tools/ci/local_mr_review.ps1 -Json`。

## Control decision

Control decision `continue` 表示当前证据足够、无需返回更早 Comet phase；该切片满足方案要求，可以合入本地 `main`。远端发布仍不在本次授权内。
