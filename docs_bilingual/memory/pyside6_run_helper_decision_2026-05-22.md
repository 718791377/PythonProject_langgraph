---
doc_id: pyside6_run_helper_decision_2026-05-22
lang: en
status: active
doc_class: memory
translation_of: docs_bilingual/memory/pyside6_run_helper_decision_2026-05-22.zh-CN.md
created_at: 2026-05-22
---

# PySide6 run helper decision - 2026-05-22

## Decision

Do not add a cross-project `run-shared-pyside6-gui.ps1` helper for the current evidence set. Keep the generated per-project `tools/gui/run_gui.ps1` as the default visible-GUI launcher contract.

## Evidence

- The first consumer apply already generated a project-local `tools/gui/run_gui.ps1` that points at the shared runtime through the project runtime contract.
- The project-local wrapper keeps the project root, GUI package name, visible-window launch boundary, and rollback path inside the consumer project.
- Import-only verification is already handled by `tools/gui/check_pyside6_env.py`, which now injects the target project's `src` path when executed by the shared runtime Python.
- A cross-project launcher would currently duplicate the generated wrapper and add another launch surface without reducing project-local complexity.

## Reopen rule

Reopen the cross-project launcher decision only when at least two consumer projects show repeated launcher logic that cannot be handled by the generated per-project wrapper or by the shared templates.

## Boundaries

- No visible GUI was launched for this decision.
- No PySide6 dependency was installed into a consumer-project `.venv`.
- No remote publication was performed.
