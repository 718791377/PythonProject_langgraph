---
doc_id: codex_user_level_context_retention_canary_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/codex_user_level_context_retention_canary_plan.md
translation_of: docs_bilingual/implementation_plans/codex_user_level_context_retention_canary_plan.md
status: active
doc_class: implementation_plan
---

# Codex 用户级上下文保留提示词哨兵实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 按任务逐项实现本计划。步骤使用 checkbox（`- [ ]`）语法跟踪。

**Goal:** 建立并维护一个 UTF-8 干净、只由 startup summary 持有字面量、用于检测 `/resume`、compaction 和长上下文后模型是否仍记得冷启动权威的提示词哨兵治理面。

**Architecture:** startup summary 双语文件是唯一字面量来源；AGENTS、治理文档、实施计划、launcher、helper 和 CI 只能间接引用该来源。脚本负责 fail-closed 检查字面量泄漏、乱码、会话诊断和上下文过滤边界；用户可见哨兵是模型自检信号，不是 wrapper response gate。

**Tech Stack:** Markdown governance docs, Python 3 checkers/tests, Codex JSONL session transcripts, PowerShell local CI, OpenSpec spec/archive workflow.

---

## Bilingual Alignment Status

- 中文计划：`docs_bilingual/implementation_plans/codex_user_level_context_retention_canary_plan.zh-CN.md`
- English companion：`docs_bilingual/implementation_plans/codex_user_level_context_retention_canary_plan.md`
- 本计划不得包含 startup-summary-defined start marker 或 end marker 的字面量，也不得包含其常见乱码形态。
- 若后续需要修改哨兵字面量，只修改 startup summary 双语文件，并通过 checker 证明其他文件仍只保持间接引用。

## 1. Ground Rules

1. **目的**：提示词哨兵用于判断模型是否在恢复会话、压缩上下文、长上下文后仍理解冷启动权威、用户级规则、项目级规则与安全边界。
2. **不是 response gate**：不得把哨兵实现为 wrapper 强制追加、response post-processing、transport injection 或“没有哨兵就自动改写回复”的门禁。
3. **唯一字面量来源**：startup summary 双语文件是唯一允许保存哨兵字面量的仓库文件；其他文件只能写“startup-summary-defined start marker / end marker”这类间接描述。
4. **用户可见但模型不可二次学习**：哨兵可以出现在用户可见 assistant 回复中；会话重放、launcher payload、压缩摘要、工具输出注入和 worker handoff 必须过滤或降权该哨兵，防止模型从历史输出副本中学习错误或乱码哨兵。
5. **UTF-8 canonical**：UTF-8 startup summary 双语文件是唯一规范来源；任何乱码输出都不能被复制到回复、文档、测试 fixture 或 launcher payload 中作为权威。
6. **脚本保护优先**：凡涉及发布、durable state、跨项目 scope、launcher payload、上下文过滤、session 诊断的规则，必须有 checker、guarded helper、CI gate 或生成式 launcher 逻辑兜底。
7. **恢复动作**：若完整 assistant 回复缺失 startup-summary-defined 哨兵或出现乱码哨兵，恢复流程是重新读取 `AGENTS.md`，再通过显式 UTF-8 路径读取 startup summary 双语文件，并按 cold-start read order 只补读继续当前任务必需的文件。

## 2. File Ownership Map

| Area | Files | Responsibility |
| --- | --- | --- |
| Canonical prompt source | `docs_bilingual/project_startup_summary.md`, `docs_bilingual/project_startup_summary.zh-CN.md` | 唯一保存哨兵字面量；说明目的、恢复动作和 read order。 |
| Recovery pointer | `AGENTS.md` | 只说明出现缺失或乱码时回到 startup summary；不得复制字面量。 |
| Surface checker | `tools/check_context_retention_canary_surface.py` | 确认字面量只在 startup summary 双语文件中；诊断 response/session 是否缺失或乱码；过滤工具输出和上下文副本。 |
| Encoding checker | `tools/check_startup_instruction_mojibake.py` | 检测 startup/instruction authority surface、response/session 中的乱码。 |
| Context filter helper | `tools/filter_session_context_canary.py` | 在需要把历史会话转成模型输入时，移除 user-visible canary marker 的副本，同时保留其他用户可见内容。 |
| Tests | `test/check_context_retention_canary_surface.test.py`, `test/check_startup_instruction_mojibake.test.py`, `test/filter_session_context_canary.test.py` | 证明泄漏、乱码、缺失、session JSONL 过滤和 UTF-8 canonical 行为。 |
| CI wiring | `tools/ci/ci_test_manifest.json`, `tools/ci/local_gate.ps1`, `.githooks/pre-commit` | 保证新增 checker 与测试进入本地 gate 和提交前检查。 |
| OpenSpec authority | `openspec/specs/codex-user-level-context-retention-canary-surface/spec.md` and matching change/archive | 将已验证行为归档到稳定 spec；后续变更先提 change。 |

## 3. Task Breakdown

### Task 1: Freeze the Canary Contract in Startup Summaries

**Files:**
- Modify: `docs_bilingual/project_startup_summary.md`
- Modify: `docs_bilingual/project_startup_summary.zh-CN.md`
- Modify: `AGENTS.md`
- Test: `tools/check_context_retention_canary_surface.py`
- Test: `tools/check_startup_instruction_mojibake.py`

- [ ] **Step 1: Read both startup summaries as UTF-8**

Run:

```powershell
python -c "from pathlib import Path; [Path(p).read_text(encoding='utf-8') for p in ['docs_bilingual/project_startup_summary.md','docs_bilingual/project_startup_summary.zh-CN.md']]; print('utf8 ok')"
```

Expected: `utf8 ok`.

- [ ] **Step 2: Confirm the marker pair exists only in startup summaries**

Run:

```powershell
python tools/check_context_retention_canary_surface.py --root . --json
```

Expected: JSON has `"ok": true` and `allowed_paths` listing only the startup summary pair.

- [ ] **Step 3: Confirm startup/instruction authority surfaces are UTF-8 clean**

Run:

```powershell
python tools/check_startup_instruction_mojibake.py --root . --json
```

Expected: JSON has `"ok": true` and no mojibake findings.

- [ ] **Step 4: Update text only by indirection**

If non-startup wording needs refinement, use this rule:

```markdown
Do not duplicate the context-retention canary prompt. Its literal text lives only in the startup summary pair; this surface may only point to those files and describe recovery behavior.
```

Expected: no non-startup file contains startup-summary-defined markers.

- [ ] **Step 5: Commit this task alone if changed**

Run:

```powershell
git add docs_bilingual/project_startup_summary.md docs_bilingual/project_startup_summary.zh-CN.md AGENTS.md
git commit -m "docs: freeze context retention canary contract"
```

Expected: commit succeeds only after the two checker commands above pass.

### Task 2: Harden Surface Checker Behavior

**Files:**
- Modify: `tools/check_context_retention_canary_surface.py`
- Modify: `test/check_context_retention_canary_surface.test.py`

- [ ] **Step 1: Add a failing test for non-startup literal duplication**

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

Expected: the test fails before checker hardening if the checker ignores non-startup duplication.

- [ ] **Step 2: Add a failing test for session diagnostics**

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

- [ ] **Step 3: Keep marker definitions non-literal inside the checker**

The checker may derive canonical values from startup summaries or non-literal codepoint construction, but it must not store the marker text directly in source code. Keep the allowed path set narrow:

```python
ALLOWED_CANARY_PROMPT_PATHS = {
    Path("docs_bilingual/project_startup_summary.md"),
    Path("docs_bilingual/project_startup_summary.zh-CN.md"),
}
```

Expected: source scanning does not find literal or mojibake marker variants in checker files.

- [ ] **Step 4: Run focused tests**

Run:

```powershell
python test/check_context_retention_canary_surface.test.py
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

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

- [ ] **Step 1: Add a failing test for corrupted assistant output**

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

- [ ] **Step 2: Detect mojibake in authority surfaces**

Ensure the checker scans `AGENTS.md`, startup summaries, governance docs, implementation plans, active OpenSpec changes, and tests for known corrupted marker variants and common startup-instruction mojibake sequences.

Expected: any corrupted marker variant outside ignored generated artifacts fails closed.

- [ ] **Step 3: Report canonical recovery text without copying corrupt bytes**

The diagnostic should say to use the UTF-8 startup summary pair as canonical and reread cold-start files. It must not echo the corrupted marker value back to the user.

Expected: JSON diagnostics expose marker counts and line numbers, not the corrupted marker string.

- [ ] **Step 4: Run focused tests**

Run:

```powershell
python test/check_startup_instruction_mojibake.test.py
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

Run:

```powershell
git add tools/check_startup_instruction_mojibake.py test/check_startup_instruction_mojibake.test.py
git commit -m "test: reject startup instruction mojibake"
```

Expected: commit contains only mojibake checker and test changes for this task.

### Task 4: Add Session Context Filtering for Model-Readable Replay

**Files:**
- Create: `tools/filter_session_context_canary.py`
- Create: `test/filter_session_context_canary.test.py`
- Modify: `tools/ci/ci_test_manifest.json`

- [ ] **Step 1: Write the failing filter test**

The filter must preserve user-visible transcript content while removing startup-summary-defined canary markers from any model-readable replay output.

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

- [ ] **Step 2: Implement CLI arguments**

Implement this CLI surface:

```powershell
python tools/filter_session_context_canary.py --root . --input .tmp/response.txt --output .tmp/model-context.txt --mode model-context --json
```

Expected JSON fields:

```json
{
  "ok": true,
  "removed_canary_markers": 2,
  "mode": "model-context"
}
```

- [ ] **Step 3: Implement UTF-8-only IO**

The helper reads input as `utf-8-sig` or `utf-8`, writes UTF-8, and returns a non-zero exit code if input cannot be decoded.

Expected: malformed input fails closed and does not write partial output.

- [ ] **Step 4: Register the test in CI manifest**

Add `python test/filter_session_context_canary.test.py` to `tools/ci/ci_test_manifest.json` in the same test group as other context-retention canary checks.

Expected: `tools/ci/local_gate.ps1` runs the new test.

- [ ] **Step 5: Commit**

Run:

```powershell
git add tools/filter_session_context_canary.py test/filter_session_context_canary.test.py tools/ci/ci_test_manifest.json
git commit -m "feat: filter context canary from model replay"
```

Expected: commit contains the helper, test, and manifest update.

### Task 5: Wire Launcher and Payload Boundaries Without Injection

**Files:**
- Modify: `docs_bilingual/governance/user_level_launcher_payload_policy.md`
- Modify: `docs_bilingual/governance/user_level_launcher_payload_policy.zh-CN.md`
- Modify: launcher/helper source files that assemble Codex startup payloads under `tools/`
- Test: existing launcher payload tests matching the touched helper names

- [ ] **Step 1: Locate payload assembly helpers**

Run:

```powershell
Select-String -Path tools\*.py,tools\*.ps1 -Pattern "model_instructions_file|developer_instructions|AGENTS.md|project_startup_summary" -List
```

Expected: output identifies the central helper files that assemble startup instructions.

- [ ] **Step 2: Add or update tests that reject canary injection**

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

- [ ] **Step 3: Keep payload file-backed and UTF-8 explicit**

If a helper passes large startup instructions, pass a short file path or config reference rather than inline generated content. Open files with explicit UTF-8 encoding.

Expected: generated launcher command lines remain short and do not contain canary marker text.

- [ ] **Step 4: Run launcher-related tests**

Run the focused tests identified by Step 1 plus:

```powershell
python tools/check_startup_instruction_mojibake.py --root . --json
python tools/check_context_retention_canary_surface.py --root . --json
```

Expected: all focused tests and both checker commands pass.

- [ ] **Step 5: Commit**

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

- [ ] **Step 1: Confirm all canary tests are CI-managed**

Run:

```powershell
python -c "import json; from pathlib import Path; data=json.loads(Path('tools/ci/ci_test_manifest.json').read_text(encoding='utf-8')); print('\n'.join(str(item) for item in data))"
```

Expected: the manifest includes the context surface, mojibake, and session context filter tests.

- [ ] **Step 2: Confirm pre-commit catches missing registrations**

Run:

```powershell
python tools/check_precommit_update_archive.py --root . --json
```

Expected: JSON has `"ok": true`; if it fails, update registration or archive status rather than bypassing.

- [ ] **Step 3: Run local gate**

Run:

```powershell
.\tools\ci\local_gate.ps1
```

Expected: local gate passes.

- [ ] **Step 4: Commit**

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

- [ ] **Step 1: Verify current OpenSpec state**

Run:

```powershell
openspec list --json
openspec validate --all --strict
```

Expected: active changes are intentional; validation passes.

- [ ] **Step 2: Add requirements for the canary surface**

The stable spec must require:

- startup summary pair is the only literal marker source;
- non-startup authority surfaces only reference the startup summary pair;
- response/session diagnostics inspect user-visible assistant messages and filter tool/context copies;
- mojibake diagnostics fail closed and do not echo corrupted marker strings;
- context replay to a model removes canary marker copies while preserving user-visible transcript text.

Expected: spec describes observable behavior, not implementation preferences.

- [ ] **Step 3: Validate and archive when implementation is complete**

Run:

```powershell
openspec validate --all --strict
python tools/run_openspec_guard.py --root .
```

Expected: both commands pass before archive or integration.

- [ ] **Step 4: Commit OpenSpec package**

Run:

```powershell
git add openspec
git commit -m "docs: specify context canary retention surface"
```

Expected: commit contains stable spec and archive movement for the completed change.

## 4. Acceptance Checklist

- [ ] `python test/check_context_retention_canary_surface.test.py` passes.
- [ ] `python test/check_startup_instruction_mojibake.test.py` passes.
- [ ] `python test/filter_session_context_canary.test.py` passes after Task 4 is implemented.
- [ ] `python tools/check_context_retention_canary_surface.py --root . --json` passes.
- [ ] `python tools/check_startup_instruction_mojibake.py --root . --json` passes.
- [ ] `python tools/check_precommit_update_archive.py --root . --json` passes.
- [ ] `openspec validate --all --strict` passes.
- [ ] `python tools/run_openspec_guard.py --root .` passes.
- [ ] `.\tools\ci\local_gate.ps1` passes.
- [ ] No file outside startup summary pair contains the marker literal or corrupted marker variants.
- [ ] Launcher payloads and model-readable session replays do not inline or preserve canary marker copies.

## 5. Release and Integration Rules

- Use a feature worktree and feature branch for implementation.
- Keep local `main` current with `gitlab/main` before writable work; local `main` may be ahead after approved local integration.
- Do not push GitLab, open or merge a GitLab MR, sync GitHub, or mutate remote refs without explicit remote-publication approval.
- If implementation touches launcher behavior, run both local gate and local MR review before local `main` integration.
- If implementation only updates this plan document, run the two canary checkers and report the branch/worktree status before asking whether to commit.
