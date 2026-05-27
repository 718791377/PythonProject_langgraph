---
doc_id: user_level_mcp_skills_browser_cli_governance_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
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
local_codex_governance_fork_reference: docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md
related_docs:
  - docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md
  - docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md
  - docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md
  - docs_bilingual/governance/codex_user_level_skills_governance_policy.zh-CN.md
---

# 用户级 MCP、Skills、Browser 与 CLI Harness 治理实施方案

## 0. 当前复核结论

本方案已按 `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` 与 `comet_runtime_agile_focus_area_plan.zh-CN.md` 的新版实施方案结构重构：先说明关系边界，再说明目标/非目标、运行时架构、Codex 使用方式、repo-local source of truth、用户级安装产物、receipt、状态契约、Comet 管理记录、阶段门禁、实施切片、任务级 backlog、本地集成、验收、证据、回滚与风险。

`status: draft` 表示完整用户级 runtime 尚未全部安装并完成 smoke test；它不表示本文缺少执行结构。当前 repo-local 的 `skills2cli`、`mcp2cli`、`codex-port`、browser owner registry、`chrome-devtools-mcp` wrapper MVP 与 CDP Bridge read-only-default guard 仍属于 `implemented-local`，不是完整用户级 `active`。

## 1. 关系模型与命名边界

本方案治理 Codex 用户级、跨项目、跨会话可复用的控制面。它不是 PyCharm IDE 集成，也不是某个单项目私有脚本。

| 名称 | 责任边界 | 默认状态 | 边界说明 |
| --- | --- | --- | --- |
| skills2cli | skill index/search/show/audit/profile suggest | implemented-local | 默认不把完整 skill bodies 放入上下文 |
| mcp2cli | MCP list/search/show/call facade | implemented-local | sensitive calls fail closed |
| codex-port | port registry / lease allocator | implemented-local | Codex ranges precede downstream consumer ranges |
| chrome-devtools-mcp | managed browser automation wrapper | implemented-local | 三类浏览器资产必须隔离 |
| CDP Bridge | browser bridge | implemented-local | read-only first |
| OpenCLI | on-demand browser/MCP adapter | planned/partial | 必须使用 --port auto 和 owner gate |
| CLI-Anything | harness generation/reference | planned | 不 hard-load 大量 skills |
| wecom-cli | WeCom/WXWork API/Webhook/GUI | planned | GUI write 默认 disabled |
| oh-my-pi | Pi family / harness reference | reference-only | 真正 sidecar 归属 pi_plugin 方案 |
| ohmyopenagent / snow-cli | 未来 durable-team 参考 | reference-only | 本方案不实施 |

## 2. 目标与非目标

目标：

1. 优先使用 Token 最低、风险最低的界面完成 discovery、indexing、status checks 与 read-only diagnostics。
2. 使用 `skills2cli` 降低 skills context budget 压力，避免暴露完整 skill bodies 或 plugin description dumps。
3. 使用 `mcp2cli` 按风险拆分 MCP discovery、profiles 与 calls；敏感 MCP 调用默认 fail closed。
4. 使用 browser owner registry 区分 `isolated-session-managed`、`project-profile` 与 human-owned Chrome assets。
5. 使用 `codex-port` 管理 port registry / lease / `pending_bind` / `registry_revision`，避免 Codex、下游消费项目与 OpenCLI 端口冲突。
6. 使用 authorization receipt schema、update receipt、rollback pointer 与 evidence redaction，让用户级工具可审计、可回滚、可恢复。

非目标：hard-load 每个 MCP 或 skill；为了隐藏 Token 压力而粗暴禁用有用的 Browser/OpenCLI/WeCom 能力；在没有 receipt 的情况下修改 `C:\Users\lenovo\.codex`；在没有当前授权的情况下读取 cookies、tokens、raw browser data、WeCom message contents 或 human-owned Chrome assets。

## 3. 运行时架构

```text
Codex session -> repo-local policy/checkers/OpenSpec -> user-level helper facade
  -> skills2cli -> mcp2cli -> codex-port -> browser lane -> CLI-Anything -> wecom-cli
```

默认用户级路径包括 `C:\Users\lenovo\.codex\tools\skills2cli\`、`C:\Users\lenovo\.codex\tools\mcp2cli\`、`C:\Users\lenovo\.codex\tools\codex-port\`、`C:\Users\lenovo\.codex\tools\browser-automation\`、`C:\Users\lenovo\.codex\tools\wecom-cli\`，对应 runtime state 放在 `C:\Users\lenovo\.codex\state\` 下。

## 4. Codex 中的使用方式

1. 先根据 repo-local policy、checker 与文档判断当前是否需要 MCP、skills、browser automation 或 CLI harness 能力。
2. discovery 阶段优先读取 `skills2cli index/search/show` 或 `mcp2cli list/search/show` 的紧凑 JSON。
3. 真实 MCP call 或 browser write 之前必须先创建 authorization receipt。
4. 端口必须使用 `codex-port lease reserve --owner codex --purpose <tool> --port auto`。
5. OpenCLI 必须要求 `--port auto`、owner registry 与 receipt。
6. WeCom 默认优先 API/Webhook；GUI automation 必须有明确用户授权和全局 WXWork lease。

## 5. Repo-local source of truth

| 分类 | repo-local source | 用户级产物 |
| --- | --- | --- |
| policy | `docs_bilingual/governance/*`, `openspec/specs/*` | 生成的 launcher/helper 配置 |
| plan | `docs_bilingual/implementation_plans/*` | 无直接 runtime 产物 |
| checker | `tools/check_*.py`, `tools/ci/local_gate.ps1` | 可选 installed wrapper |
| helper source | repo-local tools/templates | `C:\Users\lenovo\.codex\tools\...` |
| receipt schema | docs + tests | redacted runtime JSON receipt |

## 6. 安装与更新证据契约

每一次用户级安装动作都必须生成 update receipt。没有 receipt 证据的 lane 只能是 `planned` 或 `implemented-local`，不能标为 `active`。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| tool name | 是 | lane id |
| installed version | 是 | commit、tag 或 package version |
| source URL | 是 | 不能包含 token |
| install path | 是 | runtime 安装目标 |
| wrapper path | 是 | 用户级 wrapper |
| state path | 是 | runtime state root |
| smoke test command | 是 | 可重复执行 |
| smoke test result | 是 | pass/fail + timestamp |
| updater command | 是 | 必须 pin-aware |
| rollback pointer | 是 | 上一版本或备份路径 |
| owner lane | 是 | `skills2cli`、`mcp2cli`、`browser`、`wecom-cli` 等 |

runtime receipts 不得包含 secrets、cookies、tokens、raw browser data、WeCom message contents 或完整 plugin description dumps。

## 7. Token 与风险优先级模型

| Priority | Surface | Token | Risk | Default action |
| --- | --- | --- | --- | --- |
| P0 | repo docs/checkers | low | low | 直接读取 |
| P1 | `skills2cli index/search` | low | low | compact summary |
| P1 | `mcp2cli list/search/show` | low | low | compact summary |
| P2 | browser tab inventory | medium | medium | read-only + owner evidence |
| P2 | OpenCLI discovery | medium | medium | on-demand + port lease |
| P3 | MCP call / browser JS / cookies | high | high | 需要 authorization receipt |
| P3 | `wecom-cli gui attach` | high | high | 默认 disabled |

## 8. 用户级端口治理

port registry 由 `codex-port` 管理，必须支持 `registry_revision`、原子写入、`pending_bind`、lease renewal 与 crash recovery。

| Owner | Range | 说明 |
| --- | --- | --- |
| Codex general helpers | `39000-39299` | 默认 Codex 用户级 helper 端口段 |
| Codex browser/OpenCLI | `39300-39499` | OpenCLI 必须使用 `--port auto` |
| Reserved local bridge | `39500-39999` | 预留给本地桥接 |
| Downstream consumer project range | `40000-40999` | 下游消费项目端口排在 Codex 后面 |

| Command | Purpose | Receipt |
| --- | --- | --- |
| `codex-port registry show --json` | 读取 registry | 不写入 |
| `codex-port lease reserve --owner <name> --port auto --json` | 自动分配 | lease receipt |
| `codex-port lease renew --lease-id <id> --json` | 续约 | updated lease |
| `codex-port lease release --lease-id <id> --json` | 释放 | completed receipt |
| `codex-port import-legacy --owner openclaw --json` | 导入旧端口 | migration receipt |
| `codex-port gc --dry-run --json` | stale scan | 不写入 |
| `codex-port gc --apply --json` | stale cleanup | evidence-gated write |

## 9. `skills2cli` lane contract

| Command | Default output | Risk gate |
| --- | --- | --- |
| `skills2cli index --json` | id、source layer、summary hash、availability | no full body |
| `skills2cli search <query> --json` | compact matches | no full body |
| `skills2cli show <id> --json` | bounded summary + path hint | `--full` 才能展开 |
| `skills2cli profile suggest --task <text> --json` | recommendation only | never direct apply |
| `skills2cli audit warnings --since <duration> --json` | 2% budget 与 skipped-loading summary | redacted paths |

## 10. `mcp2cli` lane contract

| Operation | Default | Required evidence |
| --- | --- | --- |
| list/search/show | compact JSON | profile registry |
| low-risk read-only call | allowed | allowlist |
| medium-risk call | gated | task scope + owner |
| sensitive call | fail closed | authorization receipt schema |
| write/mutate call | fail closed | current user approval + receipt |

## 11. Browser automation 与 Chrome/DevTools/CDP/OpenCLI lane

| Asset class | Profile | Bookmarks/extensions | Default permission | Cleanup |
| --- | --- | --- | --- | --- |
| `isolated-session-managed` | per-session temp profile | 无 | 最安全自动化 | 可自动清理 |
| `project-profile` | per-project managed profile | 可选 imported baseline | 项目自动化 | stale scan + dry-run |
| human-owned asset | 用户个人 Chrome | 真实 bookmarks/extensions/cookies | 人类拥有 | 永不自动清理 |

`chrome-devtools-mcp`、CDP Bridge 与 OpenCLI 默认 inspect/read-only first。navigate、click、type、JavaScript、cookies、downloads、uploads、account data、CRM、email、calendar、Drive、Slack、HubSpot 或 WeCom 数据都需要当前任务的一次性 authorization receipt。

## 12. CLI-Anything 与 `wecom-cli` lane

| Phase | Scope | Default |
| --- | --- | --- |
| API/Webhook MVP | webhook send、app-message send、secret redaction | planned |
| Inventory | `WXWork.exe` process list、window list | read-only |
| GUI attach | attach、click、type、read UI state | disabled |
| GUI write | send message / mutate state | one-task authorization + global WXWork lease |

## 13. reference-only 项与外部来源边界

| Reference | Use | Not allowed |
| --- | --- | --- |
| The Harness Problem | hash-anchored edit reliability | no unaudited import |
| `oh-my-pi` | Pi family / UX / sidecar reference-only | no install here |
| `ohmyopenagent` | future durable-team reference | no implementation here |
| `snow-cli` | CLI product-shape reference | no implementation here |

## 14. 敏感操作授权矩阵

authorization receipt schema 必须包含 action、target、scope、expiry、session 与 operator confirmation。

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
| planned | 只有方案 | docs 或 OpenSpec 已存在 |
| implemented-local | repo-local helper/checker 存在 | tests pass |
| installed-user-level | 用户级产物存在 | update receipt 存在 |
| smoke-tested | 用户级 smoke 通过 | smoke test result is pass |
| on-demand | 可按需启用 | receipt 和 rollback pointer 存在 |
| active | 默认可用或当前启用 | all readiness gates pass |
| disabled | 已禁用 | explicit reason exists |
| reference-only | 仅参考来源 | no runtime path |
| rollback-ready | 可快速回滚 | rollback pointer verified |

状态不变式：没有 wrapper path + smoke test result + rollback pointer 就不能标 `active`；没有 authorization receipt 时 sensitive actions 必须 fail closed；没有 port lease 时 OpenCLI/browser listener 不得启动。

## 16. Comet Management Record 模板

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
| Design | planning | architecture、lane boundaries、authorization model | design doc + delta spec | return-design |
| Build | executing | patch、tests、receipt schema、state updates | implementation plan + changed paths | return-build |
| Verify | monitoring/controlling | precommit、guard、local gate、local MR review | verification report | return-build / return-design |
| Archive | closing | stable spec sync 或 archive deferral | archive receipt / deferral | return-verify |

## 18. Monitoring return semantics

| Trigger | Decision | target_phase | rework_reason |
| --- | --- | --- | --- |
| scope 或 non-goals 不清晰 | return-open | open | value-gap |
| lane boundary 或 authorization model 不完整 | return-design | design | planning-gap |
| checker/test 未注册 | return-build | build | execution-gap |
| local gate / MR review 失败 | return-build | build | verification-gap |
| 完整 change 没有 archive 或 deferral | return-verify | verify | archive-gap |

## 19. Implementation slices

### OpenSpec slice delivery matrix

| Slice | Main artifacts | Minimum validation | Completion evidence |
| --- | --- | --- | --- |
| 1. Policy/checker baseline | token/risk checker、port registry、authorization receipt schema、update receipt schema、evidence redaction | checker tests + local gate | OpenSpec spec + checker output |
| 2. skills2cli MVP | index/search/show/audit/profile suggest | compact-output 与 privacy-redaction tests | wrapper smoke + receipt |
| 3. mcp2cli MVP | profile registry、list/search/show/call facade | sensitive-call fail-closed tests | blocked call evidence |
| 4. codex-port allocator | reserve/renew/release/import-legacy/gc | pending_bind 与 concurrent reserve tests | registry_revision + lease receipt |
| 5. Browser owner registry | isolated/project/human asset separation | owner exclusivity + cleanup dry-run tests | browser lease receipt |
| 6. chrome-devtools-mcp wrapper | isolated-session-managed 与 project-profile managed wrapper | wrapper smoke | install/update receipt |
| 7. CDP Bridge/OpenCLI enforcement | read/write split 与 on-demand adapter | cookie/JS/click/type/navigate fail-closed | authorization receipt evidence |
| 8. Codex harness reference boundary | oh-my-pi 与 The Harness Problem reference-only | docs boundary check | no runtime install evidence |
| 9. CLI-Anything boundary | install/update receipts 与 harness boundary | no-hard-load 与 rollback tests | install receipt |
| 10. wecom-cli API/Webhook | webhook send、app-message send、secret redaction | dry-run 与 secret-redaction tests | redacted send summary |
| 11. wecom-cli inventory | process/window read-only inventory | no-content-capture tests | read-only inventory summary |
| 12. wecom-cli GUI gate | global WXWork lease + one-task authorization | unauthorized fail + lease exclusivity | manual smoke marker |

### Slice completion rule

切片只有在 implementation、tests、CI registration、OpenSpec update、rollback evidence 与 completed receipt 都存在时才算完成。Documentation-only 或 research-only 切片可以是 `planned` 或 `implemented-local`，但不能是 `active`。

## 20. Definition of ready before implementation

- [ ] 对应 OpenSpec change 已存在，并说明 scope / non-goals。
- [ ] lane 已有 owner、owned files、receipt schema 与 rollback method。
- [ ] 如果涉及端口，已有 `codex-port` port registry lease。
- [ ] 如果涉及浏览器，已确认 asset class 与 owner registry。
- [ ] 如果涉及敏感数据，已有当前任务的一次性 authorization receipt。
- [ ] 如果涉及用户级安装，已定义 update receipt 与 rollback pointer。
- [ ] 新测试已注册到 `tools/ci/ci_test_manifest.json` 或 local gate。

## 21. 细粒度实施清单

- [x] 创建或复用一个小 OpenSpec change，说明本方案的 scope、non-goals 与 rollback boundary。
- [x] 增加 token/risk priority controls，避免高 Token 或高风险 surface 在没有证据时成为默认能力。
- [x] 建立用户级 port registry / lease allocator，让 Codex 端口段排在下游消费项目端口段前面。
- [x] 实现最小 `codex-port` reserve/renew/release/list/import-legacy/gc contract。
- [x] 覆盖 pending_bind、live-socket collision、stale/crash evidence 与 registry_revision。
- [x] 增加 authorization receipt schema，包含 action、target、scope、expiry、session 与 operator confirmation。
- [x] 增加 update receipt 字段：tool name、installed version、source URL、install path、wrapper path、state path、smoke test command、rollback pointer、owner lane。
- [x] 增加 sanitized-evidence 规则，禁止 secrets、cookies、tokens、raw browser data、message contents 与 plugin description dumps。
- [x] 实现 compact `skills2cli index --json` 输出。
- [x] 实现 compact `skills2cli search <query> --json` 输出。
- [x] 实现 `skills2cli show <skill-id> --json`，默认不输出完整 skill bodies。
- [x] 实现 `skills2cli profile suggest --task <text> --json`，仅 recommendation-only。
- [x] 实现 `skills2cli audit warnings --since <duration> --json`，覆盖 2% skills context budget 与 skipped-loading warnings。
- [x] 增加 skills2cli compact-output、privacy-redaction、profile-non-apply 与 warning-audit tests。
- [x] 实现 `mcp2cli` allowed profile registry。
- [x] 实现 compact `mcp2cli list/search/show`。
- [x] 实现 `mcp2cli call` sensitive-category fail-closed gate。
- [x] 增加 mcp2cli profile-registry、sensitive-call-blocking、compact-output 与 receipt-required tests。
- [x] 实现 browser owner registry，包含 owner class、project slug、session id、profile path 与 lease expiry。
- [x] 实现 `chrome-devtools-mcp` isolated-session-managed wrapper。
- [x] 实现 `chrome-devtools-mcp` project-profile wrapper。
- [x] 实现 browser stale scan 与 safe-cleanup dry-run。
- [x] 增加 browser-lane tests：tab-owner exclusivity、project-profile retention、human-owned protection 与 cleanup dry-run。
- [x] 加固 CDP Bridge read-only defaults，让 write actions 必须有 owner 与 authorization receipts。
- [ ] 保持 OpenCLI 为 on-demand adapter，并接入 browser owner registry 与 --port auto。
- [x] 增加 CDP Bridge fail-closed tests，覆盖 cookie、JavaScript、click、type、navigate。
- [ ] 增加剩余 OpenCLI fail-closed tests，覆盖 cookie、JavaScript、click、type、navigate。
- [x] 将直接 oh-my-pi install、updater、smoke、rollback 工作迁入 `pi_plugin_codex_user_level_sidecar_plan.*`。
- [x] 本方案仅保留 oh-my-pi / The Harness Problem 的 reference-only harness governance boundary。
- [ ] 以用户级 install receipts 安装 CLI-Anything / CLI Hub，且不 hard-load bulk skills。
- [ ] 使用 CLI-Anything 辅助设计 wecom-cli，同时保持 repo-local source 与 authorization gates。
- [ ] 实现 read-only `wecom-cli process list --json` 与 `window list --json` inventory。
- [ ] 实现 `wecom-cli webhook send` 与 `app-message send`，带 secret redaction 与 receipts。
- [ ] 实现 `wecom-cli gui attach`，带 global WXWork lease 与 one-task authorization gate，并保持默认 disabled。
- [ ] 增加 wecom-cli process/window read-only、secret-redaction、GUI-unauthorized-fail 与 lease-exclusivity tests。
- [ ] 将所有新 test 或 checker 注册到 `tools/ci/ci_test_manifest.json` 或 shared local-gate call chain。
- [x] 对每个完成的 OpenSpec change 运行 precommit update/archive gate、local gate 与 local MR review。
- [ ] 每次用户级安装后记录 rollback-ready receipts；没有 receipt 的 lane 不得标为 active。

## 22. 本地集成顺序

1. 在隔离 feature worktree 中创建 OpenSpec change。
2. 写 Design Doc、Implementation Plan、delta spec 与 management record。
3. 修改双语 plan pair，并保持英文 ASCII primary 与 zh-CN companion 同步。
4. 运行 document pair policy、baseline checker、implementation plan checker、precommit update/archive gate、OpenSpec guard 与 local gate。
5. 使用中文提交标题提交 feature branch，然后运行 local MR review。
6. 创建 rollback backup refs，并 fast-forward merge 到 local main。
7. 远端发布必须等待用户明确说出 remote push、GitLab/MR、merge 或 GitHub sync。

## 23. Readiness gates and acceptance criteria

| Gate | Criteria | Evidence |
| --- | --- | --- |
| Documentation readiness | bilingual docs synced、structure clear、markers complete | document pair policy |
| OpenSpec readiness | proposal/design/tasks/spec complete | `openspec validate --strict` |
| Runtime readiness | wrapper + state path + smoke + rollback | update receipt |
| Authorization readiness | action/target/scope/expiry/session/operator confirmation | authorization receipt schema |
| Port readiness | lease + owner + registry_revision | port registry receipt |
| Browser readiness | owner registry + asset class + cleanup policy | browser lease receipt |
| Active readiness | installed-user-level + smoke-tested + rollback-ready | completed receipt |

## 24. Verification plan

- `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json` - 验证治理基线 marker。
- `python tools/check_implementation_plan_rules.py --root . --json` - 验证实施方案规则。
- `python tools/check_document_pair_policy.py --root . --json` - 验证双语 companion 覆盖。
- `python tools/check_precommit_update_archive.py --root . --json` - 复核更新/归档就绪度。
- `python tools/run_openspec_guard.py --root . --json` - 运行仓库 OpenSpec guards。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1` - 运行共享本地 CI 门禁。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - 提交后执行本地 MR review。
- `openspec validate <change> --strict` - 校验 change schema 与 artifacts。
- `openspec status --change <change> --json` - 报告 artifacts 完成状态。

## 25. 回滚与清理

文档重构可以通过 revert feature commit 或 reset 到 backup ref 回滚。用户级安装回滚使用 update receipt 中的 rollback pointer。端口 lease 清理先运行 `codex-port gc --dry-run --json`。浏览器清理只作用于 managed profiles，永远不自动清理 human-owned Chrome。

## 26. 风险与默认决策

| Risk | Default decision | Mitigation |
| --- | --- | --- |
| skills context 2% budget 再次超限 | 不盲目禁用 | usage audit，再使用 `skills2cli` / profile helper |
| MCP surface 泄露敏感数据 | fail closed | authorization receipt schema |
| port conflict | 不直接 kill processes | port registry + pending_bind + live-socket evidence |
| browser asset confusion | 保护 human-owned assets | asset class + owner registry |
| OpenCLI high-risk write action | on-demand only | receipt + port lease + owner gate |
| WeCom GUI misoperation | 默认 disabled | global WXWork lease + one-task authorization |
| user-level cache 被更新覆盖 | receipt + source of truth | repo-local source + updater rollback |

## 27. 自检清单

- [ ] 本方案仍保留 `plan_readiness: execution-ready`。
- [ ] 本方案仍声明 `implementation_state:`，并且不把未完成 lane 标为 active。
- [ ] 文本包含 Token、Readiness gate、OpenSpec、skills2cli、mcp2cli、CDP Bridge 与 OpenCLI。
- [ ] 文本包含 port registry、codex-port、pending_bind、registry_revision、39000-39299 与 40000-40999。
- [ ] 文本包含 authorization receipt schema、operator confirmation、update receipt 与 rollback pointer。
- [ ] 文本包含 `chrome-devtools-mcp`、`oh-my-pi`、CLI-Anything、`wecom-cli`、active、on-demand、reference-only 与 disabled。

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
