## ADDED Requirements

### Requirement: Receipt governance helper SHALL 校验 R4 smoke-tested receipts

repo-local receipt governance helper 必须为用户级 runtime promotion lanes 提供只读的 R4 smoke receipt validation surface。

有效的 R4 smoke receipt 必须包含 tool identity、owner lane、runtime stage `R4` 或 `smoke-tested`、prior install receipt evidence、bounded read-only smoke command evidence、passing smoke result、timeout release evidence、rollback pointer、rollback readiness、transcript redaction evidence 与 redaction status。helper 默认必须对 receipt references、transcripts 与 rollback pointers 输出 hash-first summary。

当 smoke receipt 试图表示 write-capable behavior、R5 live handoff、sensitive action execution、raw browser data reads、external message sends 或 user-level state mutation 时，helper 必须 fail closed。

#### Scenario: 有效 R4 smoke receipt 被接受且不暴露 raw private paths

- **GIVEN** smoke receipt 为 bounded help/status/version/safe-discovery/read-only command 记录 R4 或 `smoke-tested` stage evidence
- **WHEN** `python tools/user_level_receipt_governance.py smoke-check --receipt <path> --json` 运行
- **THEN** command 必须报告 `ok=true`、`smoke_receipt_valid=true`、`runtime_stage=R4` 与 `rollback_ready=true`
- **AND** 默认输出必须用 hashes 替代 raw install receipt paths、transcript contents 或 rollback pointers
- **AND** command 必须报告未 mutate user-level state、未 run external tools、未 read browser data。

#### Scenario: R4 smoke receipt 试图表示 live 或 write behavior

- **GIVEN** smoke receipt 标记 write behavior、live action、sensitive action execution 或 user-level mutation
- **WHEN** smoke receipt checker 运行
- **THEN** command 必须 fail closed，并输出 sanitized blocker codes
- **AND** 不得把该 lane 视为 `smoke-tested`。

### Requirement: Receipt governance helper SHALL 在不执行 rollback 的情况下校验 rollback executor receipts

repo-local receipt governance helper 必须校验 rollback executor receipts 中的 dry-run 与 apply evidence，但不得执行 rollback commands。

rollback receipt 必须包含 rollback target、rollback pointer、rollback mode、restore command evidence、dry-run result、post-rollback verification evidence、owner lane、operator authorization status 与 redaction status。apply-mode receipts 在缺少 explicit operator authorization 时必须 fail closed。

#### Scenario: Rollback apply receipt 缺少 operator authorization

- **GIVEN** rollback receipt 在缺少 explicit operator authorization 时请求 apply mode
- **WHEN** `python tools/user_level_receipt_governance.py rollback-check --receipt <path> --json` 运行
- **THEN** command 必须 fail closed
- **AND** 必须报告 `rollback_performed=false`，因为 helper 只校验 receipts，绝不执行 rollback commands。
