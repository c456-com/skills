#!/usr/bin/env python3
"""Extract book pages via OpenAI-compatible vision API — JSON output, 1 image → 1 .md."""

from __future__ import annotations

import time
from pathlib import Path

from vision_common import (
    _EXTRACT_PROMPT,
    build_base_parser,
    encode_image,
    extract_openai_text,
    extract_vision_json,
    http_post_json,
    list_images,
    load_json_config,
    page_output_path,
    resolve_api_key,
    skill_root,
    slice_images,
    write_page_md,
)


def call_vision(
    *,
    base_url: str,
    api_key: str,
    model: str,
    image_path: Path,
    max_tokens: int = 8192,
) -> tuple[dict, str]:
    base = base_url.rstrip("/")
    url = f"{base}/chat/completions" if not base.endswith("/chat/completions") else base
    mime, data = encode_image(image_path)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _EXTRACT_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}},
                ],
            }
        ],
        "max_tokens": max_tokens,
        "temperature": 0,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    response = http_post_json(url, headers, payload)
    raw = extract_openai_text(response)
    data = extract_vision_json(raw)
    body = data.get("body", "") or "\n".join(data.get("text_content", "") or data.get("text", "") or [""])
    return data, body


def main() -> None:
    parser = build_base_parser("Extract book pages via OpenAI-compatible vision API — JSON, 1:1")
    parser.add_argument("--batch-size", type=int, default=1, help=argparse.SUPPRESS)
    args = parser.parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    images_dir = Path(args.images_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    config = load_json_config(project_root)
    if config.get("vision_mode") == "agent_native":
        raise SystemExit("vision_mode is agent_native; use Agent Read instead.")
    vision = config.get("vision", {})
    api_key = resolve_api_key(config, ["OPENAI_API_KEY", "OPENROUTER_API_KEY", "DEEPSEEK_API_KEY"])
    base_url = vision.get("base_url", "https://api.openai.com/v1").strip()
    model = vision.get("model", "gpt-4o")
    all_images = list_images(images_dir)
    images = slice_images(all_images, args.start, args.end)
    print(f"OpenAI-compatible vision: {len(images)} pages, JSON output, model={model}")
    for i, img in enumerate(images, start=args.start):
        out_path = page_output_path(output_dir, i)
        if args.resume and out_path.is_file():
            print(f"  skip {out_path} (resume)")
            continue
        print(f"  page {i}: {img.name}")
        data, body = call_vision(base_url=base_url, api_key=api_key, model=model, image_path=img)
        write_page_md(out_path, page_index=i, source_image=img, body=body, backend="openai_compatible", meta=data)
        if args.delay:
            time.sleep(args.delay)
    print("Done.")


if __name__ == "__main__":
    import argparse
