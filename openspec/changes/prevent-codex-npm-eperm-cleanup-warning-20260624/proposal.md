---
change_id: prevent-codex-npm-eperm-cleanup-warning-20260624
status: proposed
owner: codex
created_at: 2026-06-24
---

# Proposal: Prevent Codex npm EPERM Cleanup Warnings

## Why

On Windows, `npm install -g @openai/codex` can finish the package update but still emit `npm warn cleanup` with `EPERM: operation not permitted, unlink ... codex.exe` when active Codex or Node processes keep the npm-installed Codex executable locked. The warning leaves `.codex-*` staging directories under the global `@openai` package root and creates ambiguous operator state: the install may be successful, but cleanup failed.

The repository already has an official update orchestration script, `tools/codex-official-update-patch-replay-template.ps1`, which owns the global npm update lane, snapshots, diff review, patch replay, and installer-test workflow. It currently runs the official update without a Windows lock preflight and does not classify npm cleanup EPERM warnings in its structured report.

## What Changes

- Add a Windows Codex lock preflight to the official update template before it runs `npm install -g @openai/codex oh-my-codex`.
- Make update stages fail closed by default on Windows when likely active Codex/Node lock holders are detected, unless an explicit override is supplied.
- Add structured report fields for lock preflight, leftover `.codex-*` staging candidates, and npm cleanup-warning classification.
- Update the generated checklist so operators close active Codex/Node sessions before official updates and treat leftover staging directories as manual cleanup after sessions exit.
- Extend the PowerShell regression test to simulate fake npm output and fake process inventory without touching real global npm installs or killing real processes.

## Out of Scope

- Remote publication, GitLab MR creation/merge, or GitHub sync.
- Modifying installed `codex-ohmy`, `codex-raw`, `codex`, `codex.cmd`, or `codex.ps1` wrapper artifacts directly.
- Making `codex-ohmy` self-update Codex.
- Killing Codex, Node, npm, or PowerShell processes automatically.
- Deleting leftover `.codex-*` staging directories automatically in this change.
- Replacing the existing official update patch replay workflow.
