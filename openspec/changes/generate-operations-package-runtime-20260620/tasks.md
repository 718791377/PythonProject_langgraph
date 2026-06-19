# Tasks: Generate Operations Package Runtime

## Stage A: Freeze plan

- [x] Create the OpenSpec change artifacts for operations-package generation.
- [x] Create the bilingual implementation plan under `docs_bilingual/implementation_plans/`.
- [x] Register the Stage A implementation plan in `docs_bilingual/docs_registry.yaml`.
- [x] Validate, commit, and integrate the Stage A plan-freeze package into local `main`.

## Stage B: Implement live runtime and generated package

- [x] Create `tools/generate_operations_package.py` with deterministic bilingual document generation.
- [x] Create `tools/check_operations_package_docs.py` for package, tailoring, I/T/O, and registry validation.
- [x] Create generated Codex durable-team operations-package document pairs.
- [x] Create generated one-person-company operations-package document pairs.
- [x] Register generated document pairs and the new checker/test in repository indexes.
- [x] Add `test/operations_package_docs.test.py` and register it in `tools/ci/ci_test_manifest.json`.
- [ ] Validate focused tests, OpenSpec, local gate, local MR review, and local-main integration.
- [ ] Archive the OpenSpec change only after Stage B runtime behavior is verified and locally integrated.
