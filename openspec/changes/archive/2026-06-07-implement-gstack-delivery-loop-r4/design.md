# Design: gstack Codex Delivery Loop Runtime R4

The gstack lane is implemented as repo-local advisory tooling, not as a controller. The runtime helper exposes only read-only delivery-loop analysis and bounded R4 smoke receipts. Its decisions are always subordinate to `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.

The helper has two execution classes:

1. dry-run actions:
   - `analyze` - classify the current work into the delivery-loop stage without mutating files.
   - `plan-dry-run` - propose the next delivery-loop steps while keeping Comet/OpenSpec/Superpowers authoritative.
   - `review-dry-run` - summarize reviewer, QA, security, and documentation gaps without applying fixes.
   - `qa-dry-run` - report browser-QA eligibility and blockers without opening a browser.
   - `ship-dry-run` - report local-main-first and remote-publication readiness without pushing or opening MRs.

   These never write repository files, user-level state, durable backend state, browser state, or remote refs. They only emit structured advisory JSON with `authority_decision`, blocker summaries, and safety markers.

2. bounded R4 smoke:
   - `smoke --receipt-dir <dir> [--install-receipt <path>]` - write one explicit smoke receipt and, only with fixture/existing install evidence, run a bounded help probe.

   This writes exactly one explicit receipt file inside the caller-provided directory. Without an install receipt it writes an honest blocked/not-smoke-tested receipt. With a fixture/existing wrapper install receipt it runs a bounded `--help` probe, redacts private paths and secrets from output, records timeout-release state, and records rollback-pointer hashes. It still does not install gstack or enable any live runtime surface.

The checker validates four surfaces:

- plan state and bilingual implementation-plan markers
- runtime dry-run probes
- smoke receipts and their `authority_decision` field, the machine-readable priority and allow/block explanation for the gstack lane
- guard/CI/safety-registry registration

The checker fails closed when:

- the priority string drifts
- `authority_decision` is missing, meaning the runtime lane cannot prove which authority layer won
- smoke receipts claim writes, browser launch, telemetry, active-candidate, or remote publication
- the runtime helper cannot prove all dry-run actions are advisory only
- required tests or guard steps are missing

The stable OpenSpec requirement is a dedicated gstack governance spec. This avoids letting the gstack lane silently piggyback on harness or adapter specs while still keeping Comet/OpenSpec/Superpowers authoritative.
