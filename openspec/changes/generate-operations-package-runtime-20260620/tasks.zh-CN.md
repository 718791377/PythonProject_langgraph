# 任务：生成运营包 Runtime

## Stage A：冻结方案

- [x] 创建运营包生成 OpenSpec 变更 artifacts。
- [x] 在 `docs_bilingual/implementation_plans/` 下创建双语实施方案。
- [x] 在 `docs_bilingual/docs_registry.yaml` 中登记 Stage A 实施方案。
- [x] 验证、提交并把 Stage A 方案冻结包合入本地 `main`。

## Stage B：实现 live runtime 与生成运营包

- [ ] 创建 `tools/generate_operations_package.py`，实现确定性双语文档生成。
- [ ] 创建 `tools/check_operations_package_docs.py`，校验运营包、裁剪、I/T/O 与 registry。
- [ ] 生成 Codex 持久化团队运营包文档配对。
- [ ] 生成一人公司运营包文档配对。
- [ ] 在仓库索引中登记生成文档配对以及新 checker/test。
- [ ] 添加 `test/operations_package_docs.test.py` 并登记到 `tools/ci/ci_test_manifest.json`。
- [ ] 验证 focused tests、OpenSpec、本地 gate、本地 MR review 和本地 main 集成。
- [ ] 仅在 Stage B runtime 行为完成验证并本地集成后归档 OpenSpec 变更。
