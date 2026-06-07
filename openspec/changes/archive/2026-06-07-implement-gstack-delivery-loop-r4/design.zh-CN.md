# Design：gstack Codex delivery-loop runtime R4

gstack lane 被实现为 repo-local advisory tooling，而不是 controller。runtime helper 只暴露只读 delivery-loop analysis 与 bounded R4 smoke receipts；其决策始终从属于 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。

helper 只有两类执行表面：

1. dry-run actions：
   - `analyze` - 在不改文件的前提下判断当前工作处于哪个 delivery-loop 阶段。
   - `plan-dry-run` - 在保持 Comet/OpenSpec/Superpowers 权威的前提下给出下一步 delivery-loop 建议。
   - `review-dry-run` - 汇总 reviewer、QA、security 与 documentation gap，但不应用修复。
   - `qa-dry-run` - 只报告 browser-QA 可准入性与 blocker，不启动浏览器。
   - `ship-dry-run` - 只报告 local-main-first 与 remote-publication readiness，不 push 也不开 MR。

   这些 action 不写 repository files、不写 user-level state、不写 durable backend state、不写 browser state，也不改 remote refs。它们只输出 advisory JSON，其中包含 `authority_decision`、blocker summary 与 safety markers。

2. bounded R4 smoke：
   - `smoke --receipt-dir <dir> [--install-receipt <path>]` - 只写一份显式 smoke receipt；仅在 fixture/existing install evidence 存在时运行 bounded help probe。

   该命令只在调用者指定的目录里写一份 receipt。没有 install receipt 时，写 honest blocked/not-smoke-tested receipt；有 fixture/existing wrapper install receipt 时，只运行 bounded `--help` probe，脱敏私有路径与密钥，记录 timeout-release 状态，并记录 rollback-pointer hashes。它仍不安装 gstack，也不启用任何 live runtime surface。

checker 负责校验四类表面：

- plan 状态与双语 implementation-plan markers
- runtime dry-run probes
- smoke receipts 与其 `authority_decision` 字段；该字段是 gstack lane 的机器可读优先级与 allow/block 解释
- guard/CI/safety-registry registration

出现以下情况时 checker 必须 fail closed：

- 优先级字符串漂移
- 缺少 `authority_decision`，也就是 runtime lane 无法证明是哪一层 authority 获胜
- smoke receipts 声称 writes、browser launch、telemetry、active-candidate 或 remote publication
- runtime helper 无法证明所有 dry-run actions 都仅为 advisory
- 缺少必需 tests 或 guard steps

stable OpenSpec requirement 使用专门的 gstack governance spec。这样可以避免 gstack lane 静默搭载到 harness 或 adapter specs 上，同时仍保持 Comet/OpenSpec/Superpowers 为权威层。
