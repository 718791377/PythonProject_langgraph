#!/usr/bin/env python3
"""R6 compatibility stub: no live runtime enabled by default."""
import json


def main() -> int:
    print(json.dumps({
        "schema_version": 1,
        "check_name": "r6_live_runtime_stub",
        "ok": False,
        "stub_only": True,
        "blockers": ["upgrade_from_source_repository_or_user_level_installer_required"],
        "live_runtime_enabled": False,
        "remote_publication_mutated": False,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
