---
change_id: generate-operations-package-runtime-20260620
status: proposed
owner: codex
created_at: 2026-06-20
---

# Design: Operations Package Generation And Runtime

## Authority Boundary

Stage B treats existing white papers, North Stars, inventory maps, tailoring rules, the PMI reference map, and the process-group contract as source authorities. The new operations package sits below those sources as an executable layer: document-system maps, registers, RACI maps, agent catalogs, tailoring decision trees, and process-group playbooks.

## Stage A / Stage B Split

Stage A freezes the contract only: OpenSpec change artifacts, a bilingual implementation plan, and a `docs_bilingual/docs_registry.yaml` entry. Stage A does not change runtime helpers, checkers, tests, generated operations package files, or CI manifests.

Stage B implements the frozen contract:

- `tools/generate_operations_package.py` creates deterministic bilingual operations-package documents.
- `tools/check_operations_package_docs.py` validates generated package coverage, I/T/O sections, tailoring rules, and registry references.
- `test/operations_package_docs.test.py` covers generator and checker behavior.
- `tools/ci/ci_test_manifest.json` registers the new test.
- `docs_bilingual/docs_registry.yaml` registers generated document pairs.

## Generated Operations Package Scope

Codex durable-team package documents include BRD, PRD, template update policy, 48 core documents register, 24 responsibility domains RACI, 12 governed AI agents catalog, 18 cross-cutting modules map, 12 reference books map, 4 virtual departments operating map, document generation order, and operating slice template.

One-person-company package documents include operations document system map, tailoring decision tree, 12 minimal startup documents guide, 60 core documents register, 30 responsibility domains RACI, 15 governed AI agents catalog, 20 cross-cutting modules map, PMI process-group playbook, architecture mode selection guide, and operations metrics/monthly review package.

## Tailoring Modes

The checker and generated documents preserve these architecture mode definitions: full architecture, whole-project lightweight, phase-local lightweight, module-level lightweight, and hybrid architecture. Every tailoring decision records why the chosen mode is not heavier or lighter and lists escalation triggers.

## Process-Group I/T/O Contract

Every execution-facing generated document contains explicit process-group sections. English files use `Inputs`, `Tools And Techniques`, and `Outputs`; Chinese companions use equivalent localized headings.

## Collaboration And Runtime Lane

Stage A remains leader-owned with advisory experts because the frozen plan does not yet exist. After Stage A lands on local `main`, Stage B is eligible for durable/persistent execution because it has at least two independent slices: runtime/checker/test and generated docs/registry.
