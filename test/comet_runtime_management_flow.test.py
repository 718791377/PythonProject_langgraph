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


def legacy_mojibake(label: str, encoding: str = "gbk") -> str:
    return label.encode("utf-8").decode(encoding, errors="replace")


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
        self.assertIn("management_record must be recorded", text)
        self.assertIn('[ -z "$management_record" ] || [ "$management_record" = "null" ]', text)

    def test_validator_declares_exact_managed_enum_contracts(self) -> None:
        text = read(VALIDATE_SCRIPT)

        expected_contracts = {
            "workflow": "full hotfix tweak",
            "phase": "open design build verify archive",
            "build_mode": "subagent-driven-development executing-plans direct",
            "isolation": "branch worktree",
            "verify_mode": "light full",
            "verify_result": "pending pass fail",
            "branch_status": "pending handled",
            "archived": "true false",
            "direct_override": "true false",
            "monitoring_status": "clear needs_decision blocked",
            "control_decision": "continue adjust-current return-open return-design return-build return-verify stop",
            "target_phase": "null open design build verify",
            "rework_reason": "null scope-gap planning-gap execution-gap verification-gap value-gap risk-change stakeholder-change",
        }

        for field, valid_values in expected_contracts.items():
            self.assertIn(f'validate_enum "{field}"', text)
            self.assertIn(f'"{valid_values}"', text)

        self.assertIn('fail "$field=\'$value\' is not valid. Expected: $valid_values"', text)

    def test_validator_declares_artifact_path_checks_and_unknown_key_warnings(self) -> None:
        text = read(VALIDATE_SCRIPT)

        for field in ["design_doc", "plan", "verification_report", "management_record"]:
            self.assertIn(f"{field}='$", text)
            self.assertIn(f"{field}='${field}' does not exist on disk", text)

        self.assertIn('KNOWN_KEYS="workflow phase design_doc plan build_mode isolation verify_mode verify_result verification_report branch_status verified_at archived direct_override build_command verify_command management_record monitoring_status control_decision target_phase rework_reason iteration_count"', text)
        self.assertIn('warn_msg "unknown field \'$key\' found"', text)
        self.assertIn("WARNINGS=$((WARNINGS + 1))", text)

    def test_validator_declares_artifact_path_safety_checks(self) -> None:
        text = read(VALIDATE_SCRIPT)

        self.assertIn("validate_artifact_path_safety()", text)
        self.assertIn("must be a repository-relative path", text)
        self.assertIn("must not contain path traversal segments", text)
        self.assertIn('[[ "$path" =~ ^[A-Za-z]: ]]', text)
        self.assertIn('[[ "$path" == ".." || "$path" == ../* || "$path" == */../* || "$path" == */.. ]]', text)
        for field in ["design_doc", "plan", "verification_report", "management_record"]:
            self.assertIn(f'validate_artifact_path_safety "{field}" "${field}"', text)

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

    def test_guard_and_archive_accept_legacy_mojibake_management_labels(self) -> None:
        guard_text = read(GUARD_SCRIPT)
        archive_text = read(ARCHIVE_SCRIPT)

        for text in [guard_text, archive_text]:
            self.assertIn("checklist_done_legacy_mojibake()", text)
            self.assertIn('("gbk", "cp936", "gb18030", "cp1252")', text)
            self.assertIn('decoded.replace("\\ufffd", "?")', text)

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

    def test_guard_declares_required_checklist_items_for_every_forward_phase(self) -> None:
        text = read(GUARD_SCRIPT)

        required_phase_items = [
            ("open", "Open / Initiating", "Value and why are stated.", "价值/Why 已说明"),
            ("open", "Open / Initiating", "Success criteria are measurable.", "成功标准已说明"),
            (
                "open",
                "Open / Initiating",
                "Stakeholders, constraints, or operating boundaries are identified.",
                "stakeholders 或 constraints 已识别",
            ),
            (
                "design",
                "Design / Planning",
                "Delivery approach is tailored: predictive, agile, or hybrid.",
                "交付方式已裁剪",
            ),
            ("design", "Design / Planning", "Major risks and assumptions are recorded.", "风险与关键假设已记录"),
            ("design", "Design / Planning", "Acceptance evidence path is defined.", "验收证据路径已定义"),
            ("build", "Build / Executing", "Execution mode is selected.", "execution mode 已选择"),
            (
                "build",
                "Build / Executing",
                "Quality evidence is recorded: TDD, review, test, or equivalent.",
                "TDD / review / quality evidence 已记录",
            ),
            (
                "build",
                "Build / Executing",
                "Blockers are cleared or have an explicit decision.",
                "当前阻塞项已清空或已有处理决策",
            ),
            (
                "verify",
                "Verify / Controlling",
                "Variance from scope, design, and acceptance criteria is checked.",
                "偏差检查完成",
            ),
            ("verify", "Verify / Controlling", "Risk and change impact are assessed.", "风险/变更影响已评估"),
            ("verify", "Verify / Controlling", "Control decision is recorded.", "control decision 已记录"),
            ("archive", "Archive / Closing", "Value outcome is summarized.", "价值结果已总结"),
            (
                "archive",
                "Archive / Closing",
                "Lessons learned or reusable guidance are recorded.",
                "经验沉淀已记录",
            ),
            (
                "archive",
                "Archive / Closing",
                "Delta spec sync, verification evidence, and archive path are confirmed.",
                "delta spec sync / verification evidence / archive path 已确认",
            ),
        ]

        for phase, section, english_item, chinese_item in required_phase_items:
            self.assertIn(f'checklist_done_named "{section}" "{english_item}"', text)
            self.assertIn(f'"{chinese_item}"', text)
            self.assertIn(f'"{english_item}"', text)
            self.assertIn(f'management_phase_complete {phase}', text)

        required_monitoring_items = [
            ("Monitoring Loop", "Current facts are checked.", "当前阶段事实已检查"),
            ("Monitoring Loop", "Continue, adjust, stop, or return decision is made.", "是否需要回退已判断"),
        ]
        for section, english_item, chinese_item in required_monitoring_items:
            self.assertIn(f'checklist_done_named "{section}" "{english_item}"', text)
            self.assertIn(f'"{chinese_item}"', text)
            self.assertIn(f'"{english_item}"', text)

        for phase_name in ["Open", "Design", "Build", "Verify", "Archive"]:
            self.assertIn(f'check "{phase_name} management checklist complete"', text)
        self.assertEqual(text.count('check "Monitoring allows forward progress" monitoring_allows_forward'), 5)

    def test_state_script_keeps_monitor_return_events_outside_forward_gate_checks(self) -> None:
        text = read(STATE_SCRIPT)

        for event, target, decision in [
            ("monitor-return-open", "open", "return-open"),
            ("monitor-return-design", "design", "return-design"),
            ("monitor-return-build", "build", "return-build"),
            ("monitor-return-verify", "verify", "return-verify"),
        ]:
            match = re.search(rf"{re.escape(event)}\)(?P<body>.*?)\s+;;", text, flags=re.DOTALL)
            self.assertIsNotNone(match, f"missing transition case for {event}")
            body = match.group("body")
            self.assertIn(f'apply_monitor_return "$change_name" "{target}" "{decision}"', body)
            self.assertNotIn("require_forward_monitoring_clear", body)

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

    def run_bash(
        self,
        root: Path,
        script: str,
        *args: str,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        run_env = None
        if env is not None:
            import os

            run_env = os.environ.copy()
            run_env.update(env)
        return subprocess.run(
            ["bash", str(root / ".codex" / "skills" / "comet" / "scripts" / script), *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=run_env,
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

    def test_validator_rejects_null_management_record(self) -> None:
        with self.make_root() as temp:
            root = Path(temp)
            self.write_minimal_change(root, "demo")
            self.run_bash(root, "comet-state.sh", "init", "demo", "full")
            self.set_yaml_field_directly(root, "demo", "management_record", "null")

            result = self.run_bash(root, "comet-yaml-validate.sh", "demo")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("management_record must be recorded", result.stderr)

    def test_validator_rejects_empty_management_record(self) -> None:
        with self.make_root() as temp:
            root = Path(temp)
            self.write_minimal_change(root, "demo")
            self.run_bash(root, "comet-state.sh", "init", "demo", "full")
            self.set_yaml_field_directly(root, "demo", "management_record", "")

            result = self.run_bash(root, "comet-yaml-validate.sh", "demo")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("management_record must be recorded", result.stderr)

    def test_validator_rejects_missing_management_record_file(self) -> None:
        with self.make_root() as temp:
            root = Path(temp)
            self.write_minimal_change(root, "demo")
            self.run_bash(root, "comet-state.sh", "init", "demo", "full")
            missing = "openspec/changes/demo/missing-management.md"
            self.set_yaml_field_directly(root, "demo", "management_record", missing)

            result = self.run_bash(root, "comet-yaml-validate.sh", "demo")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f"management_record='{missing}' does not exist on disk", result.stderr)

    def test_guard_rejects_unchecked_open_management_checklist(self) -> None:
        with self.make_root() as temp:
            root = Path(temp)
            self.write_minimal_change(root, "demo")
            self.run_bash(root, "comet-state.sh", "init", "demo", "full")

            result = self.run_bash(root, "comet-guard.sh", "demo", "open")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing management checklist section: Open / Initiating", result.stderr)
            self.assertIn("Missing management checklist item: Value and why are stated.", result.stderr)
            self.assertIn("Missing management checklist section: Monitoring Loop", result.stderr)
            self.assertIn("Missing management checklist item: Current facts are checked.", result.stderr)

    def test_guard_rejects_unchecked_management_checklists_for_all_forward_phases(self) -> None:
        cases = [
            ("design", "Design / Planning", "Delivery approach is tailored: predictive, agile, or hybrid."),
            ("build", "Build / Executing", "Execution mode is selected."),
            ("verify", "Verify / Controlling", "Variance from scope, design, and acceptance criteria is checked."),
            ("archive", "Archive / Closing", "Value outcome is summarized."),
        ]

        for phase, section, first_item in cases:
            with self.subTest(phase=phase):
                with self.make_root() as temp:
                    root = Path(temp)
                    self.write_minimal_change(root, "demo")
                    self.run_bash(root, "comet-state.sh", "init", "demo", "full")
                    self.run_bash(root, "comet-state.sh", "set", "demo", "phase", phase)
                    self.run_bash(root, "comet-state.sh", "set", "demo", "isolation", "worktree")
                    self.run_bash(root, "comet-state.sh", "set", "demo", "build_mode", "executing-plans")
                    report = root / "openspec" / "changes" / "demo" / "verification.md"
                    report.write_text("# Verification\n", encoding="utf-8")
                    self.run_bash(
                        root,
                        "comet-state.sh",
                        "set",
                        "demo",
                        "verification_report",
                        "openspec/changes/demo/verification.md",
                    )
                    self.run_bash(root, "comet-state.sh", "set", "demo", "branch_status", "handled")
                    self.run_bash(root, "comet-state.sh", "set", "demo", "archived", "true")

                    result = self.run_bash(root, "comet-guard.sh", "demo", phase, env={"COMET_SKIP_BUILD": "1"})

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(f"Missing management checklist section: {section}", result.stderr)
                    self.assertIn(f"Missing management checklist item: {first_item}", result.stderr)

    def test_guard_rejects_missing_monitoring_checklist_after_phase_items_complete(self) -> None:
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
                        "- [ ] Current facts are checked.",
                        "- [ ] Continue, adjust, stop, or return decision is made.",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = self.run_bash(root, "comet-guard.sh", "demo", "open")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing management checklist section: Monitoring Loop", result.stderr)
            self.assertIn("Missing management checklist item: Current facts are checked.", result.stderr)

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

    def test_guard_accepts_legacy_mojibake_management_template_for_open_gate(self) -> None:
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
                        f"- [x] {legacy_mojibake('价值/Why 已说明')}",
                        f"- [x] {legacy_mojibake('成功标准已说明')}",
                        f"- [x] {legacy_mojibake('stakeholders 或 constraints 已识别')}",
                        "",
                        "## Monitoring Loop",
                        f"- [x] {legacy_mojibake('当前阶段事实已检查')}",
                        f"- [x] {legacy_mojibake('是否需要回退已判断')}",
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
