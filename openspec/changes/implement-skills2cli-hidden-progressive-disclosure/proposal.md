---
change_id: implement-skills2cli-hidden-progressive-disclosure
status: proposed
owner: codex
created_at: 2026-06-30
---

# Proposal: Implement Skills2CLI Hidden Progressive Disclosure

## Why

The current `skills2cli` visibility reduction flow successfully keeps most standalone user skills outside the default model-visible list, reducing skills-context pressure. However, hidden skills are currently hard to use without either manually locating their `SKILL.md` paths or restoring a large receipt batch. The user wants hidden skills to remain hidden by default while still being available through task-scoped progressive disclosure.

## What Changes

- Add a hidden-skill discovery and soft-load surface to `skills2cli`.
- Search current visible skills and `skills2cli` hidden library entries together, with explicit visibility-state labels.
- Add alias routing for known non-installed names such as `stop-slop` and hidden upstream names such as `grill-me`.
- Record usage events when a hidden skill is loaded so future visibility decisions use evidence rather than guesses.
- Add high-confidence visibility recommendations plus a user-manual `apply-recommendations` command that is limited to once per local day and writes rollback receipts.

## Out of Scope

- Restoring all hidden skills.
- Editing plugin cache or vendor `SKILL.md` files.
- Editing `C:\Users\lenovo\.codex\config.toml`.
- Automatically triggering promote/demote in the background.
- Treating hidden skill usage as native subagent or expert evidence.
- Remote publication.
