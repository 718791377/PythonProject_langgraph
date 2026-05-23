---
doc_id: user_level_mcp_skills_browser_cli_governance_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
translation_of: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
status: draft
plan_readiness: execution-ready
implementation_state: not_started
last_reviewed_at: 2026-05-23
doc_class: implementation_plan
created_at: 2026-05-22
source_reference_file: reference_files/1.md
---

# 用户级 MCP、Skills、Browser 与 CLI Harness 治理实施方案

## 0. 当前复核结论

截至 2026-05-23，本方案作为“执行前蓝图”已具备进入 OpenSpec 小步切片的颗粒度。`status: draft` 表示用户级运行时尚未按本方案全部落地，不表示本文缺少执行结构。

复核结论：

- 内容覆盖完整：MCP facade、skills 按需发现、browser owner、Chrome DevTools MCP、CDP Bridge、OpenCLI、`oh-my-pi`、CLI-Anything 与 `wecom-cli` 均有默认状态、授权边界、安装证据和回滚要求。
- 端口治理已明确：Codex 使用靠前的用户级号段，OpenClaw 使用靠后的号段，OpenCLI 必须使用端口分配器驱动的 `--port auto`，不得固定端口；端口分配器已经具备 reserve/release/import/gc 命令契约。
- 并发分配安全已明确：registry 更新必须原子化，绑定过程使用临时 lease，长时间运行的 owner 必须续租，崩溃恢复必须有证据。
- 动态本地事实已纳入治理：运行时进程是否存在、本机安装路径等信息必须由只读 inventory 刷新，并脱敏后才能成为仓库证据。
- 颗粒度达到可实施：每个 lane 都能拆成 OpenSpec change；每个 change 都必须有 owned files、checker/test、receipt schema、rollback method 和 non-goals。
- 未勾选清单是后续实施状态，不是方案缺口；在对应代码、checker、安装产物和 receipt 都完成前，不得把 lane 标为 `active`。
- 推进原则是先 baseline 后能力：先完成 token/risk、授权 receipt、update receipt 与 evidence redaction，再实现 `skills2cli`、`mcp2cli`、browser 与 `wecom-cli` 等具体能力。

本方案下一步不是继续扩大范围，而是选择第一个 OpenSpec change，把第 16 节的第 1 个切片落到 repo-local checker/test，再按本地提交流程推进。

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
C:\Users\lenovo\.codex\tools\codex-port\
C:\Users\lenovo\.codex\tools\browser-automation\
C:\Users\lenovo\.codex\tools\wecom-cli\
C:\Users\lenovo\.codex\state\mcp2cli\
C:\Users\lenovo\.codex\state\skills2cli\
C:\Users\lenovo\.codex\state\ports\
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

## 4.1 用户级端口治理

端口归属不靠单个工具硬编码，而由号段、registry 和 lease 共同治理。

默认号段：

| 号段 | 归属 | 用途 |
| --- | --- | --- |
| `39000-39299` | Codex | MCP facade、`skills2cli` 与低风险用户级 helper。 |
| `39300-39499` | Codex | OpenCLI on-demand browser adapter。 |
| `39500-39699` | Codex | Browser automation，包括 managed `chrome-devtools-mcp` wrappers。 |
| `39700-39999` | Codex | 预留给用户级 Codex 后续扩展。 |
| `40000-40999` | OpenClaw | OpenClaw 项目服务与 OpenClaw-managed local control plane。 |

规则：

- OpenClaw 端口必须排在 Codex 端口后面；Codex 不得从 `40000-40999` 分配端口。
- OpenClaw 迁移后不得从 `39000-39999` 分配端口；已有历史 OpenClaw 端口先导入为 `legacy_reserved`，再逐步迁移。
- 所有受管本地服务默认只绑定 `127.0.0.1`；绑定 `0.0.0.0` 必须单独做安全复核并获得 one-task approval。
- smoke test 与短生命周期探测优先使用系统临时端口（`port=0`），除非确实需要稳定 lease。
- OpenCLI 在本方案中没有固定端口。它必须通过端口分配器请求 `--port auto`，并在 `39300-39499` 号段获得 lease。
- `chrome-devtools-mcp` managed wrapper 如需端口，必须从 `39500-39699` 申请；如果上游工具只使用 stdio，则不分配 TCP 端口。
- wrapper 绑定前必须同时检查 registry 与当前监听 socket 表；发生冲突时选择同号段下一个可用端口，绝不 kill 或抢占持有端口的进程。
- stale lease 只有在记录的 PID 已不存在，或只读 health check 证明 owner 已不存活时才能回收。

Registry 路径：

`C:\Users\lenovo\.codex\state\ports\registry.json`

最小 registry 字段：

- `owner`：`codex`、`openclaw` 或 `external_reserved`；
- `project` 或 `project_slug`；
- `tool`；
- `host`；
- `port`；
- `lease_id`；
- `pid`；
- `created_at`；
- `renewed_at`；
- `ttl_seconds`；
- `lease_expiry`；
- `owner_session`；
- `purpose`；
- `status`：`pending_bind`、`active`、`stale`、`legacy_reserved` 或 `released`；
- `registry_revision`：用于检测过时并发写入的单调递增 registry 版本号。

### 4.1.1 端口分配器最小命令契约

端口分配器必须是由仓库源代码生成或同步的用户级 wrapper，不能把临时端口探测逻辑散落到每个工具 wrapper 里。

最小命令：

```text
codex-port lease reserve --owner codex --project <slug> --tool <tool> --range <range-name> --purpose <text> --ttl <seconds> --json
codex-port lease renew --lease-id <lease-id> --owner-session <session-id> --ttl <seconds> --json
codex-port lease release --owner-session <session-id> --port <port> --json
codex-port lease list --owner codex --json
codex-port lease import-legacy --owner openclaw --port <port> --purpose <text> --json
codex-port lease gc --dry-run --json
```

Port-governance 冲突决策表：

| 情况 | 必须行为 |
| --- | --- |
| registry 显示空闲，但 live socket 已监听 | 视为被占用，跳到同号段下一个可用端口，并记录 collision warning。 |
| registry 显示 active，但 PID 已不存在 | 标记为 `stale`；只有写入只读 PID/health 证据后才能复用。 |
| registry 中存在已超时的 `pending_bind` lease | 只有记录对应 session 已无法完成绑定和临时 lease 超时证据后才能回收。 |
| registry 显示 `legacy_reserved` | 绝不自动分配；必须先有明确 migration 或 release receipt。 |
| 请求号段与 owner 不匹配 | fail closed，例如 Codex 请求 `40000-40999`，或 OpenClaw 迁移后请求 `39000-39999`。 |
| release 请求缺少匹配的 owner session | fail closed，并保留 lease。 |

读写边界：

- `list` 与 `gc --dry-run` 是只读动作，默认允许。
- `reserve`、`renew`、`release`、`import-legacy` 和非 dry-run `gc` 是写动作，必须在 `C:\Users\lenovo\.codex\state\ports\receipts\` 写入 receipt。
- 端口分配器永远不得终止进程。进程清理属于 owner wrapper 的责任，并且需要单独的证据和授权。

### 4.1.2 多会话并发分配与崩溃恢复

多项目、多会话同时使用要求 registry 具备原子生命周期控制，不能只依赖号段约定：

- 每次修改 registry 都必须在 `C:\Users\lenovo\.codex\state\ports\registry.lock` 或等价锁面上取得短时独占锁，校验当前 `registry_revision`，写入临时文件后原子替换 `registry.json`。
- `reserve` 必须先写入包含唯一 `lease_id`、`status=pending_bind` 与短超时的临时 lease。owner wrapper 随后绑定 socket，并在成功后把 lease 提升为 `active`；如果绑定竞争失败，则把该 lease 标记为 released/collided，并继续申请同号段可用端口。
- registry lock 必须在启动浏览器、打开监听 socket、执行网络 I/O 或运行 health probe 前释放；该锁只序列化状态写入，不能包住长时间工具操作。
- 长时间运行的受管服务必须在 lease 过期前执行 `renew`。已过期的 `active` lease 只有在 PID 或只读 health evidence 证明前 owner 不再存活后才能复用。
- wrapper 正常停止必须执行 `release`。崩溃 session 留下的过期或 stale lease 只能由带证据的 `gc` 处理；其他 session 绝不能 release 或 renew 不属于自己的 lease。
- registry 内容损坏、原子替换失败或锁归属不明确时必须 fail closed，保留恢复副本，并阻止新分配，直到修复或显式恢复。

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

动态本地事实处理：`WXWork.exe` 已被识别为企业微信目标进程名，但进程是否正在运行、安装路径在哪里都属于动态本地事实。每次实施 `wecom-cli`、执行 smoke test 或进入 GUI task 前，都必须通过只读 process/window inventory 重新确认，不能把一次会话中的运行状态写成长期事实。

事实刷新规则：

- 仓库证据只能记录 process name、owner class、presence 和脱敏路径摘要；
- 仓库证据不得记录完整本机安装路径、消息内容或 raw window data；
- 未发现正在运行的 `WXWork.exe` 只阻断 process/window inventory 或 GUI automation 测试，不阻断 API/Webhook 设计工作；
- GUI automation 保持 `disabled`，除非同时存在新鲜 process/window inventory、global WXWork lease 和 one-task authorization receipt。

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

## 13. Readiness gate 与验收标准

状态流：

`planned -> implemented-local -> installed-user-level -> smoke-tested -> active -> rollback-ready`

这些状态是可执行状态，不是宣传标签：

- `planned`：OpenSpec change、文件归属、测试目标和 rollback 目标已明确。
- `implemented-local`：仓库代码、文档和测试已在 feature branch 或 worktree 中实现。
- `installed-user-level`：用户级 wrapper 或 helper 已作为安装产物存在于仓库源码树之外，并写入 receipt。
- `smoke-tested`：用户级 wrapper 已在目标 shell 中通过最小只读或 fail-closed 命令。
- `active`：该工具可在允许 lane 与授权边界内默认使用。
- `rollback-ready`：receipt 中有足够的版本、路径、命令和备份证据，可不依赖聊天记录回退。

默认 lane 状态表：

| Lane | 初始默认状态 | 允许的默认动作 | 禁止或需授权动作 | Active 前必须具备的证据 |
| --- | --- | --- | --- | --- |
| `skills2cli` | `planned`，实现后可成为 `active` | index/search/show/warning summary 的紧凑只读输出 | apply/disable skills、输出完整 plugin skill body、记录私有完整路径 | compact-output 测试、warning audit 脱敏测试、profile 建议不直接应用的证据 |
| `mcp2cli` | `planned`，按 profile 逐步 `active` | list/search/show，非敏感 call 需 category 检查 | secrets、shell、browser state、remote mutation、payment/account/personal data call | allowed-profile registry、sensitive-call fail-closed checker、授权 receipt schema |
| `codex-port` allocator | `planned`，reserve/renew/release 均有 receipt 后可成为 `active` | 按号段 reserve/list/renew/release/import/gc lease | 跨 owner 分配端口、kill 端口持有进程、非原子 registry 写入、无证据复用 stale lease | owner-range 测试、并发 reserve fixture、live-socket 冲突 fixture、lease receipt schema、stale PID/health 证据 |
| `chrome-devtools-mcp` | `planned`，本地调试 isolated mode 可先 `active` | isolated-session local/debug inspect | human-owned Chrome、登录态 project-profile、cleanup | managed wrapper、lease、profile ownership、stale cleanup dry-run 证据 |
| CDP Bridge | `on-demand` | tab list、DOM scan、screenshot、read-only inventory | cookie、JS write、click/type/navigate sensitive context | owner check、authorization gate、read/write 分离测试 |
| OpenCLI | `on-demand` | isolated 或 project-profile 的明确任务适配 | 默认绑定 human-owned tab、常驻加载 | wrapper pin、browser owner registry、human-owned protection 测试 |
| `oh-my-pi` | `reference-only` | 架构/UX/harness 参考读取 | 替代 Codex、替代 native subagent、无 receipt 更新 runtime | pinned clone、smoke test、update/rollback receipt |
| CLI-Anything | `reference-only` | harness 结构参考和生成辅助 | 大量 hard-load skills、绕过授权规则 | isolated install receipt、update pin、rollback evidence |
| `wecom-cli` API/Webhook | `planned` | 低风险通知/API 发送，secrets 可用时受控执行 | 无 secret storage 的明文凭据、未脱敏日志 | secret redaction、webhook/app-message smoke、receipt |
| `wecom-cli` process/window inventory | `planned` | 只读列进程/窗口/前台状态 | 读取消息内容、点击、输入、发送 | process/window fixture 或 smoke、no-content-capture 测试 |
| `wecom-cli` GUI automation | `disabled` | 无默认动作 | read/send/click/type，除非 one-task approval 与全局 lease 均存在 | global WXWork lease、one-task authorization receipt、manual smoke marker |

各 lane 的 `active` 条件：

- `skills2cli`：`index`、`search`、`show` 和 warning-audit summary 可用；默认输出紧凑；输出不得泄露私有完整路径、cookie、token 或全量 plugin skill descriptions。
- `mcp2cli`：allowed profiles 明确；list/search/show 默认紧凑；敏感调用在没有匹配授权 receipt 时 fail closed。
- `codex-port`：Codex/OpenClaw 号段被强制执行，并发 reserve 保持原子性，active owner 会续租，OpenCLI 只获得 allocator 驱动的 `--port auto` lease，每个写动作都有 rollback-ready receipt。
- `chrome-devtools-mcp`：wrapper 写入 lease；isolated-session-managed 与 project-profile 模式明确区分；human-owned Chrome 被保护；stale-cleanup 必须先 dry-run 通过。
- CDP Bridge：只读检查与可写动作分离；每个写动作或敏感读取都必须先具备 owner evidence 与 authorization evidence。
- OpenCLI：在安装 pin、profile binding、阻止无授权绑定 human-owned tabs 的规则完成并通过测试前，保持 on-demand。
- `oh-my-pi`：在 updater receipts、smoke tests 和 rollback pins 存在前，保持 reference-sidecar。
- CLI-Anything：在 installation receipts、update pins 和 rollback evidence 存在前，只作为 harness-generation support。
- `wecom-cli` GUI automation：在 process/window inventory、global WXWork lease 和 one-task authorization receipts 完成并通过测试前，保持 disabled。

本方案验收标准：

- 每个 lane 都有明确默认状态：`active`、`on-demand`、`reference-only` 或 `disabled`。
- 每个用户级安装工具都有 update receipt 与 rollback pointer。
- 每个共享本地监听服务都必须通过端口分配器申请 lease、记录端口 lease receipt，并避免固定端口，除非它是已记录的 `legacy_reserved`。
- 并发端口申请必须通过原子 registry 写入和临时绑定处理进行串行化，并在复用前证明崩溃恢复安全。
- 每个敏感 lane 都有 fail-closed checker 或 wrapper guard。
- 每个 browser automation lane 在可读取或修改状态的动作前都会记录 owner class。
- 仓库证据不保存 secrets、cookies、raw browser data、完整个人运行时路径或完整 plugin description dumps。

## 14. 敏感授权矩阵

| 动作 | 默认状态 | 必需授权证据 |
| --- | --- | --- |
| Skill index/search/show | 允许 | 无；输出必须紧凑并脱敏。 |
| Skill warning audit summary | 允许 | 无；warning text 只能摘要，不得倾倒完整 skill body。 |
| MCP list/search/show | 允许 | 工具必须属于 allowed profile registry。 |
| 不涉及 secrets、副作用、远端变更或个人数据的 MCP call | 条件允许 | allowed tool category 加 compact output policy。 |
| 涉及 secrets、shell execution、browser state、remote infrastructure mutation、payment/account action 或 personal data 的 MCP call | 默认阻断 | 显式 one-task approval，并写入包含 tool、purpose、scope、expiry 的 receipt。 |
| Chrome isolated-session-managed local debugging | 允许 | managed lease 与 isolated profile path。 |
| 带登录态的 Chrome project-profile | 默认阻断 | project-profile approval 加 owner lease；跨项目复用必须重新授权。 |
| human-owned Chrome 读取或写入 | 默认阻断 | one-tab、one-task、current-session delegation；不得后台浏览个人资产。 |
| CDP Bridge 或 OpenCLI click/type/navigate/cookie/JavaScript write | 默认阻断 | owner check 加显式授权，授权中需命名 target 与 allowed action。 |
| WXWork process/window inventory | 只读允许 | 不捕获消息内容；不执行 click/type/send。 |
| WXWork message read/send/click/type | 默认阻断 | one-task approval 加 global WXWork lease 与 receipt。 |

授权 receipt 必须短期有效。一个 browser tab、一个 WXWork task、一个 MCP call family 或一个 shell-capable tool 的 receipt，不授权未来无关任务。

## 15. 安装与更新证据契约

本方案中的每个用户级安装工具都必须把 receipt 写到：

`C:\Users\lenovo\.codex\state\tool-updates\`

receipt 必填字段：

- tool name；
- installed version、git commit、package version 或 package lock hash；
- source URL；
- install path；
- wrapper path；
- state path；
- smoke test command 与 result；
- updater command；
- rollback pointer；
- last updated time；
- status：`active`、`on-demand`、`reference-only` 或 `disabled`；
- owner lane：`skills2cli`、`mcp2cli`、`codex-port`、`browser`、`oh-my-pi`、`cli-anything`、`wecom-cli` 或 `reference`。

仓库证据可以记录 receipt schema、相对 state 名称、status 和脱敏后的 smoke-test summary。仓库证据不得记录 secrets、cookies、tokens、raw browser data、消息内容或完整个人运行时路径。

端口 lease receipt 是写在 `C:\Users\lenovo\.codex\state\ports\receipts\` 下的运行时操作 receipt。它不能替代 `tool-updates` 下的安装/更新 receipt；如果工具可能打开本地监听端口，则对应安装/更新 receipt 必须引用相关 port-registry 号段、allocator wrapper 和 lease receipt schema。

更新规则：

- updater command 必须 pinned 或 version-aware；
- 改变 wrapper 行为的 update 必须重跑 smoke tests 与 authorization guard tests；
- smoke test 失败时必须继续选择上一个已安装版本；
- rollback 必须可仅凭 receipt 完成，不依赖聊天记录。

## 16. OpenSpec 实施拆分

按小步、可本地测试、可回滚的 change 实施本方案。默认拆分：

1. token-risk priority、port registry/lease rules、browser asset classes、sensitive authorization、update receipts 和 evidence redaction 的 policy/checker baseline；
2. `skills2cli` MVP：index/search/show 加 warning-audit summary，并覆盖 compact output 测试；
3. `mcp2cli` 用户级 wrapper 与 allowed profile registry；
4. browser owner registry 加 `chrome-devtools-mcp` managed wrapper，覆盖 isolated-session-managed 与 project-profile 模式；
5. CDP Bridge 与 OpenCLI on-demand enforcement，包括 human-owned tab protection；
6. `oh-my-pi` sidecar install/update receipts 与 rollback evidence；
7. CLI-Anything install/update receipts 与 harness-generation boundary；
8. `wecom-cli` API/Webhook MVP 与 secret redaction；
9. `wecom-cli` process/window inventory 与 read-only evidence；
10. `wecom-cli` gated GUI automation，包含 global WXWork lease 与 one-task authorization receipts。

OpenSpec 切片交付矩阵：

| 切片 | 主要产物 | 最小验证 | 完成证据 |
| --- | --- | --- | --- |
| 1. Policy/checker baseline | token/risk checker、port registry/lease checker、`codex-port` allocator/locking/lifecycle contract、authorization receipt schema、update receipt schema、evidence redaction policy | checker 单元测试、并发 reserve fixture、pending-bind 竞争 fixture、崩溃恢复 fail-closed fixture、local gate 注册 | checker 输出、测试记录、allocator lifecycle 证据、OpenSpec delta/spec 更新 |
| 2. `skills2cli` MVP | repo-local helper、用户级 wrapper、skill index/search/show/warning audit | compact output、privacy redaction、profile non-apply、warning audit 测试 | 脱敏索引摘要、wrapper smoke、receipt |
| 3. `mcp2cli` MVP | allowed profile registry、list/search/show/call facade | compact output、sensitive-call fail-closed、receipt-required 测试 | profile registry、授权失败样例、wrapper smoke |
| 4. Browser owner registry | owner registry、lease schema、`chrome-devtools-mcp` managed wrapper | isolated/project-profile/human-owned protection、cleanup dry-run 测试 | lease receipt、stale scan dry-run、wrapper smoke |
| 5. CDP Bridge/OpenCLI enforcement | read/write 分离 gate、OpenCLI on-demand adapter | cookie/JS/click/type/navigate sensitive action fail-closed 测试 | owner check 证据、授权 receipt 样例、阻断记录 |
| 6. `oh-my-pi` sidecar | pinned clone/install wrapper、update receipt model | wrapper help smoke、staging fetch、pin switch、rollback 测试 | lock/receipt、smoke summary、rollback pointer |
| 7. CLI-Anything boundary | isolated install receipt、harness-generation boundary | no hard-load check、update pin、rollback 测试 | install receipt、profile visibility 证据 |
| 8. `wecom-cli` API/Webhook | webhook/app-message commands、secret redaction | secret redaction、dry-run/smoke、receipt-required 测试 | 脱敏发送摘要、secret 不落库证据 |
| 9. `wecom-cli` inventory | process/window inventory commands | no-content-capture、read-only fixture/smoke 测试 | 只读 inventory 摘要、窗口内容未采集证据 |
| 10. `wecom-cli` GUI gate | global WXWork lease、one-task authorization gate | unauthorized fail、lease exclusivity、manual smoke marker 测试 | 授权 receipt、lease receipt、人工 smoke marker |

切片完成判定：每个切片只有在实现、测试、CI 注册、OpenSpec 更新、rollback 证据和 completed receipt 均存在时才算完成；如果只完成文档或研究，只能标记为 `planned` 或 `implemented-local`，不能标记为 `active`。

每个 OpenSpec change 必须定义：

- change 拥有的文件；
- 证明新行为的 local tests 或 checkers；
- 如有用户级安装产物，必须列出产物；
- 如有 receipt，必须列出 receipt path 与 schema；
- 如 change 可能绑定 TCP 端口，必须列出 local listener 或 port lease 归属；
- rollback method；
- 明确 non-goals，避免 change 膨胀。

细颗粒度实施清单：

- [ ] 为本方案创建或复用一个小步 OpenSpec change，并写明 scope、non-goals、rollback boundary。
- [ ] 建立 token/risk priority checker，禁止高 token/高风险 surface 在无证据时默认常驻。
- [ ] 建立用户级 port registry 与 allocator，确保 Codex 号段在前、OpenClaw 号段在后，并让 OpenCLI 使用 allocator 驱动的 `--port auto`。
- [ ] 实现 `codex-port lease reserve/renew/release/list/import-legacy/gc`，覆盖 owner-range 校验、registry 原子锁、临时 `pending_bind`、live-socket 冲突跳过、stale/崩溃证据和写入 receipt。
- [ ] 建立 sensitive authorization receipt schema，字段至少包含 action、target、scope、expiry、session、operator confirmation。
- [ ] 建立 user-level tool update receipt schema，并覆盖 install path、wrapper path、state path、pin、smoke、rollback pointer。
- [ ] 建立 sanitized evidence 规则，禁止提交 secrets、cookies、tokens、raw browser data、消息内容、完整个人运行时路径和完整 plugin description dumps。
- [ ] 实现 `skills2cli index --json`，输出 skill id、source layer、short description hash/summary 和可用状态。
- [ ] 实现 `skills2cli search <query> --json`，默认只返回紧凑摘要和定位信息。
- [ ] 实现 `skills2cli show <skill-id> --json`，默认不倾倒全量 skill body，完整内容需受控参数。
- [ ] 实现 `skills2cli profile suggest --task <text> --json`，只给建议，不直接 apply。
- [ ] 实现 `skills2cli audit warnings --since <duration> --json`，纳入 2% skills context budget warning 和 skipped-loading warning 摘要。
- [ ] 为 `skills2cli` 增加 compact-output、privacy redaction、profile-non-apply、warning-audit 测试。
- [ ] 实现 `mcp2cli` allowed profile registry，并区分低风险 discovery 与中高风险 call。
- [ ] 实现 `mcp2cli list/search/show` 紧凑输出与 `--full` 显式展开边界。
- [ ] 实现 `mcp2cli call` sensitive-category fail-closed gate。
- [ ] 为 `mcp2cli` 增加 profile registry、sensitive-call blocking、compact output、receipt-required 测试。
- [ ] 实现 browser owner registry，记录 owner class、project slug、session id、profile path、lease expiry。
- [ ] 实现 `chrome-devtools-mcp` managed wrapper 的 isolated-session mode。
- [ ] 实现 `chrome-devtools-mcp` managed wrapper 的 project-profile mode。
- [ ] 实现 browser stale scan 与 safe cleanup dry-run，清理范围只限已知 managed profiles。
- [ ] 为 browser lane 增加 tab owner exclusivity、project-profile retention、human-owned protection、cleanup dry-run 测试。
- [ ] 加固 CDP Bridge read-only 默认边界，写动作必须检查 owner 与授权 receipt。
- [ ] 把 OpenCLI 保持为 on-demand adapter，并接入 browser owner registry。
- [ ] 为 CDP Bridge/OpenCLI 增加 cookie/JS/click/type/navigate sensitive action fail-closed 测试。
- [ ] 安装或适配 `oh-my-pi` sidecar 时写入 pinned receipt、smoke result 和 rollback pointer。
- [ ] 为 `oh-my-pi` updater 增加 staging fetch、smoke、pin switch、rollback 测试。
- [ ] 安装 CLI-Anything / CLI Hub 时写入 user-level install receipt，不 hard-load bulk skills。
- [ ] 用 CLI-Anything 辅助设计 `wecom-cli`，但保留 repo-local source 和授权 gate。
- [ ] 实现 `wecom-cli process list --json` 与 `window list --json` 只读 inventory。
- [ ] 实现 `wecom-cli webhook send` 和 `app-message send` 的 secret redaction 与 receipt。
- [ ] 实现 `wecom-cli gui attach` 的 global WXWork lease 与 one-task authorization gate；默认保持 disabled。
- [ ] 为 `wecom-cli` 增加 process/window read-only、secret redaction、GUI unauthorized fail、lease exclusivity 测试。
- [ ] 把新增测试或 checker 注册到 `tools/ci/ci_test_manifest.json` 或共享 local gate 调用链。
- [ ] 对每个完成的 OpenSpec change 运行 precommit update/archive gate、local gate、local MR review。
- [ ] 每个用户级安装动作完成后记录 rollback-ready receipt；没有 receipt 的 lane 不得标记 active。

## 17. 实施顺序

1. 为本方案创建 OpenSpec change。
2. 增加 token/risk priority、port registry/lease、browser asset class、sensitive authorization、update receipt 的治理文档和 checker。
3. 实现 `skills2cli` MVP 和测试。
4. 增加 `mcp2cli` 用户级 wrapper 与允许 profile registry。
5. 把 `chrome-devtools-mcp` 提升为用户级 managed wrapper。
6. 加固 CDP Bridge policy，并只把 OpenCLI 作为 on-demand adapter。
7. 增加 `oh-my-pi` 用户级 external install wrapper 和 updater receipt model。
8. 安装 CLI-Anything / CLI Hub 用户级工具。
9. 构建 `wecom-cli` API/Webhook MVP，再做 window inventory，最后做带授权 gate 的 GUI automation。
10. 跑 local gate、local MR review，并在用户确认后再合入 local main。

## 18. 验证计划

- `skills2cli` 测试证明 index/search/show 不输出全量 skill descriptions。
- `mcp2cli` 测试证明 compact list/search/show 和 sensitive-call blocking。
- Browser checker 测试证明 isolated cleanup、project-profile retention、human-owned protection、tab owner exclusivity。
- Port-governance 测试证明 Codex 不会分配 OpenClaw 号段，OpenClaw 历史端口会导入为 reserved，冲突时只跳过不 kill 进程，stale lease 复用前必须有 PID/health evidence。
- Port allocator CLI 测试证明 `reserve`、`renew`、`release`、`import-legacy` 与非 dry-run `gc` 会写 receipt；并发 reserve 不会分配同一端口；pending-bind/崩溃恢复受证据门控；owner/range 或 owner-session 不匹配会 fail closed。
- CDP Bridge/OpenCLI 测试证明敏感动作必须显式授权。
- `oh-my-pi` updater 测试证明 pinned update 和 rollback receipt。
- `wecom-cli` 测试证明 process inventory 只读、secrets 脱敏、GUI write 无授权失败、WXWork GUI lease 独占。
- 仓库检查继续包括 OpenSpec guard、precommit update/archive gate、local gate、local MR review。
- Readiness-gate 测试证明没有 smoke-test evidence、install/update receipt evidence 与 rollback evidence 的 lane 不会变成 `active`。
- Authorization-matrix 测试证明敏感 MCP、browser、CDP/OpenCLI 和 WXWork 动作在没有当前 one-task authorization receipt 时 fail closed。

## 19. 来源

- https://github.com/knowsuchagency/mcp2cli
- https://github.com/jackwener/OpenCLI
- https://github.com/ChromeDevTools/chrome-devtools-mcp
- https://github.com/HKUDS/CLI-Anything
- https://clianything.cc/
- https://blog.can.ac/2026/02/12/the-harness-problem/
- https://github.com/can1357/oh-my-pi
- https://github.com/ymymssss/ohmyopenagent
- https://github.com/MayDay-wpf/snow-cli
