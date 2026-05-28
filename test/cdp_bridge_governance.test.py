import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CDP_GOVERNANCE = ROOT / "tools" / "cdp_bridge_governance.py"
BROWSER_OWNER_REGISTRY = ROOT / "tools" / "browser_owner_registry.py"
OPENCLI_GOVERNANCE = ROOT / "tools" / "opencli_governance.py"
CLI_ANYTHING_GOVERNANCE = ROOT / "tools" / "cli_anything_governance.py"


def run_cdp(args, state_dir, expect=0):
    cmd = [sys.executable, str(CDP_GOVERNANCE), "--state-dir", str(state_dir), *args, "--json"]
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - debug aid
        raise AssertionError(f"invalid json\ncmd={cmd}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}") from exc
    if proc.returncode != expect:
        raise AssertionError(f"unexpected rc {proc.returncode}, expected {expect}\ncmd={cmd}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return data


def run_opencli(args, state_dir, expect=0):
    cmd = [sys.executable, str(OPENCLI_GOVERNANCE), "--state-dir", str(state_dir), *args, "--json"]
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - debug aid
        raise AssertionError(f"invalid json\ncmd={cmd}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}") from exc
    if proc.returncode != expect:
        raise AssertionError(f"unexpected rc {proc.returncode}, expected {expect}\ncmd={cmd}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return data



def run_cli_anything(args, expect=0):
    cmd = [sys.executable, str(CLI_ANYTHING_GOVERNANCE), *args, "--json"]
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - debug aid
        raise AssertionError(f"invalid json\ncmd={cmd}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}") from exc
    if proc.returncode != expect:
        raise AssertionError(f"unexpected rc {proc.returncode}, expected {expect}\ncmd={cmd}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return data, proc.stdout


def run_owner_registry(args, owner_state_dir, expect=0):
    cmd = [sys.executable, str(BROWSER_OWNER_REGISTRY), "--state-dir", str(owner_state_dir), *args, "--json"]
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - debug aid
        raise AssertionError(f"invalid json\ncmd={cmd}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}") from exc
    if proc.returncode != expect:
        raise AssertionError(f"unexpected rc {proc.returncode}, expected {expect}\ncmd={cmd}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return data


def write_authorization_receipt(path: Path, *, target: str, session: str, action: str = "cookie.read") -> Path:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "action": "CDP Bridge sensitive browser action authorization",
                "target": target,
                "scope": f"one-task sensitive CDP action {action}",
                "expiry": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(timespec="seconds"),
                "session": session,
                "operator_confirmation": True,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def write_opencli_authorization_receipt(path: Path, *, target: str, session: str, action: str = "cookie.read") -> Path:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "action": "OpenCLI sensitive browser action authorization",
                "target": target,
                "scope": f"one-task sensitive OpenCLI action {action}",
                "expiry": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(timespec="seconds"),
                "session": session,
                "operator_confirmation": True,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def write_opencli_port_lease_receipt(path: Path, *, port: int = 39300, owner: str = "codex", status: str = "pending_bind") -> Path:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "tool": "codex-port",
                "action": "reserve",
                "sanitized": True,
                "lease_id": "opencli-port-lease-test",
                "owner": owner,
                "port": port,
                "status": status,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def write_opencli_install_receipt(path: Path, *, tool_name: str = "OpenCLI", owner_lane: str = "opencli", smoke_status: str = "pass") -> Path:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "tool_name": tool_name,
                "installed_version": "v0.1.0-test",
                "source_url": "https://example.invalid/opencli.git",
                "install_path": r"C:\Users\lenovo\.codex\tools\opencli",
                "wrapper_path": r"C:\Users\lenovo\.codex\bin\opencli.cmd",
                "state_path": r"C:\Users\lenovo\.codex\state\browser-automation\opencli",
                "smoke_test_command": "opencli --help",
                "smoke_test_result": {"status": smoke_status},
                "updater_command": "opencli-update --pin v0.1.0-test",
                "rollback_pointer": "previous-opencli-pin",
                "owner_lane": owner_lane,
                "redaction_status": "pass",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def reserve_opencli_owner(owner_state: Path, *, target: str = "tab:opencli-1", session: str = "session-a"):
    return run_owner_registry(
        [
            "lease",
            "reserve",
            "--owner-class",
            "codex-managed-isolated",
            "--project",
            "pythonproject-langgraph",
            "--session",
            session,
            "--target",
            target,
            "--profile-path",
            r"C:\Users\lenovo\.codex\state\browser-automation\isolated\opencli-session-a",
            "--purpose",
            "opencli governance unit test",
            "--ttl",
            "300",
        ],
        owner_state,
    )


class CdpBridgeGovernanceTests(unittest.TestCase):
    def test_read_only_tab_inventory_is_allowed_without_owner_or_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cdp(
                [
                    "check",
                    "--action",
                    "tab.list",
                    "--target",
                    r"tab:C:\Users\lenovo\AppData\Local\Google\Chrome\User Data",
                    "--session",
                    "session-a",
                ],
                state,
            )
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertTrue(result["ok"])
            self.assertTrue(result["dispatch_allowed"])
            self.assertEqual(result["action_kind"], "read-only")
            self.assertFalse(result["authorization_required"])
            self.assertFalse(result["owner_required"])
            self.assertFalse(result["safety"]["connects_to_cdp"])
            self.assertFalse(result["safety"]["reads_cookies"])
            self.assertNotIn(str(state), serialized)
            self.assertIn("[REDACTED_PATH]", serialized)

    def test_cookie_read_fails_closed_without_owner_or_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cdp(
                [
                    "check",
                    "--action",
                    "cookie.read",
                    "--target",
                    "tab:debug-1",
                    "--session",
                    "session-a",
                ],
                state,
                expect=3,
            )
            self.assertFalse(result["ok"])
            self.assertFalse(result["dispatch_allowed"])
            self.assertTrue(result["authorization_required"])
            self.assertTrue(result["owner_required"])
            self.assertIn("owner_lease_required", result["blockers"])
            self.assertIn("authorization_receipt_required", result["blockers"])
            self.assertTrue(result["safety"]["requested_action_would_read_cookies"])
            self.assertFalse(result["safety"]["reads_cookies"])

    def test_sensitive_action_passes_with_active_owner_and_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            owner_state = state / "owner-registry"
            target = "tab:debug-1"
            session = "session-a"
            reserved = run_owner_registry(
                [
                    "lease",
                    "reserve",
                    "--owner-class",
                    "codex-managed-isolated",
                    "--project",
                    "pythonproject-langgraph",
                    "--session",
                    session,
                    "--target",
                    target,
                    "--profile-path",
                    r"C:\Users\lenovo\.codex\state\browser-automation\isolated\session-a",
                    "--purpose",
                    "cdp governance unit test",
                    "--ttl",
                    "300",
                ],
                owner_state,
            )
            receipt = write_authorization_receipt(state / "auth.json", target=target, session=session, action="js.evaluate")
            result = run_cdp(
                [
                    "check",
                    "--action",
                    "js.evaluate",
                    "--target",
                    target,
                    "--session",
                    session,
                    "--owner-lease-id",
                    reserved["lease"]["lease_id"],
                    "--authorization-receipt",
                    str(receipt),
                ],
                state,
            )
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertTrue(result["ok"])
            self.assertTrue(result["dispatch_allowed"])
            self.assertEqual(result["owner_lease"]["owner_class"], "codex-managed-isolated")
            self.assertTrue(result["owner_verified"])
            self.assertTrue(result["authorization_verified"])
            self.assertTrue(result["safety"]["requested_action_would_execute_javascript"])
            self.assertFalse(result["safety"]["executes_javascript"])
            self.assertNotIn(str(state), serialized)

    def test_click_type_and_navigate_are_sensitive_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            for action in ["mouse.click", "keyboard.type", "page.navigate"]:
                result = run_cdp(
                    [
                        "check",
                        "--action",
                        action,
                        "--target",
                        "tab:debug-1",
                        "--session",
                        "session-a",
                    ],
                    state,
                    expect=3,
                )
                self.assertFalse(result["dispatch_allowed"], action)
                self.assertEqual(result["action_kind"], "sensitive", action)
                self.assertIn("owner_lease_required", result["blockers"], action)
                self.assertIn("authorization_receipt_required", result["blockers"], action)

    def test_unknown_action_is_blocked_as_sensitive(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_cdp(
                [
                    "check",
                    "--action",
                    "experimental.do-anything",
                    "--target",
                    "tab:debug-1",
                    "--session",
                    "session-a",
                ],
                state,
                expect=3,
            )
            self.assertFalse(result["ok"])
            self.assertEqual(result["action_kind"], "unknown")
            self.assertIn("unknown_action", result["blockers"])
            self.assertIn("owner_lease_required", result["blockers"])


class OpenCliGovernanceTests(unittest.TestCase):
    def test_read_only_inspection_requires_owner_but_not_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            missing = run_opencli(
                [
                    "check",
                    "--action",
                    "session.inspect",
                    "--target",
                    r"tab:C:\Users\lenovo\AppData\Local\Google\Chrome\User Data",
                    "--session",
                    "session-a",
                ],
                state,
                expect=3,
            )
            serialized_missing = json.dumps(missing, ensure_ascii=False)
            self.assertFalse(missing["dispatch_allowed"])
            self.assertTrue(missing["owner_required"])
            self.assertFalse(missing["authorization_required"])
            self.assertIn("owner_lease_required", missing["blockers"])
            self.assertIn("[REDACTED_PATH]", serialized_missing)

            owner_state = state / "owner-registry"
            lease = reserve_opencli_owner(owner_state)
            port_receipt = write_opencli_port_lease_receipt(state / "port-lease.json")
            allowed = run_opencli(
                [
                    "--owner-state-dir",
                    str(owner_state),
                    "check",
                    "--action",
                    "session.inspect",
                    "--target",
                    "tab:opencli-1",
                    "--session",
                    "session-a",
                    "--owner-lease-id",
                    lease["lease"]["lease_id"],
                    "--port-lease-receipt",
                    str(port_receipt),
                ],
                state,
            )
            serialized_allowed = json.dumps(allowed, ensure_ascii=False)
            self.assertTrue(allowed["ok"])
            self.assertTrue(allowed["dispatch_allowed"])
            self.assertEqual(allowed["adapter_mode"], "on-demand")
            self.assertTrue(allowed["port_policy"]["lease_verified"])
            self.assertFalse(allowed["port_policy"]["hard_coded_port_allowed"])
            self.assertFalse(allowed["authorization_required"])
            self.assertTrue(allowed["owner_verified"])
            self.assertFalse(allowed["safety"]["connects_to_browser"])
            self.assertFalse(allowed["safety"]["starts_opencli"])
            self.assertFalse(allowed["safety"]["autoload_allowed"])
            self.assertNotIn(str(state), serialized_allowed)

    def test_persistent_adapter_mode_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            owner_state = state / "owner-registry"
            lease = reserve_opencli_owner(owner_state)
            port_receipt = write_opencli_port_lease_receipt(state / "port-lease.json")
            result = run_opencli(
                [
                    "--owner-state-dir",
                    str(owner_state),
                    "check",
                    "--action",
                    "session.inspect",
                    "--target",
                    "tab:opencli-1",
                    "--session",
                    "session-a",
                    "--owner-lease-id",
                    lease["lease"]["lease_id"],
                    "--port-lease-receipt",
                    str(port_receipt),
                    "--adapter-mode",
                    "always-on",
                ],
                state,
                expect=3,
            )
            self.assertFalse(result["dispatch_allowed"])
            self.assertIn("opencli_must_remain_on_demand", result["blockers"])
            self.assertFalse(result["safety"]["autoload_allowed"])

    def test_opencli_cookie_read_fails_closed_without_owner_or_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            result = run_opencli(
                [
                    "check",
                    "--action",
                    "cookie.read",
                    "--target",
                    "tab:opencli-1",
                    "--session",
                    "session-a",
                ],
                state,
                expect=3,
            )
            self.assertFalse(result["dispatch_allowed"])
            self.assertTrue(result["owner_required"])
            self.assertTrue(result["authorization_required"])
            self.assertIn("owner_lease_required", result["blockers"])
            self.assertIn("authorization_receipt_required", result["blockers"])
            self.assertTrue(result["safety"]["requested_action_would_read_cookies"])
            self.assertFalse(result["safety"]["reads_cookies"])

    def test_opencli_sensitive_action_passes_with_active_owner_and_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            owner_state = state / "owner-registry"
            target = "tab:opencli-1"
            session = "session-a"
            lease = reserve_opencli_owner(owner_state, target=target, session=session)
            receipt = write_opencli_authorization_receipt(state / "auth.json", target=target, session=session, action="js.evaluate")
            port_receipt = write_opencli_port_lease_receipt(state / "port-lease.json")
            result = run_opencli(
                [
                    "--owner-state-dir",
                    str(owner_state),
                    "check",
                    "--action",
                    "js.evaluate",
                    "--target",
                    target,
                    "--session",
                    session,
                    "--owner-lease-id",
                    lease["lease"]["lease_id"],
                    "--authorization-receipt",
                    str(receipt),
                    "--port-lease-receipt",
                    str(port_receipt),
                ],
                state,
            )
            self.assertTrue(result["dispatch_allowed"])
            self.assertTrue(result["port_policy"]["lease_verified"])
            self.assertTrue(result["owner_verified"])
            self.assertTrue(result["authorization_verified"])
            self.assertTrue(result["safety"]["requested_action_would_execute_javascript"])
            self.assertFalse(result["safety"]["executes_javascript"])

    def test_opencli_hard_coded_port_and_missing_port_lease_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            owner_state = state / "owner-registry"
            lease = reserve_opencli_owner(owner_state)
            missing = run_opencli(
                [
                    "--owner-state-dir",
                    str(owner_state),
                    "check",
                    "--action",
                    "session.inspect",
                    "--target",
                    "tab:opencli-1",
                    "--session",
                    "session-a",
                    "--owner-lease-id",
                    lease["lease"]["lease_id"],
                ],
                state,
                expect=3,
            )
            self.assertFalse(missing["dispatch_allowed"])
            self.assertIn("opencli_port_lease_receipt_required", missing["blockers"])

            port_receipt = write_opencli_port_lease_receipt(state / "port-lease.json")
            fixed = run_opencli(
                [
                    "--owner-state-dir",
                    str(owner_state),
                    "check",
                    "--action",
                    "session.inspect",
                    "--target",
                    "tab:opencli-1",
                    "--session",
                    "session-a",
                    "--owner-lease-id",
                    lease["lease"]["lease_id"],
                    "--port",
                    "39300",
                    "--port-lease-receipt",
                    str(port_receipt),
                ],
                state,
                expect=3,
            )
            self.assertFalse(fixed["dispatch_allowed"])
            self.assertIn("opencli_port_must_be_auto", fixed["blockers"])
            self.assertEqual(fixed["port_policy"]["port_mode"], "fixed")

    def test_opencli_port_lease_must_belong_to_codex_opencli_range(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            owner_state = state / "owner-registry"
            lease = reserve_opencli_owner(owner_state)
            wrong_range = write_opencli_port_lease_receipt(state / "port-lease.json", port=40000)
            result = run_opencli(
                [
                    "--owner-state-dir",
                    str(owner_state),
                    "check",
                    "--action",
                    "session.inspect",
                    "--target",
                    "tab:opencli-1",
                    "--session",
                    "session-a",
                    "--owner-lease-id",
                    lease["lease"]["lease_id"],
                    "--port-lease-receipt",
                    str(wrong_range),
                ],
                state,
                expect=3,
            )
            self.assertFalse(result["dispatch_allowed"])
            self.assertIn("opencli_port_lease_range_mismatch", result["blockers"])

    def test_opencli_live_start_requires_install_receipt_with_owner_and_port_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            owner_state = state / "owner-registry"
            target = "tab:opencli-1"
            session = "session-a"
            lease = reserve_opencli_owner(owner_state, target=target, session=session)
            port_receipt = write_opencli_port_lease_receipt(state / "port-lease.json")
            result = run_opencli(
                [
                    "--owner-state-dir",
                    str(owner_state),
                    "start",
                    "--target",
                    target,
                    "--session",
                    session,
                    "--owner-lease-id",
                    lease["lease"]["lease_id"],
                    "--port-lease-receipt",
                    str(port_receipt),
                ],
                state,
                expect=3,
            )
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"], "opencli_live_start_blocked")
            self.assertFalse(result["start_performed"])
            self.assertFalse(result["safety"]["starts_opencli"])
            self.assertTrue(result["owner_verified"])
            self.assertIn("install_receipt_required", result["blockers"])
            self.assertNotIn(str(state), serialized)

    def test_opencli_live_start_requires_owner_evidence_with_install_and_port_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            install_receipt = write_opencli_install_receipt(state / "install.json")
            port_receipt = write_opencli_port_lease_receipt(state / "port-lease.json")
            result = run_opencli(
                [
                    "start",
                    "--target",
                    "tab:opencli-1",
                    "--session",
                    "session-a",
                    "--install-receipt",
                    str(install_receipt),
                    "--port-lease-receipt",
                    str(port_receipt),
                ],
                state,
                expect=3,
            )
            self.assertFalse(result["ok"])
            self.assertFalse(result["start_performed"])
            self.assertTrue(result["install_receipt_verified"])
            self.assertIn("owner_lease_required", result["blockers"])

    def test_opencli_live_start_with_all_evidence_still_defers_repo_local_mvp(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            owner_state = state / "owner-registry"
            target = "tab:opencli-1"
            session = "session-a"
            lease = reserve_opencli_owner(owner_state, target=target, session=session)
            install_receipt = write_opencli_install_receipt(state / "install.json")
            port_receipt = write_opencli_port_lease_receipt(state / "port-lease.json")
            result = run_opencli(
                [
                    "--owner-state-dir",
                    str(owner_state),
                    "start",
                    "--target",
                    target,
                    "--session",
                    session,
                    "--owner-lease-id",
                    lease["lease"]["lease_id"],
                    "--install-receipt",
                    str(install_receipt),
                    "--port-lease-receipt",
                    str(port_receipt),
                ],
                state,
                expect=4,
            )
            serialized = json.dumps(result, ensure_ascii=False)
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"], "live_start_not_implemented_repo_local_mvp")
            self.assertEqual(result["blockers"], ["live_start_not_implemented_repo_local_mvp"])
            self.assertFalse(result["start_performed"])
            self.assertTrue(result["owner_verified"])
            self.assertTrue(result["install_receipt_verified"])
            self.assertTrue(result["port_policy"]["lease_verified"])
            self.assertFalse(result["safety"]["starts_opencli"])
            self.assertFalse(result["safety"]["connects_to_browser"])
            self.assertFalse(result["safety"]["mutates_user_codex_config"])
            self.assertNotIn(str(state), serialized)

    def test_opencli_click_type_navigate_and_unknown_actions_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            for action in ["mouse.click", "keyboard.type", "page.navigate", "experimental.bind-personal-tab"]:
                result = run_opencli(
                    [
                        "check",
                        "--action",
                        action,
                        "--target",
                        "tab:opencli-1",
                        "--session",
                        "session-a",
                    ],
                    state,
                    expect=3,
                )
                self.assertFalse(result["dispatch_allowed"], action)
                self.assertIn("owner_lease_required", result["blockers"], action)
                self.assertIn("authorization_receipt_required", result["blockers"], action)
                if action.startswith("experimental"):
                    self.assertIn("unknown_action", result["blockers"])


    def test_cli_anything_install_record_writes_pinned_receipt_with_sanitized_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipt_dir = root / "receipts"
            install_path = root / "external" / "cli-anything"
            wrapper_path = root / "tools" / "cli-anything" / "cli-anything.cmd"
            state_path = root / "state" / "cli-anything"
            result, stdout = run_cli_anything(
                [
                    "install-record",
                    "--receipt-dir",
                    str(receipt_dir),
                    "--pin",
                    "v0.1.0",
                    "--install-path",
                    str(install_path),
                    "--wrapper-path",
                    str(wrapper_path),
                    "--state-path",
                    str(state_path),
                    "--smoke-command",
                    "cli-anything --help",
                    "--rollback-pointer",
                    "remove-created-cli-anything-directories",
                ]
            )
            self.assertTrue(result["ok"])
            self.assertTrue(result["receipt_written"])
            self.assertEqual(result["summary"]["tool_name"], "CLI-Anything")
            self.assertEqual(result["summary"]["owner_lane"], "cli-anything")
            self.assertEqual(result["summary"]["status"], "reference-only")
            self.assertEqual(result["summary"]["pinned_ref"], "v0.1.0")
            self.assertTrue(result["summary"]["harness_generation_only"])
            self.assertFalse(result["summary"]["hard_loads_skills"])
            self.assertFalse(result["safety"]["installs_cli_anything"])
            self.assertFalse(result["safety"]["hard_loads_skills"])
            self.assertNotIn(str(root), stdout)
            self.assertNotIn(str(install_path), stdout)
            receipt = receipt_dir / "cli-anything.lock.json"
            self.assertTrue(receipt.exists())

            validated, _ = run_cli_anything(["validate", "--receipt", str(receipt)])
            self.assertTrue(validated["ok"])
            self.assertTrue(validated["receipt_valid"])

    def test_cli_anything_hard_load_skills_is_blocked_without_writing_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipt_dir = root / "receipts"
            result, _ = run_cli_anything(
                [
                    "install-record",
                    "--receipt-dir",
                    str(receipt_dir),
                    "--pin",
                    "v0.1.0",
                    "--install-path",
                    str(root / "external" / "cli-anything"),
                    "--wrapper-path",
                    str(root / "tools" / "cli-anything.cmd"),
                    "--state-path",
                    str(root / "state" / "cli-anything"),
                    "--smoke-command",
                    "cli-anything --help",
                    "--rollback-pointer",
                    "previous-version",
                    "--hard-load-skills",
                ],
                expect=3,
            )
            self.assertFalse(result["ok"])
            self.assertFalse(result["receipt_written"])
            self.assertIn("hard_load_skills_must_be_false", result["blockers"])
            self.assertFalse((receipt_dir / "cli-anything.lock.json").exists())

    def test_cli_anything_update_requires_smoke_pass_and_preserves_rollback_pin(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipt_dir = root / "receipts"
            run_cli_anything(
                [
                    "install-record",
                    "--receipt-dir",
                    str(receipt_dir),
                    "--pin",
                    "v0.1.0",
                    "--install-path",
                    str(root / "external" / "cli-anything"),
                    "--wrapper-path",
                    str(root / "tools" / "cli-anything.cmd"),
                    "--state-path",
                    str(root / "state" / "cli-anything"),
                    "--smoke-command",
                    "cli-anything --help",
                    "--rollback-pointer",
                    "remove-created-cli-anything-directories",
                ]
            )
            current = receipt_dir / "cli-anything.lock.json"

            blocked, _ = run_cli_anything(
                [
                    "update-plan",
                    "--current-receipt",
                    str(current),
                    "--new-pin",
                    "v0.1.1",
                    "--staging-dir",
                    str(root / "staging" / "cli-anything"),
                    "--smoke-status",
                    "fail",
                ],
                expect=3,
            )
            self.assertFalse(blocked["pin_switch_allowed"])
            self.assertIn("smoke_result_not_passed", blocked["blockers"])
            self.assertFalse(blocked["safety"]["network_fetch_performed"])

            updated, stdout = run_cli_anything(
                [
                    "update-record",
                    "--current-receipt",
                    str(current),
                    "--receipt-dir",
                    str(receipt_dir),
                    "--new-pin",
                    "v0.1.1",
                    "--staging-dir",
                    str(root / "staging" / "cli-anything"),
                    "--smoke-command",
                    "cli-anything --help",
                    "--smoke-status",
                    "pass",
                ]
            )
            self.assertTrue(updated["pin_switch_allowed"])
            self.assertEqual(updated["rollback_pointer"]["previous_pin"], "v0.1.0")
            self.assertNotIn(str(root), stdout)

            update_files = sorted(receipt_dir.glob("cli-anything.update.*.json"))
            self.assertEqual(len(update_files), 1)
            rollback, _ = run_cli_anything(["rollback-plan", "--receipt", str(update_files[0])])
            self.assertTrue(rollback["rollback_allowed"])
            self.assertFalse(rollback["rollback_performed"])
            self.assertTrue(rollback["requires_operator_execution"])
            self.assertEqual(rollback["rollback_pointer"]["previous_pin"], "v0.1.0")

    def test_cli_anything_harness_plan_is_generation_only_and_blocks_hard_load(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            allowed, stdout = run_cli_anything(
                [
                    "harness-plan",
                    "--capability",
                    "design wecom-cli process inventory without reading message content",
                    "--output-dir",
                    str(root / "generated" / "wecom-cli"),
                    "--target-process",
                    "WXWork.exe",
                ]
            )
            self.assertTrue(allowed["ok"])
            self.assertTrue(allowed["harness_generation_allowed"])
            self.assertTrue(allowed["repo_local_source_required"])
            self.assertTrue(allowed["authorization_gate_required_for_live_control"])
            self.assertFalse(allowed["safety"]["runs_cli_anything"])
            self.assertFalse(allowed["safety"]["hard_loads_skills"])
            self.assertNotIn(str(root), stdout)

            blocked, _ = run_cli_anything(
                [
                    "harness-plan",
                    "--capability",
                    "bulk-load skills into CLI-Anything",
                    "--output-dir",
                    str(root / "generated"),
                    "--hard-load-skills",
                ],
                expect=3,
            )
            self.assertFalse(blocked["harness_generation_allowed"])
            self.assertIn("hard_load_skills_must_be_false", blocked["blockers"])


if __name__ == "__main__":
    unittest.main()
