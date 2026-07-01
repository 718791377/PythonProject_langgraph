"""PPT review viewer package."""
from __future__ import annotations

from .ppt_review_tool import build_review_session, ensure_output_dir_allowed, main, normalize_comments

__all__ = ["build_review_session", "ensure_output_dir_allowed", "main", "normalize_comments"]
