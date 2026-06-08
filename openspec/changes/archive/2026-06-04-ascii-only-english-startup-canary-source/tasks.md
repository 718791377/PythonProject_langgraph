# Tasks

## 1. Documentation and spec

- [x] 1.1 Make the English startup summary ASCII-only while describing the same marker values through codepoints.
- [x] 1.2 Keep the Chinese startup summary as the literal visible marker source.
- [x] 1.3 Update the stable canary surface spec for English-ASCII / Chinese-literal storage.

## 2. Checker and test implementation

- [x] 2.1 Update canary placement checker path rules for English ASCII-only and Chinese literal markers.
- [x] 2.2 Update startup mojibake checker tests/fixtures for the split source rule.
- [x] 2.3 Add regression coverage that English summary fails when it contains non-ASCII or literal marker text.

## 3. Verification and integration

- [x] 3.1 Run targeted canary/startup-mojibake tests and checker commands.
- [x] 3.2 Run OpenSpec validation and prepare the archive package for the final guard, precommit, local gate, and local MR review sequence.
- [x] 3.3 Prepare the feature branch for commit, local `main` integration, integrated-worktree cleanup, and the remote-publication stop gate.
