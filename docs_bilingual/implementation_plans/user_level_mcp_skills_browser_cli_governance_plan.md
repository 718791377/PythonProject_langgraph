---
doc_id: user_level_mcp_skills_browser_cli_governance_plan
lang: en
canonical: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
status: draft
doc_class: implementation_plan
created_at: 2026-05-22
source_reference_file: reference_files/1.md
---

# User-Level MCP, Skills, Browser, and CLI Harness Governance Plan

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
C:\Users\lenovo\.codex\tools\browser-automation\
C:\Users\lenovo\.codex\tools\wecom-cli\
C:\Users\lenovo\.codex\state\mcp2cli\
C:\Users\lenovo\.codex\state\skills2cli\
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

Current local fact: `WXWork.exe` is present and running from `D:\Program Files\WXWork\WXWork.exe`.

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

## 13. Implementation order

1. Create an OpenSpec change for this plan.
2. Add governance docs and checkers for token/risk priority, browser asset classes, sensitive authorization, and update receipts.
3. Implement `skills2cli` MVP and tests.
4. Add `mcp2cli` user-level wrapper and allowed-profile registry.
5. Promote `chrome-devtools-mcp` to managed user-level wrapper.
6. Harden CDP Bridge policy and add OpenCLI as on-demand adapter only.
7. Add `oh-my-pi` user-level external install wrapper and updater receipt model.
8. Install CLI-Anything / CLI Hub user-level tooling.
9. Build `wecom-cli` API/Webhook MVP, then window inventory, then gated GUI automation.
10. Run local gate, local MR review, and user confirmation before local main integration.

## 14. Validation plan

- `skills2cli` tests prove index/search/show do not emit all skill descriptions.
- `mcp2cli` tests prove compact list/search/show and sensitive-call blocking.
- Browser checker tests prove isolated cleanup, project-profile retention, human-owned protection, and tab owner exclusivity.
- CDP Bridge/OpenCLI tests prove sensitive actions require explicit authorization.
- `oh-my-pi` updater tests prove pinned update and rollback receipts.
- `wecom-cli` tests prove process inventory is read-only, secrets are redacted, GUI write actions fail without authorization, and WXWork GUI lease is exclusive.
- Repository checks continue to include OpenSpec guard, precommit update/archive gate, local gate, and local MR review.

## 15. Sources

- https://github.com/knowsuchagency/mcp2cli
- https://github.com/jackwener/OpenCLI
- https://github.com/ChromeDevTools/chrome-devtools-mcp
- https://github.com/HKUDS/CLI-Anything
- https://clianything.cc/
- https://blog.can.ac/2026/02/12/the-harness-problem/
- https://github.com/can1357/oh-my-pi
- https://github.com/ymymssss/ohmyopenagent
- https://github.com/MayDay-wpf/snow-cli
