## Tasks

- [x] Create the `chrome-devtools-mcp` project-profile managed-wrapper OpenSpec proposal, design, delta spec, and implementation tasks.
- [x] Extend `tools/chrome_devtools_mcp_managed.py` with project-profile plan/reserve/start/release/status commands.
- [x] Delegate project-profile lease writes and releases to `tools/browser_owner_registry.py`.
- [x] Require project-profile authorization receipts for reserve and live start gates.
- [x] Keep project-profile plan and reserve output sanitized with profile-path and receipt-path hashes.
- [x] Mark project profiles as long-lived and not cleanup-eligible in the repo-local MVP.
- [x] Fail closed for project-profile live start without authorization, without install receipt, and with both receipts while live start remains deferred.
- [x] Add tests for dry-run planning, authorization failure, protected lease writing, same-profile exclusivity, live-start gate order, and project-profile release receipts.
- [x] Update bilingual implementation-plan state for the completed repo-local project-profile wrapper MVP item.
- [x] Update the stable OpenSpec requirement for project-profile managed-wrapper behavior.
- [x] Run local validation and archive this completed OpenSpec change before local `main` integration.
