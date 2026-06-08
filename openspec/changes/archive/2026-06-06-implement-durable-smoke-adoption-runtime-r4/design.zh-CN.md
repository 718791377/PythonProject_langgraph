# Design: Durable Smoke Adoption Runtime R4

R4 runtime 保持有意的小范围。`run_durable_routing_smoke.py` 只执行 bounded local Python checker command，默认目标是已有 durable routing smoke gate template checker，并只写一个显式 receipt file。Helper 会校验 command 必须以 Python 开头，目标必须是 repository `tools/check_*.py` script，且不能包含 apply、durable-team、remote-publication 或 LangGraph launch markers。

Receipt 是 evidence，不是 adoption。Receipt 字段 glossary：`runtime_stage=R4` 表示这是 R4 smoke 阶段收据；`stage=smoke-tested` 表示已执行 smoke 验证；`routing_mode=read_only` 表示只读路由；`state_write_policy=receipt_only` 表示唯一写入是显式 receipt path；`adoption_performed=false`、`durable_workflow_selected=false`、`durable_workflow_running=false`、`durable_workflow_adopted=false` 表示没有选中、运行或采纳 durable workflow；`mutation_allowed=false`、`user_level_state_mutated=false` 表示不允许也没有执行 user-level mutation；`durable_team_launched=false`、`omx_apply_performed=false`、`langgraph_thread_started=false` 表示没有启动 durable team、没有执行 apply、没有启动 LangGraph thread；`remote_publication_authorized=false` 表示该 receipt 不提供远程发布授权。

`check_durable_routing_smoke_receipts.py` 校验 receipt shape，并对 adoption claim、unbounded transcript、raw sensitive data、timeout failure、missing rollback readiness 和 unsafe backend evidence fail closed。Checker 默认运行 positive 与 negative fixtures，因此 OpenSpec guard 可以在不创建 live durable state 的情况下验证 receipt contract。

Apply-mode adoption、selected/running/adopted receipts 与 live handoff receipts 仍然是后续 Stage D work。本 R4 slice 的边界是：smoke success 可以被证明，但不能被升级为 adoption。
