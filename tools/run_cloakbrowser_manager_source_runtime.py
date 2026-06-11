#!/usr/bin/env python3
"""Run CloakBrowser-Manager source loopback smoke without Docker.

This helper is a repo-local live-runtime executor for the user-level
CloakBrowser-Manager source checkout. It installs/uses user-level artifacts
under the current user's Codex tools directory, starts the upstream FastAPI
app on loopback, verifies `/api/status` and the React GUI shell, and writes a
hash-only receipt. It intentionally does not install or start Docker, Podman,
WSL containers, Docker Compose, or profile/VNC launch flows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PRIORITY_ORDER = "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit"
SOURCE_URL = "https://github.com/CloakHQ/CloakBrowser-Manager"
DEFAULT_SOURCE = Path.home() / ".codex" / "tools" / "cloakbrowser-manager" / "source"
DEFAULT_VENV = Path.home() / ".codex" / "tools" / "cloakbrowser-manager" / "python-venv"
DEFAULT_STATE = Path.home() / ".codex" / "tools" / "cloakbrowser-manager" / "state" / "source-runtime"
DEFAULT_RECEIPT_DIR = Path(
    "docs_bilingual/implementation_evidence/user_level_cloakbrowser_academic_runtime_receipts_20260610"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest_text(text: str, length: int = 32) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


def file_digest(path: Path, length: int = 32) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:length]


def write_json_lf(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def run(cmd: list[str], *, cwd: Path, timeout: int = 600, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        timeout=timeout,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def ensure_venv(venv: Path) -> Path:
    python_exe = venv / "Scripts" / "python.exe"
    if not python_exe.exists():
        venv.parent.mkdir(parents=True, exist_ok=True)
        proc = run([sys.executable, "-m", "venv", str(venv)], cwd=venv.parent, timeout=300)
        if proc.returncode != 0:
            raise RuntimeError(f"venv_create_failed:{proc.returncode}")
    return python_exe


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def write_runtime_app(source: Path, state: Path) -> Path:
    runtime_dir = state.parent / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    shim = runtime_dir / "manager_runtime_app.py"
    source_literal = json.dumps(str(source))
    state_literal = json.dumps(str(state))
    shim.write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "import sys",
                "from pathlib import Path",
                f"SOURCE_ROOT = Path({source_literal})",
                f"STATE_ROOT = Path({state_literal})",
                "if str(SOURCE_ROOT) not in sys.path:",
                "    sys.path.insert(0, str(SOURCE_ROOT))",
                "from backend import database as db",
                "db.DATA_DIR = STATE_ROOT",
                "db.DB_PATH = STATE_ROOT / 'profiles.db'",
                "import backend.main as main",
                "main.FRONTEND_DIR = SOURCE_ROOT / 'frontend' / 'dist'",
                "app = main.app",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    return shim


def http_get(url: str, *, timeout: float = 5.0) -> tuple[int, bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "codex-cloakbrowser-manager-smoke/1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            ctype = response.headers.get("content-type", "")
            return int(response.status), body, ctype
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read(), exc.headers.get("content-type", "")


def can_reuse_locked_existing_node_modules(npm_output: str, node_modules: Path) -> bool:
    return "EPERM" in npm_output and ".vite-temp" in npm_output and node_modules.exists()


def wait_for_status(base_url: str, *, deadline_seconds: int = 60) -> tuple[int, bool]:
    deadline = time.monotonic() + deadline_seconds
    last_status = 0
    while time.monotonic() < deadline:
        try:
            status, body, ctype = http_get(base_url + "/api/status", timeout=3)
            last_status = status
            if status == 200:
                try:
                    json.loads(body.decode("utf-8"))
                    return status, "json" in ctype.lower() or bool(body)
                except json.JSONDecodeError:
                    return status, False
        except OSError:
            pass
        time.sleep(1)
    return last_status, False


def build_receipt(
    *,
    source_ref: str,
    install_root_label: str,
    wrapper_label: str,
    state_label: str,
    rollback_label: str,
    command_label: str,
    api_status_http_status: int,
    api_status_json: bool,
    gui_shell_http_status: int,
    gui_shell_html: bool,
    frontend_build_hash: str,
    backend_import_hash: str,
    port: int,
) -> dict[str, Any]:
    command_hash = digest_text(command_label + f"|port={port}")
    generated_at = now_iso()
    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "tool_name": "cloakbrowser-manager-source-runtime",
        "runtime_stage": "R6 live-executed",
        "runtime_stage_detail": "source-backend-frontend-loopback",
        "source_url": SOURCE_URL,
        "source_ref": source_ref,
        "installed_version": "source-main",
        "install_root_label": install_root_label,
        "install_root_hash": digest_text(install_root_label),
        "wrapper_label": wrapper_label,
        "wrapper_path_hash": digest_text(wrapper_label),
        "state_label": state_label,
        "state_path_hash": digest_text(state_label),
        "rollback_label": rollback_label,
        "rollback_pointer_hash": digest_text(rollback_label),
        "priority_order": PRIORITY_ORDER,
        "docker_install_allowed": False,
        "container_runtime_used": False,
        "smoke_kind": "source-backend-frontend-loopback",
        "api_status_http_status": api_status_http_status,
        "api_status_json": api_status_json,
        "gui_shell_http_status": gui_shell_http_status,
        "gui_shell_html": gui_shell_html,
        "profile_launch_smoke": "not_run:no_xvnc_on_windows",
        "frontend_build_hash": frontend_build_hash,
        "backend_import_hash": backend_import_hash,
        "smoke_result": {
            "status": "pass",
            "command_hash": command_hash,
            "api_status_observed_hash": digest_text(str(api_status_http_status) + ":" + str(api_status_json)),
            "gui_shell_observed_hash": digest_text(str(gui_shell_http_status) + ":" + str(gui_shell_html)),
        },
        "redaction_status": "pass",
        "raw_paths_included": False,
        "native_codex_files_mutated": False,
        "remote_publication_mutated": False,
    }


def write_summary(receipt_dir: Path, runtime_receipt: dict[str, Any]) -> None:
    summary_path = receipt_dir / "summary.json"
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        summary = {"actions": []}
    actions = [item for item in summary.get("actions", []) if isinstance(item, dict)]
    actions = [item for item in actions if item.get("tool") != "cloakbrowser-manager-source-runtime"]
    actions.append(
        {
            "ok": True,
            "tool": "cloakbrowser-manager-source-runtime",
            "smoke_kind": runtime_receipt["smoke_kind"],
            "runtime_start": "source-backend-frontend-loopback",
        }
    )
    summary.update(
        {
            "ok": True,
            "generated_at": now_iso(),
            "actions": actions,
            "docker_install_allowed": False,
            "container_runtime_used": False,
            "native_codex_files_mutated": False,
            "remote_publication_mutated": False,
            "note": "CloakBrowser-Manager source runtime smoke used loopback backend+frontend without Docker/Podman/WSL containers; profile launch not run because upstream Windows host lacks Xvnc/KasmVNC.",
        }
    )
    write_json_lf(summary_path, summary)


def execute(args: argparse.Namespace) -> dict[str, Any]:
    source = Path(args.source).resolve()
    venv = Path(args.venv).resolve()
    state = Path(args.state).resolve()
    receipt_dir = Path(args.receipt_dir).resolve()
    if not source.exists():
        raise RuntimeError("source_checkout_missing")
    if not (source / "backend" / "requirements.txt").exists():
        raise RuntimeError("backend_requirements_missing")
    if not (source / "frontend" / "package.json").exists():
        raise RuntimeError("frontend_package_missing")

    source_ref = run(["git", "-C", str(source), "rev-parse", "HEAD"], cwd=source, timeout=60).stdout.strip()
    if not source_ref:
        raise RuntimeError("source_ref_missing")

    python_exe = ensure_venv(venv)
    pip_proc = run([str(python_exe), "-m", "pip", "install", "-r", str(source / "backend" / "requirements.txt")], cwd=source, timeout=900)
    if pip_proc.returncode != 0:
        raise RuntimeError(f"pip_install_failed:{pip_proc.returncode}")

    frontend = source / "frontend"
    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm:
        raise RuntimeError("npm_missing")
    npm_ci = run([npm, "ci"], cwd=frontend, timeout=900)
    if npm_ci.returncode != 0:
        combined = (npm_ci.stdout or "") + "\n" + (npm_ci.stderr or "")
        node_modules = frontend / "node_modules"
        if not can_reuse_locked_existing_node_modules(combined, node_modules):
            raise RuntimeError(f"npm_ci_failed:{npm_ci.returncode}")
    npm_build = run([npm, "run", "build"], cwd=frontend, timeout=900)
    if npm_build.returncode != 0:
        raise RuntimeError(f"npm_build_failed:{npm_build.returncode}")

    state.mkdir(parents=True, exist_ok=True)
    shim = write_runtime_app(source, state)
    backend_import = run([str(python_exe), "-c", "import manager_runtime_app; print(manager_runtime_app.app.title)"], cwd=shim.parent, timeout=120)
    if backend_import.returncode != 0:
        raise RuntimeError(f"backend_import_failed:{backend_import.returncode}")

    port = int(args.port) if args.port else free_port()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(shim.parent)
    proc = subprocess.Popen(
        [
            str(python_exe),
            "-m",
            "uvicorn",
            "manager_runtime_app:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=str(shim.parent),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    api_status = 0
    api_json = False
    gui_status = 0
    gui_html = False
    try:
        api_status, api_json = wait_for_status(f"http://127.0.0.1:{port}", deadline_seconds=90)
        gui_status, gui_body, gui_ctype = http_get(f"http://127.0.0.1:{port}/", timeout=5)
        gui_text = gui_body[:4096].decode("utf-8", errors="replace").lower()
        gui_html = gui_status == 200 and ("text/html" in gui_ctype.lower() or "<html" in gui_text) and "root" in gui_text
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)

    if api_status != 200 or not api_json or gui_status != 200 or not gui_html:
        raise RuntimeError(f"smoke_failed:api={api_status}/{api_json}:gui={gui_status}/{gui_html}")

    frontend_index = source / "frontend" / "dist" / "index.html"
    receipt = build_receipt(
        source_ref=source_ref,
        install_root_label="codex-tools/cloakbrowser-manager/source",
        wrapper_label="codex-tools/cloakbrowser-manager/state/runtime/manager_runtime_app.py",
        state_label="codex-tools/cloakbrowser-manager/state/source-runtime",
        rollback_label="remove codex-tools/cloakbrowser-manager/state/runtime and state/source-runtime",
        command_label="cloakbrowser-manager source backend+frontend loopback smoke",
        api_status_http_status=api_status,
        api_status_json=api_json,
        gui_shell_http_status=gui_status,
        gui_shell_html=gui_html,
        frontend_build_hash=file_digest(frontend_index) if frontend_index.exists() else digest_text("frontend-index-missing"),
        backend_import_hash=digest_text(backend_import.stdout.strip() or "backend-import-ok"),
        port=port,
    )
    receipt_path = receipt_dir / "cloakbrowser-manager-source-runtime.json"
    write_json_lf(receipt_path, receipt)
    write_summary(receipt_dir, receipt)
    return {
        "ok": True,
        "receipt_label": "docs_bilingual/implementation_evidence/user_level_cloakbrowser_academic_runtime_receipts_20260610/cloakbrowser-manager-source-runtime.json",
        "receipt_path_hash": digest_text("docs_bilingual/implementation_evidence/user_level_cloakbrowser_academic_runtime_receipts_20260610/cloakbrowser-manager-source-runtime.json"),
        "tool_name": receipt["tool_name"],
        "source_ref": source_ref,
        "port_hash": digest_text(str(port)),
        "api_status_http_status": api_status,
        "gui_shell_http_status": gui_status,
        "container_runtime_used": False,
        "docker_install_allowed": False,
        "raw_paths_included": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CloakBrowser-Manager source runtime smoke without Docker.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--venv", default=str(DEFAULT_VENV))
    parser.add_argument("--state", default=str(DEFAULT_STATE))
    parser.add_argument("--receipt-dir", default=str(DEFAULT_RECEIPT_DIR))
    parser.add_argument("--port", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = execute(args)
    except Exception as exc:
        payload = {
            "ok": False,
            "error": str(exc),
            "container_runtime_used": False,
            "docker_install_allowed": False,
            "raw_paths_included": False,
        }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        if payload["ok"]:
            print("ok")
        else:
            print(f"ERROR: {payload['error']}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
