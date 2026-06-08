#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(ROOT := Path(__file__).resolve().parents[1]))
from tools import install_user_level_mcp_skills_cli as installer  # noqa: E402


INSTALL = ROOT / "tools" / "install_user_level_mcp_skills_cli.py"
CHECK = ROOT / "tools" / "check_user_level_mcp_skills_cli_install.py"
RECEIPT_GOVERNANCE = ROOT / "tools" / "user_level_receipt_governance.py"


class UserLevelMcpSkillsCliInstallTests(unittest.TestCase):
    maxDiff = None

    def make_home(self, name: str) -> Path:
        base = ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        home = base / "codex-home"
        home.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(base, ignore_errors=True))
        return home

    def write_fake_mcp2cli(self, home: Path) -> Path:
        fake = home / "fake" / "mcp2cli.cmd"
        fake.parent.mkdir(parents=True, exist_ok=True)
        fake.write_text("@echo off\necho mcp2cli 3.2.0\nexit /b 0\n", encoding="utf-8")
        return fake

    def env_with_fake_mcp2cli(self, home: Path) -> dict[str, str]:
        env = dict(os.environ)
        env["MCP2CLI_EXE"] = str(self.write_fake_mcp2cli(home))
        return env

    def run_json(self, script: Path, *args: str, check: bool = True, env: dict[str, str] | None = None) -> tuple[int, dict]:
        proc = subprocess.run(
            [sys.executable, str(script), *args, "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            check=False,
        )
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:  # pragma: no cover - diagnostic
            raise AssertionError(f"stdout was not JSON: {proc.stdout!r}\nstderr={proc.stderr!r}") from exc
        if check and proc.returncode != 0:
            self.fail(json.dumps(payload, ensure_ascii=False, indent=2) + "\n" + proc.stderr)
        return proc.returncode, payload

    def test_plan_reports_upstream_runtime_and_skills2cli_fork_boundary(self) -> None:
        code, payload = self.run_json(INSTALL, "plan")

        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["upstream"]["source_url"], "https://github.com/knowsuchagency/mcp2cli")
        self.assertIn("uvx mcp2cli --help", payload["upstream"]["install_markers"])
        self.assertIn("uv tool install mcp2cli", payload["upstream"]["install_markers"])
        self.assertIn("npx skills add knowsuchagency/mcp2cli --skill mcp2cli", payload["upstream"]["install_markers"])
        self.assertTrue(payload["safety"]["skills2cli_is_upstream_pattern_fork"])
        self.assertFalse(payload["safety"]["native_subagent_evidence"])
        self.assertFalse(payload["safety"]["full_skill_bodies_included_by_default"])

    def test_apply_requires_explicit_flag_and_operator_confirmation(self) -> None:
        code, payload = self.run_json(INSTALL, "apply", check=False)
        self.assertEqual(code, 3)
        self.assertIn("apply_flag_required", payload["blockers"])

        home = self.make_home("needs-confirmation")
        code, payload = self.run_json(INSTALL, "apply", "--apply", "--codex-home", str(home), check=False)
        self.assertEqual(code, 3)
        self.assertIn("operator_confirmation_required", payload["blockers"])

    def test_simulated_apply_writes_wrappers_skill_and_valid_receipts(self) -> None:
        home = self.make_home("simulated-apply")
        code, payload = self.run_json(
            INSTALL,
            "apply",
            "--apply",
            "--operator-confirmation",
            "--simulate-external",
            "--codex-home",
            str(home),
            "--upstream-ref",
            "3b7440196d620df29c13d3cfb8ad36ad4792e69f",
        )

        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["mutates_user_level_state"])
        self.assertEqual(len(payload["receipt_paths"]), 2)
        self.assertTrue((home / "bin" / "mcp2cli.cmd").exists())
        self.assertTrue((home / "bin" / "skills2cli.cmd").exists())
        self.assertTrue((home / "skills" / "skills2cli" / "SKILL.md").exists())
        wrapper_text = (home / "bin" / "mcp2cli.cmd").read_text(encoding="utf-8")
        self.assertIn("UV_CACHE_DIR", wrapper_text)
        self.assertIn("mcp-skills-cli\\uv-cache", wrapper_text)
        self.assertNotIn("mcp-skills-cli/uv-cache", wrapper_text)
        self.assertIn("repo-copy:", json.dumps(payload["receipt_summaries"], ensure_ascii=False))
        self.assertNotIn("sk-test-secret", json.dumps(payload, ensure_ascii=False))

        check_code, check_payload = self.run_json(
            INSTALL,
            "check",
            "--require-installed",
            "--smoke",
            "--codex-home",
            str(home),
            env=self.env_with_fake_mcp2cli(home),
        )
        self.assertEqual(check_code, 0)
        self.assertTrue(check_payload["ok"])
        self.assertTrue(check_payload["wrapper_presence"]["mcp2cli_cmd"])
        self.assertTrue(check_payload["wrapper_presence"]["skills2cli_cmd"])
        self.assertEqual(check_payload["receipt_count"], 2)

    def test_posix_smoke_uses_safe_execution_for_generated_windows_cmd_wrappers(self) -> None:
        home = self.make_home("posix-smoke-helper")
        self.run_json(
            INSTALL,
            "apply",
            "--apply",
            "--operator-confirmation",
            "--simulate-external",
            "--codex-home",
            str(home),
        )
        paths = installer.layout(home)

        mcp_result = installer.run_wrapper_smoke(
            [str(paths["mcp2cli_cmd"]), "--version"],
            paths=paths,
            wrapper_key="mcp2cli_cmd",
            timeout=10,
            platform_name="posix",
        )
        skills_result = installer.run_wrapper_smoke(
            [str(paths["skills2cli_cmd"]), "--help"],
            paths=paths,
            wrapper_key="skills2cli_cmd",
            timeout=10,
            platform_name="posix",
        )

        self.assertEqual(mcp_result.returncode, 0, mcp_result)
        self.assertTrue(mcp_result.skipped)
        self.assertEqual(skills_result.returncode, 0, skills_result.stderr)
        self.assertFalse(skills_result.skipped)

    def test_check_is_warn_only_without_require_installed(self) -> None:
        home = self.make_home("warn-only")
        code, payload = self.run_json(INSTALL, "check", "--codex-home", str(home))

        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertGreaterEqual(len(payload["warnings"]), 1)
        self.assertFalse(payload["mutates_user_level_state"])

    def test_repository_checker_passes_repo_surfaces(self) -> None:
        code, payload = self.run_json(CHECK, "--root", str(ROOT))

        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertIn("install_helper_plan_ok", payload["info"])

    def test_checker_can_require_installed_against_simulated_home(self) -> None:
        home = self.make_home("checker-require")
        self.run_json(
            INSTALL,
            "apply",
            "--apply",
            "--operator-confirmation",
            "--simulate-external",
            "--codex-home",
            str(home),
        )

        code, payload = self.run_json(
            CHECK,
            "--root",
            str(ROOT),
            "--require-user-level-installed",
            "--smoke",
            "--codex-home",
            str(home),
            env=self.env_with_fake_mcp2cli(home),
        )
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["user_level_check"]["receipt_count"], 2)

    def test_smoke_command_writes_r4_receipts_validated_by_receipt_governance(self) -> None:
        home = self.make_home("smoke-receipts")
        self.run_json(
            INSTALL,
            "apply",
            "--apply",
            "--operator-confirmation",
            "--simulate-external",
            "--codex-home",
            str(home),
        )

        code, payload = self.run_json(
            INSTALL,
            "smoke",
            "--record",
            "--operator-confirmation",
            "--codex-home",
            str(home),
            env=self.env_with_fake_mcp2cli(home),
        )

        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["receipt_write_performed"])
        self.assertEqual(len(payload["smoke_receipt_paths"]), 2)
        self.assertEqual(
            {item["runtime_stage"] for item in payload["smoke_receipt_summaries"]},
            {"R4"},
        )
        self.assertEqual(
            {item["receipt_kind"] for item in payload["smoke_receipt_summaries"]},
            {"smoke-tested"},
        )

        for receipt_path in payload["smoke_receipt_paths"]:
            tool_name = "skills2cli" if "skills2cli" in Path(receipt_path).name else "mcp2cli"
            check_code, check_payload = self.run_json(
                RECEIPT_GOVERNANCE,
                "smoke-check",
                "--receipt",
                receipt_path,
                "--tool-name",
                tool_name,
                "--owner-lane",
                tool_name,
            )
            self.assertEqual(check_code, 0)
            self.assertTrue(check_payload["ok"])
            self.assertTrue(check_payload["smoke_receipt_valid"])
            self.assertTrue(check_payload["rollback_ready"])

    def test_checker_can_require_smoke_tested_against_simulated_home(self) -> None:
        home = self.make_home("checker-smoke-tested")
        self.run_json(
            INSTALL,
            "apply",
            "--apply",
            "--operator-confirmation",
            "--simulate-external",
            "--codex-home",
            str(home),
        )
        self.run_json(
            INSTALL,
            "smoke",
            "--record",
            "--operator-confirmation",
            "--codex-home",
            str(home),
            env=self.env_with_fake_mcp2cli(home),
        )

        code, payload = self.run_json(
            CHECK,
            "--root",
            str(ROOT),
            "--require-user-level-installed",
            "--require-smoke-tested",
            "--codex-home",
            str(home),
            env=self.env_with_fake_mcp2cli(home),
        )
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["user_level_check"]["smoke_receipt_count"], 2)


if __name__ == "__main__":
    unittest.main()
