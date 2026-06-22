# Tasks：硬化 Skills2CLI Profile Routing 后续契约

## Stage A：冻结后续契约

- [x] 创建 routing hardening 的 OpenSpec follow-up change。
- [x] 添加 delta requirements，覆盖 orthogonal schema fields、task-module identity、positive scenario quality、显式 `full` eligibility、no-auto-apply behavior evidence、install artifact surface reporting，以及 recall/rerank fail-closed 契约。
- [x] 更新双语 implementation plan，补充四原则可追溯矩阵、Phase A acceptance matrix、Phase A/Phase B boundary、统一 safety contract 与 Phase B execution slices。
- [ ] 验证 Stage A plan-freeze package 并提交本地 feature branch。
- [ ] 将 Stage A plan-freeze package 集成本地 `main`，并清理 worktree/branch。

## Stage B：实施 runtime hardening

- [ ] 扩展 `profiles.json`，加入 orthogonal schema fields、显式 task-module identity fields、缺失的 positive examples、safety fields 与 `full` explicit-only eligibility metadata。
- [ ] 更新 `skills2cli_profile_registry_contract.py`，校验 positive scenario quality、orthogonal field mappings、`scene_description` compatibility、task-module identity、显式 `full` eligibility terms 与 install artifact surface paths。
- [ ] 更新 `skills2cli.py profile suggest`，分离 eligibility 与 ordering，要求 `full` 显式 eligibility，暴露 negative-example evidence，并输出 no-auto-apply behavior evidence。
- [ ] 更新 plugin-modules helper checks，使 `load_module` 保持 soft-load only，`set_plugin_profile` 拒绝 scenario/task-module hard-load targets。
- [ ] 扩展 `check_skills2cli_profile_routing.py`、`check_plugin_modules_skill.py`、focused tests 与 CI manifest coverage。
- [ ] 用 focused tests、代表性 suggestions、OpenSpec guard、local gate 与 local MR review 验证 Stage B。
- [ ] Stage B validation 后归档本 OpenSpec change，并将 runtime package 集成本地 `main`。
