---
change: implement-wecom-cli-guarded-dry-run
status: archived-with-local-implementation
---

# Design: WeCom CLI Guarded Dry-Run

The implementation keeps `wecom-cli` as a repo-local guard, not a live adapter. The low-risk path is API/Webhook planning; the high-risk path is WXWork GUI action precheck.

Key invariant: even with valid receipts, this repository only reports dry-run dispatch eligibility and never controls `WXWork.exe`.
