---
doc_id: user_level_mcp_skills_browser_cli_governance_plan
lang: en
canonical: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
status: draft
plan_readiness: execution-ready
implementation_state: mcp2cli_mvp_repo_local_implemented
last_reviewed_at: 2026-05-24
doc_class: implementation_plan
created_at: 2026-05-22
source_reference_file: reference_files/1.md
---

# User-Level MCP, Skills, Browser, and CLI Harness Governance Plan

## 0. Current review verdict

As of 2026-05-24, this plan is sufficiently granular as a pre-execution blueprint and is ready for OpenSpec slicing. `status: draft` means the user-level runtime has not been fully implemented from this plan; it does not mean the document lacks an execution structure. The first policy/checker baseline slice has completed local implementation, validation, stable spec promotion, and OpenSpec archive closeout. The second `skills2cli` MVP and third `mcp2cli` MVP now have repo-local helpers and test coverage; they remain `implemented-local` rather than fully user-level `active` until later governed wrapper/install receipt slices land.

Review verdict:

- Coverage is complete: MCP facade, on-demand skills discovery, browser ownership, Chrome DevTools MCP, CDP Bridge, OpenCLI, `oh-my-pi`, CLI-Anything, and `wecom-cli` all have default states, authorization boundaries, install evidence, and rollback requirements.
- User-level port governance is explicit: Codex uses earlier user-level ranges, OpenClaw uses later ranges, OpenCLI must use allocator-driven `--port auto`, and the allocator has reserve/release/import/gc command contracts.
- Concurrent allocation safety is explicit: registry updates are atomic, binds use provisional leases, long-running owners renew leases, and crash recovery requires evidence.
- The granularity is implementation-ready: every lane can become an OpenSpec change, and every change must state owned files, checker/test evidence, receipt schema, rollback method, and non-goals.
- Unchecked checklist items are downstream implementation state, not plan gaps. A lane must not be marked `active` until its code, checker, install artifact, and receipt evidence all exist.
- The sequence is baseline before capability: finish token/risk, authorization receipt, update receipt, and evidence-redaction controls before implementing `skills2cli`, `mcp2cli`, browser automation, and `wecom-cli` capability surfaces.

The next action is not to broaden this plan. After the repo-local `mcp2cli` MVP is validated and archived, continue with later governed browser owner registry and `chrome-devtools-mcp` managed wrapper slices rather than installing user-level wrappers implicitly.

## 1. Purpose

This plan upgrades MCP, skills, browser automation, and CLI harness capability from ad-hoc per-project usage into user-level, multi-project, multi-session infrastructure.

The target is not to add more always-visible tools. The target is to reduce token pressure and safety risk by routing work through the smallest sufficient surface:

1. low token and low risk surfaces first;
2. high token or high risk surfaces only when the task requires them;
3. operations involving user-sensitive data require explicit user authorization;
4. all long-lived user-level helpers are pinned, auditable, updateable, and rollbackable.

The plan implements both MCP governance and skills governance. It adds `mcp2cli` for MCP tool surfaces and `skills2cli` for Codex skill surfaces.

## 2. Reference sources and implementation disposition

Implement now:

- `mcp2cli`: user-level MCP CLI facade and low-token MCP discovery/call surface.
- `skills2cli`: new local clean-room helper for skill index/search/show/profile suggestion and warning audit.
- `chrome-devtools-mcp`: promote from project-local/default usage into user-level managed browser automation.
- `CDP Bridge`: keep as user-level browser bridge with inspect-first defaults and explicit authorization for sensitive operations.
- `OpenCLI`: install as on-demand user-level adapter candidate, not as an always-on default.
- `CLI-Anything` and CLI-Anything Hub: install as user-level harness-generation/reference tooling, then use it to help design `wecom-cli`.
- `The Harness Problem`: use as the editing/harness reliability reference for future hash-anchored edit experiments.
- `oh-my-pi`: install/adapt as user-level sidecar reference runtime, not as a replacement for Codex.

Reference only for later Codex CLI personal production durable team design:

- `ohmyopenagent`: reference source for OpenAgent-style multi-agent prompts and runtime ideas.
- `snow-cli`: reference source for CLI product shape and operator interaction design.

## 3. User-level runtime layout

Use this layout unless a later implementation change explicitly replaces it:

```text
C:\Users\lenovo\.codex\external\mcp2cli\
C:\Users\lenovo\.codex\external\oh-my-pi\
C:\Users\lenovo\.codex\external\cli-anything\
C:\Users\lenovo\.codex\external\opencli\
C:\Users\lenovo\.codex\tools\mcp2cli\
C:\Users\lenovo\.codex\tools\skills2cli\
C:\Users\lenovo\.codex\tools\codex-port\
C:\Users\lenovo\.codex\tools\browser-automation\
C:\Users\lenovo\.codex\tools\wecom-cli\
C:\Users\lenovo\.codex\state\mcp2cli\
C:\Users\lenovo\.codex\state\skills2cli\
C:\Users\lenovo\.codex\state\ports\
C:\Users\lenovo\.codex\state\browser-automation\
C:\Users\lenovo\.codex\state\wecom-cli\
C:\Users\lenovo\.codex\state\tool-updates\
```

Repository source of truth remains in this repository. User-level files are install artifacts. Any installer must generate or sync user-level copies from repo-local source and must keep receipts.

## 4. Token and risk priority model

Use this priority order when multiple surfaces can solve the same task:

| Priority | Surface | Token cost | Safety risk | Default behavior |
|---|---|---:|---:|---|
| 1 | `skills2cli search/show`, `mcp2cli list/search` | Low | Low | Allowed by default |
| 2 | direct repo scripts/checkers | Low | Low | Allowed by default |
| 3 | `mcp2cli call` for non-sensitive MCP tools | Medium | Medium | Allowed after tool/category check |
| 4 | `chrome-devtools-mcp` isolated/session profile | Medium | Medium | Allowed for local/debug tasks |
| 5 | CDP Bridge read-only scan/screenshot/tab inventory | Medium | Medium | Inspect-first only |
| 6 | OpenCLI bound browser session | High | High | Explicit browser-lane authorization |
| 7 | project-profile with login state | High | High | Explicit project-profile authorization |
| 8 | human-owned Chrome or WXWork GUI write actions | High | Critical | Explicit one-task authorization required |

Sensitive operations include reading cookies, tokens, passwords, private chats, personal tabs, personal Chrome profile data, WeCom messages, or performing clicks/typing/sends in a logged-in app.

## 4.1 User-level port governance

Port ownership is governed by range, registry, and lease instead of hard-coded per-tool defaults.

Default ranges:

| Range | Owner | Purpose |
| --- | --- | --- |
| `39000-39299` | Codex | MCP facade, `skills2cli`, and low-risk user-level helpers. |
| `39300-39499` | Codex | OpenCLI on-demand browser adapter. |
| `39500-39699` | Codex | Browser automation, including managed `chrome-devtools-mcp` wrappers. |
| `39700-39999` | Codex | Reserved user-level Codex expansion. |
| `40000-40999` | OpenClaw | OpenClaw project services and OpenClaw-managed local control plane. |

Rules:

- OpenClaw ports are intentionally after Codex ports; Codex must not allocate from `40000-40999`.
- OpenClaw must not allocate from `39000-39999` after migration; existing legacy OpenClaw ports are imported as `legacy_reserved` until migrated.
- All managed local services bind to `127.0.0.1` by default; `0.0.0.0` requires a separate explicit security review and one-task approval.
- Smoke tests and short-lived probes should use OS-assigned ephemeral ports (`port=0`) unless a stable lease is required.
- OpenCLI has no fixed port in this plan. It must request `--port auto` through the port allocator and receive a lease in the `39300-39499` range.
- `chrome-devtools-mcp` managed wrappers must request browser-automation ports from `39500-39699` unless the upstream tool uses stdio only.
- A wrapper must check both the registry and the live listening socket table before binding; on conflict it selects the next allowed port, never kills the process holding the port.
- Stale leases can be reclaimed only when the recorded PID is gone or a read-only health check proves the owner is no longer alive.

Registry path:

`C:\Users\lenovo\.codex\state\ports\registry.json`

Minimum registry fields:

- `owner`: `codex`, `openclaw`, or `external_reserved`;
- `project` or `project_slug`;
- `tool`;
- `host`;
- `port`;
- `lease_id`;
- `pid`;
- `created_at`;
- `renewed_at`;
- `ttl_seconds`;
- `lease_expiry`;
- `owner_session`;
- `purpose`;
- `status`: `pending_bind`, `active`, `stale`, `legacy_reserved`, or `released`.
- `registry_revision`: monotonic registry version used to detect stale concurrent writes.

### 4.1.1 Port allocator minimum CLI contract

The allocator must be a user-level wrapper generated or synced from repository source. Do not scatter temporary port probing logic across individual tool wrappers.

Minimum commands:

```text
codex-port lease reserve --owner codex --project <slug> --tool <tool> --range <range-name> --purpose <text> --ttl <seconds> --json
codex-port lease renew --lease-id <lease-id> --owner-session <session-id> --ttl <seconds> --json
codex-port lease release --owner-session <session-id> --port <port> --json
codex-port lease list --owner codex --json
codex-port lease import-legacy --owner openclaw --port <port> --purpose <text> --json
codex-port lease gc --dry-run --json
```

Port-governance decision table:

| Case | Required behavior |
| --- | --- |
| Registry says free, but live socket is already listening | Treat the port as occupied, skip to the next allowed port, and record a collision warning. |
| Registry says active, but PID is gone | Mark `stale`; reuse only after a read-only PID or health evidence record exists. |
| Registry contains an expired `pending_bind` lease | Reclaim only after its session cannot complete binding and the provisional-lease timeout evidence is recorded. |
| Registry says `legacy_reserved` | Never allocate automatically; require an explicit migration or release receipt. |
| Requested range does not match owner | Fail closed, for example Codex requesting `40000-40999` or OpenClaw requesting `39000-39999` after migration. |
| Release request lacks the matching owner session | Fail closed and keep the lease. |

Read/write boundary:

- `list` and `gc --dry-run` are read-only and allowed by default.
- `reserve`, `renew`, `release`, `import-legacy`, and non-dry-run `gc` are write operations and must write receipts under `C:\Users\lenovo\.codex\state\ports\receipts\`.
- The allocator must never terminate processes. Process cleanup belongs to the owning wrapper and requires separate evidence and authorization.

### 4.1.2 Concurrent-session allocation and crash recovery

Multi-project and multi-session use requires an atomic registry lifecycle, not only a port-range convention:

- Each registry mutation must take a short-lived exclusive lock at `C:\Users\lenovo\.codex\state\ports\registry.lock` or an equivalent lock surface, validate the current `registry_revision`, write a temporary file, and atomically replace `registry.json`.
- `reserve` first records a unique `lease_id` with `status=pending_bind` and a short timeout. The owning wrapper then binds the socket and promotes the lease to `active`; if binding loses a race, it marks that lease released/collided and reserves another allowed port.
- The registry lock must be released before launching a browser, opening a listening socket, performing network I/O, or running a health probe; it serializes state updates, not long-running tool work.
- Long-lived managed services must call `renew` before expiry. An expired `active` lease is not reusable until PID or read-only health evidence confirms that the previous owner is no longer live.
- A normal wrapper shutdown must call `release`. A crashed session leaves an evidence-gated stale or expired lease for `gc`; another session must never release or renew a lease it does not own.
- Corrupt registry content, failed atomic replacement, or lock ownership ambiguity must fail closed, retain a recovery copy, and block new allocation until repaired or explicitly recovered.

## 5. `mcp2cli` implementation lane

Goal: reduce Codex MCP tool-list pressure by converting selected MCP surfaces into low-token CLI discovery and calls.

Implementation:

- Install `mcp2cli` in an isolated user-level runtime, not global Python.
- Pin the installed version or git commit in `C:\Users\lenovo\.codex\state\tool-updates\mcp2cli.lock.json`.
- Provide a wrapper command under `C:\Users\lenovo\.codex\tools\mcp2cli\mcp2cli.cmd` or `.ps1`.
- Add a local registry of MCP endpoints allowed for CLI facading.
- Do not expose high-risk MCP servers by default.
- CLI output must default to compact summaries; full schemas require explicit `--full`.
- Calls that access secrets, browsers, shell, remote infrastructure, or personal data require authorization gates.

Minimum commands:

```text
mcp2cli list --profile <profile> --json
mcp2cli search <query> --profile <profile> --json
mcp2cli show <tool> --profile <profile> --json
mcp2cli call <tool> --profile <profile> --json --args <json>
```

## 6. `skills2cli` implementation lane

Goal: resolve the recurring `Exceeded skills context budget of 2%` warning by making most skills discoverable on demand instead of always visible.

Implementation:

- Build a clean-room helper from repo-local source; do not fork `mcp2cli`.
- Scan repo, user, system, and plugin `SKILL.md` files into a local index.
- Store raw index under user-level state; only sanitized summaries may be committed to this repository.
- Integrate with the existing skills usage audit plan and soft-load/profile helper rules.
- Keep one small always-visible skill/profile entry that can route to `skills2cli`.

Minimum commands:

```text
skills2cli index --json
skills2cli search <query> --json
skills2cli show <skill-id> --json
skills2cli profile suggest --task <text> --json
skills2cli audit warnings --since <duration> --json
```

`skills2cli` must not apply or disable skills by itself. It recommends profiles and produces evidence; profile application remains a separate governed action.

## 7. User-level browser automation lane

Promote browser automation to a user-level, multi-project, multi-session lane.

Browser assets are exactly these three classes:

1. `isolated-session-managed`: temporary Codex-managed browser profile; may be cleaned after ownership and staleness are proven.
2. `project-profile`: long-lived project-managed profile; may contain project bookmarks, extensions, and test login state; must not be auto-deleted.
3. `human-owned-personal-asset`: user's personal Chrome; must not be auto-taken-over, auto-cleaned, or treated as Codex-managed.

Adapters:

- `chrome-devtools-mcp`: user-level managed wrapper, preferred for local/debug browser work.
- `CDP Bridge`: user-level inspect-first bridge; write actions require owner and authorization checks.
- `OpenCLI`: optional on-demand adapter for website/browser-to-CLI use cases; not default and not always loaded.

Required owner states:

```text
owner=codex-managed-isolated
owner=codex-managed-project
owner=human-owned
owner=human-delegated
```

Rules:

- One tab can have only one automation owner at a time.
- One `project-profile` can be controlled by only one session at a time.
- `human-owned-personal-asset` can become `human-delegated` only for one tab, one task, and the current session.
- User-sensitive reads and all writes/clicks/typing in logged-in contexts require explicit user authorization.
- Cleanup must never target human-owned Chrome.

## 8. `chrome-devtools-mcp` promotion

Current state: `chrome-devtools-mcp` exists in user-level Codex config, but it is effectively a bare entry and not yet fully managed for multi-project/multi-session use.

Implementation:

- Replace bare startup with a user-level managed wrapper.
- Wrapper supports:
  - `--mode isolated-session`;
  - `--mode project-profile --project <slug>`;
  - lease writing;
  - stale scan;
  - max active instance limit;
  - safe cleanup that only targets known managed profiles.
- Keep the direct Codex MCP entry for `chrome-devtools`; do not route it through MCP Router.

## 9. CDP Bridge and OpenCLI user-level adaptation

CDP Bridge:

- Keep installed as a user-level direct Codex MCP server.
- Default lane is read-only inventory, DOM scan, screenshots, and tab listing.
- Cookie reads, JS writes, clicks, typing, navigation in personal tabs, or sensitive contexts require authorization.

OpenCLI:

- Install as a user-level external tool and wrapper, not as an always-on Codex tool list expansion.
- Use only through the browser owner registry.
- Never bind a human-owned Chrome tab without explicit one-task authorization.
- Prefer `isolated-session-managed` or `project-profile` over human-owned sessions.

## 10. `oh-my-pi` user-level installation and adaptation

Goal: use `oh-my-pi` as a sidecar reference/runtime for harness and editing ideas, not as a Codex replacement.

Implementation:

- Clone to `C:\Users\lenovo\.codex\external\oh-my-pi\` at a pinned commit or tag.
- Install dependencies locally in that directory or a user-level runtime; do not install globally unless the project explicitly requires it and a wrapper records it.
- Add wrapper under `C:\Users\lenovo\.codex\tools\oh-my-pi\`.
- Per-project state must stay outside the cloned source and must include project slug and session namespace.
- Adapt only these concepts initially:
  - hash-anchored edit research;
  - CLI/harness ergonomics;
  - sidecar statistics or UX references.
- Do not replace Codex `apply_patch` or native subagent workflow.

Update strategy:

- `fetch` upstream into a staging ref.
- Run smoke tests and wrapper help checks.
- Write update receipt.
- Switch wrapper pin only after tests pass.
- Keep rollback pointer to the previous commit.

## 11. CLI-Anything and WeCom / WXWork implementation lane

Goal: install CLI-Anything at user level as harness-generation/reference tooling and build a governed `wecom-cli` for enterprise WeChat.

Implementation-time local fact handling: `WXWork.exe` has been observed as the target enterprise WeChat process name, but process presence and install path are dynamic local facts. Each `wecom-cli` implementation step, smoke test, or GUI task must refresh them through read-only process/window inventory before relying on them.

Fact refresh rule:

- repository evidence may record process name, owner class, presence, and a redacted path summary;
- repository evidence must not record the full local install path, message contents, or raw window data;
- absence of a running `WXWork.exe` blocks only process/window inventory or GUI automation tests, not API/Webhook design work;
- GUI automation remains `disabled` unless a fresh process/window inventory, global WXWork lease, and one-task authorization receipt all exist.

Installation/adaptation:

- Install CLI-Anything / CLI Hub in user-level isolated runtime.
- Do not hard-load all CLI-Anything skills into Codex context.
- Use CLI-Anything to guide harness structure, not to bypass local authorization rules.
- Generate or maintain `wecom-cli` as a governed harness under user-level tools with repo-local source.

`wecom-cli` stages:

1. API/Webhook layer, low risk:
   - send webhook notifications;
   - send app messages through official API where credentials are available;
   - secrets stored only in user-level secret storage.
2. Process/window inventory layer, medium risk:
   - list `WXWork.exe` processes;
   - list windows and titles;
   - report foreground state.
3. GUI automation layer, high risk:
   - attach to a specific WXWork process/window;
   - click/type/send/read visible chat content;
   - requires explicit one-task user authorization and a global WXWork lease.

Minimum commands:

```text
wecom-cli process list --json
wecom-cli window list --json
wecom-cli webhook send --text <text> --json
wecom-cli app-message send --to <target> --text <text> --json
wecom-cli gui attach --pid <pid> --json --require-human-authorization
```

Multi-session rule: API/Webhook commands may run concurrently if secret access is permitted; GUI automation is globally serialized because there is one WXWork desktop session.

Update strategy:

- CLI-Anything updates do not automatically rewrite `wecom-cli`.
- `wecom-cli` updates require tests, authorization policy checks, and rollback receipts.
- GUI automation changes require a manual smoke test marker before becoming active.

## 12. Reference-only items

`ohmyopenagent` and `snow-cli` remain reference-only.

Allowed use:

- review architecture ideas;
- compare CLI UX;
- inform future Codex CLI personal production durable team design.

Disallowed for this plan:

- no dependency install;
- no code copy;
- no default skill/profile inclusion;
- no runtime integration.

## 13. Readiness gates and acceptance criteria

Status flow:

`planned -> implemented-local -> installed-user-level -> smoke-tested -> active -> rollback-ready`

The status names are operational states, not marketing labels:

- `planned`: the OpenSpec change, file ownership, test target, and rollback target are known.
- `implemented-local`: repository code, docs, and tests exist on a feature branch or worktree.
- `installed-user-level`: the user-level wrapper or helper exists outside the repository source tree with a receipt.
- `smoke-tested`: the user-level wrapper has passed a minimal read-only or fail-closed command in the intended shell.
- `active`: the tool may be used by default within its allowed lane and authorization boundary.
- `rollback-ready`: the receipt contains enough version, path, command, and backup evidence to revert without guessing.

Default lane-state table:

| Lane | Initial default state | Allowed default actions | Forbidden or approval-gated actions | Evidence required before `active` |
| --- | --- | --- | --- | --- |
| `skills2cli` | `implemented-local`; eligible for user-level `active` only after a later governed wrapper/install receipt | Compact read-only index/search/show/warning summaries | Applying/disabling skills, dumping complete plugin skill bodies, recording full private paths | Compact-output tests, warning-audit redaction tests, evidence that profile suggestions do not apply changes |
| `mcp2cli` | `implemented-local`; eligible for user-level `active` only after later governed wrapper/install receipt and live adapter slices | list/search/show; non-sensitive calls through category-checked local guard facade | Secrets, shell, browser state, remote mutation, payment/account/personal-data calls | Allowed-profile registry, sensitive-call fail-closed checker, authorization receipt schema |
| `codex-port` allocator | `planned`; eligible for `active` only after receipt-backed reserve/renew/release | range-aware lease reserve/list/renew/release/import/gc | cross-owner range allocation, killing port holders, non-atomic registry writes, silent stale reuse | owner-range tests, concurrent-reservation fixtures, live-socket collision fixtures, lease receipt schema, stale PID/health evidence |
| `chrome-devtools-mcp` | `planned`; local isolated debug mode may become `active` first | isolated-session local/debug inspection | human-owned Chrome, logged-in project profiles, cleanup | Managed wrapper, lease, profile ownership, stale-cleanup dry-run evidence |
| CDP Bridge | `on-demand` | tab list, DOM scan, screenshot, read-only inventory | cookies, JavaScript write, click/type/navigate in sensitive context | owner check, authorization gate, read/write separation tests |
| OpenCLI | `on-demand` | explicit isolated or project-profile task adaptation | default binding to human-owned tabs or always-on loading | wrapper pin, browser owner registry, human-owned protection tests |
| `oh-my-pi` | `reference-only` | architecture, UX, and harness reference reading | replacing Codex, replacing native subagents, runtime updates without receipts | pinned clone, smoke test, update/rollback receipt |
| CLI-Anything | `reference-only` | harness-structure reference and generation aid | bulk hard-loading skills or bypassing authorization rules | isolated install receipt, update pin, rollback evidence |
| `wecom-cli` API/Webhook | `planned` | low-risk notifications/API sends when secrets are available and governed | plaintext credentials without secret storage or unredacted logs | secret redaction, webhook/app-message smoke, receipt |
| `wecom-cli` process/window inventory | `planned` | read-only process/window/foreground-state inventory | message-content capture, click, type, send | process/window fixture or smoke, no-content-capture tests |
| `wecom-cli` GUI automation | `disabled` | no default actions | read/send/click/type unless one-task approval and a global lease both exist | global WXWork lease, one-task authorization receipt, manual smoke marker |


Lane-specific `active` criteria:

- `skills2cli`: `index`, `search`, `show`, and warning-audit summary commands work; default output is compact; output does not leak private full paths, cookies, tokens, or full plugin skill descriptions.
- `mcp2cli`: allowed profiles are explicit; list/search/show output is compact by default; sensitive calls fail closed unless a matching authorization receipt is present.
- `codex-port`: port registry/lease enforcement keeps Codex/OpenClaw ranges separated, concurrent reserves are atomic, active owners renew leases, OpenCLI receives only allocator-driven `--port auto` leases, and every write action has a rollback-ready receipt.
- `chrome-devtools-mcp`: the wrapper writes a lease; isolated-session-managed and project-profile modes are distinct; human-owned Chrome is protected; stale-cleanup dry-run passes before cleanup is allowed.
- CDP Bridge: read-only inspection is separated from write-capable actions; every write or sensitive read requires owner evidence and authorization evidence before execution.
- OpenCLI: remains on-demand until installation pinning, profile binding, and the rule blocking unauthorized human-owned tabs are implemented and tested.
- `oh-my-pi`: remains a reference-sidecar until updater receipts, smoke tests, and rollback pins exist.
- CLI-Anything: remains harness-generation support until installation receipts, update pins, and rollback evidence exist.
- `wecom-cli` GUI automation: remains disabled until process/window inventory, a global WXWork lease, and one-task authorization receipts are implemented and tested.

Acceptance criteria for this plan:

- every lane has a documented default state: `active`, `on-demand`, `reference-only`, or `disabled`;
- every user-level installed tool has an update receipt and rollback pointer;
- every shared local listener uses the port allocator, records a port lease receipt, and avoids fixed ports except documented `legacy_reserved` entries;
- concurrent port reservations are serialized through atomic registry writes and provisional-bind handling, with crash recovery proven before reuse;
- every sensitive lane has a fail-closed checker or wrapper guard;
- every browser automation lane records owner class before actions that can read or mutate state;
- no repository evidence stores secrets, cookies, raw browser data, full personal runtime paths, or complete plugin description dumps.

## 14. Sensitive authorization matrix

| Action | Default | Required authorization evidence |
| --- | --- | --- |
| Skill index/search/show | Allowed | None; output must stay compact and redacted. |
| Skill warning audit summary | Allowed | None; warning text must be summarized without dumping full skill bodies. |
| MCP list/search/show | Allowed | Tool must belong to an allowed profile registry entry. |
| MCP call without secrets, side effects, remote mutation, or personal data | Conditional | Allowed tool category plus compact output policy. |
| MCP call with secrets, shell execution, browser state, remote infrastructure mutation, payment/account action, or personal data | Blocked by default | Explicit one-task approval plus receipt containing tool, purpose, scope, and expiry. |
| Chrome isolated-session-managed local debugging | Allowed | Managed lease and isolated profile path. |
| Chrome project-profile with login state | Blocked by default | Project-profile approval plus owner lease; no cross-project reuse without a new lease. |
| Human-owned Chrome read or write | Blocked by default | One-tab, one-task, current-session delegation; no background browsing of personal assets. |
| CDP Bridge or OpenCLI click/type/navigate/cookie/JavaScript write | Blocked by default | Owner check plus explicit approval naming the target and allowed action. |
| WXWork process/window inventory | Allowed read-only | No message content captured; no click/type/send actions. |
| WXWork message read/send/click/type | Blocked by default | One-task approval plus global WXWork lease and receipt. |

Authorization receipts must be short-lived. A receipt for one browser tab, one WXWork task, one MCP call family, or one shell-capable tool does not authorize unrelated future tasks.

## 15. Installation and update evidence contract

Every user-level installed tool in this plan must write a receipt under:

`C:\Users\lenovo\.codex\state\tool-updates\`

Required receipt fields:

- tool name;
- installed version, git commit, package version, or package lock hash;
- source URL;
- install path;
- wrapper path;
- state path;
- smoke test command and result;
- updater command;
- rollback pointer;
- last updated time;
- status: `active`, `on-demand`, `reference-only`, or `disabled`;
- owner lane: `skills2cli`, `mcp2cli`, `codex-port`, `browser`, `oh-my-pi`, `cli-anything`, `wecom-cli`, or `reference`.

Repository evidence may record the receipt schema, relative state names, status, and sanitized smoke-test summaries. It must not record secrets, cookies, tokens, raw browser data, message contents, or full personal runtime paths.

Port lease receipts are operational receipts under `C:\Users\lenovo\.codex\state\ports\receipts\`. They do not replace install/update receipts under `tool-updates`; instead the install/update receipt must reference the relevant port-registry range, allocator wrapper, and lease receipt schema when a tool can open a local listener.

Update rule:

- updater commands must be pinned or version-aware;
- an update that changes wrapper behavior must re-run smoke tests and authorization guard tests;
- a failed smoke test must leave the previous installed version selected;
- rollback must be possible from the receipt without re-reading chat history.

## 16. OpenSpec implementation split

Implement this plan as small, locally testable, rollbackable changes. Default split:

1. policy and checker baseline for token-risk priority, port registry/lease rules, browser asset classes, sensitive authorization, update receipts, and evidence redaction;
2. `skills2cli` MVP: index/search/show plus warning-audit summary with compact output tests;
3. `mcp2cli` user-level wrapper and allowed profile registry;
4. browser owner registry plus `chrome-devtools-mcp` managed wrapper for isolated-session-managed and project-profile modes;
5. CDP Bridge and OpenCLI on-demand enforcement, including human-owned tab protection;
6. `oh-my-pi` sidecar install/update receipts and rollback evidence;
7. CLI-Anything install/update receipts and harness-generation boundary;
8. `wecom-cli` API/Webhook MVP with secret redaction;
9. `wecom-cli` process/window inventory with read-only evidence;
10. `wecom-cli` gated GUI automation with global WXWork lease and one-task authorization receipts.

OpenSpec slice delivery matrix:

| Slice | Main artifacts | Minimum validation | Completion evidence |
| --- | --- | --- | --- |
| 1. Policy/checker baseline | token/risk checker, port registry/lease checker, `codex-port` allocator/locking/lifecycle contract, authorization receipt schema, update receipt schema, evidence-redaction policy | checker unit tests, concurrent-reservation fixture, pending-bind collision fixture, crash-recovery fail-closed fixture, and local-gate registration | checker output, test record, allocator lifecycle evidence, OpenSpec delta/spec update |
| 2. `skills2cli` MVP | repo-local helper, user-level wrapper, skill index/search/show/warning audit | compact-output, privacy-redaction, profile-non-apply, and warning-audit tests | redacted index summary, wrapper smoke, receipt |
| 3. `mcp2cli` MVP | allowed profile registry, list/search/show/call facade | compact-output, sensitive-call fail-closed, and receipt-required tests | profile registry, blocked authorization example, wrapper smoke |
| 4. Browser owner registry | owner registry, lease schema, managed `chrome-devtools-mcp` wrapper | isolated/project-profile/human-owned protection and cleanup dry-run tests | lease receipt, stale-scan dry-run, wrapper smoke |
| 5. CDP Bridge/OpenCLI enforcement | read/write separation gate and on-demand OpenCLI adapter | cookie/JavaScript/click/type/navigate sensitive-action fail-closed tests | owner-check evidence, authorization receipt sample, blocked-action record |
| 6. `oh-my-pi` sidecar | pinned clone/install wrapper and update receipt model | wrapper help smoke, staging fetch, pin switch, rollback tests | lock/receipt, smoke summary, rollback pointer |
| 7. CLI-Anything boundary | isolated install receipt and harness-generation boundary | no-hard-load check, update pin, rollback tests | install receipt and profile-visibility evidence |
| 8. `wecom-cli` API/Webhook | webhook/app-message commands and secret redaction | secret-redaction, dry-run/smoke, receipt-required tests | redacted send summary and evidence that secrets are not stored in repo |
| 9. `wecom-cli` inventory | process/window inventory commands | no-content-capture and read-only fixture/smoke tests | read-only inventory summary and no message-content evidence |
| 10. `wecom-cli` GUI gate | global WXWork lease and one-task authorization gate | unauthorized fail, lease exclusivity, and manual smoke marker tests | authorization receipt, lease receipt, manual smoke marker |

Slice completion rule: a slice is complete only when implementation, tests, CI registration, OpenSpec updates, rollback evidence, and a completed receipt all exist. If a slice has only documentation or research, it can be `planned` or `implemented-local`, but not `active`.

Each OpenSpec change must define:

- files owned by the change;
- local tests or checkers that prove the new behavior;
- user-level install artifact, if any;
- receipt path and schema, if any;
- local listener or port lease ownership, if the change can bind a TCP port;
- rollback method;
- explicit non-goals to keep the change from expanding.


Fine-grained implementation checklist:

- [x] Create or reuse a small OpenSpec change for this plan and state scope, non-goals, and rollback boundary.
- [x] Add a token/risk priority checker that prevents high-token or high-risk surfaces from becoming default without evidence.
- [ ] Establish the user-level port registry/lease allocator so Codex ranges come before OpenClaw ranges and OpenCLI uses allocator-driven `--port auto`.
- [ ] Implement `codex-port lease reserve/renew/release/list/import-legacy/gc` with owner-range validation, atomic registry locking, provisional `pending_bind`, live-socket collision skipping, stale/crash evidence, and write receipts.
- [x] Add the sensitive authorization receipt schema with at least action, target, scope, expiry, session, and operator confirmation.
- [x] Add the user-level tool update receipt schema covering install path, wrapper path, state path, pin, smoke result, and rollback pointer.
- [x] Add sanitized-evidence rules that forbid committing secrets, cookies, tokens, raw browser data, message contents, full personal runtime paths, or complete plugin description dumps.
- [x] Implement `skills2cli index --json` with skill id, source layer, short description hash/summary, and availability status.
- [x] Implement `skills2cli search <query> --json` with compact summaries and location hints by default.
- [x] Implement `skills2cli show <skill-id> --json` without dumping complete skill bodies by default; full content requires a governed flag.
- [x] Implement `skills2cli profile suggest --task <text> --json` as recommendation-only, never direct apply.
- [x] Implement `skills2cli audit warnings --since <duration> --json` covering 2% skills-context-budget warnings and skipped-loading warnings.
- [x] Add `skills2cli` compact-output, privacy-redaction, profile-non-apply, and warning-audit tests.
- [x] Implement the `mcp2cli` allowed profile registry and separate low-risk discovery from medium/high-risk calls.
- [x] Implement compact `mcp2cli list/search/show` output with explicit `--full` expansion boundaries.
- [x] Implement the `mcp2cli call` sensitive-category fail-closed gate.
- [x] Add `mcp2cli` profile-registry, sensitive-call-blocking, compact-output, and receipt-required tests.
- [ ] Implement the browser owner registry with owner class, project slug, session id, profile path, and lease expiry.
- [ ] Implement the `chrome-devtools-mcp` managed wrapper isolated-session mode.
- [ ] Implement the `chrome-devtools-mcp` managed wrapper project-profile mode.
- [ ] Implement browser stale scan and safe-cleanup dry-run, scoped only to known managed profiles.
- [ ] Add browser-lane tests for tab-owner exclusivity, project-profile retention, human-owned protection, and cleanup dry-run.
- [ ] Harden CDP Bridge read-only defaults so write actions require owner and authorization receipts.
- [ ] Keep OpenCLI as an on-demand adapter and connect it to the browser owner registry.
- [ ] Add CDP Bridge/OpenCLI fail-closed tests for cookie, JavaScript, click, type, and navigate sensitive actions.
- [ ] When adapting `oh-my-pi`, write pinned receipt, smoke result, and rollback pointer.
- [ ] Add `oh-my-pi` updater tests for staging fetch, smoke, pin switch, and rollback.
- [ ] Install CLI-Anything / CLI Hub with user-level install receipts and without hard-loading bulk skills.
- [ ] Use CLI-Anything to help design `wecom-cli` while keeping repo-local source and authorization gates.
- [ ] Implement read-only `wecom-cli process list --json` and `window list --json` inventory.
- [ ] Implement `wecom-cli webhook send` and `app-message send` with secret redaction and receipts.
- [ ] Implement `wecom-cli gui attach` with global WXWork lease and one-task authorization gate; keep it disabled by default.
- [ ] Add `wecom-cli` process/window read-only, secret-redaction, GUI-unauthorized-fail, and lease-exclusivity tests.
- [ ] Register every new test or checker in `tools/ci/ci_test_manifest.json` or the shared local-gate call chain.
- [x] Run the precommit update/archive gate, local gate, and local MR review for every completed OpenSpec change.
- [ ] Record rollback-ready receipts after every user-level installation; lanes without receipts must not be marked active.


## 17. Implementation order

1. Create an OpenSpec change for this plan.
2. Add governance docs and checkers for token/risk priority, port registry/lease, browser asset classes, sensitive authorization, and update receipts.
3. Implement `skills2cli` MVP and tests.
4. Add `mcp2cli` user-level wrapper and allowed-profile registry.
5. Promote `chrome-devtools-mcp` to managed user-level wrapper.
6. Harden CDP Bridge policy and add OpenCLI as on-demand adapter only.
7. Add `oh-my-pi` user-level external install wrapper and updater receipt model.
8. Install CLI-Anything / CLI Hub user-level tooling.
9. Build `wecom-cli` API/Webhook MVP, then window inventory, then gated GUI automation.
10. Run local gate, local MR review, and user confirmation before local main integration.

## 18. Validation plan

- `skills2cli` tests prove index/search/show do not emit all skill descriptions.
- `mcp2cli` tests prove compact list/search/show and sensitive-call blocking.
- Browser checker tests prove isolated cleanup, project-profile retention, human-owned protection, and tab owner exclusivity.
- Port-governance tests prove Codex never allocates OpenClaw ranges, OpenClaw legacy ports are imported as reserved, conflicts are skipped without killing processes, and stale leases require PID/health evidence before reuse.
- Port allocator CLI tests prove `reserve`, `renew`, `release`, `import-legacy`, and non-dry-run `gc` write receipts; concurrent reserves do not allocate the same port; pending-bind/crash recovery is evidence-gated; and mismatched owner/range or owner-session requests fail closed.
- CDP Bridge/OpenCLI tests prove sensitive actions require explicit authorization.
- `oh-my-pi` updater tests prove pinned update and rollback receipts.
- `wecom-cli` tests prove process inventory is read-only, secrets are redacted, GUI write actions fail without authorization, and WXWork GUI lease is exclusive.
- Repository checks continue to include OpenSpec guard, precommit update/archive gate, local gate, and local MR review.
- Readiness-gate tests prove no lane becomes `active` without smoke-test evidence, install/update receipt evidence, and rollback evidence.
- Authorization-matrix tests prove sensitive MCP, browser, CDP/OpenCLI, and WXWork actions fail closed without a current one-task authorization receipt.

## 19. Sources

- https://github.com/knowsuchagency/mcp2cli
- https://github.com/jackwener/OpenCLI
- https://github.com/ChromeDevTools/chrome-devtools-mcp
- https://github.com/HKUDS/CLI-Anything
- https://clianything.cc/
- https://blog.can.ac/2026/02/12/the-harness-problem/
- https://github.com/can1357/oh-my-pi
- https://github.com/ymymssss/ohmyopenagent
- https://github.com/MayDay-wpf/snow-cli
