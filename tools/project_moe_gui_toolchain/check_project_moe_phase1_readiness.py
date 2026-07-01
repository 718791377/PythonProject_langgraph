#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from project_moe_gui.toolchain import (  # noqa: E402
    DEFAULT_MODE_CLI,
    DEFAULT_PRIVATE_PROMPT_SOURCE,
    DEFAULT_OFF_WRAPPER,
    DEFAULT_ON_WRAPPER,
    check_phase1_readiness,
    emit,
    root_or_error,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Project MOE Phase 1 target-project readiness checker.")
    parser.add_argument("--target-project", required=True)
    parser.add_argument("--agent-name", required=True)
    parser.add_argument("--state-namespace", required=True)
    parser.add_argument("--mode-cli", default=str(DEFAULT_MODE_CLI))
    parser.add_argument("--private-prompt-source", default=str(DEFAULT_PRIVATE_PROMPT_SOURCE))
    parser.add_argument("--on-wrapper", default=str(DEFAULT_ON_WRAPPER))
    parser.add_argument("--off-wrapper", default=str(DEFAULT_OFF_WRAPPER))
    parser.add_argument(
        "--startup-hook",
        action="append",
        default=[],
        help="Relative startup/launcher file to inspect for a status --json activation checkpoint. May be repeated.",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--static-only",
        action="store_true",
        help="Inspect target-project files only and do not execute the target mode CLI. This is safer for cross-project evidence capture.",
    )
    parser.add_argument(
        "--no-exec-cli",
        action="store_true",
        help="Alias for --static-only.",
    )
    args = parser.parse_args()

    project_root, error_payload = root_or_error(args.target_project, "check_project_moe_phase1_readiness")
    if error_payload:
        return emit(error_payload, args.json)
    assert project_root is not None
    startup_hooks = [Path(value) for value in args.startup_hook] if args.startup_hook else None
    payload = check_phase1_readiness(
        project_root,
        args.agent_name,
        args.state_namespace,
        Path(args.mode_cli),
        private_prompt_source=Path(args.private_prompt_source),
        on_wrapper=Path(args.on_wrapper),
        off_wrapper=Path(args.off_wrapper),
        startup_paths=startup_hooks,
        execute_cli=not (args.static_only or args.no_exec_cli),
    )
    return emit(payload, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
