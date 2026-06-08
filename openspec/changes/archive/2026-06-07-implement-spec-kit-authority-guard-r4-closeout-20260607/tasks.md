# Tasks

## 1. Closeout package

- [x] 1.1 Create the bounded OpenSpec closeout package for Spec Kit authority guard R4.
- [x] 1.2 Record local-only scope, dry-run boundary, and remote-publication gate.

## 2. Runtime and checker

- [x] 2.1 Tighten runtime receipts to require the strict priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
- [x] 2.2 Tighten the authority guard so receipt validation fails closed when the priority order is missing or changed.
- [x] 2.3 Extend focused tests for the stricter receipt contract.

## 3. Stable evidence promotion

- [x] 3.1 Promote the R4 closeout requirement into the stable safety-rule spec pair.
- [x] 3.2 Update the safety-rule script-backing registry with the runtime helper and closeout wording.
- [x] 3.3 Update Spec Kit governance and implementation-plan wording to match the strict priority order.

## 4. Validation and local integration

- [x] 4.1 Run focused Spec Kit tests and guard validation.
- [x] 4.2 Run OpenSpec validation, precommit update/archive review, and repository guard.
- [x] 4.3 Archive the completed change and rerun validation.
- [ ] 4.4 Run local gate and local MR review on the clean feature worktree.
- [ ] 4.5 Merge into local `main`, run post-merge validation, clean the integrated feature worktree/branch, and stop at the remote-publication gate.
