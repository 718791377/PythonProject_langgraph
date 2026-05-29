# 设计：Project MOE Readiness 输出契约

## 决策

将 `warnings`、`checked_files` 和 `redacted_paths` 作为增量顶层 readiness 字段暴露。保留既有嵌套 readiness 细节，供操作者诊断使用。

## 安全

这些字段来自已经读取的元数据和目标相对路径候选项。它们不读取 private prompt 正文，也不写目标项目。

## 验证

本地集成前使用 Project MOE toolchain 回归测试和 OpenSpec validation。
