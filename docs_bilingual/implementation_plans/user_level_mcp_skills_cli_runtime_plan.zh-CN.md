---
doc_id: user_level_mcp_skills_cli_runtime_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/user_level_mcp_skills_cli_runtime_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
supersedes:
  - docs_bilingual/implementation_plans/user_level_mcp_skills_discovery_facade_plan.zh-CN.md
---

# 用户级 MCP 与 Skills CLI Runtime 方案

> **给 agentic workers：** 使用 `superpowers:executing-plans`。本方案只拥有 `mcp2cli` 与 `skills2cli` 的真实 runtime 路径；并行 session 只能处理互不重叠的写入集合。

## 目标

把已有的紧凑型 `mcp2cli` / `skills2cli` discovery facade，从 repo-local helper、checker 和 test，提升为带有 R0-R5 证据门的用户级 runtime 方案。

## 架构

`mcp2cli` 采用上游 `knowsuchagency/mcp2cli` 的 runtime 模式。`skills2cli` 是对该 CLI/skill 模式的有意 fork/adaptation，用于本地 Codex skill discovery；它不是 native-subagent，也不是 MCP server。repo-local 源码仍以 `tools/skills2cli.py`、`tools/mcp2cli.py` 和 installer/checker helper 为权威；任何复制到用户级目录的内容都是安装产物。

## 技术栈

Python helper scripts、`uvx mcp2cli --help`、`uv tool install mcp2cli`、`npx skills add knowsuchagency/mcp2cli --skill mcp2cli`、`C:/Users/lenovo/.codex` 下的用户级 wrapper、JSON receipt、rollback backup、redaction helper、OpenSpec guard 与 local CI。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local
Status: R6 live-executed
Status: Stage E live-repaired
Status: Stage D R3/R4 live-executed
Stage: Stage E Codex-compatible `skills2cli` frontmatter 报告与修复 runtime 已在本地实现，并已对 installed user/plugin skills 执行 live execution。Stage D R3/R4 user-level install/update 与 bounded smoke evidence 也已针对 `mcp2cli` 和 `skills2cli` live-executed；R5 direct MCP 或 sensitive skill handoff 仍受门禁约束，未执行。
Owner session: `implement-stage-d-mcp-skills-cli-live-runtime-20260621` 拥有 Stage D R3/R4 live-runtime evidence package；`implement-skills2cli-codex-compat-runtime-20260620` 拥有 Stage E frontmatter repair package；`implement-multi-plan-family-r6-live-runtime-20260611` 仍是较早 strict parent-family R6 receipt coverage owner。
Stage D evidence: upstream `knowsuchagency/mcp2cli` source pin 为 `e3fa0f957155da6fe8dbb981441c41b2131feda0`；`uv tool install mcp2cli` 与 `uvx mcp2cli --help` 已成功执行；user-level `mcp2cli` 与 repo-derived `skills2cli` wrappers/support files 已刷新，rollback pointer 为 `state/mcp-skills-cli/backups/20260620T191937Z`；R3 receipts 为 `mcp2cli-20260620T191938Z.json` 与 `skills2cli-20260620T191938Z.json`；R4 smoke receipts 为 `mcp2cli-smoke-20260620T191950Z.json` 与 `skills2cli-smoke-20260620T191950Z.json`。
Stage E evidence: repo runtime adds strict Codex frontmatter parsing/compatibility reports, repair helper, tests, CI manifest registration, user-level `skills2cli` support-file install, live smoke receipts, and live frontmatter repair receipts. Post-repair audit reports `invalid_total=0`; rollback manifest and sanitized receipt are stored under user-level `state/skills2cli/frontmatter-repair/`.
R6 evidence: `.omx/r6-live-runtime/receipts/` contains accepted `live-executed` evidence for lane `user-level-mcp-skills-cli-runtime`, validated by `tools/check_r6_live_runtime_receipts.py --require-coverage` and `tools/check_multi_plan_family_r6_live_runtime.py --require-coverage`.
Runtime boundary: Stage D/E 只变更已批准的 user-level `mcp2cli` / `skills2cli` install artifacts、wrappers、receipts、rollback backups 和 Codex-compatible SKILL.md metadata。它们不修改 `config.toml`，不 apply profile，不禁用 plugin，不执行 browser/GUI/WXWork/harness/Spec Kit action，不执行 R5 direct MCP/sensitive handoff，也不发布 remote refs。
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-21
<!-- CURRENT_STATUS_END -->

## 参考源

| Runtime lane | Reference source | Runtime role | R3 之前必须固定的证据 |
| --- | --- | --- | --- |
| mcp2cli | https://github.com/knowsuchagency/mcp2cli | 上游 MCP/OpenAPI/GraphQL discovery 与 call CLI 模式。 | Source URL、immutable ref/version、install command、wrapper path hash、update command、rollback pointer、redaction status。 |
| skills2cli | https://github.com/knowsuchagency/mcp2cli 加 repo-local `tools/skills2cli.py` | 按上游低 token CLI/skill 模式 fork/adaptation，用于 Codex skill discovery。 | Repo source hash、upstream pattern ref、generated SKILL.md hash、wrapper path hash、update command、rollback pointer、redaction status。 |

## Runtime Promotion Ladder

| Runtime stage | Scope | Evidence gate |
| --- | --- | --- |
| R0 project-level preflight | 只检查上游 `mcp2cli`、repo-local `skills2cli` 源码、当前 `CODEX_HOME`、`uv`/`uvx`/`npx` 可用性；不安装、不复制。 | Source URL、source pin plan、tool availability、no install/run evidence、sanitized transcript。 |
| R1 project-level fake/dry-run runtime | 运行 deterministic installer `plan` 与 simulated apply/check fixtures。 | `apply_performed=false`、fake command results、无用户级状态突变、focused tests。 |
| R2 reusable project-level helper/guard | 维护 repo-owned installer/checker、receipt schema、rollback backup layout、redaction contract 与 CI/OpenSpec guard。 | Helper/checker tests、CI manifest registration、OpenSpec guard wiring、docs registry entry。 |
| R3 user-level install/update receipt | 在显式授权下 install/update upstream `mcp2cli`，复制 repo-derived `skills2cli` wrapper/skill，并写入 sanitized receipts。 | 2026-06-20 已针对 `mcp2cli` 与 `skills2cli` live completed；receipts 包含 source pin、wrapper hashes、updater commands、rollback pointer 和 redaction status。 |
| R4 user-level smoke runtime | 对 installed wrappers 运行 bounded `--help` / `--version` / safe discovery smoke。 | 2026-06-20 已 live completed；smoke receipts 覆盖 `mcp2cli --version` 与 `skills2cli --help`，并包含 bounded transcripts、timeout release、redaction 和 rollback readiness。 |
| R5 active-candidate / bounded live handoff | 仅在 risk profile 与 sensitive-call receipt 控制下运行 direct MCP 或 skill-discovery handoff。 | 本 package 未执行；需要单独 authorization receipt、target/action allowlist、risk profile、rollback pointer 和 redacted result summary。 |


## Stage E 最后审计与 Codex 兼容 Skills Runtime 冻结

Status: implemented-local-live-repaired
冻结时间：2026-06-20
实现时间：2026-06-20
授权边界：允许本地方案更新、本地实现、用户级 live runtime 修复、本地提交和本地 `main` 合入；远端发布仍关闭。

### 问题记录

`reference_files/10.md` 是本轮 Stage E 的最后审计输入。它记录 286 条 Codex skill 加载警示：

- 285 个位于 `C:/Users/lenovo/.codex/skills` 的用户级 skill，其 frontmatter `name` 超过 Codex 兼容的 64 字符限制。
- 1 个 Twilio plugin cache skill 的 `description` 超过 Codex 兼容的 1024 字符限制。

修复目标是让已安装 skill metadata 兼容 Codex。不得删除 skills、不得禁用 plugin family，也不得把低使用频率解释成能力无用。

### 冻结设计

`skills2cli` 继续采用上游 `mcp2cli` 的渐进披露形态：先发现紧凑 metadata，再按任务搜索，需要时检查单个 skill，只有显式请求时才返回脱敏全文。它不是 native subagent，不是 expert evidence，也不是 MCP server。

Stage E 新增 repo-owned 兼容修复面：

1. 严格验证 Codex frontmatter 兼容性：必须存在 frontmatter，必须有 `name` 和 `description`，`name <= 64`，`description <= 1024`。
2. 为超长用户级 skill name 生成稳定短名；短名保留可读前缀，必要时追加确定性 hash 避免冲突。
3. 缩短超长 description，但不修改 skill 正文。
4. 默认 dry-run；live 用户级修改必须显式 apply flag 加 operator confirmation。
5. apply 前备份每个被修改的 `SKILL.md`；apply 后写入 rollback manifest 和脱敏 receipt。
6. plugin-cache 修改仅作为最小 metadata 修复；未来 plugin 更新可能覆盖，receipt 必须单独标记。
7. 本包绝不修改 `C:/Users/lenovo/.codex/config.toml`，不 apply profile，不 hard-load 或 disable plugin。

### 执行切片

- [x] Slice A - 方案冻结：更新本方案双语文件，记录最后审计问题、修复边界和验证门禁；先本地提交并合入，再进入 live runtime。
- [x] Slice B - 仓库 runtime：增强 `tools/skills2cli.py`，新增或扩展兼容 fixer 与 checker tests，保持默认输出紧凑且脱敏。
- [x] Slice C - live runtime：必要时安装/更新 repo-derived `skills2cli` 用户级 artifacts，运行用户级 smoke，对 installed skills 执行 Codex compatibility fixer，并记录脱敏 receipts 与 rollback pointers。

### 验证门禁

Stage E 聚焦门禁：

```powershell
python test/skills2cli.test.py
python test/check_codex_skills_governance.test.py
python test/user_level_mcp_skills_cli_install.test.py
python tools/check_codex_skills_governance.py --root . --json
python tools/check_user_level_mcp_skills_cli_install.py --root . --json
python tools/check_precommit_update_archive.py --root . --json
python tools/run_openspec_guard.py --root .
```

Stage E live runtime 门禁：

```powershell
python tools/skills2cli.py index --json
python tools/skills2cli.py audit warnings --since 30d --json
python tools/install_user_level_mcp_skills_cli.py check --json --require-installed
python tools/install_user_level_mcp_skills_cli.py smoke --record --operator-confirmation --json
python tools/repair_codex_skill_frontmatter.py audit --json
python tools/repair_codex_skill_frontmatter.py apply --operator-confirmation --json
```

只有 post-apply audit 对修复范围报告零 `name_too_long`、零 `description_too_long`，或剩余项被明确列为 blocked 且保留 rollback pointer 时，live repair 才可验收。

## Real Runtime Implementation Gap（真实 runtime 缺口）

之前的 discovery facade implementation 不足以声明真实 runtime ready。截至 2026-06-20，R3/R4 部分已经 live-executed，剩余缺口仅为 R5：

- [x] Source-pin review：upstream `knowsuchagency/mcp2cli` 已固定在 `e3fa0f957155da6fe8dbb981441c41b2131feda0`。
- [x] R3 install/update：`tools/install_user_level_mcp_skills_cli.py apply --apply --operator-confirmation --run-external --skip-upstream-skill-install --upstream-ref e3fa0f957155da6fe8dbb981441c41b2131feda0 --json` 已刷新批准范围内的 user-level artifacts，并为两个工具写入带 rollback 的 receipts。
- [x] R4 smoke：`tools/install_user_level_mcp_skills_cli.py smoke --record --operator-confirmation --upstream-ref e3fa0f957155da6fe8dbb981441c41b2131feda0 --json` 已为 `mcp2cli --version` 与 `skills2cli --help` 写入 `smoke-tested` receipts。
- [x] Compatibility re-check：`tools/repair_codex_skill_frontmatter.py audit --codex-home C:/Users/lenovo/.codex --include-plugins --limit 5 --json` 报告 `invalid_total=0`。
- [ ] R5 direct MCP calls 与 sensitive skill-derived actions 仍被 risk profile、sensitive-call receipt、no-native-subagent-evidence wording、redaction 和 rollback 规则阻断。

本 package 有意未执行 upstream `npx skills add knowsuchagency/mcp2cli --skill mcp2cli` 路径，因为已批准 runtime surface 是 repo-owned wrapper/support-file install 加 receipts；执行第三方 skill installation 仍是单独显式决策。

## 文件归属

本方案拥有 `mcp2cli` / `skills2cli` runtime 方案文本、repo-local installer/checker/test 证据和后续用户级 install/smoke/live receipt 约束。它不拥有 Browser/CLI adapters、CLI-Anything/WXWork_CLI 或 Codex harnesses。

## Task Backlog（任务清单）

<!-- TASK_BACKLOG_START -->
- [x] 创建 discovery-facade 后继 runtime 方案。
- [x] 记录 `knowsuchagency/mcp2cli` 为上游 runtime source，并记录 `skills2cli` 为 upstream-pattern fork/adaptation。
- [x] 把现有 repo-local helper/checker/test 仅作为 R0-R2 证据保留。
- [x] 实现 repo-local R4 smoke command 支持：可在显式传入的 Codex home fixture 中为 `mcp2cli` 与 `skills2cli` 写入 `smoke-tested` receipts。
- [x] 为 repo-local checker 增加 `--require-smoke-tested`，使 R4 smoke receipt evidence 可被强制要求，并可通过通用 receipt governance guard 校验。
- [x] Stage E plan freeze：记录 `reference_files/10.md` 最后审计问题，并冻结 `skills2cli` 渐进披露与 Codex 兼容 metadata 修复设计。
- [x] Stage E repository runtime：实现严格 `skills2cli` 兼容报告、repair helper、tests 与 checkers。
- [x] Stage E live runtime：用 rollback manifest 修复 installed user-level skill metadata，并 smoke installed `skills2cli` surface。
- [x] Stage D source pin review：固定 upstream `knowsuchagency/mcp2cli` 为 `e3fa0f957155da6fe8dbb981441c41b2131feda0`。
- [x] Stage D R3 live runtime：刷新已批准的 user-level `mcp2cli` / `skills2cli` artifacts，并写入 rollback-backed install/update receipts。
- [x] Stage D R4 live runtime：运行 bounded wrapper smoke，并为两个工具写入 `smoke-tested` receipts。
- [ ] Stage D/R5 live handoff：direct MCP calls 与 sensitive skill-derived actions 保持阻断，直到存在单独 authorization receipt。
<!-- TASK_BACKLOG_END -->

## Stage D live-runtime status（真实 runtime 状态）

Stage D R3/R4 已在批准的 user-level wrapper/support-file surface 上 completed-live。R5 按设计保持 pending，不属于本 package：

- [x] Stage D R3 source pin：upstream `mcp2cli` ref 为 `e3fa0f957155da6fe8dbb981441c41b2131feda0`。
- [x] Stage D R3 install/update receipts：user-level `state/mcp-skills-cli/receipts/` 下存在 `mcp2cli-20260620T191938Z.json` 与 `skills2cli-20260620T191938Z.json`。
- [x] Stage D R3 rollback pointer：`state/mcp-skills-cli/backups/20260620T191937Z`。
- [x] Stage D R4 smoke receipts：`mcp2cli-smoke-20260620T191950Z.json` 与 `skills2cli-smoke-20260620T191950Z.json`。
- [x] Stage D R4 bounded smoke commands：`mcp2cli --version` 返回 `mcp2cli 3.2.0`；`skills2cli --help` 返回 compact discovery CLI help。
- [x] Stage D boundary：未修改 `config.toml`，未 apply profile，未禁用 plugin，未执行 browser/GUI/WXWork/harness/Spec Kit action，未进行 remote ref mutation。
- [ ] Stage D/R5 direct MCP call 或 skill action handoff 仍受单独 risk profile、sensitive-call authorization receipt、action scope、result redaction 与 rollback evidence 门禁约束。

## 验证门禁

- `python tools/check_user_level_mcp_skills_cli_install.py --root . --json`：验证 MCP/skills CLI install surfaces 与 helper plan output。
- `python tools/check_user_level_mcp_skills_cli_install.py --root . --require-user-level-installed --require-smoke-tested --json`：在声明 Stage E live-repaired evidence 时，验证真实用户级 wrapper、skill、support-file、install receipt 与 R4 smoke receipt 状态。
- `python tools/check_precommit_update_archive.py --root . --json`：提交前检查。
- `python tools/run_openspec_guard.py --root .`：OpenSpec 与治理 guard。
- `tools/ci/local_gate.ps1` 与 `tools/ci/local_mr_review.ps1`：本地集成前的共享 gate。

## 验收标准

- 本方案与英文主文件保持双语同步，正文为中文说明，技术 token 和 checker marker 保持原样。
- R0-R2 carry-forward evidence 仅覆盖 repo-local helper/checker/test；除非同时存在 user-level receipts，否则不能声明 installed/smoked/live。
- Stage E 证据只覆盖 Codex-compatible `skills2cli` frontmatter reporting、用户级 `skills2cli` support-file install/smoke 和 installed-skill metadata repair。
- Stage D R3/R4 只有在上述 user-level install/update 与 smoke receipts、rollback pointer、redacted transcripts 均存在时才算完成；本次已满足这些证据条件。
- R5 runtime claim 仍必须有单独 active-candidate authorization、sanitized receipts 与 rollback evidence。
- 远端发布保持关闭，除非当前用户消息明确授权 remote publication。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-20 Stage D R3/R4 live runtime：branch `implement-stage-d-mcp-skills-cli-live-runtime-20260621` 将 upstream `knowsuchagency/mcp2cli` 固定在 `e3fa0f957155da6fe8dbb981441c41b2131feda0`，执行真实 `uv tool install mcp2cli` 与 `uvx mcp2cli --help`，用 rollback pointer `state/mcp-skills-cli/backups/20260620T191937Z` 刷新批准范围内的 user-level wrappers/support files，写入 R3 receipts `mcp2cli-20260620T191938Z.json` 与 `skills2cli-20260620T191938Z.json`，写入 R4 receipts `mcp2cli-smoke-20260620T191950Z.json` 与 `skills2cli-smoke-20260620T191950Z.json`，并以 `invalid_total=0` 验证 installed skill frontmatter。本 evidence 不执行 R5 direct MCP/sensitive handoff，也不授权 remote publication。
- 2026-06-20 Stage E Codex-compatible skills runtime：branch `implement-skills2cli-codex-compat-runtime-20260620` 新增 `tools/codex_skill_frontmatter.py`、`tools/repair_codex_skill_frontmatter.py`、严格 `skills2cli`/inventory 兼容报告、governance checker fail-closed 边界、installer support-file 同步和 focused tests。Live runtime 已安装/检查 repo-derived `skills2cli` user-level artifacts，运行 smoke receipt，并对 installed skills 执行 frontmatter repair；post-apply audit 为 `invalid_total=0`，rollback manifest 与 receipt 保存在 user-level `state/skills2cli/frontmatter-repair/`。本 evidence 不代表 Stage D upstream `mcp2cli` pin/install 已完成，也不授权 remote publication。
- 2026-06-07 R5 active-candidate gate：branch `implement-r5-runtime-governance-batch-20260607` 为 MCP/skills CLI runtime handoff 增加共享 active-candidate receipt validation。证据必须包含 authorization receipt、owner lease、target/action allowlist、timeout release、redacted transcript、rollback pointer/readiness、cleanup evidence，并带有按 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` 记录的 authority decision 以及 `remote_publication_mutated=false`。聚焦验证：`python test\check_r5_active_candidate_receipts.test.py` 以及 OpenSpec verification report 中列出的 lane-specific focused tests。本 package 不执行真实 user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action，也不执行 remote mutation。
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 新增本 runtime 后继方案，记录 `mcp2cli` 与 `skills2cli` 的 R3/R4/R5 缺口；未安装、未 smoke、未 live-run。
- 2026-06-06 R4 repo-local smoke receipt support：branch `implement-mcp-skills-cli-runtime-r4-20260606` 新增 `install_user_level_mcp_skills_cli.py smoke --record --operator-confirmation`、`check_user_level_mcp_skills_cli_install.py --require-smoke-tested`，并用 focused tests 验证临时 Codex-home fixtures 生成的 R4 `smoke-tested` receipts 可通过 `user_level_receipt_governance.py smoke-check`。
<!-- EVIDENCE_INDEX_END -->
