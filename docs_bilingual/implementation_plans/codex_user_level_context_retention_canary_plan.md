---
doc_id: codex_user_level_context_retention_canary_plan
lang: en
canonical: docs_bilingual/implementation_plans/codex_user_level_context_retention_canary_plan.md
status: active
doc_class: implementation_plan
---

# Codex User-Level Context-Retention Canary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and maintain a UTF-8-clean, startup-summary-owned context-retention canary that detects whether a model still remembers cold-start authority after `/resume`, compaction, or long-context pressure.

**Architecture:** The bilingual startup summary pair is the only literal marker source; AGENTS, governance docs, implementation plans, launchers, helpers, and CI may only reference that source indirectly. Scripts fail closed for literal leakage, mojibake, response/session diagnostics, and model-readable context replay filtering; the visible canary is a user-visible model self-check, not a wrapper response gate.

**Tech Stack:** Markdown governance docs, Python 3 checkers/tests, Codex JSONL session transcripts, PowerShell local CI, OpenSpec spec/archive workflow.

---

## Bilingual Alignment Status

- English plan: `docs_bilingual/implementation_plans/codex_user_level_context_retention_canary_plan.md`
- Chinese companion: `docs_bilingual/implementation_plans/codex_user_level_context_retention_canary_plan.zh-CN.md`
- This plan must not contain the startup-summary-defined start marker or end marker literal, and must not contain common mojibake variants of those markers.
- If the marker text ever changes, edit only the bilingual startup summary pair and prove that all other files still use indirect references.


## 0. Implementation Status Reconciliation

As of 2026-06-02, this source plan's core local implementation is closed through the Phase 2 child-plan family:

- `context_retention_canary_literal_boundary_plan`: `b779d51`, canary literal-boundary checking entered local `main`.
- `startup_mojibake_utf8_recovery_plan`: `43d3ae9`, UTF-8 canonical recovery source reporting entered local `main`.
- `session_replay_context_filtering_plan`: `cbc73c7`, legacy session replay filtering helpers and tests entered local `main`.
- `launcher_payload_context_boundary_plan`: `6f1ef48`, file-backed launcher payload boundary checking entered local `main`.

The legacy task breakdown below remains the task-tracking record; this reconciliation synchronizes rows that are proved by child-plan evidence and local `main` ancestry. Remote publication is not authorized by this status update.
## 0.1 Confirmed Follow-up: Canonical Visible Canary Restore

A 2026-06-02 follow-up child plan, `prompt_canary_canonical_visible_marker_restore_plan`, is confirmed for implementation after the plan package enters local `main`. It restores the startup-summary-defined canonical visible canary to the requested non-ASCII marker pair, treats the current ASCII tokens as legacy/stale compatibility input, and extends filtering expectations so model-readable session, replay, compaction, and handoff context block marker copies before prompt-authority handoff.

## 1. Ground Rules

1. **Purpose:** the canary checks whether the model still understands cold-start authority, user-level rules, project-level rules, and safety boundaries after session resume, context compaction, or long-context pressure.
2. **Not a response gate:** do not implement it as wrapper appending, response post-processing, transport injection, or automatic rewriting when a response lacks the marker.
3. **Only literal source:** the bilingual startup summary files are the only repository files allowed to store the marker literal; every other file must use indirect wording such as "startup-summary-defined start marker / end marker."
4. **User-visible but not model-relearned:** the canary may appear in user-visible assistant responses. Model-readable session, replay, compaction, launcher payload, tool-output injection, and worker handoff context must filter, block, or downgrade marker copies so the model cannot learn a wrong, stale, restored, or corrupted marker from history.
5. **UTF-8 canonical:** the UTF-8 startup summary pair is the only canonical source; corrupted runtime output must never be copied into responses, docs, fixtures, or launcher payload as authority.
6. **Script controls first:** rules affecting publication, durable state, cross-project scope, launcher payloads, context filtering, or session diagnostics need checkers, guarded helpers, CI gates, or generated launcher logic.
7. **Recovery:** if a complete assistant response misses the startup-summary-defined canary or shows a corrupted canary, reread `AGENTS.md`, reread the startup summary pair through explicit UTF-8 paths, follow the cold-start read order, and then reread only task-specific files needed to continue.

## 2. File Ownership Map

| Area | Files | Responsibility |
| --- | --- | --- |
| Canonical prompt source | `docs_bilingual/project_startup_summary.md`, `docs_bilingual/project_startup_summary.zh-CN.md` | Only files containing the marker literal; define purpose, recovery action, and read order. |
| Recovery pointer | `AGENTS.md` | Points back to startup summaries; never duplicates the literal. |
| Surface checker | `tools/check_context_retention_canary_surface.py` | Confines marker literal to startup summaries; diagnoses response/session missing or corrupted canaries; filters tool-output/context copies. |
| Encoding checker | `tools/check_startup_instruction_mojibake.py` | Detects mojibake in startup/instruction authority surfaces, responses, and sessions. |
| Context filter helper | `tools/session_replay_context_filtering.py` | Removes user-visible canary marker copies when historical sessions are converted into model-readable context, while preserving other transcript text. |
| Tests | `test/check_context_retention_canary_surface.test.py`, `test/check_startup_instruction_mojibake.test.py`, `test/check_session_replay_context_filtering.test.py` | Prove leakage, mojibake, missing markers, JSONL filtering, and UTF-8 canonical behavior. |
| CI wiring | `tools/ci/ci_test_manifest.json`, `tools/ci/local_gate.ps1`, `.githooks/pre-commit` | Keeps new checkers and tests inside local gate and pre-commit review. |
| OpenSpec authority | `openspec/specs/codex-user-level-context-retention-canary-surface/spec.md` and matching change/archive | Records verified behavior in stable spec; future behavior changes start as OpenSpec changes. |

## 3. Task Breakdown

### Task 1: Freeze the Canary Contract in Startup Summaries

**Files:**
- Modify: `docs_bilingual/project_startup_summary.md`
- Modify: `docs_bilingual/project_startup_summary.zh-CN.md`
- Modify: `AGENTS.md`
- Test: `tools/check_context_retention_canary_surface.py`
- Test: `tools/check_startup_instruction_mojibake.py`

- [x] **Step 1: Read both startup summaries as UTF-8**

Run:

```powershell
python -c "from pathlib import Path; [Path(p).read_text(encoding='utf-8') for p in ['docs_bilingual/project_startup_summary.md','docs_bilingual/project_startup_summary.zh-CN.md']]; print('utf8 ok')"
```

Expected: `utf8 ok`.

- [x] **Step 2: Confirm the marker pair exists only in startup summaries**

Run:

```powershell
python tools/check_context_retention_canary_surface.py --root . --json
```

Expected: JSON has `"ok": true` and `allowed_paths` listing only the startup summary pair.

- [x] **Step 3: Confirm authority surfaces are UTF-8 clean**

Run:

```powershell
python tools/check_startup_instruction_mojibake.py --root . --json
```

Expected: JSON has `"ok": true` and no mojibake findings.

- [x] **Step 4: Update text only by indirection**

If wording needs refinement outside startup summaries, use this rule:

```markdown
Do not duplicate the context-retention canary prompt. Its literal text lives only in the startup summary pair; this surface may only point to those files and describe recovery behavior.
```

Expected: no non-startup file contains startup-summary-defined markers.

- [x] **Step 5: Commit this task alone if changed**

Run:

```powershell
git add docs_bilingual/project_startup_summary.md docs_bilingual/project_startup_summary.zh-CN.md AGENTS.md
git commit -m "docs: freeze context retention canary contract"
```

Expected: commit succeeds only after the two checker commands pass.

### Task 2: Harden Surface Checker Behavior

**Files:**
- Modify: `tools/check_context_retention_canary_surface.py`
- Modify: `test/check_context_retention_canary_surface.test.py`

- [x] **Step 1: Add a failing test for non-startup literal duplication**

Create a test fixture that derives marker text at runtime from the startup summary file, writes it into a temporary `AGENTS.md`, runs the checker, and asserts failure. The test file must not contain the marker literal.

```python
def test_rejects_canary_literal_outside_startup_summary(tmp_path):
    root = make_repo(tmp_path)
    marker_text = read_marker_text(root / "docs_bilingual/project_startup_summary.md")
    (root / "AGENTS.md").write_text(f"Duplicated marker: {marker_text}\n", encoding="utf-8")

    payload = run_checker(root)

    assert payload["ok"] is False
    assert any("must live only" in error for error in payload["errors"])
```

Expected: fails before checker hardening if the checker ignores non-startup duplication.

- [x] **Step 2: Add a failing test for session diagnostics**

Use a JSONL event with assistant-visible content missing one marker and assert the checker reports `missing_canary` only for assistant messages, not tool events.

```python
def test_session_diagnostic_reads_only_assistant_messages(tmp_path):
    root = make_repo(tmp_path)
    session = root / ".tmp" / "session.jsonl"
    session.parent.mkdir(parents=True, exist_ok=True)
    session.write_text("\n".join([
        json.dumps({"type": "event_msg", "payload": {"type": "tool_output", "content": "tool copy"}}, ensure_ascii=False),
        json.dumps({"type": "response_item", "payload": {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "assistant text without full marker pair"}]}}, ensure_ascii=False),
    ]), encoding="utf-8")

    payload = run_checker(root, "--session-jsonl", str(session), "--latest-assistant")

    assert payload["ok"] is False
    assert payload["response_diagnostics"][-1]["status"] == "missing_canary"
```

Expected: the diagnostic ignores tool output and reports the assistant response only.

- [x] **Step 3: Keep marker definitions non-literal inside the checker**

The checker may derive canonical values from startup summaries or non-literal codepoint construction, but it must not store the marker text directly in source code. Keep the allowed path set narrow:

```python
ALLOWED_CANARY_PROMPT_PATHS = {
    Path("docs_bilingual/project_startup_summary.md"),
    Path("docs_bilingual/project_startup_summary.zh-CN.md"),
}
```

Expected: source scanning does not find literal or mojibake marker variants in checker files.

- [x] **Step 4: Run focused tests**

Run:

```powershell
python test/check_context_retention_canary_surface.test.py
```

Expected: all tests pass.

- [x] **Step 5: Commit**

Run:

```powershell
git add tools/check_context_retention_canary_surface.py test/check_context_retention_canary_surface.test.py
git commit -m "test: harden context canary surface diagnostics"
```

Expected: commit contains only checker and test changes for this task.

### Task 3: Harden Mojibake Detection and UTF-8 Canonical Recovery

**Files:**
- Modify: `tools/check_startup_instruction_mojibake.py`
- Modify: `test/check_startup_instruction_mojibake.test.py`

- [x] **Step 1: Add a failing test for corrupted assistant output**

Generate a corrupted marker variant by encoding the canonical marker with UTF-8 and decoding it through a legacy Windows encoding. Do not store the corrupted text in the test file.

```python
def corrupt_text(text: str) -> str:
    return text.encode("utf-8").decode("cp936", errors="replace")


def test_response_diagnostic_rejects_mojibake_marker(tmp_path):
    root = make_repo(tmp_path)
    marker_text = read_marker_text(root / "docs_bilingual/project_startup_summary.zh-CN.md")
    payload = run_checker(root, "--response-text", corrupt_text(marker_text))

    assert payload["ok"] is False
    assert payload["response_diagnostics"][-1]["status"] == "mojibake"
```

Expected: fails before mojibake response diagnostics are implemented.

- [x] **Step 2: Detect mojibake in authority surfaces**

Ensure the checker scans `AGENTS.md`, startup summaries, governance docs, implementation plans, active OpenSpec changes, and tests for known corrupted marker variants and common startup-instruction mojibake sequences.

Expected: any corrupted marker variant outside ignored generated artifacts fails closed.

- [x] **Step 3: Report canonical recovery text without copying corrupt bytes**

The diagnostic should say to use the UTF-8 startup summary pair as canonical and reread cold-start files. It must not echo the corrupted marker value back to the user.

Expected: JSON diagnostics expose marker counts and line numbers, not the corrupted marker string.

- [x] **Step 4: Run focused tests**

Run:

```powershell
python test/check_startup_instruction_mojibake.test.py
```

Expected: all tests pass.

- [x] **Step 5: Commit**

Run:

```powershell
git add tools/check_startup_instruction_mojibake.py test/check_startup_instruction_mojibake.test.py
git commit -m "test: reject startup instruction mojibake"
```

Expected: commit contains only mojibake checker and test changes for this task.

### Task 4: Add Session Context Filtering for Model-Readable Replay

**Files:**
- Create: `tools/session_replay_context_filtering.py`
- Create: `test/check_session_replay_context_filtering.test.py`
- Modify: `tools/ci/ci_test_manifest.json`

- [x] **Step 1: Write the failing filter test**

The filter must preserve transcript content while removing startup-summary-defined canary markers from any model-readable replay output.

```python
def test_filter_removes_canary_from_model_context_but_preserves_text(tmp_path):
    root = make_repo(tmp_path)
    marker = read_marker_text(root / "docs_bilingual/project_startup_summary.md")
    source = root / ".tmp" / "response.txt"
    output = root / ".tmp" / "model-context.txt"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(f"{marker}\nThe answer body remains.\n", encoding="utf-8")

    run_filter(root, "--input", str(source), "--output", str(output), "--mode", "model-context")

    filtered = output.read_text(encoding="utf-8")
    assert marker not in filtered
    assert "The answer body remains." in filtered
```

Expected: fails before the filter helper exists.

- [x] **Step 2: Implement CLI arguments**

Implement this CLI surface:

```powershell
python tools/session_replay_context_filtering.py --root . --input .tmp/response.txt --output .tmp/model-context.txt --mode model-context --json
```

Expected JSON fields:

```json
{
  "ok": true,
  "removed_canary_markers": 2,
  "mode": "model-context"
}
```

- [x] **Step 3: Implement UTF-8-only IO**

The helper reads input as `utf-8-sig` or `utf-8`, writes UTF-8, and returns a non-zero exit code if input cannot be decoded.

Expected: malformed input fails closed and does not write partial output.

- [x] **Step 4: Register the test in CI manifest**

Add `python test/check_session_replay_context_filtering.test.py` to `tools/ci/ci_test_manifest.json` in the same test group as other context-retention canary checks.

Expected: `tools/ci/local_gate.ps1` runs the new test.

- [x] **Step 5: Commit**

Run:

```powershell
git add tools/session_replay_context_filtering.py test/check_session_replay_context_filtering.test.py tools/ci/ci_test_manifest.json
git commit -m "feat: filter context canary from model replay"
```

Expected: commit contains the helper, test, and manifest update.

### Task 5: Wire Launcher and Payload Boundaries Without Injection

**Files:**
- Modify: `docs_bilingual/governance/user_level_launcher_payload_policy.md`
- Modify: `docs_bilingual/governance/user_level_launcher_payload_policy.zh-CN.md`
- Modify: launcher/helper source files that assemble Codex startup payloads under `tools/`
- Test: existing launcher payload tests matching the touched helper names

- [x] **Step 1: Locate payload assembly helpers**

Run:

```powershell
Select-String -Path tools\*.py,tools\*.ps1 -Pattern "model_instructions_file|developer_instructions|AGENTS.md|project_startup_summary" -List
```

Expected: output identifies the central helper files that assemble startup instructions.

- [x] **Step 2: Add or update tests that reject canary injection**

For every touched launcher helper, add a test asserting generated config references startup summary files but does not inline the marker text.

```python
def test_launcher_payload_does_not_inline_context_canary(tmp_path):
    root = make_repo(tmp_path)
    payload = render_launcher_payload(root)
    marker = read_marker_text(root / "docs_bilingual/project_startup_summary.md")

    assert "project_startup_summary" in payload
    assert marker not in payload
```

Expected: test fails if launcher payload injects the visible canary.

- [x] **Step 3: Keep payload file-backed and UTF-8 explicit**

If a helper passes large startup instructions, pass a short file path or config reference rather than inline generated content. Open files with explicit UTF-8 encoding.

Expected: generated launcher command lines remain short and do not contain canary marker text.

- [x] **Step 4: Run launcher-related tests**

Run the focused tests identified by Step 1 plus:

```powershell
python tools/check_startup_instruction_mojibake.py --root . --json
python tools/check_context_retention_canary_surface.py --root . --json
```

Expected: all focused tests and both checker commands pass.

- [x] **Step 5: Commit**

Run:

```powershell
git add docs_bilingual/governance/user_level_launcher_payload_policy.md docs_bilingual/governance/user_level_launcher_payload_policy.zh-CN.md tools test
git commit -m "fix: keep context canary out of launcher payloads"
```

Expected: commit excludes generated artifacts and includes only source/test/docs needed for launcher boundary hardening.

### Task 6: Register CI and Pre-Commit Enforcement

**Files:**
- Modify: `tools/ci/ci_test_manifest.json`
- Modify: `.githooks/pre-commit`
- Modify: `tools/check_precommit_update_archive.py` if it owns checker registration policy

- [x] **Step 1: Confirm all canary tests are CI-managed**

Run:

```powershell
python -c "import json; from pathlib import Path; data=json.loads(Path('tools/ci/ci_test_manifest.json').read_text(encoding='utf-8')); print('\n'.join(str(item) for item in data))"
```

Expected: the manifest includes the context surface, mojibake, and session context filter tests.

- [x] **Step 2: Confirm pre-commit catches missing registrations**

Run:

```powershell
python tools/check_precommit_update_archive.py --root . --json
```

Expected: JSON has `"ok": true`; if it fails, update registration or archive status rather than bypassing.

- [x] **Step 3: Run local gate**

Run:

```powershell
.\tools\ci\local_gate.ps1
```

Expected: local gate passes.

- [x] **Step 4: Commit**

Run:

```powershell
git add tools/ci/ci_test_manifest.json .githooks/pre-commit tools/check_precommit_update_archive.py
git commit -m "chore: register context canary guardrails"
```

Expected: commit is skipped if no registration file changed; otherwise it contains only CI/pre-commit wiring.

### Task 7: Sync OpenSpec and Archive Completed Behavior

**Files:**
- Modify: `openspec/specs/codex-user-level-context-retention-canary-surface/spec.md`
- Create or modify: `openspec/changes/<change-id>/`
- Archive: `openspec/changes/archive/<date>-<change-id>/`

- [x] **Step 1: Verify current OpenSpec state**

Run:

```powershell
openspec list --json
openspec validate --all --strict
```

Expected: active changes are intentional; validation passes.

- [x] **Step 2: Add requirements for the canary surface**

The stable spec must require:

- startup summary pair is the only literal marker source;
- non-startup authority surfaces only reference the startup summary pair;
- response/session diagnostics inspect user-visible assistant messages and filter tool/context copies;
- mojibake diagnostics fail closed and do not echo corrupted marker strings;
- context replay to a model removes canary marker copies while preserving user-visible transcript text.

Expected: spec describes observable behavior, not implementation preferences.

- [x] **Step 3: Validate and archive when implementation is complete**

Run:

```powershell
openspec validate --all --strict
python tools/run_openspec_guard.py --root .
```

Expected: both commands pass before archive or integration.

- [x] **Step 4: Commit OpenSpec package**

Run:

```powershell
git add openspec
git commit -m "docs: specify context canary retention surface"
```

Expected: commit contains stable spec and archive movement for the completed change.

## 4. Acceptance Checklist

- [x] `python test/check_context_retention_canary_surface.test.py` passes.
- [x] `python test/check_startup_instruction_mojibake.test.py` passes.
- [x] `python test/check_session_replay_context_filtering.test.py` passes.
- [x] `python tools/check_context_retention_canary_surface.py --root . --json` passes.
- [x] `python tools/check_startup_instruction_mojibake.py --root . --json` passes.
- [x] `python tools/check_precommit_update_archive.py --root . --json` passes.
- [x] `openspec validate --all --strict` passes.
- [x] `python tools/run_openspec_guard.py --root .` passes.
- [x] `.\tools\ci\local_gate.ps1` passes.
- [x] No file outside the startup summary pair contains the marker literal or corrupted marker variants.
- [x] Launcher payloads and model-readable session replays do not inline or preserve canary marker copies.

## 5. Release and Integration Rules

- Use a feature worktree and feature branch for implementation.
- Keep local `main` current with `gitlab/main` before writable work; local `main` may be ahead after approved local integration.
- Do not push GitLab, open or merge a GitLab MR, sync GitHub, or mutate remote refs without explicit remote-publication approval.
- If implementation touches launcher behavior, run both local gate and local MR review before local `main` integration.
- If implementation only updates this plan document, run the two canary checkers and report the branch/worktree status before asking whether to commit.
