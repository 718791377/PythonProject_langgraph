## Context

目标 implementation plan 已成为 automatic collaboration routing 的核心 active baseline。它已有主要 policy 内容，但顶部仍保留上一次 tweak 的 framing；当前用户明确要求完整 `/comet` 重构，因此需要补齐 workflow evidence，同时不能伪称 runtime enforcement 已改变。

当前 Windows shell 不提供 `bash`。Comet shell helper scripts 存在但不能运行，因此本设计记录 blocker，并用 OpenSpec/Superpowers artifacts 与仓库验证作为 fallback evidence。

## Design Decision

采用 documentation-only full Comet workflow：

1. 保留 source-of-truth policy 内容。
2. 在中文计划顶部增加 full Comet reading path 与 artifact map。
3. 同步更新英文 companion 的 high-level full Comet framing。
4. 增加 Phase 4 boundary note，说明 full Comet refactor 只是 traceability evidence，不是 Phase 4 implementation。
5. 创建 full workflow 通常需要的 OpenSpec 与 Superpowers artifacts。
6. 验证后使用 `--skip-specs` 归档，因为本 change 不引入应提升为 stable OpenSpec spec 的 runtime contract。

## Risks and Mitigations

- 风险：读者把 refactor 当作 runtime evidence。缓解：在目标计划、OpenSpec artifacts 与 verification report 中重复 documentation-only boundary。
- 风险：双语漂移增加。缓解：同步更新英文 companion 的高层 framing。
- 风险：过度声称 shell helper transition。缓解：记录 `bash_unavailable_in_current_windows_shell`。
- 风险：Phase 4 被误认为已完成。缓解：保持 Phase 4 为 `planned follow-up`。
