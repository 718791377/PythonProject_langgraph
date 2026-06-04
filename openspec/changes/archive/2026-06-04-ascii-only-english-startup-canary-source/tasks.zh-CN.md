# Tasks

## 1. Documentation and spec

- [x] 1.1 将英文启动摘要改为 ASCII-only，同时通过码点描述同一标记值。
- [x] 1.2 保留中文启动摘要作为字面可见标记来源。
- [x] 1.3 更新稳定 canary surface spec，记录 English-ASCII / Chinese-literal 存储边界。

## 2. Checker and test implementation

- [x] 2.1 更新 canary placement checker 的路径规则，覆盖英文 ASCII-only 与中文字面标记。
- [x] 2.2 更新 startup mojibake checker 测试/fixture，覆盖拆分来源规则。
- [x] 2.3 增加英文摘要包含非 ASCII 或字面标记文本时失败的回归覆盖。

## 3. Verification and integration

- [x] 3.1 运行目标 canary/startup-mojibake 测试与 checker 命令。
- [x] 3.2 运行 OpenSpec validation，并准备 archive 包以进入最终 guard、precommit、local gate 和 local MR review 序列。
- [x] 3.3 准备 feature branch，以便提交、合入本地 `main`、清理已集成 worktree，并停在远程发布门前。
