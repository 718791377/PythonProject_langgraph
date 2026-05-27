# Codex 用户级 MCP / Skills / Browser / CLI 治理规范

## 目的

本文件是 `spec.md` 的中文伴随文件，用于说明 Codex 用户级 MCP、skills、浏览器自动化和 CLI harness 治理的稳定规范。英文 ASCII `spec.md` 仍是 OpenSpec 主规范；本文件保持相同的治理意图、风险边界和验收口径。

## 要求

### Requirement: 用户级 MCP / skills / browser / CLI baseline SHALL 由脚本支撑

仓库必须用 repo-local checker、CI manifest 和 OpenSpec guard 共同约束用户级 MCP、skills、browser 与 CLI 治理面，避免只靠提示词或方案文本。

#### Scenario: baseline checker 覆盖计划、规范和 CI manifest

- **WHEN** baseline checker 运行
- **THEN** 它必须检查中英文实施方案、稳定 OpenSpec 规范、安全规则、CI manifest 注册项和关键 helper/test 文件
- **AND** 缺失任一必需治理面时必须 fail closed

### Requirement: 用户级端口治理 SHALL 在 allocator 实现前被保留

用户级端口范围、lease、pending bind、registry revision、续租和 crash recovery 规则必须先在规范和计划中固定，后续 allocator 实现不得绕过该范围。

### Requirement: 用户级 MCP / skills / browser / CLI 证据 SHALL 保持脱敏

所有 receipt、audit、browser owner registry、MCP 调用证据和 CLI harness 证据不得包含 secrets、cookies、tokens、原始浏览器数据、企业微信消息正文或完整私有路径。

### Requirement: 用户级 MCP / skills / browser / CLI 切片 SHALL 不得在缺少证据时进入 active

任何 lane 只有在 repo-local helper、checker、测试、安装或更新 receipt、smoke 结果和 rollback pointer 均存在后，才允许从 `implemented-local` / `install-ready` 进入 `active`。

### Requirement: Skills2cli MVP SHALL 提供紧凑、脱敏的 skill discovery

`skills2cli` 必须优先输出 compact JSON：skill 名称、来源、短描述 hash、profile 建议和风险元数据。默认不得输出完整 skill body 或完整 plugin description dump。

### Requirement: Skills2cli profile suggestion SHALL 只做 preview

profile suggestion 只能给出候选 profile 和理由，不能直接改写用户级 Codex 配置，也不能 hard-load 大量 skills。

### Requirement: Skills2cli warning audit SHALL 汇总 budget 与 skipped-loading warning

warning audit 必须可汇总 `Exceeded skills context budget`、`Skipped loading skill` 等警示，并保持路径和内容脱敏。

### Requirement: Codex-port allocator MVP SHALL 提供按范围感知的 port lease

端口 allocator 必须区分 Codex general helpers、Codex browser/OpenCLI、reserved local bridge、downstream consumer project range 和 emergency quarantine，并优先自动分配 Codex 范围内端口。

### Requirement: Codex-port lease lifecycle SHALL 保留 ownership、stale evidence 和 receipts

lease reserve、renew、release、gc dry-run、gc apply 都必须留下可审计 evidence；写操作必须具备 receipt，stale cleanup 必须可解释。

### Requirement: Mcp2cli MVP SHALL 提供紧凑 allowed-profile discovery

`mcp2cli` 必须支持 list/search/show/profile suggest 的低 token 发现路径，默认只暴露 server/tool 摘要和允许 profile，不得把高风险调用当成 discovery。

### Requirement: Mcp2cli MVP call facade SHALL 对敏感调用 fail closed

涉及写入、外部系统、凭据、cookie、token、浏览器输入、消息发送或用户资产的 MCP 调用，必须要求 authorization receipt 和 action scope；缺失时 fail closed。

### Requirement: Browser owner registry MVP SHALL 协调浏览器自动化 ownership

浏览器自动化必须把 `isolated-session-managed`、`project-profile` 和 `human-owned Chrome assets` 分开登记，并用 owner lease / authorization receipt 控制写操作。

### Requirement: Browser cleanup dry-run SHALL 保护 project 与 human-owned assets

浏览器 cleanup 默认只能 dry-run；不得清理 human-owned Chrome 资产，不得误删 project profile，必须输出分类和建议而不是直接删除。

### Requirement: Chrome DevTools MCP managed wrapper MVP SHALL gate isolated sessions

用户级 `chrome-devtools-mcp` managed wrapper 必须能启动隔离会话，并对点击、输入、导航、JS 执行等敏感动作要求 owner evidence 和 authorization receipt。

### Requirement: Chrome DevTools MCP managed wrapper MVP SHALL gate project profiles

project-profile 模式必须具备项目 owner、profile path、retention policy 和 cleanup policy；不得直接复制或污染用户个人 Chrome profile。

### Requirement: Chrome DevTools MCP managed wrapper MVP SHALL 暴露安全 stale scan 和 cleanup dry-run

stale scan 必须只读取 registry/lease 状态，cleanup dry-run 必须报告候选对象、owner、风险和所需授权；apply 必须另有 receipt。

### Requirement: CDP Bridge governance guard SHALL 保持 read-only 默认并对敏感动作 fail closed

CDP Bridge 默认只允许 tab inventory 等低风险读取。JS 执行、cookies、form input、navigation、click/type 等动作必须要求 owner lease 和 authorization receipt。

### Requirement: OpenCLI governance guard SHALL 保持 on-demand 并要求 browser owner evidence

OpenCLI 必须使用 `--port auto` 和 `codex-port` lease；默认只做 discovery。JS、点击、输入、导航等敏感 adapter 执行必须要求 browser owner evidence 和 authorization receipt。

### Requirement: CLI-Anything governance guard SHALL 要求 receipt evidence 和 harness-generation 边界

CLI-Anything 只能作为 harness-generation 支撑进入 repo-local MVP。安装、更新、pin 切换、rollback 和 harness plan 必须由 receipt、smoke evidence 和 rollback pointer 约束；不得 hard-load skills、运行 live control 或泄露私有路径。

### Requirement: WeCom CLI governance guard SHALL 优先 API/Webhook，并对 WXWork GUI 自动化 fail closed

仓库必须提供 repo-local `wecom-cli` governance guard，用于建模企业微信 / WeCom / WXWork 控制边界；它不得 attach `WXWork.exe`、探测本地进程、调用 live API 或 webhook、读取消息内容、发送消息、修改用户级 Codex 配置或控制 GUI 状态。

guard 至少必须支持：

- `api-status --json`：报告 API/Webhook-first 姿态，不探测进程表；
- `webhook-plan --name <name> --secret-ref <ref> --json`：规划 webhook 使用，不调用 WeCom，不保留 secret 原值；
- `gui-plan --target-process WXWork.exe --json`：报告 GUI gate 要求，不执行 live control；
- `gui-check --action <action> --session <id> --authorization-receipt <path> --lease-receipt <path> --json`：对敏感 GUI 动作进行 fail-closed 预检。

WXWork GUI 动作必须要求 global WXWork lease receipt、operator authorization receipt、session 匹配、未过期 expiry 和 timeout release evidence。有效 receipt 在 repo-local MVP 中最多只允许 dry-run dispatch eligibility，不得触发 live GUI control。

#### Scenario: 请求 API/Webhook 状态

- **WHEN** `python tools/wecom_cli_governance.py api-status --json` 运行
- **THEN** 命令必须返回 `ok=true`
- **AND** 必须报告 `api_or_webhook_first`
- **AND** 必须报告未探测进程、未控制 GUI、未读取消息正文、未调用 WeCom API

#### Scenario: Webhook planning 收到 inline secret

- **WHEN** `python tools/wecom_cli_governance.py webhook-plan --name ops --secret-ref "secret=<value>" --json` 运行
- **THEN** 命令必须 fail closed
- **AND** 不得调用 webhook
- **AND** 默认输出不得保留 raw secret value

#### Scenario: 请求 GUI planning

- **WHEN** `python tools/wecom_cli_governance.py gui-plan --target-process WXWork.exe --json` 运行
- **THEN** 命令必须返回 `ok=true`
- **AND** 必须报告 global lease、operator confirmation 和 timeout release 要求
- **AND** 必须报告 repo-local MVP 不允许 live GUI control

#### Scenario: GUI attach 缺少 receipts

- **WHEN** `python tools/wecom_cli_governance.py gui-check --action gui.attach --session session-a --json` 在无 receipt 情况下运行
- **THEN** 命令必须 fail closed
- **AND** 必须要求 operator authorization receipt 和 global WXWork lease receipt
- **AND** 必须报告 `gui_control_performed=false`

#### Scenario: GUI attach 具备有效 receipts

- **WHEN** `gui-check` 收到匹配且未过期的 operator authorization 与 global WXWork lease receipts
- **THEN** 必须返回 `dispatch_allowed=true`
- **AND** 必须保持 `dry_run_only=true`
- **AND** 必须报告 `gui_control_performed=false`
- **AND** 不得输出 raw private receipt paths
