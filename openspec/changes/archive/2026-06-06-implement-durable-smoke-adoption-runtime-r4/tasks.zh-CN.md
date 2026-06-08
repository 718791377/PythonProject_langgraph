# Tasks

## 1. OpenSpec 与 design

- [x] 1.1 创建 durable smoke R4 runtime 的 bounded OpenSpec change package。
- [x] 1.2 记录 helper-only design 与 non-adoption boundary。

## 2. Runtime 与 checker

- [x] 2.1 新增 read-only durable routing smoke runner，将 R4 receipt 写入显式 path。
- [x] 2.2 新增 fail-closed receipt validation，覆盖 timeout release、rollback readiness、transcript redaction、backend-family evidence 与 non-adoption fields。
- [x] 2.3 新增 focused tests，覆盖 valid smoke receipts、adoption-claim rejection、transcript bounds、runner success 与 unsafe apply-command rejection。

## 3. Registration 与 documentation

- [x] 3.1 在 OpenSpec guard JSON 与 non-JSON paths 中注册新 checker。
- [x] 3.2 在 CI manifest 中注册新 test。
- [x] 3.3 更新 durable smoke/adoption implementation plan 与 stable spec pair。

## 4. Validation 与 local integration

- [x] 4.1 运行 focused tests、receipt checker、runner smoke 与 receipt validation。
- [x] 4.2 运行 OpenSpec validation；precommit update/archive review 与 repository guard 作为 post-archive gates。
- [x] 4.3 归档已完成的 OpenSpec change 并重跑 validation。
- [ ] 4.4 在 clean feature worktree 上运行 local gate 与 local MR review。
- [ ] 4.5 合入本地 `main`，运行 post-merge validation，清理已集成 feature worktree/branch，并停在 remote-publication gate。
