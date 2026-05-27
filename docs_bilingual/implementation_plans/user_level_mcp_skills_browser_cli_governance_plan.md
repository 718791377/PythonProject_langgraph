---
doc_id: user_level_mcp_skills_browser_cli_governance_plan
lang: en
canonical: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
translation_of: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
status: draft
plan_readiness: execution-ready
implementation_state: cdp_bridge_read_only_defaults_repo_local_implemented
last_reviewed_at: 2026-05-27
doc_class: implementation_plan
created_at: 2026-05-22
source_reference_file: reference_files/1.md
comet_workflow: full
comet_phase_model: open-design-build-verify-archive
implementation_lane: p0_repo_local_governance_to_user_level_capability
local_codex_governance_fork_reference: docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.md
related_docs:
  - docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.md
  - docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.md
  - docs_bilingual/governance/codex_user_level_mcp_scope_policy.md
  - docs_bilingual/governance/codex_user_level_skills_governance_policy.md
---

# User-Level MCP, Skills, Browser, and CLI Harness Governance Implementation Plan (Modern Comet Structure)

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:executing-plans`; use `superpowers:subagent-driven-development` only for cross-file implementation work. Track all steps with checkboxes and run each local verification before moving on. Remote publication is not authorized by this plan.

**Goal:** Govern Codex user-level MCP, skills, browser automation, and CLI harness capabilities as a low-Token, low-risk, auditable, rollback-capable, cross-project control surface.

**Architecture:** Codex reads repo-local policy, OpenSpec, and checkers first. Low-risk discovery uses `skills2cli`, `mcp2cli`, `codex-port`, and the browser owner registry. High-risk MCP calls, CDP Bridge, OpenCLI, CLI-Anything, `wecom-cli`, cookies, or WXWork operations require an authorization receipt schema plus update receipt, rollback pointer, and redaction evidence.

**Tech Stack:** Codex user-level wrappers, Python checkers, PowerShell launchers, JSON receipts, OpenSpec deltas, Superpowers evidence, Git worktrees, CDP Bridge, chrome-devtools-mcp, OpenCLI, CLI-Anything, WeCom/WXWork adapter, and `C:\Users\lenovo\.codex` user-level runtime state.

---

## 0. Current review verdict

This version is reworked into the modern structure family used by the Pi sidecar plan and the Comet runtime plan: worker instructions, Goal, Architecture, Tech Stack, relationship boundaries, runtime contracts, file responsibility map, definition of ready, task-level backlog, acceptance criteria, required evidence, and rollback rules.

`status: draft` means the full user-level install, live smoke tests, and cross-project rollout are not complete. `plan_readiness: execution-ready` means the plan has enough structure and granularity for an agentic worker. Repo-local `skills2cli`, `mcp2cli`, `codex-port`, browser owner registry, `chrome-devtools-mcp` wrapper MVP, and CDP Bridge read-only defaults are implemented-local. A lane becomes active only after installation receipt, update receipt, smoke test result, and rollback pointer evidence exist.

## 1. Relationship model and naming boundary

| Name | Responsibility | Default state | Boundary |
| --- | --- | --- | --- |
| `skills2cli` | skill index/search/show/audit/profile suggest | implemented-local | Keeps full skill bodies out of model context and reduces Token budget pressure. |
| `mcp2cli` | MCP list/search/show/call facade | implemented-local | Discovery is low risk; real calls are risk-gated and fail closed. |
| `codex-port` | port registry, lease, pending_bind, registry_revision | implemented-local | Codex ranges precede downstream project ranges. |
| browser owner registry | browser asset registration and leases | implemented-local | Separates isolated-session-managed, project-profile, and human-owned assets. |
| `chrome-devtools-mcp` | user-level DevTools MCP wrapper | implemented-local | Read-only first; writes need owner evidence and authorization receipt. |
| CDP Bridge | browser bridge and CDP actions | implemented-local | Read-only by default; cookies, input, click, and navigation are sensitive. |
| OpenCLI | on-demand browser/MCP adapter | planned/partial | Must use `--port auto` and owner/receipt gates. |
| CLI-Anything | GUI/CLI harness generation and reference | planned | Hard-loading many skills is blocked by default. |
| `wecom-cli` | WeCom/WXWork API, webhook, and GUI adapter | planned | WXWork.exe GUI writes are disabled by default. |
| `oh-my-pi` | Pi family and harness reference | reference-only | Detailed Pi sidecar work belongs to the Pi sidecar plan. |
| `ohmyopenagent` / `snow-cli` | future durable-team reference source | reference-only | Not installed or wired by this plan. |
| human-owned Chrome | personal browser assets | disabled for automation by default | No cookies, tokens, or raw browser data without explicit approval. |

## 2. Goals and non-goals

Goals:

- [ ] Prefer lowest Token and lowest risk discovery: repo docs, `skills2cli index/search`, and `mcp2cli list/search/show`.
- [ ] Use `skills2cli` instead of persistent skill body injection to avoid plugin description dumps and skill context budget overflow.
- [ ] Use `mcp2cli` to separate MCP discovery, profile selection, and execution; sensitive MCP calls fail closed by default.
- [ ] Use browser owner registry for isolated-session-managed, project-profile, and human-owned Chrome assets.
- [ ] Use `codex-port` for port registry, pending_bind, registry_revision, lease renewal, and crash recovery.
- [ ] Use authorization receipt schema, update receipt, rollback pointer, and evidence redaction for auditability and rollback.

Non-goals:

- [ ] Do not hard-load every MCP or skill.
- [ ] Do not disable useful Browser, OpenCLI, WeCom, or Vercel capability only to reduce Token usage.
- [ ] Do not modify `C:\Users\lenovo\.codex` without a receipt.
- [ ] Do not read or expose secrets, cookies, tokens, raw browser data, WeCom message contents, or plugin description dumps.
- [ ] Do not turn OpenCLI, CDP Bridge, or CLI-Anything into default high-privilege automation lanes.

## 3. Runtime architecture

```text
Codex session
  -> repo-local policy / OpenSpec / checkers
  -> skills2cli compact discovery
  -> mcp2cli compact discovery and gated calls
  -> codex-port registry / lease / pending_bind
  -> browser owner registry
  -> chrome-devtools-mcp / CDP Bridge / OpenCLI
  -> CLI-Anything / wecom-cli guarded adapters
  -> user-level receipt / state / rollback evidence
```

Default user-level artifact roots are `C:\Users\lenovo\.codex\tools\skills2cli\`, `C:\Users\lenovo\.codex\tools\mcp2cli\`, `C:\Users\lenovo\.codex\tools\codex-port\`, `C:\Users\lenovo\.codex\tools\browser-automation\`, and `C:\Users\lenovo\.codex\tools\wecom-cli\`. Runtime state lives under `C:\Users\lenovo\.codex\state\`; repo-local source stays canonical.

## 4. Codex usage model

- [ ] Read repo-local policy, OpenSpec, and checkers before deciding whether MCP, skills, browser automation, or CLI harness capability is needed.
- [ ] In discovery, prefer compact JSON output instead of full skill bodies or plugin descriptions.
- [ ] `skills2cli show` returns summaries by default; full body access needs a task-specific reason.
- [ ] `mcp2cli call`, browser writes, CDP input, OpenCLI execution, and WeCom GUI actions require an authorization receipt schema first.
- [ ] Ports must use `codex-port lease reserve --owner codex --purpose <tool> --port auto --json`.
- [ ] OpenCLI must use `--port auto`; hard-coded colliding ports are not allowed.
- [ ] WeCom defaults to API or webhook; GUI attach requires operator confirmation, a global WXWork.exe lease, and timeout cleanup.

## 5. Repo-local source of truth

| Category | Repo-local source | User-level artifact | Update rule |
| --- | --- | --- | --- |
| policy | `docs_bilingual/governance/*`, `openspec/specs/*` | generated launcher/helper config | Policy changes first; installer output later. |
| plan | `docs_bilingual/implementation_plans/*` | no direct runtime artifact | A plan is not an active runtime. |
| checker | `tools/check_*.py`, `tools/ci/local_gate.ps1` | optional installed checker copy | Repo-local stays canonical. |
| helper source | repo-local tools/templates | `C:\Users\lenovo\.codex\tools\...` | User-level copy is install artifact only. |
| receipt schema | docs, tests, OpenSpec | redacted runtime JSON receipt | No secrets allowed. |
| OpenSpec | `openspec/changes/*`, `openspec/specs/*` | none | WHAT governance evidence. |
| Superpowers | `docs/superpowers/*` | none | HOW execution evidence. |

## 6. Installation and update evidence contract

Every user-level install or update must create an update receipt. Without receipt evidence, a lane can only be planned, partial, or implemented-local; it cannot be active.

| field | required | description |
| --- | --- | --- |
| tool name | yes | Lane id, such as `skills2cli`, `mcp2cli`, or `codex-port`. |
| installed version | yes | Commit, tag, or package version. |
| source URL | yes | Must not include tokens. |
| install path | yes | User-level install directory. |
| wrapper path | yes | Launcher or wrapper path. |
| state path | yes | Runtime state root. |
| smoke test command | yes | Repeatable command. |
| smoke test result | yes | pass/fail plus timestamp. |
| updater command | yes | Must be pin-aware. |
| rollback pointer | yes | Prior version, backup directory, or git ref. |
| owner lane | yes | `skills2cli`, `mcp2cli`, `browser`, `wecom-cli`, and similar. |
| redaction status | yes | Confirms no secrets, cookies, tokens, or raw browser data. |

## 7. Token and risk priority model

| Priority | Surface | Token | Risk | Default action |
| --- | --- | --- | --- | --- |
| P0 | repo docs/checkers/OpenSpec | low | low | Read directly. |
| P1 | `skills2cli index/search` | low | low | Compact summary. |
| P1 | `mcp2cli list/search/show` | low | low | Compact summary. |
| P2 | browser tab inventory | medium | medium | Read-only plus owner evidence. |
| P2 | OpenCLI discovery | medium | medium | On-demand plus port lease. |
| P3 | MCP call | high | high | authorization receipt. |
| P3 | CDP Bridge JS / cookies | high | high | authorization receipt plus redaction. |
| P3 | `wecom-cli gui attach` | high | high | disabled by default. |
| P3 | human-owned Chrome assets | high | high | operator confirmation required. |

## 8. User-level port governance

The port registry is owned by `codex-port` and must support `registry_revision`, atomic writes, `pending_bind`, lease renewal, and crash recovery.

| Owner | Range | Description |
| --- | --- | --- |
| Codex general helpers | `39000-39299` | Default Codex user-level helper range. |
| Codex browser/OpenCLI | `39300-39499` | OpenCLI must use `--port auto`. |
| Reserved local bridge | `39500-39999` | Reserved for local bridge use. |
| Downstream consumer project range | `40000-40999` | Downstream project ports come after Codex. |
| Emergency quarantine | `41000-41099` | Temporary collision isolation only. |

| Command | Purpose | Receipt |
| --- | --- | --- |
| `codex-port registry show --json` | Read port registry | No write. |
| `codex-port lease reserve --owner <name> --port auto --json` | Allocate automatically | lease receipt. |
| `codex-port lease renew --lease-id <id> --json` | Renew | updated lease. |
| `codex-port lease release --lease-id <id> --json` | Release | completed receipt. |
| `codex-port import-legacy --owner <name> --json` | Import old ports | migration receipt. |
| `codex-port gc --dry-run --json` | Stale scan | No write. |
| `codex-port gc --apply --json` | Stale cleanup | evidence-gated write. |

## 9. CLI JSON contracts

### 9.1 `skills2cli` lane contract

| Command | Default output | Risk gate |
| --- | --- | --- |
| `skills2cli index --json` | skill name, source, short description hash | read-only. |
| `skills2cli search <query> --json` | compact candidates | read-only. |
| `skills2cli show <name> --json` | summary, entrypoint, risk metadata | full body opt-in. |
| `skills2cli audit warnings --json` | warning summary | redact paths/content. |
| `skills2cli profile suggest --task <task> --json` | profile suggestion | preview only. |

### 9.2 `mcp2cli` lane contract

| Command | Default output | Risk gate |
| --- | --- | --- |
| `mcp2cli list --json` | server list and enabled state | read-only. |
| `mcp2cli search <query> --json` | compact capabilities | read-only. |
| `mcp2cli show <server> --json` | tool summaries | no secrets. |
| `mcp2cli call <server> <tool> --json` | guarded execution | authorization receipt required for sensitive calls. |
| `mcp2cli profile suggest --task <task> --json` | profile preview | no config mutation. |

## 10. Browser, OpenCLI, CDP, and WeCom risk gates

| Lane | Read-only allowed | Sensitive action | Required gate |
| --- | --- | --- | --- |
| isolated-session-managed | tab inventory, screenshot | click/type/navigate | owner lease plus authorization receipt. |
| project-profile | inventory with project lease | profile mutation | project authorization plus retention policy. |
| human-owned Chrome | none by default | cookies, tokens, history, message contents | explicit operator confirmation. |
| CDP Bridge | tab inventory | JS execution, cookies, form input | owner lease plus action scope. |
| OpenCLI | discovery | adapter execute | `--port auto` plus receipt. |
| CLI-Anything | harness plan | hard-load or live control | disabled until receipt and smoke pass. |
| `wecom-cli` | API status | WXWork.exe GUI automation | global WXWork lease plus operator confirmation. |

The authorization receipt schema must include `action`, `target`, `scope`, `expiry`, `session`, `operator confirmation`, `owner lane`, `redaction policy`, and `rollback pointer`.

## 11. Runtime state contract

| State | Meaning | Allowed next state |
| --- | --- | --- |
| planned | Plan exists but repo-local helper is absent. | implemented-local. |
| implemented-local | Repo-local source/checker exists. | install-ready. |
| install-ready | User-level artifact can be generated. | active or blocked. |
| active | update receipt, smoke test, and rollback pointer exist. | update-needed or disabled. |
| on-demand | Starts only for a task and is not persistent. | active or disabled. |
| disabled | Closed by default. | on-demand. |
| reference-only | Reference source only. | planned. |
| blocked | Missing receipt, smoke, permission, or safety evidence. | install-ready. |

Runtime receipts must not include secrets, cookies, tokens, raw browser data, WeCom message contents, or full plugin description dumps.

## 12. Comet Management Record template

```markdown
# Comet Management Record

## Open / Initiating
- [ ] Value and why are stated.
- [ ] Success criteria are measurable.
- [ ] Stakeholders, constraints, or operating boundaries are identified.

## Design / Planning
- [ ] Delivery approach is tailored: predictive, agile, or hybrid.
- [ ] Major risks and assumptions are recorded.
- [ ] Acceptance evidence path is defined.

## Build / Executing
- [ ] Execution mode is selected.
- [ ] Quality evidence is recorded: TDD, review, test, or equivalent.
- [ ] Blockers are cleared or have an explicit decision.

## Verify / Controlling
- [ ] Variance from scope, design, and acceptance criteria is checked.
- [ ] Risk and change impact are assessed.
- [ ] Control decision is recorded.

## Archive / Closing
- [ ] Value outcome is summarized.
- [ ] Lessons learned or reusable guidance are recorded.
- [ ] Delta spec sync, verification evidence, and archive path are confirmed.

## Monitoring Loop
- [ ] Current facts are checked.
- [ ] Continue, adjust, stop, or return decision is made.
- [ ] If returning, target_phase and rework_reason are recorded.
```

## 13. Phase gate matrix

| Comet phase | Required evidence | Gate |
| --- | --- | --- |
| Open | scope, non-goals, risk lanes, reference-only list | no unmanaged user-level mutation. |
| Design | architecture, state contract, authorization schema | no high-risk lane without receipt design. |
| Build | helper source, tests, docs, receipt samples | no install without rollback pointer. |
| Verify | local gate, local MR review, manual structure review | no merge if required sections are missing. |
| Archive | stable spec sync or explicit archive deferral | no remote publish without explicit approval. |
| Monitoring | current facts, variance, return decision | return to an earlier phase if evidence is incomplete. |

## 14. Monitoring return semantics

| Decision | Meaning | Required fields |
| --- | --- | --- |
| `continue` | Comet control decision value meaning the current evidence is sufficient for normal phase progress. | Record current facts and the evidence date. |
| `adjust-current` | Comet control decision value meaning the current phase needs a local correction before progress. | Record the blocker, owner, and correction scope. |
| `return-open` | Comet control decision value meaning scope or value definition must return to the Open phase. | Set target_phase=open and record rework_reason. |
| `return-design` | Comet control decision value meaning architecture or safety boundaries must return to the Design phase. | Set target_phase=design and record rework_reason. |
| `return-build` | Comet control decision value meaning implementation evidence must return to the Build phase. | Set target_phase=build and record rework_reason. |
| `return-verify` | Comet control decision value meaning verification evidence must return to the Verify phase. | Set target_phase=verify and record rework_reason. |
| `stop` | Comet control decision value meaning risk, authorization, or policy blocks phase progress. | Record the blocker and next user decision. |

## 15. OpenSpec slice delivery matrix

| Slice | Scope | Output | Local verification |
| --- | --- | --- | --- |
| Slice 0 | OpenSpec / Comet evidence | proposal, design, tasks, management, delta spec | `openspec validate --all`. |
| Slice 1 | `skills2cli` governance | compact index/search/show/audit contract | unit tests plus baseline checker. |
| Slice 2 | `mcp2cli` governance | discovery/call/risk profile contract | unit tests plus fail-closed tests. |
| Slice 3 | `codex-port` governance | port registry, pending_bind, registry_revision | port allocator tests. |
| Slice 4 | browser owner registry | isolated/project/human asset model | owner registry tests. |
| Slice 5 | CDP/OpenCLI/chrome-devtools-mcp | read-only defaults plus sensitive gates | CDP/OpenCLI governance tests. |
| Slice 6 | CLI-Anything / `wecom-cli` | generation-first and WXWork guard | fixture tests, no live GUI by default. |
| Slice 7 | receipts / rollback / redaction | update receipt, authorization receipt, rollback pointer | redaction and schema checks. |
| Slice 8 | local integration | local gate, local MR review, commit, local main merge | clean worktree plus rollback ref. |

### Slice completion rule

- [ ] Every slice must have repo-local source, checker, or fixture test.
- [ ] Every slice must state whether it has a user-level install artifact.
- [ ] Every slice must keep a rollback pointer or state that installation has not happened.
- [ ] Any sensitive lane missing a receipt cannot be marked active.

## 16. File responsibility map

| File group | Responsibility | Owner lane |
| --- | --- | --- |
| `docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.*` | this plan and English companion | governance plan. |
| `openspec/changes/*/specs/codex-user-level-mcp-skills-browser-cli-governance/spec.*` | WHAT delta spec | OpenSpec. |
| `docs/superpowers/specs/*user-level-mcp*` | HOW design evidence | Superpowers. |
| `tools/check_user_level_mcp_skills_browser_cli_baseline.py` | baseline markers and safety registration | checker. |
| `tools/*skills2cli*` | skill compact facade | skills2cli. |
| `tools/*mcp2cli*` | MCP compact facade | mcp2cli. |
| `tools/*codex_port*` | port registry and lease | codex-port. |
| `tools/*browser*` | browser owner registry | browser. |
| user-level `C:\Users\lenovo\.codex\tools\...` | installed helper copy | install artifact only. |

## 17. Definition of ready before implementation

- [ ] Readiness gate: this plan and its English companion are updated.
- [ ] Readiness gate: OpenSpec change has proposal, design, tasks, delta spec, and management record.
- [ ] Readiness gate: every task has a clear output and local verification.
- [ ] Readiness gate: authorization receipt schema, update receipt, and rollback pointer fields are complete.
- [ ] Readiness gate: port registry, `codex-port`, `pending_bind`, `registry_revision`, `39000-39299`, and `40000-40999` are preserved.
- [ ] Readiness gate: sensitive authorization matrix covers MCP, CDP Bridge, OpenCLI, browser, and WeCom/WXWork.
- [ ] Readiness gate: safety does not rely on prompt-only rules; it has a checker or fixture.

## 18. Fine-grained implementation checklist

### Task 0: Freeze OpenSpec change and implementation boundary

- [ ] Create or update OpenSpec proposal for the Codex user-level control surface scope.
- [ ] Create or update OpenSpec design for low-token-first, risk-gated, receipt-first behavior.
- [ ] Create or update delta spec with Token/risk priority, authorization receipt, update receipt, evidence redaction, and port registry/lease requirements.
- [ ] Create or update management record with Monitoring decision `continue`.
- [ ] Local verification: `openspec validate --all`.

### Task 1: `skills2cli` compact facade

- [ ] Define `index/search/show/audit/profile suggest` JSON output.
- [ ] Keep full skill body output opt-in.
- [ ] Warning audit output must be summarized and redacted.
- [ ] Profile suggest is preview-only and must not apply changes.
- [ ] Local verification: `skills2cli.test.py`.

### Task 2: `mcp2cli` discovery/call facade

- [ ] Define compact `list/search/show` output.
- [ ] Define risk-gated `call` behavior and fail closed defaults.
- [ ] Sensitive calls without authorization receipt must fail.
- [ ] Receipt output must not contain secrets, cookies, or tokens.
- [ ] Local verification: `mcp2cli.test.py`.

### Task 3: `codex-port` lease governance

- [ ] Keep atomic port registry writes.
- [ ] Keep `pending_bind` recoverable.
- [ ] Increment `registry_revision` on writes.
- [ ] Keep Codex port ranges before downstream consumer ranges.
- [ ] Local verification: `codex_port.test.py`.

### Task 4: Browser owner registry

- [ ] isolated-session-managed can be automatically cleaned up.
- [ ] project-profile needs project authorization and cannot be stale-cleaned accidentally.
- [ ] human-owned Chrome assets are not automated by default.
- [ ] One target can have only one owner.
- [ ] Local verification: `browser_owner_registry.test.py`.

### Task 5: CDP Bridge / chrome-devtools-mcp / OpenCLI

- [ ] Read-only tab inventory does not need sensitive authorization.
- [ ] click/type/navigate/JS/cookie read requires authorization.
- [ ] OpenCLI must use `--port auto`.
- [ ] Live start requires install receipt and owner evidence.
- [ ] Local verification: `chrome_devtools_mcp_managed.test.py` and `cdp_bridge_governance.test.py`.

### Task 6: CLI-Anything and `wecom-cli`

- [ ] CLI-Anything defaults to harness plan generation only.
- [ ] Hard-loading skills is blocked until receipt and smoke pass.
- [ ] `wecom-cli` uses API/Webhook before GUI automation.
- [ ] WXWork.exe GUI actions require global lease, operator confirmation, and timeout release.
- [ ] Local verification: fixture tests or a guarded dry-run test.

### Task 7: Receipts, rollback, and redaction

- [ ] authorization receipt schema includes action, target, scope, expiry, session, and operator confirmation.
- [ ] update receipt includes tool name, installed version, source URL, install path, wrapper path, state path, smoke test command, updater command, rollback pointer, and owner lane.
- [ ] Redaction covers secrets, cookies, tokens, raw browser data, and plugin description dumps.
- [ ] rollback pointer resolves to a prior version or backup directory.
- [ ] Local verification: baseline checker and redaction tests.

### Task 8: Local integration

- [ ] Feature worktree is clean.
- [ ] Pre-commit update/archive gate passes.
- [ ] `tools/ci/local_gate.ps1` passes.
- [ ] `tools/ci/local_mr_review.ps1` passes.
- [ ] Create local main rollback ref.
- [ ] Merge into local `main` with ff-only.
- [ ] Keep remote publication behind explicit approval gate.

## 19. Local integration order

1. Update docs, OpenSpec, and Superpowers evidence inside the feature worktree.
2. Run local marker checks and manual structure review.
3. Run `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json`.
4. Run `python tools/run_openspec_guard.py --root . --json`.
5. Run `tools/ci/local_gate.ps1 -Json`.
6. Commit with a Chinese commit subject.
7. Run `tools/ci/local_mr_review.ps1 -Json`.
8. Create `refs/backup/local-main/*` rollback ref.
9. Merge into local `main` with `git merge --ff-only <feature-branch>`.
10. Stop at the remote publication approval gate.

## 20. Readiness gates and acceptance criteria

- [ ] The target file includes `For agentic workers`, `Goal`, `Architecture`, and `Tech Stack`.
- [ ] The target file includes `File responsibility map`, `Definition of ready before implementation`, `Fine-grained implementation checklist`, completion review checklist, acceptance criteria, and required evidence.
- [ ] The English companion uses the same structure and remains an ASCII primary.
- [ ] Lane states do not label planned or partial lanes as active.
- [ ] Sensitive authorization matrix covers all high-risk surfaces.
- [ ] The checklist has at least 30 items and the tables have at least 40 rows.
- [ ] OpenSpec delta spec contains the baseline markers.
- [ ] Local gate and local MR review pass.

## 21. Verification plan

| Check | Command | Pass criteria |
| --- | --- | --- |
| Baseline | `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json` | `ok=true`. |
| OpenSpec | `python tools/run_openspec_guard.py --root . --json` | all guard steps pass. |
| Local gate | `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1 -Json` | all shared CI steps pass. |
| Local MR review | `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1 -Json` | clean feature branch and merge-tree ok. |
| Manual structure review | heading scan | required modern-structure headings exist. |

## 22. Required evidence

- [ ] OpenSpec proposal/design/tasks/spec/management record.
- [ ] Superpowers design doc, implementation plan, and verification report.
- [ ] Baseline checker output.
- [ ] Local gate JSON output or terminal summary.
- [ ] Local MR review JSON output or terminal summary.
- [ ] Local main rollback ref.
- [ ] Worktree receipt and branch-matching claim.

## 23. Rollback and cleanup

- [ ] Documentation rework can roll back through the local main rollback ref.
- [ ] User-level install changes must roll back through the update receipt rollback pointer.
- [ ] GitLab/GitHub must not be pushed without explicit remote publication approval.
- [ ] A merged but unpublished feature branch may be retained as the publication carrier.
- [ ] Cleanup requires main contains branch head, rollback ref exists, and receipt is complete.

## 24. Risks and default decisions

| Risk | Default decision | Mitigation |
| --- | --- | --- |
| Token budget still overflows | Do not hard-load skills | Use `skills2cli` compact discovery. |
| MCP calls leak sensitive data | fail closed | authorization receipt plus redaction. |
| Browser asset is mutated accidentally | human-owned disabled | owner registry plus operator confirmation. |
| Port conflicts with downstream projects | Codex range first | `codex-port --port auto`. |
| WeCom GUI automation is risky | disabled | API/Webhook first; GUI requires WXWork lease. |
| User-level install cannot roll back | blocked | update receipt plus rollback pointer. |
| Plan regresses into prose-only notes | block merge | manual structure check plus baseline checker. |

## 25. Sources

- `docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.md` - local Codex governance fork reference for user-level Pi sidecar boundaries, receipts, updates, and rollback rules.
- `docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.md` - structural reference for the Comet-style management record, monitoring loop, phase gates, and evidence layout.
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md` - authority reference for deciding whether an MCP entry belongs in Codex direct config, MCP Router, or neither.
- `docs_bilingual/governance/codex_user_level_skills_governance_policy.md` - authority reference for skills visibility, profile loading, token-budget controls, and usage-audit boundaries.
- `reference_files/1.md` - local reference capture for the upstream links and operator notes that motivated this governance fork.
