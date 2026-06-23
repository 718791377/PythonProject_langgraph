import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "tools" / "check_embedded_codex_governance_alignment.py"
POLICY = Path("docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.md")
RUNTIME_PLAN = Path("docs_bilingual/implementation_plans/embedded_codex_governance_alignment_runtime_plan.md")
REGISTRY = Path("docs_bilingual/docs_registry.yaml")
CODEX_AGENT_GOVERNANCE = Path("docs_bilingual/operations_packages/codex_cli_durable_team/agent-governance.md")
CODEX_AGENT_TOOL_POLICY = Path("docs_bilingual/operations_packages/codex_cli_durable_team/agent-tool-policy.md")
CODEX_OFFER = Path("docs_bilingual/operations_packages/codex_cli_durable_team/offer.md")
OPC_ARCHITECTURE = Path("docs_bilingual/operations_packages/one_person_company/architecture.md")
OPC_THESIS = Path("docs_bilingual/operations_packages/one_person_company/thesis.md")
MANIFEST = Path("tools/ci/ci_test_manifest.json")
SAFETY_REGISTRY = Path("tools/safety_rule_script_backing_registry.json")
GUARD = Path("tools/run_openspec_guard.py")
GUARD_TEST = Path("test/run_openspec_guard_json.test.py")


class EmbeddedCodexGovernanceAlignmentTest(unittest.TestCase):
    maxDiff = None

    def run_python(self, args: list[str], root: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=root or REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def make_root(self) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"embedded-codex-alignment-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        shutil.copytree(REPO_ROOT / "tools", root / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(REPO_ROOT / "docs_bilingual", root / "docs_bilingual")
        shutil.copytree(REPO_ROOT / "test", root / "test", ignore=shutil.ignore_patterns("__pycache__"))
        return root

    def run_checker(self, root: Path) -> dict:
        result = self.run_python([str(CHECKER), "--root", str(root), "--json"])
        self.assertNotEqual(result.stdout, "", result.stderr)
        return {"returncode": result.returncode, "payload": json.loads(result.stdout), "raw": result.stdout + result.stderr}

    def assert_checker_fails_with(self, root: Path, expected: str) -> None:
        checked = self.run_checker(root)
        self.assertNotEqual(checked["returncode"], 0, checked["raw"])
        self.assertFalse(checked["payload"]["ok"])
        self.assertTrue(any(expected in error for error in checked["payload"]["errors"]), checked["payload"]["errors"])

    def test_current_repository_checker_passes(self) -> None:
        result = self.run_python([str(CHECKER), "--root", str(REPO_ROOT), "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["required_docs"], 11)
        self.assertEqual(payload["counts"]["shared_ledgers"], 11)
        self.assertEqual(payload["counts"]["semantic_mappings"], 17)
        self.assertEqual(payload["counts"]["codex_body_primaries"], 48)
        self.assertEqual(payload["counts"]["one_person_company_body_primaries"], 60)
        self.assertEqual(payload["counts"]["total_generated_files"], 216)

    def test_checker_fails_when_governance_anchor_is_missing(self) -> None:
        root = self.make_root()
        policy = root / POLICY
        text = policy.read_text(encoding="utf-8")
        policy.write_text(text.replace("business truth", "business boundary"), encoding="utf-8")
        self.assert_checker_fails_with(root, "business truth")

    def test_checker_fails_when_shared_ledger_field_is_missing(self) -> None:
        root = self.make_root()
        policy = root / POLICY
        text = policy.read_text(encoding="utf-8")
        policy.write_text(text.replace("truth_owner", "owner_marker"), encoding="utf-8")
        self.assert_checker_fails_with(root, "truth_owner")

    def test_checker_fails_on_legacy_physical_file(self) -> None:
        root = self.make_root()
        legacy = root / CODEX_AGENT_TOOL_POLICY
        legacy.write_text("legacy stale file\n", encoding="utf-8")
        self.assert_checker_fails_with(root, "Legacy generated physical file")

    def test_checker_fails_when_canonical_file_is_missing(self) -> None:
        root = self.make_root()
        (root / CODEX_AGENT_GOVERNANCE).unlink()
        self.assert_checker_fails_with(root, "Canonical package file is missing")

    def test_checker_fails_when_business_only_file_appears_under_codex(self) -> None:
        root = self.make_root()
        target = root / CODEX_OFFER
        target.write_text("business-only offer should not be in Codex package\n", encoding="utf-8")
        self.assert_checker_fails_with(root, "Business-only truth file appears under Codex package")

    def test_checker_fails_when_codex_only_file_appears_under_one_person_company(self) -> None:
        root = self.make_root()
        target = root / OPC_ARCHITECTURE
        target.write_text("Codex-only architecture should not be in one-person-company package\n", encoding="utf-8")
        self.assert_checker_fails_with(root, "Codex-only truth file appears under one-person-company package")

    def test_checker_fails_when_registry_lacks_runtime_plan(self) -> None:
        root = self.make_root()
        registry = root / REGISTRY
        lines = registry.read_text(encoding="utf-8").splitlines()
        output: list[str] = []
        skip = False
        for line in lines:
            if line.strip() == "- doc_id: embedded_codex_governance_alignment_runtime_plan":
                skip = True
                continue
            if skip and line.startswith("  - doc_id: "):
                skip = False
            if not skip:
                output.append(line)
        registry.write_text("\n".join(output) + "\n", encoding="utf-8")
        self.assert_checker_fails_with(root, "embedded_codex_governance_alignment_runtime_plan")

    def test_checker_fails_when_registry_contains_legacy_path(self) -> None:
        root = self.make_root()
        registry = root / REGISTRY
        registry.write_text(
            registry.read_text(encoding="utf-8")
            + "\n  - doc_id: stale_agent_tool_policy\n"
            + "    doc_class: operations_package\n"
            + "    status: active\n"
            + "    canonical_path: docs_bilingual/operations_packages/codex_cli_durable_team/agent-tool-policy.md\n"
            + "    zh_cn_path: docs_bilingual/operations_packages/codex_cli_durable_team/agent-tool-policy.zh-CN.md\n",
            encoding="utf-8",
        )
        self.assert_checker_fails_with(root, "agent-tool-policy.md")

    def test_checker_fails_when_stage_b_registration_is_missing(self) -> None:
        root = self.make_root()
        manifest = root / MANIFEST
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["python_unittest"] = [item for item in data["python_unittest"] if item != "check_embedded_codex_governance_alignment.test.py"]
        manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.assert_checker_fails_with(root, "does not register `check_embedded_codex_governance_alignment.test.py`")

    def test_checker_fails_when_runtime_plan_stops_linking_boundary(self) -> None:
        root = self.make_root()
        plan = root / RUNTIME_PLAN
        text = plan.read_text(encoding="utf-8")
        plan.write_text(text.replace("docs_bilingual/governance/one_person_company_embedded_codex_governance_policy.md", "docs_bilingual/governance/other.md"), encoding="utf-8")
        self.assert_checker_fails_with(root, "embedded governance policy boundary")

    def test_checker_fails_when_safety_or_guard_registration_is_missing(self) -> None:
        root = self.make_root()
        safety = root / SAFETY_REGISTRY
        safety.write_text(safety.read_text(encoding="utf-8").replace("tools/check_embedded_codex_governance_alignment.py", "tools/check_other.py"), encoding="utf-8")
        self.assert_checker_fails_with(root, "does not register checker `tools/check_embedded_codex_governance_alignment.py`")

        root_guard = self.make_root()
        guard = root_guard / GUARD
        guard.write_text(
            guard.read_text(encoding="utf-8").replace(
                'embedded_codex_governance_alignment_script = root / "tools" / "check_embedded_codex_governance_alignment.py"',
                'embedded_codex_governance_alignment_script = root / "tools" / "check_other_alignment.py"',
            ),
            encoding="utf-8",
        )
        self.assert_checker_fails_with(root_guard, "does not declare `tools/check_embedded_codex_governance_alignment.py`")

        root2 = self.make_root()
        guard_test = root2 / GUARD_TEST
        guard_test.write_text(guard_test.read_text(encoding="utf-8").replace("check_embedded_codex_governance_alignment", "check_other_alignment"), encoding="utf-8")
        self.assert_checker_fails_with(root2, "does not mirror guard step `check_embedded_codex_governance_alignment`")


if __name__ == "__main__":
    unittest.main()
