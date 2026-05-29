# Design: WeCom CLI Guarded Dry-Run

## Boundary
`wecom-cli` is modeled as a repo-local governance guard first. The helper reports whether a future GUI action would satisfy evidence gates, but it never performs live GUI automation.

## Decisions
- API/Webhook status is the default low-risk lane.
- Inline webhook secrets are rejected; only references are accepted.
- GUI actions require both an operator authorization receipt and a global WXWork lease receipt.
- Valid receipts only permit `dry_run_only` dispatch eligibility in this repository MVP.
- Outputs use hashes or booleans rather than raw private paths or message content.

## Risks
- Treating dry-run eligibility as live authorization would be unsafe; the output explicitly reports `gui_control_performed=false`.
- Missing CI registration would allow the guard to drift; the baseline checker now requires the test registration and helper file.
