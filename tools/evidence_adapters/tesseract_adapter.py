from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import command_path, run, text_metrics


def discover_tesseract(path: str | None = None) -> str | None:
    if path and Path(path).is_file():
        return str(Path(path))
    command = command_path("tesseract", "tesseract.exe")
    if command:
        return command
    for candidate in [
        Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
        Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
    ]:
        if candidate.is_file():
            return str(candidate)
    return None


def parse_tesseract_confidence(tsv: str) -> float | None:
    lines = [line for line in tsv.splitlines() if line.strip()]
    if len(lines) < 2:
        return None
    header = lines[0].split("\t")
    try:
        conf_index = header.index("conf")
    except ValueError:
        return None
    values: list[float] = []
    for line in lines[1:]:
        cols = line.split("\t")
        if conf_index >= len(cols):
            continue
        try:
            value = float(cols[conf_index])
        except ValueError:
            continue
        if value >= 0:
            values.append(value)
    return round(sum(values) / len(values), 3) if values else None


def ocr_image_page(tesseract: str | None, image_path: Path, text_out_path: Path, languages: str) -> dict[str, Any]:
    if not tesseract:
        return {"ocr_error": "tesseract not found; OCR text and confidence were not produced.", "ocr_average_confidence": None}
    text_result = run([tesseract, str(image_path), "stdout", "-l", languages, "--psm", "3"])
    if text_result.returncode != 0:
        return {"ocr_error": text_result.message or "tesseract text OCR failed", "ocr_average_confidence": None}
    text_out_path.parent.mkdir(parents=True, exist_ok=True)
    text_out_path.write_text(text_result.stdout, encoding="utf-8", newline="\n")
    tsv_result = run([tesseract, str(image_path), "stdout", "-l", languages, "--psm", "3", "tsv"])
    confidence = parse_tesseract_confidence(tsv_result.stdout) if tsv_result.returncode == 0 else None
    return {"ocr_output_path": text_out_path, "ocr_average_confidence": confidence, "ocr_metrics": text_metrics(text_result.stdout)}
