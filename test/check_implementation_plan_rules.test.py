import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_implementation_plan_rules.py"


class ImplementationPlanRulesCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_file(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def structured_plan(self, title: str = "Sample", evidence_path: str | None = None, extra: str = "") -> str:
        evidence_line = (
            f"- [x] Evidence captured at `{evidence_path}`.\n"
            if evidence_path
            else "- [x] No completed evidence packages yet.\n"
        )
        return (
            f"# {title}\n\n"
            "## Current Status\n\n"
            "<!-- CURRENT_STATUS_START -->\n"
            "- [x] Status is current.\n"
            "<!-- CURRENT_STATUS_END -->\n\n"
            "## Task Backlog\n\n"
            "<!-- TASK_BACKLOG_START -->\n"
            "- [ ] Keep the next task small.\n"
            "<!-- TASK_BACKLOG_END -->\n\n"
            "## Completed Evidence Index\n\n"
            "<!-- EVIDENCE_INDEX_START -->\n"
            f"{evidence_line}"
            "<!-- EVIDENCE_INDEX_END -->\n"
            f"{extra}"
        )

    def registry(self, status: str = "active") -> str:
        return (
            "version: 1\n"
            "documents:\n"
            "  - doc_id: sample_plan\n"
            "    doc_class: implementation_plan\n"
            f"    status: {status}\n"
            "    canonical_path: docs_bilingual/implementation_plans/sample_plan.md\n"
            "    zh_cn_path: docs_bilingual/implementation_plans/sample_plan.zh-CN.md\n"
        )

    def run_check(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def run_check_json(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(root), "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def test_passes_for_active_english_primary_and_chinese_companion(self) -> None:
        root = self.make_root("impl-plan-pass")
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.md", self.structured_plan())
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.zh-CN.md", self.structured_plan("示例"))
        self.write_file(root, "docs_bilingual/docs_registry.yaml", self.registry())

        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertIn("Implementation plan rules check passed.", result.stdout)

        json_result = self.run_check_json(root)
        self.assertEqual(json_result.returncode, 0, json_result.stdout + "\n" + json_result.stderr)
        payload = json.loads(json_result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["check_name"], "implementation_plan_rules")
        self.assertEqual(Path(payload["root"]), root)
        self.assertTrue(payload["generated_at"])
        self.assertEqual(payload["implementation_plan_entries"], 1)
        self.assertEqual(payload["counts"]["implementation_plan_entries"], 1)
        self.assertEqual(payload["counts"]["implementation_plan_files"], 2)

    def test_warns_for_draft_chinese_canonical_without_failing(self) -> None:
        root = self.make_root("impl-plan-warn")
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.zh-CN.md", self.structured_plan("示例"))
        self.write_file(
            root,
            "docs_bilingual/docs_registry.yaml",
            "version: 1\n"
            "documents:\n"
            "  - doc_id: sample_plan\n"
            "    doc_class: implementation_plan\n"
            "    status: draft\n"
            "    canonical_path: docs_bilingual/implementation_plans/sample_plan.zh-CN.md\n"
            "    zh_cn_path: docs_bilingual/implementation_plans/sample_plan.zh-CN.md\n",
        )

        result = self.run_check(root)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertIn("Warnings:", result.stdout)
        self.assertIn("still uses a Chinese file as canonical_path", result.stdout)

        json_result = self.run_check_json(root)
        self.assertEqual(json_result.returncode, 0, json_result.stdout + "\n" + json_result.stderr)
        payload = json.loads(json_result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["check_name"], "implementation_plan_rules")
        self.assertTrue(any("still uses a Chinese file as canonical_path" in warning for warning in payload["warnings"]))
        self.assertEqual(payload["counts"]["warnings"], 2)

    def test_fails_for_mojibake_or_replacement_markers_in_plan_pair(self) -> None:
        root = self.make_root("impl-plan-mojibake")
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.md", self.structured_plan())
        self.write_file(
            root,
            "docs_bilingual/implementation_plans/sample_plan.zh-CN.md",
            "# ??\n?????`field` ?????\nReplacement: \ufffd\n",
        )
        self.write_file(root, "docs_bilingual/docs_registry.yaml", self.registry())

        result = self.run_check(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contains mojibake or replacement-character marker", result.stdout)

        json_result = self.run_check_json(root)
        self.assertNotEqual(json_result.returncode, 0)
        payload = json.loads(json_result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("contains mojibake or replacement-character marker" in error for error in payload["errors"]))
        self.assertGreaterEqual(payload["counts"]["errors"], 1)

    def test_fails_when_comet_build_references_draft_plan(self) -> None:
        root = self.make_root("impl-plan-comet-draft")
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.md", self.structured_plan())
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.zh-CN.md", self.structured_plan("示例"))
        self.write_file(root, "docs_bilingual/docs_registry.yaml", self.registry("draft"))
        self.write_file(
            root,
            "openspec/changes/sample-change/.comet.yaml",
            "workflow: full\n"
            "phase: build\n"
            "plan: docs_bilingual/implementation_plans/sample_plan.md\n",
        )

        json_result = self.run_check_json(root)
        self.assertNotEqual(json_result.returncode, 0)
        payload = json.loads(json_result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("status must be active before implementation" in error for error in payload["errors"]))

    def test_fails_when_active_plan_missing_required_anchors(self) -> None:
        root = self.make_root("impl-plan-missing-anchors")
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.md", "# Sample\n")
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.zh-CN.md", self.structured_plan("示例"))
        self.write_file(root, "docs_bilingual/docs_registry.yaml", self.registry())

        json_result = self.run_check_json(root)
        self.assertNotEqual(json_result.returncode, 0)
        payload = json.loads(json_result.stdout)
        self.assertTrue(any("missing required stable update anchors" in error for error in payload["errors"]))

    def test_warns_for_large_plan_above_warning_threshold(self) -> None:
        root = self.make_root("impl-plan-warning")
        large = "A" * (41 * 1024)
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.md", self.structured_plan(extra=large))
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.zh-CN.md", self.structured_plan("示例"))
        self.write_file(root, "docs_bilingual/docs_registry.yaml", self.registry())

        json_result = self.run_check_json(root)
        self.assertEqual(json_result.returncode, 0, json_result.stdout + "\n" + json_result.stderr)
        payload = json.loads(json_result.stdout)
        self.assertTrue(any("exceeds warning threshold" in warning for warning in payload["warnings"]))

    def test_fails_for_large_plan_above_fail_threshold_without_baseline(self) -> None:
        root = self.make_root("impl-plan-too-large")
        large = "A" * (61 * 1024)
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.md", self.structured_plan(extra=large))
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.zh-CN.md", self.structured_plan("示例"))
        self.write_file(root, "docs_bilingual/docs_registry.yaml", self.registry())

        json_result = self.run_check_json(root)
        self.assertNotEqual(json_result.returncode, 0)
        payload = json.loads(json_result.stdout)
        self.assertTrue(any("exceeds fail threshold" in error for error in payload["errors"]))

    def test_fails_when_evidence_index_references_missing_report(self) -> None:
        root = self.make_root("impl-plan-missing-evidence")
        self.write_file(
            root,
            "docs_bilingual/implementation_plans/sample_plan.md",
            self.structured_plan(evidence_path="docs/superpowers/reports/missing.md"),
        )
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.zh-CN.md", self.structured_plan("示例"))
        self.write_file(root, "docs_bilingual/docs_registry.yaml", self.registry())

        json_result = self.run_check_json(root)
        self.assertNotEqual(json_result.returncode, 0)
        payload = json.loads(json_result.stdout)
        self.assertTrue(any("evidence index references missing path" in error for error in payload["errors"]))

    def test_fails_when_many_evidence_packages_lack_index(self) -> None:
        root = self.make_root("impl-plan-evidence-ledger")
        evidence_tail = "\n".join(
            f"## 2026-05-2{i} Runtime Evidence Package\n\n- [x] Evidence.\n" for i in range(4)
        )
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.md", "# Sample\n\n" + evidence_tail)
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.zh-CN.md", self.structured_plan("示例"))
        self.write_file(root, "docs_bilingual/docs_registry.yaml", self.registry())

        json_result = self.run_check_json(root)
        self.assertNotEqual(json_result.returncode, 0)
        payload = json.loads(json_result.stdout)
        self.assertTrue(any("dated evidence-package headings" in error for error in payload["errors"]))

    def active_plan_file(self, *, lang: str = "en", companion: bool = False) -> str:
        if companion:
            front_matter = (
                "---\n"
                "doc_id: sample_plan\n"
                "lang: zh-CN\n"
                "status: active\n"
                "doc_class: implementation_plan\n"
                "translation_of: docs_bilingual/implementation_plans/sample_plan.md\n"
                "---\n"
            )
            return front_matter + self.structured_plan("Sample zh")
        front_matter = (
            "---\n"
            "doc_id: sample_plan\n"
            f"lang: {lang}\n"
            "status: active\n"
            "doc_class: implementation_plan\n"
            "zh_cn_path: docs_bilingual/implementation_plans/sample_plan.zh-CN.md\n"
            "---\n"
        )
        return front_matter + self.structured_plan()

    def test_fails_when_active_plan_file_missing_registry_record(self) -> None:
        root = self.make_root("impl-plan-missing-registry")
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.md", self.active_plan_file())
        self.write_file(root, "docs_bilingual/docs_registry.yaml", "version: 1\ndocuments:\n")

        json_result = self.run_check_json(root)

        self.assertNotEqual(json_result.returncode, 0)
        payload = json.loads(json_result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("missing a docs_registry.yaml record" in error for error in payload["errors"]))
        self.assertTrue(any("\u4e2d\u6587\u63d0\u793a" in error for error in payload["errors"]))

    def test_fails_when_active_plan_file_registered_as_draft(self) -> None:
        root = self.make_root("impl-plan-status-mismatch")
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.md", self.active_plan_file())
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.zh-CN.md", self.active_plan_file(companion=True))
        self.write_file(root, "docs_bilingual/docs_registry.yaml", self.registry("draft"))

        json_result = self.run_check_json(root)

        self.assertNotEqual(json_result.returncode, 0)
        payload = json.loads(json_result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("registered with status `draft`; expected `active`" in error for error in payload["errors"]))


    def test_fails_when_registry_active_but_plan_front_matter_is_draft(self) -> None:
        root = self.make_root("impl-plan-registry-active-file-draft")
        draft_front_matter = (
            "---\n"
            "doc_id: sample_plan\n"
            "lang: en\n"
            "status: draft\n"
            "doc_class: implementation_plan\n"
            "zh_cn_path: docs_bilingual/implementation_plans/sample_plan.zh-CN.md\n"
            "---\n"
        )
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.md", draft_front_matter + self.structured_plan())
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.zh-CN.md", self.active_plan_file(companion=True))
        self.write_file(root, "docs_bilingual/docs_registry.yaml", self.registry("active"))

        json_result = self.run_check_json(root)

        self.assertNotEqual(json_result.returncode, 0)
        payload = json.loads(json_result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(
            any(
                "registry entry `sample_plan` is active" in error
                and "front matter status is `draft`; expected `active`" in error
                for error in payload["errors"]
            )
        )

    def test_fails_when_active_plan_missing_chinese_companion_file(self) -> None:
        root = self.make_root("impl-plan-missing-companion")
        self.write_file(root, "docs_bilingual/implementation_plans/sample_plan.md", self.structured_plan())
        self.write_file(root, "docs_bilingual/docs_registry.yaml", self.registry())

        json_result = self.run_check_json(root)

        self.assertNotEqual(json_result.returncode, 0)
        payload = json.loads(json_result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("zh_cn_path does not exist" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()
