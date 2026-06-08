# Proposal：实现 gstack Codex delivery-loop runtime R4

## Why

仓库已经把冲突优先级固定为 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`，但 gstack lane 仍缺少可执行的 repo-local enforcement。没有有边界的 checker 与 runtime helper，后续实现可能会让 gstack 错误地高于 Comet、绕过 OpenSpec/Superpowers、与 harness runtime-safety 边界重叠，或被误当成真实 installed user-level runtime。

## What Changes

- 新增 `tools/gstack_codex_delivery_loop_runtime.py`，提供 repo-local guarded helper：`analyze`、`plan-dry-run`、`review-dry-run`、`qa-dry-run`、`ship-dry-run` 与 bounded R4 `smoke`。
- 新增 `tools/check_gstack_codex_delivery_loop.py`，校验方案/runtime/checker/guard wiring、优先级证据与 smoke receipts。
- 新增 focused tests，覆盖 dry-run helper、blocked/positive R4 smoke receipts、authority priority enforcement 与 redaction。
- 在 `tools/run_openspec_guard.py`、`tools/ci/ci_test_manifest.json`、`tools/safety_rule_script_backing_registry.json` 中登记 checker 与 tests。
- 更新活跃双语 implementation plans，诚实反映 implemented-local 的 R0-R4 边界。
- 新增 stable OpenSpec requirement，使 gstack delivery-loop tooling 保持 subordinate，不会默认升级为 live user-level runtime。

## Scope

- `tools/gstack_codex_delivery_loop_runtime.py` - repo-local 受保护 runtime helper，用于 advisory dry-run actions 与 bounded R4 smoke receipts。
- `tools/check_gstack_codex_delivery_loop.py` - fail-closed checker，用于校验 priority evidence、receipt validation 与 guard wiring。
- `test/gstack_codex_delivery_loop_runtime.test.py` - 运行时 helper 的 focused regression test。
- `test/check_gstack_codex_delivery_loop.test.py` - checker 的 focused regression test，覆盖 redaction 与 fail-closed 路径。
- `tools/run_openspec_guard.py` - 聚合 OpenSpec guard 入口，必须调用新的 gstack checker。
- `tools/ci/ci_test_manifest.json` - CI 管理的 Python test manifest，必须登记新的 focused tests。
- `tools/safety_rule_script_backing_registry.json` - 记录本 lane 脚本化治理边界的 safety registry 条目。
- `docs_bilingual/implementation_plans/gstack_codex_delivery_loop_runtime_governance_plan.md` 与 `.zh-CN.md`
- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md` 与 `.zh-CN.md`
- `openspec/specs/codex-user-level-gstack-delivery-loop-runtime-governance/spec.md` 与 `.zh-CN.md`（经 archive 提升后）

## Non-Goals

- 不安装、clone 或 enable upstream gstack。
- 不启用 hooks、browser QA、telemetry 或 always-on routing。
- 不修改 user-level Codex 配置、browser state、durable backend state 或 remote Git refs。
- 不让 gstack 高于 Comet、OpenSpec/Superpowers 或 harness runtime-safety 边界。
- 不创建 R5 active-candidate 或真实 user-level live runtime 行为。

## Rollout

1. 收口当前串行化 worktree，恢复 active implementation claim。
2. 完成 repo-local R0-R4 helper/checker/tests 与 plan 更新。
3. 运行 focused tests、OpenSpec guard 与本地 gates。
4. 在同一分支 archive 该 change，使 stable spec 记录 runtime 边界。
5. 合入本地 `main` 并停在 remote-publication gate。

## Rollback

- 回退该 feature commit，或回退后续 local-`main` merge commit。
- 使用 local `main` 集成前创建的 rollback ref。
- 删除新增 repo-local helper/checker/tests，并恢复之前的 implementation-plan wording。

## Verification

- `python test/gstack_codex_delivery_loop_runtime.test.py -v` - runtime helper 的 focused regression suite。
- `python test/check_gstack_codex_delivery_loop.test.py -v` - checker 的 focused regression suite。
- `python tools/check_gstack_codex_delivery_loop.py --root . --json` - gstack lane 的 repo-local governance checker。
- `python tools/gstack_codex_delivery_loop_runtime.py smoke --root . --receipt-dir .tmp/gstack-r4-smoke --json` - 写显式 receipt path 的 bounded R4 smoke command。
- `python tools/check_precommit_update_archive.py --root . --json` - 本地包的 precommit update/archive review。
- `python tools/run_openspec_guard.py --root . --json` - 包含新 gstack checker 的 aggregate repository guard。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - 集成前共享 local CI gate。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - 集成前 local MR review gate。
