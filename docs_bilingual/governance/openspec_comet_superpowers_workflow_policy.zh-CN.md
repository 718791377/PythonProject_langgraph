---
doc_id: openspec_comet_superpowers_workflow_policy
lang: zh-CN
doc_class: governance
status: active
translation_of: docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md
---

# OpenSpec Comet Superpowers 工作流策略

## 1. 目的

本文定义本仓库面向 Comet 控制的 OpenSpec + Superpowers 工作流的目标形态。

该目标是一个增量控制模型：

- OpenSpec 管 WHAT：proposal、requirements、delta specs、tasks、validation、lifecycle、archive 和 sync。
- Superpowers 管 HOW：brainstorming、technical design、implementation planning、test-driven development、subagent-driven development、code review 和 branch finishing。
- Comet 管 WHEN & NEXT：阶段分发、workflow state、transition guards、resume 和 evidence gates。

Comet 不替代 OpenSpec、Superpowers、native Codex subagents、native_omx 或 LangGraph。它只把 OpenSpec 和 Superpowers 编排成一个可恢复、可校验的工作流表面。

## 2. 证据基础

本文基于 `reference_files/2.md` 中列出的 Comet、OpenSpec 和 Superpowers 上游项目链接，以及本地 mp4 的同名主题证据。

本次会话无法完整转录本地 mp4：`OPENAI_API_KEY` 未设置，且本地 ffmpeg shim 在沙箱内不可运行。因此本次首轮升级以 README 可确认行为作为具体依据，并把视频精听/转录差异留给后续变更处理。

## 3. 分层契约

所有 Comet 风格 OpenSpec 工作都使用以下分层：

| 层 | 所有者 | 职责 |
| --- | --- | --- |
| WHAT | OpenSpec | 变更 proposal、requirements、scenarios、tasks、spec lifecycle、validation、archive 与 delta-to-main spec sync。 |
| HOW | Superpowers | 头脑风暴、技术设计、实现计划、TDD、subagent-driven development、code review 与分支收尾。 |
| CONTROL | Comet | `/comet` 入口路由、阶段识别、workflow state、guard scripts、resume 与 archive evidence checks。 |

Skills 仍然是 workflow instruction surfaces。Comet skill、OpenSpec skill、Superpowers skill 或 profile 调用不是 native subagent 证据。Native subagents 仍然是由主会话 leader 侧显式生成并 fan-in 的角色。

## 4. 五阶段工作流

完整 Comet 控制工作流是：

```text
Open -> Design -> Build -> Verify -> Archive
```

阶段归属：

1. Open：OpenSpec 负责 proposal、初始 design 和 task breakdown。
2. Design：Superpowers 负责深度 design、brainstorming 和设计文档细化。
3. Build：Superpowers 负责实现计划、TDD、subagent-driven development、code review 和 branch/worktree 执行纪律。
4. Verify：OpenSpec 和 Superpowers 共同参与；验证必须产生证据，而不能只产生自我声明。
5. Archive：OpenSpec 负责 delta-to-main spec sync、archive movement 和 archive status。

hotfix 或 tweak 等 preset workflow 只有在跳过步骤被显式记录时，才可以跳过 brainstorming 或 full planning。Verify 与 Archive 仍然必须由证据门控。

## 5. 状态与恢复契约

Comet 风格工作流不得只依赖 chat history 或未经校验的 Markdown 推断。

状态模型必须解耦：

- `.openspec.yaml` 或已安装 OpenSpec 等价物负责 spec lifecycle 和 change metadata。
- `.comet.yaml` 或仓库批准的等价物负责 workflow phase、preset、design document path、plan path、build_mode、isolation、verify_mode、verify_result、verification_report、branch_status、verified_at 和 archived state。

恢复行为：

- `/comet` 或等价入口点检测 active change 与当前 phase。
- `/comet continue` 或等价 resume path 从持久化状态恢复。
- 如果存在多个 active changes，operator 必须先选择目标 change，然后才允许继续执行。

## 6. Guard 与证据契约

阶段推进必须由可执行检查门控。

guard 必须对以下情况 fail closed：

- 缺少 proposal、spec、design、task、plan 或 report artifacts；
- phase 值无效或存在非法 phase jump；
- 离开 Build 前缺少 build_mode 或 isolation 决策；
- full workflow 中出现 `build_mode: direct`，但没有 `direct_override` 或等价显式例外；
- Verify 通过前缺少 `verification_report`；
- Verify 通过前 `branch_status` 未处理；
- 没有 verification evidence 就尝试 archive。

guard failure 应使用 `[HARD STOP]` 或等价 hard-stop 风格，并给出可执行修复建议。

Archive 需要 completed tasks、validation evidence、已有 verification report、已处理 branch state，以及 delta-to-main spec sync。

## 7. 安装与变更边界

本文档不是运行时资产变更授权。

以下动作需要显式操作员批准，或需要后续 OpenSpec change 提供明确写入范围与 rollback path：

- `npm install -g @rpamis/comet` - 全局安装 Comet package。
- `comet init` - 初始化 Comet workflow，可能写入 platform skills 和 scripts。
- `comet update` - 更新 Comet package 或已安装 skill。
- `comet doctor` - 当诊断命令会触发修复或写入动作时。
- 安装 Superpowers plugin files。
- 覆盖 `.codex/skills` 内容。
- 编辑 `C:\Users\lenovo\.codex\config.toml`。

如果 Comet 已经安装且作用域被限制在目标仓库，`comet status --json` 这类只读命令可以用于检查。

## 8. 仓库作用域边界

`D:\PythonProject_langgraph` 只拥有本策略和 Codex 编排线的 repo-local OpenSpec artifacts。

本文不授权写入：

- `D:\PythonProject_langgraph` 之外的消费者仓库；
- 本仓库之外的通用项目根目录；
- 任何消费者项目的 `.omx/state` 目录。

消费者项目如需采用 Comet/OpenSpec/Superpowers 工作流，必须在各自仓库中维护自己的 OpenSpec artifacts、repo-local state、validation 和 publication decision。

## 9. 验证

本策略由 `tools/check_openspec_comet_superpowers_policy.py` 支撑。该脚本验证双语治理面、registry 条目，以及 Comet/OpenSpec/Superpowers 核心边界术语。

将本升级视为完成前，运行：

```powershell
python tools/check_openspec_comet_superpowers_policy.py --root . --json
python test/run_openspec_guard_json.test.py
python tools/check_document_governance_rules.py --root . --json
openspec validate --all
```

如果 checker 失败，先修复 policy、registry 或 OpenSpec change，再继续。
