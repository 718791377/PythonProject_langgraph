# 任务

## 1. 治理表述

- [x] 1.1 更新 `AGENTS.md`，加入发布前归档的单 MR 默认规则。
- [x] 1.2 更新 `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md`。
- [x] 1.3 更新 `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md`。
- [x] 1.4 更新 `docs_bilingual/governance/openspec_opsx_project_usage_policy.md`。
- [x] 1.5 更新 `docs_bilingual/governance/openspec_opsx_project_usage_policy.zh-CN.md`。

## 2. OpenSpec 需求

- [x] 2.1 增加 single-MR archive package（单 MR 归档发布包）默认规则的 delta spec。
- [x] 2.2 记录 two-MR exceptions（双 MR 例外）和 archive follow-up（归档跟进）预期。
- [x] 2.3 保持 change class 为 documentation/governance 范围，使 archive evidence checks 不要求新增代码证据。

## 3. 验证

- [x] 3.1 运行 `openspec validate prefer-archive-before-publication-mr`。
- [x] 3.2 运行 `openspec validate --all`。
- [x] 3.3 运行 `python .\tools\run_openspec_guard.py --root . --tool codex --json`。
- [x] 3.4 运行 `git diff --check`。
- [x] 3.5 如果本地验证通过且该 change 仍属于小型变更，就在同一分支内归档该 change 并再次验证。
