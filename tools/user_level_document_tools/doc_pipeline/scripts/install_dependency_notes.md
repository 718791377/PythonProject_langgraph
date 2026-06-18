# Document Pipeline Dependency Notes

This file records how to unblock the remaining pilot tasks for the Word COM + Acrobat Pro + Poppler pipeline and the visual rendering QA backends.

## Poppler / pdftoppm

Required commands:

- `pdfinfo.exe`
- `pdffonts.exe`
- `pdftoppm.exe`
- `pdftocairo.exe`

After installing Poppler, either add its bin directory to PATH or record its ignored local-tools bin directory in the consumer project's local runtime config. For this shared tooling, Poppler binaries belong in a consumer-owned ignored local path such as `.local/user_level_document_tools/.../Library/bin`, not in tracked source.

```powershell
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\configure_doc_pipeline.ps1 `
  -PopplerBinDir "<consumer-project>\.local\user_level_document_tools\<poppler>\Library\bin" `
  -Force
```

Then re-run:

```powershell
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\detect_tools.ps1 -ProbeCom
```

If Poppler appears installed but the current shell cannot execute it, run:

```powershell
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\test_poppler_access.ps1 `
  -ConfigPath $(Join-Path (Get-Location) 'config\doc_pipeline\doc_pipeline_config.json')
```

Access-denied results usually mean the current constrained host cannot access the configured package path. Retry from an interactive desktop shell, or configure Poppler to an accessible ignored local tools directory.

## pdf2image and Pillow

`pdf2image` is optional visual-rendering QA support. It is installed in the Python environment used by the consumer project, normally that project's `.venv`. On Windows, `pdf2image` is not a Poppler replacement; it still needs a Poppler backend path that contains `pdftoppm`.

Pillow is optional but needed for contact sheets and is normally installed in the same virtual environment. Without Pillow, use `-SkipContactSheet`.

```powershell
<consumer-project>\.venv\Scripts\python.exe -m pip install pdf2image Pillow
```

Do not run package installation from an automated model step unless the user explicitly approves it.

## LibreOffice / soffice

LibreOffice is an external Windows installation or PATH-provided tool. The shared repository does not vendor LibreOffice installers, binaries, portable archives, or machine-specific executable paths. If it is not on PATH, fill `soffice_exe` or `libreoffice_exe` in the consumer project's local runtime config.

The `soffice` backend is optional by default. It becomes strict only when it is listed in `-RequireBackends` or `visual_qa_require_backends`.

## Word COM

If Word COM probe fails in the Codex/non-interactive host, run the quality check from an interactive desktop PowerShell window:

```cmd
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\run_doc_quality_check.cmd -InputDocx <consumer-project>\result\generated_pqq_sections.docx -JobName generated_pqq_sections -SkipContactSheet
```

## Acrobat Pro

Acrobat Pro is used manually or through Action Wizard for PDF-to-DOCX and OCR. Always run converted DOCX files through the downstream Word/Poppler checks.

## Visual rendering QA behavior

Visual QA writes render artifacts, JSON summaries, and Markdown evidence under an ignored local output root, by default:

```text
<consumer-project>/.local/user_level_document_tools/visual_render_qa/
```

Optional mode is the default: missing `pdftoppm`, `pdf2image`, or `soffice` records `skipped` or `unavailable` evidence without pretending visual QA passed and without crashing unrelated structural checks. Strict mode applies only to explicitly required backends and fails with structured evidence when a required backend is missing or unusable.
