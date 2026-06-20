# Design: Full Body Operations Package Generation

## Decision

Stage B will extend the existing operations-package runtime into a full-body document generator. The current register/governance documents stay intact; the new full-body layer is added under `docs_bilingual/operations_packages/`.

## Document Count Contract

The body-document counts are exact generated primary-document counts:

| Package | English body documents | zh-CN companions | Body files |
| --- | ---: | ---: | ---: |
| Codex durable team | 48 | 48 | 96 |
| One-person company | 60 | 60 | 120 |
| Total body layer | 108 | 108 | 216 |

The existing governance/register package documents remain generated and checked. Stage B may report total generated files as the old governance/register layer plus the 216 new body files, but the 48/60 acceptance gate is the body layer.

## Path Design

The generated body layer uses package-specific roots:

- `docs_bilingual/operations_packages/codex_cli_durable_team/<family>/<document>.md` - stores each Codex English body primary document.
- `docs_bilingual/operations_packages/codex_cli_durable_team/<family>/<document>.zh-CN.md` - stores each Codex Chinese body companion document.
- `docs_bilingual/operations_packages/one_person_company/<family>/<document>.md` - stores each one-person-company English body primary document.
- `docs_bilingual/operations_packages/one_person_company/<family>/<document>.zh-CN.md` - stores each one-person-company Chinese body companion document.

The `<family>` segment is derived from the current 8 Codex six-document families and 10 one-person-company six-document families. Filenames are derived from the tracked core-document lists.

## Body Document Structure

Every generated body document must contain:

- YAML front matter with `doc_id`, `doc_class`, `status`, `package`, `body_kind`, `generated_by`, and `lang`.
- A generated marker.
- Purpose / authority boundary.
- Package inventory summary.
- 12-layer placement.
- Tailoring Rules.
- Inputs.
- Tools And Techniques.
- Outputs.
- Process Group Operating Table.
- Closeout / registry note.

Chinese companions must include `translation_of` and localized headings for purpose, tailoring, input, tools/techniques, output, and process groups.

## Tailoring Rules

The body layer keeps five modes:

1. Full architecture.
2. Whole-project lightweight.
3. Phase-local lightweight.
4. Module-level lightweight.
5. Hybrid architecture.

Each generated body document must state why the selected or default mode is not heavier or lighter and must list escalation triggers. The checker must reject missing tailoring modes, missing rationale, or missing escalation trigger language.

## Process-Group Style

Execution-facing flow text must use a process-group grammar. For each generated body document:

- Inputs define the source evidence, risk profile, owner, constraints, and current work state.
- Tools And Techniques define lifecycle mapping, PMI process-group analysis, agile feedback, RACI, checkers, local CI, and review methods.
- Outputs define the document artifact, registry entry, validation evidence, tailoring decision, owner, closeout, and remote-publication stop point.

## Write Scope

Stage B may edit only:

- `tools/generate_operations_package.py` - renders full-body documents from tracked package authorities.
- `tools/check_operations_package_docs.py` - validates generated body counts, structure, registry, tailoring, encoding, and package isolation.
- `test/operations_package_docs.test.py` - proves the generator and checker behavior with focused regression tests.
- `docs_bilingual/docs_registry.yaml` - records generated body documents as first class bilingual artifacts.
- generated files under `docs_bilingual/operations_packages/` - hold the body layer produced by the generator.

Stage B must not edit `.omx/state/`, LangGraph durable orchestrator source, launcher routing, or unrelated governance scripts.

## Validation Strategy

Stage B checks must prove:

- 48 Codex body primary documents and 48 zh-CN companions exist.
- 60 one-person-company body primary documents and 60 zh-CN companions exist.
- Body document `doc_id`, path, and registry entries are unique.
- Every body document has I/T/O sections in order and with non-empty content.
- Every body document has all five tailoring modes and escalation trigger language.
- English primary files remain ASCII-only.
- Chinese companions are strict UTF-8 and contain no replacement characters.
- Package contamination checks keep Codex-only and one-person-company-only semantics separated.
- Generator write mode is idempotent and package-specific modes do not write the other package.
