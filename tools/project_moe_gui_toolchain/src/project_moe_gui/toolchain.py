from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

from project_moe_gui import CLI_CONTRACT, TOOLCHAIN_NAME, TOOLCHAIN_VERSION
from project_moe_gui.gui_shell import GUI_SHELL_CONTRACT


SCHEMA_VERSION = 1
DEFAULT_MODE_CLI = Path("tools/thesis_moe_mode.py")
DEFAULT_SHARED_RUNTIME_ROOT = Path(r"D:\PythonProject_langgraph\.shared_runtimes\pyside6")
CONFIG_RELATIVE = Path("tools/project_moe_gui/project_moe_gui.config.json")
MANIFEST_RELATIVE = Path("tools/project_moe_gui/project_moe_gui.install-manifest.json")
LAUNCHER_RELATIVE = Path("tools/project_moe_gui/launcher.py")
README_RELATIVE = Path("tools/project_moe_gui/README.md")
CMD_RELATIVE = Path("project-moe-gui.cmd")
MANAGED_RELATIVES = [LAUNCHER_RELATIVE, CONFIG_RELATIVE, README_RELATIVE, CMD_RELATIVE]
PROJECT_EVIDENCE = [".git", "AGENTS.md", "pyproject.toml", "requirements.txt", "README.md", "setup.cfg", "setup.py", "poetry.lock", "uv.lock"]
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
NAMESPACE_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def norm(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def blocker(code: str, message: str, **extra: Any) -> dict[str, Any]:
    payload = {"code": code, "message": message}
    payload.update(extra)
    return payload


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def load_json(path: Path, code: str, errors: list[dict[str, Any]]) -> dict[str, Any] | None:
    try:
        return json.loads(read_text(path))
    except FileNotFoundError:
        errors.append(blocker(code, f"Required JSON file is missing: {norm(path)}"))
    except Exception as exc:
        errors.append(blocker("blocked:invalid_json", f"Cannot parse JSON file: {norm(path)}", error=str(exc)))
    return None


def write_text_if_changed(path: Path, text: str) -> str:
    old = read_text(path) if path.exists() else None
    if old == text:
        return "unchanged"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return "updated" if old is not None else "created"


def write_json_if_changed(path: Path, data: dict[str, Any]) -> str:
    return write_text_if_changed(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_project(value: str) -> tuple[Path | None, dict[str, Any] | None]:
    if not value.strip():
        return None, blocker("blocked:missing_target_project", "--target-project is required.")
    root = Path(value).expanduser().resolve(strict=False)
    if not root.exists() or not root.is_dir():
        return root, blocker("blocked:target_project_not_found", "Target project directory does not exist.", target_project=str(root))
    return root, None


def project_evidence(root: Path) -> list[str]:
    return [item for item in PROJECT_EVIDENCE if (root / item).exists()]


def safe_relative(root: Path, relative: str | Path, token: str = "blocked:path_outside_project") -> tuple[Path | None, dict[str, Any] | None]:
    rel = Path(relative)
    if rel.is_absolute():
        return None, blocker(token, "Absolute project-managed paths are not allowed.", path=str(relative))
    if any(part == ".." for part in rel.parts):
        return None, blocker("blocked:path_traversal", "Relative path must not contain '..'.", path=str(relative))
    resolved_root = root.resolve(strict=False)
    full = (resolved_root / rel).resolve(strict=False)
    try:
        full.relative_to(resolved_root)
    except ValueError:
        return None, blocker(token, "Resolved path escapes target project root.", path=str(relative), resolved=str(full))
    return full, None


def validate_identifiers(agent_name: str, namespace: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if not NAME_RE.match(agent_name or ""):
        errors.append(blocker("blocked:invalid_agent_name", "Agent name must be a stable file-safe identifier.", agent_name=agent_name))
    if not NAMESPACE_RE.match(namespace or "") or "/" in namespace or "\\" in namespace:
        errors.append(blocker("blocked:invalid_state_namespace", "State namespace must be a stable directory-safe identifier.", state_namespace=namespace))
    return errors


def check_agent_toml(root: Path, agent_name: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    rel = Path(".codex/agents") / f"{agent_name}.toml"
    path, err = safe_relative(root, rel, "blocked:agent_toml_path_invalid")
    if err:
        return [err]
    assert path is not None
    if not path.exists():
        return [blocker("blocked:missing_agent_toml", "Target project must define the MOE agent TOML before GUI install.", path=norm(rel))]
    if tomllib is not None:
        try:
            data = tomllib.loads(read_text(path))
            if data.get("name") != agent_name:
                errors.append(blocker("blocked:agent_name_mismatch", "Agent TOML top-level name must match --agent-name.", expected=agent_name, observed=data.get("name")))
        except Exception as exc:
            errors.append(blocker("blocked:invalid_agent_toml", "Cannot parse target agent TOML.", path=norm(rel), error=str(exc)))
    return errors


def run_cli(root: Path, mode_cli: Path, command: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    full, err = safe_relative(root, mode_cli, "blocked:mode_cli_path_invalid")
    if err:
        return None, err
    assert full is not None
    if not full.exists():
        return None, blocker("blocked:missing_mode_cli", "Target project mode CLI is missing.", path=norm(mode_cli))
    try:
        result = subprocess.run(
            [sys.executable, str(full), command, "--json"],
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, blocker("blocked:mode_cli_timeout", "Mode CLI timed out during read-only contract check.", command=command)
    except Exception as exc:
        return None, blocker("blocked:mode_cli_invocation_failed", "Cannot invoke target project mode CLI.", command=command, error=str(exc))
    if result.returncode != 0:
        return None, blocker("blocked:mode_cli_failed", "Target project mode CLI returned non-zero.", command=command, exit_code=result.returncode, stderr=result.stderr[-800:])
    try:
        return json.loads(result.stdout), None
    except Exception as exc:
        return None, blocker("blocked:mode_cli_invalid_json", "Target project mode CLI did not emit valid JSON.", command=command, error=str(exc), stdout=result.stdout[-800:])


def check_cli_contract(root: Path, mode_cli: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    details: dict[str, Any] = {"mode_cli": norm(mode_cli), "commands_checked": []}
    for command in ["project-status", "list-sessions", "status"]:
        payload, err = run_cli(root, mode_cli, command)
        if err:
            errors.append(err)
            continue
        details["commands_checked"].append(command)
        if command == "project-status" and payload and payload.get("cli_contract") != CLI_CONTRACT:
            errors.append(blocker("blocked:cli_contract_mismatch", "Target CLI contract does not match project-moe-cli-v1.", observed=payload.get("cli_contract")))
        if command == "list-sessions" and payload and not isinstance(payload.get("sessions"), list):
            errors.append(blocker("blocked:list_sessions_contract_invalid", "list-sessions --json must return a sessions array."))
    return errors, details


def launcher_text() -> str:
    return '''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def emit(payload: dict, json_mode: bool) -> int:
    if json_mode:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{payload.get('token')}: {payload.get('message')}")
    return int(payload.get("exit_code", 0))


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch or preflight the project-local MOE GUI.")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--allow-visible", action="store_true", help="Launch a visible PySide6 window. Use only in an interactive session.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    launcher = Path(__file__).resolve()
    config_path = launcher.with_name("project_moe_gui.config.json")
    try:
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return emit({"schema_version": 1, "ok": False, "token": "blocked:launcher_config_invalid", "exit_code": 5, "message": "Cannot read Project MOE GUI config.", "error": str(exc)}, args.json)

    project_root = launcher.parents[2]
    mode_cli = project_root / str(config.get("mode_cli", "tools/thesis_moe_mode.py"))
    if not mode_cli.exists():
        return emit({"schema_version": 1, "ok": False, "token": "blocked:missing_mode_cli", "exit_code": 5, "message": "Target project mode CLI is missing.", "project_root": str(project_root), "mode_cli": str(mode_cli)}, args.json)

    def run_mode(command: str) -> tuple[dict | None, dict | None]:
        result = subprocess.run([sys.executable, str(mode_cli), command, "--json"], cwd=str(project_root), capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        if result.returncode != 0:
            return None, {"token": "blocked:mode_cli_failed", "message": "Target project mode CLI failed.", "command": command, "exit_code": result.returncode, "stderr": result.stderr[-800:]}
        try:
            payload = json.loads(result.stdout)
        except Exception as exc:
            return None, {"token": "blocked:mode_cli_invalid_json", "message": "Target project mode CLI did not emit valid JSON.", "command": command, "error": str(exc), "stdout": result.stdout[-800:]}
        return payload, None

    project_status, project_error = run_mode("project-status")
    sessions_payload, sessions_error = run_mode("list-sessions")
    status_payload, status_error = run_mode("status")
    cli_errors = [err for err in [project_error, sessions_error, status_error] if err]
    if cli_errors:
        return emit({"schema_version": 1, "ok": False, "token": cli_errors[0]["token"], "exit_code": cli_errors[0].get("exit_code", 5), "message": cli_errors[0]["message"], "project_root": str(project_root), "blockers": cli_errors}, args.json)

    source_root = Path(str(config.get("toolchain_source_root") or ""))
    if source_root:
        sys.path.insert(0, str(source_root / "src"))
    try:
        from project_moe_gui import gui_shell
    except Exception as exc:
        return emit({"schema_version": 1, "ok": False, "token": "blocked:gui_shell_unavailable", "exit_code": 5, "message": "Cannot import central Project MOE GUI shell.", "toolchain_source_root": str(source_root), "error": str(exc)}, args.json)

    preflight = gui_shell.build_gui_preflight(config, project_status=project_status, sessions_payload=sessions_payload, status_payload=status_payload)
    if args.preflight:
        return emit(preflight, args.json)
    if not args.allow_visible:
        return emit({**preflight, "ok": False, "token": "blocked:visible_gui_launch_requires_explicit_approval", "exit_code": 2, "message": "GUI shell is available. Visible PySide6 launch requires --allow-visible in an interactive session."}, args.json)
    if not preflight.get("ok"):
        return emit(preflight, args.json)
    try:
        return gui_shell.launch_visible(preflight["view_model"])
    except RuntimeError as exc:
        return emit({"schema_version": 1, "ok": False, "token": str(exc), "exit_code": 5, "message": "Visible GUI launch failed."}, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
'''


def cmd_text() -> str:
    return '@echo off\nsetlocal\ncd /d "%~dp0"\npython "%~dp0tools\\project_moe_gui\\launcher.py" %*\nexit /b %ERRORLEVEL%\n'


def readme_text(agent_name: str, namespace: str) -> str:
    return f"""# Project MOE GUI managed artifacts

This directory is managed by `D:\\PythonProject_langgraph` Project MOE GUI toolchain.

- Agent: `{agent_name}`
- State namespace: `{namespace}`
- CLI contract: `{CLI_CONTRACT}`
- GUI shell contract: `{GUI_SHELL_CONTRACT}`

Do not place private `MOE.md` content or project state files in this directory.
Phase 2B provides an import-safe GUI shell and guarded visible-launch path through the central toolchain source. Automated checks must use `--preflight`; visible PySide6 launch requires an explicit interactive command.
"""


def config_payload(root: Path, agent_name: str, namespace: str, mode_cli: Path, runtime_root: Path, existing: dict[str, Any] | None = None) -> dict[str, Any]:
    data = dict(existing or {})
    runtime_python = runtime_root / ".venv" / "Scripts" / "python.exe"
    data.update(
        {
            "schema_version": SCHEMA_VERSION,
            "toolchain": TOOLCHAIN_NAME,
            "toolchain_version": TOOLCHAIN_VERSION,
            "cli_contract": CLI_CONTRACT,
            "agent_name": agent_name,
            "state_namespace": namespace,
            "mode_cli": norm(mode_cli),
            "project_root_strategy": "launcher-parent-git-root",
            "pyside6_runtime": "shared-runtime",
            "python_runtime_strategy": "shared-gui-runtime",
            "python_utf8": True,
            "shared_runtime_root": str(runtime_root),
            "runtime_python": str(runtime_python),
            "target_project_root": str(root),
            "toolchain_source_root": str(Path(__file__).resolve().parents[2]),
            "gui_shell_contract": GUI_SHELL_CONTRACT,
        }
    )
    return data


def artifacts(root: Path, agent_name: str, namespace: str, mode_cli: Path, runtime_root: Path, existing_config: dict[str, Any] | None = None) -> dict[Path, str]:
    return {
        LAUNCHER_RELATIVE: launcher_text(),
        CONFIG_RELATIVE: json.dumps(config_payload(root, agent_name, namespace, mode_cli, runtime_root, existing_config), ensure_ascii=False, indent=2) + "\n",
        README_RELATIVE: readme_text(agent_name, namespace),
        CMD_RELATIVE: cmd_text(),
    }


def manifest_payload(root: Path, agent_name: str, namespace: str, mode_cli: Path, planned: dict[Path, str], previous: dict[str, Any] | None = None) -> dict[str, Any]:
    managed = [{"path": norm(rel), "role": "managed", "sha256": sha256_bytes(text.encode("utf-8"))} for rel, text in planned.items()]
    managed.append({"path": norm(MANIFEST_RELATIVE), "role": "manifest", "sha256": None})
    return {
        "schema_version": SCHEMA_VERSION,
        "toolchain": TOOLCHAIN_NAME,
        "toolchain_version": TOOLCHAIN_VERSION,
        "cli_contract": CLI_CONTRACT,
        "target_project_root": str(root),
        "agent_name": agent_name,
        "state_namespace": namespace,
        "mode_cli": norm(mode_cli),
        "installed_at": (previous or {}).get("installed_at") or now_utc(),
        "updated_at": now_utc(),
        "managed_files": managed,
        "protected_files": ["MOE.md", ".codex/agents/*.toml", f".omx/state/{namespace}/"],
        "rollback_hint": "Use the target project's Git history to revert managed install artifacts; do not delete .omx/state as part of GUI rollback.",
    }


def existing_install(root: Path) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    manifest = load_json(root / MANIFEST_RELATIVE, "blocked:not_installed", errors) if (root / MANIFEST_RELATIVE).exists() else None
    config = load_json(root / CONFIG_RELATIVE, "blocked:not_installed", errors) if (root / CONFIG_RELATIVE).exists() else None
    return manifest, config, errors


def preflight(root: Path, agent_name: str, namespace: str, mode_cli: Path, check_cli: bool) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    errors = validate_identifiers(agent_name, namespace)
    evidence = project_evidence(root)
    if not evidence:
        errors.append(blocker("blocked:missing_project_evidence", "Target directory does not look like a project.", expected=PROJECT_EVIDENCE))
    errors.extend(check_agent_toml(root, agent_name))
    mode_full, mode_err = safe_relative(root, mode_cli, "blocked:mode_cli_path_invalid")
    if mode_err:
        errors.append(mode_err)
    elif mode_full and not mode_full.exists():
        errors.append(blocker("blocked:missing_mode_cli", "Target project mode CLI is missing.", path=norm(mode_cli)))
    cli_details: dict[str, Any] = {}
    if check_cli and not any(error["code"].startswith("blocked:mode_cli") or error["code"] == "blocked:path_traversal" for error in errors):
        cli_errors, cli_details = check_cli_contract(root, mode_cli)
        errors.extend(cli_errors)
    return errors, {"project_root_evidence": evidence, "cli_contract_check": cli_details}


def planned_changes(root: Path, planned: dict[Path, str]) -> tuple[list[dict[str, Any]], bool]:
    changes: list[dict[str, Any]] = []
    changed = False
    for rel, text in planned.items():
        full, err = safe_relative(root, rel)
        if err:
            changes.append({"path": norm(rel), "action": "blocked", "blocker": err})
            changed = True
            continue
        assert full is not None
        old = read_text(full) if full.exists() else None
        action = "unchanged" if old == text else ("update" if full.exists() else "create")
        changed = changed or action != "unchanged"
        changes.append({"path": norm(rel), "action": action, "managed": True})
    return changes, changed


def apply_artifacts(root: Path, planned: dict[Path, str], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    applied: list[dict[str, Any]] = []
    for rel, text in planned.items():
        full, err = safe_relative(root, rel)
        if err:
            raise RuntimeError(err["message"])
        assert full is not None
        applied.append({"path": norm(rel), "status": write_text_if_changed(full, text), "managed": True})
    applied.append({"path": norm(MANIFEST_RELATIVE), "status": write_json_if_changed(root / MANIFEST_RELATIVE, manifest), "managed": True})
    return applied


def install(root: Path, agent_name: str, namespace: str, mode_cli: Path, runtime_root: Path, dry_run: bool, check_cli: bool = True) -> dict[str, Any]:
    errors, details = preflight(root, agent_name, namespace, mode_cli, check_cli)
    old_manifest, old_config, load_errors = existing_install(root)
    errors.extend(load_errors)
    planned = artifacts(root, agent_name, namespace, mode_cli, runtime_root, old_config)
    changes, changed = planned_changes(root, planned)
    manifest = manifest_payload(root, agent_name, namespace, mode_cli, planned, old_manifest)
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "command": "install_project_moe_gui",
        "mode": "dry-run" if dry_run else "apply",
        "ok": not errors,
        "token": "ok" if not errors else errors[0]["code"],
        "toolchain": TOOLCHAIN_NAME,
        "toolchain_version": TOOLCHAIN_VERSION,
        "cli_contract": CLI_CONTRACT,
        "target_project_root": str(root),
        "agent_name": agent_name,
        "state_namespace": namespace,
        "planned_writes": changes,
        "planned_skips": [],
        "planned_migrations": [],
        "no_op": not changed,
        "blockers": errors,
        "project_root_evidence": details["project_root_evidence"],
        "cli_contract_check": details["cli_contract_check"],
        "rollback_hint": manifest["rollback_hint"],
    }
    if errors or dry_run:
        return payload
    payload["applied_file_changes"] = apply_artifacts(root, planned, manifest)
    return payload


def hash_errors(root: Path, manifest: dict[str, Any] | None) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if not manifest:
        return errors
    for item in manifest.get("managed_files", []):
        rel = item.get("path")
        expected = item.get("sha256")
        if not rel or not expected:
            continue
        full, err = safe_relative(root, rel)
        if err:
            errors.append(err)
            continue
        assert full is not None
        if not full.exists():
            errors.append(blocker("blocked:managed_file_missing", "Managed file is missing.", path=rel))
            continue
        observed = sha256_file(full)
        if observed != expected:
            errors.append(blocker("blocked:managed_file_hash_mismatch", "Managed file hash does not match install manifest.", path=rel, expected=expected, observed=observed))
    return errors


def check_install(root: Path, skip_runtime_import: bool = False) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    manifest, config, load_errors = existing_install(root)
    if not manifest or not config:
        errors.extend(load_errors or [blocker("blocked:not_installed", "Project MOE GUI is not installed in target project.")])
    else:
        errors.extend(load_errors)
        errors.extend(hash_errors(root, manifest))
        agent = str(config.get("agent_name") or manifest.get("agent_name") or "")
        namespace = str(config.get("state_namespace") or manifest.get("state_namespace") or "")
        mode_cli = Path(str(config.get("mode_cli") or manifest.get("mode_cli") or DEFAULT_MODE_CLI))
        errors.extend(preflight(root, agent, namespace, mode_cli, True)[0])
        runtime_status = "skipped_by_flag"
        if not skip_runtime_import:
            runtime_python = Path(str(config.get("runtime_python") or ""))
            if not runtime_python.exists():
                runtime_status = "missing"
                errors.append(blocker("blocked:python_runtime_unavailable", "Configured PySide6 runtime Python is missing.", runtime_python=str(runtime_python)))
            else:
                result = subprocess.run([str(runtime_python), "-c", "import PySide6; print('ok')"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
                runtime_status = "import_ok" if result.returncode == 0 else "pyside6_unavailable"
                if result.returncode != 0:
                    errors.append(blocker("blocked:pyside6_unavailable", "Configured runtime cannot import PySide6.", stderr=result.stderr[-800:]))
    installed_version = manifest.get("toolchain_version") if manifest else None
    status = "not_installed"
    if manifest and config:
        status = "blocked" if errors else ("up_to_date" if installed_version == TOOLCHAIN_VERSION else "upgrade_available")
    return {
        "schema_version": SCHEMA_VERSION,
        "command": "check_project_moe_gui_install",
        "ok": not errors,
        "token": "ok" if not errors else errors[0]["code"],
        "status": status,
        "target_project_root": str(root),
        "installed_toolchain_version": installed_version,
        "target_toolchain_version": TOOLCHAIN_VERSION,
        "config_schema_version": config.get("schema_version") if config else None,
        "cli_contract": config.get("cli_contract") if config else CLI_CONTRACT,
        "migration_actions": [],
        "runtime_status": locals().get("runtime_status", "unknown"),
        "blockers": errors,
        "rollback_hint": (manifest or {}).get("rollback_hint"),
    }


def update(root: Path, dry_run: bool, skip_runtime_import: bool = True) -> dict[str, Any]:
    current = check_install(root, skip_runtime_import=skip_runtime_import)
    if current.get("blockers"):
        return {**current, "command": "update_project_moe_gui", "mode": "dry-run" if dry_run else "apply"}
    errors: list[dict[str, Any]] = []
    manifest = load_json(root / MANIFEST_RELATIVE, "blocked:not_installed", errors) or {}
    config = load_json(root / CONFIG_RELATIVE, "blocked:not_installed", errors) or {}
    agent = str(config.get("agent_name") or manifest.get("agent_name"))
    namespace = str(config.get("state_namespace") or manifest.get("state_namespace"))
    mode_cli = Path(str(config.get("mode_cli") or manifest.get("mode_cli") or DEFAULT_MODE_CLI))
    runtime_root = Path(str(config.get("shared_runtime_root") or DEFAULT_SHARED_RUNTIME_ROOT))
    planned = artifacts(root, agent, namespace, mode_cli, runtime_root, config)
    changes, changed = planned_changes(root, planned)
    new_manifest = manifest_payload(root, agent, namespace, mode_cli, planned, manifest)
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "command": "update_project_moe_gui",
        "mode": "dry-run" if dry_run else "apply",
        "ok": not errors,
        "token": "ok" if not errors else errors[0]["code"],
        "status": "migration_required" if changed else "up_to_date",
        "target_project_root": str(root),
        "installed_toolchain_version": manifest.get("toolchain_version"),
        "target_toolchain_version": TOOLCHAIN_VERSION,
        "config_schema_version": config.get("schema_version"),
        "cli_contract": config.get("cli_contract"),
        "migration_actions": changes,
        "no_op": not changed,
        "blockers": errors,
        "rollback_hint": new_manifest["rollback_hint"],
    }
    if errors or dry_run:
        return payload
    payload["applied_file_changes"] = apply_artifacts(root, planned, new_manifest)
    payload["update_receipt"] = {
        "target_project_root": str(root),
        "old_toolchain_version": manifest.get("toolchain_version"),
        "new_toolchain_version": TOOLCHAIN_VERSION,
        "schema_version": SCHEMA_VERSION,
        "changed_files": [item["path"] for item in payload["applied_file_changes"] if item["status"] != "unchanged"],
        "skipped_private_files": ["MOE.md", ".codex/agents/*.toml", f".omx/state/{namespace}/"],
        "executed_at": now_utc(),
        "rollback_hint": new_manifest["rollback_hint"],
    }
    return payload


def emit(payload: dict[str, Any], json_mode: bool) -> int:
    if json_mode:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{payload.get('token')}: {payload.get('status') or payload.get('command')}")
    return 0 if payload.get("ok") else 1


def root_or_error(target_project: str, command: str) -> tuple[Path | None, dict[str, Any] | None]:
    root, err = resolve_project(target_project)
    if err:
        return root, {"schema_version": SCHEMA_VERSION, "command": command, "ok": False, "token": err["code"], "target_project_root": str(root) if root else target_project, "blockers": [err]}
    assert root is not None
    return root, None
