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

本文基于 `reference_files/2.md` 中列出的 Comet、OpenSpec 和 Superpowers 上游项目链接、本地 mp4 的同名主题证据，以及 `PMP/PMP_MD/` 下已有 PMBOK8 缓存材料。

本次会话无法完整转录本地 mp4：`OPENAI_API_KEY` 未设置，且本地 ffmpeg shim 在沙箱内不可运行。因此本次首轮升级以 README 可确认行为作为具体依据，并把视频精听/转录差异留给后续变更处理。

## 3. 分层契约

所有 Comet 风格 OpenSpec 工作都使用以下分层：

| 层 | 所有者 | 职责 |
| --- | --- | --- |
| WHAT | OpenSpec | 变更 proposal、requirements、scenarios、tasks、spec lifecycle、validation、archive 与 delta-to-main spec sync。 |
| HOW | Superpowers | 头脑风暴、技术设计、实现计划、TDD、subagent-driven development、code review 与分支收尾。 |
| CONTROL | Comet | `/comet` 入口路由、阶段识别、workflow state、guard scripts、resume 与 archive evidence checks。 |

Skills 仍然是 workflow instruction surfaces。Comet skill、OpenSpec skill、Superpowers skill 或 profile 调用不是 native subagent 证据。Native subagents 仍然是由主会话 leader 侧显式生成并 fan-in 的角色。

文档目录边界：

- `docs_bilingual/` 是正式、持久化的文档库，用于 governance、implementation plans、product notes、startup summaries，以及已登记的中英文文档对。
- `docs/superpowers/` 只保留给 Comet state 引用的 Superpowers runtime artifacts，例如 `docs/superpowers/specs/` 下的设计文档，以及 `docs/superpowers/plans/` 下的实施计划。
- 不要把 `docs_bilingual/` 的正式文档复制到 `docs/`；只有当 workflow 明确记录这些路径时，才把 Superpowers runtime artifacts 放入 `docs/superpowers/`。

## 3A. `/plan` 之后的本地治理包

当会话退出 `/plan` 且后续任务不是纯文档任务时，第一个可执行切片是本地治理包，而不是直接进入 runtime 或代码实现。

治理包必须从 `docs_bilingual/` 开始：

- 按内容选择最合适的既有 `docs_bilingual/` 目录与 doc_class，例如 governance、implementation plans、guides、memory 或 product lifecycle notes；
- 有合适既有文件时优先更新既有文件；
- 只有没有合适既有文件能承载该决策时，才新建中英文文档对；
- 不要把 `implementation_plans/` 当成唯一可用的 `docs_bilingual/` 目标目录。

`docs_bilingual/` 更新明确后，再由该内容判断是否需要派生更新：

- 只有当任务需要 durable capability/spec lifecycle evidence、stable requirements 或 Comet/OpenSpec change 时，才更新 `openspec/`；
- 只有当任务需要 Superpowers runtime artifacts 或需要改变 `docs/` 目录契约本身时，才更新 `docs/`；
- 不得仅仅因为更新了 `docs_bilingual/` 文件，就机械创建 `openspec/` 或 `docs/` 文件。

该治理包随后按仓库完整本地提交流程执行到本地 `main` 合入，并停在远端发布门。此规则不授权 GitLab push、GitLab MR 变更或 GitHub sync。

脚本化执行约束：

- `tools/check_plan_exit_execution_governance.py`：检查包含非文档执行的提交范围必须先以 docs-only 本地治理包开头，且第一包必须触达 `docs_bilingual/`。
- `tools/complete_local_flow_to_remote_gate.py`：执行或预演从干净 feature branch 到 ff-only 合入本地 `main` 的完整本地提交流程，并在远端发布门前停止。
- `tools/check_local_flow_scripted_enforcement.py`：校验本 policy、`完整提交流程.md` 和本地流程脚本持续存在并互相链接。
- `tools/ci/local_mr_review.ps1`：在本地 MR review 中运行 `/plan` 后提交范围 checker，防止非文档执行绕过治理包。

每次更新或创建 implementation plan 也适用同一套完整本地提交流程。方案对更新并提交后，默认本地动作不是停留在 feature branch 等待，而是把本地 integration package 完成到 local `main`，然后停在远端发布门。

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

PMBOK8 Project Management Focus Areas 映射：

| Comet phase | PMBOK8 focus area | 仓库解释 |
| --- | --- | --- |
| Open | Initiating | 在打开持久化 OpenSpec artifacts 前，确认为什么值得做、成功如何判断，以及哪些 stakeholders 或 constraints 需要被识别。 |
| Design | Planning | 裁剪交付方式、范围、风险、验收证据，以及 Superpowers design 或 plan artifacts；Planning 不是一次性瀑布步骤。 |
| Build | Executing | 协调实现、TDD、review，以及 branch 或 worktree 执行纪律。 |
| Verify | Controlling | 在允许完成声明前，对照 requirements、validation evidence、risks、branch state 和 acceptance expectations 检查偏差。 |
| Archive | Closing | 通过 delta specs sync、verification evidence 保存、archive history 和可检索知识沉淀来关闭 change。 |

Monitoring 是横切 focus area，不是第六个 Comet phase。它通过 phase detection、transition guards、evidence gates、verify-fail feedback、archive readiness checks 和显式 operator decisions 实现。这样可以保持 PMBOK8 process guidance 的 non-prescriptive 特征：focus areas 可以在预测型、适应型和混合型工作中反复、重叠、按项目裁剪地出现，同时 Comet 状态机仍保持 `Open -> Design -> Build -> Verify -> Archive`。

Runtime Monitoring 不只是被动检查或阻拦。如果当前阶段发现前序关注领域不充分，Comet 可以记录 control decision，并把 active change 回退到 `open`、`design`、`build` 或 `verify` 中需要返工的阶段。回退必须保留原因和迭代次数，使工作流表现为适应型/混合型控制循环，而不是单向瀑布。

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
