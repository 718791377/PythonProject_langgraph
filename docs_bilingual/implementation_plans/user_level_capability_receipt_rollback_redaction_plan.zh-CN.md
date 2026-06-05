---
doc_id: user_level_capability_receipt_rollback_redaction_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/user_level_capability_receipt_rollback_redaction_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
source_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
---

# 用户级能力 Receipt、Rollback 与 Redaction 实施方案

> **给 agentic workers：** REQUIRED SUB-SKILL：使用 `superpowers:executing-plans`；只有实现切片写集互斥时才使用 `superpowers:subagent-driven-development`。本子方案从旧 MCP/skills/browser/CLI 来源方案拆出，必须通过常规 claim、hotspot 与 local-main retire 门禁执行。

## 目标

为用户级 capability install、update、smoke、live handoff、cleanup 与 rollback 建立统一 receipt、rollback 与 redaction runtime 证据格式。

## 来源提取

- 来源：`multi_plan_parallel_session_orchestration_plan.zh-CN.md`
- 消费者：Browser/CLI adapters、CLI-Anything/WXWork_CLI、Codex harnesses、mcp2cli/skills2cli 与后续 durable smoke/adoption runtime。

## 阶段位置

本方案应在真实 user-level install/start/live action 前优先实施，因为后续 runtime lane 都需要可复用 receipt writer、redaction 和 rollback executor。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local；ready for repository local-main-first integration；remote publication remains closed。
Current gate：保持 remote publication 关闭；Phase 6 adapter lanes 可在本地集成后消费此 receipt contract，但 live installs、live starts、GUI writes、cookie reads、sensitive MCP calls 与 external message sends 仍未授权。
Source relation：从 `user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md` 拆出；不要把旧 source plan 直接作为 parent-plan child。
Runtime boundary：repo-local helper 只验证 evidence；它不 install tools、不 start browsers、不 call sensitive MCP methods、不 read browser data、不 mutate user-level runtime。
<!-- CURRENT_STATUS_END -->

## 文件归属

- `tools/user_level_capability_receipts.py` - 写入用户级 capability receipt 与 rollback metadata。
- `tools/check_user_level_capability_receipts.py` - 校验 receipt schema、redaction 与 rollback 字段。
- `test/user_level_capability_receipts.test.py` - 覆盖 receipt helper 与 checker 行为。
- 后续 install/update/smoke/live/cleanup/rollback receipt fixtures

## 并行会话契约

一个 session 独占本 implementation_plan。其他 runtime lane 可并行准备自己的 helper，但必须等本方案 schema 稳定后再写入真实用户级 receipt。

## 任务清单

## Real Runtime Implementation Gap（真实 runtime 缺口）

Receipt governance 已实现，但真实用户级 install/start/smoke/live lane 需要更完整的 runtime receipt writers 和 rollback executors。

<!-- TASK_BACKLOG_START -->
- [x] Stage B：拆出用户级 capability receipt、rollback 与 redaction contract。
- [x] Stage B：建立 repo-local checker/helper 以验证 evidence 结构。
- [x] Stage C：记录真实 runtime receipt writer 与 rollback executor 仍是后续工作。
<!-- TASK_BACKLOG_END -->

## Stage D pending runtime work（待实施真实 runtime）

- Stage D real runtime：扩展 receipt helper schema，覆盖 install/update/smoke/live/cleanup/rollback runtime events。
- Stage D real runtime：实现 rollback executor，记录 rollback target、backup path、restore command、dry-run result 与 operator authorization。
- Stage D real runtime：为 sensitive output 增加 redaction preview、redacted transcript hash 与 no-secret persistence evidence。

## 验证门禁

- `python tools/check_user_level_capability_receipts.py --root . --json` - 验证用户级 capability receipt。
- `python tools/check_precommit_update_archive.py --root . --json` - 执行提交前更新/归档检查。
- `python tools/run_openspec_guard.py --root .` - 执行 OpenSpec 与治理 guard。
- `tools/ci/local_gate.ps1` - 执行共享本地 CI gate。

## 验收标准

- 中文对照版正文为中文。
- receipt/rollback/redaction schema 可被后续 runtime lane 复用。
- Stage D 前不得声明真实 install/start/live receipt writer 已实现。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-05 real-runtime gap update：branch `runtime-plan-standard-20260605` 将 install/update/smoke/live receipt writer 与 rollback executor 标记为 Stage D pending。
- 2026-06-04 Stage B evidence：repo-local receipt governance helper 与 checker 已可验证 evidence 结构。
<!-- EVIDENCE_INDEX_END -->
