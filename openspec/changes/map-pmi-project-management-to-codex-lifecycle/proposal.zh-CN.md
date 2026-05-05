# 将 PMI 项目管理映射到 Codex 生命周期

## Why

仓库已经有产品与商业生命周期图，但仍需要一个项目管理叠加层，说明 PMI 参考资料如何进入 Codex 平台工作和下游项目工作。

本地 `PMP/` 目录是 PMI PDF 的私有参考目录。它可以用于生命周期映射，但不能成为被 Git 跟踪的仓库内容。仓库还需要清楚区分产品/商业文档和项目治理文档。

## What Changes

- 在 `docs_bilingual/product_lifecycle/` 下新增双语 PMI 项目管理参考映射。
- 更新 Codex durable-team 平台建设生命周期，说明 PMI 概念如何裁剪到 OpenSpec 和 GitLab-first delivery。
- 新增 OpenSpec 需求，要求把 PMI 当成治理叠加层，而不是替换产品/商业生命周期。
- 保持 `PMP/` 被忽略，避免本地参考 PDF 被提交。

## Non-Goals

- 不复制 PMI 书籍正文。
- 不实现 runtime behavior；这里指实际运行时行为。
- 不启动 `native_omx`；这是面向 worker-centric execution 的 durable backend lane。
- 不启动 `langgraph`；这是图式 checkpoint 和 approval-gate backend lane。
- 不写入 `.omx/state/`；这是仓库本地 durable state 目录。
- 不修改用户级 Codex 配置。
