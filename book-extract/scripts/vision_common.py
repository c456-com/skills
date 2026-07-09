#!/usr/bin/env python3
"""Shared helpers for book-extract vision scripts (stdlib only)."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".heic", ".bmp"}


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_json_config(project_root: Path) -> dict:
    path = project_root / ".config" / "book-extract.json"
    if not path.is_file():
        raise SystemExit(f"Missing config: {path}\nCopy references/book-extract.example.json to .config/book-extract.json")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def resolve_api_key(config: dict, env_names: list[str]) -> str:
    vision = config.get("vision", {})
    key = (vision.get("api_key") or "").strip()
    if key and not key.startswith("${"):
        return key
    for name in env_names:
        val = os.environ.get(name, "").strip()
        if val:
            return val
    raise SystemExit(f"api_key empty in .config/book-extract.json; set vision.api_key or env: {', '.join(env_names)}")


def load_prompt(skill_dir: Path) -> str:
    path = skill_dir / "references" / "vision-extract-prompt.md"
    if not path.is_file():
        raise SystemExit(f"Missing prompt file: {path}")
    return path.read_text(encoding="utf-8").strip()


def list_images(images_dir: Path) -> list[Path]:
    if not images_dir.is_dir():
        raise SystemExit(f"images-dir not found: {images_dir}")
    files = [p for p in sorted(images_dir.iterdir()) if p.suffix.lower() in IMAGE_SUFFIXES]
    if not files:
        raise SystemExit(f"No images in {images_dir}")
    return files


def encode_image(path: Path) -> tuple[str, str]:
    mime, _ = mimetypes.guess_type(path.name)
    if not mime or not mime.startswith("image/"):
        mime = "image/png"
    data = base64.standard_b64encode(path.read_bytes()).decode("ascii")
    return mime, data


def page_output_path(output_dir: Path, index: int) -> Path:
    return output_dir / f"page-{index:03d}.md"


def build_base_parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--project-root", required=True, help="Knowledge base project root (contains .config/)")
    p.add_argument("--images-dir", required=True, help="Directory of page images")
    p.add_argument("--output-dir", required=True, help="Write page-NNN.md here")
    p.add_argument("--start", type=int, default=0, help="Start index in sorted image list (0-based)")
    p.add_argument("--end", type=int, default=-1, help="End index inclusive; -1 = last")
    p.add_argument("--batch-size", type=int, default=2, help="Images per API request")
    p.add_argument("--resume", action="store_true", help="Skip pages that already have page-NNN.md")
    p.add_argument("--delay", type=float, default=0.5, help="Seconds between API batches")
    return p


def slice_images(images: list[Path], start: int, end: int) -> list[Path]:
    if end < 0:
        end = len(images) - 1
    end = min(end, len(images) - 1)
    if start < 0 or start > end:
        raise SystemExit(f"Invalid range start={start} end={end} (total {len(images)})")
    return images[start : end + 1]


def http_post_json(url: str, headers: dict, payload: dict, timeout: int = 300) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code} {url}\n{detail}") from exc


def parse_page_meta(body: str) -> tuple[dict, str]:
    """Parse structured metadata header from vision output.

    Expected format (first 4 lines):
        [页眉: ...]
        [页脚: ...]
        [书页: ...]
        [章节: ...]

    Returns (meta_dict, cleaned_body).
    meta_dict keys: header_text, footer_text, book_pages (list[int|str] or None), chapter
    """
    meta: dict = {}
    lines = body.split("\n")
    meta_keys = ["header_text", "footer_text", "book_pages_raw", "chapter"]
    markers = ["[页眉:", "[页脚:", "[书页:", "[章节:"]
    consume = 0

    for i in range(min(6, len(lines))):
        stripped = lines[i].strip()
        for j, marker in enumerate(markers):
            if stripped.startswith(marker):
                content_after = stripped[len(marker):]
                end = content_after.find("]")
                val = content_after[:end].strip() if end >= 0 else content_after.strip().rstrip("]").strip()
                if marker == "[书页:":
                    meta["book_pages_raw"] = val if val else None
                elif marker == "[页眉:":
                    meta["header_text"] = val if val else None
                elif marker == "[页脚:":
                    meta["footer_text"] = val if val else None
                elif marker == "[章节:":
                    meta["chapter"] = val if val else None
                consume = max(consume, i + 1)
                break

    # Parse book_pages string into list
    if meta.get("book_pages_raw"):
        raw = meta["book_pages_raw"]
        parts = [p.strip() for p in raw.replace("，", ",").split(",")]
        book_pages = []
        for p in parts:
            try:
                book_pages.append(int(p))
            except ValueError:
                book_pages.append(p)  # keep roman numerals etc as-is
        meta["book_pages"] = book_pages if book_pages else None
    else:
        meta["book_pages"] = None
    del meta["book_pages_raw"]

    # Remove consumed lines from body
    body_lines = lines[consume:]
    # Strip leading empty lines
    while body_lines and not body_lines[0].strip():
        body_lines = body_lines[1:]
    cleaned = "\n".join(body_lines).strip()

    return meta, cleaned


def write_page_md(
    output_path: Path,
    *,
    page_index: int,
    source_image: Path,
    body: str,
    backend: str,
    meta: dict | None = None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    frontmatter_lines = [
        "---",
        f"type: book-page",
        f"extract-backend: {backend}",
        f"image-index: {page_index}",
    ]
    if meta:
        if meta.get("book_pages"):
            bp = ", ".join(str(p) for p in meta["book_pages"])
            frontmatter_lines.append(f"book-pages: [{bp}]")
        if meta.get("chapter"):
            frontmatter_lines.append(f"chapter: {meta['chapter']}")
        if meta.get("header_text"):
            frontmatter_lines.append(f"header-text: {meta['header_text']}")
        if meta.get("footer_text"):
            frontmatter_lines.append(f"footer-text: {meta['footer_text']}")
    frontmatter_lines.append("---")

    content = "\n".join(frontmatter_lines) + "\n\n" + body.strip() + "\n"
    output_path.write_text(content, encoding="utf-8")
    print(f"  wrote {output_path}")


def chunk_batches(items: list, size: int) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def extract_openai_text(response: dict) -> str:
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise SystemExit(f"Unexpected OpenAI-compatible response: {response}") from exc


def extract_anthropic_text(response: dict) -> str:
    try:
        blocks = response["content"]
        texts = [b["text"] for b in blocks if b.get("type") == "text"]
        return "\n".join(texts)
    except (KeyError, TypeError) as exc:
        raise SystemExit(f"Unexpected Anthropic response: {response}") from exc


_THINKING_MARKERS = [
    "这个任务需要我", "分析图片结构", "提取元信息",
    "让我仔细", "让我分析", "让我们", "我看一下",
    "Here's a thinking process",
]


def is_thinking_text(text: str) -> bool:
    """Detect if model output thinking/analysis instead of content."""
    head = text.strip()[:120]
    return any(m in head for m in _THINKING_MARKERS)
