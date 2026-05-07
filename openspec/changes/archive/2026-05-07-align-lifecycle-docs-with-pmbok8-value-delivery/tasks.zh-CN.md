## 1. OpenSpec Artifacts

- [x] 1.1 创建 `proposal.md`，这是 PMBOK8 value-delivery alignment 的 OpenSpec proposal。
- [x] 1.2 创建 `design.md`，这是记录 reference boundaries、project-canvas scope 和 non-runtime scope 的 OpenSpec design。
- [x] 1.3 创建 `specs/codex-product-lifecycle-document-governance/spec.md`，这是 lifecycle governance 的 delta spec。

## 2. 产品生命周期文档

- [x] 2.1 更新 `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.md`，这是英文 PMI reference map；更新后以 PMBOK8 为主要叠加层，以 PMBOK6/7/Process Groups/Agile 为补充叠加层。
- [x] 2.2 更新 `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.zh-CN.md`，这是中文 PMI reference map 对照版；范围与英文主版一致。
- [x] 2.3 更新 `docs_bilingual/product_lifecycle/product_business_document_lifecycle.md`，这是英文通用 lifecycle 文档；加入 value-delivery、project-canvas、performance-domain 和 tailoring-system guidance。
- [x] 2.4 更新 `docs_bilingual/product_lifecycle/product_business_document_lifecycle.zh-CN.md`，这是中文通用 lifecycle 对照版；加入同样 guidance。
- [x] 2.5 新增 `docs_bilingual/product_lifecycle/codex_platform_project_canvas.md`，这是英文轻量平台项目画布。
- [x] 2.6 新增 `docs_bilingual/product_lifecycle/codex_platform_project_canvas.zh-CN.md`，这是中文轻量平台项目画布对照版。

## 3. 平台与消费文档

- [x] 3.1 更新 `docs_bilingual/product_lifecycle/codex_durable_team_platform_build_lifecycle.md`，这是英文平台建设 lifecycle；加入 value outcomes 和 AI-era role boundaries。
- [x] 3.2 更新 `docs_bilingual/product_lifecycle/codex_durable_team_platform_build_lifecycle.zh-CN.md`，这是中文平台建设 lifecycle 对照版；加入同样 boundaries。
- [x] 3.3 更新 `docs_bilingual/product_lifecycle/codex_project_consumption_lifecycle.md`，这是英文下游消费 lifecycle；加入 adoption canvas 和 value feedback。
- [x] 3.4 更新 `docs_bilingual/product_lifecycle/codex_project_consumption_lifecycle.zh-CN.md`，这是中文下游消费 lifecycle 对照版；加入同样 guidance。
- [x] 3.5 更新 `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.md`，这是英文白皮书；把平台描述为 AI 时代 value-delivery system。
- [x] 3.6 更新 `docs_bilingual/whitepapers/codex_cli_personal_production_durable_team_whitepaper.zh-CN.md`，这是中文白皮书对照版；加入同样 framing。
- [x] 3.7 更新 `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md`，这是英文长期 draft plan；加入 value increments、feedback points 和 rollback-boundary release-slice rules。
- [x] 3.8 更新 `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md`，这是中文长期 draft plan 对照版；加入同样 rules。

## 4. 验证

- [x] 4.1 运行 `openspec validate --all`，这是验证全部 specs 和 changes 的 OpenSpec validation command。
- [x] 4.2 运行 `python tools/run_openspec_guard.py --root . --tool codex --json`，这是仓库 OpenSpec guard command。
- [x] 4.3 运行 `python tools/check_name_clarity_rules.py --root . --json`，这是 docs 与 OpenSpec 文件的名称解释 checker。
- [x] 4.4 运行 `git diff --check`，这是补丁空白格式验证命令。
