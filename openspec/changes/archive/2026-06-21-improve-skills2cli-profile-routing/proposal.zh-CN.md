---
change_id: improve-skills2cli-profile-routing
status: proposed
owner: codex
created_at: 2026-06-21
translation_of: openspec/changes/improve-skills2cli-profile-routing/proposal.md
---

# 提案：改进 Skills2CLI Profile 路由

## 为什么

当前 plugin-modules 的 `target_profile` registry 作为 hard-load profile 列表是有效的，但对当前会话的 skill 路由来说粒度过粗。它缺少场景描述、负样本边界、task-module 分层和 recall/rerank 证据。七个已知 plugin family 只能通过 `full` 到达，而 `full` 过大，不适合作为普通默认项，否则可能重新引发 skills context budget 压力。

30 天 `codex_skills_usage_audit` 已经提供足够证据，用于保持 profile 变更 advisory 和可回滚，同时改进系统对 soft-load 与 hard-load-preview candidate 的建议方式。

## 改什么

- 在 runtime 编辑前冻结场景化 profile routing 契约。
- 保留现有 profile ID，同时新增 alias、route terms、negative examples、ranking signals 和 task modules。
- 要求 known plugins 具备非 `full` routing ownership，除非存在明确 allowlist reason。
- 新增 `skills2cli.py profile suggest` advisory command，用于解释命中的 profiles、task modules、excluded candidates 与 soft/hard-load 边界。
- 继续把 hard-load profile apply 排除在范围外；runtime 只能建议 soft-load commands 和 hard-load preview commands。
- 拆成 Phase A plan freeze 与 Phase B runtime implementation，两者分别合入本地 `main`。

## 范围外

- 自动 apply 任何 hard-load profile。
- 编辑用户级 Codex `config.toml`。
- 批量编辑 plugin cache 或 vendor `SKILL.md` 文件。
- 远程发布、创建/合并 GitLab MR、同步 GitHub 或修改远端 ref。
