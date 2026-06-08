# codex-r5-runtime-governance 规范

## 目的
定义 R5 runtime governance receipts 的稳定仓库要求。任何声称 active-candidate 或 bounded-live handoff 的 user-level runtime lane，在被接受前，必须提供 checker-backed 的 authorization、ownership、allowlist、timeout、redaction、rollback、cleanup、authority-priority 和 no-remote-mutation evidence。

## Requirements / 需求
### Requirement: R5 active-candidate receipts SHALL be script-checkable / R5 active-candidate receipt 必须可脚本检查

Every user-level runtime lane that claims R5 active-candidate or bounded-live handoff SHALL provide a script-checkable receipt containing authorization, owner lease, target/action allowlist, timeout release, redaction, rollback, cleanup, lane authority, and no-remote-mutation evidence.

任何声称 R5 active-candidate 或 bounded-live handoff 的 user-level runtime lane，都必须提供可由脚本检查的 receipt；该 receipt 必须包含 authorization、owner lease、target/action allowlist、timeout release、redaction、rollback、cleanup、lane authority 和 no-remote-mutation evidence。

#### Scenario: positive R5 receipt is accepted / 正向 R5 receipt 被接受

- **GIVEN** a receipt declares `runtime_stage` as `active-candidate`
- **AND** it includes current authorization, owner lease, allowlist, timeout release, redacted transcript, rollback-ready pointer, cleanup evidence, and no remote mutation
- **WHEN** the lane checker validates the receipt
- **THEN** it reports the receipt as accepted R5 active-candidate evidence

- **GIVEN** receipt 声明 `runtime_stage` 为 `active-candidate`
- **AND** 它包含当前 authorization、owner lease、allowlist、timeout release、redacted transcript、rollback-ready pointer、cleanup evidence 和 no remote mutation
- **WHEN** lane checker 验证该 receipt
- **THEN** checker 报告该 receipt 可作为 R5 active-candidate evidence 被接受

#### Scenario: blocked receipt does not count as active-candidate / blocked receipt 不计入 active-candidate

- **GIVEN** a receipt declares blocked, dry-run, not-installed, or missing authorization state
- **WHEN** the lane checker validates the receipt
- **THEN** it may report honest blocked evidence
- **AND** it MUST NOT count that receipt as positive R5 active-candidate completion

- **GIVEN** receipt 声明 blocked、dry-run、not-installed 或 missing authorization state
- **WHEN** lane checker 验证该 receipt
- **THEN** checker 可以报告诚实的 blocked evidence
- **AND** checker 不得将该 receipt 计为正向 R5 active-candidate completion

### Requirement: Authority priority SHALL remain enforced at R5 / R5 必须继续强制执行 authority priority

Runtime lanes SHALL preserve the priority `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` before any R5 handoff is accepted.

Runtime lane 在任何 R5 handoff 被接受前，必须保持 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` 的优先级顺序。

#### Scenario: subordinate authority is blocked / 下级 authority 被阻断

- **GIVEN** a gstack, harness, or Spec Kit receipt attempts to override a higher-priority authority layer
- **WHEN** the checker evaluates the receipt
- **THEN** it fails with a named authority-priority error

- **GIVEN** gstack、harness 或 Spec Kit receipt 试图覆盖更高优先级的 authority layer
- **WHEN** checker 评估该 receipt
- **THEN** checker 使用具名 authority-priority error fail closed
