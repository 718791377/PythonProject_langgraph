---
change: implement-r5-runtime-governance-batch-20260607
status: active
---

# Design: R5 Runtime Governance Batch

## Authority Order

All runtime handoff gates preserve this priority:

`Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`

Comet and OpenSpec remain the WHAT/change lifecycle authority. Superpowers remains the HOW discipline. gstack may add delivery-loop guidance only after those gates pass. Harness runtime safety may further restrict execution. Spec Kit remains subordinate and may not create repository authority surfaces such as `.specify/`, root `specs/`, `/speckit.*`, or `$speckit-*` without a separate approved migration plan.

## R5 Receipt Model

Add a generic active-candidate receipt validator in `tools/user_level_receipt_governance.py` and reuse it from lane-specific checkers. A positive R5 receipt must include:

- `runtime_stage` set to `r5` or `active-candidate`;
- explicit operator authorization receipt with current scope and expiry;
- owner lease for any global/shared resource;
- target/action allowlist;
- bounded command/action transcript with redaction status and no raw secrets/private paths;
- timeout release and cleanup evidence;
- rollback pointer and rollback readiness;
- no remote-publication mutation evidence;
- lane-specific authority decision.

Blocked or dry-run receipts may be valid as blocked/dry-run evidence, but the checkers must not count them as R5 active-candidate success.

## Family Slices

1. Foundation: generic receipt validation, worktree receipt lifecycle R5 fields, selector active-candidate ownership, capability readiness projection, LangGraph release evidence, and durable smoke adoption receipt templates.
2. CLI adapter family: MCP/skills, Browser/OpenCLI/CDP, and WXWork_CLI send/action handoff receipts.
3. Delivery/harness family: Stop-Slop/Caveman, gstack, and Codex harness bounded-live receipts.
4. Spec Kit family: authority guard and subordinate adapter receipts.

## Validation Strategy

Use TDD per slice:

1. add failing fixture/unit test for a positive R5 receipt and blocked receipt distinction;
2. run the focused test and observe the expected failure;
3. implement minimal validator/checker/runtime changes;
4. rerun focused tests and the affected checker;
5. commit that plan/slice before moving to the next plan.

## Safety Boundaries

- No real user-level install/start/send/browser/GUI/MCP action is performed by this batch.
- Any future live R5 action must present a current receipt and pass the same checker before claim.
- All repo-local durable state remains under the worktree/repository `.omx` scope.
- Local `main` integration is allowed after gates; remote publication remains closed.
