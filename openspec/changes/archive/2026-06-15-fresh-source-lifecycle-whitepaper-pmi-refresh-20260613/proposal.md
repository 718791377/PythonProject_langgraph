# Change: Fresh Source Lifecycle, Whitepaper, North Star, And PMI Tailoring Refresh

## Why

The product lifecycle, whitepaper, research, and North Star documents currently cite a prior ignored extraction cache. The current request requires a fresh read of local `Business Management/` and `PMP/` sources before refreshing tracked documents, and it also asks to clarify the relationship between the 10-layer runtime research model and the 12-layer product/business lifecycle model.

## What Changes

- Add a reusable fresh-source extraction tool that reads PDFs by page, EPUBs by spine item, and Markdown files as full documents.
- Generate a new ignored local extraction cache and summary manifest for this refresh. The current implementation rerun is `fresh-source-lifecycle-whitepaper-pmi-refresh-20260614`, generated at `2026-06-14T10:48:53Z`; the OpenSpec change id remains `fresh-source-lifecycle-whitepaper-pmi-refresh-20260613` as the governed change package name.
- Refresh bilingual product lifecycle documents, the Codex durable-team whitepaper, the solo-maintainable research note, and the North Star plan so they reference the new evidence run and avoid treating old cache as current truth.
- Add the minimum bridge/index documents needed to make source evidence, 10-to-12-layer mapping, and PMI tailoring decisions auditable.

## Scope

- `tools/fresh_extract_sources.py` - extraction and evidence-manifest tool.
- `docs_bilingual/product_lifecycle/` - lifecycle, inventory, source synthesis, PMI reference, and tailoring documents.
- `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.*` - strategic whitepaper relationship and evidence refresh.
- `docs_bilingual/governance/solo_maintainable_production_persistent_team_research.*` - research-note relationship and 10-to-12-layer bridge refresh.
- `docs_bilingual/north_star_plan.*` - metrics and evidence refresh.
- This OpenSpec change package.

## Non-Goals

- Do not commit raw extracted source text or copyrighted book text.
- Do not use the previous `.omx/state/langgraph/extraction/` cache as current content evidence.
- Do not merge the whitepaper and research note into one physical file.
- Do not change remote publication state.

## Rollout

1. Create the governed change package and isolated worktree.
2. Implement and run fresh extraction into ignored local cache.
3. Refresh bilingual docs using only derived summary evidence and source-to-document mappings.
4. Validate extraction coverage, quantity constraints, stale-cache wording, bilingual pair consistency, OpenSpec guard, and local gates.
5. Commit the package and use the local-main-first flow only after validation.

## Rollback

- Revert the feature branch or local main merge commit.
- Delete the ignored local `.omx/state/langgraph/extraction/fresh-source-lifecycle-whitepaper-pmi-refresh-20260614/` cache if needed.
- No remote, external, or downstream project state is modified by this change.

## Verification

- `python tools/fresh_extract_sources.py --source-root D:/PythonProject_langgraph --output-root ./.omx/state/langgraph/extraction/fresh-source-lifecycle-whitepaper-pmi-refresh-20260614 --run-id fresh-source-lifecycle-whitepaper-pmi-refresh-20260614 --summary-only` - confirms source inventory counts without rewriting tracked conclusions.
- `python tools/fresh_extract_sources.py --source-root D:/PythonProject_langgraph --output-root ./.omx/state/langgraph/extraction/fresh-source-lifecycle-whitepaper-pmi-refresh-20260614 --run-id fresh-source-lifecycle-whitepaper-pmi-refresh-20260614` - regenerates the ignored full extraction evidence cache.
- `openspec validate fresh-source-lifecycle-whitepaper-pmi-refresh-20260613 --strict` - validates this OpenSpec change package.
- `python tools/run_openspec_guard.py --root .` - verifies repository OpenSpec and documentation-governance guard rules.
- `python tools/check_precommit_update_archive.py --root . --json` - verifies pre-commit update/archive readiness.
- `$env:PYTHONUTF8="1"; $env:PYTHONIOENCODING="utf-8"; powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1 -StepTimeoutSeconds 1800` - runs the shared local CI gate before integration.
