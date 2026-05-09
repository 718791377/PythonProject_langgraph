from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from .common import command_path, run


POPPLER_TOOL_NAMES = ("pdfinfo", "pdftotext", "pdftoppm", "pdftocairo")


@dataclass(frozen=True)
class PopplerTools:
    pdfinfo: str | None
    pdftotext: str | None
    pdftoppm: str | None
    pdftocairo: str | None = None
    bin_dir: str | None = None

    @property
    def complete_for_text(self) -> bool:
        return bool(self.pdfinfo and self.pdftotext)

    @property
    def complete_for_render(self) -> bool:
        return bool(self.pdftoppm)


def _candidate_dirs(extra_roots: list[str] | None = None) -> list[Path]:
    dirs: list[Path] = []

    def add(value: str | None) -> None:
        if not value:
            return
        try:
            path = Path(value).expanduser()
            if path not in dirs:
                dirs.append(path)
        except Exception:
            return

    for env_name in ("CODEX_POPPLER_BIN_DIR", "POPPLER_BIN_DIR"):
        add(os.environ.get(env_name))
    for item in os.environ.get("PATH", "").split(os.pathsep):
        add(item)
    home = Path.home()
    local = Path(os.environ.get("LOCALAPPDATA", "")) if os.environ.get("LOCALAPPDATA") else None
    known = [
        r"C:\Tools\poppler\Library\bin",
        r"C:\Tools\poppler\bin",
        r"C:\Program Files\poppler\Library\bin",
        r"C:\Program Files\poppler\bin",
        r"C:\Program Files (x86)\poppler\Library\bin",
        r"C:\Program Files (x86)\poppler\bin",
        str(home / "scoop" / "apps" / "poppler" / "current" / "bin"),
        str(home / "scoop" / "shims"),
    ]
    if local:
        known.append(str(local / "Microsoft" / "WinGet" / "Packages"))
    for item in known:
        add(item)
    for item in extra_roots or []:
        add(item)
    return dirs


def _tool_in_dir(directory: Path, tool_name: str) -> str | None:
    names = [tool_name]
    if not tool_name.endswith(".exe"):
        names.append(tool_name + ".exe")
    for name in names:
        candidate = directory / name
        if candidate.is_file():
            return str(candidate)
    return None


def discover_poppler(bin_dir: str | None = None, extra_roots: list[str] | None = None) -> PopplerTools:
    explicit_dirs = [bin_dir] if bin_dir else []
    candidates = [Path(p) for p in explicit_dirs if p] + _candidate_dirs(extra_roots)
    best: dict[str, str | None] = {name: None for name in POPPLER_TOOL_NAMES}
    best_dir: str | None = None
    for directory in candidates:
        found = {name: _tool_in_dir(directory, name) for name in POPPLER_TOOL_NAMES}
        if any(found.values()):
            best.update({name: found[name] or best[name] for name in POPPLER_TOOL_NAMES})
            best_dir = str(directory)
            if found.get("pdfinfo") and found.get("pdftotext") and found.get("pdftoppm"):
                return PopplerTools(
                    pdfinfo=found.get("pdfinfo"),
                    pdftotext=found.get("pdftotext"),
                    pdftoppm=found.get("pdftoppm"),
                    pdftocairo=found.get("pdftocairo"),
                    bin_dir=str(directory),
                )
    return PopplerTools(
        pdfinfo=best.get("pdfinfo") or command_path("pdfinfo", "pdfinfo.exe"),
        pdftotext=best.get("pdftotext") or command_path("pdftotext", "pdftotext.exe"),
        pdftoppm=best.get("pdftoppm") or command_path("pdftoppm", "pdftoppm.exe"),
        pdftocairo=best.get("pdftocairo") or command_path("pdftocairo", "pdftocairo.exe"),
        bin_dir=best_dir,
    )


def pdf_page_count(pdfinfo: str | None, path: Path) -> int | None:
    if not pdfinfo:
        return None
    result = run([pdfinfo, str(path)])
    if result.returncode != 0:
        return None
    match = re.search(r"^Pages:\s*(\d+)\s*$", result.stdout, re.MULTILINE)
    return int(match.group(1)) if match else None


def extract_pdf_page(pdftotext: str, path: Path, page: int, out_path: Path) -> tuple[str, str | None]:
    if out_path.exists():
        try:
            return out_path.read_text(encoding="utf-8", errors="replace"), None
        except OSError:
            pass
    out_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = out_path.with_suffix(".tmp.txt")
    result = run([pdftotext, "-f", str(page), "-l", str(page), "-layout", "-enc", "UTF-8", str(path), str(temp_path)])
    if result.returncode != 0:
        return "", result.message or f"pdftotext failed for page {page}"
    try:
        text = temp_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return "", repr(exc)
    finally:
        try:
            temp_path.unlink()
        except OSError:
            pass
    out_path.write_text(text, encoding="utf-8", newline="\n")
    return text, None


def extract_pdf_pages_whole_doc(pdftotext: str, path: Path, text_dir: Path, limit: int) -> dict[int, tuple[str, str | None]]:
    cached: dict[int, tuple[str, str | None]] = {}
    missing_pages: list[int] = []
    for page in range(1, limit + 1):
        out_path = text_dir / f"page-{page:04d}.txt"
        if out_path.exists():
            try:
                cached[page] = (out_path.read_text(encoding="utf-8", errors="replace"), None)
                continue
            except OSError:
                pass
        missing_pages.append(page)
    if not missing_pages:
        return cached
    text_dir.mkdir(parents=True, exist_ok=True)
    temp_path = text_dir.parent / f"{text_dir.name}.whole.tmp.txt"
    result = run([pdftotext, "-layout", "-enc", "UTF-8", str(path), str(temp_path)])
    if result.returncode != 0:
        error = result.message or "whole-document pdftotext failed"
        return {page: cached.get(page, ("", error)) for page in range(1, limit + 1)}
    try:
        raw = temp_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {page: cached.get(page, ("", repr(exc))) for page in range(1, limit + 1)}
    finally:
        try:
            temp_path.unlink()
        except OSError:
            pass
    parts = raw.split("\f")
    for page in range(1, limit + 1):
        if page in cached:
            continue
        out_path = text_dir / f"page-{page:04d}.txt"
        if page <= len(parts):
            text = parts[page - 1]
            out_path.write_text(text, encoding="utf-8", newline="\n")
            cached[page] = (text, None)
        else:
            cached[page] = ("", f"whole-document pdftotext did not include page {page}")
    return cached


def render_pdf_page(pdftoppm: str, path: Path, page: int, out_path: Path, dpi: int) -> str | None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and out_path.stat().st_size > 0:
        return None
    base_path = out_path.with_suffix("")
    result = run([pdftoppm, "-r", str(dpi), "-f", str(page), "-l", str(page), "-singlefile", "-png", str(path), str(base_path)])
    if result.returncode != 0:
        return result.message or f"pdftoppm failed for page {page}"
    if not out_path.exists():
        return f"pdftoppm did not create expected image: {out_path}"
    return None
