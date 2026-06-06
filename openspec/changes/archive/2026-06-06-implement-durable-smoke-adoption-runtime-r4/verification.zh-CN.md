# Verification Report

## 归档前命令

- `python test/check_durable_routing_smoke_receipts.test.py -v` - 运行 focused regression tests；结果为 6 个 tests passed。
- `python tools/check_durable_routing_smoke_receipts.py --root . --json` - 运行 checker self-test；结果为 `ok: true`，并包含 3 个 negative self-test fixtures。
- `python tools/run_durable_routing_smoke.py --root . --receipt .tmp/durable-routing-smoke-receipt.json --phase verify-accept --task "manual focused smoke" --candidate-backend-family langgraph --json` - 运行 manual focused smoke；结果为 `ok: true`，且 adoption/mutation 字段均保持 false。
- `python tools/check_durable_routing_smoke_receipts.py --root . --receipt .tmp/durable-routing-smoke-receipt.json --json` - 校验上一步生成的 receipt；`runtime_stage=R4` 表示 R4 阶段，`stage=smoke-tested` 表示 smoke 已测试，`adoption_state=not_adopted` 表示没有 adoption。
- `openspec validate implement-durable-smoke-adoption-runtime-r4 --strict` - 验证 change 本身；结果为 valid。

## 字段说明

- `ok: true` - checker 或 runner 本次执行通过。
- `runtime_stage=R4` - 该 receipt 属于 R4 smoke runtime 阶段。
- `stage=smoke-tested` - 只能证明 smoke 已测试，不能证明 durable workflow adoption。
- `adoption_state=not_adopted` - 显式记录没有采纳 durable workflow。

## 边界复核

R4 helper 只写显式 smoke receipt path，记录 timeout release 与 rollback readiness，不执行 apply-mode adoption、durable-team launch、LangGraph thread start、durable backend state mutation、user-level state mutation 或 remote publication authorization。

## 归档计划

Active delta 在同一 feature branch 内归档，将 R4 smoke receipt requirement promoted 到 stable automatic-team-routing spec。Remote publication 仍然未授权。

## Value outcome

R4 现在拥有 executable read-only smoke runner 与 fail-closed receipt checker。该实现证明 `smoke-tested` evidence，但不证明 selected/running/adopted durable workflow state、apply-mode execution、durable-team launch、LangGraph thread start、durable backend mutation、user-level mutation 或 remote publication authorization。

## Lessons learned

Smoke evidence 与 adoption evidence 必须保持为不同的 receipt class。后续 apply-mode helper 必须要求 explicit operator authorization、backend-family ownership、timeout release、rollback readiness、cleanup evidence，以及独立 selected/running/adopted/released receipt path，不能把 R4 smoke success 直接升级为 adoption。
