# Tasks

## 1. Governed setup

- [x] 1.1 Create isolated feature worktree and ownership metadata.
- [x] 1.2 Create the OpenSpec/Comet change package.

## 2. Reusable tooling

- [x] 2.1 Add reusable PDF/Poppler helper surface and ignored local Poppler cache.
- [x] 2.2 Add reusable document pipeline core scripts and example config.
- [x] 2.3 Add generic vector/retrieval toolkit and sanitized legacy adapters.

## 3. Validation

- [x] 3.1 Add regression tests for path boundaries and vector toolkit smoke behavior.
- [x] 3.2 Run targeted tests, OpenSpec validation, and repository guard.
- [x] 3.3 Prepare commit and local-main-first integration evidence.

## Validation notes

- Targeted regression test passed: `python test/user_level_document_tools.test.py`.
- OpenSpec strict validation passed: `openspec validate promote-reusable-doc-pdf-vector-tools-20260614 --strict --json`.
- Direct bilingual-pair and high-risk guard split checks passed for `verify_official_openspec`, `check_document_pair_policy`, `check_name_clarity_rules`, `check_context_retention_canary_surface`, `check_startup_instruction_mojibake`, `check_safety_rule_script_backing`, and `check_spec_kit_authority_guard`.
- Full `local_gate.ps1` passed after rerun with UTF-8 environment and a 1500-second per-step budget: `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_gate.ps1 -StepTimeoutSeconds 1500 -Json`.
