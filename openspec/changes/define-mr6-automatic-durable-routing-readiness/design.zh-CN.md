## 背景

active durable-state isolation queue 一直按小 MR 切片推进。MR 1 到 MR 5 已完成。当前 queue 把 MR 6 写成 readiness review 或 automatic durable routing hookup。

仓库证据显示 runtime hookup 已经在更早的 team-mode P5 线中存在：

- `openspec/specs/codex-user-level-team-mode-automatic-team-routing/spec.md` - automatic durable-team routing helper 与 backend-aware routing decisions 的稳定 spec。
- `tools/install-codex-user-level-team-mode.ps1` - 生成 `omx-team-auto.ps1` 这个用户级 automatic durable-team helper 的仓库源码。
- `test/install-codex-user-level-team-mode.test.ps1` - 覆盖 `effective_lane`、legacy selector rejection、empty unmanaged residue handling、native_omx launch/reuse/switch/shutdown，以及 LangGraph graph-signal selection 的测试。
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - active team-mode plan，已经把 P5 automatic durable-team routing 标为 implemented。

## 目标 / 非目标

**目标：**

- 在开启新 runtime work 前，把 MR 6 queue 与现有 runtime evidence 对账。
- 保持本 MR 只做 documentation 与 spec-status synchronization。
- 让冷启动会话的下一步更明确：不要重复 P5；只有用户明确要求 runtime exercise 时，才另开 future live smoke/adoption gate。

**非目标：**

- 不启动、复用、切换或关闭 durable teams。
- 不编辑 user-level Codex config 或 generated user-level helper files。
- 不改写 repo-local durable state。
- 不修改 MCP Router 或 direct MCP configuration。

## 决策

1. 把 MR 6 作为本 queue 的 readiness-review closeout。
   - 理由：automatic durable routing helper、stable specs 和 tests 已经存在。再次做 runtime hookup 会重复工作。
   - 备选方案：再实现一个 automatic routing helper。拒绝原因：`omx-team-auto.ps1` 已经生成并测试。

2. 更新 plan-status synchronization，而不是 runtime code。
   - 理由：缺陷是 rollout wording 过期，不是 runtime behavior 缺失。
   - 备选方案：不更新 plan 直接 no-op archive。拒绝原因：冷启动会话仍会看到 MR 6 是 pending hookup work。

3. 把 future live smoke/adoption gate 独立出来。
   - 理由：真正启动 durable team 是 runtime action，必须在明确项目选择和 operator consent 下进行。

## 风险 / 取舍

- 风险：把 MR 6 标记为 complete 可能被误解为最终 production-grade persistent team draft 已完成。缓解：明确说明这只关闭 small-step MR 6 queue item，最终 draft 仍是 north-star。
- 风险：不改 runtime 可能漏掉当前安装漂移。缓解：引用 tests 与 helper generation 作为源码证据，并把 future live smoke 留作单独显式步骤。
