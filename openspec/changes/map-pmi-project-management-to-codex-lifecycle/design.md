# Design

## Placement

The new `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.md` file is the ASCII main reference for PMI mapping. The matching `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.zh-CN.md` file is the UTF-8 Chinese companion.

The platform-build lifecycle pair receives a short PMI tailoring overlay section. It points to the dedicated PMI map instead of duplicating the full mapping.

## Reference Boundary

The local `PMP/` directory is reference-only and remains ignored by Git. The repository may summarize how PMI concepts map to this project, but it must not reproduce PMI book content or track local PDF files.

## Mapping Model

The mapping has three layers:

1. PMBOK value and principles guidance maps to value delivery, tailoring, governance, success criteria, and quality gates.
2. Process Groups guidance maps to OpenSpec and GitLab-first delivery gates: initiating, planning, executing, monitoring and controlling, and closing.
3. Agile guidance maps to exploratory work, MVP slices, short feedback loops, and hybrid delivery decisions.

## Downstream Boundary

The platform repository may define shared project-management templates and governance checks. Downstream projects own their own project charter, risk register, issue log, release plan, rollback plan, and lessons learned when those files are needed.

## Validation

Validation uses OpenSpec and repository documentation checkers. No runtime services are started.
