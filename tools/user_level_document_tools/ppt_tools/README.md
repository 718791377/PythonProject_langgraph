# PPT Render Toolchain Helpers

Shared, local-only helpers for PowerPoint/PPTX authoring, PPTX-to-PDF/PNG render probes, and visual QA status evidence.

These helpers are reusable source files only. Consumer projects keep filled configs, source decks, output decks, renderer binaries, and evidence under their own ignored local paths. The shared repository owns only portable scripts, tests, and example configs.

## Files

- `ppt_render_toolchain_config.example.json` - example-only absolute-path config fields. Copy it to a local ignored config before use.
- `ppt_render_capability_probe.py` - emits JSON capability rows that distinguish `installed`, `enabled`, `selected`, and `ready`.
- `powerpoint_com_probe.ps1` - checks interactive PowerPoint COM creation, export, cleanup, and process-leak evidence.
- `ppt_render_probe.py` - renders a PPTX through `auto`, `powerpoint`, `soffice`, or `aspose` engines when locally configured.
- `write_visual_qa_status_marker.py` - classifies render evidence into `visual_qa:*` status markers.

## Local-only runtime rule

Do not edit system/user PATH. Configure renderer paths explicitly with a copied local config, CLI flags, or process-scoped environment for the single probe process. Third-party binaries and live evidence belong under ignored `.local/` folders, not tracked source.

If PowerPoint COM is blocked by a non-interactive desktop or an error such as `0x80070520`, use the configured `soffice` or `aspose` fallback evidence, or record `visual_qa:blocked` / `visual_qa:manual_required`; do not claim PowerPoint COM rendering passed until the COM probe succeeds.

## Typical probes

```powershell
python tools/user_level_document_tools/ppt_tools/ppt_render_capability_probe.py --config <local-config> --json
powershell -NoProfile -ExecutionPolicy Bypass -File tools/user_level_document_tools/ppt_tools/powerpoint_com_probe.ps1 -OutputDir <local-output>
python tools/user_level_document_tools/ppt_tools/ppt_render_probe.py --input <deck.pptx> --output-dir <local-output> --format pdf,png --engine auto --json
```
