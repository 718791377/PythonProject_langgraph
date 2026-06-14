# Document Pipeline Setup Guide

This guide supports the local Word COM + Acrobat Pro + Poppler pipeline.

## 1. Current expected tool roles

- Microsoft Word COM: DOCX open check and Word-layout PDF export.
- Adobe Acrobat Pro: PDF to DOCX export and scanned-PDF OCR.
- Poppler: `pdfinfo`, `pdffonts`, `pdftoppm`, and `pdftocairo` for PDF inspection and rendering.
- Python: helper scripts.
- Python Pillow: optional contact-sheet image generation.

## 2. Configure Poppler

If Poppler is not on PATH, install it locally and point the scripts to its `bin` directory.

Recommended local config path:

```text
$(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')
```

Create it by copying:

```text
$(Join-Path (Get-Location) 'config\doc_pipeline')\doc_pipeline_config.example.json
```

Then set:

```json
"poppler_bin_dir": "C:\\Tools\\poppler\\Library\\bin"
```

You can also pass `-PopplerBinDir` directly to scripts.

If Poppler is configured but rendering still fails, run the focused access test:

```powershell
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\test_poppler_access.ps1 `
  -ConfigPath $(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')
```

If this reports access-denied for a WinGet package path, retry from a normal interactive desktop PowerShell or CMD session. If it is still inaccessible, reinstall or copy Poppler to an accessible tools directory such as `C:\Tools\poppler\Library\bin`, then rerun `configure_doc_pipeline.ps1 -PopplerBinDir <path> -Force`.

## 3. Configure Pillow for contact sheets

`build_contact_sheet.py` requires Pillow. If Pillow is not installed, run the quality check with `-SkipContactSheet`, or install Pillow in the Python environment you intend to use.

Example if using a project venv:

```powershell
$(Join-Path (Get-Location) '.venv')\Scripts\python.exe -m pip install Pillow
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

Poppler access check:

```powershell
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\test_poppler_access.ps1 `
  -ConfigPath $(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')
```

DOCX quality check:

```powershell
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\run_doc_quality_check.ps1 `
  -InputDocx $(Get-Location)\result\generated_pqq_sections.docx `
  -JobName generated_pqq_sections `
  -Dpi 200 `
  -ConfigPath $(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')
```

If Pillow is not installed:

```powershell
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\run_doc_quality_check.ps1 `
  -InputDocx $(Get-Location)\result\generated_pqq_sections.docx `
  -JobName generated_pqq_sections `
  -SkipContactSheet
```

PDF-only inspection after Poppler is configured:

```powershell
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\run_doc_quality_check.ps1 `
  -InputPdf $(Join-Path (Get-Location) '.local\user_level_document_tools\converted\pdf')\example.pdf `
  -JobName example_pdf `
  -Dpi 300
```

## 6. Guard reminder

Model-created generated outputs must stay under `$(Get-Location)\result` or `$(Get-Location)\intermediate`. Reusable development assets for the pipeline must stay under `$(Get-Location)\tools`, `$(Get-Location)\scripts`, `$(Get-Location)\config`, `$(Join-Path (Get-Location) '.venv')`, or another non-protected development path. Follow the workspace guard workflow before and after writes.
