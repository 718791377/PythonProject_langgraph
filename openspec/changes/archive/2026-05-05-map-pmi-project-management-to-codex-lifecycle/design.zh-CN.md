# Design

## Placement

新增 `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.md` 文件作为 PMI 映射的 ASCII 主参考。匹配的 `docs_bilingual/product_lifecycle/pmi_project_management_reference_map.zh-CN.md` 文件作为 UTF-8 中文对照版。

平台建设生命周期双语文件新增一个简短 PMI 裁剪叠加层小节。该小节指向专门的 PMI 映射文件，而不是重复完整映射。

## Reference Boundary

本地 `PMP/` 目录只作为参考，并继续被 Git 忽略。仓库可以总结 PMI 概念如何映射到本项目，但不得复制 PMI 书籍正文，也不得跟踪本地 PDF 文件。

## Mapping Model

映射分成三层：

1. PMBOK 价值与原则指导映射到 value delivery、tailoring、governance、success criteria 和 quality gates。
2. Process Groups 指导映射到 OpenSpec 和 GitLab-first delivery gates：initiating、planning、executing、monitoring and controlling、closing。
3. Agile 指导映射到探索型工作、MVP slices、短反馈循环和 hybrid delivery decisions。

## Downstream Boundary

平台仓库可以定义共享项目管理 templates 和 governance checks。下游项目在需要时拥有自己的 project charter、risk register、issue log、release plan、rollback plan 和 lessons learned。

## Validation

验证使用 OpenSpec 和仓库文档 checker。不启动 runtime services。
