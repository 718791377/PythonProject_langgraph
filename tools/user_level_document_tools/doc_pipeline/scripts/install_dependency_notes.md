# Document Pipeline Dependency Notes

This file records how to unblock the remaining pilot tasks for the Word COM + Acrobat Pro + Poppler pipeline.

## Poppler

Required commands:

- `pdfinfo.exe`
- `pdffonts.exe`
- `pdftoppm.exe`
- `pdftocairo.exe`

After installing Poppler, either add its bin directory to PATH or run:

```powershell
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\configure_doc_pipeline.ps1 `
  -PopplerBinDir "C:\Tools\poppler\Library\bin" `
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

Access-denied results usually mean the current constrained host cannot access the configured package path. Retry from an interactive desktop shell, or configure Poppler to an accessible local tools directory.

## Pillow

Pillow is optional but needed for contact sheets. Without Pillow, use `-SkipContactSheet`.

```powershell
python -m pip install Pillow
```

Do not run package installation from an automated model step unless the user explicitly approves it.

## Word COM

If Word COM probe fails in the Codex/non-interactive host, run the quality check from an interactive desktop PowerShell window:

```cmd
$(Resolve-Path (Join-Path $PSScriptRoot '..'))\scripts\run_doc_quality_check.cmd -InputDocx $(Get-Location)\result\generated_pqq_sections.docx -JobName generated_pqq_sections -SkipContactSheet
```

## Acrobat Pro

Acrobat Pro is used manually or through Action Wizard for PDF-to-DOCX and OCR. Always run converted DOCX files through the downstream Word/Poppler checks.
