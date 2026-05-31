---
doc_id: langgraph_user_level_runtime_policy
lang: zh-CN
doc_class: governance
status: active
---

# LangGraph 用户级运行时策略

## 1. 目的

本文定义这条 Codex 编排主线的标准仓库规则：官方 `langgraph` 运行时应安装在哪里，repo-local LangGraph 兼容层源码应放在哪里，以及 LangGraph 安装应如何执行。

## 2. 分层边界

- 用户级共享运行时层可以被同一 machine / user / Codex home 下的多个 `PyCharm / Codex CLI` 项目复用。
- 官方 `langgraph` Python 包是上游依赖，不是仓库内实现。
- 可选的 `langgraph-cli[inmem]` 是用于本地 server 或 CLI 工作流的用户级工具依赖，不属于 repo-local 兼容层源码。
- 本仓库拥有 `tools/langgraph_durable_orchestrator/` 下的 repo-local 兼容层与编排源码。
- 本仓库也拥有 `.omx/state/langgraph/` 下的 repo-local durable runtime state。
- 如果后续在 `C:\Users\lenovo\.codex\python\...` 下生成了用户级 helper 副本，它也只是安装产物，不是源码权威面。
- 用户级共享 venv 与 helper 层不得承载或集中化任何单仓库的 canonical durable state。

## 3. 标准目录

除非后续治理变更显式替换，否则统一采用下面这套标准布局：

1. 用户级共享 LangGraph venv：
   `C:\Users\lenovo\.codex\venvs\langgraph-py312\`
2. 可选的用户级 helper 安装产物根目录：
   `C:\Users\lenovo\.codex\python\langgraph_durable_orchestrator\`
3. UTF-8-safe 的用户级官方 LangGraph CLI wrapper：
   `C:\Users\lenovo\.codex\bin\omx-langgraph-cli.ps1`
4. repo-local 兼容层与编排源码：
   `D:\PythonProject_langgraph\tools\langgraph_durable_orchestrator\`
5. repo-local LangGraph durable state：
   `D:\PythonProject_langgraph\.omx\state\langgraph\`

用户级共享 venv 服务于跨项目的 Codex 或 OMX LangGraph runtime 接入。repo-local 源码树服务于实现与测试。repo-local `.omx/state/langgraph/` 服务于每个仓库自己的持久化状态。

## 4. 标准安装命令

这台机器默认优先使用共享 Python 3.12 venv。如果需要 `langgraph-cli[inmem]` 来支持本地 server 工作流，则 Python 必须是 3.11 或更高版本。

创建共享 venv：

```powershell
py -3.12 -m venv C:\Users\lenovo\.codex\venvs\langgraph-py312
```

通过阿里源升级该 venv 里的 pip：

```powershell
C:\Users\lenovo\.codex\venvs\langgraph-py312\Scripts\python.exe -m pip --isolated install --upgrade pip --index-url https://mirrors.aliyun.com/pypi/simple/
```

安装或升级官方 LangGraph 包：

```powershell
C:\Users\lenovo\.codex\venvs\langgraph-py312\Scripts\python.exe -m pip --isolated install --upgrade --index-url https://mirrors.aliyun.com/pypi/simple/ langgraph
```

只有在确实需要本地 server 时才安装可选 CLI：

```powershell
C:\Users\lenovo\.codex\venvs\langgraph-py312\Scripts\python.exe -m pip --isolated install --upgrade --index-url https://mirrors.aliyun.com/pypi/simple/ "langgraph-cli[inmem]"
```

当官方 CLI 已安装，而 Windows 终端又不是原生 UTF-8 干净环境时，优先使用用户级 wrapper：

```powershell
omx-langgraph-cli.ps1 --help
omx-langgraph-cli.ps1 dev --help
```

## 5. Pip 镜像规则

- 一律使用 `python.exe -m pip`，不要直接用裸 `pip`。
- 阿里源一律通过每次命令显式传入 `--index-url https://mirrors.aliyun.com/pypi/simple/`。
- 不把持久化全局 `pip config` 修改当作默认仓库规则。
- 不对这个镜像使用 `--extra-index-url`。
- 除非确实存在证书校验问题且有临时例外记录，否则不要使用 `--trusted-host`。

## 6. 仓库硬规则

- 不要把官方 `langgraph` 包安装到本仓库目录中，作为主要共享 runtime 位置。
- 不要把全局 Python 的 site-packages 当成 LangGraph runtime 的长期稳定宿主。
- 不要把 repo-local `.omx/state/langgraph/` 状态迁移进用户级共享 venv 或其他共享运行时目录。
- 不要把用户级共享运行时误当成跨项目 durable-state 池。
- 不要把 `C:\Users\lenovo\.codex\python\` 下生成的 helper 副本当成源码真相。
- 不要在 `tools/langgraph_durable_orchestrator/` 中 vendor 或 fork 官方 LangGraph 包。
- 对外状态语言必须显式区分：`installed`、`enabled`、`selected`、`ready` 不是同一个状态。
- Durable capability readiness projection 必须发布 `readiness_fields = [installed, enabled, selected, ready]`，不得把这些字段折叠成一个 availability flag。
  - `installed` 表示该 lane 所需的 helper 或 runtime artifact 已存在。
  - `enabled` 表示用户级 capability switches 允许使用该 lane。
  - `selected` 表示用户级 backend selector 或 repo-local tracked state 指向该 lane。
  - `ready` 表示该 lane 满足 `installed && enabled && selected`；selected-but-not-installed 与 enabled-but-not-selected 都仍然不是 ready。
- `backend_default` 是用户级 selected backend 的兼容视图，`backend_ready` 只表示该 selected backend 的 readiness 结果。`backend_ready=true` 不表示当前任务已经运行或采用 durable workflow、tracked LangGraph thread 或 persistent team。
- 对于仍然默认非 UTF-8 控制台编码的 Windows 终端，不要直接依赖 `langgraph.exe --help` 或 `langgraph.exe dev --help`；应改用 `omx-langgraph-cli.ps1`。

## 7. 项目级例外规则

如果另一个 PyCharm 或 Codex CLI 项目的业务代码本身直接 `import langgraph`，那个项目仍然必须在自己的项目环境里声明和安装自己的依赖。用户级共享 venv 不能替代业务项目自己的依赖管理。

## 8. 启动提示

当任务涉及以下任一问题时，应优先阅读本文：

- LangGraph 应该装在哪里
- repo-local 兼容层源码应该放在哪里
- repo-local durable state 应该放在哪里
- 如何通过阿里源安装或升级 LangGraph
- 如何在 Windows 上使用 UTF-8-safe 的官方 LangGraph CLI wrapper
