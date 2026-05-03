# 1. 实施

- [x] 1.1 新增 `tools/check_openspec_code_archive_evidence.py` - 用于检查代码类 archive evidence 的可执行 checker。
- [x] 1.2 新增 `test/check_openspec_code_archive_evidence.test.py` - 回归测试，覆盖代码类 archive 无代码证据失败，以及 docs-only archive 通过。
- [x] 1.3 接入 `tools/run_openspec_guard.py` - 本地验证和 GitLab CI 使用的聚合 guard 入口。
- [x] 1.4 更新 `test/run_openspec_guard_json.test.py` - 聚合 JSON contract 的测试，覆盖新增 guard step。
- [x] 1.5 更新 `tools/safety_rule_script_backing_registry.json` - 为脚本化 enforcement 增加 safety registry entry。
- [x] 1.6 更新 OpenSpec workflow governance docs - 让提示词提醒和脚本控制成对存在。
- [x] 1.7 允许已存在的 `x_code_evidence_paths` 声明 - 用于 implementation 已经落在 `main` 后的 archive-only closeout。
- [x] 1.8 新增 archive-only 分支回归测试 - 验证已存在的声明式证据可以通过，缺失的声明式证据会失败。

## 2. 验证

- [x] 2.1 运行 checker unit tests。
- [x] 2.2 运行 `openspec validate --all`、`python tools/run_openspec_guard.py --root . --json`、implementation-plan checker、name-clarity checker 和 `git diff --check`。

## 3. 发布

- [x] 3.1 按 GitLab-first workflow 发布：推送分支、创建 MR、等待 pipeline 通过、合并到 GitLab `main`，再把同一个 GitLab `main` 同步到 GitHub。
