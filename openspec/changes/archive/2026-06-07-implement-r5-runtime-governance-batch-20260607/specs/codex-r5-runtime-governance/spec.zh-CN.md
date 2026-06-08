---
change: implement-r5-runtime-governance-batch-20260607
status: archived
translation_of: openspec/changes/archive/2026-06-07-implement-r5-runtime-governance-batch-20260607/specs/codex-r5-runtime-governance/spec.md
---

# R5 Runtime Governance Requirement Delta

## ADDED Requirements

### Requirement: R5 active-candidate receipts SHALL be script-checkable

任何声称 R5 active-candidate 或 bounded-live handoff 的 user-level runtime lane SHALL 提供 script-checkable receipt，其中包含 authorization、owner lease、target/action allowlist、timeout release、redaction、rollback、cleanup、lane authority 和 no-remote-mutation evidence。

#### Scenario: positive R5 receipt is accepted

- **GIVEN** receipt 声明 `runtime_stage` 为 `active-candidate`
- **AND** 它包含当前 authorization、owner lease、allowlist、timeout release、redacted transcript、rollback-ready pointer、cleanup evidence 和 no remote mutation
- **WHEN** lane checker 验证该 receipt
- **THEN** 它报告 receipt 已被接受为 R5 active-candidate evidence

#### Scenario: blocked receipt does not count as active-candidate

- **GIVEN** receipt 声明 blocked、dry-run、not-installed 或 missing authorization state
- **WHEN** lane checker 验证该 receipt
- **THEN** 它可以报告诚实 blocked evidence
- **AND** 它 MUST NOT 将该 receipt 计为 positive R5 active-candidate completion

### Requirement: Authority priority SHALL remain enforced at R5

Runtime lanes SHALL 在接受任何 R5 handoff 之前保持顺序 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。

#### Scenario: subordinate authority is blocked

- **GIVEN** gstack、harness 或 Spec Kit receipt 试图覆盖更高优先级的 authority layer
- **WHEN** checker 评估该 receipt
- **THEN** 它使用命名的 authority-priority error 失败
