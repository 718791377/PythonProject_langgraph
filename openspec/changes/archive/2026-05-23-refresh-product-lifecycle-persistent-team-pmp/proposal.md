# Proposal: Refresh product lifecycle, persistent-team, and PMI tailoring docs

## Why
The repository now uses the product-lifecycle documentation as the bridge between Codex CLI personal production durable-team governance, downstream one-person-company operating models, and PMI-style delivery discipline. The user requested a fresh read of the ignored `Business Management/` and `PMP/` libraries and explicitly asked not to rely on old cached extraction results. Existing docs already declare many target inventory counts, but the concrete inventory maps, whitepaper/research relationship, and PMI tailoring rules need a synchronized refresh.

## What Changes
- Regenerate ignored extraction evidence from local sources: PDF pages, EPUB spine items, and Markdown full text.
- Update lifecycle references with the two canonical target inventories:
  - Codex CLI personal production durable team: 12 trunk layers, 4 virtual departments, 24 responsibility domains, 18 cross-cutting modules, 48 core documents, 12 governed AI agents, and 12 recommended books.
  - Personal production one-person-company operating system: 12 trunk layers, 5 virtual departments, 30 responsibility domains, 20 cross-cutting modules, 60 core documents, 15 governed AI agents, 15 recommended books, and 12 minimal startup documents.
- Clarify the relationship between the governance research document and the platform whitepaper, including the 10-layer-to-12-layer bridge and the merge policy.
- Strengthen PMI/PMBOK, Program, Portfolio, PMO, Agile, and Process Groups tailoring guidance.
- Ensure execution-facing guidance uses Inputs / Tools And Techniques / Outputs structure.
- Add missing inventory map documents where the existing lifecycle stack only declares counts.

## Capabilities
- codex-product-lifecycle-document-governance
- codex-cli-personal-production-durable-team-plan

## Impact
- Tracked docs under `docs_bilingual/product_lifecycle/`, `docs_bilingual/whitepapers/`, `docs_bilingual/governance/`, `docs_bilingual/implementation_plans/`, and `docs_bilingual/market_requirements/` may be updated.
- Ignored extraction artifacts are written under `.omx/state/langgraph/extraction/` and are not committed.
- `Business Management/` and `PMP/` remain ignored local reference directories.
- No runtime behavior, launcher behavior, or remote publication flow changes are intended.
