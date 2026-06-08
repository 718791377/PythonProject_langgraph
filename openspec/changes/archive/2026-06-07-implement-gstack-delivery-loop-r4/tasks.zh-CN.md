# Tasks

## 1. OpenSpec 与 design

- [x] 1.1 创建 gstack Codex delivery-loop runtime R4 的 bounded OpenSpec change package。
- [x] 1.2 记录严格 conflict-priority 边界与 implemented-local 的 R0-R4 scope。

## 2. Runtime 与 checker

- [x] 2.1 新增 repo-local gstack delivery-loop runtime helper，包含 dry-run actions 与 bounded R4 smoke receipts。
- [x] 2.2 新增 fail-closed checker，用于校验 priority evidence、receipt validation 与 guard/CI registration。
- [x] 2.3 保持 runtime helper 为 advisory-only，且除显式 smoke receipt path 外不产生 mutation。

## 3. Tests 与 registration

- [x] 3.1 新增 focused tests，覆盖 dry-run output、blocked smoke receipts、positive smoke receipts、forbidden live/write markers 与 redaction。
- [x] 3.2 在 `tools/ci/ci_test_manifest.json` 中登记新 tests。
- [x] 3.3 在 `tools/run_openspec_guard.py` 与 `tools/safety_rule_script_backing_registry.json` 中登记 checker。

## 4. Documentation 与 spec sync

- [x] 4.1 更新 gstack 子方案与父方案，反映 implemented-local 的 R0-R4 边界。
- [x] 4.2 新增专用 stable spec delta，描述 gstack delivery-loop runtime governance lane。

## 5. Validation 与 archive

- [x] 5.1 运行 focused tests 与 gstack checker。
- [x] 5.2 运行 `python tools/check_precommit_update_archive.py --root . --json` 与 `python tools/run_openspec_guard.py --root . --json`。
- [x] 5.3 Archive 已完成的 OpenSpec change 并重新运行 OpenSpec validation。
- [x] 5.4 在干净 feature worktree 上运行 local gate 与 local MR review。
