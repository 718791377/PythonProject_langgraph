---
change_id: harden-skills2cli-profile-routing-followup
status: proposed
owner: codex
created_at: 2026-06-22
translation_of: openspec/changes/harden-skills2cli-profile-routing-followup/proposal.md
---

# 提案：硬化 Skills2CLI Profile Routing 后续契约

## 为什么

上一轮 `improve-skills2cli-profile-routing` 已经交付场景化 profile routing 基线，并归档初始 OpenSpec 契约。专家复核认为已落地 runtime 可用，但还需要更强的 fail-closed 证据来保护路由质量与安全边界：

- 正向场景质量已经写进方案，但 shared registry contract 还没有完全 fail-closed；
- `load_policy` 同时承载 routing、activation 与 governance 语义；
- `profile.task_module` 已被 runtime 当作稳定逻辑标识，但尚未作为一等只读路由 ID 写清楚；
- `full` 目前主要靠 penalty 降权，应升级为显式 eligibility-gated troubleshooting profile；
- installed-copy drift 目前偏向 `profiles.json`，应覆盖完整 `skills2cli` artifact surface；
- no-auto-apply 已有输出 flags，但还需要行为级证据证明 config 与 plugin cache 没有被修改。

## 改什么

- 先冻结 follow-up contract，再做 runtime edits。
- 增加 Phase A acceptance matrix，把场景化描述、分层路由、负样本边界、召回重排映射到字段、OpenSpec 场景与 Phase B checker。
- 定义 Phase A / Phase B 分离，防止 plan-freeze 工作混入 runtime code、registry schema、helper script、checker 或 install changes。
- 增加统一 safety contract：允许 local-main-first，不允许远端发布，不修改 `config.toml`，不修改 plugin cache/vendor `SKILL.md`，没有后续明确 apply receipt 时不执行 profile apply。
- 要求 Phase B 增加正交 schema 字段、一等 `profile.task_module` 语义、显式 `full` eligibility gate、完整 install artifact drift reporting 与行为级 no-auto-apply tests。

## 不在范围内

- 远端发布、创建或合并 GitLab MR、同步 GitHub 或修改 remote refs。
- 编辑 `C:\Users\lenovo\.codex\config.toml`。
- 批量编辑 plugin cache 或 vendor `SKILL.md` 文件。
- 自动 apply 任何 hard-load profile。
- 把 skills、profiles 或 helper invocation 当作 native subagent/expert evidence。
