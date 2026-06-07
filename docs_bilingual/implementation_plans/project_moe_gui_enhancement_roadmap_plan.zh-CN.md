---
doc_id: project_moe_gui_enhancement_roadmap_plan
lang: zh-CN
status: active
plan_readiness: ready-for-implementation
implementation_status: planned
implementation_lane: project_moe_gui_enhancement
parent_plan: docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/project_moe_gui_enhancement_roadmap_plan.md
created_at: 2026-06-07
last_reviewed_at: 2026-06-07
scope: project_moe_gui_post_0_2_30_enhancement
related_docs:
  - docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md
  - docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.zh-CN.md
  - docs_bilingual/implementation_plans/project_moe_gui_double_click_launch_repair_plan.zh-CN.md
---

# Project MOE GUI 增强路线图实施方案

> **For agentic workers:** REQUIRED SUB-SKILL：使用 `superpowers:executing-plans` 逐项实施；只有当前平台和用户授权允许 native delegation 时，才使用 `superpowers:subagent-driven-development`。所有实施事项使用 checkbox 跟踪；每个事项完成后先运行局部验证，再进入下一事项。

**Goal:** 将 Project MOE GUI 从当前可用的本地 operator console 提升为更接近产品级的本地 GUI：具备持久化专家工作台产物、更严格的视觉门禁、更好用的 Sessions 页，以及只读的多项目安装/升级可视化能力。

**Architecture:** `D:/PythonProject_langgraph` 继续作为 Phase 2 工具链 source of truth，目标项目继续作为 Phase 1 owner。GUI 可以生成结构化 handoff artifact 和本地 runtime history，但不得直接启动 Codex、native subagent、durable team、LangGraph workflow、模型 API，也不得绕过目标项目 Phase 1 CLI gate。

**Tech Stack:** Python CLI/checkers、PySide6 shared runtime、QML Material shell、JSON view model、目标项目 Phase 1 CLI contract、本地 runtime artifact 目录、本地 CI manifest、local-first Git flow。

---

## 0. 当前复核结论

Project MOE GUI `0.2.30` 已经可以作为真实 PySide6 operator console 使用，但剩余缺口已经足够独立，应建立子方案，而不是继续把父方案无限膨胀。

完整性基线：

| 领域 | 当前状态 | 本方案闭环 |
| --- | --- | --- |
| 视觉门禁 | 覆盖主要页面的 `1180x720`，可检查非滚动容器溢出 | 多尺寸、长文本、高密度 session/lens fixture、本地 gate 接入 |
| Expert Workbench | 生成 handoff package preview 和 clipboard/runtime package | 草稿、历史、session 绑定、筛选/复用、按 carrier 结构化导出 |
| Sessions 页 | 支持 session 开关、lens/category 应用/清空和 readback | 搜索、筛选、排序、生效状态解释、override 冲突提示 |
| UI 细节 | 已有卡片、侧边栏、暗色主题 | 空状态、错误态、加载态、帮助说明和布局细节 |
| 多项目操作 | installer/updater/checker 以 CLI 形式存在 | 只读安装状态面板、版本落后检测、dry-run 更新计划、rollback 提示 |

状态解释：

- `status: active` 表示这是 post-`0.2.30` GUI 增强的当前 active 子路线图。
- `implementation_status: planned` 表示本文记录有序实施范围；不代表 runtime 已经交付。
- 父方案继续负责 Project MOE GUI 的整体架构和 readiness lane 治理。
- 本方案不授权远端发布；GitLab/GitHub 仍需用户后续明确授权。

## 当前状态
<!-- CURRENT_STATUS_START -->

- [x] 状态：post-0.2.30 Project MOE GUI 增强 active 子实施方案。
- [x] 实施状态：planned；本文不声明任何 runtime 增强切片已经完成。
- [ ] 下一实施批次：Slice A 视觉门禁常态化。

<!-- CURRENT_STATUS_END -->

## 任务积压
<!-- TASK_BACKLOG_START -->

- [ ] Slice A：视觉渲染门禁支持多尺寸与 fixture profile。
- [ ] Slice B：Expert Workbench 增加草稿、历史、session 绑定、筛选和结构化导出。
- [ ] Slice C：Sessions 页增强搜索、筛选、排序和生效状态解释。
- [ ] Slice D：增加产品级 loading、empty、error、help 状态。
- [ ] Slice E：增加只读多项目安装/升级状态面板。

<!-- TASK_BACKLOG_END -->

## 证据索引
<!-- EVIDENCE_INDEX_START -->

- Pending implementation evidence is pending future runtime slices.

<!-- EVIDENCE_INDEX_END -->

## 1. 边界与 carrier 语义

- MOE 专家是镜头或路由语义，不是执行载体。
- 主会话、native subagent、durable team、LangGraph workflow 是可以消费 MOE brief 的 carrier。
- Expert Workbench 可以为 `main-session`、`subagent`、`durable-team`、`langgraph-workflow` 生成 carrier-shaped artifact。
- 本方案内 Expert Workbench 不得直接执行这些 carrier。
- 未来“一键执行 carrier”必须单独治理，因为它需要平台 subagent 可用性、durable-team 阈值证据、LangGraph state 证据和审批门禁。
- GUI history 和 draft artifact 是 runtime artifact；默认不提交到目标项目 git。
- GUI 绝不能把目标项目私有 `MOE.md` 正文或 native agent developer instructions 复制到共享工具链产物。

## 2. Runtime artifact 契约

默认目标项目 runtime 目录：

```text
<target-project>/.project-runtime/project_moe_gui/
  workbench_drafts/
  expert_history/
  handoff_queue/
  visual_gate/
```

最小 handoff artifact 字段：

```json
{
  "schema_version": 1,
  "artifact_kind": "project_moe_gui_handoff",
  "created_at": "<iso8601>",
  "target_project": "<redacted-or-normalized-project-path>",
  "session_display_id": "<display-only-session-id>",
  "session_key_hash": "<stable-hash>",
  "selected_lenses": [],
  "selected_categories": [],
  "handoff_target": "main-session|subagent|durable-team|langgraph-workflow",
  "task_template_id": "<template-id>",
  "brief_text": "<operator-provided-brief>",
  "status": "draft|copied|queued|completed|superseded"
}
```

规则：

- `session_display_id` 只用于显示，不得暴露 raw private session id。
- `brief_text` 是 operator 输入内容，不是私有提示源内容。
- `selected_lenses=[]` 保持既有语义：除非 session 被关闭，否则该 session 允许全部可用镜头。
- 历史文件必须 append-only 或通过显式时间戳做状态迁移；不得静默覆盖 completed artifact。
- dirty target project 对写入/更新仍 fail closed；只读状态查看和历史读取可以继续。

## 3. 实施清单

### Slice A：视觉门禁 P0

- [ ] 增加默认视觉尺寸：`1180x720`、`1366x768`、`1440x900`。
- [ ] 为 visual render checker 增加 `--fixture-profile default|long-content|dense-sessions`。
- [ ] 增加长 session 名、长 lens 名、多 session、多 category、多 lens 的生成 fixture。
- [ ] 真实 PySide6 offscreen 渲染保持为显式命令，不作为每次单测默认重负载。
- [ ] 增加 size parsing、default sizes、fixture generation、overflow detection 单测。
- [ ] 如果轻量视觉 checker 测试尚未覆盖，则注册到本地 CI manifest。
- [ ] 新工具链安装到 `D:/PythonProject_paper_suggest` 后运行目标项目视觉验证。

### Slice B：Expert Workbench P1

- [ ] 增加 handoff package 草稿保存。
- [ ] 增加 expert result history 记录和状态迁移。
- [ ] 增加 brief 与 session 绑定。
- [ ] 增加按 session、handoff target、lens、category、status 的筛选。
- [ ] 为每个 handoff target 增加结构化导出动作。
- [ ] 保持“导出”只代表 artifact 生成或 clipboard copy，不代表执行 carrier。
- [ ] 增加 artifact schema、脱敏边界、draft/history 生命周期、carrier export shape 测试。

### Slice C：Sessions 可用性 P1

- [ ] 增加 Sessions 搜索文本框。
- [ ] 增加 Sessions 过滤模式：all、enabled、disabled、blocked 或 invalid。
- [ ] 增加 Sessions 排序键：last seen、display id、label、effective lens mode。
- [ ] 展示选中 session 的 effective lens/category mode。
- [ ] 展示 project default 与 session override 冲突提示。
- [ ] 增加无 session、无搜索结果、readiness blocked 空状态。
- [ ] 增加 view-model filtering、sorting、explanation text 测试。

### Slice D：UI 产品化 P2

- [ ] 为主 QML 页面增加 loading、empty、error、help 状态。
- [ ] 在不引入新 GUI framework 的前提下收紧卡片间距和操作层级。
- [ ] QFluentWidgets 在许可证审查完成前只保留为可评估的可选方向。
- [ ] 如果继续把 QFluentWidgets 列为未来选项，增加许可证审查说明。
- [ ] 扩展视觉 fixture 覆盖 empty/error/loading/help 状态。

### Slice E：多项目安装/升级面板 P2

- [ ] 增加只读 project registry 输入契约。
- [ ] 只对显式列出的项目做 install-status scanning。
- [ ] 展示 installed GUI version、source toolchain version、dirty status、readiness status、version lag。
- [ ] 生成 dry-run update plan 和 rollback hint，但不写目标项目。
- [ ] 真实 update/apply 操作继续受既有 installer/updater gate 保护。
- [ ] 增加 registry parsing、stale version detection、dirty fail-closed、dry-run output 测试。

## 4. 验证计划

每次本地提交前的最小验证：

```powershell
python .\tools\check_precommit_update_archive.py --root . --json
python .\test\project_moe_gui_toolchain.test.py
```

集成前 runtime 验证：

```powershell
python .\tools\project_moe_gui_toolchain\visual_render_check.py --target-project D:\PythonProject_paper_suggest --size 1180x720 --size 1366x768 --size 1440x900
D:\PythonProject_paper_suggest\project-moe-gui.cmd --preflight --json
```

仓库集成门禁：

```powershell
.\tools\ci\local_gate.ps1
.\tools\ci\local_mr_review.ps1
```

验收标准：

- 多尺寸视觉检查无文字溢出或非滚动容器溢出。
- 长文本和高密度 session fixture 不隐藏必需控件。
- Expert Workbench 可以保存、列出、筛选、复制、导出 handoff artifact。
- Sessions 页可以搜索、筛选、排序、解释生效状态并显示 override 冲突。
- 多项目面板默认只读，且不扫描显式配置之外的项目。
- 目标项目 dirty state 仍阻断写入/更新流程。

## 5. 回滚与本地集成

- 每个实施批次创建 feature worktree 和 branch。
- 每个完成的切片或内聚批次做本地提交。
- 合入本地 `main` 前运行 precommit update/archive gate 和本地验证。
- 批次 ready 后使用仓库 local-flow helper 进入本地 `main` 集成。
- 保留 rollback refs 和 completed receipts。
- 本地 `main` 集成后清理已合入 feature worktree 和本地 feature branch。
- 除非用户明确批准 GitLab/GitHub 发布，否则停在 remote-publication gate。
