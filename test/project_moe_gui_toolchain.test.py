from __future__ import annotations

import hashlib
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLCHAIN_SRC = REPO_ROOT / "tools" / "project_moe_gui_toolchain" / "src"
sys.path.insert(0, str(TOOLCHAIN_SRC))
from project_moe_gui.toolchain import stable_toolchain_source_root
INSTALLER = REPO_ROOT / "tools" / "project_moe_gui_toolchain" / "install_project_moe_gui.py"
CHECKER = REPO_ROOT / "tools" / "project_moe_gui_toolchain" / "check_project_moe_gui_install.py"
UPDATER = REPO_ROOT / "tools" / "project_moe_gui_toolchain" / "update_project_moe_gui.py"
UNINSTALL_PLANNER = REPO_ROOT / "tools" / "project_moe_gui_toolchain" / "plan_project_moe_gui_uninstall.py"
PHASE1_READINESS = REPO_ROOT / "tools" / "project_moe_gui_toolchain" / "check_project_moe_phase1_readiness.py"
PHASE1_SCAFFOLD = REPO_ROOT / "tools" / "project_moe_gui_toolchain" / "scaffold_project_moe_phase1.py"
GUI_PREFLIGHT_ALLOWED_TOKENS = {"ok", "blocked:pyside6_unavailable", "blocked:qfluentwidgets_unavailable"}


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
            (root / "MOE.md").write_text("# Private fixture prompt\n", encoding="utf-8")
            (root / ".codex" / "agents" / "thesis-moe-mentor.toml").write_text(
                'name = "thesis-moe-mentor"\n'
                'description = "Strict thesis mentor."\n'
                'developer_instructions = "Use strict thesis mentor rules."\n'
                "\n[project]\n"
                'scope = "repo-local"\n'
                'state_namespace = "thesis_moe"\n'
                'private_prompt_source = "MOE.md"\n'
                'private_prompt_policy = "do-not-copy-full-content"\n'
                "\n[moe]\n"
                'kind = "project-moe-agent"\n'
                'family = "project-specific"\n'
                'requires_manual_enable = true\n'
                'project_default_state = ".omx/state/thesis_moe/project-default.json"\n'
                'session_state_dir = ".omx/state/thesis_moe/sessions"\n'
                "\n[dispatch]\n"
                'mode = "brief-based"\n'
                'forbidden = ["full-history-fork-with-custom-role"]\n'
                'fallback = ["main-session-takeover", "durable-brief"]\n'
                "\n[extensions]\n",
                encoding="utf-8",
            )
        extra_payload = ""
        if cli_variant == "missing_effective_source":
            extra_payload = 'payload.pop("effective_source", None)\n'
        elif cli_variant == "unsupported_schema_version":
            extra_payload = 'payload["schema_version"] = 999\n'
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
        elif cli_variant == "assert_on_missing_effective_enabled":
            extra_payload = 'payload.pop("effective_enabled", None)\n'
        elif cli_variant == "assert_on_not_read_only":
            extra_payload = 'payload["changed_paths"] = [".omx/state/thesis_moe/project-default.json"]\npayload["atomic_write"] = True\npayload["lock_status"] = "not_locked_fixture"\n'
        elif cli_variant == "assert_on_unknown_token":
            extra_payload = 'payload.update(ok=False, token="unexpected_assert_token", exit_code=1)\n'
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
if cmd == "assert-on":
    payload.update(ok=False, token="disabled", exit_code=1, message="MOE mode is disabled", effective_enabled=False, effective_source="project-default")
elif cmd == "list-sessions":
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
    payload["session_id"] = "session-1234567890abcdef"
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

    def write_marker_mode_cli(self, root: Path, marker_name: str = "mode-cli-executed.marker") -> None:
        (root / "tools" / "thesis_moe_mode.py").write_text(
            f"""
from __future__ import annotations
import json
import sys
from pathlib import Path

# Surface tokens required by the static checker:
# project-status list-sessions status assert-on project-on project-off on off
Path({marker_name!r}).write_text("executed", encoding="utf-8")
cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
payload = {{
    "schema_version": 1,
    "command": cmd,
    "ok": True,
    "token": "ok",
    "exit_code": 0,
    "message": "marker cli executed",
    "project_root": str(Path.cwd()),
    "agent_name": "thesis-moe-mentor",
    "state_namespace": "thesis_moe",
    "generated_at": "2026-05-25T00:00:00+00:00",
    "warnings": [],
    "errors": [],
    "cli_contract": "project-moe-cli-v1",
    "effective_enabled": False,
    "effective_source": "project-default",
    "project_default_enabled": False,
    "registered_session_count": 0,
    "valid_session_count": 0,
    "invalid_session_count": 0,
    "sessions": [],
    "counts": {{"total": 0, "valid": 0}},
}}
if cmd == "assert-on":
    payload.update(ok=False, token="disabled", exit_code=1)
print(json.dumps(payload))
raise SystemExit(int(payload.get("exit_code", 0)))
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
            "On startup, resume, continue, reload, or phase change, run `python .\\tools\\thesis_moe_mode.py status --json` before applying the thesis MOE rules.\n",
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

    def test_phase1_git_status_summary_uses_read_only_optional_locks(self) -> None:
        from project_moe_gui import toolchain

        calls: list[dict] = []

        def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            calls.append({"command": command, **kwargs})
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            with patch("project_moe_gui.toolchain.subprocess.run", fake_run):
                payload = toolchain.git_status_summary(Path(tmp))

        self.assertEqual(payload["token"], "ok", payload)
        self.assertTrue(payload["read_only_git_optional_locks"])
        self.assertEqual(payload["git_optional_locks"], "0")
        self.assertEqual(calls[0]["env"]["GIT_OPTIONAL_LOCKS"], "0")

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
            self.assertEqual(payload["adaptation_lane"], "ready")
            self.assertTrue(payload["control_mode_allowed"])
            self.assertFalse(payload["bootstrap_required"])
            self.assertFalse(payload["repair_required"])
            self.assertEqual(payload["bootstrap_missing_capabilities"], [])
            for key in ["adaptation_lane", "blockers", "warnings", "checked_files", "redacted_paths", "control_mode_allowed"]:
                self.assertIn(key, payload)
            self.assertEqual(payload["blockers"], [])
            self.assertEqual(payload["warnings"], [])
            checked_roles = {record["role"] for record in payload["checked_files"]}
            self.assertTrue(
                {
                    "agent_toml",
                    "private_prompt_source",
                    "mode_cli",
                    "on_wrapper",
                    "off_wrapper",
                    "startup_hook",
                    "operator_doc",
                }.issubset(checked_roles),
                payload["checked_files"],
            )
            for record in payload["checked_files"]:
                self.assertFalse(Path(record["path"]).is_absolute(), record)
                self.assertNotIn(str(project), record["path"])
            redacted_aliases = {record["alias"] for record in payload["redacted_paths"]}
            self.assertIn("phase1.agent_toml", redacted_aliases)
            self.assertIn("phase1.private_prompt_source", redacted_aliases)
            self.assertIn("phase1.mode_cli", redacted_aliases)
            self.assertIn("phase1.on_wrapper", redacted_aliases)
            self.assertIn("phase1.off_wrapper", redacted_aliases)
            for record in payload["redacted_paths"]:
                self.assertFalse(Path(record["path"]).is_absolute(), record)
                self.assertNotIn(str(project), record["path"])
            self.assertFalse(payload["git_status"]["dirty"])
            self.assertTrue(payload["private_prompt_source"]["exists"])
            self.assertFalse(payload["private_prompt_source"]["managed_by_toolchain"])
            self.assertFalse(payload["private_prompt_source"]["under_state_dir"])
            self.assertFalse(payload["private_prompt_source"]["under_agent_dir"])
            self.assertTrue(payload["private_prompt_source"]["private_prompt_boundary_ok"])
            self.assertTrue(payload["agent_toml"]["standard_profile_ready"])
            self.assertTrue(payload["agent_toml"]["extension_fields_ok"])
            self.assertEqual(
                payload["agent_toml"]["required_extension_sections"],
                ["project", "moe", "dispatch", "extensions"],
            )
            self.assertEqual(payload["cli_contract_check"]["commands_checked"], ["project-status", "list-sessions", "status"])
            self.assertEqual(payload["cli_contract_check"]["assertion_commands_checked"], ["assert-on"])
            self.assertEqual(payload["cli_execution_mode"], "execute-read-contract")
            self.assertFalse(payload["cli_contract_check"]["execution_skipped"])
            self.assertIn("assert-on", payload["cli_contract_check"]["validated_fields"])
            self.assertTrue(payload["wrappers"]["on"]["references_expected_command"])
            self.assertTrue(payload["wrappers"]["off"]["references_expected_command"])
            self.assertTrue(payload["wrappers"]["on"]["passes_json_flag"])
            self.assertEqual(payload["wrappers"]["on"]["unsafe_shell_tokens"], [])
            self.assertEqual(payload["wrappers"]["on"]["direct_state_path_references"], [])
            self.assertTrue(payload["startup_activation_hooks"]["hook_found"])
            self.assertTrue(payload["startup_activation_hooks"]["basic_status_hook_found"])
            self.assertEqual(payload["startup_activation_hooks"]["required_tokens"], ["thesis_moe_mode.py", "status --json", "startup", "resume", "continue", "reload", "phase change"])
            self.assertTrue(payload["operator_docs"]["ready"])
            remediation = payload["remediation_plan"]
            self.assertTrue(remediation["ready_for_control"])
            self.assertEqual(remediation["lane"], "ready")
            self.assertEqual(remediation["summary"], "no_remediation_required")
            self.assertEqual(remediation["groups"], [])
            self.assertEqual(remediation["ordered_next_steps"], [])

    def test_phase1_readiness_checker_rejects_unsupported_read_contract_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-unsupported-schema"
            project.mkdir()
            self.make_project(project, cli_variant="unsupported_schema_version")
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
                expect_success=False,
            )

            blocker_codes = {item["code"] for item in payload["blockers"]}
            self.assertEqual(payload["token"], "blocked:cli_envelope_schema_version_mismatch", payload)
            self.assertIn("blocked:cli_envelope_schema_version_mismatch", blocker_codes)
            self.assertEqual(payload["adaptation_lane"], "repair")
            self.assertFalse(payload["control_mode_allowed"])
            self.assertTrue(payload["repair_required"])
            self.assertEqual(payload["cli_execution_mode"], "execute-read-contract")
            self.assertFalse(payload["cli_contract_check"]["execution_skipped"])
            self.assertIn("schema_version", payload["cli_contract_check"]["validated_fields"]["project-status"])
            remediation = payload["remediation_plan"]
            groups = {group["category"]: group for group in remediation["groups"]}
            self.assertIn("mode_cli_contract", groups)
            self.assertIn("repair_mode_cli_schema_version", groups["mode_cli_contract"]["actions"])
            self.assertTrue(groups["mode_cli_contract"]["requires_target_project_write"])

    def test_phase1_readiness_checker_static_only_does_not_execute_target_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-static-only"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-static-only", session_id="session-static-only")
            self.add_phase1_wrappers_and_startup_hook(project)
            marker = project / "cli-executed-marker.txt"
            (project / "tools" / "thesis_moe_mode.py").write_text(
                "from pathlib import Path\n"
                "Path('cli-executed-marker.txt').write_text('executed', encoding='utf-8')\n"
                "# static command surface tokens: project-on project-off on off assert-on\n"
                "# read contract tokens: project-status list-sessions status --json\n"
                "raise SystemExit(99)\n",
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
                "--static-only",
            )

            self.assertFalse(marker.exists(), "static-only readiness must not execute the target mode CLI")
            self.assertEqual(payload["token"], "ok", payload)
            self.assertEqual(payload["readiness_status"], "static-ready-candidate")
            self.assertEqual(payload["adaptation_lane"], "ready-candidate")
            self.assertFalse(payload["control_mode_allowed"])
            self.assertEqual(payload["cli_execution_mode"], "static-only")
            self.assertTrue(payload["cli_contract_check"]["execution_skipped"])
            self.assertEqual(payload["cli_contract_check"]["skip_reason"], "static_only_no_exec_cli")
            self.assertEqual(payload["cli_contract_check"]["commands_checked"], [])
            self.assertEqual(payload["cli_contract_check"]["assertion_commands_checked"], [])
            self.assertEqual(
                payload["warnings"],
                [
                    {
                        "code": "warning:read_contract_cli_execution_skipped",
                        "message": "Read-contract CLI execution was skipped because readiness ran in static-only mode.",
                        "cli_execution_mode": "static-only",
                        "skip_reason": "static_only_no_exec_cli",
                        "blocks_control_mode": True,
                    }
                ],
            )
            self.assertTrue(payload["checked_files"])
            self.assertTrue(payload["redacted_paths"])
            remediation = payload["remediation_plan"]
            self.assertFalse(remediation["ready_for_control"])
            self.assertEqual(remediation["lane"], "ready-candidate")
            self.assertEqual(remediation["cli_execution_mode"], "static-only")
            self.assertFalse(remediation["target_project_write_allowed_by_checker"])
            self.assertEqual(remediation["summary"], "execute_read_contract_required_before_control")
            self.assertEqual(remediation["ordered_next_steps"], ["run_execute_read_contract_readiness_check"])
            self.assertEqual(remediation["groups"][0]["category"], "mode_cli_contract")
            self.assertFalse(remediation["groups"][0]["safe_to_auto_apply"])

    def test_phase1_readiness_checker_skips_cli_when_static_surface_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-static-blocked"
            project.mkdir()
            self.make_project(project)
            self.write_marker_mode_cli(project)
            self.git_commit_all(project)

            marker = project / "mode-cli-executed.marker"
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

            self.assertFalse(marker.exists(), "execute-read-contract must not run target CLI while static surface blockers exist")
            self.assertEqual(payload["token"], "blocked:missing_phase1_wrapper", payload)
            cli_details = payload["cli_contract_check"]
            self.assertTrue(cli_details["execution_skipped"])
            self.assertEqual(cli_details["skip_reason"], "static_surface_blockers_present")
            self.assertIn("blocked:missing_phase1_wrapper", cli_details["static_surface_blocking_codes"])

    def test_phase1_readiness_checker_skips_cli_when_target_is_dirty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-dirty-no-exec"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-dirty-no-exec", session_id="session-phase1-dirty")
            self.add_phase1_wrappers_and_startup_hook(project)
            self.git_commit_all(project)
            self.write_marker_mode_cli(project)

            marker = project / "mode-cli-executed.marker"
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

            self.assertFalse(marker.exists(), "dirty target preflight must prevent target CLI execution")
            self.assertEqual(payload["token"], "blocked:dirty_target_project", payload)
            cli_details = payload["cli_contract_check"]
            self.assertTrue(cli_details["execution_skipped"])
            self.assertEqual(cli_details["skip_reason"], "static_surface_blockers_present")
            self.assertIn("blocked:dirty_target_project", cli_details["static_surface_blocking_codes"])

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
            self.assertEqual(payload["adaptation_lane"], "bootstrap")
            self.assertFalse(payload["control_mode_allowed"])
            self.assertTrue(payload["bootstrap_required"])
            self.assertIn("phase1_wrapper", payload["bootstrap_missing_capabilities"])
            self.assertIn("blocked:dirty_target_project", blocker_codes)
            self.assertIn("blocked:missing_phase1_wrapper", blocker_codes)
            self.assertTrue(payload["git_status"]["dirty"])
            remediation = payload["remediation_plan"]
            self.assertFalse(remediation["ready_for_control"])
            self.assertEqual(remediation["lane"], payload["adaptation_lane"])
            self.assertFalse(remediation["target_project_write_allowed_by_checker"])
            self.assertEqual(remediation["ordered_next_steps"][0], "classify_or_clean_dirty_target_worktree")
            groups = {group["category"]: group for group in remediation["groups"]}
            self.assertIn("target_git_state", groups)
            self.assertIn("phase1_wrapper", groups)
            self.assertIn("blocked:dirty_target_project", groups["target_git_state"]["codes"])
            self.assertIn("blocked:missing_phase1_wrapper", groups["phase1_wrapper"]["codes"])

    def test_phase1_readiness_checker_classifies_empty_target_as_bootstrap_lane(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-empty-target"
            project.mkdir()
            (project / "README.md").write_text("# empty target\n", encoding="utf-8")
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
            self.assertEqual(payload["adaptation_lane"], "bootstrap")
            self.assertFalse(payload["control_mode_allowed"])
            self.assertTrue(payload["bootstrap_required"])
            self.assertFalse(payload["repair_required"])
            self.assertIn("agent_toml", payload["bootstrap_missing_capabilities"])
            self.assertIn("mode_cli", payload["bootstrap_missing_capabilities"])
            self.assertIn("phase1_wrapper", payload["bootstrap_missing_capabilities"])
            self.assertIn("startup_activation_hook", payload["bootstrap_missing_capabilities"])
            self.assertIn("operator_docs", payload["bootstrap_missing_capabilities"])
            self.assertIn("blocked:missing_agent_toml", blocker_codes)
            self.assertIn("blocked:missing_mode_cli", blocker_codes)
            self.assertIn("blocked:missing_phase1_wrapper", blocker_codes)
            remediation = payload["remediation_plan"]
            self.assertEqual(remediation["lane"], "bootstrap")
            self.assertEqual(remediation["summary"], "bootstrap_phase1_surface_before_gui_control")
            categories = {group["category"] for group in remediation["groups"]}
            self.assertTrue({"agent_toml", "mode_cli", "phase1_wrapper", "startup_activation_hook", "operator_docs"}.issubset(categories))
            self.assertTrue(remediation["ordered_next_steps"])

    def test_phase1_bootstrap_scaffold_plan_is_dry_run_and_does_not_write_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-bootstrap-scaffold"
            project.mkdir()
            (project / "README.md").write_text("# bootstrap target\n", encoding="utf-8")
            self.git_commit_all(project)

            _, payload = self.run_tool(
                str(PHASE1_SCAFFOLD),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
                "--dry-run",
            )

            self.assertEqual(payload["command"], "scaffold_project_moe_phase1")
            self.assertEqual(payload["mode"], "dry-run")
            self.assertTrue(payload["read_only"])
            self.assertFalse(payload["writes_target_project"])
            self.assertTrue(payload["apply_supported"])
            self.assertTrue(payload["target_project_write_allowed_by_checker"])
            self.assertFalse(payload["control_mode_allowed"])
            self.assertEqual(payload["adaptation_lane"], "bootstrap")
            planned = {item["role"]: item for item in payload["planned_writes"]}
            self.assertEqual(planned["agent_toml"]["action"], "create")
            self.assertEqual(planned["private_prompt_source"]["action"], "create")
            self.assertEqual(planned["mode_cli"]["action"], "create")
            self.assertEqual(planned["phase1_wrapper_on"]["action"], "create")
            self.assertEqual(planned["phase1_wrapper_off"]["action"], "create")
            self.assertEqual(planned["startup_activation_hook"]["action"], "create")
            self.assertEqual(planned["operator_docs"]["action"], "create")
            self.assertTrue(all(item["content_included"] is False for item in payload["planned_writes"]))
            self.assertEqual(payload["summary"]["next_step_count"], len(payload["operator_next_steps"]))
            next_actions = [step["action"] for step in payload["operator_next_steps"]]
            self.assertEqual(
                next_actions,
                [
                    "classify_or_clean_target_project_state",
                    "review_existing_private_surfaces",
                    "create_or_update_phase1_contract_files",
                    "run_static_only_readiness_check",
                    "run_execute_read_contract_readiness_check",
                    "install_or_launch_gui_only_after_ready_lane",
                ],
            )
            create_step = next(step for step in payload["operator_next_steps"] if step["action"] == "create_or_update_phase1_contract_files")
            self.assertTrue(create_step["requires_target_project_write"])
            self.assertFalse(create_step["control_mode_allowed_after_step"])
            ready_step = payload["operator_next_steps"][-1]
            self.assertEqual(ready_step["control_mode_allowed_after_step"], "only_after_readiness_status_ready")
            self.assertFalse(payload["privacy_boundary"]["private_prompt_body_read"])
            self.assertFalse((project / ".codex" / "agents" / "thesis-moe-mentor.toml").exists())
            self.assertFalse((project / "MOE.md").exists())
            self.assertFalse((project / "tools" / "thesis_moe_mode.py").exists())

    def test_phase1_bootstrap_scaffold_apply_creates_only_missing_files_in_clean_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-bootstrap-apply"
            project.mkdir()
            (project / "README.md").write_text("# bootstrap target\n", encoding="utf-8")
            self.git_commit_all(project)

            _, payload = self.run_tool(
                str(PHASE1_SCAFFOLD),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
                "--apply",
            )

            self.assertEqual(payload["command"], "scaffold_project_moe_phase1")
            self.assertEqual(payload["mode"], "apply")
            self.assertFalse(payload["read_only"])
            self.assertTrue(payload["writes_target_project"])
            self.assertTrue(payload["apply_supported"])
            self.assertTrue(payload["target_project_write_allowed_by_checker"])
            self.assertFalse(payload["control_mode_allowed"])
            created_paths = {item["path"] for item in payload["applied_writes"]}
            self.assertEqual(
                created_paths,
                {
                    ".codex/agents/thesis-moe-mentor.toml",
                    "MOE.md",
                    "tools/thesis_moe_mode.py",
                    "thesis-moe-on.cmd",
                    "thesis-moe-off.cmd",
                    "AGENTS.md",
                    "docs_bilingual/operations/thesis_moe_mode_usage.zh-CN.md",
                },
            )
            self.assertTrue((project / ".codex" / "agents" / "thesis-moe-mentor.toml").exists())
            self.assertTrue((project / "MOE.md").exists())
            self.assertTrue((project / "tools" / "thesis_moe_mode.py").exists())
            self.assertIn("blocked:bootstrap_placeholder", (project / "tools" / "thesis_moe_mode.py").read_text(encoding="utf-8"))
            self.assertIn("Project MOE private prompt placeholder", (project / "MOE.md").read_text(encoding="utf-8"))
            self.assertTrue(all(item["scaffold_owned"] is True and item["managed"] is False for item in payload["applied_writes"]))

    def test_phase1_bootstrap_scaffold_apply_blocks_dirty_target_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-bootstrap-apply-dirty"
            project.mkdir()
            (project / "README.md").write_text("# bootstrap target\n", encoding="utf-8")
            self.git_commit_all(project)
            (project / "uncommitted.txt").write_text("dirty\n", encoding="utf-8")

            _, payload = self.run_tool(
                str(PHASE1_SCAFFOLD),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
                "--apply",
                expect_success=False,
            )

            self.assertEqual(payload["mode"], "apply")
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["token"], "blocked:dirty_target_project")
            self.assertFalse(payload["writes_target_project"])
            self.assertFalse(payload["target_project_write_allowed_by_checker"])
            self.assertFalse((project / ".codex" / "agents" / "thesis-moe-mentor.toml").exists())
            self.assertFalse((project / "MOE.md").exists())
            self.assertFalse((project / "tools" / "thesis_moe_mode.py").exists())

    def test_phase1_bootstrap_scaffold_plan_preserves_existing_private_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-bootstrap-existing"
            project.mkdir()
            (project / ".codex" / "agents").mkdir(parents=True)
            (project / "README.md").write_text("# existing target\n", encoding="utf-8")
            (project / "MOE.md").write_text("# real private prompt fixture\n", encoding="utf-8")
            (project / ".codex" / "agents" / "thesis-moe-mentor.toml").write_text(
                'name = "thesis-moe-mentor"\n'
                'description = "Existing private agent."\n'
                'developer_instructions = "Existing private instructions must not be overwritten."\n',
                encoding="utf-8",
            )
            self.git_commit_all(project)
            before_moe = self.file_digest(project / "MOE.md")
            before_agent = self.file_digest(project / ".codex" / "agents" / "thesis-moe-mentor.toml")

            _, payload = self.run_tool(
                str(PHASE1_SCAFFOLD),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
            )

            planned = {item["role"]: item for item in payload["planned_writes"]}
            self.assertEqual(planned["agent_toml"]["action"], "manual-review-existing")
            self.assertEqual(planned["private_prompt_source"]["action"], "preserve-existing-private-prompt")
            self.assertFalse(planned["agent_toml"]["content_included"])
            self.assertFalse(planned["private_prompt_source"]["content_included"])
            self.assertEqual(self.file_digest(project / "MOE.md"), before_moe)
            self.assertEqual(self.file_digest(project / ".codex" / "agents" / "thesis-moe-mentor.toml"), before_agent)
            self.assertFalse(payload["privacy_boundary"]["private_prompt_body_read"])

    def test_phase1_bootstrap_scaffold_apply_blocks_existing_private_surfaces_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-bootstrap-existing-apply"
            project.mkdir()
            (project / ".codex" / "agents").mkdir(parents=True)
            (project / "README.md").write_text("# existing target\n", encoding="utf-8")
            (project / "MOE.md").write_text("# real private prompt fixture\n", encoding="utf-8")
            (project / ".codex" / "agents" / "thesis-moe-mentor.toml").write_text(
                'name = "thesis-moe-mentor"\n'
                'description = "Existing private agent."\n'
                'developer_instructions = "Existing private instructions must not be overwritten."\n',
                encoding="utf-8",
            )
            self.git_commit_all(project)
            before_moe = self.file_digest(project / "MOE.md")
            before_agent = self.file_digest(project / ".codex" / "agents" / "thesis-moe-mentor.toml")

            _, payload = self.run_tool(
                str(PHASE1_SCAFFOLD),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
                "--apply",
                expect_success=False,
            )

            self.assertEqual(payload["mode"], "apply")
            self.assertEqual(payload["token"], "blocked:existing_phase1_surface_requires_manual_review")
            self.assertFalse(payload["writes_target_project"])
            self.assertFalse(payload["target_project_write_allowed_by_checker"])
            self.assertEqual(self.file_digest(project / "MOE.md"), before_moe)
            self.assertEqual(self.file_digest(project / ".codex" / "agents" / "thesis-moe-mentor.toml"), before_agent)
            self.assertFalse((project / "tools" / "thesis_moe_mode.py").exists())

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

    def test_phase1_readiness_checker_classifies_incomplete_docs_as_repair_lane(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-repair-docs"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-repair-docs", session_id="session-phase1-repair-docs")
            self.add_phase1_wrappers_and_startup_hook(project)
            (project / "docs_bilingual" / "operations" / "thesis_moe_mode_usage.zh-CN.md").write_text(
                "# Incomplete docs\n\nUse `project-on` only.\n",
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
            self.assertEqual(payload["adaptation_lane"], "repair")
            self.assertFalse(payload["control_mode_allowed"])
            self.assertFalse(payload["bootstrap_required"])
            self.assertTrue(payload["repair_required"])
            self.assertEqual(payload["bootstrap_missing_capabilities"], [])
            self.assertIn("blocked:phase1_operator_docs_incomplete", blocker_codes)
            remediation = payload["remediation_plan"]
            self.assertEqual(remediation["lane"], "repair")
            self.assertEqual(remediation["summary"], "repair_existing_phase1_surface_before_gui_control")
            self.assertIn("complete_phase1_operator_docs", remediation["ordered_next_steps"])

    def test_phase1_readiness_checker_blocks_incomplete_startup_hook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-incomplete-startup-hook"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-incomplete-startup-hook", session_id="session-phase1-incomplete-hook")
            self.add_phase1_wrappers_and_startup_hook(project)
            (project / "AGENTS.md").write_text(
                "On startup, run `python .\\tools\\thesis_moe_mode.py status --json` before applying the thesis MOE rules.\n",
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
            self.assertIn("blocked:moe_activation_hook_incomplete", blocker_codes)
            self.assertFalse(payload["startup_activation_hooks"]["hook_found"])
            self.assertTrue(payload["startup_activation_hooks"]["basic_status_hook_found"])
            missing = next(item["missing"] for item in payload["blockers"] if item["code"] == "blocked:moe_activation_hook_incomplete")
            self.assertIn("resume", missing)
            self.assertIn("continue", missing)
            self.assertIn("reload", missing)
            self.assertIn("phase change", missing)

    def test_phase1_readiness_checker_blocks_missing_startup_hook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-missing-startup-hook"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-missing-startup-hook", session_id="session-phase1-missing-hook")
            self.add_phase1_wrappers_and_startup_hook(project)
            (project / "AGENTS.md").unlink()
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
            self.assertIn("blocked:missing_moe_activation_hook", blocker_codes)
            self.assertFalse(payload["startup_activation_hooks"]["hook_found"])
            self.assertFalse(payload["startup_activation_hooks"]["basic_status_hook_found"])

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

    def test_phase1_readiness_checker_accepts_assert_on_disabled_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-assert-on-disabled"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-assert-on-disabled", session_id="session-assert-disabled")
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
            self.assertEqual(payload["cli_contract_check"]["assertion_commands_checked"], ["assert-on"])
            assert_on_fields = payload["cli_contract_check"]["validated_fields"]["assert-on"]
            self.assertIn("effective_enabled", assert_on_fields)
            self.assertIn("effective_source", assert_on_fields)

    def test_phase1_readiness_checker_blocks_assert_on_missing_effective_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-assert-on-missing-effective"
            project.mkdir()
            self.make_project(project, cli_variant="assert_on_missing_effective_enabled")
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
                expect_success=False,
            )

            blocker_codes = {item["code"] for item in payload["blockers"]}
            self.assertIn("blocked:assert_on_contract_invalid", blocker_codes)
            self.assertEqual(payload["cli_contract_check"]["assertion_commands_checked"], ["assert-on"])

    def test_phase1_readiness_checker_blocks_assert_on_write_result_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-assert-on-write-fields"
            project.mkdir()
            self.make_project(project, cli_variant="assert_on_not_read_only")
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
                expect_success=False,
            )

            blocker_codes = {item["code"] for item in payload["blockers"]}
            self.assertIn("blocked:assert_on_not_read_only", blocker_codes)
            self.assertEqual(payload["cli_contract_check"]["assertion_commands_checked"], ["assert-on"])

    def test_phase1_readiness_checker_blocks_assert_on_unknown_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-assert-on-unknown-token"
            project.mkdir()
            self.make_project(project, cli_variant="assert_on_unknown_token")
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
                expect_success=False,
            )

            blocker_codes = {item["code"] for item in payload["blockers"]}
            self.assertIn("blocked:assert_on_contract_invalid", blocker_codes)
            self.assertEqual(payload["cli_contract_check"]["assertion_commands_checked"], ["assert-on"])

    def test_phase1_readiness_checker_blocks_private_prompt_inside_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-private-prompt-state"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-private-prompt-state", session_id="session-private-prompt-state")
            self.add_phase1_wrappers_and_startup_hook(project)
            agent_path = project / ".codex" / "agents" / "thesis-moe-mentor.toml"
            agent_path.write_text(
                agent_path.read_text(encoding="utf-8").replace(
                    'private_prompt_source = "MOE.md"',
                    'private_prompt_source = ".omx/state/thesis_moe/private-note.json"',
                ),
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
            self.assertIn("blocked:private_prompt_source_inside_state", blocker_codes)
            self.assertTrue(payload["private_prompt_source"]["exists"])
            self.assertTrue(payload["private_prompt_source"]["under_state_dir"])
            self.assertFalse(payload["private_prompt_source"]["private_prompt_boundary_ok"])

    def test_phase1_readiness_checker_blocks_private_prompt_inside_agent_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-private-prompt-agent-dir"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-private-prompt-agent-dir", session_id="session-private-prompt-agent")
            self.add_phase1_wrappers_and_startup_hook(project)
            agent_path = project / ".codex" / "agents" / "thesis-moe-mentor.toml"
            agent_path.write_text(
                agent_path.read_text(encoding="utf-8").replace(
                    'private_prompt_source = "MOE.md"',
                    'private_prompt_source = ".codex/agents/thesis-moe-mentor.toml"',
                ),
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
            self.assertIn("blocked:private_prompt_source_inside_agent_dir", blocker_codes)
            self.assertTrue(payload["private_prompt_source"]["exists"])
            self.assertTrue(payload["private_prompt_source"]["under_agent_dir"])
            self.assertFalse(payload["private_prompt_source"]["private_prompt_boundary_ok"])

    def test_phase1_readiness_checker_blocks_private_prompt_inside_gui_managed_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "phase1-private-prompt-gui-managed"
            project.mkdir()
            self.make_stateful_project(project, project_label="phase1-private-prompt-gui-managed", session_id="session-private-prompt-gui")
            self.add_phase1_wrappers_and_startup_hook(project)
            managed_readme = project / "tools" / "project_moe_gui" / "README.md"
            managed_readme.parent.mkdir(parents=True)
            managed_readme.write_text("# Managed GUI artifact\n", encoding="utf-8")
            agent_path = project / ".codex" / "agents" / "thesis-moe-mentor.toml"
            agent_path.write_text(
                agent_path.read_text(encoding="utf-8").replace(
                    'private_prompt_source = "MOE.md"',
                    'private_prompt_source = "tools/project_moe_gui/README.md"',
                ),
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
            self.assertIn("blocked:private_prompt_source_managed_by_toolchain", blocker_codes)
            self.assertTrue(payload["private_prompt_source"]["exists"])
            self.assertTrue(payload["private_prompt_source"]["managed_by_toolchain"])
            self.assertTrue(payload["private_prompt_source"]["under_gui_managed_dir"])
            self.assertFalse(payload["private_prompt_source"]["private_prompt_boundary_ok"])

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
            self.add_phase1_wrappers_and_startup_hook(project)
            self.git_commit_all(project)
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

    def test_check_install_fails_closed_when_toolchain_source_root_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "fixture-stale-source-root"
            project.mkdir()
            self.make_stateful_project(project, project_label="fixture-stale-source-root", session_id="session-stale-source")
            _, install_payload = self.run_tool(
                str(INSTALLER),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
            )
            self.assertTrue(install_payload["ok"], install_payload)
            config_path = project / "tools" / "project_moe_gui" / "project_moe_gui.config.json"
            config = json.loads(config_path.read_text(encoding="utf-8-sig"))
            stale_root = project / ".deleted-worktree" / "tools" / "project_moe_gui_toolchain"
            config["toolchain_source_root"] = str(stale_root)
            config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            self.git_commit_all(project)

            _, payload = self.run_tool(str(CHECKER), "--target-project", str(project), "--skip-runtime-import", expect_success=False)

            self.assertEqual(payload["token"], "blocked:managed_file_hash_mismatch", payload)
            blocker_codes = {item["code"] for item in payload["blockers"]}
            self.assertIn("blocked:toolchain_source_root_unavailable", blocker_codes)
            self.assertEqual(payload["toolchain_source_status"], "missing")


    def test_update_repairs_manifest_matching_stale_toolchain_source_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "fixture-update-stale-source-root"
            project.mkdir()
            self.make_stateful_project(project, project_label="fixture-update-stale-source-root", session_id="session-update-stale")
            _, install_payload = self.run_tool(
                str(INSTALLER),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
            )
            self.assertTrue(install_payload["ok"], install_payload)
            config_path = project / "tools" / "project_moe_gui" / "project_moe_gui.config.json"
            config = json.loads(config_path.read_text(encoding="utf-8-sig"))
            config["toolchain_source_root"] = str(project / ".deleted-worktree" / "tools" / "project_moe_gui_toolchain")
            config_text = json.dumps(config, ensure_ascii=False, indent=2) + "\n"
            config_path.write_text(config_text, encoding="utf-8")
            manifest_path = project / "tools" / "project_moe_gui" / "project_moe_gui.install-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            for item in manifest["managed_files"]:
                if item.get("path") == "tools/project_moe_gui/project_moe_gui.config.json":
                    item["sha256"] = hashlib.sha256(config_path.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            self.git_commit_all(project)

            _, check_payload = self.run_tool(str(CHECKER), "--target-project", str(project), "--skip-runtime-import", expect_success=False)
            self.assertEqual(check_payload["token"], "blocked:toolchain_source_root_unavailable", check_payload)

            _, update_payload = self.run_tool(str(UPDATER), "--target-project", str(project), expect_success=True)
            self.assertEqual(update_payload["token"], "ok", update_payload)
            self.assertFalse(update_payload["no_op"], update_payload)
            repaired = json.loads(config_path.read_text(encoding="utf-8-sig"))
            self.assertNotIn(".deleted-worktree", repaired["toolchain_source_root"])

            _, final_check = self.run_tool(str(CHECKER), "--target-project", str(project), "--skip-runtime-import")
            self.assertEqual(final_check["status"], "up_to_date", final_check)
            self.assertEqual(final_check["toolchain_source_status"], "import_ok", final_check)


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

    def test_uninstall_plan_is_dry_run_and_preserves_private_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_stateful_project(project, project_label="fixture-uninstall", session_id="session-uninstall")
            self.run_tool(
                str(INSTALLER),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
            )
            private_before = self.private_project_digests(project)

            _, payload = self.run_tool(str(UNINSTALL_PLANNER), "--target-project", str(project))

            self.assertEqual(payload["command"], "plan_project_moe_gui_uninstall")
            self.assertEqual(payload["mode"], "dry-run")
            self.assertTrue(payload["read_only"])
            self.assertFalse(payload["writes_target_project"])
            self.assertTrue(payload["apply_supported"])
            self.assertFalse(payload["state_deletion_allowed"])
            self.assertFalse(payload["private_files_deletion_allowed"])
            delete_paths = {item["path"]: item for item in payload["planned_deletes"]}
            self.assertEqual(delete_paths["tools/project_moe_gui/launcher.py"]["action"], "delete")
            self.assertEqual(delete_paths["tools/project_moe_gui/project_moe_gui.install-manifest.json"]["action"], "delete")
            self.assertIn("MOE.md", payload["protected_paths_preserved"])
            self.assertIn(".codex/agents/*.toml", payload["protected_paths_preserved"])
            self.assertIn(".omx/state/thesis_moe/", payload["protected_paths_preserved"])
            self.assertTrue((project / "tools" / "project_moe_gui" / "launcher.py").exists())
            self.assertEqual(private_before, self.private_project_digests(project))

    def test_uninstall_apply_deletes_only_manifest_owned_gui_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_stateful_project(project, project_label="fixture-uninstall-apply", session_id="session-uninstall-apply")
            self.run_tool(
                str(INSTALLER),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
            )
            private_before = self.private_project_digests(project)
            launcher = project / "tools" / "project_moe_gui" / "launcher.py"
            manifest = project / "tools" / "project_moe_gui" / "project_moe_gui.install-manifest.json"
            config = project / "tools" / "project_moe_gui" / "project_moe_gui.config.json"
            command = project / "project-moe-gui.cmd"

            _, payload = self.run_tool(str(UNINSTALL_PLANNER), "--target-project", str(project), "--apply")

            self.assertEqual(payload["command"], "plan_project_moe_gui_uninstall")
            self.assertEqual(payload["mode"], "apply")
            self.assertEqual(payload["token"], "ok")
            self.assertTrue(payload["apply_requested"])
            self.assertTrue(payload["apply_supported"])
            self.assertTrue(payload["delete_executed"])
            self.assertFalse(payload["read_only"])
            self.assertTrue(payload["writes_target_project"])
            self.assertFalse(launcher.exists())
            self.assertFalse(manifest.exists())
            self.assertFalse(config.exists())
            self.assertFalse(command.exists())
            self.assertIn("tools/project_moe_gui/launcher.py", payload["uninstall_receipt"]["deleted_files"])
            self.assertEqual(private_before, self.private_project_digests(project))
            self.assertTrue((project / ".omx" / "state" / "thesis_moe").exists())

    def test_uninstall_plan_fails_closed_on_managed_hash_mismatch(self) -> None:
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

            _, payload = self.run_tool(str(UNINSTALL_PLANNER), "--target-project", str(project), expect_success=False)

            self.assertEqual(payload["token"], "blocked:managed_file_hash_mismatch")
            delete_paths = {item["path"]: item for item in payload["planned_deletes"]}
            self.assertEqual(delete_paths["tools/project_moe_gui/launcher.py"]["action"], "blocked")
            self.assertFalse(delete_paths["tools/project_moe_gui/launcher.py"]["safe_to_delete"])

    def test_uninstall_apply_fails_closed_on_manifest_path_outside_managed_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_stateful_project(project, project_label="fixture-uninstall-allowlist", session_id="session-uninstall-allowlist")
            self.run_tool(
                str(INSTALLER),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
            )
            private_before = self.private_project_digests(project)
            manifest_path = project / "tools" / "project_moe_gui" / "project_moe_gui.install-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            manifest["managed_files"].append({"path": "MOE.md", "role": "managed", "sha256": self.file_digest(project / "MOE.md")})
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

            _, payload = self.run_tool(str(UNINSTALL_PLANNER), "--target-project", str(project), "--apply", expect_success=False)

            self.assertEqual(payload["token"], "blocked:uninstall_path_not_in_managed_allowlist")
            self.assertFalse(payload["delete_executed"])
            self.assertTrue((project / "tools" / "project_moe_gui" / "launcher.py").exists())
            self.assertEqual(private_before, self.private_project_digests(project))

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
            self.add_phase1_wrappers_and_startup_hook(project)
            self.git_commit_all(project)
            self.run_tool(
                str(INSTALLER),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
            )
            self.git_commit_all(project)
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
            self.assertIn(payload["token"], GUI_PREFLIGHT_ALLOWED_TOKENS, payload)
            self.assertEqual(payload["gui_shell_contract"], "project-moe-gui-shell-v1")
            self.assertNotEqual(payload["token"], "blocked:gui_not_implemented_phase2a")
            self.assertNotIn("Interactive PySide6 GUI is implemented in Phase 2B.", result.stdout)

    def test_installed_launcher_no_args_defaults_to_visible_human_launch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project)
            self.add_phase1_wrappers_and_startup_hook(project)
            self.git_commit_all(project)
            self.install_fixture_gui(project)
            self.git_commit_all(project)

            env = dict(os.environ)
            env["PROJECT_MOE_GUI_DRY_RUN_VISIBLE"] = "1"
            result = subprocess.run(
                [sys.executable, str(project / "tools" / "project_moe_gui" / "launcher.py")],
                cwd=project,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
            self.assertIn("ok: Visible GUI launch dry-run passed.", result.stdout)
            self.assertNotIn("blocked:visible_gui_launch_requires_explicit_approval", result.stdout)

    def test_installed_launcher_visible_launch_allows_diagnostic_preflight_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project)
            self.add_phase1_wrappers_and_startup_hook(project)
            self.git_commit_all(project)
            self.install_fixture_gui(project)
            self.git_commit_all(project)

            fake_source = Path(tmp) / "fake-source"
            fake_package = fake_source / "src" / "project_moe_gui"
            fake_package.mkdir(parents=True)
            marker = project / "visible-launch-called.marker"
            (fake_package / "__init__.py").write_text("", encoding="utf-8")
            (fake_package / "toolchain.py").write_text(
                "def check_phase1_readiness(*args, **kwargs):\n"
                "    return {\n"
                "        'ok': True,\n"
                "        'token': 'ok',\n"
                "        'readiness_status': 'ready',\n"
                "        'adaptation_lane': 'ready',\n"
                "        'bootstrap_required': False,\n"
                "        'repair_required': False,\n"
                "        'control_mode_allowed': True,\n"
                "        'cli_execution_mode': 'execute-read-contract',\n"
                "        'git_status': {'token': 'ok'},\n"
                "        'blockers': [],\n"
                "    }\n",
                encoding="utf-8",
            )
            (fake_package / "gui_shell.py").write_text(
                "from pathlib import Path\n"
                "def build_gui_preflight(*args, **kwargs):\n"
                "    return {\n"
                "        'schema_version': 1,\n"
                "        'ok': False,\n"
                "        'token': 'blocked:invalid_session_record',\n"
                "        'exit_code': 5,\n"
                "        'message': 'Historical session records need review.',\n"
                "        'view_model': {'window_structure': {}, 'diagnostics_card': {'blockers': [{'token': 'blocked:invalid_session_record'}]}},\n"
                "        'blockers': [{'token': 'blocked:invalid_session_record', 'message': 'diagnostic only'}],\n"
                "    }\n"
                "def launch_visible(view_model):\n"
                f"    Path({str(marker)!r}).write_text('called', encoding='utf-8')\n"
                "    return 0\n",
                encoding="utf-8",
            )
            config_path = project / "tools" / "project_moe_gui" / "project_moe_gui.config.json"
            config = json.loads(config_path.read_text(encoding="utf-8-sig"))
            config["toolchain_source_root"] = str(fake_source)
            config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(project / "tools" / "project_moe_gui" / "launcher.py"), "--allow-visible", "--json"],
                cwd=project,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
            self.assertEqual(marker.read_text(encoding="utf-8"), "called")
            self.assertNotIn("blocked:invalid_session_record", result.stdout)

    def test_installed_launcher_visible_dry_run_does_not_require_pyside6_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project)
            self.add_phase1_wrappers_and_startup_hook(project)
            self.git_commit_all(project)
            self.install_fixture_gui(project)
            self.git_commit_all(project)

            fake_source = Path(tmp) / "fake-source"
            fake_package = fake_source / "src" / "project_moe_gui"
            fake_package.mkdir(parents=True)
            (fake_package / "__init__.py").write_text("", encoding="utf-8")
            (fake_package / "toolchain.py").write_text(
                "def check_phase1_readiness(*args, **kwargs):\n"
                "    return {\n"
                "        'ok': True,\n"
                "        'token': 'ok',\n"
                "        'readiness_status': 'ready',\n"
                "        'adaptation_lane': 'installed',\n"
                "        'bootstrap_required': False,\n"
                "        'repair_required': False,\n"
                "        'control_mode_allowed': True,\n"
                "        'cli_execution_mode': 'read-only',\n"
                "        'git_status': {'token': 'ok'},\n"
                "        'blockers': [],\n"
                "    }\n",
                encoding="utf-8",
            )
            (fake_package / "gui_shell.py").write_text(
                "def build_gui_preflight(*args, **kwargs):\n"
                "    return {\n"
                "        'schema_version': 1,\n"
                "        'ok': False,\n"
                "        'token': 'blocked:pyside6_unavailable',\n"
                "        'exit_code': 5,\n"
                "        'message': 'PySide6 is unavailable in this test fixture.',\n"
                "        'view_model': {'window_structure': {}},\n"
                "    }\n"
                "def launch_visible(view_model):\n"
                "    raise RuntimeError('should_not_launch_in_dry_run')\n",
                encoding="utf-8",
            )
            config_path = project / "tools" / "project_moe_gui" / "project_moe_gui.config.json"
            config = json.loads(config_path.read_text(encoding="utf-8-sig"))
            config["toolchain_source_root"] = str(fake_source)
            config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            env = dict(os.environ)
            env["PROJECT_MOE_GUI_DRY_RUN_VISIBLE"] = "1"
            result = subprocess.run(
                [sys.executable, str(project / "tools" / "project_moe_gui" / "launcher.py")],
                cwd=project,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
            self.assertIn("ok: Visible GUI launch dry-run passed.", result.stdout)
            self.assertNotIn("blocked:pyside6_unavailable", result.stdout)

    def test_installed_launcher_json_without_preflight_stays_machine_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project)
            self.add_phase1_wrappers_and_startup_hook(project)
            self.git_commit_all(project)
            self.install_fixture_gui(project)
            self.git_commit_all(project)

            payload = self.run_installed_launcher(project)

            self.assertFalse(payload["ok"], payload)
            self.assertEqual(payload["token"], "blocked:json_requires_preflight_for_non_visible_automation")
            self.assertEqual(payload["exit_code"], 2)
            self.assertIn("Use --preflight --json", payload["message"])

    def test_installed_launcher_missing_mode_cli_returns_bootstrap_scaffold_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project)
            self.git_commit_all(project)
            self.run_tool(
                str(INSTALLER),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
            )
            private_before = {
                "moe_prompt": self.file_digest(project / "MOE.md"),
                "agent_toml": self.file_digest(project / ".codex" / "agents" / "thesis-moe-mentor.toml"),
            }
            (project / "tools" / "thesis_moe_mode.py").unlink()

            payload = self.run_installed_launcher(project, "--preflight")

            self.assertFalse(payload["ok"], payload)
            self.assertEqual(payload["token"], "blocked:missing_mode_cli")
            self.assertEqual(payload["adaptation_lane"], "bootstrap")
            self.assertTrue(payload["bootstrap_required"])
            self.assertFalse(payload["control_mode_allowed"])
            self.assertFalse(payload["target_project_write_allowed_by_launcher"])
            self.assertEqual(payload["bootstrap_plan"]["command"], "scaffold_project_moe_phase1")
            self.assertFalse(payload["bootstrap_plan"]["writes_target_project"])
            self.assertFalse(payload["bootstrap_plan"]["privacy_boundary"]["private_prompt_body_read"])
            self.assertEqual(payload["operator_next_steps"], payload["bootstrap_plan"]["operator_next_steps"])
            next_actions = [step["action"] for step in payload["operator_next_steps"]]
            self.assertIn("create_or_update_phase1_contract_files", next_actions)
            self.assertIn("run_execute_read_contract_readiness_check", next_actions)
            planned = {item["role"]: item for item in payload["bootstrap_plan"]["planned_writes"]}
            self.assertEqual(planned["mode_cli"]["action"], "create")
            self.assertFalse(any(item["content_included"] for item in payload["bootstrap_plan"]["planned_writes"]))
            private_after = {
                "moe_prompt": self.file_digest(project / "MOE.md"),
                "agent_toml": self.file_digest(project / ".codex" / "agents" / "thesis-moe-mentor.toml"),
            }
            self.assertEqual(private_after, private_before)

    def test_installed_launcher_readiness_gate_skips_cli_when_static_surface_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_project(project)
            mode_cli = project / "tools" / "thesis_moe_mode.py"
            mode_cli.write_text(
                mode_cli.read_text(encoding="utf-8").replace(
                    "import json\n",
                    "import json\nfrom pathlib import Path\nPath('launcher-mode-cli-executed.txt').write_text('executed', encoding='utf-8')\n",
                    1,
                ),
                encoding="utf-8",
            )
            self.git_commit_all(project)
            self.run_tool(
                str(INSTALLER),
                "--target-project",
                str(project),
                "--agent-name",
                "thesis-moe-mentor",
                "--state-namespace",
                "thesis_moe",
                "--skip-cli-contract-check",
            )
            self.git_commit_all(project)

            payload = self.run_installed_launcher(project, "--preflight")

            self.assertFalse(payload["ok"], payload)
            self.assertEqual(payload["token"], "blocked:missing_phase1_wrapper")
            self.assertFalse((project / "launcher-mode-cli-executed.txt").exists())
            self.assertEqual(payload["cli_contract_check"]["skip_reason"], "static_surface_blockers_present")
            self.assertIn("blocked:missing_phase1_wrapper", payload["cli_contract_check"]["static_surface_blocking_codes"])
            self.assertFalse(payload["control_mode_allowed"])

    def test_installed_launcher_allows_runtime_namespace_state_dirty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"
            project.mkdir()
            self.make_stateful_project(project, project_label="fixture-runtime-dirty", session_id="session-runtime-dirty")
            self.add_phase1_wrappers_and_startup_hook(project)
            self.git_commit_all(project)
            self.install_fixture_gui(project)
            self.git_commit_all(project)
            state_file = project / ".omx" / "state" / "thesis_moe" / "project-default.json"
            state_file.parent.mkdir(parents=True, exist_ok=True)
            state_file.write_text(json.dumps({"schema_version": 1, "enabled": True}, ensure_ascii=False), encoding="utf-8")

            payload = self.run_installed_launcher(project, "--preflight")

            self.assertIn(payload["token"], GUI_PREFLIGHT_ALLOWED_TOKENS, payload)
            gate = payload["phase1_readiness_gate"]
            self.assertEqual(gate["readiness_status"], "ready")
            self.assertEqual(gate["git_status"]["token"], "ok:runtime_state_dirty_allowed")
            self.assertTrue(gate["git_status"]["runtime_state_dirty_allowed"])
            self.assertEqual(gate["git_status"]["runtime_state_dirty_details"]["unsafe_count"], 0)

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
        return gui_shell.execute_write_action_with_readback(config, action, session_id=session_id, project_root=project)

    def test_phase2c_fixture_a_full_install_check_update_status_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "fixture-a"
            project.mkdir()
            self.make_stateful_project(project, project_label="fixture-a", session_id="session-fixture-a")
            self.add_phase1_wrappers_and_startup_hook(project)
            self.git_commit_all(project)
            private_before = self.private_project_digests(project)

            install_payload = self.install_fixture_gui(project)
            self.git_commit_all(project)
            self.assertEqual(install_payload["mode"], "apply")
            self.assertEqual(install_payload["target_project_root"], str(project.resolve()))
            installed_config = json.loads((project / "tools" / "project_moe_gui" / "project_moe_gui.config.json").read_text(encoding="utf-8-sig"))
            self.assertNotIn("target_project_root", installed_config)
            self.assertEqual(installed_config["installed_target_project_root"], str(project.resolve()))
            self.assertIn("runtime_python", installed_config)
            expected_source_root = stable_toolchain_source_root()
            self.assertEqual(installed_config["toolchain_source_root"], str(expected_source_root))

            launcher_text = (project / "tools" / "project_moe_gui" / "launcher.py").read_text(encoding="utf-8")
            command_text = (project / "project-moe-gui.cmd").read_text(encoding="utf-8")
            self.assertIn("maybe_reexec_with_runtime", launcher_text)
            self.assertIn("PROJECT_MOE_GUI_RUNTIME_REEXEC", launcher_text)
            self.assertIn("set PYTHONUTF8=1", command_text)

            _, check_payload = self.run_tool(str(CHECKER), "--target-project", str(project), "--skip-runtime-import")
            self.assertEqual(check_payload["status"], "up_to_date")
            self.assertEqual(check_payload["runtime_status"], "skipped_by_flag")

            _, update_payload = self.run_tool(str(UPDATER), "--target-project", str(project), "--dry-run")
            self.assertTrue(update_payload["no_op"], update_payload)
            self.assertEqual(update_payload["status"], "up_to_date")

            preflight = self.run_installed_launcher(project, "--preflight")
            self.assertIn(preflight["token"], GUI_PREFLIGHT_ALLOWED_TOKENS, preflight)
            self.assertIn("launcher_runtime_python", preflight)
            self.assertIn("launcher_runtime_reexec", preflight)
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
            self.add_phase1_wrappers_and_startup_hook(project)
            self.git_commit_all(project)
            sessions_root = project / ".omx" / "state" / "thesis_moe" / "sessions"
            invalid_path = sessions_root / "session-invalid.json"
            invalid_path.write_text("{invalid-json", encoding="utf-8")
            legacy_path = sessions_root / "session-legacy.json"
            legacy_path.write_text(
                json.dumps({"session_id": "session-legacy", "enabled": False, "token": "ok"}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            self.install_fixture_gui(project)
            self.git_commit_all(project)

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
            self.add_phase1_wrappers_and_startup_hook(project_a)
            self.git_commit_all(project_a)
            self.make_stateful_project(project_b, project_label="fixture-b", session_id="session-fixture-b")
            self.add_phase1_wrappers_and_startup_hook(project_b)
            self.git_commit_all(project_b)
            self.install_fixture_gui(project_a)
            self.git_commit_all(project_a)
            self.install_fixture_gui(project_b)
            self.git_commit_all(project_b)

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


    def test_qfluent_visual_dependency_contract_requires_license_review(self) -> None:
        from project_moe_gui.qfluent_runtime import check_qfluent_runtime, expected_qfluent_dependency, qfluent_license_manifest

        dependency = expected_qfluent_dependency()
        self.assertEqual(dependency["package_name"], "PySide6-Fluent-Widgets")
        self.assertEqual(dependency["import_name"], "qfluentwidgets")
        self.assertEqual(dependency["license_family"], "GPLv3-or-commercial-dual-license")
        self.assertTrue(dependency["fail_closed_if_missing"])

        manifest = qfluent_license_manifest()
        self.assertEqual(manifest["package_name"], "PySide6-Fluent-Widgets")
        self.assertEqual(manifest["import_name"], "qfluentwidgets")
        self.assertEqual(manifest["noncommercial_license"], "GPLv3")
        self.assertTrue(manifest["commercial_use_requires_review"])
        self.assertTrue(manifest["redistribution_requires_license_review"])
        self.assertTrue(any("pypi.org/project/PySide6-Fluent-Widgets" in url for url in manifest["evidence_urls"]))

        ok_payload = check_qfluent_runtime(
            import_probe=lambda import_name: object(),
            metadata_probe=lambda package_name: {"version": "1.11.2", "license": "GPLv3"},
        )
        self.assertTrue(ok_payload["ok"], ok_payload)
        self.assertEqual(ok_payload["token"], "ok")
        self.assertEqual(ok_payload["import_status"], "import_ok")
        self.assertEqual(ok_payload["installed_version"], "1.11.2")
        self.assertTrue(ok_payload["license_manifest"]["commercial_use_requires_review"])

        def missing_import(_name: str) -> object:
            raise ModuleNotFoundError(_name)

        missing_payload = check_qfluent_runtime(import_probe=missing_import)
        self.assertFalse(missing_payload["ok"], missing_payload)
        self.assertEqual(missing_payload["token"], "blocked:qfluentwidgets_unavailable")
        self.assertEqual(missing_payload["import_status"], "missing")

    def test_qfluent_default_import_probe_suppresses_import_chatter(self) -> None:
        from project_moe_gui.qfluent_runtime import _default_import_probe

        with tempfile.TemporaryDirectory() as tmp:
            module_path = Path(tmp) / "noisy_import_probe.py"
            module_path.write_text(
                "print('third party stdout chatter')\n"
                "import sys\n"
                "print('third party stderr chatter', file=sys.stderr)\n"
                "VALUE = 'loaded'\n",
                encoding="utf-8",
            )
            sys.path.insert(0, tmp)
            sys.modules.pop("noisy_import_probe", None)
            stdout = io.StringIO()
            stderr = io.StringIO()
            try:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    module = _default_import_probe("noisy_import_probe")
            finally:
                sys.modules.pop("noisy_import_probe", None)
                try:
                    sys.path.remove(tmp)
                except ValueError:
                    pass

        self.assertEqual(getattr(module, "VALUE"), "loaded")
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")

    def test_gui_view_model_declares_fluent_cards_sidebar_and_license_gate(self) -> None:
        from project_moe_gui.gui_shell import build_view_model
        from project_moe_gui.qfluent_runtime import check_qfluent_runtime

        qfluent_status = check_qfluent_runtime(
            import_probe=lambda import_name: object(),
            metadata_probe=lambda package_name: {"version": "1.11.2", "license": "GPLv3"},
        )
        config = {
            "agent_name": "thesis-moe-mentor",
            "state_namespace": "thesis_moe",
            "runtime_project_root": "D:/target",
            "cli_contract": "project-moe-cli-v1",
        }
        project_status = {"ok": True, "token": "ok", "project_default_enabled": True, "git_branch": "main"}
        status_payload = {"ok": True, "token": "ok", "effective_enabled": True, "effective_source": "project-default"}
        sessions_payload = {
            "ok": True,
            "token": "ok",
            "sessions": [{"session_id": "session-1234567890abcdef", "effective_enabled": True, "token": "ok", "valid": True}],
        }

        view_model = build_view_model(
            config,
            project_status=project_status,
            sessions_payload=sessions_payload,
            status_payload=status_payload,
            pyside6_available=True,
            qfluent_status=qfluent_status,
        )

        region_ids = [region["id"] for region in view_model["window_structure"]["regions"]]
        self.assertIn("navigation_sidebar", region_ids)
        self.assertIn("status_overview_cards", region_ids)
        self.assertIn("diagnostics_card", region_ids)
        self.assertIn("session_table", region_ids)
        self.assertEqual(view_model["visual"]["library"], "QFluentWidgets")
        self.assertEqual(view_model["visual"]["qfluentwidgets_status"]["token"], "ok")
        self.assertTrue(view_model["visual"]["license_manifest"]["commercial_use_requires_review"])
        self.assertIn("Project", [item["label"] for item in view_model["navigation_sidebar"]["items"]])
        self.assertGreaterEqual(len(view_model["status_cards"]), 3)
        self.assertEqual(view_model["close_behavior"]["default_close_action"], "ask")

    def test_close_behavior_requires_dialog_and_explicit_tray_hide(self) -> None:
        from project_moe_gui.gui_shell import close_behavior_contract

        contract = close_behavior_contract()
        self.assertFalse(contract["auto_hide_to_tray"])
        self.assertEqual(contract["default_close_action"], "ask")
        self.assertEqual([option["id"] for option in contract["dialog_options"]], ["exit", "hide_to_tray", "cancel"])
        self.assertTrue(contract["tray_icon_created_only_after_explicit_hide"])
        self.assertEqual([item["id"] for item in contract["tray_menu_items"]], ["show", "exit"])

    def test_daemon_launch_plan_hides_cmd_window_and_uses_duplicate_lock(self) -> None:
        from project_moe_gui.daemon import build_daemon_launch_plan, windows_process_flags

        launcher = Path("tools/project_moe_gui/launcher.py")
        plan = build_daemon_launch_plan(
            launcher,
            no_args=True,
            platform_name="win32",
            runtime_python="D:/runtime/.venv/Scripts/python.exe",
            project_root="D:/target",
        )
        self.assertTrue(plan["uses_daemon"])
        self.assertTrue(plan["duplicate_instance_guard"]["enabled"])
        self.assertEqual(plan["cmd_window_policy"], "no_persistent_cmd")
        self.assertIn(plan["windows_creation_flags_label"], {"CREATE_NO_WINDOW", "DETACHED_PROCESS", "CREATE_NO_WINDOW|DETACHED_PROCESS"})
        self.assertGreater(windows_process_flags(platform_name="win32"), 0)
        self.assertIn("PROJECT_MOE_GUI_DAEMON_CHILD", plan["environment_overrides"])
        self.assertEqual(plan["argv"][0], "D:/runtime/.venv/Scripts/python.exe")
        self.assertEqual(plan["project_root"], str(Path("D:/target").resolve(strict=False)))
        runtime_dir = Path("D:/target").resolve(strict=False) / ".project-runtime" / "project_moe_gui"
        self.assertEqual(Path(plan["diagnostics_log"]), runtime_dir / "project_moe_gui.daemon.log")
        self.assertEqual(Path(plan["duplicate_instance_guard"]["lock_path"]), runtime_dir / "project_moe_gui.daemon.lock")
        self.assertNotIn("tools", Path(plan["diagnostics_log"]).parts)
        self.assertEqual(plan["stdout_stderr_policy"], "append_to_diagnostics_log")

        foreground = build_daemon_launch_plan(launcher, preflight=True, json_mode=True, platform_name="win32")
        self.assertFalse(foreground["uses_daemon"])
        self.assertEqual(foreground["reason"], "preflight_json_runs_in_foreground")

    def test_visible_launch_uses_qfluent_theme_enum_and_smoke_timer(self) -> None:
        import inspect
        from project_moe_gui import gui_shell

        source = inspect.getsource(gui_shell.launch_visible)
        self.assertIn("Theme.AUTO", source)
        self.assertNotIn('setTheme("AUTO")', source)
        self.assertIn("PROJECT_MOE_GUI_VISIBLE_SMOKE_EXIT_MS", source)
        self.assertIn("QTimer(window)", source)
        self.assertIn("app.exit(0)", source)

    def test_installer_config_and_launcher_include_daemon_and_qfluent_metadata(self) -> None:
        from project_moe_gui.toolchain import cmd_text, config_payload, launcher_text

        cfg = config_payload(Path("D:/target"), "thesis-moe-mentor", "thesis_moe", Path("tools/thesis_moe_mode.py"), Path("D:/runtime"))
        self.assertEqual(cfg["visual_dependency"]["package_name"], "PySide6-Fluent-Widgets")
        self.assertEqual(cfg["visual_dependency"]["import_name"], "qfluentwidgets")
        self.assertTrue(cfg["gui_dependency_license_manifest"]["commercial_use_requires_review"])
        self.assertTrue(cfg["daemon_launch"]["duplicate_instance_guard"]["enabled"])
        self.assertEqual(cfg["daemon_launch"]["argv"][0], "D:\\runtime\\.venv\\Scripts\\python.exe")
        self.assertEqual(cfg["daemon_launch"]["project_root"], "D:\\target")
        runtime_dir = Path("D:/target").resolve(strict=False) / ".project-runtime" / "project_moe_gui"
        self.assertEqual(Path(cfg["daemon_launch"]["diagnostics_log"]), runtime_dir / "project_moe_gui.daemon.log")
        self.assertEqual(Path(cfg["daemon_launch"]["duplicate_instance_guard"]["lock_path"]), runtime_dir / "project_moe_gui.daemon.lock")
        self.assertEqual(cfg["close_behavior"]["default_close_action"], "ask")

        launcher = launcher_text()
        self.assertIn("build_daemon_launch_plan", launcher)
        self.assertIn("PROJECT_MOE_GUI_DAEMON_CHILD", launcher)
        self.assertIn("CREATE_NO_WINDOW", launcher)
        self.assertIn("qfluent_runtime", launcher)
        self.assertIn("blocked:visible_gui_launch_failed", launcher)
        self.assertIn("append_to_diagnostics_log", launcher)

        command_text = cmd_text()
        self.assertIn("PROJECT_MOE_GUI_DAEMON_CHILD", command_text)
        self.assertIn("python", command_text.lower())


if __name__ == "__main__":
    unittest.main()
