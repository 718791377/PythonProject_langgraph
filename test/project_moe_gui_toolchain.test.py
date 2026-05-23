from __future__ import annotations

import hashlib
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
PHASE1_READINESS = REPO_ROOT / "tools" / "project_moe_gui_toolchain" / "check_project_moe_phase1_readiness.py"


STATEFUL_MODE_CLI_TEMPLATE = r'''
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_LABEL = "__PROJECT_LABEL__"
AGENT_NAME = "__AGENT_NAME__"
NAMESPACE = "__NAMESPACE__"
DEFAULT_SESSION_ID = "__SESSION_ID__"
ROOT = Path.cwd()
STATE_ROOT = ROOT / ".omx" / "state" / NAMESPACE
SESSIONS_ROOT = STATE_ROOT / "sessions"
PROJECT_DEFAULT = STATE_ROOT / "project-default.json"

def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def arg_value(name: str) -> str | None:
    if name not in sys.argv:
        return None
    index = sys.argv.index(name)
    if index + 1 >= len(sys.argv):
        return None
    return sys.argv[index + 1]

def read_json(path: Path, default: dict | None = None) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return dict(default or {})
    return payload if isinstance(payload, dict) else dict(default or {})

def read_json_with_validity(path: Path) -> tuple[dict, bool, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}, False, "invalid_json"
    if not isinstance(payload, dict):
        return {}, False, "invalid_shape"
    if payload.get("schema_version") not in {None, 1}:
        return payload, False, "unsupported_schema_version"
    return payload, True, "ok"

def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def session_path(session_id: str) -> Path:
    return SESSIONS_ROOT / f"{session_id}.json"

def project_default_enabled() -> bool:
    payload = read_json(PROJECT_DEFAULT)
    return bool(payload.get("enabled", False))

def write_project(enabled: bool) -> tuple[dict, bool]:
    before = read_json(PROJECT_DEFAULT, {"enabled": False}).get("enabled", False)
    before_payload = read_json(PROJECT_DEFAULT, {"enabled": False})
    payload = {
        "schema_version": 1,
        "project_label": PROJECT_LABEL,
        "agent_name": AGENT_NAME,
        "state_namespace": NAMESPACE,
        "scope": "project-default",
        "enabled": enabled,
        "updated_at": now(),
        "reason": "project-on" if enabled else "project-off",
    }
    write_json(PROJECT_DEFAULT, payload)
    SESSIONS_ROOT.mkdir(parents=True, exist_ok=True)
    skipped_invalid_records = []
    changed_paths = [str(PROJECT_DEFAULT)]
    for path in SESSIONS_ROOT.glob("*.json"):
        session, valid, status_reason = read_json_with_validity(path)
        if not valid:
            skipped_invalid_records.append({"path": str(path), "token": status_reason})
            continue
        if session.get("override_origin") == "manual-session":
            continue
        session.update({"enabled": enabled, "project_label": PROJECT_LABEL, "override_origin": "project-propagated", "updated_at": now()})
        write_json(path, session)
        changed_paths.append(str(path))
    after_payload = read_json(PROJECT_DEFAULT)
    return {
        "before": before_payload,
        "after": after_payload,
        "changed_paths": changed_paths,
        "skipped_invalid_records": skipped_invalid_records,
        "lock_status": "not_locked_fixture",
        "audit_path": str(STATE_ROOT / "audit.log"),
        "atomic_write": True,
    }, bool(before) == enabled

def write_session(session_id: str, enabled: bool) -> tuple[dict, bool]:
    path = session_path(session_id)
    before = read_json(path, {"enabled": False}).get("enabled", False)
    before_payload = read_json(path, {"enabled": False})
    payload = read_json(path)
    payload.update({
        "schema_version": 1,
        "project_label": PROJECT_LABEL,
        "agent_name": AGENT_NAME,
        "state_namespace": NAMESPACE,
        "scope": "session",
        "session_id": session_id,
        "enabled": enabled,
        "override_origin": "manual-session",
        "token": "ok",
        "updated_at": now(),
        "reason": "session-on" if enabled else "session-off",
    })
    write_json(path, payload)
    return {
        "before": before_payload,
        "after": read_json(path),
        "changed_paths": [str(path)],
        "skipped_invalid_records": [],
        "lock_status": "not_locked_fixture",
        "audit_path": str(STATE_ROOT / "audit.log"),
        "atomic_write": True,
    }, bool(before) == enabled

def list_sessions() -> list[dict]:
    rows = []
    SESSIONS_ROOT.mkdir(parents=True, exist_ok=True)
    for path in sorted(SESSIONS_ROOT.glob("*.json")):
        payload, valid, status_reason = read_json_with_validity(path)
        if not valid:
            rows.append({
                "project_label": PROJECT_LABEL,
                "session_id": path.stem,
                "enabled": False,
                "effective_enabled": False,
                "valid": False,
                "token": status_reason,
                "source": "invalid-record",
                "lifecycle_status": "invalid",
                "status_reason": status_reason,
            })
            continue
        source = payload.get("override_origin", "project-propagated")
        if payload.get("schema_version") is None:
            source = "legacy-compatible"
        rows.append({
            "project_label": PROJECT_LABEL,
            "session_id": payload.get("session_id") or path.stem,
            "enabled": bool(payload.get("enabled", False)),
            "effective_enabled": bool(payload.get("enabled", False)),
            "valid": True,
            "token": "ok",
            "source": source,
            "lifecycle_status": payload.get("lifecycle_status", "active"),
            "status_reason": "ok",
        })
    return rows

def envelope(command: str, **extra: object) -> dict:
    payload = {
        "schema_version": 1,
        "command": command,
        "ok": True,
        "token": "ok",
        "exit_code": 0,
        "message": "ok",
        "project_label": PROJECT_LABEL,
        "project_root": str(ROOT),
        "agent_name": AGENT_NAME,
        "state_namespace": NAMESPACE,
        "generated_at": now(),
        "cli_contract": "project-moe-cli-v1",
        "warnings": [],
        "errors": [],
    }
    payload.update(extra)
    return payload

def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    session_id = arg_value("--session-id") or DEFAULT_SESSION_ID
    if command == "project-status":
        payload = envelope(command, project_default_enabled=project_default_enabled(), project_default=read_json(PROJECT_DEFAULT, {"enabled": False}), registered_session_count=len(list_sessions()), sessions_state_root=str(SESSIONS_ROOT), git_branch="main")
    elif command == "list-sessions":
        rows = list_sessions()
        payload = envelope(command, sessions=rows, counts={"total": len(rows), "valid": len(rows)})
    elif command == "status":
        session_payload = read_json(session_path(session_id), {})
        if "enabled" in session_payload:
            effective = bool(session_payload["enabled"])
            effective_source = "session"
        else:
            effective = project_default_enabled()
            effective_source = "project-default"
        payload = envelope(command, session_id=session_id, effective_enabled=effective, effective_source=effective_source)
    elif command == "assert-on":
        session_payload = read_json(session_path(session_id), {})
        effective = bool(session_payload.get("enabled", project_default_enabled()))
        payload = envelope(command, session_id=session_id, effective_enabled=effective, effective_source="session" if "enabled" in session_payload else "project-default")
        if not effective:
            payload.update(ok=False, token="disabled", exit_code=1, message="MOE mode is disabled")
    elif command == "project-on":
        changed, no_op = write_project(True)
        payload = envelope(command, project_default_enabled=True, changed_scope="project-default", no_op=no_op, changed=changed, **changed)
    elif command == "project-off":
        changed, no_op = write_project(False)
        payload = envelope(command, project_default_enabled=False, changed_scope="project-default", no_op=no_op, changed=changed, **changed)
    elif command == "on":
        changed, no_op = write_session(session_id, True)
        payload = envelope(command, session_id=session_id, effective_enabled=True, changed_scope="session", no_op=no_op, changed=changed, **changed)
    elif command == "off":
        changed, no_op = write_session(session_id, False)
        payload = envelope(command, session_id=session_id, effective_enabled=False, changed_scope="session", no_op=no_op, changed=changed, **changed)
    else:
        payload = {"schema_version": 1, "command": command, "ok": False, "token": "usage_error", "exit_code": 2, "message": "unsupported"}
    print(json.dumps(payload, ensure_ascii=False))
    return int(payload.get("exit_code", 0))

if __name__ == "__main__":
    raise SystemExit(main())
'''


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

    def make_project(self, root: Path, *, with_agent: bool = True, cli_variant: str = "valid") -> None:
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
        extra_payload = ""
        if cli_variant == "missing_effective_source":
            extra_payload = 'payload.pop("effective_source", None)\n'
        elif cli_variant == "private_field_exposed":
            extra_payload = 'payload["raw_session_id"] = "secret-session-value"\npayload["private_prompt_text"] = "never expose prompt"\n'
        elif cli_variant == "bad_list_sessions_counts":
            extra_payload = 'payload.pop("counts", None)\n'
        elif cli_variant == "write_missing_changed_paths":
            extra_payload = 'payload.pop("changed_paths", None)\n'
        elif cli_variant == "write_scope_mismatch":
            extra_payload = 'payload["changed_scope"] = "project-default" if cmd in {"on", "off"} else "session"\n'
        elif cli_variant == "write_private_field_exposed":
            extra_payload = 'payload["raw_session_id"] = "secret-session-value"\npayload["private_prompt_text"] = "never expose prompt"\n'
        elif cli_variant == "write_missing_atomic_write":
            extra_payload = 'payload.pop("atomic_write", None)\n'
        elif cli_variant == "write_atomic_write_false":
            extra_payload = 'payload["atomic_write"] = False\n'
        elif cli_variant == "write_lock_timeout":
            extra_payload = 'payload["lock_status"] = "lock_timeout"\n'
        (root / "tools" / "thesis_moe_mode.py").write_text(
            f"""
from __future__ import annotations
import json
import sys
cmd = sys.argv[1]
payload = {{
    "schema_version": 1,
    "command": cmd,
    "ok": True,
    "token": "ok",
    "exit_code": 0,
    "message": "ok",
    "project_root": str(__import__('pathlib').Path.cwd()),
    "agent_name": "thesis-moe-mentor",
    "state_namespace": "thesis_moe",
    "generated_at": "2026-05-23T00:00:00+00:00",
    "warnings": [],
    "errors": [],
    "cli_contract": "project-moe-cli-v1",
    "sessions": [],
    "counts": {{"total": 0, "valid": 0}},
}}
if cmd == "list-sessions":
    payload["message"] = "session list read"
    payload["sessions"] = [
        {{"session_id": "session-1234567890abcdef", "enabled": False, "effective_enabled": False, "valid": True, "token": "ok", "source": "manual-session", "lifecycle_status": "active"}}
    ]
elif cmd == "project-status":
    payload["message"] = "project status read"
    payload["project_default_enabled"] = False
    payload["registered_session_count"] = 1
    payload["valid_session_count"] = 1
    payload["invalid_session_count"] = 0
    payload["git_branch"] = "main"
elif cmd == "status":
    payload["message"] = "mentor mode disabled"
    payload["effective_enabled"] = False
    payload["effective_source"] = "project-default"
    payload["session_id"] = "sessio?cdef"
elif cmd == "project-on":
    payload["message"] = "project default enabled"
    payload["project_default_enabled"] = True
    payload["before"] = {{"enabled": False}}
    payload["after"] = {{"enabled": True}}
    payload["changed_scope"] = "project-default"
    payload["changed_paths"] = [".omx/state/thesis_moe/project-default.json"]
    payload["skipped_invalid_records"] = []
    payload["lock_status"] = "not_locked_fixture"
    payload["audit_path"] = ".omx/state/thesis_moe/audit.log"
    payload["atomic_write"] = True
    payload["no_op"] = False
elif cmd == "project-off":
    payload["message"] = "project default disabled"
    payload["project_default_enabled"] = False
    payload["before"] = {{"enabled": True}}
    payload["after"] = {{"enabled": False}}
    payload["changed_scope"] = "project-default"
    payload["changed_paths"] = [".omx/state/thesis_moe/project-default.json"]
    payload["skipped_invalid_records"] = []
    payload["lock_status"] = "not_locked_fixture"
    payload["audit_path"] = ".omx/state/thesis_moe/audit.log"
    payload["atomic_write"] = True
    payload["no_op"] = False
elif cmd == "on":
    payload["message"] = "session enabled"
    payload["effective_enabled"] = True
    payload["session_id"] = "session-1234567890abcdef"
    payload["before"] = {{"enabled": False}}
    payload["after"] = {{"enabled": True}}
    payload["changed_scope"] = "session"
    payload["changed_paths"] = [".omx/state/thesis_moe/sessions/session-1234567890abcdef.json"]
    payload["skipped_invalid_records"] = []
    payload["lock_status"] = "not_locked_fixture"
    payload["audit_path"] = ".omx/state/thesis_moe/audit.log"
    payload["atomic_write"] = True
    payload["no_op"] = False
elif cmd == "off":
    payload["message"] = "session disabled"
    payload["effective_enabled"] = False
    payload["session_id"] = "session-1234567890abcdef"
    payload["before"] = {{"enabled": True}}
    payload["after"] = {{"enabled": False}}
    payload["changed_scope"] = "session"
    payload["changed_paths"] = [".omx/state/thesis_moe/sessions/session-1234567890abcdef.json"]
    payload["skipped_invalid_records"] = []
    payload["lock_status"] = "not_locked_fixture"
    payload["audit_path"] = ".omx/state/thesis_moe/audit.log"
    payload["atomic_write"] = True
    payload["no_op"] = False
else:
    payload = {{"schema_version": 1, "command": cmd, "ok": False, "token": "usage_error", "exit_code": 2, "message": "unsupported", "cli_contract": "project-moe-cli-v1"}}
{extra_payload}print(json.dumps(payload))
""".lstrip(),
            encoding="utf-8",
        )

    def make_stateful_project(
        self,
        root: Path,
        *,
        project_label: str,
        session_id: str,
        agent_name: str = "thesis-moe-mentor",
        namespace: str = "thesis_moe",
    ) -> None:
        (root / ".git").mkdir()
        (root / ".codex" / "agents").mkdir(parents=True)
        (root / "tools").mkdir()
        (root / "MOE.md").write_text(f"# Private MOE prompt for {project_label}\n", encoding="utf-8")
        (root / ".codex" / "agents" / f"{agent_name}.toml").write_text(
            f'name = "{agent_name}"\n'
            f'description = "Fixture MOE agent for {project_label}."\n'
            'developer_instructions = "Use only project-local fixture state."\n'
            "\n[project]\n"
            'scope = "repo-local"\n'
            f'state_namespace = "{namespace}"\n'
            'private_prompt_source = "MOE.md"\n'
            'private_prompt_policy = "do-not-copy-full-content"\n'
            "\n[moe]\n"
            'kind = "project-moe-agent"\n'
            'family = "project-specific"\n'
            "requires_manual_enable = true\n"
            f'project_default_state = ".omx/state/{namespace}/project-default.json"\n'
            f'session_state_dir = ".omx/state/{namespace}/sessions"\n'
            "\n[dispatch]\n"
            'mode = "brief-based"\n'
            'forbidden = ["full-history-fork-with-custom-role"]\n'
            'fallback = ["main-session-takeover", "durable-brief"]\n'
            "\n[extensions]\n",
            encoding="utf-8",
        )
        state_root = root / ".omx" / "state" / namespace
        sessions_root = state_root / "sessions"
        sessions_root.mkdir(parents=True)
        (state_root / "private-note.json").write_text(
            json.dumps({"project_label": project_label, "private": True}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (sessions_root / f"{session_id}.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_label": project_label,
                    "agent_name": agent_name,
                    "state_namespace": namespace,
                    "scope": "session",
                    "session_id": session_id,
                    "enabled": False,
                    "override_origin": "project-propagated",
                    "token": "ok",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (root / "tools" / "thesis_moe_mode.py").write_text(
            STATEFUL_MODE_CLI_TEMPLATE.replace("__PROJECT_LABEL__", project_label)
            .replace("__AGENT_NAME__", agent_name)
            .replace("__NAMESPACE__", namespace)
            .replace("__SESSION_ID__", session_id)
            .lstrip(),
            encoding="utf-8",
        )

    def add_phase1_wrappers_and_startup_hook(self, root: Path) -> None:
        (root / "thesis-moe-on.cmd").write_text(
            '@echo off\npython "%~dp0tools\\thesis_moe_mode.py" project-on --json\nexit /b %ERRORLEVEL%\n',
            encoding="utf-8",
        )
        (root / "thesis-moe-off.cmd").write_text(
            '@echo off\npython "%~dp0tools\\thesis_moe_mode.py" project-off --json\nexit /b %ERRORLEVEL%\n',
            encoding="utf-8",
        )
        (root / "AGENTS.md").write_text(
            "On startup, resume, continue, or phase change, run `python .\\tools\\thesis_moe_mode.py status --json` before applying the thesis MOE rules.\n",
            encoding="utf-8",
        )
        docs_dir = root / "docs_bilingual" / "operations"
        docs_dir.mkdir(parents=True, exist_ok=True)
        (docs_dir / "thesis_moe_mode_usage.zh-CN.md").write_text(
            "# Thesis MOE mode usage\n\n"
            "- Use `python .\\tools\\thesis_moe_mode.py project-on` or `thesis-moe-on.cmd` to enable the project default.\n"
            "- Use `python .\\tools\\thesis_moe_mode.py project-off` or `thesis-moe-off.cmd` to disable the project default.\n"
            "- Use `python .\\tools\\thesis_moe_mode.py project-status --json` for project-default state.\n"
            "- Use `python .\\tools\\thesis_moe_mode.py list-sessions --json` for redacted session rows.\n"
            "- Use `python .\\tools\\thesis_moe_mode.py status --json` for the effective current session state.\n"
            "- Use `python .\\tools\\thesis_moe_mode.py assert-on` when a hard enabled assertion is required.\n"
            "- Use `python .\\tools\\thesis_moe_mode.py on --session-id <id>` or `off --session-id <id>` for a single session override.\n",
            encoding="utf-8",
        )

    def git_commit_all(self, root: Path) -> None:
        commands = [
            ["git", "-C", str(root), "init"],
            ["git", "-C", str(root), "add", "-A"],
            ["git", "-C", str(root), "-c", "user.name=Project MOE Test", "-c", "user.email=project-moe@example.invalid", "commit", "-m", "initial fixture"],
        ]
        for command in commands:
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
            self.assertEqual(result.returncode, 0, f"{command}\nstdout={result.stdout}\nstderr={result.stderr}")

    def file_digest(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def private_project_digests(self, project: Path, *, agent_name: str = "thesis-moe-mentor", namespace: str = "thesis_moe") -> dict[str, str]:
        private_paths = {
            "agent_toml": project / ".codex" / "agents" / f"{agent_name}.toml",
            "moe_prompt": project / "MOE.md",
            "private_state": project / ".omx" / "state" / namespace / "private-note.json",
        }
        return {key: self.file_digest(path) for key, path in private_paths.items()}

    def test_phase1_readiness_checker_accepts_clean_target_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-ready"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-ready", session_id="session-phase1-ready")
            self.add_phase1_wrappers_and_startup_hook(project)
            self.git_commit_all(project)

            _, payload = self.run_tool(
                str(PHASE1_READINESS),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
            )

            self.assertEqual(payload["token"], "ok", payload)
            self.assertTrue(payload["read_only"])
            self.assertFalse(payload["writes_target_project"])
            self.assertFalse(payload["git_status"]["dirty"])
            self.assertTrue(payload["private_prompt_source"]["exists"])
            self.assertTrue(payload["agent_toml"]["standard_profile_ready"])
            self.assertTrue(payload["agent_toml"]["extension_fields_ok"])
            self.assertEqual(
                payload["agent_toml"]["required_extension_sections"],
                ["project", "moe", "dispatch", "extensions"],
            )
            self.assertEqual(payload["cli_contract_check"]["commands_checked"], ["project-status", "list-sessions", "status"])
            self.assertTrue(payload["wrappers"]["on"]["references_expected_command"])
            self.assertTrue(payload["wrappers"]["off"]["references_expected_command"])
            self.assertTrue(payload["wrappers"]["on"]["passes_json_flag"])
            self.assertEqual(payload["wrappers"]["on"]["unsafe_shell_tokens"], [])
            self.assertEqual(payload["wrappers"]["on"]["direct_state_path_references"], [])
            self.assertTrue(payload["startup_activation_hooks"]["hook_found"])
            self.assertTrue(payload["operator_docs"]["ready"])

    def test_phase1_readiness_checker_blocks_dirty_target_and_missing_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-blocked"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-blocked", session_id="session-phase1-blocked")
            self.add_phase1_wrappers_and_startup_hook(project)
            (project / "thesis-moe-off.cmd").unlink()
            self.git_commit_all(project)
            (project / "operator-note.txt").write_text("unclassified local note\n", encoding="utf-8")

            _, payload = self.run_tool(
                str(PHASE1_READINESS),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
                expect_success=False,
            )

            blocker_codes = {item["code"] for item in payload["blockers"]}
            self.assertEqual(payload["token"], "blocked:dirty_target_project", payload)
            self.assertIn("blocked:dirty_target_project", blocker_codes)
            self.assertIn("blocked:missing_phase1_wrapper", blocker_codes)
            self.assertTrue(payload["git_status"]["dirty"])

    def test_phase1_readiness_checker_blocks_missing_operator_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-missing-docs"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-missing-docs", session_id="session-phase1-docs")
            self.add_phase1_wrappers_and_startup_hook(project)
            (project / "docs_bilingual" / "operations" / "thesis_moe_mode_usage.zh-CN.md").unlink()
            self.git_commit_all(project)

            _, payload = self.run_tool(
                str(PHASE1_READINESS),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
                expect_success=False,
            )

            blocker_codes = {item["code"] for item in payload["blockers"]}
            self.assertIn("blocked:missing_phase1_operator_docs", blocker_codes)
            self.assertFalse(payload["operator_docs"]["ready"])

    def test_phase1_readiness_checker_blocks_incomplete_operator_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-incomplete-docs"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-incomplete-docs", session_id="session-phase1-incomplete-docs")
            self.add_phase1_wrappers_and_startup_hook(project)
            (project / "docs_bilingual" / "operations" / "thesis_moe_mode_usage.zh-CN.md").write_text(
                "# Incomplete docs\n\nOnly mentions thesis_moe_mode.py and project-on.\n",
                encoding="utf-8",
            )
            self.git_commit_all(project)

            _, payload = self.run_tool(
                str(PHASE1_READINESS),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
                expect_success=False,
            )

            blocker_codes = {item["code"] for item in payload["blockers"]}
            self.assertIn("blocked:phase1_operator_docs_incomplete", blocker_codes)
            missing = next(item["missing"] for item in payload["blockers"] if item["code"] == "blocked:phase1_operator_docs_incomplete")
            self.assertIn("project-off", missing)
            self.assertIn("status --json", missing)

    def test_phase1_readiness_checker_blocks_agent_toml_missing_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-agent-missing-extensions"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-agent-missing-extensions", session_id="session-agent-missing")
            self.add_phase1_wrappers_and_startup_hook(project)
            (project / ".codex" / "agents" / "thesis-moe-mentor.toml").write_text(
                'name = "thesis-moe-mentor"\n'
                'description = "Strict thesis mentor."\n'
                'developer_instructions = "Use strict thesis mentor rules."\n',
                encoding="utf-8",
            )
            self.git_commit_all(project)

            _, payload = self.run_tool(
                str(PHASE1_READINESS),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
                expect_success=False,
            )

            blocker_codes = {item["code"] for item in payload["blockers"]}
            self.assertIn("blocked:agent_toml_missing_extension_sections", blocker_codes)
            self.assertFalse(payload["agent_toml"]["standard_profile_ready"])
            self.assertEqual(
                payload["agent_toml"]["required_extension_sections"],
                ["project", "moe", "dispatch", "extensions"],
            )

    def test_phase1_readiness_checker_blocks_agent_toml_bad_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-agent-bad-boundaries"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-agent-bad-boundaries", session_id="session-agent-bad")
            self.add_phase1_wrappers_and_startup_hook(project)
            agent_path = project / ".codex" / "agents" / "thesis-moe-mentor.toml"
            agent_path.write_text(
                agent_path.read_text(encoding="utf-8")
                .replace('private_prompt_policy = "do-not-copy-full-content"', 'private_prompt_policy = "copy-full-content"')
                .replace('session_state_dir = ".omx/state/thesis_moe/sessions"', 'session_state_dir = "../sessions"')
                .replace('forbidden = ["full-history-fork-with-custom-role"]', 'forbidden = []')
                .replace('fallback = ["main-session-takeover", "durable-brief"]', 'fallback = ["full-history-fork"]'),
                encoding="utf-8",
            )
            self.git_commit_all(project)

            _, payload = self.run_tool(
                str(PHASE1_READINESS),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
                expect_success=False,
            )

            blocker_codes = {item["code"] for item in payload["blockers"]}
            self.assertIn("blocked:agent_project_boundary_invalid", blocker_codes)
            self.assertIn("blocked:agent_moe_boundary_invalid", blocker_codes)
            self.assertIn("blocked:agent_dispatch_boundary_incomplete", blocker_codes)
            self.assertFalse(payload["agent_toml"]["extension_fields_ok"])

    def test_phase1_readiness_checker_blocks_wrapper_without_json_and_direct_state_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-wrapper-direct-state"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-wrapper-direct-state", session_id="session-wrapper-direct")
            self.add_phase1_wrappers_and_startup_hook(project)
            (project / "thesis-moe-on.cmd").write_text(
                '@echo off\n'
                'python "%~dp0tools\\thesis_moe_mode.py" project-on\n'
                'echo unsafe > "%~dp0.omx\\state\\thesis_moe\\project-default.json"\n'
                "exit /b %ERRORLEVEL%\n",
                encoding="utf-8",
            )
            self.git_commit_all(project)

            _, payload = self.run_tool(
                str(PHASE1_READINESS),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
                expect_success=False,
            )

            blocker_codes = {item["code"] for item in payload["blockers"]}
            self.assertIn("blocked:phase1_wrapper_json_output_missing", blocker_codes)
            self.assertIn("blocked:phase1_wrapper_unsafe_shell_surface", blocker_codes)
            self.assertIn("blocked:phase1_wrapper_direct_state_surface", blocker_codes)
            self.assertFalse(payload["wrappers"]["on"]["passes_json_flag"])
            self.assertIn(">", payload["wrappers"]["on"]["unsafe_shell_tokens"])
            self.assertIn(".omx", payload["wrappers"]["on"]["direct_state_path_references"])

    def test_phase1_readiness_checker_blocks_wrapper_argument_passthrough_and_shell_chaining(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-wrapper-shell"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-wrapper-shell", session_id="session-wrapper-shell")
            self.add_phase1_wrappers_and_startup_hook(project)
            (project / "thesis-moe-off.cmd").write_text(
                '@echo off\n'
                'python "%~dp0tools\\thesis_moe_mode.py" project-off --json %* && echo done\n'
                "exit /b %ERRORLEVEL%\n",
                encoding="utf-8",
            )
            self.git_commit_all(project)

            _, payload = self.run_tool(
                str(PHASE1_READINESS),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
                expect_success=False,
            )

            blocker_codes = {item["code"] for item in payload["blockers"]}
            self.assertIn("blocked:phase1_wrapper_unsafe_shell_surface", blocker_codes)
            self.assertTrue(payload["wrappers"]["off"]["passes_json_flag"])
            self.assertIn("%*", payload["wrappers"]["off"]["unsafe_shell_tokens"])
            self.assertIn("&&", payload["wrappers"]["off"]["unsafe_shell_tokens"])

    def test_install_cli_contract_fixture_accepts_phase1_read_envelope(self) -> None:
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
            self.assertEqual(payload["token"], "ok", payload)
            self.assertEqual(payload["cli_contract_check"]["commands_checked"], ["project-status", "list-sessions", "status"])
            self.assertIn("effective_source", payload["cli_contract_check"]["validated_fields"]["status"])
            self.assertIn("registered_session_count", payload["cli_contract_check"]["validated_fields"]["project-status"])

    def test_install_cli_contract_rejects_missing_effective_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project, cli_variant="missing_effective_source")
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
            self.assertEqual(payload["token"], "blocked:status_contract_invalid", payload)
            self.assertIn("effective_source", payload["blockers"][0]["message"])

    def test_install_cli_contract_rejects_private_field_exposure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project, cli_variant="private_field_exposed")
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
            self.assertEqual(payload["token"], "blocked:cli_contract_private_field_exposed", payload)
            self.assertTrue(any("raw_session_id" in field for field in payload["blockers"][0]["fields"]))

    def test_install_cli_contract_rejects_list_sessions_without_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project, cli_variant="bad_list_sessions_counts")
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
            self.assertEqual(payload["token"], "blocked:list_sessions_contract_invalid", payload)

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

    def test_gui_shell_rejects_write_payload_without_changed_paths(self) -> None:
        from project_moe_gui import gui_shell

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project, cli_variant="write_missing_changed_paths")
            config = self.gui_config(project)
            result = gui_shell.execute_write_action_with_readback(config, "project-on")
            self.assertFalse(result["ok"], result)
            self.assertEqual(result["token"], "blocked:write_cli_contract_missing_fields")
            self.assertIn("changed_paths", result["errors"][0]["missing"])

    def test_gui_shell_rejects_write_payload_scope_mismatch(self) -> None:
        from project_moe_gui import gui_shell

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project, cli_variant="write_scope_mismatch")
            config = self.gui_config(project)
            result = gui_shell.execute_write_action_with_readback(config, "session-on", session_id="session-1234567890abcdef")
            self.assertFalse(result["ok"], result)
            self.assertEqual(result["token"], "blocked:write_cli_scope_mismatch")
            self.assertEqual(result["errors"][0]["expected"], "session")

    def test_gui_shell_rejects_write_payload_private_field_exposure(self) -> None:
        from project_moe_gui import gui_shell

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project, cli_variant="write_private_field_exposed")
            config = self.gui_config(project)
            result = gui_shell.execute_write_action_with_readback(config, "project-on")
            self.assertFalse(result["ok"], result)
            self.assertEqual(result["token"], "blocked:write_cli_private_field_exposed")
            self.assertTrue(any("raw_session_id" in field for field in result["errors"][0]["fields"]))

    def test_gui_shell_rejects_write_payload_without_atomic_write(self) -> None:
        from project_moe_gui import gui_shell

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project, cli_variant="write_missing_atomic_write")
            config = self.gui_config(project)
            result = gui_shell.execute_write_action_with_readback(config, "project-on")
            self.assertFalse(result["ok"], result)
            self.assertEqual(result["token"], "blocked:write_cli_contract_missing_fields")
            self.assertIn("atomic_write", result["errors"][0]["missing"])

    def test_gui_shell_rejects_write_payload_when_atomic_write_is_false(self) -> None:
        from project_moe_gui import gui_shell

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project, cli_variant="write_atomic_write_false")
            config = self.gui_config(project)
            result = gui_shell.execute_write_action_with_readback(config, "project-on")
            self.assertFalse(result["ok"], result)
            self.assertEqual(result["token"], "blocked:write_cli_atomic_write_required")

    def test_gui_shell_rejects_write_payload_with_lock_timeout(self) -> None:
        from project_moe_gui import gui_shell

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project, cli_variant="write_lock_timeout")
            config = self.gui_config(project)
            result = gui_shell.execute_write_action_with_readback(config, "project-on")
            self.assertFalse(result["ok"], result)
            self.assertEqual(result["token"], "blocked:write_cli_lock_not_clean")
            self.assertEqual(result["errors"][0]["lock_status"], "lock_timeout")

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

    def run_installed_launcher(self, project: Path, *args: str) -> dict:
        result = subprocess.run(
            [sys.executable, str(project / "tools" / "project_moe_gui" / "launcher.py"), *args, "--json"],
            cwd=project,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        try:
            return json.loads(result.stdout)
        except Exception as exc:  # pragma: no cover
            self.fail(f"launcher did not emit JSON: {exc}\nstdout={result.stdout}\nstderr={result.stderr}")

    def install_fixture_gui(self, project: Path, *, agent_name: str = "thesis-moe-mentor", namespace: str = "thesis_moe") -> dict:
        _, payload = self.run_tool(
            str(INSTALLER),
            "--target-project",
            str(project),
            "--agent-name",
            agent_name,
            "--state-namespace",
            namespace,
        )
        self.assertTrue((project / "tools" / "project_moe_gui" / "project_moe_gui.install-manifest.json").exists())
        return payload

    def run_toolchain_write(self, project: Path, action: str, *, session_id: str | None = None) -> dict:
        from project_moe_gui import gui_shell

        config = json.loads((project / "tools" / "project_moe_gui" / "project_moe_gui.config.json").read_text(encoding="utf-8-sig"))
        return gui_shell.execute_write_action_with_readback(config, action, session_id=session_id)

    def test_phase2c_fixture_a_full_install_check_update_status_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "fixture-a"
            project.mkdir()
            self.make_stateful_project(project, project_label="fixture-a", session_id="session-fixture-a")
            private_before = self.private_project_digests(project)

            install_payload = self.install_fixture_gui(project)
            self.assertEqual(install_payload["mode"], "apply")
            self.assertEqual(install_payload["target_project_root"], str(project.resolve()))

            _, check_payload = self.run_tool(str(CHECKER), "--target-project", str(project), "--skip-runtime-import")
            self.assertEqual(check_payload["status"], "up_to_date")
            self.assertEqual(check_payload["runtime_status"], "skipped_by_flag")

            _, update_payload = self.run_tool(str(UPDATER), "--target-project", str(project), "--dry-run")
            self.assertTrue(update_payload["no_op"], update_payload)
            self.assertEqual(update_payload["status"], "up_to_date")

            preflight = self.run_installed_launcher(project, "--preflight")
            self.assertIn(preflight["token"], {"ok", "blocked:pyside6_unavailable"}, preflight)
            self.assertEqual(preflight["view_model"]["top_banner"]["project_root"], str(project.resolve()))
            self.assertEqual(preflight["view_model"]["top_banner"]["current_branch"], "main")
            self.assertNotEqual(preflight["view_model"]["session_table"]["rows"][0]["display_id"], "session-fixture-a")
            self.assertTrue(preflight["view_model"]["session_table"]["rows"][0]["display_id"].startswith("sessio"))
            self.assertEqual(preflight["view_model"]["session_table"]["rows"][0]["source"], "project-propagated")

            project_on = self.run_toolchain_write(project, "project-on")
            self.assertTrue(project_on["ok"], project_on)
            self.assertTrue(project_on["readback"]["project-status"]["project_default_enabled"])
            self.assertTrue(project_on["readback"]["status"]["effective_enabled"])

            private_after = self.private_project_digests(project)
            self.assertEqual(private_before, private_after)

    def test_phase1_project_default_propagates_only_to_project_managed_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "fixture-phase1-propagation"
            project.mkdir()
            self.make_stateful_project(project, project_label="fixture-phase1", session_id="session-project-managed")
            manual_path = project / ".omx" / "state" / "thesis_moe" / "sessions" / "session-manual.json"
            manual_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "project_label": "fixture-phase1",
                        "agent_name": "thesis-moe-mentor",
                        "state_namespace": "thesis_moe",
                        "scope": "session",
                        "session_id": "session-manual",
                        "enabled": False,
                        "override_origin": "manual-session",
                        "token": "ok",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            self.install_fixture_gui(project)

            result = self.run_toolchain_write(project, "project-on")
            self.assertTrue(result["ok"], result)
            project_managed = json.loads(
                (project / ".omx" / "state" / "thesis_moe" / "sessions" / "session-project-managed.json").read_text(encoding="utf-8-sig")
            )
            manual = json.loads(manual_path.read_text(encoding="utf-8-sig"))
            self.assertTrue(project_managed["enabled"])
            self.assertEqual(project_managed["override_origin"], "project-propagated")
            self.assertFalse(manual["enabled"])
            self.assertEqual(manual["override_origin"], "manual-session")
            self.assertTrue(result["write_payload"]["project_default_enabled"])
            self.assertFalse(result["write_payload"]["no_op"])

    def test_phase1_session_override_wins_over_project_default_and_noop_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "fixture-phase1-override"
            project.mkdir()
            self.make_stateful_project(project, project_label="fixture-override", session_id="session-override")
            self.install_fixture_gui(project)

            session_on = self.run_toolchain_write(project, "session-on", session_id="session-override")
            self.assertTrue(session_on["ok"], session_on)
            self.assertEqual(session_on["write_payload"]["changed_scope"], "session")
            self.assertFalse(session_on["write_payload"]["no_op"])
            self.assertEqual(session_on["readback"]["status"]["effective_source"], "session")
            self.assertTrue(session_on["readback"]["status"]["effective_enabled"])

            second_session_on = self.run_toolchain_write(project, "session-on", session_id="session-override")
            self.assertTrue(second_session_on["ok"], second_session_on)
            self.assertTrue(second_session_on["write_payload"]["no_op"])

            project_off = self.run_toolchain_write(project, "project-off")
            self.assertTrue(project_off["ok"], project_off)
            self.assertTrue(project_off["readback"]["status"]["effective_enabled"])
            self.assertEqual(project_off["readback"]["status"]["effective_source"], "session")

    def test_phase1_invalid_and_legacy_session_records_are_classified_without_blocking_project_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "fixture-phase1-invalid-legacy"
            project.mkdir()
            self.make_stateful_project(project, project_label="fixture-invalid", session_id="session-current")
            sessions_root = project / ".omx" / "state" / "thesis_moe" / "sessions"
            invalid_path = sessions_root / "session-invalid.json"
            invalid_path.write_text("{invalid-json", encoding="utf-8")
            legacy_path = sessions_root / "session-legacy.json"
            legacy_path.write_text(
                json.dumps({"session_id": "session-legacy", "enabled": False, "token": "ok"}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            self.install_fixture_gui(project)

            project_on = self.run_toolchain_write(project, "project-on")
            self.assertTrue(project_on["ok"], project_on)
            skipped = project_on["write_payload"]["skipped_invalid_records"]
            self.assertEqual(len(skipped), 1, project_on)
            self.assertEqual(skipped[0]["token"], "invalid_json")
            self.assertEqual(invalid_path.read_text(encoding="utf-8"), "{invalid-json")
            legacy = json.loads(legacy_path.read_text(encoding="utf-8-sig"))
            self.assertTrue(legacy["enabled"])
            self.assertEqual(legacy["override_origin"], "project-propagated")
            preflight = self.run_installed_launcher(project, "--preflight")
            rows = preflight["view_model"]["session_table"]["rows"]
            token_by_session = {row["session_id"]: row["token"] for row in rows}
            self.assertEqual(token_by_session["session-invalid"], "invalid_json")
            self.assertEqual(token_by_session["session-legacy"], "ok")
            source_by_session = {row["session_id"]: row["source"] for row in rows}
            self.assertEqual(source_by_session["session-invalid"], "invalid-record")

    def test_phase2c_fixture_b_uses_same_contract_and_isolated_project_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_a = Path(tmp) / "fixture-a"
            project_b = Path(tmp) / "fixture-b"
            project_a.mkdir()
            project_b.mkdir()
            self.make_stateful_project(project_a, project_label="fixture-a", session_id="session-fixture-a")
            self.make_stateful_project(project_b, project_label="fixture-b", session_id="session-fixture-b")
            self.install_fixture_gui(project_a)
            self.install_fixture_gui(project_b)

            result_a = self.run_toolchain_write(project_a, "project-on")
            self.assertTrue(result_a["ok"], result_a)
            status_a = result_a["readback"]["project-status"]
            self.assertEqual(status_a["project_label"], "fixture-a")
            self.assertTrue(status_a["project_default_enabled"])

            _, check_b = self.run_tool(str(CHECKER), "--target-project", str(project_b), "--skip-runtime-import")
            self.assertEqual(check_b["status"], "up_to_date")
            preflight_b = self.run_installed_launcher(project_b, "--preflight")
            self.assertEqual(preflight_b["view_model"]["top_banner"]["project_root"], str(project_b.resolve()))
            self.assertEqual(preflight_b["view_model"]["project_default_card"]["label"], "disabled")
            self.assertFalse((project_b / ".omx" / "state" / "thesis_moe" / "project-default.json").exists())

            result_b = self.run_toolchain_write(project_b, "session-on", session_id="session-fixture-b")
            self.assertTrue(result_b["ok"], result_b)
            self.assertEqual(result_b["readback"]["project-status"]["project_label"], "fixture-b")
            self.assertTrue(result_b["readback"]["status"]["effective_enabled"])
            session_a = json.loads((project_a / ".omx" / "state" / "thesis_moe" / "sessions" / "session-fixture-a.json").read_text(encoding="utf-8-sig"))
            self.assertTrue(session_a["enabled"])
            self.assertFalse((project_a / ".omx" / "state" / "thesis_moe" / "sessions" / "session-fixture-b.json").exists())

    def test_phase2c_update_preserves_private_agent_prompt_and_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "fixture-private"
            project.mkdir()
            self.make_stateful_project(project, project_label="fixture-private", session_id="session-private")
            self.install_fixture_gui(project)
            private_before = self.private_project_digests(project)

            readme = project / "tools" / "project_moe_gui" / "README.md"
            readme.write_text(readme.read_text(encoding="utf-8-sig") + "\nlocal managed-file drift\n", encoding="utf-8")
            _, check_payload = self.run_tool(str(CHECKER), "--target-project", str(project), "--skip-runtime-import", expect_success=False)
            self.assertEqual(check_payload["token"], "blocked:managed_file_hash_mismatch")

            _, update_payload = self.run_tool(str(UPDATER), "--target-project", str(project), "--dry-run", expect_success=False)
            self.assertEqual(update_payload["token"], "blocked:managed_file_hash_mismatch")
            self.assertEqual(private_before, self.private_project_digests(project))


if __name__ == "__main__":
    unittest.main()
