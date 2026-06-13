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

## Verify
- [x] Variance review 已记录：旧 cache wording、bilingual pair、claim-lock、receipt schema blocker 均已修复。
- [x] Risk/change impact 已记录：tracked 文档只保留 derived evidence，不提交 raw source text。
- [x] Control decision 已记录：OpenSpec guard JSON 模式 66/66 通过后继续 local gate。

## Archive
- [ ] Local validation 后总结 value outcome。
- [ ] Archive 前记录 lessons learned。
- [ ] 通过 archive path 与 promoted stable specs 捕获 archive/sync evidence。

## Monitoring
- [x] Current facts 已记录。
- [x] Return/no-return decision：continue。
