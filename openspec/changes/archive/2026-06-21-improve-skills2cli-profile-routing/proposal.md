---
change_id: improve-skills2cli-profile-routing
status: proposed
owner: codex
created_at: 2026-06-21
---

# Proposal: Improve Skills2CLI Profile Routing

## Why

The current plugin-modules `target_profile` registry is valid as a hard-load profile list, but it is too coarse for current-session skill routing. It lacks scenario descriptions, negative examples, task-module layering, and recall/rerank evidence. Seven known plugin families are reachable only through `full`, and `full` is too large to be a normal default because it can trigger skills context budget pressure.

The 30-day `codex_skills_usage_audit` has produced enough evidence to keep profile changes advisory and reversible while improving how the system suggests soft-load and hard-load-preview candidates.

## What Changes

- Freeze a scenario-based profile routing contract before runtime edits.
- Preserve existing profile IDs while adding aliases, route terms, negative examples, ranking signals, and task modules.
- Require non-`full` routing ownership for known plugins unless an explicit allowlist reason exists.
- Add a `skills2cli.py profile suggest` advisory command that explains matched profiles, task modules, excluded candidates, and soft/hard-load boundaries.
- Keep hard-load profile apply out of scope; runtime can only suggest soft-load commands and hard-load preview commands.
- Split implementation into Phase A plan freeze and Phase B runtime implementation, each integrated into local `main` separately.

## Out of Scope

- Automatically applying any hard-load profile.
- Editing user-level Codex `config.toml`.
- Bulk-editing plugin cache or vendor `SKILL.md` files.
- Remote publication, GitLab MR creation/merge, GitHub sync, or remote ref mutation.
