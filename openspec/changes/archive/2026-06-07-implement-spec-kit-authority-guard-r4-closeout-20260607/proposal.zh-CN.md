# 变更：实现 Spec Kit Authority Guard R4 收口

## 为什么

当前 Spec Kit authority guard 已经具备 dry-run subordinate runtime 与定向测试，但 R4 收口证据仍不完整。helper 与测试必须强制执行严格冲突顺序 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`，同时 stable safety-rule spec 与 script-backing registry 也必须记录该契约，本切片才能算完成。

## 变更内容

- 收紧 `tools/spec_kit_subordinate_runtime.py` 与 `tools/check_spec_kit_authority_guard.py` 的精确优先级 receipt 契约。
- 扩展定向测试：runtime receipt 必须包含严格优先级；缺失该字段时 guard 必须拒绝。
- 将缺失的 R4 收口 requirement 提升进稳定的 `codex-user-level-safety-rule-script-backing` spec 双语对。
- 更新 safety-rule script-backing registry 与两份 Spec Kit implementation plan，使 `spec_kit_authority_guard_plan` 成为主归口，而 `spec_kit_subordinate_adapter_governance_plan` 保持从属 companion。

## 范围

- `tools/spec_kit_subordinate_runtime.py` - dry-run 从属 runtime helper。
- `tools/check_spec_kit_authority_guard.py` - fail-closed 的 Spec Kit authority checker 与 receipt validator。
- `test/spec_kit_subordinate_runtime.test.py` - 定向 runtime receipt 契约回归测试。
- `test/spec_kit_authority_guard.test.py` - 定向 authority-guard 与 receipt-validation 回归测试。
- `openspec/specs/codex-user-level-safety-rule-script-backing/spec.md` - 稳定英文 safety-rule requirement。
- `openspec/specs/codex-user-level-safety-rule-script-backing/spec.zh-CN.md` - 稳定中文 safety-rule requirement。
- `tools/safety_rule_script_backing_registry.json` - 本规则的 executable-control registry 条目。
- `docs_bilingual/governance/spec_kit_subordinate_adapter_policy.*` - subordinate adapter 治理文本。
- `docs_bilingual/implementation_plans/spec_kit_authority_guard_plan.*` - 主 implementation plan 文本。
- `docs_bilingual/implementation_plans/spec_kit_subordinate_adapter_governance_plan.*` - companion subordinate plan 文本。

## 非目标

- 不运行 live `specify`。
- 不创建 `.specify/`、根目录 `specs/`，也不生成 `/speckit.*` / `$speckit-*` 表面。
- 不执行 GitLab / GitHub 远端发布。

## 推进顺序

1. 先收紧测试，要求严格优先级。
2. 再更新 runtime helper 与 guard 满足新测试契约。
3. 然后补齐缺失的 R4 stable-spec 与 registry 收口。
4. 运行定向测试、OpenSpec validation、precommit review、repository guard、local gate 与 local MR review。
5. 在同一 feature branch 上 archive 本 change，随后合入本地 `main`，并停在远端发布门。

## 回滚

- 回滚 feature branch 提交或本地 `main` 合入提交。
- 若本地 `main` 已移动，则使用本地集成前创建的 rollback ref。
- 本切片始终保持 dry-run only，因此不需要回滚任何 user-level runtime state。

## 验证

- `python test/spec_kit_subordinate_runtime.test.py` - 运行定向 subordinate-runtime receipt 测试。
- `python test/spec_kit_authority_guard.test.py` - 运行定向 authority-guard 测试。
- `python tools/check_spec_kit_authority_guard.py --root . --json` - 校验仓库表面与 receipt 规则。
- `openspec validate implement-spec-kit-authority-guard-r4-closeout-20260607 --strict` - 校验当前 closeout change。
- `openspec validate --all` - 校验所有 changes 与 stable specs。
- `python tools/check_precommit_update_archive.py --root . --json` - 在提交前确认 update/archive readiness。
- `python tools/run_openspec_guard.py --root .` - 运行仓库 OpenSpec guard。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - 运行共享 local CI gate。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - 运行本地 MR review gate。
