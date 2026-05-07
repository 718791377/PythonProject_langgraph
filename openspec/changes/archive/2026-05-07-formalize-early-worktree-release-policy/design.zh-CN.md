# 设计

## 决策

将策略拆分为两个生命周期对象：

1. Feature worktree：临时执行面。只要本地验证已经通过，并且所有需要保留的文件已经提交、转移、摘要记录或明确丢弃，就可以删除。
2. Feature branch：发布载体。它必须保留到 GitLab MR 已合并、本地 `main` 已快进到 GitLab main commit，并且 GitHub `main` 已同步到同一 commit。

## Checker 行为

`tools/check_worktree_session_hygiene.py` 保持只读。它在 JSON 输出中报告 `worktree_release_candidates` 数组。每条记录区分：

- `worktree_release_ready`：worktree 位于非 main 分支，并且没有已跟踪、未跟踪或本地专用脏文件。
- `branch_cleanup_ready`：分支已经合入本地 `main`，本地 `main` 匹配 `gitlab/main`，并且 `github/main` 匹配本地 `main`。

checker 不删除 worktree 或 branch。它只为冷启动会话提供有脚本背书的状态面。

## 文件分类规则

策略继续把文件分类决策放在自动删除之外。释放 worktree 前，操作者必须先分类已跟踪文件、未跟踪文件、本地证据、缓存、OCR 输出、私有文件、版权文件和大文件。

## 非目标

- 不自动删除 worktree。
- 不自动删除本地或远端 branch。
- 不把私有、版权、缓存、OCR 或大体积证据 payload 作为源码事实提交。