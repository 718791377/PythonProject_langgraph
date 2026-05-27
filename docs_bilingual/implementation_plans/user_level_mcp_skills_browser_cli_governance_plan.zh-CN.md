---
doc_id: user_level_mcp_skills_browser_cli_governance_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
status: draft
plan_readiness: execution-ready
implementation_state: receipt_redaction_guard_repo_local_implemented
last_reviewed_at: 2026-05-27
doc_class: implementation_plan
created_at: 2026-05-22
source_reference_file: reference_files/1.md
comet_workflow: full
comet_phase_model: open-design-build-verify-archive
implementation_lane: p0_repo_local_governance_to_user_level_capability
local_codex_governance_fork_reference: docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md
related_docs:
  - docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md
  - docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md
  - docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md
  - docs_bilingual/governance/codex_user_level_skills_governance_policy.zh-CN.md
---

# 用户级 MCP、Skills、Browser 与 CLI Harness 治理实施方案（新版 Comet 结构）

> **For agentic workers:** REQUIRED SUB-SKILL: 使用 `superpowers:executing-plans` 执行本方案；涉及跨文件实现时再使用 `superpowers:subagent-driven-development`。所有步骤必须用 checkbox 逐项跟踪；每个任务完成后先运行该任务列出的局部验证，再进入下一任务。远端发布不属于本方案默认授权。

**Goal:** 将 Codex 用户级 MCP、skills、browser automation 与 CLI harness 从“常驻大上下文/手工调用”治理为低 Token、低风险、可审计、可回滚、可跨项目复用的用户级控制面。

**Architecture:** Codex 会话先读取 repo-local policy、OpenSpec 与 checker；低风险 discovery 走 `skills2cli`、`mcp2cli`、`codex-port` 和 browser owner registry；高风险 MCP call、CDP Bridge、OpenCLI、CLI-Anything、`wecom-cli`、cookies 或 WXWork 操作必须先写 authorization receipt schema，并保留 update receipt、rollback pointer 和 redaction evidence。

**Tech Stack:** Codex user-level wrappers、Python checkers、PowerShell launchers、JSON receipts、OpenSpec delta、Superpowers evidence、Git worktrees、CDP Bridge、chrome-devtools-mcp、OpenCLI、CLI-Anything、WeCom/WXWork adapter、`C:\Users\lenovo\.codex` user-level runtime state。

---

## 0. 当前复核结论

本版已按 `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` 和 `comet_runtime_agile_focus_area_plan.zh-CN.md` 的新版结构返工：先给出 worker 指令、Goal、Architecture、Tech Stack，再给出关系模型、runtime 契约、文件职责图、实施前就绪定义、任务级执行 Backlog、验收标准、需要保留的证据和 rollback 规则。

`status: draft` 只表示完整用户级安装、真实 smoke test 与跨项目 rollout 尚未全部完成；`plan_readiness: execution-ready` 表示本文结构与执行颗粒度已经足够让 agentic worker 接手实现。当前 repo-local `skills2cli`、`mcp2cli`、`codex-port`、browser owner registry、`chrome-devtools-mcp` wrapper MVP 与 CDP Bridge read-only defaults 属于 implemented-local；完整用户级 `active` 仍取决于 installation receipt、update receipt、smoke test result 与 rollback pointer。`wecom-cli` 当前只达到 repo-local guarded dry-run，不代表真实企业微信 GUI 自动化已启用。

## 1. 关系模型与命名边界

| 名称 | 责任边界 | 默认状态 | 边界说明 |
| --- | --- | --- | --- |
| `skills2cli` | skill index/search/show/audit/profile suggest | implemented-local | 不把完整 skill bodies 放入上下文；缓解 Token budget 压力。 |
| `mcp2cli` | MCP list/search/show/call facade | implemented-local | discovery 低风险；真实 call 需按风险分层 fail closed。 |
| `codex-port` | port registry、lease、pending_bind、registry_revision | implemented-local | Codex 端口段在下游项目之前，避免冲突。 |
| browser owner registry | 三类浏览器资产登记与 lease | implemented-local | 区分 isolated-session-managed、project-profile、human-owned。 |
| `chrome-devtools-mcp` | 用户级 DevTools MCP wrapper | implemented-local | 低风险 read-only 优先；写操作需要 owner + authorization receipt。 |
| CDP Bridge | 浏览器桥接与 CDP 操作 | implemented-local | 默认 read-only；cookies、输入、点击、导航属于敏感操作。 |
| OpenCLI | on-demand browser/MCP adapter | planned/partial | 必须 `--port auto`，并受 owner registry 与 receipt 约束。 |
| CLI-Anything | GUI/CLI harness generation/reference | planned | 不允许 hard-load 大量 skills；生成优先，执行受授权门禁控制。 |
| `wecom-cli` | WeCom/WXWork API/Webhook/GUI adapter | implemented-local | WXWork.exe GUI write 默认 disabled；repo-local guard 已提供 API/Webhook first、global lease、operator confirmation 与 timeout release dry-run 检查。 |
| `oh-my-pi` | Pi family / harness reference | reference-only | 具体 Pi sidecar 归属 `pi_plugin_codex_user_level_sidecar_plan`。 |
| `ohmyopenagent` / `snow-cli` | 未来 durable-team 参考源 | reference-only | 本方案不安装、不接入 runtime。 |
| human-owned Chrome | 用户个人资产 | disabled for automation by default | 未授权不得读取 cookies、tokens、raw browser data。 |

## 2. 目标与非目标

目标：

- [ ] 优先使用 Token 最低、风险最低的 discovery surface：repo docs、`skills2cli index/search`、`mcp2cli list/search/show`。
- [ ] 用 `skills2cli` 替代常驻 skill body 注入，避免 plugin description dumps 和 skill context budget 超限。
- [ ] 用 `mcp2cli` 将 MCP discovery、profile 选择与 call execution 拆开，敏感 MCP 调用默认 fail closed。
- [ ] 用 browser owner registry 明确 isolated-session-managed、project-profile、human-owned Chrome assets。
- [ ] 用 `codex-port` 管理 port registry、pending_bind、registry_revision、lease renewal、crash recovery。
- [ ] 用 authorization receipt schema、update receipt、rollback pointer 和 evidence redaction 确保可审计、可回滚。

非目标：

- [ ] 不 hard-load 每个 MCP 或 skill。
- [ ] 不为了减少 Token 粗暴禁用 Browser、OpenCLI、WeCom 或 Vercel 等未来可能需要的能力。
- [ ] 不在没有 receipt 的情况下修改 `C:\Users\lenovo\.codex`。
- [ ] 不读取或暴露 secrets、cookies、tokens、raw browser data、WeCom message contents。
- [ ] 不把 OpenCLI、CDP Bridge 或 CLI-Anything 变成默认高权限自动化通道。

## 3. 运行时架构

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

默认用户级产物根目录：`C:\Users\lenovo\.codex\tools\skills2cli\`、`C:\Users\lenovo\.codex\tools\mcp2cli\`、`C:\Users\lenovo\.codex\tools\codex-port\`、`C:\Users\lenovo\.codex\tools\browser-automation\`、`C:\Users\lenovo\.codex\tools\wecom-cli\`。runtime state 放在 `C:\Users\lenovo\.codex\state\`，repo-local source of truth 仍在本仓库。

## 4. Codex 中的使用方式

- [ ] 先读 repo-local policy、OpenSpec 和 checker，再决定是否需要 MCP、skills、browser automation 或 CLI harness。
- [ ] discovery 阶段优先读 compact JSON，不加载完整 skill bodies 或 plugin descriptions。
- [ ] `skills2cli show` 默认只给摘要；需要全文时必须有明确任务原因。
- [ ] `mcp2cli call`、browser write、CDP input、OpenCLI execute、WeCom GUI 操作前必须创建 authorization receipt schema。
- [ ] 端口必须通过 `codex-port lease reserve --owner codex --purpose <tool> --port auto --json` 分配。
- [ ] OpenCLI 必须使用 `--port auto`；禁止硬编码与下游项目冲突的端口。
- [ ] WeCom 默认优先 API/Webhook；GUI attach 必须有 operator confirmation、WXWork.exe 全局 lease 和超时清理。

## 5. Repo-local source of truth

| 分类 | repo-local source | 用户级产物 | 更新规则 |
| --- | --- | --- | --- |
| policy | `docs_bilingual/governance/*`、`openspec/specs/*` | 生成的 launcher/helper 配置 | policy 先变更，installer 后生成。 |
| plan | `docs_bilingual/implementation_plans/*` | 无直接 runtime 产物 | plan 不等于 active runtime。 |
| checker | `tools/check_*.py`、`tools/ci/local_gate.ps1` | 可选 installed checker copy | repo-local 是 source of truth。 |
| helper source | repo-local tools/templates | `C:\Users\lenovo\.codex\tools\...` | 用户级 copy 是 install artifact。 |
| receipt schema | docs、tests、OpenSpec | redacted runtime JSON receipt | 不能包含 secrets。 |
| OpenSpec | `openspec/changes/*`、`openspec/specs/*` | 无 | WHAT 的治理证据。 |
| Superpowers | `docs/superpowers/*` | 无 | HOW 的执行证据。 |

## 6. Installation and update evidence contract / 安装与更新证据契约

每个用户级安装或更新动作都必须生成 update receipt；没有 receipt 的 lane 只能是 planned、partial 或 implemented-local，不能标记为 active。

| field | required | 说明 |
| --- | --- | --- |
| tool name | yes | lane id，例如 `skills2cli`、`mcp2cli`、`codex-port`。 |
| installed version | yes | commit、tag 或 package version。 |
| source URL | yes | 不得包含 token。 |
| install path | yes | 用户级安装目录。 |
| wrapper path | yes | launcher 或 wrapper 路径。 |
| state path | yes | runtime state 根目录。 |
| smoke test command | yes | 可重复执行。 |
| smoke test result | yes | pass/fail + timestamp。 |
| updater command | yes | 必须 pin-aware。 |
| rollback pointer | yes | 上一版本、备份目录或 git ref。 |
| owner lane | yes | `skills2cli`、`mcp2cli`、`browser`、`wecom-cli` 等。 |
| redaction status | yes | 证明不含 secrets、cookies、tokens、raw browser data。 |

## 7. Token and risk priority model / Token 与风险优先级模型

| Priority | Surface | Token | Risk | Default action |
| --- | --- | --- | --- | --- |
| P0 | repo docs/checkers/OpenSpec | low | low | 直接读取。 |
| P1 | `skills2cli index/search` | low | low | compact summary。 |
| P1 | `mcp2cli list/search/show` | low | low | compact summary。 |
| P2 | browser tab inventory | medium | medium | read-only + owner evidence。 |
| P2 | OpenCLI discovery | medium | medium | on-demand + port lease。 |
| P3 | MCP call | high | high | authorization receipt。 |
| P3 | CDP Bridge JS / cookies | high | high | authorization receipt + redaction。 |
| P3 | `wecom-cli gui attach` | high | high | 默认 disabled。 |
| P3 | human-owned Chrome assets | high | high | operator confirmation required。 |

## 8. 用户级端口治理

port registry 由 `codex-port` 管理，必须支持 `registry_revision`、atomic write、`pending_bind`、lease renewal 和 crash recovery。

| Owner | Range | 说明 |
| --- | --- | --- |
| Codex general helpers | `39000-39299` | 默认 Codex 用户级 helper 端口段。 |
| Codex browser/OpenCLI | `39300-39499` | OpenCLI 必须使用 `--port auto`。 |
| Reserved local bridge | `39500-39999` | 预留给本地桥接。 |
| Downstream consumer project range | `40000-40999` | 下游消费项目端口排在 Codex 后面。 |
| Emergency quarantine | `41000-41099` | 临时隔离冲突，不作为默认范围。 |

| Command | Purpose | Receipt |
| --- | --- | --- |
| `codex-port registry show --json` | 读取 port registry | 无写入。 |
| `codex-port lease reserve --owner <name> --port auto --json` | 自动分配 | lease receipt。 |
| `codex-port lease renew --lease-id <id> --json` | 续约 | updated lease。 |
| `codex-port lease release --lease-id <id> --json` | 释放 | completed receipt。 |
| `codex-port import-legacy --owner <name> --json` | 导入旧端口 | migration receipt。 |
| `codex-port gc --dry-run --json` | stale scan | 无写入。 |
| `codex-port gc --apply --json` | stale cleanup | evidence-gated write。 |

## 9. CLI JSON contracts

### 9.1 `skills2cli` lane contract

| Command | Default output | Risk gate |
| --- | --- | --- |
| `skills2cli index --json` | skill name、source、short description hash | read-only。 |
| `skills2cli search <query> --json` | compact candidates | read-only。 |
| `skills2cli show <name> --json` | 摘要、entrypoint、risk metadata | full body opt-in。 |
| `skills2cli audit warnings --json` | warning summary | redact paths/content。 |
| `skills2cli profile suggest --task <task> --json` | profile suggestion | preview only。 |

### 9.2 `mcp2cli` lane contract

| Command | Default output | Risk gate |
| --- | --- | --- |
| `mcp2cli list --json` | server list + enabled state | read-only。 |
| `mcp2cli search <query> --json` | compact capabilities | read-only。 |
| `mcp2cli show <server> --json` | tool summaries | no secrets。 |
| `mcp2cli call <server> <tool> --json` | guarded execution | authorization receipt required for sensitive calls。 |
| `mcp2cli profile suggest --task <task> --json` | profile preview | no config mutation。 |

## 10. Browser / OpenCLI / CDP / WeCom 风险门禁

| Lane | Read-only allowed | Sensitive action | Required gate |
| --- | --- | --- | --- |
| isolated-session-managed | tab inventory、screenshot | click/type/navigate | owner lease + authorization receipt。 |
| project-profile | inventory with project lease | profile mutation | project authorization + retention policy。 |
| human-owned Chrome | none by default | cookies、tokens、history、message contents | explicit operator confirmation。 |
| CDP Bridge | tab inventory | JS execution、cookies、form input | owner lease + action scope。 |
| OpenCLI | discovery | adapter execute | `--port auto` + receipt。 |
| CLI-Anything | harness plan | hard-load / live control | disabled until receipt and smoke pass。 |
| `wecom-cli` | API status | WXWork.exe GUI automation | global WXWork lease + operator confirmation。 |

authorization receipt schema 必须包含：`action`、`target`、`scope`、`expiry`、`session`、`operator confirmation`、`owner lane`、`redaction policy`、`rollback pointer`。

## 11. Runtime state contract

| State | Meaning | Allowed next state |
| --- | --- | --- |
| planned | 只有方案，没有 repo-local helper。 | implemented-local。 |
| implemented-local | repo-local source/checker 已存在。 | install-ready。 |
| install-ready | 用户级安装产物可生成。 | active 或 blocked。 |
| active | update receipt、smoke test、rollback pointer 均存在。 | update-needed、disabled。 |
| on-demand | 仅按任务启动，不常驻。 | active 或 disabled。 |
| disabled | 默认关闭。 | on-demand。 |
| reference-only | 只作为资料来源。 | planned。 |
| blocked | 缺 receipt、smoke、权限或安全证据。 | install-ready。 |

runtime receipts 不得包含 secrets、cookies、tokens、raw browser data、WeCom message contents 或完整 plugin description dumps。

## 12. Comet Management Record 模板

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
| Open | scope、non-goals、risk lanes、reference-only list | no unmanaged user-level mutation。 |
| Design | architecture、state contract、authorization schema | no high-risk lane without receipt design。 |
| Build | helper source、tests、docs、receipt samples | no install without rollback pointer。 |
| Verify | local gate、local MR review、manual structure review | no merge if target structure misses required sections。 |
| Archive | stable spec sync or explicit archive deferral | no remote publish without explicit approval。 |
| Monitoring | current facts、variance、return decision | return to earlier phase if evidence is incomplete。 |

## 14. Monitoring return semantics

| Decision | Meaning | Required fields |
| --- | --- | --- |
| `continue` | Comet 控制决策取值，含义是当前证据足够，可以正常推进到下一阶段。 | 记录 current facts 与证据日期。 |
| `adjust-current` | Comet 控制决策取值，含义是当前阶段需要先做局部修正再继续推进。 | 记录 blocker、owner 与修正范围。 |
| `return-open` | Comet 控制决策取值，含义是范围或价值定义不足，必须回退到 Open 阶段。 | 设置 target_phase=open，并记录 rework_reason。 |
| `return-design` | Comet 控制决策取值，含义是架构或安全边界不足，必须回退到 Design 阶段。 | 设置 target_phase=design，并记录 rework_reason。 |
| `return-build` | Comet 控制决策取值，含义是实现证据不足，必须回退到 Build 阶段。 | 设置 target_phase=build，并记录 rework_reason。 |
| `return-verify` | Comet 控制决策取值，含义是验证证据不足，必须回退到 Verify 阶段。 | 设置 target_phase=verify，并记录 rework_reason。 |
| `stop` | Comet 控制决策取值，含义是风险、授权或治理策略阻断阶段推进。 | 记录 blocker 与下一次用户决策。 |

## 15. OpenSpec slice delivery matrix

| Slice | Scope | Output | Local verification |
| --- | --- | --- | --- |
| Slice 0 | OpenSpec / Comet evidence | proposal、design、tasks、management、delta spec | `openspec validate --all`。 |
| Slice 1 | `skills2cli` governance | compact index/search/show/audit contract | unit tests + baseline checker。 |
| Slice 2 | `mcp2cli` governance | discovery/call/risk profile contract | unit tests + fail-closed tests。 |
| Slice 3 | `codex-port` governance | port registry、pending_bind、registry_revision | port allocator tests。 |
| Slice 4 | browser owner registry | isolated/project/human asset model | owner registry tests。 |
| Slice 5 | CDP/OpenCLI/chrome-devtools-mcp | read-only defaults + sensitive gates | CDP/OpenCLI governance tests。 |
| Slice 6 | CLI-Anything / `wecom-cli` | generation-first and WXWork guard | fixture tests, no live GUI by default。 |
| Slice 7 | receipts / rollback / redaction | update receipt、authorization receipt、rollback pointer | redaction and schema checks。 |
| Slice 8 | local integration | local gate、local MR review、commit、local main merge | clean worktree + rollback ref。 |

### Slice completion rule

- [ ] 每个 slice 必须有 repo-local source、checker 或 fixture test。
- [ ] 每个 slice 必须说明是否有用户级 install artifact。
- [ ] 每个 slice 必须保留 rollback pointer 或明确说明尚未安装。
- [ ] 任一 sensitive lane 缺 receipt 时不得标记 active。

## 16. 文件职责图

| File group | Responsibility | Owner lane |
| --- | --- | --- |
| `docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.*` | 本方案与英文 companion | governance plan。 |
| `openspec/changes/*/specs/codex-user-level-mcp-skills-browser-cli-governance/spec.*` | WHAT delta spec | OpenSpec。 |
| `docs/superpowers/specs/*user-level-mcp*` | HOW design evidence | Superpowers。 |
| `tools/check_user_level_mcp_skills_browser_cli_baseline.py` | baseline markers and safety registration | checker。 |
| `tools/*skills2cli*` | skill compact facade | skills2cli。 |
| `tools/*mcp2cli*` | MCP compact facade | mcp2cli。 |
| `tools/*codex_port*` | port registry and lease | codex-port。 |
| `tools/*browser*` | browser owner registry | browser。 |
| user-level `C:\Users\lenovo\.codex\tools\...` | installed helper copy | install artifact only。 |

## 17. 实施前就绪定义

- [ ] Readiness gate: 本方案和英文 companion 均已更新。
- [ ] Readiness gate: OpenSpec change 有 proposal、design、tasks、delta spec、management record。
- [ ] Readiness gate: 每个 task 有明确 output 与 local verification。
- [ ] Readiness gate: authorization receipt schema、update receipt、rollback pointer 字段齐全。
- [ ] Readiness gate: port registry、`codex-port`、`pending_bind`、`registry_revision`、`39000-39299`、`40000-40999` 均保留。
- [ ] Readiness gate: sensitive authorization matrix 覆盖 MCP、CDP Bridge、OpenCLI、browser、WeCom/WXWork。
- [ ] Readiness gate: 不依赖 prompt-only rule，必须有 checker 或 fixture。

## 18. Fine-grained implementation checklist / 任务级执行 Backlog

### Task 0：OpenSpec change 与实现边界冻结

- [ ] 创建或更新 OpenSpec proposal，说明本方案只治理 Codex 用户级控制面。
- [ ] 创建或更新 OpenSpec design，说明 low-token-first、risk-gated 和 receipt-first 原则。
- [ ] 创建或更新 delta spec，保留 Token/risk priority、authorization receipt、update receipt、evidence redaction、port registry/lease 等要求。
- [ ] 创建或更新 management record，确认 Monitoring decision 是 `continue`。
- [ ] 局部验证：`openspec validate --all`。

### Task 1：`skills2cli` compact facade

- [ ] 定义 `index/search/show/audit/profile suggest` JSON 输出。
- [ ] 确保默认不输出 full skill body。
- [ ] warning audit 必须摘要化并 redacted。
- [ ] profile suggest 只能 preview，不自动 apply。
- [ ] 局部验证：`skills2cli.test.py`。

### Task 2：`mcp2cli` discovery/call facade

- [ ] 定义 `list/search/show` compact 输出。
- [ ] 定义 `call` 的风险分层和 fail closed 默认。
- [ ] sensitive call 缺 authorization receipt 必须失败。
- [ ] receipt 输出不得包含 secrets、cookies、tokens。
- [ ] 局部验证：`mcp2cli.test.py`。

### Task 3：`codex-port` 端口租约治理

- [ ] 实现或保持 port registry 原子写入。
- [ ] `pending_bind` 必须可恢复。
- [ ] `registry_revision` 必须随写入递增。
- [ ] Codex 端口范围必须在下游 consumer range 前。
- [ ] 局部验证：`codex_port.test.py`。

### Task 4：Browser owner registry

- [ ] isolated-session-managed 可被自动清理。
- [ ] project-profile 需要项目授权且不可被 stale cleanup 误删。
- [ ] human-owned Chrome assets 默认不可自动化。
- [ ] 同一 target 只能有一个 owner。
- [ ] 局部验证：`browser_owner_registry.test.py`。

### Task 5：CDP Bridge / chrome-devtools-mcp / OpenCLI

- [ ] read-only tab inventory 不需要敏感授权。
- [ ] click/type/navigate/JS/cookie read 必须授权。
- [ ] OpenCLI 必须用 `--port auto`。
- [ ] live start 需要 install receipt 和 owner evidence。
- [ ] 局部验证：`chrome_devtools_mcp_managed.test.py`、`cdp_bridge_governance.test.py`。

### Task 6：CLI-Anything 与 `wecom-cli`

- [x] CLI-Anything 默认只生成 harness plan。
- [x] hard-load skills 必须 blocked，直到 receipt 和 smoke pass。
- [x] `wecom-cli` 优先 API/Webhook，不默认 GUI automation。
- [x] WXWork.exe GUI 操作必须有全局 lease、operator confirmation 和超时释放。
- [x] 局部验证：`wecom_cli_governance.test.py` 覆盖 API/Webhook 优先、GUI dry-run、缺 receipt fail closed、有效 receipt 仅允许 dry-run dispatch。

### Task 7：Receipts、rollback 与 redaction

- [x] authorization receipt schema 包含 action、target、scope、expiry、session、operator confirmation，并由 `tools/user_level_receipt_governance.py auth-check` 强制校验。
- [x] update receipt 包含 tool name、installed version、source URL、install path、wrapper path、state path、smoke test command、smoke result、updater command、rollback pointer、owner lane、redaction status，并由 `tools/user_level_receipt_governance.py update-check` 强制校验。
- [x] redaction 覆盖 secrets、cookies、tokens、raw browser data、message contents、plugin description dumps，并由 `redact-check` fail closed。
- [x] rollback pointer 可定位上一版本或备份目录，默认输出只暴露 hash。
- [x] 局部验证：`user_level_receipt_governance.test.py` 和 baseline checker 覆盖 receipt schema、rollback pointer、redaction output。

### Task 8：本地集成

- [ ] feature worktree 干净。
- [ ] 本地 pre-commit update/archive gate 通过。
- [ ] `tools/ci/local_gate.ps1` 通过。
- [ ] `tools/ci/local_mr_review.ps1` 通过。
- [ ] 创建 local main rollback ref。
- [ ] ff-only 合入本地 `main`。
- [ ] 远端发布保持 explicit approval gate。

## 19. 本地集成顺序

1. 在 feature worktree 中完成文档、OpenSpec、Superpowers 证据更新。
2. 运行局部 marker 检查和人工结构对照。
3. 运行 `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json`。
4. 运行 `python tools/run_openspec_guard.py --root . --json`。
5. 运行 `tools/ci/local_gate.ps1 -Json`。
6. 提交中文 commit subject。
7. 运行 `tools/ci/local_mr_review.ps1 -Json`。
8. 创建 `refs/backup/local-main/*` rollback ref。
9. `git merge --ff-only <feature-branch>` 合入本地 `main`。
10. 停在远端发布授权门禁。

## 20. Readiness gates and acceptance criteria / 完成复核清单

- [ ] 目标文件包含 `For agentic workers`、`Goal`、`Architecture`、`Tech Stack`。
- [ ] 目标文件包含 `文件职责图`、`实施前就绪定义`、`任务级执行 Backlog`、`完成复核清单`、`验收标准`、`需要保留的证据`。
- [ ] 英文 companion 使用同等结构且保持 ASCII primary。
- [ ] lane 状态没有把 planned/partial 错标 active。
- [ ] sensitive authorization matrix 覆盖所有高风险通道。
- [ ] checklist 不少于 30 项，table rows 不少于 40 行。
- [ ] OpenSpec delta spec 包含 baseline markers。
- [ ] local gate 和 local MR review 通过。

## 21. Verification plan / 验收标准

| Check | Command | Pass criteria |
| --- | --- | --- |
| Baseline | `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json` | `ok=true`。 |
| OpenSpec | `python tools/run_openspec_guard.py --root . --json` | all guard steps pass。 |
| Local gate | `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1 -Json` | all shared CI steps pass。 |
| Local MR review | `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1 -Json` | clean feature branch, merge-tree ok。 |
| Manual structure review | heading scan | 新版结构标题存在且可读。 |

## 22. 需要保留的证据

- [ ] OpenSpec proposal/design/tasks/spec/management record。
- [ ] Superpowers design doc、implementation plan、verification report。
- [ ] baseline checker output。
- [ ] local gate JSON output 或终端摘要。
- [ ] local MR review JSON output 或终端摘要。
- [ ] local main rollback ref。
- [ ] worktree receipt 和 branch-matching claim。

## 23. Rollback 与清理

- [ ] 文档返工可通过 local main rollback ref 回退。
- [ ] 用户级安装变更必须通过 update receipt 的 rollback pointer 回退。
- [ ] 未获远端发布授权时不得推送 GitLab/GitHub。
- [ ] 已合入但未远端发布的 feature branch 可保留为 publication carrier。
- [ ] 清理 worktree 前必须确认 main contains branch head、rollback ref 存在、receipt 完成。

## 24. 风险与默认决策

| Risk | Default decision | Mitigation |
| --- | --- | --- |
| Token budget 继续超限 | 不 hard-load skills | `skills2cli` compact discovery。 |
| MCP 调用泄露敏感信息 | fail closed | authorization receipt + redaction。 |
| 浏览器资产误操作 | human-owned disabled | owner registry + operator confirmation。 |
| 端口与下游项目冲突 | Codex range first | `codex-port --port auto`。 |
| WeCom GUI 自动化风险 | disabled | API/Webhook first；GUI 需 WXWork lease。 |
| 用户级安装不可回滚 | blocked | update receipt + rollback pointer。 |
| 方案再次退化为说明书 | block merge | 人工结构检查 + baseline checker。 |

## 25. 参考源

- `docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` - 本地 Codex 治理 fork 参考源，用于用户级 Pi sidecar 边界、receipt、更新与回滚规则。
- `docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md` - Comet 新版结构参考源，用于管理记录、Monitoring loop、阶段门禁与证据布局。
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md` - MCP 权威边界参考源，用于判断 MCP 条目属于 Codex 直连、MCP Router 共享管理，还是不应纳入。
- `docs_bilingual/governance/codex_user_level_skills_governance_policy.zh-CN.md` - Skills 治理参考源，用于可见性、profile 加载、token 预算控制与 usage audit 边界。
- `reference_files/1.md` - 本地参考资料记录，用于保留触发本治理 fork 的上游链接与操作员备注。
