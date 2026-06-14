# 变更：fresh source lifecycle, whitepaper, north star, and PMI tailoring refresh

## 为什么

产品生命周期、白皮书、研究记录和 North Star 文档此前引用了旧的 ignored extraction cache。当前请求要求先重新读取本地 `Business Management/` 与 `PMP/` 来源，再刷新 tracked 文档，并说明 10 层 runtime research model 与 12 层 product/business lifecycle model 的关系。

## 变更内容

- 新增 fresh-source extraction 工具，按 PDF page、EPUB spine item、Markdown full document 读取来源。
- 生成新的 ignored local extraction cache 与 summary manifest。当前实施重跑为 `fresh-source-lifecycle-whitepaper-pmi-refresh-20260614`，生成时间 `2026-06-14T10:48:53Z`；OpenSpec change id 仍保留 `fresh-source-lifecycle-whitepaper-pmi-refresh-20260613`，作为受治理变更包名称。
- 刷新双语 product lifecycle 文档、Codex durable-team whitepaper、solo-maintainable research note 和 North Star plan，使它们引用本次 fresh evidence run，而不是把旧 cache 当作当前事实。
- 新增必要的 bridge/index 文档，使 source evidence、10-to-12-layer mapping 与 PMI tailoring decisions 可审计。

## 范围

- `tools/fresh_extract_sources.py`：抽取与 evidence manifest 工具。
- `docs_bilingual/product_lifecycle/`：生命周期、inventory、source synthesis、PMI reference 与 tailoring 文档。
- `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.*`：战略白皮书关系与证据刷新。
- `docs_bilingual/governance/solo_maintainable_production_persistent_team_research.*`：研究记录关系与 10-to-12-layer bridge 刷新。
- `docs_bilingual/north_star_plan.*`：指标与 evidence 刷新。
- 本 OpenSpec change package。

## 非目标

- 不提交 raw extracted source text 或受版权保护的书籍原文。
- 不把旧 `.omx/state/langgraph/extraction/` cache 当作当前内容证据。
- 不把 whitepaper 与 research note 物理合并为一个文件。
- 不修改 remote publication state。

## 推出

1. 创建 governed change package 与 isolated worktree。
2. 实现并运行 fresh extraction，输出到 ignored local cache。
3. 仅使用 derived summary evidence 与 source-to-document mappings 刷新双语文档。
4. 验证 extraction coverage、quantity constraints、stale-cache wording、bilingual pair consistency、OpenSpec guard 与 local gates。
5. validation 通过后提交 package，并仅按 local-main-first flow 集成。

## 回滚

- Revert feature branch 或 local main merge commit。
- 如有需要，删除 ignored local `.omx/state/langgraph/extraction/fresh-source-lifecycle-whitepaper-pmi-refresh-20260614/` cache。
- 本变更不修改 remote、external 或 downstream project state。

## 验证

- `python tools/fresh_extract_sources.py --source-root D:/PythonProject_langgraph --output-root ./.omx/state/langgraph/extraction/fresh-source-lifecycle-whitepaper-pmi-refresh-20260614 --run-id fresh-source-lifecycle-whitepaper-pmi-refresh-20260614 --summary-only` - 验证 source inventory counts，不重写 tracked conclusions。
- `python tools/fresh_extract_sources.py --source-root D:/PythonProject_langgraph --output-root ./.omx/state/langgraph/extraction/fresh-source-lifecycle-whitepaper-pmi-refresh-20260614 --run-id fresh-source-lifecycle-whitepaper-pmi-refresh-20260614` - 重新生成 ignored full extraction evidence cache。
- `openspec validate fresh-source-lifecycle-whitepaper-pmi-refresh-20260613 --strict` - 验证本 OpenSpec change package。
- `python tools/run_openspec_guard.py --root . --json` - 验证 repository OpenSpec 与 documentation-governance guard rules。
- `python tools/check_precommit_update_archive.py --root . --json` - 验证 pre-commit update/archive readiness。
- `$env:PYTHONUTF8="1"; $env:PYTHONIOENCODING="utf-8"; powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1 -StepTimeoutSeconds 1800` - 运行 shared local CI gate。
