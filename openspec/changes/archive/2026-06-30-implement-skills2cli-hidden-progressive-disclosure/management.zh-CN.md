# Management Record

## Open

- [x] Value：hidden skills 在不增加默认 model-visible pressure 的情况下仍然可用。
- [x] Success criteria：hidden search/load 能用于 `grill-me` 和 `stop-slop` alias，usage events 被记录，recommendations 被生成，apply 是 manual-only 且 receipt-backed。
- [x] Constraints：不编辑 plugin cache，不编辑 `config.toml`，不做远端发布。

## Design

- [x] Delivery tailoring：两个本地集成包，Phase A plan-freeze 与 Phase B runtime。
- [x] Risks：意外全局恢复、alias 匹配噪声、不安全 auto-apply、daily guard 绕过。
- [x] Acceptance evidence path：`test/skills2cli.test.py`、OpenSpec guard、本地 gate、本地 MR review。

## Build

- [x] Execution mode selected：worktree-isolated local-main-first implementation。
- [x] Quality evidence recorded before local `main` integration：Phase A 使用 implementation-plan rules、OpenSpec strict validation、worktree receipt checker、precommit update/archive review 与 OpenSpec guard。
- [x] Blocker decision recorded：已使用 native verifier 做只读审阅；Phase A 是方案冻结包，不需要 durable runtime team，Phase B 仍按多切片实现推进。

## Verify

- [ ] Variance review completed。
- [ ] Risk/change impact reviewed。
- [ ] Control decision：runtime validation 通过后继续归档。

## Archive

- [ ] Stable spec promoted。
- [ ] Lessons/receipt recorded。
- [ ] Archive evidence recorded。

## Monitoring

- [x] Current facts：方案在 2026-06-30 根据用户选择的默认策略冻结。
- [x] Return/no-return decision：continue；不需要返回更早阶段重做。
