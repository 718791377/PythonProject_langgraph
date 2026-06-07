# 管理清单

## Open

- [x] proposal.md 已记录价值与原因。
- [x] 已记录成功标准与约束。
- [x] 远端发布仍不在本 change 范围内。

## Design

- [x] 交付裁剪已限定为 dry-run helper、receipt validation、stable spec 提升与文档对齐。
- [x] design.md 已记录风险与假设。
- [x] proposal.md 的 verification 已列出验收证据路径。

## Build

- [x] 执行模式已选择：superpowers:executing-plans，并对 receipt contract 使用 superpowers:test-driven-development。
- [x] TDD 证据从更严格的失败 receipt 测试开始。
- [x] 这是单一串行 checker/runtime hotspot，不需要 durable team。

## Verify

- [x] 已在收口改动后重新运行定向测试、OpenSpec validation 与 repository guard。
- [ ] 已在干净的 feature worktree 上通过 local gate 与 local MR review。
- [ ] 控制决策仍是继续本地 main 集成；远端发布仍保持关闭。

## Monitoring

- [x] 当前事实：helper 仍为 dry-run only，当前工作是 stable-spec / registry 收口，不涉及 live Spec Kit mutation。
- [x] 返回/不返回决策：在本地验证前无需返回早期阶段。

## Archive

- [x] verification.md 中已总结价值结果。
- [x] 已将 lessons learned / reusable guidance 提升进 stable specs 与 registry 文本。
- [x] 已确认 delta spec sync、verification evidence 与 archive path。
