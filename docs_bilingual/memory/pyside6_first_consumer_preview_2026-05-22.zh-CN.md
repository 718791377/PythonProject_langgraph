# PySide6 首个消费项目 shared preview 证据（2026-05-22）

## 结论

- 首个消费项目选择：`D:\PythonProject_OpenClaw`。
- 选择理由：当前仓库治理文档将 `D:\PythonProject_OpenClaw` 明确为共享用户级运行时和策略的消费项目之一；本次只运行 preview，不修改消费项目。
- 根目录证据：`.git, README.md`。
- helper 状态：`ok=true`，`mode=preview`，`runtime_mode=shared`。
- 共享 runtime：`D:\PythonProject_langgraph\.shared_runtimes\pyside6`。
- 共享 runtime Python：`D:\PythonProject_langgraph\.shared_runtimes\pyside6\.venv\Scripts\python.exe`。
- 共享 runtime 状态：`import_only_verified`。
- 阻塞项：0 个。
- 警告项：1 个；当前只有 `dependency_style_unknown`，在 shared runtime preview 中不是阻塞项，但 project-local override 仍需要受支持依赖面。
- 可见 GUI：未启动；preview 输出也说明 preview 不创建文件、不安装包、不启动可见 GUI。
- 消费项目变更：未写入；`git -C D:\PythonProject_OpenClaw status --short --branch` 仅显示既有分支 ahead 状态，无脏文件。

## 执行命令

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot D:\PythonProject_OpenClaw -Mode preview -RuntimeMode shared -RuntimeRoot D:\PythonProject_langgraph\.shared_runtimes\pyside6 -DependencyStyle auto -CreateTemplate -RunSmokeTest -Json
```

## 关键 JSON 字段

| 字段 | 值 |
| --- | --- |
| `project_root` | `D:\PythonProject_OpenClaw` |
| `project_root_evidence` | `.git, README.md` |
| `runtime_mode` | `shared` |
| `shared_runtime_root` | `D:\PythonProject_langgraph\.shared_runtimes\pyside6` |
| `shared_runtime_python` | `D:\PythonProject_langgraph\.shared_runtimes\pyside6\.venv\Scripts\python.exe` |
| `shared_runtime_status` | `import_only_verified` |
| `package_manager` | `unknown` |
| `dependency_style` | `unknown` |
| `package_name` | `pythonproject_openclaw_gui` |
| `run_smoke_test` | `True` |
| `smoke_test.status` | `not_requested` |

## 计划写入范围（preview-only）

本次 preview 只列出计划写入，不执行 apply。计划写入路径如下：

| 路径 | 计划动作 | 用途 |
| --- | --- | --- |
| `tools/gui/pyside6_runtime_contract.json` | `create_if_missing` | Create a shared PySide6 runtime contract. |
| `src/pythonproject_openclaw_gui/__init__.py` | `create_if_missing` | Create a minimal PySide6 GUI template file. |
| `src/pythonproject_openclaw_gui/app.py` | `create_if_missing` | Create a minimal PySide6 GUI template file. |
| `src/pythonproject_openclaw_gui/main_window.py` | `create_if_missing` | Create a minimal PySide6 GUI template file. |
| `tools/gui/check_pyside6_env.py` | `create_if_missing` | Create a shared-runtime PySide6 environment checker. |
| `tools/gui/run_gui.ps1` | `create_if_missing` | Create a visible-GUI launcher that uses the shared runtime Python. |
| `tools/gui/adapters/README.md` | `create_if_missing` | Create a GUI adapter boundary placeholder. |
| `tests/test_gui_import.py` | `create_if_missing` | Create an import-only GUI smoke test. |

## 计划命令

| 命令 | 执行阶段 | 用途 |
| --- | --- | --- |
| `Review preview JSON and create a feature branch or rollback commit before apply.` | `manual_review` | Preserve a rollback boundary before project-local GUI writes. |
| `tools/pyside6_gui_helpers/ensure-shared-pyside6-runtime.ps1 -Mode verify -RuntimeRoot "D:\PythonProject_langgraph\.shared_runtimes\pyside6" -Json` | `preflight_or_after_apply` | Verify shared runtime import-only status without launching a visible GUI window. |
| `"D:\PythonProject_langgraph\.shared_runtimes\pyside6\.venv\Scripts\python.exe" tools/gui/check_pyside6_env.py --project-root . --json` | `planned_import_only_no_visible_gui` | Verify import-only behavior without launching a visible GUI window. |

## 阻塞项与警告

### 阻塞项

- 无。

### 警告

- `dependency_style_unknown: shared runtime mode can still create GUI files, but project-local override needs a supported dependency surface.` - 本次 preview 的非阻塞提醒。

## 下一步

- 在用户明确继续消费项目写入时，进入 `D:\PythonProject_OpenClaw` 的独立 feature worktree，先建立该消费项目自己的 rollback 边界。
- 运行 shared 模式 `apply`，生成 GUI shell、runtime contract、run helper、adapter、import smoke test 与 rollback note。
- 使用共享 runtime 运行 import-only smoke test；仍不启动可见 GUI，除非用户明确要求交互式验证。
