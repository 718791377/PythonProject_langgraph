---
doc_id: project_moe_sessions_tab_design_fallback_reason
lang: en
status: active
doc_class: design_evidence
created_at: 2026-06-09
---

# Project MOE Sessions Tab Design Fallback Reason

Pencil was preferred for this design-aid slice, but the live Pencil MCP connection failed with `transport not connected to app: trae_cn` during `get_editor_state(include_schema=true)`. Local checks also found that `@pencil.dev/cli` was available from npm metadata but not installed globally, and the `htmltool2` npm package name was not available from the registry during the earlier tool check.

Therefore this slice uses `sessions_tab_layout.html` as the design-aid fallback artifact. It is only a layout confirmation aid and is not a Project MOE GUI runtime dependency. The runtime remains PySide6/QFluentWidgets.
