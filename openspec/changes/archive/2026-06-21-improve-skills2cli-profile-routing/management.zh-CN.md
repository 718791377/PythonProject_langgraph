# 管理记录：改进 Skills2CLI Profile 路由

## Open

- [x] proposal 说明 value 与 why。
- [x] implementation plan 定义 success criteria。
- [x] 约束已记录：advisory-only、no config apply、no plugin-cache edits、no remote publication。

## Design

- [x] delivery tailoring 已选择：先合入 Phase A，再实施 Phase B。
- [x] plan 已拆分为方案冻结与 runtime 实现。
- [x] plan 与 tasks 已给出 acceptance evidence path。

## Build

- [x] execution mode：subagent-driven-development / guarded local-main-first flow。
- [x] quality evidence：Stage A 方案冻结证据已收集，OpenSpec validate、repository guard、precommit update/archive、worktree receipt 与 UTF-8 检查均已通过。
- [x] blocker decision：无当前阻塞，继续。

## Verify

- [x] variance review：Stage A 偏差复核已完成，verifier 发现的分层一致性与中文 audit 关联说明问题已修正。
- [x] risk/change impact：Stage A 风险/变更影响已复核，runtime mutation、profile apply、plugin cache 编辑、user-level config 编辑和远程发布仍不在范围内。
- [x] Control decision：continue。

## Archive

- [x] value outcome：Phase A 与 Phase B 已集成到本地 `main`；本收口补上 `scene_description` 兼容、profile-level hints 与 archive evidence，使 runtime 可解释且有 checker 支撑。
- [x] lessons learned：用户可见字段名要明确使用 `scene_description`，同时保留既有 consumer 的 `scenario_description` 兼容；即使 task modules 提供 focused hints，profile-level 输出也应保留 hints。
- [x] archive/sync evidence：OpenSpec archive 已在本目录，stable spec 已更新；本地 `main` 已包含 Stage A `3d08d6e`、Phase B `80ec3dd` 与 audit rerank 收口 `d72aee7`；远程发布仍未授权。

## Monitoring

- [x] current facts：Phase B runtime 已具备场景化 profile/task-module 路由；原先 only-full 的插件已有非 full route 覆盖；user-level 安装副本 drift 会被报告而不是被静默信任。
- [x] return/no-return decision：continue。
