## ADDED Requirements

### Requirement: Spec Kit authority guard SHALL validate generated surfaces and subordinate dry-run receipts / Spec Kit authority guard 必须校验生成表面和从属 dry-run 收据

仓库必须通过 generated-surface 与 runtime-receipt 检查，把 Spec Kit 严格保持在 Comet、OpenSpec、Superpowers、本地 main 优先门禁与远端发布门之下，避免任何 Spec Kit 表面被误当成仓库治理权威。

`tools/check_spec_kit_authority_guard.py` 必须对 `.specify/`、根目录 `specs/`、生成的 `.codex/commands/*speckit*`、`.codex/skills/*speckit*`、`.github/prompts/*speckit*`、`/speckit.*`、`$speckit-*`、extension、preset 与 workflow-output fail closed，除非单独的 active authority-migration plan 明确拥有该变更。任何 `specify init` 或 `specify self check` 命令证据都必须保持为 blocked subordinate command evidence，除非同一 authority-migration plan 明确拥有该命令边界。

仓库必须提供 `tools/spec_kit_subordinate_runtime.py` 作为 dry-run-only 的 subordinate helper。该 helper 只能支持 `source-refresh`、`probe`、`plan-dry-run`、`init-dry-run` 与 `self-check-dry-run`，必须拒绝 live 或 apply 模式名，不得运行 live `specify`，不得创建 `.specify/` 或根目录 `specs/`，也不得写入生成的 command、skill、prompt、extension、preset 或 workflow-output 表面。

Spec Kit subordinate runtime receipt 必须包含 `dry_run_only=true`、`source_url`、`source_pin`、`authority_decision` 与 `surface_status`。在 R4 中，`authority_decision.decision` 只能是 `blocked` 或 `subordinate`，必须记录胜出的 authority layer，并且必须保留精确优先级顺序 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。

#### 场景：生成的 Spec Kit command surface 被阻止

- **WHEN** 某个变更或现存仓库路径包含 `.codex/commands/speckit.plan.md`
- **AND** 没有 active Spec Kit authority-migration plan 拥有该生成 command surface
- **THEN** `python tools/check_spec_kit_authority_guard.py --root . --json` 必须失败

#### 场景：dry-run subordinate receipt 被接受

- **WHEN** `tools/spec_kit_subordinate_runtime.py probe --root <repo> --receipt-out <receipt>` 写出 dry-run receipt
- **AND** 该 receipt 记录了 `authority_decision.decision=subordinate`、`dry_run_only=true`、source evidence 与完整 surface status
- **THEN** `python tools/check_spec_kit_authority_guard.py --root <repo> --receipt <receipt> --json` 必须通过

#### 场景：live 或 apply mode 被拒绝

- **WHEN** 操作员请求 `tools/spec_kit_subordinate_runtime.py apply-live --root <repo>`
- **THEN** helper 必须在构建 runtime payload 前拒绝该模式
- **AND** 不得运行 live Spec Kit commands，也不得创建生成的 Spec Kit surfaces
