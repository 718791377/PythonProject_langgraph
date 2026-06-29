#!/usr/bin/env python3
"""Local PPT visual review session builder.

This tool is intentionally local/offline and stdlib-only. It does not edit a
PPTX. It binds already-rendered slide PNGs to region-based review comments and
writes portable evidence artifacts for manual or downstream review.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import uuid
import webbrowser
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

SESSION_SCHEMA = "ppt_review_session"
COMMENTS_SCHEMA = "ppt_review_comments"
REPORT_SCHEMA = "ppt_review_report"
SCHEMA_VERSION = 1
VALID_SEVERITIES = {"info", "low", "medium", "high", "critical"}
SEVERITY_ALIASES = {"minor": "low", "major": "high", "warning": "medium", "error": "high"}
VALID_STATUSES = {"open", "resolved", "wontfix"}
PNG_SUFFIXES = {".png"}
SHARED_TOOL_SOURCE_ROOT = Path(__file__).resolve().parents[2]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _slide_number_from_name(path: Path, fallback: int) -> int:
    stem = path.stem.lower()
    for pattern in (
        r"(?:^|[_\-\s])(?:slide|page|p)[_\-\s]*(\d+)$",
        r"(?:^|[_\-\s])(\d+)$",
    ):
        match = re.search(pattern, stem)
        if not match:
            continue
        value = int(match.group(1))
        if value > 0:
            return value
    return fallback


def _is_relative_to(path: Path, candidate_parent: Path) -> bool:
    try:
        path.relative_to(candidate_parent)
        return True
    except ValueError:
        return False


def ensure_output_dir_allowed(output_dir: Path, *, allow_source_output: bool = False) -> None:
    """Prevent accidental generated review-session writes into tracked tool source."""
    resolved = output_dir.resolve()
    source_root = SHARED_TOOL_SOURCE_ROOT.resolve()
    if not allow_source_output and _is_relative_to(resolved, source_root):
        raise ValueError(
            "output_dir resolves inside tracked shared tool source; choose a consumer-owned "
            "intermediate/result/.local directory or pass --allow-source-output for an intentional test fixture"
        )


def discover_slide_images(slides_dir: Path) -> list[Path]:
    if not slides_dir.exists():
        raise FileNotFoundError(f"slides directory does not exist: {slides_dir}")
    if not slides_dir.is_dir():
        raise NotADirectoryError(f"slides path is not a directory: {slides_dir}")
    images = [p for p in slides_dir.iterdir() if p.is_file() and p.suffix.lower() in PNG_SUFFIXES]
    images.sort(key=lambda p: (_slide_number_from_name(p, 10**9), p.name.lower()))
    if not images:
        raise ValueError(f"no slide PNG files found in {slides_dir}")
    return images


def inspect_input(input_pptx: Path | None, slide_count: int) -> dict[str, Any]:
    if input_pptx is None:
        return {"path": "", "exists": False, "sha256": "", "slide_count": slide_count}
    resolved = input_pptx.resolve()
    metadata: dict[str, Any] = {
        "path": str(resolved),
        "exists": resolved.exists(),
        "sha256": "",
        "slide_count": slide_count,
    }
    if resolved.exists() and resolved.is_file():
        metadata["size"] = resolved.stat().st_size
        metadata["sha256"] = file_sha256(resolved)
    return metadata


def _copy_slide_images(images: list[Path], output_dir: Path) -> list[dict[str, Any]]:
    slides_out = output_dir / "slides"
    slides_out.mkdir(parents=True, exist_ok=True)
    slides: list[dict[str, Any]] = []
    used_numbers: set[int] = set()
    for index, source in enumerate(images, start=1):
        slide_number = _slide_number_from_name(source, index)
        if slide_number in used_numbers:
            slide_number = index
        used_numbers.add(slide_number)
        target = slides_out / f"slide_{slide_number:03d}.png"
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)
        stat = target.stat()
        slides.append({
            "id": f"slide-{slide_number}",
            "slide": slide_number,
            "slide_number": slide_number,
            "title": f"Slide {slide_number}",
            "image": target.relative_to(output_dir).as_posix(),
            "source_image": str(source.resolve()),
            "bytes": stat.st_size,
            "sha256": file_sha256(target),
        })
    slides.sort(key=lambda row: int(row["slide_number"]))
    return slides


def _coerce_float(value: Any, field: str) -> float:
    try:
        coerced = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"roi.{field} must be a number") from exc
    return round(coerced, 6)


def _normalize_roi(raw_roi: Any) -> dict[str, float]:
    if raw_roi in (None, ""):
        return {"x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0}
    if not isinstance(raw_roi, dict):
        raise ValueError("roi must be an object")
    width_value = raw_roi.get("w", raw_roi.get("width"))
    height_value = raw_roi.get("h", raw_roi.get("height"))
    roi = {
        "x": _coerce_float(raw_roi.get("x"), "x"),
        "y": _coerce_float(raw_roi.get("y"), "y"),
        "w": _coerce_float(width_value, "w"),
        "h": _coerce_float(height_value, "h"),
    }
    for key, value in roi.items():
        if value < 0 or value > 1:
            raise ValueError(f"roi.{key} must be between 0 and 1")
    if roi["w"] <= 0 or roi["h"] <= 0:
        raise ValueError("roi.w and roi.h must be greater than 0")
    if roi["x"] + roi["w"] > 1 or roi["y"] + roi["h"] > 1:
        raise ValueError("roi rectangle must stay within normalized slide bounds")
    return roi


def _comments_from_viewer_slides(slides: list[Any]) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for slide_index, slide in enumerate(slides, start=1):
        if not isinstance(slide, dict):
            continue
        slide_number = slide.get("slide", slide.get("slide_number", slide.get("index", slide_index)))
        findings = slide.get("findings", slide.get("comments", []))
        if not isinstance(findings, list):
            continue
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            item = dict(finding)
            item.setdefault("slide", slide_number)
            if "roi" not in item and "region" not in item and "rect" in item:
                item["roi"] = item["rect"]
            flattened.append(item)
    return flattened


def normalize_comments(raw_comments: Any) -> list[dict[str, Any]]:
    """Normalize review comments into a stable list schema.

    Accepts a raw list, an object containing `comments`, `items`, or
    `annotations`, or the static viewer export shape with `slides[].findings`.
    Coordinates are normalized to x/y/w/h floats in [0, 1].
    """
    if isinstance(raw_comments, dict):
        for key in ("comments", "items", "annotations"):
            if isinstance(raw_comments.get(key), list):
                raw_comments = raw_comments[key]
                break
        else:
            if isinstance(raw_comments.get("slides"), list):
                raw_comments = _comments_from_viewer_slides(raw_comments["slides"])
    if not isinstance(raw_comments, list):
        raise ValueError("comments must be a list, a viewer export, or an object containing a comments/items/annotations list")

    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(raw_comments, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"comment {index} must be an object")
        try:
            slide = int(item.get("slide", item.get("slide_number", item.get("page"))))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"comment {index} slide must be an integer") from exc
        if slide < 1:
            raise ValueError(f"comment {index} slide must be >= 1")
        comment_text = str(item.get("comment", item.get("text", item.get("body", "")))).strip()
        if not comment_text:
            raise ValueError(f"comment {index} comment text is required")
        severity = str(item.get("severity", "medium")).strip().lower() or "medium"
        severity = SEVERITY_ALIASES.get(severity, severity)
        if severity not in VALID_SEVERITIES:
            raise ValueError(f"comment {index} severity must be one of {sorted(VALID_SEVERITIES)}")
        status = str(item.get("status", "open")).strip().lower() or "open"
        if status not in VALID_STATUSES:
            raise ValueError(f"comment {index} status must be one of {sorted(VALID_STATUSES)}")
        roi = _normalize_roi(item.get("roi", item.get("region", item.get("rect"))))
        normalized.append({
            "id": str(item.get("id") or f"comment-{index:04d}"),
            "slide": slide,
            "slide_number": slide,
            "roi": roi,
            "severity": severity,
            "category": str(item.get("category", "general")).strip() or "general",
            "comment": comment_text,
            "suggested_fix": str(item.get("suggested_fix", item.get("suggestion", ""))).strip(),
            "status": status,
            "author": str(item.get("author", "")).strip(),
            "created_at": str(item.get("created_at") or utc_now()),
        })
    normalized.sort(key=lambda row: (int(row["slide"]), row["id"]))
    return normalized


def _summarize(comments: list[dict[str, Any]]) -> dict[str, Any]:
    by_severity = {name: 0 for name in sorted(VALID_SEVERITIES)}
    by_slide: dict[str, int] = {}
    for comment in comments:
        by_severity[comment["severity"]] = by_severity.get(comment["severity"], 0) + 1
        slide_key = str(comment["slide"])
        by_slide[slide_key] = by_slide.get(slide_key, 0) + 1
    return {"total": len(comments), "by_severity": by_severity, "by_slide": by_slide}


def _html_report(manifest: dict[str, Any]) -> str:
    data = json.dumps(manifest, ensure_ascii=False).replace("</", "<\\/")
    title = f"PPT Visual Review - {manifest['deck']['name']}"
    slide_sections: list[str] = []
    comments_by_slide: dict[int, list[dict[str, Any]]] = {}
    for comment in manifest["comments"]:
        comments_by_slide.setdefault(int(comment["slide"]), []).append(comment)
    for slide in manifest["slides"]:
        slide_comments = comments_by_slide.get(int(slide["slide"]), [])
        comment_html = "".join(
            "<li>"
            f"<strong>{html.escape(c['severity'])}</strong> "
            f"[{html.escape(c['category'])}] {html.escape(c['comment'])}"
            + (f"<br><em>建议: {html.escape(c['suggested_fix'])}</em>" if c.get("suggested_fix") else "")
            + "</li>"
            for c in slide_comments
        ) or "<li>No comments.</li>"
        slide_sections.append(
            f"<section class='slide'><h2>{html.escape(slide['title'])}</h2>"
            f"<div class='stage'><img src='{html.escape(slide['image'], quote=True)}' alt='{html.escape(slide['title'], quote=True)}'>"
            f"<svg viewBox='0 0 1 1' preserveAspectRatio='none'>"
            + "".join(
                f"<rect x='{c['roi']['x']}' y='{c['roi']['y']}' width='{c['roi']['w']}' height='{c['roi']['h']}'></rect>"
                for c in slide_comments
            )
            + f"</svg></div><ul>{comment_html}</ul></section>"
        )
    return "\n".join([
        "<!doctype html>",
        "<html lang='zh-CN'>",
        "<head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>",
        f"<title>{html.escape(title)}</title>",
        "<style>body{font-family:Segoe UI,Arial,sans-serif;margin:24px;background:#f6f7fb;color:#1f2937}"
        ".slide{background:#fff;border:1px solid #d9dee8;border-radius:12px;padding:16px;margin:18px 0}"
        ".stage{position:relative;display:inline-block;max-width:100%}.stage img{display:block;max-width:100%;border:1px solid #ccd3df}"
        ".stage svg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}rect{fill:rgba(255,191,0,.18);stroke:#d97706;stroke-width:.006}"
        "#ppt-review-data{display:none}</style></head><body>",
        f"<h1>{html.escape(title)}</h1>",
        f"<p>Session: <code>{html.escape(manifest['session']['id'])}</code>; comments: {len(manifest['comments'])}</p>",
        *slide_sections,
        f"<script id='ppt-review-data' type='application/json'>{data}</script>",
        "</body></html>",
    ])


def _copy_static_viewer(output_dir: Path) -> None:
    static_dir = Path(__file__).with_name("static")
    if not static_dir.exists():
        return
    target_dir = output_dir / "viewer_static"
    target_dir.mkdir(parents=True, exist_ok=True)
    for item in static_dir.iterdir():
        if item.is_file() and item.suffix.lower() in {".html", ".css", ".js"}:
            shutil.copy2(item, target_dir / item.name)


def build_review_session(
    *,
    input_pptx: str | Path | None,
    output_dir: str | Path,
    slides_dir: str | Path,
    comments: Any | None = None,
    launch_browser: bool = False,
    allow_source_output: bool = False,
) -> dict[str, Any]:
    output = Path(output_dir).resolve()
    ensure_output_dir_allowed(output, allow_source_output=allow_source_output)
    output.mkdir(parents=True, exist_ok=True)
    source_pptx = Path(input_pptx).resolve() if input_pptx else None
    slide_images = discover_slide_images(Path(slides_dir).resolve())
    slides = _copy_slide_images(slide_images, output)
    normalized_comments = normalize_comments([] if comments is None else comments)
    slide_numbers = {int(slide["slide_number"]) for slide in slides}
    missing_slide_comments = sorted({int(comment["slide"]) for comment in normalized_comments if int(comment["slide"]) not in slide_numbers})
    if missing_slide_comments:
        raise ValueError(f"comment slide references missing rendered slide(s): {missing_slide_comments}")
    session_id = f"ppt-review-{uuid.uuid4().hex[:12]}"
    deck_name = source_pptx.stem if source_pptx else Path(slides_dir).name
    manifest = {
        "schema": SESSION_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "ready",
        "generated_at": utc_now(),
        "session": {"id": session_id, "mode": "local_static_review", "output_dir": str(output)},
        "input": inspect_input(source_pptx, len(slides)),
        "deck": {"name": deck_name, "slide_count": len(slides)},
        "slides": slides,
        "comments_schema": COMMENTS_SCHEMA,
        "comments": normalized_comments,
        "summary": _summarize(normalized_comments),
        "outputs": {
            "manifest": "session_manifest.json",
            "comments": "comments.json",
            "json_report": "review_report.json",
            "html_report": "review_report.html",
            "static_viewer": "viewer_static/ppt_review_viewer.html",
            "static_viewer_app": "viewer_static/app.js",
            "static_viewer_styles": "viewer_static/styles.css",
        },
    }
    comments_payload = {
        "schema": COMMENTS_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "generated_at": manifest["generated_at"],
        "comments": normalized_comments,
        "summary": manifest["summary"],
    }
    report_payload = {**manifest, "schema": REPORT_SCHEMA, "schema_version": SCHEMA_VERSION}
    write_json(output / "session_manifest.json", manifest)
    write_json(output / "comments.json", comments_payload)
    write_json(output / "review_report.json", report_payload)
    (output / "review_report.html").write_text(_html_report(manifest), encoding="utf-8")
    _copy_static_viewer(output)
    if launch_browser:
        webbrowser.open((output / "review_report.html").as_uri())
    return manifest


def _load_comments(path: str | None) -> Any:
    if not path:
        return []
    return read_json(Path(path))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deploy a local/offline visual PPT review session from rendered slide PNGs.")
    parser.add_argument("--input", help="Optional source PPTX recorded for provenance; it is not modified.")
    parser.add_argument("--slides-dir", required=False, help="Directory containing rendered slide PNG files.")
    parser.add_argument("--output-dir", required=False, help="Directory where review artifacts are written.")
    parser.add_argument("--comments-json", help="Optional existing comments JSON to normalize into the session.")
    parser.add_argument("--open", action="store_true", help="Open the generated HTML report in the default browser.")
    parser.add_argument("--allow-source-output", action="store_true", help="Allow output inside tracked shared-tool source for intentional test fixtures only.")
    parser.add_argument("--json", action="store_true", help="Print the generated manifest JSON to stdout.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.slides_dir or not args.output_dir:
        if argv is None and len(sys.argv) == 1:
            parser.print_help()
            return 0
        parser.error("--slides-dir and --output-dir are required when building a review session")
    try:
        manifest = build_review_session(
            input_pptx=args.input,
            output_dir=args.output_dir,
            slides_dir=args.slides_dir,
            comments=_load_comments(args.comments_json),
            launch_browser=args.open,
            allow_source_output=args.allow_source_output,
        )
    except Exception as exc:  # noqa: BLE001 - CLI should report structured local failures
        print(json.dumps({"status": "error", "error_type": exc.__class__.__name__, "error_message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"status": manifest["status"], "output_dir": manifest["session"]["output_dir"], "slides": len(manifest["slides"]), "comments": len(manifest["comments"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
