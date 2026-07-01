from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def natural_key(path: Path):
    parts = re.split(r"(\d+)", path.name)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a contact sheet from page PNG files.")
    parser.add_argument("--input-dir", required=True, help="Directory containing rendered page images")
    parser.add_argument("--output", required=True, help="Output contact sheet path")
    parser.add_argument("--pattern", default="*.png", help="Input glob pattern, default: *.png")
    parser.add_argument("--columns", type=int, default=4, help="Number of columns")
    parser.add_argument("--thumb-width", type=int, default=320, help="Thumbnail width in pixels")
    parser.add_argument("--max-pages", type=int, default=0, help="Maximum pages to include; 0 means all")
    parser.add_argument("--json", dest="json_path", default="", help="Optional JSON manifest path")
    args = parser.parse_args()

    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as exc:
        print(f"ERROR: Pillow is required for contact sheet generation: {exc}", file=sys.stderr)
        print("Install Pillow in the active Python environment or skip contact-sheet generation.", file=sys.stderr)
        return 2

    input_dir = Path(args.input_dir)
    output = Path(args.output)
    if not input_dir.exists():
        print(f"ERROR: input directory not found: {input_dir}", file=sys.stderr)
        return 1
    files = sorted(input_dir.glob(args.pattern), key=natural_key)
    if args.max_pages and args.max_pages > 0:
        files = files[: args.max_pages]
    if not files:
        print("ERROR: no input images found", file=sys.stderr)
        return 1

    columns = max(1, args.columns)
    padding = 16
    label_h = 28
    thumbs = []
    for idx, path in enumerate(files, start=1):
        with Image.open(path) as img:
            img = img.convert("RGB")
            ratio = args.thumb_width / float(img.width)
            thumb_h = max(1, int(img.height * ratio))
            thumb = img.resize((args.thumb_width, thumb_h), Image.LANCZOS)
            thumbs.append((path, idx, thumb))

    cell_w = args.thumb_width + padding * 2
    cell_h = max(t.height for _, _, t in thumbs) + label_h + padding * 2
    rows = (len(thumbs) + columns - 1) // columns
    sheet = Image.new("RGB", (cell_w * columns, cell_h * rows), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for i, (path, idx, thumb) in enumerate(thumbs):
        row = i // columns
        col = i % columns
        x = col * cell_w + padding
        y = row * cell_h + padding + label_h
        label = f"Page {idx}: {path.name}"
        draw.text((col * cell_w + padding, row * cell_h + padding), label, fill="black", font=font)
        draw.rectangle([x - 1, y - 1, x + thumb.width + 1, y + thumb.height + 1], outline="gray")
        sheet.paste(thumb, (x, y))

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)

    manifest = {
        "input_dir": str(input_dir),
        "output": str(output),
        "page_count": len(files),
        "columns": columns,
        "thumb_width": args.thumb_width,
        "files": [str(p) for p in files],
    }
    if args.json_path:
        json_path = Path(args.json_path)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
