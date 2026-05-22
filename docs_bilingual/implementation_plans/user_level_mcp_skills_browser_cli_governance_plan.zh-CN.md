---
doc_id: user_level_mcp_skills_browser_cli_governance_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
status: draft
doc_class: implementation_plan
created_at: 2026-05-22
source_reference_file: reference_files/1.md
---

# 用户级 MCP、Skills、Browser 与 CLI Harness 治理实施方案

## 1. 目的

本方案把 MCP、skills、浏览器自动化和 CLI harness 能力从零散的项目级使用，提升为用户级、多项目、多会话可复用基础设施。

目标不是增加更多常驻工具，而是通过“最小充分面”降低 token 压力和安全风险：

1. 优先使用低 token、低风险能力；
2. 只有任务确实需要时才启用高 token 或高风险能力；
3. 涉及用户敏感信息的操作必须获得用户明确授权；
4. 所有长期用户级 helper 必须可固定版本、可审计、可更新、可回滚。

本方案同时实施 MCP 治理和 skills 治理：新增面向 MCP 的 `mcp2cli`，以及面向 Codex skills 的 `skills2cli`。

## 2. 参考源与实施定位

本轮实施：

- `mcp2cli`：用户级 MCP CLI facade 和低 token MCP 发现/调用面。
- `skills2cli`：新建 clean-room 本地 helper，用于 skill index/search/show/profile suggest/warning audit。
- `chrome-devtools-mcp`：从当前项目/裸入口使用提升为用户级受管 browser automation。
- `CDP Bridge`：保留为用户级 browser bridge，默认 inspect-first，敏感操作需授权。
- `OpenCLI`：安装为 on-demand 用户级 adapter 候选，不作为默认常驻能力。
- `CLI-Anything` 与 CLI-Anything Hub：安装为用户级 harness 生成/参考工具，并用于辅助设计 `wecom-cli`。
- `The Harness Problem`：作为后续 hash-anchored edit 与 harness 可靠性研究参考。
- `oh-my-pi`：作为用户级 sidecar reference/runtime 安装适配，不替代 Codex。

仅作为后续“Codex CLI 个人开发者生产级持久化团队”参考源：

- `ohmyopenagent`：OpenAgent 风格多 agent 提示词和运行时思路参考源。
- `snow-cli`：CLI 产品形态和操作员交互设计参考源。

## 3. 用户级运行时目录布局

除非后续实施变更明确替代，默认使用以下布局：

```text
C:\Users\lenovo\.codex\external\mcp2cli\
C:\Users\lenovo\.codex\external\oh-my-pi\
C:\Users\lenovo\.codex\external\cli-anything\
C:\Users\lenovo\.codex\external\opencli\
C:\Users\lenovo\.codex\tools\mcp2cli\
C:\Users\lenovo\.codex\tools\skills2cli\
C:\Users\lenovo\.codex\tools\browser-automation\
C:\Users\lenovo\.codex\tools\wecom-cli\
C:\Users\lenovo\.codex\state\mcp2cli\
C:\Users\lenovo\.codex\state\skills2cli\
C:\Users\lenovo\.codex\state\browser-automation\
C:\Users\lenovo\.codex\state\wecom-cli\
C:\Users\lenovo\.codex\state\tool-updates\
```

本仓库仍是 source of truth。用户级文件只是安装产物。任何安装器都必须从 repo-local source 生成或同步用户级副本，并保留 receipt。

## 4. Token 与风险优先级模型

当多个能力面都能完成任务时，按以下顺序选择：

| 优先级 | 能力面 | Token 成本 | 安全风险 | 默认行为 |
|---|---|---:|---:|---|
| 1 | `skills2cli search/show`、`mcp2cli list/search` | 低 | 低 | 默认允许 |
| 2 | 仓库内脚本/checker | 低 | 低 | 默认允许 |
| 3 | 非敏感 MCP 的 `mcp2cli call` | 中 | 中 | 工具/类别检查后允许 |
| 4 | `chrome-devtools-mcp` isolated/session profile | 中 | 中 | 本地/调试任务允许 |
| 5 | CDP Bridge 只读 scan/screenshot/tab inventory | 中 | 中 | inspect-first |
| 6 | OpenCLI 绑定浏览器 session | 高 | 高 | 需显式 browser-lane 授权 |
| 7 | 带登录态 project-profile | 高 | 高 | 需显式 project-profile 授权 |
| 8 | 用户个人 Chrome 或 WXWork GUI 写操作 | 高 | 极高 | 必须显式单任务授权 |

敏感操作包括读取 cookie、token、密码、私人聊天、个人标签页、个人 Chrome profile 数据、企业微信消息，或在已登录应用中点击、输入、发送。

## 5. `mcp2cli` 实施线

目标：通过把选定 MCP 能力转成低 token CLI 发现和调用面，降低 Codex MCP tools/list 压力。

实施要求：

- 将 `mcp2cli` 安装到隔离的用户级运行时，不安装到全局 Python。
- 在 `C:\Users\lenovo\.codex\state\tool-updates\mcp2cli.lock.json` 中固定版本或 git commit。
- 在 `C:\Users\lenovo\.codex\tools\mcp2cli\` 下提供 `.cmd` 或 `.ps1` wrapper。
- 增加允许被 CLI facade 暴露的 MCP endpoint registry。
- 默认不暴露高风险 MCP server。
- CLI 默认输出 compact summary；完整 schema 必须显式 `--full`。
- 访问 secrets、browser、shell、远程基础设施或个人数据的调用必须经过授权 gate。

最小命令：

```text
mcp2cli list --profile <profile> --json
mcp2cli search <query> --profile <profile> --json
mcp2cli show <tool> --profile <profile> --json
mcp2cli call <tool> --profile <profile> --json --args <json>
```

## 6. `skills2cli` 实施线

目标：解决反复出现的 `Exceeded skills context budget of 2%` warning，让大部分 skills 从“默认可见”转为“按需发现”。

实施要求：

- 从 repo-local source 做 clean-room helper，不 fork `mcp2cli`。
- 扫描 repo、user、system、plugin `SKILL.md` 并生成本地索引。
- 原始索引保存在用户级 state；只有脱敏 summary 可以提交到本仓库。
- 接入既有 skills usage audit plan 和 soft-load/profile helper 规则。
- 只保留一个很小的常驻 skill/profile 入口来路由 `skills2cli`。

最小命令：

```text
skills2cli index --json
skills2cli search <query> --json
skills2cli show <skill-id> --json
skills2cli profile suggest --task <text> --json
skills2cli audit warnings --since <duration> --json
```

`skills2cli` 自身不得 apply 或 disable skills。它只推荐 profile 并产生证据；profile apply 仍是独立的受治理动作。

## 7. 用户级 browser automation lane

把浏览器自动化提升为用户级、多项目、多会话 lane。

浏览器资产严格分成三类：

1. `isolated-session-managed`：Codex 受管临时 profile；证明归属和 stale 后可清理。
2. `project-profile`：项目长期 profile；可包含项目收藏夹、插件、测试登录态；不得自动删除。
3. `human-owned-personal-asset`：用户个人 Chrome；不得自动接管、自动清理或视作 Codex 受管资产。

Adapter：

- `chrome-devtools-mcp`：用户级 managed wrapper，本地/调试浏览器任务优先使用。
- `CDP Bridge`：用户级 inspect-first bridge；写操作必须先检查 owner 和授权。
- `OpenCLI`：可选 on-demand adapter，用于 website/browser-to-CLI 场景；不默认加载。

必须支持的 owner 状态：

```text
owner=codex-managed-isolated
owner=codex-managed-project
owner=human-owned
owner=human-delegated
```

规则：

- 同一 tab 同一时间只能有一个 automation owner。
- 同一 `project-profile` 同一时间只能被一个 session 控制。
- `human-owned-personal-asset` 只能在 one-tab、one-task、current-session 范围内临时升级为 `human-delegated`。
- 用户敏感读取和登录态上下文里的写入/点击/输入都必须显式授权。
- cleanup 永远不能作用于 human-owned Chrome。

## 8. `chrome-devtools-mcp` 用户级提升

当前状态：用户级 Codex config 已有 `chrome-devtools-mcp`，但本质上仍是裸 entry，尚未成为多项目、多会话受管模式。

实施要求：

- 用用户级 managed wrapper 替换裸启动。
- Wrapper 支持：
  - `--mode isolated-session`；
  - `--mode project-profile --project <slug>`；
  - 写入 lease；
  - stale scan；
  - 最大活跃实例数量限制；
  - 只清理已知 managed profile 的安全 cleanup。
- 保持 Codex direct MCP entry，不经 MCP Router 转发。

## 9. CDP Bridge 与 OpenCLI 用户级适配

CDP Bridge：

- 保持为用户级 Codex direct MCP server。
- 默认 lane 是只读 inventory、DOM scan、screenshot、tab list。
- cookie 读取、JS 写入、点击、输入、个人标签页导航或敏感上下文操作必须授权。

OpenCLI：

- 安装为用户级 external tool 和 wrapper，不作为常驻 Codex tool list 扩展。
- 只能通过 browser owner registry 使用。
- 未获得明确 one-task 授权时，不得绑定 human-owned Chrome tab。
- 优先使用 `isolated-session-managed` 或 `project-profile`，而不是 human-owned session。

## 10. `oh-my-pi` 用户级安装和适配

目标：把 `oh-my-pi` 作为 sidecar reference/runtime，用于 harness 与编辑思路，不替代 Codex。

实施要求：

- 克隆到 `C:\Users\lenovo\.codex\external\oh-my-pi\`，固定 commit 或 tag。
- 依赖安装在该目录或用户级 runtime，不做无记录的全局安装。
- Wrapper 放在 `C:\Users\lenovo\.codex\tools\oh-my-pi\`。
- 每项目 state 必须放在克隆源码之外，并包含 project slug 和 session namespace。
- 首轮只适配以下概念：
  - hash-anchored edit 研究；
  - CLI/harness 人机工效；
  - sidecar stats 或 UX 参考。
- 不替代 Codex `apply_patch`，不替代 native subagent workflow。

更新策略：

- fetch upstream 到 staging ref。
- 运行 smoke tests 和 wrapper help checks。
- 写 update receipt。
- 测试通过后才切换 wrapper pin。
- 保留上一版本 rollback pointer。

## 11. CLI-Anything 与企业微信 WXWork 实施线

目标：把 CLI-Anything 安装为用户级 harness 生成/参考工具，并构建受治理的企业微信 `wecom-cli`。

当前本地事实：`WXWork.exe` 正在运行，路径为 `D:\Program Files\WXWork\WXWork.exe`。

安装/适配要求：

- CLI-Anything / CLI Hub 安装到隔离的用户级 runtime。
- 不把 CLI-Anything 大量 skills hard-load 到 Codex 上下文。
- 使用 CLI-Anything 指导 harness 结构，但不能绕过本地授权规则。
- `wecom-cli` 作为受治理 harness 维护：用户级 tools 是安装产物，repo-local source 是事实来源。

`wecom-cli` 三阶段：

1. API/Webhook 层，低风险：
   - 发送 webhook 通知；
   - 凭据可用时通过官方 API 发送应用消息；
   - secrets 只存用户级 secret storage。
2. Process/window inventory 层，中风险：
   - 列出 `WXWork.exe` 进程；
   - 列窗口和标题；
   - 报告前台状态。
3. GUI automation 层，高风险：
   - attach 到指定 WXWork process/window；
   - click/type/send/read visible chat content；
   - 必须显式 one-task 授权，并持有全局 WXWork lease。

最小命令：

```text
wecom-cli process list --json
wecom-cli window list --json
wecom-cli webhook send --text <text> --json
wecom-cli app-message send --to <target> --text <text> --json
wecom-cli gui attach --pid <pid> --json --require-human-authorization
```

多会话规则：API/Webhook 在 secret 访问被允许时可并发；GUI automation 因为只有一个 WXWork desktop session，必须全局串行。

更新策略：

- CLI-Anything 更新不得自动重写 `wecom-cli`。
- `wecom-cli` 更新必须通过测试、授权策略检查和 rollback receipt。
- GUI automation 变更必须有人工 smoke test marker 后才能 active。

## 12. 仅参考项

`ohmyopenagent` 和 `snow-cli` 仅作为参考。

允许用途：

- 阅读架构思想；
- 对比 CLI UX；
- 支撑未来 Codex CLI 个人开发者生产级持久化团队设计。

禁止用于本方案：

- 不安装依赖；
- 不复制代码；
- 不加入默认 skill/profile；
- 不做 runtime integration。

## 13. 实施顺序

1. 为本方案创建 OpenSpec change。
2. 增加 token/risk priority、browser asset class、sensitive authorization、update receipt 的治理文档和 checker。
3. 实现 `skills2cli` MVP 和测试。
4. 增加 `mcp2cli` 用户级 wrapper 与允许 profile registry。
5. 把 `chrome-devtools-mcp` 提升为用户级 managed wrapper。
6. 加固 CDP Bridge policy，并只把 OpenCLI 作为 on-demand adapter。
7. 增加 `oh-my-pi` 用户级 external install wrapper 和 updater receipt model。
8. 安装 CLI-Anything / CLI Hub 用户级工具。
9. 构建 `wecom-cli` API/Webhook MVP，再做 window inventory，最后做带授权 gate 的 GUI automation。
10. 跑 local gate、local MR review，并在用户确认后再合入 local main。

## 14. 验证计划

- `skills2cli` 测试证明 index/search/show 不输出全量 skill descriptions。
- `mcp2cli` 测试证明 compact list/search/show 和 sensitive-call blocking。
- Browser checker 测试证明 isolated cleanup、project-profile retention、human-owned protection、tab owner exclusivity。
- CDP Bridge/OpenCLI 测试证明敏感动作必须显式授权。
- `oh-my-pi` updater 测试证明 pinned update 和 rollback receipt。
- `wecom-cli` 测试证明 process inventory 只读、secrets 脱敏、GUI write 无授权失败、WXWork GUI lease 独占。
- 仓库检查继续包括 OpenSpec guard、precommit update/archive gate、local gate、local MR review。

## 15. 来源

- https://github.com/knowsuchagency/mcp2cli
- https://github.com/jackwener/OpenCLI
- https://github.com/ChromeDevTools/chrome-devtools-mcp
- https://github.com/HKUDS/CLI-Anything
- https://clianything.cc/
- https://blog.can.ac/2026/02/12/the-harness-problem/
- https://github.com/can1357/oh-my-pi
- https://github.com/ymymssss/ohmyopenagent
- https://github.com/MayDay-wpf/snow-cli
