## ADDED Requirements

### Requirement: Remote publication SHALL require fresh explicit user approval
The repository publication workflow SHALL treat local `main` integration approval and remote publication approval as separate release decisions.

After local `main` integration, the session SHALL report any intentional remote lag and SHALL NOT push to GitLab, create or update a GitLab MR, merge a GitLab MR, sync GitHub, delete a remote publication branch, or otherwise mutate remote refs unless the current user message or an approved release record explicitly authorizes that remote publication action.

Generic continuation language such as `continue`, `go on`, `proceed`, or a localized equivalent SHALL NOT be treated as remote publication approval unless it explicitly names remote publication, GitLab push/MR/merge, GitHub sync/mirror, or an equivalent remote action.

#### Scenario: Local integration is approved but remote publication is not
- **GIVEN** local validation and local MR review have passed
- **AND** the user approves local `main` integration
- **WHEN** the session integrates the batch into local `main`
- **THEN** it SHALL report intentional remote lag if local `main` leads GitLab or GitHub
- **AND** it SHALL ask for explicit remote publication approval before any GitLab or GitHub mutation

#### Scenario: Generic continuation after local integration
- **GIVEN** local `main` already contains the intended batch
- **AND** GitLab or GitHub is behind local `main`
- **WHEN** the user says `continue`, `go on`, `proceed`, or a localized equivalent without naming remote publication
- **THEN** the session SHALL treat the remote publication gate as blocked
- **AND** it SHALL ask whether to publish remotely instead of pushing, merging, mirroring, or deleting remote refs

#### Scenario: Remote publication is explicitly approved
- **GIVEN** local validation and local MR review have passed
- **AND** local `main` contains the intended batch
- **WHEN** the user explicitly approves GitLab publication, GitLab MR merge, GitHub sync, or equivalent remote publication
- **THEN** the session MAY perform only the explicitly approved remote action sequence
- **AND** it SHALL report GitLab/GitHub state and stop at the next approval boundary if scope expands