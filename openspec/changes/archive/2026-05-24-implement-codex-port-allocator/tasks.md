## Tasks

- [x] Create the `codex-port` OpenSpec proposal, design, delta spec, and tasks.
- [x] Add `tools/codex_port_ranges.json` for Codex and external project port ownership.
- [x] Implement `tools/codex_port.py lease reserve/renew/release/list/import-legacy/gc`.
- [x] Add owner-range validation, atomic registry writes, `pending_bind`, live-socket collision skipping, stale/GC evidence, and write receipts.
- [x] Add `test/codex_port.test.py` for range ownership, lifecycle, receipt, collision, legacy import, and GC dry-run behavior.
- [x] Register `codex_port.test.py` in `tools/ci/ci_test_manifest.json`.
- [x] Update bilingual implementation-plan checklist state for the completed repo-local `codex-port` allocator MVP items.
- [x] Run local validation and archive this completed OpenSpec change before local `main` integration.
