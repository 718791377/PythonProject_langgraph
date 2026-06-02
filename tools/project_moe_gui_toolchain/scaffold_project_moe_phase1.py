#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from project_moe_gui.toolchain import (  # noqa: E402
    DEFAULT_BOOTSTRAP_OPERATOR_DOC,
    DEFAULT_BOOTSTRAP_STARTUP_HOOK,
    DEFAULT_MODE_CLI,
    DEFAULT_OFF_WRAPPER,
    DEFAULT_ON_WRAPPER,
    DEFAULT_PRIVATE_PROMPT_SOURCE,
    emit,
    phase1_bootstrap_scaffold_apply,
    phase1_bootstrap_scaffold_plan,
    root_or_error,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a read-only dry-run Project MOE Phase 1 Bootstrap Lane scaffold plan.")
    parser.add_argument("--target-project", required=True)
    parser.add_argument("--agent-name", required=True)
    parser.add_argument("--state-namespace", required=True)
    parser.add_argument("--mode-cli", default=str(DEFAULT_MODE_CLI))
    parser.add_argument("--private-prompt-source", default=str(DEFAULT_PRIVATE_PROMPT_SOURCE))
    parser.add_argument("--on-wrapper", default=str(DEFAULT_ON_WRAPPER))
    parser.add_argument("--off-wrapper", default=str(DEFAULT_OFF_WRAPPER))
    parser.add_argument("--startup-hook", default=str(DEFAULT_BOOTSTRAP_STARTUP_HOOK))
    parser.add_argument("--operator-doc", default=str(DEFAULT_BOOTSTRAP_OPERATOR_DOC))
    parser.add_argument("--dry-run", action="store_true", help="Emit the default read-only scaffold plan without writing target files.")
    parser.add_argument("--apply", action="store_true", help="Create only missing Phase 1 scaffold files after target ownership and dirty-state checks pass.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.apply and args.dry_run:
        return emit(
            {
                "schema_version": 1,
                "command": "scaffold_project_moe_phase1",
                "mode": "invalid",
                "ok": False,
                "token": "blocked:conflicting_scaffold_modes",
                "exit_code": 2,
                "message": "--apply and --dry-run are mutually exclusive.",
                "blockers": [{"code": "blocked:conflicting_scaffold_modes", "message": "--apply and --dry-run are mutually exclusive."}],
            },
            args.json,
        )

    project_root, error_payload = root_or_error(args.target_project, "scaffold_project_moe_phase1")
    if error_payload:
        return emit(error_payload, args.json)
    assert project_root is not None
    scaffold = phase1_bootstrap_scaffold_apply if args.apply else phase1_bootstrap_scaffold_plan
    payload = scaffold(
        project_root,
        args.agent_name,
        args.state_namespace,
        Path(args.mode_cli),
        private_prompt_source=Path(args.private_prompt_source),
        on_wrapper=Path(args.on_wrapper),
        off_wrapper=Path(args.off_wrapper),
        startup_hook=Path(args.startup_hook),
        operator_doc=Path(args.operator_doc),
    )
    return emit(payload, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
