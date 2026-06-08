# 变更：英文启动摘要哨兵来源 ASCII-only

## Why

英文启动摘要当前直接包含非 ASCII 可见上下文保留 canary 标记。这些字节在 UTF-8 文件中有效，但英文/ASCII 取向的传输、launcher payload、终端渲染路径或 replay context 可能通过旧代码页解码并显示为 mojibake。中文启动摘要可以继续作为字面标记来源，英文摘要则用 ASCII Unicode 码点描述同一标记。

## What Changes

- 将 `docs_bilingual/project_startup_summary.md` 改为 ASCII-only，用码点描述替代字面标记文本。
- 保留 `docs_bilingual/project_startup_summary.zh-CN.md` 作为包含字面可见标记文本的启动摘要文件。
- 更新 canary placement 与 startup-mojibake 检查器，使该存储拆分可执行约束。
- 更新测试和稳定规格，记录 English-ASCII / Chinese-literal 边界。

## Impact

- 不改变用户可见的规范 canary 语义。
- 不授权远端发布。
- 回滚方式是 revert 单一本地 feature commit，并重新运行同一组 checker/test 命令。
