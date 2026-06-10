---
doc_id: user_level_cloakbrowser_academic_research_runtime_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/user_level_cloakbrowser_academic_research_runtime_plan.md
parent_plan: docs_bilingual/implementation_plans/user_level_mcp_skills_cli_runtime_plan.zh-CN.md
---

# 用户级 CloakBrowser 与 Academic Research Runtime 方案

> **给 agentic workers:** 使用 `superpowers:executing-plans`；涉及 checker 变更时使用 `superpowers:test-driven-development`。本方案只负责 CloakBrowser、CloakBrowser-Manager 与 `academic-research-suite` Codex skill 的用户级安装/运行证据，不接管 WXWork、CLI-Anything、既有 Browser/CLI adapter lane 或远端发布。

## 目标

以 receipt-backed、hash-only 证据安装并验证三个用户级能力表面：

- 来自 `https://github.com/CloakHQ/CloakBrowser` 的 CloakBrowser wrapper runtime。
- 来自 `https://github.com/CloakHQ/CloakBrowser-Manager` 的 CloakBrowser-Manager source/runtime 边界。
- 来自 `https://github.com/Imbad0202/academic-research-skills-codex` 的 Codex Academic Research Skills，按单一 `academic-research-suite` skill 安装。

## 架构

先做 repo-local governance：本仓库记录方案、checker、测试、CI 注册和 OpenSpec guard wiring。用户级安装只是 install artifact，必须落在明确的用户级目录，例如 `C:\Users\lenovo\.codex` 或隔离 tool/cache root。Runtime receipts 必须 hash-only，省略 raw paths 与 raw command transcripts，以 hash 记录 rollback pointers，并记录 remote publication remains unauthorized。

治理优先级固定为 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。native Codex files are not modified，不修改 Codex direct MCP config，生成 wrapper 不得覆盖 native Codex launcher surfaces。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: planned-local
Stage: user-level CloakBrowser / CloakBrowser-Manager / academic-research-suite runtime 的 implementation plan 与 checker package。
Current gate: 先提交本方案/checker/test package，运行 focused validation 和 local gates，合入本地 `main`，再在 fresh branch 执行真实用户级 live runtime install/smoke package。
Docker boundary: Docker is not installed by this plan。CloakBrowser-Manager live GUI/container start 在 Docker 缺失时记录为 blocked dependency receipt。
Runtime boundary: native Codex files are not modified，receipts 不保存 raw paths，remote publication remains unauthorized。
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。
Last updated: 2026-06-10
<!-- CURRENT_STATUS_END -->

## Source References

| 能力 | 来源 | Pin/version target | 用户级动作 |
| --- | --- | --- | --- |
| CloakBrowser Python | `https://github.com/CloakHQ/CloakBrowser` / PyPI `cloakbrowser` | `cloakbrowser==0.3.31` | 安装到隔离用户级 Python venv，运行 import/help/version smoke，记录 R6 live-executed receipt |
| CloakBrowser npm | `https://github.com/CloakHQ/CloakBrowser` / npm `cloakbrowser` | `cloakbrowser@0.3.31` | 可选 user-level npm/local-prefix 安装，运行 package/version/import smoke，记录 R6 live-executed 或 blocked receipt |
| CloakBrowser-Manager | `https://github.com/CloakHQ/CloakBrowser-Manager` | 执行期解析的 source `main` commit hash | clone/copy source metadata 与 config boundary；Docker is not installed by this plan；Docker 缺失的 runtime start 记录 blocked receipt |
| Academic Research Skills Codex | `https://github.com/Imbad0202/academic-research-skills-codex` | `0.1.11`，路径 `skills/academic-research-suite` | 安装到 `C:\Users\lenovo\.codex\skills\academic-research-suite`；验证只出现一个 ARS entry |

## Runtime Stages

| 阶段 | 允许动作 | 证据 |
| --- | --- | --- |
| R6 live-ready | 解析工具、版本、路径和 rollback targets，但不执行 install/start。 | checker output、planned command hashes、authorization boundary |
| R6 live-executed | 在依赖存在时执行用户级 install/smoke。 | 每项能力一份 JSON receipt，包含 source URL/ref、version、hash-only install/wrapper/state/rollback 字段、smoke result、redaction status |
| R6 blocked | 对 Docker 缺失等依赖记录诚实 blocked evidence。 | blocker name、未执行动作、rollback/cleanup 不需要或已准备、无 raw paths |

## Implementation Tasks

<!-- TASK_BACKLOG_START -->
- [x] 新建 dedicated checker `tools/check_user_level_cloakbrowser_academic_runtime.py`，验证方案表面、guard/CI/registry wiring 与可选 R6 receipts。
- [x] 新增 `test/check_user_level_cloakbrowser_academic_runtime.test.py`，覆盖 plan registration 与 hash-only receipt validation 的 red/green 行为。
- [x] 在 `tools/run_openspec_guard.py`、`tools/safety_rule_script_backing_registry.json`、`tools/ci/ci_test_manifest.json` 和 `docs_bilingual/docs_registry.yaml` 注册 checker。
- [ ] 执行真实用户级 CloakBrowser Python install 与 smoke；记录 `cloakbrowser-python` R6 live-executed receipt。
- [ ] 执行真实用户级 CloakBrowser npm install 或明确 npm blocked receipt；记录 `cloakbrowser-npm` R6 receipt。
- [ ] 解析 CloakBrowser-Manager source，并在未显式提供 Docker 时记录 Docker-missing blocked receipt。
- [ ] 使用 Codex skill installer 安装 `academic-research-suite`，记录 R6 live-executed receipt。
<!-- TASK_BACKLOG_END -->

## Validation Gates

- `python test\check_user_level_cloakbrowser_academic_runtime.test.py` - runs focused checker unit tests.
- `python tools\check_user_level_cloakbrowser_academic_runtime.py --root . --json` - verifies plan, guard, CI, and registry wiring.
- `python tools\check_user_level_cloakbrowser_academic_runtime.py --root . --receipt-dir <receipt-dir> --require-live --json` - verifies live install receipts after execution.
- `python tools\check_precommit_update_archive.py --root . --json` - verifies pre-commit update and archive readiness.
- `python tools\run_openspec_guard.py --root . --json` - runs the repository OpenSpec guard suite.
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1` - runs the mirrored local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1` - runs local MR review before integration.

## Acceptance Criteria

- 新方案在任何 live install 前已经 registry/checker-backed。
- Receipts 使用 hash-only，不包含 raw paths、raw command transcripts、secrets、cookies 或 browser data。
- 依赖与授权存在时，CloakBrowser Python 与 academic-research-suite 达到 live-executed。
- CloakBrowser-Manager 不安装 Docker；Docker 缺失记录为 blocked runtime dependency，不能静默声称成功。
- native Codex files are not modified，用户级 install artifacts 可回滚，remote publication remains unauthorized。

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-10 plan/checker package：创建 user-level CloakBrowser / CloakBrowser-Manager / academic-research-suite runtime plan、checker、tests、guard registration 与 receipt contract。本 plan package 不执行 user-level install/start/smoke。
<!-- EVIDENCE_INDEX_END -->
