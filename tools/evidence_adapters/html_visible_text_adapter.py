from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from .common import text_metrics


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.title_depth = 0
        self.title_parts: list[str] = []
        self.parts: list[str] = []
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr_map = {key.lower(): value for key, value in attrs if key and value}
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1
        if tag == "title":
            self.title_depth += 1
        if tag == "meta":
            name = attr_map.get("name") or attr_map.get("property") or attr_map.get("itemprop") or attr_map.get("http-equiv")
            content = attr_map.get("content")
            if name and content:
                self.meta[name.strip().lower()] = content.strip()

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1
        if tag == "title" and self.title_depth:
            self.title_depth -= 1

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        if self.title_depth:
            self.title_parts.append(cleaned)
        if not self.skip_depth:
            self.parts.append(cleaned)

    @property
    def visible_text(self) -> str:
        return "\n".join(self.parts)

    @property
    def title(self) -> str:
        return " ".join(self.title_parts).strip()


def likely_date(text: str) -> str | None:
    match = re.search(r"(20\d{2}[-/.\s]*\d{1,2}[-/.\s]*\d{1,2})", text)
    return match.group(1).strip() if match else None


def html_metadata(parser: VisibleTextParser, text: str) -> dict[str, Any]:
    meta = parser.meta
    return {
        "title": parser.title or meta.get("og:title"),
        "author": meta.get("author") or meta.get("article:author") or meta.get("byl"),
        "date": meta.get("article:published_time") or meta.get("publishdate") or meta.get("date") or meta.get("pubdate") or likely_date(text),
    }


def extract_visible_text(path: Path) -> tuple[str, VisibleTextParser, dict[str, Any]]:
    raw = path.read_bytes()
    html = raw.decode("utf-8-sig", errors="replace")
    parser = VisibleTextParser()
    parser.feed(html)
    text = parser.visible_text
    return text, parser, text_metrics(text)
