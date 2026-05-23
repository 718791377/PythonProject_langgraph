# Design: Fresh-read documentation refresh

## Source Reading Design
Fresh extraction is performed before tracked documentation edits:

- PDF files are iterated page by page.
- EPUB files are iterated by spine item.
- Markdown files are read in full.
- Extraction artifacts are stored in ignored `.omx/state/langgraph/extraction/` files.
- Tracked docs cite source families, coverage, and repository-specific synthesis only; they do not reproduce long copyrighted source passages.

The current extraction run produced:

- 54 source files.
- 31 PDF files, 9 EPUB files, and 14 Markdown files.
- 9,665 read units.
- Approximately 19,043,382 extracted text characters.

## Documentation Structure
Keep these document classes distinct:

- Whitepaper: narrative and cognitive framing for why the platform exists.
- Governance research: evidence and capability canon for maintainable production persistent teams.
- Product lifecycle docs: operating model, document lifecycle, target inventories, and tailoring rules.
- MRD/plan/playbook: demand, implementation north-star, and execution guidance.

The research and whitepaper should not be hard-merged during this change. Instead, the docs should include a bridge:

- The 10-layer research model is the capability core.
- The 12-layer lifecycle model adds product/governance/document-system and learning/adoption layers around that core.

## Tailoring Design
Architecture depth is selected by risk, uncertainty, coupling, and lifecycle impact:

- Full architecture for systemic, durable-state, trust, compliance, customer, release, or multi-project impact.
- Whole-project lightweight for a bounded project where all work can safely use a reduced document set.
- Phase-local lightweight for low-risk phases inside an otherwise governed project.
- Module-level lightweight for isolated, reversible module work.
- Hybrid when high-risk parts need full governance while low-risk modules or phases can remain lightweight.

Execution-facing gates and layer guidance must use Inputs / Tools And Techniques / Outputs.

## Orchestration Design
A frozen brief exists under `.omx/state/langgraph/briefs/`. Because the frozen plan has multiple independent slices, LangGraph durable workflow was selected for this task flow. The main Codex session remains the leader and owns fan-in and final integration.

## Validation
Before completion, run OpenSpec validation/guard checks and repository documentation checkers. Before commit, run the pre-commit update/archive review. Local CI and local MR review are required before integration or remote publication, unless explicitly deferred by the user.
