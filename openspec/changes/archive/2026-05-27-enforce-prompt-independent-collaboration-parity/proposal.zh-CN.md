# 提案：强制提示词无关的协同路由等价性

## 为什么

自动编排方案现在需要可执行证据来证明：等价任务不应因为提示词是否重复写了“使用 experts / durable_team / persistent team”等协同短语而得到不同路由。durable / persistent team 声明也需要统一的 checker-backed evidenceguard，避免把 readiness、陈旧 LangGraph state、skill 调用、timeout 或空 `.omx` 目录误报为运行完成证据。

## 做什么

- 新增 checker，覆盖提示词无关协同等价、冷启动读取顺序证据、durable / persistent evidenceguard 记录、expert 生命周期审计事件，以及 LangGraph state release。
- 新增文档更新与多切片路由等价 fixture pairs，并补充显式 `omx` 与 LangGraph 阈值场景。
- 将 checker 接入 OpenSpec guard、CI manifest、安全规则注册表、治理文档、实施方案、`AGENTS.md` 与稳定 OpenSpec spec。

## 影响

这是本地仓库 enforcement 变更。它不会启动 durable team，不会宣称 native expert 已执行，也不会发布到远端。
