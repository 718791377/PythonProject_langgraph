## 1. OpenSpec Artifacts

- [x] 1.1 Create the `implement-codex-user-level-team-mode-p6-windows-breakaway-worker-lifecycle` proposal, design, and capability spec deltas.
- [x] 1.2 Record that this batch is a follow-up lifecycle correction after the archived `P6` backend batch.

## 2. Runtime Follow-Up

- [x] 2.1 Add a stronger native Windows breakaway launcher path for prompt workers.
- [x] 2.2 Track the real controller pid for liveness and shutdown instead of a short-lived launcher hop.
- [x] 2.3 Align shutdown with the breakaway-launched worker shape.
- [x] 2.4 Update Windows worker guidance so controller-owned startup ACK / initial claim are not retried blindly.

## 3. Validation

- [x] 3.1 Validate that fresh Windows durable teams stay alive after the launching shell exits.
- [x] 3.2 Validate clean shutdown against the new launcher path.
- [x] 3.3 Revalidate cross-repository tracked-team isolation after the follow-up lifecycle fix.
