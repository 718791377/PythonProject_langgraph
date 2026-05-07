# Tasks

## 1. 策略措辞

- [x] 1.1 更新 `AGENTS.md`，改用主 main 工作区新鲜度表述。
- [x] 1.2 更新 `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md` 的英文规则。
- [x] 1.3 更新 `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md` 的中文规则。
- [x] 1.4 ?? `design.md`????????? checker ???

## 2. 脚本控制

- [x] 2.1 更新 `tools/check_worktree_session_hygiene.py`，让本地 `main` 落后于 `gitlab/main` 成为错误。
- [x] 2.2 本地 `main` 领先于 `gitlab/main` 时按“不落后”处理，同时提醒操作者不要把主目录 `main` 当成功能工作区。
- [x] 2.3 增加落后和领先两种场景的单元测试。

## 3. 验证

- [x] 3.1 运行 `python test/check_worktree_session_hygiene.test.py`。
- [x] 3.2 运行 `openspec validate clarify-primary-main-not-behind-rule`。
- [x] 3.3 运行 `openspec validate --all`。
- [x] 3.4 运行 `python .\tools\run_openspec_guard.py --root . --tool codex --json`。
- [x] 3.5 运行 `git diff --check`。
