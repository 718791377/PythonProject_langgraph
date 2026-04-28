## 1. OpenSpec Artifacts

- [x] 1.1 Create proposal, design, spec, and task artifacts for the MR5 helper mirror source-of-truth slice.

## 2. Helper Metadata

- [x] 2.1 Add a reusable helper mirror source-of-truth contract to `tools/install-codex-user-level-team-mode.ps1` - the repository source script that generates user-level helper scripts.
- [x] 2.2 Expose the contract from `codex-durable-state-status.ps1` - the generated read-only durable-state status helper used by cold-start sessions.
- [x] 2.3 Preserve read-only behavior: do not create, edit, delete, or activate any `.omx/state/` artifact.

## 3. Tests and Validation

- [x] 3.1 Update `test/install-codex-user-level-team-mode.test.ps1` - the installer regression test that verifies generated helper behavior.
- [x] 3.2 Run targeted installer and OpenSpec checks.
- [x] 3.3 Publish through GitLab-first MR and sync GitHub after GitLab main is green.
