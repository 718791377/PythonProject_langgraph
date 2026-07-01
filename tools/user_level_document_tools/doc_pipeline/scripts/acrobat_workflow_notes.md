# Acrobat Pro Workflow Notes

These notes describe the desktop-assisted part of the Word COM + Acrobat Pro + Poppler document pipeline.

## Text-based PDF to Word

1. Open the PDF in Adobe Acrobat Pro.
2. Use Export PDF.
3. Select Microsoft Word, then Word Document.
4. Save the DOCX under `$(Join-Path (Get-Location) '.local\user_level_document_tools\converted\docx_from_pdf')`.
5. Run the DOCX through the Word COM open check.
6. Export the converted DOCX back to PDF with Word.
7. Render the original PDF and the post-conversion PDF with Poppler.
8. Review tables, headers, footers, images, page breaks, and fonts.

## Scanned PDF to Word

1. Open the scanned PDF in Adobe Acrobat Pro.
2. Run Recognize Text / OCR.
3. Review OCR language settings before export.
4. Export to Microsoft Word.
5. Save the DOCX under `$(Join-Path (Get-Location) '.local\user_level_document_tools\converted\docx_from_pdf')`.
6. Treat the result as reconstructed content requiring human review.
7. Run Word COM and Poppler checks before using the document as a deliverable.

## Action Wizard

Use Acrobat Action Wizard for semi-batch OCR or export work when multiple PDFs need the same treatment. Keep the output folder under `$(Get-Location)\result\converted` or `$(Get-Location)\intermediate`.

## Fact Safety

PDF-to-DOCX output must not be used to invent missing facts. If contract values, durations, owners, equipment quantities, model numbers, or page references are not present in the source material, mark them as not specified or to be confirmed.

## Automation Boundary

Acrobat Pro is treated as a local desktop-assisted tool in this plan. Do not design this workflow as a fully unattended server-side Acrobat automation service.
