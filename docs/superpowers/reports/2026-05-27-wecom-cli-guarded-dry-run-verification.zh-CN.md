---
change: implement-wecom-cli-guarded-dry-run
status: pass
---

# 验证：wecom-cli 受治理 dry-run

需要保留的验证证据：

- `python test/wecom_cli_governance.test.py -v` 通过。
- `python test/check_user_level_mcp_skills_browser_cli_baseline.test.py -v` 通过。
- `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json` 通过。
- `python tools/run_openspec_guard.py --root . --json` 通过。
- 本地合入前 `tools/ci/local_gate.ps1 -Json` 通过。
- 本地合入前 `tools/ci/local_mr_review.ps1 -Json` 通过。
