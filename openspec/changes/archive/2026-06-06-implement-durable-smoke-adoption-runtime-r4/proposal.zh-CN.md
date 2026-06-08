# Change: 实现 Durable Smoke Adoption Runtime R4

## 为什么

Durable smoke/adoption gate template 已经完成评审，但 Stage D runtime backlog 仍需要一个可执行的 R4 smoke helper。如果没有具体 helper 与 receipt checker，未来 session 可能把 read-only smoke 成功误解为 durable workflow adoption、backend selection、`omx-team-auto.ps1 -Apply`、LangGraph thread start 或 remote publication approval。

## 变更内容

- 新增 `tools/run_durable_routing_smoke.py` - 运行 bounded read-only smoke，只允许 safe local Python checker command，并将 sanitized R4 `smoke-tested` receipt 写入显式 receipt path。
- 新增 `tools/check_durable_routing_smoke_receipts.py` - 校验 timeout release、rollback readiness、bounded redacted transcript、backend-family evidence 与 explicit non-adoption fields。
- 新增 focused regression coverage - 覆盖 valid receipt、adoption claim 拒绝、transcript 边界、runner success 与 unsafe apply-command 拒绝。
- 更新 OpenSpec guard 与 CI manifest - 确保新 checker/test 进入本地和远程共享 gate 的执行序列。
- 更新 durable smoke/adoption implementation plan 与 stable automatic-team-routing spec - 记录 R4 smoke receipt runtime 已实现，同时保留 apply-mode adoption 与 live handoff receipts 为 pending。

## 非目标

- 本 slice 不实现 apply-mode adoption，也不写 selected/running/adopted durable workflow receipts。
- 不运行 `omx-team-auto.ps1 -Apply`、`omx team`、LangGraph `dev` 或 thread start。
- 不将 `.omx/state/` 写作 durable backend state；runner 只写调用方显式指定的 smoke receipt path。
- 不修改 user-level configuration 或 remote Git refs。

## 验证

- `python test/check_durable_routing_smoke_receipts.test.py -v` - 运行 focused runner/checker regression tests，证明 R4 receipt 正向与负向行为。
- `python tools/check_durable_routing_smoke_receipts.py --root . --json` - 运行 receipt checker self-test，证明 adoption claim 与 unbounded transcript 会 fail closed。
- `python tools/run_durable_routing_smoke.py --root . --receipt .tmp/durable-routing-smoke-receipt.json --json` - 运行 bounded read-only smoke runner，证明只写显式 receipt path 且不执行 adoption。
- `openspec validate implement-durable-smoke-adoption-runtime-r4 --strict` - 验证本 change 的 OpenSpec 结构与 delta spec。
- `openspec validate --all` - 验证归档后全仓库 OpenSpec 状态。
- precommit、OpenSpec guard、local CI 与 local MR review gate - 在本地 main 集成前验证整个包。
