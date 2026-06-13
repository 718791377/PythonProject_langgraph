---
doc_id: recent_manual_workflow_packaging_shortlist_2026_06_13
lang: zh-CN
status: active
doc_class: memory
translation_of: docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.md
---

# 近期重复手工工作流打包短名单

生成时间：`2026-06-13T03:32:14.987198+00:00`
回看窗口：`30` 天
Chronicle：`not_enabled`（仅发现，不写入）

## 封装判断

- 项目级：本轮已实现。原因：输入依赖本仓库 Git、memory、implementation plans 与本地门禁，本仓库是 source of truth。
- 用户级：只记录候选，不安装。条件：跨两个以上项目复用、输出脱敏、具备 rollback/smoke 证据并有单独授权。
- 不封装：custom subagent、scheduler、Chronicle 写入、外部真实动作；原因是已有角色覆盖或权限/隐私面过大。

## 短名单

### local-main-first-governance-packaging: 方案 -> 本地门禁/MR review -> 本地 main 合入打包

- 推荐形式: `extend-existing/project-level-skill`
- 频率/置信度: 213 evidence hits in the lookback window / `high`
- 本轮可行动: `true`
- 理由: 本仓库反复执行方案冻结、本地验证、提交、合入 local main、停在远端发布门禁的流程。现有 helper 已覆盖合入机械动作，但仍需要窄范围 skill/CLI 固化发现与决策步骤。
- 支持证据:
  - 2026-06-13 [git] 方案：新增近期手工工作流打包计划 (5ba4dea)
  - 2026-06-12 [git] 添加会话表面单面板运行时对齐方案 (ea9a442)
  - 2026-06-12 [git] 添加通用模板复用升级方案 (f3c2900)
  - 2026-06-11 [git] 收尾多方案家族R6完成状态 (d401cf9)
  - 2026-06-11 [git] 实现多方案家族R6运行时校验 (72c657a)
  - 2026-06-11 [git] 更新多方案家族R6执行计划 (f911dd7)

### r5-r6-live-runtime-evidence-gates: R5/R6 真实运行时证据收据门禁

- 推荐形式: `extend-existing/skip-duplicate`
- 频率/置信度: 193 evidence hits in the lookback window / `high`
- 本轮可行动: `false`
- 理由: R5/R6 工作已由 checker-backed runtime 与 receipt 门禁覆盖；本轮只应复用/扩展既有门禁，避免再建宽泛重复资产。
- 支持证据:
  - 2026-06-12 [git] 补齐通用模板最终验证证据 (9493cde)
  - 2026-06-12 [git] 记录通用模板升级收尾证据 (b67b94f)
  - 2026-06-11 [git] 收尾多方案家族R6完成状态 (d401cf9)
  - 2026-06-11 [git] 实现多方案家族R6运行时校验 (72c657a)
  - 2026-06-11 [git] 更新多方案家族R6执行计划 (f911dd7)
  - 2026-06-11 [git] 文档：记录 Project MOE GUI 0.2.44 最终验收证据 (94dd221)

### skills-usage-audit-cadence: Codex skills 使用审计与 warning triage 节奏

- 推荐形式: `extend-existing`
- 频率/置信度: 177 evidence hits in the lookback window / `high`
- 本轮可行动: `false`
- 理由: 周报和 triage 文件说明该流程重复出现，但仓库已有专用审计脚本和 memory 输出。本轮应继续复用，并把脱敏信号接入本报告。
- 支持证据:
  - 2026-06-09 [git] 实现R6覆盖审计批处理 (5d37ffd)
  - 2026-06-09 [git] 记录R6覆盖审计缺口 (1455e87)
  - 2026-06-07 [git] 记录 Skills 审计6月7日延续证据 (43dda79)
  - 2026-06-06 [git] 实现 MCP skills CLI R4 smoke 收据 (bee9791)
  - 2026-06-04 [git] 实现：安装上游mcp2cli并派生skills2cli (98cc08b)
  - 2026-06-03 [git] 更新上游 mcp2cli 与 skills2cli 用户级安装方案 (dc9e620)

### gui-browser-wxwork-live-actions: GUI/浏览器/企业微信真实动作治理

- 推荐形式: `needs-more-evidence/separate-plan`
- 频率/置信度: 126 evidence hits in the lookback window / `high`
- 本轮可行动: `false`
- 理由: 该类工作重复且成本高，但涉及敏感外部真实动作。不能纳入通用打包器；需要单独方案、授权、rollback、smoke 与隐私证据。
- 支持证据:
  - 2026-06-11 [git] 实现：执行 CloakBrowser-Manager 非 Docker 运行时 (838f256)
  - 2026-06-11 [git] 方案：规划 CloakBrowser-Manager 非 Docker 运行时 (41ca534)
  - 2026-06-11 [git] 文档：记录 Project MOE GUI 0.2.44 最终验收证据 (94dd221)
  - 2026-06-11 [git] 实现：优化 Project MOE GUI Sessions 镜头优先布局 (66c9b1a)
  - 2026-06-11 [git] 文档：记录 Project MOE GUI 0.2.43 验证证据 (99bd7fc)
  - 2026-06-11 [git] 实现：执行 CloakBrowser 学术技能用户级运行时 (f969454)

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
- 频率/置信度: 18 evidence hits in the lookback window / `high`
- 本轮可行动: `true`
- 理由: 该提示是可复用元工作流，证据顺序与停止条件稳定；高置信缺口资产就是项目级 skill 加手动 CLI。
- 支持证据:
  - 2026-06-13 [git] 方案：新增近期手工工作流打包计划 (5ba4dea)
  - 2026-05-21 [git] 补强 PySide6 打包输出证据 (57946d8)
  - 2026-05-21 [git] 补充 PySide6 打包 opt-in 检查器 (8c2ad00)
  - 2026-05-19 [git] 脱敏 GitLab 手工备注路径 (58e984b)
  - 2026-06-13 [memory] recent_manual_workflow_packaging_shortlist_2026-06-13 (docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.md)
  - 2026-06-13 [memory] recent_manual_workflow_packaging_shortlist_2026-06-13.zh-CN (docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.zh-CN.md)

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
