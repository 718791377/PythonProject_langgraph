---
doc_id: user_level_mcp_skills_browser_cli_governance_plan
lang: en
canonical: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
translation: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
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

# User-Level MCP, Skills, Browser, and CLI Harness Governance Plan

## 0. Current review verdict

This plan now follows the newer implementation-plan structure used by `pi_plugin_codex_user_level_sidecar_plan.md` and `comet_runtime_agile_focus_area_plan.md`: relationship boundaries first, then goals/non-goals, runtime architecture, Codex usage, repo-local source of truth, install artifacts, receipts, state contract, Comet management record, phase gates, implementation slices, task backlog, local integration, acceptance, evidence, rollback, and risks.

`status: draft` means the complete user-level runtime is not fully installed and smoke-tested. It does not mean the document lacks execution structure. Repo-local `skills2cli`, `mcp2cli`, `codex-port`, browser owner registry, `chrome-devtools-mcp` wrapper MVPs, and CDP Bridge read-only-default guards remain `implemented-local`, not fully user-level `active`.

## 1. Relationship model and naming boundary

This plan governs Codex user-level, multi-project, multi-session reusable control surfaces. It is not PyCharm IDE integration and not a single project private script.

| Name | Owner | Default state | Boundary |
| --- | --- | --- | --- |
| skills2cli | skill index/search/show/audit/profile suggest | implemented-local | full skill bodies stay out of context |
| mcp2cli | MCP list/search/show/call facade | implemented-local | sensitive calls fail closed |
| codex-port | port registry / lease allocator | implemented-local | Codex ranges precede downstream consumer ranges |
| chrome-devtools-mcp | managed browser automation wrapper | implemented-local | three browser asset classes stay separated |
| CDP Bridge | browser bridge | implemented-local | read-only first |
| OpenCLI | on-demand browser/MCP adapter | planned/partial | requires --port auto and owner gate |
| CLI-Anything | harness generation/reference | planned | no hard-loaded bulk skills |
| wecom-cli | WeCom/WXWork API/Webhook/GUI | planned | GUI write disabled by default |
| oh-my-pi | Pi family / harness reference | reference-only | real sidecar belongs to pi_plugin plan |
| ohmyopenagent / snow-cli | future durable-team references | reference-only | not implemented here |

## 2. Goals and non-goals

Goals:

1. Prefer the lowest-token and lowest-risk surface for discovery, indexing, status checks, and read-only diagnostics.
2. Use `skills2cli` to reduce skills context budget pressure without exposing full skill bodies or plugin description dumps.
3. Use `mcp2cli` to split MCP discovery, profiles, and calls by risk; sensitive MCP calls fail closed by default.
4. Use browser owner registry to separate `isolated-session-managed`, `project-profile`, and human-owned Chrome assets.
5. Use `codex-port` for port registry / lease / `pending_bind` / `registry_revision` so Codex, downstream consumer projects, and OpenCLI do not conflict.
6. Use the authorization receipt schema, update receipt, rollback pointer, and evidence redaction so user-level tools are auditable, rollbackable, and resumable.

Non-goals: hard-loading every MCP or skill; disabling useful browser/OpenCLI/WeCom capability merely to hide token pressure; mutating `C:\Users\lenovo\.codex` without receipts; reading cookies, tokens, raw browser data, WeCom message contents, or human-owned Chrome assets without current authorization.

## 3. Runtime architecture

```text
Codex session -> repo-local policy/checkers/OpenSpec -> user-level helper facade
  -> skills2cli -> mcp2cli -> codex-port -> browser lane -> CLI-Anything -> wecom-cli
```

Default user-level paths include `C:\Users\lenovo\.codex\tools\skills2cli\`, `C:\Users\lenovo\.codex\tools\mcp2cli\`, `C:\Users\lenovo\.codex\tools\codex-port\`, `C:\Users\lenovo\.codex\tools\browser-automation\`, `C:\Users\lenovo\.codex\tools\wecom-cli\`, and matching state directories under `C:\Users\lenovo\.codex\state\`.

## 4. Codex usage model

1. Use repo-local policy, checkers, and docs to decide whether MCP, skills, browser automation, or CLI harness capability is needed.
2. For discovery, use compact JSON from `skills2cli index/search/show` or `mcp2cli list/search/show`.
3. For real MCP calls or browser writes, create an authorization receipt first.
4. For ports, use `codex-port lease reserve --owner codex --purpose <tool> --port auto`.
5. For OpenCLI, require `--port auto`, owner registry, and receipt.
6. For WeCom, prefer API/Webhook; GUI automation requires explicit user authorization and a global WXWork lease.

## 5. Repo-local source of truth

| Category | Repo-local source | User-level artifact |
| --- | --- | --- |
| policy | `docs_bilingual/governance/*`, `openspec/specs/*` | generated launcher/helper config |
| plan | `docs_bilingual/implementation_plans/*` | none |
| checker | `tools/check_*.py`, `tools/ci/local_gate.ps1` | optional installed wrapper |
| helper source | repo-local tools/templates | `C:\Users\lenovo\.codex\tools\...` |
| receipt schema | docs + tests | redacted runtime JSON receipt |

## 6. Installation and update evidence contract

Every user-level install action must create an update receipt. Without receipt evidence a lane can be only `planned` or `implemented-local`, not `active`.

| Field | Required | Notes |
| --- | --- | --- |
| tool name | yes | lane id |
| installed version | yes | commit, tag, or package version |
| source URL | yes | no token |
| install path | yes | runtime install target |
| wrapper path | yes | user-level wrapper |
| state path | yes | runtime state root |
| smoke test command | yes | repeatable |
| smoke test result | yes | pass/fail + timestamp |
| updater command | yes | pin-aware |
| rollback pointer | yes | previous version or backup path |
| owner lane | yes | `skills2cli`, `mcp2cli`, `browser`, `wecom-cli`, etc. |

Runtime receipts must not contain secrets, cookies, tokens, raw browser data, WeCom message contents, or complete plugin description dumps.

## 7. Token and risk priority model

| Priority | Surface | Token | Risk | Default action |
| --- | --- | --- | --- | --- |
| P0 | repo docs/checkers | low | low | read directly |
| P1 | `skills2cli index/search` | low | low | compact summary |
| P1 | `mcp2cli list/search/show` | low | low | compact summary |
| P2 | browser tab inventory | medium | medium | read-only with owner evidence |
| P2 | OpenCLI discovery | medium | medium | on-demand with port lease |
| P3 | MCP call / browser JS / cookies | high | high | authorization receipt required |
| P3 | `wecom-cli gui attach` | high | high | disabled by default |

## 8. User-level port governance

The port registry is managed by `codex-port` and must support `registry_revision`, atomic writes, `pending_bind`, lease renewal, and crash recovery.

| Owner | Range | Notes |
| --- | --- | --- |
| Codex general helpers | `39000-39299` | default Codex user-level helper range |
| Codex browser/OpenCLI | `39300-39499` | OpenCLI must use `--port auto` |
| Reserved local bridge | `39500-39999` | future use |
| Downstream consumer project range | `40000-40999` | consumer ports come after Codex |

| Command | Purpose | Receipt |
| --- | --- | --- |
| `codex-port registry show --json` | read registry | no write |
| `codex-port lease reserve --owner <name> --port auto --json` | auto allocate | lease receipt |
| `codex-port lease renew --lease-id <id> --json` | renew | updated lease |
| `codex-port lease release --lease-id <id> --json` | release | completed receipt |
| `codex-port import-legacy --owner openclaw --json` | import old ports | migration receipt |
| `codex-port gc --dry-run --json` | stale scan | no write |
| `codex-port gc --apply --json` | stale cleanup | evidence-gated write |

## 9. `skills2cli` lane contract

| Command | Default output | Risk gate |
| --- | --- | --- |
| `skills2cli index --json` | id, source layer, summary hash, availability | no full body |
| `skills2cli search <query> --json` | compact matches | no full body |
| `skills2cli show <id> --json` | bounded summary + path hint | `--full` required for expansion |
| `skills2cli profile suggest --task <text> --json` | recommendation only | never direct apply |
| `skills2cli audit warnings --since <duration> --json` | 2% budget and skipped-loading summary | redacted paths |

## 10. `mcp2cli` lane contract

| Operation | Default | Required evidence |
| --- | --- | --- |
| list/search/show | compact JSON | profile registry |
| low-risk read-only call | allowed | allowlist |
| medium-risk call | gated | task scope + owner |
| sensitive call | fail closed | authorization receipt schema |
| write/mutate call | fail closed | current user approval + receipt |

## 11. Browser automation and Chrome/DevTools/CDP/OpenCLI lane

| Asset class | Profile | Bookmarks/extensions | Default permission | Cleanup |
| --- | --- | --- | --- | --- |
| `isolated-session-managed` | per-session temp profile | none | safest automation | automatic cleanup allowed |
| `project-profile` | per-project managed profile | optional imported baseline | project automation | stale scan + dry-run |
| human-owned asset | user's own Chrome | real bookmarks/extensions/cookies | human-owned | never automatic cleanup |

`chrome-devtools-mcp`, CDP Bridge, and OpenCLI are inspect/read-only first. Navigate, click, type, JavaScript, cookies, downloads, uploads, account data, CRM, email, calendar, Drive, Slack, HubSpot, or WeCom data require a current one-task authorization receipt.

## 12. CLI-Anything and `wecom-cli` lane

| Phase | Scope | Default |
| --- | --- | --- |
| API/Webhook MVP | webhook send, app-message send, secret redaction | planned |
| Inventory | `WXWork.exe` process list, window list | read-only |
| GUI attach | attach, click, type, read UI state | disabled |
| GUI write | send message / mutate state | one-task authorization + global WXWork lease |

## 13. Reference-only items and external-source boundary

| Reference | Use | Not allowed |
| --- | --- | --- |
| The Harness Problem | hash-anchored edit reliability | no unaudited import |
| `oh-my-pi` | Pi family / UX / sidecar reference-only | no install here |
| `ohmyopenagent` | future durable-team reference | no implementation here |
| `snow-cli` | CLI product-shape reference | no implementation here |

## 14. Sensitive authorization matrix

The authorization receipt schema requires action, target, scope, expiry, session, and operator confirmation.

| Action | Risk | Default | Required receipt |
| --- | --- | --- | --- |
| compact list/search/show | low | allowed | none |
| read-only browser inventory | medium | allowed with owner evidence | owner lease |
| MCP sensitive call | high | fail closed | authorization receipt |
| CDP Bridge click/type/JS/cookies | high | fail closed | one-task authorization receipt |
| OpenCLI write/navigation | high | fail closed | authorization receipt + port lease |
| `wecom-cli` GUI write | high | disabled | authorization receipt + global WXWork lease |

## 15. Runtime state contract

| State | Meaning | Entry condition |
| --- | --- | --- |
| planned | plan only | docs or OpenSpec exists |
| implemented-local | repo-local helper/checker exists | tests pass |
| installed-user-level | user-level artifact exists | update receipt exists |
| smoke-tested | user-level smoke passed | smoke test result is pass |
| on-demand | can be enabled when needed | receipt and rollback pointer exist |
| active | default usable or currently enabled | all readiness gates pass |
| disabled | disabled | explicit reason exists |
| reference-only | reference source only | no runtime path |
| rollback-ready | quick rollback possible | rollback pointer verified |

State invariants: no wrapper path + smoke test result + rollback pointer means not `active`; no authorization receipt means sensitive actions fail closed; no port lease means OpenCLI/browser listener cannot start.

## 16. Comet Management Record template

```markdown
# Comet Management Record
## Open / Initiating
- [ ] Value / why is stated.
- [ ] Success criteria are stated.
- [ ] Stakeholders and constraints are identified.
## Design / Planning
- [ ] Delivery tailoring is recorded.
- [ ] Risks and assumptions are recorded.
- [ ] Acceptance evidence path is defined.
## Build / Executing
- [ ] Execution mode is selected.
- [ ] Quality evidence is recorded.
- [ ] Current blockers are cleared or have a handling decision.
## Verify / Controlling
- [ ] Variance review is complete.
- [ ] Risk/change impact is assessed.
- [ ] Control decision is recorded.
## Archive / Closing
- [ ] Value outcome is summarized.
- [ ] Lessons learned are recorded.
- [ ] Archive/sync/deferral decision is confirmed.
## Monitoring Loop
- [ ] Current phase facts are checked.
- [ ] Return/no-return decision is made.
```

## 17. Phase gate matrix

| Comet phase | PM focus | Gate | Evidence | Return |
| --- | --- | --- | --- | --- |
| Open | initiating | scope / non-goals / stakeholders / rollback | proposal.md | return-open |
| Design | planning | architecture, lane boundaries, authorization model | design doc + delta spec | return-design |
| Build | executing | patch, tests, receipt schema, state updates | implementation plan + changed paths | return-build |
| Verify | monitoring/controlling | precommit, guard, local gate, local MR review | verification report | return-build / return-design |
| Archive | closing | stable spec sync or archive deferral | archive receipt / deferral | return-verify |

## 18. Monitoring return semantics

| Trigger | Decision | target_phase | rework_reason |
| --- | --- | --- | --- |
| scope or non-goals unclear | return-open | open | value-gap |
| lane boundary or authorization model incomplete | return-design | design | planning-gap |
| checker/test not registered | return-build | build | execution-gap |
| local gate / MR review fails | return-build | build | verification-gap |
| complete change has no archive or deferral | return-verify | verify | archive-gap |

## 19. Implementation slices

### OpenSpec slice delivery matrix

| Slice | Main artifacts | Minimum validation | Completion evidence |
| --- | --- | --- | --- |
| 1. Policy/checker baseline | token/risk checker; port registry; authorization receipt schema; update receipt schema; evidence redaction | checker tests + local gate | OpenSpec spec + checker output |
| 2. skills2cli MVP | index/search/show/audit/profile suggest | compact-output and privacy-redaction tests | wrapper smoke + receipt |
| 3. mcp2cli MVP | profile registry; list/search/show/call facade | sensitive-call fail-closed tests | blocked call evidence |
| 4. codex-port allocator | reserve/renew/release/import-legacy/gc | pending_bind and concurrent reserve tests | registry_revision + lease receipt |
| 5. Browser owner registry | isolated/project/human asset separation | owner exclusivity + cleanup dry-run tests | browser lease receipt |
| 6. chrome-devtools-mcp wrapper | managed wrapper for isolated-session-managed and project-profile | wrapper smoke | install/update receipt |
| 7. CDP Bridge/OpenCLI enforcement | read/write split and on-demand adapter | cookie/JS/click/type/navigate fail-closed | authorization receipt evidence |
| 8. Codex harness reference boundary | oh-my-pi and The Harness Problem reference-only | docs boundary check | no runtime install evidence |
| 9. CLI-Anything boundary | install/update receipts and harness boundary | no-hard-load and rollback tests | install receipt |
| 10. wecom-cli API/Webhook | webhook send; app-message send; secret redaction | dry-run and secret-redaction tests | redacted send summary |
| 11. wecom-cli inventory | process/window read-only inventory | no-content-capture tests | read-only inventory summary |
| 12. wecom-cli GUI gate | global WXWork lease + one-task authorization | unauthorized fail + lease exclusivity | manual smoke marker |

### Slice completion rule

A slice is complete only when implementation, tests, CI registration, OpenSpec update, rollback evidence, and completed receipt exist. Documentation-only or research-only slices can be `planned` or `implemented-local`, but not `active`.

## 20. Definition of ready before implementation

- [ ] The corresponding OpenSpec change exists and states scope / non-goals.
- [ ] The lane has an owner, owned files, receipt schema, and rollback method.
- [ ] If a port is involved, a `codex-port` port registry lease exists.
- [ ] If a browser is involved, asset class and owner registry are confirmed.
- [ ] If sensitive data is involved, a current one-task authorization receipt exists.
- [ ] If user-level installation is involved, update receipt and rollback pointer are defined.
- [ ] New tests are registered in `tools/ci/ci_test_manifest.json` or the local gate.

## 21. Fine-grained implementation checklist

- [x] Create or reuse a small OpenSpec change for this plan and state scope, non-goals, and rollback boundary.
- [x] Add token/risk priority controls so high-token or high-risk surfaces cannot become default without evidence.
- [x] Establish the user-level port registry / lease allocator so Codex ranges come before downstream consumer ranges.
- [x] Implement the minimum codex-port reserve/renew/release/list/import-legacy/gc contract.
- [x] Cover pending_bind, live-socket collision, stale/crash evidence, and registry_revision.
- [x] Add the authorization receipt schema with action, target, scope, expiry, session, and operator confirmation.
- [x] Add update receipt fields: tool name, installed version, source URL, install path, wrapper path, state path, smoke test command, rollback pointer, owner lane.
- [x] Add sanitized-evidence rules forbidding secrets, cookies, tokens, raw browser data, message contents, and plugin description dumps.
- [x] Implement compact skills2cli index --json output.
- [x] Implement compact skills2cli search <query> --json output.
- [x] Implement skills2cli show <skill-id> --json without full skill bodies by default.
- [x] Implement skills2cli profile suggest --task <text> --json as recommendation-only.
- [x] Implement skills2cli audit warnings --since <duration> --json for 2% skills context budget and skipped-loading warnings.
- [x] Add skills2cli compact-output, privacy-redaction, profile-non-apply, and warning-audit tests.
- [x] Implement the mcp2cli allowed profile registry.
- [x] Implement compact mcp2cli list/search/show.
- [x] Implement mcp2cli call sensitive-category fail-closed gate.
- [x] Add mcp2cli profile-registry, sensitive-call-blocking, compact-output, and receipt-required tests.
- [x] Implement the browser owner registry with owner class, project slug, session id, profile path, and lease expiry.
- [x] Implement the chrome-devtools-mcp isolated-session-managed wrapper.
- [x] Implement the chrome-devtools-mcp project-profile wrapper.
- [x] Implement browser stale scan and safe-cleanup dry-run.
- [x] Add browser-lane tests for tab-owner exclusivity, project-profile retention, human-owned protection, and cleanup dry-run.
- [x] Harden CDP Bridge read-only defaults so write actions require owner and authorization receipts.
- [ ] Keep OpenCLI as an on-demand adapter and connect it to browser owner registry and --port auto.
- [x] Add CDP Bridge fail-closed tests for cookie, JavaScript, click, type, and navigate.
- [ ] Add remaining OpenCLI fail-closed tests for cookie, JavaScript, click, type, and navigate.
- [x] Move direct oh-my-pi install, updater, smoke, and rollback work into pi_plugin_codex_user_level_sidecar_plan.*.
- [x] Keep only the reference-only harness governance boundary for oh-my-pi / The Harness Problem in this plan.
- [ ] Install CLI-Anything / CLI Hub with user-level install receipts and without hard-loading bulk skills.
- [ ] Use CLI-Anything to help design wecom-cli while keeping repo-local source and authorization gates.
- [ ] Implement read-only wecom-cli process list --json and window list --json inventory.
- [ ] Implement wecom-cli webhook send and app-message send with secret redaction and receipts.
- [ ] Implement wecom-cli gui attach with global WXWork lease and one-task authorization gate; keep it disabled by default.
- [ ] Add wecom-cli process/window read-only, secret-redaction, GUI-unauthorized-fail, and lease-exclusivity tests.
- [ ] Register every new test or checker in tools/ci/ci_test_manifest.json or the shared local-gate call chain.
- [x] Run the precommit update/archive gate, local gate, and local MR review for every completed OpenSpec change.
- [ ] Record rollback-ready receipts after every user-level installation; lanes without receipts must not be marked active.

## 22. Local integration sequence

1. Create an OpenSpec change in an isolated feature worktree.
2. Write the Design Doc, Implementation Plan, delta spec, and management record.
3. Modify the bilingual plan pair and keep English ASCII primary plus zh-CN companion synchronized.
4. Run document pair policy, baseline checker, implementation plan checker, precommit update/archive gate, OpenSpec guard, and local gate.
5. Commit the feature branch with a Chinese commit subject, then run local MR review.
6. Create rollback backup refs and fast-forward merge into local main.
7. Remote publication waits for explicit user wording naming remote push, GitLab/MR, merge, or GitHub sync.

## 23. Readiness gates and acceptance criteria

| Gate | Criteria | Evidence |
| --- | --- | --- |
| Documentation readiness | bilingual docs synced, structure clear, markers complete | document pair policy |
| OpenSpec readiness | proposal/design/tasks/spec complete | `openspec validate --strict` |
| Runtime readiness | wrapper + state path + smoke + rollback | update receipt |
| Authorization readiness | action/target/scope/expiry/session/operator confirmation | authorization receipt schema |
| Port readiness | lease + owner + registry_revision | port registry receipt |
| Browser readiness | owner registry + asset class + cleanup policy | browser lease receipt |
| Active readiness | installed-user-level + smoke-tested + rollback-ready | completed receipt |

## 24. Verification plan

- `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json` - verifies governance baseline markers.
- `python tools/check_implementation_plan_rules.py --root . --json` - verifies implementation-plan rules.
- `python tools/check_document_pair_policy.py --root . --json` - verifies bilingual companion coverage.
- `python tools/check_precommit_update_archive.py --root . --json` - reviews update/archive readiness.
- `python tools/run_openspec_guard.py --root . --json` - runs repository OpenSpec guards.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\\tools\\ci\\local_gate.ps1` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\\tools\\ci\\local_mr_review.ps1` - runs local MR review after commit.
- `openspec validate <change> --strict` - validates the change schema and artifacts.
- `openspec status --change <change> --json` - reports artifact completion.

## 25. Rollback and cleanup

Rollback the documentation refactor by reverting the feature commit or resetting to the backup ref. User-level install rollback uses the update receipt rollback pointer. Port lease cleanup starts with `codex-port gc --dry-run --json`. Browser cleanup affects only managed profiles, never human-owned Chrome.

## 26. Risks and default decisions

| Risk | Default decision | Mitigation |
| --- | --- | --- |
| skills context 2% budget exceeds again | do not disable blindly | usage audit, then `skills2cli` / profile helper |
| MCP surface leaks sensitive data | fail closed | authorization receipt schema |
| port conflict | do not kill processes | port registry + pending_bind + live-socket evidence |
| browser asset confusion | protect human-owned assets | asset class + owner registry |
| OpenCLI high-risk write action | on-demand only | receipt + port lease + owner gate |
| WeCom GUI misoperation | disabled by default | global WXWork lease + one-task authorization |
| user-level cache overwritten by updates | receipt + source of truth | repo-local source + updater rollback |

## 27. Self-checklist

- [ ] This plan still has `plan_readiness: execution-ready`.
- [ ] This plan still declares `implementation_state:` and does not mark unfinished lanes as active.
- [ ] The text includes Token, Readiness gate, OpenSpec, skills2cli, mcp2cli, CDP Bridge, and OpenCLI.
- [ ] The text includes port registry, codex-port, pending_bind, registry_revision, 39000-39299, and 40000-40999.
- [ ] The text includes authorization receipt schema, operator confirmation, update receipt, and rollback pointer.
- [ ] The text includes `chrome-devtools-mcp`, `oh-my-pi`, CLI-Anything, `wecom-cli`, active, on-demand, reference-only, and disabled.

## 28. Sources

- https://github.com/knowsuchagency/mcp2cli
- https://github.com/jackwener/OpenCLI
- https://github.com/ChromeDevTools/chrome-devtools-mcp
- https://github.com/HKUDS/CLI-Anything
- https://clianything.cc/
- https://blog.can.ac/2026/02/12/the-harness-problem/
- https://github.com/can1357/oh-my-pi
- https://github.com/ymymssss/ohmyopenagent
- https://github.com/MayDay-wpf/snow-cli
