# Design: Fresh Source Lifecycle, Whitepaper, North Star, And PMI Tailoring Refresh

## Decisions

1. Keep raw source extraction local and ignored. Tracked documents record counts, statuses, hashes, source-to-document mappings, and synthesis only.
2. Treat the two target systems as parallel lifecycle profiles, not maturity levels of one profile.
3. Keep the whitepaper and research note physically separate. The whitepaper owns strategic narrative; the research note owns production-capability evidence and stricter governance reasoning.
4. Use PMBOK 8 and current PMI practice guides as primary delivery-governance inputs, while older PMBOK/process-group/agile/program/portfolio sources provide historical and execution overlays.
5. Execution-facing lifecycle content must use process-group style: Inputs, Tools and Techniques, Outputs.

## Extraction Architecture

The tool enumerates source files under `Business Management/` and `PMP/` in a supplied source root. It writes:

- `fresh_source_manifest.json` - run metadata, source inventory, counts, hashes, and status.
- `fresh_source_items.jsonl` - one record per PDF page, EPUB spine item, or Markdown full document.
- `fresh_source_synthesis.json` - compact derived mapping counts and keyword evidence for tracked-document refresh.
- `fresh_source_report.md` and `.zh-CN.md` - human-readable local evidence summaries.

PDF extraction uses `pypdf` first and falls back to PyMuPDF/fitz for files or pages where `pypdf` fails. EPUB extraction follows spine order and skips navigation entries only as marked metadata. Markdown extraction reads the whole file as UTF-8 with fallback to UTF-8-SIG.

## Document Architecture

- Source synthesis documents explain fresh-read coverage and source-family roles.
- Inventory maps remain the numerical authority for the two target profiles.
- Lifecycle docs apply those profiles to Codex platform build and downstream consumption.
- PMI reference and tailoring docs define when to use full, whole-project lightweight, phase-local lightweight, module-level lightweight, or hybrid architecture.
- Whitepaper/research/North Star summarize the bridge and point to detailed lifecycle docs.
- The implementation rerun uses evidence run `fresh-source-lifecycle-whitepaper-pmi-refresh-20260614` generated at `2026-06-14T10:48:53Z`. The OpenSpec change id remains the original `fresh-source-lifecycle-whitepaper-pmi-refresh-20260613` package id.
- The 10-to-12 layer bridge is a bridge-time aggregation, not a replacement for the research note's canonical 10-layer runtime list.
- Execution-facing additions delegate detailed I/T/O authority to lifecycle and PMI mapping documents instead of duplicating process grammar inside the whitepaper or North Star plan.

## Risk Controls

- Stale cache references must be rewritten as historical/non-current evidence.
- No tracked raw source text is committed.
- Bilingual documents are updated in paired English and zh-CN form.
- Chinese text must be written and validated as UTF-8; mojibake/three ASCII question mark additions are release blockers.
- Count constraints are explicitly validated in text and, where practical, by script checks.
