# 设计

## 放置位置

恢复的章节放在 `3.3 恢复的十层框架落地映射`，即非目标之后、三条 lane 具体职责之前。这样冷启动读者会先看到白皮书模型，再阅读 `subagent`、`native_omx` 和 `langgraph` 的 lane 职责。

## 边界

该章节只负责解释目标架构与 release 切分，不把 draft 方案推进为已实施状态，也不激活任何 durable backend。
