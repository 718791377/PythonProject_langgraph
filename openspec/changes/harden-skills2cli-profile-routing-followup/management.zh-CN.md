# 管理记录：硬化 Skills2CLI Profile Routing 后续契约

## Open checklist

- [x] 已记录 value/why：在初始 Skills2CLI profile-routing 基线之后，收口专家复核指出的 routing quality 与 safety gaps。
- [x] 已记录 success criteria：Stage A 冻结 contract；Stage B 实施 checker/runtime/test hardening；不发生远端发布或 profile apply。
- [x] 已记录 constraints：不改 `config.toml`、不改 plugin cache、不改 vendor `SKILL.md`、不修改 remote，skills/profiles 不是 native expert evidence。

## Design checklist

- [x] 已记录 delivery tailoring：两个 local-main packages，先 Stage A plan-freeze，再 Stage B runtime implementation。
- [x] 已记录 risks：只有字段没有行为证明、`full` fallback 膨胀、apply-boundary drift、installed-copy drift。
- [x] 已记录 acceptance evidence path：plan docs、delta spec、focused checker/test output、local gate、local MR review 与 completed claim。

## Build checklist

- [x] 已选择 execution mode：主会话实现，专家只读 fan-in，并使用 worktree isolation。
- [x] 已要求 quality evidence：OpenSpec validation、`check_precommit_update_archive`、`run_openspec_guard`、focused checks、local gate 与 local MR review。
- [x] Blocker decision：Stage A 无 blocker；Phase B 在 Stage A 本地 main 集成之后开始。

## Monitoring checklist

- [x] 已记录 current facts：上一轮 baseline 已在本地 main；本 change 是 follow-up hardening。
- [x] Return/no-return decision：继续；不需要返回早期阶段。

## Stage A sign-off checklist

- [x] 四原则已映射到双语实施方案与 delta spec。
- [x] Phase A/Phase B package split 已显式记录。
- [x] Safety boundary matrix 已记录 no apply、no config/cache/vendor mutation、no remote publication 与 no expert-evidence inflation。
- [ ] Stage A OpenSpec validation、precommit/archive review、repository guard、local gate 与 local MR review 通过。
- [ ] Stage A 已本地提交并集成本地 `main`。
