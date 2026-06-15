# 设计：fresh source lifecycle, whitepaper, north star, and PMI tailoring refresh

## 决策

1. Raw source extraction 只保留在 ignored local state 中。Tracked 文档只记录 counts、statuses、hashes、source-to-document mappings 与 synthesis。
2. 两个目标系统视为并行 lifecycle profiles，而不是同一 profile 的成熟度等级。
3. Whitepaper 与 research note 保持物理分离。Whitepaper 负责 strategic narrative；research note 负责 production-capability evidence 与更严格的 governance reasoning。
4. 以 PMBOK 8 与当前 PMI practice guides 作为 primary delivery-governance 输入；旧 PMBOK/process-group/agile/program/portfolio 来源提供 historical 与 execution overlays。
5. 涉及执行层面的 lifecycle 内容必须采用 process-group style：Inputs、Tools and Techniques、Outputs。

## Extraction Architecture

工具枚举指定 source root 下的 `Business Management/` 与 `PMP/` 文件，并写入：

- `fresh_source_manifest.json`：run metadata、source inventory、counts、hashes 与 status。
- `fresh_source_items.jsonl`：每个 PDF page、EPUB spine item 或 Markdown full document 的记录。
- `fresh_source_synthesis.json`：用于 tracked-document refresh 的 compact derived mapping counts 与 keyword evidence。
- `fresh_source_report.md` 与 `.zh-CN.md`：human-readable local evidence summaries。

PDF extraction 先使用 `pypdf`，当 file/page extraction 失败时 fallback 到 PyMuPDF/fitz。EPUB extraction 按 spine order 读取，并只按 metadata 跳过 navigation entries。Markdown extraction 以 UTF-8 读取全文，并 fallback 到 UTF-8-SIG。

## Document Architecture

- Source synthesis documents 说明 fresh-read coverage 与 source-family roles。
- Inventory maps 保持两个 target profiles 的 numerical authority。
- Lifecycle docs 将这些 profiles 应用于 Codex platform build 与 downstream consumption。
- PMI reference 与 tailoring docs 定义何时使用 full、whole-project lightweight、phase-local lightweight、module-level lightweight 或 hybrid architecture。
- Whitepaper/research/North Star 总结 bridge，并指向详细 lifecycle docs。
- 本次实施重跑使用 evidence run `fresh-source-lifecycle-whitepaper-pmi-refresh-20260614`，生成时间 `2026-06-14T10:48:53Z`。OpenSpec change id 仍保留原始 `fresh-source-lifecycle-whitepaper-pmi-refresh-20260613` 包名。
- 10-to-12 layer bridge 是桥接时聚合视图，不替代研究稿 canonical 10-layer runtime list。
- 面向执行的新增内容把详细 I/T/O 权威委托给 lifecycle 与 PMI mapping 文档，不在 whitepaper 或 North Star 中重复完整过程语法。

## 风险控制

- Stale cache references 必须改写为 historical/non-current evidence。
- 不提交 tracked raw source text。
- Bilingual documents 必须以 English 与 zh-CN 成对更新。
- 中文文本必须以 UTF-8 写入并验证；mojibake/three ASCII question marks 新增内容是 release blocker。
- Count constraints 在文本中显式验证，必要时用脚本检查。
