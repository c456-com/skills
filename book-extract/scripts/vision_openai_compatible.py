#!/usr/bin/env python3
"""Extract book pages via OpenAI-compatible vision API — 1 image → 1 .md file."""

from __future__ import annotations

import time
from pathlib import Path

from vision_common import (
    build_base_parser,
    encode_image,
    extract_openai_text,
    http_post_json,
    list_images,
    load_json_config,
    load_prompt,
    page_output_path,
    parse_page_meta,
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
    prompt: str,
    image_path: Path,
    max_tokens: int = 4096,
) -> str:
    base = base_url.rstrip("/")
    url = f"{base}/chat/completions" if not base.endswith("/chat/completions") else base

    mime, data = encode_image(image_path)
    content: list[dict] = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}},
    ]

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": max_tokens,
        "temperature": 0,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    response = http_post_json(url, headers, payload)
    return extract_openai_text(response)


def main() -> None:
    parser = build_base_parser("Extract book pages via OpenAI-compatible vision API — 1 image → 1 .md")
    parser.add_argument("--batch-size", type=int, default=1, help=argparse.SUPPRESS)
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    images_dir = Path(args.images_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    config = load_json_config(project_root)
    if config.get("vision_mode") == "agent_native":
        raise SystemExit("vision_mode is agent_native; use Agent Read tool instead of this script.")

    vision = config.get("vision", {})
    api_key = resolve_api_key(config, ["OPENAI_API_KEY", "OPENROUTER_API_KEY", "DEEPSEEK_API_KEY"])
    base_url = vision.get("base_url", "https://api.openai.com/v1").strip()
    model = vision.get("model", "gpt-4o")
    prompt = load_prompt(skill_root())

    all_images = list_images(images_dir)
    images = slice_images(all_images, args.start, args.end)

    print(f"OpenAI-compatible vision: {len(images)} pages, 1 image → 1 .md, model={model}")

    for i, img in enumerate(images, start=args.start):
        out_path = page_output_path(output_dir, i)
        if args.resume and out_path.is_file():
            print(f"  skip {out_path} (resume)")
            continue

        print(f"  page {i}: {img.name}")
        text = call_vision(
            base_url=base_url,
            api_key=api_key,
            model=model,
            prompt=prompt,
            image_path=img,
        )
        meta, clean_body = parse_page_meta(text)
        write_page_md(
            out_path,
            page_index=i,
            source_image=img,
            body=clean_body,
            backend="openai_compatible",
            meta=meta,
        )
        if args.delay:
            time.sleep(args.delay)

    print("Done.")


if __name__ == "__main__":
    import argparse
