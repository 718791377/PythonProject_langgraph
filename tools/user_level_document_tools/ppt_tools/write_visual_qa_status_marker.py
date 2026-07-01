#!/usr/bin/env python3
"""Classify PPT visual QA evidence into stable visual_qa:* markers."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VALID_MARKERS = {
    "visual_qa:pass",
    "visual_qa:degraded",
    "visual_qa:blocked",
    "visual_qa:manual_required",
    "visual_qa:not_applicable",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _get(payload: dict[str, Any], key: str, default: Any = None) -> Any:
    return payload.get(key, default)


def classify(payload: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    input_path = str(_get(payload, "input_path", _get(payload, "input", "")) or "")
    suffix = Path(input_path).suffix.lower() if input_path else ""
    if suffix and suffix not in {".pptx", ".pptm", ".pdf"}:
        return {
            "status": "visual_qa:not_applicable",
            "acceptance_blocked": False,
            "reasons": ["unsupported_input_type"],
        }

    pdf_ready = bool(_get(payload, "pptx_to_pdf_ready", False))
    png_ready = bool(_get(payload, "png_renderer_ready", False))
    render_status = str(_get(payload, "render_status", _get(payload, "status", "")) or "")
    if render_status in {"blocked", "visual_qa:blocked"}:
        reasons.append("render_probe_blocked")
    if suffix in {".pptx", ".pptm"} and not pdf_ready:
        reasons.append("no_pptx_to_pdf_renderer_ready")
    if not png_ready:
        reasons.append("no_png_renderer_ready")

    slide_count = _get(payload, "slide_count", None)
    rendered_pages = _get(payload, "rendered_pages", _get(payload, "rendered_files", [])) or []
    try:
        slide_count_int = int(slide_count) if slide_count is not None else None
    except Exception:  # noqa: BLE001
        slide_count_int = None
    if slide_count_int is not None:
        if len(rendered_pages) == 0:
            reasons.append("missing_rendered_pages")
        elif len(rendered_pages) < slide_count_int:
            reasons.append("page_count_mismatch")
    if any(bool(page.get("blank")) for page in rendered_pages if isinstance(page, dict)) or bool(_get(payload, "blank_rendered_page", False)):
        reasons.append("blank_rendered_page")
    if bool(_get(payload, "cjk_text_broken", False)):
        reasons.append("cjk_text_broken")
    if bool(_get(payload, "aspose_evaluation_watermark", False)) and not bool(_get(payload, "clean_renderer_ready", False)):
        reasons.append("aspose_evaluation_watermark")
        return {
            "status": "visual_qa:degraded",
            "acceptance_blocked": True,
            "reasons": sorted(set(reasons)),
        }
    if reasons:
        return {
            "status": "visual_qa:blocked",
            "acceptance_blocked": True,
            "reasons": sorted(set(reasons)),
        }

    cjk_checked = _get(payload, "cjk_smoke_checked", None)
    cjk_status = str(_get(payload, "cjk_text_status", "") or "").lower()
    if cjk_checked is False or cjk_status in {"unknown", "uncertain", "manual_required"}:
        return {
            "status": "visual_qa:manual_required",
            "acceptance_blocked": True,
            "reasons": ["cjk_text_manual_review_required"],
        }

    if bool(_get(payload, "degraded", False)):
        return {
            "status": "visual_qa:degraded",
            "acceptance_blocked": bool(_get(payload, "acceptance_blocked", True)),
            "reasons": ["degraded_renderer_evidence"],
        }
    return {
        "status": "visual_qa:pass",
        "acceptance_blocked": False,
        "reasons": [],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write a PPT visual QA status marker.")
    parser.add_argument("--from-render-report", help="JSON render/QA report to classify.")
    parser.add_argument("--input", help="Input path used when classifying unsupported input types.")
    parser.add_argument("--output", help="Optional output JSON path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    parser.add_argument("--set", action="append", default=[], help="Inject key=value into the classification payload.")
    return parser


def coerce_value(value: str) -> Any:
    lower = value.lower()
    if lower == "true":
        return True
    if lower == "false":
        return False
    if lower == "null":
        return None
    try:
        return int(value)
    except ValueError:
        return value


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = load_json(args.from_render_report)
    if args.input:
        payload["input_path"] = args.input
    for item in args.set:
        if "=" not in item:
            raise SystemExit(f"--set expects key=value, got {item!r}")
        key, value = item.split("=", 1)
        payload[key] = coerce_value(value)
    result = classify(payload)
    result.update({
        "schema_version": 1,
        "generated_at": utc_now(),
        "source_report": str(Path(args.from_render_report).resolve()) if args.from_render_report else "",
        "input_path": payload.get("input_path", ""),
    })
    if result["status"] not in VALID_MARKERS:
        result["status"] = "visual_qa:blocked"
        result.setdefault("reasons", []).append("invalid_classifier_status")
        result["acceptance_blocked"] = True
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.json or not args.output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("status") == "visual_qa:blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
