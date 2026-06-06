# Management Checklist

## Open

- [x] proposal.md 已记录 value 与 why。
- [x] 已记录 success criteria 与 constraints。
- [x] Remote publication 保持在本 change 范围外。

## Design

- [x] Delivery tailoring 限定为 read-only runner、checker、tests 与 specs。
- [x] design.md 已记录 risks 与 assumptions。
- [x] proposal.md verification 已列出 acceptance evidence path。

## Build

- [x] Execution mode selected: superpowers:executing-plans in an isolated feature worktree.
- [x] Quality evidence starts with focused tests and checker self-tests.
- [x] No blocker requires durable team launch; the work is a single serialized helper/checker slice.

## Verify

- [x] Variance review completed and recorded in verification.md.
- [x] Risk/change impact reviewed: R4 smoke receipt is non-adopting and non-mutating.
- [x] Control decision remains continue through local gates; remote publication remains closed.

## Monitoring

- [x] Current facts: runner/checker only; no apply-mode adoption or live backend launch.
- [x] Return/no-return decision: no return needed before focused validation.

## Archive

- [x] Value outcome is summarized.
- [x] Lessons learned or reusable guidance are recorded.
- [x] Delta spec sync, verification evidence, and archive path are confirmed.
