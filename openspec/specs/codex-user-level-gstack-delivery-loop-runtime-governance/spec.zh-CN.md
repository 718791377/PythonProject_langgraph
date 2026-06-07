# codex-user-level-gstack-delivery-loop-runtime-governance Specification

## Purpose
定义仓库内 repo-local gstack delivery-loop runtime 治理边界：它只能作为 subordinate、advisory 的 R4 helper/checker lane，严格服从 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`，不得默认升级为 live user-level runtime。

## Requirements

### Requirement: gstack delivery-loop runtime SHALL remain subordinate and advisory / gstack delivery-loop runtime 必须保持从属且仅作 advisory

The repository SHALL keep gstack delivery-loop runtime surfaces subordinate to the authority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.

Repo-local gstack helper output SHALL be advisory only. It SHALL NOT replace Comet control, OpenSpec WHAT authority, Superpowers HOW discipline, harness runtime-safety gates, local-main-first integration gates, or remote-publication approval gates.

仓库必须让 gstack delivery-loop runtime surface 严格从属于 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` 的 authority order。

repo-local gstack helper 的输出只能是 advisory。它不得替代 Comet control、OpenSpec WHAT authority、Superpowers HOW discipline、harness runtime-safety gates、local-main-first integration gates 或 remote-publication approval gates。

#### Scenario: Delivery-loop dry-run remains advisory / delivery-loop dry-run 继续保持 advisory

- **WHEN** `python tools/gstack_codex_delivery_loop_runtime.py analyze --root . --json` 或其他 dry-run action 被调用
- **THEN** 输出必须包含 `authority_decision`，即记录哪一层 authority 获胜以及原因的机器可读字段
- **AND** 该决策必须保留 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` 的 priority order
- **AND** helper 不得声称 controller takeover、browser launch、telemetry enablement、durable-state mutation 或 remote publication

### Requirement: gstack R4 smoke receipts SHALL stay read-only and fixture-backed / gstack R4 smoke receipts 必须保持只读且基于 fixture

The repository SHALL allow bounded gstack R4 smoke receipts only through an explicit receipt directory. The helper MAY accept a fixture/existing install receipt for a bounded help probe, but it SHALL NOT install or clone upstream gstack by itself.

Positive R4 smoke receipts SHALL remain read-only and SHALL include timeout release, rollback readiness, transcript redaction, and an `authority_decision` field. The `authority_decision` field is the machine-readable control decision that records the winning authority layer, the applied priority order, and the allow/block reason for the gstack lane. Missing install receipt evidence SHALL produce a blocked/not-smoke-tested receipt rather than a false positive.

仓库只能通过显式 receipt directory 允许有边界的 gstack R4 smoke receipts。helper 可以接受 fixture/existing install receipt 来执行 bounded help probe，但不得自行 install 或 clone upstream gstack。

正向 R4 smoke receipt 必须保持 read-only，并且包含 timeout release、rollback readiness、transcript redaction 与 `authority_decision`；这里的 `authority_decision` 是 lane 的机器可读优先级与 allow/block 解释。缺少 install receipt 证据时，必须生成 blocked/not-smoke-tested receipt，而不是伪造正向结果。

#### Scenario: Missing install receipt yields blocked smoke evidence / 缺少 install receipt 时生成 blocked smoke evidence

- **WHEN** `python tools/gstack_codex_delivery_loop_runtime.py smoke --receipt-dir <dir> --json` 在没有 install receipt 的情况下运行
- **THEN** helper 必须写出 blocked receipt
- **AND** 该 receipt 必须保持 `smoke_tested=false`
- **AND** checker 只能把它视为诚实的 blocked evidence，而不是正向 smoke-tested 结果

#### Scenario: Positive smoke remains non-live evidence / 正向 smoke 仍然只是非 live 证据

- **WHEN** helper 使用有效 fixture/existing install receipt 运行 smoke
- **THEN** 该 receipt 必须限制为 bounded help/read-only evidence
- **AND** 它不得启用 hooks、browser QA、telemetry、user-level state mutation 或 active-candidate behavior

### Requirement: gstack governance checker SHALL fail closed on priority drift or live markers / gstack governance checker 必须在优先级漂移或 live markers 出现时 fail closed

The repository SHALL provide a gstack governance checker that validates bilingual plan markers, dry-run surfaces, smoke receipts, guard/CI wiring, and the authority order.

The checker SHALL fail closed when the priority order drifts, `authority_decision` is missing, smoke receipts claim live/write behavior, or required tests/guard steps are absent.

仓库必须提供一个 gstack governance checker，用于校验 bilingual plan markers、dry-run surfaces、smoke receipts、guard/CI wiring 与 authority order。

当 priority order 漂移、缺少 `authority_decision` 字段（即缺少记录胜出 authority layer、优先级结果与 allow/block reason 的机器可读控制决策）、smoke receipts 声称 live/write behavior，或必需 tests/guard steps 缺失时，checker 必须 fail closed。

#### Scenario: Forbidden live markers are present / 出现 forbidden live markers

- **WHEN** 某个 gstack smoke receipt 或 runtime output 声称 write、browser、telemetry、active-candidate 或 remote-publication behavior
- **THEN** `python tools/check_gstack_codex_delivery_loop.py --root . --receipt-dir <dir> --json` 必须 fail closed
- **AND** checker 必须返回 sanitized blocker codes，而不是把这些 evidence 当成有效 R4 behavior
