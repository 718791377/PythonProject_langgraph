#!/usr/bin/env python3
"""CLI entry point for the local PPT visual review backend."""
from __future__ import annotations

if __package__ in {None, ""}:
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from tools.user_level_document_tools.viewers.ppt_review.ppt_review_tool import main

if __name__ == "__main__":
    raise SystemExit(main())
