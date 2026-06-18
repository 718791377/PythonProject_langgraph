---
doc_id: fresh_source_reading_evidence
lang: zh-CN
canonical: docs_bilingual/product_lifecycle/fresh_source_reading_evidence.md
translation_of: docs_bilingual/product_lifecycle/fresh_source_reading_evidence.md
doc_class: product_lifecycle
status: draft
---

# Fresh Source Reading Evidence 索引

本索引记录生命周期、白皮书、研究稿、北极星和一人公司运营刷新的当前 fresh-reading 证据边界。

## Business Management 与 PMP 抽取

- Run ID: `one-person-company-pmi-refresh-stageb-20260619`
- Generated at: `2026-06-18T18:37:58Z`
- Output root: `.omx/state/langgraph/extraction/business_pmp_20260619/`
- Source roots: `D:/PythonProject_langgraph/Business Management` 和 `D:/PythonProject_langgraph/PMP`
- Sources: 54 total；31 Business Management；23 PMP
- Units: 9,656 total；9,280 PDF pages；362 EPUB spine items；14 Markdown full documents
- Extracted characters: 18,492,044
- Blank units / low-text units: 1,034 / 1,590
- Status: all sources `ok`

| Family | Sources | Units | Characters | Format coverage |
| --- | ---: | ---: | ---: | --- |
| Business Management | 31 | 6,551 | 14,161,228 | 22 PDFs / 6,245 pages；7 EPUBs / 304 spine items；2 Markdown full files |
| PMP | 23 | 3,105 | 4,330,816 | 9 PDFs / 3,035 pages；2 EPUBs / 58 spine items；12 Markdown full files |

## Product Lifecycle Markdown 全文读取

- Run ID: `one-person-company-pmi-refresh-stageb-product-lifecycle-20260619`
- Generated at: `2026-06-18T18:48:14Z`
- Source root: `docs_bilingual/product_lifecycle/`
- Markdown documents: 26
- Full-document units: 26
- Extracted characters: 297,871
- Status: all documents `ok`

## 提交边界

Manifest 和 report 可被跟踪文档引用。原始 `fresh_source_items.jsonl` 与本地抽取 manifest 是忽略态本地证据，不得提交。

## 刷新规则

不要用记忆或旧缓存更新上述数量。必须重新运行 `tools/fresh_extract_sources.py` 读取本地源根；当生命周期文档本身属于输入集时，也要全文重读生命周期 Markdown，并用新 run ID 更新本索引。
