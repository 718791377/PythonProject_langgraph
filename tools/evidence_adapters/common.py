from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    @property
    def message(self) -> str:
        return (self.stderr.strip() or self.stdout.strip() or f"command failed with exit code {self.returncode}")


def utf8_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("LANG", "C.UTF-8")
    return env


def run(command: list[str], cwd: Path | None = None) -> CommandResult:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env=utf8_env(),
    )
    return CommandResult(command=command, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)


def command_path(*names: str) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def text_metrics(text: str) -> dict[str, Any]:
    chars = len(text)
    replacement_chars = text.count("\ufffd")
    control_chars = sum(1 for ch in text if ord(ch) < 32 and ch not in "\n\r\t")
    cjk_chars = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    latin_chars = sum(1 for ch in text if ("a" <= ch.lower() <= "z"))
    whitespace_chars = sum(1 for ch in text if ch.isspace())
    suspicious_fragments = len(re.findall(r"[A-Za-z]\s[A-Za-z]\s[A-Za-z]|[\u00c0-\u00ff]{3,}", text))
    noise_units = replacement_chars * 5 + control_chars * 3 + suspicious_fragments
    noise_ratio = min(1.0, noise_units / max(chars, 1))
    if chars < 20:
        quality = "empty-or-tiny"
    elif noise_ratio >= 0.08:
        quality = "noisy"
    elif replacement_chars or suspicious_fragments > max(20, chars // 500):
        quality = "needs-review"
    else:
        quality = "usable"
    return {
        "chars": chars,
        "replacement_chars": replacement_chars,
        "control_chars": control_chars,
        "cjk_chars": cjk_chars,
        "latin_chars": latin_chars,
        "whitespace_chars": whitespace_chars,
        "suspicious_fragments": suspicious_fragments,
        "noise_ratio": round(noise_ratio, 6),
        "quality": quality,
        "needs_review": quality != "usable",
    }
