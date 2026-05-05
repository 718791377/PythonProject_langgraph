# Design: Lifecycle MRD stack alignment

## Placement

`docs_bilingual/whitepapers/` is the white-paper directory; it holds cognitive-narrative documents.

`docs_bilingual/market_requirements/` is the MRD directory; it holds market-requirements documents and their appendices.

`docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` remains the North Star and implementation-bridge plan; it is not renamed in this change.

## Merge Decision

The former capability-profile file is physically merged into the MRD and logically separated as Appendix A. This keeps cold-start reading simpler while preserving the query-table structure.
