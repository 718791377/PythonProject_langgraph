## 1. Governance

- [x] 1.1 Add `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md` - English ASCII governance policy for multi-session Git worktree isolation.
- [x] 1.2 Add `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md` - Chinese companion governance policy for multi-session Git worktree isolation.
- [x] 1.3 Update `docs_bilingual/docs_registry.yaml` - bilingual document registry used by governance checkers.
- [x] 1.4 Update `AGENTS.md` - repository instruction surface that routes worktree and dirty-file questions to the new governance policy.
- [x] 1.5 Update `docs_bilingual/project_startup_summary.md` and `.zh-CN.md` - cold-start summaries that list required policy read order.

## 2. Script control

- [x] 2.1 Add `tools/check_worktree_session_hygiene.py` - read-only checker for dirty main, dirty worktrees, duplicate dirty paths, and mainline alignment.
- [x] 2.2 Add `test/check_worktree_session_hygiene.test.py` - unit tests for the worktree hygiene checker.
- [x] 2.3 Update `tools/run_openspec_guard.py` - repository OpenSpec guard sequence that runs the new checker.
- [x] 2.4 Update `test/run_openspec_guard_json.test.py` - JSON aggregation test for the new guard step.

## 3. OpenSpec artifacts

- [x] 3.1 Add `openspec/changes/formalize-multi-session-worktree-hygiene/proposal.md` - change proposal for the governance and checker addition.
- [x] 3.2 Add `openspec/changes/formalize-multi-session-worktree-hygiene/design.md` - design notes for checker behavior and non-destructive semantics.
- [x] 3.3 Add `openspec/changes/formalize-multi-session-worktree-hygiene/specs/codex-repository-multi-session-worktree-isolation/spec.md` - requirement delta for multi-session worktree isolation.
- [x] 3.4 Add `openspec/changes/formalize-multi-session-worktree-hygiene/tasks.md` - implementation checklist for this change.

## 4. Verification

- [x] 4.1 Run `python .\test\check_worktree_session_hygiene.test.py` and `python .\test\run_openspec_guard_json.test.py` - focused unit tests for checker and guard JSON aggregation.
- [x] 4.2 Run `python .\tools\check_document_governance_rules.py --root . --json` - governance document registry and encoding checker.
- [x] 4.3 Run `python .\tools\check_name_clarity_rules.py --root . --json` - checker that requires explanations for scripts, paths, commands, variables, and profile names.
- [x] 4.4 Run `python .\tools\check_worktree_session_hygiene.py --root . --allow-current-dirty --json` - read-only multi-session worktree hygiene checker.
- [x] 4.5 Run `python .\tools\run_openspec_guard.py --root . --tool codex --json` - repository OpenSpec guard sequence.
- [x] 4.6 Run `git diff --check` - whitespace validation for the pending patch.
