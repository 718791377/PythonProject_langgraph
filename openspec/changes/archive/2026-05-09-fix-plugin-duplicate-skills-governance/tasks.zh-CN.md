# 任务：修复插件重复 Skills 治理

## 1. 工件

- [x] 1.1 创建 proposal、design、delta spec 和 tasks 工件。
- [x] 1.2 添加双语 companion 工件以满足仓库治理检查。

## 2. Checker 实现

- [x] 2.1 更新 `tools/check_codex_skills_governance.py`，使 plugin 同层重复 skill 名称成为 warning，而不是 blocking error。
- [x] 2.2 保留 user/repo 同层重复的 blocking error，除非 registry 声明例外。

## 3. 测试与验证

- [x] 3.1 增加 plugin 层重复 skill 名称的回归覆盖。
- [x] 3.2 运行聚焦 skills governance 测试。
- [x] 3.3 运行 OpenSpec validation、repository guard、local gate、local MR review 和 `git diff --check`。


