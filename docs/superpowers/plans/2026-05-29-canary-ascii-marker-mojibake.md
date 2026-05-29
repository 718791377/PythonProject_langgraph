---
change: fix-canary-ascii-marker-mojibake-20260529
design-doc: docs/superpowers/specs/2026-05-29-canary-ascii-marker-mojibake-design.md
base-ref: e81d840af21347047d3f9877b76664f0c17512e1
archived-with: openspec/changes/archive/2026-05-29-fix-canary-ascii-marker-mojibake-20260529
---

# Canary ASCII Marker Mojibake Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this compact single-slice plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the non-ASCII visible canary marker with a transport-safe ASCII marker while preserving fail-closed historical corruption detection.

**Architecture:** The startup summary pair remains the literal source of truth. Checker/test source assembles canonical markers from fragments and historical markers from codepoints so repository-wide placement scans do not see extra literal marker copies.

**Tech Stack:** Python stdlib checkers and unittest modules; Markdown/OpenSpec docs.

---

### Task 1: Checker constants and diagnostics

**Files:**
- Modify: `tools/check_context_retention_canary_surface.py`
- Modify: `tools/check_startup_instruction_mojibake.py`

- [x] **Step 1: Set canonical markers to ASCII fragments**

Use split string constants, for example `"CODEX_CTX_" + "CANARY_START"`, instead of a contiguous literal token.

- [x] **Step 2: Preserve historical marker detection**

Keep the previous marker values built from Unicode codepoints and include both those values and their generated legacy-encoding variants in invalid canary detection.

- [x] **Step 3: Verify response/session status behavior**

Canonical ASCII evidence reports `canonical_present`; historical or corrupted marker evidence reports `mojibake_canary` and fails closed.

### Task 2: Startup summaries and tests

**Files:**
- Modify: `docs_bilingual/project_startup_summary.md`
- Modify: `docs_bilingual/project_startup_summary.zh-CN.md`
- Modify: `test/check_context_retention_canary_surface.test.py`
- Modify: `test/check_startup_instruction_mojibake.test.py`

- [x] **Step 1: Update startup summary pair**

Define the exact ASCII marker text only in the startup summary pair and state that the historical marker is legacy detection input only.

- [x] **Step 2: Update tests**

Construct canonical markers from fragments, construct historical markers from codepoints, and add regression cases for historical marker rejection.

- [ ] **Step 3: Run targeted verification**

Run:

```powershell
python test/check_context_retention_canary_surface.test.py
python test/check_startup_instruction_mojibake.test.py
python tools/check_context_retention_canary_surface.py --root . --json
python tools/check_startup_instruction_mojibake.py --root . --json
```

### Task 3: OpenSpec and integration validation

**Files:**
- Modify: `openspec/changes/fix-canary-ascii-marker-mojibake-20260529/tasks.md`
- Modify after archive: `openspec/specs/codex-user-level-context-retention-canary-surface/spec.md`

- [ ] **Step 1: Validate OpenSpec and precommit gates**

Run:

```powershell
python tools/run_openspec_guard.py --root .
python tools/check_precommit_update_archive.py --root . --json
```

- [ ] **Step 2: Run local CI and local MR review before local main merge**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .	ools\ci\local_gate.ps1 -StepTimeoutSeconds 600
powershell -NoProfile -ExecutionPolicy Bypass -File .	ools\ci\local_mr_review.ps1
```

- [ ] **Step 3: Commit and integrate locally**

Commit the implementation/archive package on the feature branch, merge to local `main` after validation, and stop before remote publication.
