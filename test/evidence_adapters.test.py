import json
import shutil
import sys
import unittest
import uuid
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import evidence_intake_pipeline as pipeline  # noqa: E402
from evidence_adapters import poppler_adapter, tesseract_adapter  # noqa: E402


class EvidenceAdaptersTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def test_discover_poppler_prefers_explicit_bin_dir(self) -> None:
        root = self.make_root("poppler-discovery")
        bin_dir = root / "poppler" / "Library" / "bin"
        bin_dir.mkdir(parents=True)
        for name in ["pdfinfo.exe", "pdftotext.exe", "pdftoppm.exe", "pdftocairo.exe"]:
            (bin_dir / name).write_text("fake", encoding="utf-8")

        tools = poppler_adapter.discover_poppler(bin_dir=str(bin_dir))

        self.assertEqual(Path(tools.pdfinfo or ""), bin_dir / "pdfinfo.exe")
        self.assertEqual(Path(tools.pdftotext or ""), bin_dir / "pdftotext.exe")
        self.assertEqual(Path(tools.pdftoppm or ""), bin_dir / "pdftoppm.exe")
        self.assertTrue(tools.complete_for_text)
        self.assertTrue(tools.complete_for_render)

    def test_tesseract_confidence_parser_averages_non_negative_word_confidence(self) -> None:
        tsv = "level\tpage_num\tconf\ttext\n1\t1\t-1\t\n5\t1\t90\tHello\n5\t1\t80\tWorld\n"

        self.assertEqual(tesseract_adapter.parse_tesseract_confidence(tsv), 85.0)

    def test_discover_tesseract_checks_standard_windows_install_paths(self) -> None:
        expected = Path("C:/Program Files/Tesseract-OCR/tesseract.exe")

        with mock.patch.object(tesseract_adapter, "command_path", return_value=None), \
             mock.patch.object(Path, "is_file", autospec=True, side_effect=lambda path: path == expected):
            self.assertEqual(tesseract_adapter.discover_tesseract(), str(expected))

    def test_parse_page_spec_deduplicates_ranges_and_rejects_invalid_values(self) -> None:
        self.assertEqual(pipeline.parse_page_spec("1,3-5,4", max_page=10), [1, 3, 4, 5])
        with self.assertRaises(ValueError):
            pipeline.parse_page_spec("0", max_page=10)
        with self.assertRaises(ValueError):
            pipeline.parse_page_spec("9-11", max_page=10)
        with self.assertRaises(ValueError):
            pipeline.parse_page_spec("5-3", max_page=10)

    def test_ocr_run_records_missing_tesseract_without_claiming_completion(self) -> None:
        root = self.make_root("ocr-run-missing-tool")
        pdf = root / "sample.pdf"
        pdf.write_bytes(b"%PDF-1.4\n% fake test pdf\n")
        output = root / ".local" / "evidence" / "ocr"
        poppler_tools = poppler_adapter.PopplerTools(
            pdfinfo="fake-pdfinfo",
            pdftotext="fake-pdftotext",
            pdftoppm="fake-pdftoppm",
            bin_dir=str(root / "fake-bin"),
        )

        def fake_extract_pages(pdftotext: str, path: Path, text_dir: Path, limit: int):
            text_dir.mkdir(parents=True, exist_ok=True)
            return {
                1: ("short", None),
                2: ("This page has enough extracted text to avoid the text-short threshold.", None),
                3: ("", None),
            }

        def fake_render(pdftoppm: str, path: Path, page: int, out_path: Path, dpi: int):
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(b"png")
            return None

        with mock.patch.object(pipeline.poppler_adapter, "discover_poppler", return_value=poppler_tools), \
             mock.patch.object(pipeline.poppler_adapter, "pdf_page_count", return_value=3), \
             mock.patch.object(pipeline.poppler_adapter, "extract_pdf_pages_whole_doc", side_effect=fake_extract_pages), \
             mock.patch.object(pipeline.poppler_adapter, "render_pdf_page", side_effect=fake_render), \
             mock.patch.object(pipeline.tesseract_adapter, "discover_tesseract", return_value=None):
            manifest = pipeline.run_page_level_ocr(
                root=root,
                pdf=pdf,
                output=output,
                scope="text-short",
                pages_spec=None,
                short_threshold=20,
                ocr_languages="eng+chi_sim",
                render_dpi=72,
            )

        self.assertEqual(manifest["requested_pages"], [1, 3])
        self.assertFalse(manifest["ocr_complete"])
        self.assertEqual(manifest["counts"]["rendered_pages"], 2)
        self.assertEqual(manifest["counts"]["blocked_pages"], 2)
        self.assertEqual(manifest["counts"]["ocr_completed_pages"], 0)
        self.assertTrue((output / "manifest.json").exists())
        self.assertTrue((output / "summary.md").exists())
        saved = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["pages"][0]["ocr_status"], "blocked")
        self.assertIn("tesseract not found", saved["pages"][0]["ocr_error"])


if __name__ == "__main__":
    unittest.main()
