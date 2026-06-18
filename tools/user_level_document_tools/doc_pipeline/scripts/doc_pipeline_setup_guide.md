# Document Pipeline Setup Guide

This guide supports the local Word COM + Acrobat Pro + Poppler pipeline and the optional visual rendering QA backends.

## 1. Current expected tool roles

- Microsoft Word COM: DOCX open check and Word-layout PDF export.
- Adobe Acrobat Pro: PDF to DOCX export and scanned-PDF OCR.
- Poppler: `pdfinfo`, `pdffonts`, `pdftoppm`, and `pdftocairo` for PDF inspection and rendering.
- Python: helper scripts and the project virtual environment.
- Python `pdf2image`: optional visual rendering QA wrapper backed by Poppler; it is not a Poppler replacement on Windows.
- Python Pillow: optional contact-sheet image generation.
- LibreOffice / `soffice`: optional DOCX-to-PDF fallback for visual QA evidence, not the final Word-layout quality baseline.

## 2. Configure local runtime paths

Recommended local config path:

```text
$(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')
```

Create it by copying:

```text
$(Join-Path (Get-Location) 'config\doc_pipeline')\doc_pipeline_config.example.json
```

Fill the runtime config with consumer-owned paths only. Keep tracked example files generic and do not commit binary payloads, installers, generated render images, or machine-specific absolute paths.

Useful fields:

```json
{
  "poppler_bin_dir": "<consumer-project>/.local/user_level_document_tools/<poppler>/Library/bin",
  "python_exe": "<consumer-project>/.venv/Scripts/python.exe",
  "soffice_exe": "",
  "visual_qa_output_root": "<consumer-project>/.local/user_level_document_tools/visual_render_qa",
  "visual_qa_default_backends": ["pdftoppm", "pdf2image", "soffice"],
  "visual_qa_require_backends": []
}
```

You can also pass `-PopplerBinDir`, `-PythonExe`, `-SofficeExe`, or `-VisualQaOutputRoot` directly to scripts.

If Poppler is configured but rendering still fails, run the focused access test:

```powershell
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\test_poppler_access.ps1 `
  -ConfigPath $(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')
```

If this reports access-denied for a package path, retry from a normal interactive desktop PowerShell or CMD session. If it is still inaccessible, reinstall or copy Poppler to an accessible ignored local tools directory, then rerun `configure_doc_pipeline.ps1 -PopplerBinDir <path> -Force`.

## 3. Configure Python packages

`pdf2image` and Pillow should be installed into the consumer project's intended Python environment, normally `.venv`.

```powershell
$(Join-Path (Get-Location) '.venv')\Scripts\python.exe -m pip install pdf2image Pillow
```

Do not install packages into system Python from an automated model step unless the user approves it.

## 4. Word COM interactive-session note

Word COM can fail from constrained or non-interactive hosts with errors such as HRESULT `0x80070520`. In that case:

1. Open a normal interactive PowerShell window as the logged-in desktop user.
2. Run the `.cmd` wrapper below rather than launching from a background/service session.
3. Keep Word closed before the test when possible.

Wrapper:

```text
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\run_doc_quality_check.cmd
```

## 5. Example commands

Tool detection:

```powershell
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\detect_tools.ps1 `
  -ConfigPath $(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json') `
  -ProbeCom
```

DOCX quality check without visual QA:

```powershell
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\run_doc_quality_check.ps1 `
  -InputDocx $(Get-Location)\result\generated_pqq_sections.docx `
  -JobName generated_pqq_sections `
  -Dpi 200 `
  -ConfigPath $(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')
```

PDF-only visual QA, optional backends:

```powershell
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\visual_render_qa.ps1 `
  -InputPdf $(Join-Path (Get-Location) '.local\user_level_document_tools\converted\pdf\example.pdf') `
  -JobName example_pdf `
  -Backends pdftoppm,pdf2image `
  -ConfigPath $(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')
```

DOCX quality check with strict visual QA for selected backends:

```powershell
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\run_doc_quality_check.ps1 `
  -InputDocx $(Get-Location)\result\generated_pqq_sections.docx `
  -JobName generated_pqq_sections `
  -RunVisualQa `
  -VisualQaBackends pdftoppm,pdf2image,soffice `
  -RequireVisualQaBackends pdftoppm `
  -ConfigPath $(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')
```

## 6. Visual QA evidence and strict behavior

Visual QA writes render images, JSON summaries, and Markdown evidence under ignored local output by default:

```text
$(Join-Path (Get-Location) '.local\user_level_document_tools\visual_render_qa')
```

Optional mode records missing backends as `skipped` or `unavailable` and lets unrelated structural checks proceed. Strict mode fails only when a backend named by `-RequireBackends` or `visual_qa_require_backends` is missing or unusable.

## 7. Guard reminder

Model-created generated outputs must stay under consumer-owned local output roots such as `result`, `intermediate`, or ignored `.local/user_level_document_tools`. Reusable development assets for the pipeline must stay under tracked source directories, while runtime config, binary tools, and render artifacts stay local. Follow the workspace guard workflow before and after writes.
