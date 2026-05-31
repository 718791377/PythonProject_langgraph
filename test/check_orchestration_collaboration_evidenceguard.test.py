from __future__ import annotations

import importlib.util
import shutil
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_orchestration_collaboration_evidenceguard.py"

spec = importlib.util.spec_from_file_location("check_orchestration_collaboration_evidenceguard", SCRIPT_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class CollaborationEvidenceguardBilingualSurfaceTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def copy_repository_surfaces(self, root: Path) -> None:
        shutil.copytree(REPO_ROOT / module.DEFAULT_FIXTURE_DIR, root / module.DEFAULT_FIXTURE_DIR)
        for rel in module.REQUIRED_SURFACE_SNIPPETS:
            src = REPO_ROOT / rel
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text(encoding="utf-8-sig"), encoding="utf-8")
        for rel in ("tools/run_openspec_guard.py", "tools/safety_rule_script_backing_registry.json"):
            src = REPO_ROOT / rel
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text(encoding="utf-8-sig"), encoding="utf-8")

    def test_extended_fixture_registration_is_required(self) -> None:
        root = self.make_root("collab-required-fixtures")
        self.copy_repository_surfaces(root)
        (root / module.DEFAULT_FIXTURE_DIR / "cold_start_read_order_valid.json").unlink()

        payload = module.run_repository_check(root)

        self.assertFalse(payload["ok"])
        self.assertTrue(
            any("cold_start_read_order_valid.json" in error for error in payload["errors"]),
            payload["errors"],
        )

    def test_chinese_openspec_surface_requires_bilingual_parity_wording(self) -> None:
        root = self.make_root("collab-zh-bilingual-snippet")
        self.copy_repository_surfaces(root)
        zh_path = root / "openspec/specs/codex-user-level-orchestration-activation-policy/spec.zh-CN.md"
        zh_text = zh_path.read_text(encoding="utf-8-sig").replace("\u53cc\u8bed OpenSpec heading parity", "OpenSpec heading parity")
        zh_path.write_text(zh_text, encoding="utf-8")

        payload = module.run_repository_check(root)

        self.assertFalse(payload["ok"])
        self.assertTrue(
            any("\u53cc\u8bed OpenSpec heading parity" in error for error in payload["errors"]),
            payload["errors"],
        )


if __name__ == "__main__":
    unittest.main()
