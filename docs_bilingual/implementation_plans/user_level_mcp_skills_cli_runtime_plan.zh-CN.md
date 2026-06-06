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
Status: active；本方案是已删除/被取代的 `user_level_mcp_skills_discovery_facade_plan` 的 runtime 后继。repo-local helper、checker 和 test 现在已经具备 R4 smoke receipt 支持，但本地验证仍不执行真实默认用户级 runtime promotion。
Runtime boundary：本包在测试和本地 gate 中不修改真实默认用户级 `CODEX_HOME`。本包的 R4 证据是 fixture-backed：`tools/install_user_level_mcp_skills_cli.py smoke --record --operator-confirmation --codex-home <temp-home>` 只对显式传入、且已经具备 R3-style update receipts 与 wrappers 的 Codex home 执行受限只读 wrapper smoke，然后分别为 `mcp2cli` 与 `skills2cli` 写入 `smoke-tested` receipts。
R4 helper evidence：`tools/check_user_level_mcp_skills_cli_install.py --require-smoke-tested --codex-home <home>` 现在可以强制要求有效 R4 smoke receipts；每份 receipt 都可通过 `tools/user_level_receipt_governance.py smoke-check` 校验。
Runtime gap：真实 live 用户级 R3/R4 仍需要显式 live 授权、source pin review、真实用户级 install/update receipts、真实受限 smoke receipts、rollback evidence 与 redaction evidence。R5 direct MCP call 或 skill action handoff 仍必须受 risk profile、sensitive-call receipt、action scope、result redaction 与 rollback evidence 约束。
Carry-forward evidence：现有证据面包括 `tools/mcp2cli.py`、`tools/skills2cli.py`、`tools/install_user_level_mcp_skills_cli.py`、`tools/check_user_level_mcp_skills_cli_install.py`、`tools/user_level_receipt_governance.py`、`test/mcp2cli.test.py`、`test/skills2cli.test.py` 与 `test/user_level_mcp_skills_cli_install.test.py`。
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
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 新增本 runtime 后继方案，记录 `mcp2cli` 与 `skills2cli` 的 R3/R4/R5 缺口；未安装、未 smoke、未 live-run。
- 2026-06-06 R4 repo-local smoke receipt support：branch `implement-mcp-skills-cli-runtime-r4-20260606` 新增 `install_user_level_mcp_skills_cli.py smoke --record --operator-confirmation`、`check_user_level_mcp_skills_cli_install.py --require-smoke-tested`，并用 focused tests 验证临时 Codex-home fixtures 生成的 R4 `smoke-tested` receipts 可通过 `user_level_receipt_governance.py smoke-check`。
<!-- EVIDENCE_INDEX_END -->
