"""Run MCP Router with MCP-safe stdout forwarding and quiet stderr logs.

The wrapper is opt-in. It copies child stdout byte-for-byte because stdout is
MCP protocol transport. It stores raw stdout/stderr data in timestamped local
logs and forwards only actionable stderr errors to wrapper stderr.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
from typing import BinaryIO, Iterable


DEFAULT_COMMAND = r"C:\Program Files\nodejs\npx.cmd"
DEFAULT_ARGS = ["-y", "@mcp_router/cli@latest", "connect"]

BENIGN_PATTERNS = [
    r"checking-for-update",
    r"update-not-available",
    r"update-available",
    r"No valid workflows found for",
    r"Executing handler directly without workflow",
    r"libpng warning: iCCP",
    r"^S?SUCCESS:\s+The process with PID \d+ \(child process of PID \d+\) has been terminated\.$",
]

ERROR_PATTERNS = [
    r"\bERROR\b",
    r"\bFAILED\b",
    r"\bException\b",
    r"\bParserError\b",
    r"\bTraceback\b",
    r"\bUnauthorized\b",
    r"\bForbidden\b",
    r"auth failed",
    r"token expired",
    r"failed to start",
    r"exit code",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command-path", default=DEFAULT_COMMAND)
    parser.add_argument("--command-arg", action="append", dest="command_args")
    parser.add_argument("--command-args-json")
    parser.add_argument("--command-args-file")
    parser.add_argument("--log-root")
    return parser.parse_args()


def load_command_args(ns: argparse.Namespace) -> list[str]:
    if ns.command_args_file:
        return [str(item) for item in json.loads(Path(ns.command_args_file).read_text(encoding="utf-8-sig"))]
    if ns.command_args_json:
        return [str(item) for item in json.loads(ns.command_args_json)]
    if ns.command_args:
        return [str(item) for item in ns.command_args]
    return list(DEFAULT_ARGS)


def default_log_root() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    return repo_root / ".omx" / "logs" / "mcp-router"


def matches_any(line: str, patterns: Iterable[re.Pattern[str]]) -> bool:
    return any(pattern.search(line) for pattern in patterns)


def decode_for_log(data: bytes) -> str:
    return data.decode("utf-8", errors="backslashreplace")


def main() -> int:
    ns = parse_args()
    command_args = load_command_args(ns)
    command_path = ns.command_path

    if not Path(command_path).exists():
        print(f"MCP Router log filter wrapper failed to find command: {command_path}", file=sys.stderr)
        return 127

    log_root = Path(ns.log_root) if ns.log_root else default_log_root()
    log_root.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
    log_path = log_root / f"{stamp}.log"
    log_lock = threading.Lock()

    error_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in ERROR_PATTERNS]

    def write_log(stream: str, data: bytes | str) -> None:
        text = decode_for_log(data) if isinstance(data, bytes) else data
        entry = f"{_dt.datetime.now(_dt.UTC).isoformat()}\t{stream}\t{text}\n"
        with log_lock:
            with log_path.open("a", encoding="utf-8", newline="") as handle:
                handle.write(entry)

    write_log("wrapper", "starting: " + " ".join([command_path, *command_args]))

    process = subprocess.Popen(
        [command_path, *command_args],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
        env=os.environ.copy(),
    )

    def copy_stdin() -> None:
        try:
            source = sys.stdin.buffer
            target = process.stdin
            if target is None:
                return
            while True:
                chunk = source.read(65536)
                if not chunk:
                    break
                target.write(chunk)
                target.flush()
        except (BrokenPipeError, OSError):
            pass
        finally:
            if process.stdin is not None:
                try:
                    process.stdin.close()
                except OSError:
                    pass

    def copy_stdout() -> None:
        stream: BinaryIO | None = process.stdout
        if stream is None:
            return
        try:
            while True:
                chunk = stream.read(65536)
                if not chunk:
                    break
                write_log("stdout", chunk)
                sys.stdout.buffer.write(chunk)
                sys.stdout.buffer.flush()
        finally:
            stream.close()

    def copy_stderr() -> None:
        stream: BinaryIO | None = process.stderr
        if stream is None:
            return
        pending = b""
        try:
            while True:
                chunk = stream.read(4096)
                if not chunk:
                    break
                write_log("stderr", chunk)
                pending += chunk
                while b"\n" in pending:
                    line, pending = pending.split(b"\n", 1)
                    handle_stderr_line(line.rstrip(b"\r"), error_patterns)
            if pending:
                handle_stderr_line(pending.rstrip(b"\r"), error_patterns)
        finally:
            stream.close()

    def handle_stderr_line(raw_line: bytes, error_patterns: list[re.Pattern[str]]) -> None:
        line = raw_line.decode("utf-8", errors="replace")
        if matches_any(line, error_patterns):
            sys.stderr.write(line + "\n")
            sys.stderr.flush()

    stdin_thread = threading.Thread(target=copy_stdin, daemon=True)
    stdout_thread = threading.Thread(target=copy_stdout, daemon=True)
    stderr_thread = threading.Thread(target=copy_stderr, daemon=True)
    stdin_thread.start()
    stdout_thread.start()
    stderr_thread.start()

    exit_code = process.wait()
    stdout_thread.join(timeout=5)
    stderr_thread.join(timeout=5)
    stdin_thread.join(timeout=1)
    write_log("wrapper", f"exit_code: {exit_code}")

    if exit_code != 0:
        print(f"MCP Router command exited with code {exit_code}. Full log: {log_path}", file=sys.stderr)
    return int(exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
