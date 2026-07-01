# 设计：PPT 可视化修改意见工具

## 架构

该工具是本地 sidecar，不是 PPT 编辑器。它消费现有渲染 helper 生成的 slide PNG，并创建可携带审阅包。后端保持 stdlib-only，可在消费者项目中无需安装 Web framework 运行。

## 数据流

1. 现有 PPT 渲染 helper 在消费者拥有的输出目录中生成 slide PNG。
2. `ppt_review_tool.py` 将 PNG 复制到审阅 session 目录并记录源文件 provenance。
3. 原始评论被规范化为包含 `slide`、`roi`、`severity`、`category`、`comment`、`suggested_fix` 和 `status` 的 schema。
4. 工具写出 JSON 证据和离线 HTML 报告。静态 viewer assets 支持人工浏览器标注流程。

## 边界

源 PPTX 只是只读元数据输入。生成的审阅 session 属于被忽略的项目输出路径。工具不启动 HTTP server、不修改 PATH、不下载依赖，也不访问外部服务。
