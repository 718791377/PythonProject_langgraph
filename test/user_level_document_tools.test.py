#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = ROOT / "tools" / "user_level_document_tools"

class UserLevelDocumentToolsTests(unittest.TestCase):
    def test_required_surfaces_exist(self) -> None:
        required = [
            TOOLS_ROOT / "pdf_tools" / "scripts" / "find_poppler.ps1",
            TOOLS_ROOT / "doc_pipeline" / "scripts" / "detect_tools.ps1",
            TOOLS_ROOT / "doc_pipeline" / "scripts" / "run_doc_quality_check.ps1",
            TOOLS_ROOT / "doc_pipeline" / "scripts" / "render_pdf_pdf2image.py",
            TOOLS_ROOT / "doc_pipeline" / "scripts" / "export_docx_to_pdf_soffice.ps1",
            TOOLS_ROOT / "doc_pipeline" / "scripts" / "visual_render_qa.ps1",
            TOOLS_ROOT / "vector_tools" / "vector_toolkit.py",
            TOOLS_ROOT / "config" / "doc_pipeline_config.example.json",
            TOOLS_ROOT / "config" / "vector_tools_config.example.json",
        ]
        self.assertEqual([], [str(p.relative_to(ROOT)) for p in required if not p.exists()])

    def test_tracked_tool_source_has_no_project_absolute_paths(self) -> None:
        forbidden = ["D:\\project", "D:/project", "D:\\PythonProject_OpenClaw", "D:/PythonProject_OpenClaw"]
        offenders: list[str] = []
        for path in TOOLS_ROOT.rglob("*"):
            if not path.is_file() or path.suffix.lower() in {".exe", ".dll", ".pyd", ".zip"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for token in forbidden:
                if token in text:
                    offenders.append(f"{path.relative_to(ROOT)} contains {token}")
        self.assertEqual([], offenders)

    def test_examples_are_placeholders_not_consumer_configs(self) -> None:
        doc_cfg = json.loads((TOOLS_ROOT / "config" / "doc_pipeline_config.example.json").read_text(encoding="utf-8"))
        vector_cfg = json.loads((TOOLS_ROOT / "config" / "vector_tools_config.example.json").read_text(encoding="utf-8"))
        self.assertIn("<consumer-project>", json.dumps(doc_cfg))
        self.assertIn("<consumer-project>", json.dumps(vector_cfg))
        self.assertEqual("", doc_cfg["poppler_bin_dir"])
        self.assertEqual("", doc_cfg["soffice_exe"])
        self.assertFalse(doc_cfg["visual_qa_enabled_by_default"])
        self.assertEqual([], doc_cfg["visual_qa_require_backends"])
        self.assertIn("pdftoppm", doc_cfg["visual_qa_default_backends"])
        self.assertIn("pdf2image", doc_cfg["visual_qa_default_backends"])
        self.assertIn("soffice", doc_cfg["visual_qa_default_backends"])

    def test_vector_toolkit_validates_and_queries_temp_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "chunks.jsonl"
            manifest.write_text(json.dumps({"id": "one", "content": "alpha beta", "sourcePath": "local"}) + "\n", encoding="utf-8")
            toolkit = TOOLS_ROOT / "vector_tools" / "vector_toolkit.py"
            validate = subprocess.run([sys.executable, str(toolkit), "validate-manifest", "--manifest", str(manifest), "--require-field", "id"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.assertEqual(0, validate.returncode, validate.stdout)
            query = subprocess.run([sys.executable, str(toolkit), "query-jsonl", "--manifest", str(manifest), "--query", "alpha"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.assertEqual(0, query.returncode, query.stdout)
            self.assertEqual(1, json.loads(query.stdout)["resultCount"])

    def test_powershell_tool_scripts_parse(self) -> None:
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if powershell is None:
            self.skipTest("PowerShell is not available")
        script = f"""
$ErrorActionPreference = 'Stop'
$root = '{str(TOOLS_ROOT).replace("'", "''")}'
$failed = @()
Get-ChildItem -LiteralPath $root -Recurse -Filter '*.ps1' | ForEach-Object {{
    $tokens = $null
    $errors = $null
    [void][System.Management.Automation.Language.Parser]::ParseFile($_.FullName, [ref]$tokens, [ref]$errors)
    if ($errors.Count -gt 0) {{
        $failed += "$($_.FullName): $($errors[0].Message)"
    }}
}}
if ($failed.Count -gt 0) {{
    $failed | ForEach-Object {{ Write-Output $_ }}
    exit 1
}}
"""
        result = subprocess.run(
            [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)

    def test_detect_tools_report_lists_visual_render_backends(self) -> None:
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if powershell is None:
            self.skipTest("PowerShell is not available")
        with tempfile.TemporaryDirectory() as tmp:
            report_dir = Path(tmp) / "detect"
            script = TOOLS_ROOT / "doc_pipeline" / "scripts" / "detect_tools.ps1"
            result = subprocess.run(
                [
                    powershell,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script),
                    "-ReportDir",
                    str(report_dir),
                    "-ConfigPath",
                    str(Path(tmp) / "missing-config.json"),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual(0, result.returncode, result.stdout)
            payload = json.loads((report_dir / "tool_detection_report.json").read_text(encoding="utf-8-sig"))
            rows = {str(row.get("backend") or row.get("name")): row for row in payload["tools"]}
            names = {str(row.get("name")) for row in payload["tools"]}
            self.assertIn("pdftoppm", rows)
            self.assertIn("pdf2image", rows)
            self.assertTrue("LibreOffice" in names or "soffice" in rows)
            for key in ("pdftoppm", "pdf2image"):
                self.assertIn("installed", rows[key])
                self.assertIn("usable", rows[key])
                self.assertIn("probe_status", rows[key])

    def test_visual_render_qa_degrades_when_optional_backends_missing(self) -> None:
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if powershell is None:
            self.skipTest("PowerShell is not available")
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "sample.pdf"
            pdf.write_bytes(MINIMAL_PDF)
            output_root = Path(tmp) / "visual"
            empty_poppler = Path(tmp) / "empty-poppler"
            empty_poppler.mkdir()
            script = TOOLS_ROOT / "doc_pipeline" / "scripts" / "visual_render_qa.ps1"
            env = os.environ.copy()
            env["PATH"] = str(Path(tmp) / "empty-path")
            result = subprocess.run(
                [
                    powershell,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script),
                    "-InputPdf",
                    str(pdf),
                    "-OutputRoot",
                    str(output_root),
                    "-Backends",
                    "pdftoppm",
                    "-PopplerBinDir",
                    str(empty_poppler),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
            )
            self.assertEqual(0, result.returncode, result.stdout)
            payload = json.loads((output_root / "sample" / "reports" / "sample_visual_render_qa.json").read_text(encoding="utf-8-sig"))
            self.assertEqual("partial", payload["status"])
            self.assertEqual("unavailable", payload["backend_results"][0]["status"])

    def test_visual_render_qa_fails_when_required_backend_missing(self) -> None:
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if powershell is None:
            self.skipTest("PowerShell is not available")
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "sample.pdf"
            pdf.write_bytes(MINIMAL_PDF)
            output_root = Path(tmp) / "visual"
            empty_poppler = Path(tmp) / "empty-poppler"
            empty_poppler.mkdir()
            script = TOOLS_ROOT / "doc_pipeline" / "scripts" / "visual_render_qa.ps1"
            env = os.environ.copy()
            env["PATH"] = str(Path(tmp) / "empty-path")
            result = subprocess.run(
                [
                    powershell,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script),
                    "-InputPdf",
                    str(pdf),
                    "-OutputRoot",
                    str(output_root),
                    "-Backends",
                    "pdftoppm",
                    "-RequireBackends",
                    "pdftoppm",
                    "-PopplerBinDir",
                    str(empty_poppler),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
            )
            self.assertNotEqual(0, result.returncode, result.stdout)
            payload = json.loads((output_root / "sample" / "reports" / "sample_visual_render_qa.json").read_text(encoding="utf-8-sig"))
            self.assertEqual("failed", payload["status"])
            self.assertEqual(["pdftoppm"], payload["missing_required_backends"])

    def test_pdftoppm_smoke_runs_only_when_available(self) -> None:
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if powershell is None:
            self.skipTest("PowerShell is not available")
        pdftoppm_bin_dir = find_tool_bin_dir("pdftoppm")
        if pdftoppm_bin_dir is None:
            self.skipTest("pdftoppm is not available")
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "sample.pdf"
            pdf.write_bytes(MINIMAL_PDF)
            output_root = Path(tmp) / "visual"
            script = TOOLS_ROOT / "doc_pipeline" / "scripts" / "visual_render_qa.ps1"
            result = subprocess.run(
                [
                    powershell,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script),
                    "-InputPdf",
                    str(pdf),
                    "-OutputRoot",
                    str(output_root),
                    "-Backends",
                    "pdftoppm",
                    "-RequireBackends",
                    "pdftoppm",
                    "-PopplerBinDir",
                    str(pdftoppm_bin_dir),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual(0, result.returncode, result.stdout)
            payload = json.loads((output_root / "sample" / "reports" / "sample_visual_render_qa.json").read_text(encoding="utf-8-sig"))
            rows = {row["backend"]: row for row in payload["backend_results"]}
            self.assertEqual("ok", rows["pdftoppm"]["status"])
            self.assertGreaterEqual(len(rows["pdftoppm"]["artifact_paths"]), 1)

    def test_pdf2image_smoke_runs_only_when_available(self) -> None:
        pdftoppm_bin_dir = find_tool_bin_dir("pdftoppm")
        if pdftoppm_bin_dir is None:
            self.skipTest("pdftoppm is not available for pdf2image")
        import_check = subprocess.run(
            [sys.executable, "-c", "import pdf2image"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if import_check.returncode != 0:
            self.skipTest("pdf2image is not importable")
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "sample.pdf"
            pdf.write_bytes(MINIMAL_PDF)
            output_dir = Path(tmp) / "render"
            report_dir = Path(tmp) / "report"
            script = TOOLS_ROOT / "doc_pipeline" / "scripts" / "render_pdf_pdf2image.py"
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--input-pdf",
                    str(pdf),
                    "--output-dir",
                    str(output_dir),
                    "--report-dir",
                    str(report_dir),
                    "--job-name",
                    "sample",
                    "--poppler-bin-dir",
                    str(pdftoppm_bin_dir),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual(0, result.returncode, result.stdout)
            payload = json.loads((report_dir / "sample_pdf2image_render.json").read_text(encoding="utf-8-sig"))
            self.assertEqual("ok", payload["status"])
            self.assertGreaterEqual(payload["rendered_count"], 1)

    def test_soffice_smoke_runs_only_when_available(self) -> None:
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if powershell is None:
            self.skipTest("PowerShell is not available")
        soffice = find_soffice()
        if soffice is None:
            self.skipTest("LibreOffice/soffice is not available")
        with tempfile.TemporaryDirectory() as tmp:
            docx = Path(tmp) / "sample.docx"
            write_minimal_docx(docx)
            output_dir = Path(tmp) / "pdf"
            report_dir = Path(tmp) / "report"
            script = TOOLS_ROOT / "doc_pipeline" / "scripts" / "export_docx_to_pdf_soffice.ps1"
            result = subprocess.run(
                [
                    powershell,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script),
                    "-InputDocx",
                    str(docx),
                    "-OutputDir",
                    str(output_dir),
                    "-ReportDir",
                    str(report_dir),
                    "-JobName",
                    "sample",
                    "-SofficeExe",
                    str(soffice),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual(0, result.returncode, result.stdout)
            payload = json.loads((report_dir / "sample_soffice_export.json").read_text(encoding="utf-8-sig"))
            self.assertEqual("ok", payload["status"])
            self.assertTrue(Path(payload["output_pdf"]).exists())


MINIMAL_PDF = b"""%PDF-1.1
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 72 72] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT /F1 12 Tf 10 40 Td (Hello) Tj ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000204 00000 n
trailer
<< /Root 1 0 R /Size 5 >>
startxref
298
%%EOF
"""


def find_tool_bin_dir(name: str) -> Path | None:
    found = shutil.which(name)
    if found:
        return Path(found).resolve().parent
    local_root = ROOT / ".local" / "user_level_document_tools"
    if local_root.exists():
        suffixes = (f"{name}.exe", name)
        for path in local_root.rglob("*"):
            if path.is_file() and path.name in suffixes:
                return path.parent.resolve()
    return None


def find_soffice() -> Path | None:
    for name in ("soffice", "soffice.exe", "libreoffice"):
        found = shutil.which(name)
        if found:
            return Path(found).resolve()
    for candidate in (
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "LibreOffice" / "program" / "soffice.exe",
        Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "LibreOffice" / "program" / "soffice.exe",
    ):
        if candidate.exists():
            return candidate.resolve()
    return None


def write_minimal_docx(path: Path) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""",
        )
        zf.writestr(
            "_rels/.rels",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""",
        )
        zf.writestr(
            "word/document.xml",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Visual QA smoke</w:t></w:r></w:p>
    <w:sectPr/>
  </w:body>
</w:document>""",
        )

if __name__ == "__main__":
    unittest.main(verbosity=2)
