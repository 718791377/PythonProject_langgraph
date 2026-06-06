#!/usr/bin/env python3
"""Run a bounded read-only durable-routing smoke and write an R4 receipt.

This helper is deliberately narrower than durable adoption. It may execute a
safe local checker command, capture a bounded sanitized transcript, and write
only the explicit receipt path requested by the caller. It never runs
apply-mode adoption, launches durable teams, starts LangGraph threads, writes
repo-local durable state, mutates user-level state, or authorizes remote
publication.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


MAX_TIMEOUT_SECONDS = 120
DEFAULT_TIMEOUT_SECONDS = 30
MAX_TRANSCRIPT_CHARS = 4000
CHECKER_RELATIVE_PATH = Path("tools/check_durable_routing_smoke_gate_template.py")
FORBIDDEN_COMMAND_TERMS = (
    "-apply",
    "omx-team-auto.ps1 -apply",
    "omx team",
    "git push",
    "git reset",
    "git clean",
    "langgraph dev",
    "langgraph up",
)
SECRET_VALUE_RE = re.compile(
    r"(?i)(sk-[A-Za-z0-9_-]{8,}|xox[baprs]-[A-Za-z0-9_-]+|(?:token|secret|password|cookie|api[_-]?key)\s*[=:]\s*[^&\s]+)"
)
WINDOWS_PATH_RE = re.compile(r"(?i)\b[A-Z]:\\(?:Users|PythonProject|project|tmp|temp)\\[^\s\"']+")
UNC_PATH_RE = re.compile(r"\\\\[^\s\"']+")
POSIX_PRIVATE_PATH_RE = re.compile(r"/(?:home|Users|tmp|var/tmp)/[^\s\"']+")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_hash(value: Any) -> str:
    payload = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest()


def short_hash(value: Any) -> str:
    return stable_hash(value)[:16]


def sanitize_text(value: Any, *, limit: int = MAX_TRANSCRIPT_CHARS) -> str:
    text = "" if value is None else str(value)
    text = SECRET_VALUE_RE.sub("[REDACTED_SECRET]", text)
    text = UNC_PATH_RE.sub("[REDACTED_PATH]", text)
    text = WINDOWS_PATH_RE.sub("[REDACTED_PATH]", text)
    text = POSIX_PRIVATE_PATH_RE.sub("[REDACTED_PATH]", text)
    return text[:limit]


def repo_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def is_python_token(token: str) -> bool:
    name = Path(token).name.lower()
    return name in {"python", "python.exe", "python3", "python3.exe"} or name.startswith("python")


def default_command(root: Path) -> list[str]:
    return [
        sys.executable,
        str((root / CHECKER_RELATIVE_PATH).resolve()),
        "--root",
        str(root.resolve()),
        "--json",
    ]


def command_for_receipt(command: Sequence[str], root: Path) -> list[str]:
    result: list[str] = []
    resolved_root = root.resolve()
    for index, token in enumerate(command):
        if index == 0 and is_python_token(token):
            result.append(Path(token).name)
            continue
        path = Path(token)
        if path.is_absolute():
            result.append(repo_relative(path, resolved_root))
        else:
            result.append(token)
    return result


def validate_safe_command(command: Sequence[str], root: Path) -> list[str]:
    blockers: list[str] = []
    if not command:
        return ["command_missing"]
    command_text = " ".join(command).lower()
    for term in FORBIDDEN_COMMAND_TERMS:
        if term in command_text:
            blockers.append(f"forbidden_command_term:{term}")
    if not is_python_token(command[0]):
        blockers.append("command_must_start_with_python")
    script_token = next((token for token in command[1:] if token.endswith(".py")), "")
    if not script_token:
        blockers.append("command_must_execute_repo_checker_script")
    else:
        script_path = Path(script_token)
        if not script_path.is_absolute():
            script_path = root / script_path
        try:
            relative = script_path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            relative = ""
        if not relative.startswith("tools/check_") or not relative.endswith(".py"):
            blockers.append("command_script_must_be_tools_check_py")
    if any(token == "--apply" or token.lower().endswith("-apply") for token in command):
        blockers.append("command_apply_flag_forbidden")
    return sorted(set(blockers))


def git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def transcript(stdout: str, stderr: str) -> dict[str, Any]:
    return {
        "stdout_excerpt": sanitize_text(stdout),
        "stderr_excerpt": sanitize_text(stderr),
        "stdout_hash": stable_hash(stdout),
        "stderr_hash": stable_hash(stderr),
        "max_excerpt_chars": MAX_TRANSCRIPT_CHARS,
        "stdout_truncated": len(stdout) > MAX_TRANSCRIPT_CHARS,
        "stderr_truncated": len(stderr) > MAX_TRANSCRIPT_CHARS,
        "raw_transcript_omitted": True,
    }


def build_receipt(
    *,
    root: Path,
    receipt_path: Path,
    command: Sequence[str],
    phase: str,
    task: str,
    candidate_backend_family: str,
    timeout_seconds: int,
    exit_code: int,
    timed_out: bool,
    stdout: str,
    stderr: str,
    safe_command_blockers: list[str],
) -> dict[str, Any]:
    head = git_head(root)
    command_transcript = transcript(stdout, stderr)
    smoke_pass = exit_code == 0 and not timed_out and not safe_command_blockers
    return {
        "schema_version": 1,
        "receipt_type": "durable-routing-smoke",
        "runtime_stage": "R4",
        "stage": "smoke-tested",
        "generated_at": now_iso(),
        "target_repository_hash": short_hash(str(root.resolve())),
        "phase": phase,
        "task": task,
        "operator_consent_boundary": "read-only smoke receipt only; adoption and mutation remain out of scope",
        "routing_mode": "read_only",
        "mutation_allowed": False,
        "read_only": True,
        "state_write_policy": "receipt_only",
        "receipt_output_path_hash": short_hash(str(receipt_path.resolve())),
        "validation_path": ["durable routing smoke command", "receipt checker"],
        "rollback_path": ["revert local feature commit or use local-main rollback ref after integration"],
        "smoke_command": command_for_receipt(command, root),
        "smoke_command_hash": stable_hash(command_for_receipt(command, root)),
        "smoke_result": {
            "status": "pass" if smoke_pass else "fail",
            "exit_code": exit_code,
            "timed_out": timed_out,
        },
        "timeout_release": {
            "status": "pass" if not timed_out else "fail",
            "released": True,
            "timeout_seconds": timeout_seconds,
            "timed_out": timed_out,
        },
        "rollback_pointer": {
            "type": "git-head",
            "commit_hash": head,
            "status": "ready" if head else "missing",
        },
        "rollback_ready": bool(head),
        "command_transcript": command_transcript,
        "transcript_redaction": {
            "status": "pass",
            "redacted_transcript_hash": stable_hash(command_transcript),
            "raw_private_paths_redacted": True,
            "raw_secrets_redacted": True,
            "raw_transcript_omitted": True,
        },
        "command_safety": {
            "safe_local_command": not safe_command_blockers,
            "blockers": safe_command_blockers,
            "forbidden_apply_markers_detected": bool(safe_command_blockers),
            "runs_external_tool": False,
        },
        "backend_family_evidence": {
            "candidate_backend_family": candidate_backend_family,
            "observed_backend_family": "none",
            "adoption_state": "not_adopted",
            "adoption_claimed": False,
            "native_omx_launched": False,
            "langgraph_thread_started": False,
        },
        "adoption_performed": False,
        "durable_workflow_selected": False,
        "durable_workflow_running": False,
        "durable_workflow_adopted": False,
        "user_level_state_mutated": False,
        "durable_state_mutated": False,
        "durable_team_launched": False,
        "omx_apply_performed": False,
        "langgraph_thread_started": False,
        "remote_publication_authorized": False,
        "redaction_status": "pass",
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a bounded read-only durable routing smoke and write an R4 receipt.")
    parser.add_argument("--root", default=".", help="Repository root for the smoke command.")
    parser.add_argument("--receipt", required=True, help="Explicit receipt output path. This is the only file the helper writes.")
    parser.add_argument("--phase", default="verify-accept", help="Project phase being smoke-tested.")
    parser.add_argument("--task", default="durable routing smoke receipt", help="Concrete task or validation question.")
    parser.add_argument(
        "--candidate-backend-family",
        default="no_durable_team",
        choices=["native_omx", "langgraph", "no_durable_team"],
        help="Backend family considered by the smoke evidence; this does not select or adopt it.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS, help="Bounded command timeout, max 120 seconds.")
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable summary.")
    parser.add_argument(
        "--command",
        nargs=argparse.REMAINDER,
        help="Optional safe local Python checker command. If omitted, the durable routing smoke gate template checker runs.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).resolve()
    receipt_path = Path(args.receipt)
    if not receipt_path.is_absolute():
        receipt_path = (Path.cwd() / receipt_path).resolve()
    timeout_seconds = max(1, min(int(args.timeout_seconds), MAX_TIMEOUT_SECONDS))
    command = args.command if args.command else default_command(root)
    if command and command[0] == "--":
        command = command[1:]

    safe_command_blockers = validate_safe_command(command, root)
    stdout = ""
    stderr = ""
    exit_code = 127 if safe_command_blockers else 0
    timed_out = False

    if not safe_command_blockers:
        try:
            result = subprocess.run(
                command,
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                check=False,
            )
            stdout = result.stdout
            stderr = result.stderr
            exit_code = result.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            exit_code = 124

    receipt = build_receipt(
        root=root,
        receipt_path=receipt_path,
        command=command,
        phase=args.phase,
        task=args.task,
        candidate_backend_family=args.candidate_backend_family,
        timeout_seconds=timeout_seconds,
        exit_code=exit_code,
        timed_out=timed_out,
        stdout=stdout,
        stderr=stderr,
        safe_command_blockers=safe_command_blockers,
    )
    write_json(receipt_path, receipt)

    summary = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "operation": "run-durable-routing-smoke",
        "ok": receipt["smoke_result"]["status"] == "pass",
        "receipt_path_hash": short_hash(str(receipt_path)),
        "receipt_type": receipt["receipt_type"],
        "runtime_stage": receipt["runtime_stage"],
        "stage": receipt["stage"],
        "smoke_status": receipt["smoke_result"]["status"],
        "exit_code": exit_code,
        "timed_out": timed_out,
        "adoption_performed": False,
        "mutation_allowed": False,
        "user_level_state_mutated": False,
        "durable_team_launched": False,
        "omx_apply_performed": False,
        "langgraph_thread_started": False,
        "remote_publication_authorized": False,
        "safe_command_blockers": safe_command_blockers,
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"durable routing smoke: {summary['smoke_status']}")
        print(f"receipt_path_hash: {summary['receipt_path_hash']}")
        for blocker in safe_command_blockers:
            print(f"ERROR: {blocker}")
    if safe_command_blockers:
        return 2
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
