---
doc_id: recent_manual_workflow_packaging_shortlist_2026_06_13
lang: zh-CN
status: active
doc_class: memory
translation_of: docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.md
---

# 近期重复手工工作流打包短名单

生成时间：`2026-06-13T12:12:20.570586+00:00`
回看窗口：`30` 天
Chronicle：`not_enabled`（仅发现，不写入）

## 封装判断

- 项目级：本轮已实现。原因：输入依赖本仓库 Git、memory、implementation plans 与本地门禁，本仓库是 source of truth。
- 用户级：只记录候选，不安装。条件：跨两个以上项目复用、输出脱敏、具备 rollback/smoke 证据并有单独授权。
- 不封装：custom subagent、scheduler、Chronicle 写入、外部真实动作；原因是已有角色覆盖或权限/隐私面过大。

## 广泛类别扫描

以下类别对应 `reference_files/5.md` 要求的 coding/research/writing/planning/communication/operations/analysis/personal administration 广泛回看范围。

- **编码与实现** (`coding`): decision=`covered_by_shortlist`, evidence_count=`289`, mapped=`r5-r6-live-runtime-evidence-gates`, `gui-browser-wxwork-live-actions`, `recent-manual-workflow-packaging`. 近期实现工作已由 runtime/receipt 门禁、GUI/浏览器治理以及打包器本身覆盖。
- **研究与来源发现** (`research`): decision=`separate_plan_required`, evidence_count=`21`, mapped=`gui-browser-wxwork-live-actions`. 近期工作出现研究工具，但浏览器/真实动作仍属敏感边界，不由本通用工作流打包。
- **写作与文档** (`writing`): decision=`covered_by_shortlist`, evidence_count=`349`, mapped=`local-main-first-governance-packaging`, `recent-manual-workflow-packaging`. 文档与方案写作高频出现，由项目级 skill/CLI 和 local-main-first 打包候选覆盖。
- **计划与路线控制** (`planning`): decision=`covered_by_shortlist`, evidence_count=`164`, mapped=`local-main-first-governance-packaging`, `recent-manual-workflow-packaging`. 证据窗口中最强的重复流程之一就是先方案后本地合入。
- **沟通与消息** (`communication`): decision=`separate_plan_required`, evidence_count=`7`, mapped=`gui-browser-wxwork-live-actions`. 已检测到消息沟通工作，但它涉及外部真实动作，因此不纳入本通用打包器。
- **运维、门禁、安装与发布** (`operations`): decision=`covered_by_shortlist`, evidence_count=`153`, mapped=`local-main-first-governance-packaging`, `r5-r6-live-runtime-evidence-gates`, `general-template-cross-project-sync`. 运维门禁与发布纪律高频重复，已映射到既有 helper 和短名单扩展。
- **分析、审计与 triage** (`analysis`): decision=`covered_by_existing_assets`, evidence_count=`275`, mapped=`skills-usage-audit-cadence`, `r5-r6-live-runtime-evidence-gates`. 审计/triage 重复性强，但既有 checker-backed 资产已足够，因此封装决策是扩展/跳过重复项。
- **个人行政事务** (`personal-administration`): decision=`scanned_no_packaging_candidate`, evidence_count=`0`, mapped=无. 本仓库近期已提交证据中没有足以封装个人行政流程的强证据。

## 短名单

### local-main-first-governance-packaging: 方案 -> 本地门禁/MR review -> 本地 main 合入打包

- 推荐形式: `extend-existing/project-level-skill`
- 频率/置信度: 214 evidence hits in the lookback window / `high`
- 本轮可行动: `true`
- 理由: 本仓库反复执行方案冻结、本地验证、提交、合入 local main、停在远端发布门禁的流程。现有 helper 已覆盖合入机械动作，但仍需要窄范围 skill/CLI 固化发现与决策步骤。
- 支持证据:
  - 2026-06-13 [git] 方案：补齐近期工作流打包广泛类别证据 (6b58c1c)
  - 2026-06-13 [git] 收尾近期手工工作流打包方案状态 (85b648c)
  - 2026-06-13 [git] 方案：记录 MOE GUI dirty target 启动修复 (5bfec68)
  - 2026-06-13 [git] 方案：新增近期手工工作流打包计划 (5ba4dea)
  - 2026-06-12 [git] 添加会话表面单面板运行时对齐方案 (ea9a442)
  - 2026-06-12 [git] 添加通用模板复用升级方案 (f3c2900)

### r5-r6-live-runtime-evidence-gates: R5/R6 真实运行时证据收据门禁

- 推荐形式: `extend-existing/skip-duplicate`
- 频率/置信度: 190 evidence hits in the lookback window / `high`
- 本轮可行动: `false`
- 理由: R5/R6 工作已由 checker-backed runtime 与 receipt 门禁覆盖；本轮只应复用/扩展既有门禁，避免再建宽泛重复资产。
- 支持证据:
  - 2026-06-13 [git] 记录 Skills 审计19点32分监控证据 (5473570)
  - 2026-06-13 [git] 方案：补齐近期工作流打包广泛类别证据 (6b58c1c)
  - 2026-06-13 [git] 记录 Skills 审计14点11分监控证据 (cbedd71)
  - 2026-06-13 [git] 记录 Skills 审计12点34分监控证据 (ea092d9)
  - 2026-06-13 [git] 记录 Skills 审计6月13日延续证据 (a9b17c1)
  - 2026-06-12 [git] 补齐通用模板最终验证证据 (9493cde)

### skills-usage-audit-cadence: Codex skills 使用审计与 warning triage 节奏

- 推荐形式: `extend-existing`
- 频率/置信度: 205 evidence hits in the lookback window / `high`
- 本轮可行动: `false`
- 理由: 周报和 triage 文件说明该流程重复出现，但仓库已有专用审计脚本和 memory 输出。本轮应继续复用，并把脱敏信号接入本报告。
- 支持证据:
  - 2026-06-13 [git] 记录 Skills 审计19点32分监控证据 (5473570)
  - 2026-06-13 [git] 记录 Skills 审计14点11分监控证据 (cbedd71)
  - 2026-06-13 [git] 记录 Skills 审计12点34分监控证据 (ea092d9)
  - 2026-06-13 [git] 记录 Skills 审计6月13日延续证据 (a9b17c1)
  - 2026-06-09 [git] 实现R6覆盖审计批处理 (5d37ffd)
  - 2026-06-09 [git] 记录R6覆盖审计缺口 (1455e87)

### gui-browser-wxwork-live-actions: GUI/浏览器/企业微信真实动作治理

- 推荐形式: `needs-more-evidence/separate-plan`
- 频率/置信度: 128 evidence hits in the lookback window / `high`
- 本轮可行动: `false`
- 理由: 该类工作重复且成本高，但涉及敏感外部真实动作。不能纳入通用打包器；需要单独方案、授权、rollback、smoke 与隐私证据。
- 支持证据:
  - 2026-06-13 [git] 修复 MOE GUI dirty target 启动与 thesis 包装器 (5d2deff)
  - 2026-06-13 [git] 方案：记录 MOE GUI dirty target 启动修复 (5bfec68)
  - 2026-06-11 [git] 实现：执行 CloakBrowser-Manager 非 Docker 运行时 (838f256)
  - 2026-06-11 [git] 方案：规划 CloakBrowser-Manager 非 Docker 运行时 (41ca534)
  - 2026-06-11 [git] 文档：记录 Project MOE GUI 0.2.44 最终验收证据 (94dd221)
  - 2026-06-11 [git] 实现：优化 Project MOE GUI Sessions 镜头优先布局 (66c9b1a)

### general-template-cross-project-sync: General/General_2 模板扩展以支持跨项目复用

- 推荐形式: `extend-existing/project-template`
- 频率/置信度: 14 evidence hits in the lookback window / `high`
- 本轮可行动: `false`
- 理由: 模板扩展是重复流程，但属于项目模板边界并已有方案/证据；本报告只列为候选，不直接修改模板目录。
- 支持证据:
  - 2026-06-12 [git] 补齐通用模板最终验证证据 (9493cde)
  - 2026-06-12 [git] 记录通用模板升级收尾证据 (b67b94f)
  - 2026-06-12 [git] 添加通用模板复用升级方案 (f3c2900)
  - 2026-06-09 [git] 修复R6模板源生成漂移 (5866f3e)
  - 2026-06-08 [git] 实现R5持久烟测采纳门模板 (fd6403f)
  - 2026-05-30 [git] 实现 durable smoke gate 模板自检 (58de0d8)

### recent-manual-workflow-packaging: 近期手工工作流打包流程本身

- 推荐形式: `project-level-skill-and-manual-cli`
- 频率/置信度: 22 evidence hits in the lookback window / `high`
- 本轮可行动: `true`
- 理由: 该提示是可复用元工作流，证据顺序与停止条件稳定；高置信缺口资产就是项目级 skill 加手动 CLI。
- 支持证据:
  - 2026-06-13 [git] 实现近期工作流打包广泛类别扫描 (1fb2710)
  - 2026-06-13 [git] 方案：补齐近期工作流打包广泛类别证据 (6b58c1c)
  - 2026-06-13 [git] 收尾近期手工工作流打包方案状态 (85b648c)
  - 2026-06-13 [git] 实现近期手工工作流打包运行时 (ca5adf1)
  - 2026-06-13 [git] 方案：新增近期手工工作流打包计划 (5ba4dea)
  - 2026-05-21 [git] 补强 PySide6 打包输出证据 (57946d8)

## 已创建或扩展

- `repo-local-recent-workflow-packaging-skill` - project-level skill - `.agents/skills/recent-workflow-packaging/SKILL.md` - `present`
- `recent-workflow-packaging-cli` - project-level manual CLI - `tools/report_recent_manual_workflow_candidates.py` - `present`

## 用户级候选

- `extend-user-level-wrapper` - 项目 CLI 的薄用户级 wrapper/config - `user-level-candidate-only` - 只有当项目 CLI 在两个以上项目稳定复用并具备 rollback/smoke 证据后才提升；本轮不执行用户级安装。

## 刻意跳过

- `custom-subagent-for-packaging` - 为工作流打包创建 custom subagent: 现有 analyst/planner/writer/verifier 已覆盖有界调查与成文需求。
- `scheduled-packaging-audit` - 定时工作流打包审计: 定时执行会扩大自动化与授权面；在单独定时自动化方案出现前保持为手动 CLI。
- `chronicle-write-integration` - Chronicle 写入或变更集成: Chronicle 在此仅用于发现；报告只记录 not_enabled 或发现信号，不写入外部状态。
- `external-live-action-automation` - 外部真实动作自动化: 浏览器、GUI、企业微信等真实动作敏感，必须有独立授权与收据。

## 需要更多证据

- `extend-user-level-wrapper` - 项目 CLI 的薄用户级 wrapper/config: 只有当项目 CLI 在两个以上项目稳定复用并具备 rollback/smoke 证据后才提升；本轮不执行用户级安装。
- `external-action-packagers` - 通用浏览器/GUI/企业微信真实动作打包器: 打包前需要按系统单独授权、rollback、隐私审查与真实 smoke 证据。

## 安全与脱敏

- `raw_sessions_read`: `False`
- `raw_runtime_logs_read`: `False`
- `chronicle_mutated`: `False`
- `user_level_config_mutated`: `False`
- `scheduler_created`: `False`
- `external_actions_performed`: `False`
- `path_redaction`: `repo-relative paths only; user-level paths reduced to names/counts; unreadable legacy text is hashed`
