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
    p.add_argument("--batch-size", type=int, default=1, help=argparse.SUPPRESS)
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


def clean_cjk_spaces(text: str) -> str:
    """Remove spaces between CJK characters."""
    t = re.sub(r"(?<=[\u4e00-\u9fff]) (?=[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])", "", text)
    t = re.sub(r"(?<=[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]) (?=[\u4e00-\u9fff])", "", t)
    return t


_EXTRACT_PROMPT = """识别书籍内容，输出纯JSON（字段名必须是header_text, footer_text, book_pages, chapter, body）：{"header_text":"","footer_text":"","book_pages":[],"chapter":"","body":"正文"}"""


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
    fm = [
        "---",
        f"type: book-page",
        f"extract-backend: {backend}",
        f"image-index: {page_index}",
    ]
    if meta:
        if meta.get("book_pages"):
            bp = ", ".join(str(p) for p in meta["book_pages"])
            fm.append(f"book-pages: [{bp}]")
        if meta.get("chapter"):
            fm.append(f"chapter: {meta['chapter']}")
        if meta.get("header_text"):
            fm.append(f"header_text: {meta['header_text']}")
        if meta.get("footer_text"):
            fm.append(f"footer_text: {meta['footer_text']}")
    fm.append("---")
    content = "\n".join(fm) + "\n\n" + clean_cjk_spaces(body.strip()) + "\n"
    output_path.write_text(content, encoding="utf-8")
    print(f"  wrote {output_path}")


def extract_vision_json(text: str) -> dict:
    """Extract JSON from model response (handles ```json wrapping)."""
    raw = text.strip()
    for sep in ["```json", "```JSON", "```"]:
        if sep in raw:
            parts = raw.split(sep, 1)
            if len(parts) > 1 and "```" in parts[1]:
                raw = parts[1].split("```")[0].strip()
    return json.loads(raw) if raw.startswith("{") else {}


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


# ---- Raw page quality validation ----

def validate_raw_page(book_dir: Path, page_idx: int) -> dict | None:
    """Validate a single raw page. Returns re-extraction params if needed."""
    path = book_dir / f"page-{page_idx:03d}.md"
    if not path.is_file():
        return {"action": "re-extract", "reason": "missing"}
    content = path.read_text(encoding="utf-8")
    parts = content.split("---\n", 2)
    if len(parts) < 3:
        return {"action": "re-extract", "reason": "bad-format"}
    body = parts[2].strip()
    if not body or body in ["(此页无正文)", ""]:
        return {"action": "re-extract", "reason": "empty"}
    return None


def validate_raw_book(book_dir: Path) -> list[dict]:
    """Validate all pages in a book. Returns list of pages needing re-extraction."""
    pages = sorted(book_dir.glob("page-*.md"))
    issues = []
    for p in pages:
        idx = int(p.stem.split("-")[1])
        result = validate_raw_page(book_dir, idx)
        if result:
            result["page"] = idx
            issues.append(result)
    # Check for gaps
    indices = set(int(p.stem.split("-")[1]) for p in pages)
    max_idx = max(indices) if indices else 0
    for i in range(1, max_idx + 1):
        if i not in indices:
            issues.append({"page": i, "action": "re-extract", "reason": "gap"})
    return issues


def _check_body_coherence(body: str) -> list[str]:
    """Heuristic: flag pages with suspicious content."""
    warnings = []
    if len(body) < 50:
        warnings.append("very-short")
    lines = body.split("\n")
    non_empty = [l for l in lines if l.strip()]
    if len(non_empty) < 2:
        warnings.append("too-few-paragraphs")
    return warnings
