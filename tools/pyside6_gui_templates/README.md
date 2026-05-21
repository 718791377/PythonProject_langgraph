# PySide6 GUI Templates

These templates are repository-local source assets for the cross-project PySide6 GUI capability. They are copied into a target project only by a preview-first helper or a human-reviewed implementation task.

Default safety contract:

- use the shared runtime at `D:\PythonProject_langgraph\.shared_runtimes\pyside6` by default;
- keep generated GUI source, runtime contracts, adapters, tests, and rollback notes project-local;
- use project-local override only when a project has a documented independent PySide6 version, packaging, or isolation requirement;
- do not install PySide6 globally;
- do not install PySide6 into a consumer project by default;
- do not launch a visible GUI unless the user requested interactive verification;
- keep GUI shell, business services, worker boundaries, diagnostics, and config/data paths separated;
- keep credentials, browser profiles, and user-private directories out of normal UI output and packaged artifacts.

Template placeholders:

- `{{package_name}}` - target Python package for the GUI, for example `my_project_gui`;
- `{{window_title}}` - deterministic window title;
- `{{project_name}}` - human-readable project name.

Recommended target layout:

```text
src/{{package_name}}/
  __init__.py
  app.py
  main_window.py
tools/gui/
  pyside6_runtime_contract.json
  run_gui.ps1
  check_pyside6_env.py
  adapters/
    README.md
tests/test_gui_import.py
packaging/pyside6_packaging_preflight.ps1
```

`requirements-gui.txt` remains available only as a project-local override template.
