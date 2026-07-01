---
doc_id: user_level_cloakbrowser_academic_research_runtime_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/user_level_cloakbrowser_academic_research_runtime_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/user_level_mcp_skills_cli_runtime_plan.md
---

# User-Level CloakBrowser and Academic Research Runtime Plan

> **For agentic workers:** use `superpowers:executing-plans`; use `superpowers:test-driven-development` for checker changes. This plan owns only the user-level installation/runtime evidence for CloakBrowser, CloakBrowser-Manager, and `academic-research-suite` Codex skill. It does not own WXWork, CLI-Anything, existing Browser/CLI adapter lanes, or remote publication.

## Goal

Install and verify three user-level capability surfaces with receipt-backed, hash-only evidence:

- CloakBrowser wrapper runtime from `https://github.com/CloakHQ/CloakBrowser`.
- CloakBrowser-Manager source/runtime boundary from `https://github.com/CloakHQ/CloakBrowser-Manager`.
- Academic Research Skills for Codex from `https://github.com/Imbad0202/academic-research-skills-codex`, installed as the single `academic-research-suite` skill.

## Architecture

Repo-local governance comes first: this repository records the plan, checker, tests, CI registration, and OpenSpec guard wiring. User-level installs are install artifacts only and live under explicit user-level roots such as `C:\Users\lenovo\.codex` or isolated tool/cache roots. Runtime receipts must be hash-only, omit raw paths and raw command transcripts, preserve rollback pointers by hash, and record that remote publication remains unauthorized.

The governance priority order is `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`. Native Codex files are not modified, Codex direct MCP config is not mutated, and generated wrappers must stay outside native Codex launcher surfaces.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: R6 live-executed
Stage: R6 live-executed CloakBrowser-Manager non-Docker source-backend-frontend-loopback runtime.
Current gate: `cloakbrowser-manager-source-runtime.json` is recorded and checker-accepted with `/api/status` HTTP 200 JSON, `/` GUI shell HTML, `container_runtime_used=false`, and `docker_install_allowed=false`; run focused validation, local CI, and local MR review before integrating this Stage B package into local `main`.
Docker boundary: Docker is not installed by this plan. Podman, WSL container engines, and Docker Compose are also out of scope; CloakBrowser-Manager must be exercised from source without a container runtime.
Runtime boundary: native Codex files are not modified, receipts do not store raw paths, and remote publication remains unauthorized.
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-11
<!-- CURRENT_STATUS_END -->

## Source References

| Capability | Source | Pin/version target | User-level action |
| --- | --- | --- | --- |
| CloakBrowser Python | `https://github.com/CloakHQ/CloakBrowser` / PyPI `cloakbrowser` | `cloakbrowser==0.3.31` | install into isolated user-level Python venv, run import/help/version smoke, record R6 live-executed receipt |
| CloakBrowser npm | `https://github.com/CloakHQ/CloakBrowser` / npm `cloakbrowser` | `cloakbrowser@0.3.31` | optional user-level npm/local-prefix install, run package/version/import smoke, record R6 live-executed or blocked receipt |
| CloakBrowser-Manager | `https://github.com/CloakHQ/CloakBrowser-Manager` | source `main` commit hash from execution time | clone/copy source metadata and config boundary; Docker is not installed by this plan; then run a non-Docker source-backend-frontend-loopback smoke from the checked-out source |
| Academic Research Skills Codex | `https://github.com/Imbad0202/academic-research-skills-codex` | `0.1.11`, path `skills/academic-research-suite` | install into `C:\Users\lenovo\.codex\skills\academic-research-suite`; verify one ARS entry only |

## Runtime Stages

| Stage | Allowed action | Evidence |
| --- | --- | --- |
| R6 live-ready | Resolve tools, versions, paths, and rollback targets without performing install/start. | checker output, planned command hashes, authorization boundary |
| R6 live-executed | Perform user-level install/smoke where dependencies exist. | one JSON receipt per capability with source URL/ref, version, hash-only install/wrapper/state/rollback fields, smoke result, redaction status |
| R6 live-executed: source-backend-frontend-loopback | Run CloakBrowser-Manager backend and built frontend from source on loopback without Docker/Podman/WSL containers. | `cloakbrowser-manager-source-runtime.json` with `container_runtime_used=false`, `docker_install_allowed=false`, `smoke_kind=source-backend-frontend-loopback`, `/api/status` HTTP 200 JSON, `/` GUI shell HTML, and `profile_launch_smoke=not_run:no_xvnc_on_windows` |
| R6 blocked | Record honest blocked evidence for missing dependency such as Docker. | blocker name, no action performed, rollback/cleanup not needed or prepared, no raw paths |

## Implementation Tasks

<!-- TASK_BACKLOG_START -->
- [x] Create a dedicated checker `tools/check_user_level_cloakbrowser_academic_runtime.py` that validates plan surfaces, guard/CI/registry wiring, and optional R6 receipts.
- [x] Add `test/check_user_level_cloakbrowser_academic_runtime.test.py` with red/green coverage for plan registration and hash-only receipt validation.
- [x] Register the checker in `tools/run_openspec_guard.py`, `tools/safety_rule_script_backing_registry.json`, `tools/ci/ci_test_manifest.json`, and `docs_bilingual/docs_registry.yaml`.
- [x] Execute real user-level CloakBrowser Python install and smoke; record `cloakbrowser-python` R6 live-executed receipt.
- [x] Execute real user-level CloakBrowser npm install and package-version smoke; record `cloakbrowser-npm` R6 live-executed receipt.
- [x] Resolve CloakBrowser-Manager source and record Docker-missing blocked receipt; Docker install/start remains outside this plan.
- [x] Update the checker/test schema for CloakBrowser-Manager non-Docker source-backend-frontend-loopback receipt validation.
- [x] Execute CloakBrowser-Manager non-Docker source-backend-frontend-loopback smoke from the source checkout and record `cloakbrowser-manager-source-runtime.json`.
- [x] Install `academic-research-suite` with Codex skill installer and record R6 live-executed receipt.
<!-- TASK_BACKLOG_END -->

## Validation Gates

- `python test\check_user_level_cloakbrowser_academic_runtime.test.py` - runs focused checker unit tests.
- `python tools\check_user_level_cloakbrowser_academic_runtime.py --root . --json` - verifies plan, guard, CI, and registry wiring.
- `python tools\check_user_level_cloakbrowser_academic_runtime.py --root . --receipt-dir <receipt-dir> --require-live --json` - verifies live install receipts after execution.
- `python tools\check_precommit_update_archive.py --root . --json` - verifies pre-commit update and archive readiness.
- `python tools\run_openspec_guard.py --root . --json` - runs the repository OpenSpec guard suite.
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1` - runs the mirrored local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1` - runs local MR review before integration.

## Acceptance Criteria

- The new plan is registered and checker-backed before any live install happens.
- Receipts are hash-only and do not include raw paths, raw command transcripts, secrets, cookies, or browser data.
- CloakBrowser Python, CloakBrowser npm package-version smoke, and academic-research-suite are live-executed when dependencies and authorization are present.
- CloakBrowser-Manager does not install Docker, Podman, WSL containers, or Docker Compose; container runtime remains out of scope.
- CloakBrowser-Manager source runtime acceptance means backend import/dependency resolution succeeds, the built React frontend is served, `/api/status` returns HTTP 200 JSON, `/` returns GUI shell HTML, and profile launch is explicitly not run on Windows because the upstream runtime expects Xvnc/KasmVNC.
- Native Codex files are not modified, user-level install artifacts remain rollbackable, and remote publication remains unauthorized.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-10 plan/checker package: creates the user-level CloakBrowser / CloakBrowser-Manager / academic-research-suite runtime plan, checker, tests, guard registration, and receipt contract. No user-level install/start/smoke is performed by the plan package.
- 2026-06-10 Stage B live runtime receipts: `docs_bilingual/implementation_evidence/user_level_cloakbrowser_academic_runtime_receipts_20260610/` records hash-only receipts for `cloakbrowser-python` R6 live-executed, `cloakbrowser-npm` R6 live-executed package-version smoke, `cloakbrowser-manager-source` R6 blocked Docker boundary, and `academic-research-suite` R6 live-executed. Native Codex files/config were not modified and remote publication was not performed.
- 2026-06-11 Stage A non-Docker Manager runtime plan: this docs-only package records the next implementation target, `cloakbrowser-manager-source-runtime`, before checker/test and live runtime execution.
- 2026-06-11 Stage B non-Docker Manager runtime execution: adds checker/test validation plus `tools/run_cloakbrowser_manager_source_runtime.py`; records `cloakbrowser-manager-source-runtime.json` with source-backend-frontend-loopback smoke, `/api/status` HTTP 200 JSON, `/` GUI shell HTML, `container_runtime_used=false`, `docker_install_allowed=false`, and `profile_launch_smoke=not_run:no_xvnc_on_windows`.
<!-- EVIDENCE_INDEX_END -->
