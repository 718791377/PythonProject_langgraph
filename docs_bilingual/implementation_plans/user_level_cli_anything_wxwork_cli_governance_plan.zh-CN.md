---
doc_id: user_level_cli_anything_wxwork_cli_governance_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/user_level_cli_anything_wxwork_cli_governance_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
supersedes:
  - docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
  - docs_bilingual/implementation_plans/user_level_browser_cli_adapter_boundary_plan.zh-CN.md
---

# 用户级 CLI-Anything 与 WXWork_CLI 治理方案

> **For agentic workers:** 使用 `superpowers:executing-plans`。只有在分配互不重叠写入集合后才使用并行子代理。本方案只管理 CLI-Anything 与 WXWork_CLI surfaces；Browser/CLI adapters 与 Codex harnesses 是独立兄弟方案。

## 目标

把 `CLI-Anything` 与 `WXWork_CLI` 治理为一个用户级 lane；未来 `WXWork_CLI` 可以通过 CLI-Anything 控制企业微信桌面进程 `WXWork.exe`。这个 lane 不是 Codex harnesses。

## 架构

Codex 先在本仓库保留项目级 guard source，只有 receipts、pins、smoke evidence、rollback pointers、redaction 与 operator authorization 完备后，才提升为用户级 wrapper。CLI-Anything generation/control 与 WXWork_CLI GUI actions 在相关 guard 证明请求安全前保持阻塞。

## 技术栈

Python guard scripts、JSON receipts、本地测试、CI manifest entries、docs registry、OpenSpec requirements、`C:\Users\lenovo\.codex` 下的用户级 Codex state、CLI-Anything 参考源，以及未来 WXWork_CLI wrapper receipts。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: planned Stage A split target；本文档包不启用任何 runtime control。
Owner session: 当前 main Codex session 拥有 parent-plan hotspot 与本 child-plan creation package。
Remote publication: not authorized / 远端发布未授权。
Migration note: Stage A 记录新 lane 与参考源；旧 baseline checker 仍读取 historical source plans。Stage B 必须先迁移 checker/tests，然后从 active governance 中移除旧 source plans。
<!-- CURRENT_STATUS_END -->

## 参考源

| Surface | 参考源 | 后续更新证据要求 |
| --- | --- | --- |
| CLI-Anything | https://github.com/HKUDS/CLI-Anything | source URL、immutable pin or commit、retrieved_at、license note、rollback pointer |
| WXWork_CLI | 面向 WXWork.exe control through CLI-Anything 的本地 Codex governance fork | wrapper path hash、owner lane、operator receipt、dry-run smoke、rollback pointer |
| WXWork.exe target | 只能通过 gated future WXWork_CLI lane 控制的企业微信桌面进程 | global lease、session match、expiry、no message-content evidence |

## 治理层级拆分

| 阶段 | 治理层级 | 允许工作 | 提升门禁 |
| --- | --- | --- | --- |
| 0 | 项目级 | taxonomy、source references、docs registry、OpenSpec wording | local docs gate |
| 1 | 项目级 | receipts、path redaction、no hard-load、no live control 的 guard/checker/tests | focused tests 与 local gate |
| 2 | 可复用项目级 | 可供其他 repo 使用的 generic receipt 与 authorization schema | checker-backed evidence 与 examples |
| 3 | 用户级 | CLI-Anything / WXWork_CLI install/update receipt 与 wrapper dry-run | 明确用户级授权、smoke pass、rollback pointer |
| 4 | 用户级 active-candidate | 有界 WXWork.exe dry-run 或 live handoff candidate | operator confirmation、global lease、expiry、rollback、no message body exposure |

## 文件归属

本子方案拥有未来 CLI-Anything 与 WXWork_CLI 治理文档、guards、tests、receipts 与 source-reference checks。它不拥有 chrome-devtools-mcp、cdp-bridge-mcp、OpenCLI、Pi、oh-my-pi 或 Codex harnesses。

## 并行 session 合约

同一时间只能有一个 session 认领本 implementation_plan。其他 session 可以并行处理 Browser/CLI adapters 或 Codex harnesses，但不得在没有串行 hotspot lease 的情况下编辑本方案、未来 checker、tests、docs registry、CI manifest 或共享 OpenSpec 热点。

## 任务 Backlog

<!-- TASK_BACKLOG_START -->
- [x] Stage A：在 `docs_bilingual/docs_registry.yaml` 注册本双语 child plan。
- [x] Stage A：记录 CLI-Anything source URL `https://github.com/HKUDS/CLI-Anything`。
- [x] Stage A：说明 WXWork_CLI 通过 CLI-Anything 控制 `WXWork.exe`，且不是 harnesses。
- [x] Stage A：保留旧 source plans 作为迁移输入，直到 Stage B checker migration 完成。
<!-- TASK_BACKLOG_END -->

## Stage B 待迁移工作

- 添加专用 CLI-Anything/WXWork_CLI surface checker。
- 将 CLI-Anything tests 从通用 CDP/OpenCLI coverage 中拆出。
- 将 active WeCom surfaces 重命名为 canonical `WXWork_CLI`，同时保留 archive history。
- 添加 no-message-content、global lease、operator authorization、timeout-release、rollback 与 dry-run checks。
- 更新 CI manifest 与 OpenSpec guard registration。
- checker 不再依赖旧 source plans 后删除旧 source plans。

## 验收标准

- CLI-Anything/WXWork_CLI 永远不被描述为 Codex harnesses。
- active docs 使用 `WXWork_CLI` 表示未来 WXWork.exe control lane。
- 没有 receipt-backed authorization，不得安装、clone、运行、探测、读取消息、发送消息或控制 WXWork.exe。
- 用户级提升在 project-level guards 本地通过前保持阻塞。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-04 Stage A evidence: 本方案记录 CLI-Anything/WXWork_CLI split target、参考源链接与 Stage B 迁移边界；implementation evidence pending Stage B.
<!-- EVIDENCE_INDEX_END -->
