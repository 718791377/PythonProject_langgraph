# 管理检查清单

## 打开
- [x] 已在 proposal 中记录价值和原因。
- [x] 成功标准记录为 fresh extraction、双语刷新和验证证据。
- [x] 约束已记录：不提交原始源文本、不复用旧缓存、不进行远程发布。

## 设计
- [x] 已记录交付裁剪方式：以本地忽略的 extraction evidence 支撑文档与治理刷新。
- [x] 已记录风险：PDF extraction fallback、旧缓存措辞、双语漂移，以及白皮书与 research 角色混淆。
- [x] 已记录验收证据路径：extraction manifest、source report、OpenSpec validation、guard、local gate。

## 构建
- [x] 已选择执行模式。实现工作在隔离 worktree 中直接完成，并为独立切片选择 durable worker lane。
- [x] 已记录质量证据：TDD、review、test 或等效证据。证据包括 extraction coverage、diff review、OpenSpec validation、repository guard、local gate、local MR review 和 post-merge local gate。
- [x] 阻塞项已清除或已有显式决策。claim-lock、receipt schema、stale-cache wording 和 bilingual drift 等构建阻塞项已在最终本地集成前修正。
- [x] 当前 evidence run 记录为 `fresh-source-lifecycle-whitepaper-pmi-refresh-20260614`，生成时间为 `2026-06-14T10:48:53Z`。
- [x] native expert review 发现中文 mojibake 与双语漂移；leader 已在最终验证前修复这些阻塞项。

## 验证
- [x] 已检查相对 scope、design 和 acceptance criteria 的偏差。stale-cache wording、bilingual pair、claim-lock 与 receipt-schema 阻塞项已修正。
- [x] 已评估风险和变更影响。tracked docs 只保留派生证据；raw source text 继续留在 ignored 路径之外。
- [x] 已记录控制决策。最终 validation、本地 main 集成和 post-merge local gate 完成后继续归档。
- [x] 在 2026-06-14 evidence 与双语修复后，重新运行 OpenSpec validation、repository guard、pre-commit update/archive review、local gate 和 local MR review。
- [x] 最终 commit 前的 fresh validation evidence：`openspec validate fresh-source-lifecycle-whitepaper-pmi-refresh-20260613 --strict` 通过；`python tools/run_openspec_guard.py --root . --json` 通过 66/66；`python tools/check_precommit_update_archive.py --root . --json` 通过；`tools/ci/local_gate.ps1 -StepTimeoutSeconds 5400` 返回 `local_ci_gate: ok`。

## 归档
- [x] 已总结价值结果。2026-06-14 fresh source-read refresh 更新了 lifecycle、whitepaper、research、North Star、PMI tailoring 和 bridge 文档，然后在本地 main `571129adc94dbe1482fa7f3c94fbbf92e681a475` 完成合并。
- [x] 已记录 lessons learned 或可复用指导。whitepaper 与 research 保持不同 lifecycle role；通过 10-to-12 bridge 和 playbook authority stack 打通，而不是重复或物理合并两者。
- [x] 已确认 delta spec sync、verification evidence 和 archive path。Delta specs 已合并进现有稳定 capability `openspec/specs/codex-product-lifecycle-document-governance/`；archive path 为 `openspec/changes/archive/2026-06-15-fresh-source-lifecycle-whitepaper-pmi-refresh-20260613/`。

## 监控
- [x] 已检查当前事实。
- [x] 已做出 continue、adjust、stop 或 return 决策。决策：继续归档；无需返回较早阶段。
