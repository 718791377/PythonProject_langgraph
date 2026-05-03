# 为什么

代码类 OpenSpec change 不允许被当成纯文档 closeout 直接归档。MR6 readiness review 暴露了一个流程缺口：即使后续读者把某个队列项理解为代码或 runtime 工作，change 仍可能只带 OpenSpec 和文档改动就被归档。

## 改什么

- 新增 `tools/check_openspec_code_archive_evidence.py` - 仓库 checker；它检查当前 git diff 中新归档的 OpenSpec change 是否具备代码证据。
- 允许 `x_code_evidence_paths` - 显式 archive metadata；当 closeout 发生在单独 archive-only MR 中时，它可以指向已经落在 `main` 的 source、executable check、CI 或 test evidence。
- 接入 `tools/run_openspec_guard.py` - 本地和 GitLab CI 使用的聚合 OpenSpec guard。
- 新增 `test/check_openspec_code_archive_evidence.test.py` - 回归测试；验证代码类 archive 没有 source/test evidence 会失败，docs-only archive 可以通过。
- 更新 OpenSpec workflow policy 和 safety-rule registry，让规则由脚本控制执行，而不是只靠提示词提醒。

## 非目标

- 不回写已经合并的 MR6 archive 历史。
- 不修改 `.omx/state/` - 这是 repo-local durable runtime state，不是 policy source。
- 不修改 `C:\Users\lenovo\.codex\config.toml` - 这是用户级 Codex config，不属于本仓库 change。
- 不修改 MCP Router 设置。
