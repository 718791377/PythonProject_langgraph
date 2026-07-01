#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from project_moe_gui.toolchain import emit, root_or_error, update


def _canonicalize(payload: dict) -> dict:
    return {**payload, "legacy_command": payload.get("command"), "command": "update_project_expert_lens_gui"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Update managed Project Expert Lens Agent GUI artifacts in a target project.")
    parser.add_argument("--target-project", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-runtime-import", action="store_true", default=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project_root, error_payload = root_or_error(args.target_project, "update_project_expert_lens_gui")
    if error_payload:
        return emit(error_payload, args.json)
    assert project_root is not None
    payload = update(project_root, dry_run=args.dry_run, skip_runtime_import=args.skip_runtime_import)
    return emit(_canonicalize(payload), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
