---
doc_id: user_level_mcp_skills_discovery_facade_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/user_level_mcp_skills_discovery_facade_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
source_plan: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
---

# 用户级 MCP 与 Skills Discovery Facade 实施方案

> **For agentic workers:** REQUIRED SUB-SKILL: 使用 `superpowers:executing-plans`；只有当实现切片写集互斥时才使用 `superpowers:subagent-driven-development`。本子方案从旧 MCP/skills/browser/CLI 来源方案拆出，必须通过常规 claim、hotspot 与 local-main retire 门禁执行。

## 目标

提供 compact `skills2cli` 与 `mcp2cli` discovery 契约，降低启动上下文并让 sensitive call 保持风险门控。既有 repo-local MVP 仍是 deterministic fail-closed facade；下一阶段实现还必须按 upstream `knowsuchagency/mcp2cli` 安装用户级 `mcp2cli` runtime，并 fork/adapt 一个 upstream-style 的用户级 `skills2cli` CLI/skill surface。

## 来源提取

从 `user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md` 的 Slice 1 与 Slice 2 提取。

本文件是 `multi_plan_parallel_session_orchestration_plan.zh-CN.md` 下拆分出的子 implementation plan。旧来源方案保留为历史索引和 baseline checker 索引；它不是本 lane 的单一执行包。

## 阶段位置

- 父方案阶段：Phase 4 自动路由与稳定会话表面。
- 执行模型：视情况多阶段推进；只有写集互斥或 hotspot 已明确串行化时，才允许多会话并行。
- 远端发布：本方案不授权远端发布。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: Stage B 已 implemented-local，并且已在用户级 Codex home 中完成 upstream-backed `mcp2cli` 安装证据；远端发布仍未授权。
Current gate: 验证、提交并将本 Stage B implementation branch 合入本地 `main`，随后停在 remote-publication approval gate。
Source relation: 从 `user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md` 提取；旧来源方案继续作为 baseline/history 索引，不作为直接子执行包。
Runtime boundary: 既有 repo-local `tools/skills2cli.py` 与 `tools/mcp2cli.py` 继续保留为 deterministic compact/fail-closed discovery facades。Stage B 已新增用户级 runtime artifacts，但没有替代这些 repo-local tests 或 safety contracts。
Upstream reference: 使用 `https://github.com/knowsuchagency/mcp2cli` 作为安装用户级 `mcp2cli` 的权威来源：`uvx mcp2cli --help` 用于 direct smoke，`uv tool install mcp2cli` 用于 user-level install，`npx skills add knowsuchagency/mcp2cli --skill mcp2cli` 用于 upstream agent-skill surface。其 README 覆盖 `--mcp`、`--mcp-stdio`、`--spec`、`--graphql`、`bake`、`--compact`、`--toon`、OAuth、env/file secret indirection、cache directories 与 generated wrapper behavior。
Implementation result: upstream `mcp2cli` 已按 upstream commit `3b7440196d620df29c13d3cfb8ad36ad4792e69f` 安装为版本 `3.2.0`，并包装到 `C:\Users\lenovo\.codex\bin\mcp2cli.cmd`；安装和 wrapper smoke 使用隔离的 `UV_CACHE_DIR=C:\Users\lenovo\.codex\state\mcp-skills-cli\uv-cache`。upstream skill 安装在 `~\.agents\skills\mcp2cli`；fork/adapt 后的 `skills2cli` wrapper 和 skill 位于 `C:\Users\lenovo\.codex\bin\skills2cli.cmd`、`C:\Users\lenovo\.codex\tools\skills2cli` 与 `~\.codex\skills\skills2cli`。最新有效 update receipts 为 `C:\Users\lenovo\.codex\state\mcp-skills-cli\receipts\mcp2cli-20260604T000705Z.json` 与 `C:\Users\lenovo\.codex\state\mcp-skills-cli\receipts\skills2cli-20260604T000705Z.json`。Skill installation 仍只是 workflow context，不是 native-subagent evidence。
<!-- CURRENT_STATUS_END -->

## 文件归属

后续实现可触及 skills facade helper、MCP facade helper、risk-profile fixture、测试、policy 文档、用户级 installer/wrapper generation scripts 与 installation receipt helpers；默认不得加载完整 skill bodies，不得在 process arguments 中暴露 secrets，并且必须让 live MCP/API calls 继续受 receipt evidence 门控。

后续实现 claim 必须在编辑前列出精确文件归属。worker 不是独自在代码库中工作，不得 revert 其他 worker 的更改，并且必须报告 changed paths。

## 并行会话契约

默认 discovery 为只读，因此可与 receipt 和 port 方案并行；任何真实 MCP call 行为都依赖 Phase 1 receipt/redaction 契约。

共享 hotspot 仍通过父方案、implementation-plan claim lock、ROB entry 与 local-main retire lock 串行化。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] 定义 compact `skills2cli` index、search、show、audit 与 profile-suggest JSON 输出。
- [x] 默认输出不得包含完整 skill bodies；warning audit 必须摘要化并 redacted。
- [x] 定义 compact `mcp2cli` list、search、show 与 risk profile 输出。
- [x] 缺少 authorization receipt evidence 的 sensitive `mcp2cli call` 必须 fail closed。
- [x] 保持 Codex direct MCP entries 直连，不把 MCP Router 当作 Codex 默认 bridge。
- [x] 记录 routing evidence，避免把 skills/profile 误标为 native subagents。
- [x] 运行本 child lane 的聚焦验证。
- [x] 产生实现证据后更新父方案 evidence index 与 Phase 7 集成方案。
- [x] Stage A: 记录 upstream-backed user-level runtime 方案，并以 docs-only governance package 合入本地 `main`。
- [x] Stage B: 在可用时使用 `uv tool install mcp2cli` 将 upstream `knowsuchagency/mcp2cli` install/wrap 为用户级 `mcp2cli`；以 `uvx mcp2cli --help` 作为非变更 preflight，并为 previous wrapper/tool state 记录 rollback pointer。
- [x] Stage B: 只通过 receipt-backed user-level update path 执行 `npx skills add knowsuchagency/mcp2cli --skill mcp2cli --global --agent codex --yes --copy` 安装 upstream `mcp2cli` skill；不得把 skill installation 当作 native-subagent evidence。
- [x] Stage B: 将 upstream `mcp2cli` skill/CLI pattern fork/adapt 成用户级 `skills2cli` wrapper/skill，委托给已安装的 skills CLI 或 repo-local compact facade，并保留 compact JSON、redaction、profile-suggest preview-only 行为，以及默认不输出 full skill bodies。
- [x] Stage B: 新增或更新 tests/checkers，覆盖 wrapper path existence、command smoke tests、rollback/update receipts、upstream version/help evidence，以及缺少 authorization receipts 时 sensitive `mcp2cli` calls fail-closed。
- [x] Stage B: 记录 upstream runtime `mcp2cli`、repo-local fail-closed facade `tools/mcp2cli.py`、user-level `skills2cli` 与 native Codex subagents 之间的边界。
<!-- TASK_BACKLOG_END -->

## 验证门禁

- MCP baseline checker: `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json` verifies source-plan baseline markers and guard registration.
- Agent/skill/profile boundary checker: `python tools/check_agent_skill_profile_surface_boundaries.py --root . --json` verifies skills are not mislabeled as native agents.
- MCP scope checker: `python tools/check_mcp_router_scope_policy.py --root . --json` verifies Codex direct MCP boundaries and Router isolation.
- Whitespace check: `git diff --check` verifies the patch has no whitespace errors.
- Stage B upstream install preflight: `uvx mcp2cli --help` must succeed before mutating user-level install state; executing `uv tool install mcp2cli` must record version/source evidence.
- Stage B skill install/update path: `npx skills add knowsuchagency/mcp2cli --skill mcp2cli --global --agent codex --yes --copy` must be receipt-backed and must not count as native-subagent evidence.
- Stage B wrapper smoke: `mcp2cli --version` or `mcp2cli --help`, `skills2cli --help`, compact discovery JSON, and sensitive-call fail-closed checks must pass after installation.

## 验收标准

- 本 lane 按阶段边界保持 discovery、receipt、lease 或 adapter 分离。
- 没有所需 receipt、owner、rollback 与 redaction evidence 时，不启用 sensitive runtime action。
- 任何 checker、test 或 OpenSpec 变更必须在 local main integration 前注册进共享 guard。
- local main integration 保持串行，远端发布仍等待显式授权。
- 用户级 `mcp2cli` 必须来源于 upstream `knowsuchagency/mcp2cli`；repo-local facade 继续作为 deterministic safe fallback 与 test harness。
- 用户级 `skills2cli` 必须是 upstream `mcp2cli` skill/CLI pattern 的 deliberate fork/adaptation，不得成为误导性的 native subagent alias，也不得成为 full skill-body injection 机制。
- installation、update、rollback 与 smoke-test receipts 必须记录 wrapper path、install path、source URL/version、state/cache paths 与 previous-state rollback pointer。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-01：由 MCP/skills/browser/CLI decomposition package 创建子方案；实现证据等待后续 claim。
- 2026-06-01：分支 `implement-mcp-skills-discovery-facade-20260601` 实现 compact discovery facade lane。证据包括 `tools/skills2cli.py`、`tools/mcp2cli.py`、`tools/mcp2cli_allowed_profiles.json`、聚焦测试 `test/skills2cli.test.py` 与 `test/mcp2cli.test.py`、MCP risk-profile 输出和 skill/profile routing evidence 的 RED/GREEN 覆盖；未执行 live MCP/browser/user-level runtime mutation。
- 2026-06-03：Stage A 方案刷新要求单独的 Stage B 实现，以将 upstream `knowsuchagency/mcp2cli` 安装为用户级 `mcp2cli`，并 fork/adapt upstream-style `skills2cli`；Stage A 仅为 docs-only，不安装工具、不修改 user-level runtime state。
- 2026-06-04 UTC：分支 `implement-upstream-mcp2cli-skills2cli-20260603` 实现 Stage B。仓库证据包括 `tools/install_user_level_mcp_skills_cli.py`、`tools/check_user_level_mcp_skills_cli_install.py`、`test/user_level_mcp_skills_cli_install.test.py`、CI manifest registration 与 OpenSpec guard registration。用户级证据使用 upstream commit `3b7440196d620df29c13d3cfb8ad36ad4792e69f`、`mcp2cli 3.2.0`、隔离 `UV_CACHE_DIR=C:\Users\lenovo\.codex\state\mcp-skills-cli\uv-cache`、receipts `C:\Users\lenovo\.codex\state\mcp-skills-cli\receipts\mcp2cli-20260604T000705Z.json` 和 `C:\Users\lenovo\.codex\state\mcp-skills-cli\receipts\skills2cli-20260604T000705Z.json`、upstream skill 位置 `~\.agents\skills\mcp2cli`，以及 fork/adapted `skills2cli` 位置 `~\.codex\skills\skills2cli`。
<!-- EVIDENCE_INDEX_END -->
