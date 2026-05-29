## 1. Documentation and specification

- [x] 1.1 Update the startup summary pair so the visible canary marker is ASCII-stable and the historical non-ASCII marker is legacy detection input only.
- [x] 1.2 Add an OpenSpec delta for the canary surface capability covering ASCII canonical markers and legacy marker rejection.

## 2. Checker and test implementation

- [x] 2.1 Update the canary surface checker to use ASCII canonical markers assembled from fragments and to keep historical marker/corruption detection fail-closed.
- [x] 2.2 Update the startup mojibake checker to accept ASCII canonical response evidence and reject historical/corrupted canary evidence.
- [x] 2.3 Update targeted tests for ASCII canonical evidence and historical/corrupted evidence rejection.

## 3. Verification and integration

- [x] 3.1 Run targeted canary and startup-mojibake tests plus checker commands.
- [x] 3.2 Run OpenSpec/precommit/local-gate validation.
- [ ] 3.3 Commit, run local MR review, merge to local `main`, and stop before remote publication.
