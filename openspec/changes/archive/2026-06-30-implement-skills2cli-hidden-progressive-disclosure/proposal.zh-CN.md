---
change_id: implement-skills2cli-hidden-progressive-disclosure
status: proposed
owner: codex
created_at: 2026-06-30
---

# Proposal：实施 Skills2CLI 隐藏库渐进披露

## Why

当前 `skills2cli` 可见性压缩流程已经能把大多数 standalone user skills 移出默认 model-visible 列表，从而降低 skills context 压力。但隐藏 skills 目前很难使用，除非人工定位 `SKILL.md` 路径，或者恢复一大批 receipt。用户希望 hidden skills 默认保持隐藏，同时仍然可以按任务范围进行渐进披露。

## What Changes

- 给 `skills2cli` 增加 hidden-skill discovery 与 soft-load 表面。
- 同时搜索当前可见 skills 与 `skills2cli` hidden library，并明确输出 visibility-state 标签。
- 为 `stop-slop` 这类未安装名称和 `grill-me` 这类隐藏上游名称增加 alias routing。
- hidden skill 被加载时记录 usage events，让未来可见性决策基于证据而不是猜测。
- 增加高置信 visibility recommendations，以及用户手动执行的 `apply-recommendations` 命令；该命令一天最多一次，并写 rollback receipts。

## Out of Scope

- 恢复全部隐藏 skills。
- 编辑 plugin cache 或 vendor `SKILL.md` 文件。
- 编辑 `C:\Users\lenovo\.codex\config.toml`。
- 后台自动触发 promote/demote。
- 把 hidden skill 使用当作 native subagent 或 expert 证据。
- 远端发布。
