from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLCHAIN_SRC = REPO_ROOT / "tools" / "project_moe_gui_toolchain" / "src"
sys.path.insert(0, str(TOOLCHAIN_SRC))
INSTALLER = REPO_ROOT / "tools" / "project_moe_gui_toolchain" / "install_project_moe_gui.py"
CHECKER = REPO_ROOT / "tools" / "project_moe_gui_toolchain" / "check_project_moe_gui_install.py"
UPDATER = REPO_ROOT / "tools" / "project_moe_gui_toolchain" / "update_project_moe_gui.py"


class ProjectMoeGuiToolchainTests(unittest.TestCase):
    def run_tool(self, *args: str, expect_success: bool | None = True) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = subprocess.run(
            [sys.executable, *args, "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        try:
            payload = json.loads(result.stdout)
        except Exception as exc:  # pragma: no cover
            self.fail(f"tool did not emit JSON: {exc}\nstdout={result.stdout}\nstderr={result.stderr}")
        if expect_success is True:
            self.assertEqual(result.returncode, 0, payload)
            self.assertTrue(payload.get("ok"), payload)
        elif expect_success is False:
            self.assertNotEqual(result.returncode, 0, payload)
            self.assertFalse(payload.get("ok"), payload)
        return result, payload

    def make_project(self, root: Path, *, with_agent: bool = True) -> None:
        (root / ".git").mkdir()
        (root / ".codex" / "agents").mkdir(parents=True)
        (root / "tools").mkdir()
        if with_agent:
            (root / ".codex" / "agents" / "thesis-moe-mentor.toml").write_text(
                'name = "thesis-moe-mentor"\n'
                'description = "Strict thesis mentor."\n'
                'developer_instructions = "Use strict thesis mentor rules."\n',
                encoding="utf-8",
            )
        (root / "tools" / "thesis_moe_mode.py").write_text(
            """
from __future__ import annotations
import json
import sys
cmd = sys.argv[1]
payload = {
    "schema_version": 1,
    "command": cmd,
    "ok": True,
    "token": "ok",
    "cli_contract": "project-moe-cli-v1",
    "sessions": [],
    "counts": {"total": 0, "valid": 0},
}
if cmd == "list-sessions":
    payload["message"] = "session list read"
    payload["sessions"] = [
        {"session_id": "session-1234567890abcdef", "enabled": False, "effective_enabled": False, "valid": True, "token": "ok", "source": "manual-session"}
    ]
elif cmd == "project-status":
    payload["message"] = "project status read"
    payload["project_default_enabled"] = False
    payload["git_branch"] = "main"
elif cmd == "status":
    payload["message"] = "mentor mode disabled"
    payload["effective_enabled"] = False
elif cmd == "project-on":
    payload["message"] = "project default enabled"
    payload["project_default_enabled"] = True
elif cmd == "project-off":
    payload["message"] = "project default disabled"
    payload["project_default_enabled"] = False
elif cmd == "on":
    payload["message"] = "session enabled"
    payload["effective_enabled"] = True
elif cmd == "off":
    payload["message"] = "session disabled"
    payload["effective_enabled"] = False
else:
    payload = {"ok": False, "token": "unsupported"}
print(json.dumps(payload))
""".lstrip(),
            encoding="utf-8",
        )

    def test_install_dry_run_does_not_write_target_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project)
            _, payload = self.run_tool(
                str(INSTALLER),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
                "--dry-run",
            )
            self.assertEqual(payload["mode"], "dry-run")
            self.assertTrue(payload["planned_writes"])
            self.assertFalse((project / "tools" / "project_moe_gui" / "launcher.py").exists())
            self.assertFalse((project / "project-moe-gui.cmd").exists())

    def test_install_apply_writes_manifest_and_check_up_to_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project)
            _, install_payload = self.run_tool(
                str(INSTALLER),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
            )
            self.assertEqual(install_payload["mode"], "apply")
            self.assertTrue((project / "tools" / "project_moe_gui" / "project_moe_gui.install-manifest.json").exists())
            self.assertTrue((project / "tools" / "project_moe_gui" / "project_moe_gui.config.json").exists())
            self.assertTrue((project / "project-moe-gui.cmd").exists())

            _, check_payload = self.run_tool(str(CHECKER), "--target-project", str(project), "--skip-runtime-import")
            self.assertEqual(check_payload["status"], "up_to_date")
            self.assertEqual(check_payload["runtime_status"], "skipped_by_flag")

    def test_install_fails_without_agent_toml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project, with_agent=False)
            _, payload = self.run_tool(
                str(INSTALLER),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
                "--dry-run",
                expect_success=False,
            )
            self.assertEqual(payload["token"], "blocked:missing_agent_toml")

    def test_check_detects_managed_file_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project)
            self.run_tool(
                str(INSTALLER),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
            )
            launcher = project / "tools" / "project_moe_gui" / "launcher.py"
            launcher.write_text(launcher.read_text(encoding="utf-8") + "\n# local mutation\n", encoding="utf-8")
            _, payload = self.run_tool(str(CHECKER), "--target-project", str(project), "--skip-runtime-import", expect_success=False)
            self.assertEqual(payload["token"], "blocked:managed_file_hash_mismatch")

    def test_path_traversal_mode_cli_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project)
            _, payload = self.run_tool(
                str(INSTALLER),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
                "--mode-cli",
                "../outside.py",
                "--dry-run",
                expect_success=False,
            )
            self.assertEqual(payload["token"], "blocked:path_traversal")

    def test_update_dry_run_reports_noop_after_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project)
            self.run_tool(
                str(INSTALLER),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
            )
            _, payload = self.run_tool(str(UPDATER), "--target-project", str(project), "--dry-run")
            self.assertTrue(payload["no_op"], payload)
            self.assertEqual(payload["status"], "up_to_date")

    def gui_config(self, project: Path) -> dict:
        return {
            "schema_version": 1,
            "toolchain": "project_moe_gui",
            "toolchain_version": "0.2.0",
            "cli_contract": "project-moe-cli-v1",
            "agent_name": "thesis-moe-mentor",
            "state_namespace": "thesis_moe",
            "mode_cli": "tools/thesis_moe_mode.py",
            "target_project_root": str(project),
            "shared_runtime_root": str(REPO_ROOT / ".shared_runtimes" / "pyside6"),
            "runtime_python": str(REPO_ROOT / ".shared_runtimes" / "pyside6" / ".venv" / "Scripts" / "python.exe"),
        }

    def test_gui_shell_import_safe_without_pyside6(self) -> None:
        from project_moe_gui import gui_shell

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            config = self.gui_config(project)
            payload = gui_shell.build_gui_preflight(config, pyside6_available=False)
            self.assertFalse(payload["ok"], payload)
            self.assertEqual(payload["token"], "blocked:pyside6_unavailable")
            self.assertEqual(payload["gui_shell_contract"], "project-moe-gui-shell-v1")
            self.assertTrue(payload["view_model"]["window_structure"]["automation_boundary"]["import_safe_without_pyside6"])

    def test_gui_shell_builds_status_card_and_empty_session_table(self) -> None:
        from project_moe_gui import gui_shell

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            config = self.gui_config(project)
            view_model = gui_shell.build_view_model(
                config,
                project_status={"ok": True, "token": "ok", "project_default_enabled": True, "git_branch": "feature/gui-shell"},
                sessions_payload={"ok": True, "token": "ok", "sessions": []},
                status_payload={"ok": True, "token": "ok", "effective_enabled": True},
                pyside6_available=False,
            )
            self.assertEqual(view_model["top_banner"]["current_branch"], "feature/gui-shell")
            self.assertEqual(view_model["project_default_card"]["label"], "enabled")
            self.assertEqual(view_model["project_default_card"]["effective_label"], "enabled")
            self.assertTrue(view_model["session_table"]["empty_state"]["is_empty"])
            self.assertEqual(view_model["session_table"]["token"], "ok")

    def test_gui_shell_action_plans_use_argv_lists_not_shell_strings(self) -> None:
        from project_moe_gui import gui_shell

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            config = self.gui_config(project)
            plan = gui_shell.build_action_plan(config, "session-on", session_id="session-1234567890abcdef")
            self.assertTrue(plan["ok"], plan)
            self.assertIsInstance(plan["argv"], list)
            self.assertFalse(plan["shell"])
            self.assertTrue(plan["writes_state"])
            self.assertFalse(plan["direct_state_write"])
            self.assertIn("--session-id", plan["argv"])
            self.assertIn("session-1234567890abcdef", plan["argv"])
            self.assertEqual(plan["scope"], "session")
            self.assertTrue(plan["requires_readback_after_write"])
            self.assertEqual([item["action"] for item in plan["readback_after_write"]], ["project-status", "list-sessions", "status"])

            refresh = gui_shell.build_refresh_plan(config)
            self.assertFalse(refresh["writes_state"])
            self.assertFalse(refresh["shell"])
            self.assertTrue(all(command["shell"] is False for command in refresh["commands"]))
            self.assertTrue(all(command["writes_state"] is False for command in refresh["commands"]))
            self.assertEqual(refresh["keyboard_shortcut"], "F5")

    def test_gui_shell_pending_write_disables_same_scope_buttons_and_keeps_read_refresh_available(self) -> None:
        from project_moe_gui import gui_shell

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            config = self.gui_config(project)
            view_model = gui_shell.build_view_model(
                config,
                project_status={"ok": True, "token": "ok", "project_default_enabled": False, "git_branch": "main"},
                sessions_payload={
                    "ok": True,
                    "token": "ok",
                    "sessions": [{"session_id": "session-1234567890abcdef", "enabled": False, "token": "ok"}],
                },
                status_payload={"ok": True, "token": "ok", "effective_enabled": False},
                pyside6_available=False,
                pending_scope="session:sessio…cdef",
            )

            row = view_model["session_table"]["rows"][0]
            self.assertFalse(row["actions"]["enable_session"]["button"]["enabled"])
            self.assertEqual(row["actions"]["enable_session"]["button"]["disabled_reason"], "pending_same_scope_write")
            self.assertFalse(row["actions"]["disable_session"]["button"]["enabled"])
            self.assertTrue(view_model["refresh_action"]["commands"][0]["ok"])
            self.assertEqual(view_model["button_state"]["pending_scope"], "session")
            self.assertEqual(view_model["button_state"]["pending_scope_key"], "session:sessio…cdef")

    def test_gui_shell_exposes_keyboard_and_high_contrast_state_text(self) -> None:
        from project_moe_gui import gui_shell

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            config = self.gui_config(project)
            view_model = gui_shell.build_view_model(
                config,
                project_status={"ok": True, "token": "ok", "project_default_enabled": True, "git_branch": "main"},
                sessions_payload={"ok": True, "token": "ok", "sessions": []},
                status_payload={"ok": True, "token": "ok", "effective_enabled": True},
                pyside6_available=False,
            )

            self.assertEqual(view_model["keyboard_navigation"]["shortcuts"]["refresh"], "F5")
            self.assertIn("Project default:", view_model["project_default_card"]["status_badge"]["high_contrast_text"])
            enable_button = view_model["project_default_card"]["actions"]["enable_project_default"]["button"]
            self.assertIn("Project default scope", enable_button["accessible_name"])
            self.assertTrue(view_model["theme_accessibility"]["status_not_color_only"])
            self.assertTrue(view_model["window_structure"]["accessibility_contract"]["write_buttons_disable_same_scope_while_pending"])

    def test_gui_shell_write_action_runs_readback_after_write(self) -> None:
        from project_moe_gui import gui_shell

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project)
            config = self.gui_config(project)
            result = gui_shell.execute_write_action_with_readback(config, "project-on")
            self.assertTrue(result["ok"], result)
            self.assertEqual(result["token"], "ok")
            self.assertTrue(result["readback_required"])
            self.assertEqual(result["readback_commands"], ["project-status", "list-sessions", "status"])
            self.assertIn("project-status", result["readback"])
            self.assertEqual(result["button_state_during_command"]["pending_scope"], "project-default")

    def test_gui_shell_invalid_session_rows_use_stable_tokens(self) -> None:
        from project_moe_gui import gui_shell

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            config = self.gui_config(project)
            table = gui_shell.build_session_table(config, {"ok": True, "token": "ok", "sessions": [{"enabled": True}, "bad-row"]})
            self.assertEqual(table["invalid_count"], 2)
            self.assertEqual(table["rows"][0]["token"], "blocked:invalid_session_record")
            self.assertEqual(table["rows"][1]["token"], "blocked:invalid_session_record")
            self.assertEqual(table["rows"][0]["actions"], {})
            self.assertEqual(table["rows"][1]["actions"], {})

    def test_installed_launcher_preflight_reports_gui_shell_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project)
            self.run_tool(
                str(INSTALLER),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
            )
            launcher = project / "tools" / "project_moe_gui" / "launcher.py"
            result = subprocess.run(
                [sys.executable, str(launcher), "--preflight", "--json"],
                cwd=project,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            payload = json.loads(result.stdout)
            self.assertIn(payload["token"], {"ok", "blocked:pyside6_unavailable"}, payload)
            self.assertEqual(payload["gui_shell_contract"], "project-moe-gui-shell-v1")
            self.assertNotEqual(payload["token"], "blocked:gui_not_implemented_phase2a")
            self.assertNotIn("Interactive PySide6 GUI is implemented in Phase 2B.", result.stdout)


if __name__ == "__main__":
    unittest.main()
