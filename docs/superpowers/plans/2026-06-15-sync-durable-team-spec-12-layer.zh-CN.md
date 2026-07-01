---
change: sync-durable-team-spec-12-layer-20260615
design-doc: docs/superpowers/specs/2026-06-15-durable-team-corpus-sync-design.md
base-ref: 516b4786aa3bffa5e42a96aafe9cdb20ba7aa32f
translation_of: docs/superpowers/plans/2026-06-15-sync-durable-team-spec-12-layer.md
archived-with: 2026-06-15-sync-durable-team-spec-12-layer-20260615
---

# 计划：同步持久化团队规格与核心文档族检查点

## 范围

面向核心 `codex_cli_personal_production_durable_team` 文档族与稳定 OpenSpec requirement 的 docs-only synchronization。

## 任务

1. 更新 OpenSpec artifacts 和稳定/增量规格。
2. 在核心 durable-team 文档族中加入 2026-06-15 corpus sync checkpoint。
3. 运行 targeted validation 并提交 bounded slice。

## 验证

- `openspec validate sync-durable-team-spec-12-layer-20260615 --strict --json`
- `openspec validate --all`
- `python tools/check_document_pair_policy.py --root . --json`
- `python tools/check_startup_instruction_mojibake.py --root . --json`
- `python tools/check_name_clarity_rules.py --root . --json`
- `python tools/check_precommit_update_archive.py --root . --json`
