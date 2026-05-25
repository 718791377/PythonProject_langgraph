---
doc_id: pi_plugin_codex_user_level_sidecar_plan
lang: en
status: draft
plan_readiness: ready-for-user-confirmation
doc_class: implementation_plan
created_at: 2026-05-24
last_reviewed_at: 2026-05-25
scope: codex_to_pi_only
implementation_lane: p0_read_only_sidecar
source_reference_file: reference_files/3.md
related_docs:
  - docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
  - docs_bilingual/governance/codex_user_level_mcp_scope_policy.md
  - docs_bilingual/governance/codex_user_level_skills_governance_policy.md
---

# `pi-plugin-codex` User-Level Sidecar Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL: use `superpowers:subagent-driven-development` when available, or `superpowers:executing-plans` for task-by-task implementation. Track every task with checkbox items. Run the task-local verification before moving to the next task.

Goal: let a Codex session call Pi on demand for read-only analysis, review, and adversarial review while keeping the Codex main session as leader. Codex remains responsible for final patches, verification, commits, and local integration.

Architecture: Codex routes through a personal plugin skill to a repo-local `codex-pi` wrapper. The wrapper starts an isolated `pi --mode rpc` child process per job, writes user-level job state and receipts, and proves that P0 does not mutate the current worktree through a read-only guard. `pi-plugin-cc` and `codex-plugin-cc` are Apache-2.0 reference sources only; Claude Code plugin surfaces, slash commands, hooks, and subagent definitions must be removed or rewritten.

Tech stack: Codex personal plugin, Codex skill, Node.js ESM wrapper, PowerShell/CMD user-level launcher, Pi CLI RPC, JSONL event parsing, repo-local checker, OpenSpec change, Windows user-level receipt and state.

---

## 0. Current review verdict

The direction is correct, but the original draft was too architectural: it lacked task-sized execution steps, a CLI JSON contract, a read-only guard algorithm, receipt schemas, fixture-test boundaries, and exact governance-document update points. This version also receives the direct `oh-my-pi` install/update/rollback governance content moved out of `user_level_mcp_skills_browser_cli_governance_plan.*`.

Completeness check:

| Check | Verdict | Location |
| --- | --- | --- |
| Direction boundary | Complete | Codex -> Pi only; Pi -> Codex is a non-goal. |
| `oh-my-pi` / `pi` / `pi-plugin-cc` relationship | Complete | Section 1 and section 6.1. |
| How Codex calls Pi | Complete | Sections 2, 3, and 4. |
| Repo-local source of truth | Complete | Section 5. |
| User-level install and receipts | Complete | Sections 6 and 6.1. |
| Read-only and write isolation | Complete | Sections 7 and 10. |
| Task granularity | Complete | Section 11. |
| Verification and rollback | Complete | Sections 13 and 14. |
| Existing governance plan linkage | Complete | Section 15. |

## 1. Relationship model and naming boundary

Based on links recorded in `reference_files/3.md`, this plan uses the following relationship model. Before implementation, every external repository must be pinned to a commit or tag and recorded in the OpenSpec proposal. Do not treat current web content as permanent fact.

| Name | Role in this plan | Install/dependency posture | Boundary |
| --- | --- | --- | --- |
| `pi` / `pi.dev` | Pi CLI/runtime and RPC capability source | P0 only detects whether a local binary exists; no automatic install | `codex-pi` calls `pi --mode rpc`; secrets remain managed by Pi itself or environment variables. |
| `oh-my-pi` / `omp` | Pi family reference runtime / harness / UX source | Default `reference-only`; may be studied as a binary override candidate | Does not replace Codex, native subagents, or `codex-ohmy`. |
| `pi-plugin-cc` | Main fork/adaptation reference | Reuse only Apache-2.0 concepts and attributable code | It is a Claude Code plugin; `.claude-plugin`, slash commands, Claude hooks, and subagent definitions must be removed or rewritten. |
| `codex-plugin-cc` | Original upstream and NOTICE/concept reference | Keep attribution and concept reference only | Its direction is Claude Code -> Codex, so the Codex app-server broker is not reused. |
| `pi-codex` | Reverse bridge where Pi calls Codex | Explicit non-goal | Do not install, depend on, or document it as a P0 prerequisite. |
| `pi-plugin-codex` | New Codex personal plugin created by this plan | P0 planned/on-demand | Exposes only the Codex-side skill plus wrapper for calling Pi. |
| `codex-ohmy` | Wrapped Codex launcher | Semantics unchanged | Continues launching Codex/oh-my-codex; does not launch Pi. |

## 2. Goals and non-goals

Goals:

1. Call Pi on demand from Codex:
   - review the current diff;
   - run adversarial review focused on permissions, rollback, and user-level state pollution;
   - analyze a failure log read-only;
   - later extend to worktree-isolated rescue in P1.
2. Make every Pi call auditable:
   - repo-local source of truth;
   - user-level install receipt;
   - setup/read-only smoke;
   - rollback pointer;
   - read-only/write gate;
   - job state that can be queried, canceled, and cleaned.
3. Keep Codex as leader:
   - Pi output is sidecar evidence;
   - Codex decides whether to accept it;
   - Codex owns final patching, verification, committing, and integration.

Non-goals:

- Do not implement Pi-side `/codex:*` commands.
- Do not install or depend on `pi-codex`.
- Do not let Pi directly modify the current worktree by default.
- Do not install `pi-plugin-cc` as a Codex-native plugin.
- Do not edit plugin/vendor cache.
- Do not treat Pi, `oh-my-pi`, or OMP as replacements for Codex, native subagents, native_omx, or LangGraph.

## 3. High-level flow

1. Codex skill detects a user intent such as Pi review or Pi adversarial review.
2. The skill calls `codex-pi` with explicit `--read-only` mode.
3. `codex-pi` builds a redacted prompt and records before-state for the read-only guard.
4. `codex-pi` starts one `pi --mode rpc` child process for the job.
5. The wrapper parses JSONL/RPC events, extracts the final assistant message, and writes a structured result.
6. The read-only guard records after-state and fails closed if the worktree changed.
7. Codex reads only the structured result and decides the next patch or verification step.

## 4. Codex skill contract

Representative user intents:

```text
Use Pi to review the current diff.
Use Pi adversarial review for permissions and rollback.
Let Pi analyze this failure log read-only.
```

The Codex skill maps those intents to explicit wrapper commands:

```powershell
codex-pi setup --json
codex-pi review --read-only --json
codex-pi adversarial-review --read-only --focus "permissions and rollback" --json
codex-pi ask --read-only --stdin --json
codex-pi status --json
codex-pi result <job-id> --json
codex-pi cancel <job-id> --json
```

P0 exposes no write command. P1 may add this in a separate OpenSpec change:

```powershell
codex-pi rescue --worktree-isolated --background --json --task "<task>"
```

P1 acceptance requires Pi to write only inside a wrapper-created or explicitly provided isolated worktree. The Codex leader can selectively port patches from the handoff summary.

## 5. Repo-local source of truth

New directory and responsibilities:

```text
tools/plugin_sources/pi-plugin-codex/
  .codex-plugin/plugin.json
  skills/pi-codex/SKILL.md
  scripts/codex-pi.mjs
  scripts/lib/pi-rpc.mjs
  scripts/lib/job-control.mjs
  scripts/lib/git-targets.mjs
  scripts/lib/read-only-guard.mjs
  scripts/lib/render.mjs
  scripts/lib/redact.mjs
  prompts/ask.md
  prompts/review.md
  prompts/adversarial-review.md
  schemas/setup-output.schema.json
  schemas/job-state.schema.json
  schemas/job-result.schema.json
  schemas/review-output.schema.json
  fixtures/fake-pi.mjs
  LICENSE
  NOTICE
```

Supporting repo files:

```text
tools/install-pi-plugin-codex.ps1
tools/check_pi_plugin_codex_contract.py
tests/pi-plugin-codex/codex-pi-cli.test.mjs
tests/pi-plugin-codex/pi-rpc-fixture.test.mjs
tests/pi-plugin-codex/read-only-guard.test.mjs
tests/pi-plugin-codex/job-control.test.mjs
tests/pi-plugin-codex/plugin-manifest.test.mjs
tests/pi-plugin-codex/docs-boundary.test.mjs
openspec/changes/add-pi-plugin-codex-sidecar/
  proposal.md
  tasks.md
  design.md
  specs/codex-user-level-tooling/spec.md
```

Responsibilities:

- `.codex-plugin/plugin.json`: Codex personal plugin manifest; points to `skills/pi-codex/SKILL.md` and wrapper usage only.
- `skills/pi-codex/SKILL.md`: Codex-side routing instructions; states that Pi output is not final verification evidence.
- `codex-pi.mjs`: CLI entrypoint; parses arguments, calls libraries, emits JSON.
- `pi-rpc.mjs`: starts `pi --mode rpc`, sends prompt, reads JSONL/RPC events, extracts final assistant message.
- `job-control.mjs`: job id, state transitions, pid, cancel, timeout, stale cleanup.
- `git-targets.mjs`: finds repo root, diff targets, and changed files without printing full personal paths.
- `read-only-guard.mjs`: compares worktree fingerprints before and after P0 commands and fails closed on mutation.
- `render.mjs`: converts Pi output into Codex-readable summaries and structured findings.
- `redact.mjs`: redacts paths, environment variables, token-like strings, and provider config fragments.
- `tools/install-pi-plugin-codex.ps1`: user-level install/update/rollback script; writes receipts and does not edit plugin cache.
- `tools/check_pi_plugin_codex_contract.py`: static boundary checker that prevents directional regressions.

## 6. User-level install artifacts and receipt

After implementation is confirmed, the controlled installer syncs artifacts to user-level paths:

```text
%USERPROFILE%\.codex\tools\codex-pi\
  codex-pi.ps1
  codex-pi.cmd
  package\

%USERPROFILE%\.codex\state\pi-plugin-codex\
  tool-updates\
  jobs\<project_slug>\
  receipts\
```

Minimum install receipt:

```json
{
  "schema_version": 1,
  "tool": "pi-plugin-codex",
  "status": "installed|rolled_back|blocked",
  "installed_at": "2026-05-24T00:00:00Z",
  "source_repo": "D:/PythonProject_langgraph",
  "source_commit": "<git sha>",
  "source_path": "tools/plugin_sources/pi-plugin-codex",
  "install_root": "%USERPROFILE%/.codex/tools/codex-pi",
  "state_root": "%USERPROFILE%/.codex/state/pi-plugin-codex",
  "pi_binary": "pi",
  "pi_version": "<redacted or null>",
  "rpc_smoke": "passed|blocked:pi_not_installed|blocked:rpc_unavailable|failed",
  "read_only_smoke": "passed|not_run|failed",
  "rollback_pointer": "<previous receipt id or null>",
  "secrets_recorded": false
}
```

Rules:

- Without a receipt, the lane can only be `reference-only` or `planned`.
- With install receipt, setup smoke, and rollback pointer, it can become `on-demand`.
- It can become `active-candidate` only after real Pi read-only smoke passes.
- The installer does not directly edit `C:\Users\lenovo\.codex\config.toml`. If personal plugin marketplace registration is needed, first emit a dry-run diff and receipt, then ask for user confirmation.

### 6.1 `oh-my-pi` / OMP reference-sidecar governance

Rules moved from the main MCP/skills/browser/CLI governance plan belong here. The main plan keeps a reference-only link. This subsection does not mean `oh-my-pi` is installed; it defines the governance boundary for any future install or binary-override study.

Default state:

- `oh-my-pi` / `omp` is `reference-only` by default.
- Move to `planned/on-demand` only when the user explicitly requests Pi family sidecar adaptation and the related OpenSpec change is frozen.
- It does not replace Codex, native subagents, native_omx, LangGraph, `codex-ohmy`, or Codex `apply_patch`.

Future controlled install layout, only for a separate implementation:

```text
%USERPROFILE%\.codex\external\oh-my-pi\
%USERPROFILE%\.codex\tools\oh-my-pi\
%USERPROFILE%\.codex\state\tool-updates\oh-my-pi\
%USERPROFILE%\.codex\state\pi-plugin-codex\
```

Install, update, and rollback rules:

- Clone must be pinned to a commit or tag; a floating branch is not reproducible install evidence.
- Dependencies must live in the external directory, a user-level isolated runtime, or a controlled package directory. Do not perform unrecorded global installs.
- The wrapper must be thin and forward to the pinned package. Do not embed long prompts or copy vendor runtime into repository documents.
- Per-project state must live outside the source clone and include a project slug, session namespace, or workspace root hash. Repository evidence may keep only redacted summaries.
- The updater must fetch to a staging ref or staging package before smoke tests, wrapper help checks, RPC/read-only smoke when applicable, and authorization-guard checks.
- Switch the wrapper pin only after smoke passes, and write an update receipt for the switch.
- The update receipt must include source URL, pinned ref, install root, wrapper path, state root, smoke summary, rollback pointer, operator confirmation scope, and `secrets_recorded=false`.
- If smoke fails, keep using the previous pinned version and do not mark the failed version active.
- Rollback must be possible from receipt data alone and must not depend on chat history.

Reusable reference scope:

- hash-anchored edit research;
- CLI / harness operator ergonomics;
- sidecar stats, prompt UX, failure recovery, and receipt-first update patterns;
- `The Harness Problem` ideas for harness reliability, recoverable editing, and explicit failure surfacing.

Forbidden scope:

- Do not make `oh-my-pi` a Codex launcher.
- Do not make `omp` binary override the default Pi binary.
- Do not store `oh-my-pi` provider config, API keys, model files, or raw user paths in the repository.
- Do not let any Pi family runtime mutate the current worktree without one-task authorization and a read-only/write guard.

## 7. CLI JSON contract

### 7.1 `setup --json`

Successful shape:

```json
{
  "schema_version": 1,
  "ok": true,
  "command": "setup",
  "status": "ready",
  "pi_binary": "pi",
  "pi_version": "1.2.3",
  "rpc_smoke": "passed",
  "state_root": "%USERPROFILE%/.codex/state/pi-plugin-codex",
  "secrets_recorded": false
}
```

Pi missing shape:

```json
{
  "schema_version": 1,
  "ok": false,
  "command": "setup",
  "status": "blocked",
  "blocker": "pi_not_installed",
  "pi_binary": "pi",
  "pi_version": null,
  "rpc_smoke": "not_run",
  "secrets_recorded": false
}
```

### 7.2 `ask/review/adversarial-review --json`

Synchronous success shape:

```json
{
  "schema_version": 1,
  "ok": true,
  "command": "review",
  "job_id": "pi_20260524_153012_ab12cd",
  "status": "succeeded",
  "mode": "read-only",
  "result_path": "%USERPROFILE%/.codex/state/pi-plugin-codex/jobs/<project_slug>/pi_20260524_153012_ab12cd/result.json",
  "summary": "Pi found 2 review points.",
  "findings": [
    {
      "severity": "medium",
      "category": "test-gap",
      "message": "Add fake Pi malformed JSONL coverage before real smoke.",
      "path": "tests/pi-plugin-codex/pi-rpc-fixture.test.mjs"
    }
  ],
  "read_only_guard": {
    "before_dirty": false,
    "after_dirty": false,
    "changed": false,
    "diff_stat_before": "",
    "diff_stat_after": ""
  },
  "secrets_recorded": false
}
```

Read-only guard failure shape:

```json
{
  "schema_version": 1,
  "ok": false,
  "command": "review",
  "job_id": "pi_20260524_153012_ab12cd",
  "status": "failed",
  "blocker": "blocked:worktree_changed_by_read_only_pi",
  "read_only_guard": {
    "before_dirty": false,
    "after_dirty": true,
    "changed": true
  },
  "result_path": null,
  "secrets_recorded": false
}
```

### 7.3 `status/result/cancel --json`

- `status` without a job id lists the current project slug's latest redacted job summaries.
- `result <job-id>` reads only a job under the current project slug.
- `cancel <job-id>` cancels only `queued|running` jobs; a missing pid with running state returns `stale_running_state` and suggests `codex-pi status --repair --json`.

## 8. Pi binary and RPC rules

Default binary is `pi`. Optional override:

```powershell
$env:CODEX_PI_BINARY = "pi"
$env:CODEX_PI_BINARY = "omp"
```

Rules:

- Override accepts only a binary name without path or an explicitly trusted absolute path; absolute path evidence must be redacted in local receipts.
- `setup` detects binary, version, RPC smoke, and provider readiness. It must not read, print, or commit raw `~/.pi/agent/models.json`.
- Provider API keys are managed only by Pi or environment variables. `codex-pi` does not persist secrets.
- Each task starts one isolated `pi --mode rpc` process. Default timeout is 180 seconds; user may pass `--timeout-seconds 30..900`.
- stdout/stderr must be redacted. Raw stderr may be written only to user-level result files after redaction.
- malformed JSONL, no final message, timeout, and spawn failure return distinct blockers: `rpc_malformed_event`, `rpc_no_final_message`, `rpc_timeout`, and `pi_spawn_failed`.

## 9. Job state schema

Job state contains at least:

```json
{
  "schema_version": 1,
  "job_id": "pi_20260524_153012_ab12cd",
  "project_slug": "pythonproject_langgraph",
  "workspace_root_hash": "sha256:...",
  "command": "review",
  "mode": "read-only",
  "pi_binary": "pi",
  "model_hint": null,
  "status": "queued|running|succeeded|failed|canceled|timed_out",
  "started_at": "2026-05-24T15:30:12Z",
  "finished_at": null,
  "pid": 12345,
  "prompt_path": "%USERPROFILE%/.codex/state/pi-plugin-codex/jobs/<project_slug>/<job_id>/prompt.redacted.md",
  "result_path": "%USERPROFILE%/.codex/state/pi-plugin-codex/jobs/<project_slug>/<job_id>/result.json",
  "read_only_guard": {
    "before_dirty": false,
    "after_dirty": null,
    "changed": null
  },
  "redacted_error": null
}
```

It must not contain API keys, raw provider config, cookies, tokens, full personal directories, unredacted shell environment dumps, raw `models.json`, or full browser/chat content.

## 10. Read-only guard algorithm

P0 `ask`, `review`, and `adversarial-review` execute this algorithm:

1. Find repo root with `git rev-parse --show-toplevel`; on failure enter non-git read-only mode and allow stdin analysis only.
2. Record before fingerprint:
   - `git status --porcelain=v1 -uno`;
   - `git diff --stat`;
   - `git diff --name-only`;
   - `git diff --cached --name-only` captures staged changed paths for the guard.
3. Render the prompt with an explicit constraint that Pi must not modify files, run write commands, or do anything except output advice.
4. Run `pi --mode rpc`.
5. Record after fingerprint.
6. If before/after differ:
   - job status = `failed`;
   - blocker = `blocked:worktree_changed_by_read_only_pi`;
   - result emits only a redacted warning and changed-path summary;
   - Codex must not use the job as valid review evidence.
7. If unchanged, emit a findings summary.

Dirty worktree policy:

- Read-only review is allowed when the worktree is already dirty.
- The guard compares before and after fingerprints; it does not require clean entry.
- Review of staged diff requires explicit `--staged`; otherwise default to unstaged plus staged summary.

## 11. Implementation task split

### Task 0: OpenSpec change and boundary freeze

Files:

- Create: `openspec/changes/add-pi-plugin-codex-sidecar/proposal.md`
- Create: `openspec/changes/add-pi-plugin-codex-sidecar/design.md`
- Create: `openspec/changes/add-pi-plugin-codex-sidecar/tasks.md`
- Create/Modify: `openspec/changes/add-pi-plugin-codex-sidecar/specs/codex-user-level-tooling/spec.md`

Steps:

- [ ] Write proposal: Codex -> Pi read-only sidecar only; Pi -> Codex, `pi-codex`, and P1 rescue are out of scope.
- [ ] Write design: capture architecture, JSON contract, and read-only guard.
- [ ] Write tasks: copy this section into the OpenSpec checklist.
- [ ] Run `python .\tools\run_openspec_guard.py --root .`, expect exit 0.
- [ ] Commit the proposal or keep it in the same feature branch as implementation per repository release policy.

### Task 1: Scaffold repo-local plugin source

Files:

- Create: `tools/plugin_sources/pi-plugin-codex/.codex-plugin/plugin.json`
- Create: `tools/plugin_sources/pi-plugin-codex/skills/pi-codex/SKILL.md`
- Create: `tools/plugin_sources/pi-plugin-codex/LICENSE`
- Create: `tools/plugin_sources/pi-plugin-codex/NOTICE`
- Create: `tests/pi-plugin-codex/plugin-manifest.test.mjs`

Steps:

- [ ] Manifest names the plugin `pi-plugin-codex` and exposes only `pi-codex` skill.
- [ ] Skill says Pi output is sidecar evidence, not final verification.
- [ ] Skill routes only to `codex-pi` wrapper commands.
- [ ] LICENSE and NOTICE preserve attribution from allowed reference code.
- [ ] Test blocks Claude Code-only plugin artifacts from being copied directly.

### Task 2: CLI entrypoint and setup

Files:

- Create: `tools/plugin_sources/pi-plugin-codex/scripts/codex-pi.mjs`
- Create: `tools/plugin_sources/pi-plugin-codex/scripts/lib/redact.mjs`
- Create: `tests/pi-plugin-codex/codex-pi-cli.test.mjs`

Steps:

- [ ] Implement `setup/status/result/cancel/ask/review/adversarial-review` argument parsing.
- [ ] `setup --json` detects Pi binary and returns stable blockers.
- [ ] stdout is JSON only; human text goes to stderr only when safe.
- [ ] Redact full user paths, tokens, provider config fragments, and API-key-like strings.
- [ ] Run `node --test tests/pi-plugin-codex/codex-pi-cli.test.mjs`, expect pass.

### Task 3: Fake Pi RPC fixture and parser

Files:

- Create: `tools/plugin_sources/pi-plugin-codex/fixtures/fake-pi.mjs`
- Create: `tools/plugin_sources/pi-plugin-codex/scripts/lib/pi-rpc.mjs`
- Create: `tests/pi-plugin-codex/pi-rpc-fixture.test.mjs`

Steps:

- [ ] `fake-pi.mjs` supports `--mode rpc` and emits success, malformed-jsonl, and no-final-message fixtures.
- [ ] `pi-rpc.mjs` starts child process, sends prompt, and parses JSONL events line by line.
- [ ] Parser extracts final assistant message.
- [ ] Missing final message returns `rpc_no_final_message`.
- [ ] Malformed JSONL returns `rpc_malformed_event` and does not write raw stderr to repository files.
- [ ] Timeout kills the child process and returns `rpc_timeout`.
- [ ] Run `node --test tests/pi-plugin-codex/pi-rpc-fixture.test.mjs`, expect pass.

### Task 4: Job control, state, and cancel

Files:

- Create: `tools/plugin_sources/pi-plugin-codex/scripts/lib/job-control.mjs`
- Create: `tools/plugin_sources/pi-plugin-codex/scripts/lib/redact.mjs`
- Create: `tests/pi-plugin-codex/job-control.test.mjs`

Steps:

- [ ] Implement project slug from git remote/repo basename, falling back to cwd basename.
- [ ] Write only slug and workspace root hash, not full root path.
- [ ] Implement job id `pi_YYYYMMDD_HHMMSS_<6hex>`.
- [ ] Implement state transitions `queued -> running -> succeeded|failed|canceled|timed_out`.
- [ ] `status --json` lists only current project slug jobs.
- [ ] `result <job-id> --json` reads only current project slug results.
- [ ] `cancel <job-id> --json` terminates a running pid; missing pid returns `stale_running_state`.
- [ ] Run `node --test tests/pi-plugin-codex/job-control.test.mjs`, expect pass.

### Task 5: Git target and read-only guard

Files:

- Create: `tools/plugin_sources/pi-plugin-codex/scripts/lib/git-targets.mjs`
- Create: `tools/plugin_sources/pi-plugin-codex/scripts/lib/read-only-guard.mjs`
- Create: `tests/pi-plugin-codex/read-only-guard.test.mjs`

Steps:

- [ ] Implement repo root, staged/unstaged file list, and diff stat detection.
- [ ] Return structured blockers when git commands fail.
- [ ] Allow dirty entry but require unchanged before/after fingerprint.
- [ ] Verify clean no-op Pi leaves fingerprint unchanged.
- [ ] Simulate a mutating fake Pi and require `blocked:worktree_changed_by_read_only_pi`.
- [ ] Run `node --test tests/pi-plugin-codex/read-only-guard.test.mjs`, expect pass.

### Task 6: Prompts and render

Files:

- Create: `tools/plugin_sources/pi-plugin-codex/prompts/ask.md`
- Create: `tools/plugin_sources/pi-plugin-codex/prompts/review.md`
- Create: `tools/plugin_sources/pi-plugin-codex/prompts/adversarial-review.md`
- Create: `tools/plugin_sources/pi-plugin-codex/scripts/lib/render.mjs`
- Create: `tests/pi-plugin-codex/render.test.mjs`

Steps:

- [ ] Prompts state read-only constraints and no file mutation.
- [ ] Review prompt includes diff stat and changed paths only, not raw secrets.
- [ ] Render returns severity/category/message/path findings.
- [ ] Adversarial review supports focus strings without shell injection.
- [ ] Run `node --test tests/pi-plugin-codex/render.test.mjs`, expect pass.

### Task 7: User-level installer and rollback

Files:

- Create: `tools/install-pi-plugin-codex.ps1`
- Create: `tests/pi-plugin-codex/install-dry-run.test.mjs`

Steps:

- [ ] Default dry-run prints target paths and planned receipt.
- [ ] `-Apply` copies package to `%USERPROFILE%\.codex\tools\codex-pi\package` and creates wrappers.
- [ ] `codex-pi.ps1` forwards to package Node entrypoint only; no long payload.
- [ ] `codex-pi.cmd` invokes the PowerShell wrapper.
- [ ] Read prior receipt and write rollback pointer before install/update.
- [ ] Smoke failure prevents active status and preserves prior version.
- [ ] Run `node --test tests/pi-plugin-codex/install-dry-run.test.mjs`, expect pass.

### Task 8: Governance docs and checker

Files:

- Modify: `docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md`
- Modify: `docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md`
- Create: `tools/check_pi_plugin_codex_contract.py`
- Create: `tests/pi-plugin-codex/docs-boundary.test.mjs`

Steps:

- [x] Move the direct `oh-my-pi` install section from the main governance plan into this Pi sidecar plan, and make the main plan reference-only.
- [x] Keep readiness states: `pi=on-demand`, `oh-my-pi/omp=reference-only`, `pi-plugin-codex=planned/on-demand`, `pi-plugin-cc=reference-only Claude Code only`, `pi-codex=non-goal reverse bridge`.
- [ ] Change OpenSpec slice 6 to `Pi family sidecar` where implementation is actually added.
- [ ] Add Pi binary, RPC smoke, job state path, and read-only guard evidence to receipt schema.
- [ ] Checker blocks documenting `pi-codex` as a dependency, documenting `pi-plugin-cc` as directly installable Codex plugin, or changing `codex-ohmy` into a Pi launcher.
- [ ] Run `python .\tools\check_pi_plugin_codex_contract.py --root . --json`, expect ok.

### Task 9: Real Pi smoke (conditional)

Files:

- Modify: `tools/plugin_sources/pi-plugin-codex/skills/pi-codex/SKILL.md`
- Modify: `docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md` only for redacted summaries.

Steps:

- [ ] Run `codex-pi setup --json`.
- [ ] If Pi is missing, record `blocked:pi_not_installed` and do not mark the lane active.
- [ ] If Pi is installed, run `codex-pi ask --read-only --stdin --json` with a non-sensitive smoke prompt.
- [ ] Run `codex-pi review --read-only --json` and require read-only guard `changed=false`.
- [ ] Commit only redacted smoke summary and blocker/status, not provider, API key, or full user path.

### Task 10: Full verification, commit, and local integration

Files:

- Modify/Create all files above.

Steps:

- [ ] Run `node --test tests/pi-plugin-codex/*.test.mjs`, expect pass.
- [ ] Run `python .\tools\check_pi_plugin_codex_contract.py --root . --json`, expect ok.
- [ ] Run `python .\tools\check_implementation_plan_rules.py --root . --json`, expect ok.
- [ ] Run `python .\tools\run_openspec_guard.py --root . --json`, expect ok.
- [ ] Run `python .\tools\check_precommit_update_archive.py --root . --json`, expect ok.
- [ ] Commit the feature branch.
- [ ] Run `tools/ci/local_gate.ps1` and `tools/ci/local_mr_review.ps1`.
- [ ] After user-approved local integration, fast-forward local `main`; remote publication still requires separate explicit approval.

## 12. P0 / P1 readiness gates

| Lane | Available commands | Required evidence | Forbidden actions |
| --- | --- | --- | --- |
| P0 reference-only | document reading | this plan + OpenSpec proposal | no install, no Pi invocation |
| P0 planned/on-demand | `setup/status/result` dry-run | CLI tests + installer dry-run + receipt schema | do not write plugin cache; do not edit Codex config |
| P0 read-only active-candidate | `ask/review/adversarial-review --read-only` | fake Pi tests + real Pi smoke if installed + read-only guard `changed=false` | do not write current worktree; do not treat Pi output as final verification |
| P1 worktree-isolated rescue | `rescue --worktree-isolated` | isolated worktree ownership + changed paths summary + Codex leader handoff | do not let Pi write the main worktree |

## 13. Verification plan

Minimum static verification:

```powershell
python .\tools\check_implementation_plan_rules.py --root . --json
python .\tools\run_openspec_guard.py --root .
```

Implementation verification:

```powershell
node --test tests/pi-plugin-codex/*.test.mjs
python .\tools\check_pi_plugin_codex_contract.py --root . --json
python .\tools\check_precommit_update_archive.py --root . --json
.\tools\ci\local_gate.ps1
.\tools\ci\local_mr_review.ps1
```

Test scenario checklist:

- fake Pi returns a final assistant message.
- fake Pi emits malformed JSONL.
- fake Pi emits no final message.
- fake Pi hangs and triggers timeout.
- cancel terminates a background job.
- status/result cannot read across project slugs.
- read-only commands leave worktree fingerprint unchanged.
- read-only mutation fixture triggers `blocked:worktree_changed_by_read_only_pi`.
- `setup` returns stable blockers for missing Pi, unconfigured provider, and unavailable RPC.
- docs checker blocks `pi-codex` as dependency.
- docs checker blocks `pi-plugin-cc` as directly installable Codex plugin.
- docs checker blocks rewriting `codex-ohmy` as a Pi launcher.
- installer dry-run writes no user-level directory; `-Apply` writes receipt.
- receipt contains no secrets, tokens, full personal directories, or raw provider config.

## 14. Rollback and cleanup

- Installer reads the prior receipt before every `-Apply` and writes the previous package path or version summary as rollback pointer.
- `tools/install-pi-plugin-codex.ps1 -Rollback <receipt-id>` restores only `%USERPROFILE%\.codex\tools\codex-pi\package` and launcher; it does not delete job history.
- `codex-pi status --repair --json` repairs only stale running state for the current project slug and records pid-missing or child-exited evidence.
- `codex-pi cleanup --older-than-days <N> --json` can be a P0.5 increment; default dry-run, `--apply` deletes old results.
- Remote publication, personal marketplace registration, and global PATH mutation are outside the default rollback scope and require separate user approval plus receipts.

## 15. Required updates to existing governance plans

After confirmation, update:

```text
docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
```

Required changes:

- Change the direct `oh-my-pi` installation/adaptation section in the main governance plan into a Codex reusable harness reference boundary.
- Keep `oh-my-pi/omp` as `reference-only` in the main plan and delegate Pi sidecar installation/update/rollback here.
- Keep `pi-plugin-codex` as `planned/on-demand` until implementation evidence exists.
- Keep `pi-plugin-cc` as `reference-only, Claude Code only`.
- Keep `pi-codex` as `non-goal, reverse bridge`.
- The main plan must not mark any Pi family lane active before real smoke and read-only guard evidence exist.

## 16. Risks and default decisions

Risks:

- Pi default model/provider may differ from Codex; quality and cost cannot be fully controlled by Codex.
- Pi may have editing capability; P0 must constrain it through read-only prompts and worktree diff guards.
- Claude Code plugin surfaces differ from Codex plugin surfaces; direct forks can retain invalid `.claude-plugin` structure.
- Background jobs can remain stale; job state, pid, cancel, timeout, and cleanup are required.
- User-level installation can pollute personal environment; installer must default to dry-run, write receipts first, and support rollback.

Default decisions:

- P0 is read-only sidecar only.
- P1 adds worktree-isolated rescue later.
- Codex leader keeps final integration authority.
- `pi-codex` is not implemented.
- `codex-ohmy` startup semantics do not change.
- Missing real Pi is not implementation failure; it keeps smoke status at `blocked:pi_not_installed`.

## 17. Self-checklist

- [x] Direction boundary is clear: Codex -> Pi, not Pi -> Codex.
- [x] File ownership is clear: repo-local source, installer, tests, OpenSpec, and governance docs all have paths.
- [x] CLI contract is clear: setup, ask/review/adversarial-review, status/result/cancel all have JSON shapes.
- [x] Read-only guard is testable: before/after fingerprint and blocker are defined.
- [x] Receipt/rollback is testable: dry-run, apply, and rollback pointer are defined.
- [x] P0/P1 split is clear: P0 does not write current worktree; P1 uses an isolated worktree.
- [x] Governance linkage is clear: existing `user_level_mcp_skills_browser_cli_governance_plan.*` update points are listed and direct `oh-my-pi` implementation content has moved here.
- [x] Pre-commit verification commands are clear: implementation plan checker, OpenSpec guard, precommit gate, local gate, local MR review.

## 18. Sources

- https://github.com/can1357/oh-my-pi
- https://blog.can.ac/2026/02/12/the-harness-problem/
- `reference_files/3.md` - local captured reference-link list for this plan.
