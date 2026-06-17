#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from project_moe_gui.toolchain import DEFAULT_MODE_CLI, DEFAULT_SHARED_RUNTIME_ROOT, emit, install, root_or_error


def _canonicalize(payload: dict) -> dict:
    return {**payload, "legacy_command": payload.get("command"), "command": "install_project_expert_lens_gui"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Install managed Project Expert Lens Agent GUI artifacts into a target project.")
    parser.add_argument("--target-project", required=True)
    parser.add_argument("--agent-name", required=True)
    parser.add_argument("--state-namespace", required=True)
    parser.add_argument("--mode-cli", default=str(DEFAULT_MODE_CLI))
    parser.add_argument("--pyside6-runtime", default=str(DEFAULT_SHARED_RUNTIME_ROOT))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-cli-contract-check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project_root, error_payload = root_or_error(args.target_project, "install_project_expert_lens_gui")
    if error_payload:
        return emit(error_payload, args.json)
    assert project_root is not None
    payload = install(
        project_root,
        args.agent_name,
        args.state_namespace,
        Path(args.mode_cli),
        Path(args.pyside6_runtime),
        dry_run=args.dry_run,
        check_cli=not args.skip_cli_contract_check,
    )
    return emit(_canonicalize(payload), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
