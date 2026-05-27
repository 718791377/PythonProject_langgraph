## 1. 治理更新
- [x] 1.1 更新 Comet/OpenSpec/Superpowers 策略，加入 docs_bilingual-first 的 `/plan` 后本地治理包规则。
- [x] 1.2 更新 OpenSpec 使用约定和 OPSX 治理，加入派生更新 OpenSpec/docs 的规则。
- [x] 1.3 更新 worktree 隔离治理，加入完整本地流程与中文提交要求。

## 2. 脚本控制
- [x] 2.1 新增前向 Markdown 双语成对 checker。
- [x] 2.2 新增中文提交主题 checker 与 commit-msg hook。
- [x] 2.3 扩展 implementation-plan 规则，检查 active Comet implementation references。
- [x] 2.4 将新检查注册到 aggregate guard、local MR review、safety registry 和 CI manifest。
- [x] 2.5 新增明确的 `/plan` 后与完整本地流程脚本/checker。

## 3. 验证
- [x] 3.1 为新增和扩展检查增加单元测试。
- [x] 3.2 运行 targeted tests 和仓库 gate。
- [x] 3.3 本地 main 合入后停在远端发布门。
