---
doc_id: reference6_reference7_reference8_user_project_live_runtime_plan
lang: zh-CN
status: active
plan_stage: R6-live-runtime
priority_order: Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit
remote_publication_allowed: false
browserbase_policy: disabled_by_user
---

# Reference 6/7/8 用户级与项目模板 Live Runtime 实施方案

## 目标

把 `reference_files/6.md`、`reference_files/7.md`、`reference_files/8.md` 中列出的能力安装或适配为 Codex 可用的用户级与项目模板表面，并用哈希脱敏 live runtime receipt 证明。Reference 6 与 Reference 7 已经是 checker-backed live runtime 基线；本方案新增 Reference 8，同时保持 6/7 基线不退化，并保持 Browserbase 禁用。

## 字段说明

- `ok=true` 表示 checker 成功结束且没有阻塞错误。
- `live_executed_count` 表示已经运行 Codex adapter smoke 并生成哈希脱敏 live runtime receipt 的必需能力数量。
- `disabled_count` 表示按政策有意排除的可选能力数量；本方案中只有 Browserbase 可以使用该状态。
- `optional_disabled:user_disabled_browserbase_service_lane` 表示 Browserbase 已按用户政策禁用，并且不阻塞 Reference 6/7/8 接受门。
- `dedupe` 表示重复 source URL 通过校验已有严格 live receipt 表示，而不是重复安装同一上游。

## 当前证据基线

- Reference 6 源列表有 9 个链接。当前严格 checker 证据显示检查成功、八个必需能力已有 live runtime receipt、一个可选 lane 被禁用，并且 Browserbase 是按用户明确政策禁用，所以不阻塞本接受门。
- Reference 6 MinerU 相关 lane 已 live-executed，包含 `MINERU_API_KEY` presence 与 MinerU/site/limit 的脱敏 service probe receipt。
- Reference 7 源列表有 25 个链接。当前严格 checker 证据显示检查成功且二十五个能力已有 live runtime receipt，并包含 `html-anything`、`open-design` 复用 Reference 6 receipt 的重复源处理。
- `reference_files/8.md` 当前有 16 个链接，尚无已提交的 Reference 8 runtime/checker/test 表面。
- 模板根目录为：`D:/PythonProject_General` 放 active reusable adapters，`D:/PythonProject_General_2` 放 inert/opt-in heavy adapters。

## 不可变政策

- 治理优先级固定为 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。
- 仅安装原始上游或仅复制源引用，永远不算 Codex live-executed 证据。
- 所有非 Codex 上游必须先有本地 Codex adapter/fork surface，才能标记为 live-executed。默认 fork 模式是本地 adapter/fork artifact；不创建或推送远端 fork。
- 不修改原生 Codex 程序文件。用户级安装可以写入 Codex-home 的 skills/tools/agents/state artifact，但不得从 `C:/Users/<user>/.codex/config.toml` 复制 secret 值。
- Browserbase 保持禁用。它的 disabled receipt 是预期状态，不能阻塞 Reference 6/7/8 完成。
- Receipt 必须哈希脱敏并便于人工确认：包含 tool/capability id、source URL、阶段、smoke kind、command hash、artifact hash、rollback pointer hash，以及不含 secret/私有原始路径的短标签。
- 外部 GUI/商业软件 lane 必须在需要时执行真实 launch/probe receipt；如果缺少桌面产品或 license，记录精确安装/配置/恢复步骤并继续其它独立 lane，不能伪造 live-executed。

## Reference 8 能力矩阵

| capability id | 来源 | 目标层 | 适配策略 | Live smoke 要求 |
| --- | --- | --- | --- | --- |
| `codex-visio-paper-figure-skill` | `https://github.com/pengjunchi0/codex-visio-paper-figure-skill` | user-level + General_2 inert | Codex skill adapter + Visio 桌面 probe wrapper | 真实 Microsoft Visio COM/process 启动或明确 executable/license receipt；fixture 写入论文图 receipt。 |
| `fireworks-tech-graph` | `https://github.com/yizhiyanhua-ai/fireworks-tech-graph` | General active | diagram/runtime wrapper adapter | 生成 SVG/PNG 技术图 fixture 并记录 artifact hash。 |
| `open-design-ref8` | `https://github.com/nexu-io/open-design` | General active | dedupe 到 Reference 6 | 校验 Reference 6 strict live receipt，并记录 Reference 8 alias receipt。 |
| `remotion` | `https://github.com/remotion-dev/remotion` | General active | Node/Remotion runtime wrapper adapter | 产生极小 render manifest/frame/video-placeholder artifact；如无法安装 Node package，则用确定性本地 fixture 加 package probe receipt。 |
| `cae-agent-hub` | `https://github.com/Cai-aa/CAE-Agent-Hub/tree/main` | General_2 inert | CAE workflow 本地 Codex fork/adapter | 可用时真实 CAE executable/license probe；否则记录精确 provision/resume receipt，不算 live-executed。 |
| `ansys-mcp-server` | `https://github.com/knewnothing-git/ansys-mcp-server` | General_2 inert | MCP adapter + Codex 边界 wrapper | 可用时真实 Ansys executable/license/MCP-server probe；否则记录精确 provision/resume receipt，不算 live-executed。 |
| `planning-with-files` | `https://github.com/OthmanAdi/planning-with-files` | user-level | Codex skill adapter | user-level state 下的 plan-from-files fixture。 |
| `compound-engineering-plugin` | `https://github.com/EveryInc/compound-engineering-plugin` | General active | Codex plugin/skill boundary adapter | 产生确定性工程计划 artifact 的工程插件 fixture。 |
| `pm-skills` | `https://github.com/phuryn/pm-skills` | user-level | Codex skill adapter | PM roadmap/task/spec artifact fixture。 |
| `scientific-agent-skills` | `https://github.com/K-Dense-AI/scientific-agent-skills` | user-level | Codex skill collection adapter | 科研 workflow fixture，记录文献/实验 artifact hash。 |
| `agency-agents-zh` | `https://github.com/jnMetaCode/agency-agents-zh` | user-level | Codex native-agent TOML adapter | 生成并校验中文 agent TOML，包含必需顶层字段。 |
| `understand-anything` | `https://github.com/Egonex-AI/Understand-Anything` | user-level + General active | 多模态/文档 skill adapter | 文档理解 fixture，记录脱敏内容/路径 hash。 |
| `zvec` | `https://github.com/alibaba/zvec` | General active | vector/search wrapper adapter | 本地 vector/index/query fixture 和 hash receipt。 |
| `system-prompts-and-models-of-ai-tools` | `https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools` | General_2 inert | 脱敏 reference-index adapter | 仅索引 metadata；不复制受限 prompt 正文或 secret。 |
| `markitdown` | `https://github.com/microsoft/markitdown` | user-level + General active | document-conversion runtime wrapper | 把极小 fixture 转成 Markdown 并记录输出 hash。 |
| `headroom` | `https://github.com/chopratejas/headroom` | user-level + General active | context-budget analyzer adapter | 分析小 fixture 并记录 budget/report hash。 |

## 实施阶段

## Current Status

<!-- CURRENT_STATUS_START -->
Status: Stage A governance package is active and frozen for Stage B implementation. The plan file is registered so Reference 8 runtime/checker/template work can cite this local-main governance package.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Stage B: add Reference 8 manifest, runtime CLI, checker, and tests.
- Stage C: run user-level adapter install and hash-redacted smoke receipts.
- Stage D: sync `D:/PythonProject_General` and `D:/PythonProject_General_2` template surfaces.
- Stage E: run Reference 6/7/8 strict checks, repository gates, local MR review, and local-main integration.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Stage A plan commit: `57c44ecb70fbf2f7aea4aa30dc200dc12d9acdcf`.
- Stage A registry fix: this docs-only governance package registers the plan as active before non-document implementation.
- Runtime evidence target: `.omx/worktree-task-receipt.json` and Reference 8 install receipts under user-level Codex state.
<!-- EVIDENCE_INDEX_END -->

### Stage A：冻结本实施方案

1. 创建/更新英文方案与中文镜像。
2. 记录 Reference 6/7 live-runtime 基线与 Reference 8 逐链接矩阵。
3. 运行不依赖 Reference 8 实现的仓库 plan/precommit/OpenSpec guard。
4. 在隔离分支/worktree 提交方案。
5. 文档阶段可行时运行 local gate 与 local MR review，然后用项目 local-flow helper 快进/本地合入 `main`。
6. 停在远端发布门禁。

### Stage B：构建 Reference 8 源码真相

1. 新增 `tools/reference8_capability_install/manifest.json`，包含 16 个能力、dedupe policy、target layers、live runtime targets、disabled/blocked protocol 与 generated policy。
2. 新增 `tools/reference8_capability_install/runtime.py`，提供遵循 Reference 6/7 约定的 `plan`、`apply`、`check`、`smoke` 子命令。
3. 新增 `tools/reference8_capability_install.py` 薄 CLI wrapper。
4. 新增 `tools/check_reference8_capability_install.py`，校验 manifest、runtime plan、registry/CI wiring、用户级安装 receipt、smoke receipt、live-executed 状态与模板同步。
5. 新增 `test/reference8_capability_install.test.py`，覆盖 manifest policy、disabled/non-blocking 行为、dedupe 到 Reference 6、receipt 脱敏与模板同步检查。

### Stage C：安装用户级 adapters 并生成 receipts

1. 运行 Reference 8 `apply --apply --operator-confirmation`，`--codex-home` 默认使用当前用户 Codex home；模板根存在时才使用 `--sync-templates`。
2. 为用户级能力写入 Codex skills，并为 `agency-agents-zh` 写入 agent TOML。
3. 在 `state/reference8-capability-install` 与 `tools/reference8-capability-install` 下写入用户级 tools/state/receipts。
4. 对每个能力运行 Reference 8 smoke。
5. Visio/CAE/Ansys 如存在真实桌面/process/license/MCP 证据则记录；否则记录精确补全命令/路径并保持 lane blocked，不能声称 live-executed。

### Stage D：同步项目模板

1. 更新 `D:/PythonProject_General`，加入 active reusable Reference 8 adapters 与 checker/local-gate 注册。
2. 更新 `D:/PythonProject_General_2`，加入 heavyweight、商业、敏感 lane 的 inert/opt-in Reference 8 adapters。
3. 如果模板仓库治理要求提交，则分别提交模板更新。
4. 保留模板仓库中无关 dirty 文件；不得覆盖消费项目状态。

### Stage E：验证、集成、清理

1. 用 live-executed 与 template-sync 参数运行 Reference 6、Reference 7、Reference 8 严格 checker。
2. 运行 `python tools/run_openspec_guard.py --root .`。
3. 运行 `tools/ci/local_gate.ps1` 与 `tools/ci/local_mr_review.ps1`。
4. 提交实现变更，运行 local-flow helper 合入本地 `main`，保留 rollback/completed-claim 证据并清理已合入 worktree/branch。
5. 汇报 local `main` 与远端 ahead/behind 状态，并停在远端发布门禁。

## 协同计划

- Native experts：平台允许时使用 explorer/researcher/verifier/test-engineer/code-reviewer 做只读映射、外部源分类、测试充分性与最终审查；只有实际 spawn 并吸收 fan-in 后才能声明 expert evidence。
- Durable team：Stage A 冻结后，把 Stage B-D 切成 Reference 8 runtime/checker、tests/CI、user-level receipts、template sync、external desktop probes 等独立执行片。
- Persistent team：仅当已有冻结方案且两个以上独立执行片活跃时启用；否则主会话保持 leader 与集成责任人。
- 主会话负责最终 fan-in、冲突解决、最终 gate 与本地 main 集成。

## 接受标准

- Reference 6 strict checker 保持 `ok=true`，Browserbase 按用户政策禁用，所有非禁用能力 live-executed。
- Reference 7 strict checker 保持 `ok=true`，且模板同步已验证。
- Reference 8 checker 报告所有非外部缺失能力 installed、smoke-tested、live-executed；外部商业桌面 lane 要么有真实 launch/probe receipt，要么有明确 provision/resume 记录且不被伪标完成。
- `D:/PythonProject_General` 与 `D:/PythonProject_General_2` 包含预期 Reference 8 模板表面与 checker 注册。
- 所有 receipts 哈希脱敏，不复制 secret 值，不触碰远端发布。
- 实现与模板变更按照 local-main-first 工作流提交并集成到本地 `main`。


