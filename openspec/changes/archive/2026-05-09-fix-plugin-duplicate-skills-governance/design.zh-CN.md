## 设计

当前 checker 已经按 source layer 区分 skill inventory rows，并且已经输出通用的 plugin bundle warning。问题在同层重复检查循环：它把所有重复 `(layer, name)` 都当成错误，除非 registry 声明例外。这与 plugin 策略冲突，因为 plugin cache 由 vendor/bundle 管理，仓库变更不应直接编辑这些文件。

实现方式是在现有 registry-exception / error 逻辑之前加入 `layer == "plugin"` 分支：

1. 如果重复行来自 `plugin` 层，输出 warning，说明 plugin duplicate 在支持细粒度过滤前是 report-only。
2. 如果重复行来自 `repo` 或 `user`，保留现有行为：registry 例外进入 deferred cleanup，否则为阻塞错误。
3. 继续把 user/plugin 跨层重复作为 warning。

这样既保持 repository-owned 和 user-owned skill 冲突的严格性，又避免 plugin bundle 产物阻塞无关仓库发布。

## 安全性

- 本变更不修改 `C:\Users\lenovo\.codex\skills`、plugin cache 目录或 `C:\Users\lenovo\.codex\config.toml`。
- 本变更不会压制所有 skills governance 错误；只把 plugin 同层重复降级为 warning。
- 保留现有 “plugin skills are bundle-managed until filtering exists” warning。

## 验证

验证重点是策略分类，而不是修改真实插件：

- 增加单元测试：构造 fake plugin cache，其中有重复 `Chrome` skill，确认 checker 成功退出并报告 warning。
- 保留现有 repo 同层重复失败测试，确保仓库本地重复仍然阻塞。
- 发布前运行 OpenSpec validation、repository guard、local gate 和 local MR review。
