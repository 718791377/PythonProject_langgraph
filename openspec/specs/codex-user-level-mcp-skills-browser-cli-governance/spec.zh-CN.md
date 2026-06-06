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

### Requirement: CLI-Anything governance guard SHALL 要求 receipt evidence 和 adapter-generation 边界

CLI-Anything 只能作为 adapter-generation 支撑进入 repo-local MVP。安装、更新、pin 切换、rollback 和 harness plan 必须由 receipt、smoke evidence 和 rollback pointer 约束；不得 hard-load skills、运行 live control 或泄露私有路径。

### Requirement: WXWork_CLI governance guard SHALL 优先 API/Webhook，并对 WXWork GUI 自动化 fail closed

仓库必须提供 repo-local `WXWork_CLI` governance guard，用于建模企业微信 / WXWork_CLI / WXWork 控制边界；它不得 attach `WXWork.exe`、探测本地进程、调用 live API 或 webhook、读取消息内容、发送消息、修改用户级 Codex 配置或控制 GUI 状态。

guard 至少必须支持：

- `api-status --json`：报告 API/Webhook-first 姿态，不探测进程表；
- `webhook-plan --name <name> --secret-ref <ref> --json`：规划 webhook 使用，不调用 WeCom，不保留 secret 原值；
- `gui-plan --target-process WXWork.exe --json`：报告 GUI gate 要求，不执行 live control；
- `gui-check --action <action> --session <id> --authorization-receipt <path> --lease-receipt <path> --json`：对敏感 GUI 动作进行 fail-closed 预检。

WXWork GUI 动作必须要求 global WXWork lease receipt、operator authorization receipt、session 匹配、未过期 expiry 和 timeout release evidence。有效 receipt 在 repo-local MVP 中最多只允许 dry-run dispatch eligibility，不得触发 live GUI control。

#### Scenario: 请求 API/Webhook 状态

- **WHEN** `python tools/wxwork_cli_governance.py api-status --json` 运行
- **THEN** 命令必须返回 `ok=true`
- **AND** 必须报告 `api_or_webhook_first`
- **AND** 必须报告未探测进程、未控制 GUI、未读取消息正文、未调用 WeCom API

#### Scenario: Webhook planning 收到 inline secret

- **WHEN** `python tools/wxwork_cli_governance.py webhook-plan --name ops --secret-ref "secret=<value>" --json` 运行
- **THEN** 命令必须 fail closed
- **AND** 不得调用 webhook
- **AND** 默认输出不得保留 raw secret value

#### Scenario: 请求 GUI planning

- **WHEN** `python tools/wxwork_cli_governance.py gui-plan --target-process WXWork.exe --json` 运行
- **THEN** 命令必须返回 `ok=true`
- **AND** 必须报告 global lease、operator confirmation 和 timeout release 要求
- **AND** 必须报告 repo-local MVP 不允许 live GUI control

#### Scenario: GUI attach 缺少 receipts

- **WHEN** `python tools/wxwork_cli_governance.py gui-check --action gui.attach --session session-a --json` 在无 receipt 情况下运行
- **THEN** 命令必须 fail closed
- **AND** 必须要求 operator authorization receipt 和 global WXWork lease receipt
- **AND** 必须报告 `gui_control_performed=false`

#### Scenario: GUI attach 具备有效 receipts

- **WHEN** `gui-check` 收到匹配且未过期的 operator authorization 与 global WXWork lease receipts
- **THEN** 必须返回 `dispatch_allowed=true`
- **AND** 必须保持 `dry_run_only=true`
- **AND** 必须报告 `gui_control_performed=false`
- **AND** 不得输出 raw private receipt paths

### Requirement: 用户级 receipt governance guard SHALL 校验 authorization、update、rollback 与 redaction evidence

仓库必须提供 repo-local 通用 receipt governance guard，用于用户级 MCP、skills、browser 与 CLI harness lanes。该 guard 必须校验单任务 authorization receipt schema、update receipt schema、rollback pointer、smoke evidence 和 redaction 边界；不得安装工具、调用 MCP server、控制浏览器、读取 browser data、修改用户级 Codex 配置，默认输出不得暴露 raw private paths 或 raw secrets。

guard 至少必须支持：

- `auth-check --receipt <path> --action <action> --target <target> --session <id> --json` - 校验单任务 authorization evidence。
- `update-check --receipt <path> --tool-name <name> --owner-lane <lane> --json` - 校验安装/更新 evidence。
- `redact-check --receipt <path> --json` - 校验敏感数据 redaction 边界。
- `smoke-check --receipt <path> --tool-name <name> --owner-lane <lane> --json` - 在不运行 smoke command 的情况下校验 R4 `smoke-tested` receipt evidence。
- `rollback-check --receipt <path> --owner-lane <lane> --json` - 在不执行 rollback 的情况下校验 rollback dry-run/apply receipt evidence。
- `template --kind authorization --json` - 输出 authorization receipt 字段模板。
- `template --kind update --json` - 输出 update receipt 字段模板。
- `template --kind smoke --json` - 输出 R4 smoke receipt 字段模板。
- `template --kind rollback --json` - 输出 rollback receipt 字段模板。

Receipt field glossary：

| Field | 含义 |
| --- | --- |
| `action` | 请求的敏感操作。 |
| `target` | 被授权执行该操作的资源或 adapter target。 |
| `scope` | 允许的 action set；必须包含请求操作或 `*`。 |
| `expiry` | 授权失效的未来时间戳。 |
| `session` | 当前 Codex session 或 owner session id。 |
| `operator_confirmation` | operator 已批准敏感操作的布尔证据。 |
| `tool_name` | 被安装或更新的用户级 helper 或 adapter。 |
| `installed_version` | 安装产物的 pinned version、tag 或 commit。 |
| `source_url` | 不含 credential 的公开来源位置。 |
| `install_path`、`wrapper_path`、`state_path` | 默认输出必须 hash 或 redact 的本地私有路径。 |
| `smoke_test_command`、`smoke_test_result` | 可重复验证命令与 pass/fail 证据。 |
| `updater_command` | pin-aware 更新命令。 |
| `rollback_pointer` | 上一版本、备份目录或 rollback reference。 |
| `owner_lane` | 所属 lane，例如 `skills2cli`、`mcp2cli` 或 `browser`。 |
| `redaction_status` | secrets、cookies、tokens、raw browser data、message contents、API keys、passwords、plugin description dumps 缺失或已脱敏的证据。 |
| `runtime_stage` | R4 smoke stage marker，通常为 `R4` 或 `smoke-tested`。 |
| `install_receipt` | 被 smoke-tested artifact 的 prior install/update receipt evidence。 |
| `smoke_command`、`smoke_type`、`smoke_result` | bounded read-only smoke evidence 与 pass/fail result；helper 只校验证据，不运行 command。 |
| `timeout_release` | smoke command 已干净释放 timeout 或 watchdog ownership 的证据。 |
| `rollback_ready` | R4 promotion 前 rollback evidence 已存在的布尔证据。 |
| `command_transcript`、`transcript_redaction` | smoke transcript evidence 及其存储前已脱敏的证明。 |
| `rollback_target`、`rollback_mode`、`restore_command` | rollback executor receipt 的 identity、dry-run/apply mode 与 restore-command evidence。 |
| `dry_run_result`、`apply_result`、`post_rollback_verification` | rollback dry-run、可选 apply 与 post-rollback verification evidence。 |
| `operator_authorization` | apply-mode rollback receipt 通过校验前必须具备的布尔授权证据。 |

#### Scenario: Authorization receipt 缺少必填字段

- **WHEN** `python tools/user_level_receipt_governance.py auth-check --receipt <path> --action browser.click --target tab:123 --session session-a --json` 针对不完整 receipt 运行
- **THEN** 命令必须 fail closed
- **AND** 必须报告缺失的 authorization receipt 字段
- **AND** 必须报告未修改用户级状态、未运行外部工具、未读取 browser data

#### Scenario: 有效 authorization receipt 被安全摘要化

- **WHEN** `auth-check` 收到 action/target/session 匹配、尚未过期且包含 operator confirmation 的 receipt
- **THEN** 命令必须返回 `ok=true`
- **AND** 必须报告 `authorization_valid=true`
- **AND** 必须输出 receipt path hash 而不是 raw receipt path

#### Scenario: Update receipt 缺少 rollback 或通过的 smoke evidence

- **WHEN** `python tools/user_level_receipt_governance.py update-check --receipt <path> --tool-name skills2cli --owner-lane skills2cli --json` 针对缺少 rollback pointer 或通过的 smoke evidence 的 update receipt 运行
- **THEN** 命令必须 fail closed
- **AND** 必须报告 rollback 和 smoke blockers

#### Scenario: 有效 update receipt 对私有路径和 rollback pointer 做 hash 化输出

- **WHEN** `update-check` 收到具有 install、wrapper、state、smoke、updater、owner-lane、redaction 和 rollback evidence 的有效 receipt
- **THEN** 命令必须返回 `ok=true`
- **AND** 必须报告 `rollback_ready=true`
- **AND** 必须对 install path、wrapper path、state path 和 rollback pointer 输出 hash

#### Scenario: Redaction check 发现原始敏感 payload

- **WHEN** `python tools/user_level_receipt_governance.py redact-check --receipt <path> --json` 针对含 cookies、inline token value、message contents 或 plugin description dumps 的 receipt 运行
- **THEN** 命令必须 fail closed
- **AND** 必须报告 redaction findings
- **AND** 默认输出不得读取 browser data 或暴露 raw secrets


### Requirement: Receipt governance helper SHALL 校验 R4 smoke-tested receipts

repo-local receipt governance helper 必须为用户级 runtime promotion lanes 提供只读的 R4 smoke receipt validation surface。

有效的 R4 smoke receipt 必须包含 tool identity、owner lane、runtime stage `R4` 或 `smoke-tested`、prior install receipt evidence、bounded read-only smoke command evidence、passing smoke result、timeout release evidence、rollback pointer、rollback readiness、transcript redaction evidence 与 redaction status。helper 默认必须对 receipt references、transcripts 与 rollback pointers 输出 hash-first summary。

当 smoke receipt 试图表示 write-capable behavior、R5 live handoff、sensitive action execution、raw browser data reads、external message sends 或 user-level state mutation 时，helper 必须 fail closed。

#### Scenario: 有效 R4 smoke receipt 被接受且不暴露 raw private paths

- **GIVEN** smoke receipt 为 bounded help/status/version/safe-discovery/read-only command 记录 R4 或 `smoke-tested` stage evidence
- **WHEN** `python tools/user_level_receipt_governance.py smoke-check --receipt <path> --json` 运行
- **THEN** command 必须报告 `ok=true`、`smoke_receipt_valid=true`、`runtime_stage=R4` 与 `rollback_ready=true`
- **AND** 默认输出必须用 hashes 替代 raw install receipt paths、transcript contents 或 rollback pointers
- **AND** command 必须报告未 mutate user-level state、未 run external tools、未 read browser data。

#### Scenario: R4 smoke receipt 试图表示 live 或 write behavior

- **GIVEN** smoke receipt 标记 write behavior、live action、sensitive action execution 或 user-level mutation
- **WHEN** smoke receipt checker 运行
- **THEN** command 必须 fail closed，并输出 sanitized blocker codes
- **AND** 不得把该 lane 视为 `smoke-tested`。

### Requirement: Receipt governance helper SHALL 在不执行 rollback 的情况下校验 rollback executor receipts

repo-local receipt governance helper 必须校验 rollback executor receipts 中的 dry-run 与 apply evidence，但不得执行 rollback commands。

rollback receipt 必须包含 rollback target、rollback pointer、rollback mode、restore command evidence、dry-run result、post-rollback verification evidence、owner lane、operator authorization status 与 redaction status。apply-mode receipts 在缺少 explicit operator authorization 时必须 fail closed。

#### Scenario: Rollback apply receipt 缺少 operator authorization

- **GIVEN** rollback receipt 在缺少 explicit operator authorization 时请求 apply mode
- **WHEN** `python tools/user_level_receipt_governance.py rollback-check --receipt <path> --json` 运行
- **THEN** command 必须 fail closed
- **AND** 必须报告 `rollback_performed=false`，因为 helper 只校验 receipts，绝不执行 rollback commands。

### Requirement: 治理方案 SHALL 使用可执行的 modern Comet 结构

用户级 MCP、skills、browser automation 与 CLI harness 治理方案必须包含面向 worker 的 Goal、Architecture 和 Tech Stack 开头块，并包含文件归属、就绪定义、任务 backlog、验收、证据、回滚和风险等面向执行的章节。

#### Scenario: modern section 齐全

- **WHEN** 人工复核该方案
- **THEN** 它必须包含 Goal、Architecture、Tech Stack、文件职责图、实施前就绪定义、任务级 backlog、验收标准、需要保留的证据、rollback 与风险章节
- **AND** 它必须保留 Token/risk priority、authorization receipt、update receipt、evidence redaction、port registry/lease、codex-port allocator、pending_bind、registry_revision、39000-39299、40000-40999、OpenSpec slice 与 fail closed governance markers

#### Scenario: runtime lane 仍受风险门禁约束

- **WHEN** 某个 lane 缺少 install、smoke、receipt 或 rollback evidence
- **THEN** 它必须保持低于 active
- **AND** 敏感 MCP、browser、CDP Bridge、OpenCLI、CLI-Anything 与 WeCom 动作必须要求当前 authorization receipt evidence

### Requirement: 治理方案 SHALL 保留完整 Comet 阶段证据

用户级 MCP、skills、browser automation 与 CLI harness 治理实施方案，在 operator 明确要求完整 `/comet` 重构时，必须描述完整的 Comet `Open -> Design -> Build -> Verify -> Archive` 工作流。

当 active change 是 full workflow 时，方案不得把当前治理方案执行模型描述为 tweak-only。

#### Scenario: 需要完整 Comet framing

- **WHEN** full Comet 重构后复核中文治理实施方案
- **THEN** 其 frontmatter 必须标识 `comet_workflow: full`
- **AND** 其 phase model 必须包含 `open-design-build-verify-archive`
- **AND** 正文必须包含明确的 Open、Design、Build、Verify、Archive gates

#### Scenario: Runtime implementation 仍然不在本次范围内

- **WHEN** full Comet refactor 已应用到文档
- **THEN** 它必须保留既有规则：真实用户级安装、live browser automation 与 WXWork GUI automation 需要独立治理证据
- **AND** 它不得把未完成 lanes 标记为 `active`

### Requirement: OpenCLI governance guard SHALL 要求 port-auto lease evidence

repo-local OpenCLI governance guard 在允许任何 OpenCLI pre-dispatch action 前，必须要求 allocator 驱动的 `--port auto` 和 sanitized codex-port lease receipt。

receipt 必须证明 Codex ownership，并且端口位于 OpenCLI/browser 范围 `39300-39499`。即使 browser owner 和 authorization evidence 有效，硬编码 OpenCLI port 也必须 fail closed。

#### Scenario: 缺少 port lease 会阻止 OpenCLI dispatch

- **WHEN** `python tools/opencli_governance.py check --action session.inspect --target tab:opencli-1 --session session-a --json` 在没有 codex-port lease receipt 的情况下运行
- **THEN** 命令必须 fail closed
- **AND** blockers 必须包含 `opencli_port_lease_receipt_required`
- **AND** 必须报告 `dispatch_allowed=false`

#### Scenario: 拒绝硬编码 OpenCLI port

- **WHEN** OpenCLI guard 收到 `--port 39300`
- **THEN** 命令必须 fail closed
- **AND** blockers 必须包含 `opencli_port_must_be_auto`
- **AND** 必须报告不允许硬编码 OpenCLI port

#### Scenario: 拒绝 OpenCLI 范围外的 port lease

- **WHEN** OpenCLI guard 收到端口不在 `39300-39499` 范围内的 codex-port lease receipt
- **THEN** 命令必须 fail closed
- **AND** blockers 必须包含 `opencli_port_lease_range_mismatch`

### Requirement: OpenCLI live-start preflight SHALL require install receipt, owner evidence, and port lease evidence

repository-local OpenCLI governance guard 必须提供非变更型 live-start preflight；如果缺少有效 OpenCLI install receipt evidence、active browser-owner lease evidence，或 Codex browser/OpenCLI range 内 sanitized codex-port `--port auto` lease evidence，必须 fail closed。

即使证据齐全，repo-local MVP 也不得启动 OpenCLI；必须返回 `live_start_not_implemented_repo_local_mvp` 与 `start_performed=false`。

#### Scenario: OpenCLI live start lacks install receipt

- **WHEN** `python tools/opencli_governance.py --state-dir <tmp> --owner-state-dir <owner-state> start --target tab:opencli-1 --session session-a --owner-lease-id <lease> --port-lease-receipt <receipt> --json` 在没有 install receipt 的情况下运行
- **THEN** 命令必须 fail closed
- **AND** blockers 必须包含 `install_receipt_required`
- **AND** 必须报告 `start_performed=false`

#### Scenario: OpenCLI live start lacks owner evidence

- **WHEN** `python tools/opencli_governance.py --state-dir <tmp> start --target tab:opencli-1 --session session-a --install-receipt <receipt> --port-lease-receipt <receipt> --json` 在没有 owner evidence 的情况下运行
- **THEN** 命令必须 fail closed
- **AND** blockers 必须包含 `owner_lease_required`
- **AND** 必须报告 `install_receipt_verified=true`

#### Scenario: OpenCLI live start has complete evidence but remains deferred

- **WHEN** OpenCLI live-start preflight 收到有效 install receipt、owner lease 与 port lease evidence
- **THEN** 命令必须以 `live_start_not_implemented_repo_local_mvp` fail closed
- **AND** 必须报告 `start_performed=false`
- **AND** 不得 install OpenCLI、start OpenCLI、launch browser、connect to browser target 或 mutate user-level Codex configuration


### Requirement: Codex harnesses governance SHALL require pinned source ledger and no-takeover guards

Codex harnesses governance SHALL be the only lane that owns harness wording. It SHALL derive future rules from these reference sources while keeping Codex as primary controller: The Harness Problem `https://blog.can.ac/2026/02/12/the-harness-problem`, oh-my-pi `https://github.com/can1357/oh-my-pi`, Pi `https://pi.dev/`, and Pi packages `https://pi.dev/packages`.

The harness lane SHALL require source ledger rows with source pin, retrieved_at, license note, and rollback pointer before adopting any derived rule or helper. It SHALL reject no Codex takeover violations, unpinned Pi packages, missing read guard, missing write guard, missing job state, missing isolated worktree, or missing changed-path report evidence.

对于 R4 user-level smoke runtime，`tools/run_codex_harnesses_smoke.py` 只能基于已有 R3 install/update receipts 生成受限 read-only Pi / oh-my-pi smoke receipts；`tools/check_codex_harnesses_smoke_receipts.py` 必须在不安装 Pi、不启动 sidecar、不运行 write-capable harness job、不替代 Codex surfaces 的前提下校验这些 receipts。缺失或无效 R3 receipts 可以生成诚实 blocked receipts，但 blocked receipts 必须保持 not smoke-tested，且不得满足 `--require-smoke-tested`。

#### Scenario: Harness governance checker runs

- **WHEN** `python tools/check_codex_harnesses_governance.py --root . --json` runs
- **THEN** it SHALL verify all four source URLs and the source-ledger fields
- **AND** it SHALL verify no Codex takeover, read guard, write guard, job state, isolated worktree, changed-path report, and unpinned Pi packages boundaries

#### Scenario: Harness R4 smoke receipts 在缺少安装证据时被阻断

- **WHEN** `python tools/run_codex_harnesses_smoke.py run --receipt-dir <dir> --json` 在没有 R3 install/update receipts 的情况下运行
- **THEN** helper 必须为 Pi 与 oh-my-pi 写入 blocked receipts
- **AND** `python tools/check_codex_harnesses_smoke_receipts.py --root . --receipt-dir <dir> --json` 必须接受这些 blocked receipts 作为诚实 evidence
- **AND** `python tools/check_codex_harnesses_smoke_receipts.py --root . --receipt-dir <dir> --require-smoke-tested --json` 必须 fail closed，因为 blocked receipts 不是 smoke-tested


### Requirement: Browser/CLI adapter boundary SHALL stay separate from sibling lanes

Stage B split marker note: the Browser/CLI adapter lane contains only chrome-devtools-mcp, CDP Bridge / cdp-bridge-mcp, and OpenCLI. CLI-Anything/WXWork_CLI are handled by adapter-generation and adapter-plan governance; they are not Browser/CLI adapters. Codex harnesses governance is separate and not Browser/CLI adapters.

#### Scenario: Adapter lane table is checked

- **WHEN** `python tools/check_user_level_browser_cli_adapter_boundary.py --root . --json` runs
- **THEN** it SHALL accept only canonical Browser/CLI adapter rows.
- **AND** it SHALL reject non-adapter lane entries.

### Requirement: Runtime promotion ladder SHALL separate project-level governance from user-level runtime

本治理族 SHALL 对 CLI-Anything/WXWork_CLI、Browser/CLI adapters 与 Codex harnesses 使用共享 R0-R5 runtime promotion ladder。该 ladder SHALL 保持本包 not installed/started/enabled in this package，并 SHALL 防止任何 lane 在缺少精确 marker evidence 时声明 runtime readiness。

Runtime stages SHALL 含义如下：

- R0 project-level preflight：仅非变异 source/environment/risk inventory。
- R1 project-level fake/dry-run runtime：仅 deterministic fixture 或 dry-run behavior。
- R2 reusable project-level helper/guard：repo-local reusable guard/helper pattern，不是 user-level global install。
- R3 user-level install/update receipt：需要 `installed-user-level`、explicit authorization、immutable pin、install/update receipt、smoke command、updater command、rollback pointer、owner lane 与 redacted path evidence。
- R4 user-level smoke runtime：需要 `smoke-tested`、bounded help/status/read-only smoke evidence、timeout release、redaction 与 rollback readiness；`tools/run_codex_harnesses_smoke.py` 生成的 blocked receipts 只是说明 R4 未运行原因的 evidence，不是 smoke-tested promotion evidence。
- R5 active-candidate / bounded live handoff：需要 `active-candidate`、current authorization receipt、owner/global lease、target/action allowlist、expiry、timeout release、rollback pointer、action 或 changed-path report 与 cleanup evidence。

#### Scenario: Runtime promotion markers are missing

- **WHEN** `python tools/check_user_level_cli_anything_wxwork_cli_governance.py --root . --json`、`python tools/check_user_level_browser_cli_adapter_boundary.py --root . --json` 或 `python tools/check_codex_harnesses_governance.py --root . --json` 运行
- **THEN** 如果 parent plan、child plan 或 stable spec 不再保留 R0/R1/R2/R3/R4/R5 stage markers，checker SHALL fail closed
- **AND** 如果 promotion contract 移除了 `installed-user-level`、`smoke-tested` 或 `active-candidate` marker evidence，checker SHALL fail closed

#### Scenario: Runtime work is attempted in the planning package

- **WHEN** runtime promotion package 只更新 plans、checkers、tests 与 stable spec text
- **THEN** 它 SHALL 声明 CLI-Anything、WXWork_CLI、browser adapters、Pi、oh-my-pi 与 harness runtime are not installed/started/enabled in this package
- **AND** 它 SHALL NOT 在缺少 receipts 时声明 R3/R4/R5 runtime evidence

#### Scenario: WXWork_CLI send action is requested before R5

- **WHEN** 在 `active-candidate` R5 evidence 存在之前考虑 WXWork_CLI send behavior
- **THEN** 该 lane SHALL fail closed
- **AND** send action allowed only at R5 SHALL 要求 global WXWork lease、explicit operator authorization、target/action allowlist、message redaction、ephemeral message handling、session match、future expiry、timeout release、rollback/stop evidence 与 sanitized post-run action report

#### Scenario: Browser adapter sensitive action is requested before R5

- **WHEN** 在 R5 evidence 存在之前考虑 chrome-devtools-mcp、CDP Bridge 或 OpenCLI click/type/navigate/JavaScript/cookie/raw-browser-data behavior
- **THEN** 该 lane SHALL fail closed
- **AND** R5 SHALL 要求 owner lease + authorization receipt、target/action allowlist 与 sanitized action reporting

#### Scenario: Codex harness sidecar attempts takeover

- **WHEN** Pi 或 oh-my-pi sidecar behavior 试图替代 Codex、native subagents、native_omx、LangGraph、codex-ohmy、apply_patch、local-main-first gates 或 main Codex CLI leader session
- **THEN** harness lane SHALL fail closed
- **AND** R5 仍 SHALL 要求 isolated worktree、read guard、write guard、job state、no Codex takeover、changed-path report、rollback 与 cleanup evidence


### Requirement: Mcp2cli 与 Skills2cli runtime helper SHALL 记录 fixture-backed R4 smoke receipts

repo-local `install_user_level_mcp_skills_cli.py` helper 必须为 `mcp2cli` 与 `skills2cli` runtime promotion evidence 提供显式 `smoke` 命令。该命令只能对显式传入的 Codex home 下的 wrappers 运行受限只读 help/version smoke commands；只有同时提供 `--record` 与 `--operator-confirmation` 时，才允许写入 R4 `smoke-tested` receipts。

repo-local `check_user_level_mcp_skills_cli_install.py` checker 必须提供 `--require-smoke-tested`，用于强制要求两个工具都具备有效 R4 smoke receipts；任何一个工具缺少 smoke evidence 时都必须 fail closed。这类 fixture-backed R4 receipts 必须能通过 `tools/user_level_receipt_governance.py smoke-check` 校验；除非另有单独 live 授权，否则不得暗示真实默认用户级 Codex home 已安装、已 smoke 或已 promotion。

#### Scenario: fixture-backed R4 smoke receipts 被记录

- **GIVEN** 一个临时 Codex home 已包含 `mcp2cli` 与 `skills2cli` 的 R3-style update receipts 和 wrappers
- **WHEN** `python tools/install_user_level_mcp_skills_cli.py smoke --record --operator-confirmation --codex-home <temp-home> --json` 运行
- **THEN** command 必须执行受限只读 wrapper smoke commands
- **AND** 必须为每个 tool 写入一份 `smoke-tested` R4 receipt
- **AND** 每份 receipt 必须通过 `python tools/user_level_receipt_governance.py smoke-check --receipt <receipt> --tool-name <tool> --owner-lane <tool> --json`
- **AND** 不得执行 R5 live handoff、sensitive calls、browser reads、external message sends 或默认用户级 Codex-home mutation。

#### Scenario: checker 强制要求 smoke-tested receipts

- **GIVEN** install-surface validation 收到一个 Codex home
- **WHEN** `python tools/check_user_level_mcp_skills_cli_install.py --root . --require-user-level-installed --require-smoke-tested --codex-home <home> --json` 运行
- **THEN** 如果 `mcp2cli` 或 `skills2cli` 任一工具缺少有效 R4 `smoke-tested` receipt，checker 必须 fail closed
- **AND** 当证据存在时，checker 必须报告 smoke receipt count 与脱敏后的最新 smoke receipt summaries。
