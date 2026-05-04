## Context / 背景

之前的 `define-durable-routing-smoke-gate-release` change 已经把 R0.6 确认为下一条只读 gate。随后操作者询问到 R2.0 是否还可以拆得更细。本 change 在任何 runtime smoke work 开始之前，先记录更细的 release-train structure。

## Goals / Non-Goals / 目标与非目标

**Goals / 目标：**

- 把 R0.6 到 R2.0 拆到未来会话可以“一条 slice 一个 OpenSpec change”的粒度。
- 把立即下一步限制在 R0.6.0 和 R0.6.1。
- 保持 production durable-team plan 只是 draft-only north-star material。
- 在 operator 明确授权 mutation 之前，保持默认 read-only boundary。

**Non-Goals / 非目标：**

- 不以 apply mode 运行 durable routing helpers。
- 不启动、停止或复用 durable team。
- 不编辑 repo-local durable state。
- 在 docs/spec updates 通过 GitLab-first review 落地之前，不归档本 change。

## Decisions / 决策

1. 使用 R0.6.0、R0.6.1 这样的 subrelease labels。
   - Rationale: subrelease labels 比宽泛的 R0.6 更适合冷启动会话限定范围。

2. 默认把每个 subrelease 当成一个 reviewed OpenSpec change。
   - Rationale: 每条小 slice 都能让 GitLab MR review、validation 和 rollback 保持有界。

3. 把 R2.0 拆成 readiness、memory、recovery、security、performance、dashboard、maintenance 和 final-release slices。
   - Rationale: production target 太大，不适合一次性安全实施。

## Risks / Trade-offs / 风险与取舍

- [Risk] 更多 slices 会带来更多 planning overhead。-> Mitigation: 每条 slice 应尽量小且机械化。
- [Risk] release labels 可能和 implementation reality 漂移。-> Mitigation: 每条 slice 都通过 OpenSpec archive，并且只在 validation 后同步 startup summaries。
- [Risk] 未来会话可能把 roadmap entry 当成状态变更授权。-> Mitigation: 每条 slice 都保留明确的 operator consent boundary。
