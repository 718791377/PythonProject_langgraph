# Change: Add Lifecycle Tailoring Rules

## Why

The current lifecycle refresh already records the two 12-layer target architectures and the PMI process-group writing rule. The remaining gap is an explicit tailoring rule that answers when to use the full architecture, when to use a lightweight architecture, and whether lightening applies to the whole project, only a phase, or only a module.

Without this rule, maintainers may either overbuild documents for small low-risk work or under-govern high-risk platform, product, compliance, payment, trust, or long-lived architecture changes.

## What Changes

- Add a bilingual lifecycle-tailoring rules document under `docs_bilingual/product_lifecycle/`.
- Link the tailoring decision model from the general lifecycle, Codex platform lifecycle, downstream project lifecycle, PMI reference map, white paper, MRD, and North Star plan.
- Define process-group style tailoring gates with Inputs, Tools and Techniques, and Outputs.
- Define full-architecture triggers, whole-project lightweight eligibility, phase/local lightweight eligibility, module-level lightweight eligibility, and escalation rules.
- Keep the update source-backed by the existing local `Business Management/` and `PMP/` extraction coverage while avoiding raw source text or long copyrighted excerpts.

## Impact

- Documentation-only change under `docs_bilingual/` and the product-lifecycle OpenSpec spec.
- No launcher, wrapper, checker, CI, MCP, skill, or durable-state runtime behavior changes.
- Ignored extraction artifacts, raw book text, OCR output, and local reference directories remain outside tracked Git files.
