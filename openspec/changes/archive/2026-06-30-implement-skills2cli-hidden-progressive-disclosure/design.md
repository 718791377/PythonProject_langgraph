# Design: Skills2CLI Hidden Progressive Disclosure

## Overview

The runtime adds a read-only hidden-skill layer beside existing visible-skill indexing. Hidden records are discovered from `CODEX_HOME/state/skills2cli/visibility-disabled/**/SKILL.md`. They are identified by stable redacted IDs and can be searched or loaded one at a time.

## Key decisions

- Hidden soft-load is read-only. It never moves directories and never changes `config.toml`.
- `hidden load` is the only hidden command that returns a full skill body, and it records a compact usage event.
- Visibility promotion/demotion is evidence-driven but not background-driven: a human/operator command must invoke `apply-recommendations`.
- Apply is limited to standalone user skills, one local-day run, three moves maximum, and rollback receipts.
- Current visible skills remain indexed by existing logic; hidden progressive disclosure adds a separate visibility-state label instead of changing existing `index/search` semantics.

## Data flow

1. `hidden index/search/suggest` builds visible records from the existing index and hidden records from `visibility-disabled`.
2. Alias expansion adds deterministic candidate boosts for `grill-me`, `stop-slop`, `deslop`, and `anti-slop`.
3. `hidden show` returns compact metadata for one record.
4. `hidden load` reads one selected `SKILL.md`, returns the body or chunk, and appends a JSONL usage event.
5. `visibility recommend` reads usage events plus current visible standalone user skills and returns promote/demote/keep-soft-load buckets.
6. `visibility apply-recommendations` loads a prior recommendation receipt, checks the daily apply guard, writes a rollback receipt, and moves at most three directories.

## Safety

All commands must report non-mutation flags. Apply commands may move standalone user skill directories only when `--apply` and `--operator-confirmation` are present. Plugin cache, repo skills, system skills, and `config.toml` are never mutation targets.
