from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
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
elif cmd == "project-status":
    payload["message"] = "project status read"
elif cmd == "status":
    payload["message"] = "mentor mode disabled"
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


if __name__ == "__main__":
    unittest.main()
