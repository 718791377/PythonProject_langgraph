# Design: PMI And Business Product Lifecycle Refresh

## Boundaries

This change is documentation-only. It does not change launchers, wrappers, checkers, CI, MCP configuration, durable state, or user-level skill installation.

The source directories `Business Management/` and `PMP/` are ignored local reference directories. The implementation may use local extraction outputs for coverage and synthesis, but it must not commit raw source text, extracted page text, OCR output, or copyrighted book excerpts.

## Source Intake

Local intake uses three granularities:

- PDF files: page iteration, page count, text metrics, and low-text page OCR review when extractable text is low.
- EPUB files: OPF spine order, one extracted text artifact per spine item.
- Markdown files: full UTF-8 text read with heading inventory.

Repository docs may cite counts, file names, and synthesized operating principles. They must not quote long passages from source material.

## Document Model

The refreshed model keeps the existing 0-11 / 12-layer trunk:

0. Cognitive narrative
1. Business
2. Market
3. Strategy
4. Metrics
5. Product
6. Technical
7. Organization
8. Execution
9. Growth
10. Operations
11. Retrospective

The Codex CLI personal production durable-team target adds:

- 4 virtual departments
- 24 responsibility domains
- 18 cross-cutting modules
- 48 core documents
- 12 governed AI agents
- 12 recommended books

The one-person-company operating-system target adds:

- 5 virtual departments
- 30 responsibility domains
- 20 cross-cutting modules
- 60 core documents
- 15 governed AI agents
- 15 recommended books
- 12 minimal startup documents

## Process-Group Style

Execution-facing lifecycle guidance uses `Inputs`, `Tools and Techniques`, and `Outputs`. PMI process groups are used as a delivery overlay:

- Initiating: charter, scope, stakeholders, expected value, and authorization.
- Planning: requirements, tailoring, risk, schedule, quality, communications, validation, release, and rollback plans.
- Executing: produce the selected increment and manage team or agent work.
- Monitoring and Controlling: inspect metrics, risks, quality, change requests, issue state, and acceptance evidence.
- Closing: archive evidence, update stable specs/docs, capture lessons learned, release or retire work, and feed reusable lessons back into governance.

## Documentation Targets

- `docs_bilingual/product_lifecycle/` remains the main lifecycle map.
- `docs_bilingual/whitepapers/` carries the Codex platform cognitive narrative.
- `docs_bilingual/market_requirements/` carries market/user/capability profiles.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.*` remains a North Star and implementation-bridge draft, not runtime completion evidence.

## Validation

Run the normal repository documentation and OpenSpec gates:

- `openspec validate --all` - validates every active change and stable spec.
- `python .\tools\run_openspec_guard.py --root .` - runs the repository OpenSpec governance guard.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1` - runs the shared local CI gate used by local and remote CI.
