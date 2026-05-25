# Receipt

- Change: `enforce-oh-my-pi-sidecar-receipt-guard`
- Status: archived with implementation in the same local integration package.
- Implementation: `tools/oh_my_pi_sidecar_governance.py`
- Tests: `test/cdp_bridge_governance.test.py`
- CI registration: existing CI-registered browser-governance test file
- User-level install artifact: none; helper writes receipts only when a caller supplies a receipt directory.
- Network/browser/process impact: none.
- Rollback: local rollback ref created before fast-forwarding local `main`.

