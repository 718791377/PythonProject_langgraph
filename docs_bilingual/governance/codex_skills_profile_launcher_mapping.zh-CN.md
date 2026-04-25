---
doc_id: codex_skills_profile_launcher_mapping
lang: zh-CN
doc_class: governance
status: active
translation_of: docs_bilingual/governance/codex_skills_profile_launcher_mapping.md
---

# Codex Skills Profile Launcher 映射

## 1. 目的

本文定义 Codex skills profile 到未来 launcher 入口的仓库治理映射。

该映射是声明式元数据。本变更不安装 launcher alias，不编辑用户级 wrapper，不编辑用户级 `config.toml`，不禁用插件，也不修改 skills。

## 2. 权威边界

权威来源如下：

- profile 定义：`docs_bilingual/governance/codex_skills_profiles.registry.yaml`
- launcher payload 安全规则：`docs_bilingual/governance/user_level_launcher_payload_policy.md`
- 发布流程：本仓库 GitLab-first 流程

用户级已安装 wrapper 是部署产物，不由本文直接修改。

## 3. 当前状态

稳定命令仍然是 `codex-ohmy`。

以下 profile 专用 alias 是未来可选名称，不是本次变更安装的命令：

- `codex-ohmy-core` - 未来可选的低负载默认 launcher alias。
- `codex-ohmy-browser` - 未来可选的浏览器自动化 launcher alias。
- `codex-ohmy-web` - 未来可选的 Web 与部署 launcher alias。
- `codex-ohmy-github` - 未来可选的 GitHub 工作流 launcher alias。
- `codex-ohmy-full` - 未来可选的临时排障 launcher alias。

后续 launcher 工作可以实现物理 alias、`--profile` 参数，或两者都实现。在那之前，registry 中的映射只作为 policy metadata 和验证输入。

## 4. Profile 映射

| Profile | 未来 alias | 用途 | 插件规则 |
| --- | --- | --- | --- |
| `core` | `codex-ohmy-core` | 非 Web 工作的低负载默认 profile。 | 不要求 Vercel 或广泛插件发现。 |
| `browser` | `codex-ohmy-browser` | 浏览器自动化和视觉验证。 | 在细粒度过滤存在前保留 Vercel 浏览器能力。 |
| `web` | `codex-ohmy-web` | Web、前端、Vercel、Next.js 和部署工作。 | 在细粒度过滤存在前保留 Vercel bundle 行为。 |
| `github` | `codex-ohmy-github` | GitHub issue 和 PR 工作活跃时使用。 | 只在 GitHub 工作流活跃时启用 GitHub 工作流能力。 |
| `full` | `codex-ohmy-full` | 临时排障和广泛发现。 | 不能作为长期默认值。 |

## 5. 安全规则

- 不要在 repository MR 中修改 `C:\Users\lenovo\.codex\config.toml`。
- 不要把本映射变更当成用户级 wrapper 安装变更。
- 不要为了降低上下文压力而禁用 Vercel 插件。
- 不要编辑 plugin cache 文件。
- 不要删除或重写用户级 skills。
- 需要 browser profile 的项目必须保留浏览器自动化和视觉验证能力。
- 需要 web profile 的项目必须保留 Vercel、Next.js、前端和部署能力。

## 6. 验证

运行：

```powershell
python tools/check_codex_skills_profile_launcher_mapping.py --root . --json
```

检查器验证：

- 每个必需 profile 都有 launcher mapping；
- 每个被映射的 profile 都存在于 profiles registry；
- alias 被标记为 future optional 或 temporary；
- `core` 是低负载默认 profile；
- `full` 是临时 profile，且不是默认值；
- browser 和 web 映射保留 Vercel / plugin 能力；
- config 和 wrapper mutation 被禁止。

## 7. 未来实现规则

后续真正实现 launcher 的变更必须先创建独立 OpenSpec change。

该后续变更需要决定使用：

- 物理 alias；
- `--profile` 参数；
- alias 和参数都支持。

它还必须遵守 launcher payload policy：大型启动指令必须通过文件引用传递，不能以内联长命令行参数传递。
