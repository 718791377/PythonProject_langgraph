---
doc_id: reference6_reference7_user_project_live_runtime_plan
lang: zh-CN
doc_class: implementation_plan
status: active
translation_of: docs_bilingual/implementation_plans/reference6_reference7_user_project_live_runtime_plan.md
---

# Reference 6/7 zh-CN Companion - Per-Link True Live Runtime Plan

## Goal / Mubiao

Upgrade `reference_files/6.md` and `reference_files/7.md` from coarse source-reference or adapter-smoke evidence to per-link, true live runtime governance. Each source link must have its own install target, Codex adapter or fork target, live smoke definition, credential or GUI gate, and hash-redacted receipt before `R6 live-executed` can be claimed.

Conflict priority remains `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.

## Current status and correction / Dangqian zhuangtai yu jiupian

The previous rollout installed Reference 6/7 surfaces and recorded checker-passing receipts, but the evidence was too coarse for the new requirement. The new acceptance standard is stricter:

- Raw upstream source discovery is not `R6 live-executed`.
- Raw upstream install alone is not `R6 live-executed`.
- A non-Codex upstream must be forked or adapted into a Codex skill, Codex native agent TOML, Codex runtime wrapper, or Codex project template before completion can count.
- External service links require real credentials and a real service call before live execution can count.
- GUI or local-service links require a real launch, login or authorization when needed, and a screenshot/export/process/port receipt before live execution can count.
- Missing credentials are not blockers to planning, but they are blockers to marking that specific link as live-executed.

## User-confirmed defaults / Yonghu queren moren

- External services: wait for credentials. If `MINERU_API_KEY` is missing, record a user-action blocker and do not mark the affected MinerU links live-executed. Browserbase is explicitly optional-disabled by user decision until `BROWSERBASE_API_KEY` and `BROWSERBASE_PROJECT_ID` are supplied for a future re-enable pass.
- Install scope: user-level plus project templates. Reusable skills and CLI wrappers install under the user Codex home; reusable project surfaces sync into `D:/PythonProject_General`; heavy or risky opt-in surfaces sync into `D:/PythonProject_General_2`.
- GUI and local services: full install/login/launch is allowed when needed. Receipts must redact paths, secrets, account identifiers, screenshots, and tokens by hash or short human-checkable labels.
- Codex config policy: reuse only environment key names and presence booleans from the Codex config shape; never copy secret values.

## Current status anchors / Dangqian zhuangtai maodian

<!-- CURRENT_STATUS_START -->

- 2026-06-18: Plan freeze reopened the Reference 6/7 work because previous checker-passing evidence was too coarse for the new per-link true live runtime requirement.
- 2026-06-18: Runtime implementation remains pending until this plan-freeze package is committed and merged into local `main`.

<!-- CURRENT_STATUS_END -->

<!-- TASK_BACKLOG_START -->

- [x] Re-read Reference 6 and Reference 7 source links.
- [x] Confirm user defaults for credentials, user-level/template scope, and GUI/live actions.
- [x] Replace coarse completion wording with per-link true live runtime criteria.
- [ ] Commit and merge this plan-freeze package into local `main`.
- [ ] Implement strict per-link live runtime manifest/runtime/checker behavior.
- [ ] Run source, user-level, template, local gate, and local MR review gates.
- [ ] Merge implementation into local `main` and stop at remote publication gate.

<!-- TASK_BACKLOG_END -->

<!-- EVIDENCE_INDEX_START -->

| Evidence item | Expected path or command | Status |
| --- | --- | --- |
| Plan-freeze checker | `python tools/check_reference7_capability_install.py --root . --json` | required before plan commit |
| Reference 6 checker | `python tools/check_reference6_capability_install.py --root . --json` | required before plan commit |
| OpenSpec guard | `python tools/run_openspec_guard.py --root . --json` | required before plan commit |
| Implementation strict live check | `python tools/check_reference6_capability_install.py ... --require-live-executed` and `python tools/check_reference7_capability_install.py ... --require-live-executed` | pending implementation |

<!-- EVIDENCE_INDEX_END -->

## Reference 6 per-link matrix / Zhu lianjie juzhen

| Source link | Capability id | Target layer | Required Codex adaptation | True live runtime smoke | Required user input |
| --- | --- | --- | --- | --- | --- |
| `https://github.com/nexu-io/open-design` | `open-design` | `D:/PythonProject_General` plus user-level wrapper | Codex runtime wrapper and template adapter | Clone or cached source is available, start the local GUI/service or documented example, then record a render/export/screenshot/port receipt | GUI login or desktop permission if upstream requires it |
| `https://github.com/nexu-io/html-anything` | `html-anything` | `D:/PythonProject_General` plus user-level wrapper | Codex runtime wrapper and template adapter | Generate one minimal HTML artifact and verify it renders in a browser or local preview | none unless upstream adds account requirements |
| `https://github.com/browserbase/skills` | `browserbase-skills` | user-level Codex skill/CLI adapter | Codex skill adapter plus service wrapper | Disabled optional lane; retain adapter and redacted resume receipt, but do not require live execution while disabled | re-enable with `BROWSERBASE_API_KEY` and `BROWSERBASE_PROJECT_ID` |
| `https://github.com/pymupdf/pymupdf` | `pymupdf` | user-level Python tool capability | Codex Python wrapper/checker | Import `fitz`, create a one-page PDF, reopen it, extract text, and render or validate page metadata | none |
| `https://github.com/opendatalab/MinerU` | `mineru` | user-level CLI/API wrapper | Codex service wrapper and optional template entry | Run a real MinerU package/API smoke against a tiny fixture document | `MINERU_API_KEY` if using official service path |
| `https://mineru.net/apiManage/limit` | `mineru-api-limit` | user-level service receipt | MinerU service receipt surface | Query or verify the account quota/limit endpoint or equivalent official API status | `MINERU_API_KEY` and logged-in account if required |
| `https://mineru.net/` | `mineru-site` | user-level service receipt | MinerU service availability receipt | Verify site/API reachability and bind it to the MinerU adapter receipt | network access and any service login required by upstream |
| `https://github.com/virgiliojr94/book-to-skill` | `book-to-skill` | user-level converter plus template fixture | Codex skill-converter adapter | Convert a tiny markdown/book fixture into a valid Codex `SKILL.md` and run schema/frontmatter smoke | none |
| `https://github.com/mattpocock/skills` | `mattpocock-skills` | user-level Codex skills adapter | Install or adapt actual skills, not just source receipt | Install at least one upstream skill into an isolated or user-level Codex skill directory and read/route it successfully | none unless upstream source changes |

## Reference 7 per-link matrix / Zhu lianjie juzhen

| Source link | Capability id | Target layer | Required Codex adaptation | True live runtime smoke | Required user input |
| --- | --- | --- | --- | --- | --- |
| `https://opc-skills.ft07.com/#install` | `opc-skills-site` | user-level | Codex OPC skill-family adapter | Refresh/read OPC skill family index and run a minimal OPC orchestration fixture | none |
| `https://github.com/easychen/opc-methodology/skills/opc-orchestrator` | `opc-orchestrator` | user-level | Codex skill | Produce a minimal orchestration artifact from fixture input | none |
| `https://github.com/easychen/opc-methodology/skills/opc-resource-audit` | `opc-resource-audit` | user-level | Codex skill | Produce a resource-audit artifact from fixture input | none |
| `https://github.com/easychen/opc-methodology/skills/opc-niche-positioning` | `opc-niche-positioning` | user-level | Codex skill | Produce a niche-positioning artifact from fixture input | none |
| `https://github.com/easychen/opc-methodology/skills/opc-value-proposition` | `opc-value-proposition` | user-level | Codex skill | Produce a value-proposition artifact from fixture input | none |
| `https://github.com/easychen/opc-methodology/skills/opc-business-model-design` | `opc-business-model-design` | user-level | Codex skill | Produce a business-model artifact from fixture input | none |
| `https://github.com/easychen/opc-methodology/skills/opc-mvp-designer` | `opc-mvp-designer` | user-level | Codex skill | Produce an MVP-design artifact from fixture input | none |
| `https://github.com/easychen/opc-methodology/skills/opc-conversion-loop` | `opc-conversion-loop` | user-level | Codex skill | Produce a conversion-loop artifact from fixture input | none |
| `https://github.com/easychen/opc-methodology/skills/opc-asset-ops` | `opc-asset-ops` | user-level | Codex skill | Produce an asset-ops checklist from fixture input | none |
| `https://github.com/easychen/opc-methodology/skills/opc-dashboard-review` | `opc-dashboard-review` | user-level | Codex skill | Review a tiny dashboard fixture and produce a review artifact | none |
| `https://github.com/msitarzewski/agency-agents` | `agency-agents` | user-level agents | Codex native-agent TOML pack adapter | Generate/list valid TOML agents with `name`, `description`, and `developer_instructions` | none |
| `https://github.com/alchaincyf/nuwa-skill` | `nuwa-skill` | user-level | Codex skill | Read the installed skill and produce a minimal generated artifact | none |
| `https://github.com/golutra/golutra` | `golutra` | `D:/PythonProject_General_2` | Codex opt-in GUI/project template adapter | Full install/login/launch or local service start with process/window/port evidence | GUI permission and account if upstream requires it |
| `https://github.com/DeepExperience/MMSkills` | `mmskills` | user-level | Codex skill collection adapter | Run at least one multimedia fixture smoke or record dependency blocker if a required GUI/model dependency is absent | possible model/GUI dependency |
| `https://github.com/Yuan1z0825/nature-skills` | `nature-skills` | user-level | Codex skill collection adapter | Run at least one nature-skill fixture smoke | none |
| `https://github.com/Imbad0202/academic-research-skills` | `academic-research-skills` | user-level | Codex skill | Run a minimal academic-research workflow fixture | none unless external scholarly API is selected |
| `https://github.com/Agents365-ai/drawio-skill` | `drawio-skill` | user-level | Codex skill | Generate or modify a `.drawio` fixture and verify XML/file structure | optional draw.io desktop/browser if upstream requires visual validation |
| `https://github.com/nexu-io/html-video` | `html-video` | `D:/PythonProject_General` | Codex runtime wrapper | Generate minimal HTML/video artifact and validate preview or output file | none unless upstream adds account requirements |
| `https://github.com/nexu-io/nexu` | `nexu` | `D:/PythonProject_General_2` | Codex opt-in bridge/template adapter | Full install/login/launch or local service smoke with account-safe receipt | account/login if upstream requires it |
| `https://github.com/nexu-io/html-anything` | `html-anything-ref7` | dedupe to Reference 6 | Reuse Reference 6 Codex adapter | Same as Reference 6 `html-anything`; receipt must point to dedupe evidence | same as Reference 6 |
| `https://github.com/nexu-io/open-design` | `open-design-ref7` | dedupe to Reference 6 | Reuse Reference 6 Codex adapter | Same as Reference 6 `open-design`; receipt must point to dedupe evidence | same as Reference 6 |
| `https://github.com/safishamsi/graphify` | `graphify` | `D:/PythonProject_General` | Codex runtime wrapper | Generate a graph artifact from a fixture and validate file/graph structure | none |
| `https://github.com/pixel-cellar/Claude-Code-Game-Studios` | `claude-code-game-studios-pixel-cellar` | `D:/PythonProject_General_2` | Fork/adapt as Codex project template | Generate a Codex project skeleton or fixture game-studio artifact; Claude-only files cannot count | none unless upstream dependency requires it |
| `https://github.com/Donchitos/Claude-Code-Game-Studios` | `claude-code-game-studios-donchitos` | `D:/PythonProject_General_2` | Fork/adapt as Codex project template | Same as pixel-cellar variant, with independent receipt | none unless upstream dependency requires it |
| `https://github.com/colbymchenry/codegraph` | `codegraph` | `D:/PythonProject_General` | Codex CLI/MCP runtime wrapper | Generate a code graph from a fixture repo and verify output structure | none unless MCP server path is explicitly selected |

## Implementation stages / Shishi jieduan

1. Plan-freeze package: update this bilingual plan, preserve the per-link matrix, run local plan gates, commit, and merge local `main` before implementation.
2. Manifest/schema package: extend Reference 6 and Reference 7 manifests with `live_runtime` records for install target, adapter target, smoke target, credentials, GUI allowance, and blocker policy.
3. Runtime package: update apply/smoke/check actions so `R6 live-executed` requires the per-link live smoke and so missing credentials produce `R6 blocked` user-action receipts.
4. User-level package: install or refresh user-level Codex skills, native-agent TOMLs, CLI wrappers, service wrappers, and redacted receipts.
5. Template package: update `D:/PythonProject_General` active adapters and `D:/PythonProject_General_2` opt-in adapters with matching checkers and local gate integration.
6. Verification package: run Reference 6/7 strict checks, OpenSpec guard, local gate, local MR review, template gates, and then merge implementation into local `main`.

After this plan is frozen, the implementation contains at least four mostly independent slices: Reference 6 schema/runtime, Reference 7 schema/runtime, user-level install receipts, and two template sync surfaces. Native experts or durable-team lanes may be used for bounded independent verification, but the main Codex session owns final fan-in and local integration.

## Checker acceptance changes / Checker yanshou bianhua

- `--require-live-executed` must fail when any per-link live smoke is only source discovery, readme discovery, placeholder adapter presence, or raw upstream installation.
- `--require-live-executed` must fail with a specific missing credential or GUI/account blocker when a selected external live action cannot run.
- Receipt validation must require an explained live-runtime field set: `live_runtime_target` names the executed adapter or template, `live_smoke_kind` names the smoke class, `live_smoke_result` records pass or blocked, `credential_gate` lists only required env key names, `codex_adapter_present` proves the Codex-facing surface exists, `raw_upstream_install_only=false` rejects source-only installs, and `redaction_status=no_secrets` confirms secret-safe receipts.
- Dedupe entries must point to the exact Reference 6 capability receipt used as their live evidence.
- Template sync checks must prove active adapters exist in General and opt-in adapters exist in General_2.

## Required credentials before affected links can complete / Shou yingxiang lianjie wanqian xuyao de pingju

```powershell
$env:BROWSERBASE_API_KEY="<secret>"
$env:BROWSERBASE_PROJECT_ID="<project-id>"
$env:MINERU_API_KEY="<secret>"
```

If any of these are missing, the implementation must print the missing key name and a redacted fill command, then continue with other links while leaving the affected link as `R6 blocked`.

Marker compatibility: Reference 7 runtime, every non-Codex upstream, raw upstream install only, env_key_name_only.

## Verification gates / Yanzheng menjin

- Pre-commit update/archive review - `python tools/check_precommit_update_archive.py --root . --json`
- OpenSpec governance guard - `python tools/run_openspec_guard.py --root . --json`
- Reference 6 user-level smoke gate - `python tools/check_reference6_capability_install.py --root . --codex-home C:/Users/lenovo/.codex --require-user-level-installed --require-smoke-tested --json`
- Reference 7 strict live/template gate - `python tools/check_reference7_capability_install.py --root . --codex-home C:/Users/lenovo/.codex --require-user-level-installed --require-smoke-tested --require-live-executed --general-root D:/PythonProject_General --general2-root D:/PythonProject_General_2 --require-template-sync --json`
- Shared local CI gate - `powershell -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1`
- Local MR review gate - `powershell -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1`
- Local gates in `D:/PythonProject_General` and `D:/PythonProject_General_2` after template sync.

## Completion criteria / Wancheng biaozhun

- The plan-freeze commit is merged into local `main` before runtime implementation starts.
- Every Reference 6/7 source link has an explicit per-link install and live-smoke record.
- All non-Codex upstreams have counted Codex adapters or forks before live completion is claimed.
- Browserbase is not marked live-executed while optional-disabled; MinerU is marked live-executed only when `MINERU_API_KEY` exists and the real service smoke passes.
- General and General_2 are updated, clean, and locally validated.
- The implementation commit is merged into local `main`; remote publication remains stopped until the user explicitly requests it.
