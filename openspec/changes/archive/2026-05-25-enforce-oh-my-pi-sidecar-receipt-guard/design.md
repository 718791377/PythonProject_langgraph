# Design: oh-my-pi sidecar receipt guard

## Boundary

`oh-my-pi` remains a `reference-only` sidecar in this slice. The new helper
only records evidence for a future governed user-level install/update flow.
It never clones, fetches, installs, runs the sidecar, mutates user-level Codex
configuration, or writes raw private paths to default output.

## Helper contract

`tools/oh_my_pi_sidecar_governance.py` exposes:

- `install-record`: write a pinned receipt to a caller-provided receipt
  directory. Tests use temporary directories; future user-level installers can
  point this at `C:\Users\lenovo\.codex\state\tool-updates\`.
- `validate`: verify receipt schema, immutable pin, source URL, smoke status,
  owner lane, non-active status, and rollback pointer.
- `update-plan`: plan a pin switch only after a valid current receipt and a
  passing external smoke result. It does not fetch or switch pins.
- `update-record`: write a new update receipt containing the previous receipt
  id, previous pin, and receipt hash as rollback evidence.
- `rollback-plan`: report rollback evidence without performing rollback.

## Safety decisions

- `main`, `master`, `HEAD`, `latest`, and branch refs are not accepted as pins.
- Default output exposes path hashes instead of raw install/wrapper/state paths.
- `active` is not an allowed sidecar status in this repo-local receipt guard.
- Any smoke failure blocks pin switching and update receipt writing.
- Rollback is always planned and operator-executed; the helper does not perform
  rollback.

## Rollback

The repository rollback is the local rollback ref created before merging this
feature branch into local `main`. Runtime rollback for future user-level
installers is the receipt-level `rollback_pointer` and previous pin evidence.
