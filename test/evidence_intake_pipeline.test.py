import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import evidence_intake_pipeline as extractor  # noqa: E402


SCRIPT_PATH = REPO_ROOT / "tools" / "evidence_intake_pipeline.py"


class EvidenceIntakePipelineTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def test_text_metrics_marks_clean_text_as_usable(self) -> None:
        text = "This is a clean paragraph about project management.\n" * 5
        metrics = extractor.text_metrics(text)
        self.assertEqual(metrics["quality"], "usable")
        self.assertFalse(metrics["needs_review"])
        self.assertGreater(metrics["latin_chars"], 20)

    def test_text_metrics_marks_tiny_or_noisy_text_for_review(self) -> None:
        tiny = extractor.text_metrics("")
        noisy = extractor.text_metrics("A B C D E F \ufffd\ufffd\ufffd" * 10)

        self.assertEqual(tiny["quality"], "empty-or-tiny")
        self.assertTrue(tiny["needs_review"])
        self.assertIn(noisy["quality"], {"noisy", "needs-review"})
        self.assertTrue(noisy["needs_review"])

    def test_visible_text_parser_removes_script_style_and_collects_metadata(self) -> None:
        html = """
        <html>
          <head>
            <title>Reference Title</title>
            <meta name="author" content="Example Author">
            <style>.hidden { display: none; }</style>
            <script>window.secret = "noise";</script>
          </head>
          <body>
            <h1>Visible Heading</h1>
            <p>Visible body 2026-05-07.</p>
          </body>
        </html>
        """
        parser = extractor.VisibleTextParser()
        parser.feed(html)

        self.assertIn("Visible Heading", parser.visible_text)
        self.assertIn("Visible body", parser.visible_text)
        self.assertNotIn("window.secret", parser.visible_text)
        self.assertNotIn(".hidden", parser.visible_text)
        self.assertEqual(parser.title, "Reference Title")
        metadata = extractor.html_metadata(parser, parser.visible_text)
        self.assertEqual(metadata["author"], "Example Author")
        self.assertEqual(metadata["date"], "2026-05-07")

    def test_classify_candidate_recommendations(self) -> None:
        root = self.make_root("inventory-classify")
        paths = {
            "tools/poppler-25.07.0/Library/bin/pdftotext.exe": "third-party-install-instead",
            ".tmp/pydeps/site-packages/readability/__init__.py": "do-not-copy",
            "intermediate/run/extract_sources.py": "project-specific-only",
            "current_progress/reference.pdf": "project-specific-only",
            "tools/html_extract_adapter.py": "consider-adapter",
        }
        for relative, expected in paths.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("placeholder", encoding="utf-8")
            record = extractor.classify_candidate(path, root)
            self.assertEqual(record["recommendation"], expected, relative)

    def test_inventory_tools_prefers_source_tools_and_skips_packaged_dependencies(self) -> None:
        root = self.make_root("inventory-tools")
        adapter = root / "tools" / "doc_pipeline" / "scripts" / "find_poppler.ps1"
        adapter.parent.mkdir(parents=True, exist_ok=True)
        adapter.write_text("Poppler pdftotext helper", encoding="utf-8")
        dep = root / "tools" / "doc_pipeline" / "python_packages" / "PIL" / "PdfImagePlugin.py"
        dep.parent.mkdir(parents=True, exist_ok=True)
        dep.write_text("dependency pdf plugin", encoding="utf-8")
        binary = root / "tools" / "poppler" / "bin" / "pdftotext.exe"
        binary.parent.mkdir(parents=True, exist_ok=True)
        binary.write_bytes(b"exe")
        output = root / "inventory.json"

        payload = extractor.inventory_tools(root, output, limit=20)
        paths = {record["path"]: record for record in payload["records"]}

        self.assertIn("tools/doc_pipeline/scripts/find_poppler.ps1", paths)
        self.assertEqual(paths["tools/doc_pipeline/scripts/find_poppler.ps1"]["recommendation"], "consider-adapter")
        self.assertIn("tools/poppler/bin/pdftotext.exe", paths)
        self.assertEqual(paths["tools/poppler/bin/pdftotext.exe"]["recommendation"], "third-party-install-instead")
        self.assertNotIn("tools/doc_pipeline/python_packages/PIL/PdfImagePlugin.py", paths)

    def test_extract_html_smoke_and_check_cli(self) -> None:
        root = self.make_root("html-extract")
        source = root / "local_reference" / "saved_pages"
        source.mkdir(parents=True, exist_ok=True)
        (source / "article.html").write_text(
            "<html><head><title>Article</title></head><body><p>Visible article body.</p><script>noise()</script></body></html>",
            encoding="utf-8",
        )
        output = root / ".local" / "evidence" / "local_reference"

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "extract",
                "--root",
                str(root),
                "--source",
                "local_reference",
                "--output",
                str(output),
                "--max-pages",
                "0",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["counts"]["htmls"], 1)
        self.assertTrue((output / "manifest.json").exists())

        check = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "check", "--output", str(output), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )
        self.assertEqual(check.returncode, 0, check.stdout + "\n" + check.stderr)
        self.assertTrue(json.loads(check.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
