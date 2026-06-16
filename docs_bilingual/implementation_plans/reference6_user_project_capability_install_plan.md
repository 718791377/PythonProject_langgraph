---
doc_id: reference6_user_project_capability_install_plan
lang: en
doc_class: implementation_plan
status: active
---

# Reference 6 User/Project Capability Install Plan

## Goal

Install or register the capabilities listed in `reference_files/6.md` through a layered model and propagate reusable entrypoints to `D:\PythonProject_General` and `D:\PythonProject_General_2`.

Reference set:

- `https://github.com/nexu-io/open-design` - open design-to-code capability reference for reusable UI/design conversion.
- `https://github.com/nexu-io/html-anything` - HTML-to-structured-output capability reference for reusable conversion flows.
- `https://github.com/browserbase/skills` - Browserbase skill collection reference for browser automation skill packaging.
- `https://github.com/pymupdf/pymupdf` - PyMuPDF source reference for PDF parsing and rendering capability.
- `https://github.com/opendatalab/MinerU` - MinerU source reference for document intelligence and extraction capability.
- `https://mineru.net/apiManage/limit` - MinerU API quota page reference for live-service readiness and blocker receipts.
- `https://mineru.net/` - MinerU service home reference for account and API capability discovery.
- `https://github.com/virgiliojr94/book-to-skill` - book-to-skill source reference for reusable skill generation from long-form documents.
- `https://github.com/mattpocock/skills` - reusable skill examples reference for Codex/Superpowers-compatible skill packaging.

## Current Status

<!-- CURRENT_STATUS_START -->

- 2026-06-16: Plan opened from `reference_files/6.md`; implementation has not yet run.
- Default decision: layered install, Codex-provider env-key reuse, redacted receipts, and no remote publication.

<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->

- [ ] Create user-level reference6 manifest, installer, smoke script, and receipt writer.
- [ ] Install or register the seven reference capabilities with pinned version or commit evidence where possible.
- [ ] Run user-level smoke tests and record explicit remediation for missing external prerequisites.
- [ ] Update `D:\PythonProject_General` with active reusable policy/checker/example config.
- [ ] Update `D:\PythonProject_General_2` with inert upgrade policy/checker/example manifest.
- [ ] Validate source, user-level, General, and General_2 gates; integrate local main and stop before remote publication.

<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->

| Evidence item | Expected path or command | Status |
| --- | --- | --- |
| Plan registration | `docs_bilingual/docs_registry.yaml` | planned in this change |
| Reference source list | `reference_files/6.md` | captured in this plan |
| User-level install receipt | user-level reference6 receipt JSON | pending implementation |
| Source validation | `python tools\run_openspec_guard.py --root . --json` | pending implementation |
| General validation | `tools\ci\local_gate.ps1 -Root D:\PythonProject_General -Json` | pending implementation |
| General_2 validation | `tools\ci\local_gate.ps1 -Root D:\PythonProject_General_2 -Json` | pending implementation |

<!-- EVIDENCE_INDEX_END -->

## Layering decision

- User-level layer: install or register reusable CLI, Python package, Node/GitHub source, skills, smoke scripts, manifest, and receipts under the user Codex/tooling surface.
- `D:\PythonProject_General`: active reusable project template entries, policy, checker, and example config. It may expose opt-in active helpers but must not commit credentials, account state, caches, browser sessions, or external action evidence.
- `D:\PythonProject_General_2`: conservative inert upgrade entries only. It must not activate user-level installs, live API calls, browser automation, remote publication, OMX/LangGraph, or R6 live runtime by default.

## API key policy

- Prefer the same provider/key shape as Codex `C:\Users\lenovo\.codex\config.toml`.
- Reuse the configured provider `env_key` by environment-variable name only; never copy or write the secret value.
- If Browserbase, MinerU, OpenAI-compatible, or other external services require dedicated keys, read only existing environment variables and validate presence with redacted receipts.
- No receipt, manifest, template, test output, or log may contain secret values.

## Blocker protocol

Implementation must not leave unresolved blockers as done. For every blocker, record:

1. what is missing,
2. exact user or operator command to fill it without revealing secrets,
3. a redacted verification command,
4. the next resume step.

Known preflight risks:

- GitHub HTTPS may fail on this host with Windows Schannel credential errors; retry with SSH remotes or a fixed Git TLS/credential setup before declaring a GitHub source installed.
- `uv` and `pnpm` may be absent; use Python venv/pip and npm/npx unless the upstream package requires otherwise.
- `mineru` and `browserbase` API smoke may require service-specific environment variables.

## Implementation tasks

1. Create user-level reference6 manifest, installer, smoke script, and receipt writer.
2. Install/register PyMuPDF, MinerU, book-to-skill, open-design, html-anything, Browserbase skills, and mattpocock skills using pinned versions or recorded commit hashes where available.
3. Run user-level smoke tests:
   - PyMuPDF import.
   - MinerU CLI/import and, when key exists, minimal API smoke.
   - book-to-skill import/help.
   - Node/GitHub projects help/readme/entrypoint smoke.
4. Update `D:\PythonProject_General` with active reusable policy/checker/example config and local-gate wiring.
5. Update `D:\PythonProject_General_2` with inert upgrade policy/checker/example manifest and local-gate wiring.
6. Validate all touched repositories and stop before remote publication.

## Verification gates

- Source repo: `python tools\run_openspec_guard.py --root . --json`, relevant checker/tests, `tools\ci\local_gate.ps1`, `tools\ci\local_mr_review.ps1`.
- User-level: manifest parse, receipt redaction check, import/help/API-smoke checks according to available keys.
- General: new reference6 checker, `tools\ci\local_gate.ps1 -Root . -Json`, local MR review.
- General_2: inert checker, `tools\ci\local_gate.ps1 -Root . -Json`, local MR review.

## Completion criteria

- Source repo plan and implementation commits are merged into local `main`.
- User-level reference6 installation has redacted receipts and either successful smoke evidence or explicit blocker instructions for missing external prerequisites.
- General and General_2 are updated on local `main`, clean, and locally validated.
- No remote publication is performed without explicit remote-publish wording.
