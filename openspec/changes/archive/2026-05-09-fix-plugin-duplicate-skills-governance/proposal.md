## Why

The local publication gate is currently blocked by a skills-governance error that is already present on `main`: duplicate plugin-supplied `Chrome` skill entries are reported as a same-layer duplicate error even though the active policy says plugin skills and plugin duplicates are bundle-managed and report-only until fine-grained filtering exists.

This blocks unrelated feature branches from passing `tools/ci/local_gate.ps1` even when their own tests and OpenSpec artifacts are healthy.

## What Changes

- Align `tools/check_codex_skills_governance.py` with the policy by classifying same-layer plugin duplicate skill names as non-blocking warnings.
- Keep same-layer user and repository duplicates blocking unless they are covered by an explicit registry exception.
- Add regression coverage for plugin-layer duplicate skill names.
- Keep all plugin and user-level skill files read-only; do not edit plugin cache, user skills, or `C:\Users\lenovo\.codex\config.toml`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-skills-governance-lifecycle`: clarify that plugin-layer duplicate skill names are report-only warnings, while unmanaged user/repo same-layer duplicates remain blocking errors.

## Impact

- Affected code: `tools/check_codex_skills_governance.py`.
- Affected tests: `test/check_codex_skills_governance.test.py`.
- Affected specs: `openspec/specs/codex-user-level-skills-governance-lifecycle/spec.md` after archive promotion.
- Impact scope: repository-local guard behavior and local/remote CI mirror gate behavior.
- Explicit non-goals: no plugin deletion, no user-level skill rewrite, no Vercel/browser capability removal, no user-level Codex config mutation.
- Rollout sequence: patch checker, add tests, validate active change, archive into the same branch if local validation passes, then publish through GitLab-first workflow.
- Rollback plan: revert the checker/test/spec delta; plugin/user skill files remain untouched.
- Validation path: `openspec validate --all`, `python tools/run_openspec_guard.py --root . --json`, `python -m unittest test/check_codex_skills_governance.test.py`, `tools/ci/local_gate.ps1 -RequireCleanGit`, `tools/ci/local_mr_review.ps1`.
- Mainline classification: small cross-mainline governance/CI blocker fix under the active user-level skills governance line.
