---
change: sync-durable-team-spec-12-layer-20260615
design-doc: docs/superpowers/specs/2026-06-15-durable-team-corpus-sync-design.md
base-ref: 516b4786aa3bffa5e42a96aafe9cdb20ba7aa32f
---

# Plan: Sync Durable-Team Spec And Core Corpus Checkpoint

## Scope

Docs-only synchronization for the core `codex_cli_personal_production_durable_team` corpus and stable OpenSpec requirement.

## Tasks

1. Update OpenSpec artifacts and stable/delta specs.
2. Add a 2026-06-15 corpus sync checkpoint to the core durable-team document family.
3. Run targeted validation and commit the bounded slice.

## Validation

- `openspec validate sync-durable-team-spec-12-layer-20260615 --strict --json`
- `openspec validate --all`
- `python tools/check_document_pair_policy.py --root . --json`
- `python tools/check_startup_instruction_mojibake.py --root . --json`
- `python tools/check_name_clarity_rules.py --root . --json`
- `python tools/check_precommit_update_archive.py --root . --json`
