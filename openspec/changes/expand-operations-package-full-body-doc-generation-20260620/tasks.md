# Tasks: Expand Operations Packages To Full Body Document Generation

## Stage A: Freeze plan and contract

- [x] Create this OpenSpec change with proposal, design, management, tasks, and delta specs.
- [x] Create the bilingual full-body implementation plan.
- [x] Register the full-body implementation plan in `docs_bilingual/docs_registry.yaml`.
- [ ] Validate Stage A.
- [ ] Commit Stage A and integrate it into local `main`.

## Stage B: Implement live runtime and generated body layer

- [ ] Extend `tools/generate_operations_package.py` to generate the 48/60 body layer under `docs_bilingual/operations_packages/`.
- [ ] Extend `tools/check_operations_package_docs.py` to validate body counts, bilingual pairs, registry coverage, I/T/O order and non-empty content, tailoring modes, encoding, and package isolation.
- [ ] Extend `test/operations_package_docs.test.py` with full-body count, pairing, I/T/O, tailoring, registry, write-mode idempotency, and contamination negative tests.
- [ ] Generate Codex durable-team body documents: 48 English primary files and 48 zh-CN companions.
- [ ] Generate one-person-company body documents: 60 English primary files and 60 zh-CN companions.
- [ ] Register every generated body document pair in `docs_bilingual/docs_registry.yaml`.
- [ ] Run focused package checks and tests.
- [ ] Run OpenSpec, repository guard, local CI, and local MR review gates.
- [ ] Commit Stage B and integrate it into local `main`.
- [ ] Archive the OpenSpec change after Stage B is verified and stable specs are synced.

## Remote publication

- [ ] Stop at the remote-publication gate unless the user explicitly authorizes GitLab/GitHub publication.
