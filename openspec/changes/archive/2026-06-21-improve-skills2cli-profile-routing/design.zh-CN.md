# 设计：场景化 Skills2CLI Profile 路由

## 当前状态

`profiles.json` 定义八个 top-level modules，并把每个 module 直接映射到 plugin bundles 与 skill-doc hints。这个形状适合 profile apply preview，但无法表达一个 profile 为什么应该或不应该匹配某个用户任务。

## 目标状态

registry 变成分层路由来源：

1. top-level profile：稳定兼容 ID 与 broad scenario；
2. scenario profile：recommendation entry，解析到 canonical `target_profile`；
3. task module：profile 下的聚焦能力块；
4. hint layer：plugin family 与 `SKILL.md` references。

Profile ID 保持稳定。新增字段采用 additive 方式，使现有脚本可以继续工作，新脚本则消费更丰富的 metadata。

## 路由模型

`skills2cli.py profile suggest` 根据 `route_when` 与 task-module examples 给用户文本评分，对 `negative_examples` 做排除或惩罚，把 audit evidence 作为 advisory boost，并在 query 没有明确要求 broad troubleshooting 时惩罚 `full`。

## 安全模型

所有 routing output 都只是 advisory。`load_module.ps1` 可以 soft-load top-level 或 nested modules。`set_plugin_profile.ps1` 只 preview/apply top-level profiles，并对 nested task modules fail closed。

## 兼容性

现有调用如 `load_module.ps1 core-dev -Json` 和 `set_plugin_profile.ps1 core-dev -Json` 必须继续工作。新增调用如 `load_module.ps1 web-saas.mobile-app -Json` 可返回 task-module 结果。对 `set_plugin_profile.ps1` 的 nested 调用必须 fail closed，并给出清晰解释。

## 兼容性细化

Scenario profiles 只是 recommendation entries。它们解析到 canonical `target_profile` IDs 和 task modules，不替代现有 `modules`，也不是合法 hard-load targets。
