#!/usr/bin/env python3
"""Render a PDF to PNG images with pdf2image and structured evidence."""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# pdf2image Render Report",
        "",
        f"- Job: {payload.get('job_name')}",
        f"- Input PDF: {payload.get('input_pdf')}",
        f"- Status: {payload.get('status')}",
        f"- DPI: {payload.get('dpi')}",
        f"- Poppler bin dir: {payload.get('poppler_bin_dir')}",
        f"- Python executable: {payload.get('python_exe')}",
        f"- Rendered files: {payload.get('rendered_count')}",
        f"- JSON: {payload.get('report_json')}",
    ]
    if payload.get("notes"):
        lines += ["", "## Notes", str(payload.get("notes"))]
    if payload.get("error_message"):
        lines += ["", "## Error", str(payload.get("error_message"))]
    for rendered in payload.get("rendered_files") or []:
        lines.append(f"- {rendered}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render a PDF with pdf2image.")
    parser.add_argument("--input-pdf", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--job-name")
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--poppler-bin-dir")
    parser.add_argument("--python-packages-dir")
    parser.add_argument("--first-page", type=int, default=1)
    parser.add_argument("--last-page", type=int, default=1)
    parser.add_argument("--traceback", action="store_true", help="Include traceback text in JSON for local debugging.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    started = utc_now()
    input_pdf = Path(args.input_pdf).resolve()
    output_dir = Path(args.output_dir).resolve()
    report_dir = Path(args.report_dir).resolve()
    job_name = args.job_name or input_pdf.stem
    json_path = report_dir / f"{job_name}_pdf2image_render.json"
    md_path = report_dir / f"{job_name}_pdf2image_render.md"
    payload: dict[str, Any] = {
        "job_name": job_name,
        "input_pdf": str(input_pdf),
        "backend": "pdf2image",
        "dpi": args.dpi,
        "poppler_bin_dir": str(Path(args.poppler_bin_dir).resolve()) if args.poppler_bin_dir else "",
        "python_exe": sys.executable,
        "python_packages_dir": str(Path(args.python_packages_dir).resolve()) if args.python_packages_dir else "",
        "package_installed": False,
        "poppler_available": False,
        "status": "unavailable",
        "exit_code": 1,
        "rendered_count": 0,
        "rendered_files": [],
        "started_at": started,
        "finished_at": None,
        "notes": "",
        "error_type": "",
        "error_message": "",
        "report_json": str(json_path),
        "report_md": str(md_path),
    }

    if args.python_packages_dir:
        sys.path.insert(0, str(Path(args.python_packages_dir).resolve()))

    try:
        if not input_pdf.exists():
            raise FileNotFoundError(f"input PDF not found: {input_pdf}")
        try:
            from pdf2image import convert_from_path  # type: ignore
        except Exception as exc:  # noqa: BLE001 - structured dependency evidence
            payload.update(
                {
                    "package_installed": False,
                    "status": "unavailable",
                    "error_type": exc.__class__.__name__,
                    "error_message": f"pdf2image is not importable: {exc}",
                    "notes": "Install pdf2image in the active virtual environment. It is not a Poppler replacement.",
                }
            )
            return_code = 1
        else:
            payload["package_installed"] = True
            poppler_path = Path(args.poppler_bin_dir).resolve() if args.poppler_bin_dir else None
            pdftoppm = None
            if poppler_path:
                for name in ("pdftoppm.exe", "pdftoppm"):
                    candidate = poppler_path / name
                    if candidate.exists():
                        pdftoppm = candidate
                        break
            else:
                from shutil import which

                found = which("pdftoppm")
                pdftoppm = Path(found).resolve() if found else None
            payload["poppler_available"] = bool(pdftoppm)
            if not pdftoppm:
                payload.update(
                    {
                        "status": "unavailable",
                        "error_type": "PopplerMissing",
                        "error_message": "pdftoppm was not found. pdf2image requires Poppler on Windows.",
                        "notes": "Pass --poppler-bin-dir or configure poppler_bin_dir in the consumer local config.",
                    }
                )
                return_code = 1
            else:
                output_dir.mkdir(parents=True, exist_ok=True)
                pages = convert_from_path(
                    str(input_pdf),
                    dpi=args.dpi,
                    output_folder=str(output_dir),
                    first_page=args.first_page,
                    last_page=args.last_page,
                    fmt="png",
                    output_file=f"{job_name}_pdf2image_page",
                    poppler_path=str(poppler_path) if poppler_path else None,
                    paths_only=False,
                )
                rendered_files: list[str] = []
                for index, page in enumerate(pages, start=args.first_page):
                    target = output_dir / f"{job_name}_pdf2image_page-{index}.png"
                    page.save(target, "PNG")
                    rendered_files.append(str(target))
                payload.update(
                    {
                        "status": "ok" if rendered_files else "failed",
                        "exit_code": 0 if rendered_files else 1,
                        "rendered_count": len(rendered_files),
                        "rendered_files": rendered_files,
                        "notes": "Rendered through pdf2image using a Poppler backend.",
                    }
                )
                return_code = 0 if rendered_files else 1
    except Exception as exc:  # noqa: BLE001 - write evidence instead of traceback-only output
        payload.update(
            {
                "status": "failed",
                "error_type": exc.__class__.__name__,
                "error_message": str(exc),
                "traceback": traceback.format_exc() if args.traceback else "",
            }
        )
        return_code = 1
    finally:
        payload["finished_at"] = utc_now()
        if payload.get("exit_code") == 1 and payload.get("status") == "ok":
            payload["exit_code"] = return_code
        write_json(json_path, payload)
        write_markdown(md_path, payload)
        print(f"Wrote: {json_path}")
        print(f"Wrote: {md_path}")

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
