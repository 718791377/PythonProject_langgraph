# Proposal: enforce remote publication single approval

## Why

The local-main-first workflow intentionally stops before remote publication unless the user explicitly approves the remote action. After approval, however, the normal green path should not fragment into repeated approvals for each GitLab and GitHub step or for sandbox elevation prompts that are already inside the approved flow.

## What changes

- Treat explicit wording such as `push remote` Chinese wording, `publish remote`, `push remote`, `remote publication`, or `use GitLab MR then sync GitHub` Chinese wording as one approval for the normal green-path remote publication flow.
- Define that green path as GitLab publication branch push/update, GitLab MR create/update, GitLab CI wait, GitLab MR merge after green CI, GitLab `main` confirmation, GitHub `main` sync of the same intended commit, and post-publication checks.
- Prefer existing sandbox-approved commands and approved command prefixes.
- If sandbox escalation is still required inside the approved green path, request one scoped escalation for the complete `push GitLab / open MR / merge MR / sync GitHub` flow instead of asking per command.
- Preserve fail-closed boundaries for force push, protected-branch changes, remote ref deletion, history rewrite, scope expansion, and credential/security configuration changes.

## Safety

This change does not authorize remote publication without a current explicit remote-publication user message or approved release record. It narrows repeated approval prompts only after such approval exists, and it leaves exceptional or destructive remote operations behind a fresh approval gate.
