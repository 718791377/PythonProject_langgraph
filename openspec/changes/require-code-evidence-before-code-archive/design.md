## Design

The guard is intentionally diff-based. It does not try to replace `openspec archive`; instead it adds a repository CI gate around archive changes.

Detection rules:

- A newly archived change is any path added or renamed under `openspec/changes/archive/YYYY-MM-DD-<change>/` in the current branch or working-tree diff.
- A code-class change is explicit when `.openspec.yaml` declares `x_change_class: code`, `runtime`, `mixed`, `tooling`, or `ci`.
- Without explicit metadata, the checker infers code-class status from archive artifacts that mention runtime, scripts, helpers, tests, checkers, guards, CI, or code behavior.
- A docs-only change can declare `x_change_class: docs`, `spec`, `governance`, `memory`, `research`, `plan`, or `status`.

Evidence rules:

- Code evidence is a changed source, executable script, test file, executable check, Git hook, or CI file outside `docs_bilingual/` and `openspec/`.
- A code-class archive can optionally declare `x_code_evidence_paths` in `.openspec.yaml`; if declared, at least one listed path must be changed in the same branch.
- The aggregate guard runs this checker before worktree cleanliness enforcement so it can evaluate dirty local archive work and MR branch diffs.

This keeps the official OpenSpec CLI semantics intact while adding a repository-specific safety gate.
