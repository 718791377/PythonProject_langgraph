## 1. Source Templates

- [x] 1.1 Update `tools/install-codex-user-level-team-mode.ps1` (managed user-level installer) so generated `team-mode-playbook.md` includes the global automatic collaboration default.
- [x] 1.2 Update `tools/install-codex-user-level-team-mode.ps1` so generated `team-mode-quick-reference.md` includes the concise global automatic collaboration default.
- [x] 1.3 Update generated `team-leader.toml` and startup model-instructions payload in `tools/install-codex-user-level-team-mode.ps1` so wrapped sessions inherit the default rule.

## 2. Governance and Guarding

- [x] 2.1 Keep bilingual governance docs in `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.*` aligned with the global default rule.
- [x] 2.2 Extend `tools/check_orchestration_activation_policy.py` (policy-surface guard) to require the global default and `platform_subagent_invocation_constraint` token.
- [x] 2.3 Add installer regression assertions in `test/install-codex-user-level-team-mode.test.ps1` (managed installer test) for generated docs and launcher instruction payloads.

## 3. Validation and Closure

- [x] 3.1 Run the orchestration activation policy checker.
- [x] 3.2 Run the installer regression test.
- [x] 3.3 Run OpenSpec guard and local gate or document any scoped validation exception.
- [x] 3.4 Archive/promote the OpenSpec change after implementation validation passes.
