from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
LOCK_FILE_NAME = "project_moe_gui.daemon.lock"
LOG_FILE_NAME = "project_moe_gui.daemon.log"
RUNTIME_DIR = Path(".project-runtime") / "project_moe_gui"


def windows_process_flags(*, platform_name: str | None = None) -> int:
    platform_name = platform_name or sys.platform
    if not platform_name.startswith("win"):
        return 0
    create_no_window = int(getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))
    detached_process = int(getattr(subprocess, "DETACHED_PROCESS", 0x00000008))
    return create_no_window | detached_process


def windows_process_flags_label(*, platform_name: str | None = None) -> str:
    flags = windows_process_flags(platform_name=platform_name)
    if not flags:
        return "none"
    labels: list[str] = []
    if flags & int(getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)):
        labels.append("CREATE_NO_WINDOW")
    if flags & int(getattr(subprocess, "DETACHED_PROCESS", 0x00000008)):
        labels.append("DETACHED_PROCESS")
    return "|".join(labels) if labels else str(flags)


def daemon_runtime_dir(launcher: str | Path, project_root: str | Path | None = None) -> Path:
    root = Path(project_root).resolve(strict=False) if project_root else Path(launcher).resolve(strict=False).parents[2]
    return root / RUNTIME_DIR


def daemon_lock_path(launcher: str | Path, project_root: str | Path | None = None) -> Path:
    return daemon_runtime_dir(launcher, project_root) / LOCK_FILE_NAME


def daemon_log_path(launcher: str | Path, project_root: str | Path | None = None) -> Path:
    return daemon_runtime_dir(launcher, project_root) / LOG_FILE_NAME


def build_daemon_launch_plan(
    launcher: str | Path,
    *,
    no_args: bool = False,
    preflight: bool = False,
    json_mode: bool = False,
    allow_visible: bool = False,
    platform_name: str | None = None,
    runtime_python: str | Path | None = None,
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    platform_name = platform_name or sys.platform
    launcher_path = Path(launcher).resolve(strict=False)
    if preflight and json_mode:
        return {
            "schema_version": SCHEMA_VERSION,
            "uses_daemon": False,
            "reason": "preflight_json_runs_in_foreground",
            "launcher": str(launcher_path),
            "cmd_window_policy": "foreground_machine_output",
        }
    should_daemon = bool(no_args and not preflight and not json_mode and not allow_visible)
    python_executable = str(runtime_python or sys.executable)
    argv = [python_executable, str(launcher_path), "--allow-visible"]
    lock_path = daemon_lock_path(launcher_path, project_root)
    log_path = daemon_log_path(launcher_path, project_root)
    return {
        "schema_version": SCHEMA_VERSION,
        "uses_daemon": should_daemon,
        "reason": "no_argument_human_launch_uses_project_daemon" if should_daemon else "foreground_launch_requested",
        "launcher": str(launcher_path),
        "project_root": str(Path(project_root).resolve(strict=False)) if project_root else None,
        "argv": argv,
        "shell": False,
        "cmd_window_policy": "no_persistent_cmd" if should_daemon else "foreground",
        "windows_creation_flags": windows_process_flags(platform_name=platform_name),
        "windows_creation_flags_label": windows_process_flags_label(platform_name=platform_name),
        "duplicate_instance_guard": {
            "enabled": True,
            "lock_path": str(lock_path),
            "pid_field": "pid",
            "stale_lock_cleanup": True,
        },
        "diagnostics_log": str(log_path),
        "stdout_stderr_policy": "append_to_diagnostics_log",
        "environment_overrides": {
            "PROJECT_MOE_GUI_DAEMON_CHILD": "1",
            "PYTHONUTF8": "1",
        },
    }


def _pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform.startswith("win"):
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            return str(pid) in result.stdout
        except Exception:
            return True
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _read_lock(lock_path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(lock_path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


@dataclass
class InstanceLock:
    path: Path
    acquired: bool


def acquire_instance_lock(lock_path: str | Path) -> InstanceLock | None:
    path = Path(lock_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        payload = _read_lock(path)
        pid = int((payload or {}).get("pid") or 0)
        if _pid_running(pid):
            return None
        try:
            path.unlink()
        except Exception:
            return None
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        fd = os.open(str(path), flags)
    except FileExistsError:
        return None
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump({"schema_version": SCHEMA_VERSION, "pid": os.getpid()}, handle)
    return InstanceLock(path=path, acquired=True)


def release_instance_lock(lock: InstanceLock | None) -> None:
    if not lock or not lock.acquired:
        return
    try:
        lock.path.unlink()
    except FileNotFoundError:
        return


def spawn_daemon_child(plan: dict[str, Any]) -> dict[str, Any]:
    if not plan.get("uses_daemon"):
        return {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "token": "blocked:daemon_not_selected",
            "exit_code": 2,
            "message": "Daemon launch was not selected for this invocation.",
            "daemon_launch": plan,
        }
    lock_info = plan.get("duplicate_instance_guard") or {}
    lock_path = Path(str(lock_info.get("lock_path") or ""))
    if lock_path.exists():
        payload = _read_lock(lock_path)
        pid = int((payload or {}).get("pid") or 0)
        if _pid_running(pid):
            return {
                "schema_version": SCHEMA_VERSION,
                "ok": True,
                "token": "ok:already_running",
                "exit_code": 0,
                "message": "Project MOE GUI daemon already appears to be running.",
                "daemon_launch": plan,
                "existing_pid": pid,
            }
        try:
            lock_path.unlink()
        except Exception:
            pass
    env = os.environ.copy()
    env.update({str(k): str(v) for k, v in (plan.get("environment_overrides") or {}).items()})
    log_path = Path(str(plan.get("diagnostics_log") or daemon_log_path(str(plan.get("launcher") or "launcher.py"), plan.get("project_root"))))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", errors="replace") as log_handle:
        log_handle.write("\n=== Project MOE GUI daemon launch ===\n")
        log_handle.write(f"argv={plan.get('argv')}\n")
        log_handle.flush()
        kwargs: dict[str, Any] = {
            "cwd": plan.get("project_root") or None,
            "env": env,
            "stdin": subprocess.DEVNULL,
            "stdout": log_handle,
            "stderr": subprocess.STDOUT,
            "shell": False,
        }
        creationflags = int(plan.get("windows_creation_flags") or 0)
        if creationflags:
            kwargs["creationflags"] = creationflags
        process = subprocess.Popen([str(item) for item in plan.get("argv", [])], **kwargs)
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": True,
        "token": "ok",
        "exit_code": 0,
        "message": "Project MOE GUI daemon launch requested; launcher parent can exit without a persistent CMD window.",
        "daemon_launch": plan,
        "spawned_pid": process.pid,
        "diagnostics_log": str(log_path),
    }
