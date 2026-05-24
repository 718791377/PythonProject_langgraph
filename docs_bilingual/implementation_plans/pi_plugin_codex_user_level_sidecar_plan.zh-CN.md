---
doc_id: pi_plugin_codex_user_level_sidecar_plan
lang: zh-CN
status: draft
plan_readiness: ready-for-user-confirmation
doc_class: implementation_plan
created_at: 2026-05-24
last_reviewed_at: 2026-05-24
scope: codex_to_pi_only
implementation_lane: p0_read_only_sidecar
source_reference_file: reference_files/3.md
related_docs:
  - docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
  - docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md
  - docs_bilingual/governance/codex_user_level_skills_governance_policy.zh-CN.md
---

# `pi-plugin-codex` 用户级 Sidecar 实施方案（已细化，待确认）

> **For agentic workers:** REQUIRED SUB-SKILL: 使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 逐任务实现。所有步骤使用 checkbox（`- [ ]`）跟踪；每个任务完成后先运行该任务列出的局部验证，再进入下一任务。

**Goal:** 在 Codex 会话中按需调用 Pi 做只读分析、review 和 adversarial review，同时保持 Codex 主会话为 leader、最终补丁与验证仍由 Codex 负责。

**Architecture:** Codex 通过 personal plugin skill 触发 repo-local `codex-pi` wrapper；wrapper 每次启动独立 `pi --mode rpc` 子进程，写入用户级 job state 与 receipt，并用 read-only guard 证明 P0 不改当前 worktree。`pi-plugin-cc` 与 `codex-plugin-cc` 仅作为 Apache-2.0 参考源，不把 Claude Code 插件面或 Pi->Codex 反向桥接搬进本方案。

**Tech Stack:** Codex personal plugin、Codex skill、Node.js ESM wrapper、PowerShell/CMD 用户级 launcher、Pi CLI RPC、JSONL event parsing、repo-local checker、OpenSpec change、Windows user-level receipt/state。

---

## 0. 本次复核结论

原方案方向正确，但颗粒度偏“架构草案”：缺少可执行的任务级拆分、CLI JSON contract、read-only guard 算法、receipt schema、fixture test 边界和治理文档更新落点。本版已补齐这些内容，因此进入 `ready-for-user-confirmation`：可以请用户确认是否进入实现；在确认前仍不得安装用户级插件、不得修改 `C:\Users\lenovo\.codex\config.toml`、不得写 personal marketplace、不得调用真实 Pi 执行仓库任务。

完备性检查：

| 检查项 | 结论 | 本方案落点 |
| --- | --- | --- |
| 方向边界 | 完整 | 只做 Codex -> Pi；Pi -> Codex 是 non-goal。 |
| `oh-my-pi` / `pi` / `pi-plugin-cc` 关系 | 完整 | 第 1 节。 |
| Codex 如何调用 Pi | 完整 | 第 2、3、4 节。 |
| repo-local source of truth | 完整 | 第 5 节。 |
| 用户级安装与 receipt | 完整 | 第 6、10 节。 |
| read-only 与写入隔离 | 完整 | 第 7、12 节。 |
| 任务级颗粒度 | 已补齐 | 第 11 节。 |
| 验证与 rollback | 已补齐 | 第 13、14 节。 |
| 与现有治理方案衔接 | 已补齐 | 第 15 节。 |

## 1. 关系模型与命名边界

基于 `reference_files/3.md` 中列出的链接，本方案采用以下关系模型。实际实现前必须固定每个外部仓库的 commit/tag，并在 OpenSpec proposal 中记录 pinned refs；不得把“当前网页内容”当作永久事实。

| 名称 | 本方案中的角色 | 是否安装/依赖 | 边界 |
| --- | --- | --- | --- |
| `pi` / `pi.dev` | Pi CLI/runtime 与 RPC 能力来源 | P0 只检测本机是否存在；不自动安装 | `codex-pi` 通过 `pi --mode rpc` 调用；secrets 仍由 Pi 自身配置或环境变量管理。 |
| `oh-my-pi` / `omp` | Pi family 的参考 runtime / harness / UX 资料 | 默认 `reference-only`；可作为 binary override 研究对象 | 不替代 Codex、不替代 native subagent、不成为 `codex-ohmy` 的启动目标。 |
| `pi-plugin-cc` | 主要 fork/adapt 参考 | 只复制允许复用的 Apache-2.0 概念和可归属代码 | 它是 Claude Code 插件；`.claude-plugin`、slash command、Claude hook、subagent 定义必须移除或改写。 |
| `codex-plugin-cc` | 原始 upstream 与 NOTICE/概念参考 | 只保留 attribution 与概念层参考 | 它的方向是 Claude Code 调 Codex，不复用 Codex app-server broker。 |
| `pi-codex` | Pi 内调用 Codex 的反向桥 | 明确 non-goal | 不安装、不依赖、不在 docs 中标成 P0 前置条件。 |
| `pi-plugin-codex` | 本方案要创建的新 Codex personal plugin | P0 planned/on-demand | 只暴露 Codex 中调用 Pi 的 skill + wrapper。 |
| `codex-ohmy` | wrapped Codex launcher | 不改语义 | 继续启动 Codex/oh-my-codex，不启动 Pi，也不变成 Pi launcher。 |

## 2. 目标与非目标

目标：

1. 在 Codex 会话中按需调用 Pi：
   - “用 Pi review 当前 diff”；
   - “用 Pi adversarial-review 重点看权限、回滚和用户级状态污染”；
   - “让 Pi 只读分析这个失败日志”；
   - P1 再扩展到 worktree-isolated rescue。
2. 让 Pi 调用可审计：
   - repo-local source of truth；
   - 用户级安装 receipt；
   - setup/read-only smoke；
   - rollback pointer；
   - read-only/write gate；
   - job state 可查询、可取消、可清理。
3. 保持 Codex 主会话为 leader：
   - Pi 输出是 sidecar evidence；
   - Codex 判断是否采纳；
   - Codex 负责最终 patch、验证、提交与合入。

非目标：

- 不实现 Pi 内 `/codex:*` 命令。
- 不安装或依赖 `pi-codex`。
- 不让 Pi 默认直接修改当前 worktree。
- 不把 `pi-plugin-cc` 当成 Codex 原生插件直接安装。
- 不修改 plugin/vendor cache。
- 不把 Pi / oh-my-pi / OMP 当成 Codex、native subagent、native_omx 或 LangGraph 的替代品。
- 不在 P0 引入长期后台 daemon；每个 job 使用独立短生命周期 `pi --mode rpc`。

## 3. 运行时架构

```text
User request in Codex
  -> Codex skill routing: pi-codex
  -> codex-pi.ps1 / codex-pi.cmd user-level launcher
  -> Node ESM wrapper: scripts/codex-pi.mjs
  -> one Pi subprocess per job: pi --mode rpc
  -> JSONL/RPC event parser
  -> user-level job state + sanitized result
  -> Codex leader reads summary and decides next action
```

边界规则：

- skill 只负责“何时调用”和“如何解释输出”，不包含 secrets 或真实 provider 配置。
- wrapper 负责执行、超时、取消、脱敏、read-only guard、receipt 和 JSON 输出。
- Pi 子进程只在 job 生命周期内存在；没有长期驻留服务就没有端口分配问题。
- P0 不写当前 worktree；P1 rescue 必须使用独立 Git worktree，并生成 changed-paths handoff summary。

## 4. Codex 中的使用方式

用户自然语言触发：

```text
用 Pi review 当前 diff
用 Pi adversarial-review 重点看权限和回滚
让 Pi 只读分析这个失败日志
```

Codex skill 应把这些意图映射到显式 wrapper 命令：

```powershell
codex-pi setup --json
codex-pi review --read-only --json
codex-pi adversarial-review --read-only --focus "权限和回滚" --json
codex-pi ask --read-only --stdin --json
codex-pi status --json
codex-pi result <job-id> --json
codex-pi cancel <job-id> --json
```

P0 不暴露写入命令。P1 可在独立 OpenSpec change 中增加：

```powershell
codex-pi rescue --worktree-isolated --background --json --task "<task>"
```

P1 验收前提：Pi 写入的只能是 wrapper 创建或显式指定的独立 worktree；Codex leader 只能从 handoff summary 选择性移植补丁。

## 5. Repo-local source of truth

新增目录与职责：

```text
tools/plugin_sources/pi-plugin-codex/
  .codex-plugin/plugin.json
  skills/pi-codex/SKILL.md
  scripts/codex-pi.mjs
  scripts/lib/pi-rpc.mjs
  scripts/lib/job-control.mjs
  scripts/lib/git-targets.mjs
  scripts/lib/read-only-guard.mjs
  scripts/lib/render.mjs
  scripts/lib/redact.mjs
  prompts/ask.md
  prompts/review.md
  prompts/adversarial-review.md
  schemas/setup-output.schema.json
  schemas/job-state.schema.json
  schemas/job-result.schema.json
  schemas/review-output.schema.json
  fixtures/fake-pi.mjs
  LICENSE
  NOTICE
```

配套仓库文件：

```text
tools/install-pi-plugin-codex.ps1
tools/check_pi_plugin_codex_contract.py
tests/pi-plugin-codex/codex-pi-cli.test.mjs
tests/pi-plugin-codex/pi-rpc-fixture.test.mjs
tests/pi-plugin-codex/read-only-guard.test.mjs
tests/pi-plugin-codex/job-control.test.mjs
tests/pi-plugin-codex/plugin-manifest.test.mjs
tests/pi-plugin-codex/docs-boundary.test.mjs
openspec/changes/add-pi-plugin-codex-sidecar/
  proposal.md
  tasks.md
  design.md
  specs/codex-user-level-tooling/spec.md
```

职责说明：

- `.codex-plugin/plugin.json`：Codex personal plugin manifest；只指向 `skills/pi-codex/SKILL.md` 和 wrapper usage，不内嵌大段运行时逻辑。
- `skills/pi-codex/SKILL.md`：Codex 侧路由说明；明确 Pi 输出不是最终验证证据。
- `codex-pi.mjs`：CLI entrypoint；解析参数、调用 lib、输出 JSON。
- `pi-rpc.mjs`：启动 `pi --mode rpc`、发送 prompt、读取 JSONL/RPC event、提取 final assistant message。
- `job-control.mjs`：job id、state transition、pid、cancel、timeout、stale cleanup。
- `git-targets.mjs`：识别 repo root、diff target、changed file list；不打印完整个人目录。
- `read-only-guard.mjs`：执行前后 worktree fingerprint，P0 发现变更则 fail closed。
- `render.mjs`：把 Pi 输出转成 Codex 可读摘要和 structured findings。
- `redact.mjs`：脱敏路径、环境变量、token-like strings 和 provider 配置片段。
- `tools/install-pi-plugin-codex.ps1`：用户级安装/更新/回滚脚本；生成 receipt，不直接改 plugin cache。
- `tools/check_pi_plugin_codex_contract.py`：静态检查文档和源码边界，防止方向性回归。

## 6. 用户级安装产物与 receipt

确认实现后，受控 installer 同步到用户级：

```text
C:\Users\lenovo\.codex\tools\codex-pi\
  codex-pi.ps1
  codex-pi.cmd
  package\

C:\Users\lenovo\.codex\state\pi-plugin-codex\
  tool-updates\
  jobs\<project_slug>\
  receipts\
```

安装 receipt 最小字段：

```json
{
  "schema_version": 1,
  "tool": "pi-plugin-codex",
  "status": "installed|rolled_back|blocked",
  "installed_at": "2026-05-24T00:00:00Z",
  "source_repo": "D:/PythonProject_langgraph",
  "source_commit": "<git sha>",
  "source_path": "tools/plugin_sources/pi-plugin-codex",
  "install_root": "%USERPROFILE%/.codex/tools/codex-pi",
  "state_root": "%USERPROFILE%/.codex/state/pi-plugin-codex",
  "pi_binary": "pi",
  "pi_version": "<redacted or null>",
  "rpc_smoke": "passed|blocked:pi_not_installed|blocked:rpc_unavailable|failed",
  "read_only_smoke": "passed|not_run|failed",
  "rollback_pointer": "<previous receipt id or null>",
  "secrets_recorded": false
}
```

规则：

- 没有 receipt 时 lane 只能是 `reference-only` 或 `planned`。
- 有 install receipt、setup smoke、rollback pointer 后才能是 `on-demand`。
- 真实 Pi read-only smoke 通过后才能成为 `active-candidate`。
- installer 不直接编辑 `C:\Users\lenovo\.codex\config.toml`；如需 Codex personal plugin marketplace 注册，先输出 dry-run diff 和 receipt，再由用户确认执行。

## 7. CLI JSON contract

### 7.1 `setup --json`

成功样例：

```json
{
  "schema_version": 1,
  "ok": true,
  "command": "setup",
  "status": "ready",
  "pi_binary": "pi",
  "pi_version": "1.2.3",
  "rpc_smoke": "passed",
  "state_root": "%USERPROFILE%/.codex/state/pi-plugin-codex",
  "secrets_recorded": false
}
```

Pi 缺失时必须稳定返回：

```json
{
  "schema_version": 1,
  "ok": false,
  "command": "setup",
  "status": "blocked",
  "blocker": "pi_not_installed",
  "pi_binary": "pi",
  "pi_version": null,
  "rpc_smoke": "not_run",
  "secrets_recorded": false
}
```

### 7.2 `ask/review/adversarial-review --json`

同步成功样例：

```json
{
  "schema_version": 1,
  "ok": true,
  "command": "review",
  "job_id": "pi_20260524_153012_ab12cd",
  "status": "succeeded",
  "mode": "read-only",
  "result_path": "%USERPROFILE%/.codex/state/pi-plugin-codex/jobs/<project_slug>/pi_20260524_153012_ab12cd/result.json",
  "summary": "Pi found 2 review points.",
  "findings": [
    {
      "severity": "medium",
      "category": "test-gap",
      "message": "Add fake Pi malformed JSONL coverage before real smoke.",
      "path": "tests/pi-plugin-codex/pi-rpc-fixture.test.mjs"
    }
  ],
  "read_only_guard": {
    "before_dirty": false,
    "after_dirty": false,
    "changed": false,
    "diff_stat_before": "",
    "diff_stat_after": ""
  },
  "secrets_recorded": false
}
```

read-only guard 失败样例：

```json
{
  "schema_version": 1,
  "ok": false,
  "command": "review",
  "job_id": "pi_20260524_153012_ab12cd",
  "status": "failed",
  "blocker": "blocked:worktree_changed_by_read_only_pi",
  "read_only_guard": {
    "before_dirty": false,
    "after_dirty": true,
    "changed": true
  },
  "result_path": null,
  "secrets_recorded": false
}
```

### 7.3 `status/result/cancel --json`

- `status` 不带 job id 时列出当前 project slug 最近 N 个 job 的脱敏摘要。
- `result <job-id>` 只读取当前 project slug 下的 job，不能跨项目读完整路径。
- `cancel <job-id>` 只能取消 `queued|running` job；成功后状态为 `canceled`；进程不存在但 state 仍 running 时返回 `stale_running_state` 并建议 `codex-pi status --repair --json`。

## 8. Pi binary 与 RPC 调用规则

默认 binary 为 `pi`。可选 override：

```powershell
$env:CODEX_PI_BINARY = "pi"
$env:CODEX_PI_BINARY = "omp"
```

规则：

- override 只接受无路径 binary 名称或显式受信任绝对路径；绝对路径必须写入本地 receipt 的脱敏摘要。
- `setup` 检测 binary、版本、RPC smoke、provider readiness；不读取、打印或提交 `~/.pi/agent/models.json` 原文。
- provider API key 只通过 Pi 自身配置或环境变量使用；`codex-pi` 不持久化 secrets。
- 每个任务启动一个独立 `pi --mode rpc`，timeout 默认 180 秒，用户可显式传 `--timeout-seconds 30..900`。
- wrapper 读取 stdout/stderr 时必须脱敏；stderr 原文只可写入用户级 result 文件，且要先过 redaction。
- malformed JSONL、无 final message、timeout、spawn failure 必须返回不同 blocker：`rpc_malformed_event`、`rpc_no_final_message`、`rpc_timeout`、`pi_spawn_failed`。

## 9. Job state schema

job state 至少包含：

```json
{
  "schema_version": 1,
  "job_id": "pi_20260524_153012_ab12cd",
  "project_slug": "pythonproject_langgraph",
  "workspace_root_hash": "sha256:...",
  "command": "review",
  "mode": "read-only",
  "pi_binary": "pi",
  "model_hint": null,
  "status": "queued|running|succeeded|failed|canceled|timed_out",
  "started_at": "2026-05-24T15:30:12Z",
  "finished_at": null,
  "pid": 12345,
  "prompt_path": "%USERPROFILE%/.codex/state/pi-plugin-codex/jobs/<project_slug>/<job_id>/prompt.redacted.md",
  "result_path": "%USERPROFILE%/.codex/state/pi-plugin-codex/jobs/<project_slug>/<job_id>/result.json",
  "read_only_guard": {
    "before_dirty": false,
    "after_dirty": null,
    "changed": null
  },
  "redacted_error": null
}
```

不得包含：API key、raw provider config、cookies、tokens、完整个人目录、未脱敏 shell 环境 dump、完整 `models.json`、完整浏览器/聊天内容。

## 10. Read-only guard 算法

P0 的 `ask`、`review`、`adversarial-review` 必须执行以下步骤：

1. 识别 repo root：`git rev-parse --show-toplevel`；失败时进入 non-git read-only mode，只允许 stdin 分析，不允许 diff review。
2. 记录 before fingerprint：
   - `git status --porcelain=v1 -uno`：记录 tracked dirty/staged 状态；
   - `git diff --stat`：记录 unstaged diff 规模摘要；
   - `git diff --name-only`：记录 unstaged changed paths；
   - `git diff --cached --name-only`：记录 staged changed paths。
3. 生成 prompt 时写入明确约束：Pi 不得修改文件、不得运行写命令、只输出建议。
4. 执行 `pi --mode rpc`。
5. 记录 after fingerprint。
6. 如果 before/after 不一致：
   - job status = `failed`；
   - blocker = `blocked:worktree_changed_by_read_only_pi`；
   - result 只输出脱敏 warning 和 changed path 摘要；
   - Codex 不得采纳该 job 为有效 review 证据。
7. 如果一致：输出 findings summary。

对当前 worktree 已经 dirty 的情况：

- 允许运行 read-only review，但 before dirty 状态要写入 JSON。
- guard 比较的是 before/after fingerprint 是否变化，不要求进入前必须 clean。
- 如果命令需要 review staged diff，必须显式 `--staged`，否则默认 review unstaged + staged summary。

## 11. 实施任务拆分

### Task 0：OpenSpec change 与实现边界冻结

**Files:**

- Create: `openspec/changes/add-pi-plugin-codex-sidecar/proposal.md`
- Create: `openspec/changes/add-pi-plugin-codex-sidecar/design.md`
- Create: `openspec/changes/add-pi-plugin-codex-sidecar/tasks.md`
- Create/Modify: `openspec/changes/add-pi-plugin-codex-sidecar/specs/codex-user-level-tooling/spec.md`

**Steps:**

- [ ] 写 proposal：目标仅为 Codex -> Pi read-only sidecar；把 Pi -> Codex、`pi-codex`、P1 rescue 标为非本 change 范围。
- [ ] 写 design：记录第 3 节架构、第 7 节 JSON contract、第 10 节 read-only guard。
- [ ] 写 tasks：按本第 11 节任务复制成 OpenSpec checklist。
- [ ] 运行 `python .\tools\run_openspec_guard.py --root .`，预期 exit 0。
- [ ] 提交 OpenSpec proposal 或与实现一起在同一功能分支内保留未提交，按仓库 release 策略决定。

### Task 1：Scaffold repo-local plugin source

**Files:**

- Create: `tools/plugin_sources/pi-plugin-codex/.codex-plugin/plugin.json`
- Create: `tools/plugin_sources/pi-plugin-codex/skills/pi-codex/SKILL.md`
- Create: `tools/plugin_sources/pi-plugin-codex/LICENSE`
- Create: `tools/plugin_sources/pi-plugin-codex/NOTICE`
- Create: `tests/pi-plugin-codex/plugin-manifest.test.mjs`

**Steps:**

- [ ] 创建目录结构，先只放 manifest、skill、LICENSE、NOTICE。
- [ ] `NOTICE` 明确引用 `openai/codex-plugin-cc` 与 `Agents365-ai/pi-plugin-cc` 的 Apache-2.0 来源；不复制无法确认许可的内容。
- [ ] `plugin.json` 只声明 plugin name、description、skill path、version 和 entry wrapper；不写用户机器绝对路径。
- [ ] `SKILL.md` 写触发条件、命令模板、read-only 默认、Pi 输出不是最终验证证据的边界。
- [ ] 写 `plugin-manifest.test.mjs` 校验 manifest 存在必需字段，skill path 指向真实文件。
- [ ] 运行 `node --test tests/pi-plugin-codex/plugin-manifest.test.mjs`，预期 pass。

### Task 2：CLI entrypoint 与 schema

**Files:**

- Create: `tools/plugin_sources/pi-plugin-codex/scripts/codex-pi.mjs`
- Create: `tools/plugin_sources/pi-plugin-codex/schemas/setup-output.schema.json`
- Create: `tools/plugin_sources/pi-plugin-codex/schemas/job-state.schema.json`
- Create: `tools/plugin_sources/pi-plugin-codex/schemas/job-result.schema.json`
- Create: `tests/pi-plugin-codex/codex-pi-cli.test.mjs`

**Steps:**

- [ ] 实现 `codex-pi.mjs --help`，列出 `setup|ask|review|adversarial-review|status|result|cancel`。
- [ ] 实现参数解析；未知命令返回 `{ok:false, blocker:"unknown_command"}` 且 exit code 2。
- [ ] 为 `setup --json` 实现 Pi 缺失 blocker，不调用网络。
- [ ] 写 schema 文件，与第 7、9 节字段保持一致。
- [ ] 写 CLI test：help、unknown command、setup pi missing 三个场景。
- [ ] 运行 `node --test tests/pi-plugin-codex/codex-pi-cli.test.mjs`，预期 pass。

### Task 3：Fake Pi fixture 与 RPC parser

**Files:**

- Create: `tools/plugin_sources/pi-plugin-codex/fixtures/fake-pi.mjs`
- Create: `tools/plugin_sources/pi-plugin-codex/scripts/lib/pi-rpc.mjs`
- Create: `tests/pi-plugin-codex/pi-rpc-fixture.test.mjs`

**Steps:**

- [ ] `fake-pi.mjs` 支持 `--mode rpc`，读取 stdin prompt，输出三类 fixture：success、malformed-jsonl、no-final-message。
- [ ] `pi-rpc.mjs` 启动 child process，传入 prompt，按行解析 JSONL/RPC event。
- [ ] parser 提取 final assistant message；没有 final 时返回 `rpc_no_final_message`。
- [ ] malformed JSONL 返回 `rpc_malformed_event`，不把 raw stderr 写进仓库。
- [ ] timeout 场景 kill 子进程并返回 `rpc_timeout`。
- [ ] 运行 `node --test tests/pi-plugin-codex/pi-rpc-fixture.test.mjs`，预期 pass。

### Task 4：Job control、state 与 cancel

**Files:**

- Create: `tools/plugin_sources/pi-plugin-codex/scripts/lib/job-control.mjs`
- Create: `tools/plugin_sources/pi-plugin-codex/scripts/lib/redact.mjs`
- Create: `tests/pi-plugin-codex/job-control.test.mjs`

**Steps:**

- [ ] 实现 project slug：优先 git remote/repo basename，fallback 到 cwd basename；只写 slug，不写完整路径。
- [ ] 实现 workspace root hash：`sha256(<absolute root>)`，JSON 只记录 hash。
- [ ] 实现 job id：`pi_YYYYMMDD_HHMMSS_<6hex>`。
- [ ] 写 state transition：`queued -> running -> succeeded|failed|canceled|timed_out`。
- [ ] `status --json` 只列当前 project slug 的 job 摘要。
- [ ] `result <job-id> --json` 只读当前 project slug 下 result。
- [ ] `cancel <job-id> --json` 对 running pid 终止子进程；pid 不存在返回 `stale_running_state`。
- [ ] 运行 `node --test tests/pi-plugin-codex/job-control.test.mjs`，预期 pass。

### Task 5：Git target 与 read-only guard

**Files:**

- Create: `tools/plugin_sources/pi-plugin-codex/scripts/lib/git-targets.mjs`
- Create: `tools/plugin_sources/pi-plugin-codex/scripts/lib/read-only-guard.mjs`
- Create: `tests/pi-plugin-codex/read-only-guard.test.mjs`

**Steps:**

- [ ] `git-targets.mjs` 实现 repo root、staged/unstaged file list、diff stat 获取；命令失败时返回 structured blocker。
- [ ] `read-only-guard.mjs` 实现 before/after fingerprint。
- [ ] 在 dirty worktree fixture 中验证 before dirty 允许，但 before/after 改变会 fail closed。
- [ ] 在 clean fixture 中验证 no-op Pi 不改变 fingerprint。
- [ ] 在 mutation fixture 中模拟 fake Pi 写文件，预期 `blocked:worktree_changed_by_read_only_pi`。
- [ ] 运行 `node --test tests/pi-plugin-codex/read-only-guard.test.mjs`，预期 pass。

### Task 6：Prompt 与 render

**Files:**

- Create: `tools/plugin_sources/pi-plugin-codex/prompts/ask.md`
- Create: `tools/plugin_sources/pi-plugin-codex/prompts/review.md`
- Create: `tools/plugin_sources/pi-plugin-codex/prompts/adversarial-review.md`
- Create: `tools/plugin_sources/pi-plugin-codex/scripts/lib/render.mjs`
- Create: `tools/plugin_sources/pi-plugin-codex/schemas/review-output.schema.json`
- Modify: `tests/pi-plugin-codex/pi-rpc-fixture.test.mjs`

**Steps:**

- [ ] `ask.md` 要求 Pi 只分析用户 stdin，不修改文件。
- [ ] `review.md` 要求 Pi 输出 severity、category、message、path、evidence；不得声称测试已通过。
- [ ] `adversarial-review.md` 要求 Pi 优先找反例、权限/回滚/状态污染风险和缺失验收。
- [ ] `render.mjs` 将 Pi 自由文本转为 `{summary, findings[]}`；无法结构化时放入 `summary` 并给 `findings: []`。
- [ ] test 覆盖 structured findings 和 freeform summary 两种输出。
- [ ] 运行 `node --test tests/pi-plugin-codex/pi-rpc-fixture.test.mjs`，预期 pass。

### Task 7：Installer、launcher 与 rollback receipt

**Files:**

- Create: `tools/install-pi-plugin-codex.ps1`
- Create: `tools/plugin_sources/pi-plugin-codex/launchers/codex-pi.ps1`
- Create: `tools/plugin_sources/pi-plugin-codex/launchers/codex-pi.cmd`
- Create: `tests/pi-plugin-codex/install-dry-run.test.mjs`

**Steps:**

- [ ] installer 默认 dry-run；需要 `-Apply` 才写用户级目录。
- [ ] dry-run 输出将复制的文件、目标相对路径、将写 receipt 的路径；不打印 secrets。
- [ ] `-Apply` 复制到 `%USERPROFILE%\.codex\tools\codex-pi\package`，并生成 wrapper。
- [ ] `codex-pi.ps1` 只转发到 package 内 Node entrypoint，不内嵌长 payload。
- [ ] `codex-pi.cmd` 调用 PowerShell wrapper，兼容 Windows PATH。
- [ ] install/update 前读取上一 receipt，写 rollback pointer。
- [ ] smoke 失败时不提升 active 状态；保留上一版本。
- [ ] 运行 `node --test tests/pi-plugin-codex/install-dry-run.test.mjs`，预期 pass。

### Task 8：治理文档和 checker

**Files:**

- Modify: `docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md`
- Modify: `docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md`
- Create: `tools/check_pi_plugin_codex_contract.py`
- Create: `tests/pi-plugin-codex/docs-boundary.test.mjs`

**Steps:**

- [ ] 把 `oh-my-pi` 小节改为 `Pi family 与 pi-plugin-codex 用户级适配`。
- [ ] readiness 表新增：`pi=on-demand`、`oh-my-pi/omp=reference-only`、`pi-plugin-codex=planned/on-demand`、`pi-plugin-cc=reference-only Claude Code only`、`pi-codex=non-goal reverse bridge`。
- [ ] OpenSpec 切片 6 改为 `Pi family sidecar`，owner lane 增加 `pi-plugin-codex`。
- [ ] receipt schema 增加 Pi binary、RPC smoke、job state path、read-only guard evidence。
- [ ] `check_pi_plugin_codex_contract.py` 防止把 `pi-codex` 标成依赖，防止把 `pi-plugin-cc` 标成可直接安装 Codex 插件，防止 `codex-ohmy` 被描述为 Pi launcher。
- [ ] 运行 `python .\tools\check_pi_plugin_codex_contract.py --root . --json`，预期 ok。

### Task 9：真实 Pi smoke（条件执行）

**Files:**

- Modify: `tools/plugin_sources/pi-plugin-codex/skills/pi-codex/SKILL.md`
- Modify: `docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md`（只记录脱敏结果摘要）

**Steps:**

- [ ] 运行 `codex-pi setup --json`。
- [ ] 如果 Pi 未安装，记录 `blocked:pi_not_installed`，不得把 lane 标为 active。
- [ ] 如果 Pi 已安装，运行 `codex-pi ask --read-only --stdin --json`，stdin 使用无敏感内容 smoke prompt。
- [ ] 运行 `codex-pi review --read-only --json`，确认 read-only guard `changed=false`。
- [ ] 只把脱敏 smoke summary 和 blocker/status 写入仓库文档；不写 provider、API key、完整用户路径。

### Task 10：总体验证、提交与本地集成

**Files:**

- Modify/Create: 上述所有文件。

**Steps:**

- [ ] 运行 `node --test tests/pi-plugin-codex/*.test.mjs`，预期 pass。
- [ ] 运行 `python .\tools\check_pi_plugin_codex_contract.py --root . --json`，预期 ok。
- [ ] 运行 `python .\tools\check_implementation_plan_rules.py --root . --json`，预期 ok。
- [ ] 运行 `python .\tools\run_openspec_guard.py --root .`，预期 ok。
- [ ] 运行 `python .\tools\check_precommit_update_archive.py --root . --json`，预期 ok。
- [ ] 提交 feature branch。
- [ ] 运行 `tools/ci/local_gate.ps1` 与 `tools/ci/local_mr_review.ps1`。
- [ ] 用户批准本地合入后，快进合入 local `main`；远程发布仍需单独明确批准。

## 12. P0 / P1 readiness gates

| Lane | 可用命令 | 必须证据 | 禁止事项 |
| --- | --- | --- | --- |
| P0 reference-only | 文档阅读 | 本方案 + OpenSpec proposal | 不安装、不调用 Pi。 |
| P0 planned/on-demand | `setup/status/result` dry-run | CLI tests + installer dry-run + receipt schema | 不写 plugin cache，不改 Codex config。 |
| P0 read-only active-candidate | `ask/review/adversarial-review --read-only` | fake Pi tests + real Pi smoke（如已安装）+ read-only guard `changed=false` | 不写当前 worktree，不把 Pi 输出当最终验证。 |
| P1 worktree-isolated rescue | `rescue --worktree-isolated` | 独立 worktree ownership + changed paths summary + Codex leader handoff | 不让 Pi 写主 worktree。 |

## 13. 验证计划

最小静态验证：

```powershell
python .\tools\check_implementation_plan_rules.py --root . --json
python .\tools\run_openspec_guard.py --root .
```

实现后验证：

```powershell
node --test tests/pi-plugin-codex/*.test.mjs
python .\tools\check_pi_plugin_codex_contract.py --root . --json
python .\tools\check_precommit_update_archive.py --root . --json
.\tools\ci\local_gate.ps1
.\tools\ci\local_mr_review.ps1
```

测试场景清单：

- fake Pi 返回 final assistant message。
- fake Pi 输出 malformed JSONL。
- fake Pi 无 final message。
- fake Pi 长时间无响应触发 timeout。
- cancel 能终止后台 job。
- status/result 不能跨 project slug 读取。
- read-only 命令前后 worktree fingerprint 不变。
- read-only mutation fixture 触发 `blocked:worktree_changed_by_read_only_pi`。
- `setup` 对 `pi` 缺失、provider 未配置、RPC 不可用分别返回稳定 blocker。
- docs checker 防止把 `pi-codex` 标为依赖。
- docs checker 防止把 `pi-plugin-cc` 标为可直接安装的 Codex 插件。
- docs checker 防止把 `codex-ohmy` 改写为 Pi launcher。
- installer dry-run 不写用户级目录，`-Apply` 才写 receipt。
- receipt 不包含 secrets、tokens、完整个人目录或 raw provider config。

## 14. Rollback 与清理

- Installer 每次 `-Apply` 前读取上一 receipt，并把上一 package 路径或版本摘要写为 rollback pointer。
- `tools/install-pi-plugin-codex.ps1 -Rollback <receipt-id>` 只恢复 `%USERPROFILE%\.codex\tools\codex-pi\package` 与 launcher；不删除 job 历史。
- `codex-pi status --repair --json` 只修复当前 project slug 的 stale running state；必须记录 pid 不存在或子进程已退出证据。
- `codex-pi cleanup --older-than-days <N> --json` 可作为 P0.5 增量；默认 dry-run，`--apply` 才删除旧 job result。
- 远程发布、personal marketplace 注册、全局 PATH 修改都不属于本方案默认 rollback 范围，必须另有用户确认和 receipt。

## 15. 对现有治理方案的更新要求

确认本方案后，更新：

```text
docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
```

建议变更：

- 标题从 `oh-my-pi 用户级安装和适配` 改为 `Pi family 与 pi-plugin-codex 用户级适配`。
- readiness 表新增：
  - `pi`：`on-demand`；
  - `oh-my-pi/omp`：`reference-only`；
  - `pi-plugin-codex`：`planned/on-demand`；
  - `pi-plugin-cc`：`reference-only, Claude Code only`；
  - `pi-codex`：`non-goal, reverse bridge`。
- OpenSpec 切片 6 从单一 `oh-my-pi` 改为 `Pi family sidecar`。
- owner lane 增加 `pi-plugin-codex`。
- 安装 receipt schema 增加 Pi binary、RPC smoke、job state path 和 read-only guard evidence。
- 完成前不得把 Pi family lane 标为 `active`；没有真实 Pi smoke 时最多是 `planned/on-demand`。

## 16. 风险与默认决策

风险：

- Pi 默认模型/provider 可能不同于 Codex，输出质量和成本不可由 Codex 完全控制。
- Pi 可能具备文件编辑能力；P0 必须通过 read-only prompt 和 worktree diff guard 约束。
- Claude Code 插件面与 Codex 插件面不同，直接 fork 会保留无效 `.claude-plugin` 结构。
- 后台任务可能残留；必须有 job state、pid、cancel、timeout 和 stale cleanup。
- 用户级安装可能污染个人环境；installer 必须 dry-run 默认、receipt 先行、rollback 可执行。

默认决策：

- P0 只做 read-only sidecar。
- P1 才做 worktree-isolated rescue。
- Codex leader 保持最终集成权。
- `pi-codex` 不纳入实现。
- `codex-ohmy` 不改变启动语义。
- 真实 Pi 缺失不是实现失败；它只让 smoke 状态保持 `blocked:pi_not_installed`。

## 17. 自检清单

- [x] 方向边界清楚：Codex -> Pi，而不是 Pi -> Codex。
- [x] 文件责任清楚：repo-local source、installer、tests、OpenSpec、governance docs 均有路径。
- [x] CLI contract 清楚：setup、ask/review/adversarial-review、status/result/cancel 都有 JSON 形状。
- [x] Read-only guard 可测试：before/after fingerprint 与 blocker 已定义。
- [x] Receipt/rollback 可测试：dry-run、apply、rollback pointer 已定义。
- [x] P0/P1 切分清楚：P0 不写当前 worktree，P1 独立 worktree。
- [x] 治理衔接清楚：现有 `user_level_mcp_skills_browser_cli_governance_plan.*` 更新点已列出。
- [x] 提交前验证命令清楚：implementation plan checker、OpenSpec guard、precommit gate、local gate、local MR review。
