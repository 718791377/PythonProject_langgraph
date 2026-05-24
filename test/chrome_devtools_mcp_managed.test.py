import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "chrome_devtools_mcp_managed.py"


def run_cmd(args, state_dir, expect=0):
    cmd = [sys.executable, str(SCRIPT), "--state-dir", str(state_dir), *args, "--json"]
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - debug aid
        raise AssertionError(f"invalid json\ncmd={cmd}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}") from exc
    if proc.returncode != expect:
        raise AssertionError(f"unexpected rc {proc.returncode}, expected {expect}\ncmd={cmd}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return data


def write_authorization_receipt(path: Path, *, target: str, session: str) -> Path:
    payload = {
        "schema_version": 1,
        "action": "browser project profile authorization",
        "target": target,
        "scope": "project-profile",
        "expiry": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(timespec="seconds"),
        "session": session,
        "operator_confirmation": True,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


class ChromeDevToolsMcpManagedTests(unittest.TestCase):
    def test_plan_isolated_session_is_dry_run_and_redacts_profile_path(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cmd(
                [
                    "isolated-session",
                    "plan",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    "session-a",
                    "--purpose",
                    "unit test",
                ],
                state,
            )
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertTrue(result["ok"])
            self.assertTrue(result["dry_run"])
            self.assertFalse(result["registry_mutated"])
            self.assertFalse(result["start_performed"])
            self.assertFalse(result["safety"]["launches_browser"])
            self.assertFalse(result["safety"]["connects_to_cdp"])
            self.assertFalse(result["safety"]["mutates_user_codex_config"])
            self.assertEqual(result["plan"]["owner_class"], "codex-managed-isolated")
            self.assertEqual(result["plan"]["port_policy"]["codex_browser_range"].split()[0], "39500-39699")
            self.assertIn("profile_path_hash", result["plan"])
            self.assertIn("[REDACTED_PATH]", serialized)
            self.assertNotIn(str(state), serialized)
            self.assertFalse((state / "owner-registry" / "registry.json").exists())

    def test_reserve_isolated_session_writes_owner_lease_and_wrapper_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cmd(
                [
                    "isolated-session",
                    "reserve",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    "session-a",
                    "--purpose",
                    "unit test reserve",
                    "--ttl",
                    "120",
                ],
                state,
            )
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertTrue(result["ok"])
            self.assertTrue(result["registry_mutated"])
            self.assertFalse(result["start_performed"])
            lease = result["owner_lease"]
            self.assertEqual(lease["owner_class"], "codex-managed-isolated")
            self.assertTrue(lease["cleanup_allowed"])
            self.assertEqual(lease["status"], "active")
            self.assertTrue(result["wrapper_receipt"]["receipt_written"])
            self.assertIn("receipt_path_hash", result["wrapper_receipt"])
            self.assertNotIn(str(state), serialized)

            registry = json.loads((state / "owner-registry" / "registry.json").read_text(encoding="utf-8"))
            self.assertEqual(len(registry["leases"]), 1)
            self.assertEqual(registry["leases"][0]["owner_class"], "codex-managed-isolated")
            self.assertTrue(list((state / "receipts").glob("*-reserve-isolated-session-*.json")))

    def test_live_start_without_install_receipt_fails_closed_without_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cmd(
                [
                    "isolated-session",
                    "start",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    "session-a",
                    "--purpose",
                    "unit test start",
                ],
                state,
                expect=3,
            )
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"], "install_receipt_required")
            self.assertFalse(result["start_performed"])
            self.assertFalse(result["safety"]["launches_browser"])
            self.assertFalse((state / "owner-registry" / "registry.json").exists())
            self.assertNotIn(str(state), serialized)

    def test_release_delegates_to_owner_registry(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            reserved = run_cmd(
                [
                    "isolated-session",
                    "reserve",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    "session-a",
                    "--purpose",
                    "unit test release",
                ],
                state,
            )
            lease_id = reserved["owner_lease"]["lease_id"]
            released = run_cmd(["isolated-session", "release", "--lease-id", lease_id, "--session", "session-a"], state)
            self.assertTrue(released["ok"])
            self.assertEqual(released["owner_lease"]["status"], "released")
            self.assertTrue(released["wrapper_receipt"]["receipt_written"])

            status = run_cmd(["isolated-session", "status"], state)
            self.assertEqual(status["leases"][0]["status"], "released")

    def test_project_profile_plan_is_dry_run_and_retention_protected(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cmd(
                [
                    "project-profile",
                    "plan",
                    "--project",
                    "pythonproject-langgraph",
                    "--profile",
                    "dev-login",
                    "--session",
                    "session-a",
                    "--purpose",
                    "project profile unit test",
                ],
                state,
            )
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertTrue(result["ok"])
            self.assertTrue(result["dry_run"])
            self.assertFalse(result["registry_mutated"])
            self.assertFalse(result["start_performed"])
            self.assertEqual(result["plan"]["mode"], "project-profile")
            self.assertEqual(result["plan"]["owner_class"], "codex-managed-project")
            self.assertEqual(result["plan"]["profile_retention"], "long-lived-project-profile")
            self.assertFalse(result["plan"]["cleanup_allowed_after_stale_evidence"])
            self.assertTrue(result["plan"]["authorization_required_for_reserve"])
            self.assertIn("[REDACTED_PATH]", serialized)
            self.assertNotIn(str(state), serialized)
            self.assertFalse((state / "owner-registry" / "registry.json").exists())

    def test_project_profile_reserve_without_authorization_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cmd(
                [
                    "project-profile",
                    "reserve",
                    "--project",
                    "pythonproject-langgraph",
                    "--profile",
                    "dev-login",
                    "--session",
                    "session-a",
                    "--purpose",
                    "missing auth",
                ],
                state,
                expect=3,
            )
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"], "authorization_required")
            self.assertIn("authorization_receipt_required", serialized)
            self.assertFalse((state / "owner-registry" / "registry.json").exists())
            self.assertNotIn(str(state), serialized)

    def test_project_profile_reserve_with_authorization_writes_non_cleanup_lease(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            target = "chrome-devtools-mcp:project:pythonproject-langgraph:dev-login"
            receipt = write_authorization_receipt(state / "auth.json", target=target, session="session-a")
            result = run_cmd(
                [
                    "project-profile",
                    "reserve",
                    "--project",
                    "pythonproject-langgraph",
                    "--profile",
                    "dev-login",
                    "--session",
                    "session-a",
                    "--purpose",
                    "authorized project profile",
                    "--authorization-receipt",
                    str(receipt),
                ],
                state,
            )
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertTrue(result["ok"])
            self.assertTrue(result["registry_mutated"])
            self.assertFalse(result["start_performed"])
            self.assertEqual(result["owner_lease"]["owner_class"], "codex-managed-project")
            self.assertFalse(result["owner_lease"]["cleanup_allowed"])
            self.assertEqual(result["plan"]["profile_retention"], "long-lived-project-profile")
            self.assertTrue(result["wrapper_receipt"]["receipt_written"])
            self.assertNotIn(str(state), serialized)

            registry = json.loads((state / "owner-registry" / "registry.json").read_text(encoding="utf-8"))
            self.assertEqual(registry["leases"][0]["owner_class"], "codex-managed-project")
            self.assertTrue(list((state / "receipts").glob("*-reserve-project-profile-*.json")))

    def test_project_profile_same_profile_is_exclusive(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            target = "chrome-devtools-mcp:project:pythonproject-langgraph:dev-login"
            receipt_a = write_authorization_receipt(state / "auth-a.json", target=target, session="session-a")
            receipt_b = write_authorization_receipt(state / "auth-b.json", target=target, session="session-b")
            run_cmd(
                [
                    "project-profile",
                    "reserve",
                    "--project",
                    "pythonproject-langgraph",
                    "--profile",
                    "dev-login",
                    "--session",
                    "session-a",
                    "--purpose",
                    "authorized project profile",
                    "--authorization-receipt",
                    str(receipt_a),
                ],
                state,
            )
            blocked = run_cmd(
                [
                    "project-profile",
                    "reserve",
                    "--project",
                    "pythonproject-langgraph",
                    "--profile",
                    "dev-login",
                    "--session",
                    "session-b",
                    "--purpose",
                    "competing project profile",
                    "--authorization-receipt",
                    str(receipt_b),
                ],
                state,
                expect=2,
            )
            self.assertFalse(blocked["ok"])
            self.assertEqual(blocked["error"], "target_already_owned")

    def test_project_profile_live_start_requires_authorization_before_install_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cmd(
                [
                    "project-profile",
                    "start",
                    "--project",
                    "pythonproject-langgraph",
                    "--profile",
                    "dev-login",
                    "--session",
                    "session-a",
                    "--purpose",
                    "live start auth gate",
                ],
                state,
                expect=3,
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"], "project_profile_authorization_required")
            self.assertFalse(result["start_performed"])
            self.assertFalse((state / "owner-registry" / "registry.json").exists())

    def test_project_profile_live_start_rejects_invalid_authorization_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            receipt = write_authorization_receipt(
                state / "auth.json",
                target="chrome-devtools-mcp:project:other-project:dev-login",
                session="session-a",
            )
            result = run_cmd(
                [
                    "project-profile",
                    "start",
                    "--project",
                    "pythonproject-langgraph",
                    "--profile",
                    "dev-login",
                    "--session",
                    "session-a",
                    "--purpose",
                    "live start invalid auth gate",
                    "--authorization-receipt",
                    str(receipt),
                ],
                state,
                expect=3,
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"], "project_profile_authorization_required")
            self.assertIn("authorization_receipt_target_mismatch", result["authorization_blockers"])
            self.assertFalse(result["start_performed"])
            self.assertFalse((state / "owner-registry" / "registry.json").exists())

    def test_project_profile_live_start_with_authorization_requires_install_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            target = "chrome-devtools-mcp:project:pythonproject-langgraph:dev-login"
            receipt = write_authorization_receipt(state / "auth.json", target=target, session="session-a")
            result = run_cmd(
                [
                    "project-profile",
                    "start",
                    "--project",
                    "pythonproject-langgraph",
                    "--profile",
                    "dev-login",
                    "--session",
                    "session-a",
                    "--purpose",
                    "live start install gate",
                    "--authorization-receipt",
                    str(receipt),
                ],
                state,
                expect=3,
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"], "install_receipt_required")
            self.assertFalse(result["start_performed"])
            self.assertFalse((state / "owner-registry" / "registry.json").exists())

    def test_project_profile_live_start_with_install_receipt_still_defers_live_start(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            target = "chrome-devtools-mcp:project:pythonproject-langgraph:dev-login"
            auth = write_authorization_receipt(state / "auth.json", target=target, session="session-a")
            install = state / "install-receipt.json"
            install.write_text(json.dumps({"tool": "chrome-devtools-mcp", "status": "installed-user-level"}), encoding="utf-8")
            result = run_cmd(
                [
                    "project-profile",
                    "start",
                    "--project",
                    "pythonproject-langgraph",
                    "--profile",
                    "dev-login",
                    "--session",
                    "session-a",
                    "--purpose",
                    "live start deferred",
                    "--authorization-receipt",
                    str(auth),
                    "--install-receipt",
                    str(install),
                ],
                state,
                expect=4,
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"], "live_start_not_implemented_repo_local_mvp")
            self.assertFalse(result["start_performed"])
            self.assertFalse((state / "owner-registry" / "registry.json").exists())

    def test_project_profile_release_writes_project_release_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            target = "chrome-devtools-mcp:project:pythonproject-langgraph:dev-login"
            receipt = write_authorization_receipt(state / "auth.json", target=target, session="session-a")
            reserved = run_cmd(
                [
                    "project-profile",
                    "reserve",
                    "--project",
                    "pythonproject-langgraph",
                    "--profile",
                    "dev-login",
                    "--session",
                    "session-a",
                    "--purpose",
                    "project profile release",
                    "--authorization-receipt",
                    str(receipt),
                ],
                state,
            )
            lease_id = reserved["owner_lease"]["lease_id"]
            released = run_cmd(["project-profile", "release", "--lease-id", lease_id, "--session", "session-a"], state)
            self.assertTrue(released["ok"])
            self.assertEqual(released["owner_lease"]["owner_class"], "codex-managed-project")
            self.assertEqual(released["owner_lease"]["status"], "released")
            self.assertTrue(list((state / "receipts").glob("*-release-project-profile-*.json")))


if __name__ == "__main__":
    unittest.main()
