# Plan: Enforce OpenCLI live-start receipt guard

- [x] 确认范围：只做 repo-local governance，不修改用户级 runtime。
- [x] 在代码变更前添加 Stage A plan-state commit。
- [x] 在 `tools/opencli_governance.py` 实现 install receipt validation。
- [x] 新增 `start` preflight 命令，要求 owner、install 与 port evidence。
- [x] 增加缺 install receipt、缺 owner evidence、证据齐全后仍 deferral 的单元测试。
- [x] 更新双语 implementation plan 状态与 checklist。
- [x] 添加 archived OpenSpec evidence 与 stable spec requirement。
- [x] 运行 targeted tests 与 repository validation。
- [x] local gate 和 local MR review 通过后合入本地 `main`。
