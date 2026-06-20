# Management Checklist

## Open

- [x] Value: convert 48/60 from register-only counts into generated body-document counts.
- [x] Success criteria: Stage A freezes plan and contract; Stage B generates 96 Codex body files and 120 one-person-company body files.
- [x] Constraints: local-main-first, no remote publication, no raw-source re-extraction, no unrelated runtime edits.

## Design

- [x] Delivery tailoring: two-stage serial local-main package.
- [x] Risks: Windows command-line length, UTF-8/Chinese corruption, registry drift, package contamination, over-editing unrelated runtime surfaces.
- [x] Acceptance evidence path: OpenSpec validation, generator/checker JSON, focused unittest, local gate, local MR review, local integration helper receipt.

## Build

- [x] Execution mode: leader-owned fan-in with advisory experts; Stage B may use disjoint runtime/test and docs/registry execution slices.
- [x] Write ownership: Stage B is limited to generator, checker, tests, registry, and generated operations package body docs.
- [ ] Stage A validation result recorded.
- [ ] Stage B validation result recorded.

## Verify

- [ ] 48 Codex body primary documents and 48 zh-CN companions verified.
- [ ] 60 one-person-company body primary documents and 60 zh-CN companions verified.
- [ ] I/T/O, tailoring, registry, encoding, idempotency, and package isolation verified.
- [ ] Local-main integration evidence recorded.

## Monitoring

- [x] Current decision: continue.
- [x] Monitoring status: clear.
- [x] Rework trigger: if Stage B cannot prove full body counts, return to design before runtime integration.

## Archive

- [ ] Stable specs synced after Stage B.
- [ ] Archive created after verification.
- [ ] Remote-publication gate preserved.
