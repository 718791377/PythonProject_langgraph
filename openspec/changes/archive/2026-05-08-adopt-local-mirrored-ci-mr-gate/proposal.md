## Why

The repository currently uses GitLab-first publication, but local and remote checks can drift when the remote CI configuration carries its own command logic. The user wants to preserve local CI, local MR review, remote CI, and remote MR review while avoiding format or rule mismatches between local and remote gates.

## What Changes

- Adopt a local-first plus mirrored CI/MR gate publication posture.
- Add `tools/ci/local_gate.ps1` as the shared local/remote CI entrypoint.
- Add `tools/ci/local_mr_review.ps1` as a local MR review summary and merge-simulation entrypoint.
- Update GitLab CI and GitHub workflow jobs to call the shared local gate script instead of duplicating the OpenSpec guard command inline.
- Update startup and worktree governance documents to require local CI and local MR review before pushing remote MR work.

## Capabilities

### New Capabilities

- `codex-repository-multi-session-worktree-isolation`: adds a mirrored local/remote CI and MR gate publication contract.

### Modified Capabilities

- None.

## Impact

- impact_scope: `AGENTS.md`, startup summaries, worktree governance policy, CI configs, local CI/MR scripts, and this OpenSpec change.
- explicit_non_goals: no removal of GitLab MR review, no removal of GitLab CI, no GitHub PR default, no user-level launcher install, and no durable state mutation.
- rollout_sequence: add local gate scripts, make remote CI call the same script, update governance text, validate locally, then publish with the existing remote MR process.
- rollback_plan: revert this change to restore direct CI commands and the previous GitLab-first-only publication wording.
- validation_path: run local gate, local MR review, `openspec validate --all`, `python .\tools\run_openspec_guard.py --root . --tool codex --json`, and `git diff --check`.
