---
doc_id: implementation_plan_confirmation_gate
lang: zh-CN
status: active
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/implementation_plan_confirmation_gate.md
---

# 实施方案确认门禁

## 目的

把 implementation plan 文件本身作为非文档实现前必须确认的治理产物。
即使已经在对话里确认过完整 plan，也不能直接进入非文档实现；必须先在 `docs_bilingual/implementation_plans/` 下创建或更新 active 状态的正式实施方案，登记到 `docs_bilingual/docs_registry.yaml`，提交并合入本地 `main`，再把该文件展示给用户确认。

## 范围决策

- 层级：项目级治理，适用于 `D:/PythonProject_langgraph`。
- 复用形态：规则形态是通用的，但本次实现只落在本仓库；除非后续明确批准，不改用户级 launcher 或全局配置。
- Stage A 类型：只创建文档和 registry 登记。
- Stage B 类型：用户确认本文件后，才允许修改治理、checker、helper 和测试。
- 远端发布：不在本方案范围内；除非用户明确要求推送或远端发布，否则停在本地 main。

## 非目标

- Stage A 不修改 runtime、checker、helper 或测试行为。
- 不把“对话里确认过 plan”视为足以进入非文档实现的授权。
- 除非用户明确要求远端发布，否则不推送 GitLab 或 GitHub。
- Stage B 不在未获得额外范围确认时修改用户级 Codex launcher 或全局配置。

## 当前状态

<!-- CURRENT_STATUS_START -->
状态：active
阶段：Stage A 文档包
责任会话：主 Codex leader 会话
当前门禁：创建并合入本 implementation plan，然后停下来等待用户确认
Stage B 进入条件：本地 `main` 合入后，用户明确确认 `docs_bilingual/implementation_plans/implementation_plan_confirmation_gate.md` 或中文对照文件
最后更新：2026-05-28
<!-- CURRENT_STATUS_END -->

## 需要落实的确认规则

退出 `/plan` 或从计划进入非文档执行时：

1. assistant 可以先在对话里讨论完整 plan。
2. 但任何非文档实现开始前，必须先在 `docs_bilingual/implementation_plans/` 下创建或更新正式 implementation plan 文件。
3. 该 plan 必须使用双语登记形式：英文 ASCII 主版 + 中文对照版。
4. 该 plan 必须在 `docs_bilingual/docs_registry.yaml` 中登记为 `doc_class: implementation_plan` 且 `status: active`。
5. plan 更新必须使用中文提交信息提交，并先合入本地 `main`。
6. assistant 必须展示 implementation plan 路径并等待用户明确确认该文件。
7. 只有在用户确认该文件之后，才允许开始非文档实现。

## Stage B 计划实施边界

用户确认本文件后，Stage B 只允许更新落实这条规则所必需的文件：

- `docs_bilingual/governance/openspec_opsx_project_usage_policy.md` - 英文治理政策，用于说明正式文件确认门禁。
- `docs_bilingual/governance/openspec_opsx_project_usage_policy.zh-CN.md` - 同一门禁的中文对照治理政策。
- `tools/check_plan_exit_execution_governance.py` - 在缺少正式 plan 文件确认时 fail closed 的 checker。
- `tools/complete_local_flow_to_remote_gate.py` - 在非文档执行前停到确认门的 helper。
- 覆盖新确认门禁的本地测试
- 只有在测试或 checker 变更需要时，才更新 CI 或 manifest 登记

Stage B 不修改无关的 Comet runtime 行为、LangGraph backend 行为或用户级 launcher 配置。

## 任务清单

<!-- TASK_BACKLOG_START -->
- [x] Stage A：创建英文 ASCII 主版 implementation plan。
- [x] Stage A：创建中文对照 implementation plan。
- [x] Stage A：在 `docs_bilingual/docs_registry.yaml` 登记为 active implementation plan。
- [ ] Stage A：使用中文提交信息提交文档包。
- [ ] Stage A：把文档包合入本地 `main`。
- [ ] Stage A：停止并要求用户确认本 implementation plan 文件后再进入 Stage B。
- [ ] Stage B：更新治理文档，明确“仅对话确认 plan”不足以进入非文档实现。
- [ ] Stage B：更新 helper/checker，使非文档执行必须具备 active、已登记、已提交的 implementation plan 和明确的文件确认证据。
- [ ] Stage B：增加“仅对话确认但没有 implementation plan 文件确认”应阻断的反向测试。
- [ ] Stage B：增加正式 active implementation plan 确认路径应放行的正向测试。
- [ ] Stage B：运行本地验证，并使用中文提交信息提交。
- [ ] Stage B：仅在用户确认本文件后，才合入本地 `main`。
<!-- TASK_BACKLOG_END -->

## 验收标准

Stage A 验收条件：

- 英文主版文件存在，并包含 implementation plan 要求的稳定更新锚点。
- 中文对照文件存在。
- `docs_bilingual/docs_registry.yaml` 将这对文件登记为 `doc_class: implementation_plan` 且 `status: active`。
- Stage A 提交信息为中文。
- Stage A 分支合入本地 `main`。
- Stage A 没有修改 runtime、checker、helper 或测试实现文件。
- assistant 在 Stage B 前停下来等待用户确认。

Stage B 只有在后续用户确认后才验收，并且必须满足：

- 治理规则明确“仅对话确认 plan”不够。
- 脚本路径会在缺少正式 implementation plan 文件确认时阻断非文档实现。
- 测试覆盖阻断路径和放行路径。
- 最终回复中包含新鲜验证证据。

## 证据索引

<!-- EVIDENCE_INDEX_START -->
- 等待 Stage A 提交证据。本计划刻意不在正文内保存完整证据包。
<!-- EVIDENCE_INDEX_END -->
