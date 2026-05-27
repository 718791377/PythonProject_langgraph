from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_SCRIPT = REPO_ROOT / ".codex" / "skills" / "comet" / "scripts" / "comet-state.sh"
GUARD_SCRIPT = REPO_ROOT / ".codex" / "skills" / "comet" / "scripts" / "comet-guard.sh"
VALIDATE_SCRIPT = REPO_ROOT / ".codex" / "skills" / "comet" / "scripts" / "comet-yaml-validate.sh"
ARCHIVE_SCRIPT = REPO_ROOT / ".codex" / "skills" / "comet" / "scripts" / "comet-archive.sh"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class CometRuntimeManagementStaticTests(unittest.TestCase):
    maxDiff = None

    def test_state_bootstrap_template_contains_management_record_sections(self) -> None:
        text = read(STATE_SCRIPT)

        for required in [
            "# Comet Management Record",
            "## Open / Initiating",
            "## Design / Planning",
            "## Build / Executing",
            "## Verify / Controlling",
            "## Archive / Closing",
            "## Monitoring Loop",
            "- [ ] 价值/Why 已说明",
            "- [ ] 成功标准已说明",
            "- [ ] stakeholders 或 constraints 已识别",
            "- [ ] 交付方式已裁剪",
            "- [ ] 风险与关键假设已记录",
            "- [ ] 验收证据路径已定义",
            "- [ ] execution mode 已选择",
            "- [ ] TDD / review / quality evidence 已记录",
            "- [ ] 当前阻塞项已清空或已有处理决策",
            "- [ ] 偏差检查完成",
            "- [ ] 风险/变更影响已评估",
            "- [ ] control decision 已记录",
            "- [ ] 价值结果已总结",
            "- [ ] 经验沉淀已记录",
            "- [ ] delta spec sync / verification evidence / archive path 已确认",
            "- [ ] 当前阶段事实已检查",
            "- [ ] 是否需要回退已判断",
            "- [ ] 若需回退，target_phase 与 rework_reason 已记录",
        ]:
            self.assertIn(required, text)

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

    def test_state_script_requires_monitoring_clear_for_forward_transitions(self) -> None:
        text = read(STATE_SCRIPT)

        self.assertIn("require_forward_monitoring_clear()", text)
        self.assertIn("monitoring_status must be 'clear'", text)
        self.assertIn("control_decision must be 'continue'", text)

        for event in ["open-complete", "design-complete", "build-complete", "verify-pass", "archived"]:
            pattern = rf"{re.escape(event)}\)\n\s+require_phase \"\$change_name\" .+?\n\s+require_forward_monitoring_clear \"\$change_name\" \"\$event\""
            self.assertRegex(text, pattern)

    def test_state_script_maps_all_monitor_return_events_to_target_phases(self) -> None:
        text = read(STATE_SCRIPT)

        for event, target, decision in [
            ("monitor-return-open", "open", "return-open"),
            ("monitor-return-design", "design", "return-design"),
            ("monitor-return-build", "build", "return-build"),
            ("monitor-return-verify", "verify", "return-verify"),
        ]:
            self.assertIn(f'{event})', text)
            self.assertIn(f'apply_monitor_return "$change_name" "{target}" "{decision}"', text)

    def test_guard_reports_missing_section_and_item_for_management_gates(self) -> None:
        text = read(GUARD_SCRIPT)

        self.assertIn("checklist_done_named()", text)
        self.assertIn("Missing management checklist section:", text)
        self.assertIn("Missing management checklist item:", text)
        self.assertIn('"Open / Initiating" "Value and why are stated."', text)
        self.assertIn('"Monitoring Loop" "Current facts are checked."', text)

    def test_archive_accepts_english_and_chinese_closing_and_monitoring_labels(self) -> None:
        text = read(ARCHIVE_SCRIPT)

        self.assertIn("checklist_done_any()", text)
        for required in [
            "Value outcome is summarized.",
            "Lessons learned or reusable guidance are recorded.",
            "Delta spec sync, verification evidence, and archive path are confirmed.",
            "Current facts are checked.",
            "Continue, adjust, stop, or return decision is made.",
            "价值结果已总结",
            "经验沉淀已记录",
        ]:
            self.assertIn(required, text)

    def test_guard_blocks_non_continue_monitoring_decisions(self) -> None:
        text = read(GUARD_SCRIPT)

        for required in [
            "monitoring_status=needs_decision; record control_decision before moving forward",
            "monitoring_status=blocked; resolve or use a monitor-return-* transition",
            "control_decision=adjust-current; update current phase evidence, then set control_decision=continue",
            "control_decision=stop; forward transition is intentionally blocked",
            "return decision requires target_phase and rework_reason",
            "control_decision=$decision requires: bash",
            "$COMET_STATE",
            "transition $CHANGE monitor-${decision}",
        ]:
            self.assertIn(required, text)

    def test_archive_requires_final_monitoring_clearance(self) -> None:
        text = read(ARCHIVE_SCRIPT)

        for required in [
            'MONITORING_STATUS=$(yaml_field "monitoring_status")',
            'CONTROL_DECISION=$(yaml_field "control_decision")',
            "expected 'clear' before archive",
            "expected 'continue' before archive",
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

    def set_yaml_field_directly(self, root: Path, name: str, field: str, value: str) -> None:
        yaml_path = root / "openspec" / "changes" / name / ".comet.yaml"
        lines = yaml_path.read_text(encoding="utf-8").splitlines()
        updated = []
        found = False
        for line in lines:
            if line.startswith(f"{field}:"):
                updated.append(f"{field}: {value}")
                found = True
            else:
                updated.append(line)
        if not found:
            updated.append(f"{field}: {value}")
        yaml_path.write_text("\n".join(updated) + "\n", encoding="utf-8")

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
            management_text = (root / "openspec" / "changes" / "demo" / "management.md").read_text(encoding="utf-8")
            self.assertIn("- [ ] 价值/Why 已说明", management_text)
            self.assertIn("- [ ] 是否需要回退已判断", management_text)

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

    def test_monitor_return_supports_all_targets_and_repeated_iterations(self) -> None:
        with self.make_root() as temp:
            root = Path(temp)
            self.write_minimal_change(root, "demo")
            self.run_bash(root, "comet-state.sh", "init", "demo", "full")

            cases = [
                ("monitor-return-open", "return-open", "open", "scope-gap", "1"),
                ("monitor-return-design", "return-design", "design", "planning-gap", "2"),
                ("monitor-return-build", "return-build", "build", "execution-gap", "3"),
                ("monitor-return-verify", "return-verify", "verify", "verification-gap", "4"),
            ]

            for event, decision, target, reason, expected_count in cases:
                for field, value in [
                    ("control_decision", decision),
                    ("target_phase", target),
                    ("rework_reason", reason),
                ]:
                    self.assertEqual(self.run_bash(root, "comet-state.sh", "set", "demo", field, value).returncode, 0)

                result = self.run_bash(root, "comet-state.sh", "transition", "demo", event)

                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                yaml_text = (root / "openspec" / "changes" / "demo" / ".comet.yaml").read_text(encoding="utf-8")
                self.assertIn(f"phase: {target}", yaml_text)
                self.assertIn(f"target_phase: {target}", yaml_text)
                self.assertIn(f"rework_reason: {reason}", yaml_text)
                self.assertIn(f"iteration_count: {expected_count}", yaml_text)
                self.assertIn("control_decision: continue", yaml_text)

    def test_monitor_return_rejects_mismatched_decision_target_and_missing_reason(self) -> None:
        with self.make_root() as temp:
            root = Path(temp)
            self.write_minimal_change(root, "demo")
            self.run_bash(root, "comet-state.sh", "init", "demo", "full")

            for field, value in [
                ("control_decision", "return-open"),
                ("target_phase", "design"),
                ("rework_reason", "planning-gap"),
            ]:
                self.assertEqual(self.run_bash(root, "comet-state.sh", "set", "demo", field, value).returncode, 0)
            result = self.run_bash(root, "comet-state.sh", "transition", "demo", "monitor-return-design")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("control_decision must be 'return-design'", result.stderr)

            for field, value in [
                ("control_decision", "return-design"),
                ("target_phase", "build"),
                ("rework_reason", "planning-gap"),
            ]:
                self.assertEqual(self.run_bash(root, "comet-state.sh", "set", "demo", field, value).returncode, 0)
            result = self.run_bash(root, "comet-state.sh", "transition", "demo", "monitor-return-design")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("target_phase must be 'design'", result.stderr)

            for field, value in [
                ("control_decision", "return-design"),
                ("target_phase", "design"),
                ("rework_reason", "null"),
            ]:
                self.assertEqual(self.run_bash(root, "comet-state.sh", "set", "demo", field, value).returncode, 0)
            result = self.run_bash(root, "comet-state.sh", "transition", "demo", "monitor-return-design")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("rework_reason must be recorded", result.stderr)

    def test_validator_rejects_non_numeric_iteration_count(self) -> None:
        with self.make_root() as temp:
            root = Path(temp)
            self.write_minimal_change(root, "demo")
            self.run_bash(root, "comet-state.sh", "init", "demo", "full")
            self.set_yaml_field_directly(root, "demo", "iteration_count", "not-a-number")

            result = self.run_bash(root, "comet-yaml-validate.sh", "demo")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("iteration_count='not-a-number' is not a non-negative integer", result.stderr)

    def test_guard_rejects_unchecked_open_management_checklist(self) -> None:
        with self.make_root() as temp:
            root = Path(temp)
            self.write_minimal_change(root, "demo")
            self.run_bash(root, "comet-state.sh", "init", "demo", "full")

            result = self.run_bash(root, "comet-guard.sh", "demo", "open")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing management checklist section: Open / Initiating", result.stderr)
            self.assertIn("Missing management checklist item: Value and why are stated.", result.stderr)

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
