#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = ROOT / "tools" / "user_level_document_tools"

class UserLevelDocumentToolsTests(unittest.TestCase):
    def test_required_surfaces_exist(self) -> None:
        required = [
            TOOLS_ROOT / "pdf_tools" / "scripts" / "find_poppler.ps1",
            TOOLS_ROOT / "doc_pipeline" / "scripts" / "detect_tools.ps1",
            TOOLS_ROOT / "doc_pipeline" / "scripts" / "run_doc_quality_check.ps1",
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

if __name__ == "__main__":
    unittest.main(verbosity=2)
