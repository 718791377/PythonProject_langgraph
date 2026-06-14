# Tasks

## 1. Governed change setup

- [x] 1.1 创建 isolated feature worktree 与 OpenSpec change package。
- [x] 1.2 记录 scope、rollback、non-goals 与 validation path。

## 2. Fresh extraction evidence

- [x] 2.1 新增 fresh-source extraction tool，支持 PDF page、EPUB spine item 与 Markdown full-document reading。
- [x] 2.2 对 `Business Management/` 与 `PMP/` 运行 summary-only inventory。
- [x] 2.3 运行 full extraction 到 ignored local cache，并记录 manifest/report evidence。
- [x] 2.4 以 `fresh-source-lifecycle-whitepaper-pmi-refresh-20260614`（`2026-06-14T10:48:53Z`）重新运行 fresh extraction，不把旧 cache 当作当前证据。

## 3. Bilingual documentation refresh

- [x] 3.1 刷新 product lifecycle synthesis、inventory、lifecycle、PMI reference 与 tailoring docs。
- [x] 3.2 刷新 whitepaper、research note 与 North Star plan，不物理合并 whitepaper 与 research。
- [x] 3.3 仅新增 auditability 所需的最小 bridge/index 文档。
- [x] 3.4 在成对英文与 zh-CN 文档中补充 bridge-time aggregation、I/T/O 权威委托、PMI 文档类型裁剪、旧版展开规则，以及 Agile/项目集/项目组合/PMO 进入退出规则。
- [x] 3.5 清除 touched tracked documents 中的 mojibake 与旧日期残留。

## 4. Validation and integration readiness

- [x] 4.1 验证 extraction coverage、stale-cache wording、双语一致性与 mojibake absence。
- [x] 4.2 运行 OpenSpec validation、precommit update/archive review 与 repository guard。
- [x] 4.3 运行 local gate 与 local MR review，并准备 local-main-first integration package。
