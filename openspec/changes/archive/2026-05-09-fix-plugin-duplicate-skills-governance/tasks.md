# Tasks: Fix Plugin Duplicate Skills Governance

## 1. Artifacts

- [x] 1.1 Create proposal, design, delta spec, and tasks artifacts.
- [x] 1.2 Add bilingual companion artifacts for repository governance checks.

## 2. Checker implementation

- [x] 2.1 Update `tools/check_codex_skills_governance.py` so same-layer plugin duplicate skill names are warnings, not blocking errors.
- [x] 2.2 Preserve blocking errors for same-layer user/repo duplicates unless the registry declares an exception.

## 3. Tests and validation

- [x] 3.1 Add regression coverage for plugin-layer duplicate skill names.
- [x] 3.2 Run the focused skills governance test.
- [x] 3.3 Run OpenSpec validation, repository guard, local gate, local MR review, and `git diff --check`.


