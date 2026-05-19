## MODIFIED Requirements

### Requirement: Remote publication SHALL require fresh explicit user approval

The repository publication workflow SHALL still treat local `main` integration approval and remote publication approval as separate release decisions.

After local `main` integration, a current user message that explicitly requests remote publication, including `push remote` Chinese wording, `publish remote`, `push remote`, `remote publication`, or `use GitLab MR then sync GitHub` Chinese wording, SHALL authorize the normal green-path remote publication sequence as one approval: GitLab publication branch push/update, GitLab MR create/update, GitLab CI wait, GitLab MR merge after green CI, GitLab `main` confirmation, GitHub `main` sync of the same intended commit, and post-publication checks.

During that approved remote publication flow, the session SHALL prefer commands already allowed by the Codex sandbox and previously approved command prefixes. If sandbox escalation is still required for GitLab push, MR, CI, merge, or GitHub sync commands inside the approved green path, the session SHALL request one scoped escalation for the whole `push GitLab / open MR / merge MR / sync GitHub` flow rather than asking once per command.

The session SHALL stop for a new approval before force push, protected-branch setting changes, remote ref deletion, history rewrite, scope expansion, credential changes, or security configuration changes.

#### Scenario: Single remote-publication approval covers the normal green path
- **GIVEN** local validation and local MR review have passed
- **AND** local `main` contains the intended batch
- **WHEN** the current user message says `push remote` Chinese wording, `publish remote`, `push remote`, `remote publication`, `use GitLab MR then sync GitHub` Chinese wording, or equivalent explicit remote-publication wording
- **THEN** the session MAY push or update the GitLab publication branch, create or update the GitLab MR, wait for GitLab CI, merge the MR after CI is green, fetch and confirm GitLab `main`, sync the same intended commit to GitHub `main`, and run post-publication state checks under the same approval
- **AND** it SHALL NOT ask for separate approvals inside that normal green path

#### Scenario: Sandbox escalation is scoped to the approved remote publication flow
- **GIVEN** the current user message has approved the normal green-path remote publication flow
- **AND** the Codex sandbox requires elevation for a GitLab push, MR, CI, merge, or GitHub sync command inside that approved flow
- **WHEN** the session requests escalation
- **THEN** the request SHALL be scoped to the complete `push GitLab / open MR / merge MR / sync GitHub` flow
- **AND** the session SHALL NOT ask for a separate escalation per green-path command

#### Scenario: Exceptional remote operation requires new approval
- **GIVEN** the current user message has approved the normal green-path remote publication flow
- **WHEN** the remote work requires force push, protected-branch setting changes, remote ref deletion, history rewrite, scope expansion, credential changes, or security configuration changes
- **THEN** the session SHALL stop before that operation
- **AND** it SHALL request a new explicit approval for the exceptional action
