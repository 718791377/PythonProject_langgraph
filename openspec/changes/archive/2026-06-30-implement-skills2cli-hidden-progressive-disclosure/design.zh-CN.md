# Design：Skills2CLI 隐藏库渐进披露

## Overview

runtime 在现有 visible-skill index 旁边增加一个只读 hidden-skill 层。Hidden records 从 `CODEX_HOME/state/skills2cli/visibility-disabled/**/SKILL.md` 发现。它们使用稳定的脱敏 ID 标识，并且可以逐个搜索或加载。

## Key decisions

- Hidden soft-load 是只读操作。它从不移动目录，也不修改 `config.toml`。
- `hidden load` 是唯一返回完整 skill body 的 hidden 命令，并记录紧凑 usage event。
- 可见性 promote/demote 由证据驱动，但不是后台驱动；必须由 human/operator 命令调用 `apply-recommendations`。
- Apply 仅限 standalone user skills，一天最多一次，每次最多三个移动，并写 rollback receipts。
- 当前可见 skills 继续使用现有索引逻辑；hidden progressive disclosure 增加单独的 visibility-state 标签，而不改变现有 `index/search` 语义。

## Data flow

1. `hidden index/search/suggest` 从现有 index 构建 visible records，并从 `visibility-disabled` 构建 hidden records。
2. Alias expansion 为 `grill-me`、`stop-slop`、`deslop`、`anti-slop` 增加确定性 candidate boosts。
3. `hidden show` 返回一个 record 的紧凑元数据。
4. `hidden load` 读取一个选定的 `SKILL.md`，返回 body 或 chunk，并追加一条 JSONL usage event。
5. `visibility recommend` 读取 usage events 和当前 visible standalone user skills，返回 promote/demote/keep-soft-load buckets。
6. `visibility apply-recommendations` 读取既有 recommendation receipt，检查 daily apply guard，写 rollback receipt，并最多移动三个目录。

## Safety

所有命令必须报告 non-mutation flags。Apply commands 只有在 `--apply` 和 `--operator-confirmation` 同时存在时，才可以移动 standalone user skill directories。Plugin cache、repo skills、system skills 与 `config.toml` 永远不是 mutation targets。
