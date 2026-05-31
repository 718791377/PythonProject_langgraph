## 1. Checker 与回归覆盖

- [x] 1.1 新增 launcher payload context-boundary checker，用于验证文件化 model-instructions 传输。
- [x] 1.2 将 checker 注册到聚合 OpenSpec guard 和安全规则登记表。
- [x] 1.3 增加当前通过场景和失败场景的回归覆盖。

## 2. Spec 生命周期

- [x] 2.1 为 startup-binding launcher payload transport 增加 OpenSpec delta。
- [x] 2.2 校验 active OpenSpec change。
- [x] 2.3 在同一个本地包内将 change 归档进稳定 startup-binding spec。

## 3. 验证与集成

- [x] 3.1 运行聚焦编译、checker 和测试命令。
- [x] 3.2 运行仓库 precommit、OpenSpec guard 和 local gate 验证。
- [ ] 3.3 提交、运行 local MR review、合入本地 `main`，并在远程发布前停止。
