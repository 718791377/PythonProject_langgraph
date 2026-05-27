from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_SCRIPT = REPO_ROOT / ".codex" / "skills" / "comet" / "scripts" / "comet-state.sh"
GUARD_SCRIPT = REPO_ROOT / ".codex" / "skills" / "comet" / "scripts" / "comet-guard.sh"
VALIDATE_SCRIPT = REPO_ROOT / ".codex" / "skills" / "comet" / "scripts" / "comet-yaml-validate.sh"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class CometRuntimeManagementStaticTests(unittest.TestCase):
    maxDiff = None

    def test_validator_declares_required_runtime_fields_and_return_invariants(self) -> None:
        text = read(VALIDATE_SCRIPT)

        required_line = next(line for line in text.splitlines() if line.startswith("REQUIRED_FIELDS="))
        self.assertIn("verification_report", required_line)
        self.assertIn("branch_status", required_line)
        self.assertIn("return decision requires target_phase and rework_reason", text)
        self.assertIn("return-open", text)
        self.assertIn("target_phase must be open", text)
        self.assertIn("return-design", text)
        self.assertIn("target_phase must be design", text)
        self.assertIn("return-build", text)
        self.assertIn("target_phase must be build", text)
        self.assertIn("return-verify", text)
        self.assertIn("target_phase must be verify", text)

    def test_guard_accepts_english_and_chinese_management_checklist_labels(self) -> None:
        text = read(GUARD_SCRIPT)

        for required in [
            "价值/Why 已说明",
            "Value and why are stated.",
            "成功标准已说明",
            "Success criteria are measurable.",
            "交付方式已裁剪",
            "Delivery approach is tailored: predictive, agile, or hybrid.",
            "当前阶段事实已检查",
            "Current facts are checked.",
        ]:
            self.assertIn(required, text)


@unittest.skipIf(shutil.which("bash") is None, "bash is not available on this platform")
class CometRuntimeManagementBehaviorTests(unittest.TestCase):
    def make_root(self) -> tempfile.TemporaryDirectory[str]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        scripts = root / ".codex" / "skills" / "comet" / "scripts"
        scripts.mkdir(parents=True)
        for source in [STATE_SCRIPT, GUARD_SCRIPT, VALIDATE_SCRIPT]:
            shutil.copy2(source, scripts / source.name)
        return temp

    def run_bash(self, root: Path, script: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(root / ".codex" / "skills" / "comet" / "scripts" / script), *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def write_minimal_change(self, root: Path, name: str) -> Path:
        change = root / "openspec" / "changes" / name
        change.mkdir(parents=True)
        (change / "proposal.md").write_text("# Proposal\n", encoding="utf-8")
        (change / "design.md").write_text("# Design\n", encoding="utf-8")
        (change / "tasks.md").write_text("- [x] Done\n", encoding="utf-8")
        return change

    def test_init_creates_management_record_and_required_runtime_fields(self) -> None:
        with self.make_root() as temp:
            root = Path(temp)
            self.write_minimal_change(root, "demo")

            result = self.run_bash(root, "comet-state.sh", "init", "demo", "full")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            yaml_text = (root / "openspec" / "changes" / "demo" / ".comet.yaml").read_text(encoding="utf-8")
            for expected in [
                "management_record: openspec/changes/demo/management.md",
                "monitoring_status: clear",
                "control_decision: continue",
                "target_phase: null",
                "rework_reason: null",
                "iteration_count: 0",
            ]:
                self.assertIn(expected, yaml_text)
            self.assertTrue((root / "openspec" / "changes" / "demo" / "management.md").exists())

    def test_validator_rejects_return_decision_without_target_and_reason(self) -> None:
        with self.make_root() as temp:
            root = Path(temp)
            self.write_minimal_change(root, "demo")
            self.run_bash(root, "comet-state.sh", "init", "demo", "full")
            yaml_path = root / "openspec" / "changes" / "demo" / ".comet.yaml"
            yaml_path.write_text(
                yaml_path.read_text(encoding="utf-8")
                .replace("control_decision: continue", "control_decision: return-design"),
                encoding="utf-8",
            )

            result = self.run_bash(root, "comet-yaml-validate.sh", "demo")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("return decision requires target_phase and rework_reason", result.stderr)

    def test_monitor_return_preserves_target_reason_and_increments_iteration(self) -> None:
        with self.make_root() as temp:
            root = Path(temp)
            self.write_minimal_change(root, "demo")
            self.run_bash(root, "comet-state.sh", "init", "demo", "full")
            for field, value in [
                ("phase", "build"),
                ("control_decision", "return-design"),
                ("target_phase", "design"),
                ("rework_reason", "planning-gap"),
            ]:
                self.assertEqual(self.run_bash(root, "comet-state.sh", "set", "demo", field, value).returncode, 0)

            result = self.run_bash(root, "comet-state.sh", "transition", "demo", "monitor-return-design")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            yaml_text = (root / "openspec" / "changes" / "demo" / ".comet.yaml").read_text(encoding="utf-8")
            self.assertIn("phase: design", yaml_text)
            self.assertIn("target_phase: design", yaml_text)
            self.assertIn("rework_reason: planning-gap", yaml_text)
            self.assertIn("iteration_count: 1", yaml_text)

    def test_guard_accepts_english_management_template_for_open_gate(self) -> None:
        with self.make_root() as temp:
            root = Path(temp)
            change = self.write_minimal_change(root, "demo")
            self.run_bash(root, "comet-state.sh", "init", "demo", "full")
            (change / "management.md").write_text(
                "\n".join(
                    [
                        "# Comet Management Record",
                        "",
                        "## Open / Initiating",
                        "- [x] Value and why are stated.",
                        "- [x] Success criteria are measurable.",
                        "- [x] Stakeholders, constraints, or operating boundaries are identified.",
                        "",
                        "## Monitoring Loop",
                        "- [x] Current facts are checked.",
                        "- [x] Continue, adjust, stop, or return decision is made.",
                        "- [ ] If returning, target_phase and rework_reason are recorded.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = self.run_bash(root, "comet-guard.sh", "demo", "open")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
