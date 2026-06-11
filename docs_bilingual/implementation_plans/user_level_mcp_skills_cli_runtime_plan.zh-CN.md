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
Stage: R6 live-runtime receipt coverage package for `user_level_mcp_skills_cli_runtime_plan`.
Owner session: `implement-multi-plan-family-r6-live-runtime-20260611` updates the strict parent-family checker; existing accepted receipts remain the live runtime evidence source.
R6 evidence: `.omx/r6-live-runtime/receipts/` contains accepted `live-executed` evidence for lane `user-level-mcp-skills-cli-runtime`, validated by `tools/check_r6_live_runtime_receipts.py --require-coverage` and `tools/check_multi_plan_family_r6_live_runtime.py --require-coverage`.
Runtime boundary: this status update performs no browser/GUI action, no WXWork message send, no harness job, no Spec Kit apply, no user-level config mutation, and no remote publication; it reconciles the plan with accepted hash-only/redacted R6 receipts.
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-11
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
| R3 user-level install/update receipt | 明确授权后安装/更新上游 `mcp2cli`，并复制 repo-derived `skills2cli` wrapper/skill，写入 sanitized receipts。 | 每个工具的 `installed-user-level` receipt、source/package/ref pin、wrapper path hash、updater command、rollback pointer、redaction status。 |
| R4 user-level smoke runtime | 对已安装 wrapper 运行受限的 `--help` / `--version` / safe discovery smoke。 | `smoke-tested` receipt、bounded command transcript、timeout release、redaction、rollback readiness。 |
| R5 active-candidate / bounded live handoff | 仅在 risk profile 与 sensitive-call receipt 控制下运行 direct MCP 或 skill-discovery handoff。 | `active-candidate` receipt、risk profile、必要的 sensitive-call authorization、action scope、rollback pointer、redacted result summary。 |

## Real Runtime Implementation Gap（真实 runtime 缺口）

旧 discovery facade 不能证明真实 runtime ready。后续必须完成：

- 只有在明确授权并完成 source pin review 后，才执行 `tools/install_user_level_mcp_skills_cli.py apply --apply --operator-confirmation ...`。
- 分别为 `mcp2cli` 与 `skills2cli` 捕获 install/update receipts，包含 wrapper hashes、source hashes、updater commands、rollback backup paths 与 redaction status。
- 使用受限 `mcp2cli --help` 或 `--version`，以及 `skills2cli --help` / safe discovery command，smoke 已安装 wrapper。
- direct MCP call 与 skill-derived sensitive action 必须受 risk profile、sensitive-call receipt、no-native-subagent-evidence wording、redaction 与 rollback 规则约束。

## 文件归属

本方案拥有 `mcp2cli` / `skills2cli` runtime 方案文本、repo-local installer/checker/test 证据和后续用户级 install/smoke/live receipt 约束。它不拥有 Browser/CLI adapters、CLI-Anything/WXWork_CLI 或 Codex harnesses。

## Task Backlog（任务清单）

<!-- TASK_BACKLOG_START -->
- [x] 创建 discovery-facade 后继 runtime 方案。
- [x] 记录 `knowsuchagency/mcp2cli` 为上游 runtime source，并记录 `skills2cli` 为 upstream-pattern fork/adaptation。
- [x] 把现有 repo-local helper/checker/test 仅作为 R0-R2 证据保留。
- [x] 实现 repo-local R4 smoke command 支持：可在显式传入的 Codex home fixture 中为 `mcp2cli` 与 `skills2cli` 写入 `smoke-tested` receipts。
- [x] 为 repo-local checker 增加 `--require-smoke-tested`，使 R4 smoke receipt evidence 可被强制要求，并可通过通用 receipt governance guard 校验。
<!-- TASK_BACKLOG_END -->

## Stage D pending runtime work（待实施真实 runtime）

- Stage D real runtime：固定上游 `mcp2cli` version/ref，并以 R3 receipt、wrapper hash、updater command、rollback pointer 与 redaction evidence 完成用户级 install/update。
- Stage D real runtime：安装/更新 repo-derived `skills2cli` wrapper 与 SKILL.md，并写入 R3 receipt、source hash、updater command、rollback pointer 与 redaction evidence。
- Stage D real runtime：为两个 wrapper 运行受限 R4 help/version/safe-discovery smoke，并记录 `smoke-tested` receipts。
- Stage D real runtime：任何 R5 direct MCP call 或 skill action handoff 都必须经过 risk profile、sensitive-call authorization receipt、action scope、result redaction 与 rollback evidence。

## 验证门禁

- `python tools/check_user_level_mcp_skills_cli_install.py --root . --json`：验证 MCP/skills CLI install surfaces 与 helper plan output。
- `python tools/check_precommit_update_archive.py --root . --json`：提交前检查。
- `python tools/run_openspec_guard.py --root .`：OpenSpec 与治理 guard。
- `tools/ci/local_gate.ps1` 与 `tools/ci/local_mr_review.ps1`：本地集成前的共享 gate。

## 验收标准

- 本方案与英文主文件保持双语同步，正文为中文说明，技术 token 和 checker marker 保持原样。
- R0-R2 仅能声明 repo-local helper/checker/test 完成，不声明用户级 installed/smoked/live。
- R3/R4/R5 必须分别有 install/update、smoke 与 live handoff receipt 才能提升状态。
- 远端发布保持关闭，除非当前用户消息明确授权 remote publication。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-07 R5 active-candidate gate：branch `implement-r5-runtime-governance-batch-20260607` 为 MCP/skills CLI runtime handoff 增加共享 active-candidate receipt validation。证据必须包含 authorization receipt、owner lease、target/action allowlist、timeout release、redacted transcript、rollback pointer/readiness、cleanup evidence，并带有按 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` 记录的 authority decision 以及 `remote_publication_mutated=false`。聚焦验证：`python test\check_r5_active_candidate_receipts.test.py` 以及 OpenSpec verification report 中列出的 lane-specific focused tests。本 package 不执行真实 user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action，也不执行 remote mutation。
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 新增本 runtime 后继方案，记录 `mcp2cli` 与 `skills2cli` 的 R3/R4/R5 缺口；未安装、未 smoke、未 live-run。
- 2026-06-06 R4 repo-local smoke receipt support：branch `implement-mcp-skills-cli-runtime-r4-20260606` 新增 `install_user_level_mcp_skills_cli.py smoke --record --operator-confirmation`、`check_user_level_mcp_skills_cli_install.py --require-smoke-tested`，并用 focused tests 验证临时 Codex-home fixtures 生成的 R4 `smoke-tested` receipts 可通过 `user_level_receipt_governance.py smoke-check`。
<!-- EVIDENCE_INDEX_END -->
