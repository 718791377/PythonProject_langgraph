---
doc_id: user_level_browser_cli_adapter_boundary_plan
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/user_level_browser_cli_adapter_boundary_plan.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md
supersedes:
  - docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
---

# 用户级 Browser / CLI Adapter 边界方案

> **For agentic workers:** 使用 `superpowers:executing-plans`；只有在写入集合互不重叠时才使用并行子代理。本子方案只管理 Browser/CLI adapters。CLI-Anything/WXWork_CLI 与 Codex harnesses 是兄弟方案，不是 adapter lane。

## 目标

Browser/CLI adapter lane 仅限 `chrome-devtools-mcp`、`cdp-bridge-mcp` / `CDP Bridge` 与 `OpenCLI`。这些 adapter 不是 Codex harnesses，本方案也不管理 CLI-Anything、WXWork_CLI、WXWork.exe、Pi 或 oh-my-pi。

## 架构

先在本仓库落地项目级治理：browser owner lease、port lease、隔离 profile、sensitive-action authorization、redaction、dry-run/live-start gate。只有具备 install/update receipt、smoke evidence、rollback pointer 与 owner evidence 后，才允许提升为用户级 adapter wrapper。

## 技术栈

Python adapter guard、`codex-port`、browser owner registry、chrome-devtools-mcp 参考源、cdp-bridge-mcp 参考源、OpenCLI 参考源、JSON receipt、OpenSpec、本地测试、CI manifest，以及提升后才允许使用的 `C:\Users\lenovo\.codex` 用户级 wrapper 状态。

## 当前状态

<!-- CURRENT_STATUS_START -->
Status: implemented-local；Stage A 重新界定 adapter lane，并保持 remote publication 显式关闭。
Current gate: Stage B 必须先迁移 baseline checker/tests，使其不再依赖旧的混合 source plan，然后才能删除旧 source plans。
Source relation: 从历史 MCP/skills/browser/CLI source plan 拆分；canonical adapter set 现在只包含 `chrome-devtools-mcp`、`cdp-bridge-mcp` / `CDP Bridge` 与 `OpenCLI`。
Runtime boundary: 本 repo-local 包不安装工具、不启动浏览器、不调用敏感 MCP 方法、不读取 cookies、不执行 JavaScript、不修改 browser/GUI 状态，也不修改用户级 runtime state。
Implementation evidence: 现有 repo-local guard 将 chrome-devtools-mcp 与 OpenCLI 保持为 on-demand wrapper，并将 CDP Bridge 默认保持 read-only。下方 temporary legacy references 只用于 Stage A 兼容旧 baseline checker，Stage B 迁移后删除。
Remote publication: not authorized / 远端发布未授权。
<!-- CURRENT_STATUS_END -->

## 参考源

| Adapter | 参考源 | 后续更新证据要求 |
| --- | --- | --- |
| chrome-devtools-mcp | https://github.com/ChromeDevTools/chrome-devtools-mcp | source URL、package/pin、install receipt、smoke、rollback pointer |
| cdp-bridge-mcp / CDP Bridge | https://github.com/Unagi-cq/cdp-bridge-mcp | source URL、pin、port/owner lease evidence、redaction evidence |
| OpenCLI | https://github.com/jackwener/OpenCLI | source URL、pin、`--port auto` evidence、owner lease、authorization receipt |

## 治理层级拆分

| 阶段 | 治理层级 | 允许工作 | 提升门禁 |
| --- | --- | --- | --- |
| 0 | 项目级 | 分类、参考源、no-harness 边界 | docs/OpenSpec gate |
| 1 | 项目级 | adapter checker/tests、owner/port lease 检查、敏感动作 fail-closed | focused tests 与 local gate |
| 2 | 可复用项目级 | 可移植 adapter guard contract | checker-backed examples |
| 3 | 用户级 | wrapper install/update receipt、smoke、rollback plan | 明确授权并通过项目级 guard |
| 4 | 用户级 active-candidate | 有界 adapter live start 或 action handoff | owner lease、authorization receipt、expiry、redaction、rollback evidence |

## 文件归属

本子方案拥有 Browser/CLI adapter 文档、未来 adapter scope checker 更新、chrome-devtools-mcp/CDP/OpenCLI guard 测试与 source-reference 检查。它不拥有 CLI-Anything、WXWork_CLI、企业微信、Pi、oh-my-pi 或 Codex harnesses。

## 并行 session 合约

同一时间只能有一个 session 认领本 implementation_plan。其他 session 可以并行处理 CLI-Anything/WXWork_CLI 或 Codex harnesses，但不得在没有串行 hotspot lease 的情况下编辑本方案、未来 checker/tests、docs registry、CI manifest 或共享 OpenSpec 热点。

## 任务 Backlog

<!-- TASK_BACKLOG_START -->
- [x] 允许特定 guard 下的 read-only tab inventory 不需要敏感授权。
- [x] click、type、navigate、JavaScript execution、cookie read 与 raw browser data access 必须有 authorization receipt。
- [x] OpenCLI-style adapters 必须使用 `--port auto` 与 sanitized `codex-port` lease evidence。
- [x] Stage A：记录 canonical Browser/CLI adapter set 与参考源链接。
- [x] Stage A：说明 CLI-Anything/WXWork_CLI 与 Codex harnesses 是兄弟方案，不是 adapters。
<!-- TASK_BACKLOG_END -->

## Stage B 待迁移工作

- 更新 adapter checker/tests，使其只接受三个 canonical adapters。
- 为 CLI-Anything、WXWork_CLI、WXWork.exe、wecom-cli 与 harness wording 添加 adapter lane 负向覆盖。
- 更新 CI manifest、safety registry 与 OpenSpec guard wiring。
- checker 迁移后移除 temporary legacy compatibility markers。
- planned Stage B checker migration remains pending outside this closed backlog。

## 已实现合约

- `tools/chrome_devtools_mcp_managed.py` 保持 chrome-devtools-mcp on-demand：isolated-session 与 project-profile plans 是 dry-run，live start 需要 install receipt evidence，repo-local MVP 仍推迟实际浏览器启动。
- `tools/cdp_bridge_governance.py` 允许 read-only tab inventory 不带敏感授权，但 click、type、navigate、JavaScript execution、cookie read、raw browser data access 与 unknown actions 必须有 owner evidence 加 authorization receipt，否则 fail closed。
- `tools/opencli_governance.py` 保持 OpenCLI on-demand，要求 `--port auto`，验证 sanitized `codex-port` lease evidence，target-bound actions 需要 owner evidence，sensitive actions 需要 authorization receipts，并且即使存在 install receipt evidence 也推迟 live start。
- 临时迁移说明：`tools/cli_anything_governance.py` 保持 CLI-Anything generation-first、阻止 hard-load skills，并将迁移到 CLI-Anything/WXWork_CLI 子方案。
- 临时迁移说明：`tools/wecom_cli_governance.py` 过去保持 `wecom-cli` API/Webhook-first，具备 global lease、operator confirmation、timeout release 与 dry-run evidence；Stage B 会把 active surfaces 重命名为 `WXWork_CLI` 并迁移到 CLI-Anything/WXWork_CLI 子方案。

## Adapter lane status

| Adapter lane | Status | Repo-local evidence | Live/runtime boundary |
| --- | --- | --- | --- |
| chrome-devtools-mcp | on-demand | `tools/chrome_devtools_mcp_managed.py`, `test/chrome_devtools_mcp_managed.test.py` | 没有 install receipt 与 owner evidence 不启动 live browser；repo-local MVP 仍推迟实际启动。 |
| CDP Bridge / cdp-bridge-mcp | on-demand | `tools/cdp_bridge_governance.py`, `test/cdp_bridge_governance.test.py` | read-only tab inventory 允许；sensitive actions 需要 owner lease 与 authorization receipt。 |
| OpenCLI | on-demand | `tools/opencli_governance.py`, OpenCLI coverage in `test/cdp_bridge_governance.test.py` | 要求 `--port auto`、sanitized `codex-port` lease evidence、owner evidence 与 receipt-gated sensitive actions。 |
| CLI-Anything | reference-only | temporary Stage A baseline-checker compatibility row only | 不是 Browser/CLI adapter；迁移到 `user_level_cli_anything_wxwork_cli_governance_plan`。 |
| wecom-cli | on-demand | temporary Stage A baseline-checker compatibility row only | 不是 Browser/CLI adapter；Stage B active naming 将迁移为 `WXWork_CLI`。 |
| future-live-adapter | planned | placeholder marker required only for Stage A baseline checker compatibility | 不代表新增 canonical adapter。 |
| future-active-candidate | active-candidate | placeholder marker required only for Stage A baseline checker compatibility | 不代表当前 live runtime。 |

## 验证门禁

- Baseline checker：`python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json` 在 Stage B 迁移前仍必跑。
- OpenSpec aggregate guard：`python tools/run_openspec_guard.py --root . --json` 验证 official workflow、document policy 与 name clarity rules。
- Whitespace check：`git diff --check` 验证 patch 没有 whitespace errors。

## 验收标准

- canonical adapter set 只包含 chrome-devtools-mcp、cdp-bridge-mcp / CDP Bridge 与 OpenCLI。
- CLI-Anything/WXWork_CLI 与 Codex harnesses 只作为 sibling plans 或 temporary migration inputs 出现。
- 没有 receipt、owner、rollback 与 redaction evidence，不启用任何 sensitive runtime action。
- 本地 main 集成保持串行，remote publication 仍需显式授权。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 2026-06-01: `user_level_browser_cli_adapter_boundary_plan` implementation evidence recorded branch `implement-user-level-browser-cli-adapter-boundary-20260601` for the earlier mixed adapter package.
- 2026-06-04 Stage A implementation evidence: this rewrite narrows the canonical Browser/CLI adapter scope to chrome-devtools-mcp, cdp-bridge-mcp/CDP Bridge, and OpenCLI; checker migration is pending Stage B.
<!-- EVIDENCE_INDEX_END -->
