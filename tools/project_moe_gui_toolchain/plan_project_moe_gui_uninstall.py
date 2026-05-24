#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from project_moe_gui.toolchain import emit, plan_uninstall, root_or_error


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan removal of managed Project MOE GUI artifacts from a target project without deleting private state.")
    parser.add_argument("--target-project", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    project_root, error_payload = root_or_error(args.target_project, "plan_project_moe_gui_uninstall")
    if error_payload:
        return emit(error_payload, args.json)
    assert project_root is not None
    return emit(plan_uninstall(project_root), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
