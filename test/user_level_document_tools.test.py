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
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

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
            TOOLS_ROOT / "ppt_tools" / "ppt_render_toolchain_config.example.json",
            TOOLS_ROOT / "ppt_tools" / "ppt_render_capability_probe.py",
            TOOLS_ROOT / "ppt_tools" / "powerpoint_com_probe.ps1",
            TOOLS_ROOT / "ppt_tools" / "ppt_render_probe.py",
            TOOLS_ROOT / "ppt_tools" / "write_visual_qa_status_marker.py",
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


    def test_ppt_render_config_example_uses_placeholders_and_absolute_path_fields(self) -> None:
        cfg_path = TOOLS_ROOT / "ppt_tools" / "ppt_render_toolchain_config.example.json"
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        serialized = json.dumps(cfg, ensure_ascii=False)
        for field in (
            "python_exe",
            "poppler_bin_dir",
            "soffice_exe",
            "magick_exe",
            "ghostscript_exe",
            "inkscape_exe",
            "aspose_license_path",
        ):
            self.assertIn(field, cfg)
            self.assertIsInstance(cfg[field], str)
        self.assertIn("<consumer-project>", serialized)
        for forbidden in ("D:\\project", "D:/project", "D:\\PythonProject_OpenClaw", "D:/PythonProject_OpenClaw"):
            self.assertNotIn(forbidden, serialized)
        for forbidden_key in ("path_mutation", "setx", "permanent_path"):
            self.assertNotIn(forbidden_key, cfg)

    def test_ppt_capability_probe_reports_missing_tools_without_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            empty_poppler = tmp_path / "empty-poppler"
            empty_poppler.mkdir()
            config = {
                "python_exe": sys.executable,
                "poppler_bin_dir": str(empty_poppler),
                "soffice_exe": str(tmp_path / "missing-soffice.exe"),
                "magick_exe": str(tmp_path / "missing-magick.exe"),
                "ghostscript_exe": str(tmp_path / "missing-gswin64c.exe"),
                "inkscape_exe": str(tmp_path / "missing-inkscape.exe"),
                "aspose_license_path": "",
                "powerpoint_com_enabled": False,
                "aspose_enabled": False,
            }
            cfg_path = tmp_path / "ppt-config.json"
            cfg_path.write_text(json.dumps(config), encoding="utf-8")
            script = TOOLS_ROOT / "ppt_tools" / "ppt_render_capability_probe.py"
            result = subprocess.run(
                [sys.executable, str(script), "--config", str(cfg_path), "--json"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual(0, result.returncode, result.stdout)
            payload = json.loads(result.stdout)
            rows = {row["name"]: row for row in payload["tools"]}
            for name in ("powerpoint", "soffice", "aspose", "pdftoppm", "pdf2image", "magick", "ghostscript", "inkscape"):
                self.assertIn(name, rows)
                for field in ("installed", "enabled", "selected", "ready"):
                    self.assertIn(field, rows[name])
            for name in ("soffice", "magick", "ghostscript", "inkscape", "pdftoppm"):
                self.assertFalse(rows[name]["installed"], rows[name])
                self.assertFalse(rows[name]["ready"], rows[name])
            self.assertEqual(["installed", "enabled", "selected", "ready"], payload["states_contract"])

    def test_ppt_capability_probe_reports_configured_non_executable_renderer_as_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake_soffice = tmp_path / "fake-soffice.exe"
            fake_soffice.write_text("not an executable", encoding="utf-8")
            empty_poppler = tmp_path / "empty-poppler"
            empty_poppler.mkdir()
            cfg_path = tmp_path / "ppt-config.json"
            cfg_path.write_text(json.dumps({
                "poppler_bin_dir": str(empty_poppler),
                "soffice_exe": str(fake_soffice),
                "magick_exe": str(tmp_path / "missing-magick.exe"),
                "ghostscript_exe": str(tmp_path / "missing-gswin64c.exe"),
                "inkscape_exe": str(tmp_path / "missing-inkscape.exe"),
                "powerpoint_com_enabled": False,
                "aspose_enabled": False,
            }), encoding="utf-8")
            script = TOOLS_ROOT / "ppt_tools" / "ppt_render_capability_probe.py"
            result = subprocess.run(
                [sys.executable, str(script), "--config", str(cfg_path), "--json", "--no-path-lookup"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual(0, result.returncode, result.stdout)
            payload = json.loads(result.stdout)
            rows = {row["name"]: row for row in payload["tools"]}
            self.assertTrue(rows["soffice"]["installed"], rows["soffice"])
            self.assertFalse(rows["soffice"]["ready"], rows["soffice"])
            self.assertEqual(str(fake_soffice), rows["soffice"]["path"])
            self.assertIn("version_probe_warning", rows["soffice"]["probe_status"])
            self.assertFalse(payload["permanent_path_mutation"])
            self.assertFalse(payload["process_scoped_path_lookup"])
            self.assertIn(payload["status"], {"degraded", "blocked"})

    def test_ppt_capability_probe_does_not_mutate_process_path(self) -> None:
        original_path = os.environ.get("PATH", "")
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = Path(tmp) / "missing-config.json"
            script = TOOLS_ROOT / "ppt_tools" / "ppt_render_capability_probe.py"
            env = os.environ.copy()
            env["PATH"] = str(Path(tmp) / "sentinel-only")
            result = subprocess.run(
                [sys.executable, str(script), "--config", str(cfg_path), "--json"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
            )
            self.assertEqual(0, result.returncode, result.stdout)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["permanent_path_mutation"])
            self.assertTrue(payload["process_scoped_path_lookup"])
            self.assertEqual(original_path, os.environ.get("PATH", ""))

    def test_powerpoint_com_probe_parses_without_running_com(self) -> None:
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if powershell is None:
            self.skipTest("PowerShell is not available")
        script_path = TOOLS_ROOT / "ppt_tools" / "powerpoint_com_probe.ps1"
        script_text = script_path.read_text(encoding="utf-8")
        for needle in ("[Environment]::UserInteractive", "PowerPoint.Application", "Quit()", "POWERPNT"):
            self.assertIn(needle, script_text)
        script = f"""
$tokens = $null
$errors = $null
[void][System.Management.Automation.Language.Parser]::ParseFile('{str(script_path).replace("'", "''")}', [ref]$tokens, [ref]$errors)
if ($errors.Count -gt 0) {{ $errors | ForEach-Object {{ Write-Output $_.Message }}; exit 1 }}
"""
        result = subprocess.run(
            [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)

    def test_ppt_render_probe_help_exposes_engine_format_and_json_options(self) -> None:
        script = TOOLS_ROOT / "ppt_tools" / "ppt_render_probe.py"
        result = subprocess.run(
            [sys.executable, str(script), "--help"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        for needle in ("--format", "pdf", "png", "--engine", "auto", "powerpoint", "soffice", "aspose", "--json"):
            self.assertIn(needle, result.stdout)

    def test_ppt_render_probe_blocks_when_no_renderer_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pptx = tmp_path / "sample.pptx"
            write_minimal_pptx(pptx, slide_count=2)
            empty_poppler = tmp_path / "empty-poppler"
            empty_poppler.mkdir()
            cfg = {
                "poppler_bin_dir": str(empty_poppler),
                "soffice_exe": str(tmp_path / "missing-soffice.exe"),
                "magick_exe": str(tmp_path / "missing-magick.exe"),
                "ghostscript_exe": str(tmp_path / "missing-gswin64c.exe"),
                "inkscape_exe": str(tmp_path / "missing-inkscape.exe"),
                "powerpoint_com_enabled": False,
                "aspose_enabled": False,
            }
            cfg_path = tmp_path / "ppt-config.json"
            cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
            out_dir = tmp_path / "out"
            script = TOOLS_ROOT / "ppt_tools" / "ppt_render_probe.py"
            env = os.environ.copy()
            env["PATH"] = str(tmp_path / "empty-path")
            result = subprocess.run(
                [sys.executable, str(script), "--input", str(pptx), "--output-dir", str(out_dir), "--format", "pdf,png", "--engine", "auto", "--config", str(cfg_path), "--json"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
            )
            self.assertNotEqual(0, result.returncode, result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual("blocked", payload["status"])
            self.assertEqual("visual_qa:blocked", payload["visual_qa_status"])
            self.assertIn("no_pptx_to_pdf_renderer_ready", payload["errors"])
            self.assertIn("no_png_renderer_ready", payload["errors"])
            self.assertEqual([], payload["artifacts"])
            self.assertIsNone(payload["selected_engine"])
            self.assertEqual(["pdf", "png"], payload["requested_formats"])

    def test_ppt_render_probe_explicit_powerpoint_blocks_when_powerpoint_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pptx = tmp_path / "sample.pptx"
            write_minimal_pptx(pptx)
            cfg_path = tmp_path / "ppt-config.json"
            cfg_path.write_text(json.dumps({
                "soffice_exe": str(tmp_path / "missing-soffice.exe"),
                "powerpoint_com_enabled": False,
                "aspose_enabled": False,
            }), encoding="utf-8")
            script = TOOLS_ROOT / "ppt_tools" / "ppt_render_probe.py"
            result = subprocess.run(
                [sys.executable, str(script), "--input", str(pptx), "--output-dir", str(tmp_path / "out"), "--format", "pdf,png", "--engine", "powerpoint", "--config", str(cfg_path), "--json"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertNotEqual(0, result.returncode, result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual("powerpoint", payload["requested_engine"])
            self.assertIsNone(payload["selected_engine"])
            self.assertEqual("blocked", payload["status"])
            self.assertEqual("visual_qa:blocked", payload["visual_qa_status"])
            self.assertFalse(payload["pptx_to_pdf_ready"])
            self.assertFalse(payload["png_renderer_ready"])
            self.assertEqual([], payload["artifacts"])
            self.assertIn("no_pptx_to_pdf_renderer_ready", payload["errors"])

    def test_ppt_render_probe_records_all_powerpoint_slide_png_evidence_for_multi_slide_deck(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pptx = tmp_path / "sample.pptx"
            write_minimal_pptx(pptx, slide_count=3)
            out_dir = tmp_path / "out"
            pdf = out_dir / "powerpoint" / "sample.pdf"
            pngs = [out_dir / "powerpoint" / f"slide{i}.png" for i in range(1, 4)]
            pdf.parent.mkdir(parents=True, exist_ok=True)
            pdf.write_bytes(MINIMAL_PDF)
            for png in pngs:
                png.write_bytes(b"\x89PNG\r\n\x1a\n")
            sys.path.insert(0, str(TOOLS_ROOT / "ppt_tools"))
            try:
                import ppt_render_probe  # type: ignore
                with mock.patch.object(ppt_render_probe, "capability_for", return_value={"tools": [{"name": "powerpoint", "ready": True}]}), \
                    mock.patch.object(ppt_render_probe, "run_powerpoint", return_value={
                        "engine": "powerpoint",
                        "status": "ok",
                        "pdf": str(pdf),
                        "png_files": [str(png) for png in pngs],
                        "artifacts": [str(pdf), *[str(png) for png in pngs]],
                    }):
                    stdout = StringIO()
                    with redirect_stdout(stdout):
                        code = ppt_render_probe.main(["--input", str(pptx), "--output-dir", str(out_dir), "--format", "pdf,png", "--engine", "powerpoint", "--json"])
            finally:
                try:
                    sys.path.remove(str(TOOLS_ROOT / "ppt_tools"))
                except ValueError:
                    pass
            self.assertNotEqual(0, code)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(3, payload["slide_count"])
            self.assertEqual([str(png) for png in pngs], payload["rendered_pages"])
            self.assertTrue(payload["pptx_to_pdf_ready"])
            self.assertTrue(payload["png_renderer_ready"])
            self.assertIn(str(pdf), payload["artifacts"])
            for png in pngs:
                self.assertIn(str(png), payload["artifacts"])

    def test_ppt_render_probe_returns_nonzero_when_visual_qa_acceptance_blocked_even_if_render_outputs_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pptx = tmp_path / "sample.pptx"
            write_minimal_pptx(pptx)
            out_dir = tmp_path / "out"
            pdf = out_dir / "aspose" / "sample.pdf"
            png = out_dir / "aspose" / "slide1.png"
            pdf.parent.mkdir(parents=True, exist_ok=True)
            pdf.write_bytes(MINIMAL_PDF)
            png.write_bytes(b"\x89PNG\r\n\x1a\n")
            sys.path.insert(0, str(TOOLS_ROOT / "ppt_tools"))
            try:
                import ppt_render_probe  # type: ignore
                with mock.patch.object(ppt_render_probe, "capability_for", return_value={"tools": [{"name": "aspose", "ready": True}]}), \
                    mock.patch.object(ppt_render_probe, "run_aspose", return_value={
                        "engine": "aspose",
                        "status": "ok",
                        "pdf": str(pdf),
                        "png_files": [str(png)],
                        "artifacts": [str(pdf), str(png)],
                        "aspose_evaluation_watermark": True,
                    }):
                    stdout = StringIO()
                    with redirect_stdout(stdout):
                        code = ppt_render_probe.main(["--input", str(pptx), "--output-dir", str(out_dir), "--format", "pdf,png", "--engine", "aspose", "--json"])
            finally:
                try:
                    sys.path.remove(str(TOOLS_ROOT / "ppt_tools"))
                except ValueError:
                    pass
            self.assertNotEqual(0, code)
            payload = json.loads(stdout.getvalue())
            self.assertEqual("acceptance_blocked", payload["status"])
            self.assertEqual("blocked", payload["acceptance_status"])
            self.assertEqual("visual_qa:degraded", payload["visual_qa_status"])
            self.assertTrue(payload["visual_qa_marker"]["acceptance_blocked"])
            self.assertIn("aspose_evaluation_watermark", payload["visual_qa_marker"]["reasons"])

    def test_ppt_visual_qa_status_classifier_returns_not_applicable_for_non_ppt_input(self) -> None:
        script = TOOLS_ROOT / "ppt_tools" / "write_visual_qa_status_marker.py"
        result = subprocess.run(
            [sys.executable, str(script), "--input", "sample.txt", "--json"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual("visual_qa:not_applicable", payload["status"])
        self.assertFalse(payload["acceptance_blocked"])

    def test_ppt_visual_qa_status_classifier_blocks_missing_or_blank_rendered_pages(self) -> None:
        script = TOOLS_ROOT / "ppt_tools" / "write_visual_qa_status_marker.py"
        cases = [
            ({"input_path": "sample.pptx", "pptx_to_pdf_ready": True, "png_renderer_ready": True, "slide_count": 3, "rendered_pages": []}, "missing_rendered_pages"),
            ({"input_path": "sample.pptx", "pptx_to_pdf_ready": True, "png_renderer_ready": True, "slide_count": 3, "rendered_pages": ["page1.png"]}, "page_count_mismatch"),
            ({"input_path": "sample.pptx", "pptx_to_pdf_ready": True, "png_renderer_ready": True, "slide_count": 1, "rendered_pages": [{"path": "page1.png", "blank": True}]}, "blank_rendered_page"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for index, (payload, reason) in enumerate(cases):
                report = Path(tmp) / f"case{index}.json"
                report.write_text(json.dumps(payload), encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, str(script), "--from-render-report", str(report), "--json"],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                self.assertNotEqual(0, result.returncode, result.stdout)
                out = json.loads(result.stdout)
                self.assertEqual("visual_qa:blocked", out["status"])
                self.assertIn(reason, out["reasons"])

    def test_ppt_visual_qa_status_classifier_degrades_for_aspose_evaluation_watermark(self) -> None:
        script = TOOLS_ROOT / "ppt_tools" / "write_visual_qa_status_marker.py"
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "aspose.json"
            report.write_text(json.dumps({
                "input_path": "sample.pptx",
                "pptx_to_pdf_ready": True,
                "png_renderer_ready": True,
                "slide_count": 1,
                "rendered_pages": ["page1.png"],
                "aspose_evaluation_watermark": True,
                "clean_renderer_ready": False,
            }), encoding="utf-8")
            result = subprocess.run([sys.executable, str(script), "--from-render-report", str(report), "--json"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.assertEqual(0, result.returncode, result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual("visual_qa:degraded", payload["status"])
            self.assertTrue(payload["acceptance_blocked"])
            self.assertIn("aspose_evaluation_watermark", payload["reasons"])

    def test_ppt_visual_qa_status_classifier_requires_manual_review_for_cjk_smoke_uncertain(self) -> None:
        script = TOOLS_ROOT / "ppt_tools" / "write_visual_qa_status_marker.py"
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "cjk.json"
            report.write_text(json.dumps({
                "input_path": "sample.pptx",
                "pptx_to_pdf_ready": True,
                "png_renderer_ready": True,
                "slide_count": 1,
                "rendered_pages": ["page1.png"],
                "cjk_smoke_checked": False,
            }), encoding="utf-8")
            result = subprocess.run([sys.executable, str(script), "--from-render-report", str(report), "--json"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.assertEqual(0, result.returncode, result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual("visual_qa:manual_required", payload["status"])
            self.assertIn("cjk_text_manual_review_required", payload["reasons"])

    def test_ppt_tools_source_has_no_permanent_path_mutation_commands(self) -> None:
        ppt_root = TOOLS_ROOT / "ppt_tools"
        forbidden = ("setx", "[Environment]::SetEnvironmentVariable", "HKCU\\Environment", "HKLM", "Machine")
        offenders: list[str] = []
        for path in ppt_root.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for token in forbidden:
                if token in text:
                    offenders.append(f"{path.relative_to(ROOT)} contains {token}")
        self.assertEqual([], offenders)

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


def write_minimal_pptx(path: Path, slide_count: int = 1) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
</Types>""",
        )
        zf.writestr(
            "_rels/.rels",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>""",
        )
        zf.writestr(
            "ppt/presentation.xml",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:sldIdLst>""" + "".join(f'<p:sldId id="{256+i}" r:id="rId{i}"/>' for i in range(1, slide_count + 1)) + """</p:sldIdLst>
</p:presentation>""",
        )
        for i in range(1, slide_count + 1):
            zf.writestr(f"ppt/slides/slide{i}.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree/></p:cSld></p:sld>""")

if __name__ == "__main__":
    unittest.main(verbosity=2)
