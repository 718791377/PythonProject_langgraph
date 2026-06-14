# Management Checklist

## Open
- [x] Proposal 已记录 value 与 why。
- [x] Success criteria 已记录为 fresh extraction、bilingual refresh 与 validation evidence。
- [x] Constraints 已记录：不提交 raw source text、不复用旧 cache、不进行 remote publication。

## Design
- [x] Delivery tailoring 已记录：documentation/governance refresh，配合 local ignored extraction evidence。
- [x] Risks 已记录：PDF extraction fallback、stale cache wording、bilingual drift、whitepaper/research role confusion。
- [x] Acceptance evidence path 已记录：extraction manifest、source report、OpenSpec validation、guard、local gate。

## Build
- [x] Execution mode 已记录：在 isolated worktree 中直接实现，durable worker lane 用于独立切片。
- [x] Quality evidence 通过 extraction coverage、diff review 与 checker runs 记录。
- [x] Blocker decision：build start 时无 blocker。
- [x] 当前 evidence run 已记录为 `fresh-source-lifecycle-whitepaper-pmi-refresh-20260614`，生成时间 `2026-06-14T10:48:53Z`。
- [x] 原生专家审查发现中文 mojibake 与双语漂移；leader 已在最终验证前修复这些 blocker。

## Verify
- [x] Variance review 已记录：旧 cache wording、bilingual pair、claim-lock、receipt schema blocker 均已修复。
- [x] Risk/change impact 已记录：tracked 文档只保留 derived evidence，不提交 raw source text。
- [x] Control decision 已记录：OpenSpec guard JSON 模式 66/66 通过后继续 local gate。
- [ ] 在 2026-06-14 evidence 与双语修复后，重新运行 OpenSpec validation、repository guard、pre-commit update/archive review、local gate 与 local MR review。
- [x] Final pre-commit fresh validation evidence: `openspec validate fresh-source-lifecycle-whitepaper-pmi-refresh-20260613 --strict` passed; `python tools/run_openspec_guard.py --root . --json` passed 66/66; `python tools/check_precommit_update_archive.py --root . --json` passed; `tools/ci/local_gate.ps1 -StepTimeoutSeconds 5400` returned `local_ci_gate: ok`.

## Archive
- [ ] Local validation 后总结 value outcome。
- [ ] Archive 前记录 lessons learned。
- [ ] 通过 archive path 与 promoted stable specs 捕获 archive/sync evidence。

## Monitoring
- [x] Current facts 已记录。
- [x] Return/no-return decision：continue。
