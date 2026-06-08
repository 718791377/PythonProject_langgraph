---
change: implement-r5-runtime-governance-batch-20260607
design-doc: openspec/changes/implement-r5-runtime-governance-batch-20260607/design.md
status: active
translation_of: docs/superpowers/plans/2026-06-07-implement-r5-runtime-governance-batch.md
---

# 实施计划：R5 Runtime Governance Batch

## 关键路径

1. 基础 receipt/checker model。
2. 用户级 CLI 敏感 action receipt 门禁。
3. delivery/harness R5 门禁。
4. Spec Kit subordinate R5 门禁。
5. 验证、归档、本地 main 集成。

## TDD 合约

每个 slice 先增加或更新 focused test，运行并观察失败，然后实现最小 checker/runtime 变更，再重跑 focused test，最后提交该 plan slice。

## 提交边界

实践上尽量每个请求的 plan 对应一个本地 commit。紧耦合的基础代码可共享 helper 实现，但 documentation/status 更新需在 commit history 中保持可见。

## 远端边界

本批次不 push，不 create/update/merge GitLab MR，不 sync GitHub，除非后续用户消息明确命名 remote publication。
