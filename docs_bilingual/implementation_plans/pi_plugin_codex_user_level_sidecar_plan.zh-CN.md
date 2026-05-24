---
doc_id: pi_plugin_codex_user_level_sidecar_plan
lang: zh-CN
status: draft
plan_readiness: pending-user-confirmation
doc_class: implementation_plan
created_at: 2026-05-24
source_reference_file: reference_files/3.md
related_docs:
  - docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
  - docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md
  - docs_bilingual/governance/codex_user_level_skills_governance_policy.zh-CN.md
---

# `pi-plugin-codex` 用户级 Sidecar 实施方案（待确认）

## 0. 当前结论

本方案只实现 **Codex 中调用 Pi**，不实现 Pi 中调用 Codex。

结论：

- 可以 fork / adapt 一个 `pi-plugin-codex`，但不能把 `pi-plugin-cc` 的 Claude Code 插件面原样搬进 Codex。
- `pi-plugin-codex` 应是 **Codex personal plugin + `codex-pi` 用户级 wrapper**：
  - Codex 通过 plugin skill 识别“用 Pi 做 review / ask / adversarial review / 后台任务”的意图；
  - 真正执行由 `codex-pi` 调用 `pi --mode rpc`；
  - job state、result、cancel、read-only gate 和 receipt 由用户级 wrapper 管理。
- `pi-plugin-cc` 是主要参考：它已经把 `codex-plugin-cc` 的 Codex runtime 换成 Pi runtime，并定义了 `pi --mode rpc`、workspace-scoped job state、review prompt、result rendering 和 cancel 流程。
- `codex-plugin-cc` 只作为原始 upstream 和 Apache-2.0 NOTICE 来源参考；不复用 Codex app-server broker，因为本方案目标不是从 Claude Code 调 Codex。
- `pi-codex` 是反向桥接（Pi 内调用 Codex），本方案明确不实现、不安装、不作为依赖。
- `codex-ohmy` 仍只作为 wrapped Codex launcher；不得被改成 Pi launcher。

本方案状态为 `draft`。在用户确认前，不安装用户级插件、不修改 `C:\Users\lenovo\.codex\config.toml`、不写个人 marketplace、不调用真实 Pi 执行任务。

## 1. 目标与非目标

目标：

1. 在 Codex 会话中按需调用 Pi：
   - “用 Pi review 当前 diff”；
   - “用 Pi adversarial-review 质疑这个实现方向”；
   - “把这段问题交给 Pi 做只读分析”；
   - 后续可扩展到 worktree-isolated rescue。
2. 让 Pi 调用保持可审计：
   - 有 repo-local source of truth；
   - 有用户级安装 receipt；
   - 有 smoke test；
   - 有 rollback pointer；
   - 有 read-only / write gate。
3. 保持 Codex 主会话为 leader：
   - Pi 产物是 sidecar evidence；
   - Codex 决定是否采纳 Pi 建议；
   - Codex 负责最终 patch、验证和集成。

非目标：

- 不实现 Pi 内 `/codex:*` 命令。
- 不安装或依赖 `pi-codex`。
- 不让 Pi 默认直接修改当前 worktree。
- 不把 `pi-plugin-cc` 当成 Codex 原生插件。
- 不修改 plugin/vendor cache。
- 不把 Pi / oh-my-pi / OMP 当成 Codex、native subagent、native_omx 或 LangGraph 的替代品。

## 2. 目标形态

### 2.1 Repo-local source of truth

新增 repo-local 源码目录：

```text
tools/plugin_sources/pi-plugin-codex/
  .codex-plugin/plugin.json
  skills/pi-codex/SKILL.md
  scripts/codex-pi.mjs
  scripts/lib/pi-rpc.mjs
  scripts/lib/job-control.mjs
  scripts/lib/git-targets.mjs
  scripts/lib/render.mjs
  prompts/review.md
  prompts/adversarial-review.md
  schemas/review-output.schema.json
  LICENSE
  NOTICE
```

说明：

- `.codex-plugin/plugin.json` 采用 Codex personal plugin manifest。
- `skills/pi-codex/SKILL.md` 是 Codex 看到的路由面，告诉 Codex 何时调用 `codex-pi` wrapper。
- `scripts/` 是 clean-room wrapper + 从 `pi-plugin-cc` 允许复用/改写的 Pi RPC/job-control 逻辑。
- `LICENSE` 和 `NOTICE` 必须保留 `codex-plugin-cc` 与 `pi-plugin-cc` 的 Apache-2.0 attribution。

### 2.2 用户级安装产物

确认后由受控 installer 同步到用户级：

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

如果需要让 Codex app/plugin UI 识别该插件，再把 repo-local plugin 同步到个人 marketplace source。默认 personal marketplace 路径按 Codex plugin-creator 约定处理；本方案不直接编辑 plugin cache。

### 2.3 Codex 中的使用方式

用户在 Codex 中自然语言触发：

```text
用 Pi review 当前 diff
用 Pi adversarial-review 重点看权限和回滚
让 Pi 只读分析这个失败日志
```

Codex 路由到 `pi-codex` skill 后调用：

```text
codex-pi setup --json
codex-pi review --read-only --json
codex-pi adversarial-review --read-only --focus <text> --json
codex-pi ask --read-only --stdin --json
codex-pi status --json
codex-pi result <job-id> --json
codex-pi cancel <job-id> --json
```

P0 不提供 worktree 写入。P1 才考虑：

```text
codex-pi rescue --worktree-isolated --background --json <task>
```

其中 `--worktree-isolated` 必须创建或使用独立工作树，不能让 Pi 默认写当前主 worktree。

## 3. 运行时契约

### 3.1 Pi binary 发现

默认 binary 为 `pi`。

可选 override：

```text
CODEX_PI_BINARY=pi
CODEX_PI_BINARY=omp
```

规则：

- `setup` 只检测 binary、版本、RPC smoke 和 provider readiness；
- 不读取、打印或提交 `~/.pi/agent/models.json` 原文；
- provider API key 只通过 Pi 自身配置或环境变量使用，`codex-pi` 不持久化 secrets。

### 3.2 Pi RPC 调用

每个任务启动一个独立：

```text
pi --mode rpc
```

`codex-pi` 负责：

- 发送初始 prompt；
- 按 JSONL / RPC event 读取 Pi 输出；
- 提取 final assistant message；
- 把状态写入 workspace-scoped job state；
- 在 cancel 时终止对应 Pi 子进程；
- 在超时时写入 structured failure。

### 3.3 Read-only 默认

P0 的 `ask`、`review`、`adversarial-review` 必须只读：

- prompt 中明确要求 Pi 不修改文件；
- wrapper 在执行前后记录 `git diff --stat` 或等价摘要；
- 如果前后 worktree 变化，命令返回 `blocked:worktree_changed_by_read_only_pi`；
- Codex 只能把 Pi 输出作为建议，不能把它当作已经通过验证的 patch。

### 3.4 Job state

job state 至少包含：

- `job_id`：用于定位单次 Pi sidecar job 的稳定 ID。
- `project_slug`：用于隔离不同项目的 Pi job state。
- `workspace_root_hash`：用于脱敏标识 job 所属 checkout。
- `command`：记录触发的 `codex-pi` 子命令。
- `mode`：记录 read-only、background 或 future worktree-isolated 模式。
- `pi_binary`：记录实际调用的是 `pi` 还是显式 override。
- `model_hint`（如有）：记录用户传入的模型提示，不记录 provider secret。
- `status`: `queued | running | succeeded | failed | canceled | timed_out`，用于状态机查询。
- `started_at`：记录 job 启动时间。
- `finished_at`：记录 job 结束时间。
- `pid`：记录可取消的 Pi 子进程标识。
- `result_path`：记录脱敏结果文件位置。
- `redacted_error`：记录脱敏后的失败原因。

不得包含：

- API key；
- raw provider config；
- cookies / tokens；
- 完整个人目录；
- 未脱敏 shell 环境 dump。

## 4. 参考 fork 策略

### 4.1 从 `pi-plugin-cc` 复用的概念

允许参考/改写：

- `pi --mode rpc` 每任务一进程模型；
- background job state；
- review / adversarial-review prompt；
- structured result rendering；
- status/result/cancel command model；
- setup readiness report；
- `--model` / thinking effort pass-through。

必须移除或替换：

- `.claude-plugin/`；
- Claude Code slash command markdown；
- Claude hook lifecycle；
- Claude stop-time review gate；
- Claude subagent 定义。

### 4.2 从 `codex-plugin-cc` 继承的边界

保留：

- Apache-2.0 LICENSE / NOTICE attribution；
- review/adversarial-review/rescue/status/result/cancel 的概念分层；
- “sidecar agent 的输出不是最终集成证据”的边界。

不复用：

- Codex app-server broker；
- Codex auth/login 检查；
- 从 Claude Code 启动 Codex 的方向性逻辑。

## 5. 实施切片

### Slice 1：文档与治理确认

产物：

- 本方案；
- 更新 `user_level_mcp_skills_browser_cli_governance_plan.*` 中的 `oh-my-pi` 小节，把它扩展为 Pi family lane；
- 明确 `pi-codex` 为反向桥接 non-goal。

验收：

- 文档说明 Codex -> Pi 与 Pi -> Codex 的方向差异；
- 文档说明 `codex-ohmy` 不启动 Pi；
- 文档说明 `pi-plugin-cc` 是参考源而不是可直接安装到 Codex 的插件。

### Slice 2：Repo-local `pi-plugin-codex` scaffold

产物：

- `tools/plugin_sources/pi-plugin-codex/`；
- plugin manifest；
- `pi-codex` skill；
- `codex-pi` Node/PowerShell wrapper；
- fake Pi fixture tests。

验收：

- plugin manifest 通过 validator；
- `codex-pi setup --json` 在无 Pi 时返回 structured blocker；
- fake Pi 下 `ask/review/status/result/cancel` 通过。

### Slice 3：真实 Pi read-only smoke

产物：

- 如果本机安装了 `pi`，运行 read-only smoke；
- 如果未安装，记录 `blocked:pi_not_installed`，不得把 lane 标为 active。

验收：

- `codex-pi review --read-only --json` 不改变 worktree；
- result 可被 Codex 摘要；
- job state 可查询和清理。

### Slice 4：用户级安装与 receipt

产物：

- installer 同步 wrapper/plugin source 到用户级；
- `tool-updates` receipt；
- rollback pointer；
- smoke summary。

验收：

- 没有 receipt 时 lane 保持 `reference-only` / `on-demand`；
- 有 receipt、smoke、rollback 后才可提升到 `active-candidate`；
- plugin cache 未被手改。

### Slice 5：P1 worktree-isolated rescue（可选）

产物：

- `codex-pi rescue --worktree-isolated`；
- 独立 worktree ownership 记录；
- result-to-Codex handoff summary。

验收：

- Pi 不写当前主 worktree；
- 独立 worktree changed paths 可报告；
- Codex leader 决定是否移植 patch。

## 6. 验证计划

最小测试：

```text
node --test tests/pi-plugin-codex/*.test.mjs
python .\tools\check_implementation_plan_rules.py --root . --json
python .\tools\run_openspec_guard.py --root .
```

新增测试场景：

- fake Pi 返回 final assistant message；
- fake Pi 输出 malformed JSONL；
- fake Pi 长时间无响应触发 timeout；
- cancel 能终止后台 job；
- read-only 命令前后 worktree diff 不变；
- `setup` 对 `pi` 缺失、provider 未配置、RPC 不可用分别返回稳定 blocker；
- 文档 checker 防止把 `pi-codex` 标为本方案依赖；
- 文档 checker 防止把 `pi-plugin-cc` 标为可直接安装的 Codex 插件。

## 7. 更新现有治理方案的建议

确认本方案后，更新：

```text
docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md
docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
```

建议变更：

- 标题从 `oh-my-pi 用户级安装和适配` 改为 `Pi family 与 pi-plugin-codex 用户级适配`；
- readiness 表新增：
  - `pi`：`on-demand`
  - `oh-my-pi/omp`：`reference-only`
  - `pi-plugin-codex`：`planned/on-demand`
  - `pi-plugin-cc`：`reference-only, Claude Code only`
  - `pi-codex`：`non-goal, reverse bridge`
- OpenSpec 切片 6 从单一 `oh-my-pi` 改为 `Pi family sidecar`；
- owner lane 增加 `pi-plugin-codex`；
- 安装 receipt schema 增加 Pi binary、RPC smoke、job state path 和 read-only guard evidence。

## 8. 风险与默认决策

风险：

- Pi 默认模型/provider 可能不同于 Codex，输出质量和成本不可由 Codex 完全控制。
- Pi 可能具备文件编辑能力；P0 必须通过 read-only prompt 和 worktree diff guard 约束。
- Claude Code 插件面与 Codex 插件面不同，直接 fork 会保留无效 `.claude-plugin` 结构。
- 后台任务可能残留；必须有 job state、pid、cancel、timeout 和 stale cleanup。

默认决策：

- P0 只做 read-only sidecar。
- P1 才做 worktree-isolated rescue。
- Codex leader 保持最终集成权。
- `pi-codex` 不纳入实现。
- `codex-ohmy` 不改变启动语义。
