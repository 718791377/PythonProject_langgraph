#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from project_moe_gui.toolchain import check_install, emit, root_or_error


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a target project's managed Project MOE GUI install artifacts.")
    parser.add_argument("--target-project", required=True)
    parser.add_argument("--skip-runtime-import", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project_root, error_payload = root_or_error(args.target_project, "check_project_moe_gui_install")
    if error_payload:
        return emit(error_payload, args.json)
    assert project_root is not None
    return emit(check_install(project_root, skip_runtime_import=args.skip_runtime_import), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
