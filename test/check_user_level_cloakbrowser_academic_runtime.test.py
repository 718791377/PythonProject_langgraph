#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "check_user_level_cloakbrowser_academic_runtime.py"
PLAN_EN = ROOT / "docs_bilingual" / "implementation_plans" / "user_level_cloakbrowser_academic_research_runtime_plan.md"
PLAN_ZH = ROOT / "docs_bilingual" / "implementation_plans" / "user_level_cloakbrowser_academic_research_runtime_plan.zh-CN.md"


class UserLevelCloakBrowserAcademicRuntimeTests(unittest.TestCase):
    maxDiff = None

    def run_checker(self, *args: str, expect: int = 0) -> dict:
        proc = subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(ROOT), "--json", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(proc.returncode, expect, proc.stdout + proc.stderr)
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError as exc:  # pragma: no cover - diagnostic
            raise AssertionError(f"stdout was not JSON: {proc.stdout!r}\nstderr={proc.stderr!r}") from exc

    def test_plan_surfaces_are_registered_and_decision_complete(self) -> None:
        data = self.run_checker()
        self.assertTrue(data["ok"], data["errors"])
        self.assertIn(data["plans"][PLAN_EN.relative_to(ROOT).as_posix()]["status"], {"planned-local", "R6 live-executed"})
        self.assertIn(data["plans"][PLAN_ZH.relative_to(ROOT).as_posix()]["status"], {"planned-local", "R6 live-executed"})
        self.assertFalse(data["policy"]["docker_install_allowed"])
        self.assertFalse(data["policy"]["native_codex_files_mutated"])
        self.assertFalse(data["policy"]["remote_publication_allowed"])
        self.assertEqual(data["sources"]["cloakbrowser"]["pypi_version"], "0.3.31")
        self.assertEqual(data["sources"]["cloakbrowser"]["npm_version"], "0.3.31")
        self.assertTrue(data["registry_guard_ci"]["runtime_script_registered"])

    def test_receipt_checker_accepts_hash_only_live_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp)
            receipt = {
                "schema_version": 1,
                "tool_name": "cloakbrowser-python",
                "runtime_stage": "R6 live-executed",
                "source_url": "https://github.com/CloakHQ/CloakBrowser",
                "source_ref": "main",
                "installed_version": "0.3.31",
                "install_root_hash": "a" * 16,
                "wrapper_path_hash": "b" * 16,
                "state_path_hash": "c" * 16,
                "smoke_result": {"status": "pass", "command_hash": "d" * 16},
                "rollback_pointer_hash": "e" * 16,
                "redaction_status": "pass",
                "raw_paths_included": False,
                "remote_publication_mutated": False,
            }
            (receipt_dir / "cloakbrowser-python.json").write_text(json.dumps(receipt), encoding="utf-8")
            (receipt_dir / "summary.json").write_text(json.dumps({"ok": True}), encoding="utf-8")
            data = self.run_checker("--receipt-dir", str(receipt_dir))
            self.assertEqual(data["receipt_summary"]["accepted"], ["cloakbrowser-python"])
            self.assertEqual(data["receipt_summary"]["sidecars_skipped"], ["summary.json"])

    def test_receipt_checker_rejects_raw_paths_and_remote_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp)
            receipt = {
                "schema_version": 1,
                "tool_name": "academic-research-suite",
                "runtime_stage": "R6 live-executed",
                "source_url": "https://github.com/Imbad0202/academic-research-skills-codex",
                "source_ref": "main",
                "installed_version": "0.1.11",
                "install_root_hash": "a" * 16,
                "wrapper_path_hash": "b" * 16,
                "state_path_hash": "c" * 16,
                "smoke_result": {"status": "pass", "command_hash": "d" * 16},
                "rollback_pointer_hash": "e" * 16,
                "redaction_status": "pass",
                "raw_paths_included": True,
                "install_root": "C:/Users/lenovo/.codex/skills/academic-research-suite",
                "remote_publication_mutated": True,
            }
            (receipt_dir / "academic-research-suite.json").write_text(json.dumps(receipt), encoding="utf-8")
            data = self.run_checker("--receipt-dir", str(receipt_dir), "--require-live", expect=1)
            self.assertIn("receipt:academic-research-suite.json:raw_paths_included_must_be_false", data["errors"])
            self.assertIn("receipt:academic-research-suite.json:remote_publication_mutated_must_be_false", data["errors"])


    def test_receipt_checker_accepts_manager_source_loopback_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp)
            receipt = {
                "schema_version": 1,
                "tool_name": "cloakbrowser-manager-source-runtime",
                "runtime_stage": "R6 live-executed",
                "runtime_stage_detail": "source-backend-frontend-loopback",
                "source_url": "https://github.com/CloakHQ/CloakBrowser-Manager",
                "source_ref": "a85b213286c8a25475a6f3243c47f99375ffa772",
                "installed_version": "source-main",
                "install_root_hash": "a" * 16,
                "wrapper_path_hash": "b" * 16,
                "state_path_hash": "c" * 16,
                "rollback_pointer_hash": "d" * 16,
                "docker_install_allowed": False,
                "container_runtime_used": False,
                "smoke_kind": "source-backend-frontend-loopback",
                "api_status_http_status": 200,
                "api_status_json": True,
                "gui_shell_http_status": 200,
                "gui_shell_html": True,
                "profile_launch_smoke": "not_run:no_xvnc_on_windows",
                "smoke_result": {"status": "pass", "command_hash": "e" * 16},
                "redaction_status": "pass",
                "raw_paths_included": False,
                "remote_publication_mutated": False,
            }
            (receipt_dir / "cloakbrowser-manager-source-runtime.json").write_text(json.dumps(receipt), encoding="utf-8")
            data = self.run_checker("--receipt-dir", str(receipt_dir))
            self.assertEqual(data["receipt_summary"]["accepted"], ["cloakbrowser-manager-source-runtime"])

    def test_receipt_checker_rejects_manager_source_loopback_container_usage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            receipt_dir = Path(tmp)
            receipt = {
                "schema_version": 1,
                "tool_name": "cloakbrowser-manager-source-runtime",
                "runtime_stage": "R6 live-executed",
                "runtime_stage_detail": "source-backend-frontend-loopback",
                "source_url": "https://github.com/CloakHQ/CloakBrowser-Manager",
                "source_ref": "a85b213286c8a25475a6f3243c47f99375ffa772",
                "installed_version": "source-main",
                "install_root_hash": "a" * 16,
                "wrapper_path_hash": "b" * 16,
                "state_path_hash": "c" * 16,
                "rollback_pointer_hash": "d" * 16,
                "docker_install_allowed": False,
                "container_runtime_used": True,
                "smoke_kind": "source-backend-frontend-loopback",
                "api_status_http_status": 200,
                "api_status_json": True,
                "gui_shell_http_status": 200,
                "gui_shell_html": True,
                "profile_launch_smoke": "not_run:no_xvnc_on_windows",
                "smoke_result": {"status": "pass", "command_hash": "e" * 16},
                "redaction_status": "pass",
                "raw_paths_included": False,
                "remote_publication_mutated": False,
            }
            (receipt_dir / "cloakbrowser-manager-source-runtime.json").write_text(json.dumps(receipt), encoding="utf-8")
            data = self.run_checker("--receipt-dir", str(receipt_dir), expect=1)
            self.assertIn(
                "receipt:cloakbrowser-manager-source-runtime.json:container_runtime_used_must_be_false",
                data["errors"],
            )


    def test_runtime_receipt_builder_redacts_manager_source_loopback_paths(self) -> None:
        import importlib.util

        helper_path = ROOT / "tools" / "run_cloakbrowser_manager_source_runtime.py"
        spec = importlib.util.spec_from_file_location("run_cloakbrowser_manager_source_runtime", helper_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt = module.build_receipt(
            source_ref="a85b213286c8a25475a6f3243c47f99375ffa772",
            install_root_label="codex-tools/cloakbrowser-manager/source",
            wrapper_label="codex-tools/cloakbrowser-manager/runtime/manager_runtime_app.py",
            state_label="codex-tools/cloakbrowser-manager/state/source-runtime",
            rollback_label="remove codex-tools/cloakbrowser-manager/runtime and state/source-runtime",
            command_label="cloakbrowser-manager source backend+frontend loopback smoke",
            api_status_http_status=200,
            api_status_json=True,
            gui_shell_http_status=200,
            gui_shell_html=True,
            frontend_build_hash="f" * 16,
            backend_import_hash="1" * 16,
            port=51731,
        )
        self.assertEqual(receipt["tool_name"], "cloakbrowser-manager-source-runtime")
        self.assertFalse(receipt["container_runtime_used"])
        self.assertFalse(receipt["docker_install_allowed"])
        self.assertFalse(receipt["raw_paths_included"])
        self.assertNotIn("install_root", receipt)
        self.assertNotIn("wrapper_path", receipt)
        self.assertNotIn("state_path", receipt)
        self.assertRegex(receipt["install_root_hash"], r"^[0-9a-f]{16,64}$")
        self.assertEqual(receipt["profile_launch_smoke"], "not_run:no_xvnc_on_windows")


    def test_runtime_helper_reuses_locked_existing_node_modules_on_windows_eperm(self) -> None:
        import importlib.util

        helper_path = ROOT / "tools" / "run_cloakbrowser_manager_source_runtime.py"
        spec = importlib.util.spec_from_file_location("run_cloakbrowser_manager_source_runtime", helper_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            node_modules = Path(tmp) / "node_modules"
            node_modules.mkdir()
            output = "npm error code EPERM\nnpm error path C:/x/node_modules/.vite-temp"
            self.assertTrue(module.can_reuse_locked_existing_node_modules(output, node_modules))
            self.assertFalse(module.can_reuse_locked_existing_node_modules("npm error code E404", node_modules))


if __name__ == "__main__":
    unittest.main()
