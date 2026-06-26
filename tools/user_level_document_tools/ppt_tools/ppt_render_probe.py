#!/usr/bin/env python3
"""PPTX-to-PDF/PNG render probe with structured visual QA evidence."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from ppt_render_capability_probe import build_payload as build_capability_payload
except Exception:  # pragma: no cover - fallback for unusual invocation paths
    build_capability_payload = None  # type: ignore

try:
    from write_visual_qa_status_marker import classify as classify_visual_qa
except Exception:  # pragma: no cover
    classify_visual_qa = None  # type: ignore


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_config(path: str | None) -> dict[str, Any]:
    if not path:
        default = Path(__file__).with_name("ppt_render_toolchain_config.example.json")
        path = str(default) if default.exists() else ""
    if not path:
        return {}
    config_path = Path(path)
    if not config_path.exists():
        return {}
    payload = json.loads(config_path.read_text(encoding="utf-8-sig"))
    return payload if isinstance(payload, dict) else {}


def parse_csv(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        for part in value.split(","):
            normalized = part.strip().lower()
            if normalized and normalized not in result:
                result.append(normalized)
    return result


def is_pptx_like(path: Path) -> bool:
    if path.suffix.lower() not in {".pptx", ".pptm"}:
        return False
    try:
        with zipfile.ZipFile(path) as zf:
            names = set(zf.namelist())
            return "[Content_Types].xml" in names
    except zipfile.BadZipFile:
        # Let renderer-specific engines produce a better failure; tests may use a fake file.
        return True
    except Exception:
        return True


def count_slides(path: Path) -> int | None:
    try:
        with zipfile.ZipFile(path) as zf:
            return len([name for name in zf.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml")])
    except Exception:
        return None


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_powerpoint(input_pptx: Path, output_dir: Path, formats: list[str]) -> dict[str, Any]:
    ps = shutil.which("powershell") or shutil.which("pwsh")
    script = Path(__file__).with_name("powerpoint_com_probe.ps1")
    if not ps:
        return {"engine": "powerpoint", "status": "blocked", "error_message": "PowerShell is not available.", "artifacts": []}
    args = [ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), "-InputPptx", str(input_pptx), "-OutputDir", str(output_dir)]
    if "png" not in formats:
        args.append("-SkipPngExport")
    report = output_dir / "powerpoint_com_probe.json"
    try:
        proc = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "engine": "powerpoint",
            "status": "blocked",
            "exit_code": None,
            "stdout": getattr(exc, "stdout", "") or "",
            "pdf": "",
            "png_files": [],
            "artifacts": [],
            "raw_report": str(report),
            "error_type": exc.__class__.__name__,
            "error_message": str(exc),
        }
    payload: dict[str, Any] = {}
    if report.exists():
        try:
            loaded = json.loads(report.read_text(encoding="utf-8-sig"))
            payload = loaded if isinstance(loaded, dict) else {}
        except Exception as exc:  # noqa: BLE001 - keep renderer failure structured
            payload = {"error_type": exc.__class__.__name__, "error_message": f"report_parse_error:{exc}"}
    png_files = payload.get("png_outputs", [])
    if not isinstance(png_files, list):
        png_files = []
    if not png_files and payload.get("png_output"):
        png_files = [payload.get("png_output")]
    artifacts = [payload.get("pdf_output"), *png_files]
    return {
        "engine": "powerpoint",
        "status": "ok" if proc.returncode == 0 and payload.get("ready") else "blocked",
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "pdf": payload.get("pdf_output", ""),
        "png_files": [str(p) for p in png_files if p],
        "artifacts": [str(p) for p in artifacts if p],
        "raw_report": str(report),
        "error_type": payload.get("error_type", ""),
        "error_message": payload.get("error_message", ""),
    }


def run_soffice(input_pptx: Path, output_dir: Path, config: dict[str, Any]) -> dict[str, Any]:
    soffice = str(config.get("soffice_exe") or "").strip()
    if not soffice:
        found = shutil.which("soffice") or shutil.which("soffice.exe") or shutil.which("libreoffice")
        soffice = found or ""
    if not soffice or not Path(soffice).is_file():
        return {"engine": "soffice", "status": "blocked", "error_message": "LibreOffice/soffice is not configured or found.", "artifacts": []}
    pdf_dir = output_dir / "soffice_pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    profile_dir = output_dir / "soffice_profile"
    profile_dir.mkdir(parents=True, exist_ok=True)
    profile_uri = profile_dir.resolve().as_uri()
    try:
        proc = subprocess.run([
            soffice,
            "--headless",
            "--nologo",
            "--nofirststartwizard",
            f"-env:UserInstallation={profile_uri}",
            "--convert-to",
            "pdf",
            "--outdir",
            str(pdf_dir),
            str(input_pptx),
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "engine": "soffice",
            "status": "blocked",
            "exit_code": None,
            "stdout": getattr(exc, "stdout", "") or "",
            "pdf": "",
            "png_files": [],
            "artifacts": [],
            "error_type": exc.__class__.__name__,
            "error_message": str(exc),
        }
    pdf = pdf_dir / (input_pptx.stem + ".pdf")
    return {
        "engine": "soffice",
        "status": "ok" if proc.returncode == 0 and pdf.exists() else "blocked",
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "pdf": str(pdf) if pdf.exists() else "",
        "png_files": [],
        "artifacts": [str(pdf)] if pdf.exists() else [],
        "error_message": "" if pdf.exists() else "soffice did not produce a PDF.",
    }


def run_aspose(input_pptx: Path, output_dir: Path, config: dict[str, Any], formats: list[str]) -> dict[str, Any]:
    try:
        import aspose.slides as slides  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return {"engine": "aspose", "status": "blocked", "error_message": f"Aspose.Slides is not importable: {exc}", "artifacts": []}
    output_dir.mkdir(parents=True, exist_ok=True)
    license_path = str(config.get("aspose_license_path") or "").strip()
    licensed = False
    if license_path and Path(license_path).is_file():
        try:
            lic = slides.License()
            lic.set_license(license_path)
            licensed = True
        except Exception:
            licensed = False
    artifacts: list[str] = []
    pdf_path = output_dir / f"{input_pptx.stem}_aspose.pdf"
    png_files: list[str] = []
    try:
        with slides.Presentation(str(input_pptx)) as pres:
            if "pdf" in formats or "png" in formats:
                pres.save(str(pdf_path), slides.export.SaveFormat.PDF)
                if pdf_path.exists():
                    artifacts.append(str(pdf_path))
            if "png" in formats:
                for index, slide in enumerate(pres.slides, start=1):
                    image = slide.get_image(1, 1)
                    png = output_dir / f"{input_pptx.stem}_aspose_slide{index}.png"
                    image.save(str(png), slides.ImageFormat.PNG)
                    if png.exists():
                        png_files.append(str(png))
                        artifacts.append(str(png))
    except Exception as exc:  # noqa: BLE001
        return {"engine": "aspose", "status": "blocked", "error_message": str(exc), "artifacts": artifacts, "aspose_evaluation_watermark": not licensed}
    return {
        "engine": "aspose",
        "status": "ok" if artifacts else "blocked",
        "pdf": str(pdf_path) if pdf_path.exists() else "",
        "png_files": png_files,
        "artifacts": artifacts,
        "aspose_evaluation_watermark": not licensed,
        "licensed": licensed,
        "error_message": "",
    }


def render_pdf_to_png(pdf: str, output_dir: Path, config: dict[str, Any]) -> list[str]:
    if not pdf:
        return []
    poppler = str(config.get("poppler_bin_dir") or "").strip()
    pdftoppm = ""
    if poppler and Path(poppler).is_dir():
        for name in ("pdftoppm.exe", "pdftoppm"):
            candidate = Path(poppler) / name
            if candidate.exists():
                pdftoppm = str(candidate)
                break
    if not pdftoppm:
        pdftoppm = shutil.which("pdftoppm") or ""
    if not pdftoppm:
        return []
    png_dir = output_dir / "pdftoppm_png"
    png_dir.mkdir(parents=True, exist_ok=True)
    prefix = png_dir / Path(pdf).stem
    try:
        proc = subprocess.run([pdftoppm, "-png", "-r", "160", pdf, str(prefix)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return []
    if proc.returncode != 0:
        return []
    return [str(p) for p in sorted(png_dir.glob("*.png"))]


def choose_engine(capabilities: list[dict[str, Any]], requested: str) -> str | None:
    if requested != "auto":
        return requested if any(r.get("name") == requested and r.get("ready") for r in capabilities) else None
    for name in ("powerpoint", "soffice", "aspose"):
        if any(r.get("name") == name and r.get("ready") for r in capabilities):
            return name
    return None


def capability_for(config_path: str | None) -> dict[str, Any]:
    if build_capability_payload is None:
        return {"tools": []}
    ns = argparse.Namespace(config=config_path, json=True, output=None, probe_com=True, no_path_lookup=False, strict_config=False, require_ready=[])
    payload, _ = build_capability_payload(ns)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render PPTX to PDF/PNG using local configured engines.")
    parser.add_argument("--input", required=True, help="Input PPTX/PPTM path.")
    parser.add_argument("--output-dir", required=True, help="Output directory for local render artifacts and reports.")
    parser.add_argument("--format", action="append", default=["pdf"], help="Requested output format(s): pdf,png.")
    parser.add_argument("--engine", choices=["auto", "powerpoint", "soffice", "aspose"], default="auto")
    parser.add_argument("--config", help="Local JSON config copied from the example template.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report to stdout.")
    parser.add_argument("--report", help="Optional report JSON path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    formats = parse_csv(args.format)
    bad_formats = sorted(set(formats) - {"pdf", "png"})
    if bad_formats:
        print(json.dumps({"status": "blocked", "error_message": f"unknown format(s): {', '.join(bad_formats)}"}, ensure_ascii=False))
        return 2
    input_pptx = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = Path(args.report).resolve() if args.report else output_dir / f"{input_pptx.stem}_ppt_render_probe.json"
    payload: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "input_path": str(input_pptx),
        "output_dir": str(output_dir),
        "requested_formats": formats,
        "requested_engine": args.engine,
        "selected_engine": None,
        "status": "blocked",
        "visual_qa_status": "visual_qa:blocked",
        "pptx_to_pdf_ready": False,
        "png_renderer_ready": False,
        "clean_renderer_ready": False,
        "slide_count": None,
        "rendered_pages": [],
        "artifacts": [],
        "errors": [],
        "capabilities": {},
    }
    if not input_pptx.exists():
        payload["errors"].append("input_not_found")
        write_json(report_path, payload)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1
    if not is_pptx_like(input_pptx):
        payload["visual_qa_status"] = "visual_qa:not_applicable"
        payload["status"] = "not_applicable"
        write_json(report_path, payload)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    config = load_config(args.config)
    capabilities = capability_for(args.config)
    payload["capabilities"] = capabilities
    tools = capabilities.get("tools", []) if isinstance(capabilities, dict) else []
    selected = choose_engine(tools, args.engine)
    payload["selected_engine"] = selected
    payload["slide_count"] = count_slides(input_pptx)
    if selected is None:
        payload["errors"].append("no_pptx_to_pdf_renderer_ready")
        if "png" in formats:
            payload["errors"].append("no_png_renderer_ready")
        evidence = {
            "input_path": str(input_pptx),
            "pptx_to_pdf_ready": False,
            "png_renderer_ready": False,
            "slide_count": payload.get("slide_count") or 1,
            "rendered_pages": [],
            "render_status": "blocked",
        }
        marker = classify_visual_qa(evidence) if classify_visual_qa else {"status": "visual_qa:blocked", "reasons": payload["errors"], "acceptance_blocked": True}
        payload["visual_qa_status"] = marker.get("status", "visual_qa:blocked")
        payload["visual_qa_marker"] = marker
        payload["acceptance_status"] = "blocked" if marker.get("acceptance_blocked", True) else "accepted"
        write_json(report_path, payload)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1

    engine_dir = output_dir / selected
    if selected == "powerpoint":
        result = run_powerpoint(input_pptx, engine_dir, formats)
    elif selected == "soffice":
        result = run_soffice(input_pptx, engine_dir, config)
    else:
        result = run_aspose(input_pptx, engine_dir, config, formats)
    payload["engine_result"] = result
    payload["artifacts"] = result.get("artifacts", [])
    pdf = result.get("pdf", "")
    png_files = [p for p in result.get("png_files", []) if p and Path(p).exists()]
    if "png" in formats and not png_files and pdf:
        png_files = render_pdf_to_png(pdf, output_dir, config)
        payload["artifacts"] = list(payload["artifacts"]) + png_files
    payload["rendered_pages"] = png_files
    payload["pptx_to_pdf_ready"] = bool(pdf and Path(pdf).exists())
    payload["png_renderer_ready"] = "png" not in formats or bool(png_files)
    payload["clean_renderer_ready"] = bool(selected != "aspose" or not result.get("aspose_evaluation_watermark"))
    payload["aspose_evaluation_watermark"] = bool(result.get("aspose_evaluation_watermark", False))
    payload["status"] = "ok" if result.get("status") == "ok" and payload["pptx_to_pdf_ready"] and payload["png_renderer_ready"] else "blocked"
    marker_input = {
        "input_path": str(input_pptx),
        "pptx_to_pdf_ready": payload["pptx_to_pdf_ready"],
        "png_renderer_ready": payload["png_renderer_ready"],
        "clean_renderer_ready": payload["clean_renderer_ready"],
        "slide_count": payload.get("slide_count"),
        "rendered_pages": png_files,
        "render_status": payload["status"],
        "aspose_evaluation_watermark": payload["aspose_evaluation_watermark"],
        "cjk_smoke_checked": False,
    }
    marker = classify_visual_qa(marker_input) if classify_visual_qa else {"status": "visual_qa:manual_required"}
    payload["visual_qa_status"] = marker.get("status", "visual_qa:blocked")
    payload["visual_qa_marker"] = marker
    payload["acceptance_status"] = "blocked" if marker.get("acceptance_blocked") else "accepted"
    if marker.get("acceptance_blocked"):
        payload["status"] = "acceptance_blocked" if payload["status"] == "ok" else payload["status"]
    write_json(report_path, payload)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
