## 1. Lifecycle contract
- [x] 1.1 Add `stale` to allowed receipt lifecycle statuses.
- [x] 1.2 Validate branch-matching claim lifecycle/status labels against the same allowed set.
- [x] 1.3 Keep completion evidence required for merged/completed/cleaned/remote-sync-needed states only.

## 2. Fixtures and tests
- [x] 2.1 Add fixture receipts for every allowed lifecycle state.
- [x] 2.2 Add focused tests for stale receipt and stale claim acceptance.
- [x] 2.3 Add focused tests for completion-evidence required and non-required lifecycle groups.

## 3. Documentation and specs
- [x] 3.1 Update the implementation plan evidence and task checklist.
- [x] 3.2 Add OpenSpec delta requirements for stale classification and completion evidence.
- [x] 3.3 Archive the change in the same local integration package after validation.

## 4. Verification
- [x] 4.1 Run focused unit tests for the receipt checker.
- [x] 4.2 Run receipt checker, implementation-plan checker, OpenSpec validation, pre-commit review, local gate, and local MR review before local main integration.
