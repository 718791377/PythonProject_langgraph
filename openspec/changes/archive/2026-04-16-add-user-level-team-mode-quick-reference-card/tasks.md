## 1. Define The Quick-Reference Scope

- [x] 1.1 Audit the currently installed user-level command surface and identify the highest-frequency commands that belong in the first-rollout quick-reference card.
- [x] 1.2 Define the quick-reference structure by operator task, and mark which commands are read-only, preview-first, or mutating.

## 2. Align User-Level Documentation

- [x] 2.1 Add the generated user-level quick-reference asset under the user-level docs directory.
- [x] 2.2 Update the generated playbook so it points operators to the quick-reference companion for common commands.

## 3. Validate The Generated Reference

- [x] 3.1 Add or update regression coverage so the generated quick-reference card matches the actually installed user-level scripts.
- [x] 3.2 Run `openspec validate --all` and confirm the new documentation capability remains consistent with the user-level command surface.
