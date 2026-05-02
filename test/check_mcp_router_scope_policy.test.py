import json
import shutil
import sqlite3
import subprocess
import sys
import unittest
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "check_mcp_router_scope_policy.py"


class McpRouterScopePolicyCheckTest(unittest.TestCase):
    maxDiff = None

    def make_root(self, name: str) -> Path:
        root = REPO_ROOT / ".omx" / "test-artifacts" / f"{name}-{uuid.uuid4().hex[:8]}"
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def write_codex_config(self, root: Path, text: str) -> Path:
        path = root / "config.toml"
        path.write_text(text, encoding="utf-8")
        return path

    def write_router_db(self, root: Path, rows: list[tuple[str, str, int, int]]) -> Path:
        path = root / "mcprouter.db"
        connection = sqlite3.connect(path)
        try:
            connection.execute(
                "CREATE TABLE servers (id TEXT, name TEXT, command TEXT, args TEXT, auto_start INTEGER, disabled INTEGER)"
            )
            for row in rows:
                connection.execute(
                    "INSERT INTO servers (id, name, command, args, auto_start, disabled) VALUES (?, ?, 'cmd', '[]', ?, ?)",
                    row,
                )
            connection.commit()
        finally:
            connection.close()
        return path

    def write_exception_file(self, root: Path) -> Path:
        path = root / "tools" / "mcp_router_scope_policy_exceptions.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "exceptions": [
                        {
                            "id": "mcp-router-disabled-for-resume-stability",
                            "status": "active",
                            "scope": "codex_mcp_router_bridge_disabled",
                            "reason": "resume stability regression",
                            "recovery_condition": "validated MCP-safe wrapper",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return path

    def run_check(self, root: Path, codex_config: Path, router_db: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--root",
                str(root),
                "--codex-config",
                str(codex_config),
                "--mcp-router-db",
                str(router_db),
                "--json",
                *extra,
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

    def good_config(self) -> str:
        return """
[mcp_servers.omx_state]
enabled = true
command = "node"

[mcp_servers.omx_memory]
enabled = true
command = "node"

[mcp_servers.omx_code_intel]
enabled = true
command = "node"

[mcp_servers.omx_trace]
enabled = true
command = "node"

[mcp_servers.chrome-devtools]
enabled = false
command = "npx"

[mcp_servers.pencil]
enabled = false
command = "pencil"

[mcp_servers.mcp_router]
enabled = true
command = "npx"
"""

    def test_passes_for_codex_direct_and_router_shared_split(self) -> None:
        root = self.make_root("mcp-scope-pass")
        codex_config = self.write_codex_config(root, self.good_config())
        router_db = self.write_router_db(root, [("id1", "chrome-devtools", 1, 0), ("id2", "pencil", 1, 0)])

        result = self.run_check(root, codex_config, router_db)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["errors"], 0)
        self.assertEqual(payload["counts"]["router_forbidden_records"], 0)

    def test_fails_when_shared_server_is_enabled_directly_in_codex(self) -> None:
        root = self.make_root("mcp-scope-codex-fail")
        codex_config = self.write_codex_config(root, self.good_config().replace("[mcp_servers.chrome-devtools]\nenabled = false", "[mcp_servers.chrome-devtools]\nenabled = true"))
        router_db = self.write_router_db(root, [("id1", "chrome-devtools", 1, 0)])

        result = self.run_check(root, codex_config, router_db)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("chrome-devtools" in error for error in payload["errors"]))

    def test_fails_when_mcp_router_bridge_is_disabled_without_exception(self) -> None:
        root = self.make_root("mcp-scope-router-disabled-fail")
        disabled_config = self.good_config().replace(
            "[mcp_servers.mcp_router]\nenabled = true",
            "[mcp_servers.mcp_router]\nenabled = false",
        )
        codex_config = self.write_codex_config(root, disabled_config)
        router_db = self.write_router_db(root, [("id1", "chrome-devtools", 1, 0)])

        result = self.run_check(root, codex_config, router_db, "--strict-router-state")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("mcp_router" in error for error in payload["errors"]))

    def test_allows_mcp_router_bridge_disabled_with_declared_stability_exception(self) -> None:
        root = self.make_root("mcp-scope-router-disabled-exception")
        self.write_exception_file(root)
        disabled_config = self.good_config().replace(
            "[mcp_servers.mcp_router]\nenabled = true",
            "[mcp_servers.mcp_router]\nenabled = false",
        )
        codex_config = self.write_codex_config(root, disabled_config)
        router_db = self.write_router_db(root, [("id1", "chrome-devtools", 1, 0)])

        result = self.run_check(root, codex_config, router_db, "--strict-router-state")
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["counts"]["errors"], 0)
        self.assertEqual(payload["counts"]["active_exceptions"], 1)
        self.assertTrue(any("temporarily disabled" in warning for warning in payload["warnings"]))
        self.assertEqual(
            payload["codex_config"]["mcp_router_disabled_exception"]["id"],
            "mcp-router-disabled-for-resume-stability",
        )

    def test_strict_router_state_fails_for_forbidden_router_server(self) -> None:
        root = self.make_root("mcp-scope-router-fail")
        codex_config = self.write_codex_config(root, self.good_config())
        router_db = self.write_router_db(root, [("id1", "omx_state", 0, 0)])

        result = self.run_check(root, codex_config, router_db, "--strict-router-state")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("omx_state" in error for error in payload["errors"]))

    def test_default_router_state_reports_forbidden_server_as_warning(self) -> None:
        root = self.make_root("mcp-scope-router-warning")
        codex_config = self.write_codex_config(root, self.good_config())
        router_db = self.write_router_db(root, [("id1", "omx_state", 0, 0)])

        result = self.run_check(root, codex_config, router_db)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(any("omx_state" in warning for warning in payload["warnings"]))


if __name__ == "__main__":
    unittest.main()
