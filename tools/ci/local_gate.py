#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "local_ci_gate"
MANIFEST_RELATIVE = Path("tools/ci/ci_test_manifest.json")


def configure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def read_manifest(root: Path) -> dict[str, Any]:
    path = root / MANIFEST_RELATIVE
    if not path.exists():
        return {"schema_version": 1, "python_unittest": [], "node_mjs": [], "powershell_ps1": []}
    return json.loads(path.read_text(encoding="utf-8"))


def run_step(name: str, command: list[str], cwd: Path, timeout_seconds: int) -> dict[str, Any]:
    started = datetime.now(timezone.utc)
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
        return {
            "name": name,
            "command": command,
            "exit_code": result.returncode,
            "ok": result.returncode == 0,
            "timed_out": False,
            "timeout_seconds": timeout_seconds,
            "started_at": started.isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "name": name,
            "command": command,
            "exit_code": 124,
            "ok": False,
            "timed_out": True,
            "timeout_seconds": timeout_seconds,
            "started_at": started.isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        }


def skipped_step(name: str, command: list[str], reason: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "name": name,
        "command": command,
        "exit_code": 0,
        "ok": True,
        "skipped": True,
        "reason": reason,
        "timed_out": False,
        "timeout_seconds": 0,
        "started_at": now,
        "completed_at": now,
        "stdout": "",
        "stderr": "",
    }


def powershell_command() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell.exe") or shutil.which("powershell")


def main() -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description="Run the shared local/remote repository CI gate.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--refresh-managed-files", action="store_true", help="Refresh official OpenSpec managed files first.")
    parser.add_argument("--require-clean-git", action="store_true", help="Fail when the repository is dirty after refresh/checks.")
    parser.add_argument("--step-timeout-seconds", type=int, default=180, help="Per-step timeout.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    timeout = max(1, int(args.step_timeout_seconds))
    manifest = read_manifest(root)
    steps: list[dict[str, Any]] = []
    errors: list[str] = []

    guard_command = [
        sys.executable,
        str(root / "tools" / "run_openspec_guard.py"),
        "--root",
        ".",
        "--tool",
        "codex",
        "--json",
    ]
    if args.refresh_managed_files:
        guard_command.append("--refresh-managed-files")
    if args.require_clean_git:
        guard_command.append("--require-clean-git")
    steps.append(run_step("openspec_guard", guard_command, root, timeout))

    python_runner = root / "tools" / "ci" / "run_python_tests.py"
    if python_runner.exists():
        steps.append(
            run_step(
                "python_unittest",
                [
                    sys.executable,
                    str(python_runner),
                    "--root",
                    str(root),
                    "--manifest",
                    MANIFEST_RELATIVE.as_posix(),
                ],
                root,
                timeout,
            )
        )
    else:
        steps.append(skipped_step("python_unittest", [sys.executable, str(python_runner)], "Python test runner is missing."))

    node_runner = root / "tools" / "ci" / "run_node_mjs_tests.mjs"
    node = shutil.which("node")
    if node and node_runner.exists():
        steps.append(run_step("node_mjs_tests", [node, str(node_runner), str(root / MANIFEST_RELATIVE)], root, timeout))
    else:
        steps.append(skipped_step("node_mjs_tests", [node or "node", str(node_runner)], "Node.js or Node.js test runner is missing."))

    ps_runner = root / "tools" / "ci" / "run_powershell_ps1_tests.ps1"
    ps = powershell_command()
    if ps and ps_runner.exists():
        steps.append(
            run_step(
                "powershell_ps1_tests",
                [
                    ps,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ps_runner),
                    "-Root",
                    str(root),
                    "-Manifest",
                    MANIFEST_RELATIVE.as_posix(),
                ],
                root,
                timeout,
            )
        )
    else:
        steps.append(skipped_step("powershell_ps1_tests", [ps or "pwsh", str(ps_runner)], "PowerShell or PowerShell test runner is missing."))

    steps.append(run_step("git_diff_check", ["git", "diff", "--check"], root, timeout))

    for step in steps:
        if not step.get("ok"):
            errors.append(f"{step['name']} failed with exit code {step['exit_code']}")

    result = {
        "schema_version": 1,
        "check_name": CHECK_NAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "ok": not errors,
        "mode": "remote_ci" if "CI" in __import__("os").environ else "local_ci",
        "shared_with_remote_ci": True,
        "manifest": {
            "path": MANIFEST_RELATIVE.as_posix(),
            "schema_version": manifest.get("schema_version"),
            "python_unittest": manifest.get("python_unittest", []),
            "node_mjs": manifest.get("node_mjs", []),
            "powershell_ps1": manifest.get("powershell_ps1", []),
        },
        "steps": steps,
        "errors": errors,
        "counts": {
            "steps_total": len(steps),
            "steps_passed": sum(1 for step in steps if step.get("ok")),
            "steps_failed": sum(1 for step in steps if not step.get("ok")),
            "errors": len(errors),
        },
    }

    report_text = json.dumps(result, ensure_ascii=False, indent=2)
    (root / "openspec-guard-report.json").write_text(report_text + "\n", encoding="utf-8")
    (root / "local-gate-report.json").write_text(report_text + "\n", encoding="utf-8")

    if args.json:
        print(report_text)
    elif result["ok"]:
        print("local_ci_gate: ok")
    else:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
