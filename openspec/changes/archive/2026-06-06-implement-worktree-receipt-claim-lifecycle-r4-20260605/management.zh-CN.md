# Management Checklist（管理清单）

## Open

- [x] Value and why evidence checked（价值与原因证据已检查）：R4 关闭 validation-only lifecycle labels（仅校验的生命周期标签）与 automated local metadata advancement（自动本地元数据推进）之间的 runtime gap（运行时缺口）。
- [x] Success criteria checked（成功标准已检查）：helper、integration hooks（集成钩子）、tests、plan pair、OpenSpec delta、validation、archive 和 local-main integration。
- [x] Stakeholders and constraints checked（相关方与约束已检查）：main Codex leader session 拥有写入范围；remote publication 未授权；不启动 durable team。

## Design

- [x] Delivery tailoring checked（交付裁剪已检查）：使用一个 focused helper 和 integration hooks，而不是扩展成 broad durable-team runtime。
- [x] Risks and assumptions checked（风险与假设已检查）：invalid transition order、dirty cleanup、missing rollback evidence、remote publication 都必须 fail closed。
- [x] Acceptance evidence path checked（验收证据路径已检查）：focused tests、receipt checker、precommit review、OpenSpec guard、local gate、local MR review。

## Build

- [x] Execution mode checked（执行模式已检查）。
- [x] TDD / review / quality evidence checked（测试驱动、审查与质量证据已检查）。
- [x] Blockers cleared or decided（阻塞项已清除或已决策）。

## Verify

- [x] Variance review checked（偏差审查已检查）。
- [x] Risk/change impact checked（风险与变更影响已检查）。
- [x] Control decision checked（控制决策已检查）。

## Archive

- [x] Value outcome checked（价值结果已检查）。
- [x] Lessons learned checked（经验教训已检查）。
- [x] Archive/sync evidence checked（归档/同步证据已检查）。

## Monitoring

- [x] Current facts checked（当前事实已检查）：本分支开始前没有 active R4 change；实现使用 isolated feature worktree（隔离功能工作树）和 active portable claim（活动便携认领）。
- [x] Return/no-return decision checked（是否返回早期阶段的决策已检查）：继续当前 change；不需要返回早期 phase。

## Evidence Notes

- Build evidence（构建证据）：R4 helper 实现后，focused lifecycle、cleanup 和 complete-flow tests 均已通过。
- Verify evidence（验证证据）：提交和归档前运行 full validation；remote publication 保持未授权。
- Archive decision（归档决策）：R4 是 focused runtime/checker/test/spec update，只有一个 rollback boundary，因此计划使用 single integration package。
