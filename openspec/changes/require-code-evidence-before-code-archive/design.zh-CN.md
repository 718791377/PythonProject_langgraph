﻿# 设计

这个 guard 故意采用 diff-based 方式。它不替代 `openspec archive`；它是在 archive change 周围增加仓库 CI gate。

检测规则：

- 当前分支或工作区 diff 中，凡是新增或重命名到 `openspec/changes/archive/YYYY-MM-DD-<change>/` 下面的路径，都视为 newly archived change。
- 如果 `.openspec.yaml` 声明 `x_change_class: code`、`runtime`、`mixed`、`tooling` 或 `ci`，则显式属于代码类 change。
- 如果没有显式 metadata，checker 会根据 archive artifacts 中是否提到 runtime、scripts、helpers、tests、checkers、guards、CI 或 code behavior 来推断是否为代码类。
- docs-only change 可以声明 `x_change_class: docs`、`spec`、`governance`、`memory`、`research`、`plan` 或 `status`。

证据规则：

- Code evidence 指 `docs_bilingual/` 和 `openspec/` 之外发生变更的 source、executable script、test file、executable check、Git hook 或 CI file。
- 代码类 archive 可以在 `.openspec.yaml` 声明 `x_code_evidence_paths`；如果声明了，至少一个列出的 path 必须在同一分支变更。
- 聚合 guard 会在 worktree cleanliness enforcement 之前运行该 checker，这样它可以检查本地 dirty archive work 和 MR branch diff。

这样既保留官方 OpenSpec CLI 语义，又增加仓库自己的安全门禁。
