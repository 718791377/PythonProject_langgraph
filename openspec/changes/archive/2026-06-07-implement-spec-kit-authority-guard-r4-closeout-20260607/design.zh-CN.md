# 设计：Spec Kit Authority Guard R4 收口

## 当前状态

仓库已经拥有 dry-run subordinate runtime helper 与 fail-closed 的 Spec Kit authority guard。定向测试已经覆盖 generated surfaces、安全引用与基础 receipt 校验。剩余缺口不是新的 runtime lane，而是最终的 R4 收口契约：helper、guard、stable spec 与 registry 仍需对齐到完全一致的冲突优先级字符串和稳定 safety-rule requirement。

## 决策

保持 runtime scope 不变，继续 dry-run only。

- 精确冲突顺序固定为 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。
- `authority_decision.priority_order` 现在属于必填 receipt 契约。
- stable safety-rule spec 记录该 requirement，避免未来冷启动 session 只依赖 plan 文本。
- script-backing registry 同时记录 checker 与 dry-run runtime helper，作为这条规则的 executable controls。
- `spec_kit_authority_guard_plan` 继续作为主 implementation plan；subordinate adapter plan 只保留 companion guidance 角色。

## 安全说明

- 不运行任何 live Spec Kit command。
- 不允许生成 `.specify/`、根目录 `specs/`、slash-command、skill-surface、extension、preset 或 workflow-output。
- runtime helper 仍然只输出 receipts。
- 本地集成仍受 local-main-first validation 与 remote-publication gate 约束。

## 验证重点

- runtime receipt 必须包含精确优先级顺序。
- guard 必须拒绝缺失或篡改该顺序的 receipt。
- stable spec 与 registry 必须记录同一条规则。
- implementation-plan 与 governance 文本必须与严格优先级顺序保持一致。
